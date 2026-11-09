"""The cast for style S6: Аня, Савелий Петрович, Тим, Вера — each a body, a pose and one or two signs."""
import numpy as np
from sil import (Fig, skel, head_rings, to_world, torso, skirt, curve, ring, ldir, rx, ry, UP, FWD)

# ------------------------------------------------------------ shared head curves (v: 0 chin .. 1 crown)
WIDTH = curve([(0, .30), (.08, .52), (.2, .74), (.35, .86), (.5, .95), (.65, 1.0), (.8, .93), (.9, .74), (.97, .42), (1, .05)])
BASE = curve([(0, .55), (.1, .72), (.25, .80), (.4, .84), (.55, .86), (.7, .88), (.82, .78), (.92, .55), (1, .05)])
BACK = curve([(0, .05), (.08, .25), (.2, .55), (.35, .82), (.5, .98), (.65, 1.0), (.8, .9), (.9, .68), (1, .05)])


def child_width():
    return curve([(0, .34), (.08, .58), (.2, .80), (.35, .92), (.5, .99), (.65, 1.0), (.8, .95), (.9, .78), (.97, .45), (1, .05)])


def leg_tube(f, J, k, r):
    """r: (hip, knee, calf, ankle) radii; calf bulge a third of the way down the shin."""
    calf = J['kn' + k] + (J['an' + k] - J['kn' + k]) * 0.3
    f.tube([J['hip' + k], J['kn' + k], calf, J['an' + k]], r)


def foot_tube(f, J, k, B):
    f.tube([J['heel' + k], J['ball' + k], J['toe' + k]], B['footR'])


def arm_tube(f, J, k, r, hand_len, hand_r, fist=False):
    s0 = J['sh' + k] + (J['el' + k] - J['sh' + k]) * 0.12
    f.tube([s0, J['el' + k], J['wr' + k]], r)
    d = J['dh' + k]
    end = J['wr' + k] + d * hand_len
    f.tube([J['wr' + k], J['wr' + k] + d * hand_len * 0.45, end], [hand_r * 0.8, hand_r, hand_r * (0.9 if fist else 0.55)])
    return end


def depth_layer(f, J, P, yaw):
    """+1 if point P is nearer the viewer than the body's axis, else -1."""
    c = (J['pel'] + J['neck']) / 2
    return 1 if f.depth(P, yaw) > f.depth(c, yaw) else -1


# ============================================================ Аня, ~20: warm, trusting, dreamy
ANYA_B = dict(thighL=41, shinL=40, ankH=7, footL=22, footR=(2.5, 2.0, 1.4), lowL=22, upL=25, neckL=9.5,
              shW=14.2, shDrop=7.5, hipW=7.2, armU=28, armF=24, H=23, W=7.0, Dp=9.4, Db=9.6)
ANYA_PROF = curve([(0, .62), (.06, .80), (.13, .74), (.19, .86), (.25, .90), (.30, .88), (.335, .93), (.37, 1.08),
                   (.42, 1.0), (.5, .93), (.56, .90), (.62, .95), (.72, .95), (.85, .82), (.95, .5), (1, .05)])


