# Р2, the fast page

`tools/web/fast.html` (`view-gpu.mjs`, `face-gpu.mjs`) is this character's page with the skin skinned and the face
worked out on the video card (`engine-gpu/`, its README). `tools/web/view.html` (`view.mjs`, `face.mjs`) is the page
as it was; both run, with the same controls. `life.mjs` is shared by both, unchanged.

What took the time in `view.mjs`, every frame, for each of 48 thousand vertices, in JavaScript: the skinning (dual
quaternions) — about two thirds; the engine's normals, which this flat-coloured page never used — a sixth; the face's
fields over its 18 thousand vertices — a tenth when the face is calm, a quarter when it speaks with an
expression; copying and sending every place. The line, found on the screen from two pictures twice the screen's size,
is the video card's work and is as it was.

What differs from `view.mjs` and `face.mjs`:
- the skin's places are worked out on the video card each frame (engine-gpu); both looks (the flat colour; the piece
  and depth for the line) read them; the processor works out the joints;
- the face is in the vertex shader of both looks: `face-gpu.mjs` is `face.mjs`'s fields written in GLSL — from each
  vertex's rest place, its piece (an attribute) and the face's numbers (a uniform) — and the shader adds the
  displacement, turned with the head, to the skinned place, as `face.mjs`'s `apply()` did. The processor only sets
  the numbers and the head's turn. (engine-gpu's normals do not know of the face; this page does not use normals.)
- the floor (`motion.floor: 'lowest'`) is found from a probe of the skin (engine-gpu's README): within 0.4 mm of
  the old over walk, sit, bow, dance, jump and run;
- nothing is sent to the video card each frame but the joints, the head's turn and the face's numbers.

What is seen: the same drawing — colours, line, face. Compared picture by picture (standing; walking from the front
and the back; a bow from the side; sitting; the face close — calm, joy while speaking, sad, surprise), 0.001–0.002 % of a
picture differs: points along the line.

Speed on a laptop with an Intel Arc 140T at 1920×1080, walking, measured roughly (other pages used the machine at the
same time): the main thread 17 → 2.8 ms a frame; speaking with an expression 18 → 2.8 ms a frame. Frames a second did not rise with it (56–58 before and 54–57 after): the processor is
nearly free now, so what holds this page is the video card — the line's two large pictures and the filter over them,
or the other pages measured beside it; that was not looked into. What is left on the processor: the floor's probe
(12 thousand vertices, 1.5–2 ms).

To check again: open both pages, pause both, choose the same motion and set the same time and expression, compare
the canvases. (`engine-gpu/check/compare.mjs` wants `window.A`, which these pages do not have.)
