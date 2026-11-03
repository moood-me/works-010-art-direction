"""The cast (Аня, Савелий Петрович, Тим, Вера) built of simple volumes. draw(name, yaw, expr) -> list of (layer, svg)."""
import math
import geo
from geo import *
from face import eye, brow, mouth, EXPR

SKIN = '#f7d7bf'
SKIN_SH = '#efbfa6'


def cheat(v, phi):
    """The face part of the head turns a little further than the skull (see fs); the back doesn't."""
    p = (phi + math.pi) % (2 * math.pi) - math.pi
    w = max(0., min(1., (2.6 - abs(p)) / 1.0))
    return phi - .38 * v.s * w


def fs(v, rings, phi, y, out=0):
    """A face feature on the head: turned a little further than the skull in 3/4 and profile, as cartoon
    turnarounds do, so the face doesn't sink into the edge."""
    return surf(v, rings, phi - .38 * v.s, y, out)


def cheek(v, rings, phi, y, r, col, op=.55):
    x, yy, fc = fs(v, rings, phi, y)
    if fc < .2:
        return ''
    return f'<ellipse cx="{f(x)}" cy="{f(yy)}" rx="{f(r * max(fc, .3))}" ry="{f(r * .62)}" fill="{col}" opacity="{op}"/>'


def hair_cap(v, rings, hairline, fill, out=3, line_where=None, shade=True):
    """Hair over the head: the head volume (a bit larger) above a hairline drawn on the surface.
    hairline(phi) -> y (head-local)."""
    big = [(r[0], r[1] + out if r[1] else 0, r[2] + out if r[2] else 0) + tuple(r[3:]) for r in rings]
    big = [(big[0][0] - out,) + big[0][1:]] + big[1:]
    cap = smooth(vol_outline(v, big))
    keys = [(cheat(v, phi), y) for phi, y in hair_keys(hairline, v)]
    pts = [surf(v, rings, phi, y, out=out)[:2] for phi, y in keys]
    pts = smooth_pts(pts)
    region = poly_d(pts + [(pts[-1][0] + 400, pts[-1][1]), (pts[-1][0] + 400, -600), (pts[0][0] - 400, -600), (pts[0][0] - 400, pts[0][1])], True)
    cid = uid('h')
    sz = 120
    o = f'<clipPath id="{cid}"><path d="{region}"/></clipPath><g clip-path="url(#{cid})">'
    o += shape(cap, fill, size=sz, shade=shade, shade_col=SKIN_SH if fill in (SKIN, '#f2cdb3') else None, off=(-.05, -.05) if fill in (SKIN, '#f2cdb3') else (-.09, -.06))
    o += '</g>'
    # the hairline edge, only where it lies on the visible face
    vis = []
    seg = []
    for phi, y in keys:
        x, yy, fc = surf(v, rings, phi, y, out=out)
        if fc > -.05 and (line_where is None or line_where(phi)):
            seg.append((x, yy))
        elif seg:
            vis.append(seg)
            seg = []
    if seg:
        vis.append(seg)
    capclip = uid('h')
    o += f'<clipPath id="{capclip}"><path d="{cap}"/></clipPath><g clip-path="url(#{capclip})">'
    for s in vis:
        if len(s) > 2:
            o += stroke(smooth(s, closed=False))
    o += '</g>'
    return o


def hair_keys(keys, v, lo=-2.0, hi=2.0):
    """Keys (phi, y) on a closed loop, the ones within the visible range around the viewer, ordered."""
    full = []
    for k in (-2 * math.pi, 0, 2 * math.pi):
        full += [(p + k, y) for p, y in keys]
    full.sort()
    c = -v.t
    out = [(p, y) for p, y in full if c + lo <= p <= c + hi]
    return out


