"""Марат, about 35, a cook — huge, loud, merry, generous. A broad face, a thick black beard cut round with a curly
edge, short dark curls, thick brows, a broad nose; laughing — the eyes narrowed to arcs, the mouth open with teeth
and tongue. A white cook's jacket with a red embroidered band along the collar and the fastening (as on a
kosovorotka), the sleeves rolled up; a long terracotta apron with an ornament hem; a towel with red woven ends
(a rushnik) over the shoulder; a ladle."""
import parts
from parts import P, expr, ribbon, strands, Torso
from kit import INK, RED, GOLD, CREAM, SKIN

NAME = 'Марат'
HAIR = '#231b18'
BEARD = '#1f1815'
JACKET = '#f6f0e2'
APRON = '#c0623a'
APRON_D = '#8f4024'
TROUS = '#3a3634'
SKIN_M = '#e2b48a'
HALO = dict(ring='#c0623a', field='#efe3c4', ink='#f6f0e2')

p = P(crown=-108, cheek=76, temple=70, jaw=70, jaw_y=58, chin=94, chin_w=30, skull=74, forehead=66, brow_z=70,
      nose_y=44, nose_z=92, nose_w=17, nose='big', lip_z=72, chin_z=66, mouth_y=64, mouth_w=24, lip='none',
      eye_x=31, eye_w=18, eye_h=8, iris=6.0, iris_col='#2a1a12', brow_y=-20, brow='thick', brow_w=1.3,
      brow_col=HAIR, ear_y=(-8, 38), skin=SKIN_M, blush=0.8, neck=46)

# his resting face is a wide laugh
CALM = dict(brow=4, tilt=-1, open=0.18, smile=1.0, mouth=0.75, wide=1.2, cheeks=1, look=(0, 0))


def e_(name):
    e = expr(name)
    if name in ('calm', 'joy'):
        e.update(CALM)
    if name == 'surprise':
        e.update(open=1.25, mouth=0.75, wide=0.75)
    if name == 'sadness':
        e.update(open=0.7, smile=-0.55, mouth=0.0, brow=4, tilt=6)
    if name == 'anger':
        e.update(open=0.75, smile=-0.6, mouth=0.55, brow=-6, tilt=-7, teeth=True)
    return e


def hair(d, v):
    """Short dark curls: a close cap whose edge is all small round curls, curl marks inside."""
    hl = parts.hairline(p, top=-80, temple=-48, side_y=4)
    pts = parts.shell(v, grow=12, y_side=6, hairline=hl)
    nshell = len(pts) - len([q for q in hl if v.facing(q[0], q[1]) > 0.05])
    pts = parts.lobes(pts, 16, 7, 1, nshell - 2)
    d.shape(pts, HAIR, 3, n=4)
    with d.clipped(pts, n=4):
        for (x, y, z) in ((-30, -100, 40), (10, -110, 20), (40, -96, 0), (-50, -70, 50), (60, -60, -30),
                          (20, -84, 60), (66, -20, -40), (-10, -88, 66)):
            if v.facing(x, y) > -0.3:
                cx, cy = v.pt(x, y, z)
                d.thin([(cx - 6, cy + 3), (cx - 4, cy - 4), (cx + 3, cy - 5), (cx + 6, cy + 1)], k=0.9,
                       color='#6a5a50')


