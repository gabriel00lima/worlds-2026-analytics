from datetime import datetime, timedelta, timezone

from fabricas import quadro_feed

from worlds2026.fontes import livestats

INICIO = datetime(2026, 10, 18, 18, 0, tzinfo=timezone.utc)


def test_arredondar_10s():
    t = datetime(2026, 10, 18, 18, 0, 37, 123456, tzinfo=timezone.utc)
    assert livestats.arredondar_10s(t) == datetime(2026, 10, 18, 18, 0, 30, tzinfo=timezone.utc)


def test_baixar_quadros_para_no_fim_do_jogo(monkeypatch):
    """O feed responde até 1 min de jogo; depois disso, só janelas vazias."""

    def janela(jogo_id, quando=None, rota="window"):
        seg = int((quando - INICIO).total_seconds())
        if seg > 60:
            return None
        estado = "finished" if seg == 60 else "in_game"
        return {"frames": [quadro_feed(f"{seg // 60:02d}:{seg % 60:02d}", estado)]}

    monkeypatch.setattr(livestats, "janela", janela)
    quadros = livestats.baixar_quadros("g1", INICIO)
    assert len(quadros) == 7
    assert quadros[-1]["gameState"] == "finished"
    assert [q["rfc460Timestamp"] for q in quadros] == sorted(q["rfc460Timestamp"] for q in quadros)


def test_baixar_quadros_descarta_o_que_vem_depois_do_fim(monkeypatch):
    def janela(jogo_id, quando=None, rota="window"):
        seg = int((quando - INICIO).total_seconds())
        if seg > 30:
            return None
        return {"frames": [quadro_feed(f"00:{seg:02d}", "finished" if seg >= 20 else "in_game")]}

    monkeypatch.setattr(livestats, "janela", janela)
    assert len(livestats.baixar_quadros("g1", INICIO)) == 3


def test_detalhes_finais_indexa_por_participante(monkeypatch):
    pedidos = []

    def janela(jogo_id, quando=None, rota="window"):
        pedidos.append((quando, rota))
        return {"frames": [{"participants": [{"participantId": 1, "items": [1001]}]}]}

    monkeypatch.setattr(livestats, "janela", janela)
    finais = livestats.detalhes_finais("g1", {"rfc460Timestamp": "2026-10-18T18:28:47.512Z"})
    assert finais == {1: {"participantId": 1, "items": [1001]}}
    assert pedidos == [(INICIO + timedelta(minutes=28, seconds=40), "details")]
