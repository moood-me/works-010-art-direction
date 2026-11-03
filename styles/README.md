# Стили персонажей

A site beside the gallery: a style taken from real works that are beautiful — samples, the style's rules, and the
same cast of characters drawn by those rules in SVG. Open: serve the repository (`python3 -m http.server`), go to
`/styles/`.

Each style is a folder `styles/<folder>/` (the list is `ITEMS` in `index.html`) with:
- `entry.json`:
  ```json
  { "name": "…", "status": "good|mid|bad", "statusText": "…", "cover": "pics/cast.png",
    "sources": [{ "name": "Klaus (2019)", "link": "https://…" }],
    "what": "the style in one or two sentences, in Russian", "verdict": "honest, in Russian",
    "blocks": [ { "title": "…", "text": "…", "list": ["a rule", "…"], "pics": [["pics/x.png", "caption"]] } ] }
  ```
- `refs/` — small copies of the sample pictures (third-party, kept only as references; sources in `notes.md`),
  `svg/` — the drawings, `pics/` — them as PNG, `notes.md` — what was done and how to repeat it, `tools/` — scripts.
