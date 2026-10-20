from alembic import context

from worlds2026.api import modelos  # noqa: F401  (registra as tabelas no metadata)
from worlds2026.api.banco import Base, criar_engine

conexao = context.config.attributes.get("conexao")


def rodar(conn) -> None:
    context.configure(connection=conn, target_metadata=Base.metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


if conexao is not None:
    rodar(conexao)
else:
    with criar_engine().connect() as conn:
        rodar(conn)
