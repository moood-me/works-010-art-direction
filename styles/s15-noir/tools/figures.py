"""The six bodies in a three-quarter pose (facing the viewer's left, lit from the left), feet on y=0.
Each body function returns dict(body=svg under the head, over=svg over the head, neck=(x, y), rot=head tilt, hs=head scale)."""
from noir import *
from head import head, neck_q, EXPR
from cast import CAST, REST

LIT = (-7, -3)


def hand(x, y, rot, s, kind, skin, flip=False, rim=None):
    """Angular hands: the fingers are one wedge, the thumb apart. Wrist at (0,0), fingers down, thumb to the left."""
    K = dict(
        rest=[(-7, -2), (7, -2), (10, 13), (8, 29), (3, 39), (-3, 37), (-6, 25), (-10, 27), (-14, 18), (-9, 9)],
        fist=[(-8, -2), (8, -2), (12, 11), (10, 23), (-1, 27), (-10, 22), (-14, 14), (-10, 7)],
        open=[(-8, -2), (8, -2), (13, 14), (20, 33), (15, 36), (9, 23), (10, 42), (4.5, 43), (3, 25), (0, 42), (-5.5, 41), (-5, 23), (-10, 34), (-15, 32), (-11, 15),
              (-20, 14), (-24, 8), (-12, 5)],
        grip=[(-8, -2), (8, -2), (13, 10), (12, 22), (4, 27), (-8, 24), (-13, 16), (-8, 12), (-12, 6)],
        point=[(-7, -2), (7, -2), (10, 12), (8, 24), (2, 26), (0, 44), (-5, 44), (-6, 24), (-12, 22), (-14, 12), (-9, 7)],
    )[kind]
    sh = {'open': [[(4, -2), (9, 14), (12, 30), (30, 40), (30, -2)]], 'rest': [[(2, -2), (5, 14), (3, 40), (14, 40), (14, -2)]],
          'fist': [[(-12, 16), (0, 14), (10, 17), (12, 30), (-12, 30)]], 'grip': [[(-12, 15), (0, 13), (13, 14), (12, 30), (-12, 30)]],
          'point': [[(2, -2), (4, 22), (-2, 26), (10, 28), (14, -2)]]}[kind]
    return g(form(K, skin, lit=(-2.5, -1.5), shadows=sh, rim=rim), x, y, s, flip=flip, rot=rot)


def shoe(x, y, L, h, col, heel=0, flip=False):
    """A shoe pointing left; (x, y) is the ankle's bottom centre on the ground line."""
    pts = [(-h * 0.5, -h), (h * 0.5, -h), (h * 0.6, 0), (-L * 0.5, 0), (-L, 0), (-L, -h * 0.25), (-L * 0.55, -h * 0.55)]
    s = form(pts, col, lit=(-3, -3), shadows=[[(0, -h), (2, 0), (h, 0), (h, -h)]])
    if heel:
        s += shape([(h * 0.1, 0), (h * 0.6, 0), (h * 0.5, heel), (h * 0.25, heel)], BLACK)
    return g(s, x, y - heel, 1, flip=flip)


