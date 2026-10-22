import io
import json
import urllib.error

from worlds2026 import config
from worlds2026.fontes import riot


def test_link_opgg():
    conta = {"game_name": "Hide on bush", "tag_line": "KR1", "platform": "kr"}
    assert riot.link_opgg(conta) == "https://www.op.gg/summoners/kr/Hide%20on%20bush-KR1"
    assert riot.link_opgg({"game_name": "x", "platform": "cn"}) is None


def test_contas_soloq_indexa_por_nick_e_sigla(tmp_path, monkeypatch):
    arq = tmp_path / "contas.json"
    arq.write_text(
        json.dumps(
            {
                "jogadores": [
                    {
                        "jogador": "Faker",
                        "sigla": "t1",
                        "leaguepedia": "https://lol.fandom.com/Faker",
                        "contas": [
                            {
                                "servidor": "KR",
                                "riot_id": "Hide on bush#KR1",
                                "game_name": "Hide on bush",
                                "tag_line": "KR1",
                                "platform": "kr",
                                "regional": "asia",
                                "consultavel_api": "sim",
                            }
                        ],
                    }
                ]
            }
        )
    )
    monkeypatch.setattr(config, "CONTAS_SOLOQ", arq)
    contas = riot.contas_soloq()
    assert list(contas) == ["faker|T1"]
    assert contas["faker|T1"]["contas"][0]["api"] is True
    assert contas["faker|T1"]["links"] == {"leaguepedia": "https://lol.fandom.com/Faker"}


