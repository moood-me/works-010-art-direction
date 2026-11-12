"""What the page needs from the style's own code (styles/s16-pixel/tools), written to web/data.js:
RAMPS — the palette (pal.py); DRAWN — Савелий's three drawn sprites with their outline, as rows of colour keys
(for the comparisons); PFACE — the portrait's face features for each expression (eyes, brows, nose, cheeks, wrinkles,
moustache, mouth), the lines of chars/savely.py's portrait() run on an empty canvas instead of on its typed head;
PATCH — what changes in such a layer for a blink, a look to the side, a mouth open in speech (lists of x, y, key);
PBODY — the portrait's shirt front, bow tie and buttons; PORTRAIT — the drawn portraits, framed.    python3 gen.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STY = os.path.join(HERE, '../../../styles/s16-pixel/tools')
sys.path.insert(0, STY); sys.path.insert(0, os.path.join(STY, 'chars'))
import pal            # noqa: E402
import portrait as P  # noqa: E402
import sprite         # noqa: E402
import savely         # noqa: E402

EXPRS = ['rest', 'joy', 'surprise', 'sadness', 'anger']


def rows(c):
    return [[k or '' for k in r] for r in c.g]


def features(expr, eye=None, mouth=None):
    """chars/savely.py portrait(): the part between the head's shading and the loupe, on an empty canvas.
    Blobs are put unconditionally (there is no typed skin under them here); the dome's shine is left to the 3D."""
    f = P.new()
    for x0, x1, y in [(20, 26, 16), (29, 35, 16), (22, 33, 18)]:                             # wrinkles
        f.hline(x0, x1, y, 's2')
    rows_eye = {'rest': ["KKKK", "ikEi", ".tt."], 'joy': [".KK.", "K..K", "...."], 'surprise': ["KKKK", "iEki", "iEki", ".tt."],
           'sadness': ["KK..", "ikKK", ".tt."], 'anger': ["..KK", "KKki", ".tt."]}[expr]
    leg = {'K': 'b1', 'i': 'w3', 'k': 'x0', 'E': 'u2', 't': 's2'}
    if eye == 'blink':                                   # ours: the lid down — a dark line where the eye's middle was
        P.eyes(f, 19, 25, ["....", "KKKK", ".tt."] if expr != 'surprise' else ["....", "....", "KKKK", ".tt."], leg)
    elif eye in ('l', 'r'):                              # ours: both eyes look to one side (rest only)
        a, b = (["KKKK", "kEii", ".tt."], ["KKKK", "Ekii", ".tt."]) if eye == 'l' else (["KKKK", "iikE", ".tt."], ["KKKK", "iiEk", ".tt."])
        f.stamp(19, 25, a, leg); f.stamp(2 * P.CX - 19 - 4, 25, b, leg)
    else:
        P.eyes(f, 19, 25, rows_eye, leg)
    P.both(f, 's2', [(17, 28), (18, 29), (19, 29), (20, 29), (21, 29), (22, 29), (23, 28), (16, 25), (15, 24), (16, 27)])
    brow = {'rest': [(15, 21), (16, 20), (17, 20), (18, 20), (19, 20), (16, 21), (17, 21), (18, 21), (19, 21), (20, 21),
                     (21, 21), (20, 22), (21, 22), (22, 22), (23, 22), (22, 23), (23, 23), (24, 23)],
            'joy': [(15, 20), (16, 19), (17, 19), (18, 19), (19, 19), (20, 19), (21, 19), (22, 20), (23, 20), (16, 20),
                    (17, 20), (18, 20), (19, 20), (20, 20), (21, 20), (23, 21), (24, 21)],
            'surprise': [(15, 18), (16, 17), (17, 17), (18, 17), (19, 17), (20, 17), (21, 17), (22, 18), (23, 18),
                         (16, 18), (17, 18), (18, 18), (19, 18), (20, 18), (21, 18), (23, 19), (24, 19)],
            'sadness': [(15, 23), (16, 23), (17, 22), (18, 22), (19, 22), (20, 21), (21, 21), (22, 20), (23, 20), (24, 19),
                        (16, 22), (18, 21), (19, 21), (21, 20), (22, 19), (23, 19)],
            'anger': [(15, 19), (16, 19), (17, 20), (18, 20), (19, 21), (20, 21), (21, 22), (22, 22), (23, 23), (24, 23),
                      (16, 20), (17, 21), (18, 21), (19, 22), (20, 22), (21, 23), (22, 23), (23, 24), (24, 24), (25, 24)]}
    brow = brow.get(expr, brow['rest'])
    P.both(f, 'w3', brow)
    low = {}
    for x, y in brow:
        low[x] = max(low.get(x, 0), y)
    P.both(f, 'w1', [(x, y + 1) for x, y in low.items() if (x, y + 1) not in brow])
    f.vline(30, 24, 29, 's2'); f.spans(29, [(26, 30), (25, 31), (25, 31), (25, 31), (26, 30)], 'z2')
    f.pxs('s4', (26, 30), (27, 30), (26, 31)); f.pxs('s1', (25, 33), (30, 33), (31, 32)); f.pxs('s2', (24, 31), (32, 31), (24, 32))
    P.blob(f, 16, 31, ['.###.', '#####', '.###.'], 'z0'); P.blob(f, 35, 31, ['.###.', '#####', '.###.'], 'z0')
    f.pxs('w1', (8, 21), (9, 22), (7, 26), (8, 27), (9, 30), (46, 22), (47, 23), (45, 27), (46, 28), (44, 31))     # flecks in the tufts (its `back` layer)
    m = P.new()
    lift = {'joy': -1}.get(expr, 0)
    m.spans(34 + lift, [(22, 33), (18, 37), (16, 39), (15, 40), (15, 40)], 'w3')
    drop = {'rest': [(14, 20), (14, 18)], 'joy': [(15, 19), None], 'surprise': [(14, 19), (14, 17)],
            'sadness': [(13, 19), (13, 17), (13, 15)], 'anger': [(14, 20), (14, 18)]}
    drop = drop.get(expr, drop['rest'])
    m.spans(39 + lift, drop, 'w3'); m.spans(39 + lift, [r and (55 - r[1], 55 - r[0]) for r in drop], 'w3')
    m.rim('w3', 'w2', [(0, 1)], 1); m.rim('w3', 'w2', [(1, 0)], 2)
    m.vline(27, 35 + lift, 37 + lift, 'w1'); m.pxs('w1', (28, 34 + lift), (21, 37 + lift), (22, 38 + lift), (34, 37 + lift), (33, 38 + lift), (18, 38 + lift), (37, 38 + lift))
    f.paste(m)
    if mouth == 'm1':                                    # ours, for speech: the mouth half open under the moustache
        f.hline(25, 30, 39 + lift, 'r0'); f.hline(25, 30, 40 + lift, 's4')
    elif mouth == 'm2':                                  # and open (the sheet's surprised mouth)
        f.spans(39 + lift, [(26, 29), (25, 30), (26, 29)], 'r0')
    elif expr == 'surprise':
        f.spans(39, [(26, 29), (25, 30), (26, 29)], 'r0')
    elif expr == 'joy':
        f.hline(23, 32, 38, 'r0'); f.hline(24, 31, 39, 'x1'); f.hline(25, 30, 40, 'r0')
    else:
        f.hline(24, 31, 39, 's1' if expr != 'sadness' else 's2'); f.hline(25, 30, 40, 's4' if expr != 'anger' else 's3')
    f.hline(25, 30, 41 if expr != 'joy' else 42, 's2')
    return f