def anya(pose=None, yaw=0, lantern=True):
    B = ANYA_B
    P = dict(nod=-16, headRoll=-5, neck=8, slump=-.5, armL=(6, 7, 14, -2), armR=(10, 5, 22, 0), legL=(2, 2, 2, 0),
             legR=(-4, 3, 4, 0), footL=(0, 10), footR=(0, 4))
    P.update(pose or {})
    J = skel(B, P)
    f = Fig()
    # legs, slim, in dark tights; soft flat shoes
    for k in 'LR':
        leg_tube(f, J, k, [6.5, 3.3, 3.8, 2.0])
        foot_tube(f, J, k, B)
    # body under a soft long coat-dress
    f.loft(torso(J, [(0, 13.5, 9.5, 10, 0), (.25, 11.5, 8.5, 8.5, 0), (.5, 13.0, 9.5, 8.5, 0), (.78, 14.5, 7.5, 7.5, -.5),
                     (.93, 11, 6, 6, -1), (1, 5.2, 4.6, 4.6, 0)]))
    f.loft(skirt(J, (13.5, 9.5, 10), 62, 8.5, 6, n=8, ease=1.3))
    f.tube([J['neck'], J['ntop']], [4.6, 4.2])
    for k in 'LR':
        arm_tube(f, J, k, [3.8, 3.0, 2.3], 11, 2.2)
    hr = head_rings(J, B['H'], B['W'], B['Dp'], B['Db'], ANYA_PROF, BASE, WIDTH, BACK, nose_w=1.0)
    f.loft(hr)
    # hair: a cap a little larger than the skull, side curtains to the shoulders, a long fall down the back
    H, W, Dp, Db = B['H'], B['W'], B['Dp'], B['Db']
    cap = []
    for v in np.linspace(.42, 1.03, 12):
        fr = 0.25 if v < .8 else .25 + (v - .8) / .2 * .7
        r = ring(WIDTH(min(v, 1)) * W * 1.13 + .4, Dp * max(BASE(min(v, 1)), .1) * fr + .5, BACK(min(v, 1)) * Db * 1.12 + .6)
        cap.append(to_world(J, r + [0, -0.14 * H + v * H + .5, 0]))
    f.loft(cap)
    curtain = []
    for v in np.linspace(.0, .5, 6):
        r = ring(W * 1.08 + .6, 1.0, Db * 0.95, n=30)
        curtain.append(to_world(J, r + [0, -0.14 * H + v * H, -1.5]))
    f.loft(curtain)
    # the long fall: from the back of the skull down over the shoulder blades (world space, gravity)
    skull = to_world(J, [0, -0.14 * H + .55 * H, -Db * 1.0])
    mid = to_world(J, [0, -0.14 * H + .55 * H, 0])
    back_z = J['chest'][2] - 8.0
    fall = []
    for u in np.linspace(0, 1, 9):
        y = skull[1] - u * 50
        bz = skull[2] * (1 - u) + (back_z - 2.6) * u
        fz = mid[2] * (1 - min(u * 2.5, 1)) + (back_z + 1.5) * min(u * 2.5, 1)
        w = W * (1.12 + .5 * np.sin(min(u, .55) / .55 * np.pi / 2) - .75 * max(u - .7, 0) / .3) + .5
        th = (fz - bz) / 2 * (1 - .6 * max(u - .75, 0) / .25)
        fall.append(ring(w, th, th, cx=mid[0], cz=fz - th) + [0, y, 0])
    fall.append(ring(W * .35, .3, .3, cx=mid[0], cz=back_z + 1) + [0, skull[1] - 56, 0])
    f.loft(fall)
    acc = []
    if lantern:
        hand = J['wrR'] + J['dhR'] * 13
        lp = hand + np.array([0, -11, 2])
        acc.append(dict(kind='lantern', p=lp, top=hand, size=6.5, col='#ffcf86'))
    return J, f, acc


# ============================================================ Савелий Петрович, ~70: a watchmaker, grumpy, kind
SAV_B = dict(thighL=37, shinL=37, ankH=7.5, footL=26, footR=(3.6, 3.1, 2.6), lowL=21, upL=25, neckL=6,
             shW=17.5, shDrop=8.5, hipW=9, armU=29, armF=26, H=24, W=8.3, Dp=10.4, Db=10.2)
SAV_PROF = curve([(0, .60), (.05, .80), (.12, .80), (.17, .86), (.22, .92), (.255, 1.06), (.29, 1.16), (.33, 1.17),
                  (.37, 1.36), (.42, 1.22), (.5, 1.04), (.56, .96), (.61, 1.08), (.66, 1.04), (.75, .95), (.88, .8),
                  (.96, .5), (1, .05)])


