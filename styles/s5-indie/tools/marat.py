"""Марат, about 35, a cook: the biggest in the cast, loud and merry. Built like the four (cast.py) of the shared
volumes, plus the parts of extra.py: thick limbs that narrow, hands with a thumb, a beard below a line, curls."""
import math
import geo
from geo import *
from face import eye, brow, mouth, EXPR
from cast import cheat, fs, cheek, hair_cap, wrap, ground, order, smooth_pts
from extra import limb, mitt, lay, lean, scallop, mass_below, band, limb2d, front_patch

SKIN_M = '#f1c7a6'
SKIN_M_SH = '#e0a888'
HAIR = '#3a2c33'
SHEEN = '#6b5560'
JACKET = '#f6eedd'
APRON = '#cf6a3f'
TROUS = '#5a5562'
CLOG = '#7a4634'
TOWEL = '#fbf7ec'
STEEL = '#c9cfd3'


def curls(v, head, hairline, out=7):
    """Short curly hair: the head volume a bit larger with a bumpy edge, above a hairline of small waves."""
    big = [(r[0], r[1] + out if r[1] else 0, r[2] + out if r[2] else 0) + tuple(r[3:]) for r in head]
    big = [(big[0][0] - out,) + big[0][1:]] + big[1:]
    cap = poly_d(scallop(vol_outline(v, big), 6.5, 22, phase=.25 + v.t * .6), True)
    keys = [(cheat(v, phi), y) for phi, y in hair_keys_(hairline, v)]
    pts = smooth_pts([surf(v, head, phi, y, out=out)[:2] for phi, y in keys])
    region = poly_d(pts + [(pts[-1][0] + 400, pts[-1][1]), (pts[-1][0] + 400, -600), (pts[0][0] - 400, -600), (pts[0][0] - 400, pts[0][1])], True)
    cid = uid('h')
    o = f'<clipPath id="{cid}"><path d="{region}"/></clipPath><g clip-path="url(#{cid})">{shape(cap, HAIR, size=120)}</g>'
    # a few curls drawn inside, lighter than the hair
    for phi, y, r, a in ((-.75, -50, 9, 30), (-.2, -56, 10, 200), (.35, -52, 9, 80), (.9, -46, 8, 250), (-1.3, -34, 8, 140),
                         (1.4, -32, 8, 320), (.05, -40, 7, 330), (-.5, -38, 7, 100), (2.1, -20, 9, 60), (-2.1, -20, 9, 200),
                         (2.7, -30, 9, 150), (-2.8, 0, 9, 20), (2.4, 8, 8, 280)):
        x, yy, fc = surf(v, head, cheat(v, phi), y, out=out)
        if fc > .3:
            k = max(fc, .5)
            a0 = math.radians(a)
            p = [(x + r * k * math.cos(a0 + t), yy + r * .8 * math.sin(a0 + t)) for t in (0, .9, 1.8, 2.7, 3.6)]
            o += stroke(smooth(p, closed=False), geo.SW * .8, SHEEN)
    return o


def hair_keys_(keys, v):
    from cast import hair_keys
    return hair_keys(keys, v)


