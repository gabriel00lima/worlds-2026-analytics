"""tabelas iniciais

Revisão: 0001
Anterior: nenhuma
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "partidas",
        sa.Column("id", sa.String(length=30), nullable=False),
        sa.Column("inicio", sa.DateTime(), nullable=False),
        sa.Column("estado", sa.String(), nullable=False),
        sa.Column("fase", sa.String(), nullable=False),
        sa.Column("bloco", sa.String(), nullable=True),
        sa.Column("melhor_de", sa.Integer(), nullable=False),
        sa.Column("time_a", sa.String(), nullable=False),
        sa.Column("time_b", sa.String(), nullable=False),
        sa.Column("vitorias_a", sa.Integer(), nullable=True),
        sa.Column("vitorias_b", sa.Integer(), nullable=True),
        sa.Column("vencedor", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_partidas_estado", "partidas", ["estado"])
    op.create_index("ix_partidas_fase", "partidas", ["fase"])
    op.create_index("ix_partidas_inicio", "partidas", ["inicio"])

    op.create_table(
        "times",
        sa.Column("codigo", sa.String(length=10), nullable=False),
        sa.Column("id_api", sa.String(length=30), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("liga", sa.String(), nullable=True),
        sa.Column("regiao", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("codigo"),
        sa.UniqueConstraint("id_api"),
    )
    op.create_table(
        "jogadores",
        sa.Column("id", sa.String(length=30), nullable=False),
        sa.Column("nick", sa.String(), nullable=False),
        sa.Column("nome", sa.String(), nullable=True),
        sa.Column("rota", sa.String(), nullable=False),
        sa.Column("titular", sa.Boolean(), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.Column("time_codigo", sa.String(length=10), nullable=False),
        sa.Column("elo", sa.String(), nullable=True),
        sa.Column("pdl", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["time_codigo"],
            ["times.codigo"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jogadores_nick", "jogadores", ["nick"])

    op.create_table(
        "jogos",
        sa.Column("id", sa.String(length=30), nullable=False),
        sa.Column("partida_id", sa.String(length=30), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("patch", sa.String(), nullable=False),
        sa.Column("duracao", sa.Integer(), nullable=False),
        sa.Column("time_azul", sa.String(), nullable=False),
        sa.Column("time_vermelho", sa.String(), nullable=False),
        sa.Column("vencedor", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["partida_id"],
            ["partidas.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jogos_partida_id", "jogos", ["partida_id"])

    op.create_table(
        "bans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("jogo_id", sa.String(length=30), nullable=False),
        sa.Column("time_codigo", sa.String(), nullable=False),
        sa.Column("campeao", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["jogo_id"],
            ["jogos.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bans_campeao", "bans", ["campeao"])
    op.create_index("ix_bans_jogo_id", "bans", ["jogo_id"])
    op.create_index("ix_bans_time_codigo", "bans", ["time_codigo"])

    op.create_table(
        "participacoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("jogo_id", sa.String(length=30), nullable=False),
        sa.Column("jogador_id", sa.String(), nullable=True),
        sa.Column("nick", sa.String(), nullable=False),
        sa.Column("time_codigo", sa.String(), nullable=False),
        sa.Column("lado", sa.String(), nullable=False),
        sa.Column("rota", sa.String(), nullable=False),
        sa.Column("campeao", sa.String(), nullable=False),
        sa.Column("venceu", sa.Boolean(), nullable=False),
        sa.Column("abates", sa.Integer(), nullable=False),
        sa.Column("mortes", sa.Integer(), nullable=False),
        sa.Column("assistencias", sa.Integer(), nullable=False),
        sa.Column("ouro", sa.Integer(), nullable=False),
        sa.Column("cs", sa.Integer(), nullable=False),
        sa.Column("dano_total", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["jogo_id"],
            ["jogos.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_participacoes_campeao", "participacoes", ["campeao"])
    op.create_index("ix_participacoes_jogador_id", "participacoes", ["jogador_id"])
    op.create_index("ix_participacoes_jogo_id", "participacoes", ["jogo_id"])
    op.create_index("ix_participacoes_time_codigo", "participacoes", ["time_codigo"])

    op.create_table(
        "partidas_soloq",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("jogador_id", sa.String(length=30), nullable=False),
        sa.Column("fim", sa.DateTime(), nullable=False),
        sa.Column("campeao", sa.String(), nullable=False),
        sa.Column("venceu", sa.Boolean(), nullable=False),
        sa.Column("abates", sa.Integer(), nullable=False),
        sa.Column("mortes", sa.Integer(), nullable=False),
        sa.Column("assistencias", sa.Integer(), nullable=False),
        sa.Column("cs", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["jogador_id"],
            ["jogadores.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_partidas_soloq_jogador_id", "partidas_soloq", ["jogador_id"])


def downgrade() -> None:
    op.drop_index("ix_partidas_soloq_jogador_id", table_name="partidas_soloq")

    op.drop_table("partidas_soloq")
    op.drop_index("ix_participacoes_time_codigo", table_name="participacoes")
    op.drop_index("ix_participacoes_jogo_id", table_name="participacoes")
    op.drop_index("ix_participacoes_jogador_id", table_name="participacoes")
    op.drop_index("ix_participacoes_campeao", table_name="participacoes")

    op.drop_table("participacoes")
    op.drop_index("ix_bans_time_codigo", table_name="bans")
    op.drop_index("ix_bans_jogo_id", table_name="bans")
    op.drop_index("ix_bans_campeao", table_name="bans")

    op.drop_table("bans")
    op.drop_index("ix_jogos_partida_id", table_name="jogos")

    op.drop_table("jogos")
    op.drop_index("ix_jogadores_nick", table_name="jogadores")

    op.drop_table("jogadores")
    op.drop_table("times")
    op.drop_index("ix_partidas_inicio", table_name="partidas")
    op.drop_index("ix_partidas_fase", table_name="partidas")
    op.drop_index("ix_partidas_estado", table_name="partidas")

    op.drop_table("partidas")
