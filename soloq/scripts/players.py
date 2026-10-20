import json, re, sys, time
sys.path.insert(0, sys.argv[1]); from roster import wikitext
r = [x for x in json.load(open(sys.argv[2])) if x["role"] in ("t","j","m","a","b","s")]
out = {}
for x in r:
    p = x["player_page"]
    for attempt in range(4):
        try:
            wt, title = wikitext(p); break
        except Exception as e:
            print("ERR", p, e, file=sys.stderr); time.sleep(10*(attempt+1)); wt, title = "", p
    def field(k):
        m = re.search(r"^\|"+k+r"=(.*)$", wt, re.M); return m.group(1).strip() if m else ""
    out[p] = {"title": title, "id": field("id"), "name": field("name"), "country": field("country"),
              "residency": field("residency"), "ids": field("ids"), "lolpros": field("lolpros"), "dpmlol": field("dpmlol"), "deeplol": field("deeplol")}
    print(p, "|", out[p]["ids"][:150], file=sys.stderr)
    time.sleep(1.5)
json.dump(out, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
