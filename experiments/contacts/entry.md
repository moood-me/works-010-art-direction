# К1 — касания: руки приходят на место

**Folder:** `experiments/contacts/` · **page:** `experiments/contacts/index.html` · **grew from:** the early engine
(`engine/`, Д1) and its Anny bodies.

**What it is.** A person walks up and touches a place in the scene — leans on a table with both hands, puts a hand
on another person's shoulder, sits in an armchair with the hands on the armrests. The place is given to Kimodo as its
own hand constraint (a whole pose: the palms on their places, the pelvis where the person stands or sits); Kimodo
makes the walk, the lean, the sitting, the elbows; a small arm correction takes the palm the last 4–6 cm on our body.

**Verdict.** The principle works for all three of Pavel's scenes: Kimodo itself brings the hands within 2–3 cm in
its own space, 4–6 cm on our bodies, and the correction puts the palm exactly on the table top, the armrest, the
shoulder. The table is the best: a natural walk, stop and lean. The shoulder works but the man's arm comes up nearly
level, a little stiff, and his hand passes 1–2 cm into the edge of her shoulder for a few frames on the way. The
armchair works; the chair is boxes, and she sits with the knees wide. Without the constraints Kimodo does none of
these (it sits at the table, stands without leaning, doesn't walk to the other person).

**Pictures** (best first):

- `pics/table-sheet.png` — стол: подходит, останавливается, опирается руками; сбоку и с другой стороны.
- `pics/table-close.png` — руки на столе близко: как Kimodo (ладони висят над столом на 4–5 см) и с поправкой.
- `pics/table-side.mp4`, `pics/table-whole.mp4` — стол, фильмы с двух сторон.
- `pics/shoulder-sheet.png` — рука на плечо: подходит и кладёт руку ей на плечо; с двух сторон.
- `pics/shoulder-close.png` — ладонь на плече близко: как Kimodo и с поправкой.
- `pics/shoulder-side.mp4`, `pics/shoulder-whole.mp4` — плечо, фильмы с двух сторон.
- `pics/armchair-sheet.png` — кресло: подходит, поворачивается, садится, руки на подлокотники; с двух сторон.
- `pics/armchair-close.png` — руки на подлокотниках близко: как Kimodo и с поправкой.
- `pics/armchair-side.mp4`, `pics/armchair-whole.mp4` — кресло, фильмы с двух сторон.
- `pics/table.png`, `pics/shoulder.png`, `pics/armchair.png` — по одному кадру каждой сцены.