def beard(d, v):
    """The beard: a black mass from ear to ear under the cheekbones, round at the chin, its edge curly; the
    moustache over it; the mouth is cut out of it."""
    pts = []
    for x, y in ((-70, 0), (-74, 30), (-66, 72), (-46, 104), (-20, 122), (0, 126), (20, 122), (46, 104), (66, 72),
                 (74, 30), (70, 0), (60, 30), (44, 46), (24, 48), (0, 46), (-24, 48), (-44, 46), (-60, 30)):
        lift = 8 if y > 30 else 4
        yy = min(y, p.chin - 2)
        if v.facing(x * 0.97, yy) < 0.08:
            # turned away: the beard's edge runs along the silhouette on that side
            lo, hi = v.extent(yy, 10)
            q = (lo if x < 0 else hi, y)
        elif abs(x) < 50 and y > 60:
            q = v.pt(x * 1.0, y, p.zs(x * 0.9, yy) + lift + (y - p.chin) * 0.25 * (y > p.chin))
        else:
            q = v.surf(x * 0.97, y, lift)
        pts.append(q)
    # keep the hidden half of the beard inside the silhouette: points turned away fold onto the edge
    # the inner edge (the cheek line) is only there where it faces us; behind, it follows the far silhouette too
    outer = pts[:11]
    outer = parts.lobes(outer, 9, 6, 0, len(outer) - 1)
    poly = outer + pts[11:]
    d.shape(poly, BEARD, 3, n=4)
    with d.clipped(poly, n=4):
        for (x, y) in ((-40, 80), (-14, 104), (14, 104), (40, 80), (-58, 50), (58, 50), (0, 90)):
            if v.facing(x, y) > 0.2:
                cx, cy = v.surf(x, y, 8)
                d.thin([(cx - 6, cy - 2), (cx - 2, cy + 4), (cx + 5, cy + 3), (cx + 7, cy - 3)], k=0.9,
                       color='#5a4a42')


def moustache(d, v):
    m = [v.surf(x, y, 6) for x, y in ((-34, 62), (-30, 52), (-16, 48), (0, 50), (16, 48), (30, 52), (34, 62),
                                      (18, 56), (0, 55), (-18, 56))]
    d.shape(m, BEARD, 2.6)


def bust(d, yaw=24, e=None):
    e = e or e_('calm')
    v = parts.View(p, yaw)
    t = Torso(yaw * 0.6, W=190, neck=46, top=112, slope=30, depth=0.55, bottom=440)
    parts.neck(d, v)
    out = t.outline()
    d.shape(out, JACKET)
    # a stand collar and a fastening off-centre, both with an embroidered band
    d.band([t.pt(-50, 118), t.pt(-24, 138), t.pt(0, 142), t.pt(24, 138), t.pt(50, 118)], 18, None, 'cross', RED)
    d.band([t.pt(40, 136), t.pt(46, 260), t.pt(48, 440)], 18, None, 'cross', RED)
    for i in range(4):
        bx, by = t.pt(70, 190 + i * 60)
        d.circle(bx, by, 6, '#e8dcc0', w=2)
    # the apron's bib and straps
    d.shape([t.pt(-80, 330), t.pt(80, 330), t.pt(84, 440), t.pt(-84, 440)], APRON, n=2)
    for sd in (-1, 1):
        d.ink([t.pt(sd * 80, 330), t.pt(sd * 70, 220), t.pt(sd * 52, 122)], 7, color=APRON_D)
    # the towel over the near shoulder: white linen with a red woven end
    tw = [t.pt(110, 140), t.pt(170, 150), t.pt(190, 240), t.pt(176, 440), t.pt(116, 440), t.pt(128, 260)]
    d.shape(tw, '#fbf7ec', pattern=d.p_stripes('#d9cdb0', 18, 3, 90))
    with d.clipped(tw):
        d.band([t.pt(100, 300), t.pt(200, 300)], 30, None, 'rhomb', RED, n=2)
        d.band([t.pt(100, 336), t.pt(200, 336)], 12, None, 'teeth', RED, n=2)
    parts.head(d, p, yaw, e, under=beard, front=hair, extra=moustache)
    return v


HEIGHT = 1540


def ladle(d, x, y, ang=0):
    with d.g(x, y, 1, ang):
        d.shape([(-7, 0), (7, 0), (6, -300), (-6, -300)], '#b9b0a0', 2.6, n=2)
        d.shape([(-46, -300), (46, -300), (40, -340), (0, -356), (-40, -340)], '#cfc6b4', 2.8)
        d.thin([(-40, -306), (40, -306)], k=0.9)


