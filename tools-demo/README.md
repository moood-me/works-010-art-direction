# Чужие инструменты — демонстрация

A site beside the gallery: for each part of a character, what we have now against what a ready open tool gives.
Open: serve the repository (`python3 -m http.server`) and go to `/tools-demo/`.

Each page is a folder `tools-demo/<folder>/` (the list is `ITEMS` in `index.html`) with:
- `entry.json`:
  ```json
  { "name": "Деформации тела и лица", "status": "good|mid|bad", "statusText": "лучше нашего",
    "tools": [{ "name": "libigl", "link": "https://..." }],
    "what": "what the tool is, one or two sentences, in Russian",
    "verdict": "the honest conclusion, in Russian",
    "compare": [ { "title": "one function or thing",
                   "now":  { "text": "how it is with us", "pics": [["../../docs/pictures/…png", "caption"]] },
                   "with": { "text": "how it is with the tool", "pics": [["pics/x.webp", "caption"], ["pics/turn.mp4", "caption"]] } } ] }
  ```
  Picture paths are relative to the folder; `.mp4`/`.webm` show as videos.
- `pics/` — the pictures, `notes.md` — what was done and how to repeat it, scripts in `tools/`.
