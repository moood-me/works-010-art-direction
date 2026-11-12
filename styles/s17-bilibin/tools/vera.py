"""Вера, about 40 — strict, clever, tired. A long narrow face, straight brows, narrow eyes with a line under them,
thin lips; dark hair pulled back into a low knot, a grey lock at the temple; narrow glasses; a dark teal dress
and over the shoulders a black shawl printed with roses (the Pavlovo Posad shawl, worn today as it was then);
a folder held to the chest."""
import parts
from parts import P, expr, ribbon, strands, Torso
from kit import INK, RED, GOLD, CREAM, SKIN

NAME = 'Вера'
HAIR = '#2e2420'
GREY = '#8f8780'
DRESS = '#2f5a5a'
SHAWL = '#231d1b'
ROSE = '#b8402f'
LEAF = '#5d6b3a'
HALO = dict(ring='#2f5a5a', field='#e2dcc4', ink='#b8402f')

p = P(cheek=60, temple=60, jaw=50, jaw_y=58, chin=96, chin_w=15, skull=67, forehead=64, brow_z=68, nose_z=86,
      nose_y=48, nose_w=10, nose='straight', lip_z=68, chin_z=64, mouth_y=70, mouth_w=17, lip='thin',
      lip_col='#a8554c', eye_x=28, eye_w=19, eye_h=7, iris=5.4, iris_col='#3a3a3a', lashes=1, under=1,
      brow_y=-17, brow='straight', brow_w=0.9, brow_col='#2e2420', ear_y=(-6, 40), skin='#efd6bb', neck=29)

CALM = dict(brow=-1, tilt=-1.5, open=0.8, smile=-0.1, wide=0.95, look=(-1, 0))


def e_(name):
    e = expr(name)
    if name == 'calm':
        e.update(CALM)
    return e


def hl():
    return parts.hairline(p, top=-76, temple=-46, side_y=12)


def knot(d, v):
    """The low knot at the back of the head (behind it in front and three-quarter views)."""
    kx, ky = v.pt(0, 24, -p.bb(24) - 26)
    if v.yaw < 10:
        return
    d.shape([(kx - 30, ky - 30), (kx + 26, ky - 34), (kx + 40, ky + 4), (kx + 20, ky + 34), (kx - 24, ky + 30),
             (kx - 36, ky)], HAIR, 3)
    for r in (22, 12):
        d.thin([(kx - r, ky), (kx, ky - r), (kx + r, ky), (kx, ky + r * 0.8)], k=0.9, color='#7a6a60')


def hair(d, v):
    pts = parts.shell(v, grow=8, y_side=20, hairline=hl(), y_back=36)
    d.shape(pts, HAIR, 3)
    with d.clipped(pts):
        # combed straight back: strands from the hairline to the knot
        strands(d, [v.surf(-50, -60, 4), v.pt(-30, -116, 10), v.pt(30, -112, -40), v.pt(60, 30, -60)],
                [v.surf(50, -60, 4), v.pt(70, -60, -10), v.pt(72, 10, -40), v.pt(60, 34, -60)], 8, color='#6a5a52',
                k=0.8)
    d.ink(pts, closed=True)
    # one grey lock at the near temple
    r = v.surf(40, -62, 6)
    if v.facing(40, -62) > 0.2:
        ribbon(d, [r, (r[0] + 20, r[1] + 10), (r[0] + 36, r[1] + 34)], 12, 6, GREY, inner=0, taper0=0.8)


def extra(d, v):
    """Narrow glasses with thin dark rims."""
    for sd in (1, -1):
        f = v.facing(p.eye_x * sd, 0)
        if f < 0.25:
            continue
        cx, cy = v.surf(p.eye_x * sd, 1, 8)
        w, h = 22 * (0.3 + 0.7 * f), 13
        d.ink([(cx - w, cy - h, 'c'), (cx + w, cy - h, 'c'), (cx + w * 0.9, cy + h, 'c'), (cx - w * 0.9, cy + h, 'c')],
              2.6, closed=True, color='#3a2a22', n=2)
    if v.yaw < 70:
        l, r = v.surf(-p.eye_x + 20, -3, 10), v.surf(p.eye_x - 20, -3, 10)
        d.ink([l, ((l[0] + r[0]) / 2, l[1] - 3), r], 2.4, color='#3a2a22')
    if v.facing(p.eye_x + 22, 0) > 0.1:
        d.ink([v.surf(p.eye_x + 22, -6, 6), v.pt(p.a(0) * 0.98, -4, -12)], 2.4, color='#3a2a22')


def shawl_pattern(d):
    """The printed shawl: a black ground with big red roses and green leaves, scattered (a pattern tile)."""
    key = ('shawl',)
    if key in d._ids:
        return d._ids[key]
    body = ''
    for cx, cy, r in ((30, 30, 15), (95, 85, 13), (90, 20, 8), (25, 95, 9)):
        for i in range(2):
            a0 = i * 120
            body += ('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="#5d6b3a" transform="rotate(%d %d %d)"/>'
                     % (cx + r + 6, cy + 4, r * 0.8, r * 0.35, a0 + 20, cx, cy))
        body += '<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (cx, cy, r, ROSE)
        for k in (0.75, 0.5, 0.25):
            body += ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#7a2418" stroke-width="1.5" '
                     'stroke-dasharray="%.1f %.1f"/>' % (cx + r * 0.08, cy - r * 0.05, r * k, r * k * 2.2, r * k * 1.1))
    pid = d._pat(key, 120, 120, body)
    return pid


