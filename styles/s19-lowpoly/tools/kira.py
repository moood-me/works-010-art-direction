"""Кира, about 15 — prickly, closed, defiant; vulnerable underneath. Thin and angular, all elbows and knees, a slouch,
the head a little down and the look from under the brows, sideways. Short choppy dark hair, a long fringe over one
eye; an oversized plum hoodie, lime headphones round the neck, narrow charcoal trousers, heavy boots with lime laces."""
import math
import numpy as np
from poly import hull, mirror_x, press
import face as F
import body as B

COL = dict(skin='#ecc0a8', hair='#2a2230', hair2='#1c1622', hoodie='#5b3550', hoodie2='#4a2b42', trousers='#34333b',
           boot='#26222a', sole='#141216', lime='#c8e04a', cup='#2e2b33')

SPEC = dict(
    skin=COL['skin'], lip='#c66f78', eye='#2a2230', brow='#2a2230',
    crown=10.8, skull_w=6.8, back=9.0, face_z=8.2,
    fore_w=4.3, fore_y=7.4, temple_w=6.5,
    brow_y=2.2, brow_z=8.8, brow_w=5.4,
    cheek_w=4.7, cheek_y=-2.4, cheek_z=6.4, zyg_w=6.3,
    low_w=3.0, low_y=-5.0, low_z=6.8, mouth_y=-5.9, mouth_z=8.0, mouth_w=1.8,
    jaw_w=4.6, jaw_y=-6.4, jaw_z=2.6, chin_w=1.3, chin_y=-9.2, chin_z=6.8,
    nose_top=0.4, nose_tip_y=-3.3, nose_tip_z=10.2, nose_w=1.15, nose_base_y=-3.9,
    eye_x=2.9, eye_y=-0.3, eye_w=1.5, eye_h=0.66, eye_rest='half', iris=1.0, lid_th=0.3, lash=0.26,
    look=(0.75, 0.35),
    brow_th=0.34, brow_len=2.8, brow_lift=0.45, brow_in=1.0, brow_arch=0.0,
    lip_w=1.5, lip_h=0.42, smile=0.0, mouth_line=0.12,
    ear_h=5.4,
)

EXPR = {
    'rest': dict(brow_up=-0.3, brow_tilt=0.6, mouth='smirk'),
    'joy': dict(brow_up=0.1, brow_tilt=0.2, eye='half', mouth='smirk', smile=0.4, look=(0.3, 0.0)),
    'surprise': dict(brow_up=1.0, brow_tilt=-0.2, eye='wide', mouth='o', open=0.8, look=(0, 0.2)),
    'sad': dict(brow_up=0.3, brow_tilt=-1.0, eye='low', mouth='down', smile=-0.5, look=(0.4, -0.8)),
    'anger': dict(brow_up=-0.6, brow_tilt=1.4, eye='narrow', mouth='tight', smile=-0.4, look=(0, 0)),
}

PROP = dict(pelvis_y=83.0, hip_w=7.2, hip_drop=3.5, thigh=40.0, shin=39.5, ankle_h=8.0, foot=24.0,
            waist=15.0, chest=26.0, neck=6.0, head_off=10.0, head_z=1.0, shoulder_w=12.0, sh_drop=4.5,
            upper_arm=28.0, forearm=24.0, hand=15.5, head_scale=1.2)

POSES = {
    # a slouch: hips forward, shoulders and head forward and down, the weight on one leg, the other knee bent in;
    # the left hand deep in the hoodie pocket, the right hand at the headphones' cable
    'stand': dict(hip=(0, 0, 3), pelvis=(-8, -12, 5), spine=(16, 6, -6), neck=(14, 10, 0), head=(4, 18, -8),
                  arm_L=(16, 30, -40, 78, (0, -10, 0)), arm_R=(4, 22, -30, 112, (0, 0, 20)),
                  leg_L=(-3, 12, 14, 26, (-4, -8)), leg_R=(8, -4, 4, 2, (0, 12))),
    'turn': dict(pelvis=(-4, 0, 0), spine=(10, 0, 0), neck=(8, 0, 0), head=(2, 0, 0),
                 arm_L=(9, 2, 0, 10, (0, 0, 0)), arm_R=(9, 2, 0, 10, (0, 0, 0)),
                 leg_L=(3, 0, 0, 0, (0, 6)), leg_R=(3, 0, 0, 0, (0, 6))),
    'portrait': dict(pelvis=(-4, 0, 0), spine=(8, 4, 0), neck=(6, 4, 0), head=(2, 6, -6),
                     arm_L=(9, 2, 0, 10, (0, 0, 0)), arm_R=(9, 2, 0, 10, (0, 0, 0))),
}
PORTRAIT_POSE = 'portrait'
FIGURE_YAW = -18
PORTRAIT_CAM = (-12, -6, 14.0)


