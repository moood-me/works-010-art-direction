"""Вера, about 40 — strict, clever, tired. A tight bun, glasses, a long face, a dark teal coat, a wine scarf,
arms crossed."""
LEG = {'V': 'v2', 'v': 'v1', 'X': 'v3', 'K': 'v1', 'E': 'u4', 'T': 'e1', 'd': 'e0', 'L': 'e2',
       'R': 'r1', 'r': 'r0', 'Q': 'r2', 'N': 'v1', 'n': 'v0'}

FRONT = [
    ".........VVVv",
    "........VXVVVv",
    ".........VVVv",
    "......VVXXVVVVVVv",
    ".....VVXXVVVVVVVVv",
    ".....VXVVVVVVVVVVv",
    ".....VXVVsssssVVVv",
    ".....VVsssssssssVv",
    ".....VvsKKKsKKKtVv",
    ".....VvsEkEKEkEtvv",
    "......vsttssstttv",
    "......vssssstsstv",
    ".......sssuuusst",
    "........sssssst",
    ".........ssstt",
    "..........uuu",
    ".........QRRRr",
    "......TTTQRRRrTTd",
    ".....TLTTTQRrTTTdd",
    ".....TLTTTTRrTTTTd",
    ".....TLTTTTRrTTTTd",
    ".....TTTTTTTTTTTdd",
    ".....TLLLLLLLTTssd",
    ".....TTTTTTTTTTstd",
    ".....dsTTTTTTTTTTd",
    "......ddddddddddd",
    "......TLTTTTTTTTd",
    "......TLTTTTTTTTd",
    "......TLTTTTTTTTd",
    "......TLTTTTTTTTd",
    "......TLTTTTTTTTdd",
    ".....TTLTTTTTTTTdd",
    ".....TTLTTTTTdTTdd",
    ".....TTLTTTTTdTTdd",
    ".....TTLTTTTTdTTdd",
    ".....TTLTTTTTdTTdd",
    ".....TTLTTTTdTTTdd",
    ".....TTLTTTTdTTTdd",
    ".....TTTTTTTdTTTdd",
    ".....TTTTTTTTTTTdd",
    ".....dddddddddddd",
    ".........Nn.Nn",
    ".........Nn.Nn",
    ".........Nn.Nn",
    ".........Nn.Nn",
    "........NNn.NNn",
]
VIEWS = {'front': FRONT}


# ---------------------------------------------------------------- portrait
import portrait as P


