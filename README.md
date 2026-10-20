# Central do Worlds 2026

Site e API com as chaves, estatísticas e replays do Mundial de League of Legends 2026, em português e no horário de Brasília.

**Site:** https://gabriel00lima.github.io/worlds-2026-analytics/

![Página inicial](docs/img/inicio.png)

## Sobre

Comecei esse projeto porque queria acompanhar o Worlds num lugar só: ver a chave, abrir um confronto e entender o que aconteceu no jogo sem precisar rever a transmissão inteira.

A parte em Python busca os dados na API do LoL Esports, processa a linha do tempo de cada partida e gera um site estático com tudo embutido. Os mesmos dados vão para um banco SQL e ficam disponíveis numa API REST.

No site dá para:

- navegar pelo Play-In, pela Fase Suíça e pelo mata-mata, com a chance de classificação de cada time na Suíça;
- abrir um jogo e assistir aos principais lances num mapa animado, com narração;
- clicar em qualquer jogador e ver como ele foi naquele jogo, no torneio e na solo queue;
- ver o meta do torneio (campeões mais escolhidos e banidos), comparar dois jogadores e conferir os destaques do dia;
- deixar palpites e adicionar os jogos na agenda.

![Replay de Karmine Corp x MVK](docs/img/replay.png)

## Estrutura

```
src/worlds2026/
  fontes/           um cliente para cada fonte: LoL Esports, feed livestats, Leaguepedia, Riot, Data Dragon
  processamento.py  transforma os quadros do feed em lances, série de ouro e estatísticas
  pipeline.py       as etapas da coleta, da agenda até o site pronto
  site.py           junta o template, o CSS, o JS e os dados num único index.html
  api/              API REST com FastAPI e SQLAlchemy, com migrações do Alembic em api/migracoes
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

O site é HTML, CSS e JavaScript sem framework, com animações em GSAP. O `site.py` embute tudo num único `docs/index.html`, que o GitHub Pages publica.

![Painel do jogador](docs/img/jogador.png)

## API

A API carrega os dados da última coleta num banco e responde em JSON. A documentação interativa fica em `/docs`.

O banco é PostgreSQL no Docker e SQLite quando roda direto na máquina, escolhido pela `DATABASE_URL`. O esquema é versionado com Alembic: a API aplica as migrações que faltam ao subir. Uma mudança nos modelos vira migração com `alembic revision --autogenerate -m "..."`, e um teste falha se algum modelo mudar sem migração.

| Rota | O que devolve |
|---|---|
| `GET /partidas` | séries do torneio, com filtros por fase, estado e time |
| `GET /partidas/{id}` | a série com cada jogo, as estatísticas dos 10 jogadores e os bans |
| `GET /times` e `/times/{sigla}` | campanha, elenco, campeões mais jogados e mais banidos pelo time e contra ele |
| `GET /jogadores/{id}` | desempenho no torneio, campeões no torneio e na solo queue, elo |
| `GET /estatisticas/jogadores` | ranking por abates, KDA ou dano |
| `GET /estatisticas/campeoes` | campeões por presença (escolhas + bans), com vitórias |

## Rodando

```bash
pip install -e ".[dev]"
python -m worlds2026              # coleta os dados e atualiza docs/index.html
python -m worlds2026 --so-site    # só regera o site com o que já está em cache
python -m worlds2026 api          # carrega o banco e sobe a API em http://localhost:8000
pytest --cov
```

Ou com Docker, que sobe a API junto com um PostgreSQL, depois de rodar a coleta uma vez:

```bash
docker compose up
```

O CI roda `ruff`, `mypy` e os testes a cada push. Os testes da API e das migrações rodam também contra um PostgreSQL de verdade.

## Limitações

O feed não manda a posição dos jogadores, então no replay eles aparecem na rota em que jogam, não no ponto exato do mapa. As contas de solo queue vêm da Leaguepedia, que é mantida pela comunidade e às vezes está desatualizada.

---

Projeto pessoal, sem ligação com a Riot Games. Licença MIT.
