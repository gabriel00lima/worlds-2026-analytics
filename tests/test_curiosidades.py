import json

from worlds2026 import config, curiosidades


def test_ler_curiosidades(tmp_path, monkeypatch):
    (tmp_path / "times").mkdir()
    (tmp_path / "confrontos").mkdir()
    (tmp_path / "times" / "gen-g.json").write_text(json.dumps({"id": "gen-g", "seed": "LCK 1", "extra": "x"}))
    (tmp_path / "confrontos" / "r1.json").write_text(
        json.dumps({"time_a": {"id": "t1"}, "time_b": {"id": "gen-g"}, "manchete": "Clássico"})
    )
    monkeypatch.setattr(config, "CURIOSIDADES", tmp_path)

    dados = curiosidades.ler_curiosidades()
    assert dados["times"]["GEN"]["seed"] == "LCK 1"
    assert "extra" not in dados["times"]["GEN"]
    assert dados["confrontos"][0]["times"] == ["GEN", "T1"]
    assert dados["confrontos"][0]["manchete"] == "Clássico"


def test_sem_pasta(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CURIOSIDADES", tmp_path / "nada")
    assert curiosidades.ler_curiosidades() == {"times": {}, "confrontos": []}


def test_curiosidades_sobre_apostas_ficam_de_fora(tmp_path, monkeypatch):
    (tmp_path / "times").mkdir()
    (tmp_path / "confrontos").mkdir()
    curios = [{"texto": "Favorita nas casas de apostas"}, {"texto": "Odds de 1.5"}, {"texto": "Estreia no Mundial"}]
    (tmp_path / "times" / "t1.json").write_text(json.dumps({"id": "t1", "curiosidades": curios}))
    monkeypatch.setattr(config, "CURIOSIDADES", tmp_path)
    assert curiosidades.ler_curiosidades()["times"]["T1"]["curiosidades"] == [{"texto": "Estreia no Mundial"}]
