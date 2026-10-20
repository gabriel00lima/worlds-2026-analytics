(function () {
  "use strict";
  const W = window.W;
  const $ = (s, r = document) => r.querySelector(s);
  const esc = (s) =>
    String(s ?? "").replace(
      /[&<>"']/g,
      (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c],
    );
  const TZ = "America/Sao_Paulo";
  const fmt = (iso, o) => new Intl.DateTimeFormat("pt-BR", { timeZone: TZ, ...o }).format(new Date(iso));
  const dataHora = (iso) =>
    fmt(iso, { weekday: "short", day: "2-digit", month: "2-digit" }).replace(/\./g, "") +
    " · " +
    fmt(iso, { hour: "2-digit", minute: "2-digit" });
  const hora = (iso) => fmt(iso, { hour: "2-digit", minute: "2-digit" });
  const horaFalada = (iso) => {
    const [h, m] = hora(iso).split(":");
    return +h + (m === "00" ? " horas" : " e " + +m);
  };
  const mmss = (s) => {
    s = Math.max(0, Math.round(s));
    return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0");
  };
  const min = (s) => Math.max(1, Math.round(s / 60));
  const pct = (x, d = 0) => (x == null || isNaN(x) ? "–" : (x * 100).toFixed(d) + "%");
  const n1 = (x, d = 1) =>
    x == null || isNaN(x)
      ? "–"
      : Number(x).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });
  const mil = (x) =>
    x == null || isNaN(x)
      ? "–"
      : (x > 0 ? "+" : x < 0 ? "−" : "") +
        (Math.abs(x) / 1000).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) +
        "k";
  const sinal = (x) => (x == null ? "–" : (x > 0 ? "+" : x < 0 ? "−" : "") + Math.abs(Math.round(x)));
  const ROTAS = ["top", "jungle", "mid", "bottom", "support"];
  const ROTA_PT = { top: "Topo", jungle: "Selva", mid: "Meio", bottom: "Atirador", support: "Suporte" };
  const ROTA_LANE = {
    top: "rota do topo",
    jungle: "selva",
    mid: "rota do meio",
    bottom: "rota de baixo",
    support: "rota de baixo",
  };
  const DRAG = {
    cloud: ["Vento", "#9fd3e6"],
    infernal: ["Infernal", "#e8613a"],
    mountain: ["Montanha", "#b08a5a"],
    ocean: ["Oceano", "#3e8ed0"],
    hextech: ["Hextec", "#5fd3c8"],
    chemtech: ["Quimtec", "#a3c43c"],
    elder: ["Ancião", "#d7c9ff"],
  };
  const PARADO = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- índices ---------- */
  const TIMES = W.times;
  const porId = {};
  Object.values(TIMES).forEach((t) => (porId[t.id] = t.codigo));
  const PARTIDAS = W.partidas.slice().sort((a, b) => a.inicio.localeCompare(b.inicio));
  const PID = {};
  PARTIDAS.forEach((p) => (PID[p.id] = p));
  const JOGOS = W.jogos.map(analisar);
  const jogosDe = (pid) => JOGOS.filter((j) => j.partida === pid).sort((a, b) => a.numero - b.numero);
  const logo = (c) => TIMES[c]?.logo || "";
  const nomeT = (c) => TIMES[c]?.nome || c;
  const FOTO = {};
  Object.values(TIMES).forEach((t) => t.jogadores.forEach((p) => (FOTO[p.id] = p.foto)));
  const camp = (k) => W.campeoes[k] || { nome: k, icone: "" };
  const img = (src, cls, alt = "", st = "") =>
    src
      ? `<img class="${cls || ""}" src="${src}" alt="${esc(alt)}" ${st ? `style="${st}"` : ""}>`
      : `<span class="vazio ${cls || ""}"></span>`;
  const mini = (c) => img(logo(c), "", c, "width:18px;height:18px;object-fit:contain;vertical-align:-4px");

  function analisar(j) {
    const az = porId[j.timeAzul],
      vm = porId[j.timeVermelho];
    const fim = j.serie[j.serie.length - 1];
    const em = (s) => j.serie.reduce((a, b) => (Math.abs(b[0] - s) < Math.abs(a[0] - s) ? b : a));
    const s15 = j.duracao >= 900 ? em(900) : null;
    const jog = j.jogadores.map((x) => {
      const p = fim[3][x.pid - 1] || [0, 0, 0, 0, 0, 0];
      return {
        ...x,
        nick: String(x.nick || "").trim(),
        time: x.lado === "blue" ? az : vm,
        ouro: p[0],
        k: p[1],
        d: p[2],
        a: p[3],
        cs: p[4],
        nivel: p[5],
        ouro15: s15 ? s15[3][x.pid - 1][0] : null,
        cs15: s15 ? s15[3][x.pid - 1][4] : null,
      };
    });
    jog.forEach((x) => {
      const op = jog.find((y) => y.lado !== x.lado && y.rota === x.rota);
      x.gd15 = x.ouro15 != null && op ? x.ouro15 - op.ouro15 : null;
      x.csd15 = x.cs15 != null && op ? x.cs15 - op.cs15 : null;
    });
    const ev = j.eventos.slice().sort((a, b) => a.s - b.s);
    const primeiro = (t) => ev.find((e) => e.tipo === t);
    const contar = (t, l) =>
      ev.filter((e) => e.tipo === t && e.lado === l).reduce((s, e) => s + (e.n || 1), 0);
    const tot = {};
    for (const l of ["blue", "red"])
      tot[l] = {
        abates: contar("abate", l),
        dragoes: contar("dragao", l),
        barons: contar("barao", l),
        torres: contar("torre", l),
        ouro: l === "blue" ? fim[1] : fim[2],
      };
    return {
      ...j,
      az,
      vm,
      venc: j.vencedor === "blue" ? az : vm,
      lados: { blue: az, red: vm },
      jog,
      ev,
      fim,
      s15,
      fb: primeiro("abate"),
      fd: primeiro("dragao"),
      ft: primeiro("torre"),
      fbar: primeiro("barao"),
      tot,
    };
  }
  const ladoDe = (j, c) => (j.az === c ? "blue" : j.vm === c ? "red" : null);
  const outro = (l) => (l === "blue" ? "red" : "blue");
  const kda = (x) => (x.k + x.a) / Math.max(1, x.d);

  /* ---------- estatísticas agregadas deste Worlds ---------- */
  function statsTime(c) {
    const js = JOGOS.filter((j) => j.az === c || j.vm === c);
    if (!js.length) return null;
    const r = {
      jogos: js.length,
      v: 0,
      fb: 0,
      fd: 0,
      ft: 0,
      fbar: 0,
      drag: 0,
      bar: 0,
      tor: 0,
      abates: 0,
      mortes: 0,
      dur: 0,
      gd15: [],
      camps: {},
      dragTipos: {},
      bansPor: {},
      bansContra: {},
      jogosLp: 0,
      arautos: 0,
      larvas: 0,
    };
    for (const j of js) {
      const l = ladoDe(j, c),
        o = outro(l);
      if (j.venc === c) r.v++;
      if (j.fb?.lado === l) r.fb++;
      if (j.fd?.lado === l) r.fd++;
      if (j.ft?.lado === l) r.ft++;
      if (j.fbar?.lado === l) r.fbar++;
      r.drag += j.tot[l].dragoes;
      r.bar += j.tot[l].barons;
      r.tor += j.tot[l].torres;
      r.abates += j.tot[l].abates;
      r.mortes += j.tot[o].abates;
      r.dur += j.duracao;
      j.ev
        .filter((e) => e.tipo === "dragao" && e.lado === l)
        .forEach((e) => (r.dragTipos[e.dragao] = (r.dragTipos[e.dragao] || 0) + 1));
      if (j.s15) r.gd15.push(l === "blue" ? j.s15[1] - j.s15[2] : j.s15[2] - j.s15[1]);
      j.jog.filter((x) => x.lado === l).forEach((x) => (r.camps[x.campeao] = (r.camps[x.campeao] || 0) + 1));
      if (j.lp) {
        r.jogosLp = (r.jogosLp || 0) + 1;
        j.lp.bans[l].forEach((b) => (r.bansPor[b] = (r.bansPor[b] || 0) + 1));
        j.lp.bans[o].forEach((b) => (r.bansContra[b] = (r.bansContra[b] || 0) + 1));
        r.arautos += j.lp.arautos[l] || 0;
        r.larvas += j.lp.larvas[l] || 0;
      }
    }
    const n = r.jogos;
    return {
      ...r,
      arautosJ: r.jogosLp ? r.arautos / r.jogosLp : null,
      larvasJ: r.jogosLp ? r.larvas / r.jogosLp : null,
      wr: r.v / n,
      pfb: r.fb / n,
      pfd: r.fd / n,
      pft: r.ft / n,
      pfbar: r.fbar / n,
      dragJ: r.drag / n,
      barJ: r.bar / n,
      torJ: r.tor / n,
      abJ: r.abates / n,
      morJ: r.mortes / n,
      durM: r.dur / n,
      gd15m: r.gd15.length ? r.gd15.reduce((a, b) => a + b, 0) / r.gd15.length : null,
    };
  }
  const _sj = {};
  function statsJogador(id) {
    if (id in _sj) return _sj[id];
    const L = [];
    for (const j of JOGOS)
      for (const x of j.jog)
        if (x.jogadorId === id)
          L.push({
            ...x,
            j,
            dur: j.duracao,
            venceu: j.venc === x.time,
            fbK: j.fb?.por?.[0] === x.pid ? 1 : 0,
            fbM: j.fb?.vitimas?.[0] === x.pid ? 1 : 0,
          });
    if (!L.length) return (_sj[id] = null);
    L.sort((a, b) => ordemJogo(a.j).localeCompare(ordemJogo(b.j)));
    const s = (f) => L.reduce((a, x) => a + (x[f] || 0), 0);
    const media = (f) => {
      const v = L.filter((x) => x[f] != null);
      return v.length ? v.reduce((a, x) => a + x[f], 0) / v.length : null;
    };
    const camps = {},
      det = {};
    L.forEach((x) => {
      camps[x.campeao] = (camps[x.campeao] || 0) + 1;
      const c = (det[x.campeao] = det[x.campeao] || { j: 0, v: 0, k: 0, d: 0, a: 0 });
      c.j++;
      c.v += x.venceu ? 1 : 0;
      c.k += x.k;
      c.d += x.d;
      c.a += x.a;
    });
    const k = s("k"),
      d = s("d"),
      a = s("a"),
      m = s("dur") / 60;
    const comDano = L.filter((x) => x.danoTotal != null);
    return (_sj[id] = {
      jogos: L.length,
      linhas: L,
      k,
      d,
      a,
      kda: (k + a) / Math.max(1, d),
      csm: s("cs") / m,
      gd15: media("gd15"),
      dano: media("dano"),
      kp: media("kp"),
      camps,
      det,
      v: L.filter((x) => x.venceu).length,
      dpm: comDano.length
        ? comDano.reduce((t, x) => t + x.danoTotal, 0) / (comDano.reduce((t, x) => t + x.dur, 0) / 60)
        : null,
      visao: media("visao"),
      fbK: s("fbK"),
      fbM: s("fbM"),
      wardsM: s("wards") / m,
    });
  }
  function acharJogador(id) {
    for (const t of Object.values(TIMES))
      for (const p of t.jogadores) if (p.id === id) return { pl: p, time: t.codigo };
    for (const j of JOGOS)
      for (const x of j.jog)
        if (x.jogadorId === id)
          return { pl: { id, nick: x.nick, nome: "", rota: x.rota, foto: null }, time: x.time };
    return null;
  }
  function campanha(c) {
    return PARTIDAS.filter((p) => p.estado === "completed" && p.times.some((t) => t.codigo === c)).map(
      (p) => {
        const eu = p.times.find((t) => t.codigo === c),
          ele = p.times.find((t) => t.codigo !== c);
        return {
          p,
          venceu: eu.resultado === "win",
          placar: `${eu.vitorias}-${ele.vitorias}`,
          adv: ele.codigo,
        };
      },
    );
  }
  function recordeSuica(c, antesDe) {
    let v = 0,
      d = 0;
    for (const p of PARTIDAS) {
      if (p.fase !== "swiss" || p.estado !== "completed") continue;
      if (antesDe && p.inicio >= antesDe) continue;
      const eu = p.times.find((t) => t.codigo === c);
      if (!eu) continue;
      eu.resultado === "win" ? v++ : d++;
    }
    return [v, d];
  }

  /* ---------- fases ---------- */
  const SUICA = PARTIDAS.filter((p) => p.fase === "swiss");
  const RODADAS = [
    SUICA.slice(0, 8),
    SUICA.slice(8, 16),
    SUICA.slice(16, 24),
    SUICA.slice(24, 30),
    SUICA.slice(30, 33),
  ];
  const MATA = PARTIDAS.filter((p) => p.fase === "knockouts");
  const PLAYIN = PARTIDAS.filter((p) => p.fase === "play_ins");
  const NOMES_PLAYIN = [
    "Chave superior · rodada 1",
    "Chave superior · rodada 1",
    "Final da chave superior",
    "Chave inferior · rodada 1",
    "Final da chave inferior",
    "Final do Play-In",
  ];
  const NOMES_MATA = [
    "Quartas de final 1",
    "Quartas de final 2",
    "Quartas de final 3",
    "Quartas de final 4",
    "Semifinal 1",
    "Semifinal 2",
    "Grande final",
  ];
  function rotuloFase(p, curto) {
    if (p.fase === "swiss") {
      const r = RODADAS.findIndex((x) => x.includes(p));
      return curto ? `Suíça R${r + 1}` : `Fase Suíça, rodada ${r + 1}`;
    }
    if (p.fase === "knockouts") {
      const n = NOMES_MATA[MATA.indexOf(p)] || p.bloco;
      return curto ? n.replace("Quartas de final", "Quartas").replace("Grande final", "Final") : n;
    }
    const nm = NOMES_PLAYIN[PLAYIN.indexOf(p)] || "";
    return curto ? "Play-In" : /play-in/i.test(nm) ? nm : "Play-In, " + nm.toLowerCase();
  }

  /* ---------- topo ---------- */
  function topo() {
    const hoje = fmt(new Date().toISOString(), { year: "numeric", month: "2-digit", day: "2-digit" })
      .split("/")
      .reverse()
      .join("-");
    const fases = [
      ["Play-In", "2026-10-15", "2026-10-18", "15–18/out · Los Angeles"],
      ["Fase Suíça", "2026-10-23", "2026-10-31", "23–31/out · Allen, Texas"],
      ["Quartas", "2026-11-03", "2026-11-06", "3–6/nov"],
      ["Semis", "2026-11-07", "2026-11-08", "7–8/nov"],
      ["Final", "2026-11-14", "2026-11-14", "14/nov · Nova York"],
    ];
    $("#fases").innerHTML = fases
      .map(([n, a, b, t]) => `<span class="${hoje >= a && hoje <= b ? "agora" : ""}"><b>${n}</b> ${t}</span>`)
      .join("");
    $("#atualizado").innerHTML =
      `Dados de ${dataHora(W.atualizado)} (Brasília)<br>Patch ${esc(JOGOS[0]?.patch || "–")}`;
    const fut = PARTIDAS.filter((p) => p.estado !== "completed").slice(0, 16);
    $("#proximos").innerHTML = fut.length
      ? fut
          .map((p, i) => {
            const [a, b] = p.times;
            const tbd = a.codigo === "TBD";
            return `<button class="prox ${i === 0 ? "primeiro" : ""}" data-partida="${p.id}"><div class="quando"><span>${dataHora(p.inicio)}</span><span>${rotuloFase(p, true)}</span></div>
      <div class="vs">${tbd ? '<span class="vazio"></span><span class="muted" style="font-size:16px">A definir</span>' : `${img(logo(a.codigo), "", a.codigo)}${esc(a.codigo)} <span class="muted" style="font-size:14px">×</span> ${esc(b.codigo)}${img(logo(b.codigo), "", b.codigo)}`}</div>
      ${i === 0 ? `<div class="contagem" data-contagem="${p.inicio}"></div>` : ""}</button>`;
          })
          .join("")
      : '<span class="muted">O torneio terminou.</span>';
  }
  function contagens() {
    document.querySelectorAll("[data-contagem]").forEach((el) => {
      const ms = new Date(el.dataset.contagem) - Date.now();
      if (ms <= 0) {
        el.textContent = "já começou";
        return;
      }
      const d = Math.floor(ms / 864e5),
        h = Math.floor(ms / 36e5) % 24,
        m = Math.floor(ms / 6e4) % 60,
        s = Math.floor(ms / 1e3) % 60;
      el.textContent =
        (d ? d + "d " : "") +
        String(h).padStart(2, "0") +
        "h " +
        String(m).padStart(2, "0") +
        "m " +
        String(s).padStart(2, "0") +
        "s";
    });
  }

  /* ---------- cartões e painéis ---------- */
  function cartao(p, extra = "") {
    const fim = p.estado === "completed",
      vivo = p.estado === "inProgress";
    const linha = (t) =>
      `<div class="linha ${fim ? (t.resultado === "win" ? "ganhou" : "perdeu") : ""}">${t.codigo === "TBD" ? '<span class="vazio"></span>' : img(logo(t.codigo), "", t.codigo)}<span class="nm">${t.codigo === "TBD" ? '<span class="muted">A definir</span>' : esc(nomeT(t.codigo))}</span><span class="pl">${fim || vivo ? (t.vitorias ?? 0) : ""}</span></div>`;
    const tag = fim
      ? '<span class="tag fim">Encerrado</span>'
      : vivo
        ? '<span class="tag vivo">Ao vivo</span>'
        : `<span class="tag">MD${p.melhorDe}</span>`;
    return `<button class="conf" data-partida="${p.id}"><div class="meta"><span>${dataHora(p.inicio)}</span>${tag}</div>${linha(p.times[0])}${linha(p.times[1])}${extra}</button>`;
  }
  /* ---------- história das séries e destaque do Play-In ---------- */
  function historiaSerie(p) {
    const js = jogosDe(p.id);
    if (!js.length || p.estado !== "completed") return "";
    const w = p.times.find((t) => t.resultado === "win").codigo,
      l = p.times.find((t) => t.resultado !== "win").codigo;
    let a = 0,
      b = 0,
      atras = false;
    const passos = [];
    for (const g of js) {
      g.venc === w ? a++ : b++;
      if (b > a) atras = true;
      passos.push([a, b]);
    }
    const mvp = js
      .flatMap((g) => g.jog.filter((x) => x.time === w))
      .reduce((m, x) => {
        const k = m[x.jogadorId] || (m[x.jogadorId] = { ...x, k: 0, d: 0, a: 0 });
        k.k += x.k;
        k.d += x.d;
        k.a += x.a;
        return m;
      }, {});
    const top = Object.values(mvp).sort((x, y) => kda(y) - kda(x))[0];
    const longo = js.slice().sort((x, y) => y.duracao - x.duracao)[0];
    let txt;
    if (b === 0) txt = `${esc(nomeT(w))} não deu chance: ${a} a 0, sem perder um mapa.`;
    else if (atras)
      txt = `Virada! ${esc(nomeT(w))} chegou a estar atrás, ${passos.find((x) => x[1] > x[0]).join(" a ")}, e buscou o ${a} a ${b}.`;
    else if (a - b === 1 && a + b === p.melhorDe)
      txt = `Série decidida no último jogo: ${esc(nomeT(w))} venceu por ${a} a ${b}.`;
    else txt = `${esc(nomeT(w))} controlou a série e venceu por ${a} a ${b}.`;
    return `${txt}${top ? ` Destaque para ${esc(top.nick)}, com ${top.k}/${top.d}/${top.a} na série.` : ""} Jogo mais longo: ${mmss(longo.duracao)}.`;
  }
  function heroiPlayin() {
    const fin = PLAYIN[PLAYIN.length - 1];
    if (!fin || fin.estado !== "completed") return "";
    const camp_ = fin.times.find((t) => t.resultado === "win").codigo;
    const swissComecou = SUICA.some((p) => p.estado !== "unstarted");
    if (swissComecou) return "";
    const series = PLAYIN.filter((p) => p.estado === "completed" && p.times.some((t) => t.codigo === camp_));
    const gs = series.flatMap((p) => jogosDe(p.id));
    const v = gs.filter((g) => g.venc === camp_).length;
    const js = gs.flatMap((g) => g.jog.filter((x) => x.time === camp_));
    const por = {};
    js.forEach((x) => {
      const k = por[x.jogadorId] || (por[x.jogadorId] = { ...x, k: 0, d: 0, a: 0, j: 0 });
      k.k += x.k;
      k.d += x.d;
      k.a += x.a;
      k.j++;
    });
    const craque = Object.values(por).sort((a, b) => kda(b) - kda(a))[0];
    const foto = craque && FOTO[craque.jogadorId];
    const estreia = PARTIDAS.find((p) => p.fase === "swiss" && p.times.some((t) => t.codigo === camp_));
    const advE = estreia?.times.find((t) => t.codigo !== camp_)?.codigo;
    return `<div class="heroi-pi">
    <div class="h-logo">${img(logo(camp_), "", camp_)}</div>
    <div class="h-txt"><div class="eyebrow">Campeã do Play-In · Los Angeles</div><h2>${esc(nomeT(camp_))} está no Mundial!</h2>
      <p>Em sua primeira participação em Mundiais, a ${esc(nomeT(camp_))} venceu ${series.length} séries e ${v} de ${gs.length} jogos para ganhar a vaga do Play-In na Fase Suíça.${craque ? ` O craque da campanha foi <b>${esc(craque.nick)}</b>, com ${craque.k}/${craque.d}/${craque.a} em ${craque.j} jogos.` : ""}${estreia ? ` A estreia na Suíça é contra a ${esc(nomeT(advE))}, ${fmt(estreia.inicio, { weekday: "long", day: "numeric", month: "long" })} às ${hora(estreia.inicio)}.` : ""}</p>
      <div class="h-series">${series
        .map((p) => {
          const eu = p.times.find((t) => t.codigo === camp_),
            ele = p.times.find((t) => t.codigo !== camp_);
          return `<button class="h-serie" data-partida="${p.id}"><span class="eyebrow">${esc(NOMES_PLAYIN[PLAYIN.indexOf(p)] || "")}</span><b>${eu.vitorias} × ${ele.vitorias} ${mini(ele.codigo)} ${esc(ele.codigo)}</b><span>${historiaSerie(p)}</span></button>`;
        })
        .join("")}</div>
      <div class="h-acoes"><button class="botao-pi" data-aba="playin" data-rolar>Como foi o Play-In ›</button><button class="link" data-time="${camp_}">Ver o time</button>${craque ? `<button class="link" data-jogador="${craque.jogadorId}">Ver ${esc(craque.nick)}</button>` : ""}</div></div>
    ${foto ? `<img class="h-foto" src="${foto}" alt="${esc(craque.nick)}">` : ""}</div>`;
  }
  function painelPlayin() {
    const g = (i) =>
      PLAYIN[i]
        ? `<h4>${NOMES_PLAYIN[i]}</h4>${cartao(PLAYIN[i])}${historiaSerie(PLAYIN[i]) ? `<p class="historia-serie">${historiaSerie(PLAYIN[i])}</p>` : ""}`
        : "";
    $("#p-playin").innerHTML =
      `<p class="nota" style="margin:0 0 16px">Quatro times em dupla eliminação, todas as séries em melhor de 5. Só o campeão do Play-In avançou para a Fase Suíça. Clique numa série para ver os jogos, os números de cada jogador e assistir ao jogo narrado.</p>
  <div class="playin"><div class="bloco">${g(0)}${g(1)}</div><div class="bloco">${g(2)}${g(3)}</div><div class="bloco">${g(4)}${g(5)}</div></div>`;
  }
  function painelSuica() {
    const datas = (r) => {
      const d = [...new Set(r.map((p) => fmt(p.inicio, { day: "2-digit", month: "2-digit" })))];
      return d.length > 1 ? d[0].slice(0, 2) + " a " + d[d.length - 1] : d[0];
    };
    const grupos = [
      "Todos com 0-0",
      "Grupos 1-0 e 0-1",
      "Grupos 2-0, 1-1 e 0-2",
      "Grupos 2-1 e 1-2",
      "Grupo 2-2",
    ];
    const cols = RODADAS.map(
      (r, i) =>
        `<div class="rodada"><h3>Rodada ${i + 1} <small>${datas(r)}</small></h3><div class="grupo-rec">${grupos[i]}</div><div class="lista">${r
          .map((p) => {
            let rec = "";
            if (p.times[0].codigo !== "TBD" && i > 0) {
              const ra = recordeSuica(p.times[0].codigo, p.inicio);
              rec = `<div class="grupo-rec">grupo ${ra[0]}-${ra[1]}</div>`;
            }
            return cartao(p, rec);
          })
          .join("")}</div></div>`,
    ).join("");
    const cods = [...new Set(SUICA.flatMap((p) => p.times.map((t) => t.codigo)).filter((c) => c !== "TBD"))];
    const tab = cods
      .map((c) => ({ c, r: recordeSuica(c) }))
      .sort((x, y) => y.r[0] - y.r[1] - (x.r[0] - x.r[1]) || nomeT(x.c).localeCompare(nomeT(y.c)));
    $("#p-suica").innerHTML =
      `<p class="nota" style="margin:0 0 16px">16 times. Três vitórias classificam para o mata-mata e três derrotas eliminam. Séries que valem vaga ou eliminação são em melhor de 3 e as demais em melhor de 1. Depois de cada rodada há um sorteio entre times com a mesma campanha, por isso os confrontos seguintes aparecem como "a definir".</p>
  <div class="suica">${cols}</div>
  <h3 style="margin-top:26px;font-size:22px;text-transform:uppercase">Campanhas na Suíça</h3>
  <div class="classif">${tab.map(({ c, r }) => `<button class="t" data-time="${c}">${img(logo(c), "", c)}<b>${esc(nomeT(c))}</b><span class="num">${r[0]}-${r[1]}</span>${r[0] >= 3 ? '<span class="pill ok">Classificado</span>' : r[1] >= 3 ? '<span class="pill fora">Eliminado</span>' : '<span class="pill jog">Na disputa</span>'}</button>`).join("")}</div>
  <div id="chances"><h3 style="margin-top:26px;font-size:22px;text-transform:uppercase">Chance de classificação</h3><p class="nota">Calculando…</p></div>`;
    setTimeout(() => {
      const el = $("#chances");
      if (el) el.innerHTML = blocoChances();
    }, 60);
  }
  /* ---------- chance de classificação (Monte Carlo) ---------- */
  function forcaSuica() {
    const f = {};
    for (const p of SUICA) {
      if (p.estado !== "completed") continue;
      for (const t of p.times) {
        const o = p.times.find((x) => x !== t);
        const g = f[t.codigo] || (f[t.codigo] = { v: 0, j: 0 });
        g.v += t.vitorias || 0;
        g.j += (t.vitorias || 0) + (o.vitorias || 0);
      }
    }
    const s = {};
    for (const c of Object.keys(f)) s[c] = (f[c].v + 3) / (f[c].j + 6);
    return (c) => s[c] ?? 0.5;
  }
  function chanceJogo(a, b, md, F) {
    const pa = F(a),
      pb = F(b);
    let p = pa / (pa + pb);
    if (md === 3) p = p * p * (3 - 2 * p);
    return p;
  }
  function simularSuica(n = 10000) {
    const cods = [...new Set(SUICA.flatMap((p) => p.times.map((t) => t.codigo)).filter((c) => c !== "TBD"))];
    if (cods.length < 16) return null;
    const F = forcaSuica(),
      out = {};
    cods.forEach((c) => (out[c] = { c30: 0, cl: 0, el: 0, e03: 0 }));
    if (!SUICA.some((p) => p.estado === "completed")) {
      cods.forEach((c) => (out[c] = { c30: 0.125, cl: 0.5, el: 0.5, e03: 0.125 }));
      return out;
    }
    let sem = 20261023;
    const rnd = () => {
      sem = (sem + 0x6d2b79f5) | 0;
      let t = Math.imul(sem ^ (sem >>> 15), 1 | sem);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    const embaralhar = (a) => {
      for (let i = a.length - 1; i > 0; i--) {
        const k = (rnd() * (i + 1)) | 0;
        [a[i], a[k]] = [a[k], a[i]];
      }
      return a;
    };
    for (let it = 0; it < n; it++) {
      const v = {},
        d = {},
        jog = new Set();
      cods.forEach((c) => {
        v[c] = 0;
        d[c] = 0;
      });
      const par = (a, b) => (a < b ? a + "|" + b : b + "|" + a);
      const jogar = (a, b, md, real) => {
        let ga;
        if (real) {
          ga = real.times.find((t) => t.codigo === a).resultado === "win";
        } else ga = rnd() < chanceJogo(a, b, md, F);
        ga ? (v[a]++, d[b]++) : (v[b]++, d[a]++);
        jog.add(par(a, b));
      };
      for (const r of RODADAS) {
        const usados = new Set();
        for (const p of r) {
          const [a, b] = p.times.map((t) => t.codigo);
          if (a === "TBD" || b === "TBD") continue;
          usados.add(a);
          usados.add(b);
          jogar(a, b, p.melhorDe, p.estado === "completed" ? p : null);
        }
        const grupos = {};
        for (const c of cods) {
          if (usados.has(c) || v[c] >= 3 || d[c] >= 3) continue;
          (grupos[v[c] + "-" + d[c]] ??= []).push(c);
        }
        for (const [k, g] of Object.entries(grupos)) {
          const md = /^2-|-2$/.test(k) ? 3 : 1;
          let ord = g;
          for (let t = 0; t < 30; t++) {
            ord = embaralhar(g.slice());
            let ok = true;
            for (let i = 0; i + 1 < ord.length; i += 2)
              if (jog.has(par(ord[i], ord[i + 1]))) {
                ok = false;
                break;
              }
            if (ok) break;
          }
          for (let i = 0; i + 1 < ord.length; i += 2) jogar(ord[i], ord[i + 1], md, null);
        }
      }
      for (const c of cods) {
        const o = out[c];
        if (v[c] >= 3) {
          o.cl++;
          if (d[c] === 0) o.c30++;
        } else {
          o.el++;
          if (v[c] === 0) o.e03++;
        }
      }
    }
    for (const c of cods) for (const k in out[c]) out[c][k] /= n;
    return out;
  }
  function blocoChances() {
    const sim = simularSuica();
    if (!sim) return "";
    const jogados = SUICA.filter((p) => p.estado === "completed").length;
    const tab = Object.entries(sim).sort(
      (x, y) => y[1].cl - x[1].cl || y[1].c30 - x[1].c30 || nomeT(x[0]).localeCompare(nomeT(y[0])),
    );
    const barra = (x) => `<span class="barra-ch"><span style="width:${(x * 100).toFixed(1)}%"></span></span>`;
    const p0 = (x) =>
      x > 0 && x < 0.005 ? "<1%" : x < 1 && x > 0.995 ? ">99%" : x === 0.125 ? "12,5%" : pct(x);
    return `<h3 style="margin-top:26px;font-size:22px;text-transform:uppercase">Chance de classificação</h3>
  <p class="nota" style="margin:6px 0 12px">${jogados ? `Simulamos 10 mil vezes o resto da Fase Suíça, com sorteios sem revanche entre times de mesma campanha e os ${jogados} resultados já conhecidos. A chance de cada jogo vem das partidas vencidas por cada time neste Worlds, puxada para 50% enquanto há poucos jogos.` : `Antes da primeira rodada, todo jogo vale 50% para cada lado, então os números são iguais para todos. A partir dos primeiros resultados, 10 mil simulações do resto da fase passam a usar as vitórias de cada time neste Worlds.`}</p>
  <div class="chances" role="table"><div class="ch cab" role="row"><span></span><span>Time</span><span>Classifica</span><span>3-0</span><span>Cai 0-3</span></div>
  ${tab.map(([c, o]) => `<button class="ch" role="row" data-time="${c}">${img(logo(c), "", c)}<b>${esc(nomeT(c))}</b><span class="num">${barra(o.cl)}${p0(o.cl)}</span><span class="num">${p0(o.c30)}</span><span class="num muted">${p0(o.e03)}</span></button>`).join("")}</div>`;
  }
  function painelMata() {
    const c = (i) => (MATA[i] ? cartao(MATA[i]) : "");
    $("#p-matamata").innerHTML =
      `<p class="nota" style="margin:0 0 16px">Os oito classificados da Fase Suíça em eliminação simples, tudo em melhor de 5. Quartas e semis em Allen, no Texas, e a final no Barclays Center, em Nova York.</p>
  <div class="chave"><div class="col"><h3>Quartas</h3>${c(0)}${c(1)}${c(2)}${c(3)}</div><div class="col"><h3>Semifinais</h3>${c(4)}${c(5)}</div><div class="col final-dest"><h3>Final · 14/nov</h3>${c(6)}</div></div>`;
  }
  function painelTimes() {
    const naSuica = (c) => SUICA.some((p) => p.times.some((t) => t.codigo === c));
    const cods = Object.keys(TIMES).sort(
      (a, b) => naSuica(b) - naSuica(a) || nomeT(a).localeCompare(nomeT(b)),
    );
    $("#p-times").innerHTML =
      `<div class="grade-times">${cods.map((c) => `<button class="cartao-time" data-time="${c}">${img(logo(c), "", c)}<b>${esc(c)}</b><small>${esc(nomeT(c))} · ${esc(TIMES[c].liga || "")}${naSuica(c) ? "" : " · caiu no Play-In"}</small></button>`).join("")}</div>`;
  }

  /* ---------- folha ---------- */
  const folha = $("#folha"),
    folhaIn = $("#folha-in");
  let pararPlayer = null;
  const parar = () => {
    if (pararPlayer) {
      pararPlayer();
      pararPlayer = null;
    }
    try {
      speechSynthesis.cancel();
    } catch (_) {}
    pararGravadas();
  };
  // Pilha de telas da folha: abrir um jogador de dentro de um confronto permite voltar ao confronto.
  let pilha = [],
    atual = null;
  let SEMSP = false;
  try {
    SEMSP = localStorage.getItem("semSpoiler") === "1";
  } catch (_) {}
  function aplicarSpoiler() {
    document.body.classList.toggle("sem-spoiler", SEMSP);
    const bt = $("#bt-spoiler");
    if (bt) {
      bt.setAttribute("aria-pressed", SEMSP);
      bt.textContent = SEMSP ? "Sem spoiler: ligado" : "Sem spoiler";
    }
    for (const id of ["p-destaques", "p-meta", "p-comparar"]) {
      const el = document.getElementById(id);
      if (el && !el.querySelector(":scope>.sp-nota"))
        el.insertAdjacentHTML(
          "afterbegin",
          `<div class="sp-nota">Modo sem spoiler ligado: esta aba mostra resultados. <button class="link" data-sp-off>Desligar</button></div>`,
        );
    }
  }
  document.addEventListener("click", (e) => {
    if (e.target.closest("#bt-spoiler")) {
      SEMSP = !SEMSP;
      try {
        localStorage.setItem("semSpoiler", SEMSP ? "1" : "0");
      } catch (_) {}
      aplicarSpoiler();
    } else if (e.target.closest("[data-sp-off]")) {
      SEMSP = false;
      try {
        localStorage.setItem("semSpoiler", "0");
      } catch (_) {}
      aplicarSpoiler();
    }
  });
  function navegar(fn) {
    if (folha.open && atual) pilha.push(atual);
    atual = fn;
    fn();
  }
  const slug = (s) => String(s).trim().replace(/\s+/g, "_");
  function marcar(h) {
    try {
      history.replaceState(null, "", h ? "#" + h : location.pathname + location.search);
    } catch (_) {}
    const b = $("#copiar-link");
    if (b) {
      b.hidden = !h || window.top !== window;
      b.onclick = () => {
        navigator.clipboard?.writeText(location.href).then(
          () => {
            b.textContent = "Link copiado";
            setTimeout(() => (b.textContent = "Copiar link"), 1500);
          },
          () => {},
        );
      };
    }
  }
  function abrirFolha(html) {
    parar();
    folhaIn.innerHTML =
      `<div class="barra-folha">${pilha.length ? '<button class="voltar" id="voltar">‹ Voltar</button>' : "<span></span>"}<button class="link copiar-link" id="copiar-link" hidden>Copiar link</button><button class="fechar" aria-label="Fechar" id="fechar">×</button></div><div class="sp-aviso"><span>Modo sem spoiler: os resultados desta tela estão escondidos.</span><span class="sp-vods"></span><button class="link" id="sp-ver">Mostrar resultados</button></div><div class="sp-conteudo">` +
      html +
      `</div>`;
    folhaIn.classList.toggle("fechada", SEMSP);
    setTimeout(() => {
      const v = folhaIn.querySelector(".sp-vods"),
        a = folhaIn.querySelector(".sp-conteudo .vod a");
      if (v && a)
        v.innerHTML = `<a href="${a.href}" target="_blank" rel="noopener">▶ Ver o VOD sem spoiler</a>`;
    }, 0);
    $("#sp-ver").onclick = () => {
      folhaIn.classList.remove("fechada");
      folhaIn.querySelector(".sp-aviso").hidden = true;
    };
    if (!folha.open) folha.showModal();
    folha.scrollTop = 0;
    $("#fechar").onclick = () => folha.close();
    const v = $("#voltar");
    if (v)
      v.onclick = () => {
        atual = pilha.pop();
        atual();
      };
  }
  folha.addEventListener("click", (e) => {
    if (e.target === folha) folha.close();
  });
  folha.addEventListener("close", () => {
    parar();
    pilha = [];
    atual = null;
    marcar("");
  });

  function placarao(p) {
    const [a, b] = p.times;
    const temPlacar = p.estado === "completed" || p.estado === "inProgress";
    const lado = (t, dir) =>
      `<div class="lado ${dir ? "dir" : ""}">${dir ? "" : img(logo(t.codigo), "", t.codigo)}<div style="min-width:0"><h2>${t.codigo === "TBD" ? "A definir" : esc(nomeT(t.codigo))}</h2><div class="muted" style="font-size:13px">${esc(TIMES[t.codigo]?.liga || "")}</div></div>${dir ? img(logo(t.codigo), "", t.codigo) : ""}</div>`;
    return `<div class="eyebrow">${rotuloFase(p)} · melhor de ${p.melhorDe}</div>
  <div class="placarao">${lado(a)}<div class="centro">${temPlacar ? `<div class="pts">${a.vitorias ?? 0}<span class="x">×</span>${b.vitorias ?? 0}</div>` : `<div class="pts" style="font-size:30px;color:var(--muted)">×</div>`}<div class="muted" style="font-size:12.5px">${dataHora(p.inicio)}</div></div>${lado(b, true)}</div>`;
  }
  function abrirPartida(id, k0 = 0) {
    const p = PID[id];
    if (!p) return;
    const js = jogosDe(id);
    if (!js.length) {
      abrirFolha(placarao(p) + previa(p));
      ligarPrevia(p);
      marcar("p" + id);
      return;
    }
    abrirFolha(
      placarao(p) +
        `<div class="sub-abas" id="sub">${js.map((j, i) => `<button data-j="${i}" aria-pressed="false">Jogo ${j.numero}</button>`).join("")}<button data-j="resumo" aria-pressed="false">Resumo da série</button></div><div id="conteudo-jogo"></div>`,
    );
    const mostra = (k) => {
      document
        .querySelectorAll("#sub button")
        .forEach((b) => b.setAttribute("aria-pressed", b.dataset.j === String(k)));
      parar();
      atual = () => abrirPartida(id, k);
      $("#conteudo-jogo").innerHTML =
        k === "resumo"
          ? resumoSerie(p, js)
          : viewJogo(js[k], blocoFearless(p, js, js[k].numero, "Já usados antes deste jogo"));
      if (k !== "resumo") ligarJogo(js[k]);
    };
    document
      .querySelectorAll("#sub button")
      .forEach((b) => (b.onclick = () => mostra(b.dataset.j === "resumo" ? "resumo" : +b.dataset.j)));
    mostra(k0 === "resumo" || js[k0] ? k0 : 0);
    marcar("p" + id);
  }

  /* ---------- Fearless Draft ---------- */
  function queimados(js, ate) {
    const r = {};
    for (const j of js) {
      if (j.numero >= ate) continue;
      for (const x of j.jog) (r[x.time] ??= []).push(x.campeao);
    }
    return r;
  }
  function blocoFearless(p, js, ate, titulo) {
    if (p.melhorDe < 2) return "";
    const [A, B] = p.times.map((t) => t.codigo),
      q = queimados(js, ate),
      tot = (q[A]?.length || 0) + (q[B]?.length || 0);
    if (!tot) return "";
    const lista = (c) =>
      (q[c] || [])
        .map((k) => `<span title="${esc(camp(k).nome)}">${img(camp(k).icone, "", camp(k).nome)}</span>`)
        .join("");
    return `<div class="bloco-f"><h3>${titulo} <small>Fearless Draft: ${tot} campeões fora do resto da série, para os dois times</small></h3>${[A, B].map((c) => `<div class="linha-bans"><b>${esc(c)}</b><div class="bans queimados">${lista(c)}</div></div>`).join("")}</div>`;
  }
  function disputados(sa, sb, n = 6) {
    if (!sa || !sb) return [];
    return Object.keys(sa.camps)
      .filter((k) => sb.camps[k])
      .sort((x, y) => sb.camps[y] + sa.camps[y] - (sb.camps[x] + sa.camps[x]))
      .slice(0, n);
  }

  /* ---------- jogo encerrado ---------- */
  function linhaCab(a, b) {
    return `<div class="l"><span class="v b azul">${esc(a)}</span><span></span><span class="rot"></span><span></span><span class="v verm">${esc(b)}</span></div>`;
  }
  function linhaCmp(a, b, va, vb, rot) {
    const tot = (va || 0) + (vb || 0) || 1;
    return `<div class="l"><span class="v b">${a}</span><div class="barra esq"><i style="width:${((va || 0) / tot) * 100}%;background:var(--blue)"></i></div><span class="rot">${rot}</span><div class="barra"><i style="width:${((vb || 0) / tot) * 100}%;background:var(--red)"></i></div><span class="v">${b}</span></div>`;
  }
  // link do VOD no segundo s do jogo (estimado; o vídeo começa no draft)
  function linkVod(j, s) {
    const v = j.vod;
    if (!v) return "";
    return `https://www.youtube.com/watch?v=${encodeURIComponent(v.yt)}${v.t0 != null ? `&t=${Math.max(0, Math.round(v.t0 + s - 5))}s` : ""}`;
  }
  function viewJogo(j, extra = "") {
    const T = j.tot,
      f = (x) => x.toLocaleString("pt-BR");
    const s15 = j.s15 ? j.s15[1] - j.s15[2] : null;
    const primeiro = (n, e) =>
      `<div class="l"><span class="v b azul">${e?.lado === "blue" ? "✓ " + mmss(e.s) : ""}</span><span></span><span class="rot">${n}</span><span></span><span class="v verm">${e?.lado === "red" ? mmss(e.s) + " ✓" : ""}</span></div>`;
    return `<button class="botao-video" id="ver-video"><span class="play"></span><span><b>Assistir ao jogo narrado</b><span>Os principais lances dos ${min(j.duracao)} minutos, um atrás do outro, no mapa e com narração</span></span></button>
  <div id="area-video"></div>
  ${j.vod ? `<p class="vod"><a href="${linkVod(j, 0)}" target="_blank" rel="noopener">▶ Assistir ao VOD oficial${j.vod.idioma === "pt-BR" ? " em português" : " (em inglês)"}</a><small>no YouTube do LoL Esports · o início do jogo no vídeo é aproximado</small></p>` : ""}
  <div class="bloco-f"><h3>Jogo ${j.numero} <small>${mini(j.venc)} vitória de ${esc(nomeT(j.venc))} em ${mmss(j.duracao)} · patch ${esc(j.patch)}</small></h3>
    <div class="cmp">${linhaCab(j.az + " · lado azul", j.vm + " · lado vermelho")}
    ${linhaCmp(T.blue.abates, T.red.abates, T.blue.abates, T.red.abates, "Abates")}
    ${linhaCmp((T.blue.ouro / 1000).toFixed(1) + "k", (T.red.ouro / 1000).toFixed(1) + "k", T.blue.ouro, T.red.ouro, "Ouro")}
    ${linhaCmp(T.blue.torres, T.red.torres, T.blue.torres, T.red.torres, "Torres")}
    ${linhaCmp(T.blue.dragoes, T.red.dragoes, T.blue.dragoes, T.red.dragoes, "Dragões")}
    ${linhaCmp(T.blue.barons, T.red.barons, T.blue.barons, T.red.barons, "Barões")}
    ${j.lp ? linhaCmp(j.lp.arautos.blue ?? 0, j.lp.arautos.red ?? 0, j.lp.arautos.blue ?? 0, j.lp.arautos.red ?? 0, "Arautos") + linhaCmp(j.lp.larvas.blue ?? 0, j.lp.larvas.red ?? 0, j.lp.larvas.blue ?? 0, j.lp.larvas.red ?? 0, "Vastilarvas") : ""}
    ${s15 != null ? linhaCmp(s15 > 0 ? mil(s15) : "", s15 < 0 ? mil(-s15) : "", Math.max(0, s15), Math.max(0, -s15), "Vantagem aos 15 min") : ""}
    ${primeiro("First blood", j.fb)}${primeiro("Primeiro dragão", j.fd)}${primeiro("Primeira torre", j.ft)}${primeiro("Primeiro Barão", j.fbar)}</div></div>
  ${extra}<div class="bloco-f"><h3>Bans</h3>${j.lp ? ["blue", "red"].map((l) => `<div class="linha-bans"><b class="${l === "blue" ? "azul" : "verm"}">${esc(j.lados[l])}</b><div class="bans">${j.lp.bans[l].map((b) => `<span title="${esc(camp(b).nome)}">${img(camp(b).icone, "", camp(b).nome)}</span>`).join("") || '<span class="muted">sem bans</span>'}</div></div>`).join("") : '<p class="muted" style="margin:0">Os bans deste jogo ainda não foram registrados na Leaguepedia.</p>'}</div>
  <div class="bloco-f"><h3>Ouro ao longo do jogo <small>diferença entre os times; acima da linha, vantagem de ${esc(j.az)}</small></h3>${graficoOuro(j, j.duracao, false)}</div>
  <div class="bloco-f"><h3>Chance de vitória <small>acima da linha, ${esc(j.az)} favorito; o ponto dourado marca o pior momento de quem venceu</small></h3>${graficoChance(j)}</div>
  <div class="bloco-f"><h3>Jogadores <small>clique num jogador para ver os números dele · Ouro@15: diferença para o rival de rota aos 15 min</small></h3>${tabelaJogadores(j)}</div>`;
  }
  function graficoOuro(j, ate, escuro) {
    const L = 640,
      H = 150,
      pad = 34;
    const S = j.serie;
    const dmax = Math.max(2000, ...S.map((x) => Math.abs(x[1] - x[2])));
    const lim = Math.ceil(dmax / 2000) * 2000;
    const X = (s) => pad + (s / j.duracao) * (L - pad - 8),
      Y = (d) => H / 2 - (d / lim) * (H / 2 - 14);
    const pts = S.filter((x) => x[0] <= ate)
      .map((x) => `${X(x[0]).toFixed(1)},${Y(x[1] - x[2]).toFixed(1)}`)
      .join(" ");
    const fg = escuro ? "#e9edf2" : "var(--fg)",
      az = escuro ? "#4ea3f0" : "var(--blue)",
      vm = escuro ? "#f0675c" : "var(--red)";
    const ticks = [];
    for (let m = 0; m * 60 <= j.duracao; m += 5) ticks.push(m);
    const id = "g" + j.id + (escuro ? "e" : "");
    return `<svg viewBox="0 0 ${L} ${H}" style="width:100%;height:auto;display:block" role="img" aria-label="Diferença de ouro entre os times">
    ${ticks.map((m) => `<line x1="${X(m * 60)}" x2="${X(m * 60)}" y1="8" y2="${H - 16}" stroke="${fg}" stroke-opacity=".1"/><text x="${X(m * 60)}" y="${H - 3}" font-size="10" text-anchor="middle" fill="${fg}" fill-opacity=".6" font-family="JetBrains Mono,monospace">${m}'</text>`).join("")}
    <line x1="${pad}" x2="${L - 8}" y1="${H / 2}" y2="${H / 2}" stroke="${fg}" stroke-opacity=".35"/>
    <text x="0" y="${Y(lim) + 4}" font-size="10" fill="${az}" font-family="JetBrains Mono,monospace">+${lim / 1000}k</text>
    <text x="0" y="${Y(-lim) + 4}" font-size="10" fill="${vm}" font-family="JetBrains Mono,monospace">+${lim / 1000}k</text>
    <clipPath id="${id}a"><rect x="0" y="0" width="${L}" height="${H / 2}"/></clipPath><clipPath id="${id}b"><rect x="0" y="${H / 2}" width="${L}" height="${H / 2}"/></clipPath>
    <polyline points="${pts}" fill="none" stroke="${az}" stroke-width="2.2" stroke-linejoin="round" clip-path="url(#${id}a)"/>
    <polyline points="${pts}" fill="none" stroke="${vm}" stroke-width="2.2" stroke-linejoin="round" clip-path="url(#${id}b)"/>
  </svg>`;
  }
  function tabelaJogadores(j) {
    const linha = (x) => {
      const c = camp(x.campeao);
      const foto = FOTO[x.jogadorId];
      const dpm = x.danoTotal != null ? Math.round(x.danoTotal / (j.duracao / 60)) : null;
      return `<tr class="clic ${x.pid === 5 ? "sep" : ""}" data-jogador="${x.jogadorId}" data-jogo="${j.id}" tabindex="0"><td><div class="jog">${foto ? `<img class="foto" src="${foto}" alt="">` : `<span class="foto"></span>`}${img(c.icone, "camp", c.nome)}<span><b class="${x.lado === "blue" ? "azul" : "verm"}">${esc(x.nick)}</b><small>${esc(c.nome)} · ${ROTA_PT[x.rota] || x.rota}</small></span></div></td>
    <td>${x.k}/${x.d}/${x.a}</td><td>${n1(kda(x))}</td><td>${x.cs}</td><td>${n1(x.cs / (j.duracao / 60))}</td><td>${(x.ouro / 1000).toFixed(1)}k</td>
    <td class="${x.gd15 > 0 ? "pos" : x.gd15 < 0 ? "neg" : ""}">${sinal(x.gd15)}</td><td>${dpm ?? "–"}</td><td>${pct(x.dano)}</td><td>${pct(x.kp)}</td><td>${x.visao ?? x.wards ?? "–"}</td>
    <td><div class="itens">${(x.itens || [])
      .filter((i) => W.itens[i])
      .map(
        (i) =>
          `<img src="${W.itens[i].icone}" alt="${esc(W.itens[i].nome)}" title="${esc(W.itens[i].nome)}">`,
      )
      .join("")}</div></td></tr>`;
    };
    return `<div class="tab-wrap"><table class="est"><thead><tr><th>Jogador</th><th>K/D/A</th><th>KDA</th><th>CS</th><th>CS/min</th><th>Ouro</th><th>Ouro@15</th><th title="Dano a campeões por minuto">DPM</th><th title="Parcela do dano a campeões do time">% dano</th><th title="Participação em abates">KP</th><th title="Placar de visão (ou sentinelas colocadas quando a Leaguepedia não tem o jogo)">Visão</th><th>Itens finais</th></tr></thead><tbody>${j.jog.map(linha).join("")}</tbody></table></div>`;
  }
  function resumoSerie(p, js) {
    const [A, B] = p.times.map((t) => t.codigo);
    const soma = (c, f) => js.reduce((s, j) => s + f(j, ladoDe(j, c)), 0);
    const linhas = [
      ["Abates", (j, l) => j.tot[l].abates],
      ["Torres", (j, l) => j.tot[l].torres],
      ["Dragões", (j, l) => j.tot[l].dragoes],
      ["Barões", (j, l) => j.tot[l].barons],
      ["First bloods", (j, l) => (j.fb?.lado === l ? 1 : 0)],
    ];
    const ac = {};
    for (const j of js)
      for (const x of j.jog) {
        const y = (ac[x.jogadorId] = ac[x.jogadorId] || { ...x, k: 0, d: 0, a: 0, camps: [] });
        y.k += x.k;
        y.d += x.d;
        y.a += x.a;
        y.camps.push(x.campeao);
      }
    const venc = (p.times.find((t) => t.resultado === "win") || {}).codigo;
    const mvp = Object.values(ac)
      .filter((x) => x.time === venc)
      .sort((a, b) => kda(b) - kda(a))[0];
    return `<div class="bloco-f"><h3>Série</h3><div class="cmp">${linhaCab(A, B)}${linhas
      .map(([n, f]) => {
        const a = soma(A, f),
          b = soma(B, f);
        return linhaCmp(a, b, a, b, n);
      })
      .join("")}</div></div>
   ${mvp ? `<div class="bloco-f"><h3>Destaque da série <small>melhor KDA do vencedor</small></h3><div class="jog clic" data-jogador="${mvp.jogadorId}">${FOTO[mvp.jogadorId] ? `<img class="foto" style="width:64px;height:64px" src="${FOTO[mvp.jogadorId]}" alt="">` : ""}<span><b style="font-family:var(--display);font-size:24px">${esc(mvp.nick)}</b><small style="font-size:13px">${ROTA_PT[mvp.rota]} do ${esc(nomeT(mvp.time))} · ${mvp.k}/${mvp.d}/${mvp.a} na série · KDA ${n1(kda(mvp))} · ${mvp.camps.map((c) => esc(camp(c).nome)).join(", ")}</small></span></div></div>` : ""}
   ${blocoFearless(p, js, 99, "Campeões queimados na série")}
   <div class="bloco-f"><h3>Jogo a jogo</h3><div class="campanha">${js.map((j) => `<div class="r"><span class="res v">${j.numero}</span><span>${mini(j.venc)} <b>${esc(nomeT(j.venc))}</b> venceu em ${mmss(j.duracao)} · abates ${j.tot.blue.abates} × ${j.tot.red.abates}</span><span class="muted num" style="font-size:12px">${esc(j.az)} no azul</span></div>`).join("")}</div></div>`;
  }

  /* ---------- narração de um jogo ---------- */
  function roteiroJogo(j) {
    // Narração no estilo de transmissão brasileira: frases curtas, variadas e com emoção.
    let sem = [...String(j.id)].reduce((a, c) => (a * 31 + c.charCodeAt(0)) | 0, 7);
    const rnd = () => {
      sem = (sem * 1103515245 + 12345) | 0;
      return ((sem >>> 8) & 0xffff) / 0x10000;
    };
    const um = (...op) => op[Math.floor(rnd() * op.length)];
    const jg = (pid) => j.jog[pid - 1];
    const T = (l) => j.lados[l];
    const N = (l) => nomeT(j.lados[l]);
    const R = [];
    const add = (s, txt, tipo, ev, hype) => R.push({ s, txt, tipo, ev, hype });
    const cm = (x) => camp(x.campeao).nome;
    const vl = j.vencedor,
      pd = outro(vl);
    const placarSerie = jogosDe(j.partida).filter((g) => g.numero < j.numero);
    const vA = placarSerie.filter((g) => g.venc === j.az).length,
      vB = placarSerie.filter((g) => g.venc === j.vm).length;
    add(
      0,
      j.numero === 1
        ? um(
            `Tá valendo! Jogo 1 entre ${N("blue")} e ${N("red")}. ${T("blue")} começa no lado azul.`,
            `Começou! ${N("blue")} do lado azul, ${N("red")} do vermelho. Bora pro jogo 1!`,
          )
        : um(
            `Jogo ${j.numero}! A série está ${Math.max(vA, vB)} a ${Math.min(vA, vB)}${vA === vB ? ", tudo igual" : ` para ${vA > vB ? T("blue") : T("red")}`}. ${T("blue")} ${jogosDe(j.partida).find((g) => g.numero === j.numero - 1)?.az === j.az ? "segue" : "agora"} no lado azul.`,
            `Vamos pro jogo ${j.numero}, com ${vA > vB ? `${T("blue")} na frente, ${vA} a ${vB}` : vB > vA ? `${T("red")} na frente, ${vB} a ${vA}` : `a série empatada em ${vA} a ${vB}`}.`,
          ),
      "inicio",
    );
    const fb = j.fb;
    if (fb) {
      const k = jg(fb.por[0]),
        v = jg(fb.vitimas[0]);
      const onde = v ? (v.rota === "jungle" ? "na selva" : "na " + ROTA_LANE[v.rota]) : "";
      add(
        fb.s,
        k && v
          ? um(
              `PRIMEIRO SANGUE! ${k.nick} de ${cm(k)} pega o ${v.nick} ${onde}!`,
              `Abriu o placar! ${k.nick} acha o ${v.nick} ${onde} e o first blood é do ${T(fb.lado)}!`,
              `Olha o first blood! ${k.nick}, de ${cm(k)}, em cima do ${v.nick}, com ${min(fb.s)} minutos de jogo!`,
            )
          : `First blood para ${N(fb.lado)}!`,
        "abate",
        fb,
        true,
      );
    }
    if (j.fd) {
      const d = DRAG[j.fd.dragao]?.[0] || "";
      add(
        j.fd.s,
        fb && fb.lado !== j.fd.lado
          ? um(
              `Mas ${T(j.fd.lado)} responde no objetivo: primeiro dragão${d ? ", o " + d : ""}, é deles.`,
              `${T(j.fd.lado)} troca o abate pelo dragão${d ? " " + d : ""}. Negócio justo.`,
            )
          : um(
              `E ${T(j.fd.lado)} emenda o primeiro dragão${d ? ", o " + d : ""}.`,
              `Dragão ${d} garantido para ${T(j.fd.lado)}. Começo controlado.`,
            ),
        "dragao",
        j.fd,
      );
    }
    if (j.ft)
      add(
        j.ft.s,
        um(
          `Caiu a primeira torre! Ponto pra ${T(j.ft.lado)}, com ${min(j.ft.s)} minutos.`,
          `${T(j.ft.lado)} derruba a primeira torre e o mapa começa a abrir.`,
          `Primeira torre no chão, e quem levou foi ${T(j.ft.lado)}.`,
        ),
        "torre",
        j.ft,
      );
    const ab = j.ev.filter((e) => e.tipo === "abate");
    const lutas = [];
    let cur = null;
    for (const e of ab) {
      if (cur && e.s - cur.fim <= 30) {
        cur.fim = e.s;
        cur.ev.push(e);
      } else {
        cur = { ini: e.s, fim: e.s, ev: [e] };
        lutas.push(cur);
      }
    }
    for (const l of lutas) {
      const b = l.ev.filter((e) => e.lado === "blue").reduce((s, e) => s + e.n, 0),
        r = l.ev.filter((e) => e.lado === "red").reduce((s, e) => s + e.n, 0);
      if (b + r < 3 || l.ev.includes(fb)) continue;
      const v = b > r ? "blue" : r > b ? "red" : null;
      const por = {};
      l.ev.forEach((e) => e.por.slice(0, 1).forEach((p) => (por[p] = (por[p] || 0) + 1)));
      const top = Object.entries(por).sort((a, b) => b[1] - a[1])[0];
      const heroi = top && top[1] >= 2 ? jg(+top[0]) : null;
      const mx = Math.max(b, r),
        mn = Math.min(b, r);
      const multi = heroi
        ? { 2: "double kill", 3: "TRIPLE KILL", 4: "QUADRA KILL", 5: "PENTAKILL" }[Math.min(5, top[1])]
        : "";
      const txt = !v
        ? um(
            `Troca franca! ${b} pra cada lado e ninguém sai no lucro.`,
            `Que briga! Termina ${b} a ${r}, tudo igual.`,
          )
        : mn === 0 && mx >= 4
          ? um(
              `QUE MASSACRE! ${T(v)} limpa a luta, ${mx} a zero!`,
              `ACE! Não sobrou ninguém! ${T(v)} passa o rodo, ${mx} a 0!`,
            )
          : mx >= 5
            ? um(
                `LUTA GIGANTE! ${T(v)} leva a melhor, ${mx} a ${mn}!`,
                `Que teamfight! ${T(v)} vence a briga, ${mx} abates contra ${mn}!`,
              )
            : um(
                `Briga boa pra ${T(v)}, ${mx} a ${mn}.`,
                `${T(v)} sai na frente na luta, ${mx} a ${mn}.`,
                `Mais uma pra conta do ${T(v)}: ${mx} a ${mn} na briga.`,
              );
      add(
        l.ini,
        txt +
          (heroi && top[1] >= 3
            ? ` ${multi}! ${heroi.nick} de ${cm(heroi)} tá impossível!`
            : heroi && top[1] === 2 && rnd() < 0.5
              ? ` Double kill do ${heroi.nick}!`
              : ""),
        "luta",
        { ...l.ev[0], lado: v || l.ev[0].lado },
        mx >= 4 || (heroi && top[1] >= 3),
      );
    }
    for (const l of ["blue", "red"]) {
      const ds = j.ev.filter((e) => e.tipo === "dragao" && e.lado === l && e.dragao !== "elder");
      if (ds.length >= 4)
        add(
          ds[3].s,
          um(
            `ALMA DO DRAGÃO! ${T(l)} garante a alma ${DRAG[ds[3].dragao] ? "de " + DRAG[ds[3].dragao][0] : ""}, e isso pesa demais!`,
            `É a alma! ${T(l)} fecha os quatro dragões e fica muito mais forte.`,
          ),
          "dragao",
          ds[3],
          true,
        );
    }
    j.ev
      .filter((e) => e.tipo === "dragao" && e.dragao === "elder")
      .forEach((e) =>
        add(
          e.s,
          um(
            `DRAGÃO ANCIÃO! ${T(e.lado)} pega o Ancião e agora queima tudo!`,
            `O Ancião é do ${T(e.lado)}! Momento decisivo!`,
          ),
          "dragao",
          e,
          true,
        ),
      );
    j.ev
      .filter((e) => e.tipo === "barao")
      .forEach((e, i) =>
        add(
          e.s,
          i
            ? um(`Mais um Barão pro ${T(e.lado)}!`, `${T(e.lado)} de novo no Barão! Controle total.`)
            : um(
                `BARÃO! ${T(e.lado)} garante o Barão Na'Shor com ${min(e.s)} minutos!`,
                `Olha o Barão! É do ${T(e.lado)}, e agora eles vão pra cima!`,
              ),
          "barao",
          e,
          !i,
        ),
      );
    for (const l of ["blue", "red"]) {
      const e = j.ev.find((e) => e.tipo === "inibidor" && e.lado === l);
      if (e)
        add(
          e.s,
          um(
            `Caiu o inibidor! ${T(l)} invade a base adversária!`,
            `${T(l)} quebra o inibidor e os super minions vêm aí!`,
          ),
          "inibidor",
          e,
        );
    }
    if (j.duracao > 15 * 60 + 90) {
      const x = j.serie.reduce((a, b) => (Math.abs(b[0] - 900) < Math.abs(a[0] - 900) ? b : a));
      const d = x[1] - x[2];
      const k = (Math.abs(d) / 1000).toFixed(1).replace(".", ",").replace(",0", "");
      add(
        900,
        Math.abs(d) < 800
          ? um(
              `Quinze minutos e o ouro tá colado. Jogo aberto!`,
              `Bateu os 15 e ninguém se distanciou. Tudo pode acontecer.`,
            )
          : Math.abs(d) > 5000
            ? um(
                `Quinze minutos e ${T(d > 0 ? "blue" : "red")} já abre ${k} mil de ouro. Tá dominando!`,
                `${k} mil de vantagem pro ${T(d > 0 ? "blue" : "red")} aos 15. Que começo!`,
              )
            : um(
                `Aos 15, ${T(d > 0 ? "blue" : "red")} tem ${k} mil de ouro a mais.`,
                `${T(d > 0 ? "blue" : "red")} vai na frente aos 15, ${k} mil de vantagem.`,
              ),
        "ouro",
      );
    }
    let ant = 0;
    for (const x of j.serie) {
      const d = x[1] - x[2];
      if (x[0] > 600 && ant && Math.sign(d) !== Math.sign(ant) && Math.abs(ant) > 2500 && Math.abs(d) > 500) {
        add(
          x[0],
          um(
            `VIRADA! ${T(d > 0 ? "blue" : "red")} passa à frente no ouro! Que reação!`,
            `Não acredito! ${T(d > 0 ? "blue" : "red")} virou o jogo no ouro!`,
          ),
          "ouro",
          null,
          true,
        );
        ant = d;
        continue;
      }
      if (Math.abs(d) > Math.abs(ant) || Math.sign(d) !== Math.sign(ant)) ant = d;
    }
    const melhor = j.jog.filter((x) => x.lado === vl).sort((a, b) => kda(b) - kda(a))[0];
    const dif = j.tot[vl].abates - j.tot[pd].abates;
    const serieFim = placarSerie.filter((g) => g.venc === j.venc).length + 1;
    const precisa = Math.ceil((PID[j.partida]?.melhorDe || 1) / 2);
    add(
      j.duracao,
      (serieFim >= precisa
        ? um(
            `ACABOU! ${N(vl)} vence e fecha a série!`,
            `É DO ${T(vl).toUpperCase()}! Vitória e série garantida!`,
          )
        : um(`Fim de jogo! Vitória do ${N(vl)}!`, `Explode o nexus! ${N(vl)} leva essa!`)) +
        ` ${dif >= 10 ? `Atropelo, ${j.tot[vl].abates} a ${j.tot[pd].abates} nos abates.` : dif <= 0 ? `E olha que perdeu nos abates, ${j.tot[vl].abates} a ${j.tot[pd].abates}!` : `${j.tot[vl].abates} a ${j.tot[pd].abates} nos abates.`}` +
        (melhor
          ? ` Grande nome: ${melhor.nick}, de ${cm(melhor)}, ${melhor.k} ${melhor.k === 1 ? "abate" : "abates"}, ${melhor.d} ${melhor.d === 1 ? "morte" : "mortes"} e ${melhor.a} ${melhor.a === 1 ? "assistência" : "assistências"}.`
          : ""),
      "fim",
      { lado: vl },
      true,
    );
    return R.sort((a, b) => a.s - b.s);
  }

  // Usado por gerar_audio.py para gravar a narração com voz neural.
  window.__roteiros = () =>
    JOGOS.map((j) => ({ id: j.id, falas: roteiroJogo(j).map((r) => ({ txt: r.txt, hype: !!r.hype })) }));

  /* ---------- voz ---------- */
  // Narração gravada (voz neural): um mp3 por jogo em audio/<id>.mp3, com o início e a duração de cada fala em W.audio.
  const AUDIO = W.audio || {};
  const _aud = {};
  function falaGravada(j, k, txt) {
    const a = AUDIO[j.id];
    if (!a || !a.falas[k] || a.falas[k][0] !== txt) return null;
    return a.falas[k];
  }
  function tocarGravada(j, f, vel) {
    return new Promise((res) => {
      let el = _aud[j.id];
      if (!el) {
        el = _aud[j.id] = new Audio(AUDIO[j.id].src || "audio/" + j.id + ".mp3");
        el.preload = "auto";
      }
      let feito = false;
      const fim = () => {
        if (feito) return;
        feito = true;
        try {
          el.pause();
        } catch (_) {}
        res(true);
      };
      try {
        el.playbackRate = vel || 1;
        el.currentTime = f[1];
        const pr = el.play();
        if (pr && pr.catch)
          pr.catch(() => {
            if (!feito) {
              feito = true;
              res(false);
            }
          });
        setTimeout(fim, (f[2] * 1000) / (vel || 1) + 60);
      } catch (_) {
        feito = true;
        res(false);
      }
    });
  }
  function pararGravadas() {
    Object.values(_aud).forEach((a) => {
      try {
        a.pause();
      } catch (_) {}
    });
  }
  let vozLigada = true;
  // Vozes "Natural"/"Online" (Edge) e as do Google (Chrome) soam bem melhor que as vozes locais padrão.
  function notaVoz(v) {
    const n = v.name;
    let s = 0;
    if (/natural|neural|online/i.test(n)) s += 50;
    if (/google/i.test(n)) s += 30;
    if (/francisca|thalita|antonio|luciana|felipe|camila|vitoria|donato/i.test(n)) s += 15;
    if (/pt[-_]BR/i.test(v.lang)) s += 10;
    if (!v.localService) s += 5;
    return s;
  }
  function vozesPt() {
    try {
      return speechSynthesis
        .getVoices()
        .filter((x) => /^pt/i.test(x.lang))
        .sort((a, b) => notaVoz(b) - notaVoz(a));
    } catch (_) {
      return [];
    }
  }
  function vozPt() {
    const vs = vozesPt();
    let nome = null;
    try {
      nome = localStorage.getItem("voz");
    } catch (_) {}
    return vs.find((v) => v.name === nome) || vs[0] || null;
  }
  function seletorVoz() {
    const vs = vozesPt();
    if (vs.length < 2) return "";
    const atual = vozPt();
    return `<select data-escolhe-voz aria-label="Voz da narração">${vs.map((v) => `<option ${v === atual ? "selected" : ""} value="${esc(v.name)}">${esc(v.name.replace(/^(Microsoft|Google) /, "").replace(/ - .*| Online.*| \(.*\)/, "") + (/natural|online/i.test(v.name) ? " (natural)" : ""))}</option>`).join("")}</select>`;
  }
  function ligarSeletorVoz(raiz) {
    const s = raiz.querySelector("[data-escolhe-voz]");
    if (s)
      s.onchange = () => {
        try {
          localStorage.setItem("voz", s.value);
        } catch (_) {}
      };
  }
  try {
    speechSynthesis.addEventListener("voiceschanged", () =>
      document.querySelectorAll("[data-lugar-voz]").forEach((el) => {
        el.innerHTML = seletorVoz();
        ligarSeletorVoz(el);
      }),
    );
  } catch (_) {}
  function falar(txt, vel, hype) {
    // Sem pausas artificiais: a próxima fala começa assim que a voz termina. Falas de lance forte saem mais rápidas e agudas.
    return new Promise((res) => {
      const estim = Math.min(4200, 900 + txt.length * 26) / vel;
      if (!vozLigada || !("speechSynthesis" in window)) {
        setTimeout(res, estim);
        return;
      }
      try {
        const u = new SpeechSynthesisUtterance(txt);
        u.lang = "pt-BR";
        const v = vozPt();
        if (v) u.voice = v;
        const natural = /natural|neural|online|google/i.test(v?.name || "");
        u.rate = Math.min(1.6, (natural ? 1.18 : 1.1) * (hype ? 1.08 : 1) * Math.sqrt(vel));
        u.pitch = hype ? 1.15 : 1.02;
        let feito = false;
        const ok = () => {
          if (!feito) {
            feito = true;
            res();
          }
        };
        u.onend = ok;
        u.onerror = () => setTimeout(ok, 300);
        setTimeout(ok, 2500 + txt.length * 80);
        if (speechSynthesis.speaking || speechSynthesis.pending) speechSynthesis.cancel();
        speechSynthesis.speak(u);
      } catch (_) {
        setTimeout(res, estim);
      }
    });
  }

  /* ---------- mapa ---------- */
  const imgCache = {};
  function im(src) {
    if (!src) return null;
    if (!imgCache[src]) {
      const i = new Image();
      i.src = src;
      imgCache[src] = i;
    }
    return imgCache[src];
  }
  const POS = {
    top: [
      [0.12, 0.32],
      [0.15, 0.15],
      [0.32, 0.12],
    ],
    mid: [
      [0.42, 0.58],
      [0.5, 0.5],
      [0.58, 0.42],
    ],
    bottom: [
      [0.68, 0.88],
      [0.85, 0.85],
      [0.88, 0.68],
    ],
    jungle: [
      [0.28, 0.5],
      [0.47, 0.72],
      [0.53, 0.28],
      [0.72, 0.5],
      [0.34, 0.64],
      [0.66, 0.36],
    ],
  };
  POS.support = POS.bottom;
  const DRAGAO = [0.67, 0.69],
    BARAO = [0.33, 0.31];
  function posEvento(e, j, seed) {
    const r = (k) => {
      const x = Math.sin(seed * 91.7 + k * 47.3) * 43758.5453;
      return x - Math.floor(x);
    };
    let b;
    if (e.tipo === "dragao") b = DRAGAO;
    else if (e.tipo === "barao") b = BARAO;
    else if (e.tipo === "abate") {
      const v = j.jog[(e.vitimas[0] || e.por[0] || 1) - 1];
      const op = POS[v?.rota] || POS.mid;
      b = op[Math.floor(r(1) * op.length)];
    } else if (e.tipo === "torre" || e.tipo === "inibidor") {
      const d = e.tipo === "inibidor" ? 0.07 : 0.18 + r(3) * 0.12;
      b =
        e.lado === "blue"
          ? [0.9 - d * (r(2) < 0.5 ? 1 : 0.3), 0.1 + d * (r(2) < 0.5 ? 0.3 : 1)]
          : [0.1 + d * (r(2) < 0.5 ? 1 : 0.3), 0.9 - d * (r(2) < 0.5 ? 0.3 : 1)];
    } else b = [0.5, 0.5];
    return [b[0] + (r(4) - 0.5) * 0.05, b[1] + (r(5) - 0.5) * 0.05];
  }
  function desenharMapa(cv, j, t, marcas) {
    const ctx = cv.getContext("2d");
    const S = cv.width,
      c = (x) => x * S;
    ctx.fillStyle = "#13221a";
    ctx.fillRect(0, 0, S, S);
    ctx.fillStyle = "#1a3123";
    [
      [0.3, 0.56, 0.15],
      [0.53, 0.76, 0.13],
      [0.44, 0.26, 0.15],
      [0.74, 0.47, 0.13],
    ].forEach(([x, y, r]) => {
      ctx.beginPath();
      ctx.arc(c(x), c(y), c(r), 0, 7);
      ctx.fill();
    });
    ctx.strokeStyle = "#1d4660";
    ctx.lineWidth = c(0.07);
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(c(0.06), c(0.06));
    ctx.quadraticCurveTo(c(0.5), c(0.5), c(0.94), c(0.94));
    ctx.stroke();
    ctx.strokeStyle = "#3e4d38";
    ctx.lineWidth = c(0.035);
    ctx.lineJoin = "round";
    ctx.beginPath();
    ctx.moveTo(c(0.12), c(0.88));
    ctx.lineTo(c(0.12), c(0.12));
    ctx.lineTo(c(0.88), c(0.12));
    ctx.moveTo(c(0.12), c(0.88));
    ctx.lineTo(c(0.88), c(0.88));
    ctx.lineTo(c(0.88), c(0.12));
    ctx.moveTo(c(0.15), c(0.85));
    ctx.lineTo(c(0.85), c(0.15));
    ctx.stroke();
    [
      ["#6b5a2c", DRAGAO],
      ["#4b3a66", BARAO],
    ].forEach(([cor, [x, y]]) => {
      ctx.fillStyle = cor;
      ctx.beginPath();
      ctx.arc(c(x), c(y), c(0.045), 0, 7);
      ctx.fill();
    });
    [
      ["#4ea3f0", [0.1, 0.9]],
      ["#f0675c", [0.9, 0.1]],
    ].forEach(([cor, [x, y]]) => {
      ctx.fillStyle = cor;
      ctx.globalAlpha = 0.22;
      ctx.beginPath();
      ctx.arc(c(x), c(y), c(0.14), 0, 7);
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.beginPath();
      ctx.arc(c(x), c(y), c(0.035), 0, 7);
      ctx.fill();
    });
    ctx.textAlign = "center";
    for (const m of marcas) {
      const idade = t - m.s;
      if (idade < 0 || idade > 80) continue;
      const a = 1 - idade / 80;
      const [x, y] = m.p;
      const cor = m.e.lado === "blue" ? "#4ea3f0" : "#f0675c";
      ctx.globalAlpha = Math.max(0.15, a);
      if (m.e.tipo === "abate") {
        const v = j.jog[(m.e.vitimas[0] || 1) - 1],
          k = j.jog[(m.e.por[0] || 1) - 1];
        const iv = im(camp(v?.campeao).icone),
          ik = im(camp(k?.campeao).icone);
        const R = c(0.045);
        ctx.strokeStyle = cor;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(c(x), c(y), R + 3 + (PARADO ? 0 : (1 - a) * 16), 0, 7);
        ctx.stroke();
        if (iv && iv.complete && iv.naturalWidth) {
          ctx.save();
          ctx.beginPath();
          ctx.arc(c(x), c(y), R, 0, 7);
          ctx.clip();
          ctx.filter = "grayscale(1) brightness(.75)";
          ctx.drawImage(iv, c(x) - R, c(y) - R, R * 2, R * 2);
          ctx.restore();
        }
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(c(x) - R * 0.45, c(y) - R * 0.45);
        ctx.lineTo(c(x) + R * 0.45, c(y) + R * 0.45);
        ctx.moveTo(c(x) + R * 0.45, c(y) - R * 0.45);
        ctx.lineTo(c(x) - R * 0.45, c(y) + R * 0.45);
        ctx.stroke();
        if (ik && ik.complete && ik.naturalWidth) {
          const r2 = R * 0.62,
            kx = c(x) + R * 0.95,
            ky = c(y) - R * 0.95;
          ctx.save();
          ctx.beginPath();
          ctx.arc(kx, ky, r2, 0, 7);
          ctx.clip();
          ctx.drawImage(ik, kx - r2, ky - r2, r2 * 2, r2 * 2);
          ctx.restore();
          ctx.strokeStyle = cor;
          ctx.lineWidth = 2.5;
          ctx.beginPath();
          ctx.arc(kx, ky, r2, 0, 7);
          ctx.stroke();
        }
        if (m.e.n > 1) {
          ctx.fillStyle = "#fff";
          ctx.font = `700 ${Math.round(S * 0.04)}px Barlow Condensed,sans-serif`;
          ctx.fillText("×" + m.e.n, c(x), c(y) + R + S * 0.04);
        }
      } else {
        const R = c(m.e.tipo === "barao" ? 0.055 : 0.042);
        ctx.fillStyle =
          m.e.tipo === "dragao" ? DRAG[m.e.dragao]?.[1] || cor : m.e.tipo === "barao" ? "#a77ce8" : cor;
        ctx.beginPath();
        if (m.e.tipo === "torre" || m.e.tipo === "inibidor")
          ctx.rect(c(x) - R * 0.55, c(y) - R * 0.55, R * 1.1, R * 1.1);
        else ctx.arc(c(x), c(y), R * 0.7, 0, 7);
        ctx.fill();
        ctx.strokeStyle = cor;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(c(x), c(y), R + (PARADO ? 0 : (1 - a) * 18), 0, 7);
        ctx.stroke();
        ctx.fillStyle = "#fff";
        ctx.font = `700 ${Math.round(S * 0.032)}px Barlow Condensed,sans-serif`;
        ctx.fillText(
          { dragao: DRAG[m.e.dragao]?.[0] || "Dragão", barao: "Barão", torre: "Torre", inibidor: "Inibidor" }[
            m.e.tipo
          ] || "",
          c(x),
          c(y) + R + S * 0.04,
        );
      }
      ctx.globalAlpha = 1;
    }
    ctx.textAlign = "left";
  }

  /* ---------- reprodutor de jogo (o "vídeo") ---------- */
  function playerJogo(area, j) {
    // Mostra só os momentos narrados: avança rápido pelo mapa até o próximo lance e narra, sem trechos parados.
    const rot = roteiroJogo(j);
    const marcas = j.ev.map((e, i) => ({ s: e.s, e, p: posEvento(e, j, i + 1) }));
    const cor = (e) => (e?.lado === "red" ? "#f0675c" : e?.lado === "blue" ? "#4ea3f0" : "#d9b46a");
    area.innerHTML = `<div class="player"><div class="tela"><canvas class="mapa" width="720" height="720" aria-label="Mapa com os lances do jogo"></canvas>
    <div class="lado-d"><div class="hud"><div class="t">${img(logo(j.az), "", j.az)}${esc(j.az)}</div><div class="clock" data-clock>0:00</div><div class="t dir">${esc(j.vm)}${img(logo(j.vm), "", j.vm)}</div></div>
      <div style="display:grid;gap:4px"><div class="linha-hud"><span>Abates <b data-k="blue">0</b> · Torres <b data-t="blue">0</b></span><span class="dir">Torres <b data-t="red">0</b> · Abates <b data-k="red">0</b></span></div>
      <div class="linha-hud"><span>Ouro <b data-g="blue">2,5k</b></span><span class="dir">Ouro <b data-g="red">2,5k</b></span></div>
      <div class="linha-hud"><div class="drags" data-d="blue"></div><div class="drags dir" data-d="red"></div></div></div>
      <div data-graf></div>
      <div class="legenda" data-leg aria-live="polite"><small>Lance 1 de ${rot.length}</small>${esc(rot[0].txt)}</div></div></div>
    <div class="controles"><button data-ant aria-label="Lance anterior">⏮</button><button data-play aria-label="Tocar ou pausar">▶ Play</button><button data-prox aria-label="Próximo lance">⏭</button>
      <div class="trilha" data-trilha><div class="base"></div><div class="feito" data-feito></div>${rot.map((r, i) => `<i class="mk" data-i="${i}" title="${mmss(r.s)}" style="left:calc(${(r.s / j.duracao) * 100}% - 1px);background:${cor(r.ev)}"></i>`).join("")}</div>
      <button data-voz aria-pressed="${vozLigada}" aria-label="Narração por voz">Voz</button><span data-lugar-voz>${seletorVoz()}</span></div>
    <div class="controles" style="border:0;padding-top:0"><div class="lista-ev" data-lista>${rot.map((r, i) => `<button class="momento" data-i="${i}"><span class="num">${mmss(r.s)}</span> ${esc(r.txt)}</button>`).join("")}</div></div></div>`;
    const cv = area.querySelector("canvas"),
      q = (s) => area.querySelector(s);
    ligarSeletorVoz(area);
    let t = 0,
      i = 0,
      tocando = false,
      token = 0,
      ultGraf = -99,
      terminou = false;
    const em = (s) => {
      let a = j.serie[0];
      for (const x of j.serie) {
        if (x[0] <= s) a = x;
        else break;
      }
      return a;
    };
    function hud() {
      q("[data-clock]").textContent = mmss(t);
      const ev = j.ev.filter((e) => e.s <= t);
      for (const l of ["blue", "red"]) {
        q(`[data-k="${l}"]`).textContent = ev
          .filter((e) => e.tipo === "abate" && e.lado === l)
          .reduce((s, e) => s + e.n, 0);
        q(`[data-t="${l}"]`).textContent = ev.filter((e) => e.tipo === "torre" && e.lado === l).length;
        q(`[data-d="${l}"]`).innerHTML =
          ev
            .filter((e) => e.tipo === "dragao" && e.lado === l)
            .map(
              (e) =>
                `<i title="${DRAG[e.dragao]?.[0] || e.dragao}" style="background:${DRAG[e.dragao]?.[1] || "#888"}"></i>`,
            )
            .join("") +
          ev
            .filter((e) => e.tipo === "barao" && e.lado === l)
            .map(() => `<i title="Barão" style="background:#a77ce8;border-radius:50%"></i>`)
            .join("");
      }
      const x = em(t);
      q('[data-g="blue"]').textContent = (x[1] / 1000).toFixed(1).replace(".", ",") + "k";
      q('[data-g="red"]').textContent = (x[2] / 1000).toFixed(1).replace(".", ",") + "k";
      q("[data-feito]").style.width = (t / j.duracao) * 100 + "%";
      if (Math.abs(t - ultGraf) >= 15) {
        q("[data-graf]").innerHTML = graficoOuro(j, t, true);
        ultGraf = t;
      }
      desenharMapa(cv, j, t, marcas);
    }
    function mostrar(k) {
      const r = rot[k];
      q("[data-leg]").innerHTML =
        `<small>${mmss(r.s)} · lance ${k + 1} de ${rot.length}${linkVod(j, r.s) ? ` · <a href="${linkVod(j, r.s)}" target="_blank" rel="noopener" title="O momento no vídeo é aproximado">ver na transmissão</a>` : ""}</small>${esc(r.txt)}`;
      area.querySelectorAll(".momento").forEach((b) => b.classList.toggle("atual", +b.dataset.i === k));
      const b = area.querySelector(`.momento[data-i="${k}"]`);
      if (b) {
        const l = q("[data-lista]");
        l.scrollTop = b.offsetTop - l.offsetTop - 30;
      }
    }
    const espera = (ms) => new Promise((r) => setTimeout(r, ms));
    function avancar(alvo, ms, meu) {
      return new Promise((res) => {
        const t0 = t;
        if (PARADO || ms <= 0 || alvo <= t0) {
          t = alvo;
          hud();
          res();
          return;
        }
        const ini = performance.now();
        q("[data-clock]").classList.add("rapido");
        const f = (now) => {
          if (meu !== token) {
            res();
            return;
          }
          const p = Math.min(1, (now - ini) / ms);
          t = t0 + (alvo - t0) * (1 - Math.pow(1 - p, 2));
          hud();
          if (p < 1) requestAnimationFrame(f);
          else {
            q("[data-clock]").classList.remove("rapido");
            res();
          }
        };
        requestAnimationFrame(f);
      });
    }
    function botao() {
      q("[data-play]").textContent = tocando ? "❚❚ Pausar" : terminou ? "↺ Rever" : "▶ Play";
    }
    async function tocar(k) {
      const meu = ++token;
      tocando = true;
      terminou = false;
      botao();
      try {
        speechSynthesis.cancel();
      } catch (_) {}
      for (i = k; i < rot.length; i++) {
        const r = rot[i];
        await avancar(r.s, Math.min(1100, Math.max(300, (r.s - t) * 4)), meu);
        if (meu !== token) return;
        mostrar(i);
        {
          const f = vozLigada && falaGravada(j, i, r.txt);
          if (!(f && (await tocarGravada(j, f, 1)))) await falar(r.txt, 1, r.hype);
        }
        if (meu !== token) return;
      }
      i = rot.length - 1;
      tocando = false;
      terminou = true;
      botao();
    }
    function pausar() {
      token++;
      tocando = false;
      try {
        speechSynthesis.cancel();
      } catch (_) {}
      pararGravadas();
      botao();
    }
    function irPara(k) {
      k = Math.max(0, Math.min(rot.length - 1, k));
      token++;
      if (t > rot[k].s) t = Math.max(0, rot[k].s - 20);
      ultGraf = -99;
      tocar(k);
    }
    q("[data-play]").onclick = () => {
      if (tocando) pausar();
      else if (terminou) {
        t = 0;
        ultGraf = -99;
        tocar(0);
      } else tocar(i);
    };
    q("[data-ant]").onclick = () => irPara(i - 1);
    q("[data-prox]").onclick = () => irPara(i + 1);
    q("[data-trilha]").onclick = (e) => {
      const mk = e.target.closest("[data-i]");
      let k;
      if (mk) k = +mk.dataset.i;
      else {
        const b = e.currentTarget.getBoundingClientRect();
        const s = ((e.clientX - b.left) / b.width) * j.duracao;
        k = rot.findIndex((r) => r.s >= s);
        if (k < 0) k = rot.length - 1;
      }
      irPara(k);
    };
    q("[data-lista]").onclick = (e) => {
      const b = e.target.closest("[data-i]");
      if (!b) return;
      irPara(+b.dataset.i);
    };
    q("[data-voz]").onclick = (e) => {
      vozLigada = !vozLigada;
      e.currentTarget.setAttribute("aria-pressed", vozLigada);
      if (!vozLigada)
        try {
          speechSynthesis.cancel();
        } catch (_) {}
    };
    hud();
    j.jog.forEach((x) => {
      const im_ = im(camp(x.campeao).icone);
      if (im_ && !im_.complete)
        im_.addEventListener("load", () => {
          if (!tocando) desenharMapa(cv, j, t, marcas);
        });
    });
    return () => {
      token++;
      tocando = false;
      try {
        speechSynthesis.cancel();
      } catch (_) {}
    };
  }
  function ligarJogo(j) {
    const b = $("#ver-video");
    if (!b) return;
    b.onclick = () => {
      b.hidden = true;
      pararPlayer = playerJogo($("#area-video"), j);
      $("#area-video [data-play]").click();
    };
  }

  /* ---------- prévia de confronto futuro ---------- */
  function curiosConfronto(a, b) {
    const k = [a, b].sort().join("|");
    return (W.curiosidades?.confrontos || []).find((c) => c.times.join("|") === k);
  }
  const titulares = (c) => (TIMES[c]?.jogadores || []).filter((p) => p.titular);
  const tagC = (c) =>
    c === "inferido"
      ? '<span class="conf-tag">ao que tudo indica</span>'
      : c === "fonte_unica"
        ? '<span class="conf-tag">fonte única</span>'
        : "";
  function topCamps(s, n = 8) {
    return s
      ? Object.entries(s.camps)
          .sort((a, b) => b[1] - a[1])
          .slice(0, n)
          .map(
            ([k, v]) =>
              `<span class="c">${img(camp(k).icone, "", camp(k).nome)}${esc(camp(k).nome)} <span class="muted num">${v}</span></span>`,
          )
          .join("")
      : '<span class="muted">Ainda sem jogos neste Worlds.</span>';
  }
  function previa(p) {
    const [A, B] = p.times.map((t) => t.codigo);
    if (A === "TBD" || B === "TBD")
      return `<div class="bloco-f"><h3>Confronto a definir</h3><p style="margin-top:0">${p.fase === "swiss" ? "Os times deste jogo saem do sorteio feito ao fim da rodada anterior, entre times com a mesma campanha." : "Os times deste jogo saem dos resultados da fase anterior."} Quando o confronto for definido, esta página mostra a prévia completa.</p>
    <div class="eyebrow">Começa em</div><div class="relogio" data-contagem="${p.inicio}"></div><p class="muted" style="margin-bottom:0">${fmt(p.inicio, { weekday: "long", day: "numeric", month: "long" })}, ${hora(p.inicio)} (Brasília) · melhor de ${p.melhorDe}</p></div>`;
    const sa = statsTime(A),
      sb = statsTime(B),
      cur = curiosConfronto(A, B);
    const camp_ = (c) => {
      const l = campanha(c);
      return l.length
        ? `<div class="campanha">${l.map((x) => `<div class="r"><span class="res ${x.venceu ? "v" : "d"}">${x.venceu ? "V" : "D"}</span><button class="link" data-partida="${x.p.id}">${x.venceu ? "Venceu" : "Perdeu para"} ${esc(nomeT(x.adv))} · ${rotuloFase(x.p, true)}</button><span class="num">${x.placar}</span></div>`).join("")}</div>`
        : `<p class="muted" style="margin:0">Estreia neste jogo.</p>`;
    };
    const cmpL =
      sa || sb
        ? [
            ["Vitórias", "wr", pct],
            ["First blood", "pfb", pct],
            ["Primeiro dragão", "pfd", pct],
            ["Primeira torre", "pft", pct],
            ["Dragões por jogo", "dragJ", n1],
            ["Barões por jogo", "barJ", n1],
            ["Abates por jogo", "abJ", n1],
            ["Vantagem aos 15", "gd15m", mil],
            ["Duração média", "durM", mmss],
          ]
            .map(([n, k, f]) => {
              const va = sa?.[k],
                vb = sb?.[k];
              const pos = (v) => (v == null || !sa || !sb ? 0 : k === "gd15m" ? Math.max(0, v + 4000) : v);
              return linhaCmp(sa ? f(va) : "–", sb ? f(vb) : "–", pos(va), pos(vb), n);
            })
            .join("")
        : "";
    const duelos = ROTAS.map((r) => {
      const pa = titulares(A).find((x) => x.rota === r),
        pb = titulares(B).find((x) => x.rota === r);
      const lado = (pl, dir) => {
        if (!pl) return `<div class="p ${dir ? "dir" : ""}"><span class="sem-foto">?</span></div>`;
        const st = statsJogador(pl.id);
        return `<div class="p ${dir ? "dir" : ""}" data-jogador="${pl.id}" style="cursor:pointer">${pl.foto ? `<img class="f" src="${pl.foto}" alt="${esc(pl.nick)}">` : `<span class="sem-foto">${esc(pl.nick[0])}</span>`}<div style="min-width:0"><b>${esc(pl.nick)}</b><div class="ns">${st ? `KDA ${n1(st.kda)} · ${n1(st.csm)} CS/min<br>Ouro@15 ${sinal(st.gd15)} · dano ${pct(st.dano)}` : "sem jogos neste Worlds"}</div></div></div>`;
      };
      return `<div class="duelo">${lado(pa)}<div class="rota">${ROTA_PT[r]}</div>${lado(pb, true)}</div>`;
    }).join("");
    const cA = W.curiosidades?.times?.[A],
      cB = W.curiosidades?.times?.[B];
    const fatos = [
      ...(cur?.curiosidades || []),
      ...(cA?.curiosidades || []).slice(0, 2),
      ...(cB?.curiosidades || []).slice(0, 2),
    ];
    return `<div class="bloco-f" style="display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap"><div><div class="eyebrow">Começa em</div><div class="relogio" data-contagem="${p.inicio}"></div></div><div style="text-align:right"><b>${fmt(p.inicio, { weekday: "long", day: "numeric", month: "long" })}</b><br><span class="relogio" style="font-size:24px">${hora(p.inicio)}</span> <span class="muted">Brasília</span></div></div>
  <p style="margin:-4px 0 12px;font-size:13px"><a href="${linkAgenda(p)}" target="_blank" rel="noopener">Adicionar ao Google Agenda</a></p>
  <button class="botao-video" id="ver-previa"><span class="play"></span><span><b>Assistir à prévia narrada</b><span>${!sa && !sb ? "Elencos, histórico e curiosidades do confronto" : "Como cada time chega, duelo de destaque e curiosidades"}</span></span></button>
  <div id="area-video"></div>
  ${cur?.manchete ? `<div class="bloco-f"><h3>${esc(cur.manchete)}</h3><p style="margin:0">${esc(cur.resumo_historico || "")}</p></div>` : ""}
  <div class="dois"><div class="bloco-f"><h3>Campanha · ${esc(A)}</h3>${camp_(A)}</div><div class="bloco-f"><h3>Campanha · ${esc(B)}</h3>${camp_(B)}</div></div>
  <div class="bloco-f"><h3>Duelo por posição <small>números só deste Worlds · clique num jogador</small></h3><div class="duelos">${duelos}</div></div>
  ${cmpL ? `<div class="bloco-f"><h3>Comparativo dos times <small>${sa ? sa.jogos : 0} × ${sb ? sb.jogos : 0} jogos neste Worlds</small></h3><div class="cmp">${linhaCab(A, B)}${cmpL}</div></div>` : `<div class="bloco-f"><h3>Comparativo dos times</h3><p class="muted" style="margin:0">Nenhum dos dois jogou ainda neste Worlds. O comparativo aparece depois da primeira partida de cada um.</p></div>`}
  ${
    p.melhorDe > 1
      ? `<div class="bloco-f"><h3>Fearless Draft</h3><p style="margin:0">Em séries melhor de ${p.melhorDe}, cada campeão escolhido num jogo fica fora dos jogos seguintes para os dois times. Os campeões que os dois times já usaram neste Worlds são os mais prováveis de sumir cedo da série.</p>${
          disputados(sa, sb).length
            ? `<div class="camps" style="margin-top:10px">${disputados(sa, sb)
                .map(
                  (k) =>
                    `<span class="c">${img(camp(k).icone, "", camp(k).nome)}${esc(camp(k).nome)} <span class="muted num">${sa.camps[k]}+${sb.camps[k]}</span></span>`,
                )
                .join("")}</div>`
            : ""
        }</div>`
      : ""
  }
  <div class="dois"><div class="bloco-f"><h3>Campeões · ${esc(A)}</h3><div class="camps">${topCamps(sa)}</div></div><div class="bloco-f"><h3>Campeões · ${esc(B)}</h3><div class="camps">${topCamps(sb)}</div></div></div>
  ${sa?.jogosLp || sb?.jogosLp ? `<div class="dois"><div class="bloco-f"><h3>Bans · ${esc(A)}</h3>${blocoBans(A, sa)}</div><div class="bloco-f"><h3>Bans · ${esc(B)}</h3>${blocoBans(B, sb)}</div></div>` : ""}
  ${fatos.length ? `<div class="bloco-f"><h3>Curiosidades <small>histórico de fora deste Worlds</small></h3><ul class="curios">${fatos.map((f) => `<li>${esc(f.texto)}${tagC(f.confianca)}</li>`).join("")}</ul></div>` : ""}
  <div class="bloco-f"><h3>Seu palpite</h3><div class="palpite" id="palpite"></div></div>`;
  }
  function ligarPrevia(p) {
    contagens();
    const b = $("#ver-previa");
    if (b)
      b.onclick = () => {
        b.hidden = true;
        pararPlayer = playerPrevia($("#area-video"), p);
      };
    const pal = $("#palpite");
    if (pal) montarPalpite(pal, p);
  }
  function roteiroPrevia(p) {
    const [A, B] = p.times.map((t) => t.codigo);
    const sa = statsTime(A),
      sb = statsTime(B),
      cur = curiosConfronto(A, B);
    const S = [];
    S.push({
      tipo: "abre",
      txt: `Chegou a hora! ${nomeT(A)} contra ${nomeT(B)}, ${rotuloFase(p).toLowerCase()}, ${fmt(p.inicio, { weekday: "long" })} às ${horaFalada(p.inicio)}, horário de Brasília. ${p.melhorDe === 1 ? "Jogo único, sem margem pra erro!" : `Melhor de ${p.melhorDe}!`}`,
    });
    const cp = (c) => {
      const l = campanha(c);
      if (!l.length) return `${nomeT(c)} estreia neste jogo.`;
      const v = l.filter((x) => x.venceu).length,
        d = l.length - v;
      return `${nomeT(c)} chega com ${v} ${v === 1 ? "série vencida" : "séries vencidas"} e ${d} ${d === 1 ? "perdida" : "perdidas"} neste Worlds.`;
    };
    S.push({ tipo: "campanha", txt: cp(A) + " " + cp(B) });
    if (sa || sb) {
      const fr = [];
      for (const [n, k] of [
        ["o first blood", "pfb"],
        ["o primeiro dragão", "pfd"],
        ["a primeira torre", "pft"],
      ]) {
        const t = [
          [A, sa],
          [B, sb],
        ]
          .filter((x) => x[1])
          .sort((x, y) => y[1][k] - x[1][k])[0];
        if (t && t[1][k] >= 0.6) fr.push(`${nomeT(t[0])} pegou ${n} em ${pct(t[1][k])} dos jogos`);
      }
      S.push({
        tipo: "barras",
        txt: fr.length ? fr.join(". ") + "." : "Nos números do torneio, os dois times chegam equilibrados.",
        linhas: [
          ["Vitórias", "wr"],
          ["First blood", "pfb"],
          ["Primeiro dragão", "pfd"],
          ["Primeira torre", "pft"],
          ["Dragões/jogo", "dragJ"],
          ["Barões/jogo", "barJ"],
        ],
      });
      const cand = [A, B]
        .flatMap((c) => titulares(c).map((pl) => ({ pl, c, st: statsJogador(pl.id) })))
        .filter((x) => x.st);
      const g = cand.filter((x) => x.st.gd15 != null).sort((a, b) => b.st.gd15 - a.st.gd15)[0];
      const k = cand.slice().sort((a, b) => b.st.kda - a.st.kda)[0];
      if (g && g.st.gd15 > 300)
        S.push({
          tipo: "jogador",
          x: g,
          txt: `De olho em ${g.pl.nick}, ${ROTA_PT[g.pl.rota].toLowerCase()} do ${nomeT(g.c)}. Aos 15 minutos ele tem, em média, ${Math.round(g.st.gd15)} de ouro a mais que o rival de rota: um começo de jogo agressivo.`,
        });
      if (k && k !== g)
        S.push({
          tipo: "jogador",
          x: k,
          txt: `${k.pl.nick}, do ${nomeT(k.c)}, tem o melhor KDA do confronto neste Worlds: ${n1(k.st.kda)}, com ${k.st.k} abates e ${k.st.d} mortes em ${k.st.jogos} jogos.`,
        });
      const cs = [
        [A, sa],
        [B, sb],
      ]
        .filter((x) => x[1])
        .map(([c, s]) => {
          const t = Object.entries(s.camps).sort((a, b) => b[1] - a[1])[0];
          return t && t[1] > 1 ? `${nomeT(c)} já jogou de ${camp(t[0]).nome} ${t[1]} vezes` : "";
        })
        .filter(Boolean);
      if (cs.length && p.melhorDe > 1)
        S.push({
          tipo: "camps",
          txt: `De olho no draft: ${cs.join(" e ")}. Com o Fearless, campeão usado num jogo some da série para os dois times.`,
        });
    } else
      S.push({
        tipo: "texto",
        tit: "Sem jogos ainda",
        txt: `Nenhum dos dois entrou em campo neste Worlds, então ainda não há números do torneio. Vamos aos elencos.`,
      });
    S.push({
      tipo: "elencos",
      txt: `${nomeT(A)} vem com ${titulares(A)
        .map((x) => x.nick)
        .join(", ")}. ${nomeT(B)} com ${titulares(B)
        .map((x) => x.nick)
        .join(", ")}.`,
    });
    if (cur?.resumo_historico)
      S.push({ tipo: "texto", tit: cur.manchete || "Histórico", txt: cur.resumo_historico });
    (cur?.curiosidades || [])
      .filter((f) => f.confianca === "confirmado")
      .slice(0, 3)
      .forEach((f) => S.push({ tipo: "texto", tit: "Curiosidade", txt: f.texto }));
    S.push({ tipo: "fim", txt: `E você, quem leva? Deixe seu palpite logo abaixo.` });
    return S;
  }
  function playerPrevia(area, p) {
    const [A, B] = p.times.map((t) => t.codigo);
    const sa = statsTime(A),
      sb = statsTime(B);
    const S = roteiroPrevia(p);
    let i = 0,
      ativo = true,
      pausado = false,
      token = 0;
    area.innerHTML = `<div class="player"><div data-slide></div><div class="controles"><button data-play aria-label="Tocar ou pausar">❚❚ Pausar</button><div class="trilha" style="cursor:default"><div class="base"></div><div class="feito" data-feito></div></div><button data-voz aria-pressed="${vozLigada}" aria-label="Narração por voz">Voz</button><span data-lugar-voz>${seletorVoz()}</span><button data-prox>Próximo ›</button></div></div>`;
    ligarSeletorVoz(area);
    const q = (s) => area.querySelector(s);
    const lg = (c, cls = "lg") => img(logo(c), cls, c);
    const vds = (c) =>
      campanha(c)
        .map(
          (x) =>
            `<span class="res ${x.venceu ? "v" : "d"}" style="margin:2px">${x.venceu ? "V" : "D"}</span>`,
        )
        .join("") || '<span style="color:var(--pmut)">estreia</span>';
    function render(s) {
      let h = "";
      if (s.tipo === "abre")
        h = `<div class="lado-a-lado fade">${lg(A)}<div class="grande">×</div>${lg(B)}</div><h4 class="fade" style="text-align:center">${esc(nomeT(A))} × ${esc(nomeT(B))}</h4><p class="fade" style="text-align:center;color:var(--pmut);margin:0">${dataHora(p.inicio)} · Brasília · melhor de ${p.melhorDe}</p>`;
      else if (s.tipo === "campanha")
        h = `<h4 class="fade">Como chegam</h4><div class="lado-a-lado fade"><div style="text-align:center">${lg(A)}<div style="margin-top:8px">${vds(A)}</div></div><span></span><div style="text-align:center">${lg(B)}<div style="margin-top:8px">${vds(B)}</div></div></div>`;
      else if (s.tipo === "barras")
        h = `<h4 class="fade">Números do torneio</h4><div style="display:flex;justify-content:space-between;font-family:var(--display);font-weight:700;font-size:20px"><span style="color:var(--blue)">${esc(A)}</span><span style="color:var(--red)">${esc(B)}</span></div><div class="barras">${s.linhas
          .map(([n, k]) => {
            const va = sa?.[k] ?? 0,
              vb = sb?.[k] ?? 0,
              m = k.endsWith("J") ? Math.max(va, vb, 0.01) : 1;
            const f = k.endsWith("J") ? n1 : pct;
            return `<div style="display:grid;gap:4px"><span style="text-align:right">${sa ? f(va) : "–"}</span><div class="bar esq"><i data-w="${(va / m) * 100}" style="background:var(--blue)"></i></div></div><span class="rot">${n}</span><div style="display:grid;gap:4px"><span>${sb ? f(vb) : "–"}</span><div class="bar"><i data-w="${(vb / m) * 100}" style="background:var(--red)"></i></div></div>`;
          })
          .join("")}</div>`;
      else if (s.tipo === "jogador") {
        const x = s.x;
        h = `<div class="fade" style="display:flex;gap:18px;align-items:center;flex-wrap:wrap">${x.pl.foto ? `<img class="fp" src="${x.pl.foto}" alt="">` : ""}<div><div class="eyebrow">${esc(nomeT(x.c))} · ${ROTA_PT[x.pl.rota]}</div><h4>${esc(x.pl.nick)}</h4><div class="num" style="color:var(--pmut);margin-top:6px">KDA ${n1(x.st.kda)} · Ouro@15 ${sinal(x.st.gd15)} · ${n1(x.st.csm)} CS/min · dano ${pct(x.st.dano)}</div></div></div>`;
      } else if (s.tipo === "camps")
        h = `<h4 class="fade">Campeões mais usados</h4>${[
          [A, sa],
          [B, sb],
        ]
          .filter((x) => x[1])
          .map(
            ([c, st]) =>
              `<div class="fade" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">${img(logo(c), "", c, "width:34px;height:34px;object-fit:contain")}${Object.entries(
                st.camps,
              )
                .sort((a, b) => b[1] - a[1])
                .slice(0, 6)
                .map(
                  ([k, v]) =>
                    `<span style="display:inline-flex;align-items:center;gap:4px;font-size:13px">${img(camp(k).icone, "", camp(k).nome, "width:40px;height:40px;border-radius:6px")}×${v}</span>`,
                )
                .join("")}</div>`,
          )
          .join("")}`;
      else if (s.tipo === "elencos")
        h = `<h4 class="fade">Os titulares</h4>${[A, B]
          .map(
            (c) =>
              `<div class="fade" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">${img(logo(c), "", c, "width:34px;height:34px;object-fit:contain")}${titulares(
                c,
              )
                .map(
                  (pl) =>
                    `<div style="text-align:center;width:70px">${pl.foto ? `<img src="${pl.foto}" style="width:56px;height:56px;border-radius:50%;object-fit:cover;background:#1b2b3d" alt="">` : `<div style="width:56px;height:56px;border-radius:50%;background:#1b2b3d;margin:auto"></div>`}<div style="font-size:12px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(pl.nick)}</div></div>`,
                )
                .join("")}</div>`,
          )
          .join("")}`;
      else if (s.tipo === "fim")
        h = `<div class="lado-a-lado fade">${lg(A)}<div class="grande">Quem<br>leva?</div>${lg(B)}</div>`;
      else
        h = `<div class="eyebrow fade">${esc(s.tit || "")}</div><p class="fade" style="font-size:clamp(19px,2.6vw,26px);line-height:1.35;margin:0;max-width:42ch">${esc(s.txt)}</p>`;
      q("[data-slide]").innerHTML =
        `<div class="slide">${h}${s.tipo === "texto" ? "" : `<div class="rodape">${esc(s.txt)}</div>`}</div>`;
      requestAnimationFrame(() =>
        requestAnimationFrame(() =>
          q("[data-slide]")
            .querySelectorAll("[data-w]")
            .forEach((el) => (el.style.width = el.dataset.w + "%")),
        ),
      );
      q("[data-feito]").style.width = ((i + 1) / S.length) * 100 + "%";
    }
    async function rodar() {
      const meu = ++token;
      while (ativo && !pausado && i < S.length && meu === token) {
        render(S[i]);
        await falar(S[i].txt, 1);
        await new Promise((r) => setTimeout(r, 250));
        if (meu !== token || pausado || !ativo) return;
        if (i === S.length - 1) break;
        i++;
      }
      if (meu === token && i === S.length - 1 && !pausado) {
        pausado = true;
        q("[data-play]").textContent = "↺ Rever";
      }
    }
    q("[data-play]").onclick = () => {
      const rever = q("[data-play]").textContent.includes("Rever");
      if (rever) i = 0;
      pausado = !pausado && !rever;
      q("[data-play]").textContent = pausado ? "▶ Continuar" : "❚❚ Pausar";
      if (pausado) {
        token++;
        try {
          speechSynthesis.cancel();
        } catch (_) {}
      } else rodar();
    };
    q("[data-prox]").onclick = () => {
      try {
        speechSynthesis.cancel();
      } catch (_) {}
      i = Math.min(S.length - 1, i + 1);
      pausado = false;
      q("[data-play]").textContent = "❚❚ Pausar";
      rodar();
    };
    q("[data-voz]").onclick = (e) => {
      vozLigada = !vozLigada;
      e.currentTarget.setAttribute("aria-pressed", vozLigada);
      if (!vozLigada)
        try {
          speechSynthesis.cancel();
        } catch (_) {}
    };
    rodar();
    return () => {
      ativo = false;
      token++;
      try {
        speechSynthesis.cancel();
      } catch (_) {}
    };
  }

  /* ---------- palpites: salvos no navegador (localStorage) ---------- */
  let DB = null,
    MEU_ID = null,
    TODOS = {};
  const ouvintes = new Set();
  function meuLocal() {
    try {
      return JSON.parse(localStorage.getItem("palpites") || "{}");
    } catch (_) {
      return {};
    }
  }
  function salvarLocal(o) {
    try {
      localStorage.setItem("palpites", JSON.stringify(o));
    } catch (_) {}
  }
  function montarPalpite(el, p) {
    const [A, B] = p.times.map((t) => t.codigo);
    const vence = Math.ceil(p.melhorDe / 2);
    const placares = p.melhorDe === 1 ? [] : Array.from({ length: vence }, (_, k) => `${vence}-${k}`);
    const meus = () => (DB && MEU_ID ? TODOS[MEU_ID] || meuLocal() : meuLocal());
    const desenha = () => {
      const meu = meus()[p.id] || {};
      const votos = (DB ? Object.values(TODOS) : [meuLocal()]).map((x) => x[p.id]).filter(Boolean);
      const va = votos.filter((v) => v.time === A).length,
        vb = votos.filter((v) => v.time === B).length,
        tot = va + vb;
      el.innerHTML = `<div class="opcoes">${[A, B].map((c) => `<button data-voto="${c}" aria-pressed="${meu.time === c}">${img(logo(c), "", c)}${esc(nomeT(c))}</button>`).join("")}</div>
      ${placares.length && meu.time ? `<div class="opcoes">${placares.map((s) => `<button data-placar="${s}" aria-pressed="${meu.placar === s}">${esc(meu.time)} ${s}</button>`).join("")}</div>` : ""}
      ${tot ? `<div class="votos"><i style="width:${(va / tot) * 100}%;background:var(--blue)"></i><i style="width:${(vb / tot) * 100}%;background:var(--red)"></i></div><div class="muted num" style="font-size:12.5px;display:flex;justify-content:space-between;gap:8px"><span>${esc(A)} ${pct(va / tot)}</span><span>${tot} ${tot === 1 ? "palpite" : "palpites"}${DB ? "" : " neste navegador"}</span><span>${esc(B)} ${pct(vb / tot)}</span></div>` : `<div class="muted" style="font-size:13px">Ninguém palpitou ainda. Escolha quem vence${placares.length ? " e o placar" : ""}.</div>`}`;
      el.querySelectorAll("[data-voto]").forEach(
        (b) => (b.onclick = () => gravar({ time: b.dataset.voto, placar: null })),
      );
      el.querySelectorAll("[data-placar]").forEach(
        (b) => (b.onclick = () => gravar({ ...meu, placar: b.dataset.placar })),
      );
    };
    async function gravar(v) {
      const novo = { ...meus(), [p.id]: v };
      salvarLocal(novo);
      if (DB && MEU_ID) {
        TODOS[MEU_ID] = novo;
        try {
          await DB.collection("palpites").doc(MEU_ID).set({ picks: novo, em: new Date().toISOString() });
        } catch (_) {}
      }
      desenha();
    }
    ouvintes.clear();
    ouvintes.add(desenha);
    desenha();
  }

  /* ---------- ranking dos palpites ---------- */
  function pontosPalpites(picks) {
    let pts = 0,
      acertos = 0,
      exatos = 0,
      n = 0;
    for (const [pid, v] of Object.entries(picks || {})) {
      const p = PID[pid];
      if (!p || p.estado !== "completed" || !v?.time) continue;
      n++;
      const w = p.times.find((t) => t.resultado === "win");
      if (!w || w.codigo !== v.time) continue;
      acertos++;
      pts += 1;
      const l = p.times.find((t) => t !== w);
      if (v.placar && v.placar === `${w.vitorias}-${l.vitorias}`) {
        exatos++;
        pts += 1;
      }
    }
    return { pts, acertos, exatos, n };
  }
  async function rankingPalpites() {
    const el = $("#ranking-palpites");
    if (!el) return;
    if (!DB) {
      const r = pontosPalpites(meuLocal());
      el.innerHTML = r.n
        ? `<p style="margin:0">Você acertou <b>${r.acertos}</b> de ${r.n} palpites${r.exatos ? ` e cravou o placar ${r.exatos} ${r.exatos === 1 ? "vez" : "vezes"}` : ""}.</p><p class="muted" style="font-size:12.5px;margin:6px 0 0">Palpites guardados só neste navegador.</p>`
        : '<p class="muted" style="margin:0">Dê palpites nas prévias dos jogos e acompanhe aqui quantos você acertou.</p>';
      return;
    }
    const lst = Object.entries(TODOS)
      .map(([id, pk]) => ({ id, ...pontosPalpites(pk) }))
      .filter((x) => x.n)
      .sort((a, b) => b.pts - a.pts || b.exatos - a.exatos || a.n - b.n);
    if (!lst.length) {
      el.innerHTML =
        '<p class="muted" style="margin:0">O ranking aparece quando o primeiro jogo com palpites terminar. Cada vencedor certo vale 1 ponto, e o placar exato da série vale mais 1.</p>';
      return;
    }
    let ps = {};
    el.innerHTML = `<ol>${lst
      .slice(0, 20)
      .map(
        (x, i) =>
          `<li><button style="cursor:default"><span class="ord">${i + 1}</span><span class="sem-foto" style="width:34px;height:34px;font-size:14px" data-ini></span><span><b data-nome></b><small>${x.acertos} de ${x.n} vencedores${x.exatos ? ` · ${x.exatos} ${x.exatos === 1 ? "placar exato" : "placares exatos"}` : ""}</small></span><span class="val">${x.pts}</span></button></li>`,
      )
      .join(
        "",
      )}</ol><p class="muted" style="font-size:12px;margin:8px 0 0">Vencedor certo vale 1 ponto; placar exato da série, mais 1.</p>`;
    el.querySelectorAll("li").forEach((li, i) => {
      const x = lst[i],
        nome = ps[x.id]?.name || (x.id === MEU_ID ? "Você" : "Alguém");
      li.querySelector("[data-nome]").textContent =
        nome + (x.id === MEU_ID && nome !== "Você" ? " (você)" : "");
      li.querySelector("[data-ini]").textContent = nome[0] || "?";
    });
  }

  /* ---------- agenda ---------- */
  function linkAgenda(p) {
    const [a, b] = p.times;
    const ini = new Date(p.inicio),
      fim = new Date(+ini + (p.melhorDe === 1 ? 1 : p.melhorDe === 3 ? 3 : 5) * 3600e3);
    const z = (d) => d.toISOString().replace(/[-:]/g, "").replace(/\.\d+/, "");
    const tit = `Worlds 2026: ${a.codigo === "TBD" ? "a definir" : a.codigo} x ${b.codigo === "TBD" ? "a definir" : b.codigo}`;
    return (
      "https://calendar.google.com/calendar/render?action=TEMPLATE&text=" +
      encodeURIComponent(tit) +
      "&dates=" +
      z(ini) +
      "/" +
      z(fim) +
      "&details=" +
      encodeURIComponent(rotuloFase(p) + ", melhor de " + p.melhorDe + ". Transmissão em lolesports.com")
    );
  }
  function icsTime(c) {
    const z = (d) => new Date(d).toISOString().replace(/[-:]/g, "").replace(/\.\d+/, "");
    const ev = PARTIDAS.filter((p) => p.estado !== "completed" && p.times.some((t) => t.codigo === c)).map(
      (p) => {
        const [a, b] = p.times;
        return [
          "BEGIN:VEVENT",
          "UID:" + p.id + "@worlds2026",
          "DTSTAMP:" + z(Date.now()),
          "DTSTART:" + z(p.inicio),
          "DTEND:" + z(+new Date(p.inicio) + p.melhorDe * 3600e3),
          "SUMMARY:Worlds 2026: " + a.codigo + " x " + b.codigo,
          "DESCRIPTION:" + rotuloFase(p) + "\\, melhor de " + p.melhorDe,
          "END:VEVENT",
        ].join("\r\n");
      },
    );
    return [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//Central do Worlds 2026//PT-BR",
      "CALSCALE:GREGORIAN",
      ...ev,
      "END:VCALENDAR",
    ].join("\r\n");
  }
  function blocoAgenda(c) {
    const fut = PARTIDAS.filter((p) => p.estado !== "completed" && p.times.some((t) => t.codigo === c));
    if (!fut.length) return "";
    const solto = window.top === window;
    return `<div class="bloco-f"><h3>Na sua agenda <small>horário de Brasília</small></h3><div class="lista-linhas">${fut
      .map((p) => {
        const adv = p.times.find((t) => t.codigo !== c);
        return `<div class="r"><span class="tag">MD${p.melhorDe}</span><span>${dataHora(p.inicio)} · ${adv && adv.codigo !== "TBD" ? "contra " + esc(nomeT(adv.codigo)) : "adversário a definir"}</span><a href="${linkAgenda(p)}" target="_blank" rel="noopener">Google Agenda</a></div>`;
      })
      .join("")}</div>
  ${solto ? `<button class="link" style="margin-top:10px" data-ics="${c}">Baixar todos os jogos (.ics, para iPhone e Outlook)</button>` : ""}</div>`;
  }
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-ics]");
    if (!b) return;
    const c = b.dataset.ics;
    const url = URL.createObjectURL(new Blob([icsTime(c)], { type: "text/calendar" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `worlds-2026-${c.toLowerCase()}.ics`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  });

  /* ---------- time ---------- */
  function abrirTime(c) {
    const t = TIMES[c];
    if (!t) return;
    const s = statsTime(c);
    const cur = W.curiosidades?.times?.[c];
    const prox = PARTIDAS.find((p) => p.estado !== "completed" && p.times.some((x) => x.codigo === c));
    const elenco = t.jogadores
      .map((pl) => {
        const st = statsJogador(pl.id);
        return `<div class="duelo clic" data-jogador="${pl.id}" style="grid-template-columns:1fr auto"><div class="p">${pl.foto ? `<img class="f" src="${pl.foto}" alt="">` : `<span class="sem-foto">${esc(pl.nick[0])}</span>`}<div style="min-width:0"><b>${esc(pl.nick)}</b><div class="ns">${esc(pl.nome)}${pl.titular ? "" : " · reserva"}</div></div></div><div class="ns" style="text-align:right"><span class="rota" style="display:block">${ROTA_PT[pl.rota] || pl.rota}</span>${st ? `${st.k}/${st.d}/${st.a} · KDA ${n1(st.kda)}<br>${n1(st.csm)} CS/min · Ouro@15 ${sinal(st.gd15)}<br>dano ${pct(st.dano)} · KP ${pct(st.kp)}` : "sem jogos ainda"}</div></div>`;
      })
      .join("");
    abrirFolha(`<div class="placarao" style="grid-template-columns:auto 1fr"><div>${img(t.logo, "", c)}</div><div style="min-width:0"><div class="eyebrow">${esc(t.liga || "")}${cur?.seed ? " · " + esc(cur.seed) : ""}</div><h2>${esc(t.nome)}</h2>${cur?.como_classificou ? `<div class="muted">${esc(cur.como_classificou)}</div>` : ""}</div></div>
  ${prox ? `<div class="bloco-f"><h3>Próximo jogo <small>horário de Brasília</small></h3>${cartao(prox)}</div>` : ""}
  ${blocoAgenda(c)}
  <div class="bloco-f"><h3>Elenco <small>números só deste Worlds</small></h3><div class="duelos">${elenco}</div></div>
  ${
    s
      ? `<div class="bloco-f"><h3>No torneio <small>${s.jogos} ${s.jogos === 1 ? "jogo" : "jogos"} · ${s.v} ${s.v === 1 ? "vitória" : "vitórias"}</small></h3><div class="cmp">${[
          ["First blood", s.pfb],
          ["Primeiro dragão", s.pfd],
          ["Primeira torre", s.pft],
          ["Primeiro Barão", s.pfbar],
          ["Vitórias", s.wr],
        ]
          .map(
            ([n, v]) =>
              `<div class="l" style="grid-template-columns:130px 1fr 52px"><span class="rot" style="text-align:left">${n}</span><div class="barra"><i style="width:${v * 100}%;background:var(--gold)"></i></div><span class="v">${pct(v)}</span></div>`,
          )
          .join("")}</div>
    <p class="muted num" style="font-size:12.5px;margin:10px 0 0">${n1(s.abJ)} abates e ${n1(s.morJ)} mortes por jogo · ${n1(s.dragJ)} dragões · ${n1(s.barJ)} barões · duração média ${mmss(s.durM)} · vantagem aos 15 ${mil(s.gd15m)}</p></div>
  <div class="bloco-f"><h3>Campeões jogados</h3><div class="camps">${topCamps(s, 40)}</div></div>
  <div class="bloco-f"><h3>Bans</h3>${blocoBans(c, s)}</div>`
      : `<div class="bloco-f"><p class="muted" style="margin:0">${esc(t.nome)} ainda não jogou neste Worlds.</p></div>`
  }
  ${blocoHistTime(c)}
  <div class="bloco-f"><h3>Séries disputadas</h3><div style="display:grid;gap:8px">${
    campanha(c)
      .map((x) => cartao(x.p))
      .join("") || '<p class="muted" style="margin:0">Nenhuma ainda.</p>'
  }</div></div>
  ${cur?.curiosidades?.length ? `<div class="bloco-f"><h3>Curiosidades <small>histórico de fora deste Worlds</small></h3><ul class="curios">${cur.titulos_mundiais?.length ? `<li>Títulos mundiais: ${cur.titulos_mundiais.join(", ")}.</li>` : ""}${cur.curiosidades.map((f) => `<li>${esc(f.texto)}${tagC(f.confianca)}</li>`).join("")}</ul></div>` : ""}`);
    contagens();
    marcar("time-" + c);
  }

  /* ---------- jogador ---------- */
  /* ---------- jogador: história no torneio ---------- */
  const ordemJogo = (j) => (PID[j.partida]?.inicio || "") + String(j.numero).padStart(2, "0");
  function rivalDe(j, x) {
    return j.jog.find((y) => y.lado !== x.lado && y.rota === x.rota);
  }
  function fraseJogo(y) {
    const g = y.j,
      op = rivalDe(g, y),
      adv = nomeT(g.lados[outro(y.lado)]),
      c = camp(y.campeao).nome,
      k = kda(y);
    const partes = [];
    if (y.d === 0 && y.k + y.a >= 5) partes.push(`jogo perfeito de ${c}, sem morrer`);
    else if (k >= 6) partes.push(`atuação dominante de ${c}`);
    else if (k >= 3) partes.push(`bom jogo de ${c}`);
    else partes.push(`jogou de ${c}`);
    if (y.gd15 != null && op) {
      if (y.gd15 >= 1000) partes.push(`abriu ${mil(y.gd15)} de ouro sobre ${op.nick} aos 15`);
      else if (y.gd15 <= -1000)
        partes.push(`ficou ${mil(-y.gd15).replace("+", "")} atrás de ${op.nick} aos 15`);
    }
    if (y.kp != null && y.kp >= 0.75) partes.push(`esteve em ${pct(y.kp)} dos abates do time`);
    if (y.fbK) partes.push("fez o first blood");
    const t = partes.join(", ");
    return (
      t.charAt(0).toUpperCase() +
      t.slice(1) +
      (y.venceu
        ? `, e ${esc(g.lados[y.lado])} venceu ${esc(adv)}.`
        : `, mas ${esc(g.lados[y.lado])} perdeu para ${esc(adv)}.`)
    );
  }
  function pontosFortes(id, pl, st) {
    const pares = [
      ...new Set(JOGOS.flatMap((j) => j.jog.filter((x) => x.rota === pl.rota).map((x) => x.jogadorId))),
    ]
      .map((i) => statsJogador(i))
      .filter((s) => s && s.jogos >= 2);
    if (pares.length < 4 || st.jogos < 2) return [];
    const r = ROTA_PT[pl.rota] || "";
    const quem =
      { top: "topos", jungle: "caçadores", mid: "meios", bottom: "atiradores", support: "suportes" }[
        pl.rota
      ] || "jogadores da rota";
    const met = [
      ["KDA", (s) => s.kda],
      ["CS por minuto", (s) => s.csm, pl.rota === "support"],
      ["ouro aos 15", (s) => s.gd15],
      ["dano por minuto", (s) => s.dpm, pl.rota === "support"],
      ["participação em abates", (s) => s.kp],
      ["placar de visão", (s) => s.visao],
    ];
    const out = [];
    for (const [n, f, pula] of met) {
      if (pula) continue;
      const v = f(st);
      if (v == null) continue;
      const vs = pares
        .map(f)
        .filter((x) => x != null)
        .sort((a, b) => b - a);
      const pos = vs.indexOf(v) + 1;
      if (pos && pos <= 3)
        out.push({
          t: pos === 1 ? `Melhor ${n} entre os ${quem}` : `${pos}º em ${n} entre os ${quem}`,
          bom: true,
        });
      else if (pos && pos >= vs.length - 1 && vs.length >= 6)
        out.push({ t: `Entre os piores em ${n} da rota`, bom: false });
    }
    return out.slice(0, 4);
  }
  function resumoHumano(pl, st, time) {
    if (!st) return "";
    const L = st.linhas,
      mel = L.slice().sort((a, b) => kda(b) - kda(a) || b.k - a.k)[0];
    const fav = Object.entries(st.camps).sort((a, b) => b[1] - a[1])[0];
    const seq = [];
    for (const y of L) {
      if (seq.length && seq[seq.length - 1].v === y.venceu) seq[seq.length - 1].n++;
      else seq.push({ v: y.venceu, n: 1 });
    }
    const ult = seq[seq.length - 1];
    return `<p class="historia">${esc(pl.nick)} jogou <b>${st.jogos} ${st.jogos === 1 ? "jogo" : "jogos"}</b> por ${esc(nomeT(time))} neste Worlds e venceu <b>${st.v}</b>. ${fav && fav[1] > 1 ? `O campeão de confiança é <b>${esc(camp(fav[0]).nome)}</b>, escolhido ${fav[1]} vezes. ` : ""}O melhor jogo foi de ${esc(camp(mel.campeao).nome)} contra ${esc(nomeT(mel.j.lados[outro(mel.lado)]))}, com ${mel.k}/${mel.d}/${mel.a}.${ult.n >= 2 ? ` Chega ${ult.v ? `com ${ult.n} vitórias seguidas` : `de ${ult.n} derrotas seguidas`}.` : ""}</p>`;
  }
  function graficoForma(id, st) {
    const L = st.linhas;
    if (L.length < 2) return "";
    const W_ = 640,
      H = 120,
      pad = 8,
      bw = Math.min(46, (W_ - pad * 2) / L.length - 6);
    const mx = Math.max(4, ...L.map((y) => kda(y)));
    return `<div class="forma" role="group" aria-label="KDA jogo a jogo"><svg viewBox="0 0 ${W_} ${H + 22}" style="width:100%;height:auto;display:block">
    ${L.map((y, i) => {
      const v = kda(y),
        h = Math.max(3, (v / mx) * (H - 14)),
        x = pad + i * ((W_ - pad * 2) / L.length) + ((W_ - pad * 2) / L.length - bw) / 2;
      return `<g class="barra-forma" data-ir="${i}" tabindex="0" role="button" aria-label="Jogo ${i + 1}: ${esc(camp(y.campeao).nome)}, ${y.k}/${y.d}/${y.a}"><title>${esc(camp(y.campeao).nome)} contra ${esc(y.j.lados[outro(y.lado)])}: ${y.k}/${y.d}/${y.a}</title>
        <rect x="${x}" y="${H - h}" width="${bw}" height="${h}" rx="4" fill="${y.venceu ? "var(--good)" : "var(--red)"}" fill-opacity=".8"/>
        <text x="${x + bw / 2}" y="${H - h - 4}" font-size="10" text-anchor="middle" fill="var(--fg)" font-family="JetBrains Mono,monospace">${n1(v)}</text>
        <text x="${x + bw / 2}" y="${H + 14}" font-size="10" text-anchor="middle" fill="var(--muted)" font-family="JetBrains Mono,monospace">${esc(y.j.lados[outro(y.lado)])}</text></g>`;
    }).join("")}
  </svg><div class="muted" style="font-size:12px">KDA em cada jogo, na ordem em que aconteceram. Verde é vitória, vermelho é derrota. Toque numa barra para abrir o jogo na linha do tempo.</div></div>`;
  }
  function linhaTempo(id, st) {
    const series = [];
    for (const [i, y] of st.linhas.entries()) {
      const u = series[series.length - 1];
      if (u && u.pid === y.j.partida) u.itens.push([i, y]);
      else series.push({ pid: y.j.partida, itens: [[i, y]] });
    }
    return series
      .map((sr) => {
        const p = PID[sr.pid],
          y0 = sr.itens[0][1],
          eu = p.times.find((t) => t.codigo === y0.time),
          ele = p.times.find((t) => t.codigo !== y0.time);
        const fim = p.estado === "completed",
          ganhou = eu?.resultado === "win";
        return `<div class="serie-j"><div class="serie-cab">${fim ? `<span class="res ${ganhou ? "v" : "d"}">${ganhou ? "V" : "D"}</span>` : ""}${mini(ele?.codigo)} ${esc(y0.time)} ${eu?.vitorias ?? ""}×${ele?.vitorias ?? ""} ${esc(ele?.codigo || "")}<small>${rotuloFase(p)} · ${fmt(p.inicio, { day: "numeric", month: "long" })}</small></div>
    <ol class="jornada">${sr.itens.map(([i, y]) => itemJornada(i, y)).join("")}</ol></div>`;
      })
      .join("");
  }
  function itemJornada(i, y) {
    const g = y.j,
      adv = g.lados[outro(y.lado)],
      c = camp(y.campeao),
      op = rivalDe(g, y),
      m = g.duracao / 60,
      tor = g.tot[y.lado].torres,
      torC = g.tot[outro(y.lado)].torres;
    return `<li class="${y.venceu ? "v" : "d"}" data-passo="${i}"><button class="cab-j" aria-expanded="false">
      <span class="ponto"></span>
      <span class="quando-j">Jogo ${g.numero}<small>${mmss(g.duracao)}</small></span>
      ${img(c.icone, "ic", c.nome)}
      <span class="meio-j"><b>${y.venceu ? "Vitória" : "Derrota"} de ${esc(c.nome)}${op ? ` contra ${esc(op.nick)} (${esc(camp(op.campeao).nome)})` : ""}</b><small>${y.k}/${y.d}/${y.a} · ${n1(y.cs / m)} CS/min${y.gd15 != null ? ` · ${sinal(y.gd15)} aos 15` : ""} · torres ${tor}×${torC}</small></span>
      <span class="seta">›</span></button>
      <div class="corpo-j" hidden><p class="frase">${fraseJogo(y)}</p>
        <div class="tiles">${tile(`${y.k}/${y.d}/${y.a}`, "K/D/A")}${tile(n1(kda(y)), "KDA")}${tile(n1(y.cs / m), "CS/min")}${tile(pct(y.dano), "% do dano")}${tile(pct(y.kp), "Particip.")}${tile(`${tor}×${torC}`, "Torres")}</div>
        <h4 class="sub-h">O jogo dele, lance a lance <small>passe o mouse ou toque num momento para ver no gráfico de ouro contra ${op ? esc(op.nick) : "o rival"}</small></h4>
        ${blocoAcontecimentos(y)}
        <div class="itens" style="margin-top:10px">${(y.itens || [])
          .filter((k) => W.itens[k])
          .map(
            (k) =>
              `<img src="${W.itens[k].icone}" alt="${esc(W.itens[k].nome)}" title="${esc(W.itens[k].nome)}">`,
          )
          .join("")}</div>
        <button class="link" style="margin-top:8px" data-partida="${g.partida}" data-k="${jogosDe(g.partida).indexOf(g)}">Ver o jogo completo, com o replay narrado ›</button></div></li>`;
  }
  let JORN = [];
  function ligarJornada(raiz) {
    const abrir = (li, foco) => {
      const b = li.querySelector(".cab-j"),
        c = li.querySelector(".corpo-j"),
        aberto = !c.hidden;
      c.hidden = aberto;
      b.setAttribute("aria-expanded", !aberto);
      li.classList.toggle("aberto", !aberto);
      if (!aberto && !c.dataset.ligado) {
        c.dataset.ligado = 1;
        const y = JORN[+li.dataset.passo];
        if (y) ligarAcontecimentos(c, y);
      }
      if (!aberto && G) {
        G.fromTo(
          c,
          { height: 0, opacity: 0 },
          { height: "auto", opacity: 1, duration: 0.4, ease: "power2.out", clearProps: "height" },
        );
        animarEm(c);
      }
      if (foco) li.scrollIntoView({ behavior: PARADO ? "auto" : "smooth", block: "center" });
    };
    raiz.querySelectorAll(".jornada .cab-j").forEach((b) => (b.onclick = () => abrir(b.closest("li"))));
    raiz.querySelectorAll(".barra-forma").forEach((g) => {
      const ir = () => {
        const li = raiz.querySelector(`.jornada li[data-passo="${g.dataset.ir}"]`);
        if (li) {
          if (li.querySelector(".corpo-j").hidden) abrir(li, true);
          else li.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      };
      g.onclick = ir;
      g.onkeydown = (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          ir();
        }
      };
    });
  }
  function acontecimentos(y) {
    const g = y.j,
      eu = y.lado,
      op = rivalDe(g, y),
      nick = (pid) => g.jog[pid - 1]?.nick || "?",
      cp = (pid) => camp(g.jog[pid - 1]?.campeao).nome;
    const L = [];
    const meusTimes = g.lados[eu],
      deles = g.lados[outro(eu)];
    for (const e of g.ev) {
      if (e.tipo === "abate") {
        const v = e.vitimas || [],
          p = e.por || [];
        if (v.includes(y.pid))
          L.push({
            s: e.s,
            t: "morte",
            txt: `Morreu para ${esc(nick(p[0]))} (${esc(cp(p[0]))})${p.length > 1 ? ` com ajuda de ${p.length - 1}` : ""}`,
          });
        else if (p[0] === y.pid)
          L.push({
            s: e.s,
            t: "abate",
            txt: `Abateu ${v.map((x) => esc(nick(x))).join(", ")}${v.length >= 2 ? ` (${v.length === 2 ? "double kill" : v.length === 3 ? "triple kill" : v.length === 4 ? "quadra kill" : "pentakill"})` : ""}${op && v.includes(op.pid) ? ", o rival de rota" : ""}`,
          });
        else if (p.includes(y.pid))
          L.push({ s: e.s, t: "assist", txt: `Ajudou no abate de ${v.map((x) => esc(nick(x))).join(", ")}` });
      } else if (e.tipo === "torre")
        L.push({
          s: e.s,
          t: "obj",
          bom: e.lado === eu,
          txt:
            e.lado === eu
              ? `${esc(meusTimes)} derrubou uma torre`
              : `${esc(deles)} derrubou uma torre de ${esc(meusTimes)}`,
        });
      else if (e.tipo === "dragao")
        L.push({
          s: e.s,
          t: "obj",
          bom: e.lado === eu,
          txt: `${e.lado === eu ? esc(meusTimes) : esc(deles)} pegou o dragão ${DRAG[e.dragao]?.[0] || e.dragao}`,
        });
      else if (e.tipo === "barao")
        L.push({
          s: e.s,
          t: "obj",
          bom: e.lado === eu,
          txt: `${e.lado === eu ? esc(meusTimes) : esc(deles)} pegou o Barão`,
        });
      else if (e.tipo === "inibidor")
        L.push({
          s: e.s,
          t: "obj",
          bom: e.lado === eu,
          txt: `${e.lado === eu ? esc(meusTimes) : esc(deles)} derrubou um inibidor`,
        });
    }
    if (op)
      for (const m of [5, 10, 15, 20, 25, 30]) {
        if (m * 60 > g.duracao) break;
        const fr = g.serie.reduce((a, b) => (Math.abs(b[0] - m * 60) < Math.abs(a[0] - m * 60) ? b : a));
        const d = fr[3][y.pid - 1][0] - fr[3][op.pid - 1][0];
        L.push({
          s: m * 60,
          t: "ouro",
          bom: d >= 0,
          txt:
            Math.abs(d) < 300
              ? `Aos ${m} min, ouro empatado com ${esc(op.nick)}`
              : `Aos ${m} min, ${d > 0 ? `${mil(d)} de ouro à frente de` : `${mil(-d).replace("+", "")} de ouro atrás de`} ${esc(op.nick)}`,
        });
      }
    L.push({
      s: g.duracao,
      t: "fim",
      bom: y.venceu,
      txt: y.venceu
        ? `Vitória de ${esc(meusTimes)} aos ${mmss(g.duracao)}`
        : `Derrota aos ${mmss(g.duracao)}`,
    });
    return L.sort((a, b) => a.s - b.s);
  }
  function graficoAcontecimentos(y, L) {
    const g = y.j,
      op = rivalDe(g, y);
    if (!op) return "";
    const W_ = 640,
      H = 130,
      pad = 34;
    const S = g.serie.map((s) => [s[0], s[3][y.pid - 1][0] - s[3][op.pid - 1][0]]);
    const lim = Math.ceil(Math.max(1000, ...S.map((s) => Math.abs(s[1]))) / 1000) * 1000;
    const X = (s) => pad + (s / g.duracao) * (W_ - pad - 8),
      Y = (d) => H / 2 - (d / lim) * (H / 2 - 14);
    const em = (s) => S.reduce((a, b) => (Math.abs(b[0] - s) < Math.abs(a[0] - s) ? b : a))[1];
    const pts = S.map((s) => `${X(s[0]).toFixed(1)},${Y(s[1]).toFixed(1)}`).join(" ");
    const id = "ac" + g.id + y.pid;
    return `<svg viewBox="0 0 ${W_} ${H}" class="graf-ac" style="width:100%;height:auto;display:block" role="img" aria-label="Ouro contra ${esc(op.nick)}, com abates e mortes marcados">
    <line x1="${pad}" x2="${W_ - 8}" y1="${H / 2}" y2="${H / 2}" stroke="var(--fg)" stroke-opacity=".3"/>
    <text x="0" y="${Y(lim) + 4}" font-size="10" fill="var(--good)" font-family="JetBrains Mono,monospace">+${lim / 1000}k</text><text x="0" y="${Y(-lim) + 4}" font-size="10" fill="var(--red)" font-family="JetBrains Mono,monospace">−${lim / 1000}k</text>
    <clipPath id="${id}a"><rect x="0" y="0" width="${W_}" height="${H / 2}"/></clipPath><clipPath id="${id}b"><rect x="0" y="${H / 2}" width="${W_}" height="${H / 2}"/></clipPath>
    <polyline points="${pts}" fill="none" stroke="var(--good)" stroke-width="2" clip-path="url(#${id}a)"/><polyline points="${pts}" fill="none" stroke="var(--red)" stroke-width="2" clip-path="url(#${id}b)"/>
    ${L.map((e, i) => (e.t === "abate" || e.t === "morte" ? `<circle class="mk-ac" data-ac="${i}" cx="${X(e.s)}" cy="${Y(em(e.s))}" r="5" fill="${e.t === "abate" ? "var(--good)" : "var(--red)"}" stroke="var(--bg)" stroke-width="1.5"><title>${mmss(e.s)} · ${e.txt.replace(/<[^>]+>/g, "")}</title></circle>` : "")).join("")}
    <line class="cursor-ac" x1="0" x2="0" y1="6" y2="${H - 6}" stroke="var(--gold)" stroke-width="1.5" opacity="0"/>
  </svg>`;
  }
  function blocoAcontecimentos(y) {
    const L = acontecimentos(y);
    const ic = { abate: "⚔", morte: "✖", assist: "＋", obj: "▲", ouro: "◆", alerta: "!", fim: "●" };
    return `<div class="acont"><div class="filtros" role="group" aria-label="Filtrar acontecimentos"><button data-f="tudo" aria-pressed="true">Tudo</button><button data-f="luta" aria-pressed="false">Abates e mortes</button><button data-f="obj" aria-pressed="false">Objetivos</button><button data-f="ouro" aria-pressed="false">Ouro na rota</button></div>
    ${graficoAcontecimentos(y, L)}
    <ol class="lista-ac">${L.map((e, i) => `<li data-i="${i}" data-s="${e.s}" data-t="${e.t}" class="${e.t} ${e.bom === true ? "bom" : e.bom === false ? "ruim" : ""}"><span class="num">${mmss(e.s)}</span><span class="ic-ac" aria-hidden="true">${ic[e.t]}</span><span>${e.txt}</span></li>`).join("")}</ol></div>`;
  }
  function ligarAcontecimentos(raiz, y) {
    raiz.querySelectorAll(".acont").forEach((ac) => {
      const svg = ac.querySelector(".graf-ac"),
        cur = ac.querySelector(".cursor-ac"),
        g = y.j,
        pad = 34,
        W_ = 640;
      const marca = (s) => {
        if (!cur) return;
        const x = pad + (s / g.duracao) * (W_ - pad - 8);
        cur.setAttribute("x1", x);
        cur.setAttribute("x2", x);
        cur.setAttribute("opacity", 1);
      };
      ac.querySelectorAll(".lista-ac li").forEach((li) => {
        li.onmouseenter = () => {
          marca(+li.dataset.s);
          ac.querySelectorAll(".mk-ac").forEach((m) =>
            m.setAttribute("r", m.dataset.ac === li.dataset.i ? 8 : 5),
          );
        };
        li.onclick = li.onmouseenter;
      });
      ac.querySelectorAll(".mk-ac").forEach(
        (m) =>
          (m.onclick = () => {
            const li = ac.querySelector(`.lista-ac li[data-i="${m.dataset.ac}"]`);
            if (li) {
              ac.querySelectorAll(".lista-ac li").forEach((x) => x.classList.remove("foco"));
              li.classList.add("foco");
              li.scrollIntoView({ block: "nearest", behavior: "smooth" });
            }
          }),
      );
      ac.querySelectorAll(".filtros button").forEach(
        (b) =>
          (b.onclick = () => {
            ac.querySelectorAll(".filtros button").forEach((x) => x.setAttribute("aria-pressed", x === b));
            const f = b.dataset.f;
            ac.querySelectorAll(".lista-ac li").forEach((li) => {
              const t = li.dataset.t;
              li.hidden = !(
                f === "tudo" ||
                t === "fim" ||
                (f === "luta" && ["abate", "morte", "assist", "alerta"].includes(t)) ||
                (f === "obj" && t === "obj") ||
                (f === "ouro" && t === "ouro")
              );
            });
          }),
      );
    });
  }
  function cartoesCampeoes(st) {
    return `<div class="camp-cards">${Object.entries(st.det)
      .sort((a, b) => b[1].j - a[1].j)
      .map(([k, c]) => {
        const wr = c.v / c.j,
          R = 20,
          C = 2 * Math.PI * R;
        return `<div class="camp-card">${img(camp(k).icone, "", camp(k).nome)}<div><b>${esc(camp(k).nome)}</b><small>${c.j} ${c.j === 1 ? "jogo" : "jogos"} · KDA ${n1((c.k + c.a) / Math.max(1, c.d))}</small></div>
      <svg viewBox="0 0 50 50" class="anel" aria-label="${pct(wr)} de vitórias"><circle cx="25" cy="25" r="${R}" fill="none" stroke="var(--surface-2)" stroke-width="5"/><circle cx="25" cy="25" r="${R}" fill="none" stroke="${wr >= 0.5 ? "var(--good)" : "var(--red)"}" stroke-width="5" stroke-linecap="round" stroke-dasharray="${C * wr} ${C}" transform="rotate(-90 25 25)"/><text x="25" y="29" text-anchor="middle" font-size="11" fill="var(--fg)" font-family="JetBrains Mono,monospace">${Math.round(wr * 100)}%</text></svg></div>`;
      })
      .join("")}</div>`;
  }

  const tile = (v, r) => `<div class="tile"><b>${v}</b><span>${r}</span></div>`;
  const TIER = {
    IRON: "Ferro",
    BRONZE: "Bronze",
    SILVER: "Prata",
    GOLD: "Ouro",
    PLATINUM: "Platina",
    EMERALD: "Esmeralda",
    DIAMOND: "Diamante",
    MASTER: "Mestre",
    GRANDMASTER: "Grão-Mestre",
    CHALLENGER: "Desafiante",
  };
  function graficoDuelo(j, x) {
    const op = j.jog.find((y) => y.lado !== x.lado && y.rota === x.rota);
    if (!op) return "";
    const L = 640,
      H = 130,
      pad = 34;
    const S = j.serie.map((s) => [s[0], s[3][x.pid - 1][0] - s[3][op.pid - 1][0]]);
    const lim = Math.ceil(Math.max(1000, ...S.map((s) => Math.abs(s[1]))) / 1000) * 1000;
    const X = (s) => pad + (s / j.duracao) * (L - pad - 8),
      Y = (d) => H / 2 - (d / lim) * (H / 2 - 14);
    const pts = S.map((s) => `${X(s[0]).toFixed(1)},${Y(s[1]).toFixed(1)}`).join(" ");
    const ticks = [];
    for (let m = 0; m * 60 <= j.duracao; m += 5) ticks.push(m);
    return `<div class="muted" style="font-size:12.5px;margin-bottom:4px">Diferença de ouro para ${esc(op.nick)} (${esc(camp(op.campeao).nome)}) ao longo do jogo</div>
  <svg viewBox="0 0 ${L} ${H}" style="width:100%;height:auto;display:block" role="img" aria-label="Diferença de ouro contra o rival de rota">
  ${ticks.map((m) => `<line x1="${X(m * 60)}" x2="${X(m * 60)}" y1="6" y2="${H - 16}" stroke="var(--fg)" stroke-opacity=".1"/><text x="${X(m * 60)}" y="${H - 3}" font-size="10" text-anchor="middle" fill="var(--fg)" fill-opacity=".6" font-family="JetBrains Mono,monospace">${m}'</text>`).join("")}
  <line x1="${pad}" x2="${L - 8}" y1="${H / 2}" y2="${H / 2}" stroke="var(--fg)" stroke-opacity=".35"/>
  <text x="0" y="${Y(lim) + 4}" font-size="10" fill="var(--good)" font-family="JetBrains Mono,monospace">+${lim / 1000}k</text><text x="0" y="${Y(-lim) + 4}" font-size="10" fill="var(--red)" font-family="JetBrains Mono,monospace">−${lim / 1000}k</text>
  <clipPath id="dp${j.id}${x.pid}a"><rect x="0" y="0" width="${L}" height="${H / 2}"/></clipPath><clipPath id="dp${j.id}${x.pid}b"><rect x="0" y="${H / 2}" width="${L}" height="${H / 2}"/></clipPath>
  <polyline points="${pts}" fill="none" stroke="var(--good)" stroke-width="2.2" clip-path="url(#dp${j.id}${x.pid}a)"/><polyline points="${pts}" fill="none" stroke="var(--red)" stroke-width="2.2" clip-path="url(#dp${j.id}${x.pid}b)"/></svg>`;
  }
  function abrirJogador(id, jogoId) {
    const a = acharJogador(id);
    if (!a) return;
    const { pl, time } = a;
    const st = statsJogador(id);
    const j = jogoId ? JOGOS.find((g) => g.id === jogoId) : null;
    const x = j?.jog.find((y) => y.jogadorId === id);
    const foto = pl.foto || FOTO[id];
    let html = `<div class="perfil">${logo(time) ? `<img class="logo-fundo" src="${logo(time)}" alt="">` : ""}${foto ? `<img class="f" src="${foto}" alt="${esc(pl.nick)}">` : `<span class="sem-foto" style="width:104px;height:104px;font-size:36px">${esc(pl.nick[0])}</span>`}<div style="min-width:0"><div class="eyebrow">${mini(time)} ${esc(nomeT(time))} · ${ROTA_PT[pl.rota] || pl.rota}</div><h2>${esc(pl.nick)}</h2>${pl.nome ? `<div class="muted">${esc(pl.nome)}</div>` : ""}</div></div>`;
    if (x) {
      const c = camp(x.campeao),
        venceu = j.venc === time,
        adv = j.lados[outro(x.lado)],
        p = PID[j.partida];
      const dpm = x.danoTotal != null ? Math.round(x.danoTotal / (j.duracao / 60)) : null;
      html += `<div class="bloco-f"><h3>Neste jogo <small>${rotuloFase(p, true)} · jogo ${j.numero} contra ${esc(nomeT(adv))}</small></h3>
      <div style="display:flex;gap:14px;align-items:center;margin-bottom:12px;flex-wrap:wrap">${img(c.icone, "", c.nome, "width:64px;height:64px;border-radius:10px")}<div><b style="font-family:var(--display);font-size:26px">${esc(c.nome)}</b><div><span class="res ${venceu ? "v" : "d"}">${venceu ? "V" : "D"}</span> <span class="muted">${venceu ? "Vitória" : "Derrota"} em ${mmss(j.duracao)}</span></div></div>
      <div class="itens" style="margin-left:auto">${(x.itens || [])
        .filter((i) => W.itens[i])
        .map(
          (i) =>
            `<img src="${W.itens[i].icone}" alt="${esc(W.itens[i].nome)}" title="${esc(W.itens[i].nome)}" style="width:32px;height:32px">`,
        )
        .join("")}</div></div>
      <div class="tiles">${tile(`${x.k}/${x.d}/${x.a}`, "K/D/A")}${tile(n1(kda(x)), "KDA")}${tile(x.cs, "CS")}${tile(n1(x.cs / (j.duracao / 60)), "CS/min")}${tile((x.ouro / 1000).toFixed(1) + "k", "Ouro")}${tile(sinal(x.gd15), "Ouro@15")}${tile(dpm ?? "–", "Dano/min")}${tile(pct(x.dano), "% do dano")}${tile(pct(x.kp), "Particip.")}${tile(x.visao ?? "–", "Visão")}${tile(x.wards ?? "–", "Sentinelas")}${tile(x.nivel, "Nível")}</div>
      <div style="margin-top:14px">${graficoDuelo(j, x)}</div>
      <button class="link" style="margin-top:8px" data-partida="${j.partida}" data-k="${jogosDe(j.partida).indexOf(j)}">Ver o jogo completo ›</button></div>`;
    }
    if (st) {
      const fortes = pontosFortes(id, pl, st);
      html +=
        resumoHumano(pl, st, time) +
        (fortes.length
          ? `<div class="fortes">${fortes.map((f) => `<span class="${f.bom ? "" : "ruim"}">${esc(f.t)}</span>`).join("")}</div>`
          : "");
      html += `<div class="bloco-f"><h3>Jornada no Worlds <small>${st.jogos} ${st.jogos === 1 ? "jogo" : "jogos"} em ordem · toque num jogo para ver os detalhes</small></h3>${graficoForma(id, st)}${linhaTempo(id, st)}</div>
    <div class="bloco-f"><h3>Números no torneio <small>${st.v} ${st.v === 1 ? "vitória" : "vitórias"} em ${st.jogos}</small></h3>
      <div class="tiles">${tile(`${st.k}/${st.d}/${st.a}`, "K/D/A total")}${tile(n1(st.kda), "KDA")}${tile(n1(st.csm), "CS/min")}${tile(sinal(st.gd15), "Ouro@15 médio")}${tile(st.dpm ? Math.round(st.dpm) : "–", "Dano/min")}${tile(pct(st.dano), "% do dano")}${tile(pct(st.kp), "Particip.")}${tile(st.visao != null ? n1(st.visao, 0) : "–", "Visão média")}${tile(st.fbK, "First bloods")}</div></div>
    <div class="bloco-f"><h3>Campeões no torneio <small>anel: aproveitamento</small></h3>${cartoesCampeoes(st)}</div>`;
    } else {
      const prox = PARTIDAS.find((p) => p.estado !== "completed" && p.times.some((t) => t.codigo === time));
      html +=
        blocoSoloq(pl) +
        `<div class="bloco-f"><h3>Estreia no Worlds 2026</h3><p style="margin:0 0 10px">${esc(pl.nick)} ainda não entrou em campo neste Worlds. Os números do torneio aparecem aqui depois do primeiro jogo.</p>${prox ? cartao(prox) : ""}</div>`;
    }
    html += blocoHistJogador(pl, st);
    if (st) html += blocoSoloq(pl);
    JORN = st ? st.linhas : [];
    abrirFolha(html);
    ligarJornada(folhaIn);
    marcar("jogador-" + slug(pl.nick));
  }
  const COR_TIER = {
    IRON: "#6b5a50",
    BRONZE: "#a0673f",
    SILVER: "#8d9aa6",
    GOLD: "#c99a3c",
    PLATINUM: "#3fa79a",
    EMERALD: "#2fa35b",
    DIAMOND: "#5b7fe0",
    MASTER: "#9d4dc9",
    GRANDMASTER: "#d1453b",
    CHALLENGER: "#e7b74a",
  };
  const duracaoFalada = (s) => {
    const m = Math.round(s / 60),
      h = Math.floor(m / 60);
    return h ? `${h}h${String(m % 60).padStart(2, "0")}` : `${m} min`;
  };
  function historiaSoloq(pl, sq) {
    const P = sq.partidas.slice().sort((a, b) => b[0] - a[0]);
    if (!P.length) return "";
    const dia = (x) => diaBR(new Date(x[0]).toISOString());
    const d0 = dia(P[0]),
      doDia = P.filter((x) => dia(x) === d0);
    const hoje = diaBR(new Date().toISOString()),
      ontem = diaBR(new Date(Date.now() - 864e5).toISOString());
    const quando =
      d0 === hoje
        ? "Hoje"
        : d0 === ontem
          ? "Ontem"
          : "No último dia em que jogou (" +
            fmt(new Date(P[0][0]).toISOString(), { weekday: "long", day: "numeric", month: "numeric" }) +
            ")";
    const v = doDia.filter((x) => x[3]).length,
      dur = doDia.reduce((s, x) => s + (x[1] || 0), 0);
    const cs = {};
    doDia.forEach((x) => (cs[x[2]] = (cs[x[2]] || 0) + 1));
    const fav = Object.entries(cs).sort((a, b) => b[1] - a[1])[0];
    const dest = doDia
      .slice()
      .sort(
        (a, b) => (b[4] + b[6]) / Math.max(1, b[5]) - (a[4] + a[6]) / Math.max(1, a[5]) || b[4] - a[4],
      )[0];
    let pdl = "";
    const H = sq.hist || [];
    if (H.length >= 2) {
      const ini = H.find((h) => diaBR(new Date(h[0]).toISOString()) >= d0) || H[H.length - 2];
      const fim = H[H.length - 1];
      const pts = (h) =>
        (({ IRON: 0, BRONZE: 400, SILVER: 800, GOLD: 1200, PLATINUM: 1600, EMERALD: 2000, DIAMOND: 2400 })[
          h[1]
        ] ?? 2800) +
        (["MASTER", "GRANDMASTER", "CHALLENGER"].includes(h[1])
          ? 0
          : { IV: 0, III: 100, II: 200, I: 300 }[h[2]] || 0) +
        (h[3] || 0);
      const dp = pts(fim) - pts(ini);
      if (ini !== fim && dp) pdl = ` e ${dp > 0 ? "ganhou" : "perdeu"} <b>${Math.abs(dp)} PDL</b>`;
    }
    const m = dest ? Math.max(1, dest[1] / 60) : 1;
    return `<p class="historia">${quando}, <b>${esc(pl.nick)}</b> jogou <b>${doDia.length} ${doDia.length === 1 ? "partida" : "partidas"}</b>, cerca de ${duracaoFalada(dur)} de jogo, ${doDia.length > 1 && v === doDia.length ? "e venceu todas" : doDia.length > 1 && !v ? "e perdeu todas" : `com ${v} ${v === 1 ? "vitória" : "vitórias"} e ${doDia.length - v} ${doDia.length - v === 1 ? "derrota" : "derrotas"}`}${pdl}.
    ${fav && fav[1] > 1 ? `O campeão do dia foi <b>${esc(camp(fav[0]).nome)}</b>, ${fav[1]} vezes. ` : ""}${dest ? `O destaque foi uma ${dest[3] ? "vitória" : "derrota"} de <b>${esc(camp(dest[2]).nome)}</b> com ${dest[4]}/${dest[5]}/${dest[6]} e ${n1(dest[7] / m)} CS por minuto.` : ""}</p>`;
  }
  function ritmoSoloq(sq) {
    const P = sq.partidas;
    const por = {};
    P.forEach((x) => {
      const d = diaBR(new Date(x[0]).toISOString());
      const o = por[d] || (por[d] = { min: 0, v: 0, d: 0 });
      o.min += (x[1] || 0) / 60;
      x[3] ? o.v++ : o.d++;
    });
    const dias = Object.keys(por).sort().slice(-7);
    if (dias.length < 2) return "";
    const mx = Math.max(...dias.map((d) => por[d].min));
    return `<div class="ritmo">${dias
      .map((d) => {
        const o = por[d];
        return `<div class="dia-r" title="${o.v}V ${o.d}D · ${duracaoFalada(o.min * 60)}"><span class="col-r"><i style="height:${Math.max(6, (o.min / mx) * 100)}%"><b style="height:${(o.v / (o.v + o.d)) * 100}%"></b></i></span><small>${d.slice(8)}/${d.slice(5, 7)}</small><small class="num">${duracaoFalada(o.min * 60)}</small></div>`;
      })
      .join("")}</div>
  <div class="muted" style="font-size:12px;margin-top:4px">Tempo de jogo por dia nas últimas ranqueadas. A parte verde é a fatia de vitórias.</div>`;
  }
  // partida em andamento no momento da coleta; só aparece se a coleta for recente (até 2 h)
  function agoraSoloq(sq) {
    const a = sq.agora;
    if (!a || Date.now() - a.visto > 2 * 3600e3) return "";
    const c = camp(a.camp);
    const min = a.inicio ? Math.max(0, Math.round((a.visto - a.inicio) / 60000)) : null;
    return `<div class="sq-agora">${img(c.icone, "", c.nome)}<span><span class="tag vivo">Em partida</span> <b>ranqueada de ${esc(c.nome)}</b><small>visto às ${hora(new Date(a.visto).toISOString())}${min != null ? ` · ${min} min de jogo` : ""}</small></span></div>`;
  }
  function maestriaSoloq(sq) {
    const M = sq.maestria || [];
    if (!M.length) return "";
    const top = Math.max(...M.map((m) => m[2] || 0), 1);
    const fmt = (n) => (n >= 1e6 ? n1(n / 1e6) + " mi" : Math.round(n / 1e3) + " mil");
    return `<h4 class="sub-h">Maestria <small>campeões com mais pontos na conta</small></h4><div class="pool">${M.map(([k, nv, pts]) => `<div class="pool-l">${img(camp(k).icone, "", camp(k).nome)}<span><b>${esc(camp(k).nome)}</b><small>nível ${nv} · ${fmt(pts || 0)} pontos</small></span><span class="pool-b mae"><i style="width:${((pts || 0) / top) * 100}%;background:var(--gold)"></i></span><span></span></div>`).join("")}</div>`;
  }
  function blocoSoloq(pl) {
    const sq = pl.soloq,
      ct = pl.contas;
    const links = ct
      ? Object.entries(ct.links || {})
          .map(
            ([k, u]) =>
              `<a href="${esc(u)}" target="_blank" rel="noopener">${{ dpm_lol: "dpm.lol", lolpros: "lolpros.gg", leaguepedia: "Leaguepedia" }[k] || k}</a>`,
          )
          .join(" · ")
      : "";
    let h = `<div class="bloco-f soloq"><h3>Solo queue <small>fora do Worlds · ${sq ? `conta ${sq.link ? `<a href="${esc(sq.link)}" target="_blank" rel="noopener">${esc(sq.conta)}</a>` : esc(sq.conta)} (${esc(sq.servidor)})` : ""}</small></h3>`;
    if (sq && sq.partidas?.length) {
      const P = sq.partidas.slice().sort((a, b) => b[0] - a[0]);
      const vit = P.filter((p) => p[3]).length;
      const e = sq.elo;
      const alto = e && ["MASTER", "GRANDMASTER", "CHALLENGER"].includes(e.tier);
      const cor = COR_TIER[e?.tier] || "var(--muted)";
      const wr = e ? e.wins / Math.max(1, e.wins + e.losses) : null,
        R = 22,
        C = 2 * Math.PI * R;
      const camps = {};
      P.forEach((p) => {
        const c = (camps[p[2]] = camps[p[2]] || { j: 0, v: 0, k: 0, d: 0, a: 0 });
        c.j++;
        c.v += p[3] ? 1 : 0;
        c.k += p[4];
        c.d += p[5];
        c.a += p[6];
      });
      h += `<div class="sq-topo">
      <div class="emblema" style="--cor:${cor}"><span>${e ? esc((TIER[e.tier] || e.tier).slice(0, 1)) : "–"}</span></div>
      <div class="sq-elo"><b>${e ? `${TIER[e.tier] || e.tier}${alto ? "" : " " + e.rank}` : "Sem elo"}</b><span class="num">${e ? e.leaguePoints + " PDL" : ""}</span>${e && !alto ? `<span class="lp-barra"><i style="width:${Math.min(100, e.leaguePoints)}%;background:${cor}"></i></span>` : ""}</div>
      ${wr != null ? `<div class="sq-temp"><svg viewBox="0 0 54 54" class="anel"><circle cx="27" cy="27" r="${R}" fill="none" stroke="var(--surface-2)" stroke-width="5"/><circle cx="27" cy="27" r="${R}" fill="none" stroke="${wr >= 0.5 ? "var(--good)" : "var(--red)"}" stroke-width="5" stroke-linecap="round" stroke-dasharray="${C * wr} ${C}" transform="rotate(-90 27 27)"/><text x="27" y="31" text-anchor="middle" font-size="11.5" fill="var(--fg)" font-family="JetBrains Mono,monospace">${Math.round(wr * 100)}%</text></svg><span><b class="num">${e.wins}V ${e.losses}D</b><small>na temporada</small></span></div>` : ""}
      <div class="sq-temp"><span><b class="num">${vit}V ${P.length - vit}D</b><small>nas últimas ${P.length}</small></span></div></div>
    ${agoraSoloq(sq)}${historiaSoloq(pl, sq)}
    <h4 class="sub-h">Últimas partidas <small>da mais recente para a mais antiga · passe o mouse para ver os números</small></h4>
    <div class="faixa-sq">${P.map((p) => {
      const c = camp(p[2]);
      const m = Math.max(1, (p[1] || 1) / 60);
      return `<div class="pq ${p[3] ? "v" : "d"}" tabindex="0" title="${esc(c.nome)} · ${p[3] ? "vitória" : "derrota"} · ${p[4]}/${p[5]}/${p[6]} · ${n1(p[7] / m)} CS/min · ${dataHora(new Date(p[0]).toISOString())}">${img(c.icone, "", c.nome)}<small class="num">${p[4]}/${p[5]}/${p[6]}</small></div>`;
    }).join("")}</div>
    ${ritmoSoloq(sq)}${maestriaSoloq(sq)}
    <h4 class="sub-h">Campeões na solo queue</h4>
    <div class="pool">${Object.entries(camps)
      .sort((a, b) => b[1].j - a[1].j)
      .slice(0, 6)
      .map(
        ([k, c]) =>
          `<div class="pool-l">${img(camp(k).icone, "", camp(k).nome)}<span><b>${esc(camp(k).nome)}</b><small>${c.j} ${c.j === 1 ? "jogo" : "jogos"} · KDA ${n1((c.k + c.a) / Math.max(1, c.d))}</small></span><span class="pool-b"><i style="width:${(c.v / c.j) * 100}%"></i></span><span class="num">${Math.round((c.v / c.j) * 100)}%</span></div>`,
      )
      .join("")}</div>`;
    } else if (ct && ct.contas.length) {
      h += `<p class="muted" style="margin-top:0;font-size:13px">Não conseguimos ler as ranqueadas recentes deste jogador na API da Riot (a conta pode ter mudado de nome). As contas conhecidas, segundo a Leaguepedia:</p>
    <div class="lista-linhas">${ct.contas
      .slice(0, 8)
      .map(
        (c) =>
          `<div class="r"><span class="tag">${esc(c.servidor || "")}</span><span>${c.link ? `<a href="${esc(c.link)}" target="_blank" rel="noopener">${esc(c.riotId)}</a>` : esc(c.riotId)}</span><span></span></div>`,
      )
      .join("")}</div>`;
    } else
      h += `<p class="muted" style="margin:0">Não encontramos contas de solo queue conhecidas deste jogador.</p>`;
    return (
      h +
      (links ? `<p style="font-size:13px;margin:12px 0 0">Mais sobre o jogador: ${links}</p>` : "") +
      `</div>`
    );
  }

  /* ---------- chance de vitória ao longo do jogo ---------- */
  // Regressão logística simples, ajustada nos próprios jogos coletados: diferença de ouro (e seu peso com o tempo), torres, dragões e barões.
  function estadoEm(j, s) {
    const fr = j.serie.reduce((a, b) => (b[0] <= s ? b : a), j.serie[0]);
    const c = (t, l) =>
      j.ev.filter((e) => e.s <= s && e.tipo === t && e.lado === l).reduce((x, e) => x + (e.n || 1), 0);
    const gd = (fr[1] - fr[2]) / 1000,
      m = s / 1800;
    return [
      gd,
      gd * m,
      c("torre", "blue") - c("torre", "red"),
      c("dragao", "blue") - c("dragao", "red"),
      c("barao", "blue") - c("barao", "red"),
    ];
  }
  let _modelo = null;
  function modeloVitoria() {
    if (_modelo) return _modelo;
    const X = [],
      Y = [];
    for (const j of JOGOS)
      for (const fr of j.serie) {
        if (fr[0] < 60) continue;
        X.push(estadoEm(j, fr[0]));
        Y.push(j.vencedor === "blue" ? 1 : 0);
      }
    let w = [0.35, 0.35, 0.15, 0.1, 0.3],
      b = 0;
    const lr = 0.05,
      l2 = 0.01;
    for (let it = 0; it < 400 && X.length; it++) {
      const g = w.map(() => 0);
      let gb = 0;
      for (let i = 0; i < X.length; i++) {
        const z = b + X[i].reduce((s, x, k) => s + x * w[k], 0),
          e = 1 / (1 + Math.exp(-z)) - Y[i];
        gb += e;
        X[i].forEach((x, k) => (g[k] += e * x));
      }
      w = w.map((v, k) => v - lr * (g[k] / X.length + l2 * v));
      b -= (lr * gb) / X.length;
    }
    return (_modelo = { w, b: 0 }); // sem viés de lado: o modelo só olha o estado do jogo
  }
  function chanceAzul(j, s) {
    const m = modeloVitoria(),
      x = estadoEm(j, s);
    return 1 / (1 + Math.exp(-(m.b + x.reduce((t, v, k) => t + v * m.w[k], 0))));
  }
  function graficoChance(j) {
    const L = 640,
      H = 150,
      pad = 34;
    const pts = j.serie.map((fr) => [fr[0], fr[0] < 60 ? 0.5 : chanceAzul(j, fr[0])]);
    const X = (s) => pad + (s / j.duracao) * (L - pad - 8),
      Y = (p) => 8 + (1 - p) * (H - 24);
    const vAz = j.vencedor === "blue";
    let pior = { p: 0.5, s: 0 },
      pv = 0.5;
    for (const [s, p] of pts) {
      const q = vAz ? p : 1 - p;
      if (q < pv) {
        pv = q;
        pior = { p, s };
      }
    }
    const ticks = [];
    for (let m = 0; m * 60 <= j.duracao; m += 5) ticks.push(m);
    const linha = pts.map(([s, p]) => `${X(s).toFixed(1)},${Y(p).toFixed(1)}`).join(" ");
    const nota =
      pv < 0.35
        ? `${esc(j.venc)} chegou a ter só ${pct(pv)} de chance aos ${mmss(pior.s)} e virou o jogo.`
        : `${esc(j.venc)} nunca ficou muito atrás: a menor chance foi ${pct(pv)}.`;
    return `<svg viewBox="0 0 ${L} ${H}" style="width:100%;height:auto;display:block" role="img" aria-label="Chance de vitória de cada time ao longo do jogo">
    ${ticks.map((m) => `<line x1="${X(m * 60)}" x2="${X(m * 60)}" y1="8" y2="${H - 16}" stroke="var(--fg)" stroke-opacity=".1"/><text x="${X(m * 60)}" y="${H - 3}" font-size="10" text-anchor="middle" fill="var(--fg)" fill-opacity=".6" font-family="JetBrains Mono,monospace">${m}'</text>`).join("")}
    <line x1="${pad}" x2="${L - 8}" y1="${Y(0.5)}" y2="${Y(0.5)}" stroke="var(--fg)" stroke-opacity=".35" stroke-dasharray="3 3"/>
    <text x="0" y="${Y(1) + 8}" font-size="10" fill="var(--blue)" font-family="JetBrains Mono,monospace">${esc(j.az)}</text><text x="0" y="${Y(0)}" font-size="10" fill="var(--red)" font-family="JetBrains Mono,monospace">${esc(j.vm)}</text>
    <clipPath id="wp${j.id}a"><rect x="0" y="0" width="${L}" height="${Y(0.5)}"/></clipPath><clipPath id="wp${j.id}b"><rect x="0" y="${Y(0.5)}" width="${L}" height="${H}"/></clipPath>
    <polyline points="${linha}" fill="none" stroke="var(--blue)" stroke-width="2.2" stroke-linejoin="round" clip-path="url(#wp${j.id}a)"/><polyline points="${linha}" fill="none" stroke="var(--red)" stroke-width="2.2" stroke-linejoin="round" clip-path="url(#wp${j.id}b)"/>
    ${pv < 0.35 ? `<circle cx="${X(pior.s)}" cy="${Y(pior.p)}" r="4" fill="var(--gold)"/>` : ""}
  </svg><p class="muted" style="font-size:12.5px;margin:6px 0 0">${nota} Estimativa a partir de ouro, torres, dragões e barões, calibrada nos ${JOGOS.length} jogos deste Worlds.</p>`;
  }

  /* ---------- meta do torneio ---------- */
  function painelMeta() {
    if (!JOGOS.length) {
      $("#p-meta").innerHTML =
        '<p class="muted">As estatísticas de meta aparecem depois dos primeiros jogos.</p>';
      return;
    }
    const n = JOGOS.length,
      c = {};
    let jogosLp = 0;
    const ent = (k) => (c[k] ??= { p: 0, v: 0, b: 0, az: 0, k: 0, d: 0, a: 0 });
    for (const j of JOGOS) {
      for (const x of j.jog) {
        const e = ent(x.campeao);
        e.p++;
        if (j.venc === x.time) e.v++;
        e.k += x.k;
        e.d += x.d;
        e.a += x.a;
      }
      if (j.lp) {
        jogosLp++;
        ["blue", "red"].forEach((l) => j.lp.bans[l].forEach((b) => ent(b).b++));
      }
    }
    const azul = JOGOS.filter((j) => j.vencedor === "blue").length,
      dur = JOGOS.reduce((s, j) => s + j.duracao, 0) / n;
    const drag = {};
    JOGOS.forEach((j) =>
      j.ev.filter((e) => e.tipo === "dragao").forEach((e) => (drag[e.dragao] = (drag[e.dragao] || 0) + 1)),
    );
    const almas = {};
    JOGOS.forEach((j) => {
      for (const l of ["blue", "red"]) {
        const d = j.ev.filter((e) => e.tipo === "dragao" && e.lado === l && e.dragao !== "elder");
        if (d.length >= 4) {
          const t = d[3].dragao;
          almas[t] = (almas[t] || 0) + 1;
        }
      }
    });
    const fb =
      JOGOS.filter((j) => j.fb && j.fb.lado === j.vencedor).length / JOGOS.filter((j) => j.fb).length;
    const fd =
      JOGOS.filter((j) => j.fd && j.fd.lado === j.vencedor).length / JOGOS.filter((j) => j.fd).length;
    const ft =
      JOGOS.filter((j) => j.ft && j.ft.lado === j.vencedor).length / JOGOS.filter((j) => j.ft).length;
    const g15 = JOGOS.filter((j) => j.s15 && j.s15[1] !== j.s15[2]);
    const g15v =
      g15.filter((j) => j.s15[1] > j.s15[2] === (j.vencedor === "blue")).length / Math.max(1, g15.length);
    const linhas = Object.entries(c)
      .map(([k, e]) => ({ ...e, id: k, pres: e.p / n + (jogosLp ? e.b / jogosLp : 0), hist: presHist(k) }))
      .sort((a, b) => b.pres - a.pres || b.p - a.p);
    const tabela = (lst) =>
      `<div class="tab-wrap"><table class="est meta"><thead><tr><th>Campeão</th><th title="Escolhas sobre todos os jogos mais bans sobre os jogos com bans registrados">Presença</th><th>Escolhas</th><th>Bans</th><th>Vitórias</th><th>Aproveit.</th><th>KDA</th><th title="Presença média nos 15 Mundiais anteriores (2011 a 2025), contando zero quando não apareceu">Média histórica</th></tr></thead><tbody>${lst.map((e) => `<tr class="clic" data-camp="${esc(e.id)}" tabindex="0"><td><div class="jog">${img(camp(e.id).icone, "camp", camp(e.id).nome)}<b>${esc(camp(e.id).nome)}</b></div></td><td>${pct(e.pres)}</td><td>${e.p}</td><td>${jogosLp ? e.b : "–"}</td><td>${e.v}</td><td>${e.p ? pct(e.v / e.p) : "–"}</td><td>${e.p ? n1((e.k + e.a) / Math.max(1, e.d)) : "–"}</td><td class="muted">${e.hist == null ? "–" : pct(e.hist)}</td></tr>`).join("")}</tbody></table></div>`;
    const barraL = (rot, v, cor) =>
      `<div class="l" style="grid-template-columns:150px 1fr 52px"><span class="rot" style="text-align:left">${rot}</span><div class="barra"><i style="width:${v * 100}%;background:${cor || "var(--gold)"}"></i></div><span class="v">${pct(v)}</span></div>`;
    const dragTot = Object.values(drag).reduce((a, b) => a + b, 0) || 1;
    $("#p-meta").innerHTML =
      `<p class="nota" style="margin:0 0 16px">O que está forte neste Worlds, com os ${n} jogos disputados até agora. Os bans vêm da Leaguepedia, que tem ${jogosLp} desses jogos registrados.</p>
  <div class="tiles" style="margin-bottom:14px">${tile(pct(azul / n), "Vitórias do lado azul")}${tile(pct(1 - azul / n), "Vitórias do lado vermelho")}${tile(mmss(dur), "Duração média")}${tile(Object.keys(c).filter((k) => c[k].p).length, "Campeões escolhidos")}${tile(Object.keys(c).length, "Escolhidos ou banidos")}</div>
  <div class="dois"><div class="bloco-f"><h3>O que mais decide jogo <small>quem conseguiu primeiro e venceu</small></h3><div class="cmp">${barraL("First blood", fb)}${barraL("Primeiro dragão", fd)}${barraL("Primeira torre", ft)}${barraL("À frente aos 15 min", g15v)}</div></div>
  <div class="bloco-f"><h3>Dragões <small>${dragTot} abatidos${Object.keys(almas).length ? ` · ${Object.values(almas).reduce((a, b) => a + b, 0)} almas` : ""}</small></h3><div class="cmp">${Object.entries(
    drag,
  )
    .sort((a, b) => b[1] - a[1])
    .map(([k, v]) =>
      barraL(
        `${DRAG[k]?.[0] || k}${almas[k] ? ` <small class="muted">· ${almas[k]} ${almas[k] === 1 ? "alma" : "almas"}</small>` : ""}`,
        v / dragTot,
        DRAG[k]?.[1],
      ),
    )
    .join("")}</div></div></div>
  <div class="bloco-f"><h3>Campeões <small>ordenados por presença · clique no título de uma coluna para reordenar</small></h3><div id="tab-meta">${tabela(linhas)}</div></div>`;
    const chaves = ["nome", "pres", "p", "b", "v", "wr", "kda", "hist"];
    const ligar = () =>
      $("#p-meta")
        .querySelectorAll("table.meta th")
        .forEach((th, i) => {
          th.style.cursor = "pointer";
          th.onclick = () => {
            const k = chaves[i];
            const val = (e) =>
              k === "nome"
                ? camp(e.id).nome
                : k === "hist"
                  ? (e.hist ?? -1)
                  : k === "wr"
                    ? e.p
                      ? e.v / e.p
                      : -1
                    : k === "kda"
                      ? e.p
                        ? (e.k + e.a) / Math.max(1, e.d)
                        : -1
                      : e[k];
            linhas.sort((x, y) => (k === "nome" ? val(x).localeCompare(val(y)) : val(y) - val(x)));
            $("#tab-meta").innerHTML = tabela(linhas);
            ligar();
          };
        });
    ligar();
  }

  /* ---------- comparar jogadores ---------- */
  function opcoesJogadores(sel) {
    const grupos = Object.values(TIMES)
      .filter((t) => t.jogadores.some((p) => statsJogador(p.id)))
      .sort((a, b) => a.nome.localeCompare(b.nome));
    return grupos
      .map(
        (t) =>
          `<optgroup label="${esc(t.nome)}">${t.jogadores
            .filter((p) => statsJogador(p.id))
            .map(
              (p) =>
                `<option value="${p.id}" ${p.id === sel ? "selected" : ""}>${esc(p.nick)} · ${ROTA_PT[p.rota] || p.rota}</option>`,
            )
            .join("")}</optgroup>`,
      )
      .join("");
  }
  function painelComparar(a, b) {
    const ids = [...new Set(JOGOS.flatMap((j) => j.jog.map((x) => x.jogadorId)))];
    if (!ids.length) {
      $("#p-comparar").innerHTML = '<p class="muted">O comparador aparece depois dos primeiros jogos.</p>';
      return;
    }
    if (!a || !b) {
      const st = ids
        .map((id) => ({ id, s: statsJogador(id), ...acharJogador(id) }))
        .filter((x) => x.pl && x.s);
      const mids = st.filter((x) => x.pl.rota === "mid").sort((x, y) => y.s.jogos - x.s.jogos);
      a = a || mids[0]?.id || ids[0];
      b = b || mids.find((x) => x.time !== acharJogador(a).time)?.id || ids[1];
    }
    const A = acharJogador(a),
      B = acharJogador(b),
      sa = statsJogador(a),
      sb = statsJogador(b);
    const lin = [
      ["Jogos", (s) => s.jogos, (v) => v, 0],
      ["Vitórias", (s) => s.v / s.jogos, pct, 0],
      ["KDA", (s) => s.kda, n1, 0],
      ["Abates por jogo", (s) => s.k / s.jogos, n1, 0],
      ["Mortes por jogo", (s) => s.d / s.jogos, n1, 1],
      ["Assistências por jogo", (s) => s.a / s.jogos, n1, 0],
      ["CS por minuto", (s) => s.csm, n1, 0],
      ["Ouro@15", (s) => s.gd15, sinal, 0],
      ["Dano por minuto", (s) => s.dpm, (v) => (v == null ? "–" : Math.round(v)), 0],
      ["% do dano do time", (s) => s.dano, pct, 0],
      ["Participação em abates", (s) => s.kp, pct, 0],
      ["Visão por jogo", (s) => s.visao, (v) => (v == null ? "–" : Math.round(v)), 0],
      ["First bloods", (s) => s.fbK, (v) => v, 0],
    ];
    const cab = (x, s, id) =>
      `<div class="cmp-jog">${x.pl.foto || FOTO[id] ? `<img class="f" src="${x.pl.foto || FOTO[id]}" alt="">` : `<span class="sem-foto">${esc(x.pl.nick[0])}</span>`}<div><b>${esc(x.pl.nick)}</b><div class="ns">${mini(x.time)} ${esc(nomeT(x.time))} · ${ROTA_PT[x.pl.rota] || ""}</div></div></div>`;
    const linha = ([rot, f, fm, menor]) => {
      const va = f(sa),
        vb = f(sb);
      const ga = va != null && vb != null && (menor ? va < vb : va > vb),
        gb = va != null && vb != null && (menor ? vb < va : vb > va);
      return `<div class="l cmp2"><span class="v b ${ga ? "melhor" : ""}">${fm(va)}</span><span class="rot">${rot}</span><span class="v ${gb ? "melhor" : ""}">${fm(vb)}</span></div>`;
    };
    $("#p-comparar").innerHTML =
      `<p class="nota" style="margin:0 0 16px">Escolha dois jogadores de qualquer time para ver os números lado a lado, só com jogos deste Worlds. Em dourado, quem leva vantagem em cada linha.</p>
  <div class="escolhas"><select data-cmp="a" aria-label="Primeiro jogador">${opcoesJogadores(a)}</select><span class="muted">×</span><select data-cmp="b" aria-label="Segundo jogador">${opcoesJogadores(b)}</select></div>
  <div class="bloco-f"><div class="dois cab-cmp"><button class="link" data-jogador="${a}">${cab(A, sa, a)}</button><button class="link dir" data-jogador="${b}">${cab(B, sb, b)}</button></div>
  <div class="cmp">${lin.map(linha).join("")}</div></div>
  <div class="dois"><div class="bloco-f"><h3>Campeões · ${esc(A.pl.nick)}</h3><div class="camps">${topCamps(sa)}</div></div><div class="bloco-f"><h3>Campeões · ${esc(B.pl.nick)}</h3><div class="camps">${topCamps(sb)}</div></div></div>`;
    $("#p-comparar")
      .querySelectorAll("[data-cmp]")
      .forEach(
        (s) =>
          (s.onchange = () => {
            const v = s.value;
            s.dataset.cmp === "a" ? painelComparar(v, b) : painelComparar(a, v);
          }),
      );
  }

  /* ---------- destaques do dia ---------- */
  function diaBR(iso) {
    return fmt(iso, { year: "numeric", month: "2-digit", day: "2-digit" }).split("/").reverse().join("-");
  }
  function destaquesDoDia() {
    const comJogo = JOGOS.filter((j) => PID[j.partida]);
    if (!comJogo.length) return "";
    const dia = comJogo
      .map((j) => diaBR(PID[j.partida].inicio))
      .sort()
      .pop();
    const js = comJogo.filter((j) => diaBR(PID[j.partida].inicio) === dia);
    const longo = js.slice().sort((a, b) => b.duracao - a.duracao)[0];
    let virada = null;
    for (const j of js) {
      const sinalV = j.vencedor === "blue" ? 1 : -1;
      const pior = Math.min(...j.serie.map((f) => (f[1] - f[2]) * sinalV));
      if (pior <= -2500 && (!virada || pior < virada.d)) virada = { j, d: pior };
    }
    let kd = null;
    for (const j of js)
      for (const x of j.jog) {
        const v = kda(x);
        if (!kd || v > kd.v || (v === kd.v && x.k > kd.x.k)) kd = { j, x, v };
      }
    let ab = null;
    for (const j of js) for (const x of j.jog) if (!ab || x.k > ab.x.k) ab = { j, x };
    const quando = fmt(PID[js[0].partida].inicio, { weekday: "long", day: "numeric", month: "long" });
    const item = (rot, valor, txt, attrs) =>
      `<button class="dd" ${attrs}><span class="eyebrow">${rot}</span><b>${valor}</b><span>${txt}</span></button>`;
    const jl = (j) => `data-partida="${j.partida}" data-k="${jogosDe(j.partida).indexOf(j)}"`;
    return `<div class="bloco-f destaque-dia"><h3>Destaques do dia <small>${quando} · ${js.length} ${js.length === 1 ? "jogo" : "jogos"}</small></h3><div class="dd-grade">
    ${item("Jogo mais longo", mmss(longo.duracao), `${esc(longo.az)} × ${esc(longo.vm)}, vitória de ${esc(longo.venc)}`, jl(longo))}
    ${virada ? item("Maior virada", mil(-virada.d).replace("+", ""), `${esc(virada.j.venc)} esteve atrás em ouro e venceu ${esc(virada.j.az === virada.j.venc ? virada.j.vm : virada.j.az)}`, jl(virada.j)) : ""}
    ${item("Melhor KDA", `${kd.x.k}/${kd.x.d}/${kd.x.a}`, `${esc(kd.x.nick)} de ${esc(camp(kd.x.campeao).nome)} (${esc(kd.x.time)})`, `data-jogador="${kd.x.jogadorId}" data-jogo="${kd.j.id}"`)}
    ${ab.x !== kd.x ? item("Mais abates", ab.x.k, `${esc(ab.x.nick)} de ${esc(camp(ab.x.campeao).nome)} (${esc(ab.x.time)})`, `data-jogador="${ab.x.jogadorId}" data-jogo="${ab.j.id}"`) : ""}
  </div></div>`;
  }

  /* ---------- destaques do torneio ---------- */
  /* ---------- tabela por posição (estilo Oracle's Elixir / gol.gg) ---------- */
  function metricasPosicao() {
    const M = {};
    for (const j of JOGOS) {
      const min = j.duracao / 60;
      const f10 = j.serie.reduce((a, b) => (Math.abs(b[0] - 600) < Math.abs(a[0] - 600) ? b : a), j.serie[0]);
      const ouroTime = {};
      j.jog.forEach((x) => (ouroTime[x.lado] = (ouroTime[x.lado] || 0) + (x.ouro || 0)));
      for (const x of j.jog) {
        const m = (M[x.jogadorId] ??= {
          id: x.jogadorId,
          nick: x.nick,
          time: x.time,
          rota: x.rota,
          j: 0,
          v: 0,
          k: 0,
          d: 0,
          a: 0,
          ouro: 0,
          min: 0,
          cs: 0,
          wards: 0,
          parte: 0,
          csd: 0,
          ncsd: 0,
          dano: 0,
          minDano: 0,
        });
        m.j++;
        if (j.venc === x.time) m.v++;
        m.k += x.k;
        m.d += x.d;
        m.a += x.a;
        m.ouro += x.ouro || 0;
        m.min += min;
        m.cs += x.cs || 0;
        m.wards += x.wards || 0;
        m.parte += ouroTime[x.lado] ? (x.ouro || 0) / ouroTime[x.lado] : 0;
        if (x.danoTotal != null) {
          m.dano += x.danoTotal;
          m.minDano += min;
        }
        const op = j.jog.find((o) => o.lado !== x.lado && o.rota === x.rota);
        if (op && j.duracao >= 600 && f10[3]) {
          m.csd += f10[3][x.pid - 1][4] - f10[3][op.pid - 1][4];
          m.ncsd++;
        }
      }
    }
    return Object.values(M).map((m) => ({
      ...m,
      kda: (m.k + m.a) / Math.max(1, m.d),
      dpm: m.minDano ? m.dano / m.minDano : null,
      gpm: m.ouro / m.min,
      parteOuro: m.parte / m.j,
      csd10: m.ncsd ? m.csd / m.ncsd : null,
      csm: m.cs / m.min,
      wpm: m.wards / m.min,
    }));
  }
  const COLS_POS = [
    ["nick", "Jogador", null],
    ["j", "Jogos", (v) => v],
    ["kda", "KDA", n1],
    ["dpm", "Dano/min", (v) => (v == null ? "–" : Math.round(v))],
    ["gpm", "Ouro/min", (v) => Math.round(v)],
    ["parteOuro", "% do ouro", pct],
    ["csd10", "CS dif. @10", (v) => (v == null ? "–" : (v > 0 ? "+" : "") + n1(v))],
    ["csm", "CS/min", n1],
    ["wpm", "Sentinelas/min", (v) => v.toFixed(2).replace(".", ",")],
  ];
  let _pos = { rota: "top", ord: "kda" };
  function tabelaPosicao() {
    const L = metricasPosicao().filter((m) => _pos.rota === "todas" || m.rota === _pos.rota);
    const k = _pos.ord;
    L.sort((a, b) => (k === "nick" ? a.nick.localeCompare(b.nick) : (b[k] ?? -1e9) - (a[k] ?? -1e9)));
    return `<div class="filtros-pos" role="group" aria-label="Posição">${[
      ["top", "Topo"],
      ["jungle", "Selva"],
      ["mid", "Meio"],
      ["bottom", "Atirador"],
      ["support", "Suporte"],
      ["todas", "Todas"],
    ]
      .map(
        ([r, n]) =>
          `<button class="link ${_pos.rota === r ? "ativo" : ""}" data-pos="${r}" aria-pressed="${_pos.rota === r}">${n}</button>`,
      )
      .join("")}</div>
  <div class="tab-wrap"><table class="est pos"><thead><tr>${COLS_POS.map(([c, n]) => `<th data-ord="${c}" class="${c === k ? "ord" : ""}" tabindex="0">${n}</th>`).join("")}</tr></thead><tbody>${L.map((m) => `<tr class="clic" data-jogador="${m.id}" tabindex="0">${COLS_POS.map(([c, n, f]) => (c === "nick" ? `<td><b>${esc(m.nick)}</b> <small class="muted">${esc(m.time)}</small></td>` : `<td class="num">${f(m[c])}</td>`)).join("")}</tr>`).join("")}</tbody></table></div>
  <p class="muted" style="font-size:12px;margin:8px 0 0">Dano por minuto só nos jogos com placar da Leaguepedia. CS dif. @10 é a diferença de tropas abatidas para o rival da mesma rota aos 10 minutos.</p>`;
  }
  function ligarPosicao() {
    const el = $("#tab-pos");
    if (!el) return;
    const r = () => {
      el.innerHTML = tabelaPosicao();
    };
    r();
    el.addEventListener("click", (e) => {
      const b = e.target.closest("[data-pos]");
      if (b) {
        _pos.rota = b.dataset.pos;
        r();
        return;
      }
      const th = e.target.closest("th[data-ord]");
      if (th) {
        _pos.ord = th.dataset.ord;
        r();
      }
    });
    el.addEventListener("keydown", (e) => {
      const th = e.target.closest("th[data-ord]");
      if (th && (e.key === "Enter" || e.key === " ")) {
        e.preventDefault();
        _pos.ord = th.dataset.ord;
        r();
      }
    });
  }

  function painelDestaques() {
    if (!JOGOS.length) {
      $("#p-destaques").innerHTML = '<p class="muted">Os destaques aparecem depois dos primeiros jogos.</p>';
      return;
    }
    const ids = [...new Set(JOGOS.flatMap((j) => j.jog.map((x) => x.jogadorId)))];
    const J = ids.map((id) => ({ id, st: statsJogador(id), ...acharJogador(id) }));
    const lj = (titulo, sub, val, fmt_, filtro = () => true, asc = false) => {
      const l = J.filter((x) => filtro(x) && val(x) != null)
        .sort((a, b) => (asc ? val(a) - val(b) : val(b) - val(a)))
        .slice(0, 5);
      return `<div class="bloco-f"><h3>${titulo} <small>${sub || ""}</small></h3><ol>${l.map((x, i) => `<li><button data-jogador="${x.id}"><span class="ord">${i + 1}</span>${x.pl.foto ? `<img class="f" src="${x.pl.foto}" alt="">` : `<span class="sem-foto" style="width:34px;height:34px;font-size:14px">${esc(x.pl.nick[0])}</span>`}<span><b>${esc(x.pl.nick)}</b><small>${esc(x.time)} · ${ROTA_PT[x.pl.rota] || ""} · ${x.st.jogos} ${x.st.jogos === 1 ? "jogo" : "jogos"}</small></span><span class="val">${fmt_(val(x))}</span></button></li>`).join("")}</ol></div>`;
    };
    const min3 = (x) => x.st.jogos >= 3;
    // campeões
    const picks = {},
      vit = {},
      bans = {};
    let jogosLp = 0;
    for (const j of JOGOS) {
      for (const x of j.jog) {
        picks[x.campeao] = (picks[x.campeao] || 0) + 1;
        if (j.venc === x.time) vit[x.campeao] = (vit[x.campeao] || 0) + 1;
      }
      if (j.lp) {
        jogosLp++;
        ["blue", "red"].forEach((l) => j.lp.bans[l].forEach((b) => (bans[b] = (bans[b] || 0) + 1)));
      }
    }
    const lc = (titulo, sub, obj, fmt_) => {
      const l = Object.entries(obj)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      return `<div class="bloco-f"><h3>${titulo} <small>${sub}</small></h3><ol>${l.map(([k, v], i) => `<li><button style="cursor:default"><span class="ord">${i + 1}</span>${img(camp(k).icone, "c", camp(k).nome)}<span><b>${esc(camp(k).nome)}</b><small>${fmt_(k, v)}</small></span><span class="val">${v}</span></button></li>`).join("")}</ol></div>`;
    };
    const pres = {};
    Object.keys({ ...picks, ...bans }).forEach((k) => (pres[k] = (picks[k] || 0) + (bans[k] || 0)));
    // times
    const ts = Object.keys(TIMES)
      .map((c) => ({ c, s: statsTime(c) }))
      .filter((x) => x.s);
    const lt = (titulo, sub, val, fmt_) => {
      const l = ts
        .filter((x) => val(x.s) != null)
        .sort((a, b) => val(b.s) - val(a.s))
        .slice(0, 5);
      return `<div class="bloco-f"><h3>${titulo} <small>${sub || ""}</small></h3><ol>${l.map((x, i) => `<li><button data-time="${x.c}"><span class="ord">${i + 1}</span>${img(logo(x.c), "c", x.c, "object-fit:contain")}<span><b>${esc(nomeT(x.c))}</b><small>${x.s.jogos} jogos</small></span><span class="val">${fmt_(val(x.s))}</span></button></li>`).join("")}</ol></div>`;
    };
    // jogos marcantes
    const jm = (titulo, j, txt) =>
      j
        ? `<button class="r" data-partida="${j.partida}" data-k="${jogosDe(j.partida).indexOf(j)}"><span class="eyebrow" style="min-width:120px">${titulo}</span><span>${mini(j.az)} ${esc(j.az)} × ${esc(j.vm)} ${mini(j.vm)} <span class="muted">· ${rotuloFase(PID[j.partida], true)}, jogo ${j.numero}</span></span><span class="num">${txt(j)}</span></button>`
        : "";
    const porDur = JOGOS.slice().sort((a, b) => b.duracao - a.duracao),
      porAb = JOGOS.slice().sort(
        (a, b) => b.tot.blue.abates + b.tot.red.abates - (a.tot.blue.abates + a.tot.red.abates),
      );
    setTimeout(rankingPalpites, 0);
    $("#p-destaques").innerHTML =
      destaquesDoDia() +
      `<p class="nota" style="margin:0 0 16px">Rankings com os ${JOGOS.length} jogos já disputados neste Worlds. Bans, dano por minuto e visão vêm da Leaguepedia, que tem ${jogosLp} desses jogos registrados até agora. Clique num jogador ou time para ver mais.</p>
  <h3 style="font-size:22px;text-transform:uppercase;margin-bottom:10px">Jogadores</h3>
  <div class="ranking">${lj(
    "Mais abates",
    "",
    (x) => x.st.k,
    (v) => v,
  )}${lj("Melhor KDA", "mínimo 3 jogos", (x) => x.st.kda, n1, min3)}${lj(
    "Mais CS por minuto",
    "sem suportes",
    (x) => x.st.csm,
    n1,
    (x) => x.pl.rota !== "support",
  )}
  ${lj("Maior vantagem aos 15", "ouro sobre o rival de rota · mínimo 3 jogos", (x) => x.st.gd15, sinal, min3)}${lj(
    "Mais dano por minuto",
    "",
    (x) => x.st.dpm,
    (v) => Math.round(v),
  )}${lj("Maior participação em abates", "mínimo 3 jogos", (x) => x.st.kp, pct, min3)}
  ${lj(
    "Mais first bloods",
    "quem fez o primeiro abate do jogo",
    (x) => x.st.fbK || null,
    (v) => v,
  )}${lj(
    "Maior placar de visão",
    "média por jogo",
    (x) => x.st.visao,
    (v) => Math.round(v),
  )}</div>
  <h3 style="font-size:22px;text-transform:uppercase;margin:22px 0 10px">Por posição</h3>
  <div class="bloco-f" id="tab-pos"></div>
  <h3 style="font-size:22px;text-transform:uppercase;margin:22px 0 10px">Campeões</h3>
  <div class="ranking">${lc("Mais escolhidos", `em ${JOGOS.length} jogos`, picks, (k, v) => `${vit[k] || 0} vitórias · ${pct((vit[k] || 0) / v)} de aproveitamento`)}${jogosLp ? lc("Mais banidos", `em ${jogosLp} de ${JOGOS.length} jogos com bans registrados${W.lpTentativa ? ` · Leaguepedia consultada em ${dataHora(new Date(W.lpTentativa).toISOString())}` : ""}`, bans, (k, v) => `banido em ${pct(v / jogosLp)} dos jogos`) : ""}${jogosLp ? lc("Mais presentes", "escolhidos + banidos", pres, (k, v) => `${picks[k] || 0} escolhas e ${bans[k] || 0} bans`) : ""}</div>
  <h3 style="font-size:22px;text-transform:uppercase;margin:22px 0 10px">Times</h3>
  <div class="ranking">${lt("First blood", "% dos jogos", (s) => s.pfb, pct)}${lt("Dragões por jogo", "", (s) => s.dragJ, n1)}${lt("Abates por jogo", "", (s) => s.abJ, n1)}${lt("Vantagem média aos 15", "", (s) => s.gd15m, mil)}${lt("Arautos por jogo", "jogos registrados na Leaguepedia", (s) => (s.jogosLp ? s.arautosJ : null), n1)}${lt("Jogos mais longos", "duração média", (s) => s.durM, mmss)}</div>
  <h3 style="font-size:22px;text-transform:uppercase;margin:22px 0 10px">Ranking dos palpites</h3>
  <div class="ranking"><div class="bloco-f" id="ranking-palpites"></div></div>
  <h3 style="font-size:22px;text-transform:uppercase;margin:22px 0 10px">Jogos marcantes</h3>
  <div class="bloco-f"><div class="lista-linhas">${jm("Mais longo", porDur[0], (j) => mmss(j.duracao))}${jm("Mais curto", porDur[porDur.length - 1], (j) => mmss(j.duracao))}${jm("Mais abates", porAb[0], (j) => `${j.tot.blue.abates + j.tot.red.abates} abates`)}${jm("Menos abates", porAb[porAb.length - 1], (j) => `${j.tot.blue.abates + j.tot.red.abates} abates`)}</div></div>`;
    ligarPosicao();
  }
  function blocoBans(c, s) {
    if (!s || !s.jogosLp) return `<p class="muted" style="margin:0">Sem bans registrados ainda.</p>`;
    const top = (o) =>
      Object.entries(o)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6)
        .map(
          ([k, v]) =>
            `<span class="c">${img(camp(k).icone, "", camp(k).nome)}${esc(camp(k).nome)} <span class="muted num">${v}</span></span>`,
        )
        .join("") || '<span class="muted">nenhum</span>';
    return `<div class="muted" style="font-size:12px;margin-bottom:6px">Banidos por ${esc(c)}</div><div class="camps">${top(s.bansPor)}</div><div class="muted" style="font-size:12px;margin:10px 0 6px">Banidos contra ${esc(c)}</div><div class="camps">${top(s.bansContra)}</div><div class="muted" style="font-size:11.5px;margin-top:8px">${s.jogosLp} de ${s.jogos} jogos com bans registrados</div>`;
  }

  /* ---------- animações (GSAP) ---------- */
  // Tudo aqui é opcional: sem GSAP, ou com "reduzir movimento" ligado, o site funciona igual, só que parado.
  const G = !PARADO && window.gsap ? window.gsap : null;
  if (G && window.ScrollTrigger) G.registerPlugin(window.ScrollTrigger);
  const jaAnimado = new WeakSet();
  const SEL_ENTRA =
    ".pq,.pool-l,.dia-r,.conf,.bloco-f,.classif .t,.chances .ch,.cartao-time,.rodada h3,.ranking li,.prox,.dd,.lista-linhas .r,.duelo,.tile";
  function contar(el) {
    const txt = el.textContent.trim(),
      m = txt.match(/^([+−-]?)(\d{1,3}(?:\.\d{3})*|\d+)(?:,(\d+))?(%|k| PDL)?$/);
    if (!m) return;
    const casas = m[3] ? m[3].length : 0,
      alvo = parseFloat(m[2].replace(/\./g, "") + (m[3] ? "." + m[3] : "")),
      suf = m[4] || "",
      pre = m[1];
    const o = { v: 0 };
    G.to(o, {
      v: alvo,
      duration: 0.9,
      ease: "power2.out",
      onUpdate: () => {
        el.textContent =
          pre +
          o.v.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas }) +
          suf;
      },
      onComplete: () => {
        el.textContent = txt;
      },
    });
  }
  function animarEm(raiz) {
    if (!G || !raiz || raiz.closest?.(".player,.palpite")) return;
    const novos = [...raiz.querySelectorAll(SEL_ENTRA)].filter(
      (e) => !jaAnimado.has(e) && !e.closest(".player,.palpite") && e.offsetParent !== null,
    );
    novos.forEach((e) => jaAnimado.add(e));
    if (novos.length) {
      const vis = novos.filter((e) => e.getBoundingClientRect().top < innerHeight + 40),
        depois = novos.filter((e) => !vis.includes(e));
      G.fromTo(
        vis.slice(0, 60),
        { y: 18, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.5,
          ease: "power3.out",
          stagger: 0.025,
          clearProps: "transform,opacity",
        },
      );
      if (window.ScrollTrigger && depois.length)
        ScrollTrigger.batch(depois, {
          start: "top 95%",
          once: true,
          scroller: raiz.closest("dialog") || undefined,
          onEnter: (b) =>
            G.fromTo(
              b,
              { y: 18, opacity: 0 },
              {
                y: 0,
                opacity: 1,
                duration: 0.45,
                ease: "power3.out",
                stagger: 0.03,
                clearProps: "transform,opacity",
              },
            ),
        });
    }
    raiz.querySelectorAll(".barra i,.barra-ch>span,.votos i,.pool-b i,.lp-barra i").forEach((b) => {
      if (jaAnimado.has(b) || b.closest(".player")) return;
      jaAnimado.add(b);
      G.from(b, {
        scaleX: 0,
        transformOrigin: b.closest(".esq") ? "right center" : "left center",
        duration: 0.9,
        ease: "power3.out",
        delay: 0.15,
        clearProps: "transform",
      });
    });
    raiz.querySelectorAll(".tile b,.chances .ch .num,.dd b,.placarao .pts").forEach((el) => {
      if (jaAnimado.has(el) || el.closest(".player")) return;
      jaAnimado.add(el);
      if (el.matches(".placarao .pts")) {
        G.from(el, { scale: 0.6, opacity: 0, duration: 0.6, ease: "back.out(2)" });
        return;
      }
      if (el.childNodes.length === 1 && el.firstChild.nodeType === 3) {
        contar(el);
        return;
      }
      const n = [...el.childNodes].find((x) => x.nodeType === 3 && x.textContent.trim());
      if (!n) return;
      const s = document.createElement("span");
      s.textContent = n.textContent;
      el.replaceChild(s, n);
      contar(s);
    });
    raiz.querySelectorAll(".bloco-f svg polyline").forEach((pl) => {
      if (jaAnimado.has(pl) || pl.closest(".player")) return;
      jaAnimado.add(pl);
      let L = 0;
      try {
        L = pl.getTotalLength();
      } catch (_) {}
      if (!L) return;
      G.fromTo(
        pl,
        { strokeDasharray: L, strokeDashoffset: L },
        {
          strokeDashoffset: 0,
          duration: 1.4,
          ease: "power2.inOut",
          clearProps: "strokeDasharray,strokeDashoffset",
        },
      );
    });
  }
  function vidaTopo() {
    const h1 = $("header.topo h1");
    if (G && h1) {
      const partes = [];
      h1.childNodes.forEach((n) => {
        if (n.nodeType === 3) {
          [...n.textContent].forEach((ch) =>
            partes.push(ch === " " ? " " : `<span class="letra">${ch}</span>`),
          );
        } else
          partes.push(
            `<span class="letra-ouro">${[...n.textContent].map((ch) => `<span class="letra">${ch}</span>`).join("")}</span>`,
          );
      });
      h1.innerHTML = partes.join("");
      h1.setAttribute("aria-label", "Worlds 2026");
      G.from(h1.querySelectorAll(".letra"), {
        yPercent: 110,
        opacity: 0,
        rotate: 6,
        duration: 0.8,
        ease: "power4.out",
        stagger: 0.04,
      });
      G.from("header.topo .eyebrow,header.topo .fases span,.atualizado", {
        y: 10,
        opacity: 0,
        duration: 0.6,
        stagger: 0.05,
        delay: 0.3,
        ease: "power2.out",
      });
      G.from(".faixa .prox", {
        x: 40,
        opacity: 0,
        duration: 0.6,
        stagger: 0.06,
        delay: 0.4,
        ease: "power3.out",
        clearProps: "transform,opacity",
      });
      document.querySelectorAll(".faixa .prox").forEach((e) => jaAnimado.add(e));
    }
    // fundo do topo: pontos dourados à deriva ligados por linhas finas, como o mapa hextec das transmissões
    const cab = $("header.topo");
    if (!cab) return;
    const cv = document.createElement("canvas");
    cv.className = "fundo-topo";
    cv.setAttribute("aria-hidden", "true");
    cab.prepend(cv);
    const ctx = cv.getContext("2d");
    let W_ = 0,
      H_ = 0,
      pts = [];
    const dpr = Math.min(2, devicePixelRatio || 1);
    const medir = () => {
      const r = cab.getBoundingClientRect();
      W_ = r.width;
      H_ = r.height;
      cv.width = W_ * dpr;
      cv.height = H_ * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const n = Math.round(Math.min(70, W_ / 18));
      pts = Array.from({ length: n }, () => ({
        x: Math.random() * W_,
        y: Math.random() * H_,
        vx: (Math.random() - 0.5) * 0.25,
        vy: (Math.random() - 0.5) * 0.25,
        r: Math.random() * 1.6 + 0.6,
      }));
    };
    medir();
    addEventListener("resize", medir);
    const ouro = () =>
      getComputedStyle(document.documentElement).getPropertyValue("--gold").trim() || "#9a7425";
    let cor = ouro();
    matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", () => (cor = ouro()));
    let mx = -999,
      my = -999;
    cab.addEventListener("pointermove", (e) => {
      const r = cab.getBoundingClientRect();
      mx = e.clientX - r.left;
      my = e.clientY - r.top;
    });
    cab.addEventListener("pointerleave", () => {
      mx = my = -999;
    });
    const quadro = () => {
      ctx.clearRect(0, 0, W_, H_);
      ctx.fillStyle = cor;
      ctx.strokeStyle = cor;
      for (const p of pts) {
        if (!PARADO) {
          p.x += p.vx;
          p.y += p.vy;
          if (p.x < 0 || p.x > W_) p.vx *= -1;
          if (p.y < 0 || p.y > H_) p.vy *= -1;
        }
        const dm = Math.hypot(p.x - mx, p.y - my);
        ctx.globalAlpha = dm < 120 ? 0.9 : 0.45;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r + (dm < 120 ? 1 : 0), 0, 7);
        ctx.fill();
      }
      for (let i = 0; i < pts.length; i++)
        for (let k = i + 1; k < pts.length; k++) {
          const a = pts[i],
            b = pts[k],
            d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d < 110) {
            ctx.globalAlpha = (1 - d / 110) * 0.22;
            ctx.lineWidth = 0.7;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      ctx.globalAlpha = 1;
      if (!PARADO && !document.hidden) requestAnimationFrame(quadro);
    };
    quadro();
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden && !PARADO) requestAnimationFrame(quadro);
    });
  }
  function indicadorAbas() {
    const nav = $("#abas");
    if (!nav) return;
    const ind = document.createElement("span");
    ind.className = "ind-aba";
    nav.appendChild(ind);
    const mover = (anim) => {
      const b = nav.querySelector('[aria-selected="true"]');
      if (!b) return;
      const x = b.offsetLeft,
        w = b.offsetWidth;
      if (G && anim) G.to(ind, { x, width: w, duration: 0.45, ease: "power3.inOut" });
      else {
        ind.style.transform = `translateX(${x}px)`;
        ind.style.width = w + "px";
      }
    };
    new MutationObserver(() => mover(true)).observe(nav, {
      subtree: true,
      attributes: true,
      attributeFilter: ["aria-selected"],
    });
    addEventListener("resize", () => mover(false));
    mover(false);
    nav.classList.add("com-ind");
  }
  function ligarVida() {
    vidaTopo();
    indicadorAbas();
    if (!G) return;
    ABAS.forEach((a) => {
      const sec = $("#p-" + a);
      new MutationObserver(() => {
        if (!sec.hidden) requestAnimationFrame(() => animarEm(sec));
      }).observe(sec, { attributes: true, attributeFilter: ["hidden"], childList: true, subtree: true });
    });
    const vis = ABAS.map((a) => $("#p-" + a)).find((s) => !s.hidden);
    if (vis) animarEm(vis);
    const dt = $("#dia-topo");
    if (dt && !dt.hidden) animarEm(dt);
    const hp = $(".heroi-pi");
    if (hp) {
      G.from(hp, {
        y: 24,
        opacity: 0,
        duration: 0.7,
        delay: 0.35,
        ease: "power3.out",
        clearProps: "transform,opacity",
      });
      G.from(hp.querySelectorAll(".h-logo img,.h-foto"), {
        scale: 0.6,
        opacity: 0,
        rotate: -8,
        duration: 0.8,
        delay: 0.6,
        ease: "back.out(1.8)",
        clearProps: "all",
      });
      G.from(hp.querySelectorAll(".h-serie"), {
        y: 14,
        opacity: 0,
        stagger: 0.08,
        delay: 0.8,
        duration: 0.5,
        clearProps: "transform,opacity",
      });
    }
    let pend = false;
    new MutationObserver(() => {
      if (pend) return;
      pend = true;
      requestAnimationFrame(() => {
        pend = false;
        animarEm(folhaIn);
      });
    }).observe(folhaIn, { childList: true, subtree: true });
    const abrir = folha.showModal.bind(folha);
    folha.showModal = () => {
      abrir();
      G.fromTo(
        folha,
        { x: 80, opacity: 0.4 },
        { x: 0, opacity: 1, duration: 0.45, ease: "power3.out", clearProps: "transform,opacity" },
      );
    };
  }

  /* ---------- 2026 × história dos Mundiais (2011 a 2025, Leaguepedia) ---------- */
  const HIST = W.historia || { jogadores: {}, times: {}, campeoes: {}, recordes: {}, jogosEd: {} };
  const nrm = (s) => (s || "").toLowerCase().replace(/[^a-z0-9]/g, "");
  const N_EDICOES = Object.keys(HIST.jogosEd || {}).length || 15;
  // presença média do campeão nas edições anteriores, contando zero nas que ele não apareceu
  function presHist(k) {
    const H = HIST.campeoes?.[k]?.ed;
    if (!HIST.campeoes || !Object.keys(HIST.campeoes).length) return null;
    if (!H) return 0;
    return H.reduce((s, e) => s + (e[3] || 0), 0) / 100 / N_EDICOES;
  }
  const chipsEd = (lst, agora) =>
    `<div class="edicoes">${lst.map(([a, t, v]) => `<span class="ed ${t ? "top" : ""}" title="${esc(v.titulo || "")}"><b>${a}</b><small>${esc(t || v.txt)}</small></span>`).join("")}${agora ? `<span class="ed agora"><b>2026</b><small>${agora}</small></span>` : ""}</div>`;
  function blocoHistTime(c) {
    const h = HIST.times?.[c];
    if (!h) return "";
    const s = statsTime(c);
    const agora = s ? `${s.v}V ${s.jogos - s.v}D até aqui` : "estreia em breve";
    if (!h.participacoes)
      return `<div class="bloco-f"><h3>Nos Mundiais <small>2011 a 2025</small></h3><p style="margin:0">Primeira participação de ${esc(nomeT(c))} num Mundial.</p>${chipsEd([], agora)}</div>`;
    return `<div class="bloco-f"><h3>Nos Mundiais <small>2011 a 2025, segundo a Leaguepedia</small></h3><div class="tiles">${tile(h.participacoes, h.participacoes === 1 ? "participação" : "participações")}${tile(h.titulos, h.titulos === 1 ? "título" : "títulos")}${tile(h.finais, h.finais === 1 ? "final" : "finais")}${tile(`${h.vitorias}V ${h.jogos - h.vitorias}D`, "em jogos")}</div>
    ${chipsEd(
      h.ed.map(([a, n, jg, v, r]) => [
        a,
        r,
        { txt: `${v}V ${jg - v}D`, titulo: `${n || ""} · ${v} vitórias em ${jg} jogos` },
      ]),
      agora,
    )}</div>`;
  }
  function blocoHistJogador(pl, st) {
    const h = HIST.jogadores?.[nrm(pl.nick)];
    if (!h) return "";
    const m = h.m || {};
    if (m.estreante_2026 || !m.jogos)
      return h.historia
        ? `<div class="bloco-f"><h3>Carreira em Mundiais</h3><p class="historia" style="margin:0">${esc(h.historia)}</p></div>`
        : "";
    const k26 = st ? st.k : 0,
      j26 = st ? st.jogos : 0,
      v26 = st ? st.v : 0,
      tot = (m.abates || 0) + k26;
    // posição entre os que mais abateram na história, somando os abates deste ano
    let rec = "";
    const L = (HIST.recordes?.jogadores_mais_abates || []).map((r) => ({
      n: r.jogador,
      a: r.abates + (nrm(r.jogador) === nrm(pl.nick) ? k26 : 0),
    }));
    if (L.length) {
      if (!L.some((r) => nrm(r.n) === nrm(pl.nick))) L.push({ n: pl.nick, a: tot });
      L.sort((x, y) => y.a - x.a);
      const pos = L.findIndex((r) => nrm(r.n) === nrm(pl.nick));
      if (pos === 0)
        rec = `É quem mais abateu na história do Worlds: ${tot} abates somando 2026${L[1] ? `, ${tot - L[1].a} à frente de ${esc(L[1].n)}` : ""}.`;
      else if (pos > 0 && pos < 10)
        rec = `É o ${pos + 1}º que mais abateu na história do Worlds, com ${tot} abates somando 2026. Faltam ${L[pos - 1].a - tot + 1} para passar ${esc(L[pos - 1].n)}.`;
    }
    return `<div class="bloco-f"><h3>Carreira em Mundiais <small>2011 a 2025, mais os jogos de 2026</small></h3>${h.historia ? `<p class="historia">${esc(h.historia)}</p>` : ""}
    <div class="tiles">${tile((m.participacoes_ate_2025 || 0) + 1, "Mundiais, com 2026")}${tile((m.jogos || 0) + j26, "jogos")}${tile((m.vitorias || 0) + v26, "vitórias")}${tile(tot, "abates")}${tile(m.titulos?.length || 0, (m.titulos?.length || 0) === 1 ? "título" : "títulos")}</div>
    ${rec ? `<p class="muted" style="font-size:13px;margin:10px 0 0">${rec}</p>` : ""}
    ${chipsEd(
      h.ed.map(([a, t, jg, v, kd, r, cs]) => [
        a,
        /campe|vice|semi/i.test(r || "") ? r : "",
        {
          txt: `${v}V ${jg - v}D`,
          titulo: `${t || ""} · KDA ${kd ?? "–"}${cs.length ? " · " + cs.join(", ") : ""}`,
        },
      ]),
      st ? `${v26}V ${j26 - v26}D até aqui` : "",
    )}</div>`;
  }

  /* ---------- página de campeão ---------- */
  const CAMP_NOME = {};
  for (const [k, c] of Object.entries(W.campeoes || {})) CAMP_NOME[c.nome] = k;
  function abrirCampeao(k) {
    const c = camp(k);
    if (!c) return;
    const usos = [];
    for (const j of JOGOS)
      for (const x of j.jog) if (x.campeao === k) usos.push({ j, x, venceu: j.venc === x.time });
    let bans = 0,
      jl = 0;
    for (const j of JOGOS)
      if (j.lp) {
        jl++;
        if ([...j.lp.bans.blue, ...j.lp.bans.red].includes(k)) bans++;
      }
    const v = usos.filter((u) => u.venceu).length,
      K = usos.reduce((s, u) => s + u.x.k, 0),
      D = usos.reduce((s, u) => s + u.x.d, 0),
      A = usos.reduce((s, u) => s + u.x.a, 0);
    const pres = JOGOS.length ? usos.length / JOGOS.length + (jl ? bans / jl : 0) : 0; // mesmo cálculo da aba Meta: bans só sobre os jogos com bans registrados
    const H = HIST.campeoes?.[k]?.ed || [],
      hp = presHist(k);
    const tp = H.reduce((s, e) => s + e[1], 0),
      tb = H.reduce((s, e) => s + e[2], 0),
      tv = H.reduce((s, e) => s + e[4], 0);
    const anos = Object.keys(HIST.jogosEd || {})
      .map(Number)
      .sort((a, b) => a - b);
    const porAno = Object.fromEntries(H.map((e) => [e[0], e]));
    const mx = Math.max(1, ...H.map((e) => e[3] || 0), pres * 100);
    const graf = anos.length
      ? `<div class="hist-camp">${[...anos, 2026]
          .map((a) => {
            const p = a === 2026 ? pres * 100 : porAno[a]?.[3] || 0;
            return `<div class="hc ${a === 2026 ? "agora" : ""}" title="${a}: presença ${Math.round(p)}%"><i style="height:${Math.max(2, (p / mx) * 100)}%"></i><small>${String(a).slice(2)}</small></div>`;
          })
          .join("")}</div>`
      : "";
    const lista = usos
      .slice()
      .sort((a, b) => (PID[b.j.partida]?.inicio || "").localeCompare(PID[a.j.partida]?.inicio || ""))
      .map((u) => {
        const adv = u.j.lados[outro(u.x.lado)];
        return `<div class="r clic" data-partida="${u.j.partida}" data-k="${jogosDe(u.j.partida).indexOf(u.j)}" tabindex="0"><span class="res ${u.venceu ? "v" : "d"}">${u.venceu ? "V" : "D"}</span><span><b>${esc(u.x.nick || "")}</b> <small class="muted">${mini(u.x.time)} contra ${esc(adv)}</small></span><span class="num">${u.x.k}/${u.x.d}/${u.x.a}</span></div>`;
      })
      .join("");
    abrirFolha(`<div class="perfil camp-perfil">${img(c.icone, "f", c.nome)}<div><div class="eyebrow">Campeão</div><h2>${esc(c.nome)}</h2><div class="muted">${usos.length ? `${usos.length} ${usos.length === 1 ? "escolha" : "escolhas"} neste Worlds` : "Ainda não escolhido neste Worlds"}</div></div></div>
    <div class="bloco-f"><h3>Neste Worlds</h3><div class="tiles">${tile(pct(pres), "presença")}${tile(usos.length, "escolhas")}${tile(usos.length ? pct(v / usos.length) : "–", "aproveitamento")}${tile(jl ? bans : "–", jl ? `bans em ${jl} jogos` : "bans")}${tile(usos.length ? n1((K + A) / Math.max(1, D)) : "–", "KDA")}</div></div>
    ${usos.length ? `<div class="bloco-f"><h3>Quem jogou <small>toque para abrir o jogo</small></h3><div class="lista-linhas">${lista}</div></div>` : ""}
    ${
      anos.length
        ? `<div class="bloco-f"><h3>Nos Mundiais anteriores <small>presença por edição, escolhas + bans</small></h3>${graf}
      <p style="margin:10px 0 0;font-size:14px">${H.length ? `Apareceu em ${H.length} dos ${anos.length} Mundiais anteriores, com ${tp} escolhas, ${tb} bans e ${tp ? pct(tv / tp) : "–"} de aproveitamento. A presença média na história é de ${pct(hp)}; em 2026 está em ${pct(pres)}.` : `Nunca apareceu num Mundial antes de 2026.`}</p></div>`
        : ""
    }`);
  }

  /* ---------- busca única ---------- */
  function indiceBusca() {
    const L = [];
    for (const [c, t] of Object.entries(TIMES))
      L.push({ t: "time", id: c, nome: t.nome, sub: c, chave: nrm(t.nome + " " + c), img: t.logo });
    for (const [c, t] of Object.entries(TIMES))
      for (const pl of t.jogadores)
        L.push({
          t: "jogador",
          id: pl.id,
          nome: pl.nick,
          sub: `${c} · ${ROTA_PT[pl.rota] || ""}`,
          chave: nrm(pl.nick + " " + (pl.nome || "")),
          img: pl.foto || FOTO[pl.id],
        });
    const usados = new Set(JOGOS.flatMap((j) => j.jog.map((x) => x.campeao)));
    for (const [k, c] of Object.entries(W.campeoes || {}))
      L.push({
        t: "campeao",
        id: k,
        nome: c.nome,
        sub: usados.has(k) ? "campeão · jogado em 2026" : "campeão",
        chave: nrm(c.nome + " " + k),
        img: c.icone,
        peso: usados.has(k) ? 1 : 0,
      });
    return L;
  }
  let _idx = null;
  function buscar(q) {
    q = nrm(q);
    if (!q) return [];
    _idx = _idx || indiceBusca();
    return _idx
      .map((x) => ({ x, p: x.chave.startsWith(q) ? 3 : x.chave.includes(q) ? 1 : 0 }))
      .filter((r) => r.p)
      .sort(
        (a, b) =>
          b.p - a.p ||
          (b.x.peso || 0) - (a.x.peso || 0) ||
          (a.x.t === "campeao") - (b.x.t === "campeao") ||
          a.x.nome.localeCompare(b.x.nome),
      )
      .slice(0, 8)
      .map((r) => r.x);
  }
  function abrirResultado(x) {
    if (x.t === "time") navegar(() => abrirTime(x.id));
    else if (x.t === "jogador") navegar(() => abrirJogador(x.id));
    else navegar(() => abrirCampeao(x.id));
  }
  function ligarBusca() {
    const inp = $("#busca"),
      lst = $("#busca-res");
    if (!inp) return;
    let res = [],
      sel = 0;
    const desenhar = () => {
      lst.hidden = !res.length;
      inp.setAttribute("aria-expanded", !!res.length);
      lst.innerHTML = res
        .map(
          (x, i) =>
            `<li role="option" id="br-${i}" aria-selected="${i === sel}" data-i="${i}">${x.img ? `<img src="${x.img}" alt="">` : `<span class="sem-foto">${esc(x.nome[0])}</span>`}<span><b>${esc(x.nome)}</b><small>${esc(x.t === "time" ? "time · " + x.sub : x.t === "jogador" ? "jogador · " + x.sub : x.sub)}</small></span></li>`,
        )
        .join("");
      inp.setAttribute("aria-activedescendant", res.length ? "br-" + sel : "");
    };
    inp.addEventListener("input", () => {
      res = buscar(inp.value);
      sel = 0;
      desenhar();
    });
    inp.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") {
        sel = Math.min(res.length - 1, sel + 1);
        desenhar();
        e.preventDefault();
      } else if (e.key === "ArrowUp") {
        sel = Math.max(0, sel - 1);
        desenhar();
        e.preventDefault();
      } else if (e.key === "Enter" && res[sel]) {
        abrirResultado(res[sel]);
        inp.value = "";
        res = [];
        desenhar();
        inp.blur();
      } else if (e.key === "Escape") {
        inp.value = "";
        res = [];
        desenhar();
        inp.blur();
      }
    });
    lst.addEventListener("mousedown", (e) => {
      const li = e.target.closest("li");
      if (!li) return;
      e.preventDefault();
      abrirResultado(res[+li.dataset.i]);
      inp.value = "";
      res = [];
      desenhar();
    });
    inp.addEventListener("blur", () =>
      setTimeout(() => {
        res = [];
        desenhar();
      }, 150),
    );
    document.addEventListener("keydown", (e) => {
      if (
        e.key === "/" &&
        !/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName || "") &&
        !folha.open
      ) {
        e.preventDefault();
        inp.focus();
      }
    });
  }

  /* ---------- versão em inglês da interface ---------- */
  // Traduz rótulos, títulos e botões; textos gerados (histórias, narração) continuam em português.
  const EN = {
    "A definir": "TBD",
    "Na disputa": "In contention",
    Encerrado: "Final",
    "Ao vivo": "Live",
    "Mais abates": "Most kills",
    "Melhor KDA": "Best KDA",
    "Chave superior · rodada 1": "Upper bracket · round 1",
    "Chave inferior · rodada 1": "Lower bracket · round 1",
    "Final da chave superior": "Upper bracket final",
    "Final da chave inferior": "Lower bracket final",
    "Final do Play-In": "Play-In final",
    "Modo sem spoiler ligado: esta aba mostra resultados.":
      "Spoiler-free mode is on: this tab shows results.",
    Desligar: "Turn off",
    "First blood": "First blood",
    Vitórias: "Wins",
    "Fase Suíça": "Swiss Stage",
    Quartas: "Quarterfinals",
    Semis: "Semis",
    Final: "Final",
    "Destaques do dia": "Highlights of the day",
    "Jogo mais longo": "Longest game",
    "Maior virada": "Biggest comeback",
    Times: "Teams",
    "mínimo 3 jogos": "min. 3 games",
    Jogos: "Games",
    Campeões: "Champions",
    "Abates por jogo": "Kills per game",
    Campeão: "Champion",
    "Primeiro dragão": "First dragon",
    "Primeira torre": "First tower",
    "Primeiro Barão": "First Baron",
    Bans: "Bans",
    Jogadores: "Players",
    Topo: "Top",
    Selva: "Jungle",
    Meio: "Mid",
    Atirador: "Bot",
    Suporte: "Support",
    Jogador: "Player",
    Time: "Team",
    Dragões: "Dragons",
    "Ouro@15": "Gold@15",
    "Ouro@15 médio": "Avg gold@15",
    "Participação em abates": "Kill participation",
    "Dano/min": "Damage/min",
    "First bloods": "First bloods",
    Torres: "Towers",
    Barões: "Barons",
    Arautos: "Heralds",
    Vastilarvas: "Voidgrubs",
    Abates: "Kills",
    Ouro: "Gold",
    Visão: "Vision",
    "Itens finais": "Final items",
    "Sem spoiler": "No spoilers",
    "Sem spoiler: ligado": "No spoilers: on",
    "Próximos jogos · horário de Brasília": "Upcoming games · Brasília time",
    "horário de Brasília": "Brasília time",
    "Como foi o Play-In ›": "How the Play-In went ›",
    "Ver o time": "See the team",
    "Mata-mata": "Knockouts",
    Destaques: "Highlights",
    Meta: "Meta",
    Comparar: "Compare",
    "Rodada 1": "Round 1",
    "Rodada 2": "Round 2",
    "Rodada 3": "Round 3",
    "Rodada 4": "Round 4",
    "Rodada 5": "Round 5",
    "Todos com 0-0": "Everyone at 0-0",
    "Grupos 1-0 e 0-1": "1-0 and 0-1 pools",
    "Grupos 2-0, 1-1 e 0-2": "2-0, 1-1 and 0-2 pools",
    "Grupos 2-1 e 1-2": "2-1 and 1-2 pools",
    "Grupo 2-2": "2-2 pool",
    "Campanhas na Suíça": "Swiss records",
    "Chance de classificação": "Chance to advance",
    Classifica: "Advances",
    "Cai 0-3": "Out 0-3",
    Semifinais: "Semifinals",
    "Mais CS por minuto": "Most CS per minute",
    "sem suportes": "no supports",
    "Maior vantagem aos 15": "Biggest lead at 15",
    "ouro sobre o rival de rota": "gold over lane opponent",
    "Mais dano por minuto": "Most damage per minute",
    "Maior participação em abates": "Highest kill participation",
    "Mais first bloods": "Most first bloods",
    "quem fez o primeiro abate do jogo": "who got the game's first kill",
    "Maior placar de visão": "Highest vision score",
    "média por jogo": "average per game",
    "Por posição": "By position",
    Todas: "All",
    "Ouro/min": "Gold/min",
    "% do ouro": "Gold share",
    "CS dif. @10": "CS diff @10",
    "Sentinelas/min": "Wards/min",
    "Mais escolhidos": "Most picked",
    "Mais banidos": "Most banned",
    "Mais presentes": "Highest presence",
    "escolhidos + banidos": "picked + banned",
    "% dos jogos": "% of games",
    "Dragões por jogo": "Dragons per game",
    "Vantagem média aos 15": "Avg lead at 15",
    "Arautos por jogo": "Heralds per game",
    "jogos registrados na Leaguepedia": "games recorded on Leaguepedia",
    "Jogos mais longos": "Longest games",
    "duração média": "average length",
    "Ranking dos palpites": "Prediction leaderboard",
    "Jogos marcantes": "Notable games",
    "Mais longo": "Longest",
    "Mais curto": "Shortest",
    "Menos abates": "Fewest kills",
    "Vitórias do lado azul": "Blue side wins",
    "Vitórias do lado vermelho": "Red side wins",
    "Duração média": "Average length",
    "Campeões escolhidos": "Champions picked",
    "Escolhidos ou banidos": "Picked or banned",
    "O que mais decide jogo": "What decides games",
    "quem conseguiu primeiro e venceu": "got it first and won",
    "À frente aos 15 min": "Ahead at 15 min",
    Infernal: "Infernal",
    Quimtec: "Chemtech",
    Vento: "Cloud",
    Montanha: "Mountain",
    Oceano: "Ocean",
    Hextec: "Hextech",
    Ancião: "Elder",
    Presença: "Presence",
    Escolhas: "Picks",
    "Aproveit.": "Win rate",
    "Média histórica": "Historical avg",
    "Mortes por jogo": "Deaths per game",
    "Assistências por jogo": "Assists per game",
    "CS por minuto": "CS per minute",
    "Dano por minuto": "Damage per minute",
    "% do dano do time": "Team damage share",
    "Visão por jogo": "Vision per game",
    "Buscar jogador, time ou campeão  /": "Search player, team or champion  /",
    "Buscar jogador, time ou campeão": "Search player, team or champion",
    Posição: "Position",
    "Primeiro jogador": "First player",
    "Segundo jogador": "Second player",
    "% do dano": "Damage share",
    "Particip.": "KP",
    "O jogo dele, lance a lance": "Their game, play by play",
    Tudo: "All",
    "Abates e mortes": "Kills and deaths",
    Objetivos: "Objectives",
    "Ouro na rota": "Lane gold",
    "Ver o jogo completo, com o replay narrado ›": "See the full game, with the narrated replay ›",
    "Ver o jogo completo ›": "See the full game ›",
    "Filtrar acontecimentos": "Filter events",
    "Copiar link": "Copy link",
    "Link copiado": "Link copied",
    "Modo sem spoiler: os resultados desta tela estão escondidos.":
      "Spoiler-free mode: results on this screen are hidden.",
    "Mostrar resultados": "Show results",
    Fechar: "Close",
    "‹ Voltar": "‹ Back",
    "sem jogos ainda": "no games yet",
    Semifinal: "Semifinal",
    "▶ Ver o VOD sem spoiler": "▶ Watch the VOD spoiler-free",
    "Resumo da série": "Series summary",
    "Assistir ao jogo narrado": "Watch the narrated game",
    "▶ Assistir ao VOD oficial em português": "▶ Watch the official VOD (Portuguese)",
    "▶ Assistir ao VOD oficial (em inglês)": "▶ Watch the official VOD (English)",
    "no YouTube do LoL Esports · o início do jogo no vídeo é aproximado":
      "on LoL Esports' YouTube · the game start in the video is approximate",
    "ver na transmissão": "see on stream",
    "Vantagem aos 15 min": "Lead at 15 min",
    "Ouro ao longo do jogo": "Gold over time",
    "Chance de vitória": "Win chance",
    "% dano": "Damage %",
    Elenco: "Roster",
    "Próximo jogo": "Next game",
    "No torneio": "In the tournament",
    "Campeões jogados": "Champions played",
    "Séries disputadas": "Series played",
    "Nos Mundiais": "At Worlds",
    "Carreira em Mundiais": "Worlds career",
    "Neste Worlds": "At this Worlds",
    "Quem jogou": "Who played it",
    "Nos Mundiais anteriores": "At past Worlds",
    "Jornada no Worlds": "Worlds journey",
    "Números no torneio": "Tournament stats",
    "Campeões no torneio": "Champions in the tournament",
    "Solo queue": "Solo queue",
    "Últimas partidas": "Recent games",
    Maestria: "Mastery",
    "Campeões na solo queue": "Solo queue champions",
    "Estreia no Worlds 2026": "Worlds 2026 debut",
    "Neste jogo": "This game",
    Curiosidades: "Fun facts",
    Prévia: "Preview",
    "Assistir à prévia narrada": "Watch the narrated preview",
    "Destaque da série": "Series standout",
    Voz: "Voice",
    "▶ Play": "▶ Play",
    "❚❚ Pausar": "❚❚ Pause",
    "Lance anterior": "Previous play",
    "Próximo lance": "Next play",
    "Tocar ou pausar": "Play or pause",
    "Narração por voz": "Voice narration",
    "Voz da narração": "Narration voice",
    participação: "appearance",
    participações: "appearances",
    título: "title",
    títulos: "titles",
    finais: "finals",
    "em jogos": "in games",
    jogos: "games",
    vitórias: "wins",
    abates: "kills",
    presença: "presence",
    escolhas: "picks",
    aproveitamento: "win rate",
    "Grão-Mestre": "Grandmaster",
    Mestre: "Master",
    Desafiante: "Challenger",
    Diamante: "Diamond",
    Esmeralda: "Emerald",
    Platina: "Platinum",
    "na temporada": "this season",
    "Mundiais, com 2026": "Worlds, incl. 2026",
    "Campeão mundial": "World champion",
    Vice: "Runner-up",
    "K/D/A total": "Total K/D/A",
    Agenda: "Schedule",
    "Adicionar ao Google Agenda": "Add to Google Calendar",
  };
  const SEM = { seg: "Mon", ter: "Tue", qua: "Wed", qui: "Thu", sex: "Fri", sáb: "Sat", dom: "Sun" };
  const EN_RE = [
    [
      /^(seg|ter|qua|qui|sex|sáb|dom), (\d\d)\/(\d\d) · (\d\d:\d\d)$/,
      (m, d, a, b, h) => `${SEM[d]}, ${b}/${a} · ${h}`,
    ],
    [
      /^Dados de (seg|ter|qua|qui|sex|sáb|dom), (\d\d)\/(\d\d) · (\d\d:\d\d) \(Brasília\)$/,
      (m, d, a, b, h) => `Data from ${SEM[d]}, ${b}/${a} · ${h} (Brasília time)`,
    ],
    [/^(.+) derrubou uma torre de (.+)$/, "$1 took a $2 tower"],
    [/^(.+) derrubou uma torre$/, "$1 took a tower"],
    [/^(.+) derrubou um inibidor$/, "$1 took an inhibitor"],
    [/^(.+) pegou o dragão (.+)$/, "$1 took the $2 dragon"],
    [/^(.+) pegou o Barão$/, "$1 took Baron"],
    [/^Abateu (.+), o rival de rota$/, "Killed $1, the lane opponent"],
    [/^Abateu (.+)$/, "Killed $1"],
    [/^Morreu para (.+)$/, "Died to $1"],
    [/^Aos (\d+) min, ouro empatado com (.+)$/, "At $1 min, even gold with $2"],
    [/^Jogo (\d+)$/, "Game $1"],
    [/^Suíça R(\d)$/, "Swiss R$1"],
    [/^Ver (.+)$/, "See $1"],
    [/^(\S+) de (.+) \(([A-Z0-9]+)\)$/, "$1 on $2 ($3)"],
    [/^(\d+) jogos?$/, (m, n) => `${n} game${n === "1" ? "" : "s"}`],
    [/^(\d+) jogos$/, "$1 games"],
    [/^em (\d+) jogos$/, "in $1 games"],
    [/^banido em (.+) dos jogos$/, "banned in $1 of games"],
    [
      /^(.+) · (Topo|Selva|Meio|Atirador|Suporte) · (\d+) jogos?$/,
      (m, t, r, n) => `${t} · ${EN[r]} · ${n} game${n === "1" ? "" : "s"}`,
    ],
    [/^(.+) · (Topo|Selva|Meio|Atirador|Suporte)$/, (m, t, r) => `${t} · ${EN[r]}`],
    [/^(.+), vitória de (.+)$/, "$1, won by $2"],
    [/^(.+) · caiu no Play-In$/, "$1 · out in the Play-In"],
    [/^Campeões · (.+)$/, "Champions · $1"],
    [/^Ouro contra (.+), com abates e mortes marcados$/, "Gold vs $1, with kills and deaths marked"],
    [/^(\d+)% de vitórias$/, "$1% wins"],
  ];
  let LANG = "pt";
  try {
    LANG = localStorage.getItem("lang") === "en" ? "en" : "pt";
  } catch (_) {}
  function trTexto(t) {
    const s = t.trim();
    if (!s) return t;
    let r = EN[s];
    if (r == null)
      for (const [re, f] of EN_RE) {
        if (re.test(s)) {
          r = s.replace(re, f);
          break;
        }
      }
    return r == null ? t : t.replace(s, r);
  }
  function traduzir(raiz) {
    if (LANG !== "en" || !raiz) return;
    const w = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT);
    let n;
    const L = [];
    while ((n = w.nextNode()))
      if (!n.parentElement?.closest("script,style,[data-leg],.lista-ev,.historia,.historia-serie,.nota"))
        L.push(n);
    for (const n of L) {
      const t = trTexto(n.textContent);
      if (t !== n.textContent) n.textContent = t;
    }
    (raiz.querySelectorAll ? raiz : document)
      .querySelectorAll("[placeholder],[title],[aria-label]")
      .forEach((e) =>
        ["placeholder", "title", "aria-label"].forEach((a) => {
          const v = e.getAttribute(a);
          if (v) {
            const t = trTexto(v);
            if (t !== v) e.setAttribute(a, t);
          }
        }),
      );
  }
  function ligarIdioma() {
    if (!document.documentElement.lang) document.documentElement.lang = "pt-BR";
    const bt = $("#bt-lang");
    if (bt) {
      bt.textContent = LANG === "en" ? "PT" : "EN";
      bt.title =
        LANG === "en" ? "Ver em português" : "View in English (generated stories stay in Portuguese)";
      bt.onclick = () => {
        try {
          localStorage.setItem("lang", LANG === "en" ? "pt" : "en");
        } catch (_) {}
        location.reload();
      };
    }
    if (LANG !== "en") return;
    document.documentElement.lang = "en";
    traduzir(document.body);
    let fila = new Set(),
      pend = false;
    new MutationObserver((ms) => {
      for (const m of ms) m.addedNodes.forEach((x) => fila.add(x.nodeType === 3 ? x.parentElement : x));
      if (pend) return;
      pend = true;
      requestAnimationFrame(() => {
        pend = false;
        const f = [...fila];
        fila.clear();
        f.forEach((x) => x && x.isConnected && traduzir(x));
      });
    }).observe(document.body, { childList: true, subtree: true });
  }

  /* ---------- navegação ---------- */
  const ABAS = ["playin", "suica", "matamata", "destaques", "meta", "comparar", "times"];
  function aba(nome) {
    ABAS.forEach((a) => {
      $("#p-" + a).hidden = a !== nome;
      $(`#abas [data-aba="${a}"]`).setAttribute("aria-selected", a === nome);
    });
    try {
      localStorage.setItem("aba", nome);
    } catch (_) {}
  }
  document.addEventListener("click", (e) => {
    const cp = e.target.closest("[data-camp]");
    if (cp) {
      navegar(() => abrirCampeao(cp.dataset.camp));
      return;
    }
    if (
      e.target.tagName === "IMG" &&
      CAMP_NOME[e.target.alt] &&
      !e.target.closest("button,a,[data-jogador],[data-partida],[data-time],.clic,canvas")
    ) {
      navegar(() => abrirCampeao(CAMP_NOME[e.target.alt]));
      return;
    }
    const ab = e.target.closest("[data-aba]");
    if (ab) {
      aba(ab.dataset.aba);
      if (ab.hasAttribute("data-rolar")) $("#abas").scrollIntoView({ behavior: PARADO ? "auto" : "smooth" });
      return;
    }
    const jg = e.target.closest("[data-jogador]");
    if (jg) {
      const id = jg.dataset.jogador,
        jo = jg.dataset.jogo;
      navegar(() => abrirJogador(id, jo));
      return;
    }
    const pa = e.target.closest("[data-partida]");
    if (pa) {
      const id = pa.dataset.partida,
        k = pa.dataset.k;
      navegar(() => abrirPartida(id, k ? +k : 0));
      return;
    }
    const ti = e.target.closest("[data-time]");
    if (ti) {
      const c = ti.dataset.time;
      navegar(() => abrirTime(c));
    }
  });
  topo();
  $("#heroi-topo").innerHTML = heroiPlayin();
  {
    const ult = JOGOS.map((j) => PID[j.partida]?.inicio)
      .filter(Boolean)
      .sort()
      .pop();
    if (ult && Date.now() - new Date(ult) < 36 * 36e5) {
      const el = $("#dia-topo");
      el.innerHTML = destaquesDoDia();
      el.hidden = false;
    }
  }
  painelPlayin();
  painelSuica();
  painelMata();
  painelDestaques();
  painelMeta();
  painelComparar();
  painelTimes();
  aplicarSpoiler();
  ligarBusca();
  ligarIdioma();
  ["p-destaques", "p-meta", "p-comparar"].forEach((id) =>
    new MutationObserver(() => {
      const el = document.getElementById(id);
      if (!el.querySelector(":scope>.sp-nota")) aplicarSpoiler();
    }).observe(document.getElementById(id), { childList: true }),
  );
  const h = (location.hash || "").slice(1);
  let inicial = ABAS.includes(h) ? h : null;
  if (!inicial) {
    try {
      inicial = localStorage.getItem("aba");
    } catch (_) {}
  }
  if (!ABAS.includes(inicial)) {
    const d = new Date().toISOString();
    inicial = d < "2026-10-23T17" ? "playin" : d < "2026-11-01" ? "suica" : "matamata";
  }
  aba(inicial);
  function rotearHash(h) {
    if (/^p\d+$/.test(h)) navegar(() => abrirPartida(h.slice(1)));
    else if (h.startsWith("time-")) {
      const c = Object.keys(TIMES).find(
        (x) => x.toLowerCase() === decodeURIComponent(h.slice(5)).toLowerCase(),
      );
      if (c) navegar(() => abrirTime(c));
    } else if (h.startsWith("jogador-")) {
      const n = decodeURIComponent(h.slice(8)).toLowerCase();
      let id = null;
      for (const t of Object.values(TIMES))
        for (const p of t.jogadores) if (!id && slug(p.nick).toLowerCase() === n) id = p.id;
      if (id) navegar(() => abrirJogador(id));
    } else if (ABAS.includes(h)) {
      if (folha.open) folha.close();
      aba(h);
    }
  }
  rotearHash(h);
  // link colado com a página já aberta (marcar() usa replaceState, que não dispara este evento)
  addEventListener("hashchange", () => rotearHash((location.hash || "").slice(1)));
  contagens();
  setInterval(contagens, 1000);
  ligarVida();
})();
