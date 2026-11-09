"""Вера, about 40 — strict, clever, tired. The long face and the narrow eye of Utamaro's women, the hair
gathered into one black mass with a pin through it (a pencil); her own long coat, glasses, a folder."""
import parts
from kit import INK

NAME = 'Вера'
HAIR = '#1f1a1c'
SHEEN = '#8c8a94'
COAT = '#3f5263'
SCARF = '#b4899a'
FOLDER = '#c9a35a'
HEIGHT = 760

p = parts.P(long=1.16, cheek=-3, chin=-2, jaw=-1,
            eye=dict(w=40, h=6.6, iris=6.6, lid=3.6, slant=-2.5, lower=0.5, bag=0.55, lash=0.3, crease=0.5,
                     color='#2e2624'),
            brow=dict(kind='arc', w=3.0, len=42, arch=2, y=-21, tilt=-2),
            nose=dict(kind='long', s=0.95), mouth=dict(w=22, y=62, lip='#a3483a', full=0.7),
            blush=('#e2a48f', 0.0))
CALM = 'stern'
EXPR = {'joy': dict(lift=2, tilt=1, open=0.6, look=(0, 0), mouth='smile'),
        'anger': dict(lift=-6, tilt=-9, open=0.8, look=(0, 0), mouth='frown')}


def hair_back(d, view):
    """The knot of hair behind the crown, a pencil through it."""
    d.line([(26, -150), (120, -62)], 5.0, 'even', '#c9a35a', nib=0)
    d.line([(26, -150), (34, -142)], 5.0, 'even', '#2f2a28', nib=0)
    knot = parts.oval(80, -98, 36, 31, 12, rot=-30)
    d.fill(knot, HAIR)
    d.strands([(52, -118), (80, -130), (110, -112), (112, -84)], [(62, -94), (80, -100), (96, -92), (96, -78)], 4, 0.9,
              SHEEN, op=0.55)


def hair_front(d, view):
    line = [(-80, -30), (-68, -62), (-32, -84), (10, -74), (40, -48), (52, -18)]
    d.fill([(-80, -30), (-82, -58), (-62, -92), (-22, -110), (30, -110), (70, -92), (94, -54), (96, -12), (84, 26),
            (70, 30), (72, 6), (64, -16, 'c')] + line[::-1][1:], HAIR)
    d.strands(line, [(-82, -40), (-62, -92), (-10, -110), (60, -98), (94, -50)], 6, 0.9, SHEEN, op=0.55, t0=0.12)
    d.strands([(52, -18), (64, -16), (72, 6)], [(94, -54), (96, -12), (84, 26)], 3, 0.9, SHEEN, op=0.55)
    d.fringe(line, 6, 0.9, HAIR, lean=0.9, step=3.0, side=1)
    d.line([(50, -20), (46, 2), (48, 18)], 1.6, 'taper', HAIR)


def extra(d, view, ex, lay):
    parts.glasses(d, view, r=22, ry=13, y=1, lw=1.8, tint=0, sq=0.12)
    d.line([(-22, 40), (-18, 50), (-21, 58)], 1.0, 'swell', nib=0, op=0.6)


def clothes(d, view):
    sh = parts.shoulders(view, 122, drop=4, neck=42)
    komon = d.dots('#6d8296', 9, 1.3)
    d.shape(sh, COAT, 3.8, pattern=komon, nib=0.6)
    # the scarf at the neck
    sc = [(-36, 150), (-40, 180), (-10, 214), (30, 208), (60, 176), (58, 140), (20, 150), (-10, 156)]
    d.shape(sc, SCARF, 2.6, pattern=d.stripes('#8f6577', 8, 2, rot=70), nib=0.5)
    d.line([(-30, 172), (0, 188), (40, 174)], 2.2, 'swell')
    # lapels
    d.line([(-38, 184), (-30, 240), (-4, 300), (4, 345)], 4.2, 'taper')
    d.line([(58, 178), (40, 240), (10, 300)], 4.2, 'taper')
    d.line([(-38, 184), (-66, 226), (-40, 262), (-22, 262)], 2.8, 'taper')
    d.line([(58, 178), (92, 224), (62, 262), (30, 264)], 2.8, 'taper')
    d.line([(118, 238), (124, 292), (120, 345)], 3.2, 'taper')


