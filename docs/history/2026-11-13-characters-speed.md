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

(Р5's page needs `?pack=../../data/anya.json` in its address, as its `entry.json` gives it; the survey opened it
without and it did not start. The two rows marked "not the script" were wrong: see below.)

**What was made.** `engine-gpu/` beside `engine/` (its README says how it works, how to use it, what is the same and
what is not): each frame the posed skin is drawn into two small float textures — every vertex's place (the engine's
skinning: centres of rotation, dual quaternions, linear), then every vertex's normal from the posed triangles around
it (the engine's `normalsOf`) — and the materials that draw the skin only read them. The processor works out the
joints, the floor from a probe of the skin, and whatever a page does to a few vertices of the posed skin (a skirt
pushed off the legs, a face's forms), given as offsets.

The first version skinned in each material's vertex shader and turned the rest's normals with the joints. Eighteen
pages were made on it and compared with their old pages: the light lay differently on cloth and at bends — a fold on
Р16's apron between the legs nearly went, the shade on Р9's skirt and cardigan lay elsewhere. That is the forms'
fineness the requirements ask for, so the module was changed to the two textures and the pages moved to it; they
now match their old pages.

**Fast pages, beside the old ones.** For 30 characters: `tools/web/fast.html` with fast copies of the scripts that
had to change, and `notes-fast.md` in the character's folder (what took the time, what differs, what is seen). The
old pages and their scripts are untouched. `entry.json` and `items.json` are untouched too: the catalogue still
opens the old pages.

- *Skinning on the processor → engine-gpu*: Р1, Р17, Р18 (С3), Р5, Р15, Р16 (С2), Р7, Р19, Р20 (С4), Р9, Р25, Р26
  (С7), Р10, Р27, Р28 (С8), Р2, Р31, Р32 (С10), Р45, Р47. Beside the skinning, where a page did it: the face's canvas
  redrawn and sent only when the face changed; the canvas's size set only when it changed; a skirt's push computed
  for the skirt's points only; the face's forms as offsets for the vertices they move.
- *Pen, watercolour, print, manga* (Р12, Р35, Р36 — С12; Р37, Р38 — С13; Р50; Р48): the survey's reading was wrong —
  the time is script: one drawing took 45–175 ms and the page froze for it (these pages draw about 12 times a second
  on purpose). The page was read back whole from the video card, waiting for it, and masks and tones were made over
  the whole page. Now: only the figure's rectangle, a read-back that does not stop the page, the pen's noise worked
  out only when asked. The pictures are the same to the pixel. Skinning stays on the processor there (the lines are
  found from every vertex's place).
- *Р8, Р23, Р24 (С6)*: the video card was busy — everything is drawn at twice the page's size and averaged, and the
  scene's target was multisampled ×4 on top. The multisampling was taken off; the 2× stays. Enlarged four times, a
  long thin nearly upright line shows small steps; not looked at in motion.

**Checked.** Each fast page against its old page at 6–12 moments (stand, walk, sit, bow, dance, run, the face close,
the back), pixel by pixel, in real Chrome, and the largest differences looked at by eye. On the new module the pages
match: most moments differ in 0–15 pixels of the page; where more (up to 0.4 %; Р10 sitting 1 %), it is the whole
outline a part of a pixel off, from the floor. Р45 was also watched in motion by an Opus agent, old against fast, on
the first version: nothing flickers or jumps.

**The floor is the weak place.** `gs.lowest(pose)` skins a probe of 6–15 thousand vertices on the processor. It is
within 0.5 mm on most pages and 1–2.6 mm at worst on Р1, Р9, Р10, Р15, Р16, Р20 (dancing, sitting, lying), so there
the figure stands a part of a pixel off (Р10 sitting: a pixel). It is also the largest thing left for the processor.
Finding it exactly on the video card would give it to the processor a frame late, and what rides on the joints
needs it at once.

**Speed after**, the same survey (the page as a viewer has it, «шаг», 1920×1080, the machine idle): the main thread's
milliseconds a frame, frames a second, the longest gap between frames in 4 seconds.

| Page | Main thread, ms: was → is | Frames a second: was → is | Longest gap, ms: was → is |
|---|---|---|---|
| Р1 | 7.4 → 4.0 | 60 → 60 | 21 → 19 |
| Р2 | 12.7 → 3.1 | 51–60 → 49–51 | 22–51 → 41–51 |
| Р7 | 8.8 → 4.7 | 60 → 60 | 20 → 20 |
| Р8 | 1.4 → 1.8 | 15 → 60 | 71 → 19 |
| Р9 | 11.2 → 5.6 | 60 → 60 | 20 → 20 |
| Р10 | 16.5 → 3.1 | 60 → 60 | 32 → 20 |
| Р12 | 28.7 → 4.2 | 29 → 60 | 110 → 27 |
| Р15 | 8.3 → 2.7 | 60 → 60 | 22 → 24 |
| Р16 | 9.6 → 3.2 | 60 → 60 | 21 → 19 |
| Р17 | 4.2 → 2.8 | 60 → 60 | 21 → 18 |
| Р18 | 4.2 → 2.7 | 60 → 60 | 20 → 18 |
| Р19 | 8.5 → 4.8 | 60 → 60 | 22 → 20 |
| Р20 | 9.5 → 4.9 | 60 → 60 | 21 → 21 |
| Р23 | 1.3 → 1.8 | 16 → 60 | 68 → 18 |
| Р24 | 2.2 → 3.3 | 16 → 60 | 66 → 19 |
| Р25 | 14.6 → 3.6 | 60 → 60 | 20 → 20 |
| Р26 | 14.6 → 3.6 | 60 → 60 | 19 → 19 |
| Р27 | 24.7 → 3.7 | 41 → 60 | 36 → 19 |
| Р28 | 32.2 → 3.5 | 31 → 60 | 39 → 20 |
| Р31 | 19.1 → 3.3 | 50–55 → 47–52 | 31–52 → 37–51 |
| Р32 | 20.4 → 3.6 | 49 → 51 | 29 → 39 |
| Р35 | 36.2 → 7.8 | 23 → 55 | 111 → 49 |
| Р36 | 128 → 9.7 | 8 → 53 | 194 → 75 |
| Р37 | 109 → 4.9 | 9 → 60 | 118 → 27 |
| Р38 | 137 → 5.3 | 7 → 60 | 155 → 27 |
| Р45 | 6.8 → 4.2 | 60 → 60 | 20 → 20 |
| Р47 | 13.9 → 4.7 | 53 → 53 | 32 → 37 |
| Р48 | 11.2 → 5.1 | 48 → 60 | 79 → 32 |
| Р50 | 143 → 5.9 | 7 → 60 | 149 → 31 |

Р5 (driven by script, walking): the processor 2.4 → 0.8 ms a frame. The main thread's number is the whole page — its
controls, the live face, three.js — not the skinning alone.

Р2, Р31, Р32 and Р47 stay near 50 frames a second, as before, with the processor now nearly free: the video card
is busy with the style itself (the line found from pictures twice the page's size; Р47's piece picture at twice the
size, multisampled). Р35 and Р36 still have gaps of 50–75 ms. None of that was looked into further.

**Several characters in one scene** — `engine-gpu/bench/`: characters of Р45's size (38 thousand vertices) walking,
drawn as the Р pages draw (a shadow map, the body, an outline's hull). Frames a second (the processor's ms a frame):

| Characters | The old way | engine-gpu |
|---|---|---|
| 1 | 60 (3.8) | 60 (1.6) |
| 4 | 56 (17) | 60 (4.3) |
| 9 | 25 (38) | 60 (7.4) |
| 16 | 14 (71) | 60 (12.5), one gap of 33 ms in 4 s |

**How to repeat.** `engine-gpu/check/compare.mjs` (a page against its fast variant: pictures, difference, speed; it
needs `window.A` with `set` and `render`, which not all pages have) and `engine-gpu/check/bench.mjs` (the table
above); both open real Chrome and need `playwright` (`PLAYWRIGHT_FROM`).

**Who did what.** The module, Р45, Р47's move to the new module, the measuring: the orchestrator (Fable). The other
pages: four Fable agents, a family or two each, each returning with what differed and what it doubted. Looking at
Р45 in motion: an Opus agent.

**Not done.** A phone was not measured. Hair and clothes were not thinned: with the skinning on the video card the
number of vertices hardly matters on this machine. Р3, Р6, Р11, Р13, Р14, Р29, Р30, Р33, Р34 (4–7 ms a frame, 60
frames a second) were not looked into. The SVG pages (С12, С13, Р50) still have the browser repaint their SVG with
its filters for every drawing; cheap inside a game's scene would mean painting the medium with shaders — another
renderer. The fast pages were compared as stills (but Р45); in motion they were not watched. The catalogue does not
show the fast pages.