def savely(pose=None, yaw=0, watch=True):
    B = SAV_B
    P = dict(lean=5, hunch=24, neck=14, nod=4, slump=2.5,
             armL=(-24, 10, -12, -84), armR=(4, 10, 66, -62), legL=(4, 1, 6, 0), legR=(-3, 1.5, 4, 0),
             footL=(0, 16), footR=(0, 12))
    P.update(pose or {})
    J = skel(B, P)
    f = Fig()
    for k in 'LR':
        leg_tube(f, J, k, [8, 5.2, 5.6, 3.8])
        foot_tube(f, J, k, B)
    # heavy coat: broad round back, chest sinking, to below the knee
    f.loft(torso(J, [(0, 16.5, 12.5, 11, 0), (.3, 16, 12, 11, 0), (.55, 17.5, 11, 12.5, -.5), (.78, 19, 9, 11.5, -1.5),
                     (.92, 16, 7, 9, -2), (1, 7.5, 6, 6.5, -1)]))
    f.loft(skirt(J, (16.5, 12.5, 11), 46, 4.5, 7.5, n=8, ease=1.1))
    f.tube([J['neck'], J['ntop']], [6.5, 5.5])
    hand = {}
    for k in 'LR':
        hand[k] = arm_tube(f, J, k, [5.4, 4.4, 3.4], 12, 3.0, fist=(k == 'L'))
    H, W, Dp, Db = B['H'], B['W'], B['Dp'], B['Db']
    f.loft(head_rings(J, H, W, Dp, Db, SAV_PROF, BASE, WIDTH, BACK, nose_w=1.6))
    # moustache: a soft heavy mass under the nose, wider than the mouth
    mo = [to_world(J, ring(3.6 - abs(v - .27) * 18, 1.6, 1.0, cz=Dp * 1.06) + [0, -0.14 * H + v * H, 0]) for v in np.linspace(.2, .33, 4)]
    f.loft(mo)
    # flat cap: a crown pulled forward and a short stiff brim
    cap = []
    for i, v in enumerate(np.linspace(.66, 1.05, 8)):
        u = (v - .66) / .39
        w = W * 1.14 * (1 - .35 * u ** 3) + .6
        cap.append(to_world(J, ring(w, Dp * (1.02 + .22 * u), Db * 1.08 * (1 - .4 * u ** 2), cz=1.0 * u) + [0, -0.14 * H + v * H + .4, 0]))
    f.loft(cap)
    brim = [to_world(J, ring(W * .95, Dp * 1.55, Db * .2, cz=0) + [0, -0.14 * H + v * H, 0]) for v in (.665, .70)]
    f.loft(brim)
    acc = []
    # the loupe pushed up on the cap above the brim: a short black cylinder, its glass catching light
    lb = np.array([W * .42, -0.14 * H + .74 * H, Dp * 1.02])
    le = lb + [0, .6, 3.2]
    f.tube([to_world(J, lb), to_world(J, le)], [1.9, 1.7])
    acc.append(dict(kind='glint', p=to_world(J, le + [0, 0, .3]), r=1.1, col='#f3d9a4'))
    if watch:
        acc.append(dict(kind='watch', p=hand['R'] + np.array([0, 1.5, 1.5]), r=2.6, col='#f2b85c'))
        # the chain from the waistcoat pocket to the hand
        pocket = J['chest'] + J['Rup'] @ np.array([-5.0, -4, 11.5])
        acc.append(dict(kind='chain', a=pocket, b=hand['R'], col='#d9a557'))
    return J, f, acc


# ============================================================ Тим, ~8: mischievous, curious
TIM_B = dict(thighL=26, shinL=26, ankH=6, footL=19, footR=(3.2, 3.0, 2.6), lowL=16, upL=16, neckL=4.5,
             shW=10, shDrop=5.5, hipW=5.6, armU=20, armF=18, H=26, W=9.6, Dp=10.2, Db=10.8)
TIM_PROF = curve([(0, .62), (.06, .78), (.13, .76), (.19, .84), (.25, .88), (.31, .90), (.36, .98), (.40, 1.04),
                  (.45, .98), (.52, .92), (.6, .93), (.7, .96), (.85, .86), (.95, .52), (1, .05)])


