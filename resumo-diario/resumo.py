#!/usr/bin/env python3
"""Resumo diário do Worlds 2026 a partir da API do LoL Esports (não oficial).

Uso: python3 resumo.py [AAAA-MM-DD]   (data em horário de Brasília; padrão = ontem)
Imprime o resumo em Markdown. Sem jogos concluídos na data, imprime "SEM_JOGOS"
na primeira linha, seguido dos próximos jogos.
"""
import datetime as dt, json, os, sys, urllib.request, urllib.error

KEY = os.environ.get("LOLESPORTS_API_KEY", "0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z")  # chave pública do próprio lolesports.com
API = "https://esports-api.lolesports.com/persisted/gw"
FEED = "https://feed.lolesports.com/livestats/v1"
WORLDS = "98767975604431411"
BRT = dt.timezone(dt.timedelta(hours=-3))


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        if e.code in (204, 404):
            return None
        raise


def api(path):
    return get(f"{API}/{path}", {"x-api-key": KEY})["data"]


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def iso10(t):
    t = t.astimezone(dt.timezone.utc).replace(microsecond=0)
    return t.replace(second=t.second // 10 * 10).strftime("%Y-%m-%dT%H:%M:%SZ")


def window(game_id, at=None):
    q = f"?startingTime={iso10(at)}" if at else ""
    w = get(f"{FEED}/window/{game_id}{q}")
    return w if w and w.get("frames") else None


def game_stats(game_id):
    first = window(game_id)
    if not first:
        return None
    start = ts(first["frames"][0]["rfc460Timestamp"])
    final = window(game_id, start + dt.timedelta(minutes=100))
    if not final or final["frames"][-1]["gameState"] != "finished":
        return None
    # busca binária (passos de 10 s) do primeiro quadro "finished" para estimar a duração
    lo, hi = 0, 6000
    while hi - lo > 10:
        mid = (lo + hi) // 2
        w = window(game_id, start + dt.timedelta(seconds=mid))
        if w and w["frames"][-1]["gameState"] == "finished":
            hi = mid
        else:
            lo = mid
    md = first["gameMetadata"]
    f = final["frames"][-1]
    return {"meta": md, "frame": f, "dur": hi}


def mmss(s):
    return f"{s // 60}:{s % 60:02d}"


def series_block(ev):
    m = ev["match"]
    a, b = m["teams"]
    det = api(f"getEventDetails?hl=pt-BR&id={m['id']}")["event"]["match"]
    tid = {t["id"]: t["code"] for t in det["teams"]}
    bo = m["strategy"]["count"]
    win = a if a["result"]["outcome"] == "win" else b
    lose = b if win is a else a
    hora = ts(ev["startTime"]).astimezone(BRT).strftime("%H:%M")
    head = f"**{win['code']} {win['result']['gameWins']}–{lose['result']['gameWins']} {lose['code']}** (Bo{bo}, {hora})"
    lines, players = [], {}
    for g in det["games"]:
        if g["state"] != "completed":
            continue
        st = game_stats(g["id"])
        if not st:
            lines.append(f"  - Jogo {g['number']}: estatísticas indisponíveis")
            continue
        md, f = st["meta"], st["frame"]
        sides = {}
        for side in ("blue", "red"):
            tm, fr = md[f"{side}TeamMetadata"], f[f"{side}Team"]
            code = tid.get(tm["esportsTeamId"], "?")
            sides[side] = (code, fr)
            for pm, pf in zip(tm["participantMetadata"], fr["participants"]):
                p = players.setdefault(pm["summonerName"], {"k": 0, "d": 0, "a": 0, "champs": [], "team": code})
                p["k"] += pf["kills"]; p["d"] += pf["deaths"]; p["a"] += pf["assists"]
                p["champs"].append(pm["championId"])
        (bc, bf), (rc, rf) = sides["blue"], sides["red"]
        gw = bc if bf["inhibitors"] > rf["inhibitors"] or (bf["inhibitors"] == rf["inhibitors"] and bf["towers"] >= rf["towers"]) else rc
        wf, lf = (bf, rf) if gw == bc else (rf, bf)
        gold = (wf["totalGold"] - lf["totalGold"]) / 1000
        lines.append(
            f"  - Jogo {g['number']}: vitória **{gw}** em {mmss(st['dur'])} · abates {bf['totalKills']}–{rf['totalKills']} ({bc} azul × {rc} vermelho)"
            f" · ouro {gold:+.1f}k · barões {wf['barons']}–{lf['barons']} · dragões {len(wf['dragons'])}–{len(lf['dragons'])}")
    dest = ""
    if players:
        def kda(p):
            return (p["k"] + p["a"]) / max(1, p["d"])
        top = max((p for p in players.items() if p[1]["team"] == win["code"]), key=lambda x: (kda(x[1]), x[1]["k"]), default=None)
        if top:
            n, p = top
            dest = f"  - Destaque: **{n}** ({', '.join(dict.fromkeys(p['champs']))}) {p['k']}/{p['d']}/{p['a']}, KDA {kda(p):.1f}"
    rec = ""
    if a.get("record"):
        rec = f"  - Campanha: {a['code']} {a['record']['wins']}-{a['record']['losses']} · {b['code']} {b['record']['wins']}-{b['record']['losses']}"
    return "\n".join([f"- {head}"] + lines + ([dest] if dest else []) + ([rec] if rec else []))


def main():
    day = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else (dt.datetime.now(BRT).date() - dt.timedelta(days=1))
    evs = api(f"getSchedule?hl=pt-BR&leagueId={WORLDS}")["schedule"]["events"]
    evs = [e for e in evs if e.get("type") == "match"]
    today = [e for e in evs if ts(e["startTime"]).astimezone(BRT).date() == day]
    done = [e for e in today if e["state"] == "completed"]
    out = []
    if not done:
        out.append("SEM_JOGOS")
    else:
        fase = done[0].get("blockName", "")
        out.append(f"## Worlds 2026 · {day.strftime('%d/%m')} · {fase}\n")
        for e in sorted(done, key=lambda e: e["startTime"]):
            out.append(series_block(e))
        pend = [e for e in today if e["state"] != "completed"]
        if pend:
            out.append(f"\n_{len(pend)} série(s) do dia ainda sem resultado na API._")
    nxt = [e for e in evs if e["state"] == "unstarted" and ts(e["startTime"]).astimezone(BRT).date() > day]
    if nxt:
        d0 = min(ts(e["startTime"]).astimezone(BRT).date() for e in nxt)
        out.append(f"\n**Próximos jogos ({d0.strftime('%d/%m')}, horário de Brasília)**")
        for e in sorted((e for e in nxt if ts(e["startTime"]).astimezone(BRT).date() == d0), key=lambda e: e["startTime"]):
            a, b = e["match"]["teams"]
            out.append(f"- {ts(e['startTime']).astimezone(BRT).strftime('%H:%M')} · {a['code']} × {b['code']} (Bo{e['match']['strategy']['count']}) · {e.get('blockName','')}")
    else:
        out.append("\nSem próximos jogos na agenda.")
    print("\n".join(out))


if __name__ == "__main__":
    main()
