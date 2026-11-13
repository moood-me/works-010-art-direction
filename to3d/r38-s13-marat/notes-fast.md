# Р38, the fast page

`tools/web/fast.html` (`print-fast.js`, `kit-fast.js`, `char-fast.js`) is this character's page made to hold up its
printing without stopping the page. `tools/web/view.html` (`print.js`) is the page as it was; both run, both take the
same `window.A.set({...})`.

The page prints the figure anew about 12 times a second (the ui's own pace). What took the time of a printing in the
old page, measured in Chrome's profiler:
- the colour blocks: a picture of the whole page (1920×1080) was filled pixel by pixel and packed into a PNG
  (`toDataURL`) — once for the blocks, once for the skin's mask, once for every cloth pattern's mask. 80–120 ms;
- waiting for the video card: the unseen picture was read back with `readPixels`, which stops the page until the card
  has finished everything before it. 20–50 ms.

What differs from `print.js`:
- the unseen picture is read back, and the blocks' and masks' pictures made, only in the figure's rectangle of the
  picture; each is put at its place in the page (`kit-fast.js` differs from `kit.js` in this only: `pattern()` takes
  the mask with its rectangle);
- the read-back does not stop the page: the picture is copied into a buffer on the card and taken when the card says
  it is done. So `A.render()` gives a promise (it is done when the print is on the page), and `A.set()` waits for a
  printing begun before it;
- the pictures' canvas is kept in memory (`willReadFrequently`).

What is seen: the same pictures — six moments (stand, walk, sit, dance, run, the face close) differ from the old page
in no pixel. Speed on a laptop with an Intel Arc 140T at 1920×1080, walking, the machine busy with other work: the old
page stops for 130–175 ms at every printing and makes 5–7 of them a second, nothing moving between; the fast page
works 25–40 ms a printing, keeps 60 frames a second and makes 10–11 printings a second.

What is still heavy: the picture is an SVG the browser paints anew for every printing — the sheet's grain, paper and
age are filters over the whole page. With the camera close the figure's rectangle is the whole page, and the blocks
cost as before. To make this medium cheap in a game's scene it would have to be painted by shaders: another renderer,
not done.

To check again: old page against fast page at the same moments, by screenshots of the page in real Chrome at
1920×1080 (the picture is an SVG or a 2D canvas over a hidden WebGL canvas, so `engine-gpu/check/compare.mjs`, which
takes the WebGL canvas, does not see it); `await A.render()` before each screenshot.
