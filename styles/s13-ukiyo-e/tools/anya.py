"""Аня, about 20 — warm, trusting, dreamy. The long oval face and the loose hair of the shin-hanga beauties;
her own yellow cardigan and blue dress, printed flat with small patterns."""
import parts
from kit import INK, SKIN

NAME = 'Аня'
HAIR = '#2c1a17'
SHEEN = '#b98a62'
CARD = '#d8a23a'
DRESS = '#6f8fa8'
HEIGHT = 720

p = parts.P(long=1.08, cheek=0, chin=-3,
            eye=dict(w=42, h=8.6, iris=7.6, lid=3.8, slant=-1.5, lower=0.4, lash=1.0, color='#3a2a1e', crease=0.35),
            brow=dict(kind='arc', w=2.6, len=42, arch=6, y=-28),
            nose=dict(kind='soft', s=0.82), mouth=dict(w=23, y=62, full=1.15),
            blush=('#e79a86', 0.26))
CALM = 'dream'


def hair_back(d, view):
    if view == 'q':
        out = [(84, -92), (108, -40), (112, 30), (104, 110), (120, 200), (136, 310)]
        inn = [(30, -60), (44, 20), (36, 110), (24, 200), (30, 320)]
    elif view == 'f':
        d.fill([(-70, -90), (-102, -30), (-108, 60), (-118, 180), (-128, 320), (128, 320), (118, 180), (108, 60),
                (102, -30), (70, -90)], HAIR)
        d.strands([(-70, -80), (-102, -30), (-108, 60), (-118, 180), (-128, 320)],
                  [(-60, -60), (-70, 30), (-66, 120), (-70, 200), (-64, 320)], 4, 0.8, SHEEN, op=0.5)
        d.strands([(70, -80), (102, -30), (108, 60), (118, 180), (128, 320)],
                  [(60, -60), (70, 30), (66, 120), (70, 200), (64, 320)], 4, 0.8, SHEEN, op=0.5)
        return
    else:
        return
    d.fill(out + inn[::-1], HAIR)
    d.strands(out, inn, 9, 0.8, SHEEN, op=0.5, t0=0.06, t1=0.9)


def hair_side_fall(d):
    """Side view: the hair falls over the back and the shoulder."""
    out = [(96, -70), (110, -10), (104, 70), (112, 170), (130, 320)]
    inn = [(34, -30), (40, 40), (30, 130), (20, 220), (14, 320)]
    d.fill(out + inn[::-1], HAIR)
    d.strands(out, inn, 10, 0.8, SHEEN, op=0.5, t0=0.05, t1=0.92)
    d.line(inn, 1.6, 'even')


def hair_front(d, view):
    if view == 'q':
        part = (-26, -86)
        near = [part, (14, -68), (40, -42), (52, -20)]
        far = [part, (-50, -77), (-68, -57), (-78, -32)]
        d.fill([(-80, -26), (-80, -60), (-58, -98), (-14, -116), (36, -118), (80, -100), (104, -58), (108, -10),
                (100, 50), (74, 52), (76, 12), (66, -18, 'c')] + near[::-1][:-1] + [part + ('c',)] + far[1:], HAIR)
        d.strands(near, [(-18, -115), (36, -118), (80, -100), (106, -46)], 5, 0.8, SHEEN, op=0.5, t0=0.08)
        d.strands(far, [(-22, -115), (-58, -98), (-80, -60), (-81, -30)], 3, 0.8, SHEEN, op=0.5, t0=0.15)
        d.fringe(near, 7, 0.9, HAIR, lean=0.9, step=3.2, side=1)
        d.fringe(far, 5, 0.9, HAIR, lean=-0.9, step=3.2, side=-1)
        # a loose lock in front of the ear
        d.line([(50, -22), (48, 6), (52, 30), (46, 52)], 2.2, 'taper', HAIR)
        d.line([(46, -24), (42, 2), (44, 20)], 1.3, 'taper', HAIR)
    elif view == 'f':
        part = (10, -86)
        right = [part, (42, -70), (66, -42), (76, -8), (78, 14)]
        left = [part, (-22, -80), (-52, -62), (-72, -34), (-78, 14)]
        d.fill([(-78, 14), (-96, -6), (-96, -50), (-74, -94), (-30, -117), (30, -117), (74, -94), (96, -50),
                (96, -6), (78, 14, 'c')] + right[::-1][1:-1] + [part + ('c',)] + left[1:-1], HAIR)
        d.strands(right, [(12, -117), (60, -104), (94, -56), (97, -6)], 4, 0.8, SHEEN, op=0.5, t0=0.1)
        d.strands(left, [(8, -117), (-40, -112), (-90, -62), (-97, -6)], 4, 0.8, SHEEN, op=0.5, t0=0.1)
        d.fringe(right, 6, 0.9, HAIR, lean=0.9, step=3.2, side=1)
        d.fringe(left, 6, 0.9, HAIR, lean=-0.9, step=3.2, side=-1)
    else:
        line = [(-79, -44), (-52, -62), (-20, -48), (4, -24), (14, -6)]
        d.fill([(-79, -44), (-74, -78), (-40, -108), (10, -116), (72, -100), (104, -56), (110, -6), (100, 40),
                (40, 44), (38, 8), (14, -6, 'c')] + line[::-1][1:], HAIR)
        d.strands(line, [(-70, -84), (-30, -112), (40, -112), (100, -60)], 5, 0.8, SHEEN, op=0.5, t0=0.1)
        d.strands([(14, -6), (38, 8), (40, 44)], [(104, -56), (110, -6), (100, 40)], 3, 0.8, SHEEN, op=0.5)
        d.fringe(line, 6, 0.9, HAIR, lean=0.9, step=3.2, side=1)
        d.line([(12, -8), (8, 16), (12, 36)], 2.0, 'taper', HAIR)


