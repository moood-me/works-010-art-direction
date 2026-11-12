"""Кира, about 15 — prickly, closed, defiant; vulnerable underneath. A longer face than a child's, smaller eyes,
a low straight brow, the mouth pressed into a crooked half-smirk; short choppy dark hair, a long fringe falling
across the forehead to the far side (both eyes stay visible); an oversized plum hoodie printed with a band of
folk birds-and-rhombs ornament (a print on a today's hoodie), lime headphones round the neck, charcoal narrow
trousers, heavy boots with lime laces."""
import parts
from parts import P, expr, ribbon, strands, Torso
from kit import INK, RED, GOLD, CREAM, SKIN

NAME = 'Кира'
HAIR = '#1d1820'
HOODIE = '#4a2c46'
HOODIE_D = '#33202f'
PRINT = '#c8b8c4'
TROUS = '#34333a'
LIME = '#c6d93a'
HALO = dict(ring='#33202f', field='#ddd6c4', ink='#c6d93a')

p = P(crown=-110, chin=90, cheek=58, temple=59, jaw=45, jaw_y=56, chin_w=14, skull=66, forehead=62, brow_z=66,
      nose_y=44, nose_z=82, nose_w=9, lip_z=66, chin_z=60, mouth_y=64, mouth_w=15, lip='full', lip_col='#b5716c',
      eye_x=27, eye_w=17, eye_h=7.5, iris=5.6, iris_col='#3b3040', lashes=2, brow_y=-15, brow='straight',
      brow_w=1.05, brow_col=HAIR, ear_y=(-6, 36), skin='#efd8c2', neck=25)

# resting face: the brow low, the look from under it sideways, the mouth pressed and pulled to one side
CALM = dict(brow=-3, tilt=-2, open=0.78, smile=-0.05, wide=0.9, smirk=0.7, look=(-4, -1))


def e_(name):
    e = expr(name)
    if name == 'calm':
        e.update(CALM)
    if name == 'joy':
        # she doesn't smile openly: a crooked half-smile, the eyes still guarded
        e.update(open=0.7, smile=0.35, mouth=0.0, smirk=1.0, cheeks=0, brow=0, tilt=0, look=(-3, 0))
    if name == 'anger':
        e.update(mouth=0.0, smile=-0.6, open=0.8, look=(-2, -1))
    return e


def hl():
    return parts.hairline(p, top=-74, temple=-44, side_y=8)


def hair(d, v):
    """Short choppy hair: a cap whose edge breaks into pointed uneven locks; the fringe a long sharp sweep across
    the forehead to the far side, ending at the far cheekbone."""
    pts = parts.shell(v, grow=14, y_side=34, hairline=hl(), y_back=40)
    nshell = len(pts) - len([q for q in hl() if v.facing(q[0], q[1]) > 0.05])
    pts = parts.lobes(pts, 8, 9, 0, nshell - 1, sharp=2.0)
    d.shape(pts, HAIR, 3, n=4)
    with d.clipped(pts, n=4):
        c = v.pt(20, p.crown + 6, -20)
        strands(d, [c, v.pt(-50, -80, 60), v.pt(-70, 0, 30)], [c, v.pt(66, -60, 0), v.pt(70, 30, -40)], 6,
                color='#5a4a5a', k=0.8)
    # the fringe: three long pointed locks from the crown over the forehead, toward the far side
    for (x0, y0, x1, y1, w) in ((30, -84, -44, -6, 44), (6, -86, -60, 14, 34), (50, -74, -16, -24, 30)):
        r = v.surf(x0, y0, 10)
        t = v.surf(x1, y1, 10)
        m = v.surf((x0 + x1) / 2 + 6, (y0 + y1) / 2 - 10, 14)
        ribbon(d, [r, m, t], w, 3, HAIR, inner=1, taper0=0.8, inner_col='#5a4a5a')


def headphones(d, t, front=True):
    """Lime headphones round the neck: a band behind, two cups on the collarbones."""
    if not front:
        d.ink([t.pt(-62, 150), t.pt(-50, 110, -40), t.pt(0, 100, -50), t.pt(50, 110, -40), t.pt(62, 150)], 9,
              color='#2a2a2a')
        return
    for sd in (-1, 1):
        cx, cy = t.pt(sd * 56, 156)
        d.shape([(cx - 24, cy - 12), (cx + 24, cy - 12), (cx + 26, cy + 18), (cx - 26, cy + 18)], LIME, 3, n=4)
        d.shape([(cx - 15, cy - 4), (cx + 15, cy - 4), (cx + 15, cy + 10), (cx - 15, cy + 10)], '#2a2a2a', 2, n=4)