def bust(d, yaw=-26, e=None):
    e = e or e_('calm')
    v = parts.View(p, abs(yaw))
    flip = yaw < 0
    with d.g(0, 0, 1, 0, flip):
        t = Torso(abs(yaw) * 0.6, W=126, neck=29, top=118, slope=44, depth=0.5, bottom=440)
        parts.neck(d, v)
        out = t.outline()
        d.shape(out, DRESS)
        # a round neckline
        d.ink([t.pt(-34, 120), t.pt(-20, 146), t.pt(0, 152), t.pt(20, 146), t.pt(34, 120)], d.THIN)
        # the shawl: over both shoulders, its two ends crossing low on the chest, a fringe at the edge
        sh = [t.pt(-60, 128), t.pt(-130, 160), t.pt(-140, 260), t.pt(-110, 440), t.pt(-10, 440, 70), t.pt(30, 330),
              t.pt(80, 260), t.pt(140, 250), t.pt(132, 160), t.pt(60, 128), t.pt(40, 200), t.pt(0, 260),
              t.pt(-30, 220)]
        d.shape(sh, SHAWL, pattern=shawl_pattern(d))
        d.band([t.pt(60, 130), t.pt(40, 200), t.pt(0, 262), t.pt(-24, 226), t.pt(-58, 132)], 12, None, 'teeth', ROSE,
               ground=SHAWL)
        parts.head(d, p, abs(yaw), e, back=knot, front=hair, extra=extra)
    return v


HEIGHT = 1480


def folder(d, x, y, ang=0):
    with d.g(x, y, 1, ang):
        d.shape([(-70, -100, 'c'), (70, -100, 'c'), (70, 100, 'c'), (-70, 100, 'c')], '#8a3a2a', n=2)
        d.shape([(-60, -90, 'c'), (64, -90, 'c'), (64, 94, 'c'), (-60, 94, 'c')], '#f3ead6', 1.6, n=2)
        d.shape([(-70, -100, 'c'), (70, -100, 'c'), (70, 100, 'c'), (-70, 100, 'c')], '#8a3a2a', n=2)
        d.band([(-50, -60), (50, -60)], 16, None, 'rhomb', GOLD, ground='#8a3a2a', n=2)


def figure(d, e=None):
    """She stands straight and still, weight on one leg, the folder held to her chest with both arms; the head
    a little raised, the look down her nose — strictness; the shoulders slightly fallen — tiredness."""
    import fig
    e = e or e_('calm')
    yaw = 26
    v = parts.View(p, yaw)
    with d.g(0, 0, 1, 0, True):
        # legs under the long dress: only the ankles and shoes show
        fig.leg(d, (-30, 700), (-30, 1000), (-34, 1320), '#3a3030', 70, 38)
        fig.leg(d, (36, 700), (44, 1000), (70, 1310), '#3a3030', 70, 38)
        fig.shoe(d, (-34, 1320), -1, '#2a2220', 70, 36)
        fig.shoe(d, (70, 1310), 1, '#2a2220', 70, 36)
        dress = [(-32, 118), (-96, 140), (-120, 180), (-114, 330), (-92, 520), (-120, 800), (-150, 1290, 'c'),
                 (170, 1280, 'c'), (130, 800), (100, 510), (120, 330), (126, 180), (100, 140), (32, 116)]
        d.shape(dress, DRESS)
        for xx in (-60, 10, 80):
            d.thin([(xx * 0.7, 560), (xx * 1.1, 900), (xx * 1.3, 1270)], k=0.9)
        d.band([(-150, 1262), (0, 1270), (170, 1254)], 26, None, 'teeth', ROSE, ground=DRESS)
        # the shawl over the shoulders, its point down the back, ends hanging in front
        sh = [(-40, 116), (-110, 144), (-140, 220), (-150, 400), (-130, 560), (-90, 600), (-60, 470), (-40, 300),
              (40, 300), (64, 470), (100, 600), (140, 560), (156, 400), (146, 220), (110, 144), (40, 114),
              (0, 160)]
        d.shape(sh, SHAWL, pattern=shawl_pattern(d))
        for side in (-1, 1):
            xx = -110 if side < 0 else 120
            d.band([(xx - 24 * side, 590), (xx + 24 * side, 560)], 14, None, 'teeth', ROSE, ground=SHAWL, n=2)
        with d.g(4, 110, 1, 4):
            with d.g(0, -110):
                parts.neck(d, v)
                parts.head(d, p, yaw, e, back=knot, front=hair, extra=extra)
        # both forearms across the chest holding the folder upright
        folder(d, -10, 370, -8)
        fig.arm(d, (-110, 196), (-130, 420), (20, 420), DRESS, 54, 40, skin=p.skin, pose='rest', hand_ang=-80,
                hand_s=1.25)
        fig.arm(d, (118, 196), (136, 430), (-20, 360), DRESS, 54, 40, skin=p.skin, pose='rest', hand_ang=96,
                hand_s=1.25)
    return v
