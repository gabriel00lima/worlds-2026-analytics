"""Tabelas do banco."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .banco import Base


class DataUTC(TypeDecorator[datetime]):
    """Guarda em UTC e devolve com fuso, mesmo no SQLite, que não guarda fuso horário."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, valor, dialect):
        return valor.astimezone(timezone.utc).replace(tzinfo=None) if valor else valor

    def process_result_value(self, valor, dialect):
        return valor.replace(tzinfo=timezone.utc) if valor else valor


class Time(Base):
    __tablename__ = "times"

    codigo: Mapped[str] = mapped_column(String(10), primary_key=True)
    id_api: Mapped[str] = mapped_column(String(30), unique=True)
    nome: Mapped[str]
    liga: Mapped[str | None]
    regiao: Mapped[str | None]

    jogadores: Mapped[list["Jogador"]] = relationship(back_populates="time", order_by="Jogador.ordem")


class Jogador(Base):
    __tablename__ = "jogadores"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    nick: Mapped[str] = mapped_column(index=True)
    nome: Mapped[str | None]
    rota: Mapped[str]
    titular: Mapped[bool]
    ordem: Mapped[int]
    time_codigo: Mapped[str] = mapped_column(ForeignKey("times.codigo"))
    elo: Mapped[str | None]
    pdl: Mapped[int | None]

    time: Mapped[Time] = relationship(back_populates="jogadores")
    partidas_soloq: Mapped[list["PartidaSoloq"]] = relationship(back_populates="jogador")


class Partida(Base):
    """Uma série (melhor de 1, 3 ou 5)."""

    __tablename__ = "partidas"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    inicio: Mapped[datetime] = mapped_column(DataUTC, index=True)
    estado: Mapped[str] = mapped_column(index=True)
    fase: Mapped[str] = mapped_column(index=True)
    bloco: Mapped[str | None]
    melhor_de: Mapped[int]
    time_a: Mapped[str]
    time_b: Mapped[str]
    vitorias_a: Mapped[int | None]
    vitorias_b: Mapped[int | None]
    vencedor: Mapped[str | None]

    jogos: Mapped[list["Jogo"]] = relationship(back_populates="partida", order_by="Jogo.numero")


class Jogo(Base):
    __tablename__ = "jogos"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    partida_id: Mapped[str] = mapped_column(ForeignKey("partidas.id"), index=True)
    numero: Mapped[int]
    patch: Mapped[str]
    duracao: Mapped[int]
    time_azul: Mapped[str]
    time_vermelho: Mapped[str]
    vencedor: Mapped[str]

    partida: Mapped[Partida] = relationship(back_populates="jogos")
    participacoes: Mapped[list["Participacao"]] = relationship(back_populates="jogo")
    bans: Mapped[list["Ban"]] = relationship(back_populates="jogo")


class Participacao(Base):
    """Linha de estatísticas de um jogador num jogo."""

    __tablename__ = "participacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    jogo_id: Mapped[str] = mapped_column(ForeignKey("jogos.id"), index=True)
    jogador_id: Mapped[str | None] = mapped_column(index=True)
    nick: Mapped[str]
    time_codigo: Mapped[str] = mapped_column(index=True)
    lado: Mapped[str]
    rota: Mapped[str]
    campeao: Mapped[str] = mapped_column(index=True)
    venceu: Mapped[bool]
    abates: Mapped[int]
    mortes: Mapped[int]
    assistencias: Mapped[int]
    ouro: Mapped[int]
    cs: Mapped[int]
    dano_total: Mapped[int | None]

    jogo: Mapped[Jogo] = relationship(back_populates="participacoes")


class Ban(Base):
    __tablename__ = "bans"

    id: Mapped[int] = mapped_column(primary_key=True)
    jogo_id: Mapped[str] = mapped_column(ForeignKey("jogos.id"), index=True)
    time_codigo: Mapped[str] = mapped_column(index=True)
    campeao: Mapped[str] = mapped_column(index=True)

    jogo: Mapped[Jogo] = relationship(back_populates="bans")


class PartidaSoloq(Base):
    __tablename__ = "partidas_soloq"

    id: Mapped[int] = mapped_column(primary_key=True)
    jogador_id: Mapped[str] = mapped_column(ForeignKey("jogadores.id"), index=True)
    fim: Mapped[datetime] = mapped_column(DataUTC)
    campeao: Mapped[str]
    venceu: Mapped[bool]
    abates: Mapped[int]
    mortes: Mapped[int]
    assistencias: Mapped[int]
    cs: Mapped[int]
    dano: Mapped[int | None]
    ouro: Mapped[int | None]
    posicao: Mapped[str | None]

    jogador: Mapped[Jogador] = relationship(back_populates="partidas_soloq")
