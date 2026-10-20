"""Carrega no banco os dados gerados pela coleta (.cache/dados.json)."""

import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Engine, delete
from sqlalchemy.orm import Session

from .. import config
from ..arquivos import ler_json
from .banco import Base
from .modelos import Ban, Jogador, Jogo, Participacao, Partida, PartidaSoloq, Time

log = logging.getLogger(__name__)

Json = dict[str, Any]
TABELAS = (PartidaSoloq, Ban, Participacao, Jogo, Partida, Jogador, Time)


def _data(texto: str) -> datetime:
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))


def _elo(soloq: Json | None) -> tuple[str | None, int | None]:
    elo = (soloq or {}).get("elo")
    if not elo:
        return None, None
    return f"{elo['tier']} {elo['rank']}".title(), elo.get("leaguePoints")


def times_e_jogadores(dados: Json) -> list[Time]:
    times = []
    for t in dados["times"].values():
        time = Time(codigo=t["codigo"], id_api=t["id"], nome=t["nome"], liga=t.get("liga"), regiao=t.get("regiao"))
        for ordem, pl in enumerate(t["jogadores"]):
            elo, pdl = _elo(pl.get("soloq"))
            jogador = Jogador(
                id=pl["id"],
                nick=pl["nick"],
                nome=pl.get("nome") or None,
                rota=pl["rota"],
                titular=pl["titular"],
                ordem=ordem,
                elo=elo,
                pdl=pdl,
            )
            for fim, _dur, campeao, venceu, k, d, a, cs in (pl.get("soloq") or {}).get("partidas", []):
                jogador.partidas_soloq.append(
                    PartidaSoloq(
                        fim=datetime.fromtimestamp(fim / 1000, timezone.utc),
                        campeao=campeao,
                        venceu=venceu,
                        abates=k,
                        mortes=d,
                        assistencias=a,
                        cs=cs,
                    )
                )
            time.jogadores.append(jogador)
        times.append(time)
    return times


def partida(p: Json) -> Partida:
    a, b = p["times"]
    vencedor = next((t["codigo"] for t in p["times"] if t.get("resultado") == "win"), None)
    return Partida(
        id=p["id"],
        inicio=_data(p["inicio"]),
        estado=p["estado"],
        fase=p["fase"],
        bloco=p.get("bloco"),
        melhor_de=p["melhorDe"],
        time_a=a["codigo"],
        time_b=b["codigo"],
        vitorias_a=a.get("vitorias"),
        vitorias_b=b.get("vitorias"),
        vencedor=vencedor,
    )


def jogo(j: Json, codigo_do_id: dict[str, str]) -> Jogo:
    azul, vermelho = codigo_do_id.get(j["timeAzul"], "?"), codigo_do_id.get(j["timeVermelho"], "?")
    vencedor = azul if j["vencedor"] == "blue" else vermelho
    novo = Jogo(
        id=j["id"],
        partida_id=j["partida"],
        numero=j["numero"],
        patch=j["patch"],
        duracao=j["duracao"],
        time_azul=azul,
        time_vermelho=vermelho,
        vencedor=vencedor,
    )
    final = j["serie"][-1][3]  # [ouro, k, d, a, cs, nível] dos 10 jogadores no fim do jogo
    for x in j["jogadores"]:
        ouro, k, d, a, cs, _nivel = final[x["pid"] - 1]
        time = azul if x["lado"] == "blue" else vermelho
        novo.participacoes.append(
            Participacao(
                jogador_id=x.get("jogadorId"),
                nick=x["nick"],
                time_codigo=time,
                lado=x["lado"],
                rota=x["rota"],
                campeao=x["campeao"],
                venceu=time == vencedor,
                abates=k,
                mortes=d,
                assistencias=a,
                ouro=ouro,
                cs=cs,
                dano_total=x.get("danoTotal"),
            )
        )
    for lado, time in (("blue", azul), ("red", vermelho)):
        for campeao in ((j.get("lp") or {}).get("bans") or {}).get(lado, []):
            novo.bans.append(Ban(time_codigo=time, campeao=campeao))
    return novo


def carregar(engine: Engine, dados: Json) -> dict[str, int]:
    """Recria o conteúdo do banco a partir dos dados da coleta. Devolve quantas linhas entraram por tabela."""
    Base.metadata.create_all(engine)
    codigo_do_id = {t["id"]: t["codigo"] for t in dados["times"].values()}
    with Session(engine) as s, s.begin():
        for tabela in TABELAS:
            s.execute(delete(tabela))
        s.add_all(times_e_jogadores(dados))
        s.add_all(partida(p) for p in dados["partidas"])
        s.add_all(jogo(j, codigo_do_id) for j in dados["jogos"])
    with Session(engine) as s:
        return {t.__tablename__: s.query(t).count() for t in reversed(TABELAS)}


def carregar_do_cache(engine: Engine) -> dict[str, int]:
    dados = ler_json(config.CACHE / "dados.json")
    if dados is None:
        raise FileNotFoundError("rode a coleta antes: python -m worlds2026")
    contagem = carregar(engine, dados)
    log.info("banco carregado: %s", ", ".join(f"{n} {t}" for t, n in contagem.items()))
    return contagem
