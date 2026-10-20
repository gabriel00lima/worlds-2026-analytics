from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import consultas
from ..banco import sessao
from ..esquemas import ContagemCampeao, Desempenho, JogadorDetalhe, JogadorResumo
from ..modelos import Jogador

router = APIRouter(prefix="/jogadores", tags=["jogadores"])
SessaoDep = Annotated[Session, Depends(sessao)]


@router.get("", response_model=list[JogadorResumo])
def buscar(s: SessaoDep, nick: Annotated[str | None, Query(description="parte do nick")] = None):
    q = select(Jogador).order_by(Jogador.time_codigo, Jogador.ordem)
    if nick:
        q = q.where(Jogador.nick.ilike(f"%{nick}%"))
    return s.scalars(q).all()


def _desempenho(s: Session, jogador_id: str) -> Desempenho | None:
    jogos, vitorias, k, d, a, cs, segundos = consultas.totais_do_jogador(s, jogador_id)
    if not jogos:
        return None
    return Desempenho(
        jogos=jogos,
        vitorias=vitorias,
        abates=k,
        mortes=d,
        assistencias=a,
        kda=consultas.kda(k, d, a),
        abates_por_jogo=round(k / jogos, 2),
        cs_por_minuto=round(cs / (segundos / 60), 1) if segundos else None,
    )


@router.get("/{jogador_id}", response_model=JogadorDetalhe)
def detalhar(jogador_id: str, s: SessaoDep):
    jogador = s.get(Jogador, jogador_id)
    if jogador is None:
        raise HTTPException(404, "jogador não encontrado")

    def contagem(linhas):
        return [ContagemCampeao(campeao=c, jogos=n, vitorias=v) for c, n, v in linhas]

    return {
        **JogadorResumo.model_validate(jogador).model_dump(),
        "torneio": _desempenho(s, jogador_id),
        "campeoes_torneio": contagem(consultas.campeoes_do_jogador_no_torneio(s, jogador_id)),
        "campeoes_soloq": contagem(consultas.campeoes_do_jogador_na_soloq(s, jogador_id)),
    }
