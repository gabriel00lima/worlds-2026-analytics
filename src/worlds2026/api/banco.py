"""Conexão com o banco. Usa SQLite por padrão; DATABASE_URL aponta para outro banco."""

import os
from collections.abc import Iterator
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .. import config

URL_PADRAO = f"sqlite:///{config.CACHE / 'worlds2026.db'}"
MIGRACOES = Path(__file__).parent / "migracoes"


class Base(DeclarativeBase):
    pass


def criar_engine(url: str | None = None) -> Engine:
    url = url or os.environ.get("DATABASE_URL", URL_PADRAO)
    if url.startswith("sqlite:///"):
        config.CACHE.mkdir(parents=True, exist_ok=True)
    return create_engine(url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {})


def migrar(engine: Engine) -> None:
    """Aplica as migrações que faltam (alembic upgrade head)."""
    cfg = Config()
    cfg.set_main_option("script_location", str(MIGRACOES))
    with engine.begin() as conn:
        cfg.attributes["conexao"] = conn
        command.upgrade(cfg, "head")


engine = criar_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def sessao() -> Iterator[Session]:
    """Dependência do FastAPI: uma sessão por requisição."""
    with SessionLocal() as s:
        yield s
