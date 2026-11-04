# Brief for every agent of the "Чужие инструменты" demo

## Why
Repository `/home/user/works-010-art-direction` (read its `CLAUDE.md`, `docs/README.md`, `docs/requirements.md`,
`docs/directions.md`) works out how to make beautiful stylised 3D characters for moood's games — cartoon of different
degrees, with motion (Kimodo) and expressions. Bodies are NAVER's Anny (moood's baked bodies and Anny's own settings),
heads, faces, hair and clothes we have so far invented ourselves, and Pavel (the owner) finds they look rather ugly.
He asked: show me, for each ready open tool we found, "this function / this thing looks like this with us now — and with
the tool it can look like this". Each agent does one page of a small site.

## The site
`tools-demo/index.html` (done; don't change it). Your page is the folder named in your task: `tools-demo/<folder>/`
with `entry.json` (format in `tools-demo/README.md`), `pics/`, `notes.md`, `tools/` (your scripts). Text a person reads
is in Russian, plain words, short; Pavel reads it.

- "Сейчас у нас": our existing pictures from `docs/pictures/` (referenced by relative path `../../docs/pictures/...`,
  don't copy them), or new renders of our current things if no existing picture compares fairly. The gallery
  (`gallery/index.html`, its `groups` list) says which picture is which path; the experiments are in `experiments/`.
- "С инструментом": what the tool really gives, made by you now. Same character / same angle / same task as the
  "now" side wherever possible, so the comparison is fair.
- Several compare blocks, one per function or thing (e.g. "клетка", "сглаживание", "лицо по точкам").
- `verdict`: honest — better, partly better, not better, and why, what it would take. `status`: good / mid / bad.
- Animations as short `.mp4` (h264, ≤ 10 s) when motion is the point. Keep your folder under ~15 MB total
  (webp or jpg for big pictures).

## Rules
- Work ONLY inside your folder `tools-demo/<folder>/` and in `/home/user/cache/<folder>/` (downloads, clones, models,
  big temporary files). Don't touch anything else in the repository; don't run git commit/push/checkout/stash — the
  orchestrator commits. Other agents work in parallel in the same tree.
- Blender 4.5 LTS is installed: `/home/user/cache/blender/blender -b ...` (background, Python scripts). No GPU: render
  with Workbench, EEVEE if it works headless, or Cycles CPU at low samples. Headless Chromium + Playwright work for
  three.js pages (see `engine/check/shots.mjs` for how this repository shoots pictures).
- 4 CPU cores and 15 GB RAM are shared by 6 agents: keep simulations and renders short; don't run more than one heavy
  process at a time.
- If the tool cannot run here (needs a GPU, code not published, etc.), say so in your final report and in the page —
  don't fake it, don't replace it with something of your own.
- No workarounds that pretend: what is shown on the "with the tool" side must come from the tool.
- Look at every picture yourself, as a person would, before putting it on the page; don't show results with visible
  bugs from your own setup (wrong scale, camera off, broken import). If the tool's own result is weak, show it and say so.
- `notes.md`: what was done, why, and how to repeat it (commands, versions, sources, licences of downloaded assets).
- Pictures of third-party assets: note where they came from and their licence in `notes.md`.

## Final report (your last message)
Short, in Russian: what the page shows, the verdict, what didn't work and why, and the list of files you made.
