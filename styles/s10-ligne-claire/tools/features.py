"""Faces in the ligne-claire manner: few marks, all in the one even line.

Eyes: an upper-lid stroke a little heavier than the contour, a black oval pupil tucked under it, no white and
no shine (Hergé, Chaland, Floc'h); women get two or three short lashes at the outer end. Brows: a thin filled
crescent. Nose: comes from the 3D contour; in near-front views a small hook at the tip. Mouth: one stroke with
small corner ticks; open mouths are a dark shape with a tongue.  Wrinkles and bags: one short thin stroke each.

Expressions are numbers in a dict (see EXPR): lid (openness), brow (lift), tilt (inner end up +, down -),
smile (corners up +, down -), open (mouth opening), look (pupil shift), squint (lower lid push).
"""
import numpy as np
import lc
from head import Mark

EXPR = {
    'calm': dict(),
    'dream': dict(lid=0.55, brow=1.5, tilt=1.5, smile=0.35, look=(1.5, -0.5)),
    'joy': dict(lid=0.0, happy=True, brow=3, smile=1.0, open=7, squint=1),
    'surprise': dict(lid=1.25, brow=7, open=8, round=True, smile=0.0),
    'sad': dict(lid=0.5, brow=1, tilt=5, smile=-0.8, look=(0, 1.5)),
    'anger': dict(lid=0.75, brow=-4, tilt=-6, smile=-0.5, open=5, teeth=True, squint=0.6),
}


def ex(e, k, d=0.0):
    return e.get(k, d) if e else d


def lerp(a, b, t):
    return a + (b - a) * t


def eye_marks(h, side, e, st):
    """One eye at the face position st['x'] * side, st['y']. st: style of the character's eyes."""
    x, y = st['x'] * side, st['y']
    W = st.get('w', 10)                         # half width
    lid = ex(e, 'lid', st.get('lid', 0.85))
    out = []
    flip = side < 0
    look = ex(e, 'look', (0, 0))
    lu = look[0] * (1 if side > 0 else 1)       # look shifts both pupils the same way on screen
    if ex(e, 'happy'):
        # closed, smiling eye: an arch
        uv = [(-W * 0.9, 1.5), (-W * 0.4, -2.8), (W * 0.25, -3.6), (W * 0.9, -1.0)]
        out.append(Mark(h.on_face(x, y, uv, flip), w=st.get('lidw', 1.35)))
        if st.get('lashes'):
            out.append(Mark(h.on_face(x, y, [(W * 0.85, -1.2), (W * 1.2, -3.2)], flip), w=1.0))
        return out
    top = -4.6 * (0.4 + 0.6 * lid) - (1.6 if ex(e, 'round') else 0)
    lidc = [(-W, 1.2), (-W * 0.55, top * 0.8), (W * 0.1, top), (W * 0.65, top * 0.75), (W * 1.05, 0.2)]
    # pupil: an oval under the lid, cut by it
    pr = st.get('pupil', (3.3, 4.3))
    if ex(e, 'round'):
        pr = (pr[0] * 0.8, pr[1] * 0.8)
    pc = (st.get('pu', 1.0) + lu * (1 if not flip else -1), 0.4 + look[1])
    lid_v = np.interp(np.linspace(-1, 1, 41) * pr[0] + pc[0],
                      [p[0] for p in lidc], [p[1] for p in lidc])
    pupil = []
    for k, a in enumerate(np.linspace(0, 2 * np.pi, 41)[:-1]):
        u = pc[0] + pr[0] * np.cos(a)
        v = pc[1] + pr[1] * np.sin(a)
        lv = np.interp(u, [p[0] for p in lidc], [p[1] for p in lidc]) + 0.8
        pupil.append((u, max(v, lv)))
    lower = st.get('lower', True)
    if ex(e, 'round'):
        # a wide-open eye shows its white: outline the whole eye
        low = [(W * 1.05, 0.2), (W * 0.5, 4.8), (-W * 0.4, 4.6), (-W, 1.2)]
        out.append(Mark(h.on_face(x, y, lidc + low[1:-1], flip), kind='shape', fill='#ffffff', w=0.7))
    out.append(Mark(h.on_face(x, y, pupil, flip), kind='shape', fill=lc.INK, w=0))
    out.append(Mark(h.on_face(x, y, lidc, flip), w=st.get('lidw', 1.35)))
    if st.get('lashes'):
        out.append(Mark(h.on_face(x, y, [(W * 0.95, -0.3), (W * 1.3, -2.6)], flip), w=1.0))
        out.append(Mark(h.on_face(x, y, [(W * 0.7, top * 0.75), (W * 0.95, top * 0.75 - 2.4)], flip), w=0.9))
    sq = ex(e, 'squint', 0)
    if lower and not ex(e, 'round'):
        lv = 5.0 - sq * 1.8
        out.append(Mark(h.on_face(x, y, [(-W * 0.1, lv), (W * 0.45, lv - 0.3 - sq * 0.6), (W * 0.8, lv - 1.4)], flip),
                        w=0.55))
    if st.get('bags'):
        out.append(Mark(h.on_face(x, y, [(-W * 0.5, 9), (W * 0.1, 10.2), (W * 0.6, 9.2)], flip), w=0.55))
    if st.get('crowsfeet'):
        out.append(Mark(h.on_face(x, y, [(W * 1.3, 1), (W * 1.75, 2.5)], flip), w=0.55))
        out.append(Mark(h.on_face(x, y, [(W * 1.3, 3.5), (W * 1.7, 5.8)], flip), w=0.55))
    return out


