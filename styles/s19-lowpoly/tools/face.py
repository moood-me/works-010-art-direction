"""The low-poly head: a handful of planes chosen by hand, tiny graphic features pressed on them.

Head space (cm): x to the character's left (viewer's right when it faces us), y up, z forward (out of the face);
the origin is between the ears at eye level. A character gives a `spec` (see DEFAULT) — the numbers move the points,
and so the planes: a broad jaw, a long chin, high cheekbones, a sharp nose are different points, not different code.

A face is: the head (one convex piece: skull, brow, cheekbone, cheek, jaw, chin), the nose (its own wedge), the ears,
and decals: eyes (a dark almond, a lid line), brows (a slim quad), the mouth (a lip line, a lower lip plane), cheeks.
"""
import math
import numpy as np
from shapely.geometry import Polygon
from poly import hull, press, mirror_x, hexcol, mix, tohex

DEFAULT = dict(
    skin='#e2b39a', lip='#c27d76', eye='#2b2433', brow='#4a3328', white=None,
    # skull and face (half sizes, cm)
    crown=11.2, skull_w=7.1, back=9.4, face_z=8.6,
    fore_w=4.4, fore_y=7.5, temple_w=6.8,
    brow_y=2.4, brow_z=9.0, brow_w=5.6,
    cheek_w=5.0, cheek_y=-2.2, cheek_z=6.5, zyg_w=6.7,
    low_w=3.4, low_y=-5.0, low_z=7.2,
    mouth_y=-6.3, mouth_z=8.4, mouth_w=2.0,
    jaw_w=5.3, jaw_y=-6.6, jaw_z=2.6,
    chin_w=1.7, chin_y=-9.8, chin_z=7.3, chin_front=0.0,
    # nose
    nose_top=0.6, nose_tip_y=-3.6, nose_tip_z=10.9, nose_w=1.4, nose_base_y=-4.6, nose_bridge=0.0,
    # eyes
    eye_x=2.95, eye_y=-0.35, eye_w=1.55, eye_h=0.62, eye_tilt=0.0, lid=True, lash=0.0,
    # brows
    brow_th=0.42, brow_len=3.0, brow_lift=0.75, brow_in=0.9,
    # mouth
    lip_w=1.9, lip_h=0.55, mouth_line=0.13,
    ear_y=-0.5, ear_h=5.6, ear_w=0.9,
    cheek_col=None,
)

# expressions: offsets read by eyes(), brows(), mouth()
EXPR = {
    'rest': {},
    'joy': dict(brow_up=0.35, brow_tilt=0.15, eye='smile', mouth='smile', smile=0.9, cheek_up=0.35),
    'surprise': dict(brow_up=1.1, brow_tilt=0.0, eye='wide', mouth='o', open=1.1),
    'sad': dict(brow_up=0.3, brow_tilt=-0.9, eye='low', mouth='down', smile=-0.6),
    'anger': dict(brow_up=-0.55, brow_tilt=1.1, eye='narrow', mouth='tight', smile=-0.35),
}


def S(spec):
    s = dict(DEFAULT); s.update(spec); return s


def head_points(s):
    cr, sw = s['crown'], s['skull_w']
    P = [
        (0, cr, -1.5), (sw * 0.66, cr - 1.3, 1.2), (sw * 0.68, cr - 1.4, -4.8), (0, cr - 2.6, -s['back'] * 0.86),
        (sw * 0.76, 4.6, -s['back'] * 0.72), (0, 0.5, -s['back']),
        (sw * 0.74, -1.8, -s['back'] * 0.72), (0, -4.6, -s['back'] * 0.82), (sw * 0.55, -5.6, -s['back'] * 0.5),
        (0, s['fore_y'], s['face_z'] - 0.6), (s['fore_w'], s['fore_y'] - 0.1, s['face_z'] - 2.2),
        (s['temple_w'], 4.0, 3.0), (sw, 1.0, -2.4),
        (0, s['brow_y'], s['brow_z']), (s['brow_w'] * 0.53, s['brow_y'] + 0.35, s['brow_z'] - 0.3),
        (s['brow_w'], s['brow_y'] - 0.5, s['brow_z'] - 2.2),
        (s['cheek_w'], s['cheek_y'], s['cheek_z']), (s['zyg_w'], s['cheek_y'] + 1.2, 2.6),
        (s['low_w'], s['low_y'], s['low_z']),
        (0, s['mouth_y'] + 0.4, s['mouth_z'] + 0.5), (s['mouth_w'], s['mouth_y'] - 0.4, s['mouth_z'] - 0.6),
        (s['jaw_w'], s['jaw_y'], s['jaw_z']), (s['jaw_w'] + 0.4, s['jaw_y'] + 1.7, -1.8),
        (s['chin_w'], s['chin_y'] + 0.25, s['chin_z']), (0, s['chin_y'], s['chin_z'] + 0.3 + s['chin_front']),
        (s['chin_w'] + 0.9, s['chin_y'] + 0.4, s['chin_z'] - 3.4), (s['jaw_w'] * 0.62, s['jaw_y'] - 1.3, -0.4),
    ]
    return mirror_x(P)