def sprig(d, x, y, s=1.0, rot=0):
    """A sprig of camomile."""
    with d.g(x, y, s, rot):
        d.line([(0, 0), (-4, -40), (4, -84)], 2.2, 'even', '#4c5a34')
        d.line([(-3, -36), (-22, -56), (-28, -70)], 1.8, 'taper', '#4c5a34')
        d.line([(1, -58), (20, -70), (26, -80)], 1.8, 'taper', '#4c5a34')
        d.fill([(-2, -22), (-16, -26), (-24, -20), (-12, -16)], '#6d7c46')
        d.fill([(1, -46), (14, -44), (20, -36), (8, -38)], '#6d7c46')
        parts.flower(d, 5, -92, 13, n=7)
        parts.flower(d, -30, -76, 10, n=7, rot=20)
        parts.flower(d, 29, -86, 9, n=7, rot=10)


def clothes(d, view):
    sh = parts.shoulders(view, 124, drop=10)
    blossoms = d.blossoms('#f3ead6', 30, 3.6, heart='#d8a23a')
    hemp = d.asanoha('#b9812a', 26, 1.0)
    d.shape(sh, CARD, 3.8, pattern=hemp, nib=0.6)
    if view == 'q':
        op = [(-30, 166), (-42, 250), (-38, 345), (46, 345), (52, 250), (58, 150)]
        scoop = [(-30, 166), (-20, 192), (10, 206), (42, 194), (58, 150)]
        folds = [[(118, 236), (124, 290), (120, 345)], [(-66, 250), (-70, 300), (-66, 345)]]
    elif view == 'f':
        op = [(-40, 154), (-46, 250), (-42, 345), (42, 345), (46, 250), (40, 154)]
        scoop = [(-40, 154), (-27, 192), (0, 205), (27, 192), (40, 154)]
        folds = [[(98, 240), (104, 295), (100, 345)], [(-98, 240), (-104, 295), (-100, 345)]]
    else:
        op = [(-2, 164), (-22, 204), (-34, 256), (-33, 345), (-6, 345), (-6, 256), (8, 204), (14, 190)]
        scoop = [(-2, 164), (2, 184), (22, 192), (48, 186), (62, 148)]
        folds = [[(40, 220), (30, 285), (36, 345)]]
    d.fill(op, DRESS, pattern=blossoms, n=1 if view != 's' else 8)
    d.fill([scoop[0] + ('c',)] + scoop[1:-1] + [scoop[-1] + ('c',), (scoop[-1][0] - 30, 128), (scoop[0][0] + 20, 132)],
           p['skin'])
    if view != 's':
        d.line([(x, y + 6) for x, y in scoop], 5.0, 'swell', '#f3ead6')
        d.line(scoop, 2.4, 'swell')
        d.line(op[0:3], 3.8, 'taper')
        d.line(op[5:2:-1], 3.8, 'taper')
    else:
        d.line(scoop, 2.6, 'swell')
        d.line(op[4:8], 3.4, 'tail')
    for f in folds:
        d.line(f, 3.2, 'taper')