# ---------------- Аня ----------------
def anya(pose=None):
    p = CAST['anya']; sk = p['skin']; card = '#c9982f'; dress = '#4b6788'; s = []
    # legs: the weight on the near one, the far foot set back on its toe
    s.append(limb([(-10, -260), (-18, -150), (-14, -96), (-22, -28)], [30, 21, 23, 12], sk, lit=(-6, -2)))
    s.append(shoe(-20, 0, 44, 24, '#7d3528'))
    s.append(limb([(20, -260), (18, -150), (22, -96), (12, -28)], [32, 22, 25, 13], sk, lit=(-7, -2), shadows=[[(18, -260), (22, -150), (26, -96), (14, -28), (40, -28), (40, -260)]]))
    s.append(shoe(14, 0, 46, 25, '#7d3528'))
    # the skirt swung by the hip
    s.append(form([(-24, -446), (26, -446), (46, -396), (74, -226), (20, -216), (-54, -228), (-36, -396)], dress, lit=LIT,
                  shadows=[[(8, -446), (22, -396), (10, -320), (34, -216), (90, -216), (60, -446)], [(-28, -228), (-20, -340), (-12, -228)]]))
    # the cardigan: sloping shoulders, the waist
    s.append(form([(-40, -548), (-16, -568), (26, -570), (54, -548), (52, -500), (34, -440), (38, -420), (-28, -420), (-24, -440), (-38, -500)], card, lit=LIT,
                  shadows=[[(20, -574), (28, -520), (14, -470), (22, -420), (60, -420), (60, -574)], [(-36, -500), (-16, -492), (4, -500), (-16, -486)]],
                  under=[([(-18, -570), (24, -572), (2, -506)], sk), ([(-10, -536), (12, -540), (2, -506)], dress)]))
    # far arm behind the back; near arm: the hand at the chest with a flower
    s.append(limb([(-32, -548), (-40, -486), (-30, -440)], [20, 18, 14], card, lit=(-5, -2)))
    s.append(limb([(46, -550), (60, -478), (10, -500)], [25, 22, 16], card, lit=(-6, -3), shadows=[[(50, -560), (66, -470), (10, -490), (10, -484), (80, -470), (80, -560)]]))
    s.append(line([(4, -506), (-8, -548)], '#5d7a4a', 2.4))
    s.append(''.join(g(shape([(0, 0), (-4, -11), (0, -14), (4, -11)], '#efe9d8'), -8, -550, 1, rot=a) for a in range(0, 360, 51)) + '<circle cx="-8" cy="-550" r="4" fill="#d9a53a"/>')
    s.append(hand(10, -500, 96, 0.78, 'grip', sk))
    return dict(body=''.join(s), neck=(8, -566), rot=-7, hs=0.66)


# ---------------- Савелий Петрович ----------------
def sav(pose=None):
    p = CAST['sav']; sk = p['skin']; vest = '#3f5a48'; shirt = '#cfc9b8'; tr = '#4a4038'; s = []
    # far arm behind the back: only the shoulder is seen
    s.append(limb([(16, -250), (20, -130), (18, -22)], [40, 34, 28], tr, lit=LIT, shadows=[[(18, -250), (24, -130), (20, -22), (50, -22), (50, -250)]]))
    s.append(shoe(22, 0, 52, 22, '#2a2320'))
    s.append(limb([(-18, -250), (-20, -130), (-24, -22)], [38, 32, 27], tr, lit=LIT))
    s.append(shoe(-22, 0, 52, 22, '#2a2320'))
    # trunk: stooped, the belly forward
    s.append(form([(-34, -500), (-6, -522), (30, -518), (56, -494), (62, -430), (54, -330), (48, -240), (-40, -240), (-48, -320), (-50, -400), (-46, -460)], shirt, lit=LIT,
                  shadows=[[(30, -530), (40, -470), (28, -400), (36, -240), (70, -240), (70, -530)]]))
    s.append(form([(-30, -492), (-8, -470), (-2, -400), (-12, -300), (-44, -296), (-50, -400), (-44, -462)], vest, lit=(-5, -2)))
    s.append(form([(8, -516), (34, -514), (56, -492), (62, -430), (56, -300), (10, -296), (4, -400), (0, -470)], vest, lit=(-5, -2),
                  shadows=[[(24, -520), (34, -460), (22, -400), (30, -296), (70, -296), (70, -520)]]))
    s.append(shape([(-14, -486), (-2, -500), (6, -484), (-2, -470)], '#7a2e2a'))   # bow tie
    # near arm: the watch held up before the face
    s.append(limb([(44, -494), (30, -420), (-30, -436)], [34, 30, 24], shirt, lit=(-6, -3), shadows=[[(30, -440), (-30, -432), (-30, -420), (36, -400), (60, -420), (56, -500), (44, -470)]]))
    s.append(hand(-32, -437, 78, 0.85, 'grip', sk))
    s.append(f'<circle cx="-50" cy="-452" r="15" fill="#c9a243"/><circle cx="-50" cy="-452" r="11" fill="#efe7cf"/>'
             + line([(-50, -452), (-50, -460)], BLACK, 1.6) + line([(-50, -452), (-45, -449)], BLACK, 1.6)
             + f'<path d="M-40 -440 Q -20 -380 -4 -400" fill="none" stroke="#c9a243" stroke-width="2"/>')
    return dict(body=''.join(s), neck=(2, -504), rot=-12, hs=0.68)


