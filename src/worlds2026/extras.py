"""Dados complementares: placares da Leaguepedia (bans, arautos, dano) e solo queue pela API da Riot."""
import json, os, re, time, urllib.parse, urllib.request

from . import config

CACHE = str(config.CACHE)
UA = "MetricasWorldsBot/0.1 (personal project)"

# Páginas de placares do Worlds 2026 na Leaguepedia (as que ainda não existem são ignoradas).
PAGINAS_LP = ["2026_Season_World_Championship/Play-In/Scoreboards",
              "2026_Season_World_Championship/Main_Event/Scoreboards"] + \
             [f"2026_Season_World_Championship/Main_Event/Scoreboards/Week_{i}" for i in range(1, 5)]


def norm(nome):
    return re.sub(r"[^a-z0-9]", "", (nome or "").lower())


def wikitext(pagina):
    q = urllib.parse.urlencode({"action": "parse", "page": pagina, "prop": "wikitext", "format": "json", "redirects": 1})
    for tentativa in range(4):
        req = urllib.request.Request("https://lol.fandom.com/api.php?" + q, headers={"User-Agent": UA})
        d = json.load(urllib.request.urlopen(req, timeout=30))
        err = (d.get("error") or {}).get("code")
        if err == "missingtitle":
            return None
        if err == "ratelimited":
            time.sleep(15 * (tentativa + 1))
            continue
        if err:
            raise RuntimeError(err)
        return d["parse"]["wikitext"]["*"]
    raise RuntimeError("Leaguepedia limitou as consultas")


def _campos(bloco):
    out = {}
    for m in re.finditer(r"\|\s*([a-z0-9_]+)\s*=\s*([^|{}\n]*)", bloco):
        out.setdefault(m.group(1), m.group(2).strip())
    return out


def placares_leaguepedia(chave_por_nome):
    """Lista de jogos com bans, arautos, larvas e dano de cada jogador, identificados pelos 10 campeões."""
    arq = os.path.join(CACHE, "leaguepedia.json")
    antigos = json.load(open(arq)) if os.path.exists(arq) else {}
    for pagina in PAGINAS_LP:
        try:
            wt = wikitext(pagina)
        except Exception as e:
            print("  leaguepedia falhou em", pagina, e)
            continue
        time.sleep(2)
        if not wt:
            continue
        for bloco in re.split(r"\{\{Scoreboard/Season", wt)[1:]:
            cab = _campos(re.sub(r"\|(blue|red)\d=\{\{Scoreboard/Player.*?\|runes=\{\{[^}]*\}\}\}\}", "", bloco, flags=re.S))
            jog = {}
            for lado in ("blue", "red"):
                for i in range(1, 6):
                    m = re.search(r"\|" + lado + str(i) + r"=\{\{Scoreboard/Player(.*?)\|runes=", bloco, re.S)
                    if m:
                        jog[f"{lado}{i}"] = _campos(m.group(1))
            if len(jog) < 10:
                continue
            ck = lambda n: chave_por_nome.get(norm(n), n)
            campeoes = sorted(norm(ck(p.get("champion"))) for p in jog.values())
            chave = "|".join(campeoes)
            bans = lambda t: [ck(cab.get(f"{t}ban{i}")) for i in range(1, 6) if cab.get(f"{t}ban{i}") and cab.get(f"{t}ban{i}") not in ("None", "Loss of Ban")]
            num = lambda v: int(v) if str(v).strip().lstrip("-").isdigit() else None
            antigos[chave] = {
                "vencedor": "blue" if cab.get("winner") == "1" else "red" if cab.get("winner") == "2" else None,
                "bans": {"blue": bans("team1"), "red": bans("team2")},
                "arautos": {"blue": num(cab.get("team1rh")), "red": num(cab.get("team2rh"))},
                "larvas": {"blue": num(cab.get("team1vg")), "red": num(cab.get("team2vg"))},
                "atakhan": {"blue": num(cab.get("team1at")), "red": num(cab.get("team2at"))},
                "jogadores": {norm(ck(p.get("champion"))): {"danoTotal": num(p.get("damagetochamps")), "visao": num(p.get("visionscore"))}
                              for p in jog.values()},
            }
    json.dump(antigos, open(arq, "w"), ensure_ascii=False)
    return antigos


def enriquecer_jogos(jogos, lp):
    for j in jogos:
        chave = "|".join(sorted(norm(x["campeao"]) for x in j["jogadores"]))
        info = lp.get(chave)
        if not info:
            j["lp"] = None
            continue
        if info["vencedor"] and info["vencedor"] != j["vencedor"]:
            print("  vencedor corrigido pela Leaguepedia:", j["id"], j["vencedor"], "→", info["vencedor"])
            j["vencedor"] = info["vencedor"]
        j["lp"] = {k: info[k] for k in ("bans", "arautos", "larvas", "atakhan")}
        for x in j["jogadores"]:
            x.update(info["jogadores"].get(norm(x["campeao"]), {}))


