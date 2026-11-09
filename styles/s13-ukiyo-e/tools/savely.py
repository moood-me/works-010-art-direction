"""Савелий Петрович, about 70, a watchmaker — grumpy outside, kind inside. An old actor of Sharaku: a heavy
nose, a mouth pulled down, bushy brows, small sharp eyes — and round wire glasses, a white moustache, a
waistcoat."""
import parts
from kit import INK

NAME = 'Савелий Петрович'
WHITE = '#f6f0e0'
GREY = '#6e6a66'
VEST = '#566b4b'
TROUSERS = '#7d7164'
TIE = '#8e3b2c'
HEIGHT = 620

p = parts.P(skin='#f2dfc6', long=0.98, cheek=11, jaw=12, chin=7, brow_ridge=3,
            eye=dict(w=30, h=8, iris=5.6, lid=3.2, slant=1.0, lower=0.7, bag=0.6, crease=0.5, color='#3a302c'),
            brow=dict(kind='bushy', w=7, len=42, arch=5, y=-22, tilt=-3, color=GREY),
            nose=dict(kind='big', s=1.08), mouth=dict(w=30, y=73, lip=None, full=1.0),
            blush=('#e2957c', 0.22), ear=1.2)
CALM = dict(lift=-3, tilt=-5, open=0.9, look=(-1, 1), mouth='frown')
EXPR = {'joy': dict(lift=4, tilt=2, open=0.0, mouth='laugh', blush=0.5),
        'surprise': dict(lift=12, tilt=2, open=1.6, look=(0, 0), mouth='o'),
        'sad': dict(lift=0, tilt=9, open=0.7, look=(-1, 2.5), mouth='sad'),
        'anger': dict(lift=-8, tilt=-11, open=0.9, look=(0, 0), mouth='snarl')}


def tufts(d, view):
    """What is left of the hair: white tufts over the ears."""
    def tuft(shape, edge, lean):
        d.fill(shape, WHITE)
        d.line(edge, 1.4, 'even', GREY)
        d.fringe(edge, 13, 1.2, GREY, lean=lean, step=4.0, side=1)
    if view == 'q':
        tuft([(44, -40), (66, -56), (92, -34), (100, 6), (90, 40), (68, 38), (74, 8), (62, -16)],
             [(66, -56), (92, -34), (100, 6), (90, 40)], 0.6)
        d.strands([(48, -38), (66, -14), (74, 10), (70, 36)], [(68, -54), (92, -32), (99, 6), (90, 38)], 5, 1.0, GREY,
                  op=0.8)
        d.fringe([(-80, -36), (-82, -16), (-80, 2)], 10, 1.2, GREY, lean=0.5, step=4.0, side=1)
    elif view == 'f':
        for sg in (1, -1):
            shape = [(sg * 72, -48), (sg * 92, -44), (sg * 106, -14), (sg * 102, 26), (sg * 88, 36), (sg * 90, 0),
                     (sg * 80, -24)]
            d.fill(shape, WHITE)
            edge = [(sg * 92, -44), (sg * 106, -14), (sg * 102, 26)]
            d.line(edge, 1.4, 'even', GREY)
            d.fringe(edge, 12, 1.2, GREY, lean=0.5, step=4.0, side=-sg)
            d.strands([(sg * 76, -44), (sg * 86, -10), (sg * 90, 30)], edge, 3, 1.0, GREY, op=0.8)
    else:
        tuft([(20, -40), (60, -62), (98, -40), (104, 0), (86, 36), (44, 44), (40, 14), (10, -14)],
             [(60, -62), (98, -40), (104, 0), (86, 36), (44, 44)], 0.5)
        d.strands([(22, -38), (36, -8), (42, 16), (44, 40)], [(62, -60), (98, -38), (103, 0), (86, 34)], 7, 1.0, GREY,
                  op=0.8)


