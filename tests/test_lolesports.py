from worlds2026.fontes import lolesports


def evento(mid, inicio, estado="completed"):
    return {
        "startTime": inicio,
        "state": estado,
        "blockName": "Rodada 1",
        "match": {
            "id": mid,
            "strategy": {"count": 3},
            "teams": [
                {"code": "T1", "name": "T1", "result": {"gameWins": 2, "outcome": "win"}},
                {"code": "GEN", "name": "Gen.G", "result": {"gameWins": 1, "outcome": "loss"}},
            ],
        },
    }


def test_converter_evento():
    p = lolesports.converter_evento(evento("m1", "2026-10-23T17:00:00Z"), "swiss")
    assert p["melhorDe"] == 3 and p["fase"] == "swiss"
    assert p["times"][0] == {"codigo": "T1", "nome": "T1", "vitorias": 2, "resultado": "win"}


def test_agenda_liga_pagina_ordena_e_remove_repetidos(monkeypatch):
    paginas = {
        None: {"events": [evento("m3", "2026-10-20"), evento("m2", "2026-10-15")], "pages": {"older": "tok"}},
        "tok": {"events": [evento("m2", "2026-10-15"), evento("m1", "2026-09-01")], "pages": {"older": "fim"}},
    }
    pedidos = []

    def api_falsa(rota, **params):
        pedidos.append(params.get("pageToken"))
        return {"schedule": paginas[params.get("pageToken")]}

    monkeypatch.setattr(lolesports, "api", api_falsa)
    eventos = lolesports.agenda_liga("liga", ate_data="2026-10-01")
    assert [e["match"]["id"] for e in eventos] == ["m1", "m2", "m3"]
    assert pedidos == [None, "tok"]  # parou ao passar de ate_data
