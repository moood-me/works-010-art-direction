"""Putting a puppet head together: skin, features, hair; and helpers for hair locks.

draw_head(d, P, ex, S, cx, cy, yaw, roll) -> {'back': [...], 'head': [...]}
  P  — the character (shape tables, feature params, colours, hair function), see cast.py;
  ex — the expression (a dict of small numbers; see EXPR in cast.py);
  S  — head height in px; (cx, cy) — screen position of the head centre.
'back' goes behind the body (hair that hangs behind), 'head' over it.
"""
import math
from sculpt import pts, poly, f, mix
from head import Head, eye, brow, nose, mouth, ear, wrinkle, blush, freckles
import hair as H


def draw_head(d, P, ex, S, cx, cy, yaw=30, roll=0):
    h = Head(P['shape'], S, cx, cy, yaw, roll)
    back, front = [], []
    skin = P['skin']
    hair = P.get('hair')
    # hair(h, d, P, ex) → dict(col, locks=[Lock], cap=(line, y_back, k) or None, extra_back=[svg], extra_front=[svg])
    hd = hair(h, d, P, ex) if hair else None
    front_locks = []
    if hd:
        cap_back = cap_front = None
        if hd.get('cap'):
            line, y_back, k = hd['cap']
            cap_back, cap_front = H.cap_polys(h, k, line, y_back)
        split = P.get('hair_split', 0.0)
        gs = [(H.geom(h, L)['z'], L) for L in hd['locks']]
        bl = [L for z, L in sorted(gs, key=lambda t: t[0]) if z < split]
        front_locks = [L for z, L in sorted(gs, key=lambda t: t[0]) if z >= split]
        back.extend(hd.get('extra_back', []))
        back.append(H.mass(d, h, P, bl, hd['col'], cap=cap_back))
    # far ear
    for side in (-1, 1):
        ear(h, d, side, P, front, behind=True)
    # the head itself
    o = h.outline()
    face = d.rad([(0, mix(skin, '#fff1e2', 0.22), 1), (0.6, skin, 1), (1, mix(skin, P.get('skin_shade', '#a0505a'), 0.3), 1)],
                 cx=0.42, cy=0.55, r=0.62)
    fid = d.form(S * 0.9, shade=P.get('shade', '#5a2438'), depth=P.get('shade_depth', 0.9), ao=0.3, sheen=0.18, rim=0.2)
    front.append(f'<path d="{pts(o)}" fill="url(#{face})" filter="url(#{fid})"/>')
    tid = d.tex('clay', 1.0, P.get('skin_tex', 0.10), seed=5)
    front.append(f'<path d="{pts(o)}" fill="{skin}" filter="url(#{tid})"/>')
    # cheeks, freckles
    for side in (-1, 1):
        blush(h, d, side, P, front, P.get('blush', 0.3), P.get('blush_col', '#e0606a'))
    if P.get('freckles'):
        freckles(h, d, P, front, P['freckles'])
    # sculpted wrinkles
    for (phi, y, lp, sw) in P.get('wrinkles', []):
        wrinkle(h, d, phi, y, lp, P, front, sw)
    # chin/jaw separation (soft)
    # eyes, brows, nose, mouth — far side first
    order = (-1, 1) if yaw >= 0 else (1, -1)
    for side in order:
        eye(h, d, side, P, ex, skin, front)
    for side in order:
        brow(h, d, side, P, {**ex, 'brow_in': ex.get('brow_in', 0) * (1 if side else 1)}, front)
    mouth(h, d, P, ex, front)
    if P.get('under_nose'):                 # moustache and the like: over the mouth, under the nose
        front.extend(P['under_nose'](h, d, P, ex))
    nose(h, d, P, front)
    # near ear
    for side in (-1, 1):
        ear(h, d, side, P, front, behind=False)
    # hair over the head
    if hd:
        front.append(H.mass(d, h, P, front_locks, hd['col'], cap=cap_front))
        front.extend(hd.get('extra_front', []))
    if P.get('over_all'):                   # glasses, a loupe: over everything
        front.extend(P['over_all'](h, d, P, ex))
    return {'back': back, 'head': front, 'h': h}


