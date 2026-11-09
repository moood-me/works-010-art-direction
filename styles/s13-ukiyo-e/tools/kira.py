"""Кира, about 15 — prickly, closed, defiant; vulnerable underneath. A thin long face of the shin-hanga, the
look sideways from under a lowered brow, the mouth pressed; black hair cut in jags, the fringe over one eye;
her own oversized hoodie printed with a dark pattern, acid-yellow headphones round the neck, heavy boots."""
import parts
from kit import INK

NAME = 'Кира'
HAIR = '#1c181c'
SHEEN = '#7f7a90'
PLUM = '#4b2f48'
PLUM_D = '#33203a'
LIME = '#cfdc3c'
COAL = '#3a383c'
HEIGHT = 690

p = parts.P(long=1.1, cheek=-3, chin=-5, jaw=-2,
            eye=dict(w=34, h=7.4, iris=6.6, lid=4.4, slant=-1, lower=0.75, bag=0.3, color='#2a2428'),
            brow=dict(kind='arc', w=3.4, len=36, arch=1, y=-19, tilt=-4),
            nose=dict(kind='soft', s=0.84), mouth=dict(w=18, y=62, lip='#8a3d48', full=0.8),
            blush=('#e2a48f', 0.0))
CALM = dict(lift=-2, tilt=-4, open=0.82, look=(5, 0.5), mouth='pressed')
EXPR = {'joy': dict(lift=1, tilt=-1, open=0.8, look=(4, 0), mouth='smirk'),
        'surprise': dict(lift=9, tilt=2, open=1.5, look=(1, 0), mouth='o'),
        'sad': dict(lift=0, tilt=8, open=0.65, look=(2, 3), mouth='sad'),
        'anger': dict(lift=-7, tilt=-10, open=0.85, look=(5, 0), mouth='frown')}


def hair_back(d, view):
    d.fill([(60, -100), (100, -60), (106, -6, 'c'), (112, 34, 'c'), (94, 30), (96, 60, 'c'), (78, 46), (72, 70, 'c'),
            (60, 40), (40, 0)], HAIR)


def hair_front(d, view):
    """Cut in jags; the long fringe falls from the parting over the far eye."""
    cap = [(22, -84, 'c'), (-20, -112), (-62, -98), (-88, -60), (-90, -20, 'c'),
           (-88, 26, 'c'), (-78, 2), (-72, 40, 'c'), (-62, 8), (-54, 34, 'c'), (-44, 0), (-36, 14, 'c'), (-28, -18),
           (-4, -34), (20, -60)]
    top = [(22, -84, 'c'), (-20, -114), (30, -120), (78, -102), (104, -58), (108, -8, 'c'), (86, 24), (80, -4, 'c'),
           (70, 30, 'c'), (64, -14), (52, -22, 'c'), (46, 18, 'c'), (40, -30), (30, -62)]
    d.fill(top, HAIR)
    d.fill(cap, HAIR)
    d.strands([(18, -86), (-20, -100), (-60, -80), (-80, -30), (-80, 10)],
              [(18, -62), (-6, -50), (-30, -34), (-46, -10), (-50, 16)], 5, 0.9, SHEEN, op=0.55, t0=0.1)
    d.strands([(26, -88), (60, -80), (88, -50), (92, -6)], [(32, -62), (46, -40), (60, -20), (66, 10)], 4, 0.9, SHEEN,
              op=0.55, t0=0.1)


def extra(d, view, ex, lay):
    # a ring in the ear
    d.contour(parts.oval(62, 36, 4.5, 5.5, 8), 1.6, '#8a8684', nib=0)


def phones(d, x, y, s=1.0, far=False):
    """A cup of the headphones."""
    k = 0.6 if far else 1.0
    d.shape(parts.oval(x, y, 26 * s * k, 34 * s, 12, rot=-12), LIME, 2.8 * s ** 0.5, nib=0.5)
    d.shape(parts.oval(x - 3 * s, y, 15 * s * k, 22 * s, 12, rot=-12), COAL, 1.6)


def clothes(d, view):
    hemp = d.asanoha(PLUM_D, 30, 1.4)
    hood = [(-64, 176), (-52, 110), (10, 84), (96, 100), (140, 162), (128, 230), (-50, 230)]
    d.shape(hood, PLUM_D, 3.6, nib=0.6)
    return hemp


