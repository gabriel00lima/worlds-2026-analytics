"""Grava a narração dos replays com voz neural (Microsoft Edge TTS, pt-BR).

Os roteiros saem do próprio site: o docs/index.html é aberto num navegador sem rede e a
mesma função que o site usa para narrar devolve as falas de cada jogo. Cada jogo vira um
mp3 em docs/audio/<id>.mp3, e o docs/audio/index.json guarda o início e a duração de cada
fala. Só regrava os jogos cujo roteiro mudou. Depois, `python -m worlds2026 --so-site`
embute o índice no site.

Precisa de `pip install -e ".[narracao]"` e do Playwright para Node (`npm i -g playwright`).
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import edge_tts

RAIZ = Path(__file__).resolve().parents[1]
SITE = RAIZ / "docs" / "index.html"
PASTA = RAIZ / "docs" / "audio"
VOZ = "pt-BR-AntonioNeural"
KBPS = 48  # o serviço devolve mp3 mono 24 kHz a 48 kbit/s, taxa constante: dá para medir a duração pelo tamanho

EXPORTAR = r"""
const fs = require("fs");
const { chromium } = require("playwright");
(async () => {
  const navegador = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
  const pagina = await navegador.newPage();
  await pagina.route(/^https?:/, (r) => r.abort());
  // servido como UTF-8; aberto via file:// os acentos poderiam ser lidos errado
  await pagina.route("http://local/index.html", (r) =>
    r.fulfill({ body: fs.readFileSync(process.argv[2]), contentType: "text/html; charset=utf-8" }),
  );
  await pagina.goto("http://local/index.html");
  await pagina.waitForFunction(() => window.__roteiros);
  process.stdout.write(JSON.stringify(await pagina.evaluate(() => window.__roteiros())));
  await navegador.close();
})();
"""


def roteiros() -> list[dict]:
    raiz_global = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(EXPORTAR)
    try:
        saida = subprocess.run(
            ["node", f.name, str(SITE)],
            capture_output=True,
            text=True,
            timeout=180,
            env={**os.environ, "NODE_PATH": os.environ.get("NODE_PATH", raiz_global)},
        )
    finally:
        os.remove(f.name)
    if saida.returncode:
        sys.exit("não consegui ler os roteiros: " + saida.stderr[-400:])
    return json.loads(saida.stdout)


async def gravar(texto: str, empolgado: bool) -> bytes:
    voz = edge_tts.Communicate(
        texto,
        VOZ,
        rate="+18%" if empolgado else "+10%",
        pitch="+6Hz" if empolgado else "+0Hz",
        proxy=os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"),
    )
    audio = b""
    async for parte in voz.stream():
        if parte["type"] == "audio":
            audio += parte["data"]
    return audio


async def main() -> None:
    PASTA.mkdir(parents=True, exist_ok=True)
    arq = PASTA / "index.json"
    indice = json.loads(arq.read_text()) if arq.exists() else {}
    for r in roteiros():
        falas = [f["txt"] for f in r["falas"]]
        mp3 = PASTA / f"{r['id']}.mp3"
        if r["id"] in indice and [f[0] for f in indice[r["id"]]["falas"]] == falas and mp3.exists():
            continue
        dados, marcas, inicio = b"", [], 0.0
        for f in r["falas"]:
            audio = await gravar(f["txt"], f["hype"])
            duracao = len(audio) * 8 / (KBPS * 1000)
            marcas.append([f["txt"], round(inicio, 3), round(duracao, 3)])
            dados += audio
            inicio += duracao
        mp3.write_bytes(dados)
        indice[r["id"]] = {"falas": marcas}
        arq.write_text(json.dumps(indice, ensure_ascii=False))
        print(f"{r['id']}: {len(marcas)} falas, {inicio:.0f} s")
    print(f"{len(indice)} jogos com narração gravada")


if __name__ == "__main__":
    asyncio.run(main())
