import base64
import io

from PIL import Image

from worlds2026 import imagens


def png(w, h):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), "red").save(buf, "PNG")
    return buf.getvalue()


def test_para_data_uri_reduz_e_corta_quadrado():
    uri = imagens.para_data_uri(png(400, 200), 100, quadrado=True)
    assert uri.startswith("data:image/webp;base64,")
    im = Image.open(io.BytesIO(base64.b64decode(uri.split(",", 1)[1])))
    assert im.size == (100, 100)


def test_miniatura_usa_cache(monkeypatch):
    chamadas = []

    def baixar(url):
        chamadas.append(url)
        return png(64, 64)

    monkeypatch.setattr(imagens.rede, "baixar", baixar)
    primeira = imagens.miniatura("http://x/logo.png", 32)
    segunda = imagens.miniatura("http://x/logo.png", 32)
    assert primeira == segunda and primeira.startswith("data:image/webp")
    assert chamadas == ["https://x/logo.png"]


def test_miniatura_sem_url():
    assert imagens.miniatura(None, 32) is None


def test_miniatura_falha_vira_none(monkeypatch):
    monkeypatch.setattr(imagens.rede, "baixar", lambda url: b"isso nao e imagem")
    assert imagens.miniatura("https://x/quebrada.png", 32) is None
