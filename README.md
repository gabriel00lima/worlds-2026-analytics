# Central do Worlds 2026

Site com as chaves, estatísticas e replays do Mundial de League of Legends 2026, em português e no horário de Brasília.

**Site:** https://gabriel00lima.github.io/worlds-2026-analytics/

![Página inicial](docs/img/inicio.png)

## Sobre

Comecei esse projeto porque queria acompanhar o Worlds num lugar só: ver a chave, abrir um confronto e entender o que aconteceu no jogo sem precisar rever a transmissão inteira.

A parte em Python busca os dados na API do LoL Esports, processa a linha do tempo de cada partida e gera uma página estática com tudo embutido. Clicando num confronto dá para ver a prévia, os números de cada jogador e um replay animado com os principais lances narrados.

![Replay de Karmine Corp x MVK](docs/img/replay.png)

## Estrutura

```
src/worlds2026/
  coletor.py      busca agenda, times e partidas, processa os jogos e monta o site
  extras.py       bans da Leaguepedia e partidas de solo queue pela API da Riot
  config.py       caminhos do projeto
web/
  modelo.html     o site (HTML, CSS e JavaScript), onde os dados são injetados
data/
  curiosidades/   histórico e curiosidades de cada time e confronto
  soloq/          contas de solo queue dos jogadores
scripts/
  gerar_curiosidades.py
tests/
docs/             site publicado no GitHub Pages
```

## Como funciona

O `coletor.py` baixa a agenda, os times, os elencos e o estado de cada jogo, que o feed da Riot entrega de 10 em 10 segundos. Como o feed não diz o que aconteceu, os abates, torres e dragões são encontrados comparando um quadro com o seguinte. Os downloads rodam em paralelo e ficam em cache, então só o que é novo é baixado de novo.

O `extras.py` complementa com os bans da Leaguepedia e, se houver uma `RIOT_API_KEY` no ambiente, com as partidas de solo queue dos jogadores.

O site é HTML, CSS e JavaScript sem framework. Os dados entram no `web/modelo.html` e saem num único `docs/index.html`, que o GitHub Pages publica.

![Prévia de Gen.G x Invictus Gaming](docs/img/previa.png)

## Rodando

```bash
pip install -e ".[dev]"
python -m worlds2026            # coleta os dados e atualiza docs/index.html
python -m worlds2026 --so-site  # só regera o site com o que já está em cache
pytest
```

## Limitações

O feed não manda a posição dos jogadores, então no replay eles aparecem na rota em que jogam, não no ponto exato do mapa. As contas de solo queue vêm da Leaguepedia, que é mantida pela comunidade e às vezes está desatualizada.

---

Projeto pessoal, sem ligação com a Riot Games. Licença MIT.
