from datetime import datetime, timezone

from worlds2026 import coletor, extras


def quadro(abates_azul=0, abates_verm=0, torres_azul=0, dragoes_azul=(), k=None, d=None):
    """Monta um quadro mínimo no formato que processar_jogo gera."""
    def time(abates, torres, dragoes, kills, deaths):
        return {
            "ouro": 2500, "abates": abates, "torres": torres, "inibidores": 0, "barons": 0,
            "dragoes": list(dragoes),
            "p": [[500, kills[i], deaths[i], 0, 0, 1] for i in range(5)],
        }
    k = k or [0] * 5
    d = d or [0] * 5
    return {
        "blueTeam": time(abates_azul, torres_azul, dragoes_azul, k, [0] * 5),
        "redTeam": time(abates_verm, 0, (), [0] * 5, d),
    }


def test_ts_le_horario_utc():
    assert coletor.ts("2026-10-18T18:00:05Z") == datetime(2026, 10, 18, 18, 0, 5, tzinfo=timezone.utc)


def test_iso_ida_e_volta():
    t = datetime(2026, 11, 14, 20, 30, tzinfo=timezone.utc)
    assert coletor.ts(coletor.iso(t)) == t


def test_diferencas_detecta_abate_com_autor_e_vitima():
    a = quadro()
    b = quadro(abates_azul=1, k=[0, 0, 1, 0, 0], d=[0, 0, 0, 1, 0])
    ev = coletor.diferencas(a, b, 300, None)
    assert ev == [{"s": 300, "tipo": "abate", "lado": "blue", "n": 1, "por": [3], "vitimas": [9]}]


def test_diferencas_detecta_torre_e_dragao():
    a = quadro()
    b = quadro(torres_azul=2, dragoes_azul=["ocean"])
    tipos = sorted(e["tipo"] for e in coletor.diferencas(a, b, 900, None))
    assert tipos == ["dragao", "torre", "torre"]


def test_diferencas_sem_mudanca_nao_gera_evento():
    assert coletor.diferencas(quadro(), quadro(), 60, None) == []


def test_compactar_guarda_um_ponto_a_cada_30s_e_o_ultimo():
    serie = [dict(quadro(), s=s) for s in range(0, 100, 10)]
    pontos = [p[0] for p in coletor.compactar(serie)]
    assert pontos == [0, 30, 60, 90]


def test_norm_ignora_caixa_e_simbolos():

    assert extras.norm("T1 Faker!") == "t1faker"
    assert extras.norm(None) == ""
