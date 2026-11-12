"""Марат, about 35, a cook — huge, loud, merry, generous. The biggest of the cast: a barrel chest, heavy shoulders,
thick forearms, big hands, a short neck; short black curls, a thick black beard, a broad nose; a white cook's jacket
with the sleeves rolled up, a long terracotta apron, a towel over the shoulder, a ladle. He laughs with the whole body."""
import math
import numpy as np
from poly import hull, mirror_x, press
import face as F
import body as B

COL = dict(skin='#c98d6a', hair='#231c1f', hair2='#16111a', beard='#211a1d', jacket='#f3ede2', button='#c25a36',
           apron='#c2603a', apron2='#a64f30', trousers='#3a3540', shoe='#2a2326', sole='#141015', towel='#e9dcc4',
           stripe='#c25a36', ladle='#b9b7bd', handle='#7a5338')

SPEC = dict(
    skin=COL['skin'], lip='#a5594e', eye='#221a1c', brow=COL['hair'],
    crown=10.8, skull_w=7.9, back=9.8, face_z=8.8,
    fore_w=5.0, fore_y=7.2, temple_w=7.4,
    brow_y=2.4, brow_z=9.6, brow_w=6.0,
    cheek_w=5.8, cheek_y=-2.2, cheek_z=7.0, zyg_w=7.4,
    low_w=4.6, low_y=-5.0, low_z=7.4, mouth_y=-6.2, mouth_z=8.6, mouth_w=2.6,
    jaw_w=6.2, jaw_y=-7.0, jaw_z=2.8, chin_w=2.6, chin_y=-10.0, chin_z=7.2,
    nose_top=0.6, nose_tip_y=-3.9, nose_tip_z=11.6, nose_w=2.3, nose_base_y=-4.6,
    eye_x=3.2, eye_y=-0.4, eye_w=1.5, eye_h=0.7, iris=0.95, lid_th=0.24,
    brow_th=0.62, brow_len=3.1, brow_lift=0.75, brow_in=1.0, brow_arch=0.3,
    lip_w=2.5, lip_h=0.5, smile=0.9, mouth_rest='laugh', lips=False,
    ear_h=6.0, ear_w=1.2, cheek_col='#c96a58',
)

EXPR = {   # his rest IS a wide laugh
    'rest': dict(eye='smile', crow=1, mouth='laugh', open=1.0, smile=1.0, brow_up=0.4, brow_tilt=-0.2, cheek_up=0.5),
    'joy': dict(eye='smile', crow=1, mouth='laugh', open=1.35, smile=1.0, brow_up=0.7, brow_tilt=-0.3, cheek_up=0.6),
    'surprise': dict(brow_up=1.3, eye='wide', mouth='o', open=1.4),
    'sad': dict(brow_up=0.5, brow_tilt=-1.1, eye='low', mouth='down', smile=-0.8, look=(0, -0.6)),
    'anger': dict(brow_up=-0.7, brow_tilt=1.4, eye='narrow', mouth='shout', open=1.1, smile=-0.3),
}

PROP = dict(pelvis_y=93.0, hip_w=11.5, hip_drop=4.0, thigh=44.0, shin=43.0, ankle_h=8.0, foot=29.0,
            waist=20.0, chest=35.0, neck=3.0, head_off=11.0, head_z=1.5, shoulder_w=23.5, sh_drop=6.5,
            upper_arm=32.0, forearm=28.0, hand=21.0, head_scale=1.3)

POSES = {
    # laughing back, the ladle up in his right hand, the left fist on the hip; the weight on the right leg
    'stand': dict(pelvis=(-4, -8, -3), spine=(-12, -8, 6), neck=(-6, -4, 2), head=(-14, -8, 8),
                  arm_R=(46, 30, 40, 70, (0, 0, -10)), arm_L=(38, -14, -60, 105, (0, 20, 30)),
                  leg_L=(9, 6, 14, 6, (0, 20)), leg_R=(4, -4, 8, 2, (0, 14))),
    'turn': dict(arm_L=(14, 2, 0, 12, (0, 0, 0)), arm_R=(14, 2, 0, 12, (0, 0, 0)),
                 leg_L=(4, 0, 0, 0, (0, 8)), leg_R=(4, 0, 0, 0, (0, 8))),
    'portrait': dict(spine=(-6, -4, 2), neck=(-4, -2, 0), head=(-8, -6, 6), arm_L=(14, 2, 0, 12, (0, 0, 0)),
                     arm_R=(14, 2, 0, 12, (0, 0, 0))),
}
PORTRAIT_POSE = 'portrait'
FIGURE_YAW = 18
PLINTH = 40.0
PORTRAIT_CAM = (16, -10, 11.8)