def hair(e):
    h, h2 = COL['hair'], COL['hair2']
    cap = hull(mirror_x([(0, 12.0, -1.0), (5.2, 10.8, 1.8), (5.6, 10.6, -5.0), (0, 9.6, -9.6), (7.4, 5.0, -1.0),
                         (7.6, 3.6, -6.4), (0, 2.6, -10.6), (6.8, -1.6, -7.2), (0, 9.0, 7.2), (4.4, 8.6, 6.0),
                         (6.9, 4.6, 3.4), (7.4, 0.4, 0.4)]), h, 'hair', 'cap')
    out = [cap]
    # choppy ends: jagged little pieces round the sides and nape
    for x, y, z, dx, dy, dz in [(7.2, 1.0, -2.0, 1.4, -4.6, 0.6), (7.0, 0.6, -6.0, 1.0, -5.0, -1.2),
                                (-7.2, 1.0, -2.0, -1.4, -4.4, 0.6), (-7.0, 0.6, -6.0, -1.0, -5.4, -1.2),
                                (3.6, -1.6, -9.4, 0.6, -4.6, -1.4), (-3.6, -1.6, -9.4, -0.6, -5.0, -1.4),
                                (0, -1.8, -10.0, 0.0, -4.0, -1.2)]:
        b = np.array([x, y, z]); t = b + np.array([dx, dy, dz])
        side = np.cross([dx, dy, dz], [0, 0, 1.0]); side = side / (np.linalg.norm(side) + 1e-9) * 1.8
        out.append(hull([b + side, b - side, b + np.array([0, 0, 1.4]), b - np.array([0, 0, 1.4]), t],
                        h2 if z < -6 else h, 'hair', 'chop'))
    # the long fringe from a side parting falls over her right eye (the viewer's left) to the cheekbone
    fr = hull([(2.8, 11.4, 5.4), (0.4, 10.8, 7.8), (-3.4, 9.0, 8.9), (-5.8, 4.0, 8.4), (-5.0, -1.0, 9.0),
               (-3.2, -2.6, 9.3), (-2.0, 1.4, 9.8), (-0.4, 5.6, 9.6), (-6.8, 7.0, 4.6), (-4.4, 10.2, 6.0)],
              h, 'hair', 'fringe')
    tip = hull([(-3.2, -0.6, 9.4), (-4.6, -0.8, 9.0), (-3.6, -4.4, 8.6), (-2.6, 1.0, 9.8)], h, 'hair', 'tip')
    out += [fr, tip]
    return out


def head(expr):
    e = dict(EXPR.get(expr, {})) if isinstance(expr, str) else dict(expr)
    return F.head(SPEC, e) + hair(e)


