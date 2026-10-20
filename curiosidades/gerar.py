import json, os

OUT = os.path.dirname(os.path.abspath(__file__))
HOJE = "2026-10-20"

S = {
    "dot_draw": "https://dotesports.com/league-of-legends/news/worlds-2026-swiss-stage-draw",
    "sheep_draw": "https://www.sheepesports.com/en/articles/worlds-2026-swiss-stage-round-1-draw/en",
    "khan_r1": "https://sports.khan.co.kr/en/article/202610191300007/",
    "gosu_teams": "https://www.gosugamers.net/lol/news/79314-all-teams-and-players-qualified-for-the-league-of-legends-world-championship-2026",
    "egw_teams": "https://egamersworld.com/blog/every-worlds-2026-team-qualified-6Q23AMZcmS",
    "strafe_cblol": "https://www.strafe.com/news/read/all-cblol-teams-at-worlds-2026-and-how-they-qualified/",
    "strafe_lpl": "https://www.strafe.com/news/read/all-lpl-teams-at-worlds-2026-and-how-they-qualified/",
    "midgg": "https://mid.gg/esports/worlds-2026",
    "tips_gen_ig": "https://tips.gg/archive/geng-lol-vs-invictus-gaming-lol/",
    "lck_final": "https://www.gosugamers.net/lol/news/79163-gen-g-are-the-2026-lck-season-champions-after-defeating-hanwha-life-esports",
    "lck_final_sbs": "https://news.sbs.co.kr/english/article.do?news_id=N1008750797",
    "wiki_2018": "https://en.wikipedia.org/wiki/2018_League_of_Legends_World_Championship",
    "fs25_tl_cfo": "https://rft.gg/match/12712-team-liquid-vs-ctbc-flying-oyster-2025-03-13",
    "cfo_qf25": "https://www.e4equip.com/post/ctbc-flying-oyster-worlds-2025-quarterfinal",
    "cfo_lp": "https://liquipedia.net/leagueoflegends/CTBC_Flying_Oyster",
    "egw_tl_cfo": "https://egamersworld.com/lol/match/q8qUtLA6g/team-liquid-vs-ctbc-flying-oyster-zaN6r1ueRf",
    "ewc_al_kc": "https://escorenews.com/en/lol/esports-world-cup-2026/playoff/all-gamers-anyone-s-legen-vs-karmine-corp-639031",
    "ewc_al_kc2": "https://rft.gg/match/12407-anyone-s-legend-vs-karmine-corp-2026-07-17",
    "ewc_kc_t1": "https://www.sheepesports.com/en/lol/matches/Esports%20World%20Cup%202026_Semifinals_1",
    "ewc_final": "https://www.gosugamers.net/lol/news/78825-dplus-kia-crowned-2026-league-of-legends-esports-world-cup-champions-after-defeating-karmine-corp",
    "ewc_final_kj": "https://www.koreajoongangdaily.com/sports/dplus-kia-wins-esports-world-cup-league-of-legends-title/12780581",
    "ewc_official": "https://www.esportsworldcup.com/en/press-releases/dplus-kia-win-lol-at-ewc26",
    "ewc_g2_dk": "https://cryptobriefing.com/g2-esports-eliminated-from-ewc-2026-after-loss-to-dplus-kia/",
    "ewc_dexerto": "https://www.dexerto.com/league-of-legends/how-to-watch-ewc-2026-league-of-legends-stream-schedule-results-teams-3387307/",
    "pi_final": "https://www.invenglobal.com/articles/27333/karmine-corp-claims-final-main-event-spot-defeats-mvk-in-play-in-final",
    "pi_final_egw": "https://egamersworld.com/lol/news/37891/karmine-corp-sweep-mvk-esports-3-0-to-secure-histo-JGn7JUv8u",
    "pi_day2": "https://www.gosugamers.net/lol/news/79364-karmine-corp-sweep-mvk-esports-furia-eliminate-cloud9-kia-on-day-2-of-worlds-2026-play-ins",
    "kc_roster": "https://bo3.gg/lol/news/official-karmine-corp-has-finalized-its-roster-for-the-2026-lec-season",
    "wiki_al": "https://en.wikipedia.org/wiki/Anyone%27s_Legend",
    "msi26_final": "https://www.sheepesports.com/articles/hanwha-life-esports-crowned-msi-2026-champion-after-3-2-against-bilibili-gaming/en",
    "msi26_rdy": "https://rdy.gg/en/lol/news/hle-wins-msi-2026",
    "msi26_g2_t1": "https://dotesports.com/league-of-legends/news/g2-esports-eliminate-t1-from-msi-2026-ending-legendary-international-top-four-streak",
    "msi26_lyon_tsw": "https://liquipedia.net/leagueoflegends/Match:ID_MSI26Brakt_R02-M004",
    "hle_roster": "https://www.sheepesports.com/en/all/articles/lol-hanwha-life-esports-completed-2026-lck-roster/en",
    "w24_lp": "https://liquipedia.net/leagueoflegends/World_Championship/2024",
    "w24_gosu": "https://www.gosugamers.net/lol/news/73426-worlds-2024-top-esports-defeat-dplus-kia-hanwha-life-outplay-flyquest-to-qualify-for-quarterfinals",
    "cblol_final": "https://www.techtudo.com.br/noticias/2026/10/final-do-cblol-2026-los-bate-furia-em-revanche-do-primeiro-split-e-e-campea-edjogos.ghtml",
    "t1_diario": "https://diariodelsur.com.co/noticias/t1-y-faker-preparan-su-debut-en-la-fase-suiza-de-worlds-2026-en-estados-unidos",
    "brazil_hist": "https://www.sheepesports.com/articles/lol-worlds-2024-pain-gaming-the-last-cblol-s-glimmer-turns-into-fireworks/en",
    "lyon_preview": "https://www.yardbarker.com/entertainment/articles/worlds_2026_lyon_preview_knocked_off_their_temporary_throne_by_strengthened_rosters/s1_17456_44399263",
    "wiki_lcs26": "https://en.wikipedia.org/wiki/2026_LCS_season",
    "tsw_lp": "https://lol.fandom.com/wiki/Team_Secret_Whales",
    "msi25_blg_koi": "https://liquipedia.net/leagueoflegends/Match:ID_MSI25Brakt_R01-M004",
    "msi25_yard": "https://www.yardbarker.com/video_games/articles/msi_2025_movistar_koi_versus_bilibili_gaming_the_east_destroys_west_hope/s1_17458_42412187",
    "ewc_blg_koi": "https://rft.gg/match/12396-bilibili-gaming-vs-movistar-koi-2026-07-15",
    "lec_summer": "https://esports.gg/news/league-of-legends/lec-summer-2026-playoffs-results/",
    "insider_draw": "https://insider-gaming.com/worlds-2026-swiss-stage-draw-confirmed/",
    "wiki_2020": "https://en.wikipedia.org/wiki/2020_League_of_Legends_World_Championship",
    "wiki_2019": "https://en.wikipedia.org/wiki/2019_League_of_Legends_World_Championship",
    "wiki_2017": "https://en.wikipedia.org/wiki/2017_League_of_Legends_World_Championship",
    "wiki_2021": "https://en.wikipedia.org/wiki/2021_League_of_Legends_World_Championship",
    "wiki_2023": "https://en.wikipedia.org/wiki/2023_League_of_Legends_World_Championship",
    "wiki_2024": "https://en.wikipedia.org/wiki/2024_League_of_Legends_World_Championship",
    "wiki_2025": "https://en.wikipedia.org/wiki/2025_League_of_Legends_World_Championship",
    "wiki_t1": "https://en.wikipedia.org/wiki/T1_(esports)",
    "wiki_msi19": "https://en.wikipedia.org/wiki/2019_Mid-Season_Invitational",
    "wiki_msi_geng": "https://en.wikipedia.org/wiki/2025_Mid-Season_Invitational",
}

