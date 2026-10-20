"""Linha de comando.

python -m worlds2026                 coleta os dados e gera o site
python -m worlds2026 --so-site       regera o site só com o cache
python -m worlds2026 banco           carrega no banco os dados da última coleta
python -m worlds2026 api             carrega o banco e sobe a API em http://localhost:8000
"""

import argparse
import logging

from . import pipeline


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="worlds2026", description="Dados do Mundial de League of Legends 2026.")
    parser.add_argument("-v", "--verbose", action="store_true", help="mostra detalhes das requisições")
    parser.add_argument(
        "--so-site", action="store_true", help="não baixa jogos novos; regera o site com o que já está em cache"
    )
    sub = parser.add_subparsers(dest="comando")
    sub.add_parser("coletar", help="coleta os dados e gera o site (padrão)")
    sub.add_parser("banco", help="carrega no banco os dados da última coleta")
    api = sub.add_parser("api", help="sobe a API REST")
    api.add_argument("--host", default="127.0.0.1")
    api.add_argument("--porta", type=int, default=8000)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = criar_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s")

    if args.comando in (None, "coletar"):
        pipeline.executar(so_cache=args.so_site)
        return

    from .api import banco, carga

    carga.carregar_do_cache(banco.engine)
    if args.comando == "api":
        import uvicorn

        uvicorn.run("worlds2026.api.app:app", host=args.host, port=args.porta)
