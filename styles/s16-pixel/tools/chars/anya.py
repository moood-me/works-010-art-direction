"""Аня, about 20 — warm, trusting, dreamy. Auburn hair to the chest, a mustard cardigan, a teal skirt, a book."""
LEG = {'A': 'a1', 'B': 'a2', 'C': 'a3', 'D': 'a4', 'Y': 't2', 'y': 't1', 'Z': 't3', 'W': 'w3', 'w': 'w2',
       'T': 'e2', 'd': 'e1', 'L': 'e3', 'O': 'b2', 'o': 'b1', 'R': 'r2', 'q': 'r1', 'F': 'r4'}

FRONT = [
    "........BBBBBBB.........",
    "......BBCCCCCBBBB.......",
    ".....BCCDDCCCBBBBB......",
    "....BCCDCCCCBBBBBBA.....",
    "....BCCCCBBsBBBBBBA.....",
    "....CCBBBssssBBBBBA.....",
    "....CBBssssssssBBBA.....",
    "....CBBsskssskstBBA.....",
    "....CBBsskssskstBBA.....",
    "....CBBspsssssptBBA.....",
    "....CBBsssuuusstBBA.....",
    "....CBBBsssssstBBBA.....",
    "....CBBBAsssssABBBA.....",
    "....CBBA..uuu..BBBA.....",
    "....CBBYYWsssWYYBBA.....",
    "...YCBBYZWWsWWYyBBAy....",
    "...YYBBYYWWWWWYyBAyy....",
    "...YYBAYRRRRRRqyAyyy....",
    "...YYyAYRFFRRRqyyyyy....",
    "...YYyYYRRRRRRqyyyyy....",
    "...YYyYYRRRRRRqyyyyy....",
    "....YYyssRRRRRssyyy.....",
    "....yYYstqqqqqstyy......",
    ".....yyYYYYYYYyyy.......",
    "......TTTTTTTTTdd.......",
    "......TLTTTTTTTdd.......",
    ".....TTLTTTTTTTTdd......",
    ".....TLTTTTTTTTTdd......",
    "....TTLTTTTdTTTTddd.....",
    "....TLTTTTTdTTTTTdd.....",
    "....TLTTTTdTTTTTTdd.....",
    "...TTLTTTTdTTTTTTddd....",
    "...TTTTTTdTTTTTTTTdd....",
    "...dTTTddTTTTddTTddd....",
    "........st...st.........",
    "........st...st.........",
    "........st...st.........",
    "........st...st.........",
    "........st...st.........",
    "........Ww...Ww.........",
    "........Ww...Ww.........",
    ".......OOo...OOo........",
    ".......OOo...oOO........",
]
VIEWS = {'front': FRONT}


# ---------------------------------------------------------------- portrait
import portrait as P

EYE = {'rest': [".KKKK.", "KiEkEK", "KiEkEi", ".iEEi.", "..tt.."],
       'joy': ["......", ".KKKK.", "K....K", "......"],
       'surprise': [".KKKK.", "KiEEiK", "KiEkiK", ".iEEi.", "..tt.."],
       'sadness': ["......", "KKKK..", ".iEkKK", ".iEkEi", "..tt.."],
       'anger': ["...KK.", ".KKEki", "KiEkEi", "..tt.."]}