def bust(d, yaw=-30, e=None):
    e = e or e_('calm')
    v = parts.View(p, abs(yaw))
    with d.g(0, 0, 1, 0, yaw < 0):
        t = Torso(abs(yaw) * 0.5, W=118, neck=25, top=118, slope=26, depth=0.6, bottom=440, drop=10)
        parts.neck(d, v)
        out = t.outline()
        d.shape(out, HOODIE)
        # the hood lying round the neck
        hood = [t.pt(-82, 128), t.pt(-50, 112, -30), t.pt(0, 104, -50), t.pt(50, 112, -30), t.pt(82, 128),
                t.pt(56, 160), t.pt(0, 172), t.pt(-56, 160)]
        d.shape(hood, HOODIE_D)
        d.ink([t.pt(-40, 146), t.pt(0, 156), t.pt(40, 146)], d.THIN)
        # strings
        for sd in (-1, 1):
            d.ink([t.pt(sd * 16, 168), t.pt(sd * 20, 240), t.pt(sd * 14, 290)], 3, color='#d8d0c8')
        # the printed ornament band across the chest
        with d.clipped(out):
            d.band([t.pt(-140, 330), t.pt(0, 336), t.pt(140, 330)], 46, None, 'rhomb', PRINT, ground=HOODIE_D,
                   step=48)
            d.band([t.pt(-140, 368), t.pt(0, 374), t.pt(140, 368)], 12, None, 'teeth', PRINT, ground=HOODIE_D)
        d.ink(out, closed=True)
        headphones(d, t)
        with d.g(-4, 104, 1, 7):
            with d.g(0, -104):
                parts.head(d, p, abs(yaw), e, front=hair)
    return v


HEIGHT = 1420


def boot(d, ankle, s=1):
    import fig
    fig.shoe(d, ankle, s, '#26242a', 86, 48, sole='#4a4650', laces=LIME, boot=50)


def figure(d, e=None):
    """She slouches: the shoulders rounded forward, the head down, the look from under the brow sideways; the
    arms crossed tight on the chest (closed), the weight on one hip, one boot turned in — awkward, not settled."""
    import fig
    e = e or e_('calm')
    yaw = 30
    v = parts.View(p, yaw)
    with d.g(0, 0, 1, 0, True):
        # legs: narrow, one knee turned in
        fig.leg(d, (-34, 690), (-30, 1000), (-40, 1290), TROUS, 76, 46)
        fig.leg(d, (36, 690), (8, 990), (40, 1290), TROUS, 76, 46)
        boot(d, (-40, 1290), -1)
        boot(d, (40, 1290), 1)
        # the hoodie: oversized, hanging to the hips, the shoulders slumped forward
        hd = [(-30, 116), (-80, 136), (-118, 170), (-138, 240), (-140, 360), (-130, 520), (-126, 740, 'c'),
              (126, 732, 'c'), (130, 520), (140, 360), (136, 236), (114, 166), (80, 132), (30, 114)]
        d.shape(hd, HOODIE)
        d.band([(-128, 712), (0, 720), (128, 706)], 30, None, 'stripe', HOODIE_D, ground=HOODIE_D, step=10)
        with d.clipped(hd):
            d.band([(-150, 350), (0, 356), (150, 350)], 46, None, 'rhomb', PRINT, ground=HOODIE_D, step=48)
        d.ink(hd, closed=True)
        hood = [(-82, 128), (-50, 104), (0, 96), (50, 104), (82, 128), (56, 158), (0, 168), (-56, 158)]
        d.shape(hood, HOODIE_D)
        # head down, the far eye looking out from under the fringe
        with d.g(-6, 100, 1, 10):
            with d.g(0, -100):
                parts.neck(d, v)
                parts.head(d, p, yaw, e, front=hair)
        for sd in (-1, 1):
            cx, cy = sd * 56, 152
            d.shape([(cx - 24, cy - 12), (cx + 24, cy - 12), (cx + 26, cy + 18), (cx - 26, cy + 18)], LIME, 3, n=4)
        # crossed arms: the far forearm under, the near over; sleeves pulled down to the knuckles
        fig.arm(d, (-120, 200), (-136, 440), (70, 400), HOODIE, 66, 54, skin=p.skin, pose='fist', hand_s=1.15,
                hand_ang=-100)
        fig.arm(d, (124, 196), (136, 450), (-70, 430), HOODIE, 66, 54, skin=p.skin, pose='fist', hand_s=1.15,
                hand_ang=100, cuff=(HOODIE_D, HOODIE_D))
    return v
