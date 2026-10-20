"""Feed de estatísticas ao vivo: o estado de cada jogo em janelas de 10 segundos."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any

from .. import rede
from ..tempo import iso, ts

FEED = "https://feed.lolesports.com/livestats/v1"
LOTE = 48
MAX_JANELAS = 600

Json = dict[str, Any]


def janela(jogo_id: str, quando: datetime | None = None, rota: str = "window") -> Json | None:
    url = f"{FEED}/{rota}/{jogo_id}"
    if quando:
        url += f"?startingTime={iso(quando)}"
    return rede.baixar_json(url)


def arredondar_10s(t: datetime) -> datetime:
    t = t.replace(microsecond=0)
    return t - timedelta(seconds=t.second % 10)


def baixar_quadros(jogo_id: str, inicio: datetime) -> list[Json]:
    """Todos os quadros do jogo, em ordem, até o primeiro com estado "finished".

    As janelas são buscadas em lotes paralelos até um lote inteiro vir vazio
    ou o jogo terminar.
    """
    quadros: dict[str, Json] = {}
    k, fim = 0, False
    with ThreadPoolExecutor(24) as ex:
        while not fim and k < MAX_JANELAS:
            lote = range(k, k + LOTE)
            respostas = list(ex.map(lambda i: janela(jogo_id, inicio + timedelta(seconds=10 * i)), lote))
            vazios = 0
            for r in respostas:
                fs = (r or {}).get("frames") or []
                if not fs:
                    vazios += 1
                    continue
                for f in fs:
                    quadros[f["rfc460Timestamp"]] = f
                fim = fim or any(f["gameState"] == "finished" for f in fs)
            fim = fim or vazios == LOTE
            k += LOTE

    ordenados = [quadros[t] for t in sorted(quadros)]
    for i, f in enumerate(ordenados):
        if f["gameState"] == "finished":
            return ordenados[: i + 1]
    return ordenados


def detalhes_finais(jogo_id: str, ultimo: Json) -> dict[int, Json]:
    """Estatísticas do último quadro por participante (dano, visão, itens, runas)."""
    d = janela(jogo_id, arredondar_10s(ts(ultimo["rfc460Timestamp"])), "details")
    participantes = ((d or {}).get("frames") or [{}])[-1].get("participants", [])
    return {p["participantId"]: p for p in participantes}
