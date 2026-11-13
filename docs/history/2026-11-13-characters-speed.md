# The Р characters' speed: skinning on the video card (2026-11-13)

Branch `perf-characters`, not merged into `main`: Pavel merges.

**What called for it.** Pavel asked what the speed would be if the drawn characters built in 3D (section Р) were put
into a real scene of a game. An agent read the code and measured two pages on a server without a video card: the
skinning, the normals and more are computed in JavaScript for every vertex every frame, about 8 ms a character.
Pavel then asked an agent on his own computer (it has a video card) to make the characters work properly for speed,
in a worktree of its own, deciding itself: "Если что-то очень сложно, пускай в стену не бьётся. Идеальная точность
там тоже не нужна. Пускай оптимизирует, пускай решает сама." Code and code review by Fable, looking and testing by
Opus subagents.

**How it was measured.** Real Chrome on Pavel's laptop (Intel Core Ultra 7 255H, Intel Arc 140T), a 1920×1080 page,
the machine otherwise idle (3–8 % of the processor). Not the software renderer: its numbers say nothing here.

**All 50 pages as they were**, each playing «шаг» where it has it, 4 seconds: the main thread's milliseconds a frame
(of them script), frames a second.

| Pages | Main thread, ms a frame | Frames a second | What it is |
|---|---|---|---|
| Р4, Р21, Р22, Р39–Р44, Р46, Р49 | 1–2 | 60 | fast already |
| Р3, Р6, Р13, Р14, Р29, Р30 | 4–7, script almost none | 60 | not looked into |
| Р11, Р33, Р34 | 5–7 | 60 | not looked into |
| Р17, Р18 | 4 | 60 | skinning on the processor |
| Р1, Р45 | 7 | 60 | skinning on the processor |
| Р7, Р15, Р16, Р19, Р20 | 8–10 | 60 | skinning on the processor |
| Р2, Р9 | 11–13 | 60 | skinning on the processor |
| Р25, Р26, Р47 | 14–15 | 53–60 | skinning on the processor |
| Р10 | 16 | 60 | skinning on the processor |
| Р31, Р32 | 19–20 | 49–53 | skinning on the processor |
| Р27, Р28 | 25–32 | 31–41 | skinning on the processor |
| Р8, Р23, Р24 | 1–2 | 15–16 | the video card is busy, not the processor: not looked into |
| Р12, Р35, Р48 | 11–36, script 1–2 | 23–48 | not the script: not looked into |
| Р36, Р37, Р38, Р50 | 110–140, script 3–5 | 7–9 | not the script: not looked into |

(Р5's page did not start in the survey: a 404 on one of its files.)

**What was made.** `engine-gpu/` beside `engine/` (its README says how to use it and what is the same and what is
not): the engine's skinning — centres of rotation, dual quaternions, linear — in the vertex shader, with the
Skinner's own centres as an attribute and the joints in a small texture; normals are the rest's, turned with the
joints; the floor from a probe of the skin; and a way to keep a few vertices on the processor for what a page does
to the posed skin (a skirt pushed off the legs).

**Р45 (Аня, нуар) as the first page**: `to3d/r45-s15-anya/tools/web/fast.html` with `anya-gpu.js`, beside
`view.html` and `anya.js`, which are as they were. Besides the skinning: the face's canvas is redrawn and sent to the
video card only when the face's numbers changed; the skirt's push is computed for the skirt's points only, with flat
arrays, and skipped when no point is in a leg; the canvas's size is set only when it changed (set anew each frame, the
browser allocates the picture anew). The `morph` option was dropped in the fast page: the pack has no morphs.

**Checked.**
- The processor's skinning of a few vertices against the engine's own: the same to 0.0005 mm. The floor probe against
  all vertices over walk, sit, dance, lie, roll, jump, bow: 1.5 mm at worst, 0.05 mm on average.
- Old page against fast page, the same eight moments (stand, walk, sit, wave, dance, bow, run, the face close), pixel
  by pixel: 0.07–0.37 % of the picture differs — the antialiased outline everywhere, and the black's edge on the skirt
  and on the jacket's folds lying a few pixels differently (the normals are not recomputed from the posed triangles).
- Speed of Р45, walking: the processor 5.3 → 1.7 ms a frame.
- Several characters of Р45's size (38 thousand vertices) walking in one scene, `engine-gpu/bench/`, drawn as the Р
  pages draw (a shadow map, the body, an outline):

| Characters | The old way: frames a second (processor, ms) | The new way |
|---|---|---|
| 1 | 60 (3.8) | 60 (0.6) |
| 2 | 60 (7.4) | 60 (1.6) |
| 4 | 56 (17) | 60 (2.8) |
| 9 | 25 (38) | 60 (5.5) |
| 16 | 14 (71) | 60 (9.6) |

**How to repeat.** `engine-gpu/check/compare.mjs` (a page against its fast variant: pictures, difference, speed) and
`engine-gpu/check/bench.mjs` (the table above); both open real Chrome and need `playwright` (`PLAYWRIGHT_FROM`).

**Not done.** A phone was not measured. Hair and clothes were not thinned: with the skinning on the video card the
number of vertices hardly matters on this machine.
