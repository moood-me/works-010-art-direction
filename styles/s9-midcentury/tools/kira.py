"""Кира, about 15 — prickly, closed, defiant; vulnerable underneath. Thin and angular, a slouch, the head down and
the look from under the brows, sideways. Short choppy dark hair with a long fringe over one eye, a mouth pressed
shut, an oversized plum hoodie, lime headphones round the neck, narrow trousers, heavy boots with lime laces."""
from kit import edge, shape, brush, blush, ell, circle, dryb, limb, hand, mix, INK
from face import eye, brow, mouth, EXPR

SKIN = '#f3d9c8'
SKIN_D = '#dcb3a0'
HAIR = '#262029'
HAIR_L = '#4d4257'
HOOD = '#47294a'
HOOD_D = '#321c36'
HOOD_L = '#5f3a62'
TROUS = '#34323a'
BOOT = '#232127'
SOLE = '#3c3a42'
LIME = '#d2e23c'
LIME_D = '#9fb022'
CORD = '#d9cfdc'
CHEEK = '#e58a7c'
LIPC = '#9c4048'
FIG_SCALE = 1.1  # how much larger the full figure is drawn on its own page
BUST_DY = -14

# she never smiles openly: joy is a crooked half-smirk and softer eyes
OWN = {
    'calm':     dict(eye='look', lid=0.55, gaze=2.6, brow=(5, -1), mouth='flat', ms=0.9, cheek=0.8),
    'joy':      dict(eye='look', lid=0.25, gaze=1.0, brow=(-1, -3), brow2=(-5, -4), mouth='smirk', ms=1.05, cheek=1.25),
    'surprise': dict(eye='wide', brow=(-7, -6), mouth='o', ms=0.95, cheek=1.0),
    'sad':      dict(eye='sad', brow=(-6, 4), mouth='frown', ms=0.8, cheek=0.9),
    'anger':    dict(eye='glare', brow=(9, -5), mouth='shout', ms=0.95, cheek=1.35),
}


def _e(expr):
    e = dict(EXPR[expr])
    e.update(OWN.get(expr, {}))
    return e


def _eye(x, y, s, e, side, squash=1.0, toward=-1):
    """Her eye: small, a heavy dark upper lid, no lash flick; when calm the iris slides sideways (toward = ±1 in x)."""
    k = e['eye']
    if k == 'look':
        return eye(x, y, s, 'look', side=side, squash=squash, lash=False, lid=e.get('lid', 0), gaze=side * toward * e.get('gaze', 1))
    return eye(x, y, s * 0.92, k, side=side, squash=squash, lash=False)


def _mouth(x, y, s, e, side=1, width=0.7):
    return mouth(x, y, s * e.get('ms', 1), e['mouth'], side=side, width=width, color=LIPC)


