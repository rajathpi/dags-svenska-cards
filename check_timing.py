"""Check each card's timing against the caption's word-level timestamps.

For every card: when is the bold word actually spoken, when does its sentence finish,
and does the page's clip window (t-0.6 .. end+0.4) cover both?
"""
import json, re, sys
vid = sys.argv[1] if len(sys.argv) > 1 else "r4eMbzM9QkA"
cap = json.load(open(f"transcripts/{vid}.sv-orig.json3", encoding="utf-8"))
toks = []  # (seconds, word)
for e in cap["events"]:
    for s in e.get("segs", []):
        w = s.get("utf8", "").strip()
        if w:
            toks.append(((e["tStartMs"] + s.get("tOffsetMs", 0)) / 1000, w))
norm = lambda w: re.sub(r"[^a-zåäöéü0-9]", "", w.lower())
deck = json.load(open(f"decks/{vid}.json", encoding="utf-8"))
bad = 0
for c in deck["cards"]:
    bold = re.findall(r"<b>(.*?)</b>", c["sentence"])[0]
    first = norm(bold.split()[0])
    sent_words = [norm(w) for w in re.sub(r"<[^>]+>", "", c["sentence"]).split()]
    # sentence start = first caption token near t that begins the sentence
    cands = [i for i, (ts, w) in enumerate(toks) if abs(ts - c["t"]) <= 3 and norm(w) == sent_words[0]]
    if not cands:
        print(f"?? {c['word']:<14} sentence start not found near {c['t']}"); bad += 1; continue
    i0 = min(cands, key=lambda i: abs(toks[i][0] - c["t"]))
    seg = toks[i0:i0 + len(sent_words) + 4]
    wt = next((ts for ts, w in seg if norm(w).startswith(first[:5]) or first.startswith(norm(w)[:5]) and len(norm(w)) > 2), None)
    last = toks[min(i0 + len(sent_words) - 1, len(toks) - 1)][0]
    lo, hi = c["t"] - 0.6, c["end"] + 0.4
    # a word token's timestamp is its onset; give the last word ~0.6 s to be said
    flags = []
    if wt is None: flags.append("WORD NOT FOUND")
    elif not (lo <= wt <= hi): flags.append(f"word@{wt:.1f} outside clip")
    if last + 0.6 > hi: flags.append(f"sentence ends ~{last + 0.6:.1f} > clip end {hi:.1f}")
    if toks[i0][0] < lo: flags.append(f"sentence starts {toks[i0][0]:.1f} before clip {lo:.1f}")
    bad += bool(flags)
    print(f"{'XX' if flags else 'ok'} {c['word']:<14} t={c['t']:>3} end={c['end']:>3} start={toks[i0][0]:6.1f} word={wt if wt is None else round(wt,1)!s:>6} last={last:6.1f}  {'; '.join(flags)}")
print(f"\n{len(deck['cards']) - bad}/{len(deck['cards'])} cards OK")
