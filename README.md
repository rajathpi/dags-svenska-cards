# Dags För Svenska · Cards

Flashcards built from the words in [Dags För Svenska!](https://www.youtube.com/@DagsF%C3%B6rSvenska) videos.
Watch a video, then rehearse its words. Every card links back to the second the word is said, and the
study page plays that line in the creator's own voice through YouTube's player.

**All credit to Dags För Svenska!** This is an unofficial, fan-made study companion. The videos, voice and
original content belong to the creator. Go watch and subscribe. The cards quote only the one short line
where each word appears, and the full transcripts are not published here.

## Use it
- **On the web:** open the GitHub Pages site, pick a video, press *Study*. Progress is saved in your browser.
- **In Anki:** download the `.apkg` for a video from Releases. Cards have Swedish + English audio and a
  "hear it in the video" link.

## Add a video (maintainers)
```
py -3.12 -m yt_dlp --skip-download --write-auto-subs --sub-langs sv-orig --sub-format json3 -o "transcripts/%(id)s" <url>
py -3.12 extract.py <id>          # captions -> timestamped sentences (local only, gitignored)
# write decks/<id>.json: word, pos, forms, english, t, sentence (<b>word</b>), sentence_en, note
py -3.12 make_index.py            # refresh the video picker
py -3.11 build_deck.py <id>       # -> build/<id>/dags-for-svenska-<id>.apkg
```
Translations and word choice are hand-checked, not machine output. Auto-caption slips are fixed (e.g. "Ren" → Rhen).
