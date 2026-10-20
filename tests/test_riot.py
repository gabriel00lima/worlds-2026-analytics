import json

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
        "/lol/match/v5/matches/by-puuid/pp/ids?queue=420&count=10": ["KR_100"],
        "/lol/match/v5/matches/by-puuid/ps/ids?queue=420&count=10": ["KR_200"],
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
                    }
                ],
            }
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
    resultado = riot.soloq(contas, "chave")["faker|T1"]
    assert resultado["conta"] == "Smurf#KR2"
    assert resultado["elo"]["tier"] == "CHALLENGER"
    assert resultado["partidas"] == [[1, 1800, "Azir", True, 5, 1, 7, 312]]


def test_soloq_para_quando_a_chave_e_recusada(monkeypatch):
    def recusa(self, regiao, caminho):
        raise riot.ChaveRecusada("expirada")

    monkeypatch.setattr(riot.ClienteRiot, "get", recusa)
    contas = {"x|Y": {"contas": [{"riotId": "a#b", "gameName": "a", "tagLine": "b", "api": True, "regional": "asia"}]}}
    assert riot.soloq(contas, "chave") == {}
