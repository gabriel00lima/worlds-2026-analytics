"""Transforma os quadros brutos do feed num jogo pronto para o site.

O feed só informa o estado acumulado (ouro, abates, torres...) a cada 10 s.
Os lances são deduzidos comparando um quadro com o anterior.
"""

from typing import Any

from .tempo import ts

Json = dict[str, Any]
LADOS = ("blueTeam", "redTeam")


def resumo_quadro(quadro: Json) -> Json:
    """Estado de cada time e [ouro, k, d, a, cs, nível] de cada jogador."""
    out = {}
    for lado in LADOS:
        t = quadro[lado]
        out[lado] = {
            "ouro": t["totalGold"],
            "abates": t["totalKills"],
            "torres": t["towers"],
            "inibidores": t["inhibitors"],
            "barons": t["barons"],
            "dragoes": list(t["dragons"]),
            "p": [
                [p["totalGold"], p["kills"], p["deaths"], p["assists"], p["creepScore"], p["level"]]
                for p in t["participants"]
            ],
        }
    return out


def relogio_de_jogo(quadros: list[Json]) -> list[tuple[float, Json]]:
    """Associa cada quadro ao tempo de jogo, sem contar as pausas."""
    amostras: list[tuple[float, Json]] = []
    relogio = 0.0
    anterior = None
    for f in quadros:
        t = ts(f["rfc460Timestamp"])
        if anterior is not None and anterior[1] == "in_game":
            relogio += (t - anterior[0]).total_seconds()
        anterior = (t, f["gameState"])
        amostras.append((relogio, f))
    return amostras


def diferencas(a: Json, b: Json, seg: int) -> list[Json]:
    """Lances entre dois resumos seguidos: abates (com autores e vítimas), dragões, torres, inibidores e Barões."""
    eventos = []
    for lado, outro in (("blueTeam", "redTeam"), ("redTeam", "blueTeam")):
        cor = "blue" if lado == "blueTeam" else "red"
        antes, depois = a[lado], b[lado]
        n = depois["abates"] - antes["abates"]
        if n > 0:
            matadores = [i for i in range(5) if depois["p"][i][1] > antes["p"][i][1]]
            mortos = [i for i in range(5) if b[outro]["p"][i][2] > a[outro]["p"][i][2]]
            base, base_vitima = (0, 5) if lado == "blueTeam" else (5, 0)
            eventos.append(
                {
                    "s": seg,
                    "tipo": "abate",
                    "lado": cor,
                    "n": n,
                    "por": [base + i + 1 for i in matadores],
                    "vitimas": [base_vitima + i + 1 for i in mortos],
                }
            )
        for dragao in depois["dragoes"][len(antes["dragoes"]) :]:
            eventos.append({"s": seg, "tipo": "dragao", "lado": cor, "dragao": dragao})
        for campo, tipo in (("torres", "torre"), ("inibidores", "inibidor"), ("barons", "barao")):
            eventos += [{"s": seg, "tipo": tipo, "lado": cor}] * (depois[campo] - antes[campo])
    return eventos


def compactar(serie: list[Json]) -> list[list[Any]]:
    """Reduz a série a um ponto a cada ~30 s, sempre mantendo o último."""
    out, ultimo = [], -999
    for x in serie:
        if x["s"] - ultimo >= 30 or x is serie[-1]:
            out.append([x["s"], x["blueTeam"]["ouro"], x["redTeam"]["ouro"], x["blueTeam"]["p"] + x["redTeam"]["p"]])
            ultimo = x["s"]
    return out


def estimar_vencedor(final: Json) -> str:
    """O feed não diz quem venceu: decide por inibidores, depois torres e ouro."""

    def peso(t: Json) -> float:
        return t["inibidores"] * 10 + t["torres"] + t["ouro"] / 10000

    return "blue" if peso(final["blueTeam"]) >= peso(final["redTeam"]) else "red"


def nick_sem_sigla(nome: str) -> str:
    """O feed manda "T1 Faker"; o site usa só "Faker"."""
    return nome.strip().split(" ", 1)[-1].strip()


def jogadores(meta: Json, finais: dict[int, Json]) -> list[Json]:
    out = []
    for lado, md in (("blue", meta["blueTeamMetadata"]), ("red", meta["redTeamMetadata"])):
        for pm in md["participantMetadata"]:
            d = finais.get(pm["participantId"], {})
            out.append(
                {
                    "pid": pm["participantId"],
                    "lado": lado,
                    "jogadorId": pm.get("esportsPlayerId"),
                    "nick": nick_sem_sigla(pm["summonerName"]),
                    "campeao": pm["championId"],
                    "rota": pm["role"],
                    "dano": d.get("championDamageShare"),
                    "kp": d.get("killParticipation"),
                    "wards": d.get("wardsPlaced"),
                    "wardsDestruidas": d.get("wardsDestroyed"),
                    "itens": d.get("items", []),
                    "runas": (d.get("perkMetadata") or {}).get("perks", [])[:1],
                }
            )
    return out


def montar_jogo(
    jogo_id: str, partida_id: str, numero: int, meta: Json, quadros: list[Json], finais: dict[int, Json]
) -> Json:
    amostras = relogio_de_jogo(quadros)
    # o feed começa com alguns segundos de carregamento: o jogo começa no primeiro ouro > 0
    inicio = next((s for s, f in amostras if f["blueTeam"]["totalGold"] > 0), 0)
    duracao = amostras[-1][0] - inicio

    serie: list[Json] = []
    eventos: list[Json] = []
    anterior = None
    for s, f in amostras:
        seg = max(0, round(s - inicio))
        atual = resumo_quadro(f)
        if anterior:
            eventos += diferencas(anterior, atual, seg)
        anterior = atual
        if not serie or seg - serie[-1]["s"] >= 10 or f is amostras[-1][1]:
            serie.append({"s": seg, **atual})

    return {
        "id": jogo_id,
        "partida": partida_id,
        "numero": numero,
        "patch": ".".join(meta.get("patchVersion", "").split(".")[:2]),
        "timeAzul": meta["blueTeamMetadata"]["esportsTeamId"],
        "timeVermelho": meta["redTeamMetadata"]["esportsTeamId"],
        "duracao": round(duracao),
        "vencedor": estimar_vencedor(serie[-1]),
        "jogadores": jogadores(meta, finais),
        "serie": compactar(serie),
        "eventos": eventos,
    }
