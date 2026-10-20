#!/usr/bin/env python3
"""Coleta os dados do Worlds 2026 e gera o site (index.html) com tudo embutido.

Fontes: API do LoL Esports (agenda, chaves, times, escalações), feed de
estatísticas ao vivo do LoL Esports (linha do tempo de cada jogo, a cada 10 s),
Data Dragon (ícones de campeões e itens) e static.lolesports.com (fotos e logos).

Uso: python -m worlds2026            # coleta o que falta e gera docs/index.html
     python -m worlds2026 --so-site  # só regera o site com o cache atual
"""
import base64, io, json, re, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from PIL import Image

from . import config, extras

CACHE = str(config.CACHE)
os.makedirs(os.path.join(CACHE, "jogos"), exist_ok=True)
os.makedirs(os.path.join(CACHE, "img"), exist_ok=True)

API = "https://esports-api.lolesports.com/persisted/gw"
FEED = "https://feed.lolesports.com/livestats/v1"
CHAVE = os.environ.get("LOLESPORTS_API_KEY", "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z")  # chave pública do próprio lolesports.com
LIGA_WORLDS = "98767975604431411"
TORNEIO = "115660540725177488"  # worlds_2026


def baixar(url, json_=True, tentativas=4, cabecalhos=None):
    h = {"User-Agent": "Mozilla/5.0 (site-worlds)"}
    if url.startswith(API):
        h["x-api-key"] = CHAVE
    h.update(cabecalhos or {})
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r:
                corpo = r.read()
                if not corpo:
                    return None
                return json.loads(corpo) if json_ else corpo
        except urllib.error.HTTPError as e:
            if e.code in (204, 404):
                return None
            if i == tentativas - 1:
                raise
        except Exception:
            if i == tentativas - 1:
                raise
        time.sleep(1.5 * (i + 1))


def api(rota, **params):
    params.setdefault("hl", "pt-BR")
    return baixar(f"{API}/{rota}?{urllib.parse.urlencode(params)}")


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


# ---------------------------------------------------------------- agenda

def agenda_liga(liga_id, ate_data="2026-10-01", paginas=6):
    """Eventos da liga a partir da página atual, voltando no tempo até ate_data."""
    eventos, token = [], None
    for _ in range(paginas):
        p = {"leagueId": liga_id}
        if token:
            p["pageToken"] = token
        d = api("getSchedule", **p)["data"]["schedule"]
        eventos += d["events"]
        token = (d.get("pages") or {}).get("older")
        if not token or min(e["startTime"] for e in d["events"]) < ate_data:
            break
    vistos, out = set(), []
    for e in sorted(eventos, key=lambda e: e["startTime"]):
        mid = (e.get("match") or {}).get("id")
        if mid and mid not in vistos:
            vistos.add(mid)
            out.append(e)
    return out


def montar_agenda():
    est = api("getStandings", tournamentId=TORNEIO)["data"]["standings"][0]["stages"]
    fase_de = {}
    for st in est:
        for sec in st["sections"]:
            for m in sec["matches"]:
                fase_de[m["id"]] = st["slug"]
    eventos = [e for e in agenda_liga(LIGA_WORLDS) if e["match"]["id"] in fase_de]
    partidas = []
    for e in eventos:
        m = e["match"]
        partidas.append({
            "id": m["id"],
            "inicio": e["startTime"],
            "estado": e["state"],
            "fase": fase_de[m["id"]],
            "bloco": e.get("blockName"),
            "melhorDe": (m.get("strategy") or {}).get("count", 1),
            "times": [{
                "codigo": t["code"], "nome": t["name"],
                "vitorias": (t.get("result") or {}).get("gameWins"),
                "resultado": (t.get("result") or {}).get("outcome"),
            } for t in m["teams"]],
        })
    return partidas


# ---------------------------------------------------------------- jogos

def frame_em(jogo_id, quando, rota="window"):
    d = baixar(f"{FEED}/{rota}/{jogo_id}?startingTime={iso(quando)}")
    return d


