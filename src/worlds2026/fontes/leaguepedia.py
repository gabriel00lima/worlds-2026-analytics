"""Leaguepedia: bans, arautos, larvas e dano de cada jogo, lidos do wikitext das páginas de placares.

Os jogos da Leaguepedia são casados com os do feed pelos 10 campeões em campo.
"""

import logging
import re
import time
import urllib.error
import urllib.parse
from typing import Any

from .. import config, rede
from ..arquivos import ler_json, salvar_json
from ..texto import norm

log = logging.getLogger(__name__)

API = "https://lol.fandom.com/api.php"
PAGINAS = [
    "2026_Season_World_Championship/Play-In/Scoreboards",
    "2026_Season_World_Championship/Main_Event/Scoreboards",
    *(f"2026_Season_World_Championship/Main_Event/Scoreboards/Week_{i}" for i in range(1, 5)),
]
SEM_BAN = ("None", "Loss of Ban")

Json = dict[str, Any]


def caminho_cache():
    return config.CACHE / "leaguepedia.json"


def wikitext(pagina: str) -> str | None:
    q = urllib.parse.urlencode(
        {"action": "parse", "page": pagina, "prop": "wikitext", "format": "json", "redirects": 1}
    )
    for tentativa in range(1, 5):
        d = rede.baixar_json(f"{API}?{q}")
        if d is None:
            return None
        erro = (d.get("error") or {}).get("code")
        if erro == "missingtitle":
            return None
        if erro == "ratelimited":
            time.sleep(15 * tentativa)
            continue
        if erro:
            raise RuntimeError(erro)
        return d["parse"]["wikitext"]["*"]
    raise RuntimeError("Leaguepedia limitou as consultas")


def campos(bloco: str) -> dict[str, str]:
    """Parâmetros "|nome=valor" de um template, mantendo a primeira ocorrência."""
    out: dict[str, str] = {}
    for m in re.finditer(r"\|\s*([a-z0-9_]+)\s*=\s*([^|{}\n]*)", bloco):
        out.setdefault(m.group(1), m.group(2).strip())
    return out


def _numero(valor: Any) -> int | None:
    texto = str(valor).strip()
    return int(texto) if texto.lstrip("-").isdigit() else None


def chave_do_jogo(campeoes: list[str]) -> str:
    return "|".join(sorted(norm(c) for c in campeoes))


def _jogadores_do_placar(bloco: str) -> dict[str, dict[str, str]]:
    jogadores = {}
    for lado in ("blue", "red"):
        for i in range(1, 6):
            m = re.search(rf"\|{lado}{i}=\{{\{{Scoreboard/Player(.*?)\|runes=", bloco, re.S)
            if m:
                jogadores[f"{lado}{i}"] = campos(m.group(1))
    return jogadores


def _por_lado(cab: dict[str, str], campo: str) -> dict[str, int | None]:
    return {"blue": _numero(cab.get(f"team1{campo}")), "red": _numero(cab.get(f"team2{campo}"))}


def _bans(cab: dict[str, str], time: str) -> list[str]:
    valores = (cab.get(f"{time}ban{i}") for i in range(1, 6))
    return [b for b in valores if b and b not in SEM_BAN]


def ler_placares(wt: str, chave_por_nome: dict[str, str]) -> dict[str, Json]:
    """Extrai os jogos de uma página de placares."""

    def chave_campeao(nome: str | None) -> str:
        return chave_por_nome.get(norm(nome), nome or "")

    jogos = {}
    for bloco in re.split(r"\{\{Scoreboard/Season", wt)[1:]:
        jogadores = _jogadores_do_placar(bloco)
        if len(jogadores) < 10:
            continue
        sem_jogadores = re.sub(
            r"\|(blue|red)\d=\{\{Scoreboard/Player.*?\|runes=\{\{[^}]*\}\}\}\}", "", bloco, flags=re.S
        )
        cab = campos(sem_jogadores)
        chave = chave_do_jogo([chave_campeao(p.get("champion")) for p in jogadores.values()])
        jogos[chave] = {
            "vencedor": {"1": "blue", "2": "red"}.get(cab.get("winner", "")),
            "bans": {
                "blue": [chave_campeao(b) for b in _bans(cab, "team1")],
                "red": [chave_campeao(b) for b in _bans(cab, "team2")],
            },
            "arautos": _por_lado(cab, "rh"),
            "larvas": _por_lado(cab, "vg"),
            "atakhan": _por_lado(cab, "at"),
            "jogadores": {
                norm(chave_campeao(p.get("champion"))): {
                    "danoTotal": _numero(p.get("damagetochamps")),
                    "visao": _numero(p.get("visionscore")),
                }
                for p in jogadores.values()
            },
        }
    return jogos


def placares(chave_por_nome: dict[str, str]) -> dict[str, Json]:
    """Todos os jogos do torneio na Leaguepedia, somados ao que já estava em cache."""
    jogos = ler_json(caminho_cache(), {})
    for pagina in PAGINAS:
        try:
            wt = wikitext(pagina)
        except (RuntimeError, urllib.error.URLError, OSError) as e:
            log.warning("Leaguepedia falhou em %s: %s", pagina, e)
            continue
        time.sleep(2)
        if wt:
            jogos.update(ler_placares(wt, chave_por_nome))
    salvar_json(caminho_cache(), jogos)
    return jogos


def placares_em_cache() -> dict[str, Json]:
    return ler_json(caminho_cache(), {})


def enriquecer_jogos(jogos: list[Json], lp: dict[str, Json]) -> None:
    """Acrescenta bans, objetivos e dano, e corrige o vencedor estimado quando a Leaguepedia discorda."""
    for j in jogos:
        info = lp.get(chave_do_jogo([x["campeao"] for x in j["jogadores"]]))
        if not info:
            j["lp"] = None
            continue
        if info["vencedor"] and info["vencedor"] != j["vencedor"]:
            log.info("vencedor corrigido pela Leaguepedia: %s %s → %s", j["id"], j["vencedor"], info["vencedor"])
            j["vencedor"] = info["vencedor"]
        j["lp"] = {k: info[k] for k in ("bans", "arautos", "larvas", "atakhan")}
        for x in j["jogadores"]:
            x.update(info["jogadores"].get(norm(x["campeao"]), {}))
