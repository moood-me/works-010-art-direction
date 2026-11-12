# К1 — касания: руки приходят на место

**Folder:** `experiments/contacts/` · **page:** `experiments/contacts/index.html` · **grew from:** the early engine
(`engine/`, Д1) and its Anny bodies.

**What it is.** A person walks up and touches a place in the scene — leans on a table with both hands, puts a hand
on another person's shoulder, sits in an armchair with the hands on the armrests. The place is given to Kimodo as its
own hand constraint (a whole pose: the palms on their places, the pelvis where the person stands or sits); Kimodo
makes the walk, the lean, the sitting, the elbows; a small arm correction takes the palm the last 4–8 cm on our body.

**Verdict.** The principle works for all three of Pavel's scenes: Kimodo itself brings the hands within 2–3 cm in
its own space, 4–8 cm on our bodies, and the correction puts the palm on the table top, the armrest, the shoulder.
The table is the best: a natural walk, stop and lean. The shoulder, second try: he stands beside her, off her
shoulder, the elbow bent and hanging, the hand on top of the shoulder — natural, but he looks over her head, not at
her (Kimodo keeps the head up; two prompts tried). The armchair, second try: the knees nearly together (20–29 cm,
was 48), but Kimodo's hands drift off the armrests between the held frames and the correction takes up to 11 cm; the
chair is boxes. Without the constraints Kimodo does none of these. The first versions of the shoulder and the
armchair are kept beside on the page (weaker: chest to chest with a level arm; knees wide).

**Pictures** (best first):

- `pics/table-sheet.png` — стол: подходит, останавливается, опирается руками; сбоку и с другой стороны.
- `pics/table-close.png` — руки на столе близко: как Kimodo (ладони висят над столом на 4–5 см) и с поправкой.
- `pics/table-side.mp4`, `pics/table-whole.mp4` — стол, фильмы с двух сторон.
- `pics/shoulder2-sheet.png` — плечо, вторая попытка: встаёт сбоку от неё, локоть согнут, ладонь на верху плеча; с двух сторон.
- `pics/shoulder2-close.png` — ладонь на плече близко: как Kimodo и с поправкой.
- `pics/shoulder2-front.mp4`, `pics/shoulder2-whole.mp4` — плечо, вторая попытка, фильмы с двух сторон.
- `pics/armchair2-sheet.png` — кресло, вторая попытка: садится, колени почти вместе; сбоку и спереди.
- `pics/armchair-knees.png` — колени спереди: первая попытка (48 см) и вторая (20 см в удерживаемых кадрах, 29 см между ними).
- `pics/armchair2-close.png` — руки на подлокотниках близко: как Kimodo (руки приподняты над ними) и с поправкой.
- `pics/armchair2-side.mp4`, `pics/armchair2-front.mp4` — кресло, вторая попытка, фильмы с двух сторон.
- `pics/armchair-sheet.png`, `pics/armchair-close.png`, `pics/armchair-side.mp4`, `pics/armchair-whole.mp4` — кресло, первая попытка (колени широко).
- `pics/shoulder-sheet.png`, `pics/shoulder-close.png`, `pics/shoulder-side.mp4`, `pics/shoulder-whole.mp4` — плечо, первая попытка (стоит грудь к груди, рука прямой планкой).
- `pics/table.png`, `pics/shoulder2.png`, `pics/armchair2.png`, `pics/shoulder.png`, `pics/armchair.png` — по одному кадру каждой сцены.
