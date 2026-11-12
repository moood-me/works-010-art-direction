"""Тим, about 8 — mischievous, curious. A round face, big eyes, a snub nose, freckles; red hair in tousled
locks; a red-and-cream striped T-shirt, blue shorts, knee socks with a knitted ornament band, sneakers; a
magnifying glass."""
import parts
from parts import P, expr, ribbon, strands, Torso
from kit import INK, RED, GOLD, CREAM, SKIN

NAME = 'Тим'
HAIR = '#b8552c'
HAIR_D = '#8a3a1c'
TEE = '#f2e8d2'
STRIPE = '#b0402e'
SHORTS = '#4f6f8f'
SOCK = '#efe6cf'
HALO = dict(ring='#4f6f8f', field='#e6dcbf', ink='#e1b85a')

p = P(crown=-104, chin=80, cheek=70, temple=68, jaw=60, jaw_y=48, chin_w=22, skull=74, forehead=68, brow_z=66,
      nose_y=36, nose_z=76, nose_w=10, nose='snub', lip_z=64, chin_z=58, mouth_y=54, mouth_w=16, lip='thin',
      lip_col='#c9705e', eye_x=29, eye_w=21, eye_h=10.5, iris=7.4, iris_col='#4a6a3a', brow_y=-20, brow='arc',
      brow_w=1.0, brow_col='#8a3a1c', ear_y=(-6, 34), blush=0.8, neck=26)
p.freckles = [(x * s, y) for s in (1, -1) for x, y in ((24, 22), (32, 18), (38, 25), (28, 28), (42, 18))]

CALM = dict(brow=3, tilt=-1, open=1.05, smile=0.6, wide=0.95, smirk=0.6, look=(-2, 0))


def e_(name):
    e = expr(name)
    if name == 'calm':
        e.update(CALM)
    return e


def hair(d, v):
    """A full rounded cap whose edge breaks into short rounded tufts, a cowlick on the crown, a fringe of three
    locks curling to the side."""
    hl = parts.hairline(p, top=-72, temple=-42, side_y=6)
    pts = parts.shell(v, grow=16, y_side=10, hairline=hl)
    nshell = len(pts) - len([q for q in hl if v.facing(q[0], q[1]) > 0.05])
    pts = parts.lobes(pts, 9, 13, 2, nshell - 3, sharp=0.4)
    d.shape(pts, HAIR, 3, n=4)
    with d.clipped(pts, n=4):
        c = v.pt(14, p.crown + 4, -10)
        strands(d, [c, v.pt(-50, -80, 60), v.pt(-74, -10, 30)], [c, v.pt(60, -80, 30), v.pt(76, 0, -10)], 7, k=0.8)
    r = v.pt(14, p.crown - 2, -10)
    ribbon(d, [r, (r[0] + 6, r[1] - 22), (r[0] + 22, r[1] - 30)], 16, 6, HAIR, inner=0, curl=7, taper0=0.5)
    for (x, w, dx, c) in ((-36, 28, -16, 7), (-8, 30, 4, -7), (22, 26, 18, -7)):
        r = v.surf(x, -82, 8)
        ribbon(d, [r, (r[0] + dx * 0.4, r[1] + 16), (r[0] + dx, r[1] + 30)], w, 8, HAIR, inner=1, curl=c,
               taper0=0.75)


def bust(d, yaw=24, e=None):
    e = e or e_('calm')
    v = parts.View(p, yaw)
    t = Torso(yaw * 0.6, W=118, neck=27, top=96, slope=30, depth=0.55, bottom=400)
    parts.neck(d, v)
    out = t.outline()
    d.shape(out, TEE, pattern=d.p_stripes(STRIPE, 26, 12, 90))
    d.ink(out, closed=True)
    d.band([t.pt(-30, 104), t.pt(-16, 126), t.pt(0, 132), t.pt(16, 126), t.pt(30, 104)], 12, None, 'stripe', STRIPE,
           ground=STRIPE)
    parts.head(d, p, yaw, e, front=hair)
    return v


HEIGHT = 1050


def magnifier(d, x, y, r=46, ang=0):
    with d.g(x, y, 1, ang):
        d.shape([(-8, r), (8, r), (10, r + 90), (-10, r + 90)], '#7a4a2a', 2.8, n=2)
        d.circle(0, 0, r, '#cfe0e0', w=6)
        d.raw('<circle cx="0" cy="0" r="%s" fill="none" stroke="#c99a3c" stroke-width="4"/>' % (r - 1))
        d.thin([(-r * 0.5, -r * 0.2), (-r * 0.3, -r * 0.5)], k=1.4, color='#fff')


def figure(d, e=None):
    """He leans forward on one leg, peering through the magnifying glass at something on the ground ahead,
    the other arm flung back for balance — one diagonal from the back heel to the lens."""
    import fig
    e = e or e_('calm')
    yaw = 30
    v = parts.View(p, yaw)
    # back arm, flung back
    fig.arm(d, (90, 170), (150, 300), (210, 380), TEE, 40, 32, d.p_stripes(STRIPE, 22, 10, 30), skin=p.skin,
            pose='open', hand_s=1.0)
    # legs: front leg bent, back leg straight on its toes
    fig.leg(d, (-30, 520), (-90, 700), (-100, 910), p.skin, 64, 40)
    fig.leg(d, (36, 520), (90, 720), (150, 900), p.skin, 64, 40)
    for kx, ky, ax, ay in ((-90, 700, -100, 910), (90, 720, 150, 900)):
        d.band([(kx + (ax - kx) * 0.45, ky + (ay - ky) * 0.45), (ax, ay)], 46, None, 'rhomb', RED, ground=SOCK,
               step=26)
    fig.shoe(d, (-100, 910), -1, '#4f6f8f', 72, 36, sole='#f2e8d2', laces='#f2e8d2')
    with d.g(150, 900, 1, 30):
        fig.shoe(d, (0, 0), 1, '#4f6f8f', 72, 36, sole='#f2e8d2', laces='#f2e8d2')
    # shorts
    d.shape([(-80, 430), (88, 420), (100, 520), (110, 600), (34, 610), (14, 560), (-6, 600), (-104, 590),
             (-96, 520)], SHORTS)
    d.thin([(4, 450), (8, 560)], k=0.9)
    # T-shirt: the torso leaning forward
    with d.g(0, 520, 1, -12):
        with d.g(0, -520):
            tee = [(-28, 104), (-74, 120), (-96, 160), (-90, 300), (-88, 470, 'c'), (92, 462, 'c'), (96, 300),
                   (98, 160), (76, 120), (28, 102)]
            d.shape(tee, TEE, pattern=d.p_stripes(STRIPE, 26, 12, 90))
            d.ink(tee, closed=True)
            d.band([(-30, 104), (-16, 124), (0, 130), (16, 124), (30, 104)], 12, None, 'stripe', STRIPE,
                   ground=STRIPE)
            with d.g(-10, 104, 1, -6):
                with d.g(0, -104):
                    parts.neck(d, v)
                    parts.head(d, p, yaw, e, front=hair)
            # front arm stretched forward with the lens before his eye
            magnifier(d, -170, 120, 44, -20)
            fig.arm(d, (-70, 170), (-120, 290), (-160, 220), TEE, 40, 32, d.p_stripes(STRIPE, 22, 10, 30),
                    skin=p.skin, pose='fist', hand_s=1.0, hand_ang=170)
    return v
