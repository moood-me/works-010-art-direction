"""Тим, about 8 — mischievous, curious. A round head with a small face low on it, straw hair in spiky tufts,
freckles; a red-and-white striped T-shirt, blue shorts, a plaster on the knee; about to launch a paper plane."""
import math
import numpy as np
from poly import hull, mirror_x, press
import face as F
import body as B

COL = dict(skin='#f0bea0', hair='#e2b552', hair2='#c4913a', shirt='#f2ece2', stripe='#cf4436', shorts='#3f6596',
           sock='#f1ede6', shoe='#d34d3f', sole='#f1ece4', plane='#f6f3ec', plaster='#e9c79b')

SPEC = dict(
    skin=COL['skin'], lip='#d98b7e', eye='#2c3140', brow='#b58a3c',
    crown=10.6, skull_w=7.3, back=9.0, face_z=8.0,
    fore_w=4.6, fore_y=7.0, temple_w=7.0,
    brow_y=1.4, brow_z=8.6, brow_w=5.4,
    cheek_w=5.2, cheek_y=-3.0, cheek_z=6.6, zyg_w=6.6,
    low_w=4.0, low_y=-5.2, low_z=6.6, mouth_y=-5.2, mouth_z=7.8, mouth_w=2.0,
    jaw_w=5.0, jaw_y=-5.6, jaw_z=2.6, chin_w=1.9, chin_y=-8.0, chin_z=6.4,
    nose_top=-0.6, nose_tip_y=-3.0, nose_tip_z=9.4, nose_w=1.2, nose_base_y=-3.5,
    eye_x=2.9, eye_y=-0.9, eye_w=1.65, eye_h=0.95, iris=0.9, lid_th=0.18, look=(0.35, 0.2),
    brow_th=0.38, brow_len=2.6, brow_lift=0.75, brow_in=1.0,
    lip_w=1.6, lip_h=0.5, smile=0.0, mouth_rest='smirk', lips=False,
    ear_y=-1.4, ear_h=5.2, ear_w=1.3, cheek_col='#ec8f7c',
)

EXPR = {
    'rest': dict(mouth='smirk', brow_up=0.2, brow_tilt=0.4),
    'joy': dict(brow_up=0.5, brow_tilt=0.0, eye='smile', mouth='laugh', open=0.9, smile=0.9, cheek_up=0.4),
    'surprise': dict(brow_up=1.2, eye='wide', mouth='o', open=1.1),
    'sad': dict(brow_up=0.4, brow_tilt=-1.0, eye='low', mouth='down', smile=-0.7, look=(0, -0.6)),
    'anger': dict(brow_up=-0.5, brow_tilt=1.3, eye='narrow', mouth='shout', open=0.7, smile=-0.4),
}

PROP = dict(pelvis_y=63.0, hip_w=6.2, hip_drop=3.0, thigh=29.0, shin=28.0, ankle_h=5.5, foot=18.0,
            waist=12.0, chest=20.0, neck=3.5, head_off=8.8, head_z=0.5, shoulder_w=10.8, sh_drop=2.5,
            upper_arm=20.0, forearm=17.0, hand=12.5, head_scale=1.12)

POSES = {
    # weight forward on the left foot, the right arm back with the paper plane, the left hand out for balance
    'stand': dict(hip=(0, 0, 2), pelvis=(-4, 18, 4), spine=(10, 10, -6), neck=(-6, -10, 2), head=(-6, -16, 8),
                  arm_R=(35, -40, 40, 70, (0, 0, -30)), arm_L=(38, 30, -10, 30, (0, 20, 0)),
                  leg_L=(4, 22, 0, 22, (6, 8)), leg_R=(4, -16, 0, 14, (-14, 10))),
    'turn': dict(arm_L=(10, 2, 0, 12, (0, 0, 0)), arm_R=(10, 2, 0, 12, (0, 0, 0)),
                 leg_L=(4, 0, 0, 0, (0, 8)), leg_R=(4, 0, 0, 0, (0, 8))),
    'portrait': dict(spine=(2, 6, 0), neck=(0, 2, 0), head=(-4, 6, 6), arm_L=(10, 2, 0, 12, (0, 0, 0)),
                     arm_R=(10, 2, 0, 12, (0, 0, 0))),
}
PORTRAIT_POSE = 'portrait'
FIGURE_YAW = 24
PLINTH = 28.0
PORTRAIT_CAM = (20, -7, 14.0)


def hair(e):
    h, h2 = COL['hair'], COL['hair2']
    cap = hull(mirror_x([(0, 12.2, -0.5), (5.0, 11.0, 2.4), (5.6, 10.6, -4.6), (0, 10.0, -9.0), (7.6, 5.4, -0.4),
                         (7.8, 4.0, -6.0), (0, 3.4, -10.0), (6.8, -0.8, -7.4), (0, 8.4, 7.4), (4.6, 7.6, 6.4),
                         (6.9, 4.4, 3.6), (7.6, 1.4, 1.2)]), h, 'hair', 'cap')
    out = [cap]
    # tufts: little pyramids sticking out of the cap, a cowlick on top
    tufts = [((0.6, 11.6, 4.6), (-0.8, 14.0, 6.4), 2.2), ((-3.6, 10.6, 5.6), (-5.8, 11.4, 8.0), 1.9),
             ((3.4, 10.8, 5.2), (5.0, 11.8, 7.8), 1.9), ((-1.2, 12.0, -2.0), (-1.4, 14.6, -3.2), 2.2),
             ((4.4, 10.4, -3.4), (7.4, 11.8, -4.0), 1.9), ((-5.0, 9.6, -3.0), (-8.0, 10.4, -3.6), 1.9),
             ((1.6, 8.8, 7.2), (2.4, 7.0, 10.0), 1.8), ((-2.0, 9.0, 7.0), (-3.6, 6.6, 9.6), 1.8)]
    for i, (a, tip, r) in enumerate(tufts):
        a = np.array(a); tip = np.array(tip)
        d = tip - a; up = np.cross(d, [0.3, 0.2, 1.0])
        u = up / np.linalg.norm(up) * r; v = np.cross(d, u); v = v / np.linalg.norm(v) * r
        pts = [a + u, a - u, a + v * 0.8, a - v * 0.8, tip]
        out.append(hull(pts, h if i % 3 else h2, 'hair', 'tuft'))
    return out