def marat(yaw=0, ex='neutral', pose='stand'):
    v = View(yaw)
    E = dict(EXPR[ex])
    sw = geo.SW
    P = dict(sclera=False, iris_col='#2a2022', lash=1.3, brow_col=HAIR, brow_w=3.1, brow_arch=5, mouth_w=19, lip='#b9705c')
    squint = 0
    if ex == 'neutral':
        # his resting face is a wide smile: eyes open, pushed up from below by the cheeks
        E.update(lid=(.04, .04), brow=(-5, 2), mouth='beam')
        squint = .34
    elif ex == 'joy':
        E.update(brow=(-5, 3), mouth='laugh')
    elif ex == 'surprise':
        E.update(brow=(-7, 0))
    elif ex == 'sad':
        E.update(brow=(-4, -11))
    elif ex == 'anger':
        E.update(brow=(5, 10))
    head = [(-70, 0, 0, 0, -3), (-64, 38, 36, 0, -3), (-46, 62, 58, 0, -3), (-20, 72, 64, 0, -1), (6, 76, 65, 0, 2),
            (28, 76, 62, 0, 5), (46, 66, 54, 0, 8), (58, 48, 42, 0, 10), (66, 24, 24, 0, 11), (69, 0, 0, 0, 11)]
    HS = 1.1                 # the head is drawn 1.1 times larger; the line keeps its weight
    geo.SW = sw = sw / HS
    hp = []
    hp.append((20, vol(v, head, SKIN_M, shade_col=SKIN_M_SH, off=(-.05, -.05))))
    for phi in (-1.6, 1.6):
        ex_, ey_, ef_ = surf(v, head, cheat(v, phi), 4, out=-3)
        sgn = -1 if phi < 0 else 1
        side_x = ex_ + sgn * 7 * v.c
        w_ = 8 + 6 * max(0, ef_)
        ear = shape(ellipse_d(side_x, ey_, w_, 15), SKIN_M, size=24, shade_col=SKIN_M_SH)
        if ef_ > .2:
            ear += stroke(f'M{f(side_x - 2 * ef_)},{f(ey_ - 7)} q{f(6 * ef_)},6 0,13', sw * .7)
        hp.append((20.9 if ef_ > .2 else 19.5, ear))

    # the beard: one black mass from ear to ear, under the cheeks and round the mouth
    beard = [(-22, 72, 64, 0, -1), (6, 77.5, 67, 0, 2), (28, 80, 67, 0, 5), (46, 77, 62, 0, 8), (60, 67, 55, 0, 11),
             (72, 52, 44, 0, 13), (81, 32, 29, 0, 14), (86, 12, 12, 0, 14), (87, 0, 0, 0, 14)]
    bl = [(-2.6, 95), (-1.75, 60), (-1.52, -12), (-1.25, -6), (-1.06, 12), (-.9, 27), (-.7, 33), (-.5, 32), (-.34, 26), (-.2, 21),
          (0, 19), (.2, 21), (.34, 26), (.5, 32), (.7, 33), (.9, 27), (1.06, 12), (1.25, -6), (1.52, -12), (1.75, 60), (2.6, 95)]
    hp.append((20.6, mass_below(v, beard, bl, HAIR, edge=LINE)))

    fp = ''
    fp += cheek(v, head, -.7, 17, 13, '#ee8a70', .55)
    fp += cheek(v, head, .7, 17, 13, '#ee8a70', .55)
    for side, phi in ((-1, -.4), (1, .4)):
        x, y, fc = fs(v, head, phi, -4)
        fp += eye(v, x, y, fc, 8, 10.5, side, E, P, sw)
        if squint and fc > .12:
            # the lower lid pushed up by the smiling cheek
            rx = 8 * max(fc, .25) ** .85
            yy = y + 10.5 * (1 - 2 * squint)
            fp += (f'<path d="M{f(x - rx * 1.5)},{f(yy + 3)} Q{f(x)},{f(yy - 5)} {f(x + rx * 1.5)},{f(yy + 3)} L{f(x + rx * 1.5)},{f(y + 13)} L{f(x - rx * 1.5)},{f(y + 13)} Z" fill="{SKIN_M}"/>'
                   + stroke(f'M{f(x - rx * 1.25)},{f(yy + 1.8)} Q{f(x)},{f(yy - 4.5)} {f(x + rx * 1.25)},{f(yy + 1.8)}', sw * .9))
        if ex == 'joy' and fc > .3:
            ox = x + side * 13 * fc
            fp += stroke(f'M{f(ox)},{f(y - 3)} l{f(side * 5 * fc)},-3 M{f(ox + side)},{f(y + 2)} l{f(side * 5 * fc)},1', sw * .6, extra='opacity=".6"')
        bx, by, bf = fs(v, head, phi * 1.08, -20)
        fp += brow(v, bx, by, bf, 25, side, E, P, sw)
    hp.append((21, fp))

    # the mouth sits in the beard: teeth and tongue carry it; a closed mouth is a lower lip under the moustache
    mx, my, mf = fs(v, head, 0, 37, out=4)
    mp = ''
    if mf > .1:
        k = max(mf, .3) ** .8
        if E['mouth'] in ('beam', 'laugh', 'clench'):
            mp += mouth(mx, my + (0 if E['mouth'] != 'clench' else 2), mf, E, P, sw)
        elif E['mouth'] == 'o':
            mp += shape(ellipse_d(mx, my + 7, 8 * k, 10), '#7b2f35', shade=False, sw=sw) + stroke(ellipse_d(mx, my + 7, 8 * k, 10), sw, P['lip'])
            mp += f'<ellipse cx="{f(mx)}" cy="{f(my + 13)}" rx="{f(5 * k)}" ry="3.5" fill="#e0767a"/>'
        else:   # frown: a pouting lower lip
            mp += shape(f'M{f(mx - 11 * k)},{f(my + 9)} Q{f(mx)},{f(my - 1)} {f(mx + 11 * k)},{f(my + 9)} Q{f(mx)},{f(my + 15)} {f(mx - 11 * k)},{f(my + 9)} Z', '#e59a84', shade=False, sw=sw * .7)
    hp.append((21.3, mp))
    # a broad nose
    nx, ny, nf = fs(v, head, 0, 12, out=4)
    hp.append((21.6, shape(ellipse_d(nx, ny, 14.5, 10.5), '#efb293', size=24, sw=sw)))
    # the moustache: two thick wings over the mouth; they lift with a smile and droop with sadness
    if mf > -.2:
        k = max(mf, .3)
        cx, cy = nx, ny + 9
        R = 31 * k
        lift = {'neutral': -5, 'joy': -8, 'anger': 3, 'sad': 6, 'surprise': -1}.get(ex, 0)
        pts = [(cx, cy - 1), (cx + R * .5, cy - 4), (cx + R, cy + 3 + lift), (cx + R * 1.16, cy + 11 + lift * 1.3),
               (cx + R * .7, cy + 12 + lift * .6), (cx + R * .3, cy + 13), (cx, cy + 9),
               (cx - R * .3, cy + 13), (cx - R * .7, cy + 12 + lift * .6), (cx - R * 1.16, cy + 11 + lift * 1.3), (cx - R, cy + 3 + lift),
               (cx - R * .5, cy - 4)]
        d = smooth(pts)
        hp.append((21.5, f'<path d="{d}" fill="{HAIR}"/>' + stroke(d, sw * .9, SHEEN)))
    hl = [(-3.1, 30), (-2.6, 28), (-2.2, 16), (-1.95, 4), (-1.8, -4), (-1.55, -16), (-1.42, -4), (-1.3, 2), (-1.18, -16), (-1.02, -28), (-.9, -36),
          (-.76, -34), (-.62, -41), (-.48, -38), (-.34, -45), (-.2, -41), (-.06, -47), (.08, -42), (.22, -46), (.36, -40), (.5, -43),
          (.64, -37), (.78, -39), (.9, -33), (1.02, -28), (1.18, -16), (1.3, 2), (1.42, -4), (1.55, -16), (1.8, -4), (1.95, 4),
          (2.2, 16), (2.6, 28), (3.1, 30)]
    hp.append((22, curls(v, head, hl)))
    tilt = {'neutral': -4, 'joy': -9, 'surprise': -3, 'sad': 7, 'anger': -3}.get(ex, -4)
    back = {'joy': 9}.get(ex, 0)          # the head thrown back in a laugh
    hx = -back * v.s * 1.2 + 6 * v.s
    up = wrap(hp, f'translate({f(hx)},{-378 + back * .6:.1f}) rotate({f(tilt * v.c - back * 1.6 * v.s)}) scale({HS})')
    geo.SW = sw = sw * HS

    # the body: a barrel — chest out, belly forward
    torso = [(-338, 0, 0, 0, 2), (-334, 52, 38, 0, 2), (-322, 82, 50, 0, 3), (-296, 94, 60, 0, 5), (-250, 99, 68, 0, 9),
             (-200, 100, 73, 0, 13), (-150, 96, 71, 0, 13), (-114, 88, 62, 0, 9), (-106, 0, 0, 0, 8)]
    up.append((10.0, vol(v, torso, JACKET)))
    # the apron: a bib and a long skirt, in front only
    ap = [(-296, 96, 62, 0, 5), (-250, 101, 70, 0, 9), (-200, 102, 75, 0, 13), (-150, 98, 73, 0, 13), (-112, 92, 66, 0, 10),
          (-78, 88, 62, 0, 9), (-56, 86, 60, 0, 9)]
    rows = [(y, .5 if y < -236 else 1.02) for y in (-290, -270, -250, -238, -234, -214, -190, -160, -130, -100, -74, -56)]
    apd = poly_d(front_patch(v, ap, rows, bottom_wave=5), True)
    big = [(-300, 0, 0, 0, 5)] + ap + [(-50, 0, 0, 0, 9)]
    cid = uid('a')
    apron = f'<clipPath id="{cid}"><path d="{smooth(vol_outline(v, big))}"/></clipPath><g clip-path="url(#{cid})">{shape(apd, APRON, size=150)}</g>'
    # strings: round the waist and up to the neck
    apron += band(v, ap, -226, [1.02 + i * .1 for i in range(43)], 5, APRON, out=0)
    for s_ in (-1, 1):
        a_ = surf(v, ap, s_ * .46, -290)
        b_ = surf(v, torso, s_ * .34, -326, out=1)
        if a_[2] > .05 and b_[2] > .05:
            dd = f'M{f(a_[0])},{f(a_[1] + 2)} L{f(b_[0])},{f(b_[1])}'
            apron += stroke(dd, 5 + 2 * sw, cap='butt') + stroke(dd, 5, APRON, cap='butt')
    # a pocket on the skirt of the apron
    pk = [surf(v, ap, a_, y_, out=1) for a_, y_ in ((-.3, -176), (.3, -176), (.28, -138), (0, -132), (-.28, -138))]
    if min(p[2] for p in pk) > .2:
        apron += stroke(smooth([p[:2] for p in pk], closed=True, k=.06), sw * .8)
    up.append((10.3, apron))
    # two rows of buttons above the bib
    det = ''
    for a_, y_ in ((-.2, -306), (.2, -306)):
        b_ = surf(v, torso, a_, y_, out=1)
        if b_[2] > .2:
            det += f'<circle cx="{f(b_[0])}" cy="{f(b_[1])}" r="3.6" fill="{JACKET}" stroke="{LINE}" stroke-width="{f(sw * .6)}"/>'
    up.append((10.35, det))
    # the towel over his left shoulder
    tw = [(-66, -322, -34), (-68, -342, 0), (-66, -318, 42), (-62, -262, 60)]
    tl = lay(v, -66, 50, 15.4, 9.7, -30)
    tpts = [v.p(*p) for p in tw]
    towel = limb2d(tpts, [24, 26, 27, 28], TOWEL, sw=sw)
    e0, e1 = smooth_pts(tpts, 8)[-5], smooth_pts(tpts, 8)[-1]
    for t in (.25, .6):
        px, py = e0[0] + (e1[0] - e0[0]) * t, e0[1] + (e1[1] - e0[1]) * t
        towel += stroke(f'M{f(px - 12.5)},{f(py + 1)} L{f(px + 12.5)},{f(py - 1)}', 4.5, APRON, cap='butt')
    up.append((tl, towel))

    # arms: sleeves rolled to the elbow, thick forearms, big hands
    if pose == 'calm':
        arms = {-1: [(-90, -306, 4), (-118, -236, 6), (-110, -172, 22)], 1: [(90, -306, 4), (118, -236, 6), (110, -172, 22)]}
        hands = {-1: ((-108, -158, 24), (10, -6, 12)), 1: ((108, -158, 24), (-10, -6, 12))}
    else:
        up_ = {'joy': 26}.get(ex, 0)
        arms = {1: [(90, -306, 4), (132, -252 - up_ * .5, 16), (128, -314 - up_, 42)], -1: [(-90, -306, 4), (-146, -246, -10), (-110, -196, 26)]}
        hands = {1: ((128, -328 - up_, 44), (-15, -4, 10)), -1: ((-104, -188, 32), None)}
    for s_ in (-1, 1):
        S, El, W = arms[s_]
        (hx_, hy_, hz_), th = hands[s_]
        L = lay(v, hx_, hz_, 16, 9.5, -20)
        if pose != 'calm' and s_ == 1:
            # the ladle, held up like a sceptre
            hl_ = [(hx_ + 1, hy_ + 30, hz_), (hx_ - 3, hy_ - 78, hz_ - 4)]
            a, b = v.p(*hl_[0]), v.p(*hl_[1])
            lad = stroke(poly_d([a, b]), 6 + 2 * sw) + stroke(poly_d([a, b]), 6, STEEL)
            bx_, by_ = b
            bowl = f'M{f(bx_ - 21)},{f(by_ - 12)} Q{f(bx_ - 20)},{f(by_ + 14)} {f(bx_)},{f(by_ + 14)} Q{f(bx_ + 20)},{f(by_ + 14)} {f(bx_ + 21)},{f(by_ - 12)} Z'
            lad += shape(bowl, STEEL, size=44) + shape(ellipse_d(bx_, by_ - 12, 21, 6), '#e9eef0', shade=False)
            up.append((L - .02, lad))
        fore = limb(v, [El, W], [37, 28], SKIN_M, shade_col=SKIN_M_SH)
        sleeve = limb(v, [S, El], [46, 42], JACKET)
        ex_, ey_ = v.p(*El)
        sx_, sy_ = v.p(*S)
        ux, uy = ex_ - sx_, ey_ - sy_
        ul = math.hypot(ux, uy) or 1
        ux, uy = ux / ul, uy / ul
        roll = limb2d([(ex_ - ux * 13, ey_ - uy * 13), (ex_ + ux * 1, ey_ + uy * 1)], [47, 47], JACKET, n=3)
        hand = mitt(v, hx_, hy_, hz_, 20, SKIN_M, thumb=th, shade_col=SKIN_M_SH)
        if pose == 'calm' or s_ == -1:
            up.append((L, sleeve + fore + roll + hand))
        else:   # the raised forearm passes in front of the sleeve
            up.append((L, sleeve + roll + fore + hand))
    side = {'neutral': 2.5, 'joy': 3.5, 'sad': 0, 'anger': 0, 'surprise': 0}.get(ex, 0)
    fwd = {'neutral': -3, 'joy': -8, 'sad': 5, 'anger': 3, 'surprise': -4}.get(ex, 0)
    parts = wrap(up, 'translate(0,-8) ' + lean(v, side, fwd, (0, -112)))

    # legs wide apart, clogs
    for X in (-40, 40):
        parts.append((9, tube(v, [(X * .9, -124, 2), (X, -18, 0)], 40, TROUS)))
        cl = [(-26, 0, 0, X, 5), (-23, 19, 18, X, 5), (-12, 22, 27, X, 10), (-2, 22, 30, X, 12), (1, 0, 0, X, 12)]
        parts.append((order(v, 9.1, X, 0), vol(v, cl, CLOG, size=40)))
    parts.append(ground(98))
    return parts
