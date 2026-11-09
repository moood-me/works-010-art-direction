"""Марат, about 35, a cook — huge, loud, merry, generous. A hero of Kuniyoshi and a wrestler of Hokusai's
sketchbooks: a square head on a short neck, a black beard drawn hair by hair at its edge, heavy brows, eyes
closed into arcs by the laugh, the mouth wide open; his own white jacket, a terracotta apron, a ladle."""
import parts
from kit import INK

NAME = 'Марат'
HAIR = '#1f1a1a'
SHEEN = '#8a8684'
WHITE = '#f8f2e2'
TERRA = '#c8683a'
TERRA_D = '#9c4a26'
SKIN = '#f1d7b6'
HEIGHT = 800
TOP = 910     # with the ladle up
X = 450

p = parts.P(skin=SKIN, long=0.98, cheek=11, jaw=14, chin=9, brow_ridge=3,
            eye=dict(w=32, h=8.5, iris=6.2, lid=4.0, slant=0, lower=0.6, color='#2a2220'),
            brow=dict(kind='thick', w=9.5, len=44, arch=7, y=-24),
            nose=dict(kind='broad', s=1.12), mouth=dict(w=40, y=66, lip=None, full=1.2),
            blush=('#e2876a', 0.45), ear=1.2)
CALM = 'grin'
EXPR = {'joy': dict(lift=5, tilt=1, open=0.0, mouth='grin', blush=0.6),
        'surprise': dict(lift=12, tilt=2, open=1.6, look=(0, 0), mouth='gasp'),
        'sad': dict(lift=0, tilt=9, open=0.7, look=(-1, 2.5), mouth='sad'),
        'anger': dict(lift=-8, tilt=-10, open=0.9, look=(0, 0), mouth='snarl')}

HAIRS = {
    'q': ([(-82, -28), (-82, -64), (-58, -100), (-14, -117), (36, -119), (80, -101), (105, -56), (107, -10), (92, 30)],
          [(72, 26), (66, 0), (56, -22), (40, -46), (10, -64), (-30, -72), (-60, -58), (-77, -38)]),
    'f': ([(-86, 0), (-93, -44), (-72, -93), (-30, -117), (30, -117), (72, -93), (93, -44), (86, 0)],
          [(76, -4), (70, -40), (44, -64), (0, -74), (-44, -64), (-70, -40), (-76, -4)]),
    's': ([(-80, -40), (-76, -80), (-40, -109), (10, -117), (70, -101), (105, -54), (105, -6), (84, 30), (44, 36)],
          [(40, 10), (22, -10), (6, -30), (-20, -52), (-52, -60), (-75, -48)]),
}
BEARDS = {
    'q': ([(52, -8), (66, 30), (60, 72), (36, 104), (0, 122), (-38, 124), (-66, 106), (-80, 76), (-84, 46)],
          [(-70, 42), (-52, 40), (-30, 43), (-10, 50), (10, 44), (30, 30), (44, 10)]),
    'f': ([(80, -8), (90, 30), (80, 76), (52, 110), (0, 126), (-52, 110), (-80, 76), (-90, 30), (-80, -8)],
          [(-70, 12), (-56, 36), (-30, 43), (0, 46), (30, 43), (56, 36), (70, 12)]),
    's': ([(16, -10), (28, 30), (16, 68), (-14, 100), (-50, 116), (-82, 104), (-92, 76), (-88, 50)],
          [(-80, 42), (-60, 40), (-36, 44), (-12, 30), (4, 10)]),
}


def hair(d, view):
    out, inn = HAIRS[view]
    d.fill(parts.scallop(out, 12, out=-1) + parts.scallop(inn, 8), HAIR)
    for t in (0.3, 0.62):
        from kit import curve, lerp_pts
        mid = lerp_pts(curve(out), curve(inn[::-1]), t)
        for i in range(3, len(mid) - 3, 7):
            x, y = mid[i]
            d.line([(x - 6, y + 3), (x - 2, y - 5), (x + 5, y - 3), (x + 4, y + 3)], 1.1, 'swell', SHEEN, nib=0, op=0.7)


