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
  fontes/           um cliente para cada fonte: LoL Esports, feed livestats, Leaguepedia, Riot, Data Dragon
  processamento.py  transforma os quadros do feed em lances, série de ouro e estatísticas
  pipeline.py       as etapas da coleta, da agenda até o site pronto
  site.py           junta o template, o CSS, o JS e os dados num único index.html
  cli.py            linha de comando
web/                o site: index.html, estilo.css e app.js
data/               curiosidades dos confrontos e contas de solo queue
scripts/            gerador das curiosidades
tests/              testes com pytest, incluindo uma coleta completa com as fontes simuladas
docs/               site publicado no GitHub Pages
```

## Como funciona

O feed da Riot entrega o estado de cada jogo de 10 em 10 segundos, mas não diz o que aconteceu. O `processamento.py` encontra os abates, torres e dragões comparando um quadro com o seguinte e desconta as pausas técnicas do relógio. Essa parte não acessa a rede, o que deixa fácil de testar.

Os clientes em `fontes/` cuidam da parte chata: paginação, novas tentativas quando a API falha e cache em disco, para que rodar de novo só baixe o que é novo. Os quadros de cada jogo são buscados em paralelo. Se houver uma `RIOT_API_KEY` no ambiente, entram também as partidas de solo queue dos jogadores.

O site é HTML, CSS e JavaScript sem framework. O `site.py` embute tudo num único `docs/index.html`, que o GitHub Pages publica.

![Prévia de Gen.G x Invictus Gaming](docs/img/previa.png)

## Rodando

```bash
pip install -e ".[dev]"
python -m worlds2026            # coleta os dados e atualiza docs/index.html
python -m worlds2026 --so-site  # só regera o site com o que já está em cache
pytest --cov
```

O CI roda `ruff`, `mypy` e os testes a cada push.

## Limitações

O feed não manda a posição dos jogadores, então no replay eles aparecem na rota em que jogam, não no ponto exato do mapa. As contas de solo queue vêm da Leaguepedia, que é mantida pela comunidade e às vezes está desatualizada.

---

Projeto pessoal, sem ligação com a Riot Games. Licença MIT.