def tim(pose=None, yaw=0, slingshot=True, scarf_wind=1.0):
    B = TIM_B
    P = dict(lean=-5, hunch=6, neck=10, nod=-22, headRoll=12, headYaw=0, hipShift=0,
             armL=(-30, 14, -50, -60), armR=(-26, 14, -54, -64), legL=(0, 3, 0, 0), legR=(-4, 7, 0, 0),
             footL=(0, 14), footR=(0, 22))
    P.update(pose or {})
    J = skel(B, P)
    f = Fig()
    for k in 'LR':
        leg_tube(f, J, k, [5.2, 3.1, 3.5, 2.5])
        foot_tube(f, J, k, B)
    # an oversized jacket that ends at the hips, shorts under it
    f.loft(torso(J, [(-.05, 10.5, 8.5, 8.5, 0), (.25, 9.8, 7.8, 7.8, 0), (.6, 10.4, 7.8, 7.4, 0), (.85, 10.8, 6.5, 6.5, 0), (1, 5, 4.5, 4.5, 0)]))
    for k in 'LR':   # shorts: a wide short tube over each thigh
        f.tube([J['hip' + k], J['hip' + k] + (J['kn' + k] - J['hip' + k]) * .62], [6.0, 5.0])
    f.tube([J['neck'], J['ntop']], [4.0, 3.6])
    hand = {}
    for k in 'LR':
        hand[k] = arm_tube(f, J, k, [3.6, 3.1, 2.7], 8, 2.1, fist=True)
    H, W, Dp, Db = B['H'], B['W'], B['Dp'], B['Db']
    f.loft(head_rings(J, H, W, Dp, Db, TIM_PROF, BASE, child_width(), BACK, nose_w=1.0))
    # hair: a round tousled cap and the cowlick — three tufts standing up at the crown, a fringe point
    cap = []
    for v in np.linspace(.5, 1.04, 10):
        vv = min(v, 1)
        fr = .3 if v < .78 else .3 + (v - .78) / .22 * .75
        cap.append(to_world(J, ring(child_width()(vv) * W * 1.1 + .5, Dp * BASE(vv) * fr + .6, BACK(vv) * Db * 1.1 + .7) +
                            [0, -0.14 * H + v * H + .3, 0]))
    f.loft(cap)
    crown = np.array([0, -0.14 * H + .98 * H, -Db * .25])
    for dx, dz, ln, lean in ((0, -.5, 9.0, -26), (-.6, 2.2, 5.0, 14)):
        base = crown + [dx, -.5, dz]
        dirv = rx(-lean) @ np.array([dx * .12, 1, 0])
        tip = base + dirv / np.linalg.norm(dirv) * ln
        midp = (base + tip) / 2 + [0, 0, -.8]
        f.tube([to_world(J, base), to_world(J, midp), to_world(J, tip)], [2.2, 1.3, .2])
    fr = np.array([W * .25, -0.14 * H + .86 * H, Dp * .8])
    f.tube([to_world(J, fr), to_world(J, fr + [1.2, -2.8, 1.6])], [1.8, .3])
    acc = []
    # red scarf: a ring round the neck and two tails thrown back by the wind
    nc = (J['neck'] + J['ntop']) / 2
    acc.append(dict(kind='tube', pts=[nc + [0, -1.5, 0]], r=[4.6], col='#d9472f', ref=nc + [0, 0, 6], ring=True))
    t0 = nc + J['Rup'] @ np.array([-2.5, -1, -4.5])
    w = scarf_wind
    pts = [t0]
    for i in range(1, 6):
        u = i / 5
        pts.append(t0 + np.array([-2.5 * w * u, -9 * u + 6 * w * u * u, -19 * w * u]) + np.array([0, 1.4 * np.sin(u * 7) * w, 0]))
    acc.append(dict(kind='tube', pts=pts, r=[2.4, 2.5, 2.4, 2.3, 2.2, 2.0], col='#d9472f', ref=t0))
    if slingshot:
        k = 'R'
        h = hand[k]
        stem = h + np.array([0, 4, -1.5])
        fa = stem + np.array([-1.6, 4.2, -.5]); fb = stem + np.array([1.6, 4.2, -.5])
        f.tube([h, stem], [.8, .8]); f.tube([stem, fa], [.75, .55]); f.tube([stem, fb], [.75, .55])
    return J, f, acc


# ============================================================ Вера, ~40: strict, clever, tired
VERA_B = dict(thighL=44, shinL=43, ankH=7, footL=23, footR=(2.5, 2.0, 1.3), lowL=23, upL=26, neckL=9.5,
              shW=15, shDrop=6.5, hipW=7, armU=30, armF=26, H=23.5, W=6.9, Dp=9.6, Db=9.4)
