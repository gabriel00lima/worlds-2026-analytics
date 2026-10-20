from worlds2026.texto import sem_caixa_alta


def test_times_so_mudam_com_nome_todo_em_maiusculas_e_composto():
    assert sem_caixa_alta("TOP ESPORTS") == "Top Esports"
    assert sem_caixa_alta("FURIA") == "FURIA"
    assert sem_caixa_alta("Gen.G Esports") == "Gen.G Esports"
    assert sem_caixa_alta(None) == ""


def test_pessoas_mudam_palavra_a_palavra():
    assert sem_caixa_alta("SOOHWAN Kim", pessoa=True) == "Soohwan Kim"
    assert sem_caixa_alta("Lee SANG-HYEOK", pessoa=True) == "Lee Sang-Hyeok"
    assert sem_caixa_alta("Jo HE", pessoa=True) == "Jo HE"