def f(*keys):
    return [S[k] for k in keys]

def c(texto, fontes, confianca="confirmado"):
    # confianca: confirmado (2+ fontes ou fonte de referência), fonte_unica, inferido
    return {"texto": texto, "confianca": confianca, "fontes": fontes}

def j(posicao, jogador, confianca="confirmado"):
    return {"posicao": posicao, "jogador": jogador, "confianca": confianca}

def elenco(top, jg, mid, adc, sup, conf="confirmado"):
    return [j("top", top, conf), j("jungle", jg, conf), j("mid", mid, conf), j("atirador", adc, conf), j("suporte", sup, conf)]

TIMES = {
  "gen-g": dict(nome="Gen.G", sigla="GEN", regiao="LCK", seed="LCK #1",
    como_classificou="Campeã da LCK 2026 (3–1 na Hanwha Life na final de 13/09).",
    elenco=elenco("Kiin", "Canyon", "Chovy", "Ruler", "Duro"), elenco_fontes=f("gosu_teams", "midgg"),
    titulos_mundiais=[], melhor_mundial="A organização reivindica a linhagem da Samsung (campeã em 2014 e 2017); como Gen.G, semifinal.",
    curiosidades=[
      c("Bicampeã seguida da LCK (2025 e 2026) e sétimo título da liga; Ruler foi o MVP da final de 2026.", f("lck_final", "lck_final_sbs")),
      c("É apontada como o elenco mais forte que nunca ganhou um Mundial jogando junto. Ruler (2017) e Canyon (2020) já foram campeões por outros times; Chovy nunca foi.", f("midgg", "wiki_2017", "wiki_2020")),
    ]),
  "ig": dict(nome="Invictus Gaming", sigla="IG", regiao="LPL", seed="LPL #4",
    como_classificou="Quarta vaga da LPL, vinda pela chave inferior dos playoffs do Split 3.",
    elenco=elenco("TheShy", "Wei", "Rookie", "JiaQi", "Meiko"), elenco_fontes=f("strafe_lpl", "midgg"),
    titulos_mundiais=[2018], melhor_mundial="Campeã em 2018 (3–0 na Fnatic, em Incheon).",
    curiosidades=[
      c("TheShy e Rookie foram campeões mundiais juntos pela IG em 2018 e voltam ao Mundial lado a lado pelo segundo ano seguido.", f("strafe_lpl", "wiki_2018")),
      c("Em 2025 a IG teve de passar pelo Play-In; em 2026 entrou direto no Swiss.", f("strafe_lpl")),
    ]),
  "tl": dict(nome="Team Liquid", sigla="TL", regiao="LCS", seed="LCS",
    como_classificou="Uma das vagas da LCS.",
    elenco=elenco("Morgan", "Josedeodo", "Quid", "Yeon", "CoreJJ", "fonte_unica"), elenco_fontes=f("gosu_teams"),
    titulos_mundiais=[], melhor_mundial="Nunca chegou a uma semifinal de Mundial.",
    curiosidades=[
      c("O suporte CoreJJ é campeão mundial: venceu o Mundial de 2017 pela Samsung Galaxy.", f("wiki_2017")),
      c("Há divergência na escalação: outra fonte lista Reignover e UmTi no elenco recente.", f("egw_tl_cfo"), "fonte_unica"),
    ]),
  "cfo": dict(nome="CTBC Flying Oyster", sigla="CFO", regiao="LCP", seed="LCP #2",
    como_classificou="Segunda vaga da LCP.",
    elenco=elenco("Rest", "Shad0w", "Pout", "Doggo", "Kino"), elenco_fontes=f("gosu_teams", "cfo_lp"),
    titulos_mundiais=[], melhor_mundial="Quartas de final em 2025.",
    curiosidades=[
      c("Em 2025 chegou às quartas do Mundial, a primeira vez em dez anos que um time da região ficou entre os oito melhores.", f("cfo_qf25")),
      c("Pout (mid) e Kino (suporte) entraram no time em abril de 2026.", f("cfo_lp"), "fonte_unica"),
    ]),
  "al": dict(nome="Anyone's Legend", sigla="AL", regiao="LPL", seed="LPL #1",
    como_classificou="Campeã da final do Split 3 da LPL 2026, seu segundo título.",
    elenco=elenco("Breathe", "Tarzan", "Shanks", "Hope", "Kael", "fonte_unica"), elenco_fontes=f("gosu_teams"),
    titulos_mundiais=[], melhor_mundial="Sem campanha marcante em Mundiais até aqui.",
    curiosidades=[
      c("Primeira cabeça de chave da China em 2026, com o segundo título de LPL da história do clube.", f("wiki_al", "gosu_teams")),
      c("Fontes divergem sobre o top: uma lista Breathe, outra (mais antiga) lista Flandre.", f("gosu_teams", "egw_teams"), "fonte_unica"),
    ]),
  "kc": dict(nome="Karmine Corp", sigla="KC", regiao="LEC", seed="LEC #3 (via Play-In)",
    como_classificou="Terceira da LEC; venceu o Play-In em Los Angeles (3–2 no Cloud9 Kia e 3–0 duas vezes na MVK).",
    elenco=elenco("Canna", "Yike", "Kyeahoo", "Caliste", "Busio"), elenco_fontes=f("kc_roster", "pi_final"),
    titulos_mundiais=[], melhor_mundial="Estreia em Mundiais em 2026.",
    curiosidades=[
      c("Primeiro Mundial da história do clube francês, conquistado no Play-In.", f("pi_final", "pi_final_egw")),
      c("Vice da Esports World Cup 2026: eliminou a AL (2–0) e a T1 (2–1) e perdeu a final para a Dplus KIA (0–3).", f("ewc_al_kc", "ewc_kc_t1", "ewc_final")),
      c("A dupla de bot Caliste e Busio foi o destaque do Play-In.", f("pi_day2")),
    ]),
  "g2": dict(nome="G2 Esports", sigla="G2", regiao="LEC", seed="LEC #1",
    como_classificou="Campeã da LEC Summer 2026 (3–0 na Movistar KOI na final).",
    elenco=elenco("BrokenBlade", "SkewMond", "Caps", "Hans Sama", "Labrov", "fonte_unica"), elenco_fontes=f("ewc_dexerto"),
    titulos_mundiais=[], melhor_mundial="Vice-campeã em 2019 (0–3 para a FunPlus Phoenix).",
    curiosidades=[
      c("Eliminou a T1 do MSI 2026, encerrando a sequência de top 4 internacional da T1.", f("msi26_g2_t1")),
      c("Caps foi vice mundial duas vezes seguidas: 2018 pela Fnatic e 2019 pela G2.", f("wiki_2018", "wiki_2019")),
      c("Foi campeã do MSI 2019, até hoje o último MSI vencido por um time europeu.", f("wiki_msi19"), "fonte_unica"),
    ]),
  "dk": dict(nome="Dplus KIA", sigla="DK", regiao="LCK", seed="LCK #4",
    como_classificou="Quarta vaga da LCK, garantida pelo bom resultado da Coreia no MSI 2026.",
    elenco=elenco("Siwoo", "Lucid", "ShowMaker", "Smash", "Career"), elenco_fontes=f("gosu_teams", "ewc_dexerto"),
    titulos_mundiais=[2020], melhor_mundial="Campeã em 2020 como DAMWON Gaming (3–1 na Suning).",
    curiosidades=[
      c("Campeã da Esports World Cup 2026 com 3–0 na Karmine Corp; Smash foi o MVP. Foi o primeiro grande título internacional do clube em quase seis anos.", f("ewc_final", "ewc_final_kj", "ewc_official")),
      c("ShowMaker é o único remanescente do time campeão mundial de 2020.", f("wiki_2020"), "inferido"),
    ]),
  "hle": dict(nome="Hanwha Life Esports", sigla="HLE", regiao="LCK", seed="LCK #2",
    como_classificou="Campeã do MSI 2026 e vice da LCK 2026.",
    elenco=elenco("Zeus", "Kanavi", "Zeka", "Gumayusi", "Delight"), elenco_fontes=f("hle_roster"),
    titulos_mundiais=[], melhor_mundial="Quartas de final.",
    curiosidades=[
      c("Campeã do MSI 2026 em casa (Daejeon), com virada de 3–2 sobre a BLG; Zeus foi o MVP da final. Primeiro MSI do clube e quinto da Coreia.", f("msi26_final", "msi26_rdy")),
      c("Tem dois ex-campeões mundiais pela T1: Zeus (2023) e Gumayusi.", f("hle_roster", "wiki_2023")),
      c("Perdeu a final da LCK 2026 para a Gen.G por 3–1.", f("lck_final")),
    ]),
  "tes": dict(nome="Top Esports", sigla="TES", regiao="LPL", seed="LPL #3",
    como_classificou="Terceira vaga da LPL.",
    elenco=elenco("369", "Tian", "Creme", "JackeyLove", "Zhuo", "fonte_unica"), elenco_fontes=f("gosu_teams"),
    titulos_mundiais=[], melhor_mundial="Semifinal em 2020 (caiu para a Suning).",
    curiosidades=[
      c("O atirador JackeyLove foi campeão mundial em 2018 pela IG, adversária chinesa deste mesmo Mundial.", f("wiki_2018")),
      c("Tian (jungle) foi campeão mundial em 2019 pela FunPlus Phoenix.", f("wiki_2019")),
    ]),
  "los": dict(nome="LOS", sigla="LOS", regiao="CBLOL", seed="CBLOL #1",
    como_classificou="Campeã da Etapa 2 do CBLOL 2026 (3–2 na FURIA, 10/10, Arena Carioca 1, Rio).",
    elenco=elenco("Zest", "Curse", "Feisty", "Duduhh", "Ackerman", "fonte_unica"), elenco_fontes=f("egw_teams", "strafe_cblol"),
    titulos_mundiais=[], melhor_mundial="Estreia em Mundiais.",
    curiosidades=[
      c("Ganhou o título em cima da FURIA como revanche: na Etapa 1, em junho, a FURIA tinha vencido a LOS por 3–1.", f("cblol_final")),
      c("Montou o elenco em torno de dois coreanos, Zest (top) e Feisty (mid), e chega como grande azarão.", f("strafe_cblol"), "fonte_unica"),
      c("É o único time brasileiro no Swiss: a FURIA caiu no Play-In.", f("pi_day2")),
    ]),
  "t1": dict(nome="T1", sigla="T1", regiao="LCK", seed="LCK #3",
    como_classificou="Terceira vaga da LCK.",
    elenco=elenco("Doran", "Oner", "Faker", "Peyz", "Keria"), elenco_fontes=f("gosu_teams"),
    titulos_mundiais=[2013, 2015, 2016, 2023, 2024, 2025], melhor_mundial="Seis vezes campeã, incluindo os três últimos Mundiais.",
    curiosidades=[
      c("Tricampeã seguida (2023, 2024, 2025) e dona de seis títulos: busca o sétimo.", f("t1_diario", "wiki_t1", "wiki_2025")),
      c("Faker esteve em todos os seis títulos do clube.", f("wiki_t1")),
      c("Não ganha um título nacional desde a primavera de 2022 e costuma crescer só no Mundial.", f("t1_diario"), "fonte_unica"),
      c("Em 2026 caiu para a G2 no MSI e para a Karmine Corp na semifinal da EWC.", f("msi26_g2_t1", "ewc_kc_t1")),
    ]),
  "tsw": dict(nome="Team Secret Whales", sigla="TSW", regiao="LCP", seed="LCP #1",
    como_classificou="Campeã e primeira cabeça de chave da LCP.",
    elenco=elenco("Pun", "Hizto", "Dire", "Eddie", "Bie", "fonte_unica"), elenco_fontes=f("tsw_lp", "gosu_teams"),
    titulos_mundiais=[], melhor_mundial="Sem campanha marcante.",
    curiosidades=[
      c("Foi eliminada do MSI 2026 justamente pela LYON, por 3–0.", f("msi26_lyon_tsw")),
    ]),
  "lyon": dict(nome="LYON", sigla="LYON", regiao="LCS", seed="LCS",
    como_classificou="Campeã do Lock-In e do Spring da LCS 2026, vice no Summer.",
    elenco=elenco("Dhokla", "Inspired", "Saint", "Berserker", "Isles"), elenco_fontes=f("lyon_preview", "wiki_lcs26"),
    titulos_mundiais=[], melhor_mundial="Estreia com este elenco.",
    curiosidades=[
      c("No MSI 2026 chegou à final da chave inferior e só caiu numa virada da HLE, que depois foi campeã.", f("msi26_final")),
      c("Dhokla entrou no top no lugar de Zamudo, que teve problema de visto.", f("lyon_preview"), "fonte_unica"),
    ]),
  "blg": dict(nome="Bilibili Gaming", sigla="BLG", regiao="LPL", seed="LPL #2",
    como_classificou="Segunda vaga da LPL.",
    elenco=elenco("Bin", "XUN", "Knight", "Viper", "ON"), elenco_fontes=f("gosu_teams"),
    titulos_mundiais=[], melhor_mundial="Vice-campeã em 2024 (2–3 para a T1).",
    curiosidades=[
      c("Vice do MSI 2026: venceu a HLE por 3–1 na final da chave superior e perdeu a revanche na grande final por 3–2.", f("msi26_final", "msi26_rdy")),
      c("Viper, campeão mundial de 2021 pela EDG, voltou à China pela BLG depois de jogar na HLE.", f("hle_roster", "wiki_2021")),
    ]),
  "koi": dict(nome="Movistar KOI", sigla="MKOI", regiao="LEC", seed="LEC #2",
    como_classificou="Vice da LEC Summer 2026.",
    elenco=elenco("Myrwn", "Elyoya", "Jojopyun", "Supa", "Alvaro", "fonte_unica"), elenco_fontes=f("ewc_blg_koi"),
    titulos_mundiais=[], melhor_mundial="Sem campanha marcante com o nome atual.",
    curiosidades=[
      c("Perdeu a final da LEC Summer 2026 para a G2 por 3–0.", f("lec_summer"), "fonte_unica"),
    ]),
}