def body_marks():
    """chars/savely.py portrait(): the shirt in the V of the vest, the bow tie, the buttons — on an empty canvas."""
    b = P.new()
    for j in range(12):
        hw = max(0, 6 - j // 2)
        if hw:
            b.hline(28 - hw, 27 + hw, 44 + j, 'w3'); b.px(27 + hw, 44 + j, 'w2')
            b.px(28 - hw - 1, 44 + j, 'g3'); b.px(28 + hw, 44 + j, 'g1')
    b.spans(43, [(23, 32)], 'w3'); b.pxs('w2', (22, 44), (33, 44), (23, 45), (32, 45))
    b.spans(45, [(24, 26), (24, 31), (24, 26)], 'r2'); b.spans(45, [(29, 31), None, (29, 31)], 'r2')
    b.pxs('r1', (27, 46), (28, 46), (31, 47), (31, 45)); b.pxs('r3', (24, 45), (25, 45))
    b.pxs('t3', (27, 50), (27, 54)); b.pxs('g1', (28, 50), (28, 54))
    return b


out = {
    'PBODY': rows(body_marks()),
    'RAMPS': pal.RAMPS,
    'DRAWN': {v: rows(sprite.make(savely.VIEWS[v], savely.LEG)) for v in ('front', 'q', 'side')},
    'PFACE': {e: rows(features(e)) for e in EXPRS},
    'PATCH': {},
    'PORTRAIT': {e: rows(P.framed(savely.portrait(e))) for e in EXPRS},
}
def patch(a, b):
    return [[x, y, b.g[y][x] or ''] for y in range(a.h) for x in range(a.w) if a.g[y][x] != b.g[y][x]]


for e in EXPRS:
    base = features(e)
    out['PATCH'][e + ':blink'] = patch(base, features(e, eye='blink'))
    out['PATCH'][e + ':m1'] = patch(base, features(e, mouth='m1'))
    out['PATCH'][e + ':m2'] = patch(base, features(e, mouth='m2'))
out['PATCH']['rest:l'] = patch(features('rest'), features('rest', eye='l'))
out['PATCH']['rest:r'] = patch(features('rest'), features('rest', eye='r'))
with open(os.path.join(HERE, 'web/data.js'), 'w') as fh:
    fh.write('// written by tools/gen.py from styles/s16-pixel/tools — do not edit\n')
    for k, v in out.items():
        fh.write(f'export const {k} = {json.dumps(v, separators=(",", ":"))};\n')
json.dump(out, open('/home/user/cache/to3d-r16-s16-savely/data.json', 'w'))
print('ok', {k: len(v) for k, v in out.items()})