def processar_jogo(jogo_id, partida_id, numero):
    arq = os.path.join(CACHE, "jogos", f"{jogo_id}.json")
    if os.path.exists(arq):
        return json.load(open(arq))
    primeiro = baixar(f"{FEED}/window/{jogo_id}")
    if not primeiro or not primeiro.get("frames"):
        return None
    meta = primeiro["gameMetadata"]
    t0 = ts(primeiro["frames"][0]["rfc460Timestamp"]).replace(microsecond=0)
    t0 -= timedelta(seconds=t0.second % 10)

    # Busca janelas de 10 s em lotes paralelos até o jogo terminar.
    frames, k, fim = {}, 0, False
    with ThreadPoolExecutor(24) as ex:
        while not fim and k < 600:
            lote = list(range(k, k + 48))
            res = list(ex.map(lambda i: frame_em(jogo_id, t0 + timedelta(seconds=10 * i)), lote))
            vazios = 0
            for i, r in zip(lote, res):
                fs = (r or {}).get("frames") or []
                if not fs:
                    vazios += 1
                    continue
                for f in fs:
                    frames[f["rfc460Timestamp"]] = f
                if any(f["gameState"] == "finished" for f in fs):
                    fim = True
            if vazios == len(lote):
                fim = True
            k += 48
    lista = [frames[k] for k in sorted(frames)]
    # descarta o que vier depois do primeiro "finished"
    for i, f in enumerate(lista):
        if f["gameState"] == "finished":
            lista = lista[: i + 1]
            break

    # Relógio de jogo: soma só o tempo em "in_game" (pausas não contam).
    amostras, relogio, ant = [], 0.0, None
    for f in lista:
        t = ts(f["rfc460Timestamp"])
        if ant is not None and ant[1] == "in_game":
            relogio += (t - ant[0]).total_seconds()
        ant = (t, f["gameState"])
        amostras.append((relogio, f))
    # o feed começa com alguns segundos de carregamento: começa a contar no 1º ouro > 0
    inicio_ouro = next((s for s, f in amostras if f["blueTeam"]["totalGold"] > 0), 0)
    duracao = amostras[-1][0] - inicio_ouro

    def resumo(f):
        out = {}
        for lado in ("blueTeam", "redTeam"):
            t = f[lado]
            out[lado] = {
                "ouro": t["totalGold"], "abates": t["totalKills"], "torres": t["towers"],
                "inibidores": t["inhibitors"], "barons": t["barons"], "dragoes": list(t["dragons"]),
                "p": [[p["totalGold"], p["kills"], p["deaths"], p["assists"], p["creepScore"], p["level"]]
                      for p in t["participants"]],
            }
        return out

    # Uma amostra por segundo de jogo arredondado a 10 s; eventos por diferença.
    serie, eventos, anterior = [], [], None
    for s, f in amostras:
        seg = max(0, round(s - inicio_ouro))
        r = resumo(f)
        if anterior:
            eventos += diferencas(anterior, r, seg, meta)
        anterior = r
        if not serie or seg - serie[-1]["s"] >= 10 or f is amostras[-1][1]:
            serie.append({"s": seg, **r})

    # Estatísticas finais por jogador (dano, KP, visão, itens, runas).
    det = frame_em(jogo_id, ts(lista[-1]["rfc460Timestamp"]).replace(microsecond=0) - timedelta(seconds=ts(lista[-1]["rfc460Timestamp"]).second % 10), "details")
    finais = {p["participantId"]: p for p in ((det or {}).get("frames") or [{}])[-1].get("participants", [])}

    final = serie[-1]
    b, r = final["blueTeam"], final["redTeam"]
    placar = lambda t: t["inibidores"] * 10 + t["torres"] + t["ouro"] / 10000
    vencedor = "blue" if placar(b) >= placar(r) else "red"

    jogadores = []
    for lado, md in (("blue", meta["blueTeamMetadata"]), ("red", meta["redTeamMetadata"])):
        for pm in md["participantMetadata"]:
            d = finais.get(pm["participantId"], {})
            jogadores.append({
                "pid": pm["participantId"], "lado": lado, "jogadorId": pm.get("esportsPlayerId"),
                "nick": pm["summonerName"].split(" ", 1)[-1] if " " in pm["summonerName"] else pm["summonerName"],
                "campeao": pm["championId"], "rota": pm["role"],
                "dano": d.get("championDamageShare"), "kp": d.get("killParticipation"),
                "wards": d.get("wardsPlaced"), "wardsDestruidas": d.get("wardsDestroyed"),
                "itens": d.get("items", []), "runas": (d.get("perkMetadata") or {}).get("perks", [])[:1],
            })

    jogo = {
        "id": jogo_id, "partida": partida_id, "numero": numero,
        "patch": ".".join(meta.get("patchVersion", "").split(".")[:2]),
        "timeAzul": meta["blueTeamMetadata"]["esportsTeamId"], "timeVermelho": meta["redTeamMetadata"]["esportsTeamId"],
        "duracao": round(duracao), "vencedor": vencedor, "jogadores": jogadores,
        "serie": compactar(serie), "eventos": eventos,
    }
    json.dump(jogo, open(arq, "w"), ensure_ascii=False)
    return jogo


