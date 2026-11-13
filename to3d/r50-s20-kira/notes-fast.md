# Р50, the fast page

`tools/web/fast.html` (`kira-fast.js`) is this character's page made to hold up its drawing without stopping the page.
`tools/web/view.html` (`kira.js`) is the page as it was; both run, both take the same `window.A.set({...})`.

The page draws the figure anew about 12 times a second (the ui's own pace). What took the time of a drawing in the old
page, measured in Chrome's profiler:
- the paint's masks: for every paint (and the hatching) the whole page was gone through pixel by pixel, and the mask
  taken from a canvas kept on the video card (`toDataURL` waits for the card). About 100 ms;
- waiting for the video card: the unseen picture was read back with `readPixels`, which stops the page until the card
  has finished everything before it. 20–50 ms.

What differs from `kira.js`:
- the unseen picture is read back, and the masks made, only in the figure's rectangle of the picture;
- the read-back does not stop the page: the picture is copied into a buffer on the card and taken when the card says
  it is done. So `A.render()` gives a promise (it is done when the drawing is on the page), and `A.set()` waits for a
  drawing begun before it;
- the masks' canvas is kept in memory (`willReadFrequently`).

What is seen: the same pictures — six moments (stand, walk, sit, dance, run, the face close) differ from the old page
in no pixel. Speed on a laptop with an Intel Arc 140T at 1920×1080, walking, the machine busy with other work: the old
page stops for 145–175 ms at every drawing and makes 5–7 of them a second, nothing moving between; the fast page works
30–45 ms a drawing, keeps 60 frames a second and makes 10–11 drawings a second.

What is still heavy: the masks are still gone through once for every paint (ten times over the figure's rectangle),
and the picture is an SVG the browser paints anew for every drawing. With the camera close the figure's rectangle is
the whole page, and the masks cost as before. To make this medium cheap in a game's scene it would have to be painted
by shaders: another renderer, not done.

To check again: old page against fast page at the same moments, by screenshots of the page in real Chrome at
1920×1080 (the picture is an SVG or a 2D canvas over a hidden WebGL canvas, so `engine-gpu/check/compare.mjs`, which
takes the WebGL canvas, does not see it); `await A.render()` before each screenshot.
