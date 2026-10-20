"""Requisições HTTP com novas tentativas."""

import json
import logging
import time
import urllib.error
import urllib.request
from typing import Any

log = logging.getLogger(__name__)

USER_AGENT = "worlds2026-analytics/1.0 (+https://github.com/gabriel00lima/worlds-2026-analytics)"
SEM_CONTEUDO = (204, 404)


def baixar(url: str, cabecalhos: dict[str, str] | None = None, tentativas: int = 4) -> bytes | None:
    """Retorna o corpo da resposta, ou None quando o recurso não existe ou veio vazio."""
    h = {"User-Agent": USER_AGENT, **(cabecalhos or {})}
    for i in range(1, tentativas + 1):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r:
                return r.read() or None
        except urllib.error.HTTPError as e:
            if e.code in SEM_CONTEUDO:
                return None
            if i == tentativas:
                raise
            log.debug("HTTP %s em %s, tentativa %d", e.code, url, i)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if i == tentativas:
                raise
            log.debug("%s em %s, tentativa %d", e, url, i)
        time.sleep(1.5 * i)
    return None


def baixar_json(url: str, cabecalhos: dict[str, str] | None = None, tentativas: int = 4) -> Any:
    corpo = baixar(url, cabecalhos, tentativas)
    return json.loads(corpo) if corpo else None