CONF = [
  dict(id="r1-gen-g-ig", a="gen-g", b="ig",
    manchete="A campeã da Coreia contra os campeões mundiais de 2018",
    historico=[
      dict(evento="Mid-Season Cup 2020", data="2020-05-29", fase="Grupos", vencedor="gen-g", placar="1–0", fontes=f("tips_gen_ig"), confianca="confirmado"),
      dict(evento="Puyuan Esports Festival 2025 (exibição)", data="2025-12-27", fase="Grupos", vencedor="gen-g", placar="2–0", fontes=f("tips_gen_ig"), confianca="fonte_unica"),
    ],
    resumo_historico="Nunca se enfrentaram em Mundial nem em MSI. Nos dois encontros conhecidos, deu Gen.G.",
    primeiro_encontro_mundial=True,
    curiosidades=[
      c("Primeiro encontro das duas em Mundiais.", f("tips_gen_ig"), "inferido"),
      c("TheShy e Rookie, campeões de 2018 pela IG, contra o elenco da Gen.G que nunca ganhou o Mundial junto.", f("strafe_lpl", "midgg")),
      c("Um site de previsões dá 93% de chance para a Gen.G.", f("tips_gen_ig"), "fonte_unica"),
    ],
    duelos=[dict(posicao="mid", a="Chovy", b="Rookie", nota="Dois dos mids mais premiados de suas regiões."), dict(posicao="top", a="Kiin", b="TheShy")]),
  dict(id="r1-tl-cfo", a="tl", b="cfo",
    manchete="Liquid quer devolver a derrota do First Stand",
    historico=[dict(evento="First Stand 2025", data="2025-03-13", fase="Round robin (Bo3)", vencedor="cfo", placar="2–0", fontes=f("fs25_tl_cfo"), confianca="confirmado")],
    resumo_historico="Único encontro conhecido: CFO 2–0 no First Stand 2025.",
    primeiro_encontro_mundial=True,
    curiosidades=[
      c("A CFO chegou às quartas no Mundial de 2025, algo que a região não fazia havia dez anos.", f("cfo_qf25")),
      c("Nas casas de aposta a Liquid é favorita (1,35 contra 2,90).", f("egw_tl_cfo"), "fonte_unica"),
      c("CoreJJ, suporte da Liquid, é campeão mundial de 2017.", f("wiki_2017")),
    ],
    duelos=[dict(posicao="mid", a="Quid", b="Pout")]),
  dict(id="r1-al-kc", a="al", b="kc",
    manchete="Revanche da Esports World Cup",
    historico=[dict(evento="Esports World Cup 2026", data="2026-07-17", fase="Quartas (Bo3)", vencedor="kc", placar="2–0", fontes=f("ewc_al_kc", "ewc_al_kc2"), confianca="confirmado")],
    resumo_historico="Último encontro: KC 2–0 nas quartas da EWC 2026 (18–11 e 12–4 em abates).",
    primeiro_encontro_mundial=True,
    curiosidades=[
      c("A KC estreia em Mundiais e chega embalada pelo Play-In, onde perdeu só dois mapas.", f("pi_final", "pi_day2")),
      c("Na EWC a KC venceu a AL e depois eliminou a T1 antes de perder a final.", f("ewc_al_kc", "ewc_kc_t1", "ewc_final")),
      c("A AL é a primeira cabeça de chave da China.", f("gosu_teams")),
    ],
    duelos=[dict(posicao="bot", a="Hope", b="Caliste", nota="Caliste e Busio foram os destaques da KC no Play-In.")]),
  dict(id="r1-g2-dk", a="g2", b="dk",
    manchete="Reencontro de 2023 e revanche da EWC",
    historico=[
      dict(evento="Mundial 2023", data="2023-10", fase="Swiss, rodada 1 (Bo1)", vencedor="g2", placar="1–0", fontes=f("khan_r1"), confianca="fonte_unica"),
      dict(evento="Esports World Cup 2026", data="2026-07", fase="Grupos (Bo3)", vencedor="dk", placar="2–0", fontes=f("ewc_official", "ewc_g2_dk"), confianca="confirmado"),
    ],
    resumo_historico="1–1 nos encontros recentes: G2 venceu a estreia do Swiss de 2023, DK venceu na EWC 2026.",
    primeiro_encontro_mundial=False,
    curiosidades=[
      c("Em 2023 as duas também se enfrentaram na estreia do Swiss, e a G2 venceu.", f("khan_r1"), "fonte_unica"),
      c("A DK chega como campeã da EWC 2026.", f("ewc_final", "ewc_official")),
      c("Duelo de mids campeões e vices: ShowMaker (campeão em 2020) contra Caps (vice em 2018 e 2019).", f("khan_r1", "wiki_2020", "wiki_2018", "wiki_2019")),
    ],
    duelos=[dict(posicao="mid", a="Caps", b="ShowMaker", nota="Apontado pela imprensa coreana como o duelo central.")]),
  dict(id="r1-hle-tes", a="hle", b="tes",
    manchete="Campeã do MSI contra JackeyLove",
    historico=[],
    resumo_historico="Não achamos encontro anterior em Mundial. Em 2024 as duas passaram do Swiss com 3–1 sem se cruzar.",
    primeiro_encontro_mundial=True,
    curiosidades=[
      c("Em 2024 as duas fizeram 3–1 no Swiss e foram às quartas, sem se enfrentar.", f("w24_lp", "w24_gosu")),
      c("A HLE é a atual campeã do MSI.", f("msi26_final")),
      c("Três campeões mundiais no bot e no top: Zeus e Gumayusi (pela T1) de um lado, JackeyLove (pela IG, 2018) do outro.", f("hle_roster", "wiki_2018", "wiki_2023")),
    ],
    duelos=[dict(posicao="atirador", a="Gumayusi", b="JackeyLove"), dict(posicao="top", a="Zeus", b="369")]),
  dict(id="r1-los-t1", a="los", b="t1",
    manchete="O Brasil contra a tricampeã",
    historico=[],
    resumo_historico="Nunca se enfrentaram.",
    primeiro_encontro_mundial=True,
    curiosidades=[
      c("Primeiro jogo da história entre LOS e T1.", f("dot_draw"), "inferido"),
      c("A T1 venceu os três últimos Mundiais e tenta o sétimo título.", f("t1_diario", "wiki_t1")),
      c("Não encontramos registro de time do CBLOL vencendo um time coreano em Mundial. As vitórias mais lembradas do Brasil são KaBuM! sobre a Alliance (2014) e INTZ sobre a EDG (2016).", f("brazil_hist"), "inferido"),
      c("A LOS ganhou o CBLOL há menos de duas semanas, em 10/10, numa final de cinco jogos.", f("cblol_final")),
    ],
    duelos=[dict(posicao="mid", a="Feisty", b="Faker")]),
  dict(id="r1-tsw-lyon", a="tsw", b="lyon",
    manchete="Revanche do MSI",
    historico=[dict(evento="MSI 2026", data="2026-07", fase="Chave eliminatória (Bo5)", vencedor="lyon", placar="3–0", fontes=f("msi26_lyon_tsw"), confianca="confirmado")],
    resumo_historico="Último encontro: LYON 3–0, eliminando a TSW do MSI 2026.",
    primeiro_encontro_mundial=True,
    curiosidades=[
      c("A LYON varreu a TSW no MSI e depois foi até a final da chave inferior.", f("msi26_lyon_tsw", "msi26_final")),
    ],
    duelos=[dict(posicao="jungle", a="Hizto", b="Inspired")]),
  dict(id="r1-blg-koi", a="blg", b="koi",
    manchete="A KOI ainda não venceu a BLG em séries",
    historico=[
      dict(evento="MSI 2025", data="2025-07-03", fase="Chave superior, rodada 1 (Bo5)", vencedor="blg", placar="3–1", fontes=f("msi25_blg_koi", "msi25_yard"), confianca="confirmado"),
      dict(evento="Esports World Cup 2026", data="2026-07-15", fase="Fase de grupos", vencedor="blg", placar="1–0", fontes=f("ewc_blg_koi"), confianca="fonte_unica"),
    ],
    resumo_historico="BLG venceu os dois encontros conhecidos (3–1 no MSI 2025 e na EWC 2026).",
    primeiro_encontro_mundial=True,
    curiosidades=[
      c("No MSI 2025 a KOI tirou dois mapas da BLG, um deles com atuação de destaque de Jojopyun.", f("msi25_yard")),
      c("A BLG foi vice-campeã do MSI 2026, perdendo a final para a HLE por 3–2.", f("msi26_final")),
    ],
    duelos=[dict(posicao="atirador", a="Viper", b="Supa"), dict(posicao="mid", a="Knight", b="Jojopyun")]),
]

