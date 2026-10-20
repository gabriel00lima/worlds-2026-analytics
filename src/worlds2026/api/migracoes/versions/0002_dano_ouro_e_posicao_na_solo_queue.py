"""dano, ouro e posição nas partidas de solo queue

Revisão: 0002
Anterior: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("partidas_soloq", schema=None) as batch_op:
        batch_op.add_column(sa.Column("dano", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("ouro", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("posicao", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("partidas_soloq", schema=None) as batch_op:
        batch_op.drop_column("posicao")
        batch_op.drop_column("ouro")
        batch_op.drop_column("dano")
