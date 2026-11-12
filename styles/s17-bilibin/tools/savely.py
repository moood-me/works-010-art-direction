"""Савелий Петрович, about 70, a watchmaker — grumpy outside, kind inside. A bald dome, a white fringe round the
back, bushy white brows knitted, a white moustache, round glasses; a white shirt,
a knitted olive waistcoat with a folk rhomb pattern, a red bow tie; a pocket watch in his palm."""
import parts
from parts import P, expr, ribbon, strands, Torso
from kit import INK, RED, GOLD, CREAM, SKIN

NAME = 'Савелий Петрович'
WHITE = '#f1ece0'
WHITE_L = '#b9b0a0'
SHIRT = '#efe9da'
VEST = '#5d6b3a'
VEST_P = '#c9b77a'
TROUS = '#6b6660'
HALO = dict(ring='#5d6b3a', field='#e3dcbf', ink='#c99a3c')
SKIN_O = '#ecc9a8'

p = P(cheek=66, temple=63, jaw=58, jaw_y=58, chin=92, chin_w=20, skull=70, forehead=66, brow_z=70, nose_z=92,
      nose_y=46, nose_w=13, nose='big', lip_z=68, chin_z=64, mouth_y=67, mouth_w=19, lip='none',
      eye_x=29, eye_w=17, eye_h=7, iris=5.0, iris_col='#3d4a52', brow_y=-18, brow='bushy', brow_w=1.25,
      brow_col='#e9e4d8', wrinkles=3, under=2, skin=SKIN_O, ear_y=(-10, 44), blush=0.6)

CALM = dict(brow=-1, tilt=-3, open=0.85, smile=-0.25, look=(-1, 1))


def e_(name):
    e = expr(name)
    if name == 'calm':
        e.update(CALM)
    if name == 'joy':
        e.update(open=0.2, smile=0.9, mouth=0.35)
    return e


def fringe(d, v):
    for sd in ((1, -1) if v.yaw < 20 else (1,)):
        pts = parts.side_hair(v, -46, 40, 9, 0.25 if sd > 0 else 0.25, sd, bumps=5)
        d.shape(pts, WHITE, 2.6)
        strands(d, pts[1:8], pts[-1:-8:-1], 3, color=WHITE_L, k=0.8)


def extra(d, v):
    """Moustache and glasses."""
    # moustache: a white mass under the nose, its ends drooping (grumpy), strands in grey
    m = []
    for x, y in ((-30, 66), (-34, 60), (-24, 52), (-8, 50), (0, 52), (8, 50), (24, 52), (34, 60), (30, 66),
                 (16, 60), (0, 60), (-16, 60)):
        m.append(v.surf(x, y, 4))
    d.shape(m, WHITE, 2.4)
    for x in (-18, -8, 8, 18):
        d.thin([v.surf(x, 53, 5), v.surf(x * 1.3, 61, 5)], k=0.6, color=WHITE_L)
    # round glasses
    for sd in (1, -1):
        f = v.facing(p.eye_x * sd, 0)
        if f < 0.25:
            continue
        cx, cy = v.surf(p.eye_x * sd, 2, 8)
        rx, ry = 19 * (0.3 + 0.7 * f), 18
        d.raw('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#fff" fill-opacity="0.12" stroke="#7a5a2a" '
              'stroke-width="%.2f"/>' % (cx, cy, rx, ry, 3.0 * d.lw))
    l, r = v.surf(-p.eye_x + 17, -2, 10), v.surf(p.eye_x - 17, -2, 10)
    if v.yaw < 70:
        d.ink([l, ((l[0] + r[0]) / 2, l[1] - 4), r], 2.6, color='#7a5a2a')
    temple = v.surf(p.eye_x + 19, -2, 6)
    if v.facing(p.eye_x + 19, 0) > 0.1:
        d.ink([temple, v.pt(p.a(0) * 0.98, -2, -10)], 2.6, color='#7a5a2a')


