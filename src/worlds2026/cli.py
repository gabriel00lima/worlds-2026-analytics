"""Linha de comando: python -m worlds2026 [--so-site] [-v]."""

import argparse
import logging

from . import pipeline


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worlds2026",
        description="Coleta os dados do Worlds 2026 e gera o site em docs/index.html.",
    )
    parser.add_argument(
        "--so-site", action="store_true", help="não baixa jogos novos; regera o site com o que já está em cache"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="mostra detalhes das requisições")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = criar_parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s")
    pipeline.executar(so_cache=args.so_site)
