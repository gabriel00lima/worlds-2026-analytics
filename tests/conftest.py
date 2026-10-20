import os

import pytest
from sqlalchemy import StaticPool, create_engine

from worlds2026 import config


@pytest.fixture(autouse=True)
def cache_temporario(tmp_path, monkeypatch):
    """Nenhum teste escreve no cache real do projeto."""
    monkeypatch.setattr(config, "CACHE", tmp_path / "cache")
    monkeypatch.setattr(config, "CACHE_JOGOS", tmp_path / "cache" / "jogos")
    monkeypatch.setattr(config, "CACHE_IMAGENS", tmp_path / "cache" / "img")
    monkeypatch.setattr(config, "SOLOQ_PARTIDAS", tmp_path / "soloq-partidas.json")
    config.preparar_pastas()
    return tmp_path / "cache"


@pytest.fixture
def meta_jogo():
    def lado(time_id, inicio):
        return {
            "esportsTeamId": time_id,
            "participantMetadata": [
                {
                    "participantId": inicio + i,
                    "esportsPlayerId": f"p{inicio + i}",
                    "summonerName": f"TM Jogador{inicio + i}",
                    "championId": c,
                    "role": r,
                }
                for i, (c, r) in enumerate(
                    zip(
                        ["Gnar", "Vi", "Ahri", "Jinx", "Nami"],
                        ["top", "jungle", "mid", "bottom", "support"],
                        strict=True,
                    )
                )
            ],
        }

    return {"patchVersion": "16.20.123", "blueTeamMetadata": lado("azul", 1), "redTeamMetadata": lado("verm", 6)}


@pytest.fixture
def engine():
    """SQLite em memória, ou o banco de TEST_DATABASE_URL (o CI usa um PostgreSQL)."""
    url = os.environ.get("TEST_DATABASE_URL")
    if url:
        engine = create_engine(url)
    else:
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    yield engine
    engine.dispose()
