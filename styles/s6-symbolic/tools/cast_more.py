"""Two more of the cast for style S6: Марат and Кира — each a body, a pose and one or two signs.
Built on the same shared parts as the four (sil.py solids, cast.py limbs and head curves); registered in cast.CAST."""
import random
import numpy as np
from sil import Fig, skel, head_rings, to_world, torso, curve, ring
from cast import WIDTH, BASE, BACK, leg_tube, foot_tube, arm_tube


def hp(B, x, v, z):
    """A point in head space: x across, v 0 chin .. 1 crown, z forward."""
    return np.array([x, -0.14 * B['H'] + v * B['H'], z])


# ============================================================ Марат, ~35: a cook — huge, loud, merry, generous
MARAT_B = dict(thighL=47, shinL=46, ankH=8, footL=30, footR=(4.4, 3.8, 3.1), lowL=27, upL=30, neckL=4.5,
               shW=24.5, shDrop=8.5, hipW=11.5, armU=33, armF=29, H=26, W=9.4, Dp=11.2, Db=11.2)
# a broad short nose, a heavy brow, the mouth open in a laugh between the moustache and the beard
MARAT_PROF = curve([(0, .7), (.06, .9), (.12, .96), (.17, 1.0), (.195, .97), (.215, .80), (.25, .77), (.275, .86),
                    (.30, 1.08), (.33, 1.13), (.37, 1.31), (.41, 1.21), (.47, 1.0), (.52, 1.02), (.56, 1.10),
                    (.62, 1.04), (.72, .98), (.85, .84), (.95, .5), (1, .05)])
MARAT_BEARD = curve([(-.32, .1), (-.24, .5), (-.12, .82), (.03, .98), (.14, .96), (.21, .8)])      # half width × W
MARAT_BEARD_F = curve([(-.32, .62), (-.24, .92), (-.12, 1.09), (0, 1.13), (.1, 1.08), (.2, .98)])  # front × Dp