def nose_points(s):
    t, ty, tz, w, by = s['nose_top'], s['nose_tip_y'], s['nose_tip_z'], s['nose_w'], s['nose_base_y']
    bz = s['brow_z'] + 0.05
    return mirror_x([
        (0, t, bz), (0.45, t - 0.2, bz - 0.4),
        (0, (t + ty) / 2 + 0.2, (bz + tz) / 2 + 0.05 + s['nose_bridge']),
        (0, ty, tz), (w * 0.45, ty - 0.1, tz - 0.6),
        (w, by + 0.25, tz - 2.3), (w * 0.55, by, tz - 1.5), (0, by, tz - 1.2),
        (w * 0.75, (t + by) / 2 - 0.8, bz - 1.6),
    ])


def ear(s, side=1):
    x = s['skull_w'] - 0.2; y = s['ear_y']; h = s['ear_h']
    pts = [(x, y + h * 0.5, -0.6), (x + s['ear_w'], y + h * 0.42, -1.6), (x + s['ear_w'] * 1.1, y - h * 0.1, -2.3),
           (x + s['ear_w'] * 0.6, y - h * 0.5, -1.2), (x, y - h * 0.45, -0.2), (x - 0.4, y, -2.6), (x + 0.2, y + 0.1, 0.1)]
    return hull([(side * px, py, pz) for px, py, pz in pts], s['skin'], 'skin', 'ear')


def head(spec, expr='rest', extra=None):
    """→ pieces in head space: head, nose, ears (features pressed on the head)."""
    s = S(spec)
    e = dict(EXPR[expr]) if isinstance(expr, str) else dict(expr)
    if extra:
        e.update(extra)
    pts = head_points(s)
    if e.get('open', 0) > 0.6 and e.get('jaw', True):   # an open mouth drops the chin a little
        drop = (e['open'] - 0.6) * 1.2
        pts = [(x, y - drop * max(0, (-5.5 - y)) / 4.5, z) for x, y, z in pts]
    H = hull(pts, s['skin'], 'skin', 'head')
    N = hull(nose_points(s), s['skin'], 'skin', 'nose')
    for side in (1, -1):
        eye(H, s, e, side)
        brow(H, s, e, side)
    mouth(H, s, e)
    if s['cheek_col']:
        for side in (1, -1):
            cx = side * (s['cheek_w'] - 0.6)
            cy = s['cheek_y'] - 1.6 + e.get('cheek_up', 0)
            press(H, [(cx + side * a, cy + b, 9) for a, b in [(-1.2, 0.3), (0, 0.9), (1.3, 0.2), (0.2, -0.8)]],
                  s['cheek_col'], 0.35)
    return [H, N, ear(s, 1), ear(s, -1)]