def figure(d, e=None):
    """He laughs with the whole body: the head thrown back a little, one fist on the hip, the other hand raises the
    ladle high — a broad arc from the planted feet up through the chest to the ladle."""
    import fig
    e = e or e_('calm')
    yaw = 22
    v = parts.View(p, yaw)
    # legs: planted wide
    fig.leg(d, (-70, 760), (-90, 1060), (-100, 1380), TROUS, 130, 80)
    fig.leg(d, (76, 760), (104, 1060), (120, 1380), TROUS, 130, 80)
    fig.shoe(d, (-100, 1380), -1, '#2a2220', 96, 48)
    fig.shoe(d, (120, 1380), 1, '#2a2220', 96, 48)
    # jacket: a barrel
    jk = [(-46, 110), (-130, 132), (-196, 180), (-212, 300), (-200, 500), (-186, 760, 'c'), (192, 760, 'c'),
          (212, 500), (220, 300), (204, 180), (136, 130), (46, 108)]
    d.shape(jk, JACKET)
    d.band([(-50, 116), (-24, 136), (0, 140), (24, 136), (50, 116)], 18, None, 'cross', RED)
    d.band([(40, 134), (48, 300), (50, 520)], 18, None, 'cross', RED)
    for i in range(4):
        d.circle(74, 190 + i * 70, 6, '#e8dcc0', w=2)
    # the apron, long, with an ornament hem
    ap = [(-96, 300, 'c'), (100, 300, 'c'), (106, 520), (176, 560), (200, 1170), (-196, 1180), (-172, 560),
          (-104, 520)]
    d.shape(ap, APRON)
    for xx in (-90, 0, 90):
        d.thin([(xx * 0.9, 560), (xx * 1.1, 1150)], k=0.9, color=APRON_D)
    with d.clipped(ap):
        d.band([(-210, 1130), (0, 1138), (210, 1124)], 46, None, 'rhomb', '#f6f0e2', ground=APRON_D, step=46)
    d.ink(ap, closed=True)
    d.band([(-200, 540), (0, 548), (206, 540)], 16, None, 'stripe', APRON_D, ground=APRON_D)
    for sd in (-1, 1):
        d.ink([(sd * 96, 306), (sd * 80, 220), (sd * 56, 124)], 8, color=APRON_D)
    # the head, thrown back a little with laughter
    with d.g(0, 112, 1, 6):
        with d.g(0, -112):
            parts.neck(d, v)
            parts.head(d, p, yaw, e, under=beard, front=hair, extra=moustache)
    # the towel over the far shoulder
    tw = [(-120, 130), (-196, 150), (-216, 250), (-200, 520), (-150, 520), (-150, 260)]
    d.shape(tw, '#fbf7ec', pattern=d.p_stripes('#d9cdb0', 18, 3, 90))
    with d.clipped(tw):
        d.band([(-230, 470), (-130, 470)], 30, None, 'rhomb', RED, n=2)
        d.band([(-230, 506), (-130, 506)], 12, None, 'teeth', RED, n=2)
    # arms: the sleeves rolled up above the elbow, thick forearms. Fist on the hip:
    fig.arm(d, (-176, 200), (-262, 400), (-168, 560), JACKET, 96, 70, skin=SKIN_M, pose='fist', hand_s=1.6,
            flip=True, fore=SKIN_M, roll=(JACKET, RED), hand_ang=-60)
    # the ladle raised high
    ladle(d, 262, 0, 12)
    fig.arm(d, (186, 196), (300, 230), (270, 20), JACKET, 96, 70, skin=SKIN_M, pose='fist', hand_s=1.6,
            hand_ang=172, fore=SKIN_M, roll=(JACKET, RED))
    return v
