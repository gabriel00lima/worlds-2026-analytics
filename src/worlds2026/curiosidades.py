"""Lê o histórico e as curiosidades de data/curiosidades."""

from typing import Any

from . import config
from .arquivos import ler_json

# ids usados nos arquivos de curiosidades que diferem da sigla oficial do time
SIGLA_POR_ID = {"gen-g": "GEN", "tl": "TLAW", "koi": "MKOI"}
CAMPOS_TIME = ("seed", "como_classificou", "titulos_mundiais", "melhor_mundial", "curiosidades")
CAMPOS_CONFRONTO = ("manchete", "resumo_historico", "historico", "curiosidades")


def sigla(time_id: str) -> str:
    return SIGLA_POR_ID.get(time_id, time_id.upper())


def ler_curiosidades() -> dict[str, Any]:
    out: dict[str, Any] = {"times": {}, "confrontos": []}
    base = config.CURIOSIDADES
    if not base.is_dir():
        return out
    for arq in sorted((base / "times").glob("*.json")):
        d = ler_json(arq)
        out["times"][sigla(d["id"])] = {k: d.get(k) for k in CAMPOS_TIME}
    for arq in sorted((base / "confrontos").glob("*.json")):
        d = ler_json(arq)
        times = sorted([sigla(d["time_a"]["id"]), sigla(d["time_b"]["id"])])
        out["confrontos"].append({"times": times, **{k: d.get(k) for k in CAMPOS_CONFRONTO}})
    return out