def extra(d, view, ex, lay):
    lw = 1.1
    if view == 'q':
        for w in ([(-62, -54), (-30, -60), (12, -55)], [(-66, -42), (-30, -47), (20, -43)],
                  [(-56, -66), (-28, -71), (2, -68)]):
            d.line(w, lw, 'swell', nib=0, op=0.75)
        for w in ([(16, -2), (26, -8)], [(17, 3), (28, 3)], [(16, 8), (25, 13)]):
            d.line(w, lw, 'taper', nib=0, op=0.75)
        d.line([(-26, 46), (-18, 58), (-20, 74)], lw * 1.3, 'swell', nib=0)
        d.line([(30, 50), (38, 66), (30, 82)], lw, 'swell', nib=0, op=0.7)
        # the moustache
        m = [(-58, 49), (-42, 47), (-20, 53), (-4, 68), (-10, 74), (-28, 65), (-46, 63), (-58, 65), (-72, 69),
             (-76, 64), (-68, 54)]
        d.shape(m, WHITE, 1.5, GREY)
        d.strands([(-50, 50), (-28, 53), (-8, 68)], [(-50, 62), (-30, 64), (-11, 73)], 3, 1.0, GREY, op=0.9)
        d.strands([(-56, 51), (-68, 56), (-74, 64)], [(-56, 63), (-64, 65), (-72, 68)], 2, 1.0, GREY, op=0.9)
    elif view == 'f':
        for w in ([(-40, -56), (0, -60), (40, -56)], [(-46, -44), (0, -48), (46, -44)], [(-30, -68), (0, -71), (30, -68)]):
            d.line(w, lw, 'swell', nib=0, op=0.75)
        for sg in (1, -1):
            for w in ([(sg * 52, -2), (sg * 62, -8)], [(sg * 53, 3), (sg * 64, 3)], [(sg * 52, 8), (sg * 61, 13)]):
                d.line(w, lw, 'taper', nib=0, op=0.75)
            d.line([(sg * 20, 46), (sg * 28, 58), (sg * 26, 74)], lw * 1.3, 'swell', nib=0)
            m = [(0, 50), (sg * 20, 49), (sg * 38, 58), (sg * 46, 72), (sg * 38, 74), (sg * 22, 66), (0, 64)]
            d.shape(m, WHITE, 1.5, GREY)
            d.strands([(sg * 4, 53), (sg * 24, 54), (sg * 42, 70)], [(sg * 4, 62), (sg * 22, 64), (sg * 38, 73)], 3,
                      1.0, GREY, op=0.9)
    else:
        for w in ([(-74, -50), (-50, -56), (-24, -52)], [(-76, -38), (-50, -44), (-20, -40)]):
            d.line(w, lw, 'swell', nib=0, op=0.75)
        for w in ([(-28, -2), (-18, -8)], [(-27, 3), (-16, 3)], [(-28, 8), (-19, 13)]):
            d.line(w, lw, 'taper', nib=0, op=0.75)
        d.line([(-58, 44), (-50, 56), (-52, 72)], lw * 1.3, 'swell', nib=0)
        m = [(-86, 44), (-70, 42), (-52, 52), (-44, 68), (-50, 72), (-64, 62), (-80, 60), (-88, 54)]
        d.shape(m, WHITE, 1.5, GREY)
        d.strands([(-82, 46), (-62, 48), (-47, 67)], [(-82, 57), (-64, 59), (-50, 71)], 3, 1.0, GREY, op=0.9)
    parts.glasses(d, view, r=20, y=4, lw=1.9, tint=0)


def hd(d, view, expr):
    parts.head(d, p, view, expr, extra=extra, front=tufts)


def bow(d, x, y, s=1.0):
    d.shape([(x, y), (x - 26 * s, y - 13 * s), (x - 30 * s, y + 12 * s)], TIE, 1.8)
    d.shape([(x, y), (x + 28 * s, y - 14 * s), (x + 30 * s, y + 13 * s)], TIE, 1.8)
    d.shape(parts.oval(x, y, 6 * s, 7 * s, 8), TIE, 1.8)


def clothes(d, view):
    sh = parts.shoulders(view, 128, drop=14, neck=46)
    pat = d.kasuri('#8da07a', 20, 6)
    d.shape(sh, WHITE, 3.8, nib=0.6)
    if view == 'q':
        vest = [(-70, 345), (-74, 262), (-62, 204), (-30, 172, 'c'), (2, 270, 'c'), (58, 156, 'c'), (104, 190),
                (118, 262), (120, 345)]
        d.shape(vest, VEST, 3.4, pattern=pat, nib=0.6)
        d.line([(-30, 172), (-12, 196), (4, 208)], 2.4, 'taper')
        d.line([(58, 156), (36, 190), (10, 208)], 2.4, 'taper')
        bow(d, 6, 206, 1.0)
        d.dot(2, 300, 4.5, '#d9c9a0')
        d.dot(3, 332, 4.5, '#d9c9a0')
        d.line([(130, 250), (136, 300), (132, 345)], 2.8, 'taper', GREY)
    elif view == 'f':
        vest = [(-104, 345), (-106, 262), (-88, 202), (-42, 166, 'c'), (0, 272, 'c'), (42, 166, 'c'), (88, 202),
                (106, 262), (104, 345)]
        d.shape(vest, VEST, 3.4, pattern=pat, nib=0.6)
        d.line([(-42, 166), (-22, 194), (-4, 208)], 2.4, 'taper')
        d.line([(42, 166), (22, 194), (4, 208)], 2.4, 'taper')
        bow(d, 0, 208, 1.0)
        d.dot(0, 302, 4.5, '#d9c9a0')
        d.dot(0, 334, 4.5, '#d9c9a0')
    else:
        vest = [(-34, 345), (-40, 262), (-26, 206), (0, 172, 'c'), (-10, 215), (18, 206), (62, 158, 'c'), (44, 262),
                (40, 345)]
        d.shape(vest, VEST, 3.4, pattern=pat, nib=0.6)
        d.shape([(-16, 198), (-34, 190), (-36, 214)], TIE, 1.8)
        d.line([(60, 240), (70, 300), (66, 345)], 2.8, 'taper', GREY)


