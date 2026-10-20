from worlds2026 import cli


def test_parser_padrao():
    args = cli.criar_parser().parse_args([])
    assert not args.so_site and not args.verbose


def test_main_repassa_so_site(monkeypatch):
    chamadas = []
    monkeypatch.setattr(cli.pipeline, "executar", lambda so_cache: chamadas.append(so_cache))
    cli.main(["--so-site"])
    assert chamadas == [True]