def diferencas(a, b, seg, meta):
    ev = []
    for lado, outro in (("blueTeam", "redTeam"), ("redTeam", "blueTeam")):
        cor = "blue" if lado == "blueTeam" else "red"
        A, B = a[lado], b[lado]
        mortos = [i for i in range(5) if b[outro]["p"][i][2] > a[outro]["p"][i][2]]
        matadores = [i for i in range(5) if B["p"][i][1] > A["p"][i][1]]
        n = B["abates"] - A["abates"]
        if n > 0:
            base = 0 if lado == "blueTeam" else 5
            vit = 5 if lado == "blueTeam" else 0
            ev.append({"s": seg, "tipo": "abate", "lado": cor, "n": n,
                       "por": [base + i + 1 for i in matadores], "vitimas": [vit + i + 1 for i in mortos]})
        for d in B["dragoes"][len(A["dragoes"]):]:
            ev.append({"s": seg, "tipo": "dragao", "lado": cor, "dragao": d})
        for campo, tipo in (("torres", "torre"), ("inibidores", "inibidor"), ("barons", "barao")):
            for _ in range(B[campo] - A[campo]):
                ev.append({"s": seg, "tipo": tipo, "lado": cor})
    return ev


def compactar(serie):
    """Série a cada ~30 s: ouro dos times e [ouro,k,d,a,cs,nível] dos 10 jogadores."""
    out, ult = [], -999
    for x in serie:
        if x["s"] - ult >= 30 or x is serie[-1]:
            out.append([x["s"], x["blueTeam"]["ouro"], x["redTeam"]["ouro"],
                        x["blueTeam"]["p"] + x["redTeam"]["p"]])
            ult = x["s"]
    return out


# ---------------------------------------------------------------- times e imagens