def portrait(expr='rest'):
    back = P.new()                                         # the bun, a pin through it
    back.sym(P.CX, 0, [4, 6, 7, 7, 7, 7, 6, 4], 'v2')
    back.rim('v2', 'v1', [(1, 0)], 3); back.pxs('v3', (23, 1), (24, 1), (22, 2), (23, 2), (22, 3), (22, 4)); back.px(24, 2, 'v4')
    back.line(35, 3, 40, 0, 't3'); back.px(41, 0, 'r2'); back.hline(24, 31, 7, 'v0')
    body = P.new()
    body.rect(24, 38, 8, 12, 's2'); body.spans(42, [(24, 31), (25, 31)], 's1'); body.vline(24, 44, 47, 's3'); body.vline(25, 44, 46, 's3')
    coat = [(18, 37), (14, 41), (12, 43), (10, 45), (9, 46), (9, 46), (8, 47), (8, 47), (8, 47)]
    body.spans(47, coat, 'e1')
    body.rim('e1', 'e0', [(1, 0)], 5); body.spans(47, [(18, 24), (14, 19), (12, 15), (10, 12)], 'e2')
    body.line(27, 52, 24, 55, 'e0'); body.line(28, 52, 31, 55, 'e0'); body.pxs('e2', (23, 54), (22, 55))
    body.spans(45, [(21, 34), (20, 35), (20, 35), (20, 35), (21, 34)], 'r1')                 # the scarf
    body.spans(45, [(21, 28), (20, 25)], 'r2'); body.spans(48, [(30, 35), (26, 34)], 'r0')
    body.spans(50, [(27, 31), (27, 31), (27, 30), (28, 30)], 'r1'); body.vline(31, 50, 52, 'r0'); body.px(27, 50, 'r2')
    head = P.new()
    head.sym(P.CX, 8, [5, 7, 9, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 10,
                       10, 10, 9, 9, 8, 8, 7, 6, 5, 4], 's3')
    head.spans(24, [(15, 16), (15, 16), (15, 16), (15, 16), (16, 16)], 's3'); head.spans(24, [(39, 40)] * 4, 's2')
    P.skin(head, 's')
    f = head
    # cheekbones and the tired lines
    for x, y in [(36, 31), (36, 32), (35, 33), (35, 34), (34, 35)]:
        f.px(x, y, 's2')
    eye = {'rest': ["sssss", "KKKKK", "iEkEi", "ttttt"], 'joy': ["sssss", ".KKK.", "K...K", "....."],
           'surprise': ["KKKKK", "iEkEi", "iEkEi", ".ttt."], 'sadness': ["sssss", "KKKK.", "iEkKK", "ttttt"],
           'anger': ["...KK", "KKKEi", "iEkEi", "ttttt"]}[expr]
    P.eyes(f, 19, 24, eye, {'K': 'v0', 'i': 'w3', 'k': 'x0', 'E': 'u2', 't': 's2', 's': 's2'})
    brow = {'rest': [(17, 22), (18, 21), (19, 21), (20, 21), (21, 21), (22, 21), (23, 21), (24, 22)],
            'joy': [(17, 21), (18, 20), (19, 20), (20, 20), (21, 20), (22, 20), (23, 21)],
            'surprise': [(17, 20), (18, 19), (19, 19), (20, 19), (21, 19), (22, 19), (23, 20)],
            'sadness': [(17, 22), (18, 22), (19, 21), (20, 21), (21, 20), (22, 20), (23, 19)],
            'anger': [(17, 20), (18, 20), (19, 21), (20, 21), (21, 21), (22, 22), (23, 22), (24, 23)]}[expr]
    P.both(f, 'v1', brow)
    f.vline(29, 24, 32, 's2'); f.pxs('s1', (27, 33), (28, 33), (30, 32)); f.vline(27, 27, 31, 's4'); f.pxs('s2', (26, 33), (30, 33))
    if expr == 'rest':
        f.hline(24, 31, 36, 'x3'); f.hline(26, 29, 38, 's2')
    elif expr == 'joy':
        f.pxs('x3', (23, 35), (32, 35)); f.hline(24, 31, 36, 'x3'); f.hline(26, 29, 37, 'z0')
    elif expr == 'surprise':
        f.spans(36, [(26, 29), (25, 30), (26, 29)], 'x3'); f.hline(26, 29, 37, 'r0')
    elif expr == 'sadness':
        f.hline(25, 30, 36, 'x3'); f.pxs('x3', (24, 37), (31, 37)); f.pxs('s2', (23, 38), (32, 38)); f.hline(26, 29, 38, 's2')
    elif expr == 'anger':
        f.hline(25, 30, 36, 'r0'); f.pxs('r0', (24, 37), (31, 37)); f.hline(26, 29, 38, 's2')
    # glasses: a thin dark frame, a glint on each lens
    g = P.new()
    for x0 in (17, 32):
        g.hline(x0, x0 + 6, 23, 'v2'); g.vline(x0, 24, 27, 'v2'); g.vline(x0 + 6, 24, 27, 'v2'); g.hline(x0 + 1, x0 + 5, 28, 'v3')
        g.pxs('u4', (x0 + 1, 24), (x0 + 5, 27))
    g.hline(24, 31, 24, 'v2'); g.pxs('v2', (16, 24), (15, 24), (39, 24), (40, 24))
    # hair: pulled back tight, a high hairline
    hair = P.new()
    hair.sym(P.CX, 6, [5, 8, 10, 11, 12, 12, 12, 12, 12, 12], 'v2')
    win = {11: (25, 30), 12: (22, 33), 13: (20, 35), 14: (19, 36), 15: (18, 37)}
    for y in range(11, 24):
        a, b = win.get(y, (18, 37))
        hair.hline(16, a - 1, y, 'v2'); hair.hline(b + 1, 39, y, 'v2')
    hair.rim('v2', 'v1', [(1, 0)], 3)
    for x0, y0, x1, y1 in [(27, 6, 20, 12), (24, 6, 17, 14), (22, 7, 16, 20), (30, 6, 37, 12), (33, 7, 39, 16)]:
        hair.line(x0, y0, x1, y1, 'v1')
    for x0, y0, x1, y1 in [(25, 7, 19, 12), (23, 8, 17, 16)]:
        hair.line(x0, y0, x1, y1, 'v3')
    hair.pxs('v4', (22, 9), (21, 10), (23, 8))
    hair.line(31, 8, 36, 13, 'v3'); hair.line(32, 8, 37, 13, 'v4')            # a grey strand
    c = P.stack(back, body, head, g, hair)
    P.cast(c, 'v', 's', 1)
    P.jaw(c, 's', 're', dirs=((1, 0), (0, 1)))
    return c
