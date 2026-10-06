"""Regenerate the README screenshots in shots/ with headless Chrome.

    py -3.12 -m http.server 8053      (in this folder, or the "dags-svenska" preview config)
    py -3.12 make_shots.py
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SITE = "http://localhost:8053/"
OUT = os.path.join(HERE, "shots")


def shoot(url, name, w, h, scale=2, budget=15000):
    path = os.path.join(OUT, name)
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--mute-audio",
                    f"--window-size={w},{h}", f"--force-device-scale-factor={scale}",
                    f"--virtual-time-budget={budget}", f"--screenshot={path}", url],
                   check=True, capture_output=True)
    print(name, os.path.getsize(path) // 1024, "KB")


def anki_card(vid, word, night=False):
    """Render one Anki card back from the real templates, so the README shows what Anki shows."""
    d = json.load(open(os.path.join(HERE, "decks", f"{vid}.json"), encoding="utf-8"))
    c = next(x for x in d["cards"] if x["word"] == word)
    t = c["t"]
    f = {"Word": c["word"], "POS": c["pos"], "Forms": c["forms"], "English": c["english"],
         "Sentence": c["sentence"], "SentenceEnglish": c["sentence_en"], "Note": c.get("note", ""),
         "Audio": "", "AudioBack": '<span class="play">▶</span>',
         "Video": f"{d['episode']} · {d['title']}", "Timestamp": f"{t // 60}:{t % 60:02d}",
         "Link": "#", "Channel": d["channel"], "ChannelURL": "#"}
    tpl = open(os.path.join(HERE, "templates", "back.html"), encoding="utf-8").read()
    tpl = re.sub(r"\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}", lambda m: m.group(2) if f.get(m.group(1)) else "", tpl, flags=re.S)
    body = re.sub(r"\{\{(\w+)\}\}", lambda m: f.get(m.group(1), ""), tpl)
    css = open(os.path.join(HERE, "templates", "card.css"), encoding="utf-8").read()
    page = f"""<!doctype html><meta charset="utf-8"><style>{css}
      html, body {{ margin: 0; background: {'#1d1b19' if night else '#fbf8f1'}; }}
      .play {{ display: inline-flex; width: 34px; height: 34px; border-radius: 50%; align-items: center; justify-content: center;
               background: #3d6fb6; color: #fff; font: 14px system-ui; }}</style>
      <div class="card{' nightMode' if night else ''}">{body}</div>"""
    tmp = os.path.join(OUT, "_anki.html")
    open(tmp, "w", encoding="utf-8").write(page)
    return tmp


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    shoot(SITE + "#shot#answer#light", "study.png", 1280, 720)
    shoot(SITE + "#shot#words#light", "words.png", 1280, 720)
    shoot(SITE + "#shot#answer#dark", "dark.png", 1280, 720)
    # headless Chrome won't go below ~500px wide, so "phone" is a 500px window
    shoot(SITE + "#shot#answer#light", "phone.png", 500, 1000, scale=2)
    tmp = anki_card("r4eMbzM9QkA", "ledtråd")
    shoot("file:///" + tmp.replace("\\", "/"), "anki.png", 560, 600, budget=1500)
    os.remove(tmp)
    # shrink for the README (2x captures are ~900 KB each)
    from PIL import Image
    for f, w in [("study", 1600), ("words", 1200), ("dark", 1200), ("phone", 500), ("anki", 560)]:
        png = os.path.join(OUT, f + ".png")
        im = Image.open(png)
        im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).convert("RGB").save(
            os.path.join(OUT, f + ".jpg"), quality=86, optimize=True, progressive=True)
        os.remove(png)
