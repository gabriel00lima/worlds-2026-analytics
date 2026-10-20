"""Gera curiosidades/jogadores/<id>.json (uma história curta por jogador do Swiss 2026).

Entradas: soloq/contas-soloq.json (81 jogadores, Leaguepedia) e mundiais-passados/ (estatísticas de Worlds 2011-2025).
Rodar: python3 gerar_jogadores.py
"""

import json
import os
import re
import unicodedata
import urllib.parse
from collections import defaultdict

DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def ler(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


OUT = os.path.join(DADOS, "curiosidades", "jogadores")
HOJE = "2026-10-20"

SIGLA_ID = {
    "GEN": "gen-g",
    "AL CN": "al",
    "TL": "tl",
    "G2": "g2",
    "TSTW": "tsw",
    "LOS": "los",
    "HLE": "hle",
    "BLG": "blg",
    "LYON24": "lyon",
    "MKOI": "koi",
    "T1": "t1",
    "TES": "tes",
    "CFO": "cfo",
    "Dplus": "dk",
    "IG": "ig",
    "KCORP": "kc",
}
NOME_TIME = {
    "gen-g": "Gen.G",
    "al": "Anyone's Legend",
    "tl": "Team Liquid",
    "g2": "G2 Esports",
    "tsw": "Team Secret Whales",
    "los": "LOS",
    "hle": "Hanwha Life Esports",
    "blg": "Bilibili Gaming",
    "lyon": "LYON",
    "koi": "Movistar KOI",
    "t1": "T1",
    "tes": "Top Esports",
    "cfo": "CTBC Flying Oyster",
    "dk": "Dplus KIA",
    "ig": "Invictus Gaming",
    "kc": "Karmine Corp",
}
PAIS = {
    "South Korea": "Coreia do Sul",
    "Korea": "Coreia do Sul",
    "China": "China",
    "Argentina": "Argentina",
    "Australia": "Austrália",
    "Brazil": "Brasil",
    "Canada": "Canadá",
    "Denmark": "Dinamarca",
    "France": "França",
    "Germany": "Alemanha",
    "Greece": "Grécia",
    "India": "Índia",
    "Italy": "Itália",
    "Poland": "Polônia",
    "Spain": "Espanha",
    "Sweden": "Suécia",
    "Taiwan": "Taiwan",
    "United States": "Estados Unidos",
    "Vietnam": "Vietnã",
}
POS = {"top": "top laner", "jungle": "caçador", "mid": "mid laner", "adc": "atirador", "suporte": "suporte"}

MP = "mundiais-passados/ (Leaguepedia, estatísticas de cada Worlds 2011-2025)"
U = {
    "lck26": "https://www.gosugamers.net/lol/news/79163-gen-g-are-the-2026-lck-season-champions-after-defeating-hanwha-life-esports",
    "msi26": "https://www.sheepesports.com/articles/hanwha-life-esports-crowned-msi-2026-champion-after-3-2-against-bilibili-gaming/en",
    "ewc26": "https://www.gosugamers.net/lol/news/78825-dplus-kia-crowned-2026-league-of-legends-esports-world-cup-champions-after-defeating-karmine-corp",
    "ewc26_kc": "https://www.sheepesports.com/en/lol/matches/Esports%20World%20Cup%202026_Semifinals_1",
    "pi26": "https://www.invenglobal.com/articles/27333/karmine-corp-claims-final-main-event-spot-defeats-mvk-in-play-in-final",
    "pi26_d2": "https://www.gosugamers.net/lol/news/79364-karmine-corp-sweep-mvk-esports-furia-eliminate-cloud9-kia-on-day-2-of-worlds-2026-play-ins",
    "cblol26": "https://www.techtudo.com.br/noticias/2026/10/final-do-cblol-2026-los-bate-furia-em-revanche-do-primeiro-split-e-e-campea-edjogos.ghtml",
    "cblol26_mvp": "https://maisesports.com.br/cblol-2026-curse-e-eleito-mvp-da-final-apos-titulo-da-los-contra-a-furia",
    "lec26": "https://esports.gg/news/league-of-legends/lec-summer-2026-playoffs-results/",
    "lcs26": "https://en.wikipedia.org/wiki/2026_LCS_season",
    "lpl26": "https://en.wikipedia.org/wiki/Anyone%27s_Legend",
    "lyon": "https://www.yardbarker.com/entertainment/articles/worlds_2026_lyon_preview_knocked_off_their_temporary_throne_by_strengthened_rosters/s1_17456_44399263",
    "cfo25": "https://www.e4equip.com/post/ctbc-flying-oyster-worlds-2025-quarterfinal",
    "estreantes": "https://www.gosugamers.net/lol/news/79319-league-of-legends-worlds-2026-debutants-23-players-making-their-first-worlds-appearance",
    "smash": "https://www.sheepesports.com/articles/sources-smash-set-to-join-dplus-kia/en",
    "career": "https://www.sheepesports.com/de/all/articles/lol-career-joins-dplus-kia/en",
    "caliste": "https://www.sheepesports.com/articles/lol-who-is-caliste/en",
    "kyeahoo": "https://www.esports.net/fr/actualites/lol/mercato-karmine-corp-kyeahoo-lec-2026/",
    "w2022": "https://en.wikipedia.org/wiki/2022_League_of_Legends_World_Championship",
    "msi24": "https://en.wikipedia.org/wiki/2024_Mid-Season_Invitational",
    "msi25": "https://en.wikipedia.org/wiki/2025_Mid-Season_Invitational",
    "msi23": "https://en.wikipedia.org/wiki/2023_Mid-Season_Invitational",
    "msi19": "https://en.wikipedia.org/wiki/2019_Mid-Season_Invitational",
    "faker": "https://en.wikipedia.org/wiki/Faker_(gamer)",
}


def d(texto, fontes, confianca="confirmado"):
    return {"texto": texto, "confianca": confianca, "fontes": fontes}


# Conquistas de 2026 do time atual (valem para quem está no elenco)
TIME_2026 = {
    "gen-g": d("A Gen.G, seu time, é a campeã da LCK 2026 (3–1 na Hanwha Life na final).", [U["lck26"]]),
    "hle": d("A Hanwha Life, seu time, é a campeã do MSI 2026, com virada de 3–2 sobre a BLG na final.", [U["msi26"]]),
    "dk": d("A Dplus KIA, seu time, venceu a Esports World Cup 2026 com 3–0 na Karmine Corp na final.", [U["ewc26"]]),
    "blg": d("A BLG, seu time, foi vice do MSI 2026 e só perdeu a final no quinto jogo.", [U["msi26"]]),
    "kc": d(
        "A Karmine Corp, seu time, venceu o Play-In e joga o primeiro Mundial da sua história, depois de ser vice da Esports World Cup 2026.",
        [U["pi26"], U["ewc26"]],
    ),
    "los": d(
        "Campeão do CBLOL 2026 (Etapa 2) com a LOS, 3–2 na FURIA na final de 10/10.", [U["cblol26"], U["cblol26_mvp"]]
    ),
    "g2": d("A G2, seu time, é a campeã da LEC Summer 2026 e primeira cabeça de chave da Europa.", [U["lec26"]]),
    "lyon": d("A LYON, seu time, venceu o Lock-In e o Spring da LCS 2026.", [U["lyon"], U["lcs26"]]),
    "al": d(
        "A Anyone's Legend, seu time, venceu o Split 3 da LPL 2026 e é a primeira cabeça de chave da China.",
        [U["lpl26"]],
    ),
}

# Destaques individuais que não saem das tabelas. confianca "conhecimento_previo" = fato público até meados de 2026,
# não relido nesta pesquisa; a fonte indicada é onde conferir.
EXTRA = {
    "Ruler": [
        d("Foi o MVP da final da LCK 2026.", [U["lck26"]]),
        d("Na China, pela JD Gaming, venceu o MSI de 2023.", [U["msi23"]], "conhecimento_previo"),
    ],
    "Chovy": [d("Venceu o MSI em 2024 e 2025 com a Gen.G.", [U["msi24"], U["msi25"]], "conhecimento_previo")],
    "Canyon": [d("Venceu o MSI em 2024 e 2025 com a Gen.G.", [U["msi24"], U["msi25"]], "conhecimento_previo")],
    "Kiin": [d("Venceu o MSI em 2024 e 2025 com a Gen.G.", [U["msi24"], U["msi25"]], "conhecimento_previo")],
    "Zeus": [d("Foi o MVP da final do MSI 2026.", [U["msi26"]])],
    "Faker": [d("Além dos seis Mundiais, venceu o MSI em 2016 e 2017.", [U["faker"]], "conhecimento_previo")],
    "Caps": [d("Venceu o MSI 2019 com a G2.", [U["msi19"]], "conhecimento_previo")],
    "Zeka": [
        d(
            "A DRX campeã de 2022 saiu do Play-In, uma das campanhas mais improváveis da história do torneio.",
            [U["w2022"]],
            "conhecimento_previo",
        )
    ],
    "Smash": [
        d("Foi o MVP da final da Esports World Cup 2026.", [U["ewc26"]]),
        d(
            "Fez toda a carreira de base na T1 e chegou a substituir Gumayusi no time principal no começo de 2025, antes de assinar com a Dplus KIA.",
            [U["smash"]],
        ),
    ],
    "Career": [
        d("Estreia na elite coreana em 2026, depois de passar pelas bases da DRX e da BNK FearX.", [U["career"]])
    ],
    "Caliste": [
        d("Estreou na LEC aos 18 anos, em 2025, e foi eleito o novato do ano.", [U["caliste"]]),
        d("Ele e Busio foram a dupla de destaque da KC no Play-In de 2026.", [U["pi26_d2"]]),
    ],
    "Busio": [d("Ele e Caliste foram a dupla de destaque da KC no Play-In de 2026.", [U["pi26_d2"]])],
    "kyeahoo": [d("Chegou da DRX, da Coreia, para o mid da Karmine Corp em 2026.", [U["kyeahoo"]])],
    "Curse": [d("Foi o MVP da final do CBLOL 2026; no terceiro jogo, de Wukong, fez 7/1/1.", [U["cblol26_mvp"]])],
    "Doggo": [
        d("Fez parte da CFO que chegou às quartas em 2025, a melhor campanha da região em dez anos.", [U["cfo25"]])
    ],
    "Rest": [
        d("Fez parte da CFO que chegou às quartas em 2025, a melhor campanha da região em dez anos.", [U["cfo25"]])
    ],
}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def anos_txt(a):
    a = [str(x) for x in a]
    return a[0] if len(a) == 1 else ", ".join(a[:-1]) + " e " + a[-1]


def main():
    jog = ler(os.path.join(DADOS, "soloq", "contas.json"))["jogadores"]
    J = ler(os.path.join(DADOS, "mundiais-passados", "jogadores-por-edicao.json"))["edicoes"]
    E = ler(os.path.join(DADOS, "mundiais-passados", "edicoes.json"))["edicoes"]
    ed_por_ano = {e["ano"]: e for e in E}

    # totais de carreira de todos os jogadores da história, para ranking
    tot = defaultdict(lambda: {"abates": 0, "jogos": 0, "vitorias": 0, "edicoes": 0})
    for ed in J.values():
        for r in ed["jogadores"]:
            t = tot[r["pagina"].lower()]
            t["abates"] += r["abates"]
            t["jogos"] += r["jogos"]
            t["vitorias"] += r["vitorias"]
            t["edicoes"] += 1

    def rank(page, campo):
        v = tot[page.lower()][campo]
        return 1 + sum(1 for x in tot.values() if x[campo] > v) if v else None

    os.makedirs(OUT, exist_ok=True)
    indice = []
    for p in jog:
        page = urllib.parse.unquote(p["leaguepedia"].rsplit("/wiki/", 1)[1]).replace("_", " ")
        tid = SIGLA_ID[p["sigla"]]
        nome = p["jogador"]
        eds = []
        for ano, ed in sorted(J.items()):
            for r in ed["jogadores"]:
                if r["pagina"].lower() != page.lower():
                    continue
                e = ed_por_ano[int(ano)]
                res = None
                times = r["times"]
                if (
                    e["campeao"]["time"] in times
                    and nome.lower() in [n.lower() for n in e["campeao"].get("elenco_que_jogou", [])] + [page.lower()]
                    or e["campeao"]["time"] in times
                ):
                    res = "Campeão"
                elif e["vice"]["time"] in times:
                    res = "Vice"
                elif any(s["time"] in times for s in e["semifinalistas"]):
                    res = "Semifinal"
                eds.append(
                    {
                        "ano": int(ano),
                        "time": " / ".join(times),
                        "jogos": r["jogos"],
                        "vitorias": r["vitorias"],
                        "derrotas": r["derrotas"],
                        "abates": r["abates"],
                        "mortes": r["mortes"],
                        "assistencias": r["assistencias"],
                        "kda": r["kda"],
                        "campeoes_mais_usados": r["campeoes_mais_usados"],
                        "resultado": res,
                    }
                )
        jogos = sum(e["jogos"] for e in eds)
        vit = sum(e["vitorias"] for e in eds)
        k = sum(e["abates"] for e in eds)
        m = sum(e["mortes"] for e in eds)
        a = sum(e["assistencias"] for e in eds)
        titulos = [e["ano"] for e in eds if e["resultado"] == "Campeão"]
        vices = [e["ano"] for e in eds if e["resultado"] == "Vice"]
        semis = [e["ano"] for e in eds if e["resultado"] == "Semifinal"]
        mvp = [e["ano"] for e in E if (e.get("mvp_final") or {}).get("jogador", "").lower() == nome.lower()]
        times_hist = []
        for e in eds:
            for t in e["time"].split(" / "):
                t = re.sub(r" \(.*\)$", "", t).replace("EDward", "EDward").replace("Evil Geniuses.NA", "Evil Geniuses")
                if t not in times_hist:
                    times_hist.append(t)

        destaques = []
        pais = PAIS.get(p["pais"], p["pais"])
        pos = POS.get(p["posicao"], p["posicao"])
        if not eds:
            destaques.append(d("Faz em 2026 o seu primeiro Mundial.", [MP]))
        else:
            n = len(eds)
            txt = f"Está no {n + 1}º Mundial da carreira" if n > 1 else "Está no segundo Mundial da carreira"
            if jogos >= 5:
                txt += f" (antes: {anos_txt([e['ano'] for e in eds])}), somando {jogos} jogos e {vit} vitória{'s' if vit != 1 else ''} até 2025."
            else:
                txt += f" (o primeiro foi em {eds[0]['ano']}, pela {re.sub(r' [(].*[)]$', '', eds[0]['time'])})."
            destaques.append(d(txt, [MP]))
        if titulos:
            destaques.append(d(f"Campeão mundial em {anos_txt(titulos)}.", [MP]))
        if mvp:
            destaques.append(d(f"Eleito MVP da final do Mundial em {anos_txt(mvp)}.", [MP]))
        if vices:
            destaques.append(d(f"Disputou a final em {anos_txt(vices)}, ficando com o vice.", [MP]))
        if semis:
            destaques.append(d(f"Chegou à semifinal em {anos_txt(semis)}.", [MP]))
        if len(times_hist) >= 3:
            destaques.append(d(f"Jogou Mundiais por {len(times_hist)} times diferentes: {anos_txt(times_hist)}.", [MP]))
        if eds:
            rk = rank(page, "abates")
            rj = rank(page, "jogos")
            if rk and rk <= 20:
                destaques.append(
                    d(
                        (
                            f"É o {rk}º jogador com mais abates na história dos Mundiais ({k})."
                            if rk > 1
                            else f"É o jogador com mais abates na história dos Mundiais ({k})."
                        ),
                        [MP],
                    )
                )
            if rj and rj <= 20 and rj != rk:
                destaques.append(
                    d(
                        (
                            f"É o {rj}º com mais jogos disputados em Mundiais ({jogos})."
                            if rj > 1
                            else f"É o jogador com mais jogos em Mundiais ({jogos})."
                        ),
                        [MP],
                    )
                )
            melhor = max(eds, key=lambda e: e["kda"] if e["jogos"] >= 5 else 0)
            if melhor["jogos"] >= 5 and melhor["kda"] >= 4.5:
                destaques.append(
                    d(
                        f"Seu melhor Mundial em KDA foi {melhor['ano']}: {melhor['kda']:.2f} em {melhor['jogos']} jogos.",
                        [MP],
                    )
                )
            camps = defaultdict(int)
            for e in eds:
                for c in e["campeoes_mais_usados"]:
                    camps[c] += 1
            fav = [c for c, q in sorted(camps.items(), key=lambda x: -x[1]) if q >= 2][:3]
            if fav:
                destaques.append(d(f"Campeões que mais aparecem nos seus Mundiais: {anos_txt(fav)}.", [MP]))
        if tid in TIME_2026:
            destaques.append(TIME_2026[tid])
        destaques += EXTRA.get(nome, [])

        # história curta: até 3 frases, em ordem de importância
        real = p["nome"].replace("&nbsp;", " ")
        frases = [f"{nome} ({real}, {pais}) é {pos} da {NOME_TIME[tid]}."]
        for x in [x for x in destaques if x["confianca"] == "confirmado"][:3]:
            frases.append(x["texto"])
        historia = " ".join(frases)

        fontes = sorted({f for x in destaques for f in x["fontes"]} | {p["leaguepedia"]})
        doc = {
            "id": slug(nome),
            "jogador": nome,
            "nome_real": p["nome"].replace("&nbsp;", " "),
            "pais": pais,
            "time_id": tid,
            "time": NOME_TIME[tid],
            "posicao": p["posicao"],
            "leaguepedia": p["leaguepedia"],
            "historia": historia,
            "destaques": destaques,
            "mundiais": {
                "participacoes_ate_2025": len(eds),
                "estreante_2026": not eds,
                "jogos": jogos,
                "vitorias": vit,
                "derrotas": jogos - vit,
                "winrate_pct": round(100 * vit / jogos, 1) if jogos else None,
                "abates": k,
                "mortes": m,
                "assistencias": a,
                "kda": round((k + a) / max(m, 1), 2) if jogos else None,
                "titulos": titulos,
                "vices": vices,
                "semifinais": semis,
                "mvp_final": mvp,
                "times": times_hist,
                "edicoes": eds,
            },
            "fontes": fontes,
            "atualizado_em": HOJE,
        }
        with open(f"{OUT}/{doc['id']}.json", "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2)
        indice.append(
            {
                "id": doc["id"],
                "jogador": nome,
                "time_id": tid,
                "posicao": p["posicao"],
                "titulos": len(titulos),
                "estreante": not eds,
                "arquivo": f"jogadores/{doc['id']}.json",
            }
        )
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump({"atualizado_em": HOJE, "total": len(indice), "jogadores": indice}, fh, ensure_ascii=False, indent=2)
    print("jogadores:", len(indice))


if __name__ == "__main__":
    main()