def head(expr):
    e = dict(EXPR.get(expr, {})) if isinstance(expr, str) else dict(expr)
    pcs = F.head(SPEC, e)
    H = pcs[0]
    # freckles: tiny dark diamonds across the nose and cheeks
    for x, y in [(-3.6, -2.3), (-2.6, -2.8), (-4.4, -3.0), (-3.2, -3.5), (2.8, -2.4), (3.8, -2.9), (2.6, -3.4),
                 (4.5, -2.4), (-1.3, -1.9), (1.4, -1.9)]:
        press(H, [(x - 0.22, y, 20), (x, y + 0.2, 20), (x + 0.22, y, 20), (x, y - 0.2, 20)], '#b9714f', 0.8, lift=0.1)
    return pcs + hair(e)


def plane(sk, k):
    """A paper plane held by its keel, nose forward."""
    J = sk.j[k]; R = J['Rh']; o = J['wr']; s = J['s']
    W = lambda pts: [o + R @ np.array([s * x, y, z]) for x, y, z in pts]
    nose = (0, -8.5, 14.0)
    wl = hull(W([(0, -9.5, -6.0), nose, (-9.0, -6.0, -6.0), (0, -8.0, -6.0)]), COL['plane'], 'cloth', 'wing')
    wr = hull(W([(0, -9.5, -6.0), nose, (9.0, -6.0, -6.0), (0, -8.0, -6.0)]), COL['plane'], 'cloth', 'wing')
    keel = hull(W([(0, -9.5, -6.0), nose, (0, -12.5, -5.0), (0.2, -9.5, -6.0)]), COL['plane'], 'cloth', 'keel')
    return [wl, wr, keel]


def figure(pose='stand', expr='rest', over=None):
    q = dict(POSES[pose]); q.update(over or {})
    sk = B.Skel(PROP, q)
    c = COL
    out = []
    for k in ('L', 'R'):
        J = sk.j[k]
        top = J['hip'] + 0.35 * (J['kn'] - J['hip'])
        lg = B.leg(sk, k, (4.4, 3.4, 3.6, 2.4), c['skin'], top=top)
        out += lg
        sock = B.limb(J['an'] + 0.45 * (J['kn'] - J['an']), J['an'], 3.0, 2.7, c['sock'], ext=(0.0, 0.2))
        out.append(sock)
        out += B.shoe(sk, k, c['shoe'], sole=c['sole'])
    # the plaster just under the left knee
    J = sk.j['L']; d = J['Rs'][:, 2]; up = J['Rs'][:, 1]; side = np.cross(up, d)
    m = J['kn'] - up * 3.5 + d * 6
    press(out[1], [m + side * a + up * b for a, b in [(-1.6, -1.0), (1.6, -1.2), (1.6, 1.0), (-1.6, 1.2)]],
          c['plaster'], 1.0, dir=tuple(d), lift=0.1)
    shorts = [B.torso_hull(sk, 'p', 'p', [(10, 11.0, 7.0, 7.0, 8, 0), (0, 12.4, 7.6, 7.8, 8, 0), (-6, 12.2, 7.4, 7.4, 8, 0)],
                           c['shorts'], name='shorts')]
    for k in ('L', 'R'):
        J = sk.j[k]
        shorts += B.chain([J['hip'], J['hip'] + 0.42 * (J['kn'] - J['hip'])], (6.2, 5.6), c['shorts'], cap=(0.0, 0.0))
    out += shorts
    shirt = B.torso_hull(sk, 'c', 'w', [(-5, 11.2, 7.2, 7.0, 8, 0.8), (8, 11.6, 7.0, 7.0, 8, 0.6),
                                       (15, 11.4, 6.0, 6.2, 8, 0), (19.4, 6.4, 3.8, 4.2, 8, 0)], c['shirt'], name='shirt')
    out.append(shirt)
    for y in (-3.0, 1.4, 5.8, 10.2, 14.6):
        B.band(shirt, sk, 'c', 'w', y, y + 2.2, c['stripe'], n=16)
    out.append(B.limb(sk.neckb - sk.Rc @ np.array([0, 1.5, 0]), sk.necktop + sk.Rn @ np.array([0, 2.0, 0]),
                      3.2, 3.0, c['skin'], 'skin', ext=0.1))
    for k in ('L', 'R'):
        J = sk.j[k]
        sh = B.shoulder(sk, k, 3.8, c['shirt'], inner=4.2)
        out.append(sh)
        sleeve = B.limb(J['sh'], J['sh'] + 0.45 * (J['el'] - J['sh']), 3.8, 3.5, c['shirt'], ext=(0.2, 0.0))
        B.band(sleeve, sk, J['Ru'], J['sh'], -6.2, -4.6, c['stripe'], n=12)
        out.append(sleeve)
        out += B.arm(sk, k, (2.9, 2.5, 2.1), c['skin'], 'skin')
    out += B.hand(sk, 'R', c['skin'], 'fist' if pose == 'stand' else 'relax')
    out += B.hand(sk, 'L', c['skin'], 'open' if pose == 'stand' else 'relax')
    if pose == 'stand':
        out += plane(sk, 'R')
    out += sk.place_head(head(expr))
    return out, sk
