"""Аня, about 20 — warm, trusting, dreamy. Long copper hair, a mustard cardigan over a blue dress."""
import numpy as np
from poly import hull, mirror_x, press
import face as F
import body as B

COL = dict(skin='#eab59a', hair='#b4532f', hair2='#8f3d24', cardigan='#d9a43a', dress='#4f79a8',
           leg='#e3ad94', shoe='#9c3b2c', sole='#5b2a22', book='#7c4f78')

SPEC = dict(
    skin=COL['skin'], lip='#d48a82', eye='#2e2230', brow='#7a3a24',
    crown=10.8, skull_w=6.9, back=9.0, face_z=8.4,
    cheek_w=4.8, cheek_y=-2.4, cheek_z=6.6, zyg_w=6.4,
    low_w=3.2, low_y=-4.8, low_z=7.1, mouth_y=-5.8, mouth_z=8.2, mouth_w=1.9,
    jaw_w=4.8, jaw_y=-6.0, jaw_z=2.8, chin_w=1.5, chin_y=-8.9, chin_z=6.9,
    nose_top=0.4, nose_tip_y=-3.3, nose_tip_z=10.4, nose_w=1.3, nose_base_y=-4.0,
    eye_x=2.95, eye_y=-0.3, eye_w=1.75, eye_h=0.8, lash=0.35, look=(0.15, 0.1),
    brow_th=0.32, brow_len=2.9, brow_lift=0.9, brow_in=1.0, brow_arch=0.6,
    lip_w=1.7, lip_h=0.6, smile=0.25, cheek_col='#e48a7c',
)

PROP = dict(pelvis_y=86.0, hip_w=8.0, thigh=41.0, shin=40.0, waist=16.0, chest=28.0, neck=5.5, head_off=10.0,
            shoulder_w=12.8, sh_drop=4.0, upper_arm=27.0, forearm=23.5, hand=16.0, foot=21.0, head_scale=1.26)

POSES = {
    # weight on the right leg, the left knee forward, a book held to the chest, the head tilted and lifted: a dreamy S
    'stand': dict(hip=(0, 0, 0), pelvis=(0, -6, -5), spine=(-3, 8, 5), neck=(-4, 4, 3), head=(-6, 14, 8),
                  arm_L=(10, -5, -50, 125, (10, 0, -20)), arm_R=(7, -4, 12, 14, (0, 0, 0)),
                  leg_L=(-3, 10, 12, 20, (-5, 6)), leg_R=(1, -2, 6, 2, (0, 14))),
    'portrait': dict(spine=(-2, 6, 2), neck=(-3, 4, 2), head=(-5, 12, 8), arm_L=(9, 2, 0, 10, (0, 0, 0)),
                     arm_R=(9, 2, 0, 10, (0, 0, 0))),
    'turn': dict(arm_L=(9, 2, 0, 10, (0, 0, 0)), arm_R=(9, 2, 0, 10, (0, 0, 0)),
                 leg_L=(3, 0, 0, 0, (0, 6)), leg_R=(3, 0, 0, 0, (0, 6))),
}


def hair(expr='rest'):
    h, h2 = COL['hair'], COL['hair2']
    # the cap: the hairline comes low at the temples and frames the face
    cap = hull(mirror_x([(0, 12.2, -1.0), (5.2, 10.8, 1.8), (5.6, 10.8, -5.2), (0, 9.6, -9.8), (7.5, 5.0, -1.0),
                         (7.7, 4.0, -6.5), (0, 3.0, -10.8), (6.8, -1.0, -8.2), (0, 9.4, 6.8), (4.6, 8.0, 6.2),
                         (6.9, 4.0, 3.6), (7.6, 0.5, 0.8)]), h, 'hair', 'cap')
    back = hull(mirror_x([(6.8, 4.0, -4.0), (0, 5.0, -10.6), (8.0, -6.0, -3.6), (8.6, -16.0, -3.6), (0, -8.0, -10.6),
                          (7.4, -27.0, -3.6), (0, -29.0, -6.5), (5.0, -28.5, -6.0), (7.8, -14.0, -8.0)]), h2, 'hair', 'back')
    # long locks down the sides, close to the cheeks, over the ears, in front of the shoulders
    locks = []
    for s in (1, -1):
        locks.append(hull([(s * 5.4, 9.2, 5.4), (s * 7.0, 5.6, 3.8), (s * 7.6, 1.0, 2.6), (s * 8.2, -9.0, 1.6),
                           (s * 8.4, -20.0 + 2 * (s < 0), 1.8), (s * 6.8, -21.5 + 2 * (s < 0), 2.0), (s * 6.6, -9.0, 3.2),
                           (s * 6.5, 0.5, 4.6), (s * 8.6, -12, -1.0), (s * 7.8, 4.0, -0.5)], h, 'hair', 'lock'))
    # parted a little off the middle; each side sweeps out over the forehead to the temple
    swL = hull([(-0.8, 11.4, 6.2), (-1.0, 9.6, 8.4), (-3.4, 8.4, 8.3), (-6.2, 5.2, 6.4), (-7.3, 2.6, 4.4),
                (-7.6, 6.8, 2.8), (-4.8, 10.8, 5.2), (-2.6, 10.0, 7.6)], h, 'hair', 'sweepR')
    swR = hull([(0.6, 11.4, 6.2), (1.0, 9.8, 8.3), (3.4, 8.8, 8.0), (6.0, 6.0, 6.2), (7.2, 3.2, 4.2),
                (7.6, 7.0, 2.6), (4.6, 10.8, 5.2), (2.4, 10.4, 7.4)], h, 'hair', 'sweepL')
    return [cap, back] + locks + [swL, swR]