# ---------------------------------------------------------------- solo queue

OPGG = {"kr": "kr", "euw1": "euw", "na1": "na", "br1": "br", "vn2": "vn", "tw2": "tw", "eun1": "eune", "jp1": "jp"}


def contas_soloq():
    arq = str(config.CONTAS_SOLOQ)
    if not os.path.exists(arq):
        return {}
    out = {}
    for p in json.load(open(arq))["jogadores"]:
        contas = []
        for c in p.get("contas", []):
            link = None
            if c.get("tag_line") and c.get("platform") in OPGG:
                link = f"https://www.op.gg/summoners/{OPGG[c['platform']]}/{urllib.parse.quote(c['game_name'])}-{urllib.parse.quote(c['tag_line'])}"
            contas.append({"servidor": c.get("servidor"), "riotId": c.get("riot_id"), "link": link,
                           "platform": c.get("platform"), "regional": c.get("regional"),
                           "gameName": c.get("game_name"), "tagLine": c.get("tag_line"), "api": c.get("consultavel_api") == "sim"})
        out[norm(p["jogador"]) + "|" + p["sigla"].upper()] = {
            "links": {k: p.get(k) for k in ("dpm_lol", "lolpros", "leaguepedia") if p.get(k)}, "contas": contas}
    return out


class Riot:
    def __init__(self, chave):
        self.chave = chave

    def get(self, regiao, caminho):
        url = f"https://{regiao}.api.riotgames.com{caminho}"
        for tentativa in range(6):
            req = urllib.request.Request(url, headers={"X-Riot-Token": self.chave, "User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    time.sleep(1.25)  # cabe no limite de 100 chamadas a cada 2 minutos
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                if e.code == 429:
                    time.sleep(int(e.headers.get("Retry-After", "10")) + 1)
                    continue
                if e.code in (401, 403):
                    raise RuntimeError("chave da Riot recusada (expirada ou inválida)")
                time.sleep(3)
        return None


def soloq_riot(contas, chave, campeao_por_id):
    """Elo e últimas partidas ranqueadas da conta mais ativa de cada jogador. Usa cache de puuid e partidas."""
    arq = os.path.join(CACHE, "soloq.json")
    cache = json.load(open(arq)) if os.path.exists(arq) else {"puuid": {}, "partidas": {}}
    riot = Riot(chave)
    out = {}
    try:
        for chave_j, info in contas.items():
            melhor = None
            for c in [c for c in info["contas"] if c["api"]][:4]:
                k = c["riotId"]
                if k not in cache["puuid"]:
                    acc = riot.get(c["regional"], f"/riot/account/v1/accounts/by-riot-id/{urllib.parse.quote(c['gameName'])}/{urllib.parse.quote(c['tagLine'])}")
                    cache["puuid"][k] = acc and acc["puuid"]
                puuid = cache["puuid"][k]
                if not puuid:
                    continue
                ids = riot.get(c["regional"], f"/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&count=10") or []
                if ids and (not melhor or ids[0] > melhor[2][0]):
                    melhor = (c, puuid, ids)
            if not melhor:
                continue
            c, puuid, ids = melhor
            liga = riot.get(c["platform"], f"/lol/league/v4/entries/by-puuid/{puuid}") or []
            elo = next((e for e in liga if e.get("queueType") == "RANKED_SOLO_5x5"), None)
            partidas = []
            for mid in ids:
                if mid not in cache["partidas"]:
                    m = riot.get(c["regional"], f"/lol/match/v5/matches/{mid}")
                    if not m:
                        continue
                    cache["partidas"][mid] = {"fim": m["info"].get("gameEndTimestamp"), "dur": m["info"].get("gameDuration"),
                                              "p": {x["puuid"]: [x["championName"], x["win"], x["kills"], x["deaths"], x["assists"],
                                                                 x["totalMinionsKilled"] + x["neutralMinionsKilled"]] for x in m["info"]["participants"]}}
                pm = cache["partidas"][mid]
                if puuid in pm["p"]:
                    partidas.append([pm["fim"], pm["dur"], *pm["p"][puuid]])
            out[chave_j] = {"conta": c["riotId"], "servidor": c["servidor"], "link": c["link"],
                            "elo": elo and {k: elo.get(k) for k in ("tier", "rank", "leaguePoints", "wins", "losses")},
                            "partidas": partidas}
            print("   soloq", chave_j, c["riotId"], len(partidas), "partidas")
    except RuntimeError as e:
        print("  solo queue interrompida:", e)
    json.dump(cache, open(arq, "w"))
    return out
