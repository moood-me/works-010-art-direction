# 2026-11-03 — other people's tools, and styles drawn (branch `ccr-a7af59de-aubv8d`)

**What called for it.** Pavel asked whether anyone does the work of this repository better — libraries, standards,
software an agent can run itself — since our own clothes and faces look rather ugly. A search found a few tools that
could replace parts of ours. He asked to see each on a small site: "this thing looks like this with us now — and like
this with the tool", and later also what each tool does in the cases it was made for. Then, talking about how to
make characters beautiful without an artist, we agreed to try two steps: take a style from real works that are
beautiful (samples, the style's rules) and draw characters by those rules first, in SVG, before any 3D. Pavel asked
not to start 3D; he wants to look at the drawings.

**What was done.**
- `tools-demo/` — a site like the gallery (`index.html` reads each page's `entry.json`; format in its README): Н1
  deformations (libigl), Н2 garments as sewing patterns (GarmentCode), Н3 cloth in motion (Blender, HOOD /
  ContourCraft), Н4 hair (Blender's hair nodes, HairDeck), Н5 heads, faces, bodies (Blender Studio characters, Human
  Base Meshes, StdGEN), Н6 toon light and outline (MToon from three-vrm), Н7 forms from an outline (Monster Mash).
  Each page: «Что умеет сам по себе» (the tool used as intended) and comparisons with ours; each page's `notes.md`
  says how it was made.
- `styles/` — a site of the same kind: six styles — С1 Pixar/Disney, С2 Klaus, С3 graphic flat (Nimona, Cartoon
  Saloon, Hilda), С4 illustrated near-real (Arcane), С5 indie heroes, С6 symbolic (Journey, Limbo, Gris, "hope").
  Each: 10–12 samples (third-party, kept only as references, sources in `notes.md`), the style's rules, and the same
  cast drawn in SVG by the rules — Аня (20, warm, dreamy), Савелий Петрович (70, a watchmaker, grumpy and kind), Тим
  (8, mischievous), Вера (40, strict, tired): portraits, figures, turnarounds, expression sheets, the four together.
  The cast was chosen by me so the styles can be compared.

**How, to repeat it.** One agent per page, run in parallel by the orchestrating session with a common brief (what
the repository is for, the page format, work only in your folder, look at every picture yourself, say honestly what
didn't work). Blender 4.5 LTS was downloaded into a cache folder outside the repository and run headless; downloads,
clones and drafts stayed in that cache. The orchestrator looked at each result and committed it.

**Seen.** The tools mostly don't beat ours in beauty (libigl, MToon and Monster Mash rest on the same ideas); the
pretty VRM avatars shown on Н6 owe their looks to the artists' textures and forms, not to the shader. Of the styles,
the flat graphic (С3), Klaus's light (С2) and the symbolic scene (С6) came out best; Pixar (С1) and Arcane (С4) look
like dolls and mannequins — SVG drawn by a script from 3D-like forms loses the life of drawing.
