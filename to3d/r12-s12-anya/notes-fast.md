# Р12, the fast page

`tools/web/fast.html` (`anya-fast.js`, `pen-fast.js`) is this character's page made to hold up its drawing without stopping the page.
`tools/web/view.html` (`anya.js`) is the page as it was; both run, both take the same `window.A.set({...})`.

The page draws the figure anew about 12 times a second (the ui's own pace: a drawing held for two frames). What took
the time of a drawing in the old page, measured in Chrome's profiler:
- waiting for the video card: the unseen picture (which wash a pixel belongs to, how far it is) was read back with
  `readPixels`, which stops the page until the card has finished everything before it — also the last drawing's SVG
  with its watercolour filters. 20–50 ms;
- the pen: every stroke made four tables of 512 random numbers for its noise and used a few of them. 20–35 ms;
- the washes' masks: made over the whole page, and each taken from a canvas kept on the video card (`toDataURL`
  waits for the card again). 15–25 ms.

What differs from ``anya.js``:
- the unseen picture is read back, and the masks made, only in the figure's rectangle of the picture;
- the read-back does not stop the page: the picture is copied into a buffer on the card and taken when the card says
  it is done. So `A.render()` gives a promise (it is done when the drawing is on the page), and `A.set()` waits for a
  drawing begun before it;
- the masks' canvas is kept in memory (`willReadFrequently`);
- `pen-fast.js`: a number of a stroke's noise is worked out when the stroke asks for it — the same numbers as the
  tables had, so the same strokes.

What is seen: the same pictures — six moments (stand, walk, sit, dance, run, the face close) differ from the old page
in no pixel. Speed on a laptop with an Intel Arc 140T at 1920×1080, walking, the machine busy with other work: the old
page stops for 45–90 ms at every drawing, 18–47 frames a second between the stops, 9–11 drawings a second; the fast page works 15–25 ms a drawing, the page keeps 56–60 frames a second, 10–11 drawings a second.

What is still heavy: the picture is an SVG the browser paints anew for every drawing, with the watercolour's filters
(turbulence, displacement, erosion) for every wash — the video card's work, about 20 ms a drawing, now beside the
page instead of in front of it. With the camera close the figure's rectangle is the whole page, and the masks cost as
before. To make this medium cheap in a game's scene it would have to be painted by shaders instead of SVG filters:
another renderer, not done.

To check again: old page against fast page at the same moments, by screenshots of the page in real Chrome at
1920×1080 (the picture is an SVG or a 2D canvas over a hidden WebGL canvas, so `engine-gpu/check/compare.mjs`, which
takes the WebGL canvas, does not see it); `await A.render()` before each screenshot.