def smooth_pts(pts, n=6):
    """Sample a Catmull-Rom curve through pts (open), to get a dense smooth polyline."""
    if len(pts) < 3:
        return pts
    res = []
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            res.append(tuple(.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                   + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    res.append(pts[-1])
    return res


def small_nose(v, head, y, r=4.5):
    """A tiny nose: a short curve from the front, a little bump in profile."""
    nx, ny, nf = surf(v, head, 0, y, out=0)
    if nf < -.05:
        return ''
    if v.s < .85:
        return stroke(f'M{f(nx - 2 + 3 * v.s)},{f(ny)} q{f(2 + 2 * v.s)},2 {f(4)},0', geo.SW * .9)
    # profile: a soft bump past the face edge
    bx, by, _ = surf(v, head, -v.t * .0, y - 4, out=0)
    return (f'<path d="M{f(nx - 3)},{f(ny - 8)} Q{f(nx + r * 1.4)},{f(ny - 2)} {f(nx + r * .3)},{f(ny + 3)} L{f(nx - 6)},{f(ny + 3)} Z" fill="{SKIN}"/>'
            + stroke(f'M{f(nx - 1)},{f(ny - 8)} Q{f(nx + r * 1.4)},{f(ny - 2)} {f(nx + r * .2)},{f(ny + 3)}', geo.SW * .9))


def wrap(parts, tr):
    return [(l, f'<g transform="{tr}">{s}</g>') for l, s in parts]


def ground(rx=70):
    return (-50, f'<ellipse cx="0" cy="2" rx="{rx}" ry="{rx * .16:.1f}" fill="#2a1f3d" opacity=".13"/>')


def order(v, base, X, Z, k=.02):
    return base + v.depth(X, Z) * k


# ---------------------------------------------------------------- Аня
VAR = {}


def anya(yaw=0, ex='neutral', pose='stand'):
    v = View(yaw)
    E = dict(EXPR[ex])
    sw = geo.SW
    HAIR = '#a9573a'
    SWEATER = '#f1c56e'
    SCARF = '#e06650'
    TIGHTS = '#5a4256'
    BOOT = '#7c4b3a'
    P = dict(sclera=False, iris_col='#3d2a2c', lash=1.3, flick=True, brow_col='#7a3e2a', brow_w=1.4, mouth_w=7, smile=3.5, look=(0, -2))
    P.update(VAR.get('P', {}))
    if ex == 'neutral':
        E['lid'] = (0, 0)
    head = [(-70, 0, 0, 0, -4), (-64, 36, 34, 0, -4), (-48, 60, 56, 0, -4), (-24, 68, 62, 0, -3), (0, 70, 62, 0, 0),
            (20, 66, 58, 0, 3), (38, 54, 48, 0, 7), (51, 36, 34, 0, 10), (58, 16, 18, 0, 12), (60, 0, 0, 0, 12)]
    hp = []
    # back hair: a soft bob that falls to the shoulders, with a curled-out end
    back = [(-50, 0, 0, 0, -4), (-46, 62, 58, 0, -5), (-26, 78, 70, 0, -12), (6, 80, 72, 0, -14),
            (36, 82, 66, 0, -16), (56, 88, 60, 0, -18), (68, 92, 52, 0, -20), (73, 0, 0, 0, -20)]
    hp.append((5, vol(v, back, HAIR)))
    hp.append((20, vol(v, head, SKIN, shade_col=SKIN_SH, off=(-.05, -.05))))
    # face
    fp = ''
    fp += cheek(v, head, -.62, 26, 11, '#f08a7a')
    fp += cheek(v, head, .62, 26, 11, '#f08a7a')
    for side, phi in ((-1, -.43), (1, .43)):
        x, y, fc = fs(v, head, phi, 13)
        fp += eye(v, x, y, fc, 10, 14, side, E, P, sw)
        bx, by, bf = fs(v, head, phi * 1.05, -14)
        fp += brow(v, bx, by, bf, 18, side, E, P, sw)
    # a tiny nose: just a small curve
    fp += small_nose(v, head, 25)
    mx, my, mf = fs(v, head, 0, 38)
    fp += mouth(mx, my, mf, E, P, sw)
    hp.append((21, fp))

    # hairline keys (phi, y): parting at +.5, the fringe swept toward -X in three locks; a long lock in front of
    # each ear; above the ears; then the back falls to the nape
    hl = [(-1.95, 72), (-1.6, 46), (-1.3, 40), (-1.12, 22), (-.98, 12),
          (-.9, 10), (-.7, -10), (-.6, 2), (-.52, 4), (-.42, -4), (-.3, -16), (-.14, -4), (-.06, -6), (.06, -18),
          (.3, -32), (.5, -42), (.75, -28), (.95, -10), (1.08, 12), (1.25, 36), (1.6, 46), (1.95, 72)]
    hp.append((22, hair_cap(v, head, hl, HAIR, out=6)))
    # a little hair clip (the second sign: a yellow star)
    cx, cy, cf = surf(v, head, .78, -30, out=4)
    if cf > .05:
        hp.append((23, shape(star_d(cx, cy, 8.5, 4), '#f6d04d', size=16, sw=sw * .8)))
    tilt = {'neutral': 5, 'joy': 3, 'surprise': -2, 'sad': 7, 'anger': -3}.get(ex, 5)
    parts = wrap(hp, f'translate(0,-306) rotate({tilt})')

    # body
    # a flared skirt under a short, cosy sweater
    skirt = [(-140, 0, 0), (-138, 44, 34), (-120, 52, 40), (-100, 64, 48), (-92, 68, 50), (-89, 0, 0)]
    parts.append((10.0, vol(v, skirt, '#3f4f7d')))
    sweater = [(-238, 0, 0), (-234, 30, 26), (-226, 44, 34), (-202, 48, 36), (-170, 50, 37), (-140, 55, 40),
               (-127, 57, 41), (-123, 0, 0)]
    parts.append((10.2, vol(v, sweater, SWEATER)))
    rib = ''
    for i in range(-6, 7):
        phi = i * .24
        x1, y1, f1 = surf(v, sweater, phi, -133)
        x2, y2, f2 = surf(v, sweater, phi, -126)
        if f1 > .15:
            rib += stroke(f'M{f(x1)},{f(y1)} L{f(x2)},{f(y2 + 1)}', geo.SW * .6, extra='opacity=".55"')
    parts.append((10.25, rib))
    scarf = [(-248, 0, 0, 0, 2), (-246, 34, 32, 0, 2), (-238, 47, 40, 0, 4), (-224, 49, 42, 0, 5), (-215, 42, 36, 0, 5), (-213, 0, 0, 0, 5)]
    parts.append((15, vol(v, scarf, SCARF)))
    # scarf ends: one hangs down the chest, one is thrown over the shoulder (moves a little in the wind)
    t1 = [(-16, -222, 44), (-20, -195, 47), (-17, -160, 46)]
    parts.append((order(v, 15.5, -16, 46), tube(v, t1, 20, SCARF, cap='butt')))
    fx, fy = v.p(-17, -160, 46)
    fr = ''
    for i in range(4):
        fr += stroke(f'M{f(fx - 8 + i * 5.3)},{f(fy)} l0,8', sw * .9, SCARF)
    parts.append((order(v, 15.4, -16, 46), f'<g>{fr}</g>'))
    t2 = [(22, -232, 30), (38, -226, -10), (50, -205, -30)]
    parts.append((order(v, 9.5, 30, -30), tube(v, t2, 18, SCARF, cap='butt')))
    # legs and boots
    for X in (-21, 21):
        parts.append((9, tube(v, [(X, -100, 0), (X * 1.05, -24, 0)], 16, TIGHTS)))
        boot = [(-38, 0, 0, X, 3), (-35, 12, 12, X, 3), (-20, 15, 18, X, 7), (-6, 15, 21, X, 9), (0, 13, 19, X, 9), (1, 0, 0, X, 9)]
        parts.append((order(v, 9.1, X, 0), vol(v, boot, BOOT, size=30)))
    # arms: hands held together at the chest, dreamy
    if pose == 'stand':
        arms = {-1: [(-44, -222, 0), (-54, -185, 16), (-15, -170, 48)], 1: [(44, -222, 0), (53, -185, 16), (10, -168, 48)]}
        hands = {-1: (-10, -170, 52), 1: (8, -168, 54)}
    for s in (-1, 1):
        parts.append((order(v, 16, s * 46, 10), tube(v, arms[s], 21, SWEATER)))
        hx, hy, hz = hands[s]
        parts.append((order(v, 16.1, hx, hz), sphere(v, hx, hy, hz, 11.5, SKIN)))
    parts.append(ground(66))
    return parts


def star_d(x, y, R, r, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        a = math.radians(rot + i * 180 / n)
        rr = R if i % 2 == 0 else r
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    # soft corners
    return smooth(pts, k=.04)


# ---------------------------------------------------------------- Савелий Петрович
def savely(yaw=0, ex='neutral', pose='stand'):
    v = View(yaw)
    E = dict(EXPR[ex])
    sw = geo.SW
    WHITE = '#ece8e1'
    SKIN_O = '#f2cdb3'
    VEST = '#56624c'
    SHIRT = '#efe6d3'
    TROUS = '#6e5d52'
    SLIP = '#7d3d35'
    BRASS = '#d6a347'
    P = dict(sclera=False, iris_col='#2f2426', lash=1.25, brow_kind='bush', brow_col=WHITE, mouth_w=9)
    # grumpy by default: low lids, brows pulled down to the nose
    if ex == 'neutral':
        E['lid'] = (.42, .3)
        E['brow'] = (3, 5)
        E['mouth'] = 'grump'
    elif ex == 'joy':
        E['brow'] = (-4, 2)
    head = [(-62, 0, 0, 0, -2), (-56, 34, 32, 0, -2), (-40, 54, 52, 0, -2), (-16, 62, 58, 0, 0), (8, 66, 60, 0, 2),
            (28, 67, 58, 0, 5), (44, 60, 50, 0, 8), (54, 44, 38, 0, 10), (60, 22, 22, 0, 10), (63, 0, 0, 0, 10)]
    hp = []
    hp.append((20, vol(v, head, SKIN_O, shade_col='#e4b399', off=(-.05, -.05))))
    for phi in (-1.6, 1.6):
        ex_, ey_, ef_ = surf(v, head, cheat(v, phi), 6, out=-2)
        if ef_ > -.4:
            lay = 20.5 if ef_ > .1 else 19.5
            w_ = 12 * max(ef_, .35) + 3
            hp.append((lay, shape(ellipse_d(ex_ + (0 if ef_ > .1 else (-1 if phi < 0 else 1) * 8 * v.c), ey_, w_, 16), SKIN_O, size=22)
                       + (stroke(f'M{f(ex_ - 2 * ef_)},{f(ey_ - 7)} q{f(5 * ef_)},6 0,13', sw * .7) if ef_ > .1 else '')))
    # white hair: a horseshoe round the back of the head, puffs over the ears
    hl = [(-2.6, 34), (-2.0, 26), (-1.75, 4), (-1.45, -16), (-1.2, -14), (-1.05, -30), (-.9, -90), (.9, -90), (1.05, -30),
          (1.2, -14), (1.45, -16), (1.75, 4), (2.0, 26), (2.6, 34)]
    hp.append((22, hair_cap(v, head, hl, WHITE, out=5, line_where=lambda p: abs((p + math.pi) % (2 * math.pi) - math.pi) > 1.0)))
    bald = [(-3.2, -26), (-2.2, -30), (-1.4, -34), (-1.0, -40), (-.6, -64), (0, -66), (.6, -64), (1.0, -40), (1.4, -34), (2.2, -30), (3.2, -26)]
    hp.append((22.05, hair_cap(v, head, bald, SKIN_O, out=5, line_where=lambda p: abs((p + math.pi) % (2 * math.pi) - math.pi) > 1.02)))
    for phi in (-1.3, 1.3):
        px, py, pf = surf(v, head, cheat(v, phi), -14, out=8)
        dep = v.depth(math.sin(phi), math.cos(phi))
        if pf > -.5:
            r = 14
            pts = [(px - r * 1.1, py + 2), (px - r * .6, py - r * .9), (px + r * .3, py - r * 1.05), (px + r * 1.1, py - r * .2),
                   (px + r * .8, py + r * .8), (px - r * .2, py + r * .9)]
            hp.append((22.5 if pf > .05 else 19, shape(smooth(pts), WHITE, size=2 * r, sw=sw * .9)))
    # three wisps on the bald top
    tx, ty, tf = surf(v, head, 0, -58, out=1)
    hp.append((22.6, stroke(f'M{f(tx - 6)},{f(ty + 4)} q-2,-14 8,-16 M{f(tx + 1)},{f(ty + 2)} q2,-12 12,-10', sw * .9)))
    fp = ''
    fp += cheek(v, head, -.62, 24, 12, '#ea8a78', .5)
    fp += cheek(v, head, .62, 24, 12, '#ea8a78', .5)
    for side, phi in ((-1, -.42), (1, .42)):
        x, y, fc = fs(v, head, phi, 6)
        fp += eye(v, x, y, fc, 6.5, 8.5, side, E, P, sw)
        bx, by, bf = fs(v, head, phi * 1.08, -9)
        fp += brow(v, bx, by, bf, 24, side, E, P, sw)
        # crow's feet: age in two strokes
        if fc > .3:
            ox = x + side * 13 * fc
            fp += stroke(f'M{f(ox)},{f(y - 3)} l{f(side * 5 * fc)},-2 M{f(ox)},{f(y + 3)} l{f(side * 5 * fc)},2', sw * .6, extra='opacity=".6"')
    mx, my, mf = fs(v, head, 0, 47)
    show_mouth = E['mouth'] in ('open', 'o', 'clench')
    if show_mouth:
        fp += mouth(mx, my, mf, E, P, sw)
    hp.append((21, fp))
    # big round nose
    nx, ny, nf = fs(v, head, 0, 22, out=4)
    hp.append((21.6, sphere(v, 0, 0, 0, 0, SKIN_O) if False else shape(ellipse_d(nx, ny, 12, 11), '#f0b29c', size=22, sw=sw)))
    # the walrus moustache: two drooping lobes under the nose
    if mf > -.2:
        k = max(mf, .25)
        cx, cy = nx, ny + 8
        L = 30 * k
        R = 30 * k
        lift = {'joy': -5, 'anger': 2, 'sad': 4}.get(ex, 0)
        pts = [(cx, cy - 2), (cx + R * .55, cy - 3), (cx + R, cy + 6 + lift), (cx + R * 1.05, cy + 16 + lift),
               (cx + R * .6, cy + 14 + lift * .5), (cx + R * .25, cy + 17), (cx, cy + 12),
               (cx - L * .25, cy + 17), (cx - L * .6, cy + 14 + lift * .5), (cx - L * 1.05, cy + 16 + lift), (cx - L, cy + 6 + lift),
               (cx - L * .55, cy - 3)]
        hp.append((21.5, shape(smooth(pts), WHITE, size=40, sw=sw)))
    # the loupe, pushed up onto the forehead: the one thing he is known by
    lx, ly, lf = fs(v, head, .38, -30, out=2)
    if lf > -.1:
        r = 13
        sq = max(lf, .3)
        lo = ''
        lo += shape(f'M{f(lx - r * sq)},{f(ly)} L{f(lx - r * sq)},{f(ly - 6)} A{f(r * sq)},{f(r * .45)} 0 0,1 {f(lx + r * sq)},{f(ly - 6)} L{f(lx + r * sq)},{f(ly)} A{f(r * sq)},{f(r * .45)} 0 0,1 {f(lx - r * sq)},{f(ly)} Z', '#2d2a2e', size=26, shade=False, sw=sw)
        lo += shape(ellipse_d(lx, ly - 12, r * sq, r * .45), BRASS, size=26, sw=sw)
        lo += f'<ellipse cx="{f(lx)}" cy="{f(ly - 12)}" rx="{f(r * sq * .62)}" ry="{f(r * .26)}" fill="#bfe3ee"/>'
        lo += stroke(f'M{f(lx - r * sq * .3)},{f(ly - 14)} l{f(r * sq * .3)},-1', sw * .7, '#fff')
        # the band
        bpts = []
        for phi in [-1.6 + i * .2 for i in range(17)]:
            bx_, by_, bf_ = fs(v, head, phi, -34 + 4 * math.cos(phi), out=1)
            if bf_ > 0:
                bpts.append((bx_, by_))
        band = stroke(smooth(bpts, closed=False), sw * 1.9, '#6a4a3a') if len(bpts) > 2 else ''
        hp.append((22.8, band + lo))
    tilt = {'neutral': -3, 'joy': 2, 'surprise': -5, 'sad': 6, 'anger': -6}.get(ex, -3)
    parts = wrap(hp, f'translate({f(v.s * 18)},-226) rotate({tilt})')

    # body: a pear with a hunch (the shoulders come forward)
    shirt = [(-180, 0, 0, 0, 12), (-176, 32, 30, 0, 12), (-166, 50, 40, 0, 9), (-136, 62, 48, 0, 5), (-100, 72, 56, 0, 6),
             (-76, 70, 54, 0, 4), (-66, 0, 0, 0, 2)]
    vest = [(-172, 0, 0, 0, 10), (-168, 44, 37, 0, 10), (-146, 59, 47, 0, 6), (-106, 73, 57, 0, 7), (-80, 72, 55, 0, 5),
            (-72, 66, 50, 0, 4), (-68, 0, 0, 0, 3)]
    hump = [(-188, 0, 0, 0, -2), (-183, 38, 30, 0, -8), (-166, 48, 38, 0, -14), (-146, 44, 34, 0, -10), (-136, 0, 0, 0, -6)]
    parts.append((9.9, vol(v, hump, SHIRT)))
    parts.append((10.0, vol(v, shirt, SHIRT)))
    # the waistcoat: open at the front, so the shirt shows in a V
    vd = smooth(vol_outline(v, vest))
    cid = uid('v')
    vx, vy, vf = surf(v, vest, 0, -168)
    vx2, vy2, vf2 = surf(v, vest, 0, -114)
    vee = f'M{f(vx - 15)},{f(vy - 30)} L{f(vx2)},{f(vy2)} L{f(vx + 15)},{f(vy - 30)} Z'
    if vf > .1:
        parts.append((10.1, f'<mask id="{cid}" maskUnits="userSpaceOnUse" x="-500" y="-600" width="1000" height="800"><rect x="-500" y="-600" width="1000" height="800" fill="#fff"/><path d="{vee}" fill="#000"/></mask><g mask="url(#{cid})">{shape(vd, VEST, size=120)}</g>'))
    else:
        parts.append((10.1, shape(vd, VEST, size=120)))
    det = ''
    for yb in (-108, -94, -80):
        bx, by, bf = surf(v, vest, 0, yb, out=1)
        if bf > .15:
            det += f'<circle cx="{f(bx + 2)}" cy="{f(by)}" r="3" fill="{BRASS}" stroke="{LINE}" stroke-width="{f(sw * .5)}"/>'
    # watch chain from a button to the pocket
    c1 = surf(v, vest, .05, -94, out=1)
    c2 = surf(v, vest, .6, -86, out=1)
    if c1[2] > .1 and c2[2] > .1:
        det += stroke(f'M{f(c1[0])},{f(c1[1])} Q{f((c1[0] + c2[0]) / 2)},{f(c1[1] + 16)} {f(c2[0])},{f(c2[1])}', sw * .8, BRASS)
        det += stroke(f'M{f(c2[0] - 8)},{f(c2[1] + 2)} l16,0', sw, LINE)
    parts.append((10.2, det))
    # legs: short, a little bent; slippers
    for X in (-24, 24):
        parts.append((9, tube(v, [(X, -72, 0), (X * 1.05, -42, 5), (X * 1.1, -14, 0)], 26, TROUS)))
        sl = [(-20, 0, 0, X * 1.1, 6), (-17, 14, 14, X * 1.1, 6), (-8, 16, 22, X * 1.1, 10), (0, 15, 22, X * 1.1, 12), (1, 0, 0, X * 1.1, 12)]
        parts.append((order(v, 9.1, X, 0), vol(v, sl, SLIP, size=30)))
    # arms: hands clasped behind the back
    for s_ in (-1, 1):
        arm = [(s_ * 52, -160, 6), (s_ * 72, -120, -10), (s_ * 24, -94, -56)]
        parts.append((order(v, 9.6 if v.s < .3 else 9.9, s_ * 60, -20), tube(v, arm, 22, SHIRT)))
        parts.append((order(v, 9.55, s_ * 14, -60), sphere(v, s_ * 14, -92, -60, 11, SKIN_O)))
    parts.append(ground(70))
    return parts


# ---------------------------------------------------------------- Тим
def tim(yaw=0, ex='neutral', pose='stand'):
    v = View(yaw)
    E = dict(EXPR[ex])
    sw = geo.SW
    HAIR = '#d8893d'
    CAP = '#3d6db0'
    TEE = '#d65a43'
    SHORTS = '#c39a6a'
    SHOE = '#d2463b'
    P = dict(sclera=False, iris_col='#2f2426', lash=1.2, brow_col='#9b5a2a', brow_w=1.6, mouth_w=9, gap=True, look=(3, 0))
    if ex == 'neutral':
        E['lid'] = (.05, .22)
        E['brow'] = (-2, 0)
        E['mouth'] = 'smirk'
    elif ex == 'joy':
        E['mouth'] = 'grin'
    head = [(-64, 0, 0, 0, -2), (-58, 38, 36, 0, -2), (-40, 62, 58, 0, -2), (-14, 70, 64, 0, -1), (10, 70, 62, 0, 2),
            (30, 64, 56, 0, 5), (46, 48, 42, 0, 8), (56, 26, 26, 0, 9), (59, 0, 0, 0, 9)]
    hp = []
    hp.append((20, vol(v, head, SKIN, shade_col=SKIN_SH, off=(-.05, -.05))))
    # ears that stick out
    for phi in (-1.57, 1.57):
        ex_, ey_, ef_ = surf(v, head, cheat(v, phi), 10, out=-3)
        sgn = -1 if phi < 0 else 1
        side_x = ex_ + sgn * 8 * v.c
        lay = 20.5 if ef_ > .2 else 19.5
        w_ = 9 + 6 * max(0, ef_)
        ear = shape(ellipse_d(side_x, ey_, w_, 15), SKIN, size=24, shade_col=SKIN_SH)
        if ef_ > .2:
            ear += stroke(f'M{f(side_x - 2 * ef_)},{f(ey_ - 7)} q{f(6 * ef_)},6 0,13', sw * .7)
        hp.append((lay, ear))
    # short ginger hair, spiky tufts out under the cap
    hl = [(-2.6, 30), (-2.1, 20), (-1.8, -6), (-1.45, -8), (-1.3, -20), (-1.05, -18), (-.9, -30), (-.72, -14), (-.55, -30),
          (-.36, -10), (-.18, -30), (0, -12), (.18, -30), (.36, -12), (.55, -30), (.72, -14), (.9, -30), (1.05, -18),
          (1.3, -20), (1.45, -8), (1.8, -6), (2.1, 20), (2.6, 30)]
    hp.append((22, hair_cap(v, head, hl, HAIR, out=6)))
    # the cap, worn backwards: a dome; its brim sticks out at the back
    cl = [(-3.2, -8), (-2.4, -12), (-1.6, -28), (-.8, -36), (0, -38), (.8, -36), (1.6, -28), (2.4, -12), (3.2, -8)]
    hp.append((22.4, hair_cap(v, head, cl, CAP, out=9)))
    # the brim at the back
    bx0, by0 = 0, -10
    brim = [(-16, 0, 0, 0, -62), (-14, 30, 18, 0, -72), (-9, 32, 22, 0, -80), (-6, 0, 0, 0, -84)]
    bdep = v.depth(0, -70)
    hp.append((22.3 if bdep > 0 else 19, vol(v, brim, '#335d99', size=50)))
    # a button on top
    tx, ty, tf = surf(v, head, 0, -66, out=9)
    hp.append((22.5, f'<ellipse cx="{f(tx)}" cy="{f(ty + 2)}" rx="6" ry="3.5" fill="{CAP}" stroke="{LINE}" stroke-width="{f(sw * .8)}"/>'))
    fp = ''
    fp += cheek(v, head, -.62, 26, 11, '#f08a7a', .5)
    fp += cheek(v, head, .62, 26, 11, '#f08a7a', .5)
    # freckles
    for dx, dy in ((-.5, 22), (-.38, 27), (-.62, 28), (.5, 22), (.38, 27), (.62, 28)):
        x_, y_, f_ = fs(v, head, dx, dy)
        if f_ > .25:
            fp += f'<circle cx="{f(x_)}" cy="{f(y_)}" r="1.7" fill="#b86a3e"/>'
    for side, phi in ((-1, -.42), (1, .42)):
        x, y, fc = fs(v, head, phi, 10)
        fp += eye(v, x, y, fc, 10.5, 13, side, E, P, sw)
        bx, by, bf = fs(v, head, phi * 1.05, -13)
        E2 = dict(E)
        if ex == 'neutral' and side == 1:
            E2['brow'] = (-7, -4)   # one brow up: up to something
        fp += brow(v, bx, by, bf, 18, side, E2, P, sw)
    fp += small_nose(v, head, 24)
    mx, my, mf = fs(v, head, .08, 38)
    fp += mouth(mx, my, mf, E, P, sw)
    # a plaster on the cheek
    px, py, pf = fs(v, head, .8, 31)
    if pf > .2:
        fp += f'<g transform="translate({f(px)},{f(py)}) rotate(-25) scale({f(max(pf, .4))},1)"><rect x="-10" y="-5" width="20" height="10" rx="4" fill="#f1d3a6" stroke="{LINE}" stroke-width="{f(sw * .7)}"/><rect x="-3.5" y="-3.5" width="7" height="7" fill="#e3b986"/></g>'
    hp.append((21, fp))
    tilt = {'neutral': -6, 'joy': -3, 'surprise': -2, 'sad': 6, 'anger': -4}.get(ex, -6)
    parts = wrap(hp, f'translate(0,-205) rotate({tilt})')

    tee = [(-150, 0, 0), (-147, 30, 22), (-138, 40, 28), (-110, 41, 30), (-86, 44, 31), (-80, 0, 0)]
    shorts = [(-92, 0, 0), (-90, 40, 29), (-76, 42, 30), (-70, 0, 0)]
    parts.append((10.0, vol(v, shorts, SHORTS)))
    for X in (-19, 19):
        parts.append((order(v, 9.95, X, 0), tube(v, [(X, -76, 0), (X * 1.08, -56, 0)], 26, SHORTS, cap='butt')))
    parts.append((10.2, vol(v, tee, TEE)))
    # two stripes on the tee
    st = ''
    for yy in (-118, -104):
        pts = []
        for phi in [-1.5 + i * .15 for i in range(21)]:
            x_, y_, f_ = surf(v, tee, phi, yy, out=0)
            if f_ > 0:
                pts.append((x_, y_))
        if len(pts) > 2:
            st += stroke(smooth(pts, closed=False), 7, '#f3e3c4')
    cid = uid('t')
    parts.append((10.25, f'<clipPath id="{cid}"><path d="{smooth(vol_outline(v, tee))}"/></clipPath><g clip-path="url(#{cid})">{st}</g>'))
    # the slingshot sticking out of the back pocket
    sx, sy = v.p(24, -96, -30)
    sdep = v.depth(24, -30)
    sling = stroke(f'M{f(sx)},{f(sy + 10)} L{f(sx)},{f(sy - 8)} M{f(sx)},{f(sy - 8)} L{f(sx - 8)},{f(sy - 24)} M{f(sx)},{f(sy - 8)} L{f(sx + 8)},{f(sy - 24)}', 9) + \
        stroke(f'M{f(sx)},{f(sy + 10)} L{f(sx)},{f(sy - 8)} M{f(sx)},{f(sy - 8)} L{f(sx - 8)},{f(sy - 24)} M{f(sx)},{f(sy - 8)} L{f(sx + 8)},{f(sy - 24)}', 5, '#9a6a3c')
    parts.append((9.7 if sdep < 5 else 10.3, sling))
    # legs, socks, sneakers; a plaster on one knee
    for X in (-17, 17):
        parts.append((9, tube(v, [(X, -58, 0), (X * 1.08, -20, 0)], 15, SKIN)))
        parts.append((9.05, tube(v, [(X * 1.07, -26, 0), (X * 1.08, -16, 0)], 16, '#f3efe6', cap='butt')))
        sh = [(-24, 0, 0, X * 1.1, 4), (-21, 13, 14, X * 1.1, 4), (-10, 15, 20, X * 1.1, 8), (-2, 15, 22, X * 1.1, 10), (1, 0, 0, X * 1.1, 10)]
        parts.append((order(v, 9.1, X, 0), vol(v, sh, SHOE, size=30)))
        sx_, sy_ = v.p(X * 1.1, -3, 8)
        parts.append((order(v, 9.11, X, 0), f'<path d="M{f(sx_ - 15 * max(v.c, .2) - 4 * v.s)},{f(sy_)} L{f(sx_ + 15 * max(v.c, .2) + 12 * v.s)},{f(sy_)}" stroke="#f3efe6" stroke-width="4"/>'))
    kx, ky = v.p(-18, -42, 8)
    if v.depth(-18, 8) > 0:
        parts.append((9.2, f'<rect x="{f(kx - 6)}" y="{f(ky - 4)}" width="12" height="8" rx="3" fill="#f1d3a6" stroke="{LINE}" stroke-width="{f(sw * .6)}"/>'))
    # arms: hiding something behind his back
    for s_ in (-1, 1):
        arm = [(s_ * 38, -140, 2), (s_ * 48, -110, -10), (s_ * 18, -96, -40)]
        parts.append((order(v, 9.6 if v.s < .3 else 9.9, s_ * 40, -20), tube(v, arm, 15, SKIN)))
        sl = [(s_ * 38, -140, 2), (s_ * 44, -126, -2)]
        parts.append((order(v, 9.61 if v.s < .3 else 9.91, s_ * 40, -20), tube(v, sl, 19, TEE)))
        parts.append((order(v, 9.55, s_ * 12, -44), sphere(v, s_ * 12, -96, -44, 9.5, SKIN)))
    parts.append(ground(52))
    return parts


# ---------------------------------------------------------------- Вера
def vera(yaw=0, ex='neutral', pose='stand'):
    v = View(yaw)
    E = dict(EXPR[ex])
    sw = geo.SW
    HAIR = '#3c2f3b'
    COAT = '#2f5b5f'
    NECK = '#7a4560'
    TROUS = '#3a3940'
    SHOE = '#26232a'
    P = dict(sclera=False, iris_col='#2f2426', lash=1.5, flick=True, brow_col='#3c2f3b', brow_w=1.9, brow_arch=1, mouth_w=8, bags=True)
    if ex == 'neutral':
        E['lid'] = (.36, .3)
        E['brow'] = (2, 3)
        E['mouth'] = 'strict'
    elif ex == 'joy':
        E['mouth'] = 'soft'
        P['smile'] = 6
    elif ex in ('sad',):
        E['lid'] = (.25, .5)
    head = [(-72, 0, 0, 0, -3), (-66, 30, 32, 0, -3), (-50, 52, 54, 0, -3), (-24, 59, 60, 0, -2), (4, 59, 58, 0, 2),
            (26, 55, 52, 0, 5), (44, 44, 41, 0, 9), (58, 27, 27, 0, 12), (66, 11, 13, 0, 13), (68, 0, 0, 0, 13)]
    hp = []
    # the bun at the back of the crown, with a pencil through it
    bun = [(-112, 0, 0, 0, -18), (-106, 22, 22, 0, -20), (-92, 30, 30, 0, -22), (-76, 27, 27, 0, -22), (-68, 0, 0, 0, -22)]
    bdep = v.depth(0, -30)
    hp.append((19.8 if v.s < .3 else 22.2, vol(v, bun, HAIR, size=40)))
    px1, py1 = v.p(-40, -104, -10)
    px2, py2 = v.p(40, -84, -34)
    pencil = stroke(f'M{f(px1)},{f(py1)} L{f(px2)},{f(py2)}', 9) + stroke(f'M{f(px1)},{f(py1)} L{f(px2)},{f(py2)}', 5, '#e9b949') + \
        f'<circle cx="{f(px2)}" cy="{f(py2)}" r="3" fill="#e58a8a" stroke="{LINE}" stroke-width="1.5"/>'
    hp.append((19.7 if v.s < .3 else 22.3, pencil))
    hp.append((20, vol(v, head, SKIN, shade_col=SKIN_SH, off=(-.05, -.05))))
    for phi in (-1.6, 1.6):
        ex_, ey_, ef_ = surf(v, head, cheat(v, phi), 6, out=-2)
        if ef_ > .1:
            hp.append((20.5, shape(ellipse_d(ex_, ey_, 8 * ef_ + 2, 11), SKIN, size=18, shade_col=SKIN_SH)
                       + f'<circle cx="{f(ex_)}" cy="{f(ey_ + 11)}" r="2.6" fill="#cfd6dc" stroke="{LINE}" stroke-width="1.2"/>'))
    # hair pulled back tight from a middle parting, the ear half covered
    # a side parting; the hair sweeps across the forehead in one smooth wave and is pulled back over the ears
    hl = [(-2.6, 40), (-2.0, 20), (-1.75, 0), (-1.55, -6), (-1.35, 0), (-1.12, -8), (-.85, -22), (-.5, -32), (-.15, -36),
          (.2, -42), (.38, -50), (.5, -44), (.8, -34), (1.1, -18), (1.35, -2), (1.55, -6), (1.75, 0), (2.0, 20), (2.6, 40)]
    hp.append((22, hair_cap(v, head, hl, HAIR, out=4)))
    fp = ''
    fp += cheek(v, head, -.6, 26, 9, '#e98a7c', .3)
    fp += cheek(v, head, .6, 26, 9, '#e98a7c', .3)
    eyes = []
    for side, phi in ((-1, -.42), (1, .42)):
        x, y, fc = fs(v, head, phi, 8)
        fp += eye(v, x, y, fc, 8, 10.5, side, E, P, sw)
        eyes.append((x, y, fc))
        bx, by, bf = fs(v, head, phi * 1.05, -9)
        fp += brow(v, bx, by, bf, 21, side, E, P, sw)
    # a straight, fine nose: one line down and a small turn
    nx, ny, nf = fs(v, head, 0, 12)
    nx2, ny2, nf2 = fs(v, head, .02, 30, out=1)
    if v.s < .85:
        fp += stroke(f'M{f(nx2 - 3 - 2 * v.s)},{f(ny2)} q{f(4 + 3 * v.s)},2 {f(6)},-1', sw * .9)
    else:
        fp += small_nose(v, head, 26, r=5.5)
    mx, my, mf = fs(v, head, 0, 44)
    fp += mouth(mx, my, mf, E, P, sw)
    # glasses: two soft rectangles and a bridge
    gl = ''
    for x, y, fc in eyes:
        if fc > .12:
            w_ = 15 * max(fc, .25) ** .85
            gl += f'<rect x="{f(x - w_)}" y="{f(y - 11)}" width="{f(2 * w_)}" height="22" rx="6" fill="none" stroke="{LINE}" stroke-width="{f(sw * .9)}"/>'
            gl += stroke(f'M{f(x - w_ * .5)},{f(y - 7)} l{f(w_ * .45)},-2', sw * .6, '#fff', extra='opacity=".8"')
    if len([e for e in eyes if e[2] > .12]) == 2:
        (x1, y1, f1), (x2, y2, f2) = eyes
        w1 = 15 * max(f1, .25) ** .85
        w2 = 15 * max(f2, .25) ** .85
        gl += stroke(f'M{f(x1 + w1)},{f(y1 - 3)} Q{f((x1 + x2) / 2)},{f(y1 - 7)} {f(x2 - w2)},{f(y2 - 3)}', sw * .9)
    # the arm of the glasses toward the ear, seen in profile and 3/4
    near = eyes[0]
    if v.s > .3 and near[2] > .12:
        ex_, ey_, ef_ = surf(v, head, -1.5, 2)
        w_ = 15 * max(near[2], .25) ** .85
        gl += stroke(f'M{f(near[0] - w_)},{f(near[1] - 5)} L{f(ex_)},{f(ey_)}', sw * .9)
    hp.append((21, fp))
    hp.append((21.8, gl))
    tilt = {'neutral': 2, 'joy': 4, 'surprise': -2, 'sad': 6, 'anger': -2}.get(ex, 2)
    parts = wrap(hp, f'translate(0,-352) rotate({tilt})')

    # a long coat, a turtleneck at the throat
    neck = [(-296, 0, 0, 0, 2), (-292, 22, 22, 0, 2), (-280, 26, 25, 0, 2), (-266, 28, 26, 0, 2), (-262, 0, 0, 0, 2)]
    parts.append((15, vol(v, neck, NECK, size=40)))
    coat = [(-272, 0, 0), (-268, 34, 26), (-258, 48, 34), (-230, 50, 36), (-180, 48, 36), (-140, 52, 38), (-90, 60, 42),
            (-62, 64, 44), (-58, 0, 0)]
    parts.append((10.2, vol(v, coat, COAT)))
    # the coat's front edge and collar
    det = ''
    e1 = surf(v, coat, .12, -262)
    e2 = surf(v, coat, .16, -64)
    if e1[2] > .1:
        det += stroke(f'M{f(e1[0])},{f(e1[1])} L{f(e2[0])},{f(e2[1])}', sw * .9)
        for yb in (-236, -204, -172):
            b = surf(v, coat, .26, yb, out=1)
            if b[2] > .1:
                det += f'<circle cx="{f(b[0])}" cy="{f(b[1])}" r="3.4" fill="#1f3c3f" stroke="{LINE}" stroke-width="{f(sw * .5)}"/>'
    parts.append((10.3, det))
    for X in (-15, 15):
        parts.append((9, tube(v, [(X, -70, 0), (X, -14, 0)], 17, TROUS)))
        sh = [(-16, 0, 0, X, 4), (-14, 10, 11, X, 4), (-6, 11, 18, X, 7), (0, 10, 19, X, 9), (1, 0, 0, X, 9)]
        parts.append((order(v, 9.1, X, 0), vol(v, sh, SHOE, size=30)))
    # arms: holding a folder against her chest
    fx, fy = v.p(0, -180, 40)
    folder = [(-34, -222, 42), (30, -222, 46), (30, -148, 46), (-34, -148, 42)]
    fpts = [v.p(*p) for p in folder]
    fdep = v.depth(0, 44)
    parts.append((15.5, shape(poly_d(fpts, True), '#e9dcc0', size=60, sw=sw) + stroke(poly_d([((fpts[0][0] + fpts[1][0]) / 2, fpts[0][1] + 2), ((fpts[0][0] + fpts[1][0]) / 2 + 6, fpts[0][1] - 6)]), sw * .9, '#d36b5a')))
    for s_ in (-1, 1):
        arm = [(s_ * 42, -262, 0), (s_ * 52, -212, 14), (s_ * 18, -186, 50)]
        parts.append((order(v, 16, s_ * 48, 10), tube(v, arm, 17, COAT)))
        hx, hy, hz = s_ * 14, -186, 52
        parts.append((order(v, 16.1, hx, hz), sphere(v, hx, hy, hz, 9.5, SKIN)))
    parts.append(ground(56))
    return parts


CAST = {'anya': anya, 'savely': savely, 'tim': tim, 'vera': vera}


def render(name, yaw=0, ex='neutral', **kw):
    parts = CAST[name](yaw, ex, **kw)
    parts.sort(key=lambda p: p[0])
    return ''.join(s for _, s in parts)
