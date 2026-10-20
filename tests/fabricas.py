"""Monta dados no formato do feed livestats para os testes."""


def jogador(ouro=500, k=0, d=0, a=0, cs=0, nivel=1):
    return {"totalGold": ouro, "kills": k, "deaths": d, "assists": a, "creepScore": cs, "level": nivel}


def time_feed(ouro=2500, abates=0, torres=0, inibidores=0, barons=0, dragoes=(), jogadores=None):
    return {
        "totalGold": ouro,
        "totalKills": abates,
        "towers": torres,
        "inhibitors": inibidores,
        "barons": barons,
        "dragons": list(dragoes),
        "participants": jogadores or [jogador() for _ in range(5)],
    }


def quadro_feed(hora, estado="in_game", azul=None, vermelho=None):
    """Quadro no formato bruto do feed livestats."""
    return {
        "rfc460Timestamp": f"2026-10-18T18:{hora}Z",
        "gameState": estado,
        "blueTeam": azul or time_feed(),
        "redTeam": vermelho or time_feed(),
    }