def miniatura(url, lado, formato="WEBP", quadrado=False):
    if not url:
        return None
    url = url.replace("http://", "https://")
    nome = os.path.join(CACHE, "img", f"{abs(hash((url, lado))) % 10**12}_{lado}.txt")
    nome = os.path.join(CACHE, "img", base64.urlsafe_b64encode(f"{url}|{lado}".encode()).decode()[-60:] + ".txt")
    if os.path.exists(nome):
        return open(nome).read() or None
    try:
        dados = baixar(url, json_=False)
        im = Image.open(io.BytesIO(dados)).convert("RGBA")
        if quadrado:
            w, h = im.size
            c = min(w, h)
            im = im.crop(((w - c) // 2, 0, (w - c) // 2 + c, c))
        im.thumbnail((lado, lado))
        buf = io.BytesIO()
        im.save(buf, formato, quality=72, method=6)
        uri = f"data:image/{formato.lower()};base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print("  imagem falhou", url, e)
        uri = ""
    open(nome, "w").write(uri)
    return uri or None


def titulares_regionais(time, ligas):
    """IDs dos 5 jogadores da última partida oficial do time na liga dele."""
    liga = (time.get("homeLeague") or {}).get("name")
    lid = ligas.get(liga)
    if not lid:
        return []
    try:
        evs = agenda_liga(lid, ate_data="2026-01-01", paginas=3)
    except Exception:
        return []
    for e in reversed(evs):
        if e["state"] != "completed":
            continue
        if time["code"] not in [t["code"] for t in e["match"]["teams"]]:
            continue
        det = api("getEventDetails", id=e["match"]["id"])["data"]["event"]["match"]
        for g in reversed(det["games"]):
            if g["state"] != "completed":
                continue
            w = baixar(f"{FEED}/window/{g['id']}")
            if not w:
                continue
            md = w["gameMetadata"]
            for lado in ("blueTeamMetadata", "redTeamMetadata"):
                if md[lado]["esportsTeamId"] == time["id"]:
                    return [p["esportsPlayerId"] for p in md[lado]["participantMetadata"]]
    return []


CODIGO_CURIOSIDADES = {"gen-g": "GEN", "tl": "TLAW", "koi": "MKOI"}


def ler_curiosidades():
    """Curiosidades e histórico de data/curiosidades (opcional)."""
    base = str(config.CURIOSIDADES)
    out = {"times": {}, "confrontos": []}
    if not os.path.isdir(base):
        return out
    cod = lambda i: CODIGO_CURIOSIDADES.get(i, i.upper())
    for arq in sorted(os.listdir(os.path.join(base, "times"))):
        d = json.load(open(os.path.join(base, "times", arq)))
        out["times"][cod(d["id"])] = {k: d.get(k) for k in ("seed", "como_classificou", "titulos_mundiais", "melhor_mundial", "curiosidades")}
    for arq in sorted(os.listdir(os.path.join(base, "confrontos"))):
        d = json.load(open(os.path.join(base, "confrontos", arq)))
        out["confrontos"].append({"times": sorted([cod(d["time_a"]["id"]), cod(d["time_b"]["id"])]),
                                  **{k: d.get(k) for k in ("manchete", "resumo_historico", "historico", "curiosidades")}})
    return out


def main():
    so_site = "--so-site" in sys.argv
    agora = datetime.now(timezone.utc)
    print("agenda…")
    partidas = montar_agenda()
    codigos = {t["codigo"] for p in partidas for t in p["times"] if t["codigo"] != "TBD"}

    print("times…")
    todos = api("getTeams")["data"]["teams"]
    ligas = {l["name"]: l["id"] for l in api("getLeagues")["data"]["leagues"]}
    nomes = {t["codigo"]: t["nome"] for p in partidas for t in p["times"] if t["codigo"] != "TBD"}
    por_codigo = {}
    for c, nome in nomes.items():
        cands = [t for t in todos if t["code"] == c]
        exatos = [t for t in cands if t["name"].lower() == nome.lower()]
        cands = exatos or [t for t in cands if not re.search(r"academy|challengers", t["name"], re.I)] or cands
        cands.sort(key=lambda t: (t.get("status") != "active", -len(t.get("players") or [])))
        por_codigo[c] = cands[0]

    print("jogos…")
    jogos = []
    for p in partidas:
        if p["estado"] not in ("completed", "inProgress"):
            continue
        det = api("getEventDetails", id=p["id"])["data"]["event"]["match"]
        for g in det["games"]:
            if g["state"] == "completed" and not so_site:
                print("  ", p["times"][0]["codigo"], "x", p["times"][1]["codigo"], "jogo", g["number"])
                j = processar_jogo(g["id"], p["id"], g["number"])
            else:
                arq = os.path.join(CACHE, "jogos", f"{g['id']}.json")
                j = json.load(open(arq)) if os.path.exists(arq) else None
            if j:
                jogos.append(j)

    print("leaguepedia (bans, arautos, dano)…")
    versao = baixar("https://ddragon.leagueoflegends.com/api/versions.json")[0]
    camp = baixar(f"https://ddragon.leagueoflegends.com/cdn/{versao}/data/pt_BR/champion.json")["data"]
    camp_en = baixar(f"https://ddragon.leagueoflegends.com/cdn/{versao}/data/en_US/champion.json")["data"]
    chave_por_nome = {}
    for k, v in camp_en.items():
        chave_por_nome[extras.norm(v["name"])] = k
        chave_por_nome[extras.norm(k)] = k
    if so_site:
        arq_lp = os.path.join(CACHE, "leaguepedia.json")
        lp = json.load(open(arq_lp)) if os.path.exists(arq_lp) else {}
    else:
        lp = extras.placares_leaguepedia(chave_por_nome)
    extras.enriquecer_jogos(jogos, lp)

    # confere o vencedor de cada jogo com o placar oficial da série
    id_codigo = {t["id"]: c for c, t in por_codigo.items()}
    for p in partidas:
        js = [j for j in jogos if j["partida"] == p["id"]]
        if not js:
            continue
        cont = {}
        for j in js:
            c = id_codigo.get(j["timeAzul"] if j["vencedor"] == "blue" else j["timeVermelho"])
            cont[c] = cont.get(c, 0) + 1
        oficial = {t["codigo"]: t["vitorias"] for t in p["times"]}
        if p["estado"] == "completed" and cont != {k: v for k, v in oficial.items() if v}:
            print("  ATENÇÃO: vencedores estimados", cont, "≠ placar oficial", oficial)

    print("escalações e fotos…")
    titulares_por_time = {}
    for c, t in por_codigo.items():
        ids = []
        for j in jogos:
            for lado, tid in (("blue", j["timeAzul"]), ("red", j["timeVermelho"])):
                if tid == t["id"]:
                    ids = [x["jogadorId"] for x in j["jogadores"] if x["lado"] == lado]
        if not ids and not so_site:
            ids = titulares_regionais(t, ligas)
        titulares_por_time[c] = ids
    cache_tit = os.path.join(CACHE, "titulares.json")
    antigos = json.load(open(cache_tit)) if os.path.exists(cache_tit) else {}
    for c in titulares_por_time:
        if not titulares_por_time[c]:
            titulares_por_time[c] = antigos.get(c, [])
    json.dump(titulares_por_time, open(cache_tit, "w"))

    ordem = {"top": 0, "jungle": 1, "mid": 2, "bottom": 3, "support": 4}
    times = {}
    for c, t in por_codigo.items():
        tit = titulares_por_time.get(c, [])
        jogs = []
        for pl in t.get("players", []):
            usado = pl["id"] in tit or any(pl["id"] == x["jogadorId"] for j in jogos for x in j["jogadores"])
            if not usado:
                continue
            jogs.append({
                "id": pl["id"], "nick": pl["summonerName"].strip(), "nome": f"{pl.get('firstName','')} {pl.get('lastName','')}".strip(),
                "rota": pl["role"], "titular": pl["id"] in tit,
                "foto": None if "default-headshot" in (pl.get("image") or "") else miniatura(pl.get("image"), 160, quadrado=True),
            })
        jogs.sort(key=lambda x: (not x["titular"], ordem.get(x["rota"], 9)))
        times[c] = {
            "id": t["id"], "codigo": c, "nome": t["name"], "liga": (t.get("homeLeague") or {}).get("name"),
            "regiao": (t.get("homeLeague") or {}).get("region"),
            "logo": miniatura(t.get("image"), 128, "PNG" if False else "WEBP"), "jogadores": jogs,
        }
        print("  ", c, len(jogs), "jogadores")

    print("solo queue…")
    contas = extras.contas_soloq()
    soloq = {}
    arq_sq = os.path.join(CACHE, "soloq-saida.json")
    if os.environ.get("RIOT_API_KEY") and not so_site:
        soloq = extras.soloq_riot(contas, os.environ["RIOT_API_KEY"], None)
        if soloq:
            json.dump(soloq, open(arq_sq, "w"))
    if not soloq and os.path.exists(arq_sq):
        soloq = json.load(open(arq_sq))
    for t in times.values():
        for pl in t["jogadores"]:
            k = next((k for k in contas if k.split("|")[0] == extras.norm(pl["nick"])), None)
            if k:
                pl["contas"] = contas[k]
                pl["soloq"] = soloq.get(k)

    print("campeões e itens…")
    chave_camp = {k.lower(): k for k in camp}
    usados = {x["campeao"] for j in jogos for x in j["jogadores"]}
    usados |= {b for j in jogos if j.get("lp") for l in ("blue", "red") for b in j["lp"]["bans"][l]}
    usados |= {p[2] for t in times.values() for pl in t["jogadores"] if pl.get("soloq") for p in pl["soloq"]["partidas"]}
    campeoes = {}
    for nome in usados:
        k = chave_camp.get(nome.lower().replace(" ", "").replace("'", "").replace(".", ""), nome)
        campeoes[nome] = {
            "nome": camp.get(k, {}).get("name", nome),
            "icone": miniatura(f"https://ddragon.leagueoflegends.com/cdn/{versao}/img/champion/{k}.png", 64),
        }
    itens_usados = {i for j in jogos for x in j["jogadores"] for i in x["itens"] if i}
    itd = baixar(f"https://ddragon.leagueoflegends.com/cdn/{versao}/data/pt_BR/item.json")["data"]
    itens = {}
    for i in itens_usados:
        if str(i) in itd:
            itens[i] = {"nome": itd[str(i)]["name"],
                        "icone": miniatura(f"https://ddragon.leagueoflegends.com/cdn/{versao}/img/item/{i}.png", 40)}

    curiosidades = ler_curiosidades()

    dados = {
        "atualizado": iso(agora), "curiosidades": curiosidades, "versaoDD": versao,
        "partidas": partidas, "times": times, "jogos": jogos, "campeoes": campeoes, "itens": itens,
    }
    json.dump(dados, open(os.path.join(CACHE, "dados.json"), "w"), ensure_ascii=False)
    modelo = open(config.MODELO, encoding="utf-8").read()
    html = modelo.replace("/*__DADOS__*/null", json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    open(config.SITE, "w", encoding="utf-8").write(html)
    print(f"ok: {len(partidas)} partidas, {len(jogos)} jogos, {len(times)} times, index.html {len(html)/1e6:.2f} MB")


if __name__ == "__main__":
    main()