os.makedirs(f"{OUT}/times", exist_ok=True)
os.makedirs(f"{OUT}/confrontos", exist_ok=True)

for tid, t in TIMES.items():
    extra = {"ig": ["wiki_2018"], "dk": ["wiki_2020"], "g2": ["wiki_2019"], "blg": ["wiki_2024"], "t1": ["wiki_t1"], "tes": ["wiki_2020"], "kc": ["pi_final"]}.get(tid, [])
    fontes = sorted({u for x in t["curiosidades"] for u in x["fontes"]} | set(t["elenco_fontes"]) | set(f(*extra)))
    doc = {"id": tid, **{k: v for k, v in t.items()}, "fontes": fontes, "atualizado_em": HOJE}
    with open(f"{OUT}/times/{tid}.json", "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)

idx = []
for cf in CONF:
    fontes = {S["dot_draw"], S["sheep_draw"]}
    for x in cf["curiosidades"] + cf["historico"]:
        fontes |= set(x["fontes"])
    doc = {"id": cf["id"], "fase": "Swiss", "rodada": 1, "data": "2026-10-23", "formato": "Bo1",
           "time_a": {"id": cf["a"], "nome": TIMES[cf["a"]]["nome"]},
           "time_b": {"id": cf["b"], "nome": TIMES[cf["b"]]["nome"]},
           **{k: cf[k] for k in ("manchete", "resumo_historico", "primeiro_encontro_mundial", "historico", "curiosidades", "duelos")},
           "fontes": sorted(fontes), "atualizado_em": HOJE}
    with open(f"{OUT}/confrontos/{cf['id']}.json", "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
    idx.append({"id": cf["id"], "rodada": 1, "time_a": cf["a"], "time_b": cf["b"], "manchete": cf["manchete"],
                "arquivo": f"confrontos/{cf['id']}.json"})

with open(f"{OUT}/index.json", "w", encoding="utf-8") as fh:
    json.dump({"atualizado_em": HOJE, "confrontos": idx,
               "times": {tid: f"times/{tid}.json" for tid in TIMES}}, fh, ensure_ascii=False, indent=2)
print("ok", len(TIMES), len(CONF))
