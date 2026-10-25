"""Rebuild decks/index.json (the video picker) from every decks/<id>.json."""
import glob, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
out = []
for p in sorted(glob.glob(os.path.join(HERE, "decks", "*.json"))):
    if p.endswith("index.json"): continue
    d = json.load(open(p, encoding="utf-8"))
    out.append({"id": d["video"], "title": d["title"], "episode": d["episode"], "short": d.get("short", ""), "count": len(d["cards"])})
# episode order: ep. 1, 2, … 7 part 1, 7 part 2, …, then the beginner series
def order(v):
    nums = [int(n) for n in re.findall(r"\d+", v["episode"])]
    return ("beginner" in v["episode"], nums)
out.sort(key=order)
json.dump(out, open(os.path.join(HERE, "decks", "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(out)
