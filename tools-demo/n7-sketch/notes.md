# Н7 — Формы из контура (Monster Mash)

## What was done and why

Pavel asked, for each ready open tool, "this thing looks like this with us now — and with the tool it can look like
this". This page is Monster Mash (Google, Apache-2.0; Dvorožňák et al., "Monster Mash: A Single-View Approach to Casual
3D Modeling and Animation", SIGGRAPH Asia 2020): outlines of parts drawn over each other are inflated into one soft
3D shape, which can then be deformed and animated by dragging points on it.

- Built the upstream app (desktop, SDL) to make sure the code builds as published, then built a small harness
  (`tools/mm_harness.cpp`) on the same sources without the window: it does, step by step, what the app does on a
  mouse stroke (draws the stroke into the outline image with the app's own painter, thickness 3, closes the gap with a
  "Neumann" line, fills the region), stacks the parts back to front, calls `performReconstruction()` (the app's
  switch to 3D), runs the ARAP-L engine until it settles (as the paint loop does), writes `rest.obj` and the part of
  each vertex. With an animation file it puts control points on the model as a left click in the animate mode does
  (`Def3D::addControlPointOnFace`, front view), moves them frame by frame, pauses the z-solve as the app does while an
  animation plays, runs 10 engine iterations a frame and writes `f####.obj`. Nothing of Monster Mash is changed.
- Our characters: П1 bear (`experiments/indie`), П2 cat and imp, v2 (`experiments/toon`). Shot standing, front,
  three-quarter (0.75 rad) and side with `tools/shoot_ours.cjs` (the pages' own looks; the indie page's figure turned
  in place as by dragging, the toon page by its `yaw` parameter).
- Outlines traced by hand on the front shots (`tools/outlines.py`): one outline per part, back to front; a part that
  grows out of another is an open stroke whose ends lie inside it (the app closes it with the Neumann line — that is
  what makes the join smooth), a part lying on another (the bear's muzzle) is closed. Traced over the picture with a
  coordinate grid and corrected by overlay (`trace.png`).
- Colours: Monster Mash's own "template image" idea — our front picture mapped onto the front side
  (`tools/texture.py` takes our dark silhouette line out of it and spreads colours a little past the silhouette, so
  the line does not lie on the surface as a band). Only parts that carry drawing (head, muzzle, body) take the
  picture; other parts, every back side and steep sides (where a planar picture only smears) are one colour per part —
  the median of the picture over it, or given (imp's claws, hooves, horns; cat's gloves and feet).
- Rendered with `tools/view.html` (three.js 0.160, as our pages): preset `indie` copies П1's lights, toon ramp,
  dark line, floor and fixed camera (the front then lines up with our picture pixel for pixel); preset `toon` copies
  П2's lights, ramp, ink hull and fitted camera turned by yaw; preset `mm` is Monster Mash's own look (its matcap
  `data/shaders/matcapOrange.jpg`, no light, no line) for the "what it is for" part.
- Motion: bear waves (points on feet, body, left paw held; right paw led along an arc; head point swaying), and,
  for the tool's own case, a creature drawn from scratch in side view walking on the spot (four foot points in
  diagonal pairs, body, head, tail) — `tools/anim.py`. Pavel's later request (via the coordinator): show the tool in
  the cases it was made for, and say in each compare block what the method is and what it is for — hence `uses`.

## Findings

- Front: almost exactly what was drawn; parts join softly, with no lumps or seams — its best side.
- Depth is invented from the outline width only: everything stays in the drawing plane; bear head depth ≈ 0.54 of
  its width (ours 0.88), feet do not point forward, arms are flat paddles at the sides, thin parts (claws, tail tip)
  become sausages. Control is only the part order and one inflation strength (a per-region strength exists in the
  code, not in the app's UI; not used here).
- Motion by points works, soft and rubbery, but it is hand dragging in the screen plane; no bones, no Kimodo.

## How to repeat

```sh
C=/home/user/cache/n7-sketch; T=tools-demo/n7-sketch/tools      # T relative to the repository
apt-get install -y libsdl2-dev
git clone --depth 1 https://github.com/google/monster-mash $C/monster-mash        # commit eb2869ad (2026-03-11)
wget http://www.netlib.org/voronoi/triangle.zip && unzip triangle.zip -d $C/monster-mash/third_party/triangle
# gcc 13: miniz is included inside a namespace before <cstdint>; force-include it (build flag only, no source change)
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-include cstdint" -DCMAKE_C_FLAGS="-include stdint.h" \
      -DMM=$C/monster-mash -S $T -B $C/hbuild && make -C $C/hbuild
python3 -m http.server 8791            # in the repository
W=$C/work; NODE_PATH=$(npm root -g) node $T/shoot_ours.cjs $W bear cat,imp
python3 $T/outlines.py $W; for n in bear cat imp; do python3 $T/texture.py $W $n; done
python3 $T/anim.py $W bear-wave; python3 $T/anim.py $W monster-walk
for n in cat imp; do $C/hbuild/mm_harness $W/$n/shape.txt $W/$n; done
$C/hbuild/mm_harness $W/bear/shape.txt $W/bear $W/bear/anim.txt
$C/hbuild/mm_harness $W/monster/shape.txt $W/monster $W/monster/anim.txt
cp $C/monster-mash/data/shaders/matcapOrange.jpg $W/; ln -s $PWD/$T/view.html $W/view.html
(cd $W && python3 -m http.server 8792)
node $T/shoot_mm.cjs '[{"name":"mm-bear","dir":"bear","preset":"indie","w":479,"h":479,"k":0.002381,"u0":239.5,"vFloor":378},
  {"name":"mm-cat","dir":"cat","preset":"toon","w":700,"h":800,"k":0.0025},{"name":"mm-imp","dir":"imp","preset":"toon","w":700,"h":800,"k":0.0025},
  {"name":"mm-monster","dir":"monster","preset":"mm","w":800,"h":700,"k":0.0025,"u0":500}]' $W
# frames: add "frames":60,"yaw":-0.45 (bear-wave) / "frames":96,"yaw":0.6 (walk); then ffmpeg -framerate 24 ... libx264 yuv420p
```

The pictures in `pics/` are crops and rows of these renders (webp), the videos h264 at 24 fps.

## Sources and licences

- Monster Mash — https://github.com/google/monster-mash, `src` Apache-2.0; its third-party code under its own licences.
  Not copied here; only rendered results and our harness (which compiles against a checkout).
- Triangle (J. R. Shewchuk) — http://www.netlib.org/voronoi/triangle.zip; free for non-commercial use only (its own
  licence); needed to build Monster Mash, kept in the cache, not in the repository.
- The matcap `matcapOrange.jpg` is Monster Mash's own (its `data/`), used for the `mm` look; kept in the cache.
- The characters are ours (П1, П2).