def marat(pose=None, yaw=0, ladle=True, towel=True, hot=True):
    B = MARAT_B
    # leaning back from the hips, the belly forward, the head thrown back in a laugh; one fist on the hip,
    # the other hand holding the ladle up like a sceptre
    P = dict(lean=-7, hunch=-2, neck=-4, nod=-14, headRoll=0, slump=-1.5,
             armL=(-14, 44, 6, -84), armR=(12, 62, 14, 50), legL=(10, 12, 4, 0), legR=(-8, 12, 2, 0),
             footL=(0, 18), footR=(0, 14))
    P.update(pose or {})
    J = skel(B, P)
    f = Fig()
    for k in 'LR':
        leg_tube(f, J, k, [10.5, 6.4, 6.6, 4.4])
        foot_tube(f, J, k, B)
    # the cook's jacket: a barrel chest and a belly, heavy shoulders, ends at the hips
    f.loft(torso(J, [(-.1, 19.5, 14, 12.5, 0), (.08, 20.5, 16.5, 12.5, 0), (.28, 21.5, 17.5, 12.5, .5),
                     (.5, 23.5, 16.5, 13, 0), (.7, 26, 14, 13, -.5), (.84, 27, 11, 12, -1), (.94, 21, 8.5, 9.5, -1),
                     (1, 9.5, 7.5, 7.5, 0)]))
    # the long apron: a front panel from the belly to the shins — the legs stay seen behind it in profile
    ap = []
    for u in np.linspace(0, 1, 7):
        c = J['pel'] + J['Rlow'] @ np.array([0, B['lowL'] * .30, 0]) * (1 - u) + np.array([0, -(B['thighL'] + B['shinL'] * .22) * u, 0])
        ap.append(c + ring(15.5 - 2.0 * u, 17.6 - 4.0 * u, 2.5 - 2.0 * u, cz=2.0 * (1 - u)))
    f.loft(ap)
    f.tube([J['neck'], J['ntop']], [8.6, 8.0])
    hand = {}
    for k in 'LR':
        # sleeves rolled up above the elbow: a thick roll, then a heavy bare forearm and a big hand
        s0 = J['sh' + k] + (J['el' + k] - J['sh' + k]) * 0.1
        roll = J['sh' + k] + (J['el' + k] - J['sh' + k]) * 0.78
        f.tube([s0, roll, J['el' + k]], [9.2, 8.2, 6.4])
        f.tube([roll], [8.6])
        fore = J['el' + k] + (J['wr' + k] - J['el' + k]) * 0.3
        f.tube([J['el' + k], fore, J['wr' + k]], [6.2, 6.6, 4.6])
        d = J['dh' + k]
        hand[k] = J['wr' + k] + d * 13
        f.tube([J['wr' + k], J['wr' + k] + d * 6.5, hand[k]], [4.4, 5.3, 4.0])
    H, W, Dp, Db = B['H'], B['W'], B['Dp'], B['Db']
    f.loft(head_rings(J, H, W, Dp, Db, MARAT_PROF, BASE, WIDTH, BACK, nose_w=2.2))
    # the beard: a thick spade from under the lower lip, wider than the jaw
    f.loft([to_world(J, ring(MARAT_BEARD(v) * W, MARAT_BEARD_F(v) * Dp, 3.5) + hp(B, 0, v, 0)) for v in np.linspace(-.32, .2, 11)])
    # the moustache over the open mouth
    f.loft([to_world(J, ring(4.6 - abs(v - .30) * 22, 1.5, 1.0, cz=Dp * 1.03) + hp(B, 0, v, 0)) for v in np.linspace(.275, .335, 4)])
    # short curly hair: a cap and curls over it — the edge of the head is scalloped from any side
    cap = []
    for v in np.linspace(.5, 1.02, 9):
        vv = min(v, 1)
        fr = .28 if v < .78 else .28 + (v - .78) / .22 * .8
        cap.append(to_world(J, ring(WIDTH(vv) * W * 1.08 + .4, Dp * BASE(vv) * fr + .5, BACK(vv) * Db * 1.08 + .5) + hp(B, 0, v, .3 / H)))
    f.loft(cap)
    rnd = random.Random(11)
    for v in (.56, .68, .79, .89, .97, 1.03):
        vv = min(v, 1)
        n = 12 if v < .9 else (8 if v < 1 else 3)
        for i in range(n):
            th = (i + rnd.uniform(-.2, .2) + (.5 if int(v * 100) % 2 else 0)) / n * 2 * np.pi
            front = np.sin(th) > .25
            if front and v < .8:
                continue          # the face stays open
            w = WIDTH(vv) * W * 1.08 + .6
            d = (Dp * BASE(vv) * (.5 if v < .9 else .95) + .6) if np.sin(th) > 0 else (BACK(vv) * Db * 1.08 + .7)
            c = np.array([w * np.cos(th), 0, d * np.sin(th)]) + hp(B, 0, v, 0)
            f.tube([to_world(J, c)], [rnd.uniform(2.3, 3.1)])
    acc = []
    if towel:
        # the towel over the shoulder: warm white, the one light thing on him
        sh = J['neck'] + J['Rup'] @ np.array([-15.0, -1.0, 0])
        pts = [sh + J['Rup'] @ np.array(q) for q in ([1.5, -34, 13.5], [.8, -20, 14.2], [.2, -9, 11.5], [0, -3.4, 5.5], [0, -3.2, 0],
                                                     [.1, -6.5, -5.5])]
        acc.append(dict(kind='tube', pts=pts, r=[3.7, 3.5, 3.3, 3.0, 2.9, 2.9], col='#f1e3c8', ref=sh + J['Rup'] @ np.array([0, 0, 12.0])))
    if ladle:
        d = J['dhR']
        top = hand['R'] + d * 25
        f.tube([hand['R'] - d * 6, top], [1.0, .9])
        bowl = top + d * 3.0
        f.loft([ring(r, r, r) + bowl + [0, y, 0] for y, r in ((-4.2, 2.2), (-2.6, 4.6), (0, 5.6), (.8, 5.6))])   # the bowl, flat on top
        if hot:
            acc.append(dict(kind='watch', p=bowl + np.array([0, 1.6, 0]), r=3.4, col='#f08a4b'))
            st = [bowl + np.array([1.4 * np.sin(u * 5.5), 6.5 + 13 * u, 0]) for u in np.linspace(0, 1, 7)]
            acc.append(dict(kind='tube', pts=st, r=[.75, .7, .62, .52, .42, .3, .15], col='#f3d9c0', ref=bowl + [0, 0, 60.0]))
    return J, f, acc


