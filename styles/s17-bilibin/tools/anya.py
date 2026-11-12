"""Аня, about 20 — warm, trusting, dreamy. In this style: Mucha's girl — long chestnut hair in flowing locks that
end in curls, the lids a little lowered; a today's cream blouse with a red embroidered yoke, a mustard cardigan,
a blue skirt of small-flower print."""
import kit
import parts
from parts import P, expr, ribbon, strands, Torso
from kit import INK, RED, GOLD, CREAM, SKIN_SH

NAME = 'Аня'
HAIR = '#8a4a2a'
HAIR_D = '#5e2f1c'
BLOUSE = '#f3e9d2'
CARDI = '#c99a3c'
SKIRT = '#55708a'
HALO = dict(ring='#b9894a', field='#e8d6ae', ink='#8a4a2a')

p = P(cheek=61, temple=61, jaw=46, jaw_y=50, chin=84, chin_w=15, skull=67, forehead=62, brow_z=65, nose_z=80,
      nose_y=40, nose_w=9, lip_z=68, chin_z=60, mouth_y=58, mouth_w=16, lip='full', lip_col='#c25a4e',
      eye_x=28, eye_w=21, eye_h=9, iris=6.2, iris_col='#5a3a22', lashes=3, brow_y=-21, brow='arc', brow_w=0.85,
      blush=0.5)

CALM = dict(open=0.82, smile=0.35, look=(0, 0.5))


def e_(name):
    e = expr(name)
    if name == 'calm':
        e.update(CALM)
    return e


def hl():
    # parted on the far side; the hair sweeps across the forehead toward the near temple
    pts = []
    for x, y in ((-p.a(10) * 0.92, 10), (-p.a(-42) * 0.88, -42), (-30, -76), (-20, -84), (-4, -76), (22, -66),
                 (44, -54), (p.a(-34) * 0.9, -34), (p.a(10) * 0.93, 10)):
        pts.append((x, y, p.zs(x, y) + 2))
    return pts


def hair_back(d, v):
    """The mass behind: wider than the skull, falling past the shoulders, its edge waving."""
    bx = v.pt(0, 0, -30)[0]
    pts = [(bx - 70, -100), (bx - 96, -30), (bx - 104, 60), (bx - 118, 160), (bx - 112, 250), (bx - 124, 330),
           (bx - 80, 360), (bx - 40, 330), (bx + 10, 365), (bx + 60, 335), (bx + 110, 350), (bx + 124, 260),
           (bx + 116, 160), (bx + 108, 60), (bx + 100, -30), (bx + 70, -104), (bx, -134)]
    d.shape(pts, HAIR_D, 3)
    strands(d, [(bx - 90, -20), (bx - 110, 120), (bx - 104, 330)], [(bx + 92, -20), (bx + 116, 120), (bx + 100, 330)],
            8, color='#3d1d12', k=0.9)


def hair_front(d, v):
    """The cap, parted on the far side, then the locks that flow out of it over the temples and down in front of
    the shoulders, each ending in a curl."""
    pts = parts.shell(v, grow=16, y_side=18, hairline=hl(), y_back=18 + 120 * v.s)
    d.shape(pts, HAIR, 3)
    part = v.pt(-22, p.crown + 8, 30)
    with d.clipped(pts):
        strands(d, [part, v.pt(20, -100, 70), v.pt(66, -40, 40), v.pt(76, 10, 0)],
                [part, v.pt(-40, -90, 70), v.pt(-66, -40, 40), v.pt(-72, 10, 10)], 7, k=0.85, t0=0.05, t1=0.95)
    d.ink(pts, closed=True)
    # near side: two locks out of the mass above the ear, over the shoulder
    n0 = v.pt(50, -70, 40)
    ribbon(d, [n0, (n0[0] + 30, n0[1] + 50), (n0[0] + 36, n0[1] + 120), (n0[0] + 26, n0[1] + 200),
               (n0[0] + 46, n0[1] + 280), (n0[0] + 34, n0[1] + 350)], 40, 12, HAIR, inner=3, curl=-14, taper0=0.2)
    ribbon(d, [(n0[0] + 8, n0[1] + 30), (n0[0] + 40, n0[1] + 90), (n0[0] + 58, n0[1] + 180),
               (n0[0] + 88, n0[1] + 260)], 30, 9, HAIR, inner=2, curl=12, taper0=0.2)
    # far side: a lock out of the parting, framing the cheek
    f0 = v.pt(-34, -84, 50)
    ribbon(d, [f0, (f0[0] - 26, f0[1] + 30), (f0[0] - 32, f0[1] + 100), (f0[0] - 26, f0[1] + 180),
               (f0[0] - 46, f0[1] + 260), (f0[0] - 36, f0[1] + 330)], 32, 10, HAIR, inner=2, curl=14, taper0=0.25)


