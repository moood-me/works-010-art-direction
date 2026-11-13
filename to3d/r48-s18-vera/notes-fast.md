# Р48, the fast page

`tools/web/fast.html` (`vera-fast.js`) is this character's page made to hold up its drawing without stopping the page.
`tools/web/view.html` (`vera.js`) is the page as it was; both run, both take the same `window.A.set({...})`.

The page draws the figure anew about 12 times a second (the ui's own pace). What took the time of a drawing in the old
page, measured in Chrome's profiler:
- the tone: every pixel of the whole page (1920×1080) was unpacked from the unseen picture and gone through for its
  band, shadow and screentone. 30–35 ms;
- waiting for the video card: the unseen picture was read back with `readPixels`, which stops the page until the card
  has finished everything before it. 10–25 ms.

What differs from `vera.js`:
- the unseen picture is read back, and the tone made, only in a rectangle of the page: the figure's, and as far to the
  right of it and below as its black band falls; the tone's dots stay fixed to the page;
- the read-back does not stop the page: the picture is copied into a buffer on the card and taken when the card says
  it is done. So `A.render()` gives a promise (it is done when the drawing is on the page), and `A.set()` waits for a
  drawing begun before it.

What is seen: the same pictures — six moments (stand, walk, sit, dance, run, the face close) differ from the old page
in no pixel. Speed on a laptop with an Intel Arc 140T at 1920×1080, walking, the machine busy with other work: the old
page stops for 55–65 ms at every drawing, 30–35 frames a second between the stops; the fast page works about 30 ms a
drawing and keeps 60 frames a second; both make 10–11 drawings a second.

What is still heavy: the figure is skinned and its lines found on the processor (the lines need every vertex's place
in the picture), about 10 ms a drawing. With the camera close the rectangle is the whole page, and the tone costs as
before. The backdrop (`sky`), when asked for, is still toned over the whole page at every drawing; the ui does not ask
for it.

To check again: old page against fast page at the same moments, by screenshots of the page in real Chrome at
1920×1080 (the picture is an SVG or a 2D canvas over a hidden WebGL canvas, so `engine-gpu/check/compare.mjs`, which
takes the WebGL canvas, does not see it); `await A.render()` before each screenshot.
