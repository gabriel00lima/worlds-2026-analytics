from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect

from worlds2026.api import banco, modelos  # noqa: F401  (registra as tabelas)


def test_migracoes_criam_as_tabelas_dos_modelos(engine):
    banco.migrar(engine)
    tabelas = set(inspect(engine).get_table_names())
    assert tabelas == set(banco.Base.metadata.tables) | {"alembic_version"}


def test_modelos_nao_tem_mudanca_sem_migracao(engine):
    """Se este teste falhar, falta gerar uma migração: alembic revision --autogenerate -m "..." """
    banco.migrar(engine)
    with engine.connect() as conn:
        diferencas = compare_metadata(MigrationContext.configure(conn), banco.Base.metadata)
    assert diferencas == []


def test_migrar_de_novo_nao_faz_nada(engine):
    banco.migrar(engine)
    banco.migrar(engine)
    with engine.connect() as conn:
        assert MigrationContext.configure(conn).get_current_revision() == "0002"


def test_downgrade_remove_tudo(engine):
    banco.migrar(engine)
    cfg = Config()
    cfg.set_main_option("script_location", str(banco.MIGRACOES))
    with engine.begin() as conn:
        cfg.attributes["conexao"] = conn
        command.downgrade(cfg, "base")
    assert set(inspect(engine).get_table_names()) == {"alembic_version"}