# ---------------- Тим ----------------
def tim(pose=None):
    p = CAST['tim']; sk = p['skin']; red = '#c23b2c'; cream = '#e6dcc4'; sh = '#2f4466'; s = []
    # far arm up: the slingshot
    s.append(limb([(-26, -372), (-54, -330), (-66, -382)], [20, 17, 13], sk, lit=(-4, -2)))
    s.append(g(line([(0, 0), (0, -26)], '#8a5a34', 5) + line([(0, -26), (-10, -46)], '#8a5a34', 4.5) + line([(0, -26), (10, -46)], '#8a5a34', 4.5)
               + line([(-10, -46), (4, -34), (10, -46)], '#1a1a1a', 1.5), -67, -392, 1, rot=-12))
    s.append(hand(-66, -380, 170, 0.72, 'fist', sk))
    # legs apart
    s.append(limb([(-18, -196), (-30, -110), (-34, -24)], [26, 20, 14], sk, lit=(-5, -2)))
    s.append(shape([(-42, -52), (-26, -52), (-27, -24), (-41, -24)], cream))
    s.append(shoe(-33, 0, 44, 24, red))
    s.append(limb([(18, -196), (30, -110), (36, -24)], [27, 21, 15], sk, lit=(-6, -2), shadows=[[(20, -196), (34, -110), (38, -24), (60, -24), (60, -196)]]))
    s.append(shape([(28, -52), (44, -52), (44, -24), (29, -24)], cream) + shape([(38, -52), (44, -52), (44, -24), (38, -24)], BLACK))
    s.append(shoe(37, 0, 46, 25, red))
    # shorts
    s.append(form([(-34, -256), (38, -256), (46, -170), (6, -164), (2, -200), (-6, -164), (-42, -170)], sh, lit=LIT,
                  shadows=[[(14, -256), (22, -164), (60, -164), (50, -256)]]))
    # striped shirt
    body = [(-30, -384), (-6, -394), (22, -394), (44, -380), (46, -330), (40, -250), (-36, -250), (-38, -330)]
    stripes = ''.join(shape([(-60, y), (60, y - 6), (60, y + 8), (-60, y + 14)], red) for y in range(-384, -240, 30))
    c = uid()
    s.append(form(body, cream, lit=LIT))
    s.append(clip(body, g(stripes, -7, -3) + shape([(18, -400), (26, -330), (18, -250), (60, -250), (60, -400)], BLACK)))
    # near arm: fist on the hip
    s.append(limb([(42, -374), (70, -322), (44, -272)], [20, 18, 14], sk, lit=(-5, -2), shadows=[[(44, -380), (74, -322), (46, -272), (90, -272), (90, -380)]]))
    s.append(form([(30, -386), (48, -380), (56, -352), (38, -346)], cream, lit=(-4, -2), shadows=[[(44, -390), (48, -346), (60, -346), (60, -390)]]))
    s.append(hand(44, -274, 60, 0.72, 'fist', sk))
    return dict(body=''.join(s), neck=(6, -384), rot=6, hs=0.68)


