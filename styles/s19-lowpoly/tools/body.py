"""The body: a small skeleton (forward kinematics from a pose) and the low-poly parts hung on it.

World space (cm): y up, the figure faces +z (toward the viewer at yaw 0), x is the figure's left.
A character module gives proportions (`prop`) and a pose (angles in degrees); `Skel` turns them into joints and
frames; the helpers below build convex pieces between joints: `limb`, `hand`, `shoe`, `torso_hull`.
"""
import math
import numpy as np
from poly import Rx, Ry, Rz, euler, hull, segment, chain, ring, unit, frame_along, Piece, mix, hexcol

PROP = dict(   # an adult woman, about 168 cm
    pelvis_y=92.0, hip_w=8.6, hip_drop=4.0, thigh=43.0, shin=42.0, ankle_h=7.0, foot=24.0,
    waist=17.0, chest=30.0, neck=9.0, head_off=10.5, head_z=1.0, head_scale=1.0,
    shoulder_w=17.0, sh_drop=3.0, upper_arm=29.0, forearm=25.0, hand=17.5,
)

POSE = dict(
    hip=(0, 0, 0), pelvis=(0, 0, 0), spine=(0, 0, 0), neck=(0, 0, 0), head=(0, 0, 0),
    arm_L=(8, 0, 0, 8, (0, 0, 0)), arm_R=(8, 0, 0, 8, (0, 0, 0)),
    leg_L=(3, 0, 0, 0, (0, 0)), leg_R=(3, 0, 0, 0, (0, 0)),
    shrug=(0, 0), ground='auto',
)


class Skel:
    """Joints (np arrays) and frames (3×3) of a posed figure. side +1 = the figure's left (+x), −1 = right."""

    def __init__(self, prop, pose):
        p = dict(PROP); p.update(prop); self.p = p
        q = dict(POSE); q.update(pose); self.q = q
        self.P = np.array([0, p['pelvis_y'], 0.0]) + np.array(q['hip'], float)
        self.Rp = euler(*q['pelvis'])
        self.waist = self.P + self.Rp @ np.array([0, p['waist'], 0])
        self.Rc = self.Rp @ euler(*q['spine'])
        self.neckb = self.waist + self.Rc @ np.array([0, p['chest'], 0])
        self.Rn = self.Rc @ euler(*q['neck'])
        self.necktop = self.neckb + self.Rn @ np.array([0, p['neck'], 0])
        self.Rh = self.Rn @ euler(*q['head'])
        self.head = self.necktop + self.Rh @ np.array([0, p['head_off'], p['head_z']])
        self.j = {}
        for s, k in ((1, 'L'), (-1, 'R')):
            sh = self.neckb + self.Rc @ np.array([s * p['shoulder_w'], -p['sh_drop'] + q['shrug'][0 if s > 0 else 1], -1.0])
            abd, fwd, tw, bend, wr = q['arm_' + k]
            Ru = self.Rc @ Rz(s * abd) @ Rx(-fwd) @ Ry(s * tw)
            el = sh + Ru @ np.array([0, -p['upper_arm'], 0])
            Rf = Ru @ Rx(-bend)
            wr_ = el + Rf @ np.array([0, -p['forearm'], 0])
            Rhand = Rf @ euler(wr[0], s * (wr[1] + 30), s * wr[2])   # the back of a hanging hand turns a little forward
            hip = self.P + self.Rp @ np.array([s * p['hip_w'], -p['hip_drop'], 0])
            labd, lfwd, ltw, lbend, ft = q['leg_' + k]
            Rt = self.Rp @ Rz(s * labd) @ Rx(-lfwd) @ Ry(s * ltw)
            kn = hip + Rt @ np.array([0, -p['thigh'], 0])
            Rs = Rt @ Rx(lbend)
            an = kn + Rs @ np.array([0, -p['shin'], 0])
            yaw = math.degrees(math.atan2(Rt[0, 2], Rt[2, 2]))
            Rft = Ry(yaw + s * ft[1]) @ Rx(ft[0])
            self.j[k] = dict(sh=sh, Ru=Ru, el=el, Rf=Rf, wr=wr_, Rh=Rhand, hip=hip, Rt=Rt, kn=kn, Rs=Rs, an=an,
                             Rft=Rft, s=s)
        if q['ground'] == 'auto':
            low = min(self.j['L']['an'][1], self.j['R']['an'][1]) - p['ankle_h']
            self.shift(-low)

    def shift(self, dy):
        d = np.array([0, dy, 0.0])
        for a in ('P', 'waist', 'neckb', 'necktop', 'head'):
            setattr(self, a, getattr(self, a) + d)
        for k in self.j.values():
            for a in ('sh', 'el', 'wr', 'hip', 'kn', 'an'):
                k[a] = k[a] + d

    def at(self, frame, origin, pts):
        """Points given in a frame (pelvis 'p', chest 'c', head 'h', or a 3×3) → world."""
        R = {'p': self.Rp, 'c': self.Rc, 'h': self.Rh, 'n': self.Rn}.get(frame, frame) if isinstance(frame, str) else frame
        o = {'p': self.P, 'w': self.waist, 'c': self.neckb, 'h': self.head}.get(origin, origin) \
            if isinstance(origin, str) else origin
        return [np.asarray(o) + R @ np.asarray(q, float) for q in pts]

    def place_head(self, pieces):
        sc = self.p['head_scale']
        return [pc.moved(self.Rh * sc, self.head) for pc in pieces]


