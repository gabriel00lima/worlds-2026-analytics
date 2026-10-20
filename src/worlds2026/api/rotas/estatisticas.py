from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import consultas
from ..banco import sessao
from ..esquemas import EstatisticaCampeao, RankingJogador

router = APIRouter(prefix="/estatisticas", tags=["estatísticas"])
SessaoDep = Annotated[Session, Depends(sessao)]


@router.get("/jogadores", response_model=list[RankingJogador])
def ranking_jogadores(
    s: SessaoDep,
    ordenar: Literal["abates", "kda", "dano"] = "abates",
    limite: Annotated[int, Query(ge=1, le=100)] = 10,
    minimo_jogos: Annotated[int, Query(ge=1)] = 1,
):
    ranking = [
        RankingJogador(
            jogador_id=jid,
            nick=nick,
            time_codigo=time,
            jogos=n,
            abates=k,
            mortes=d,
            assistencias=a,
            kda=consultas.kda(k, d, a),
            dano_por_jogo=round(dano, 1) if dano is not None else None,
        )
        for jid, nick, time, n, k, d, a, dano in consultas.ranking_jogadores(s, minimo_jogos)
    ]
    chave = {
        "abates": lambda r: r.abates,
        "kda": lambda r: r.kda,
        "dano": lambda r: r.dano_por_jogo or 0,
    }[ordenar]
    return sorted(ranking, key=chave, reverse=True)[:limite]


@router.get("/campeoes", response_model=list[EstatisticaCampeao])
def campeoes(s: SessaoDep, limite: Annotated[int, Query(ge=1, le=200)] = 20):
    """Campeões por presença: fração dos jogos em que foram escolhidos ou banidos.

    As escolhas são contadas sobre todos os jogos e os bans só sobre os jogos que têm bans registrados.
    """
    escolhas, banidos, total, com_bans = consultas.estatisticas_campeoes(s)
    linhas = []
    for campeao in set(escolhas) | set(banidos):
        n, v = escolhas.get(campeao, (0, 0))
        b = banidos.get(campeao, 0)
        linhas.append(
            EstatisticaCampeao(
                campeao=campeao,
                escolhas=n,
                vitorias=v,
                bans=b,
                presenca=round(min(1, (n / total if total else 0) + (b / com_bans if com_bans else 0)), 3),
            )
        )
    return sorted(linhas, key=lambda x: (-x.presenca, x.campeao))[:limite]
