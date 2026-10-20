"""Formatos das respostas da API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Modelo(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PartidaResumo(Modelo):
    id: str
    inicio: datetime
    estado: str
    fase: str
    bloco: str | None
    melhor_de: int
    time_a: str
    time_b: str
    vitorias_a: int | None
    vitorias_b: int | None
    vencedor: str | None


class LinhaJogador(Modelo):
    jogador_id: str | None
    nick: str
    time_codigo: str
    rota: str
    campeao: str
    abates: int
    mortes: int
    assistencias: int
    ouro: int
    cs: int
    dano_total: int | None


class BanSaida(Modelo):
    time_codigo: str
    campeao: str


class JogoSaida(Modelo):
    id: str
    numero: int
    patch: str
    duracao: int
    time_azul: str
    time_vermelho: str
    vencedor: str
    participacoes: list[LinhaJogador]
    bans: list[BanSaida]


class PartidaDetalhe(PartidaResumo):
    jogos: list[JogoSaida]


class JogadorResumo(Modelo):
    id: str
    nick: str
    nome: str | None
    rota: str
    titular: bool
    time_codigo: str
    elo: str | None
    pdl: int | None


class TimeResumo(Modelo):
    codigo: str
    nome: str
    liga: str | None
    regiao: str | None
    vitorias: int = 0
    derrotas: int = 0


class ContagemCampeao(BaseModel):
    campeao: str
    jogos: int
    vitorias: int


class ContagemBan(BaseModel):
    campeao: str
    bans: int


class TimeDetalhe(TimeResumo):
    jogadores: list[JogadorResumo]
    campeoes: list[ContagemCampeao]
    mais_banidos_pelo_time: list[ContagemBan]
    mais_banidos_contra: list[ContagemBan]


class Desempenho(BaseModel):
    jogos: int
    vitorias: int
    abates: int
    mortes: int
    assistencias: int
    kda: float
    abates_por_jogo: float
    cs_por_minuto: float | None


class JogadorDetalhe(JogadorResumo):
    torneio: Desempenho | None
    campeoes_torneio: list[ContagemCampeao]
    campeoes_soloq: list[ContagemCampeao]


class RankingJogador(BaseModel):
    jogador_id: str | None
    nick: str
    time_codigo: str
    jogos: int
    abates: int
    mortes: int
    assistencias: int
    kda: float
    dano_por_jogo: float | None


class EstatisticaCampeao(BaseModel):
    campeao: str
    escolhas: int
    vitorias: int
    bans: int
    presenca: float
