from worlds2026.fontes import leaguepedia

CHAMPS = ["Gnar", "Vi", "Ahri", "Jinx", "Nami", "Renekton", "Sejuani", "Orianna", "Kai'Sa", "Rell"]


def jogador_wt(lado, i, campeao, dano):
    return (
        f"|{lado}{i}={{{{Scoreboard/Player|champion={campeao}|damagetochamps={dano}"
        f"|visionscore=20|runes={{{{Runes|x}}}}}}}}\n"
    )


def placar_wt(vencedor="1"):
    cab = (
        f"{{{{Scoreboard/Season|winner={vencedor}|team1ban1=Yone|team1ban2=None|team2ban1=Loss of Ban"
        "|team2ban2=Kaisa|team1rh=1|team2rh=0|team1vg=3|team2vg=x\n"
    )
    jog = "".join(jogador_wt("blue", i + 1, c, 1000 * (i + 1)) for i, c in enumerate(CHAMPS[:5]))
    jog += "".join(jogador_wt("red", i + 1, c, 500) for i, c in enumerate(CHAMPS[5:]))
    return cab + jog + "}}"


CHAVE_POR_NOME = {"kaisa": "Kaisa"}


def test_campos_mantem_primeira_ocorrencia():
    assert leaguepedia.campos("|a=1|b= 2 |a=3") == {"a": "1", "b": "2"}


def test_ler_placares_extrai_bans_objetivos_e_dano():
    jogos = leaguepedia.ler_placares(placar_wt(), CHAVE_POR_NOME)
    (jogo,) = jogos.values()
    assert jogo["vencedor"] == "blue"
    assert jogo["bans"] == {"blue": ["Yone"], "red": ["Kaisa"]}
    assert jogo["arautos"] == {"blue": 1, "red": 0}
    assert jogo["larvas"] == {"blue": 3, "red": None}
    assert jogo["jogadores"]["ahri"] == {"danoTotal": 3000, "visao": 20}
    assert "kaisa" in jogo["jogadores"]


def test_ler_placares_ignora_placar_incompleto():
    incompleto = placar_wt().split("|red1=")[0] + "}}"
    assert leaguepedia.ler_placares(incompleto, {}) == {}


def test_enriquecer_jogos_casa_pelos_campeoes_e_corrige_vencedor():
    lp = leaguepedia.ler_placares(placar_wt(vencedor="2"), CHAVE_POR_NOME)
    nomes = CHAMPS[:8] + ["Kaisa", "Rell"]
    jogo = {"id": "g1", "vencedor": "blue", "jogadores": [{"campeao": c} for c in nomes]}
    leaguepedia.enriquecer_jogos([jogo], lp)
    assert jogo["vencedor"] == "red"
    assert jogo["lp"]["bans"]["blue"] == ["Yone"]
    assert jogo["jogadores"][2]["danoTotal"] == 3000


def test_enriquecer_jogos_sem_correspondencia():
    jogo = {"id": "g2", "vencedor": "red", "jogadores": [{"campeao": "Teemo"}]}
    leaguepedia.enriquecer_jogos([jogo], {})
    assert jogo["lp"] is None and jogo["vencedor"] == "red"


def test_wikitext_pagina_inexistente(monkeypatch):
    monkeypatch.setattr(leaguepedia.rede, "baixar_json", lambda url: {"error": {"code": "missingtitle"}})
    assert leaguepedia.wikitext("Pagina") is None
