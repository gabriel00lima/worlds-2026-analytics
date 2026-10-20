"""Roda a coleta inteira com todas as fontes externas substituídas por dados fixos."""

import json

from fabricas import quadro_feed, time_feed

from worlds2026 import config, imagens, pipeline
from worlds2026.fontes import ddragon, leaguepedia, livestats, lolesports


def meta(jogadores_por_lado):
    def lado(time_id, inicio):
        return {
            "esportsTeamId": time_id,
            "participantMetadata": [
                {
                    "participantId": inicio + i,
                    "esportsPlayerId": f"{time_id}-{i}",
                    "summonerName": f"X {time_id}{i}",
                    "championId": "Ahri",
                    "role": "mid",
                }
                for i in range(jogadores_por_lado)
            ],
        }

    return {"patchVersion": "16.20.1", "blueTeamMetadata": lado("id-t1", 1), "redTeamMetadata": lado("id-gen", 6)}


def preparar_fontes(monkeypatch, tmp_path):
    partidas = [
        {
            "id": "m1",
            "inicio": "2026-10-18T18:00:00Z",
            "estado": "completed",
            "fase": "swiss",
            "bloco": "R1",
            "melhorDe": 1,
            "times": [
                {"codigo": "T1", "nome": "T1", "vitorias": 1, "resultado": "win"},
                {"codigo": "GEN", "nome": "Gen.G", "vitorias": 0, "resultado": "loss"},
            ],
        }
    ]
    times = [
        {
            "id": "id-t1",
            "code": "T1",
            "name": "T1",
            "status": "active",
            "image": None,
            "players": [{"id": f"id-t1-{i}", "summonerName": f"T1 {i}", "role": "mid"} for i in range(5)],
        },
        {
            "id": "id-gen",
            "code": "GEN",
            "name": "Gen.G",
            "status": "active",
            "image": None,
            "players": [{"id": f"id-gen-{i}", "summonerName": f"GEN {i}", "role": "mid"} for i in range(5)],
        },
    ]
    vitoria_azul = time_feed(ouro=40000, torres=9, inibidores=1)
    quadros = [quadro_feed("00:00"), quadro_feed("00:10", "finished", azul=vitoria_azul)]

    monkeypatch.setattr(lolesports, "montar_agenda", lambda: partidas)
    monkeypatch.setattr(lolesports, "times", lambda: times)
    monkeypatch.setattr(lolesports, "ligas", lambda: {})
    monkeypatch.setattr(
        lolesports, "detalhes_partida", lambda pid: {"games": [{"id": "g1", "number": 1, "state": "completed"}]}
    )
    monkeypatch.setattr(
        livestats,
        "janela",
        lambda jogo_id, quando=None, rota="window": {"frames": quadros[:1], "gameMetadata": meta(5)},
    )
    monkeypatch.setattr(livestats, "baixar_quadros", lambda jogo_id, inicio: quadros)
    monkeypatch.setattr(livestats, "detalhes_finais", lambda jogo_id, ultimo: {})
    monkeypatch.setattr(ddragon, "versao_atual", lambda: "16.20.1")
    monkeypatch.setattr(ddragon, "campeoes", lambda versao, idioma="pt_BR": {"Ahri": {"name": "Ahri", "key": "103"}})
    monkeypatch.setattr(ddragon, "itens", lambda versao: {})
    monkeypatch.setattr(leaguepedia, "placares", lambda chave_por_nome: {})
    monkeypatch.setattr(imagens, "miniatura", lambda url, lado, quadrado=False: None)
    monkeypatch.setattr(config, "CURIOSIDADES", tmp_path / "sem-curiosidades")
    monkeypatch.setattr(config, "CONTAS_SOLOQ", tmp_path / "sem-contas.json")
    monkeypatch.setattr(config, "RIOT_API_KEY", None)
    monkeypatch.setattr(config, "SITE", tmp_path / "index.html")
    monkeypatch.setattr(pipeline.site, "gerar", lambda dados: len(json.dumps(dados)))


def test_coleta_completa(monkeypatch, tmp_path):
    preparar_fontes(monkeypatch, tmp_path)

    dados = pipeline.executar()

    (jogo,) = dados["jogos"]
    assert jogo["vencedor"] == "blue" and jogo["lp"] is None
    assert set(dados["times"]) == {"T1", "GEN"}
    assert [j["titular"] for j in dados["times"]["T1"]["jogadores"]] == [True] * 5
    assert dados["campeoes"]["Ahri"]["nome"] == "Ahri"
    assert (config.CACHE_JOGOS / "g1.json").exists()


def test_so_site_usa_apenas_o_cache(monkeypatch, tmp_path):
    preparar_fontes(monkeypatch, tmp_path)
    pipeline.executar()

    def nao_pode_baixar(*args, **kwargs):
        raise AssertionError("não deveria acessar a rede")

    monkeypatch.setattr(livestats, "baixar_quadros", nao_pode_baixar)
    monkeypatch.setattr(leaguepedia, "placares", nao_pode_baixar)
    dados = pipeline.executar(so_cache=True)
    assert len(dados["jogos"]) == 1
