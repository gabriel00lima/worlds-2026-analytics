import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from worlds2026.api import banco, carga
from worlds2026.api.app import criar_app

ROTAS = ["top", "jungle", "mid", "bottom", "support"]


def time(codigo, id_api, nicks, soloq=None):
    return {
        "id": id_api,
        "codigo": codigo,
        "nome": codigo,
        "liga": "LCK",
        "regiao": "KOREA",
        "jogadores": [
            {
                "id": f"{codigo}-{i}",
                "nick": nick,
                "nome": None,
                "rota": ROTAS[i],
                "titular": True,
                "soloq": soloq if i == 2 else None,
            }
            for i, nick in enumerate(nicks)
        ],
    }


def jogo(jid, campeoes_azul, campeoes_verm, vencedor, abates_mid_azul, bans=None):
    jogadores = []
    for lado, codigo, campeoes in (("blue", "T1", campeoes_azul), ("red", "GEN", campeoes_verm)):
        for i, campeao in enumerate(campeoes):
            pid = i + 1 if lado == "blue" else i + 6
            jogadores.append(
                {
                    "pid": pid,
                    "lado": lado,
                    "jogadorId": f"{codigo}-{i}",
                    "nick": f"{codigo}{i}",
                    "campeao": campeao,
                    "rota": ROTAS[i],
                    "danoTotal": 10000 + 1000 * i,
                }
            )
    finais = [[10000, abates_mid_azul if p == 2 else 1, 2, 3, 200, 18] for p in range(10)]
    return {
        "id": jid,
        "partida": "m1",
        "numero": int(jid[-1]),
        "patch": "16.20",
        "timeAzul": "id-t1",
        "timeVermelho": "id-gen",
        "duracao": 1800,
        "vencedor": vencedor,
        "jogadores": jogadores,
        "serie": [[1800, 50000, 48000, finais]],
        "lp": {"bans": bans} if bans else None,
    }


def dados_exemplo():
    soloq = {
        "elo": {"tier": "CHALLENGER", "rank": "I", "leaguePoints": 1200},
        "partidas": [
            [1791538149565, 1579, "Azir", True, 5, 1, 7, 300],
            [1791519902553, 1874, "Azir", False, 2, 4, 3, 250],
            [1791384065583, 2040, "Ahri", True, 9, 0, 4, 280],
        ],
    }
    campeoes_t1 = ["Gnar", "Vi", "Azir", "Jinx", "Nami"]
    campeoes_gen = ["Renekton", "Sejuani", "Orianna", "Kaisa", "Rell"]
    return {
        "times": {
            "T1": time("T1", "id-t1", ["Zeus", "Oner", "Faker", "Gumayusi", "Keria"], soloq),
            "GEN": time("GEN", "id-gen", ["Kiin", "Canyon", "Chovy", "Ruler", "Duro"]),
        },
        "partidas": [
            {
                "id": "m1",
                "inicio": "2026-10-23T17:00:00Z",
                "estado": "completed",
                "fase": "swiss",
                "bloco": "R1",
                "melhorDe": 3,
                "times": [
                    {"codigo": "T1", "vitorias": 2, "resultado": "win"},
                    {"codigo": "GEN", "vitorias": 1, "resultado": "loss"},
                ],
            },
            {
                "id": "m2",
                "inicio": "2026-10-25T17:00:00Z",
                "estado": "unstarted",
                "fase": "swiss",
                "bloco": "R3",
                "melhorDe": 1,
                "times": [{"codigo": "T1", "vitorias": 0}, {"codigo": "TBD", "vitorias": 0}],
            },
        ],
        "jogos": [
            jogo("g1", campeoes_t1, campeoes_gen, "blue", 7, {"blue": ["Yone", "Kalista"], "red": ["Yone"]}),
            jogo(
                "g2", ["Gnar", "Vi", "Ahri", "Jinx", "Nami"], campeoes_gen, "red", 2, {"blue": ["Kalista"], "red": []}
            ),
            jogo("g3", campeoes_t1, campeoes_gen, "blue", 4),
        ],
    }


@pytest.fixture
def cliente(engine):
    carga.carregar(engine, dados_exemplo())
    fabrica = sessionmaker(bind=engine, expire_on_commit=False)

    def sessao_de_teste():
        with fabrica() as s:
            yield s

    app = criar_app()
    app.dependency_overrides[banco.sessao] = sessao_de_teste
    return TestClient(app)


def test_saude(cliente):
    assert cliente.get("/saude").json() == {"status": "ok"}


