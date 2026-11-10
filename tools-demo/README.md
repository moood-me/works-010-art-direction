# Чужие инструменты — демонстрация

A site beside the gallery: for each part of a character, what we have now against what a ready open tool gives.
Open: serve the repository (`python3 -m http.server`) and go to `/tools-demo/`.

Each page is a folder `tools-demo/<folder>/` (the list is `items.json`: a line `[code, folder]` a page) with:
- `entry.json`:
  ```json
  { "name": "Деформации тела и лица", "status": "good|mid|bad", "statusText": "лучше нашего",
    "tools": [{ "name": "libigl", "link": "https://..." }],
    "what": "what the tool is, one or two sentences, in Russian",
    "verdict": "the honest conclusion, in Russian",
    "uses": [ { "title": "what the tool is made for", "text": "that use in the real world, plain, in Russian",
                "pics": [["pics/use1.webp", "caption"]] } ],
    "compare": [ { "title": "one function or thing",
                   "now":  { "text": "how it is with us", "pics": [["../../docs/pictures/…png", "caption"]] },
                   "with": { "text": "how it is with the tool", "pics": [["pics/x.webp", "caption"], ["pics/turn.mp4", "caption"]] } } ] }
  ```
  `uses` (shown first, «Что умеет сам по себе»): the tool in the cases it was made for, used as intended, even where
  they are not ours — so Pavel sees what the thing is and why it exists. `compare`: against what we have.
  Picture paths are relative to the folder; `.mp4`/`.webm` show as videos.
- `pics/` — the pictures, `notes.md` — what was done and how to repeat it, scripts in `tools/`.
