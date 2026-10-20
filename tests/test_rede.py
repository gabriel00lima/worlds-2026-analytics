import io
import urllib.error

import pytest

from worlds2026 import rede


class Resposta(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def erro_http(codigo):
    return urllib.error.HTTPError("https://x", codigo, "erro", {}, None)


@pytest.fixture(autouse=True)
def sem_espera(monkeypatch):
    monkeypatch.setattr(rede.time, "sleep", lambda s: None)


def test_baixar_json(monkeypatch):
    monkeypatch.setattr(rede.urllib.request, "urlopen", lambda req, timeout: Resposta(b'{"ok": 1}'))
    assert rede.baixar_json("https://x") == {"ok": 1}


def test_baixar_404_retorna_none(monkeypatch):
    def urlopen(req, timeout):
        raise erro_http(404)

    monkeypatch.setattr(rede.urllib.request, "urlopen", urlopen)
    assert rede.baixar("https://x") is None


def test_baixar_tenta_de_novo_apos_falha(monkeypatch):
    respostas = [erro_http(503), urllib.error.URLError("caiu"), Resposta(b"ok")]

    def urlopen(req, timeout):
        r = respostas.pop(0)
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(rede.urllib.request, "urlopen", urlopen)
    assert rede.baixar("https://x") == b"ok"


def test_baixar_desiste_depois_das_tentativas(monkeypatch):
    def urlopen(req, timeout):
        raise erro_http(500)

    monkeypatch.setattr(rede.urllib.request, "urlopen", urlopen)
    with pytest.raises(urllib.error.HTTPError):
        rede.baixar("https://x", tentativas=2)