def bust(d, view='q', expr=None, hand=False):
    expr = expr or CALM
    if view != 's':
        hair_back(d, view)
    parts.neck(d, p, view, 44, 80)
    clothes(d, view)
    if view == 's':
        hair_side_fall(d)
    parts.head(d, p, view, expr, front=hair_front)
    if hand:
        sprig(d, -98, 252, 1.2, -10)
        parts.hand(d, -58, 318, 1.2, 163, 'pinch', skin=p['skin'], lw=1.5)
        d.shape([(-96, 345), (-88, 318), (-50, 300), (-22, 320), (-20, 345)], CARD, 3.4,
                pattern=d.asanoha('#b9812a', 26, 1.0), nib=0.6)


def figure(d):
    """Standing, the head bent to a sprig of camomile held at the chest. Feet at y = 0; a head is about 92."""
    blossoms = d.blossoms('#f3ead6', 22, 2.6, heart='#d8a23a')
    hemp = d.asanoha('#b9812a', 18, 0.8)
    hx, hy, hs, rot = -14, -668, 0.46, -8
    with d.g(hx, hy, hs, rot):
        hair_back(d, 'q')
    # legs and shoes
    for (kx, ax, ay) in ((-20, -22, -24), (24, 22, -14)):
        d.shape(parts.tube([(kx, -220), (ax + 4, -110), (ax, ay - 8)], [34, 26, 15]), p['skin'], 2.0)
        d.shape([(ax + 11, ay - 12), (ax + 12, ay + 4), (ax - 8, ay + 8), (ax - 36, ay + 9), (ax - 38, ay + 2),
                 (ax - 10, ay - 5)], '#8a3b2c', 2.4, nib=0.6)
    # far arm, hanging a little away from the body
    d.shape([(-34, -592), (-52, -566), (-66, -484), (-70, -420), (-50, -414), (-44, -480), (-34, -530)], CARD, 3.0,
            pattern=hemp, nib=0.6)
    parts.hand(d, -60, -418, 0.56, 8, 'rest', skin=p['skin'], lw=1.5)
    d.line([(-72, -420), (-60, -413), (-48, -415)], 2.8, 'swell')
    # the skirt, swung by a step
    skirt = [(-22, -452), (-36, -380), (-64, -270), (-98, -178, 'c'), (-70, -160), (-42, -174), (-8, -156),
             (26, -170), (58, -154), (82, -172, 'c'), (74, -270), (62, -370), (40, -452)]
    d.shape(skirt, DRESS, 3.4, pattern=blossoms, nib=0.6)
    for f in ([(-8, -440), (-30, -300), (-42, -176)], [(14, -430), (10, -290), (26, -172)],
              [(32, -420), (52, -290), (58, -156)], [(-18, -410), (-56, -280), (-70, -200)]):
        d.line(f, 3.0, 'taper')
    # the cardigan
    body = [(-38, -592), (-46, -520), (-32, -440), (-32, -402), (48, -396), (46, -450), (54, -520), (50, -598),
            (22, -612), (-14, -608)]
    d.shape(body, CARD, 3.2, pattern=hemp, nib=0.6)
    op = [(-12, -606), (-18, -520), (-10, -400), (16, -398), (22, -520), (20, -610)]
    d.fill(op, DRESS, pattern=blossoms, n=1)
    d.line(op[0:3], 3.0, 'taper')
    d.line(op[5:2:-1], 3.0, 'taper')
    d.fill([(-12, -608), (-6, -584), (4, -578), (16, -586), (20, -612), (4, -620)], p['skin'])
    d.line([(-12, -606), (-6, -584), (4, -578), (16, -586), (20, -610)], 1.8, 'swell')
    with d.g(hx, hy, hs, rot):
        parts.neck(d, p, 'q', 44, 70)
    d.fill([(-10, -600), (-5, -586), (4, -581), (14, -588), (17, -602), (4, -612)], p['skin'])
    # near arm across the chest, the sprig in its fingers
    sprig(d, -25, -548, 0.56, -12)
    parts.hand(d, -2, -522, 0.56, 160, 'pinch', skin=p['skin'], lw=1.5)
    d.shape([(34, -604), (58, -594), (74, -540), (80, -480), (66, -464), (2, -510), (-6, -532), (44, -508, 'c'),
             (46, -560)], CARD, 3.2, pattern=hemp, nib=0.6)
    d.line([(60, -500), (72, -492), (76, -478)], 2.6, 'taper')
    d.line([(44, -508), (54, -496), (60, -482)], 2.6, 'taper')
    d.line([(-7, -534), (-2, -521), (4, -509)], 2.8, 'swell')
    with d.g(hx, hy, hs, rot):
        parts.head(d, p, 'q', CALM, front=hair_front)
