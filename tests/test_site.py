import pytest

from worlds2026 import site


@pytest.fixture
def web(tmp_path):
    (tmp_path / "index.html").write_text(
        '<head><link rel="stylesheet" href="estilo.css" /></head>'
        "<script>window.W = /*__DADOS__*/ null;</script>"
        '<script src="app.js"></script>'
    )
    (tmp_path / "estilo.css").write_text("body{color:red}")
    (tmp_path / "app.js").write_text("console.log(W)")
    return tmp_path


def test_renderizar_embute_css_js_e_dados(web):
    html = site.renderizar({"nome": "Ação"}, web)
    assert "<style>\nbody{color:red}</style>" in html
    assert "<script>\nconsole.log(W)</script>" in html
    assert 'window.W = {"nome":"Ação"};' in html
    assert "estilo.css" not in html and "app.js" not in html


def test_renderizar_escapa_fechamento_de_script(web):
    html = site.renderizar({"texto": "</script><b>"}, web)
    assert "<\\/script><b>" in html


def test_renderizar_falha_sem_marcador(web):
    (web / "index.html").write_text("<p>sem nada</p>")
    with pytest.raises(ValueError):
        site.renderizar({}, web)
