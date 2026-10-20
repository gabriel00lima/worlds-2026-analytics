import resumo


def test_ts_converte_para_datetime_com_fuso():
    assert resumo.ts("2026-10-18T18:00:00Z").utcoffset().total_seconds() == 0
