"""Тим, about 8 — mischievous, curious. A child of Hokusai's sketchbooks and Harunobu's prints: a round head,
a big forehead, a snub nose, round cheeks in pink bokashi; his own striped shirt and shorts, a butterfly net."""
import parts
from kit import INK

NAME = 'Тим'
HAIR = '#5a3220'
SHEEN = '#b98458'
WHITE = '#f6f0e0'
REDS = '#b8402f'
SHORTS = '#3f5a78'
HEIGHT = 500

p = parts.P(long=0.86, cheek=8, chin=1, jaw=2,
            eye=dict(w=36, h=12, iris=8.6, lid=3.2, slant=0.5, lower=0.4, y=10, color='#3a2a1e'),
            brow=dict(kind='arc', w=3.0, len=30, arch=5, y=-26),
            nose=dict(kind='snub', s=0.9), mouth=dict(w=26, y=60, lip=None, full=1.0),
            blush=('#e88f78', 0.5), ear=1.15)
CALM = dict(lift=3, tilt=-2, open=0.95, look=(-2, -1.5), mouth='smirk')
EXPR = {'joy': dict(lift=4, tilt=0, open=0.0, mouth='grin', blush=0.5),
        'surprise': dict(lift=12, tilt=2, open=1.5, look=(0, 0), mouth='gasp'),
        'sad': dict(lift=1, tilt=9, open=0.75, look=(-1, 3), mouth='sad'),
        'anger': dict(lift=-8, tilt=-10, open=0.85, look=(0, 0), mouth='frown')}


def hair_front(d, view):
    """A tousled mop: tufts sticking out of the outline, a jagged fringe."""
    out = [(-82, -22, 'c'), (-92, -52, 'c'), (-76, -66), (-80, -96, 'c'), (-50, -100), (-40, -126, 'c'), (-10, -112),
           (12, -132, 'c'), (34, -110), (66, -120, 'c'), (76, -92), (104, -80, 'c'), (98, -50), (114, -22, 'c'),
           (98, -4), (102, 30, 'c'), (82, 26), (72, 46, 'c'), (66, 18, 'c')]
    bang = [(60, -16, 'c'), (44, -36), (32, -20, 'c'), (16, -46), (0, -26, 'c'), (-18, -50), (-32, -32, 'c'),
            (-50, -54), (-60, -36, 'c'), (-72, -50)]
    d.fill(out + bang, HAIR)
    d.strands([(-40, -120), (-70, -90), (-84, -50)], [(-20, -70), (-48, -60), (-66, -44)], 3, 0.9, SHEEN, op=0.6)
    d.strands([(10, -126), (60, -112), (100, -60), (100, 10)], [(0, -60), (36, -50), (62, -20), (70, 20)], 5, 0.9,
              SHEEN, op=0.6)
    d.strands([(-36, -122), (-10, -110), (12, -128)], [(-30, -50), (-8, -42), (14, -48)], 3, 0.9, SHEEN, op=0.6)


def extra(d, view, ex, lay):
    for x, y in ((-64, 30), (-58, 36), (-68, 38), (0, 34), (8, 40), (16, 33), (10, 28)):
        d.dot(x, y, 1.3, '#b0704e')
    if ex['mouth'] in ('grin', 'laugh'):
        mx, my = lay['mouth'][0], lay['mouth'][1]
        d.fill([(mx - 1, my - 3), (mx + 5, my - 3), (mx + 5, my + 5), (mx - 1, my + 5)], '#5a2420', n=1)


def clothes(d, view):
    sh = parts.shoulders(view, 104, drop=10, neck=36)
    st = d.stripes(REDS, 30, 14, rot=90)
    d.shape(sh, WHITE, 3.6, pattern=st, nib=0.6)
    band = [(-26, 164), (-14, 186), (12, 196), (38, 186), (50, 146)]
    d.fill([(-26, 164, 'c')] + band[1:-1] + [(50, 146, 'c'), (20, 128), (-8, 132)], p['skin'])
    d.line([(x, y + 4) for x, y in band], 7.0, 'even', REDS)
    d.line(band, 2.0, 'swell')
    d.line([(100, 232), (106, 290), (102, 345)], 3.0, 'taper')


def bust(d, view='q', expr=None, hand=False):
    expr = EXPR.get(expr, expr) or CALM
    parts.neck(d, p, 'q', 40, 60)
    with d.g(0, -14):
        clothes(d, 'q')
    parts.head(d, p, 'q', expr, extra=extra, front=hair_front)
    if hand:
        parts.hand(d, -84, 345, 1.1, 180, 'point', skin=p['skin'], lw=1.6)
        beetle(d, -93, 222, 1.1)


def beetle(d, x, y, s=1.0):
    """A stag beetle on a thread — the summer toy of the boys in the old prints."""
    with d.g(x, y, s, -20):
        d.shape(parts.oval(0, -14, 13, 18, 10), '#2f2a28', 1.2)
        d.shape(parts.oval(0, -36, 9, 8, 8), '#2f2a28', 1.2)
        d.line([(0, -32), (0, 2)], 1.0, 'even', '#8a7f72', nib=0)
        d.line([(-4, -42), (-12, -56), (-4, -62)], 2.4, 'taper')
        d.line([(4, -42), (12, -56), (4, -62)], 2.4, 'taper')
        for sg in (-1, 1):
            for k, (a, b) in enumerate((((10, -26), (24, -34)), ((12, -14), (28, -12)), ((10, -2), (24, 8)))):
                d.line([(sg * a[0], a[1]), (sg * b[0], b[1]), (sg * (b[0] + 4), b[1] + 8)], 1.6, 'taper')


