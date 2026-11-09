"""Савелий Петрович, about 70, a watchmaker — grumpy outside, kind inside. A bald dome, white tufts, brows and
moustache, a loupe pushed up on the forehead, a moss vest; he looks at a pocket watch."""
LEG = {'W': 'w3', 'w': 'w2', 'x': 'w1', 'G': 'g2', 'g': 'g1', 'F': 'g3', 'B': 'b2', 'b': 'b1', 'N': 'b1',
       'Y': 't3', 'y': 't2', 'R': 'r2', 'L': 'n2', 'M': 'n1', 'e': 'u3'}

FRONT = [
    ".........sssss",
    ".......sshhsseMst",
    "......sshhsssMMstt",
    "......LLLLLLLLLLL",
    "....WWsssssssssstWx",
    "...WWWsWWsssssWWtWWx",
    "...WWwsskWsssWkstwWx",
    "...xWwssssssstssstwWx",
    "....Wwspsshptssptwx",
    "....xwsWWWWuWWWwtx",
    "......WWwsuuusWww",
    "......wsssssssttx",
    "........tsssstt",
    ".......WWWRRWWWW",
    ".....WWGGGWWGGGWWw",
    "....WWWGGGGWGGGgWWw",
    "....WWwGFGGGGGGgWWw",
    "....WWwGFYYYGGGgwWw",
    "....wwwGGYiyGyygwWw",
    ".....ssssyyyyGGgwWw",
    "......tsssstGGGgwst",
    ".......GGGGGGGGg.st",
    ".......BBBBBBBBb.st",
    ".......BBBBBBBBbsst",
    ".......BBBBBBBBb",
    ".......BBBB.BBBb",
    ".......BBBb.BBBb",
    ".......BBBb.BBBb",
    ".......BBBb.BBBb",
    ".......BBBb.BBBb",
    ".......BBBb.BBBb",
    ".......BBBb.BBBb",
    ".......BBBb.BBBb",
    ".......BBBb.BBBb",
    ".......BBBb.BBBb",
    ".......NNNN.NNNN",
    "......NNNNN.NNNNN",
]
Q = [
    ".........sssss",
    ".......sshhssseMst",
    "......sshhsssssMMt",
    "......LLLLLLLLLLLL",
    "....WWssssssssssst",
    "...WWWssWWsssssWWtx",
    "...WWwssskWsssWkstx",
    "...xWwsssssssstsstx",
    "....Wwsspssshptspt",
    "....xwssWWWWuWWWwt",
    "......sWWwsuuusWw",
    "......ssssssssstt",
    "........tssssstt",
    ".......WWWWRRWWW",
    ".....WWGGGGWWGGWw",
    "....WWWGGGGGWGGgWw",
    "....WWwGFGGGGGGgWw",
    "....WWwGFGYYYGGgww",
    "....wwwGGGYiyGygWw",
    ".....sssssyyyyGgWw",
    "......tsssstGGGgst",
    ".......GGGGGGGGg.t",
    ".......BBBBBBBBb",
    ".......BBBBBBBBb",
    ".......BBBBBBBBb",
    ".......BBBB.BBBb",
] + [".......BBBb.BBBb"] * 9 + [
    ".......NNNN.NNNN",
    ".......NNNNN.NNNNN",
]
SIDE = [
    "..........sssss",
    "........sshhsssst",
    ".......sshhssssMeM",
    ".......LLLLLLLLLMM",
    ".....WWsssssssssst",
    "....WWWWsssssssWWW",
    "....WWWwsstsssskss",
    "....xWWwssttsssssst",
    ".....WWwssssspsshpt",
    ".....xwwsssssssWWWW",
    ".......wssssssWWWw",
    "........sssssssWw",
    ".........tssssst",
    "........WWWWWRW",
    ".......GGWWWWGg",
    "......GGGWWWWGGg",
    "......GGGWWwWGGg",
    "......GGGwWWwGGg",
    "......GGGGwWWWWss",
    "......GGGGGwwwwsst",
    "......GGGGGGGGg.y",
    ".......GGGGGGGg.YYY",
    ".......BBBBBBBb.YiY",
    ".......BBBBBBBb.yyy",
    ".......BBBBBBBb",
    ".......BBBBBBb",
] + ["........BBBBb"] * 9 + [
    "........NNNNNN",
    "........NNNNNNN",
]
VIEWS = {'front': FRONT, 'q': Q, 'side': SIDE}


# ---------------------------------------------------------------- portrait
import portrait as P