def hair(e):
    h, h2 = COL['hair'], COL['hair2']
    cap = hull(mirror_x([(0, 12.2, -0.6), (5.6, 11.0, 1.6), (6.0, 10.8, -5.0), (0, 10.0, -9.8), (8.0, 5.4, -1.0),
                         (8.2, 4.0, -6.8), (0, 3.4, -10.8), (7.2, -1.0, -7.8), (0, 9.0, 7.4), (4.8, 8.6, 6.2),
                         (7.4, 5.4, 3.0), (8.0, 1.6, 0.6)]), h, 'hair', 'cap')
    out = [cap]
    # curls: small lumps over the cap
    rnd = np.random.RandomState(4)
    for x, y, z in [(0, 12.4, 2.6), (-3.6, 11.8, 3.6), (3.6, 11.8, 3.4), (-6.0, 9.6, 2.0), (6.0, 9.8, 1.6),
                    (-2.0, 12.6, -2.6), (2.6, 12.4, -3.0), (-5.6, 10.6, -4.6), (5.6, 10.4, -4.8), (0, 11.0, -7.2),
                    (-1.6, 10.6, 6.2), (2.0, 10.4, 6.0), (-7.4, 7.0, -2.4), (7.4, 7.0, -2.6)]:
        r = 2.0 + rnd.rand() * 0.6
        pts = [(x + r * a, y + r * b, z + r * c) for a, b, c in
               [(1, 0, 0), (-1, 0, 0), (0, 0.9, 0), (0, -0.6, 0), (0, 0, 1), (0, 0, -1), (0.6, 0.6, 0.6), (-0.6, 0.6, -0.6)]]
        out.append(hull(pts, h if rnd.rand() > 0.4 else h2, 'hair', 'curl'))
    # the beard: one heavy piece round the jaw, open where the mouth is (two side halves and the chin below it)
    op = e.get('open', 0)
    drop = max(0.0, op - 0.6) * 1.2
    my = SPEC['mouth_y']
    for s in (1, -1):
        out.append(hull([(s * 7.4, 0.6, 1.0), (s * 7.6, -4.0, 0.8), (s * 6.6, -8.0, 2.4), (s * 4.2, -10.6 - drop, 5.6),
                         (s * 3.2, -6.4, 8.8), (s * 5.4, -3.2, 7.4), (s * 6.4, -1.0, 5.4), (s * 6.2, -6.0, -1.0),
                         (s * 2.8, -9.6 - drop, 8.4)], COL['beard'], 'hair', 'beard'))
    out.append(hull(mirror_x([(2.8, my - 1.6 - 1.6 * op, 8.6), (3.6, -10.6 - drop, 6.6), (0, -13.2 - drop, 7.6),
                              (0, -12.4 - drop, 4.0), (2.4, -11.8 - drop, 3.6), (0, my - 1.8 - 1.6 * op, 9.0)]),
                    COL['beard'], 'hair', 'chin-beard'))
    # the moustache above the open mouth
    out.append(hull(mirror_x([(0.4, -4.9, 11.0), (2.0, -4.9, 10.2), (3.4, -5.8 + 0.4, 8.8), (3.0, -6.2 + 0.5, 8.6),
                              (0, -5.6, 10.4)]), COL['beard'], 'hair', 'moustache'))
    return out


def head(expr):
    e = dict(EXPR.get(expr, {})) if isinstance(expr, str) else dict(expr)
    return F.head(SPEC, e) + hair(e)


def ladle(sk, k):
    J = sk.j[k]; R = J['Rh']; o = J['wr']; s = J['s']
    W = lambda pts: [o + R @ np.array([s * x, y, z]) for x, y, z in pts]
    # the handle runs through the fist along the hand's z axis, the bowl at the top end
    hnd = hull(W([(-1.0 + dx, -8.0 + dy, z) for dx in (-0.6, 0.6) for dy in (-0.7, 0.7) for z in (-6.0, 32.0)]),
               COL['handle'], 'cloth', 'handle')
    bowl = []
    for a in np.linspace(0, 2 * math.pi, 9)[:-1]:
        bowl += [(-1.0 + 6.0 * math.cos(a), -8.0 + 6.0 * math.sin(a), 32.0), (-1.0 + 3.6 * math.cos(a), -8.0 + 3.6 * math.sin(a), 36.4)]
    return [hnd, hull(W(bowl), COL['ladle'], 'metal', 'bowl')]