def bust(d, view='q', expr=None, hand=False):
    expr = EXPR.get(expr, expr) or CALM
    hemp = clothes(d, 'q')
    with d.g(8, 14, 1.0, -7):
        hair_back(d, 'q')
        parts.neck(d, p, 'q', 40, 70)
    sh = parts.shoulders('q', 124, drop=22, neck=46, top=156)
    d.shape(sh, PLUM, 4.0, pattern=hemp, nib=0.6)
    # the neck of the hoodie, the cords
    d.shape([(-40, 172), (-30, 200), (10, 214), (52, 200), (66, 160), (54, 152), (40, 184), (8, 194), (-22, 184)],
            PLUM_D, 2.6, nib=0.5)
    d.line([(-14, 204), (-20, 262), (-16, 318)], 3.4, 'even', '#e9e2cf', nib=0)
    d.line([(22, 208), (26, 270), (22, 330)], 3.4, 'even', '#e9e2cf', nib=0)
    d.line([(-16, 318), (-16, 332)], 5.0, 'even', LIME, nib=0)
    d.line([(22, 330), (22, 344)], 5.0, 'even', LIME, nib=0)
    d.line([(112, 250), (120, 300), (116, 345)], 3.4, 'taper')
    d.line([(-60, 256), (-66, 300), (-62, 345)], 3.0, 'taper')
    phones(d, -44, 178, 1.0, far=True)
    phones(d, 82, 176, 1.0)
    with d.g(8, 14, 1.0, -7):
        parts.head(d, p, 'q', expr, extra=extra, front=hair_front)


def figure(d):
    """A slouch: the head down, the shoulders round, one hand in the pocket, the sleeve of the other down to
    the fingers, a boot turned in. Feet at y = 0."""
    hemp = d.asanoha(PLUM_D, 20, 1.0)
    hx, hy, hs, rot = -34, -622, 0.47, -13
    sk = p['skin']
    # legs, boots
    for i, (hipx, kx, ax) in enumerate(((0, -14, -8), (30, 34, 40))):
        d.shape(parts.tube([(hipx, -340), (kx, -190), (ax, -50)], [44, 32, 26]), COAL, 3.0, nib=0.6)
        boot = [(ax + 17, -74), (ax + 19, -4), (ax - 12, 4), (ax - 48, 4), (ax - 54, -14), (ax - 40, -30),
                (ax - 16, -40), (ax - 16, -72)]
        if i == 0:
            boot = [(ax + 17, -74), (ax + 19, -2), (ax - 10, 6), (ax - 34, 10), (ax - 44, -4), (ax - 34, -24),
                    (ax - 16, -40), (ax - 16, -72)]
        d.shape(boot, '#242024', 2.6, nib=0.5)
        d.line([(ax - 46, 2), (ax - 10, 3), (ax + 18, -3)] if i else [(ax - 34, 8), (ax - 8, 5), (ax + 18, -1)], 4.0,
               'even', '#5a565c', nib=0)
        for k in range(3):
            y = -38 - k * 11
            d.line([(ax - 15, y), (ax - 4, y + 4)], 2.2, 'even', LIME, nib=0)
    d.line([(8, -330), (-4, -250), (-12, -190)], 2.6, 'taper')
    # the hood on the back
    d.shape([(-10, -612), (30, -624), (70, -596), (78, -548), (40, -530), (0, -560)], PLUM_D, 3.0, nib=0.6)
    with d.g(hx, hy, hs, rot):
        hair_back(d, 'q')
        parts.neck(d, p, 'q', 40, 60)
    # near hand, half in the sleeve
    parts.hand(d, 62, -366, 0.5, 4, 'rest', skin=sk, lw=1.4)
    # the hoodie, too big
    body = [(-40, -584), (-62, -516), (-64, -420), (-54, -334), (-30, -322), (64, -316), (78, -420), (76, -520),
            (50, -594), (4, -604)]
    d.shape(body, PLUM, 3.6, pattern=hemp, nib=0.6)
    d.shape([(-58, -430), (-10, -436), (-6, -356), (-56, -352)], PLUM, 2.6, pattern=hemp, nib=0.5)
    d.line([(-54, -334), (0, -326), (64, -316)], 6.0, 'even', PLUM_D)
    # far arm into the pocket
    d.shape([(-38, -582), (-64, -540), (-74, -450), (-52, -396), (-30, -410), (-44, -470), (-34, -536)], PLUM, 3.0,
            pattern=hemp, nib=0.6)
    d.line([(-66, -470), (-56, -452), (-42, -452)], 2.6, 'taper')
    # near arm hanging
    d.shape([(40, -592), (66, -580), (82, -480), (80, -372), (56, -350), (48, -372), (50, -470), (40, -540)], PLUM,
            3.4, pattern=hemp, nib=0.6)
    d.line([(52, -470), (64, -452), (74, -458)], 2.6, 'taper')
    d.line([(50, -372), (66, -362), (80, -372)], 5.0, 'even', PLUM_D)
    # the cords, the headphones
    d.line([(-16, -584), (-22, -540), (-20, -500)], 2.2, 'even', '#e9e2cf', nib=0)
    d.line([(0, -582), (2, -536), (0, -492)], 2.2, 'even', '#e9e2cf', nib=0)
    d.line([(-20, -500), (-20, -490)], 3.6, 'even', LIME, nib=0)
    d.line([(0, -492), (0, -482)], 3.6, 'even', LIME, nib=0)
    d.line([(-36, -590), (-10, -574), (22, -590)], 5.0, 'swell', LIME, nib=0)
    phones(d, 26, -588, 0.5)
    with d.g(hx, hy, hs, rot):
        parts.head(d, p, 'q', CALM, extra=extra, front=hair_front)
