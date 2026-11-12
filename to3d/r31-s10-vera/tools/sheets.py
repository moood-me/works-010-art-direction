"""The drawing's own sheets that the style's page doesn't have for this character — the turnaround (front, three
quarters, profile) and the expressions — drawn by the style's code as it is (styles/s10-ligne-claire/tools/build.py),
into CACHE/draw/ (nothing is written into the style's folder).
usage: python3 sheets.py CACHE [turn] [expr]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import who                                   # noqa: E402
C, what = sys.argv[1], sys.argv[2:] or ['turn', 'expr']
sys.argv = sys.argv[:1]
import lc, build                             # noqa: E402
out = os.path.join(C, 'draw')
os.makedirs(out, exist_ok=True)
for name, fn in (('turn', lambda: build.turnaround(who.ID)), ('expr', lambda: build.expressions(who.ID))):
    if name in what:
        d = fn()
        p = os.path.join(out, f'{name}-{who.ID}.svg')
        d.save(p)
        lc.render(p, p.replace('.svg', '.png'), d.w, d.h)
        print(p)
