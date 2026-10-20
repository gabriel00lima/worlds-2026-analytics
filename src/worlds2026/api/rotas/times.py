from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .. import consultas
from ..banco import sessao
from ..esquemas import ContagemBan, ContagemCampeao, JogadorResumo, TimeDetalhe, TimeResumo
from ..modelos import Time

router = APIRouter(prefix="/times", tags=["times"])
SessaoDep = Annotated[Session, Depends(sessao)]


def _resumo(time: Time, campanha: dict[str, tuple[int, int]]) -> dict:
    vitorias, derrotas = campanha.get(time.codigo, (0, 0))
    return {
        "codigo": time.codigo,
        "nome": time.nome,
        "liga": time.liga,
        "regiao": time.regiao,
        "vitorias": vitorias,
        "derrotas": derrotas,
    }


@router.get("", response_model=list[TimeResumo])
def listar(s: SessaoDep):
    campanha = consultas.campanha_dos_times(s)
    return [_resumo(t, campanha) for t in s.scalars(select(Time).order_by(Time.codigo))]


@router.get("/{codigo}", response_model=TimeDetalhe)
def detalhar(codigo: str, s: SessaoDep):
    time = s.scalar(select(Time).where(Time.codigo == codigo.upper()).options(selectinload(Time.jogadores)))
    if time is None:
        raise HTTPException(404, "time não encontrado")
    return {
        **_resumo(time, consultas.campanha_dos_times(s)),
        "jogadores": [JogadorResumo.model_validate(j) for j in time.jogadores],
        "campeoes": [
            ContagemCampeao(campeao=c, jogos=n, vitorias=v) for c, n, v in consultas.campeoes_do_time(s, time.codigo)
        ],
        "mais_banidos_pelo_time": [ContagemBan(campeao=c, bans=n) for c, n in consultas.bans(s, pelo_time=time.codigo)],
        "mais_banidos_contra": [
            ContagemBan(campeao=c, bans=n) for c, n in consultas.bans(s, contra_o_time=time.codigo)
        ],
    }
