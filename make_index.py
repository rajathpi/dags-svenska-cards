"""Rebuild decks/index.json (the video list) and decks/all.json (every card, for search and mixed review)
from every decks/<id>.json, and check that each video sits on a line in decks/lines.json."""
import glob, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
out, cards = [], {}
for p in sorted(glob.glob(os.path.join(HERE, "decks", "*.json"))):
    if os.path.basename(p) in ("index.json", "all.json", "lines.json"): continue
    d = json.load(open(p, encoding="utf-8"))
    out.append({"id": d["video"], "title": d["title"], "episode": d["episode"], "short": d.get("short", ""),
                "duration": d.get("duration"), "count": len(d["cards"])})
    cards[d["video"]] = [[c["word"], c["english"], c["pos"], c["forms"], c["sentence"], c["sentence_en"],
                          c.get("note", ""), c["t"], c["end"]] for c in d["cards"]]
# episode order: ep. 1, 2, … 7 part 1, 7 part 2, …, then the beginner series
def order(v):
    nums = [int(n) for n in re.findall(r"\d+", v["episode"])]
    return ("beginner" in v["episode"], nums)
out.sort(key=order)
json.dump(out, open(os.path.join(HERE, "decks", "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(cards, open(os.path.join(HERE, "decks", "all.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
lines = json.load(open(os.path.join(HERE, "decks", "lines.json"), encoding="utf-8"))["lines"]
placed = {v for l in lines for v in l["videos"]}
missing = [v["episode"] + " " + v["id"] for v in out if v["id"] not in placed]
print(len(out), "videos,", sum(v["count"] for v in out), "cards")
if missing: print("NOT ON A LINE YET (add to decks/lines.json):", ", ".join(missing))
