# Brief: one of our drawn characters → a good 3D character

## Why
Repository `/home/user/works-010-art-direction` (read `CLAUDE.md`, `docs/README.md`, `docs/problem.md`,
`docs/requirements.md`, `docs/directions.md`, `engine/README.md`) is about beautiful stylised 3D characters for
moood's games, moving by Kimodo. Agents drew a cast of four (Аня, Савелий Петрович, Тим, Вера) in twelve styles in SVG
(`styles/`, open `/styles/` with `python3 -m http.server`); Pavel liked them a lot. A neural picture-to-3D model
(StdGEN, `tools-demo/n8-stdgen/`) guessed the shape but gave a "cheap toy" quality: blotchy colour, holes, smeared
faces. Our own earlier 3D heads and bodies looked assembled, not designed.

The approach to try now: don't turn the drawing into 3D by a neural net — build the 3D from good ready bases and fit
it to our drawing, which is the brief and the measure:
1. **Body — Anny** (engine bodies in `engine/data`, `engine/src/body.js`, skeleton SOMA, retargeting and skinning in
   `engine/src`, Kimodo motions in `engine/motions`, the viewer in `engine/viewer`). Fit proportions to the drawing's
   front and side views with deformers (our cage/landmark tools in `experiments/form-tools`; libigl is installed in
   `/home/user/cache/n1-deform`). Check by overlaying the render on the drawing.
2. **Head and face — a good base made by artists, not invented**: e.g. a stylised head from Blender's Human Base
   Meshes (CC0; downloaded in `/home/user/cache/n5-heads/hbm`), clean loops around eyes and mouth; fitted by points to
   the drawing in front view and profile; the eye as a ball with real lids; joined to Anny's body (or the base head
   replaces Anny's head, or Anny's head is wrapped onto it — see `experiments/heads-wrap` for how we did a wrap).
   See `tools-demo/n5-heads/` for what is better in Blender Studio's heads.
3. **Colour and fine features — from our own SVG**: project the clean drawing onto the model (front, side) as a
   texture or a painted layer — no neural blotches, the drawing's fineness kept.
4. **Clothes** — fitted to the drawing: modelled shells for stylised clothes, or GarmentCode patterns / cloth
   (`tools-demo/n2-garments`, `tools-demo/n3-cloth`, our О3 in `experiments/cloth`), whatever serves.
5. **Hair** — big locks along curves (our В1, `experiments/hair`), the silhouette from the drawing's views.
6. **Look** — a material for the style: stepped shade, outline, rim (see `tools-demo/n6-toon` for MToon).
7. **Judge by eye**: render in the same views as the drawing, side by side and overlaid, many times.

A neural model (StdGEN results in `/home/user/cache/hf/out/`) may be used only as a hint for the back and sides where
there is no drawing — not as the result.

## Your job
Your character and its drawings are named in your task. Make it a 3D character this way, as good as you can: it must
look like the drawing and be attractive — Pavel judges by eye whether it is a pleasant character, not a toy. Show:
- the drawing and the 3D render side by side in the drawing's views (front, three-quarter, profile), and overlaid;
- a turn around (short mp4);
- the character moving by a Kimodo motion through the engine (walk; short mp4) — it must have the SOMA skeleton;
- if you get that far: a few facial expressions from the drawing's expression sheet;
- steps along the way (what each base gave), so Pavel sees how it was built.
Decide yourself how far to go on each part; don't hammer at one wall — if something doesn't work, say so and move on.
Look at everything yourself before showing; don't show what you find ugly without saying so.

## The page
Folder `to3d/<folder>/` with `entry.json` (format as `styles/README.md`: name, status, statusText, cover, sources,
what, verdict, blocks of title/text/list/pics; `.mp4` show as videos), `pics/`, `notes.md` (what was done, how to
repeat, licences of bases used), `tools/` (your scripts). Russian for text a person reads, plain words. Keep the folder
under ~20 MB (webp/jpg, short mp4s).

## Rules
- Work ONLY in `to3d/<folder>/` and `/home/user/cache/to3d-<folder>/`. Don't touch anything else in the repository;
  no git commit/push/checkout/stash — the orchestrator commits. Another agent works in parallel.
- Blender 4.5: `/home/user/cache/blender/blender -b` (no GPU: Cycles CPU or Workbench; EEVEE doesn't run headless).
  Headless Chromium + Playwright for three.js (`engine/check/shots.mjs` shows how). 4 CPU cores, 15 GB RAM, shared.
- No neural image generation for the result; your own code and the bases.

## Final report (your last message)
Short, in Russian: what the page shows, how it came out honestly, what didn't work, files made.

## Second round (seven more characters) — also
- Learn from the five done: `to3d/r1-s3-anya`, `r2-s10-savely`, `r3-s9-tim`, `r4-s5-vera` (good, alive) and
  `r5-s2-anya` (middling: blotches on the face, a rough figure) — read their `notes.md`, reuse their code where it fits
  (fitting heads, face layers, the live face — blinks, saccades, gaze leading the head, speech mouth shapes, blended
  expressions —, viewers), but make your character in its own style.
- If your character comes out good, go on at once: the live face, a few Kimodo motions with it (only those in
  `engine/motions` — don't order new ones from the studio), and a browser viewer `tools/web/view.html` (turn with the
  mouse, choose motion and expression, play/pause/scrub, talk on/off) with the data it needs inside your folder; set
  `"view3d": "tools/web/view.html"` and a short `"view3dNote"` in entry.json — the site shows it as a «3D» tab.
  If it comes out weak, say so and stop there.
- Frame the motion videos so the character is big in the frame (a camera following it).