def portrait(expr='rest'):
    S = {'K': 'a0', 'i': 'w3', 'E': 'e2', 'k': 'x0', 't': 's2', 'g': 'x1'}
    # back hair: a long mass to the shoulders and below
    back = P.new()
    back.sym(P.CX, 5, [6, 10, 13, 15, 16, 17, 18, 18, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19,
                       19, 19, 19, 19, 19, 19, 20, 20, 20, 20, 20, 21, 21, 21, 21, 21, 21, 21, 21, 20, 20, 20, 19,
                       19, 19, 18, 18, 17], 'a2')
    back.rim('a2', 'a1', [(1, 0)], 4)
    back.rect(18, 36, 20, 12, 'a1')                       # the dark behind the neck
    # neck and clothes
    body = P.new()
    body.rect(24, 38, 8, 9, 's2')
    body.spans(40, [(24, 31), (25, 31)], 's1')            # under the chin
    body.spans(45, [(21, 34), (18, 37), (15, 40), (12, 43), (10, 45), (8, 47), (7, 48), (6, 49), (6, 49),
                    (5, 50), (5, 50)], 't2')
    body.rim('t2', 't1', [(1, 0)], 5)
    body.spans(45, [(22, 28), (19, 24), (16, 20), (13, 17), (11, 14)], 't3')   # light on the shoulder
    for j, (a, b) in enumerate([(23, 32), (23, 32), (24, 31), (24, 31), (25, 30), (25, 30), (26, 29), (26, 29),
                                (27, 28), (27, 28)]):
        body.hline(a, b, 46 + j, 'w3')                    # the blouse in the V of the cardigan
        body.px(b, 46 + j, 'w2'); body.px(a - 1, 46 + j, 't1'); body.px(b + 1, 46 + j, 't1')
    body.spans(44, [(24, 31), (24, 31)], 's3'); body.hline(27, 31, 45, 's2'); body.hline(24, 31, 44, 's2')
    body.pxs('w3', (22, 45), (23, 45), (32, 45), (33, 45), (21, 46), (22, 46), (33, 46), (34, 46))   # collar
    # hair in front of the shoulders
    body.spans(40, [(8, 15)] * 3 + [(8, 14)] * 4 + [(9, 14)] * 3 + [(9, 13)] * 3 + [(10, 13)] * 3, 'a2')
    body.spans(40, [(40, 47)] * 3 + [(41, 47)] * 4 + [(41, 46)] * 3 + [(42, 46)] * 3 + [(42, 45)] * 3, 'a1')
    for y in range(40, 56):
        if body.get(9, y) == 'a2' and y % 5 != 2:
            body.px(10, y, 'a3')
    # head
    head = P.new()
    head.sym(P.CX, 10, [7, 9, 10, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 11, 11,
                        10, 10, 9, 8, 7, 6, 6, 5, 4], 's3')
    P.skin(head, 's')
    # features
    f = head
    le, re = (18, 24), (32, 24)
    eye = EYE[expr]
    f.stamp(le[0], le[1], eye, S); f.stamp(re[0], re[1], eye, S, flip=True)
    if expr in ('rest', 'sadness', 'anger', 'surprise'):
        gy = {'rest': 25, 'sadness': 26, 'anger': 26, 'surprise': 25}[expr]
        f.pxs('x1', (20, gy), (34, gy))                    # the glints, both on the lit side
    brows = {'rest': [(18, 22), (19, 21), (20, 21), (21, 21), (22, 21), (23, 22)],
             'joy': [(18, 21), (19, 20), (20, 20), (21, 20), (22, 20), (23, 21)],
             'surprise': [(18, 20), (19, 19), (20, 19), (21, 19), (22, 19), (23, 20)],
             'sadness': [(18, 23), (19, 22), (20, 22), (21, 21), (22, 21), (23, 20)],
             'anger': [(18, 20), (19, 20), (20, 21), (21, 21), (22, 22), (23, 23)]}[expr]
    f.pxs('a1', *brows); f.pxs('a1', *P.mirror_pts(brows))
    f.pxs('s2', (29, 29), (29, 30), (29, 31), (29, 32)); f.pxs('s1', (28, 33), (29, 33)); f.pxs('s4', (27, 31), (27, 32))
    P.blob(f, 18, 31, ['.###.', '#####', '.###.'], 'z0', 's3'); P.blob(f, 33, 31, ['.###.', '#####', '.###.'], 'z0', 's3')
    if expr == 'rest':
        f.pxs('x3', (24, 36), (25, 37), (26, 37), (27, 37), (28, 37), (29, 37), (30, 37), (31, 36))
        f.pxs('x2', (26, 38), (27, 38), (28, 38), (29, 38))
    elif expr == 'joy':
        f.pxs('x3', (23, 35), (24, 36), (25, 36), (26, 36), (27, 36), (28, 36), (29, 36), (30, 36), (31, 36), (32, 35))
        f.hline(25, 30, 37, 'x1'); f.hline(26, 29, 38, 'x3'); f.pxs('x3', (24, 37), (31, 37), (25, 38), (30, 38))
        f.hline(26, 29, 39, 'x2')
    elif expr == 'surprise':
        f.spans(36, [(26, 29), (25, 30), (25, 30), (26, 29)], 'x3'); f.spans(37, [(26, 29), (27, 28)], 'r0')
    elif expr == 'sadness':
        f.pxs('x3', (24, 38), (25, 37), (26, 37), (27, 37), (28, 37), (29, 37), (30, 37), (31, 38))
        f.pxs('x2', (27, 38), (28, 38))
    elif expr == 'anger':
        f.pxs('x3', (25, 37), (26, 36), (27, 36), (28, 36), (29, 36), (30, 37)); f.pxs('s2', (27, 38), (28, 38))
    # front hair: a parting left of the middle, two sweeps, locks along the cheeks
    hair = P.new()
    hair.sym(P.CX, 6, [8, 11, 13, 14, 15, 15, 16, 16, 16, 16], 'a2')
    win = {12: (23, 25), 13: (21, 27), 14: (20, 30), 15: (19, 33), 16: (18, 35), 17: (18, 37), 18: (17, 38),
           19: (17, 38)}
    for y in range(12, 34):
        a, b = win.get(y, (16 + (y > 26), 39 - (y > 24)))
        hair.hline(12, a - 1, y, 'a2'); hair.hline(b + 1, 43, y, 'a2')
    hair.rim('a2', 'a1', [(1, 0)], 3)
    for y in range(6, 34):                                 # keep inside the back mass
        for x in range(56):
            if hair.g[y][x] and not back.g[y][x]:
                hair.g[y][x] = None
    # light on the hair: a broken band round the crown, two glints
    for x, y, n in [(17, 9, 5), (15, 10, 6), (14, 11, 5), (13, 12, 4), (12, 13, 3), (25, 8, 6), (27, 9, 7),
                    (30, 10, 5), (11, 20, 2), (11, 21, 2), (11, 22, 2), (11, 26, 2), (11, 27, 2), (11, 28, 2)]:
        hair.hline(x, x + n - 1, y, 'a3')
    hair.pxs('a4', (16, 10), (17, 10), (18, 10), (15, 11), (28, 9), (29, 9), (30, 9))
    for x0, y0, x1, y1 in [(24, 7, 14, 17), (27, 6, 41, 15), (13, 20, 14, 33), (42, 18, 41, 33)]:
        hair.line(x0, y0, x1, y1, 'a1')                    # strands
    c = P.new()
    for l in (back, body, head, hair):
        c.paste(l)
    P.cast(c, 'a', 's', 2)
    P.jaw(c, 's', 'a', dirs=((1, 0),))
    return c
