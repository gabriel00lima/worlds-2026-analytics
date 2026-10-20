"""Gera o index.html final: o template de web/ com o CSS, o JS e os dados embutidos num arquivo só."""

import json
import re
from pathlib import Path
from typing import Any

from . import config

MARCADOR_DADOS = re.compile(r"/\*__DADOS__\*/\s*null")
LINK_CSS = re.compile(r'<link rel="stylesheet" href="estilo\.css"\s*/?>')
SCRIPT_APP = re.compile(r'<script src="app\.js"></script>')


def _substituir_uma_vez(padrao: re.Pattern[str], texto: str, novo: str) -> str:
    resultado, n = padrao.subn(lambda _: novo, texto, count=1)
    if n != 1:
        raise ValueError(f"{padrao.pattern} não encontrado no template")
    return resultado


def renderizar(dados: dict[str, Any], web: Path = config.WEB) -> str:
    html = (web / "index.html").read_text(encoding="utf-8")
    css = (web / "estilo.css").read_text(encoding="utf-8")
    js = (web / "app.js").read_text(encoding="utf-8")
    json_dados = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    html = _substituir_uma_vez(MARCADOR_DADOS, html, json_dados)
    html = _substituir_uma_vez(LINK_CSS, html, f"<style>\n{css}</style>")
    return _substituir_uma_vez(SCRIPT_APP, html, f"<script>\n{js}</script>")


def gerar(dados: dict[str, Any], destino: Path = config.SITE) -> int:
    html = renderizar(dados)
    destino.write_text(html, encoding="utf-8")
    return len(html)