# ---------------------------------------------------------------------------------------------------------- parts

def limb(a, b, ra, rb, color, mat='cloth', n=6, ext=0.35, flat=1.0, up=(0, 0, 1), name='', phase=30):
    return segment(a, b, ra, rb, color, mat, n=n, ext=ext, flat=flat, up=up, name=name, phase=phase)


def leg(sk, k, r, color, mat='skin', top=None, n=6):
    """hip → knee → ankle; r = (hip, knee, ankle) radii. `top` starts higher (a thigh under a skirt)."""
    J = sk.j[k]
    if len(r) == 4:   # a calf: a wider ring a third of the way down the shin
        calf = J['kn'] + 0.32 * (J['an'] - J['kn'])
        return chain([J['hip'] if top is None else top, J['kn'], calf, J['an']], r, color, mat, n=n, cap=(0.3, 0.0))
    return chain([J['hip'] if top is None else top, J['kn'], J['an']], r, color, mat, n=n, cap=(0.3, 0.0))


def arm(sk, k, r, color, mat='cloth', n=6, upto='wr'):
    """shoulder → elbow → wrist; r = (shoulder, elbow, wrist) radii."""
    J = sk.j[k]
    return chain([J['sh'], J['el'], J[upto]], r, color, mat, n=n, cap=(0.25, 0.15))


def shoulder(sk, k, r, color, mat='cloth', inner=5.5, top=1.5):
    """The slope from the neck to the arm (trapezius and deltoid as one piece): the hull of two points by the neck
    and the first ring of the arm."""
    J = sk.j[k]; s = J['s']
    pts = sk.at('c', 'c', [(s * inner, -0.6, 3.2), (s * inner, -0.6, -3.4), (s * inner * 0.8, -3.0, 0.0)])
    R = frame_along(J['el'] - J['sh'])
    a = J['sh'] + R[:, 1] * (-top)
    b = J['sh'] + 0.22 * (J['el'] - J['sh'])
    pts += ring(a, R, r * 0.9, r * 0.9, 6, 30) + ring(b, R, r, r, 6, 30)
    return hull(pts, color, mat, 'shoulder')


def torso_hull(sk, frame, origin, rings, color, mat='cloth', name='', bias=0.0, side=0, gap=1.0):
    """One convex piece through rings given as (y, half-width, front depth, back depth, n, front push) in a frame.
    side ±1 keeps only that half (an open jacket's panel), reaching `gap` cm past the middle."""
    pts = []
    R = {'p': sk.Rp, 'c': sk.Rc}[frame]
    o = {'p': sk.P, 'w': sk.waist, 'c': sk.neckb}[origin] if isinstance(origin, str) else origin
    for y, w, df, db, n, push in rings:
        for i in range(n):
            a = 2 * math.pi * i / n + math.pi / n
            x = w * math.sin(a); c = math.cos(a)
            z = (df + push * c * c) * c if c > 0 else db * c
            if side and side * x < -gap:
                x = -side * gap
            pts.append(o + R @ np.array([x, y, z]))
    return hull(pts, color, mat, name, bias)