def net(d, x1, y1, x2, y2, r=34):
    """A butterfly net: the pole from (x1, y1) to the hoop at (x2, y2)."""
    d.line([(x1, y1), (x2, y2)], 4.6, 'even', '#8a6a3a', nib=0)
    hoop = parts.oval(x2 - r * 0.7, y2 - r * 0.7, r, r * 0.55, 12, rot=-35)
    bag = [hoop[2], hoop[1], hoop[0], hoop[11], hoop[10], hoop[9], (x2 - r * 0.2, y2 + r * 0.9),
           (x2 - r * 1.3, y2 + r * 1.5), (x2 - r * 1.6, y2 + r * 0.4)]
    d.fill(bag, WHITE, op=0.55)
    d.strands([hoop[9], (x2 - r * 0.3, y2 + r * 0.7), (x2 - r * 1.3, y2 + r * 1.5)],
              [hoop[3], (x2 - r * 1.7, y2 + r * 0.2), (x2 - r * 1.3, y2 + r * 1.5)], 6, 0.8, '#6e6a66', op=0.7, jitter=0)
    d.contour(hoop, 2.4, '#8a6a3a', nib=0.2)


def figure(d):
    """Running after a butterfly, the net up, one foot off the ground. Feet at y = 0."""
    st = d.stripes(REDS, 22, 10, rot=96)
    hx, hy, hs, rot = -34, -434, 0.5, 9
    sk = p['skin']
    # far arm, swung back
    d.shape(parts.tube([(8, -370), (40, -338), (70, -314)], [26, 22, 18]), sk, 1.8)
    parts.hand(d, 68, -315, 0.4, -64, 'open', skin=sk, lw=1.4)
    d.shape([(-4, -384), (20, -386), (44, -350), (30, -334), (6, -350)], WHITE, 2.6, pattern=st, nib=0.6)
    # back leg, kicked up
    d.shape(parts.tube([(14, -214), (26, -146), (64, -110)], [40, 30, 22]), sk, 1.9)
    d.shape([(54, -124), (74, -128), (96, -100), (92, -84), (70, -92), (58, -102)], WHITE, 2.0)
    d.shape([(70, -92), (92, -84), (104, -64), (94, -56), (78, -66), (66, -80)], REDS, 2.2, nib=0.6)
    # front leg, landing
    d.shape(parts.tube([(-22, -214), (-50, -134), (-56, -36)], [42, 31, 22]), sk, 1.9)
    d.line([(-58, -144), (-50, -130), (-40, -134)], 1.4, 'swell', nib=0)
    d.fill([(-62, -124), (-46, -128), (-44, -114), (-60, -110)], '#e8c9a0')
    d.contour([(-62, -124), (-46, -128), (-44, -114), (-60, -110)], 1.2)
    d.shape([(-68, -58), (-44, -56), (-44, -30), (-68, -30)], WHITE, 2.0)
    d.shape([(-42, -34), (-40, -4), (-66, 2), (-98, 0), (-100, -10), (-72, -30)], REDS, 2.4, nib=0.6)
    d.line([(-98, -2), (-70, 1), (-42, -4)], 3.0, 'even', WHITE)
    # shorts
    shorts = [(-34, -276), (-46, -210), (-8, -196), (2, -236, 'c'), (4, -196), (40, -204), (30, -268)]
    d.shape(shorts, SHORTS, 3.2, nib=0.6, pattern=d.dots('#6f8fa8', 8, 1.2))
    d.line([(-10, -264), (-22, -230), (-28, -204)], 2.4, 'taper')
    # the shirt, pulled by the run
    shirt = [(-36, -382), (-46, -320), (-36, -262), (34, -252), (36, -320), (24, -388), (-4, -396)]
    d.shape(shirt, WHITE, 3.2, pattern=st, nib=0.6)
    d.line([(20, -330), (30, -290), (32, -256)], 2.4, 'taper')
    with d.g(hx, hy, hs, rot):
        parts.neck(d, p, 'q', 40, 44)
    d.line([(-28, -386), (-14, -378), (2, -384), (10, -396)], 5.0, 'even', REDS)
    # the net and the near arm
    net(d, 30, -280, -128, -474)
    d.shape([(4, -392), (26, -384), (14, -340), (-10, -336), (-18, -352)], WHITE, 2.8, pattern=st, nib=0.6)
    d.shape(parts.tube([(-4, -342), (-28, -348), (-50, -366)], [24, 21, 18]), sk, 1.8)
    parts.hand(d, -48, -364, 0.5, 118, 'grip', skin=sk, lw=1.4)
    with d.g(hx, hy, hs, rot):
        parts.head(d, p, 'q', dict(lift=6, tilt=0, open=1.1, look=(-3, -3), mouth='grin'), extra=extra,
                   front=hair_front)
    # the butterfly
    with d.g(-178, -560, 1.0, -20):
        d.shape([(0, 0), (-16, -18), (-24, -6), (-12, 4)], '#d8a23a', 1.4)
        d.shape([(0, 0), (14, -20), (24, -10), (12, 4)], '#d8a23a', 1.4)
        d.line([(0, -6), (0, 8)], 2.4, 'even')
