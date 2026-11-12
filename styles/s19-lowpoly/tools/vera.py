"""Вера, about 40 — strict, clever, tired. A long narrow face, high cheekbones, a straight nose, thin lips;
dark hair pulled into a bun with a grey strand; thin rectangular glasses; a long teal coat, a folder under the arm."""
import math
import numpy as np
from poly import hull, mirror_x, press
import face as F
import body as B

COL = dict(skin='#e4b39c', hair='#3a2c30', hair2='#2a2024', grey='#8d8790', coat='#2f6f73', coat2='#285e62',
           scarf='#8e3a46', trousers='#2b2a35', shoe='#2a2228', sole='#17131a', folder='#c9b48a', frame='#2a2228')

SPEC = dict(
    skin=COL['skin'], lip='#b4545c', eye='#2b2530', brow='#3a2c30',
    crown=10.8, skull_w=6.9, back=9.2, face_z=8.4,
    fore_w=4.4, fore_y=7.6, temple_w=6.6,
    brow_y=2.4, brow_z=9.0, brow_w=5.5,
    cheek_w=5.2, cheek_y=-1.8, cheek_z=6.4, zyg_w=6.7,
    low_w=3.0, low_y=-5.0, low_z=6.9, mouth_y=-6.2, mouth_z=8.1, mouth_w=1.8,
    jaw_w=4.5, jaw_y=-6.6, jaw_z=2.6, chin_w=1.4, chin_y=-9.4, chin_z=6.9,
    nose_top=0.8, nose_tip_y=-4.0, nose_tip_z=10.8, nose_w=1.2, nose_base_y=-4.6,
    eye_x=2.95, eye_y=-0.2, eye_w=1.6, eye_h=0.62, eye_rest='half', lash=0.32, lid_th=0.24,
    brow_th=0.26, brow_len=3.0, brow_lift=0.7, brow_in=1.1, brow_arch=0.7,
    lip_w=1.6, lip_h=0.5, smile=-0.15, mouth_line=0.11,
    ear_h=5.8,
)

EXPR = {
    'rest': dict(brow_up=-0.1, brow_tilt=0.35),
    'joy': dict(brow_up=0.3, brow_tilt=-0.2, eye='smile', mouth='smile', smile=0.7, cheek_up=0.3),
    'surprise': dict(brow_up=1.0, eye='wide', mouth='o', open=0.9),
    'sad': dict(brow_up=0.3, brow_tilt=-0.9, eye='low', mouth='down', smile=-0.6, look=(0, -0.5)),
    'anger': dict(brow_up=-0.6, brow_tilt=1.3, eye='narrow', mouth='tight', smile=-0.5),
}

PROP = dict(pelvis_y=93.0, hip_w=8.2, thigh=44.0, shin=43.0, waist=17.0, chest=29.0, neck=5.5, head_off=10.2,
            shoulder_w=13.4, sh_drop=4.5, upper_arm=28.5, forearm=24.5, hand=17.0, foot=23.0, head_scale=1.24)

POSES = {
    # upright, weight on the left leg, chin a little up, arms crossed over the folder held to her chest
    'stand': dict(pelvis=(0, 8, 3), spine=(-3, -6, -3), neck=(-2, -6, 0), head=(-6, -10, -2),
                  arm_R=(3, 28, -85, 118, (0, 10, 0)), arm_L=(3, 36, -85, 112, (0, 10, 0)),
                  leg_L=(0, 0, 4, 0, (0, 12)), leg_R=(2, 4, 14, 6, (0, 18))),
    'turn': dict(arm_L=(8, 2, 0, 8, (0, 0, 0)), arm_R=(8, 2, 0, 8, (0, 0, 0)),
                 leg_L=(3, 0, 0, 0, (0, 6)), leg_R=(3, 0, 0, 0, (0, 6))),
    'portrait': dict(spine=(-2, -6, 0), neck=(-2, -4, 0), head=(-5, -8, -2), arm_L=(8, 2, 0, 8, (0, 0, 0)),
                     arm_R=(8, 2, 0, 8, (0, 0, 0))),
}
PORTRAIT_POSE = 'portrait'
FIGURE_YAW = -20
PORTRAIT_CAM = (-26, -6, 14.0)


def hair(e):
    h, h2 = COL['hair'], COL['hair2']
    # pulled back smooth from a middle parting
    cap = hull(mirror_x([(0, 12.0, -0.8), (5.0, 10.8, 1.8), (5.4, 10.6, -5.0), (0, 9.6, -9.6), (7.3, 5.0, -1.0),
                         (7.4, 4.0, -6.4), (0, 3.0, -10.4), (6.4, -1.4, -7.4), (0, 8.4, 7.6), (4.4, 8.2, 6.2),
                         (6.7, 5.2, 3.2), (7.3, 1.0, 0.0), (0, -2.0, -9.8)]), h, 'hair', 'cap')
    bun = hull([(x * 0.95, y + 9.6, z - 8.4) for x, y, z in
                mirror_x([(3.6, 0, 0), (2.4, 2.6, -1.0), (0, 3.4, -1.6), (2.6, -2.4, -1.0), (0, -3.2, -1.4),
                          (2.2, 0.4, -4.4), (0, 0, -5.0), (0, 2.0, 1.0)])], h2, 'hair', 'bun')
    out = [cap, bun]
    for sd in (1, -1):   # swept back over the tops of the ears
        out.append(hull([(sd * 4.8, 9.0, 6.0), (sd * 7.6, 6.2, 3.4), (sd * 8.7, 1.6, 0.2), (sd * 8.2, -0.8, -3.8),
                         (sd * 7.4, 3.6, -8.0), (sd * 6.2, 9.0, -4.0), (sd * 7.0, 2.4, 2.6), (sd * 2.0, 10.4, 6.6)],
                        h, 'hair', 'wing'))
    # the grey strand from the temple back
    press(cap, [(4.9, 10.0, 20), (5.6, 9.6, 20), (6.6, 6.2, 20), (6.2, 6.2, 20)], COL['grey'], 0.9, lift=0.08)
    return out


