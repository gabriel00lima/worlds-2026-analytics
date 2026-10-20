import re


def norm(nome: str | None) -> str:
    """Só letras minúsculas e dígitos, para comparar nomes escritos de jeitos diferentes."""
    return re.sub(r"[^a-z0-9]", "", (nome or "").lower())


def sem_caixa_alta(nome: str | None, pessoa: bool = False) -> str:
    """Corrige nomes que a API manda todos em maiúsculas (TOP ESPORTS, SOOHWAN Kim).

    Times só mudam quando o nome inteiro está em maiúsculas e tem mais de uma palavra, para
    FURIA e LYON ficarem como estão. Nomes de pessoas são corrigidos palavra a palavra.
    """
    nome = nome or ""
    if pessoa:
        return " ".join(
            "-".join(x.capitalize() for x in w.split("-"))
            if len(w) > 2 and w.isupper() and w.replace("-", "").isalpha()
            else w
            for w in nome.split(" ")
        )
    return nome.title() if nome.isupper() and " " in nome else nome
