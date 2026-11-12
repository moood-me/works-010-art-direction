"""Савелий Петрович, about 70, a watchmaker — grumpy outside, kind inside.
Bald crown with white tufts over the ears, bushy white brows and moustache, a loupe pushed up on the forehead;
a green knitted waistcoat over a white shirt, brown trousers; stooped, looking at a pocket watch."""
import numpy as np
from poly import hull, mirror_x, press, hexcol, mix, tohex
import face as F
import body as B

COL = dict(skin='#e2ae96', hair='#e9e5df', hair2='#c9c4bf', vest='#4f6b45', shirt='#efe9df', trousers='#6b5240',
           shoe='#3f2f27', sole='#231a16', watch='#d9b25a', loupe='#2a2730', brass='#c9a24e')

SPEC = dict(
    skin=COL['skin'], lip='#b9756e', eye='#2c2a33', brow=COL['hair'],
    crown=10.0, skull_w=7.6, back=9.6, face_z=8.4,
    fore_w=4.8, fore_y=7.0, temple_w=7.1,
    brow_y=2.2, brow_z=9.2, brow_w=5.8,
    cheek_w=5.2, cheek_y=-2.6, cheek_z=6.4, zyg_w=6.8,
    low_w=3.8, low_y=-5.4, low_z=7.0, mouth_y=-6.6, mouth_z=8.3, mouth_w=2.2,
    jaw_w=5.6, jaw_y=-7.0, jaw_z=2.4, chin_w=2.0, chin_y=-10.2, chin_z=7.2,
    nose_top=0.4, nose_tip_y=-4.6, nose_tip_z=11.6, nose_w=1.9, nose_base_y=-5.2, nose_bridge=0.3,
    eye_x=3.0, eye_y=-0.5, eye_w=1.45, eye_h=0.62, eye_rest='half', lid_th=0.26, iris=1.0,
    brow_th=0.0, lip_w=1.8, lip_h=0.4, smile=-0.35, lips=False,
    ear_h=6.6, ear_w=1.2, cheek_col='#e08c80', laugh_lines=True,
)

PROP = dict(pelvis_y=77.0, hip_w=9.4, thigh=37.0, shin=36.5, waist=17.0, chest=27.0, neck=6.0, head_off=10.2,
            head_z=2.0, shoulder_w=15.5, sh_drop=5.0, upper_arm=27.0, forearm=24.0, hand=18.0, foot=25.0,
            head_scale=1.28)

POSES = {
    # stooped over the watch in his right hand; the left hand on the small of the back
    'stand': dict(pelvis=(4, 10, 0), spine=(14, 4, -3), neck=(6, -6, 0), head=(0, -14, -4),
                  arm_R=(8, 25, -40, 105, (10, -30, 0)), arm_L=(22, -30, 0, 70, (0, 40, 0)),
                  leg_L=(2, 8, 8, 12, (0, 14)), leg_R=(4, -4, 12, 8, (0, 16))),
    'turn': dict(pelvis=(3, 0, 0), spine=(10, 0, 0), neck=(6, 0, 0), head=(-4, 0, 0),
                 arm_L=(9, 4, 0, 14, (0, 0, 0)), arm_R=(9, 4, 0, 14, (0, 0, 0)),
                 leg_L=(3, 0, 0, 2, (0, 10)), leg_R=(3, 0, 0, 2, (0, 10))),
    'portrait': dict(pelvis=(3, 0, 0), spine=(10, 4, 0), neck=(6, 0, 0), head=(-2, 6, -3),
                     arm_L=(9, 4, 0, 14, (0, 0, 0)), arm_R=(9, 4, 0, 14, (0, 0, 0))),
}
PORTRAIT_POSE = 'portrait'
FIGURE_YAW = -22

EXPR = {   # his own faces: grumpy at rest, the joy is a warm crinkled smile under the moustache
    'rest': dict(brow_up=-0.2, brow_tilt=0.5),
    'joy': dict(brow_up=0.4, brow_tilt=-0.2, eye='smile', crow=1, smile=0.9, cheek_up=0.5),
    'surprise': dict(brow_up=1.3, brow_tilt=-0.2, eye='wide', mouth='o', open=1.0),
    'sad': dict(brow_up=0.4, brow_tilt=-0.9, eye='low', smile=-0.9),
    'anger': dict(brow_up=-0.7, brow_tilt=1.3, eye='narrow', mouth='shout', open=0.9, smile=-0.4),
}