def hand(sk, k, color, kind='relax', size=None, curl=None, mat='skin'):
    """A low-poly hand at the wrist of arm k: a palm, a block of fingers (bent by `curl`), a thumb.
    kinds: relax, fist, open (fingers apart), point. Hand space: the hand goes down −y, the back of it faces out
    (the figure's side, +x for the left), the thumb is forward (+z)."""
    J = sk.j[k]; s = J['s']; L = size or sk.p['hand']; R = J['Rh']; o = J['wr']
    W = lambda pts: [o + R @ np.array([s * x, y, z]) for x, y, z in pts]
    th = 0.075 * L; w = 0.24 * L
    out = []
    palm = [(th, 0.03 * L, w * 0.8), (th, 0.03 * L, -w * 0.75), (-th, 0.03 * L, w * 0.8), (-th, 0.03 * L, -w * 0.7),
            (th * 0.9, -0.5 * L, w * 1.0), (th * 0.9, -0.5 * L, -w * 0.95), (-th * 0.9, -0.5 * L, w), (-th, -0.5 * L, -w * 0.9),
            (th * 1.15, -0.25 * L, 0)]
    if kind == 'fist':
        palm = [(x * 1.3 if x < 0 else x, y * 0.95, z) for x, y, z in palm]
    out.append(hull(W(palm), color, mat, 'palm'))
    c = curl if curl is not None else {'relax': 28, 'fist': 100, 'open': 6, 'point': 95}[kind]
    knuck = np.array([0, -0.49 * L, 0])
    Rk = Rz(-s * 0 + 0) @ Rz(c * 1.0)  # bend toward the palm (−x in hand space)
    if kind in ('relax', 'fist', 'point'):
        fl = 0.42 * L if kind == 'relax' else 0.26 * L
        blk = [(th * 0.85, 0, w * 0.95), (th * 0.85, 0, -w * 0.9), (-th * 0.85, 0, w * 0.95), (-th * 0.85, 0, -w * 0.85),
               (th * 0.7, -fl, w * 0.75), (th * 0.7, -fl, -w * 0.6), (-th * 0.6, -fl * 0.95, w * 0.7),
               (-th * 0.6, -fl * 0.95, -w * 0.55), (th * 0.2, -fl * 1.06, w * 0.1)]
        if kind == 'fist':
            blk = [(th * 0.9, 0, w * 0.95), (th * 0.9, 0, -w * 0.9), (-th * 1.3, 0, w * 0.95), (-th * 1.3, 0, -w * 0.85),
                   (th * 0.9, -0.24 * L, w * 0.85), (th * 0.9, -0.24 * L, -w * 0.75), (-th * 1.6, -0.2 * L, w * 0.8),
                   (-th * 1.6, -0.2 * L, -w * 0.7)]
            Rk = np.eye(3)
        if kind == 'point':
            blk = [(x, y, z) for x, y, z in blk if z < w * 0.6] + [(th * 0.8, 0, w * 0.15), (-th * 0.8, 0, w * 0.15),
                                                                     (th * 0.8, -fl, w * 0.1), (-th * 0.6, -fl, w * 0.1)]
        pts = [knuck + Rk @ np.array(q) for q in blk]
        out.append(hull(W(pts), color, mat, 'fingers'))
        if kind == 'point':
            pts = [knuck + np.array(q) for q in [(th * .7, 0, w * .95), (-th * .7, 0, w * .95), (th * .7, 0, w * .45),
                                                  (-th * .7, 0, w * .45), (th * .5, -.44 * L, w * .8), (-th * .5, -.44 * L, w * .8),
                                                  (th * .5, -.42 * L, w * .5), (-th * .5, -.42 * L, w * .5)]]
            out.append(hull(W(pts), color, mat, 'index'))
    else:   # open: four fingers, spread a little
        for i, (zc, ln, spread) in enumerate([(0.72, 0.4, 8), (0.25, 0.45, 2), (-0.22, 0.43, -4), (-0.66, 0.34, -11)]):
            Rf = Rx(spread) @ Rz(c + 4 * i)
            z0 = zc * w; fw = 0.18 * w * 1.3
            pts = [knuck + np.array([0, 0, z0]) + Rf @ np.array(q) for q in
                   [(th * .8, 0, fw), (th * .8, 0, -fw), (-th * .8, 0, fw), (-th * .8, 0, -fw),
                    (th * .6, -ln * L, fw * .8), (th * .6, -ln * L, -fw * .8), (-th * .6, -ln * L * .97, fw * .8),
                    (-th * .6, -ln * L * .97, -fw * .8)]]
            out.append(hull(W(pts), color, mat, 'finger'))
    # the thumb: from the heel of the palm forward and down
    tc = {'relax': 0.0, 'fist': 1.0, 'open': -0.3, 'point': 1.0}[kind]
    tip = (-th * (0.6 + 1.6 * tc), -0.5 * L + 0.12 * L * tc, w * (1.35 - 0.6 * tc))
    tp = [(th * 0.7, -0.05 * L, w * 0.75), (-th * 0.9, -0.08 * L, w * 0.7), (th * 0.6, -0.26 * L, w * 1.15),
          (-th * 0.9, -0.24 * L, w * 1.1), (tip[0] + th * 0.5, tip[1], tip[2]), (tip[0] - th * 0.5, tip[1], tip[2]),
          (tip[0], tip[1] - 0.04 * L, tip[2] - 0.05 * L)]
    out.append(hull(W(tp), color, mat, 'thumb'))
    return out


