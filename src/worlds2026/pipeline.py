"""Etapas da coleta, da agenda até o site pronto."""

import logging
import re
from datetime import datetime, timezone
from typing import Any

from . import config, curiosidades, historia, imagens, site
from .arquivos import ler_json, salvar_json
from .fontes import ddragon, leaguepedia, lolesports, riot
from .jogos import jogo_em_cache, processar_jogo
from .tempo import iso
from .texto import norm, sem_caixa_alta

log = logging.getLogger(__name__)

Json = dict[str, Any]
ORDEM_ROTAS = {"top": 0, "jungle": 1, "mid": 2, "bottom": 3, "support": 4}


def escolher_times(partidas: list[Json], todos: list[Json]) -> dict[str, Json]:
    """Para cada sigla do torneio, o time certo da API (a mesma sigla aparece em academias e times antigos)."""
    nomes = {t["codigo"]: t["nome"] for p in partidas for t in p["times"] if t["codigo"] != "TBD"}
    por_codigo = {}
    for codigo, nome in nomes.items():
        candidatos = [t for t in todos if t["code"] == codigo]
        exatos = [t for t in candidatos if t["name"].lower() == nome.lower()]
        principais = [t for t in candidatos if not re.search(r"academy|challengers", t["name"], re.I)]
        candidatos = exatos or principais or candidatos
        candidatos.sort(key=lambda t: (t.get("status") != "active", -len(t.get("players") or [])))
        por_codigo[codigo] = candidatos[0]
    return por_codigo


def coletar_jogos(partidas: list[Json], so_cache: bool) -> list[Json]:
    jogos = []
    for p in partidas:
        if p["estado"] not in ("completed", "inProgress"):
            continue
        for g in lolesports.detalhes_partida(p["id"])["games"]:
            if g["state"] == "completed" and not so_cache:
                log.info("  %s x %s, jogo %s", p["times"][0]["codigo"], p["times"][1]["codigo"], g["number"])
                jogo = processar_jogo(g["id"], p["id"], g["number"])
            else:
                jogo = jogo_em_cache(g["id"])
            if jogo:
                jogo["vod"] = lolesports.vod_do_jogo(g, jogo["duracao"])
                jogos.append(jogo)
    return jogos


def conferir_vencedores(partidas: list[Json], jogos: list[Json], por_codigo: dict[str, Json]) -> list[str]:
    """Compara os vencedores estimados com o placar oficial de cada série e devolve as divergências."""
    codigo_do_id = {t["id"]: c for c, t in por_codigo.items()}
    divergencias = []
    for p in partidas:
        da_serie = [j for j in jogos if j["partida"] == p["id"]]
        if not da_serie or p["estado"] != "completed":
            continue
        contagem: dict[str | None, int] = {}
        for j in da_serie:
            vencedor = codigo_do_id.get(j["timeAzul"] if j["vencedor"] == "blue" else j["timeVermelho"])
            contagem[vencedor] = contagem.get(vencedor, 0) + 1
        oficial = {t["codigo"]: t["vitorias"] for t in p["times"]}
        if contagem != {k: v for k, v in oficial.items() if v}:
            divergencias.append(f"{p['id']}: estimado {contagem}, oficial {oficial}")
    return divergencias


def definir_titulares(
    por_codigo: dict[str, Json], jogos: list[Json], ids_ligas: dict[str, str], so_cache: bool
) -> dict[str, list[str]]:
    """Titulares de cada time: os do último jogo no Worlds, ou os da liga regional antes da estreia."""
    titulares = {}
    for codigo, t in por_codigo.items():
        ids: list[str] = []
        for j in jogos:
            for lado, time_id in (("blue", j["timeAzul"]), ("red", j["timeVermelho"])):
                if time_id == t["id"]:
                    ids = [x["jogadorId"] for x in j["jogadores"] if x["lado"] == lado]
        if not ids and not so_cache:
            ids = lolesports.titulares_regionais(t, ids_ligas)
        titulares[codigo] = ids

    arq = config.CACHE / "titulares.json"
    anteriores = ler_json(arq, {})
    for codigo, ids in titulares.items():
        if not ids:
            titulares[codigo] = anteriores.get(codigo, [])
    salvar_json(arq, titulares)
    return titulares


def montar_times(por_codigo: dict[str, Json], titulares: dict[str, list[str]], jogos: list[Json]) -> dict[str, Json]:
    jogaram = {x["jogadorId"] for j in jogos for x in j["jogadores"]}
    times = {}
    for codigo, t in por_codigo.items():
        tit = titulares.get(codigo, [])
        jogadores = []
        for pl in t.get("players", []):
            if pl["id"] not in tit and pl["id"] not in jogaram:
                continue
            foto = pl.get("image") or ""
            jogadores.append(
                {
                    "id": pl["id"],
                    "nick": pl["summonerName"].strip(),
                    "nome": sem_caixa_alta(f"{pl.get('firstName', '')} {pl.get('lastName', '')}".strip(), pessoa=True),
                    "rota": pl["role"],
                    "titular": pl["id"] in tit,
                    "foto": None if "default-headshot" in foto else imagens.miniatura(foto, 160, quadrado=True),
                }
            )
        jogadores.sort(key=lambda x: (not x["titular"], ORDEM_ROTAS.get(x["rota"], 9)))
        liga = t.get("homeLeague") or {}
        times[codigo] = {
            "id": t["id"],
            "codigo": codigo,
            "nome": sem_caixa_alta(t["name"]),
            "liga": liga.get("name"),
            "regiao": liga.get("region"),
            "logo": imagens.miniatura(t.get("image"), 128),
            "jogadores": jogadores,
        }
        log.info("  %s: %d jogadores", codigo, len(jogadores))
    return times


