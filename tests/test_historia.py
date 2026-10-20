import json

from worlds2026 import config, historia
from worlds2026.fontes import leaguepedia, lolesports


def escrever(caminho, dados):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados), encoding="utf-8")


def test_historia_junta_jogadores_times_e_campeoes(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "MUNDIAIS_PASSADOS", tmp_path / "mp")
    monkeypatch.setattr(config, "CURIOSIDADES", tmp_path / "cur")
    escrever(
        tmp_path / "cur" / "jogadores" / "faker.json",
        {
            "jogador": "Faker",
            "historia": "11º Mundial",
            "mundiais": {
                "titulos": [2013],
                "edicoes": [{"ano": 2013, "time": "SKT", "jogos": 10, "resultado": "campeão"}],
            },
        },
    )
    escrever(
        tmp_path / "mp" / "times-2026-historico.json",
        {"times": {"gen-g": {"titulos": 1, "edicoes": [{"ano": 2017, "nome": "Samsung Galaxy", "jogos": 20}]}}},
    )
    escrever(
        tmp_path / "mp" / "campeoes-por-edicao.json",
        {
            "edicoes": {
                "2013": {"jogos_total": 50, "campeoes": [{"campeao": "Nunu & Willump", "picks": 5, "bans": 2}]},
                "2024": {"jogos_total": 80, "campeoes": [{"campeao": "Campeão que não existe", "picks": 1}]},
            }
        },
    )
    escrever(tmp_path / "mp" / "recordes.json", {"recordes": {"jogadores_mais_titulos": list(range(15))}})

    h = historia.ler_historia({"Nunu": {"name": "Nunu & Willump"}})

    assert h["jogadores"]["faker"]["m"]["titulos"] == [2013]
    assert h["jogadores"]["faker"]["ed"] == [[2013, "SKT", 10, None, None, "campeão", []]]
    assert h["times"]["GEN"]["ed"] == [[2017, "Samsung Galaxy", 20, None, None]]
    assert h["campeoes"] == {"Nunu": {"ed": [[2013, 5, 2, None, 0]]}}
    assert h["recordes"]["jogadores_mais_titulos"] == list(range(10))
    assert h["recordes"]["jogadores_mais_abates"] == []
    assert h["jogosEd"] == {2013: 50, 2024: 80}


def test_historia_sem_dados(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "MUNDIAIS_PASSADOS", tmp_path / "nada")
    assert historia.ler_historia({}) == {"jogadores": {}, "times": {}, "campeoes": {}, "recordes": {}}


def test_historia_com_os_dados_do_repositorio():
    h = historia.ler_historia({"Ahri": {"name": "Ahri"}})
    assert 2013 in h["jogadores"]["faker"]["m"]["titulos"]
    assert "T1" in h["times"] and h["campeoes"]["Ahri"]["ed"]


def test_vod_prefere_portugues_e_estima_o_inicio():
    game = {
        "vods": [
            {"provider": "youtube", "parameter": "en", "locale": "en-US"},
            {"provider": "youtube", "parameter": "pt", "locale": "pt-BR", "startMillis": 0, "endMillis": 3_000_000},
            {"provider": "twitch", "parameter": "x", "locale": "pt-BR"},
        ]
    }
    assert lolesports.vod_do_jogo(game, 1800) == {"yt": "pt", "t0": 3000 - 1800 - 30, "idioma": "pt-BR"}


def test_vod_em_ingles_sem_tempo_e_sem_vod():
    game = {"vods": [{"provider": "youtube", "parameter": "en", "locale": "en-US"}]}
    assert lolesports.vod_do_jogo(game, 1800) == {"yt": "en", "t0": None, "idioma": "en-US"}
    assert lolesports.vod_do_jogo({"vods": None}, 1800) is None


def test_placares_registram_a_ultima_tentativa(monkeypatch):
    assert leaguepedia.ultima_tentativa() is None
    monkeypatch.setattr(leaguepedia, "wikitext", lambda pagina: None)
    monkeypatch.setattr(leaguepedia.time, "sleep", lambda s: None)
    leaguepedia.placares({})
    assert leaguepedia.ultima_tentativa() > 0