# ============================================================ Кира, ~15: prickly, closed; vulnerable underneath
KIRA_B = dict(thighL=41, shinL=41, ankH=9, footL=25.5, footR=(4.6, 4.4, 3.9), lowL=20, upL=22, neckL=9,
              shW=11.2, shDrop=7.5, hipW=6.2, armU=27, armF=25, H=22.4, W=6.9, Dp=9.0, Db=9.3)
# a long narrow face, a small sharp nose, the lips pressed, a pointed chin
KIRA_PROF = curve([(0, .64), (.06, .84), (.12, .78), (.18, .85), (.235, .90), (.27, .885), (.30, .90), (.335, .93),
                   (.375, 1.10), (.42, 1.0), (.5, .92), (.56, .90), (.62, .94), (.72, .95), (.85, .82), (.95, .5), (1, .05)])


def kira(pose=None, yaw=0, phones=True, pocket=True, hood=1.0):
    B = KIRA_B
    # a slouch: the pelvis forward, the back round, the head down and forward; the weight on one leg, the other
    # knee loose; the hands deep in the hoodie's pocket, the elbows out
    P = dict(lean=-6, hunch=26, neck=14, nod=-10, headRoll=0, slump=3.5, shrug=1.6,
             armL=(-24, 15, 70, -50), armR=(-24, 15, 70, -50), legL=(8, 2, 2, 0), legR=(22, 3, 30, 0),
             footL=(0, 4), footR=(8, 2))
    P.update(pose or {})
    J = skel(B, P)
    f = Fig()
    for k in 'LR':
        leg_tube(f, J, k, [5.0, 3.0, 3.2, 2.7])       # narrow trousers on thin long legs
        # heavy boots: a high thick shaft and a thick sole
        up = J['an' + k] + (J['kn' + k] - J['an' + k]) * .34
        f.tube([up, J['an' + k]], [4.3, 4.5])
        foot_tube(f, J, k, B)
    # the oversized hoodie: a box wider than she is, dropped shoulders, the hem below the hips
    f.loft(torso(J, [(-.2, 13.2, 9.6, 9.8, 0), (.1, 13.6, 10, 9.6, 0), (.45, 13.4, 9.4, 9.6, 0), (.75, 14.2, 8.2, 9.2, 0),
                     (.9, 12.5, 6.8, 7.8, 0), (1, 5.4, 4.6, 4.8, 0)]))
    if hood:
        # the hood hanging on the back
        f.tube([J['neck'] + J['Rup'] @ np.array([0, 2.5, -4.5]), J['neck'] + J['Rup'] @ np.array([0, -3.5, -8.5 * hood]),
                J['neck'] + J['Rup'] @ np.array([0, -11, -8.5 * hood])], [5.6, 5.4, 2.6])
    f.tube([J['neck'], J['ntop']], [3.5, 3.2])
    hand = {}
    for k in 'LR':
        # wide long sleeves that swallow the hands
        hand[k] = arm_tube(f, J, k, [5.0, 4.6, 4.0], 8, 3.4, fist=True)
    if pocket:
        c = (hand['L'] + hand['R']) / 2
        f.tube([hand['L'], c, hand['R']], [3.6, 3.8, 3.6])
    H, W, Dp, Db = B['H'], B['W'], B['Dp'], B['Db']
    f.loft(head_rings(J, H, W, Dp, Db, KIRA_PROF, BASE, WIDTH, BACK, nose_w=.9))
    # short choppy hair: a cap, sharp ends sticking out at the nape and the crown
    cap = []
    for v in np.linspace(.36, 1.03, 12):
        vv = min(v, 1)
        fr = .22 if v < .78 else .22 + (v - .78) / .22 * .8
        cap.append(to_world(J, ring(WIDTH(vv) * W * 1.12 + .5, Dp * BASE(vv) * fr + .5, BACK(vv) * Db * 1.12 + .7) + hp(B, 0, v, 0) + [0, .4, 0]))
    f.loft(cap)
    for (x, v, z), (dx, dy, dz), ln in (((0, .38, -Db * .95), (0, -1.1, -1), 5.5), ((2.5, .52, -Db * 1.05), (.3, -.7, -1), 4.0),
                                         
                                         ((W * 1.0, .42, -2), (.8, -1, -.3), 4.5),
                                         ((-W * 1.0, .42, -2), (-.8, -1, -.3), 4.5)):
        b0 = hp(B, x, v, z); dv = np.array([dx, dy, dz], float); dv /= np.linalg.norm(dv)
        f.tube([to_world(J, b0 - dv * 2), to_world(J, b0 + dv * ln * .5), to_world(J, b0 + dv * ln)], [2.4, 1.5, .15])
    # the long fringe: from the crown forward and down over one eye, past the line of the forehead
    for x, ln, fz, w in ((W * .30, 1.0, 1.0, 2.6), (W * .62, .8, .7, 2.2), (-W * .1, .62, .9, 2.0)):
        a = hp(B, x, .93, Dp * .45)
        b = hp(B, x * 1.05, .80, Dp * (.90 + .08 * fz))
        c = hp(B, x * 1.1, .80 - .15 * ln, Dp * (.97 + .07 * fz))
        e = hp(B, x * 1.15, .80 - .35 * ln, Dp * (.96 + .05 * fz))
        f.tube([to_world(J, q) for q in (a, b, c, e)], [w, w, w * .7, .15])
    acc = []
    if phones:
        # headphones round the neck: the one sharp colour on her
        col = '#d2ee3c'
        nc = J['neck'] * .55 + J['ntop'] * .45
        R = J['Rup']
        if phones == 'on':
            # on the head: the band over the crown, a cup on each ear
            for s_ in (-1, 1):
                ref = to_world(J, hp(B, s_ * 40.0, .5, 0))
                band = [to_world(J, hp(B, s_ * (W * 1.16 + .4) * np.cos(t), .50 + .60 * np.sin(t), -1.0)) for t in np.linspace(0, np.pi / 2, 7)]
                acc.append(dict(kind='tube', pts=band, r=[1.15] * 7, col=col, ref=ref))
                c = hp(B, s_ * (W * 1.12 + .6), .47, -1.0)
                acc.append(dict(kind='tube', pts=[to_world(J, c + [0, 1.0, 0]), to_world(J, c + [0, -1.0, 0])], r=[2.7, 2.7], col=col, ref=ref))
            return J, f, acc
        for s_ in (-1, 1):
            ref = nc + R @ np.array([s_ * 30.0, 0, -20.0])
            band = [nc + R @ np.array([s_ * 5.2 * np.cos(t), -1.2 - 5.0 * np.sin(t) ** 2, -7.0 * np.sin(t) - .5]) for t in np.linspace(0, np.pi / 2, 6)]
            acc.append(dict(kind='tube', pts=band, r=[1.0] * 6, col=col, ref=ref))
            c = nc + R @ np.array([s_ * 5.0, -2.0, 1.2])
            acc.append(dict(kind='tube', pts=[c + R @ np.array([0, .7, -.2]), c + R @ np.array([0, -.7, .2])], r=[2.5, 2.5], col=col, ref=ref))
    return J, f, acc


MORE = dict(marat=marat, kira=kira)
MORE_NAMES = dict(marat='Марат', kira='Кира')
