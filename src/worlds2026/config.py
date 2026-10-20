"""Caminhos, identificadores e chaves usados pela coleta."""

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

DADOS = RAIZ / "data"
CURIOSIDADES = DADOS / "curiosidades"
CONTAS_SOLOQ = DADOS / "soloq" / "contas.json"
# Última solo queue baixada. Fica versionada para o site manter os dados quando a coleta roda sem chave da Riot.
SOLOQ_PARTIDAS = DADOS / "soloq" / "partidas.json"

CACHE = RAIZ / ".cache"
CACHE_JOGOS = CACHE / "jogos"
CACHE_IMAGENS = CACHE / "img"

WEB = RAIZ / "web"
SITE = RAIZ / "docs" / "index.html"
# Narração gravada por scripts/gerar_audio.py: um mp3 por jogo e o índice com o tempo de cada fala.
AUDIO = RAIZ / "docs" / "audio"

LIGA_WORLDS = "98767975604431411"
TORNEIO_WORLDS_2026 = "115660540725177488"

# Chave pública que o próprio lolesports.com envia do navegador.
LOLESPORTS_API_KEY = os.environ.get("LOLESPORTS_API_KEY", "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z")
RIOT_API_KEY = os.environ.get("RIOT_API_KEY")


def preparar_pastas() -> None:
    for pasta in (CACHE_JOGOS, CACHE_IMAGENS):
        pasta.mkdir(parents=True, exist_ok=True)
