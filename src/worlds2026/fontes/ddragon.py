"""Data Dragon: nomes e ícones de campeões e itens."""

from typing import Any

from .. import rede

BASE = "https://ddragon.leagueoflegends.com"


def versao_atual() -> str:
    return rede.baixar_json(f"{BASE}/api/versions.json")[0]


def campeoes(versao: str, idioma: str = "pt_BR") -> dict[str, Any]:
    return rede.baixar_json(f"{BASE}/cdn/{versao}/data/{idioma}/champion.json")["data"]


def itens(versao: str) -> dict[str, Any]:
    return rede.baixar_json(f"{BASE}/cdn/{versao}/data/pt_BR/item.json")["data"]


def icone_campeao(versao: str, chave: str) -> str:
    return f"{BASE}/cdn/{versao}/img/champion/{chave}.png"


def icone_item(versao: str, item_id: int) -> str:
    return f"{BASE}/cdn/{versao}/img/item/{item_id}.png"
