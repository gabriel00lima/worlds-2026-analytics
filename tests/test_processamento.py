from fabricas import jogador, quadro_feed, time_feed

from worlds2026 import processamento as proc


def resumo(**kw):
    return proc.resumo_quadro(quadro_feed("00:00", **kw))


def test_resumo_quadro_extrai_times_e_jogadores():
    r = resumo(azul=time_feed(ouro=3000, abates=2, dragoes=["ocean"]))
    assert r["blueTeam"]["ouro"] == 3000
    assert r["blueTeam"]["dragoes"] == ["ocean"]
    assert r["blueTeam"]["p"][0] == [500, 0, 0, 0, 0, 1]
    assert len(r["redTeam"]["p"]) == 5


def test_relogio_de_jogo_ignora_pausas():
    quadros = [
        quadro_feed("00:00"),
        quadro_feed("00:10", "paused"),
        quadro_feed("05:10"),  # 5 minutos de pausa técnica
        quadro_feed("05:20"),
    ]
    tempos = [s for s, _ in proc.relogio_de_jogo(quadros)]
    assert tempos == [0, 10, 10, 20]


def test_diferencas_abate_com_autor_e_vitima():
    a = resumo()
    jog_azul = [jogador(k=1 if i == 2 else 0) for i in range(5)]
    jog_verm = [jogador(d=1 if i == 3 else 0) for i in range(5)]
    b = resumo(azul=time_feed(abates=1, jogadores=jog_azul), vermelho=time_feed(jogadores=jog_verm))
    assert proc.diferencas(a, b, 300) == [
        {"s": 300, "tipo": "abate", "lado": "blue", "n": 1, "por": [3], "vitimas": [9]}
    ]


def test_diferencas_abate_do_lado_vermelho_numera_de_6_a_10():
    a = resumo()
    jog_verm = [jogador(k=1 if i == 0 else 0) for i in range(5)]
    jog_azul = [jogador(d=1 if i == 4 else 0) for i in range(5)]
    b = resumo(azul=time_feed(jogadores=jog_azul), vermelho=time_feed(abates=1, jogadores=jog_verm))
    (ev,) = proc.diferencas(a, b, 60)
    assert (ev["lado"], ev["por"], ev["vitimas"]) == ("red", [6], [5])


def test_diferencas_objetivos():
    b = resumo(azul=time_feed(torres=2, dragoes=["ocean"]), vermelho=time_feed(barons=1))
    tipos = sorted(e["tipo"] for e in proc.diferencas(resumo(), b, 900))
    assert tipos == ["barao", "dragao", "torre", "torre"]


def test_diferencas_sem_mudanca():
    assert proc.diferencas(resumo(), resumo(), 60) == []


def test_compactar_mantem_um_ponto_a_cada_30s_e_o_ultimo():
    serie = [{"s": s, **resumo()} for s in range(0, 100, 10)]
    assert [p[0] for p in proc.compactar(serie)] == [0, 30, 60, 90]


def test_estimar_vencedor_prioriza_inibidores_sobre_ouro():
    final = {
        "blueTeam": {"inibidores": 1, "torres": 5, "ouro": 40000},
        "redTeam": {"inibidores": 0, "torres": 8, "ouro": 60000},
    }
    assert proc.estimar_vencedor(final) == "blue"


def test_nick_sem_sigla():
    assert proc.nick_sem_sigla("T1 Faker") == "Faker"
    assert proc.nick_sem_sigla(" Loki Bin ") == "Bin"
    assert proc.nick_sem_sigla("Canyon") == "Canyon"


def test_montar_jogo_completo(meta_jogo):
    jog_azul = [jogador(ouro=3000, k=3 if i == 1 else 0) for i in range(5)]
    jog_verm = [jogador(d=1) if i < 3 else jogador() for i in range(5)]
    quadros = [
        quadro_feed("00:00", azul=time_feed(ouro=0), vermelho=time_feed(ouro=0)),  # carregamento
        quadro_feed("00:10"),
        quadro_feed(
            "10:10",
            azul=time_feed(ouro=15000, abates=3, torres=11, inibidores=2, jogadores=jog_azul),
            vermelho=time_feed(ouro=9000, jogadores=jog_verm),
        ),
        quadro_feed(
            "10:20",
            "finished",
            azul=time_feed(ouro=15000, abates=3, torres=11, inibidores=2, jogadores=jog_azul),
            vermelho=time_feed(ouro=9000, jogadores=jog_verm),
        ),
    ]
    finais = {1: {"championDamageShare": 0.3, "items": [3031], "perkMetadata": {"perks": [8005, 1]}}}

    jogo = proc.montar_jogo("g1", "m1", 1, meta_jogo, quadros, finais)

    assert jogo["patch"] == "16.20"
    assert jogo["duracao"] == 610
    assert jogo["vencedor"] == "blue"
    assert (jogo["timeAzul"], jogo["timeVermelho"]) == ("azul", "verm")
    abates = [e for e in jogo["eventos"] if e["tipo"] == "abate"]
    assert abates == [{"s": 600, "tipo": "abate", "lado": "blue", "n": 3, "por": [2], "vitimas": [6, 7, 8]}]
    assert sum(e["tipo"] == "torre" for e in jogo["eventos"]) == 11
    primeiro = jogo["jogadores"][0]
    assert (primeiro["nick"], primeiro["dano"], primeiro["itens"], primeiro["runas"]) == (
        "Jogador1",
        0.3,
        [3031],
        [8005],
    )
    assert jogo["jogadores"][5]["lado"] == "red"
