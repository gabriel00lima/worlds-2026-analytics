from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from ..banco import sessao
from ..esquemas import PartidaDetalhe, PartidaResumo
from ..modelos import Jogo, Partida

router = APIRouter(prefix="/partidas", tags=["partidas"])
SessaoDep = Annotated[Session, Depends(sessao)]


@router.get("", response_model=list[PartidaResumo])
def listar(
    s: SessaoDep,
    fase: Annotated[str | None, Query(description="play_ins, swiss ou knockouts")] = None,
    estado: Annotated[str | None, Query(description="unstarted, inProgress ou completed")] = None,
    time: Annotated[str | None, Query(description="sigla do time, como T1")] = None,
):
    q = select(Partida).order_by(Partida.inicio)
    if fase:
        q = q.where(Partida.fase == fase)
    if estado:
        q = q.where(Partida.estado == estado)
    if time:
        q = q.where(or_(Partida.time_a == time.upper(), Partida.time_b == time.upper()))
    return s.scalars(q).all()


@router.get("/{partida_id}", response_model=PartidaDetalhe)
def detalhar(partida_id: str, s: SessaoDep):
    q = (
        select(Partida)
        .where(Partida.id == partida_id)
        .options(
            selectinload(Partida.jogos).selectinload(Jogo.participacoes),
            selectinload(Partida.jogos).selectinload(Jogo.bans),
        )
    )
    partida = s.scalar(q)
    if partida is None:
        raise HTTPException(404, "partida não encontrada")
    return partida
