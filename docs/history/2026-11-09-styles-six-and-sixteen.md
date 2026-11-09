# 2026-11-09 — the cast grows to six, the styles to sixteen (branch `claude/gallant-knuth-5qo916`)

**What called for it.** Pavel asked for four more styles, С13–С16 — strongly unlike the twelve and each other, again
taken from real works that are beautiful — and for two more characters, sharply different from the four in age,
character and mood, drawn in all sixteen styles: in the twelve existing ones by each style's own code and rules, so
that they stand beside the four as their own. One agent per style; pictures shown to him as each style was done.
The work starts from `ccr-a7af59de-aubv8d` (not merged into main), on a new branch.

**Decided by me (Claude, the orchestrating session).**
- The two characters: **Марат**, about 35, a cook — huge, loud, merry, generous (the only one whose resting face is a
  wide smile; white jacket, terracotta apron); **Кира**, about 15 — thin, angular, prickly and closed (a fringe over
  one eye, a dark plum hoodie, lime headphones). What the cast lacked: a big man in his prime and open joy; a
  teenager and sullenness. Their descriptions are in `docs/briefs/styles-more.md`.
- The four styles: С13 Japanese woodblock print (Utamaro, Hokusai, Sharaku, shin-hanga), С14 layered cut paper
  (Tearaway, Eric Carle, Norstein, Reiniger, Matisse), С15 noir by the black shape (Mignola, Bruce Timm, Cooke,
  Miller), С16 pixel art (Eastward, Owlboy, Celeste, 16-bit portraits). Chosen to differ by what does the drawing:
  a brush line and printed pattern; paper with thickness and shadows; a black shape and one light; the pixel.
- The pages' covers stay the four together; the six together is a new picture beside it.

**What was done.**
- `styles/s1…s12`: Марат and Кира added to each — a portrait, the figure, a turnaround and an expression sheet (in
  most styles for both), all six together; a module per character in the style's `tools/`, shared code only
  extended; the four's pictures unchanged (the agents compared regenerated SVG byte for byte). Each `notes.md` has a
  "Round three" section and how to add a character.
- `styles/s13-ukiyo-e`, `s14-paper`, `s15-noir`, `s16-pixel`: samples, rules, all six drawn, the page; listed in
  `styles/index.html`.
- Redone after my look: Кира's three-quarter face in С9 (the nose tip under the fringe read as an ear), her head in
  С12 (one eye in a blank cheek; still the weakest Кира), her age in С2 (the profile read as forty), the neck of the
  front views in С15.

**How, to repeat it.** The brief `docs/briefs/styles-more.md` (part A: add characters to an existing style; part B:
a new style) on top of `docs/briefs/styles.md`; one background agent per style, each only in its folder and
`/home/user/cache/styles-<folder>/`, no git; the orchestrator looks at every result, sends weak pictures back once
with what is wrong, commits per style. Sixteen agents ran at once on 4 cores without trouble (drawing is light).
The session's network was limited to package registries: an environment `moood-works` was made with the hosts the
samples came from (Wikimedia, the Met, the Art Institute of Chicago, ukiyo-e.org, Steam, Fandom's image host and a
few more). Even so many samples didn't download (rate limits on Wikimedia, 403 from sprite archives, artists' own
sites not on the list) — each new style's `notes.md` lists what it could and couldn't look at. A container restart
in the middle stopped five agents; their files were intact and they were resumed by message. Some styles' code
needs `shapely`, `scipy`, `scikit-image` from pip.

**Seen.** In `docs/findings.md`, "Drawing styles, round three".

**Next, asked by Pavel the same day.** Two more characters in 3D in each style that has its six — one of the three
old ones not yet in 3D there and one new one (`to3d/` Р13–Р36, brief: "Third round" in `docs/briefs/to3d.md`).
Blender 4.5 and the Human Base Meshes bundle were downloaded again into `/home/user/cache/` (Blender's sites added
to the environment). A note on that round will follow it.