VERA_PROF = curve([(0, .66), (.06, .86), (.12, .80), (.18, .86), (.24, .89), (.30, .89), (.335, .98), (.38, 1.15),
                   (.44, 1.05), (.5, .97), (.56, .93), (.62, .97), (.72, .96), (.85, .82), (.95, .5), (1, .05)])


def vera(pose=None, yaw=0, folder=True):
    B = VERA_B
    P = dict(nod=8, headRoll=3, slump=1.5, shrug=-.5,
             armL=(18, 3, 58, -80), armR=(4, 5, 6, 0), legL=(0, 1.5, 0, 0), legR=(0, 1.5, 0, 0),
             footL=(0, 7), footR=(0, 9))
    P.update(pose or {})
    J = skel(B, P)
    f = Fig()
    for k in 'LR':
        leg_tube(f, J, k, [6.2, 3.2, 3.6, 1.9])
        foot_tube(f, J, k, B)
    # a long straight coat: shoulders square, a belt, a narrow column to below the knee
    f.loft(torso(J, [(0, 12.5, 9, 9.5, 0), (.25, 11.0, 8, 8, 0), (.3, 11.0, 8, 8, 0), (.55, 13.5, 9, 8.5, 0),
                     (.8, 16.5, 7.5, 7.5, 0), (.92, 13, 6.5, 6.5, 0), (1, 6.5, 5.5, 5.5, 0)]))
    f.loft(skirt(J, (12.5, 9, 9.5), 64, 2.4, 6, n=8, ease=1.6))
    # a high collar round the neck
    f.tube([J['neck'], (J['neck'] * .4 + J['ntop'] * .6)], [5.4, 4.9])
    f.tube([J['neck'], J['ntop']], [4.4, 4.0])
    hand = {}
    for k in 'LR':
        hand[k] = arm_tube(f, J, k, [3.9, 3.2, 2.4], 11, 2.2)
    H, W, Dp, Db = B['H'], B['W'], B['Dp'], B['Db']
    f.loft(head_rings(J, H, W, Dp, Db, VERA_PROF, BASE, WIDTH, BACK, nose_w=1.0))
    # hair pulled back tight (a thin cap), and a high bun at the back of the crown
    cap = []
    for v in np.linspace(.45, 1.01, 10):
        vv = min(v, 1)
        fr = .2 if v < .8 else .2 + (v - .8) / .2 * .72
        cap.append(to_world(J, ring(WIDTH(vv) * W * 1.05 + .3, Dp * BASE(vv) * fr + .3, BACK(vv) * Db * 1.05 + .4) + [0, -0.14 * H + v * H + .2, 0]))
    f.loft(cap)
    bun = np.array([0, -0.14 * H + .86 * H, -Db * .82])
    f.tube([to_world(J, bun), to_world(J, bun + [0, 1.6, -1.2])], [4.4, 4.2])
    acc = []
    # glasses: two lenses catching a cold light
    for s in (-1, 1):
        acc.append(dict(kind='lens', p=to_world(J, [s * W * .38, -0.14 * H + .52 * H, Dp * .98]), r=1.55, col='#e6eefc',
                        head=True))
    if folder:
        # a folder pressed to the chest under the left forearm
        c = J['chest'] + J['Rup'] @ np.array([1.0, -3.0, 12.0])
        R = J['Rup'] @ rx(-14) @ ry(-12)
        pts = []
        for x in (-11.5, 11.5):
            for y in (-15, 15):
                for z in (-1.2, 1.2):
                    pts.append(c + R @ np.array([x, y, z * 1.3]))
        pts = np.array(pts)
        f.loft([pts[:4], pts[4:]])
        J['folder'] = c
    return J, f, acc


CAST = dict(anya=anya, savely=savely, tim=tim, vera=vera)
NAMES = dict(anya='Аня', savely='Савелий Петрович', tim='Тим', vera='Вера')

# the two that joined later live in their own module
from cast_more import MORE, MORE_NAMES
CAST.update(MORE); NAMES.update(MORE_NAMES)
