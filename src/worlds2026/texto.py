import re


def norm(nome: str | None) -> str:
    """Só letras minúsculas e dígitos, para comparar nomes escritos de jeitos diferentes."""
    return re.sub(r"[^a-z0-9]", "", (nome or "").lower())