def head(view='34', expr='calm', neck=True):
    """The head around (0, 0), crown near y=-125, chin near y=95, already tipped a little down;
    neck=False leaves the neck to the figure."""
    e = _e(expr)
    bi, bo = e['brow']
    b2i, b2o = e.get('brow2', e['brow'])
    cheek = e.get('cheek', 1.0)
    o = []
    if view == '34':
        # choppy hair behind: ragged ends at the nape and by the far cheek
        o.append(shape([(-28, -130), (30, -128), (70, -104), (86, -60), (86, -14), (92, 30, 'c'), (78, 14), (74, 46, 'c'), (60, 20),
                        (0, 40), (-40, 54), (-54, 88, 'c'), (-64, 58), (-82, 78, 'c'), (-84, 42), (-102, 46, 'c'), (-94, 4),
                        (-92, -56), (-68, -108)], HAIR))
        o.append(shape([(-70, -100), (-88, -128, 'c'), (-56, -116), (-50, -142, 'c'), (-28, -122)], HAIR))
        if neck:
            o.append(shape([(-20, 64), (16, 76), (20, 150), (-26, 150)], SKIN_D))
        face = [(-52, -56), (-38, -96), (0, -110), (38, -100), (58, -70), (64, -30), (64, 4), (60, 32), (50, 58), (34, 82),
                (14, 95), (-6, 90), (-28, 70), (-46, 42), (-56, 0)]
        o.append(shape(face, SKIN))
        o.append(edge(face, 9, 13, 1.8, '#9a6a60'))
        o.append(blush(-22, 40, 12 * cheek, CHEEK, 0.5))
        o.append(_eye(-12, 12, 1.25, e, -1))
        o.append(_eye(40, 10, 1.15, e, 1, squash=0.62))
        o.append(brush([(-24, 22), (-12, 25), (-2, 22)], 1.5, SKIN_D, taper=(0.4, 0.4)))
        o.append(brow(-12, -7, 1.2, side=-1, inner=bi, outer=bo, w=4.2, length=0.95))
        o.append(brow(42, -9, 1.15, side=1, inner=b2i, outer=b2o, w=3.4, squash=0.6))
        o.append(_mouth(27, 67, 1.4, e))
        # the fringe: parted on the near side, it falls across the forehead and over the far eye in ragged points
        o.append(shape([(-58, 4, 'c'), (-62, -40), (-58, -84), (-26, -122), (26, -126), (66, -104), (86, -62), (86, -20),
                        (88, 20, 'c'), (76, -4), (68, 24, 'c'), (54, -2), (42, 28, 'c'), (28, -8), (8, -30), (-16, -42), (-34, -38),
                        (-50, -26)], HAIR))
        o.append(shape([(-56, -30), (-66, 0), (-60, 36, 'c'), (-50, 10), (-48, -20)], HAIR))
        o.append(dryb([[(-36, -110), (10, -80), (44, -30), (56, 20)], [(-10, -120), (40, -92), (68, -40), (76, 10)],
                       [(-52, -90), (-30, -60), (-10, -48)]], 2.8, HAIR_L, 0.7))
        # the tip of a straight sharp nose comes out under the fringe and breaks the far cheek
        o.append(shape([(58, 20), (64, 30), (72, 41, 'c'), (64, 46), (55, 44)], SKIN))
        o.append(brush([(60, 22), (72, 41), (64, 46), (56, 45)], 2.2, '#a8685a', taper=(0.2, 0.15)))
        return ['<g transform="rotate(6 0 70)">'] + o + ['</g>']
    if view == 'front':
        o.append(shape([(0, -132), (56, -120), (88, -78), (92, -20), (98, 34, 'c'), (84, 18), (78, 56, 'c'), (64, 30), (0, 50),
                        (-62, 34), (-70, 64, 'c'), (-82, 30), (-100, 46, 'c'), (-92, -20), (-88, -78), (-56, -120)], HAIR))
        o.append(shape([(-62, -108), (-76, -136, 'c'), (-46, -122), (-36, -146, 'c'), (-18, -126)], HAIR))
        if neck:
            o.append(shape([(-19, 66), (19, 66), (22, 150), (-22, 150)], SKIN_D))
        o.append(shape([(0, -106), (38, -98), (58, -64), (62, -16), (56, 30), (42, 64), (20, 90), (0, 96), (-20, 90), (-42, 64),
                        (-56, 30), (-62, -16), (-58, -64), (-38, -98)], SKIN))
        o.append(blush(-36, 42, 11 * cheek, CHEEK, 0.5))
        o.append(blush(36, 42, 11 * cheek, CHEEK, 0.5))
        o.append(_eye(-25, 16, 1.1, e, -1))
        o.append(_eye(25, 16, 1.1, e, 1))
        o.append(brow(-26, -1, 1.0, side=-1, inner=bi, outer=bo, w=3.6))
        o.append(brow(26, -1, 1.0, side=1, inner=b2i, outer=b2o, w=3.6))
        o.append(brush([(3, 20), (7, 42), (0, 46)], 2.4, '#b47868', taper=(0.4, 0.2)))
        o.append(_mouth(0, 68, 1.05, e, width=0.8))
        # the head is lowered: more crown than forehead; the fringe hangs over her left eye
        o.append(shape([(-62, 6, 'c'), (-70, -40), (-64, -90), (-30, -124), (28, -126), (68, -100), (86, -56), (84, -10),
                        (76, 42, 'c'), (64, 8), (54, 50, 'c'), (42, 6), (30, 34, 'c'), (20, 0), (4, -22), (-18, -32), (-38, -28),
                        (-54, -14)], HAIR))
        o.append(shape([(-60, -20), (-72, 6), (-64, 40, 'c'), (-54, 14), (-52, -10)], HAIR))
        o.append(dryb([[(-40, -112), (6, -78), (38, -24), (48, 26)], [(-12, -122), (40, -90), (66, -34), (72, 14)],
                       [(-56, -86), (-34, -54), (-14, -40)]], 2.8, HAIR_L, 0.7))
        return o
    if view == 'side':
        o.append(shape([(-20, -132), (30, -124), (60, -98), (66, -60), (40, -40), (0, 0), (0, 40), (-14, 78, 'c'), (-26, 50),
                        (-44, 84, 'c'), (-52, 52), (-74, 72, 'c'), (-74, 40), (-98, 44, 'c'), (-90, 0), (-94, -56), (-66, -112)], HAIR))
        o.append(shape([(-76, -96), (-96, -122, 'c'), (-64, -112), (-60, -140, 'c'), (-36, -122)], HAIR))
        if neck:
            o.append(shape([(-12, 60), (18, 72), (16, 150), (-26, 150)], SKIN_D))
        # profile: a straight sharp nose, thin pressed lips, a small firm chin
        o.append(shape([(-30, -100), (20, -104), (50, -84), (60, -50), (62, -14), (61, 2), (68, 22), (77, 37, 'c'), (66, 43),
                        (63, 50), (65, 57), (61, 62), (62, 70), (56, 84), (38, 95), (12, 93), (-8, 80), (-22, 40), (-30, -40)], SKIN))
        o.append(blush(24, 40, 11 * cheek, CHEEK, 0.5))
        o.append(_eye(42, 10, 1.1, e, 1, squash=0.75, toward=1))
        o.append(brow(44, -7, 1.0, side=1, inner=b2i, outer=b2o, w=3.6, squash=0.7))
        o.append(_mouth(57, 66, 1.0, e, width=0.5))
        # hair over the ear, the fringe hanging forward past the forehead
        o.append(shape([(-34, 20, 'c'), (-42, -30), (-40, -86), (-6, -120), (36, -122), (66, -98), (80, -60), (86, -16), (88, 22, 'c'),
                        (76, -2), (70, 30, 'c'), (62, -8), (52, -30), (30, -44), (4, -40), (-8, -10), (-8, 30), (-18, 62, 'c'),
                        (-26, 30)], HAIR))
        o.append(dryb([[(-20, -100), (20, -80), (56, -50), (72, -6)], [(-30, -70), (-18, -20), (-18, 30)], [(10, -112), (50, -92), (76, -50)]],
                      2.8, HAIR_L, 0.7))
        return ['<g transform="rotate(6 0 70)">'] + o + ['</g>']
    raise ValueError(view)


