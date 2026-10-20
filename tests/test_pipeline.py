from worlds2026 import config, pipeline
from worlds2026.arquivos import ler_json, salvar_json


def partida(pid, a, b, vit_a, vit_b, estado="completed"):
    return {
        "id": pid,
        "estado": estado,
        "times": [{"codigo": a, "nome": a, "vitorias": vit_a}, {"codigo": b, "nome": b, "vitorias": vit_b}],
    }


def test_escolher_times_evita_academias_e_times_inativos():
    partidas = [partida("m1", "T1", "GEN", 0, 0)]
    todos = [
        {"id": "t1-academy", "code": "T1", "name": "T1 Academy", "status": "active", "players": [1] * 7},
        {"id": "t1-antigo", "code": "T1", "name": "T1", "status": "archived", "players": [1] * 5},
        {"id": "t1", "code": "T1", "name": "T1", "status": "active", "players": [1] * 5},
        {"id": "gen", "code": "GEN", "name": "Gen.G Esports", "status": "active"},
    ]
    escolhidos = pipeline.escolher_times(partidas, todos)
    assert escolhidos["T1"]["id"] == "t1"
    assert escolhidos["GEN"]["id"] == "gen"


def jogo(pid, vencedor):
    return {"partida": pid, "timeAzul": "id-t1", "timeVermelho": "id-gen", "vencedor": vencedor}


POR_CODIGO = {"T1": {"id": "id-t1"}, "GEN": {"id": "id-gen"}}


def test_conferir_vencedores_sem_divergencia():
    partidas = [partida("m1", "T1", "GEN", 2, 1)]
    jogos = [jogo("m1", "blue"), jogo("m1", "red"), jogo("m1", "blue")]
    assert pipeline.conferir_vencedores(partidas, jogos, POR_CODIGO) == []


def test_conferir_vencedores_aponta_divergencia():
    partidas = [partida("m1", "T1", "GEN", 2, 0)]
    jogos = [jogo("m1", "blue"), jogo("m1", "red")]
    (divergencia,) = pipeline.conferir_vencedores(partidas, jogos, POR_CODIGO)
    assert divergencia.startswith("m1")


def test_conferir_vencedores_ignora_serie_em_andamento():
    partidas = [partida("m1", "T1", "GEN", 1, 0, estado="inProgress")]
    assert pipeline.conferir_vencedores(partidas, [jogo("m1", "red")], POR_CODIGO) == []


def test_montar_times_ordena_titulares_por_rota(monkeypatch):
    monkeypatch.setattr(pipeline.imagens, "miniatura", lambda url, lado, quadrado=False: f"img:{url}")
    time = {
        "id": "id-t1",
        "name": "T1",
        "image": "logo.png",
        "homeLeague": {"name": "LCK", "region": "KOREA"},
        "players": [
            {"id": "sup", "summonerName": "Keria", "role": "support", "image": "keria.png"},
            {"id": "top", "summonerName": "Doran ", "role": "top", "image": "default-headshot.png"},
            {"id": "res", "summonerName": "Reserva", "role": "mid"},
            {"id": "fora", "summonerName": "Nunca jogou", "role": "mid"},
        ],
    }
    jogos = [{"jogadores": [{"jogadorId": "res"}]}]
    times = pipeline.montar_times({"T1": time}, {"T1": ["sup", "top"]}, jogos)
    jogadores = times["T1"]["jogadores"]
    assert [j["id"] for j in jogadores] == ["top", "sup", "res"]
    assert jogadores[0]["nick"] == "Doran" and jogadores[0]["foto"] is None
    assert jogadores[1]["foto"] == "img:keria.png"
    assert times["T1"]["liga"] == "LCK" and times["T1"]["logo"] == "img:logo.png"


def test_montar_campeoes_normaliza_nomes(monkeypatch):
    monkeypatch.setattr(pipeline.imagens, "miniatura", lambda url, lado, quadrado=False: url)
    camp = {"KSante": {"name": "K'Sante"}, "MonkeyKing": {"name": "Wukong"}}
    jogos = [{"jogadores": [{"campeao": "K'Sante"}, {"campeao": "MonkeyKing"}], "lp": None}]
    campeoes = pipeline.montar_campeoes("16.20.1", camp, jogos, {})
    assert campeoes["K'Sante"]["nome"] == "K'Sante"
    assert campeoes["K'Sante"]["icone"].endswith("/champion/KSante.png")
    assert campeoes["MonkeyKing"]["nome"] == "Wukong"


def times_com_doran():
    return {"HLE": {"jogadores": [{"nick": "Doran"}, {"nick": "Sem conta"}]}}


def test_soloq_sem_chave_usa_a_ultima_salva(monkeypatch):
    monkeypatch.setattr(pipeline.riot, "contas_soloq", lambda: {"doran|HLE": ["doran#KR1"]})
    monkeypatch.setattr(config, "RIOT_API_KEY", None)
    salvar_json(config.SOLOQ_PARTIDAS, {"doran|HLE": {"elo": "salvo"}})
    times = times_com_doran()
    pipeline.anexar_soloq(times, so_cache=False)
    doran, sem_conta = times["HLE"]["jogadores"]
    assert doran["soloq"] == {"elo": "salvo"} and doran["contas"] == ["doran#KR1"]
    assert "soloq" not in sem_conta


def test_soloq_com_chave_baixa_e_salva(monkeypatch):
    monkeypatch.setattr(pipeline.riot, "contas_soloq", lambda: {"doran|HLE": ["doran#KR1"]})
    monkeypatch.setattr(config, "RIOT_API_KEY", "chave")
    monkeypatch.setattr(pipeline.riot, "soloq", lambda contas, chave, campeoes: {"doran|HLE": {"elo": "novo"}})
    salvar_json(config.SOLOQ_PARTIDAS, {"doran|HLE": {"elo": "salvo"}})
    times = times_com_doran()
    pipeline.anexar_soloq(times, so_cache=False)
    assert times["HLE"]["jogadores"][0]["soloq"] == {"elo": "novo"}
    assert ler_json(config.SOLOQ_PARTIDAS) == {"doran|HLE": {"elo": "novo"}}


def test_soloq_com_chave_recusada_mantem_a_salva(monkeypatch):
    monkeypatch.setattr(pipeline.riot, "contas_soloq", lambda: {"doran|HLE": ["doran#KR1"]})
    monkeypatch.setattr(config, "RIOT_API_KEY", "chave-vencida")
    monkeypatch.setattr(pipeline.riot, "soloq", lambda contas, chave, campeoes: {})
    salvar_json(config.SOLOQ_PARTIDAS, {"doran|HLE": {"elo": "salvo"}})
    times = times_com_doran()
    pipeline.anexar_soloq(times, so_cache=False)
    assert times["HLE"]["jogadores"][0]["soloq"] == {"elo": "salvo"}