def glasses():
    """Thin rectangular frames in front of the eyes: four bars round each lens and a bridge."""
    fc = COL['frame']; out = []
    z = 8.8
    def bar(a, b, t=0.16):
        a = np.array(a); b = np.array(b)
        cube = [(dx, dy, dz) for dx in (-t, t) for dy in (-t, t) for dz in (-t, t)]
        return hull([a + d for d in cube] + [b + d for d in cube], fc, 'metal', 'frame')
    for s in (1, -1):
        x0, x1, y0, y1 = s * 1.1, s * 5.0, -1.6, 0.9
        zc = z - 1.2
        out += [bar((x0, y1, z), (x1, y1, zc)), bar((x0, y0, z), (x1, y0 + 0.2, zc)), bar((x0, y0, z), (x0, y1, z)),
                bar((x1, y0 + 0.2, zc), (x1, y1, zc)), bar((x1, y1 - 0.2, zc), (s * 7.0, 0.6, 0.0), 0.13)]
    out.append(bar((-1.1, 0.4, z), (1.1, 0.4, z), 0.14))
    return out


def head(expr):
    e = dict(EXPR.get(expr, {})) if isinstance(expr, str) else dict(expr)
    pcs = F.head(SPEC, e)
    H = pcs[0]
    # tiredness: a faint shadow under each eye
    for s in (1, -1):
        press(H, [(s * 1.7, -1.05, 20), (s * 4.3, -0.85, 20), (s * 3.6, -1.6, 20), (s * 2.3, -1.65, 20)],
              '#a8707a', 0.25, lift=0.07)
    return pcs + hair(e) + glasses()


def folder(sk):
    """A folder held upright against her chest, under the crossed arms."""
    pts = sk.at('c', 'w', [(x, y, z) for x in (-7.0, 9.0) for y in (0.0, 24.0) for z in (8.4, 9.6)])
    return [hull(pts, COL['folder'], 'cloth', 'folder')]


def figure(pose='stand', expr='rest', over=None):
    q = dict(POSES[pose]); q.update(over or {})
    sk = B.Skel(PROP, q)
    c = COL
    out = []
    for k in ('L', 'R'):
        J = sk.j[k]
        out += B.leg(sk, k, (6.0, 4.4, 4.6, 3.6), c['trousers'], 'cloth')
        out += B.shoe(sk, k, c['shoe'], sole=c['sole'])
    # the coat: a long straight piece from the shoulders to the calves, belted; a wide collar
    out.append(B.torso_hull(sk, 'c', 'w', [(-3, 11.6, 7.2, 7.0, 8, 0), (13, 12.6, 7.0, 6.8, 8, 1.4),
                                         (22, 13.4, 5.8, 6.0, 8, 0), (26.6, 8.6, 4.4, 4.8, 8, 0), (29.0, 4.6, 3.6, 3.8, 6, 0)],
                            c['coat'], name='coat-top'))
    skirt = B.torso_hull(sk, 'p', 'p', [(17, 11.8, 7.2, 7.0, 8, 0), (2, 14.0, 8.6, 9.4, 8, 0),
                                        (-54, 19.0, 15.5, 12.0, 8, 0)], c['coat'], name='coat-skirt')
    out.append(skirt)
    # the front edge of the coat and the belt
    press(skirt, sk.at('p', 'p', [(0.6, 16, 30), (1.6, 16, 30), (2.2, -54, 30), (1.2, -54, 30)]), c['coat2'], 1.0,
          dir=tuple(sk.Rp[:, 2]), lift=0.1)
    B.band(skirt, sk, 'p', 'p', 14.0, 16.4, c['coat2'], n=16)
    # the scarf at the neck: a small knot of colour
    out.append(B.torso_hull(sk, 'c', 'c', [(-3.0, 5.4, 5.0, 4.4, 6, 0), (1.0, 4.6, 4.4, 4.4, 6, 0)], c['scarf'], name='scarf'))
    out.append(B.limb(sk.neckb - sk.Rc @ np.array([0, 2.0, 0]), sk.necktop + sk.Rn @ np.array([0, 2.0, 0]),
                      4.3, 4.0, c['skin'], 'skin', ext=0.1))
    for k in ('L', 'R'):
        out.append(B.shoulder(sk, k, 4.4, c['coat'], inner=5.0))
        out += B.arm(sk, k, (4.4, 3.5, 3.2), c['coat'])
    out += B.hand(sk, 'R', c['skin'], 'relax', curl=40)
    out += B.hand(sk, 'L', c['skin'], 'relax', curl=40)
    if pose == 'stand':
        out += folder(sk)
    out += sk.place_head(head(expr))
    return out, sk