def _eye2d(s, e):
    """The eye drawn flat, outer corner at +x: → [(polygon points, colour key)], back to front.
    An almond of white (few points), an octagon iris cut by it, a dark upper lid band (thicker toward the outer
    corner), a speck of light; a crescent when it laughs."""
    w, h = s['eye_w'], s['eye_h']
    kind = e.get('eye', s.get('eye_rest', 'open'))
    if kind == 'smile':
        cres = [(-w, -0.05), (-0.35 * w, 0.5 * h + 0.15), (0.45 * w, 0.55 * h + 0.15), (1.08 * w, 0.05),
                (0.45 * w, 0.3 * h), (-0.4 * w, 0.22 * h)]
        return [(cres, 'eye')]
    top, bot, lid_drop, outer_lift = 1.0, 0.75, 0.0, 0.0
    if kind == 'wide':
        top, bot = 1.35, 1.0
    elif kind == 'low':        # sad: the upper lid falls toward the outer corner
        top, lid_drop = 0.85, 0.35
    elif kind == 'narrow':     # anger: a flat, low upper lid
        top, bot, lid_drop = 0.62, 0.65, -0.15
    elif kind == 'half':       # heavy-lidded, sideways look
        top, bot = 0.62, 0.7
    hh = h * top
    upper = [(-w, 0.0), (-0.55 * w, 0.78 * hh + 0.1 * lid_drop), (0.15 * w, hh - 0.2 * lid_drop * h),
             (0.75 * w, 0.62 * hh - lid_drop * h * 0.9), (1.05 * w, 0.12 * h - lid_drop * h * 0.5)]
    lower = [(0.6 * w, -0.42 * h * bot), (-0.15 * w, -0.55 * h * bot), (-0.7 * w, -0.4 * h * bot)]
    almond = Polygon(upper + lower)
    look = e.get('look', s.get('look', (0.0, 0.0)))
    r = h * s.get('iris', 0.95)
    ix, iy = look[0] * w * 0.45, 0.05 * h + look[1] * h * 0.3
    iris = Polygon([(ix + r * math.cos(t), iy + r * math.sin(t)) for t in [math.pi * (k / 4 + 1 / 8) for k in range(8)]])
    iris = iris.intersection(almond)
    out = [(list(almond.exterior.coords)[:-1], 'white')]
    if not iris.is_empty and iris.geom_type == 'Polygon':
        out.append((list(iris.exterior.coords)[:-1], 'eye'))
        pr = r * 0.42
        pupil = Polygon([(ix + pr * math.cos(t), iy + pr * math.sin(t)) for t in [math.pi * k / 3 for k in range(6)]]).intersection(almond)
        if not pupil.is_empty and pupil.geom_type == 'Polygon':
            out.append((list(pupil.exterior.coords)[:-1], 'pupil'))
    # the upper lid: a band along the top edge, thick at the outer corner
    th = s.get('lid_th', 0.22)
    band = upper + [(x, y - th * (0.6 + 0.8 * max(0, x / w))) for x, y in reversed(upper)]
    band = Polygon(band).buffer(0)
    out.append((list(band.exterior.coords)[:-1] if band.geom_type == 'Polygon' else upper, 'lid'))
    if s['lash'] > 0:
        L = s['lash']
        x1, y1 = upper[-1]; x0, y0 = upper[-2]
        out.append(([(x0, y0 - 0.05), (x1 + L * 0.9, y1 + L * 0.55), (x1 - 0.1, y1 - 0.18)], 'lid'))
    # a speck of light, upper left of the iris
    if s.get('speck', True) and kind != 'narrow':
        sx, sy = ix - r * 0.35, iy + r * 0.35
        sp = 0.16 * h / 0.7
        out.append(([(sx - sp, sy), (sx, sy + sp), (sx + sp, sy), (sx, sy - sp)], 'speck'))
    # the crease above the lid
    if s.get('crease', True):
        cr = [(-0.85 * w, 0.95 * hh + 0.25), (0.1 * w, hh + 0.42 - 0.2 * lid_drop), (0.95 * w, 0.62 * hh + 0.32 - 0.6 * lid_drop * h)]
        out.append((cr + [(x + 0.05, y - 0.13) for x, y in reversed(cr)], 'crease'))
    return out


def eye(H, s, e, side):
    cx, cy, t = side * s['eye_x'], s['eye_y'], s['eye_tilt']
    skin, ink = hexcol(s['skin']), hexcol(s['eye'])
    cols = dict(white=s.get('white') or tohex(mix(hexcol('#f3ece6'), skin, 0.18)), eye=s['eye'],
                pupil=tohex(mix(ink, hexcol('#000000'), 0.6)), lid=tohex(mix(ink, hexcol('#000000'), 0.3)),
                speck='#fbf7f2', crease=tohex(mix(skin, ink, 0.32)))
    lift = 0.06
    for poly, key in _eye2d(s, e):
        if key == 'eye' and e.get('eye', s.get('eye_rest', 'open')) == 'smile':
            col = tohex(mix(ink, hexcol('#000000'), 0.3))
        else:
            col = cols[key]
        press(H, [(cx + side * a, cy + b + t * a, 20) for a, b in poly], col, 1.0, lift=lift)
        lift += 0.015
    if e.get('eye') == 'smile' and e.get('crow', 0):
        w = s['eye_w']
        press(H, [(cx + side * a, cy + b, 20) for a, b in [(1.25 * w, -0.1), (1.9 * w, 0.1), (1.9 * w, -0.05), (1.25 * w, -0.3)]],
              mix(skin, ink, 0.35), 1.0, lift=0.07)


def brow(H, s, e, side):
    if s['brow_th'] <= 0:   # the character draws its own brows (pieces)
        return
    up, tilt = e.get('brow_up', 0.0), e.get('brow_tilt', 0.0)
    L, th = s['brow_len'], s['brow_th']
    x0 = side * s['brow_in']; y0 = s['eye_y'] + s['eye_h'] + s['brow_lift'] + 0.55 + up
    yin = y0 - tilt * 0.45; yout = y0 + 0.25 + tilt * 0.25 - s.get('brow_arch', 0) * 0.3
    ymid = (yin + yout) / 2 + 0.25 + s.get('brow_arch', 0) * 0.35
    xm = side * (s['brow_in'] + L * 0.55); xo = side * (s['brow_in'] + L)
    shape = [(x0, yin + th * 0.6, 20), (xm, ymid + th * 0.55, 20), (xo, yout + th * 0.1, 20),
             (xo, yout - th * 0.25, 20), (xm, ymid - th * 0.5, 20), (x0, yin - th * 0.5, 20)]
    press(H, shape, s['brow'], 1.0, lift=0.09)


