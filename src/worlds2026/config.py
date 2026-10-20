"""Caminhos usados pela coleta e pela geração do site."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

DADOS = RAIZ / "data"
CURIOSIDADES = DADOS / "curiosidades"
CONTAS_SOLOQ = DADOS / "soloq" / "contas.json"

CACHE = RAIZ / ".cache"
MODELO = RAIZ / "web" / "modelo.html"
SITE = RAIZ / "docs" / "index.html"
