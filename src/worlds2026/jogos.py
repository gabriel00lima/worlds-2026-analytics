"""Busca e processa cada jogo, guardando o resultado em cache."""

import logging
from pathlib import Path
from typing import Any

from . import config
from .arquivos import ler_json, salvar_json
from .fontes import livestats
from .processamento import montar_jogo
from .tempo import ts

log = logging.getLogger(__name__)

Json = dict[str, Any]


def caminho_cache(jogo_id: str) -> Path:
    return config.CACHE_JOGOS / f"{jogo_id}.json"


def jogo_em_cache(jogo_id: str) -> Json | None:
    return ler_json(caminho_cache(jogo_id))


def processar_jogo(jogo_id: str, partida_id: str, numero: int) -> Json | None:
    if (jogo := jogo_em_cache(jogo_id)) is not None:
        return jogo
    primeira = livestats.janela(jogo_id)
    if not primeira or not primeira.get("frames"):
        return None
    inicio = livestats.arredondar_10s(ts(primeira["frames"][0]["rfc460Timestamp"]))
    quadros = livestats.baixar_quadros(jogo_id, inicio)
    if not quadros:
        return None
    finais = livestats.detalhes_finais(jogo_id, quadros[-1])
    jogo = montar_jogo(jogo_id, partida_id, numero, primeira["gameMetadata"], quadros, finais)
    salvar_json(caminho_cache(jogo_id), jogo)
    return jogo