def mouth(H, s, e):
    kind = e.get('mouth', s.get('mouth_rest', 'line'))
    w, my, sm = s['lip_w'], s['mouth_y'], e.get('smile', s.get('smile', 0.0))
    lip, dark = s['lip'], mix(hexcol(s['lip']), hexcol('#2a1820'), 0.55)
    C = (0, my, 0)
    z = 20
    if kind in ('line', 'smile', 'down', 'tight', 'smirk'):
        th = s['mouth_line'] * (0.7 if kind == 'tight' else 1.0)
        cw = w * (1.15 if kind == 'smile' else 0.85 if kind == 'tight' else 1.0)
        lc, rc = sm * 0.55, sm * 0.55
        if kind == 'smirk':
            lc, rc = 0.55, -0.05
        line = [(-cw, my + lc, z), (-0.35 * cw, my + 0.05 + lc * 0.25, z), (0.35 * cw, my + 0.05 + rc * 0.25, z),
                (cw, my + rc, z), (cw, my + rc - th, z), (0.35 * cw, my - th + rc * 0.15, z),
                (-0.35 * cw, my - th + lc * 0.15, z), (-cw, my + lc - th, z)]
        # the lower lip: a small plane under the line
        lh = s['lip_h'] * (0.6 if kind == 'tight' else 1.0)
        low = [(-0.75 * cw, my - th + lc * 0.6, z), (0.75 * cw, my - th + rc * 0.6, z),
               (0.45 * cw, my - th - lh, z), (-0.45 * cw, my - th - lh, z)]
        upper = [(-cw * 0.95, my + lc * 0.9, z), (-0.2 * cw, my + lh * 0.75, z), (0, my + lh * 0.6, z),
                 (0.2 * cw, my + lh * 0.75, z), (cw * 0.95, my + rc * 0.9, z)]
        if s.get('lips', True):
            press(H, low, lip, 0.6)
            press(H, upper, mix(hexcol(lip), hexcol('#3a2028'), 0.12), 0.5)
        press(H, line, dark, 1.0, lift=0.1)
        if kind == 'smile' and sm > 0.5 and s.get('laugh_lines'):   # laugh lines
            for sd in (1, -1):
                press(H, [(sd * (cw + 0.5), my + 1.5, z), (sd * (cw + 0.75), my + 1.45, z),
                          (sd * (cw + 0.55), my - 0.2, z), (sd * (cw + 0.35), my - 0.1, z)],
                      mix(hexcol(s['skin']), hexcol('#5a3030'), 0.35), 0.8)
    elif kind in ('open', 'o', 'laugh', 'shout'):
        op = e.get('open', 1.0)
        if kind == 'o':
            ww, top, bot = w * 0.55, 0.45, -0.9 * op
            shape = [(-ww, my - 0.1), (-ww * 0.6, my + top), (ww * 0.6, my + top), (ww, my - 0.1),
                     (ww * 0.6, my + bot), (-ww * 0.6, my + bot)]
        else:
            ww = w * (1.3 if kind == 'laugh' else 1.05)
            up = sm * 0.5
            top = 0.25; bot = -1.5 * op
            shape = [(-ww, my + up), (-ww * 0.45, my + top), (ww * 0.45, my + top), (ww, my + up),
                     (ww * 0.55, my + bot * 0.85), (0, my + bot), (-ww * 0.55, my + bot * 0.85)]
        press(H, [(x, y, z) for x, y in shape], '#3a1a22', 1.0, lift=0.1)
        if kind != 'o':
            ww = w * (1.3 if kind == 'laugh' else 1.05)
            teeth = [(-ww * 0.8, my + 0.12 + sm * 0.25), (ww * 0.8, my + 0.12 + sm * 0.25),
                     (ww * 0.62, my - 0.38), (-ww * 0.62, my - 0.38)]
            press(H, [(x, y, z) for x, y in teeth], '#f4eee4', 1.0, lift=0.13)
            tongue = [(-ww * 0.45, my + bot * 0.8), (0, my + bot * 0.55), (ww * 0.45, my + bot * 0.8),
                      (ww * 0.25, my + bot * 0.97), (-ww * 0.25, my + bot * 0.97)]
            press(H, [(x, y, z) for x, y in tongue], '#c45a5e', 1.0, lift=0.12)
            lowlip = [(-ww * 0.6, my + bot - 0.05), (ww * 0.6, my + bot - 0.05), (ww * 0.35, my + bot - 0.6),
                      (-ww * 0.35, my + bot - 0.6)]
            press(H, [(x, y, z) for x, y in lowlip], lip, 0.8)
