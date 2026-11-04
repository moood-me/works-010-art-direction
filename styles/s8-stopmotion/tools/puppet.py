"""Putting a puppet head together: skin, features, hair; and helpers for hair locks.

draw_head(d, P, ex, S, cx, cy, yaw, roll) -> {'back': [...], 'head': [...]}
  P  — the character (shape tables, feature params, colours, hair function), see cast.py;
  ex — the expression (a dict of small numbers; see EXPR in cast.py);
  S  — head height in px; (cx, cy) — screen position of the head centre.
'back' goes behind the body (hair that hangs behind), 'head' over it.
"""
import math
from sculpt import pts, poly, f, mix
from head import Head, eye, brow, nose, mouth, ear, wrinkle, blush, freckles, lock, cap


def draw_head(d, P, ex, S, cx, cy, yaw=30, roll=0):
    h = Head(P['shape'], S, cx, cy, yaw, roll)
    back, front = [], []
    skin = P['skin']
    hair = P.get('hair')
    hl = hair(h, d, P, ex) if hair else {'back': [], 'cap': '', 'locks': []}
    # hair behind the head
    locks = sorted(hl['locks'], key=lambda t: t[0])
    back.extend(hl['back'])
    for z, s in locks:
        if z < P.get('hair_split', -0.05):
            back.append(s)
    # far ear
    for side in (-1, 1):
        ear(h, d, side, P, front, behind=True)
    # the head itself
    o = h.outline()
    face = d.rad([(0, mix(skin, '#fff1e2', 0.22), 1), (0.6, skin, 1), (1, mix(skin, P.get('skin_shade', '#a0505a'), 0.3), 1)],
                 cx=0.42, cy=0.55, r=0.62)
    fid = d.form(S * 0.9, shade=P.get('shade', '#5a2438'), depth=0.42, ao=0.3, sheen=0.16, rim=0.22)
    front.append(f'<path d="{pts(o)}" fill="url(#{face})" filter="url(#{fid})"/>')
    tid = d.tex('clay' if P.get('clay') else 'skin', 1.0, P.get('skin_tex', 0.10), seed=5)
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
    nose(h, d, P, front)
    # near ear
    for side in (-1, 1):
        ear(h, d, side, P, front, behind=False)
    # hair over the head
    if hl['cap']:
        front.append(hl['cap'])
    for z, s in locks:
        if z >= P.get('hair_split', -0.05):
            front.append(s)
    front.extend(hl.get('top', []))
    return {'back': back, 'head': front, 'h': h}


# ------------------------------------------------------------------ hair helpers

def shell_path(h, phi0, y0, phi1, y1, n=8, out=0.03, k=1.04, ease=1.0):
    """Points over the hair shell from (phi0, y0) to (phi1, y1)."""
    ps = []
    for i in range(n + 1):
        t = i / n
        te = t ** ease
        phi = phi0 + (phi1 - phi0) * t
        y = y0 + (y1 - y0) * te
        ps.append(h.surf(phi, y, out, k))
    return ps


def hang(p, length, n=8, out_x=0.0, back_z=0.0, wave=0.0, waves=1.5, phase=0.0, side=1, curl_end=0.0):
    """Continue a lock straight down from point p: length in head units, drifting out (x) and back (z), waving."""
    x0, y0, z0 = p
    ps = []
    for i in range(1, n + 1):
        t = i / n
        x = x0 + side * (out_x * t + wave * math.sin(2 * math.pi * waves * t + phase)) + side * curl_end * t ** 4
        y = y0 + length * t
        z = z0 + back_z * t
        ps.append((x, y, z))
    return ps


def hair_cap(h, d, P, k, y_top, line, col, extra_out=0.0):
    """The mass of hair over the skull, given form and a fibre texture. line(phi) → hairline y."""
    S = h.S
    body = cap(h, d, k, y_top, line, col, None)
    fid = d.form(S * 0.8, shade=P.get('hair_shade', '#140808'), depth=0.55, ao=0.4, sheen=0.25, rim=0.3)
    return f'<g filter="url(#{fid})">{body}</g>'