def beard(d, view, ex, lay):
    out, inn = BEARDS[view]
    d.fill(out + inn, HAIR)
    d.fringe(out, 9, 1.3, HAIR, lean=0.5, step=3.4, side=-1)
    d.fringe(inn, 6, 1.1, HAIR, lean=0.3, step=3.4, side=-1)


def hd(d, view, expr):
    parts.head(d, p, view, expr, under=beard, front=hair)


def ladle(d, x1, y1, x2, y2, r=30):
    """A ladle: the handle from (x1, y1) up to the bowl at (x2, y2)."""
    d.line([(x1, y1), (x2, y2)], 7.0, 'even', '#8a6a3a', nib=0)
    d.shape(parts.oval(x2, y2 - r * 0.7, r, r * 0.8, 12), '#b9b4a8', 2.6, nib=0.5)
    d.fill(parts.oval(x2, y2 - r * 0.8, r * 0.74, r * 0.5, 12), '#8f8a80')
    d.line([(x2 - r * 0.7, y2 - r * 0.8), (x2, y2 - r * 1.25), (x2 + r * 0.7, y2 - r * 0.8)], 1.6, 'swell')


def clothes(d, view):
    sh = parts.shoulders(view, 178, drop=4, neck=64, top=140)
    waves = d.seigaiha('#e08e5c', 16, 1.2)
    towel = d.stripes(TERRA, 22, 6)
    d.shape(sh, WHITE, 4.2, nib=0.6)
    if view == 'q':
        d.shape([(124, 162), (176, 200), (188, 345), (128, 345), (120, 250)], WHITE, 3.0, pattern=towel, nib=0.6)
        d.shape([(-68, 345, 'c'), (-64, 276, 'c'), (72, 264, 'c'), (84, 345, 'c')], TERRA, 3.4, pattern=waves, nib=0.6)
        d.line([(-64, 276), (-48, 220), (-40, 168)], 9, 'even', TERRA)
        d.line([(72, 264), (78, 210), (74, 150)], 9, 'even', TERRA)
        d.shape([(-58, 142), (-64, 172), (-14, 196), (52, 184), (90, 144), (80, 122), (40, 158), (-10, 166)], WHITE,
                3.0, nib=0.6)
        d.line([(-14, 196), (-8, 230), (-12, 270)], 3.0, 'taper')
        for x, y in ((-36, 238), (22, 232)):
            d.shape(parts.oval(x, y, 6, 6, 8), WHITE, 1.6)
        d.line([(-98, 250), (-104, 300), (-100, 345)], 3.4, 'taper')
    elif view == 'f':
        d.shape([(96, 166), (150, 192), (162, 345), (104, 345), (98, 250)], WHITE, 3.0, pattern=towel, nib=0.6)
        d.shape([(-78, 345, 'c'), (-72, 270, 'c'), (72, 270, 'c'), (78, 345, 'c')], TERRA, 3.4, pattern=waves, nib=0.6)
        d.line([(-72, 270), (-64, 214), (-52, 166)], 9, 'even', TERRA)
        d.line([(72, 270), (64, 214), (52, 166)], 9, 'even', TERRA)
        d.shape([(-70, 130), (-74, 168), (-30, 190), (0, 194), (30, 190), (74, 168), (70, 130), (30, 160), (-30, 160)],
                WHITE, 3.0, nib=0.6)
        d.line([(0, 194), (4, 230), (0, 270)], 3.0, 'taper')
        for x, y in ((-28, 236), (28, 236)):
            d.shape(parts.oval(x, y, 6, 6, 8), WHITE, 1.6)
    else:
        d.shape([(-60, 345, 'c'), (-58, 268, 'c'), (-20, 262, 'c'), (-14, 345, 'c')], TERRA, 3.4, pattern=waves, nib=0.6)
        d.line([(-40, 266), (-24, 210), (-10, 166)], 9, 'even', TERRA)
        d.shape([(-24, 150), (-30, 180), (10, 192), (70, 176), (102, 138), (80, 124), (40, 156), (0, 160)], WHITE, 3.0,
                nib=0.6)
        d.shape([(30, 162), (92, 172), (108, 345), (44, 345), (34, 250)], WHITE, 3.0, pattern=towel, nib=0.6)


