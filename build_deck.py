"""Build an Anki deck (.apkg) for one Dags För Svenska! video from decks/<id>.json.

    py -3.11 build_deck.py r4eMbzM9QkA

Audio reuses the HP deck's Speaker (Piper sv_SE-nst + Kokoro EN "sandwich" on the back).
Every card credits the channel and links to the exact second in the video.
"""
import json
import os
import re
import sys
import zlib

import genanki

sys.path.insert(0, r"C:\Users\rajat\Desktop\claude\anki-hp")
from build import Speaker, strip_tags  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ["Word", "POS", "Forms", "English", "Sentence", "SentenceEnglish", "Note",
          "Audio", "AudioBack", "Video", "Timestamp", "Link", "Channel", "ChannelURL"]

T = lambda f: open(os.path.join(HERE, "templates", f), encoding="utf-8").read()
MODEL = genanki.Model(
    1791200000001, "Dags För Svenska (word + video line + audio)",
    fields=[{"name": f} for f in FIELDS],
    templates=[{"name": "Swedish → English", "qfmt": T("front.html"), "afmt": T("back.html")}],
    css=T("card.css"),
)


def mmss(t):
    return f"{t // 60}:{t % 60:02d}"


def main(vid):
    meta = json.load(open(os.path.join(HERE, "decks", f"{vid}.json"), encoding="utf-8"))
    out = os.path.join(HERE, "build", vid)
    media_dir = os.path.join(out, "media")
    os.makedirs(media_dir, exist_ok=True)
    spk = Speaker()
    deck = genanki.Deck(1791200000000 + zlib.crc32(vid.encode()) % 100000,
                        f"Dags För Svenska::{meta['episode']} {meta['title']}")
    media = []
    for c in meta["cards"]:
        slug = re.sub(r"[^a-zåäö]+", "_", c["word"].lower()).strip("_")
        sv = strip_tags(c["sentence"])
        front = os.path.join(media_dir, f"dfs_{vid}_{slug}.mp3")
        back = os.path.join(media_dir, f"dfs_{vid}_{slug}_back.mp3")
        if not os.path.exists(front):
            spk.card_audio(c["word"].replace("…", ""), sv, front)
        if not os.path.exists(back):
            spk.back_audio(c["english"].replace(";", ","), c["sentence_en"], sv, back)
        media += [front, back]
        f = {"Word": c["word"], "POS": c["pos"], "Forms": c["forms"], "English": c["english"],
             "Sentence": c["sentence"], "SentenceEnglish": c["sentence_en"], "Note": c.get("note", ""),
             "Audio": f"[sound:{os.path.basename(front)}]", "AudioBack": f"[sound:{os.path.basename(back)}]",
             "Video": f"{meta['episode']} · {meta['title']}", "Timestamp": mmss(c["t"]),
             "Link": f"https://youtu.be/{vid}?t={max(0, c['t'] - 1)}",
             "Channel": meta["channel"], "ChannelURL": meta["channel_url"]}
        deck.add_note(genanki.Note(model=MODEL, fields=[f[k] for k in FIELDS],
                                   tags=["DagsForSvenska", f"video_{vid}"],
                                   guid=genanki.guid_for("dfs", vid, c["word"])))
        print("ok", c["word"])
    pkg = genanki.Package(deck)
    pkg.media_files = media
    apkg = os.path.join(out, f"dags-for-svenska-{vid}.apkg")
    pkg.write_to_file(apkg)
    print("wrote", apkg, len(meta["cards"]), "cards")


if __name__ == "__main__":
    main(sys.argv[1])