def bust(d, view='q', expr=None, hand=False):
    expr = EXPR.get(expr, expr) or CALM
    parts.neck(d, p, view, 70, 40)
    with d.g(0, -30):
        clothes(d, view)
    hd(d, view, expr)
    if hand:
        watch(d, -92, 250, 1.5)
        parts.hand(d, -48, 335, 1.2, 152, 'pinch', skin=p['skin'], lw=1.6)
        d.shape([(-96, 345), (-84, 322), (-46, 312), (-22, 330), (-20, 345)], WHITE, 3.4, nib=0.6)


def watch(d, x, y, s=1.0, chain=None):
    """A pocket watch."""
    d.shape(parts.oval(x, y - 25 * s, 6 * s, 7 * s, 8), '#c9a548', 1.4)
    d.shape(parts.oval(x, y, 21 * s, 21 * s, 12), '#c9a548', 2.0)
    d.shape(parts.oval(x, y, 16 * s, 16 * s, 12), WHITE, 1.2)
    d.line([(x, y), (x, y - 11 * s)], 1.6, 'even', nib=0)
    d.line([(x, y), (x + 8 * s, y + 3 * s)], 1.6, 'even', nib=0)
    d.dot(x, y, 1.6 * s)


def figure(d):
    """Stooped, the pocket watch on his palm, a finger raised: 'listen'. Feet at y = 0."""
    pat = d.kasuri('#8da07a', 14, 4)
    stripes = d.stripes('#665b50', 9, 2)
    hx, hy, hs, rot = -54, -508, 0.52, -8
    for (hipx, kx, ax) in ((2, -12, -4), (36, 28, 38)):
        d.shape(parts.tube([(hipx, -280), (kx, -150), (ax, -22)], [56, 44, 36]), TROUSERS, 3.2, pattern=stripes,
                nib=0.6)
        d.shape([(ax + 18, -26), (ax + 19, -2), (ax - 10, 2), (ax - 42, 2), (ax - 44, -8), (ax - 18, -24)], '#2f2a28',
                2.0)
    d.line([(10, -262), (2, -200), (-6, -150)], 2.6, 'taper')
    # far arm: the shirt sleeve, the finger up
    d.shape([(-22, -464), (-52, -446), (-90, -392), (-82, -370), (-62, -374), (-38, -408)], WHITE, 3.0, nib=0.6)
    d.shape(parts.tube([(-76, -380), (-94, -414), (-101, -442)], [28, 23, 19]), WHITE, 2.8, nib=0.6)
    parts.hand(d, -102, -440, 0.56, 186, 'point', flip=True, skin=p['skin'], lw=1.5)
    d.line([(-111, -437), (-102, -443), (-93, -440)], 2.6, 'swell')
    # the body: a round back, a belly
    body = [(-30, -464), (-58, -400), (-56, -320), (-32, -262), (68, -258), (80, -330), (74, -410), (44, -470),
            (8, -484)]
    d.shape(body, VEST, 3.6, pattern=pat, nib=0.6)
    d.fill([(-28, -466), (-36, -434), (-26, -404), (-8, -434), (4, -482)], WHITE)
    d.line([(-28, -466), (-36, -434), (-26, -404)], 2.2, 'taper')
    d.line([(4, -482), (-8, -434), (-26, -404)], 2.2, 'taper')
    bow(d, -26, -446, 0.5)
    for i, y in enumerate((-374, -332, -292)):
        d.dot(-38 + i * 3, y, 3, '#d9c9a0')
    d.line([(-40, -340), (-24, -318), (-4, -326)], 1.6, 'even', '#a8862e')
    # near arm: the watch on the palm
    d.shape([(26, -470), (52, -460), (68, -400), (66, -344), (44, -330), (30, -352), (34, -410)], WHITE, 3.2, nib=0.6)
    d.shape(parts.tube([(52, -346), (4, -352), (-28, -358)], [32, 27, 23]), WHITE, 3.0, nib=0.6)
    d.line([(44, -370), (56, -356), (60, -340)], 2.4, 'taper')
    parts.hand(d, -28, -358, 0.56, 82, 'open', skin=p['skin'], lw=1.5)
    d.line([(-28, -371), (-30, -358), (-27, -345)], 2.6, 'swell')
    watch(d, -55, -364, 0.62)
    with d.g(hx, hy, hs, rot):
        parts.neck(d, p, 'q', 64, 30)
    d.fill([(-26, -468), (-32, -450), (-12, -444), (0, -474)], WHITE)
    with d.g(hx, hy, hs, rot):
        hd(d, 'q', CALM)