def bust(d, view='q', expr=None, hand=False):
    expr = EXPR.get(expr, expr) or CALM
    parts.neck(d, p, view, 90, 40)
    with d.g(0, -14):
        clothes(d, view)
    hd(d, view, expr)
    if hand:
        ladle(d, -112, 345, -128, 150, 44)
        parts.hand(d, -62, 338, 1.5, 122, 'grip', skin=SKIN, lw=1.7)


def figure(d):
    """Laughing, leaning back, the belly forward, the ladle high, the other hand open: 'come and eat!'.
    Feet at y = 0."""
    waves = d.seigaiha('#e08e5c', 12, 1.0)
    checks = d.checks('#3f4a5a', 7)
    towel = d.stripes(TERRA, 14, 4)
    hx, hy, hs, rot = -6, -724, 0.5, 9
    for (hipx, kx, ax) in ((-30, -46, -50), (44, 58, 62)):
        d.shape(parts.tube([(hipx, -350), (kx, -180), (ax, -30)], [86, 66, 52]), '#e6dfd0', 3.4, pattern=checks, nib=0.6)
        d.shape([(ax + 26, -34), (ax + 28, -2), (ax - 20, 4), (ax - 62, 4), (ax - 66, -10), (ax - 30, -32)], '#2a2426',
                2.6, nib=0.5)
    # far arm, thrown open
    d.shape(parts.tube([(-132, -584), (-170, -598), (-204, -616)], [50, 44, 34]), SKIN, 2.2)
    parts.hand(d, -202, -615, 0.8, 104, 'open', flip=True, skin=SKIN, lw=1.6)
    d.shape([(-56, -660), (-92, -648), (-150, -612), (-146, -562), (-116, -560), (-70, -590)], WHITE, 3.4, nib=0.6)
    d.line([(-146, -612), (-138, -588), (-140, -564)], 3.0, 'swell')
    # the jacket
    body = [(-76, -648), (-106, -566), (-122, -452), (-104, -350), (-70, -330), (86, -322), (106, -430), (110, -566),
            (98, -658), (10, -680)]
    d.shape(body, WHITE, 4.0, nib=0.6)
    for x, y in ((-70, -590), (-14, -596)):
        d.shape(parts.oval(x, y, 5, 5, 8), WHITE, 1.4)
    # the long apron
    apron = [(-74, -566, 'c'), (-116, -462), (-116, -380), (-98, -250), (-92, -128, 'c'), (-30, -118), (44, -122, 'c'),
             (60, -330), (54, -470), (36, -572, 'c')]
    d.shape(apron, TERRA, 3.8, pattern=waves, nib=0.6)
    d.line([(-74, -566), (-56, -620), (-40, -664)], 7, 'even', TERRA)
    d.line([(36, -572), (40, -620), (34, -668)], 7, 'even', TERRA)
    d.line([(-118, -440), (-30, -452), (56, -448)], 5.0, 'swell', TERRA_D)
    for f in ([(-60, -440), (-76, -300), (-70, -130)], [(-10, -440), (-14, -290), (-6, -124)],
              [(30, -440), (40, -290), (36, -126)]):
        d.line(f, 3.0, 'taper', TERRA_D)
    # the towel over the shoulder
    d.shape([(60, -672), (98, -664), (108, -560), (72, -552), (66, -610)], WHITE, 2.8, pattern=towel, nib=0.6)
    # near arm up, the ladle
    ladle(d, 172, -700, 118, -862, 30)
    d.shape([(70, -662), (104, -652), (172, -672), (170, -722), (136, -716), (84, -700)], WHITE, 3.6, nib=0.6)
    d.line([(160, -674), (150, -698), (156, -720)], 3.0, 'swell')
    d.shape(parts.tube([(154, -700), (152, -744), (150, -780)], [50, 44, 34]), SKIN, 2.2)
    parts.hand(d, 150, -778, 0.8, 196, 'grip', skin=SKIN, lw=1.6)
    with d.g(hx, hy, hs, rot):
        parts.neck(d, p, 'q', 90, 30)
    d.shape([(-40, -664), (-44, -648), (-10, -636), (30, -642), (48, -668), (40, -678), (20, -656), (-8, -652)], WHITE,
            2.6, nib=0.6)
    with d.g(hx, hy, hs, rot):
        hd(d, 'q', CALM)