def hair(e):
    h, h2 = COL['hair'], COL['hair2']
    out = []
    # tufts over the ears and round the back, the crown bare
    for s in (1, -1):
        out.append(hull([(s * 6.6, 4.2, 1.4), (s * 8.4, 3.0, 0.2), (s * 9.2, -0.6, -1.6), (s * 8.0, -3.6, -2.4),
                         (s * 7.2, -2.2, 0.8), (s * 6.9, 1.8, -5.6), (s * 8.4, 0.2, -5.0), (s * 7.6, 3.8, -3.6)],
                        h, 'hair', 'tuft'))
        out.append(hull([(s * 8.6, 3.4, -1.0), (s * 10.6, 2.6, -2.6), (s * 10.0, -0.8, -1.4), (s * 8.4, -0.4, 0.6),
                         (s * 9.0, 1.4, -4.4)], h, 'hair', 'wisp'))
        out.append(hull([(s * 7.6, -1.6, -1.0), (s * 9.4, -2.6, -2.6), (s * 8.4, -4.8, -2.0), (s * 7.4, -3.6, -0.2),
                         (s * 7.8, -3.0, -5.0)], h2, 'hair', 'wisp'))
    out.append(hull(mirror_x([(5.8, 2.6, -7.0), (3.0, 2.2, -9.6), (0, 2.4, -10.2), (6.8, -2.4, -6.0), (3.2, -4.0, -8.8),
                              (0, -4.4, -9.4)]), h2, 'hair', 'back'))
    # bushy brows: little roofs over the eyes
    up, tilt = e.get('brow_up', 0), e.get('brow_tilt', 0)
    for s in (1, -1):
        y0 = 1.9 + up
        yin, yout = y0 - tilt * 0.5, y0 + tilt * 0.25 - 0.5
        out.append(hull([(s * 0.9, yin + 0.5, 9.6), (s * 2.6, y0 + 0.9, 9.6), (s * 4.6, yout + 0.6, 8.4),
                         (s * 5.6, yout - 0.5, 7.0), (s * 4.0, yout - 0.2, 9.0), (s * 1.2, yin - 0.4, 9.6),
                         (s * 2.6, y0 + 0.2, 10.4), (s * 4.0, yout + 0.2, 9.4)], h, 'hair', 'brow'))
    # the moustache: two heavy wings from under the nose, drooping
    sm = e.get('smile', SPEC['smile'])
    for s in (1, -1):
        out.append(hull([(s * 0.2, -4.9, 10.6), (s * 1.6, -5.0, 10.0), (s * 3.4, -6.4 + sm * 0.6, 8.6),
                         (s * 3.8, -7.6 + sm * 0.9, 7.6), (s * 2.4, -7.0 + sm * 0.5, 9.0), (s * 0.4, -6.4, 9.8),
                         (s * 1.4, -5.8, 10.6), (s * 2.6, -5.6, 8.6)], h, 'hair', 'moustache'))
    return out


def loupe(where='forehead'):
    """A jeweller's loupe: a short dark cylinder with a brass rim, in his right eye or pushed up on the forehead."""
    import math
    from poly import Rx
    if where == 'eye':
        o, R = np.array([-3.0, -0.5, 8.2]), np.eye(3)
    else:
        o, R = np.array([-2.6, 6.8, 8.2]), Rx(-62)
    cyl = lambda r0, r1, z0, z1: [o + R @ np.array([r * math.cos(t), r * math.sin(t), z])
                                  for t in np.linspace(0, 2 * math.pi, 9)[:-1] for r, z in ((r0, z0), (r1, z1))]
    return [hull(cyl(1.7, 1.45, 0.0, 2.6), COL['loupe'], 'metal', 'loupe'),
            hull(cyl(1.55, 1.55, 2.5, 3.1), COL['brass'], 'metal', 'rim')]