def bust(d, view='q', expr=None, hand=False):
    expr = EXPR.get(expr, expr) or CALM
    hair_back(d, 'q')
    parts.neck(d, p, 'q', 42, 70)
    clothes(d, 'q')
    parts.head(d, p, 'q', expr, extra=extra, front=hair_front)
    if hand:
        d.shape([(-128, 345), (-120, 252), (-36, 240), (-30, 345)], FOLDER, 3.0, nib=0.6)
        d.shape([(-108, 270), (-60, 264), (-58, 288), (-106, 294)], '#f6f0e0', 1.4)
        parts.hand(d, -30, 332, 1.2, 108, 'rest', skin=p['skin'], lw=1.6)
        d.shape([(-34, 345), (-36, 312), (-10, 300), (10, 345)], COAT, 3.4, pattern=d.dots('#6d8296', 9, 1.3), nib=0.6)


def figure(d):
    """Straight as a pole, a folder held to her side; only the hem of the coat moves. Feet at y = 0."""
    komon = d.dots('#6d8296', 7, 1.0)
    hx, hy, hs, rot = -6, -712, 0.46, -2
    with d.g(hx, hy, hs, rot):
        hair_back(d, 'q')
    for ax, ay in ((-20, -18), (22, -12)):
        d.shape(parts.tube([(ax, -150), (ax + 1, -80), (ax, ay - 8)], [26, 20, 14]), '#4a4347', 1.8)
        d.shape([(ax + 10, ay - 12), (ax + 11, ay + 4), (ax + 4, ay + 6), (ax + 2, ay - 2), (ax - 34, ay + 8),
                 (ax - 38, ay + 2), (ax - 10, ay - 6)], '#2a2426', 2.0)
    # far arm
    d.shape([(-36, -640), (-54, -606), (-62, -500), (-66, -412), (-46, -408), (-42, -500), (-36, -560)], COAT, 3.0,
            pattern=komon, nib=0.6)
    parts.hand(d, -56, -410, 0.54, 6, 'rest', skin=p['skin'], lw=1.5)
    d.line([(-68, -412), (-56, -406), (-45, -408)], 2.8, 'swell')
    # the coat
    coat = [(-40, -642), (-46, -560), (-36, -474), (-48, -330), (-64, -140, 'c'), (-22, -126), (28, -136),
            (70, -124, 'c'), (58, -330), (44, -474), (50, -560), (46, -648), (4, -660)]
    d.shape(coat, COAT, 3.6, pattern=komon, nib=0.6)
    d.line([(-6, -640), (-12, -474), (-18, -300), (-22, -128)], 3.2, 'taper')
    for f in ([(30, -460), (44, -300), (50, -132)], [(-30, -460), (-40, -300), (-46, -150)],
              [(10, -440), (16, -280), (28, -138)]):
        d.line(f, 2.6, 'taper')
    belt = [(-37, -482), (44, -486), (45, -462), (-36, -458)]
    d.shape(belt, '#2f3d4b', 2.2)
    d.shape([(-12, -486), (4, -486), (6, -458), (-10, -458)], '#c9a548', 1.4)
    for y in (-600, -540):
        d.dot(-22, y, 3.2, '#c9a548')
        d.dot(10, y - 2, 3.2, '#c9a548')
    # scarf
    d.shape([(-22, -650), (-24, -630), (-6, -616), (18, -620), (30, -640), (28, -660), (4, -654)], SCARF, 2.2,
            pattern=d.stripes('#8f6577', 6, 1.6, rot=70), nib=0.5)
    # the folder and the near arm
    d.shape([(-28, -566), (30, -578), (40, -470), (-18, -458)], FOLDER, 2.8, nib=0.6)
    d.shape([(-16, -548), (14, -554), (16, -536), (-14, -530)], '#f6f0e0', 1.2)
    d.shape([(30, -654), (56, -642), (72, -560), (74, -482), (58, -462), (12, -500), (6, -522), (42, -540, 'c'),
             (44, -600)], COAT, 3.2, pattern=komon, nib=0.6)
    d.line([(58, -500), (68, -492), (72, -478)], 2.6, 'taper')
    d.line([(42, -540), (52, -524), (58, -508)], 2.6, 'taper')
    parts.hand(d, 8, -510, 0.54, 78, 'rest', skin=p['skin'], lw=1.5)
    d.line([(5, -523), (9, -510), (14, -498)], 2.8, 'swell')
    with d.g(hx, hy, hs, rot):
        parts.neck(d, p, 'q', 42, 60)
    d.shape([(-20, -654), (-22, -634), (-4, -622), (16, -626), (26, -644), (24, -662), (4, -656)], SCARF, 2.2,
            pattern=d.stripes('#8f6577', 6, 1.6, rot=70), nib=0.5)
    with d.g(hx, hy, hs, rot):
        parts.head(d, p, 'q', CALM, extra=extra, front=hair_front)