# ---------------- Вера ----------------
def vera(pose=None):
    p = CAST['vera']; sk = p['skin']; coat = '#2f5560'; s = []
    s.append(limb([(-10, -200), (-12, -110), (-14, -34)], [22, 17, 11], '#3a3340', lit=(-5, -2)))
    s.append(shoe(-12, 0, 40, 20, '#2a2228', heel=10))
    s.append(limb([(14, -200), (12, -110), (8, -34)], [24, 18, 12], '#3a3340', lit=(-5, -2), shadows=[[(12, -200), (14, -110), (8, -34), (30, -34), (30, -200)]]))
    s.append(shoe(10, 0, 42, 21, '#2a2228', heel=10))
    # the long coat
    s.append(form([(-30, -592), (-8, -606), (24, -606), (50, -590), (52, -500), (44, -440), (50, -300), (54, -172), (10, -166), (-40, -172), (-34, -300), (-30, -440), (-36, -520)],
                  coat, lit=LIT, shadows=[[(20, -610), (30, -520), (16, -440), (26, -300), (22, -166), (70, -166), (70, -610)], [(-8, -440), (-2, -300), (-6, -168), (2, -168), (4, -300)]],
                  under=[([(-12, -606), (22, -608), (6, -560)], '#d8d2c2')]))
    s.append(shape([(-14, -606), (4, -556), (-4, -540), (-22, -590)], '#234149') + shape([(24, -608), (6, -556), (14, -540), (34, -596)], BLACK))
    # arms crossed, a book held to the chest
    s.append(limb([(-28, -584), (-44, -516), (0, -500)], [22, 20, 16], coat, lit=(-5, -2)))
    s.append(shape([(-22, -548), (22, -556), (28, -486), (-16, -478)], '#a23a34') + shape([(8, -553), (22, -556), (28, -486), (14, -484)], BLACK))
    s.append(limb([(46, -582), (54, -512), (-6, -494)], [24, 22, 17], coat, lit=(-6, -3), shadows=[[(50, -590), (60, -512), (-6, -486), (-6, -480), (70, -490), (70, -590)]]))
    s.append(hand(-8, -495, 100, 0.78, 'rest', sk))
    return dict(body=''.join(s), neck=(8, -596), rot=3, hs=0.64)