def anexar_soloq(times: dict[str, Json], so_cache: bool, campeao_por_id: dict[str, str] | None = None) -> None:
    contas = riot.contas_soloq()
    arq = config.SOLOQ_PARTIDAS
    soloq: dict[str, Json] = {}
    if not config.RIOT_API_KEY and not so_cache:
        log.info("solo queue: RIOT_API_KEY não está no ambiente, mantendo os dados da última coleta")
    if config.RIOT_API_KEY and not so_cache:
        soloq = riot.soloq(contas, config.RIOT_API_KEY, campeao_por_id or {})
        if soloq:
            salvar_json(arq, soloq)
    soloq = soloq or ler_json(arq, {})
    for t in times.values():
        for pl in t["jogadores"]:
            chave = next((k for k in contas if k.split("|")[0] == norm(pl["nick"])), None)
            if chave:
                pl["contas"] = contas[chave]
                pl["soloq"] = soloq.get(chave)


def montar_campeoes(versao: str, camp: dict[str, Any], jogos: list[Json], times: dict[str, Json]) -> dict[str, Json]:
    chave_por_nome = {k.lower(): k for k in camp}
    usados = {x["campeao"] for j in jogos for x in j["jogadores"]}
    usados |= {b for j in jogos if j.get("lp") for lado in ("blue", "red") for b in j["lp"]["bans"][lado]}
    usados |= {
        p[2] for t in times.values() for pl in t["jogadores"] if pl.get("soloq") for p in pl["soloq"]["partidas"]
    }
    campeoes = {}
    for nome in usados:
        chave = chave_por_nome.get(re.sub(r"[ '.]", "", nome.lower()), nome)
        campeoes[nome] = {
            "nome": camp.get(chave, {}).get("name", nome),
            "icone": imagens.miniatura(ddragon.icone_campeao(versao, chave), 64),
        }
    return campeoes


def montar_itens(versao: str, jogos: list[Json]) -> dict[int, Json]:
    usados = {i for j in jogos for x in j["jogadores"] for i in x["itens"] if i}
    todos = ddragon.itens(versao)
    return {
        i: {"nome": todos[str(i)]["name"], "icone": imagens.miniatura(ddragon.icone_item(versao, i), 40)}
        for i in usados
        if str(i) in todos
    }


def executar(so_cache: bool = False) -> Json:
    """Roda a coleta inteira e grava docs/index.html. Com so_cache, só usa o que já foi baixado dos jogos."""
    config.preparar_pastas()
    agora = datetime.now(timezone.utc)

    log.info("agenda")
    partidas = lolesports.montar_agenda()

    log.info("times")
    por_codigo = escolher_times(partidas, lolesports.times())
    ids_ligas = lolesports.ligas()

    log.info("jogos")
    jogos = coletar_jogos(partidas, so_cache)

    log.info("Leaguepedia (bans, arautos, dano)")
    versao = ddragon.versao_atual()
    camp = ddragon.campeoes(versao)
    camp_en = ddragon.campeoes(versao, "en_US")
    chave_por_nome = {}
    for chave, c in camp_en.items():
        chave_por_nome[norm(c["name"])] = chave
        chave_por_nome[norm(chave)] = chave
    lp = leaguepedia.placares_em_cache() if so_cache else leaguepedia.placares(chave_por_nome)
    leaguepedia.enriquecer_jogos(jogos, lp)

    for d in conferir_vencedores(partidas, jogos, por_codigo):
        log.warning("vencedor estimado diverge do placar oficial: %s", d)

    log.info("escalações e fotos")
    titulares = definir_titulares(por_codigo, jogos, ids_ligas, so_cache)
    times = montar_times(por_codigo, titulares, jogos)

    log.info("solo queue")
    anexar_soloq(times, so_cache, {c["key"]: chave for chave, c in camp.items()})

    log.info("campeões e itens")
    dados = {
        "atualizado": iso(agora),
        "curiosidades": curiosidades.ler_curiosidades(),
        "versaoDD": versao,
        "partidas": partidas,
        "times": times,
        "jogos": jogos,
        "campeoes": montar_campeoes(versao, camp, jogos, times),
        "itens": montar_itens(versao, jogos),
        "historia": historia.ler_historia(camp_en),
        "audio": ler_json(config.AUDIO / "index.json", {}),
    }
    tentativa = leaguepedia.ultima_tentativa()
    if tentativa:
        dados["lpTentativa"] = tentativa
    salvar_json(config.CACHE / "dados.json", dados)
    tamanho = site.gerar(dados)
    log.info(
        "pronto: %d partidas, %d jogos, %d times, site com %.2f MB",
        len(partidas),
        len(jogos),
        len(times),
        tamanho / 1e6,
    )
    return dados
