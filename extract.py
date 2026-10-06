"""json3 auto-captions -> sentences with start timestamps (seconds)."""
import json, re, sys
vid = sys.argv[1]
d = json.load(open(f'transcripts/{vid}.sv-orig.json3', encoding='utf-8'))
words = []  # (ms, token)
for e in d['events']:
    for s in e.get('segs', []):
        t = s.get('utf8', '')
        if t:
            words.append((e['tStartMs'] + s.get('tOffsetMs', 0), t.replace('\n', ' ')))
sents, cur, start = [], '', None
for ms, t in words:
    if start is None: start = ms
    cur += t
    if re.search(r'[.!?]\s*$', cur):
        s = re.sub(r'\s+', ' ', cur).strip()
        s = re.sub(r'^>>\s*|\[musik\]\s*', '', s).strip()
        if s: sents.append({'t': round(start / 1000), 'sv': s})
        cur, start = '', None
if cur.strip(): sents.append({'t': round(start / 1000), 'sv': re.sub(r'\s+', ' ', cur).strip()})
json.dump(sents, open(f'transcripts/{vid}.sentences.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(sents), 'sentences')