def headphones(sk):
    """Round the neck: a lime band behind the neck and two dark cups resting on the collarbones."""
    out = []
    band = sk.at('c', 'c', [(x, y, z) for x, y, z in mirror_x([(6.4, 2.8, -1.0), (5.4, 4.2, -4.6), (0, 4.4, -6.4),
                                                                (6.6, 1.6, -1.4), (5.4, 3.0, -5.4), (0, 3.2, -7.2)])])
    out.append(hull(band, COL['lime'], 'cloth', 'hp-band'))
    for s in (1, -1):
        c = np.array([s * 6.2, 0.6, 4.2])
        pts = []
        for a in np.linspace(0, 2 * math.pi, 9)[:-1]:
            for dx in (-1.2, 1.2):
                pts.append(c + np.array([dx * s * 0.5 + s * 0.0, 3.0 * math.sin(a), 3.0 * math.cos(a)]) +
                           np.array([dx, 0, 0]))
        cup = hull(sk.at('c', 'c', pts), COL['cup'], 'cloth', 'cup')
        out.append(cup)
        ring = [c + np.array([s * 1.5, 2.2 * math.sin(a), 2.2 * math.cos(a)]) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
        ring += [c + np.array([s * 1.9, 2.2 * math.sin(a), 2.2 * math.cos(a)]) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
        out.append(hull(sk.at('c', 'c', ring), COL['lime'], 'cloth', 'cup-ring'))
    return out


def figure(pose='stand', expr='rest', over=None):
    q = dict(POSES[pose]); q.update(over or {})
    sk = B.Skel(PROP, q)
    c = COL
    out = []
    for k in ('L', 'R'):
        J = sk.j[k]
        out += B.leg(sk, k, (5.6, 4.0, 4.2, 3.2), c['trousers'], 'cloth')
        bt = B.shoe(sk, k, c['boot'], kind='boot', sole=c['sole'])
        # lime laces: a few short strokes across the boot's front
        R = J['Rft']; a = J['an']; s = J['s']; F_ = sk.p['foot']
        for i in range(3):
            zc = 0.18 * F_ + i * 0.07 * F_; yc = -sk.p['ankle_h'] * (0.05 - i * 0.12) + 1.2
            pts = [a + R @ np.array([s * x, yc + dy, zc + dz]) for x, dy, dz in
                   [(-1.6, 0.25, 0.4), (1.6, 0.25, 0.4), (1.6, -0.25, -0.4), (-1.6, -0.25, -0.4)]]
            press(bt[0], pts, c['lime'], 1.0, dir=tuple(R @ np.array([0, 0.6, 0.8])), lift=0.1)
        out += bt
    # the hoodie: too big for her, long, hanging straight off the shoulders; a kangaroo pocket
    hood_body = B.torso_hull(sk, 'c', 'w', [(-21, 14.2, 9.0, 8.4, 8, 0), (-2, 14.0, 8.6, 8.4, 8, 0.6),
                                           (12, 13.8, 8.0, 8.0, 8, 0.6), (21, 13.6, 6.6, 7.0, 8, 0),
                                           (25.6, 8.6, 4.8, 5.4, 8, 0), (27.4, 5.4, 4.2, 4.4, 6, 0)],
                               c['hoodie'], name='hoodie')
    out.append(hood_body)
    B.band(hood_body, sk, 'c', 'w', -21.0, -18.4, c['hoodie2'], n=16)
    press(hood_body, sk.at('c', 'w', [(-9.0, -16.6, 40), (9.0, -16.6, 40), (6.4, -4.6, 40), (-6.4, -4.6, 40)]), c['hoodie2'],
          1.0, dir=tuple(sk.Rc[:, 2]), lift=0.12)
    # the hood bunched behind the neck
    out.append(hull(sk.at('c', 'c', mirror_x([(6.6, 1.0, -2.0), (5.4, 4.6, -6.8), (0, 5.4, -8.6), (4.0, -4.0, -8.4),
                                               (0, -5.0, -9.2), (6.0, -2.0, -5.0), (3.4, 2.2, 1.6)])),
                    c['hoodie2'], 'cloth', 'hood'))
    out.append(B.limb(sk.neckb - sk.Rc @ np.array([0, 2.0, 0]), sk.necktop + sk.Rn @ np.array([0, 2.0, 0]),
                      3.9, 3.6, c['skin'], 'skin', ext=0.1))
    # drawstrings
    for s in (1, -1):
        press(hood_body, sk.at('c', 'w', [(s * 2.2, 24.6, 40), (s * 2.9, 24.6, 40), (s * 2.9, 15.6, 40), (s * 2.2, 15.8, 40)]),
              '#e6dde4', 1.0, dir=tuple(sk.Rc[:, 2]), lift=0.14)
    out += headphones(sk)
    for k in ('L', 'R'):
        J = sk.j[k]
        out.append(B.shoulder(sk, k, 4.6, c['hoodie'], inner=4.8))
        out += B.arm(sk, k, (4.6, 4.0, 4.0), c['hoodie'], upto='wr')
        # the sleeve runs past the wrist: a loose cuff over half the hand
        end = J['wr'] + J['Rh'] @ np.array([0, -4.0, 0])
        out.append(B.limb(J['wr'] + 0.15 * (J['el'] - J['wr']), end, 4.0, 3.8, c['hoodie2'], ext=0.0))
    if pose == 'stand':
        out += B.hand(sk, 'R', c['skin'], 'relax', curl=70)   # the left hand is in the pocket
    else:
        out += B.hand(sk, 'R', c['skin'], 'relax', curl=30)
        out += B.hand(sk, 'L', c['skin'], 'relax', curl=30)
    out += sk.place_head(head(expr))
    return out, sk
