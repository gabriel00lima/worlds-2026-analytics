"""Baixa logos, fotos e ícones e os converte em miniaturas WebP embutíveis (data URI)."""

import base64
import io
import logging
import urllib.error

from PIL import Image, UnidentifiedImageError

from . import config, rede

log = logging.getLogger(__name__)


def _arquivo_cache(url: str, lado: int):
    nome = base64.urlsafe_b64encode(f"{url}|{lado}".encode()).decode()[-60:]
    return config.CACHE_IMAGENS / f"{nome}.txt"


def para_data_uri(dados: bytes, lado: int, quadrado: bool = False, formato: str = "WEBP") -> str:
    im = Image.open(io.BytesIO(dados)).convert("RGBA")
    if quadrado:
        w, h = im.size
        c = min(w, h)
        im = im.crop(((w - c) // 2, 0, (w - c) // 2 + c, c))
    im.thumbnail((lado, lado))
    buf = io.BytesIO()
    im.save(buf, formato, quality=72, method=6)
    return f"data:image/{formato.lower()};base64," + base64.b64encode(buf.getvalue()).decode()


def miniatura(url: str | None, lado: int, quadrado: bool = False) -> str | None:
    """Data URI da imagem reduzida, ou None se não houver imagem. Falhas também ficam em cache."""
    if not url:
        return None
    url = url.replace("http://", "https://")
    cache = _arquivo_cache(url, lado)
    if cache.exists():
        return cache.read_text() or None
    try:
        dados = rede.baixar(url)
        uri = para_data_uri(dados, lado, quadrado) if dados else ""
    except (urllib.error.URLError, OSError, UnidentifiedImageError) as e:
        log.warning("imagem falhou: %s (%s)", url, e)
        uri = ""
    cache.write_text(uri)
    return uri or None
