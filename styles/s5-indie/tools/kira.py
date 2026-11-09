"""Кира, about 15: prickly and closed — thin, angular, slouching, a fringe over one eye. Built like the four
(cast.py) of the shared volumes, plus the parts of extra.py: sleeves that widen, a lean of the body, patches."""
import math
import geo
from geo import *
from face import eye, brow, mouth, EXPR
from cast import cheat, fs, cheek, hair_cap, small_nose, wrap, ground, order, SKIN, SKIN_SH
from extra import limb, limb2d, mitt, lay, lean, band, front_patch

HAIR = '#2f2937'
HOODIE = '#5b3558'
HOOD = '#4c2b4b'
TROUS = '#3d3a45'
BOOT = '#35303a'
SOLE = '#1f1c23'
ACID = '#d2ea3e'
PAD = '#2b2730'


def kira(yaw=0, ex='neutral', pose='stand'):
    v = View(yaw)
    E = dict(EXPR[ex])
    sw = geo.SW
    P = dict(sclera=False, iris_col='#2a2226', lash=1.7, flick=True, brow_col=HAIR, brow_w=1.9, brow_arch=1, mouth_w=6.5, look=(-3, 1))
    if ex == 'neutral':
        # from under the brows, sideways; the mouth pressed shut
        E.update(lid=(.4, .26), brow=(3, 5), mouth='tight')
    elif ex == 'joy':
        # she never smiles openly: a crooked half-smirk, the lids a little softer
        E.update(lid=(.2, .12), brow=(-3, 1), mouth='half', shut=False)
        P['look'] = (-2, 0)
    elif ex == 'surprise':
        E.update(big=1.1)
    elif ex == 'sad':
        # she hides it: no tear, the look goes down and away
        E.update(lid=(.22, .52), brow=(-2, -8), tear=False)
        P['look'] = (-3, 3)
    elif ex == 'anger':
        E.update(lid=(.5, .12))
    # a longer face than a child's, a small chin
    head = [(-62, 0, 0, 0, -3), (-56, 32, 32, 0, -3), (-40, 53, 52, 0, -3), (-16, 61, 57, 0, -2), (6, 62, 56, 0, 1),
            (24, 58, 51, 0, 4), (40, 47, 41, 0, 8), (52, 31, 28, 0, 11), (59, 13, 14, 0, 12), (61, 0, 0, 0, 12)]
    hp = []
    # the back of the hair: short, cut unevenly — spikes stick out under it
    back = [(-48, 0, 0, 0, -4), (-44, 54, 54, 0, -5), (-20, 67, 62, 0, -8), (10, 69, 60, 0, -10), (30, 65, 52, 0, -12),
            (44, 52, 40, 0, -12), (50, 0, 0, 0, -12)]
    sp = ''
    for phi, y, dx, dy, w in ((-2.7, 32, -3, 20, 20), (-2.0, 30, -6, 19, 20), 
                              (2.0, 30, 6, 21, 20), (2.7, 32, 3, 19, 20), (3.14, 34, 0, 20, 22)):
        x, yy, fc = surf(v, back, phi, y)
        k = math.sin(phi) * v.c + math.cos(phi) * v.s      # which way the tip goes on screen
        sp += limb2d([(x, yy), (x + abs(dx) * (1 if k >= 0 else -1) * max(abs(k), .3), yy + dy)], [w, 2], HAIR, n=4)
    hp.append((4.9, sp))
    hp.append((5, vol(v, back, HAIR)))
    hp.append((20, vol(v, head, SKIN, shade_col=SKIN_SH, off=(-.05, -.05))))
    # the ear on the open side, two small rings in it
    ex_, ey_, ef_ = surf(v, head, cheat(v, -1.6), 12, out=-2)
    if ef_ > .1:
        ear = shape(ellipse_d(ex_, ey_, 7 * ef_ + 2, 11), SKIN, size=18, shade_col=SKIN_SH)
        for dy in (-7, 0):
            ear += f'<circle cx="{f(ex_ - 4 * ef_)}" cy="{f(ey_ + dy)}" r="2.3" fill="none" stroke="#b9c0c6" stroke-width="1.5"/>'
        hp.append((20.5, ear))
    fp = ''
    fp += cheek(v, head, -.62, 28, 9, '#e98a7c', .3)
    fp += cheek(v, head, .62, 28, 9, '#e98a7c', .3)
    for side, phi in ((-1, -.42), (1, .42)):
        x, y, fc = fs(v, head, phi, 13)
        fp += eye(v, x, y, fc, 8.5, 11.5, side, E, P, sw)
        bx, by, bf = fs(v, head, phi * 1.05, -5)
        fp += brow(v, bx, by, bf, 18, side, E, P, sw)
    fp += small_nose(v, head, 28)
    mx, my, mf = fs(v, head, .05, 43)
    fp += mouth(mx, my, mf, E, P, sw)
    hp.append((21, fp))
    # the hairline: a parting on her right, the fringe falls in choppy locks across the face and over her left eye;
    # the hair is tucked behind the right ear
    hl = [(-3.1, 40), (-2.6, 38), (-2.1, 30), (-1.85, 10), (-1.6, -10), (-1.4, -4), (-1.25, 8), (-1.12, -8), (-.95, -24), (-.78, -36),
          (-.62, -30), (-.5, -18), (-.4, -24), (-.26, -6), (-.16, -14), (-.02, 6), (.08, -4), (.2, 18), (.3, 8), (.44, 27),
          (.54, 17), (.68, 31), (.8, 20), (.95, 33), (1.08, 16), (1.22, 30), (1.4, 10), (1.6, 28), (1.8, 14), (2.1, 32),
          (2.6, 38), (3.1, 40)]
    # tufts on the crown
    tf = ''
    for phi, y, dx, dy in ((-.15, -62, 6, -13), (.75, -55, 12, -9)):
        x, yy, fc = surf(v, head, phi, y, out=5)
        tf += limb2d([(x, yy + 6), (x + dx * (v.c + .3), yy + dy)], [15, 2], HAIR, n=4)
    hp.append((21.9, tf))
    hp.append((22, hair_cap(v, head, hl, HAIR, out=6)))
    tilt = {'neutral': 7, 'joy': 4, 'surprise': -1, 'sad': 10, 'anger': 3}.get(ex, 7)
    up = wrap(hp, f'translate({f(13 * v.s)},-300) rotate({f(tilt * v.c + 4 * v.s)})')

    # an oversized hoodie on narrow shoulders: round back, the hips forward
    hoodie = [(-264, 0, 0, 0, -5), (-260, 28, 25, 0, -5), (-250, 41, 32, 0, -6), (-224, 47, 37, 0, -4), (-190, 52, 39, 3, 2),
              (-164, 56, 41, 5, 6), (-150, 54, 39, 6, 7), (-146, 0, 0, 6, 7)]
    hood = [(-276, 0, 0, 0, -20), (-270, 30, 18, 0, -26), (-254, 42, 24, 0, -32), (-236, 36, 20, 0, -30), (-226, 0, 0, 0, -26)]
    up.append((8 if v.depth(0, -30) < 20 else 15.6, vol(v, hood, HOOD, size=60)))
    up.append((10.2, vol(v, hoodie, HOODIE)))
    # the hem band and the strings
    det = ''
    hem = [surf(v, hoodie, -1.5 + i * .15, -157) for i in range(21)]
    hem = [p[:2] for p in hem if p[2] > .05]
    if len(hem) > 2:
        det += stroke(smooth(hem, closed=False), sw * .7, extra='opacity=".7"')
    for a_, y2 in ((-.2, -214), (.16, -206)):
        s1, s2 = surf(v, hoodie, a_, -256, out=1), surf(v, hoodie, a_ * 1.1, y2, out=1)
        if s1[2] > .15:
            det += stroke(f'M{f(s1[0])},{f(s1[1])} Q{f(s1[0] - 2)},{f((s1[1] + s2[1]) / 2)} {f(s2[0])},{f(s2[1])}', 2.6, '#e9e1d4')
    up.append((10.3, det))
    # headphones round the neck: the one acid thing
    nk = [(-270, 34, 29, 0, -6), (-250, 43, 34, 0, -6), (-224, 49, 39, 0, -4)]
    up.append((14, band(v, nk, lambda p: -248 + 22 * math.cos(p), [.8 + i * .1 for i in range(48)], 7, ACID, out=1)))
    for a_ in (-.8, .8):
        cx_, cy_, cf_ = surf(v, nk, a_, -231, out=4)
        if cf_ > -.3:
            k = max(abs(math.sin(a_) * v.c + math.cos(a_) * v.s), .0) * .5 + .5
            cup = shape(ellipse_d(cx_, cy_, 13 * k, 16), ACID, size=28) + shape(ellipse_d(cx_, cy_, 7 * k, 9.5), PAD, shade=False, sw=sw * .7)
            up.append((15 if cf_ > .05 else 8.5, cup))

    # arms: her right hand deep in the pocket, the left hangs — a sleeve too long, the hand half in it
    a1 = [(-41, -250, -2), (-66, -204, -6), (-28, -176, 38)]
    up.append((lay(v, -40, 30, 16, 9.6, -30), limb(v, a1, [21, 24, 23], HOODIE)))
    rows = [(y, .66 if y > -192 else .5) for y in (-198, -192, -180, -168, -160)]
    pk = front_patch(v, hoodie, rows)
    if len(pk) > 4:
        up.append((16.2 if v.depth(-28, 38) > -30 else 10.25, shape(smooth(pk, k=.07), HOODIE, size=70, sw=sw * .9)))
    a2 = [(41, -250, -2), (63, -200, 0), (60, -150, 12)]
    L2 = lay(v, 60, 8, 16, 9.6, -30)
    up.append((L2 - .01, mitt(v, 61, -138, 14, 8.5, SKIN, thumb=(-6, -3, 6))))
    up.append((L2, limb(v, a2, [21, 23, 27], HOODIE)))
    side = {'neutral': -3.5, 'joy': -3, 'surprise': 1, 'sad': -2, 'anger': 2}.get(ex, -3)
    fwd = {'neutral': 7, 'joy': 5, 'surprise': -2, 'sad': 10, 'anger': 8}.get(ex, 7)
    parts = wrap(up, lean(v, side, fwd, (6, -150)))

    # long thin legs: the weight on her left, the right knee out; heavy boots
    legs = {1: [(22, -152, 4), (24, -96, 4), (22, -36, 0)], -1: [(-12, -152, 4), (-33, -98, 14), (-36, -36, 2)]}
    for s_, X in ((1, 22), (-1, -36)):
        parts.append((order(v, 9, X, 0), tube(v, legs[s_], 13, TROUS)))
        Z = 0 if s_ == 1 else 2
        boot = [(-48, 0, 0, X, Z + 1), (-45, 13, 13, X, Z + 1), (-32, 14, 15, X, Z + 2), (-20, 16, 21, X, Z + 7), (-9, 17, 26, X, Z + 10),
                (-7, 0, 0, X, Z + 10)]
        sole = [(-10, 0, 0, X, Z + 10), (-9, 18.5, 27.5, X, Z + 10), (0, 18.5, 27.5, X, Z + 10), (1, 0, 0, X, Z + 10)]
        b = vol(v, sole, SOLE, size=30) + vol(v, boot, BOOT, size=34)
        for y_ in (-39, -31, -23):
            l1, l2 = surf(v, boot, -.5, y_, out=.5), surf(v, boot, .5, y_ + 2, out=.5)
            if l1[2] > .2 and l2[2] > .2:
                b += stroke(f'M{f(l1[0])},{f(l1[1])} L{f(l2[0])},{f(l2[1])}', 2.4, ACID)
        parts.append((order(v, 9.1, X, 0), b))
    parts.append(ground(60))
    return parts
