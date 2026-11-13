# Р24, the fast page

`tools/web/fast.html` (`app-fast.js`, `figure-fast.js`) is this character's page with the scene's picture not
multisampled. `tools/web/view.html` (`app.js`, `figure.js`) is the page as it was; both run, both take the same
`window.A`.

What took the time: the video card, not the processor. The page draws everything twice larger (3840×2160 for a
1920×1080 page) and averages it down, so the rim cut from the figure's mask is smooth; and the scene's picture at that
size was multisampled four times besides — sixteen samples a pixel of the page. Switching the passes off one by one:
without the scene's pass a frame takes 17 ms instead of 250 (the card shared with other work); with the scene's
picture not multisampled, 15–21 ms. The figure's pass, the composite and the averaging down cost little.

What differs from `figure.js`: one thing — the scene's render target has no `samples: 4`. Four samples a pixel stay
(drawn twice larger, averaged down).

What is seen: the same picture; 0.001–0.05 % of its pixels differ, on edges. Enlarged four times, a long thin line
that is nearly upright or nearly level (a window's bar) has small steps where it was even.

Speed on a laptop with an Intel Arc 140T at 1920×1080, walking, the card busy with other work: 11 frames a second →
60 (15–16 when the survey was made on an idle machine).

To check again: `node engine-gpu/check/compare.mjs <jobs.json> <outdir>` with `old` the `view.html?shots=1` and `new`
the `fast.html?shots=1`, each shot's `set` with `"size": [1920, 1080]` (docs/history/2026-11-13-characters-speed.md).