def _phones(x, y, s=1.0, rot=0):
    """One cup of the headphones lying on the collarbone: a lime shell, a dark pad."""
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({s})">' + ell(0, 0, 21, 27, LIME) + ell(3, 1, 13, 19, LIME_D)
            + ell(5, 1, 9, 14, HOOD_D) + '</g>')


def bust(view='34'):
    """Narrow sloping shoulders lost in a big hoodie; the hood bunched behind the neck, the headphones round it."""
    o = []
    if view == 'side':
        o.append(shape([(-70, 126), (-30, 108), (-6, 130), (-10, 170), (-60, 176)], HOOD_D))
        body = [(-96, 300), (-92, 210), (-62, 150), (-16, 132), (28, 150), (50, 210), (60, 300)]
        o.append(shape(body, HOOD))
        o.append(brush([(-34, 126), (-10, 150), (22, 150)], 9, LIME, taper=(0.05, 0.05)))
        o.append(_phones(14, 172, 1.0, 12))
        o.append(brush([(30, 176), (34, 250)], 3, CORD, taper=(0, 0.2)))
        o.append(brush([(-52, 200), (-46, 300)], 3, HOOD_D, taper=(0.3, 0)))
        return o
    sx = 1 if view == '34' else 0
    # the hood, heaped on the shoulders behind the neck
    o.append(shape([(-66 + sx * 4, 176), (-58, 128), (-26, 110), (24 + sx * 4, 112), (58 + sx * 6, 132), (66 + sx * 6, 178)], HOOD_D))
    body = [(-124 + sx * 12, 300), (-116 + sx * 12, 228), (-90 + sx * 10, 180), (-38, 154), (42 + sx * 6, 156), (92 + sx * 4, 182),
            (112, 228), (118, 300)]
    o.append(shape(body, HOOD))
    cx = sx * 6
    # the neck opening and the drawstrings
    o.append(shape([(cx - 30, 150), (cx, 160), (cx + 32, 152), (cx + 10, 190, 'c'), (cx - 6, 190, 'c')], HOOD_D))
    o.append(brush([(cx - 12, 182), (cx - 16, 232), (cx - 13, 262)], 3.2, CORD, taper=(0, 0.1)))
    o.append(brush([(cx + 14, 182), (cx + 20, 226), (cx + 18, 250)], 3.2, CORD, taper=(0, 0.1)))
    o.append(brush([(-84 + sx * 10, 204), (-78 + sx * 10, 300)], 3, HOOD_D, taper=(0.3, 0)))
    o.append(brush([(90, 206), (90, 300)], 3, HOOD_D, taper=(0.3, 0)))
    # headphones round the neck: the band behind, a cup on each collarbone
    o.append(brush([(cx - 52, 168), (cx - 46, 130), (cx - 26, 116)], 9, LIME, taper=(0.02, 0.1)))
    o.append(brush([(cx + 54, 170), (cx + 50, 134), (cx + 32, 118)], 9, LIME, taper=(0.02, 0.1)))
    o.append(_phones(cx - 52, 184, 1.0, 14))
    o.append(_phones(cx + 54, 186, 0.9, -14))
    return o


