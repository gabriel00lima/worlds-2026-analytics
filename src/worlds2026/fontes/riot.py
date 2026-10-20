"""Solo queue dos jogadores pela API oficial da Riot (precisa de RIOT_API_KEY)."""

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .. import config
from ..arquivos import ler_json, salvar_json
from ..texto import norm

log = logging.getLogger(__name__)

FILA_RANQUEADA_SOLO = 420
OPGG = {"kr": "kr", "euw1": "euw", "na1": "na", "br1": "br", "vn2": "vn", "tw2": "tw", "eun1": "eune", "jp1": "jp"}

Json = dict[str, Any]


class ChaveRecusada(RuntimeError):
    pass


class ClienteRiot:
    """Cliente mínimo que respeita o limite da chave de desenvolvedor (100 chamadas a cada 2 minutos)."""

    INTERVALO = 1.25

    def __init__(self, chave: str):
        self.chave = chave

    def get(self, regiao: str, caminho: str) -> Any:
        url = f"https://{regiao}.api.riotgames.com{caminho}"
        for _ in range(6):
            req = urllib.request.Request(url, headers={"X-Riot-Token": self.chave})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    time.sleep(self.INTERVALO)
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                if e.code == 429:
                    time.sleep(int(e.headers.get("Retry-After", "10")) + 1)
                    continue
                if e.code in (401, 403):
                    raise ChaveRecusada("chave da Riot recusada (expirada ou inválida)") from e
                time.sleep(3)
        return None


def link_opgg(conta: Json) -> str | None:
    if not conta.get("tag_line") or conta.get("platform") not in OPGG:
        return None
    nome = urllib.parse.quote(conta["game_name"])
    tag = urllib.parse.quote(conta["tag_line"])
    return f"https://www.op.gg/summoners/{OPGG[conta['platform']]}/{nome}-{tag}"


def contas_soloq() -> dict[str, Json]:
    """Contas conhecidas de cada jogador, indexadas por "nick|SIGLA"."""
    dados = ler_json(config.CONTAS_SOLOQ)
    if not dados:
        return {}
    out = {}
    for p in dados["jogadores"]:
        contas = [
            {
                "servidor": c.get("servidor"),
                "riotId": c.get("riot_id"),
                "link": link_opgg(c),
                "platform": c.get("platform"),
                "regional": c.get("regional"),
                "gameName": c.get("game_name"),
                "tagLine": c.get("tag_line"),
                "api": c.get("consultavel_api") == "sim",
            }
            for c in p.get("contas", [])
        ]
        links = {k: p.get(k) for k in ("dpm_lol", "lolpros", "leaguepedia") if p.get(k)}
        out[f"{norm(p['jogador'])}|{p['sigla'].upper()}"] = {"links": links, "contas": contas}
    return out


def _conta_mais_ativa(riot: ClienteRiot, contas: list[Json], cache: Json) -> tuple[Json, str, list[str]] | None:
    """Entre as contas consultáveis, a que jogou a ranqueada mais recente."""
    melhor = None
    for c in [c for c in contas if c["api"]][:4]:
        if c["riotId"] not in cache["puuid"]:
            nome, tag = urllib.parse.quote(c["gameName"]), urllib.parse.quote(c["tagLine"])
            conta = riot.get(c["regional"], f"/riot/account/v1/accounts/by-riot-id/{nome}/{tag}")
            cache["puuid"][c["riotId"]] = conta and conta["puuid"]
        puuid = cache["puuid"][c["riotId"]]
        if not puuid:
            continue
        ids = (
            riot.get(c["regional"], f"/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={FILA_RANQUEADA_SOLO}&count=10")
            or []
        )
        if ids and (not melhor or ids[0] > melhor[2][0]):
            melhor = (c, puuid, ids)
    return melhor


def _resumo_partida(partida: Json) -> Json:
    info = partida["info"]
    return {
        "fim": info.get("gameEndTimestamp"),
        "dur": info.get("gameDuration"),
        "p": {
            x["puuid"]: [
                x["championName"],
                x["win"],
                x["kills"],
                x["deaths"],
                x["assists"],
                x["totalMinionsKilled"] + x["neutralMinionsKilled"],
            ]
            for x in info["participants"]
        },
    }


def soloq(contas: dict[str, Json], chave: str) -> dict[str, Json]:
    """Elo e últimas partidas ranqueadas da conta mais ativa de cada jogador."""
    arq = config.CACHE / "soloq.json"
    cache = ler_json(arq, {"puuid": {}, "partidas": {}})
    riot = ClienteRiot(chave)
    out = {}
    try:
        for jogador, info in contas.items():
            escolhida = _conta_mais_ativa(riot, info["contas"], cache)
            if not escolhida:
                continue
            c, puuid, ids = escolhida
            filas = riot.get(c["platform"], f"/lol/league/v4/entries/by-puuid/{puuid}") or []
            elo = next((e for e in filas if e.get("queueType") == "RANKED_SOLO_5x5"), None)
            partidas = []
            for mid in ids:
                if mid not in cache["partidas"]:
                    m = riot.get(c["regional"], f"/lol/match/v5/matches/{mid}")
                    if not m:
                        continue
                    cache["partidas"][mid] = _resumo_partida(m)
                pm = cache["partidas"][mid]
                if puuid in pm["p"]:
                    partidas.append([pm["fim"], pm["dur"], *pm["p"][puuid]])
            out[jogador] = {
                "conta": c["riotId"],
                "servidor": c["servidor"],
                "link": c["link"],
                "elo": elo and {k: elo.get(k) for k in ("tier", "rank", "leaguePoints", "wins", "losses")},
                "partidas": partidas,
            }
            log.info("soloq %s: %s, %d partidas", jogador, c["riotId"], len(partidas))
    except ChaveRecusada as e:
        log.warning("solo queue interrompida: %s", e)
    salvar_json(arq, cache)
    return out
