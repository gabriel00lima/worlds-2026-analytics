"""Consultas de agregação usadas pelas rotas."""

from typing import Any

from sqlalchemy import ColumnElement, Select, case, func, select
from sqlalchemy.orm import Session

from .modelos import Ban, Jogo, Participacao, PartidaSoloq


def kda(abates: int, mortes: int, assistencias: int) -> float:
    return round((abates + assistencias) / max(1, mortes), 2)


def _vitorias(coluna: Any) -> ColumnElement[int]:
    return func.sum(case((coluna, 1), else_=0))


def campeoes_do_jogador_no_torneio(s: Session, jogador_id: str) -> list[tuple[str, int, int]]:
    q = (
        select(Participacao.campeao, func.count(), _vitorias(Participacao.venceu))
        .where(Participacao.jogador_id == jogador_id)
        .group_by(Participacao.campeao)
        .order_by(func.count().desc(), Participacao.campeao)
    )
    return [(c, n, v) for c, n, v in s.execute(q)]


def campeoes_do_jogador_na_soloq(s: Session, jogador_id: str) -> list[tuple[str, int, int]]:
    q = (
        select(PartidaSoloq.campeao, func.count(), _vitorias(PartidaSoloq.venceu))
        .where(PartidaSoloq.jogador_id == jogador_id)
        .group_by(PartidaSoloq.campeao)
        .order_by(func.count().desc(), PartidaSoloq.campeao)
    )
    return [(c, n, v) for c, n, v in s.execute(q)]


def totais_do_jogador(s: Session, jogador_id: str):
    q = (
        select(
            func.count(),
            _vitorias(Participacao.venceu),
            func.sum(Participacao.abates),
            func.sum(Participacao.mortes),
            func.sum(Participacao.assistencias),
            func.sum(Participacao.cs),
            func.sum(Jogo.duracao),
        )
        .join(Jogo)
        .where(Participacao.jogador_id == jogador_id)
    )
    return s.execute(q).one()


def campeoes_do_time(s: Session, codigo: str) -> list[tuple[str, int, int]]:
    q = (
        select(Participacao.campeao, func.count(), _vitorias(Participacao.venceu))
        .where(Participacao.time_codigo == codigo)
        .group_by(Participacao.campeao)
        .order_by(func.count().desc(), Participacao.campeao)
        .limit(10)
    )
    return [(c, n, v) for c, n, v in s.execute(q)]


def bans(s: Session, pelo_time: str | None = None, contra_o_time: str | None = None, limite: int = 5):
    q: Select = select(Ban.campeao, func.count().label("n")).group_by(Ban.campeao)
    if pelo_time:
        q = q.where(Ban.time_codigo == pelo_time)
    if contra_o_time:
        q = q.join(Jogo).where(
            Ban.time_codigo != contra_o_time,
            (Jogo.time_azul == contra_o_time) | (Jogo.time_vermelho == contra_o_time),
        )
    return [tuple(r) for r in s.execute(q.order_by(func.count().desc(), Ban.campeao).limit(limite))]


def campanha_dos_times(s: Session) -> dict[str, tuple[int, int]]:
    """Vitórias e derrotas de cada time, contando jogos (não séries)."""
    q = select(
        Participacao.time_codigo,
        func.count(func.distinct(case((Participacao.venceu, Participacao.jogo_id)))),
        func.count(func.distinct(case((~Participacao.venceu, Participacao.jogo_id)))),
    ).group_by(Participacao.time_codigo)
    return {codigo: (v, d) for codigo, v, d in s.execute(q)}


def ranking_jogadores(s: Session, minimo_jogos: int):
    q = (
        select(
            Participacao.jogador_id,
            func.max(Participacao.nick),
            func.max(Participacao.time_codigo),
            func.count(),
            func.sum(Participacao.abates),
            func.sum(Participacao.mortes),
            func.sum(Participacao.assistencias),
            func.avg(Participacao.dano_total),
        )
        .group_by(Participacao.jogador_id)
        .having(func.count() >= minimo_jogos)
    )
    return s.execute(q).all()


def estatisticas_campeoes(s: Session):
    q = select(Participacao.campeao, func.count(), _vitorias(Participacao.venceu)).group_by(Participacao.campeao)
    escolhas = {c: (n, v) for c, n, v in s.execute(q)}
    banidos = {c: n for c, n in s.execute(select(Ban.campeao, func.count()).group_by(Ban.campeao))}
    total_jogos = s.scalar(select(func.count()).select_from(Jogo)) or 0
    return escolhas, banidos, total_jogos