def bust(d, yaw=25, e=None, hand=False):
    e = e or e_('calm')
    v = parts.View(p, yaw)
    t = Torso(yaw * 0.55, W=134, neck=27, top=118, slope=48, depth=0.5, bottom=440)
    hair_back(d, v)
    parts.neck(d, v)
    out = t.outline()
    # the cardigan: the whole torso
    d.shape(out, CARDI, 3, pattern=d.p_herring('#a87c2a', 12, 1.2))
    # the blouse in the V of the cardigan, with an embroidered yoke along the neckline
    vl = [t.pt(-30, 116), t.pt(-40, 200), t.pt(-14, 330), t.pt(0, 440, 60)]
    vr = [t.pt(30, 116), t.pt(40, 200), t.pt(14, 330), t.pt(0, 440, 60)]
    blouse = vl + vr[::-1]
    d.shape(blouse, BLOUSE, 0)
    neckline = [t.pt(-28, 122), t.pt(-14, 144), t.pt(0, 150), t.pt(14, 144), t.pt(28, 122)]
    with d.clipped(blouse):
        d.band([t.pt(-48, 116), t.pt(-24, 156), t.pt(0, 166), t.pt(24, 156), t.pt(48, 116)], 22, None, 'cross', RED)
        d.band([t.pt(-4, 180), t.pt(-2, 300), t.pt(0, 440)], 14, None, 'rhomb', RED)
    d.ink(vl)
    d.ink(vr)
    # the cardigan's ribbed band along the opening
    for side in (-1, 1):
        rib = [t.pt(side * 34, 112), t.pt(side * 46, 200), t.pt(side * 20, 330), t.pt(side * 6, 440, 60)]
        d.band(rib, 14, None, 'stripe', '#a87c2a', ground=CARDI, step=8)
    for i in range(3):
        bx, by = t.pt(-28 + i * 6, 250 + i * 50)
    d.ink(neckline, d.THIN)
    parts.head(d, p, yaw, e, back=None, front=hair_front)
    if hand:
        # a hand at the collar, fingers resting on the lock (a dreamy gesture)
        parts.hand(d, 60, 300, ang=160, s=1.15, pose='rest', skin=p.skin)
    return v


HEIGHT = 1460      # 7.3 heads


def figure(d, e=None):
    """Full figure: she stands in a soft S — weight on her right leg, hip out, head tilted toward the raised hand
    that holds a lock at her collar; the other hand hangs with a bunch of field flowers."""
    import fig
    e = e or e_('calm')
    yaw = 20
    v = parts.View(p, yaw)
    tilt = -7
    # hair behind everything (it hangs from the tilted head)
    with d.g(0, 110, 1, tilt):
        with d.g(0, -110):
            hair_back(d, v)
    # legs under the skirt
    fig.leg(d, (-40, 700), (-38, 1000), (-30, 1290), SKIN_LEG, 80, 40)
    fig.leg(d, (45, 700), (60, 990), (98, 1270), SKIN_LEG, 80, 40)
    fig.shoe(d, (-30, 1290), -1, '#8a3a2a', 70, 38)
    fig.shoe(d, (98, 1270), 1, '#8a3a2a', 70, 38)
    # far arm, hanging, with the flowers
    fig.flowers(d, -168, 760, 1.0)
    fig.arm(d, (-104, 200), (-138, 460), (-150, 690), CARDI, 60, 44, d.p_herring('#a87c2a', 12, 1.2),
            cuff=(CARDI, '#a87c2a'), skin=p.skin, pose='fist', flip=True, hand_s=1.3)
    # the skirt
    fig.skirt(d, (-92, 500), (98, 494), (-175, 1075), (190, 1060), SKIRT, d.p_sprig('#e9d9b0', '#9fb06a', 40, 3.6),
              hem=('rhomb', RED, CREAM, 30), folds=4)
    # the torso: blouse, then the open cardigan over it
    torso = [(-30, 116), (-70, 140), (-108, 168), (-122, 220), (-106, 360), (-92, 520, 'c'), (96, 512, 'c'),
             (108, 360), (124, 214), (112, 162), (72, 134), (30, 112)]
    d.shape(torso, BLOUSE)
    with d.clipped(torso):
        d.band([(-50, 112), (-26, 156), (0, 168), (26, 154), (50, 108)], 22, None, 'cross', RED)
        d.band([(-2, 176), (-1, 340), (0, 520)], 14, None, 'rhomb', RED)
    for sd in (-1, 1):
        panel = [(sd * 30, 112), (sd * 72, 134), (sd * 110, 162), (sd * 124, 220), (sd * 108, 360),
                 (sd * 100, 545, 'c'), (sd * 40, 552, 'c'), (sd * 46, 360), (sd * 40, 210)]
        d.shape(panel, CARDI, pattern=d.p_herring('#a87c2a', 12, 1.2))
        d.band([(sd * 36, 116), (sd * 44, 220), (sd * 48, 360), (sd * 42, 550)], 13, None, 'stripe', '#a87c2a',
               ground=CARDI, step=8)
    # the head, tilted, on its neck
    with d.g(0, 110, 1, tilt):
        with d.g(0, -110):
            parts.neck(d, v)
            parts.head(d, p, yaw, e, front=hair_front)
    # near arm: raised, the hand at the collar holding the lock
    fig.arm(d, (108, 196), (146, 430), (92, 318), CARDI, 58, 42, d.p_herring('#a87c2a', 12, 1.2),
            cuff=(CARDI, '#a87c2a'), skin=p.skin, pose='rest', hand_ang=118, hand_s=1.25)
    return v


SKIN_LEG = '#ead2b4'