def brow_marks(h, side, e, st):
    x, y = st['x'] * side, st['y']
    flip = side < 0
    L = st.get('len', 12)
    th = st.get('th', 1.6)
    lift = ex(e, 'brow', 0)
    tilt = ex(e, 'tilt', 0)
    arch = st.get('arch', 3.0)
    # spine from inner (-L) to outer (+L)
    spine = [(-L, -lift - tilt + 1), (-L * 0.3, -lift - tilt * 0.6 - arch * 0.8), (L * 0.35, -lift - arch),
             (L, -lift + tilt * 0.3 + 1.5 - arch * 0.2)]
    if tilt < 0:      # anger: straight and pulled down at the inner end
        spine = [(-L, -lift - tilt + 1.5), (0, -lift - tilt * 0.3 - 1), (L, -lift + 0.5)]
    if st.get('style') == 'line':
        return [Mark(h.on_face(x, y, spine, flip), w=st.get('lw', 1.3), stroke=st.get('colour', lc.INK))]
    # a thin crescent: thicker inside, thin at the tail
    top, bot = [], []
    for k, (u, v) in enumerate(spine):
        t = k / (len(spine) - 1)
        tt = th * (1.1 - 0.75 * t) * (1 if not st.get('bushy') else 1.7)
        top.append((u, v - tt))
        bot.append((u, v + tt * 0.8))
    pts = top + bot[::-1]
    return [Mark(h.on_face(x, y, pts, flip), kind='shape', fill=st.get('colour', lc.INK), w=0.6,
                 corners=(0, len(top) - 1, len(top), len(pts) - 1))]


def mouth_marks(h, e, st):
    y = st['y']
    W = st.get('w', 11)
    sm = ex(e, 'smile', st.get('smile', 0.15))
    op = ex(e, 'open', 0)
    out = []
    if op > 0:
        if ex(e, 'round'):
            pts = [(0, -op * 0.45), (W * 0.42, 0), (0, op * 0.65), (-W * 0.42, 0)]
            out.append(Mark(h.on_face(0, y, pts), kind='shape', fill='#4a1a14', w=1.0))
            return out
        up = -sm * 4
        top = [(-W * 1.15, up - 0.5), (-W * 0.5, -1.0), (0, -0.6), (W * 0.5, -1.0), (W * 1.15, up - 0.5)]
        if sm > 0:
            bot = [(W * 0.85, up + op * 0.3), (W * 0.3, op * 0.95), (-W * 0.3, op * 0.95), (-W * 0.85, up + op * 0.3)]
        else:
            bot = [(W * 0.9, op * 0.75), (W * 0.3, op), (-W * 0.3, op), (-W * 0.9, op * 0.75)]
        pts = top + bot
        out.append(Mark(h.on_face(0, y, pts), kind='shape', fill='#4a1a14', w=1.0, corners=(0, 4)))
        if ex(e, 'teeth'):
            teeth = [(-W * 0.85, -0.5), (W * 0.85, -0.5), (W * 0.7, op * 0.38), (-W * 0.7, op * 0.38)]
            out.append(Mark(h.on_face(0, y, teeth), kind='shape', fill='#ffffff', w=0.6, corners=(0, 1, 2, 3)))
        elif sm > 0:
            tongue = [(-W * 0.45, op * 0.9), (0, op * 0.45), (W * 0.45, op * 0.9)]
            out.append(Mark(h.on_face(0, y, tongue + [(0, op * 0.98)]), kind='shape', fill='#c8564a', w=0))
        return out
    c = sm * 3.2
    pts = [(-W, -c), (-W * 0.45, 0.4 - c * 0.15), (0, 0.6), (W * 0.45, 0.4 - c * 0.15), (W, -c)]
    out.append(Mark(h.on_face(0, y, pts), w=1.0))
    # corner ticks: small strokes that catch the smile or the frown
    tick = 2.2
    for s in (-1, 1):
        if sm > 0.2:
            out.append(Mark(h.on_face(0, y, [(s * (W - 0.6), -c - tick * 0.7), (s * (W + 1.2), -c + 0.8)]), w=0.8))
        elif st.get('ticks', True):
            out.append(Mark(h.on_face(0, y, [(s * (W - 0.4), -c - 1.4), (s * (W + 0.8), -c + 0.8)]), w=0.7))
    if st.get('lower', True):
        lv = st.get('lower_y', 6.5) + max(0, sm) * 0.5
        out.append(Mark(h.on_face(0, y, [(-W * 0.35, lv), (0, lv + 0.4), (W * 0.35, lv)]), w=0.6))
    return out


def nose_marks(h, e, st, view_yaw):
    """The nose tip in near-front views (in turned views the 3D contour draws it)."""
    out = []
    y = st['y']
    W = st.get('w', 7)
    if abs(view_yaw) < 25:
        s = 1 if view_yaw >= 0 else -1
        out.append(Mark(h.on_face(0, y, [(-W * s, -4), (-W * 1.05 * s, -0.5), (-W * 0.5 * s, 1.5), (0, 1.6),
                                           (W * 0.45 * s, 1.0)]), w=0.85))
        out.append(Mark(h.on_face(0, y, [(W * 0.85 * s, -1.6), (W * 1.0 * s, 0.4)]), w=0.7))
    return out