def bust(d, yaw=28, e=None):
    e = e or e_('calm')
    v = parts.View(p, yaw)
    t = Torso(yaw * 0.6, W=160, neck=36, top=120, slope=34, depth=0.55, bottom=440)
    parts.neck(d, v)
    out = t.outline()
    d.shape(out, SHIRT)
    # the waistcoat: from the shoulders down, open in a V at the chest
    vest_l = [t.pt(-60, 132), t.pt(-118, 150), t.pt(-136, 200), t.pt(-128, 300), t.pt(-126, 440), t.pt(-2, 440, 70),
              t.pt(-6, 280), t.pt(-38, 176)]
    vest_r = [t.pt(60, 132), t.pt(118, 150), t.pt(136, 200), t.pt(128, 300), t.pt(126, 440), t.pt(2, 440, 70),
              t.pt(6, 280), t.pt(38, 176)]
    for vv in (vest_l, vest_r):
        d.shape(vv, VEST, pattern=d.p_rhombs(VEST_P, 22, 1.6))
        d.band([vv[0], vv[-1], vv[-2], vv[-3]], 12, None, 'dots', VEST_P, ground='#4a5530')
    # buttons
    for i in range(3):
        bx, by = t.pt(4, 320 + i * 40)
        d.circle(bx, by, 5, '#c99a3c', w=1.8)
    # collar and bow tie
    for sd in (-1, 1):
        d.shape([t.pt(sd * 30, 118), t.pt(sd * 44, 140), t.pt(sd * 12, 162), t.pt(sd * 4, 140)], SHIRT, 2.4)
    bx, by = t.pt(0, 150)
    d.shape([(bx, by), (bx - 26, by - 14), (bx - 28, by + 14)], RED, 2.4, n=2)
    d.shape([(bx, by), (bx + 26, by - 14), (bx + 28, by + 14)], RED, 2.4, n=2)
    d.circle(bx, by, 6, RED, w=2.4)
    parts.head(d, p, yaw, e, front=fringe, extra=extra)
    return v


HEIGHT = 1300


def figure(d, e=None):
    """He stands stooped, the line of the back one long curve forward: the head pushed out over the watch in his
    palm, the other hand behind his back."""
    import fig
    e = e or e_('calm')
    yaw = 30
    v = parts.View(p, yaw)
    # legs: knees a little bent
    fig.leg(d, (-50, 660), (-52, 920), (-40, 1150), TROUS, 96, 64)
    fig.leg(d, (52, 660), (74, 910), (74, 1150), TROUS, 96, 64)
    fig.shoe(d, (-40, 1150), -1, '#3a2a22', 82, 40)
    fig.shoe(d, (74, 1150), 1, '#3a2a22', 82, 40)
    # the upper body leans forward from the hips
    with d.g(0, 660, 1, -7):
        with d.g(0, -660):
            fig.arm(d, (-104, 210), (-128, 440), (-40, 560), SHIRT, 58, 44)
            shirt = [(-36, 120), (-92, 140), (-128, 182), (-140, 260), (-132, 420), (-124, 560), (-110, 680, 'c'),
                     (116, 680, 'c'), (136, 560), (146, 400), (138, 230), (100, 146), (40, 116)]
            d.shape(shirt, SHIRT)
            vest = [[(-40, 128), (-94, 146), (-126, 190), (-136, 270), (-128, 430), (-122, 560), (-114, 664, 'c'),
                     (-4, 676, 'c'), (-2, 400), (-26, 200)],
                    [(44, 126), (98, 148), (134, 220), (146, 400), (136, 560), (118, 662, 'c'), (4, 676, 'c'),
                     (4, 400), (30, 200)]]
            for vv in vest:
                d.shape(vv, VEST, pattern=d.p_rhombs(VEST_P, 22, 1.6))
                d.band(vv[-3:][::-1] + [vv[0]], 11, None, 'dots', VEST_P, ground='#4a5530')
            for i in range(4):
                d.circle(4, 420 + i * 60, 5, GOLD, w=1.8)
            for sd in (-1, 1):
                d.shape([(sd * 30, 118), (sd * 46, 142), (sd * 12, 164), (sd * 4, 140)], SHIRT, 2.4)
            d.shape([(0, 150), (-26, 136), (-28, 164)], RED, 2.4, n=2)
            d.shape([(0, 150), (26, 136), (28, 164)], RED, 2.4, n=2)
            d.circle(0, 150, 6, RED, w=2.4)
            # the head pushed forward and bowed over the watch
            with d.g(-16, 112, 1, -10):
                with d.g(0, -112):
                    parts.neck(d, v)
                    parts.head(d, p, yaw, e, front=fringe, extra=extra)
            # the watch on its chain, in the open palm in front of the chest
            wx, wy = -36, 392
            d.ink([(4, 470), (40, 520), (wx + 30, wy + 30), (wx + 8, wy + 20)], 2.4, color=GOLD)
            fig.arm(d, (122, 214), (156, 452), (40, 420), SHIRT, 60, 46, skin=SKIN_O, pose='open', hand_ang=96,
                    hand_s=1.3)
            d.circle(wx, wy, 28, '#e9d7a0', w=3)
            d.circle(wx, wy, 22, '#f8f0dc', w=1.6)
            d.ink([(wx, wy), (wx, wy - 15)], 2.4)
            d.ink([(wx, wy), (wx + 11, wy + 4)], 2.4)
            d.circle(wx, wy - 32, 5, '#e9d7a0', w=2)
    return v
