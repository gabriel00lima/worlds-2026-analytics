"""Conexão com o banco. Usa SQLite por padrão; DATABASE_URL aponta para outro banco."""

import os
from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .. import config

URL_PADRAO = f"sqlite:///{config.CACHE / 'worlds2026.db'}"


class Base(DeclarativeBase):
    pass


def criar_engine(url: str | None = None) -> Engine:
    url = url or os.environ.get("DATABASE_URL", URL_PADRAO)
    if url.startswith("sqlite:///"):
        config.CACHE.mkdir(parents=True, exist_ok=True)
    return create_engine(url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {})


engine = criar_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def sessao() -> Iterator[Session]:
    """Dependência do FastAPI: uma sessão por requisição."""
    with SessionLocal() as s:
        yield s