def test_contas_soloq_sem_arquivo(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CONTAS_SOLOQ", tmp_path / "nao-existe.json")
    assert riot.contas_soloq() == {}


def test_soloq_escolhe_a_conta_mais_ativa(monkeypatch):
    respostas = {
        "/riot/account/v1/accounts/by-riot-id/Principal/KR1": {"puuid": "pp"},
        "/riot/account/v1/accounts/by-riot-id/Smurf/KR2": {"puuid": "ps"},
        "/lol/match/v5/matches/by-puuid/pp/ids?queue=420&count=20": ["KR_100"],
        "/lol/match/v5/matches/by-puuid/ps/ids?queue=420&count=20": ["KR_200"],
        "/lol/league/v4/entries/by-puuid/ps": [
            {
                "queueType": "RANKED_SOLO_5x5",
                "tier": "CHALLENGER",
                "rank": "I",
                "leaguePoints": 1500,
                "wins": 90,
                "losses": 60,
            }
        ],
        "/lol/match/v5/matches/KR_200": {
            "info": {
                "gameEndTimestamp": 1,
                "gameDuration": 1800,
                "participants": [
                    {
                        "puuid": "ps",
                        "championName": "Azir",
                        "win": True,
                        "kills": 5,
                        "deaths": 1,
                        "assists": 7,
                        "totalMinionsKilled": 300,
                        "neutralMinionsKilled": 12,
                        "totalDamageDealtToChampions": 25000,
                        "goldEarned": 13000,
                        "teamPosition": "MIDDLE",
                    }
                ],
            }
        },
        "/lol/champion-mastery/v4/champion-masteries/by-puuid/ps/top?count=5": [
            {"championId": 268, "championLevel": 50, "championPoints": 900000}
        ],
        "/lol/spectator/v5/active-games/by-summoner/ps": {
            "gameQueueConfigId": 420,
            "gameStartTime": 1234,
            "participants": [{"puuid": "ps", "championId": 61}],
        },
    }
    monkeypatch.setattr(riot.ClienteRiot, "get", lambda self, regiao, caminho: respostas.get(caminho))

    def conta(nome, tag):
        return {
            "riotId": f"{nome}#{tag}",
            "gameName": nome,
            "tagLine": tag,
            "api": True,
            "servidor": "KR",
            "regional": "asia",
            "platform": "kr",
            "link": None,
        }

    contas = {"faker|T1": {"contas": [conta("Principal", "KR1"), conta("Smurf", "KR2")]}}
    campeoes = {"268": "Azir", "61": "Orianna"}
    resultado = riot.soloq(contas, "chave", campeoes)["faker|T1"]
    assert resultado["conta"] == "Smurf#KR2"
    assert resultado["elo"]["tier"] == "CHALLENGER"
    assert resultado["partidas"] == [[1, 1800, "Azir", True, 5, 1, 7, 312, 25000, 13000, "MIDDLE"]]
    assert resultado["maestria"] == [["Azir", 50, 900000]]
    assert resultado["agora"]["camp"] == "Orianna" and resultado["agora"]["inicio"] == 1234
    assert [p[1:4] for p in resultado["hist"]] == [["CHALLENGER", "I", 1500]]

    # numa nova coleta com o mesmo elo o histórico não ganha ponto repetido
    assert len(riot.soloq(contas, "chave", campeoes)["faker|T1"]["hist"]) == 1


def test_soloq_para_quando_a_chave_e_recusada(monkeypatch):
    def recusa(self, regiao, caminho):
        raise riot.ChaveRecusada("expirada")

    monkeypatch.setattr(riot.ClienteRiot, "get", recusa)
    contas = {"x|Y": {"contas": [{"riotId": "a#b", "gameName": "a", "tagLine": "b", "api": True, "regional": "asia"}]}}
    assert riot.soloq(contas, "chave", {}) == {}
    # o cache é salvo mesmo quando a coleta para no meio
    assert (config.CACHE / "soloq.json").exists()


def test_historico_registra_mudanca_de_pdl_e_guarda_so_os_ultimos():
    cache: dict = {"hist": {}}
    for i in range(40):
        riot._historico(cache, "x", {"tier": "MASTER", "rank": "I", "leaguePoints": i}, i)
    riot._historico(cache, "x", {"tier": "MASTER", "rank": "I", "leaguePoints": 39}, 99)
    hist = cache["hist"]["x"]
    assert len(hist) == 30 and hist[-1] == [39, "MASTER", "I", 39, None, None]


def test_partida_ao_vivo_ignora_outras_filas(monkeypatch):
    monkeypatch.setattr(
        riot.ClienteRiot, "get", lambda self, regiao, caminho: {"gameQueueConfigId": 450, "participants": []}
    )
    assert riot._partida_ao_vivo(riot.ClienteRiot("c"), "kr", "p", {}, 0) is None


def test_cliente_tenta_de_novo_quando_a_rede_falha(monkeypatch):
    tentativas = []

    def urlopen(req, timeout):
        tentativas.append(req.full_url)
        if len(tentativas) < 3:
            raise urllib.error.URLError("conexão recusada")
        return io.BytesIO(b'{"ok": true}')

    monkeypatch.setattr(riot.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(riot.time, "sleep", lambda s: None)
    assert riot.ClienteRiot("c").get("kr", "/x") == {"ok": True}
    assert len(tentativas) == 3


def test_puuid_de_outra_chave_e_buscado_de_novo(monkeypatch):
    """O puuid é cifrado por chave: o salvo com a chave antiga dá HTTP 400 e precisa ser trocado."""
    chamadas = []

    def get(self, regiao, caminho):
        chamadas.append(caminho)
        self.status = None
        if caminho.startswith("/riot/account"):
            return {"puuid": "novo"}
        if "by-puuid/velho/" in caminho:
            self.status = 400
            return None
        return ["KR_1"]

    monkeypatch.setattr(riot.ClienteRiot, "get", get)
    cache = {"puuid": {"a#KR1": "velho"}, "partidas": {}}
    conta = {"riotId": "a#KR1", "gameName": "a", "tagLine": "KR1", "regional": "asia"}
    assert riot._partidas_recentes(riot.ClienteRiot("c"), conta, cache) == ("novo", ["KR_1"])
    assert cache["puuid"]["a#KR1"] == "novo"
    assert len(chamadas) == 3


def test_http_400_nao_tenta_de_novo(monkeypatch):
    tentativas = []

    def urlopen(req, timeout):
        tentativas.append(1)
        raise urllib.error.HTTPError(req.full_url, 400, "Bad Request", {}, None)

    monkeypatch.setattr(riot.urllib.request, "urlopen", urlopen)
    cliente = riot.ClienteRiot("c")
    assert cliente.get("kr", "/x") is None
    assert len(tentativas) == 1 and cliente.status == 400 and cliente.falhas == 1
