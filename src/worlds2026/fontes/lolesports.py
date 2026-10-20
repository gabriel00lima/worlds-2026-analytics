"""API do LoL Esports: agenda, chaves, times e detalhes das séries."""

import logging
import urllib.parse
from typing import Any

from .. import config, rede

log = logging.getLogger(__name__)

API = "https://esports-api.lolesports.com/persisted/gw"
FEED = "https://feed.lolesports.com/livestats/v1"

Json = dict[str, Any]


def api(rota: str, **params: str) -> Json:
    params.setdefault("hl", "pt-BR")
    url = f"{API}/{rota}?{urllib.parse.urlencode(params)}"
    resposta = rede.baixar_json(url, {"x-api-key": config.LOLESPORTS_API_KEY})
    if resposta is None:
        raise RuntimeError(f"resposta vazia de {rota}")
    return resposta["data"]


def agenda_liga(liga_id: str, ate_data: str = "2026-10-01", paginas: int = 6) -> list[Json]:
    """Eventos da liga a partir da página atual, voltando no tempo até ate_data."""
    eventos: list[Json] = []
    token = None
    for _ in range(paginas):
        params = {"leagueId": liga_id}
        if token:
            params["pageToken"] = token
        agenda = api("getSchedule", **params)["schedule"]
        eventos += agenda["events"]
        token = (agenda.get("pages") or {}).get("older")
        if not token or min(e["startTime"] for e in agenda["events"]) < ate_data:
            break

    vistos: set[str] = set()
    unicos = []
    for e in sorted(eventos, key=lambda e: e["startTime"]):
        partida = (e.get("match") or {}).get("id")
        if partida and partida not in vistos:
            vistos.add(partida)
            unicos.append(e)
    return unicos


def fases_do_torneio(torneio_id: str) -> dict[str, str]:
    """Mapeia o id de cada partida para a fase (play_in, swiss, knockouts)."""
    etapas = api("getStandings", tournamentId=torneio_id)["standings"][0]["stages"]
    return {m["id"]: etapa["slug"] for etapa in etapas for secao in etapa["sections"] for m in secao["matches"]}


def converter_evento(evento: Json, fase: str) -> Json:
    partida = evento["match"]
    return {
        "id": partida["id"],
        "inicio": evento["startTime"],
        "estado": evento["state"],
        "fase": fase,
        "bloco": evento.get("blockName"),
        "melhorDe": (partida.get("strategy") or {}).get("count", 1),
        "times": [
            {
                "codigo": t["code"],
                "nome": t["name"],
                "vitorias": (t.get("result") or {}).get("gameWins"),
                "resultado": (t.get("result") or {}).get("outcome"),
            }
            for t in partida["teams"]
        ],
    }


def montar_agenda() -> list[Json]:
    fase_de = fases_do_torneio(config.TORNEIO_WORLDS_2026)
    eventos = agenda_liga(config.LIGA_WORLDS)
    return [converter_evento(e, fase_de[e["match"]["id"]]) for e in eventos if e["match"]["id"] in fase_de]


def detalhes_partida(partida_id: str) -> Json:
    return api("getEventDetails", id=partida_id)["event"]["match"]


def times() -> list[Json]:
    return api("getTeams")["teams"]


def ligas() -> dict[str, str]:
    return {liga["name"]: liga["id"] for liga in api("getLeagues")["leagues"]}


def titulares_regionais(time: Json, ids_ligas: dict[str, str]) -> list[str]:
    """IDs dos 5 jogadores da última partida oficial do time na liga dele."""
    liga_id = ids_ligas.get((time.get("homeLeague") or {}).get("name", ""))
    if not liga_id:
        return []
    try:
        eventos = agenda_liga(liga_id, ate_data="2026-01-01", paginas=3)
    except (RuntimeError, OSError, ValueError) as erro:
        log.warning("agenda da liga de %s indisponível: %s", time["code"], erro)
        return []

    for e in reversed(eventos):
        if e["state"] != "completed" or time["code"] not in [t["code"] for t in e["match"]["teams"]]:
            continue
        for jogo in reversed(detalhes_partida(e["match"]["id"])["games"]):
            if jogo["state"] != "completed":
                continue
            janela = rede.baixar_json(f"{FEED}/window/{jogo['id']}")
            if not janela:
                continue
            meta = janela["gameMetadata"]
            for lado in ("blueTeamMetadata", "redTeamMetadata"):
                if meta[lado]["esportsTeamId"] == time["id"]:
                    return [p["esportsPlayerId"] for p in meta[lado]["participantMetadata"]]
    return []


def vod_do_jogo(game: Json, duracao: int | None) -> Json | None:
    """VOD oficial do jogo no YouTube, de preferência em português.

    O trecho do vídeo começa no draft, então o início da partida é estimado contando a
    duração para trás a partir do fim do trecho.
    """
    vods = [v for v in game.get("vods") or [] if v.get("provider") == "youtube" and v.get("parameter")]
    for idioma in ("pt-BR", "en-US"):
        v = next((v for v in vods if v.get("locale") == idioma), None)
        if v:
            inicio = None
            if v.get("endMillis") and duracao:
                inicio = max((v.get("startMillis") or 0) // 1000, v["endMillis"] // 1000 - duracao - 30)
            return {"yt": v["parameter"], "t0": inicio, "idioma": idioma}
    return None