def towel(sk):
    """A towel over the left shoulder: a slab down the front and a shorter one down the back."""
    p = sk.at('c', 'c', [(x, y, z) for x in (9.0, 18.0) for y, z in ((1.0, 10.0), (1.0, -10.0), (2.2, 0.0))])
    front = sk.at('c', 'c', [(x, y, z) for x in (9.4, 17.4) for y, z in ((0.0, 10.2), (-28.0, 15.6), (-28.0, 14.2), (0.0, 8.6))])
    back = sk.at('c', 'c', [(x, y, z) for x in (9.4, 17.4) for y, z in ((0.0, -9.8), (-16.0, -12.8), (-16.0, -11.4), (0.0, -8.4))])
    top = hull(p, COL['towel'], 'cloth', 'towel')
    f = hull(front, COL['towel'], 'cloth', 'towel')
    B.band(f, sk, 'c', sk.neckb + sk.Rc @ np.array([13.4, 0, 12]), -24.0, -22.4, COL['stripe'], n=8)
    B.band(f, sk, 'c', sk.neckb + sk.Rc @ np.array([13.4, 0, 12]), -21.4, -20.6, COL['stripe'], n=8)
    return [top, f, hull(back, COL['towel'], 'cloth', 'towel')]


def figure(pose='stand', expr='rest', over=None):
    q = dict(POSES[pose]); q.update(over or {})
    sk = B.Skel(PROP, q)
    c = COL
    out = []
    for k in ('L', 'R'):
        out += B.leg(sk, k, (10.0, 7.6, 8.0, 5.6), c['trousers'], 'cloth', n=7)
        out += B.shoe(sk, k, c['shoe'], sole=c['sole'])
    # the jacket: a barrel of a chest over a round belly, double-breasted
    out.append(B.torso_hull(sk, 'p', 'p', [(20, 22.0, 14.4, 12.0, 10, 6.0), (6, 22.6, 14.0, 12.4, 10, 5.0),
                                         (-8, 20.0, 11.6, 11.6, 10, 1.0)], c['jacket'], name='belly'))
    jacket = B.torso_hull(sk, 'c', 'w', [(-2, 22.6, 14.6, 12.4, 10, 5.4), (14, 24.6, 14.2, 12.8, 10, 3.0),
                                        (26, 24.4, 11.0, 11.0, 10, 0.6), (32.5, 15.0, 7.0, 7.8, 10, 0), (35.0, 8.0, 5.0, 5.8, 8, 0)],
                         c['jacket'], name='jacket')
    out.append(jacket)
    for i in range(3):   # two rows of buttons
        for x in (-4.6, 4.6):
            y = 8 + i * 6.5
            press(jacket, sk.at('c', 'w', [(x + dx, y + dy, 40) for dx, dy in [(-0.8, 0), (0, 0.8), (0.8, 0), (0, -0.8)]]),
                  c['button'], 1.0, dir=tuple(sk.Rc[:, 2]), lift=0.12)
    # the apron: from the chest to below the knee, a slab over the belly
    ap = B.torso_hull(sk, 'p', 'p', [(33, 10.0, 17.0, -10.0, 8, 5.0), (26, 17.0, 18.0, -8.0, 8, 6.0), (18, 21.0, 18.4, -7.0, 8, 7.4),
                                     (4, 23.8, 17.4, -5.0, 8, 6.4), (-42, 23.0, 14.2, -5.0, 8, 0)], c['apron'], name='apron')
    out.append(ap)
    B.band(ap, sk, 'p', 'p', 15.2, 17.2, c['apron2'], n=16, a0=-80, a1=80)
    # collar
    out.append(B.torso_hull(sk, 'c', 'c', [(-2.5, 9.0, 7.8, 6.8, 8, 0), (1.6, 7.6, 6.4, 6.4, 8, 0)], c['jacket'], name='collar'))
    out.append(B.limb(sk.neckb - sk.Rc @ np.array([0, 2.0, 0]), sk.necktop + sk.Rn @ np.array([0, 2.6, 0]),
                      6.6, 6.0, c['skin'], 'skin', ext=0.1))
    for k in ('L', 'R'):
        J = sk.j[k]
        out.append(B.shoulder(sk, k, 7.6, c['jacket'], inner=8.0, top=2.6))
        # sleeves rolled up above the elbow: the jacket to mid upper arm, a fat roll, then the bare thick forearm
        mid = J['sh'] + 0.62 * (J['el'] - J['sh'])
        out += B.chain([J['sh'], mid], (7.6, 6.8), c['jacket'], cap=(0.3, 0.0))
        out.append(B.limb(mid - 0.06 * (J['el'] - J['sh']), mid + 0.1 * (J['el'] - J['sh']), 7.6, 7.4, c['jacket'], ext=0.0, n=8))
        out += B.chain([mid, J['el'], J['wr']], (6.0, 5.6, 4.4), c['skin'], 'skin', cap=(0.0, 0.2))
    out += B.hand(sk, 'R', c['skin'], 'fist')
    out += B.hand(sk, 'L', c['skin'], 'fist')
    if pose == 'stand':
        out += ladle(sk, 'R')
    out += towel(sk)
    out += sk.place_head(head(expr))
    return out, sk