def test_carga_conta_linhas(engine):
    contagem = carga.carregar(engine, dados_exemplo())
    assert contagem == {
        "times": 2,
        "jogadores": 10,
        "partidas": 2,
        "jogos": 3,
        "participacoes": 30,
        "bans": 4,
        "partidas_soloq": 3,
    }
    # recarregar substitui em vez de duplicar
    assert carga.carregar(engine, dados_exemplo())["participacoes"] == 30


def test_listar_partidas_com_filtros(cliente):
    assert [p["id"] for p in cliente.get("/partidas").json()] == ["m1", "m2"]
    assert [p["id"] for p in cliente.get("/partidas", params={"estado": "completed"}).json()] == ["m1"]
    assert [p["id"] for p in cliente.get("/partidas", params={"time": "gen"}).json()] == ["m1"]
    assert cliente.get("/partidas").json()[0]["inicio"] == "2026-10-23T17:00:00Z"


def test_detalhe_da_partida_traz_jogos_e_bans(cliente):
    p = cliente.get("/partidas/m1").json()
    assert p["vencedor"] == "T1"
    assert [j["vencedor"] for j in p["jogos"]] == ["T1", "GEN", "T1"]
    assert len(p["jogos"][0]["participacoes"]) == 10
    assert {"time_codigo": "T1", "campeao": "Kalista"} in p["jogos"][0]["bans"]


def test_partida_inexistente(cliente):
    assert cliente.get("/partidas/nao-existe").status_code == 404


def test_times_com_campanha(cliente):
    times = {t["codigo"]: t for t in cliente.get("/times").json()}
    assert (times["T1"]["vitorias"], times["T1"]["derrotas"]) == (2, 1)
    assert (times["GEN"]["vitorias"], times["GEN"]["derrotas"]) == (1, 2)


def test_detalhe_do_time(cliente):
    t = cliente.get("/times/t1").json()
    assert [j["nick"] for j in t["jogadores"]] == ["Zeus", "Oner", "Faker", "Gumayusi", "Keria"]
    assert t["mais_banidos_pelo_time"][0] == {"campeao": "Kalista", "bans": 2}
    assert t["mais_banidos_contra"] == [{"campeao": "Yone", "bans": 1}]
    assert {"campeao": "Azir", "jogos": 2, "vitorias": 2} in t["campeoes"]


def test_detalhe_do_jogador_com_torneio_e_soloq(cliente):
    j = cliente.get("/jogadores/T1-2").json()
    assert j["nick"] == "Faker" and j["elo"] == "Challenger I" and j["pdl"] == 1200
    assert j["torneio"]["jogos"] == 3 and j["torneio"]["vitorias"] == 2
    assert j["torneio"]["abates"] == 13
    assert j["torneio"]["kda"] == round((13 + 9) / 6, 2)
    assert j["torneio"]["cs_por_minuto"] == round(600 / 90, 1)
    assert j["campeoes_torneio"][0] == {"campeao": "Azir", "jogos": 2, "vitorias": 2}
    assert j["campeoes_soloq"][0] == {"campeao": "Azir", "jogos": 2, "vitorias": 1}


def test_jogador_sem_jogos(cliente, monkeypatch):
    assert cliente.get("/jogadores/nao-existe").status_code == 404


def test_buscar_jogador_por_nick(cliente):
    assert [j["id"] for j in cliente.get("/jogadores", params={"nick": "fak"}).json()] == ["T1-2"]


def test_ranking_de_abates(cliente):
    ranking = cliente.get("/estatisticas/jogadores", params={"limite": 1}).json()
    assert ranking[0]["nick"] == "T12" and ranking[0]["abates"] == 13


def test_ranking_por_dano(cliente):
    ranking = cliente.get("/estatisticas/jogadores", params={"ordenar": "dano", "limite": 2}).json()
    assert [r["dano_por_jogo"] for r in ranking] == [14000.0, 14000.0]


def test_ranking_valida_parametros(cliente):
    assert cliente.get("/estatisticas/jogadores", params={"ordenar": "ouro"}).status_code == 422
    assert cliente.get("/estatisticas/jogadores", params={"limite": 0}).status_code == 422


def test_campeoes_por_presenca(cliente):
    campeoes = {c["campeao"]: c for c in cliente.get("/estatisticas/campeoes", params={"limite": 50}).json()}
    assert campeoes["Gnar"]["escolhas"] == 3 and campeoes["Gnar"]["presenca"] == 1.0
    assert campeoes["Kalista"] == {"campeao": "Kalista", "escolhas": 0, "vitorias": 0, "bans": 2, "presenca": 0.667}
    assert campeoes["Azir"]["vitorias"] == 2