def _boot(x, toe):
    """A heavy boot standing at (x, 0): thick sole, a blunt toe (toe = ±1), lime laces."""
    t = toe
    o = [shape([(x - t * 24, -64, 'c'), (x + t * 14, -64, 'c'), (x + t * 18, -40), (x + t * 52, -30), (x + t * 60, -10, 'c'),
                (x - t * 26, -10, 'c')], BOOT),
         shape([(x - t * 28, -12, 'c'), (x + t * 62, -12, 'c'), (x + t * 62, 0, 'c'), (x - t * 28, 0, 'c')], SOLE)]
    for i in range(3):
        y = -56 + i * 9
        o.append(brush([(x + t * (2 + i * 4), y), (x + t * (16 + i * 5), y + 5)], 3, LIME, taper=(0, 0)))
    return ''.join(o)


def figure(expr='calm'):
    """Full figure, feet at y=0, about 6 heads with the slouch: hips forward, the back round, the head pushed forward
    and down; one hand in the pocket of the hoodie, the other hanging out of a sleeve that is too long."""
    o = []
    # long thin legs, all knees: the weight on the back leg, the other knee poked forward, toes turned in
    o.append(limb([(-14, -300), (-30, -176)], [28, 21], TROUS, cap=False))
    o.append(limb([(-30, -180), (-22, -56)], [21, 16], TROUS, cap=False))
    o.append(limb([(18, -300), (46, -184)], [28, 21], TROUS, cap=False))
    o.append(limb([(46, -188), (32, -56)], [21, 16], TROUS, cap=False))
    o.append(circle(-30, -178, 11.5, TROUS))
    o.append(circle(46, -186, 11.5, TROUS))
    o.append(_boot(-26, 1))
    o.append(_boot(34, 1))
    # the far arm hangs in front, the sleeve down to the knuckles
    o.append(hand(62, -332, 1.15, 4, SKIN, SKIN_D, 'curl', side=-1))
    o.append(limb([(34, -512), (60, -430)], [36, 30], HOOD_D, cap='round'))
    o.append(limb([(60, -434), (62, -334)], [30, 27], HOOD_D, cap='round'))
    # the hoodie: a big dark bean, round at the back, hanging off the shoulders
    body = [(-22, -552), (-60, -522), (-80, -450), (-74, -360), (-60, -284), (-10, -268), (50, -278), (60, -350), (50, -430),
            (44, -500), (22, -548)]
    o.append(shape(body, HOOD))
    o.append(shape([(-46, -560), (-14, -576), (14, -560), (20, -530), (-42, -520)], HOOD_D))
    o.append(brush([(-60, -290), (-10, -274), (50, -284)], 9, HOOD_D, taper=(0.03, 0.03)))
    o.append(shape([(-24, -366, 'c'), (42, -360, 'c'), (50, -306), (-38, -314)], HOOD_D, opacity=0.75))
    o.append(dryb([[(-62, -480), (-68, -420), (-60, -350)], [(30, -480), (40, -430), (38, -390)]], 3, HOOD_L, 0.6))
    # headphones round the neck, drawstrings
    o.append(brush([(-32, -548), (-10, -528), (18, -532)], 8, LIME, taper=(0.05, 0.05)))
    o.append(_phones(22, -516, 0.72, 10))
    o.append(brush([(0, -516), (-4, -470)], 2.4, CORD, taper=(0, 0.1)))
    o.append(brush([(8, -500), (10, -462)], 2.4, CORD, taper=(0, 0.1)))
    # the near arm: a long sleeve down into the pocket, the elbow sticking out behind
    o.append(limb([(-38, -522), (-78, -424)], [36, 31], HOOD_L, cap='round'))
    o.append(limb([(-78, -428), (-22, -344)], [31, 25], HOOD_L, cap='round'))
    o.append(circle(-78, -426, 15.5, HOOD_L))
    o.append(brush([(-40, -372), (-24, -350), (-8, -342)], 2.6, HOOD_D, taper=(0.3, 0.3)))
    # the head pushed forward and down
    o.append(shape([(-6, -560), (16, -556), (18, -528), (-6, -530)], SKIN_D))
    o.append('<g transform="translate(24,-594) rotate(9) scale(0.52)">' + ''.join(head('34', expr, neck=False)) + '</g>')
    return o
