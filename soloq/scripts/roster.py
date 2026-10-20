import json, re, sys, urllib.request, urllib.parse
UA = "MetricasWorldsBot/0.1 (personal project)"
def wikitext(page):
    q = urllib.parse.urlencode({"action":"parse","page":page,"prop":"wikitext","format":"json","redirects":1})
    req = urllib.request.Request("https://lol.fandom.com/api.php?"+q, headers={"User-Agent":UA})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    if "error" in d: raise RuntimeError(d["error"])
    return d["parse"]["wikitext"]["*"], d["parse"]["title"]
if __name__ == "__main__":
    wt,_ = wikitext("2026_Season_World_Championship/Main_Event")
    out = []
    for blk in re.split(r"\{\{TeamRoster\|", wt)[1:]:
        team = re.search(r"team=([^|\n]+)", blk).group(1).strip()
        region = (re.search(r"\|region=([^|\n]+)", blk) or [None,""])[1].strip()
        for m in re.finditer(r"\{\{TeamRoster/Line\|([^}]*)\}\}", blk):
            f = dict(kv.split("=",1) for kv in m.group(1).split("|") if "=" in kv)
            f = {k.strip():v.strip() for k,v in f.items()}
            out.append({"team_code":team,"region":region,"player_page":f.get("player"),"role":f.get("role"),"flag":f.get("flag"), **{k:v for k,v in f.items() if k not in("player","role","flag")}})
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
