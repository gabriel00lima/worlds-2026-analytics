"""Resumo dos Mundiais de 2011 a 2025, para o site comparar 2026 com a história.

Lê data/mundiais-passados (campeões por edição, recordes, histórico dos times) e
data/curiosidades/jogadores (carreira de cada jogador em Mundiais).
"""

import re
from typing import Any

from . import config
from .arquivos import ler_json
from .curiosidades import sigla

Json = dict[str, Any]
CAMPOS_CARREIRA = (
    "participacoes_ate_2025",
    "estreante_2026",
    "jogos",
    "vitorias",
    "abates",
    "kda",
    "titulos",
    "vices",
    "semifinais",
    "mvp_final",
)
CAMPOS_TIME = ("participacoes", "titulos", "finais", "jogos", "vitorias")
RECORDES = ("jogadores_mais_abates", "jogadores_mais_jogos", "jogadores_mais_vitorias", "jogadores_mais_titulos")


def chave(nome: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (nome or "").lower())


def jogadores() -> dict[str, Json]:
    out = {}
    for arq in sorted((config.CURIOSIDADES / "jogadores").glob("*.json")):
        d = ler_json(arq)
        m = d.get("mundiais") or {}
        out[chave(d.get("jogador"))] = {
            "historia": d.get("historia"),
            "m": {k: m.get(k) for k in CAMPOS_CARREIRA},
            "ed": [
                [
                    e["ano"],
                    e.get("time"),
                    e.get("jogos"),
                    e.get("vitorias"),
                    e.get("kda"),
                    e.get("resultado"),
                    e.get("campeoes_mais_usados") or [],
                ]
                for e in m.get("edicoes") or []
            ],
        }
    return out


def times(historico: Json) -> dict[str, Json]:
    return {
        sigla(time_id): {
            **{k: t.get(k) for k in CAMPOS_TIME},
            "ed": [
                [e["ano"], e.get("nome"), e.get("jogos"), e.get("vitorias"), e.get("resultado_top4")]
                for e in t.get("edicoes") or []
            ],
        }
        for time_id, t in historico["times"].items()
    }


def campeoes(edicoes: Json, camp_en: Json) -> dict[str, Json]:
    """Escolhas, bans, presença e vitórias de cada campeão por edição, indexados pelo id do Data Dragon."""
    por_nome = {chave(c["name"]): k for k, c in camp_en.items()}
    out: dict[str, Json] = {}
    for ano, e in sorted(edicoes.items()):
        for c in e.get("campeoes") or []:
            k = por_nome.get(chave(c["campeao"]))
            if k:
                out.setdefault(k, {"ed": []})["ed"].append(
                    [int(ano), c.get("picks") or 0, c.get("bans") or 0, c.get("presenca_pct"), c.get("vitorias") or 0]
                )
    return out


def ler_historia(camp_en: Json) -> Json:
    base = config.MUNDIAIS_PASSADOS
    if not base.is_dir():
        return {"jogadores": {}, "times": {}, "campeoes": {}, "recordes": {}}
    edicoes = ler_json(base / "campeoes-por-edicao.json")["edicoes"]
    recordes = ler_json(base / "recordes.json")["recordes"]
    return {
        "jogadores": jogadores(),
        "times": times(ler_json(base / "times-2026-historico.json")),
        "campeoes": campeoes(edicoes, camp_en),
        "recordes": {k: recordes.get(k, [])[:10] for k in RECORDES},
        "jogosEd": {int(ano): e.get("jogos_total") for ano, e in edicoes.items()},
    }