def book(sk, k):
    J = sk.j[k]; R = J['Rh']; o = J['wr']; s = J['s']
    W = lambda pts: [o + R @ np.array([s * x, y, z]) for x, y, z in pts]
    pts = [(x, y, z) for x in (-2.6, -0.6) for y in (-1.0, -21.0) for z in (-3.0, 12.0)]
    pages = [(x, y, z) for x in (-2.4, -0.8) for y in (-1.6, -20.4) for z in (-2.4, 11.6)]
    return [hull(W(pts), COL['book'], 'cloth', 'book', bias=0.5)]


PORTRAIT_POSE = 'portrait'


def figure(pose='stand', expr='rest', over=None):
    q = dict(POSES[pose]); q.update(over or {})
    sk = B.Skel(PROP, q)
    c = COL
    out = []
    for k in ('L', 'R'):
        J = sk.j[k]
        top = J['hip'] + 0.45 * (J['kn'] - J['hip'])   # the thigh only from under the skirt
        out += B.leg(sk, k, (5.2, 3.9, 4.2, 2.5), c['leg'], top=top)
        out += B.shoe(sk, k, c['shoe'], sole=c['sole'])
    # the dress: a bodice and a skirt to below the knee
    out.append(B.torso_hull(sk, 'c', 'w', [(-1, 9.6, 6.0, 5.6, 8, 0), (13, 11.4, 6.4, 6.4, 8, 2.6),
                                         (21, 12.4, 5.2, 5.4, 8, 0.8), (26.5, 9.0, 3.8, 4.4, 8, 0), (29, 4.6, 3.2, 3.4, 6, 0)],
                            c['dress'], name='bodice'))
    out.append(B.torso_hull(sk, 'p', 'p', [(16, 9.8, 6.0, 5.6, 10, 0), (3, 13.2, 8.0, 8.8, 10, 0),
                                         (-33, 21.0, 14.0, 13.0, 10, 0)], c['dress'], name='skirt'))
    # the cardigan: two open panels with the back, ending at the hip
    for s in (1, -1):
        out.append(B.torso_hull(sk, 'c', 'w', [(-5, 11.6, 7.2, 7.0, 10, 0), (13, 12.6, 7.4, 7.0, 10, 2.6),
                                             (21, 13.4, 6.0, 6.2, 10, 0.8), (26.5, 10.2, 4.6, 5.0, 10, 0),
                                             (28.6, 5.6, 4.0, 4.2, 8, 0)],
                                c['cardigan'], name='cardigan', side=s, gap=-2.0 if s > 0 else -2.4))
    out.append(B.limb(sk.neckb - sk.Rc @ np.array([0, 2.0, 0]), sk.necktop + sk.Rn @ np.array([0, 2.0, 0]),
                      4.4, 4.1, c['skin'], 'skin', ext=0.1, flat=0.95))
    for k in ('L', 'R'):
        J = sk.j[k]
        out.append(B.shoulder(sk, k, 4.5, c['cardigan'], inner=4.8))
        out += B.arm(sk, k, (4.5, 3.4, 2.9), c['cardigan'])
        out += B.hand(sk, k, c['skin'], 'relax')
    if pose == 'stand':
        out += book(sk, 'L')
    out += sk.place_head(F.head(SPEC, expr) + hair(expr))
    return out, sk
