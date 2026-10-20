import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
for pasta in ("site-worlds", "resumo-diario"):
    sys.path.insert(0, str(RAIZ / pasta))
