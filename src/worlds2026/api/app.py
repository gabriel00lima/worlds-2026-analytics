"""Aplicação FastAPI. Rodar com: python -m worlds2026 api"""

from fastapi import FastAPI

from .. import __version__
from .rotas import estatisticas, jogadores, partidas, times


def criar_app() -> FastAPI:
    app = FastAPI(
        title="Worlds 2026 API",
        version=__version__,
        description="Partidas, times, jogadores e estatísticas do Mundial de League of Legends 2026.",
    )
    for modulo in (partidas, times, jogadores, estatisticas):
        app.include_router(modulo.router)

    @app.get("/saude", tags=["infra"])
    def saude() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = criar_app()