def portrait(expr='rest'):
    back = P.new()                                         # white tufts at the sides
    tuft = [(11, 14), (9, 14), (8, 14), (7, 14), (6, 14), (6, 14), (7, 14), (6, 14), (5, 14), (6, 14), (6, 14),
            (7, 14), (7, 14), (8, 14), (9, 14), (10, 14), (12, 14)]
    back.spans(17, tuft, 'w3'); back.spans(17, [(55 - b, 55 - a) for a, b in tuft], 'w3')
    back.rim('w3', 'w2', [(0, 1)], 2); back.rim('w3', 'w2', [(1, 0)], 1)
    for x in range(44, 51):
        for y in range(17, 34):
            if back.get(x, y) == 'w3':
                back.px(x, y, 'w2')
    back.pxs('w1', (8, 21), (9, 22), (7, 26), (8, 27), (9, 30), (46, 22), (47, 23), (45, 27), (46, 28), (44, 31))
    body = P.new()
    body.rect(23, 38, 10, 8, 's2'); body.spans(41, [(23, 32), (24, 32)], 's1')
    sh = [(19, 36), (15, 40), (12, 43), (9, 46), (7, 48), (6, 49), (5, 50), (4, 51), (4, 51), (3, 52), (3, 52), (3, 52)]
    body.spans(44, sh, 'w3')
    vest = [(19, 36), (16, 39), (14, 41), (13, 42), (12, 43), (12, 43), (11, 44), (11, 44), (11, 44), (11, 44), (11, 44), (11, 44)]
    body.spans(44, vest, 'g2')
    body.rim('g2', 'g1', [(1, 0)], 4); body.rim('w3', 'w2', [(1, 0)], 3)
    for j in range(12):                                    # the shirt in the V of the vest
        hw = max(0, 6 - j // 2)
        if hw:
            body.hline(28 - hw, 27 + hw, 44 + j, 'w3'); body.px(27 + hw, 44 + j, 'w2')
            body.px(28 - hw - 1, 44 + j, 'g3'); body.px(28 + hw, 44 + j, 'g1')
    body.spans(43, [(23, 32)], 'w3'); body.pxs('w2', (22, 44), (33, 44), (23, 45), (32, 45))
    body.spans(45, [(24, 26), (24, 31), (24, 26)], 'r2'); body.spans(45, [(29, 31), None, (29, 31)], 'r2')
    body.pxs('r1', (27, 46), (28, 46), (31, 47), (31, 45)); body.pxs('r3', (24, 45), (25, 45))      # a bow tie
    body.pxs('t3', (27, 50), (27, 54)); body.pxs('g1', (28, 50), (28, 54))                           # buttons
    body.spans(44, [(12, 16), (9, 13), (7, 10)], 'w4')
    head = P.new()
    head.sym(P.CX, 7, [6, 9, 11, 12, 13, 13, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14,
                       14, 14, 14, 14, 14, 13, 13, 12, 11, 10, 8], 's3')
    P.skin(head, 's')
    f = head
    P.blob(f, 18, 9, ['..####', '.#####', '####..', '###...', '##....'], 's4', 's3')      # the shine of the dome
    for x0, x1, y in [(20, 26, 16), (29, 35, 16), (22, 33, 18)]:                             # wrinkles
        f.hline(x0, x1, y, 's2')
    # eyes: small, under heavy brows
    eye = {'rest': ["KKKK", "ikEi", ".tt."], 'joy': [".KK.", "K..K", "...."], 'surprise': ["KKKK", "iEki", "iEki", ".tt."],
           'sadness': ["KK..", "ikKK", ".tt."], 'anger': ["..KK", "KKki", ".tt."]}[expr]
    P.eyes(f, 19, 25, eye, {'K': 'b1', 'i': 'w3', 'k': 'x0', 'E': 'u2', 't': 's2'})
    P.both(f, 's2', [(17, 28), (18, 29), (19, 29), (20, 29), (21, 29), (22, 29), (23, 28), (16, 25), (15, 24), (16, 27)])
    brow = {'rest': [(15, 21), (16, 20), (17, 20), (18, 20), (19, 20), (16, 21), (17, 21), (18, 21), (19, 21), (20, 21),
                     (21, 21), (20, 22), (21, 22), (22, 22), (23, 22), (22, 23), (23, 23), (24, 23)],
            'joy': [(15, 20), (16, 19), (17, 19), (18, 19), (19, 19), (20, 19), (21, 19), (22, 20), (23, 20), (16, 20),
                    (17, 20), (18, 20), (19, 20), (20, 20), (21, 20), (23, 21), (24, 21)],
            'surprise': [(15, 18), (16, 17), (17, 17), (18, 17), (19, 17), (20, 17), (21, 17), (22, 18), (23, 18),
                         (16, 18), (17, 18), (18, 18), (19, 18), (20, 18), (21, 18), (23, 19), (24, 19)],
            'sadness': [(15, 23), (16, 23), (17, 22), (18, 22), (19, 22), (20, 21), (21, 21), (22, 20), (23, 20), (24, 19),
                        (16, 22), (18, 21), (19, 21), (21, 20), (22, 19), (23, 19)],
            'anger': [(15, 19), (16, 19), (17, 20), (18, 20), (19, 21), (20, 21), (21, 22), (22, 22), (23, 23), (24, 23),
                      (16, 20), (17, 21), (18, 21), (19, 22), (20, 22), (21, 23), (22, 23), (23, 24), (24, 24), (25, 24)]}[expr]
    P.both(f, 'w3', brow)
    low = {}
    for x, y in brow:
        low[x] = max(low.get(x, 0), y)
    P.both(f, 'w1', [(x, y + 1) for x, y in low.items() if (x, y + 1) not in brow])
    # the nose: big and a little red
    f.vline(30, 24, 29, 's2'); f.spans(29, [(26, 30), (25, 31), (25, 31), (25, 31), (26, 30)], 'z2')
    f.pxs('s4', (26, 30), (27, 30), (26, 31)); f.pxs('s1', (25, 33), (30, 33), (31, 32)); f.pxs('s2', (24, 31), (32, 31), (24, 32))
    P.blob(f, 16, 31, ['.###.', '#####', '.###.'], 'z0', 's3'); P.blob(f, 35, 31, ['.###.', '#####', '.###.'], 'z0', 's3')
    # the moustache hides the mouth; the lower lip under it
    m = P.new()
    lift = {'joy': -1}.get(expr, 0)
    m.spans(34 + lift, [(22, 33), (18, 37), (16, 39), (15, 40), (15, 40)], 'w3')
    drop = {'rest': [(14, 20), (14, 18)], 'joy': [(15, 19), None], 'surprise': [(14, 19), (14, 17)],
            'sadness': [(13, 19), (13, 17), (13, 15)], 'anger': [(14, 20), (14, 18)]}[expr]
    m.spans(39 + lift, drop, 'w3'); m.spans(39 + lift, [r and (55 - r[1], 55 - r[0]) for r in drop], 'w3')
    m.rim('w3', 'w2', [(0, 1)], 1); m.rim('w3', 'w2', [(1, 0)], 2)
    m.vline(27, 35 + lift, 37 + lift, 'w1'); m.pxs('w1', (28, 34 + lift), (21, 37 + lift), (22, 38 + lift), (34, 37 + lift), (33, 38 + lift), (18, 38 + lift), (37, 38 + lift))
    f.paste(m)
    if expr == 'surprise':
        f.spans(39, [(26, 29), (25, 30), (26, 29)], 'r0')
    elif expr == 'joy':
        f.hline(23, 32, 38, 'r0'); f.hline(24, 31, 39, 'x1'); f.hline(25, 30, 40, 'r0')
    else:
        f.hline(24, 31, 39, 's1' if expr != 'sadness' else 's2'); f.hline(25, 30, 40, 's4' if expr != 'anger' else 's3')
    f.hline(25, 30, 41 if expr != 'joy' else 42, 's2')
    # the loupe pushed up on the forehead, on its strap
    lp = P.new()
    lp.hline(15, 40, 13, 'n2'); lp.hline(14, 41, 14, 'n1'); lp.pxs('n3', (17, 13), (18, 13), (19, 13), (25, 13), (26, 13))
    lp.spans(8, [(32, 37), (31, 38), (31, 38), (31, 38), (31, 38), (31, 38), (31, 38), (32, 37)], 'n1')
    lp.spans(9, [(32, 36), (32, 36), (32, 36)], 'u2'); lp.pxs('u4', (32, 9), (33, 9), (32, 10)); lp.pxs('u1', (36, 11), (35, 11), (36, 10))
    lp.pxs('n3', (31, 12), (31, 13), (32, 15), (33, 15)); lp.hline(31, 38, 12, 'n2')
    c = P.stack(back, body, head, lp)
    P.jaw(c, 's', 'w', dirs=((1, 0),))
    return c
