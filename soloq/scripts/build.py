import json, re, csv, sys, html
roster = json.load(open(sys.argv[1])); players = json.load(open(sys.argv[2])); outdir = sys.argv[3]
TEAMS = {"GEN":"Gen.G","AL CN":"Anyone's Legend","TL":"Team Liquid","G2":"G2 Esports","TSTW":"Team Secret Whales","LOS":"LOS",
 "HLE":"Hanwha Life Esports","BLG":"Bilibili Gaming","LYON24":"LYON","MKOI":"Movistar KOI","T1":"T1","TES":"Top Esports",
 "CFO":"CTBC Flying Oyster","Dplus":"Dplus KIA","IG":"Invictus Gaming","KCORP":"Karmine Corp"}
ROLE = {"t":"top","j":"jungle","m":"mid","a":"adc","b":"adc","s":"suporte"}
# servidor -> (platform da API, regional da Account-V1)
PLAT = {"KR":("kr","asia"),"EUW":("euw1","europe"),"NA":("na1","americas"),"BR":("br1","americas"),
        "VN":("vn2","asia"),"TW":("tw2","asia"),"CN":(None,None)}
rows, js = [], []
for r in roster:
    if r["role"] not in ROLE: continue
    p = players[r["player_page"]]
    raw = re.sub(r"'''\s*<br>\s*([A-Z]{2,3})'''", r"<br>'''\1'''", html.unescape(p["ids"]))
    nick = r["player_page"].split(" (")[0]
    accts, server, order = [], None, 0
    for chunk in re.split(r"<br\s*/?>", raw):
        chunk = chunk.strip()
        m = re.match(r"'''\s*([A-Z]{2,3})\s*(?::''')?\s*(?:''')?\s*:?\s*(.*)$", chunk)
        if m: server, chunk = m.group(1), m.group(2)
        m2 = re.match(r"(.*)\((VN|KR|EUW|NA|BR)\)\s*$", chunk)
        if m2: chunk, server = m2.group(1), m2.group(2)
        for a in re.split(r"[,;]", chunk):
            a = a.strip().strip("'").strip()
            if not a or not server: continue
            if "#" in a:
                g, t = a.rsplit("#", 1); g, t = g.strip(), t.strip()
            else: g, t = a, ""
            order += 1
            plat, reg = PLAT.get(server, (None, None))
            accts.append({"servidor": server, "riot_id": f"{g}#{t}" if t else g, "game_name": g, "tag_line": t,
                "platform": plat or "", "regional": reg or "",
                "consultavel_api": "sim" if (t and plat) else "nao",
                "obs": "" if t else ("servidor chinês (fora da API da Riot)" if server=="CN" else "sem tag: nome antigo, antes do Riot ID"),
                "ordem": order})
    base = {"time": TEAMS[r["team_code"]], "sigla": r["team_code"], "regiao_liga": r["region"], "jogador": nick,
            "nome": p["name"], "pais": p["country"], "posicao": ROLE[r["role"]], "leaguepedia": "https://lol.fandom.com/wiki/"+p["title"].replace(" ","_"),
            "dpm_lol": p["dpmlol"], "lolpros": p["lolpros"]}
    js.append({**base, "contas": accts})
    for a in accts: rows.append({**base, **a})
    if not accts: rows.append({**base, "servidor":"", "riot_id":"", "game_name":"", "tag_line":"", "platform":"", "regional":"", "consultavel_api":"nao", "obs":"nenhuma conta listada na Leaguepedia", "ordem":0})
cols = ["time","sigla","regiao_liga","jogador","nome","pais","posicao","ordem","servidor","riot_id","game_name","tag_line","platform","regional","consultavel_api","obs","leaguepedia","dpm_lol","lolpros"]
with open(outdir+"/contas-soloq.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, cols); w.writeheader(); [w.writerow({c:x.get(c,"") for c in cols}) for x in rows]
json.dump({"fonte":"Leaguepedia (lol.fandom.com), escalações de 2026 Season World Championship/Main Event e campo ids de cada jogador","coletado_em":"2026-10-20","jogadores":js},
          open(outdir+"/contas-soloq.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
import collections
print(len(js), "jogadores;", len(rows), "linhas;", collections.Counter(x["consultavel_api"] for x in rows), collections.Counter(x["servidor"] for x in rows))
print("sem conta consultável:", [p["jogador"] for p in js if not any(a["consultavel_api"]=="sim" for a in p["contas"])])