def shoe(sk, k, color, kind='shoe', size=None, sole=None, h=None):
    """A shoe or boot in the foot frame: the heel at the ankle, the toe forward (+z)."""
    J = sk.j[k]; F = size or sk.p['foot']; R = J['Rft']; a = J['an']; s = J['s']
    ah = sk.p['ankle_h'] if h is None else h
    w = 0.2 * F
    y0 = -ah
    pts = [(-w * 0.8, y0, -0.22 * F), (w * 0.8, y0, -0.22 * F), (-w, y0, 0.45 * F), (w * 0.95, y0, 0.45 * F),
           (-w * 0.6, y0, 0.74 * F), (w * 0.6, y0, 0.74 * F), (0, y0, 0.78 * F),
           (-w * 0.75, y0 + 0.45 * ah, 0.72 * F), (w * 0.75, y0 + 0.45 * ah, 0.72 * F),
           (-w * 0.85, y0 + 0.9 * ah, 0.36 * F), (w * 0.85, y0 + 0.9 * ah, 0.36 * F),
           (-w * 0.75, 1.0, -0.15 * F), (w * 0.75, 1.0, -0.15 * F), (0, 1.2, -0.24 * F), (0, 1.0, 0.1 * F)]
    if kind == 'boot':
        pts += [(-w * 0.8, ah * 1.4, -0.12 * F), (w * 0.8, ah * 1.4, -0.12 * F), (0, ah * 1.4, 0.12 * F),
                (0, ah * 1.4, -0.22 * F)]
        pts = [(x * 1.15, y, z * 1.04) for x, y, z in pts]
    out = [hull([a + R @ np.array([s * x, y, z]) for x, y, z in pts], color, 'cloth', 'shoe')]
    if sole:
        sp = [(-w * 0.85, y0 - 1.6, -0.24 * F), (w * 0.85, y0 - 1.6, -0.24 * F), (-w * 1.02, y0 - 1.6, 0.45 * F),
              (w * 0.97, y0 - 1.6, 0.45 * F), (-w * 0.6, y0 - 1.6, 0.78 * F), (w * 0.6, y0 - 1.6, 0.78 * F)]
        if kind == 'boot':
            sp = [(x * 1.18, y, z * 1.05) for x, y, z in sp]
        sp = sp + [(x, y0 + 0.2, z) for x, y, z in sp]
        out.append(hull([a + R @ np.array([s * x, y, z]) for x, y, z in sp], sole, 'cloth', 'sole'))
    return out


def ground_shadow(cx, z, w, color='#000000', op=0.16):
    """A flat soft-edged oval of facets under the feet, drawn before the figure (an SVG polygon in world xz)."""
    return dict(cx=cx, z=z, w=w, color=color, op=op)


def band(piece, sk, frame, origin, y0, y1, color, n=24, a0=0.0, a1=360.0, op=1.0, lift=0.12):
    """A stripe round a body piece between heights y0 and y1 of a frame: each corner is carried along a level ray
    from the frame's axis at its own height out onto the piece's facets, so the stripe wraps them and keeps its
    width. Angles from the front (+z), toward +x."""
    import math
    from poly import face_planes, unit
    R = {'p': sk.Rp, 'c': sk.Rc}[frame] if isinstance(frame, str) else frame
    o = {'p': sk.P, 'w': sk.waist, 'c': sk.neckb}[origin] if isinstance(origin, str) else np.asarray(origin, float)
    planes = face_planes(piece.pts, piece.faces)
    def hit(t, y):
        c = o + R @ np.array([0, y, 0]); d = R @ np.array([math.sin(t), 0, math.cos(t)])
        k = min(-(np.dot(nn, c) + oo) / nd for nn, oo in planes for nd in [np.dot(nn, d)] if nd > 1e-9)
        return c + d * (k + lift)
    angs = np.linspace(math.radians(a0), math.radians(a1), n + 1)
    for t0, t1 in zip(angs[:-1], angs[1:]):
        q = [hit(t0, y0), hit(t1, y0), hit(t1, y1), hit(t0, y1)]
        piece.decals.append((np.array(q), hexcol(color), op))
    return piece
