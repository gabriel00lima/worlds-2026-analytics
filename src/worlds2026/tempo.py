from datetime import datetime


def iso(t: datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def ts(texto: str) -> datetime:
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))
