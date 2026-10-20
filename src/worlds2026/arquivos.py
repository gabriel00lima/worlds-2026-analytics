"""Leitura e escrita de JSON em disco."""

import json
from pathlib import Path
from typing import Any


def ler_json(caminho: Path, padrao: Any = None) -> Any:
    if not caminho.exists():
        return padrao
    with caminho.open(encoding="utf-8") as f:
        return json.load(f)


def salvar_json(caminho: Path, dados: Any) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False)