def head(expr, loupe_at='forehead'):
    e = dict(EXPR.get(expr, {})) if isinstance(expr, str) else dict(expr)
    e.setdefault('loupe', loupe_at)
    pcs = F.head(SPEC, e)
    H = pcs[0]
    lp = e.get('loupe', 'forehead')
    if lp == 'forehead':   # its strap round the head
        press(H, [(-6.6, 7.4, 20), (6.6, 7.4, 20), (6.6, 6.6, 20), (-6.6, 6.6, 20)], '#3a3036', 1.0, lift=0.08)
    return pcs + hair(e) + (loupe(lp) if lp else [])


def watch(sk, k):
    J = sk.j[k]; R = J['Rh']; o = J['wr']; s = J['s']
    W = lambda pts: [o + R @ np.array([s * x, y, z]) for x, y, z in pts]
    import math
    case = [(-2.2 + 0.6 * dz, -9.0 + 2.6 * math.cos(a), 2.4 + 2.6 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]
            for dz in (0, 1)]
    face = hull(W(case), COL['watch'], 'metal', 'watch')
    press(face, W([(-3.5, -9.0 + 1.8 * math.cos(a), 2.4 + 1.8 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]),
          '#f4ecd8', 1.0, centre=W([(-1.9, -9.0, 2.4)])[0], lift=0.05)
    return [face]


def figure(pose='stand', expr='rest', over=None):
    q = dict(POSES[pose]); q.update(over or {})
    sk = B.Skel(PROP, q)
    c = COL
    out = []
    for k in ('L', 'R'):
        out += B.leg(sk, k, (6.8, 5.4, 5.6, 4.6), c['trousers'], 'cloth')
        out += B.shoe(sk, k, c['shoe'], sole=c['sole'])
    # trousers up to the waist, the shirt, the waistcoat over it with a pointed hem
    out.append(B.torso_hull(sk, 'p', 'p', [(17, 14.6, 8.6, 8.4, 8, 1.0), (2, 15.8, 8.8, 9.0, 8, 0), (-7, 14.6, 8.0, 8.0, 8, 0)],
                            c['trousers'], name='hips'))
    out.append(B.torso_hull(sk, 'c', 'w', [(-2, 15.2, 9.6, 8.6, 8, 2.0), (12, 15.6, 9.0, 8.8, 8, 0.8),
                                         (21, 14.6, 7.0, 7.6, 8, 0), (26, 9.0, 4.8, 5.6, 8, 0), (28, 5.0, 3.6, 4.0, 6, 0)],
                            c['shirt'], name='shirt'))
    vest = B.torso_hull(sk, 'c', 'w', [(-5, 15.8, 10.4, 9.2, 10, 2.2), (12, 16.2, 9.8, 9.4, 10, 0.8),
                                      (21, 15.4, 7.8, 8.2, 10, 0), (26.5, 9.6, 5.4, 6.2, 10, 0)], c['vest'], name='vest')
    # the V of the neck opening and the buttons
    out.append(vest)
    out.append(B.limb(sk.neckb - sk.Rc @ np.array([0, 2.0, 0]), sk.necktop + sk.Rn @ np.array([0, 2.0, 0]),
                      4.8, 4.4, c['skin'], 'skin', ext=0.1))
    for k in ('L', 'R'):
        out.append(B.shoulder(sk, k, 5.0, c['shirt'], inner=6.0))
        out += B.arm(sk, k, (5.0, 4.0, 3.6), c['shirt'])
        J = sk.j[k]
        cuff = J['wr'] + 0.18 * (J['el'] - J['wr'])
        out.append(B.limb(cuff, J['wr'] + 0.02 * (J['el'] - J['wr']), 3.9, 3.8, c['shirt'], ext=0.0))
    out += B.hand(sk, 'R', c['skin'], 'relax', curl=55)
    out += B.hand(sk, 'L', c['skin'], 'fist')
    if pose == 'stand':
        out += watch(sk, 'R')
    # the vest buttons: pressed on the vest front
    for i in range(4):
        y = 4 + i * 4.2
        pts = sk.at('c', 'w', [(0.0 + dx, y + dy, 30) for dx, dy in [(-0.6, 0), (0, 0.6), (0.6, 0), (0, -0.6)]])
        # pressed along the chest's forward axis
        press(vest, pts, '#d8c38c', 1.0, dir=tuple(sk.Rc[:, 2]), lift=0.1)
    out += sk.place_head(head(expr, 'eye' if pose == 'stand' else None))
    return out, sk