# ---------------- Марат ----------------
def marat(pose=None):
    p = CAST['marat']; sk = p['skin']; wh = '#e8dfca'; ap = '#c2582e'; tr = '#3a3a44'; s = []; o = []
    # far arm thrown wide, an open hand
    s.append(limb([(-96, -600), (-170, -556), (-196, -650)], [62, 56, 40], sk, lit=(-7, -3), shadows=[[(-150, -540), (-176, -530), (-200, -560), (-170, -548)]]))
    s.append(limb([(-90, -606), (-140, -574)], [72, 64], wh, lit=(-6, -3)))
    s.append(hand(-198, -654, 172, 1.5, 'open', sk, flip=True))
    # legs
    s.append(limb([(-48, -300), (-62, -150), (-66, -24)], [74, 56, 44], tr, lit=LIT))
    s.append(shoe(-62, 0, 78, 30, '#26262c'))
    s.append(limb([(48, -300), (58, -150), (60, -24)], [76, 58, 46], tr, lit=LIT, shadows=[[(52, -300), (64, -150), (64, -24), (110, -24), (110, -300)]]))
    s.append(shoe(64, 0, 80, 32, '#26262c'))
    # the barrel
    s.append(form([(-104, -610), (-40, -646), (50, -646), (116, -612), (132, -520), (128, -400), (104, -290), (-100, -290), (-126, -400), (-124, -520)], wh, lit=(-9, -4),
                  shadows=[[(56, -660), (78, -560), (60, -470), (80, -290), (150, -290), (150, -660)], [(-90, -450), (-30, -438), (30, -450), (-30, -428)]]))
    s.append(''.join(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{BLACK}"/>' for x, y in [(-52, -580), (-56, -520), (0, -584), (0, -524)]))
    # apron
    s.append(form([(-92, -468), (86, -468), (106, -300), (98, -140), (-96, -140), (-106, -300)], ap, lit=(-8, -3),
                  shadows=[[(44, -470), (60, -380), (44, -300), (62, -140), (120, -140), (120, -470)], [(-40, -140), (-32, -270), (-22, -140)]]))
    s.append(line([(-92, -466), (86, -466)], BLACK, 3))
    # towel on the near shoulder
    s.append(form([(64, -646), (108, -622), (118, -500), (80, -492), (72, -550)], '#f1ecdf', lit=(-5, -2), shadows=[[(100, -650), (106, -492), (130, -492), (130, -650)]],
                  under=[([(60, -524), (130, -532), (130, -520), (60, -512)], ap)]))
    # near arm: the ladle raised
    o.append(limb([(116, -598), (186, -560), (204, -664)], [66, 58, 42], sk, lit=(-8, -3), shadows=[[(130, -580), (186, -532), (214, -560), (224, -664), (250, -664), (250, -500), (120, -500)]]))
    o.append(limb([(108, -604), (160, -574)], [76, 68], wh, lit=(-6, -3), shadows=[[(110, -580), (164, -546), (180, -520), (90, -520)]]))
    o.append(g(line([(0, 26), (0, -120)], '#9aa0a8', 7) + form([(-26, -124, 's'), (26, -124, 's'), (20, -92, 's'), (0, -82, 's'), (-20, -92, 's')], '#9aa0a8', lit=(-5, -4)), 206, -680, 1, rot=16))
    o.append(hand(204, -668, 188, 1.5, 'fist', sk))
    return dict(body=''.join(s), over=''.join(o), neck=(8, -634), rot=-8, hs=0.66)


# ---------------- Кира ----------------
def kira(pose=None):
    p = CAST['kira']; sk = p['skin']; hood = '#4b2d4f'; tr = '#34343f'; lime = '#c9e23a'; s = []
    # legs: the weight on the far one, the near foot set forward
    s.append(limb([(4, -300), (-2, -160), (10, -40)], [28, 22, 18], tr, lit=(-5, -2)))
    s.append(shoe(12, 0, 54, 36, '#2a2a33'))
    s.append(limb([(26, -300), (0, -165), (-34, -40)], [30, 23, 19], tr, lit=(-6, -2), shadows=[[(28, -300), (4, -165), (-30, -40), (0, -40), (30, -165), (50, -300)]]))
    s.append(shoe(-32, 0, 56, 38, '#2a2a33'))
    s.append(''.join(line([(-52 + i * 2, -16 - i * 6), (-40 + i * 2, -19 - i * 6)], lime, 2.4) for i in range(3)))
    # the oversized hoodie: shoulders hunched, the belly forward
    s.append(form([(-30, -548), (-2, -562), (34, -562), (62, -540), (70, -470), (64, -380), (56, -300), (48, -284), (-14, -288), (-26, -310), (-34, -400), (-40, -480)], hood, lit=LIT,
                  shadows=[[(24, -570), (36, -480), (20, -400), (28, -284), (80, -284), (80, -570)], [(-30, -330), (10, -322), (46, -330), (10, -312)]]))
    # arms into the front pocket
    s.append(limb([(-28, -536), (-42, -440), (-4, -372)], [26, 26, 22], hood, lit=(-5, -2), shadows=[[(-40, -420), (-10, -372), (4, -360), (-20, -360)]]))
    s.append(limb([(56, -534), (72, -430), (22, -366)], [30, 30, 24], hood, lit=(-7, -3), shadows=[[(60, -540), (80, -430), (24, -350), (90, -350), (90, -540)]]))
    s.append(form([(-16, -386), (34, -386), (40, -330), (-20, -330)], hood, lit=(-3, -5), shadows=[[(14, -390), (20, -330), (44, -330), (44, -390)]]))
    # hood behind the neck, headphones round it
    s.append(form([(-20, -566), (10, -584), (48, -572), (60, -540), (30, -548), (-6, -544), (-26, -540)], hood, lit=(-5, -3), shadows=[[(26, -590), (30, -540), (70, -540), (70, -590)]]))
    o = line([(-18, -560), (4, -548, 's'), (34, -552, 's'), (48, -566)], lime, 6)
    o += form([(-30, -574), (-14, -578), (-10, -546), (-26, -540)], lime, lit=(-3, -2)) + form([(40, -582), (56, -578), (58, -546), (42, -544)], lime, lit=(-3, -2), shadows=[[(50, -590), (50, -540), (60, -540), (60, -590)]])
    return dict(body=''.join(s), over=o, neck=(-2, -556), rot=-9, hs=0.64)


BODY = dict(anya=anya, sav=sav, tim=tim, vera=vera, marat=marat, kira=kira)
HEIGHT = dict(tim=520, sav=640, kira=668, anya=690, vera=720, marat=780)


def figure(k, expr=None, x=0, y=0, s=1.0, flip=False, pose=None):
    p = CAST[k]; b = BODY[k](pose); nx, ny = b['neck']; hs = b['hs']
    e = expr or REST[k]
    place = lambda inner: f'<g transform="translate({nx},{ny}) rotate({b["rot"]}) scale({hs}) translate(-15,-95)">{inner}</g>'
    inner = place(neck_q(p)) + b['body'] + place(head('q', p, e)) + b.get('over', '')
    return g(inner, x, y, s, flip=flip)
