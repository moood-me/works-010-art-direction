"""Кира, about 15 — prickly, closed, defiant. Choppy dark hair with a fringe over one eye, an oversized plum
hoodie, lime headphones round the neck, narrow trousers, heavy boots; hands in the pouch, a slouch."""
LEG = {'H': 'n1', 'M': 'n3', 'D': 'n0', 'K': 'x0', 'G': 'l2', 'g': 'l1', 'P': 'p2', 'Q': 'p1', 'L': 'p3',
       'N': 'n3', 'n': 'n2', 'B': 'v2', 'b': 'v1'}

FRONT = [
    "........H..HH.H",
    ".......HHMHHHHHH",
    "......HMMHHHHHHHHD",
    ".....HMHHHHHHHHHHD",
    "....HHHHHHMHHHHHHHD",
    ".....HHsssHHMHHHHD",
    "....HHsssssHHMHHHD",
    ".....HsKKKssHHHHHD",
    ".....HsskssstHHHHHD",
    ".....DssksssstHHD",
    "......ssssssust.H",
    ".......sssuusst",
    "........sssst",
    "..........ut",
    ".......GG.utt.GG",
    "......PGGPLLPPGGQ",
    ".....PLgHPPPPPHgPQ",
    ".....PLPPPPPPPPPPQ",
    "....PPLPPPPPPPPPPQQ",
    "....PLPQPPPPPPPQPPQ",
    "....PLPQPPPPPPPQPPQ",
    "....PLPQPPPPPPPQPPQ",
    "....PLPQPPPPPPPQPPQ",
    "....PLPQPPPPPPPQPPQ",
    "....PPLPQQQQQQQPPQQ",
    ".....PPLPPPPPPPPQQ",
    ".....QPPPPPPPPPPQQ",
    "......QQPPPPPPPQQ",
    "......QQQQQQQQQQQ",
    ".......NNn..NNn",
    ".......NNn..NNn",
    ".......NNn..NNn",
    ".......NNn..NNn",
    ".......NNn...NNn",
    ".......NNn...NNn",
    ".......NNn...NNn",
    ".......NNn...NNn",
    ".......NNn....NNn",
    ".......NNn....NNn",
    ".......NNn....NNn",
    "......BBBB...BBBBb",
    "......BGBB...BBGBb",
    ".....BBGBB...BBGBBb",
    ".....BBBBB...BBBBBBb",
    ".....bbbbb...bbbbbbb",
]
Q = [
    "........H..HH.H",
    ".......HHMHHHHHH",
    "......HMMHHHHHHHHD",
    ".....HMHHHHHHHHHHD",
    "....HHHHHHMHHHHHHD",
    ".....HHHHsssHHMHHD",
    "....HHHHsssssHHMHD",
    ".....HHHsKKKssHHHD",
    ".....HHHsskssstHHD",
    ".....DHHsskssssHD",
    "......DHsssssssut",
    ".......Dsssssuust",
    ".........ssssst",
    "...........ut",
    "......GG.Putt.G",
    ".....PGGPPLPPPGQ",
    "....PLgHPPPPPPgQ",
    "....PLPPPPPPPPPQQ",
    "....PLPPPPPPPPPPQ",
    "....PLPQPPPPPPQPQ",
    ".....LPQPPPPPPQPQ",
    ".....LPQPPPPPPQPQQ",
    ".....PLQPPPPPPQPPQ",
    ".....PLPQPPPPPQPPQ",
    ".....PPLPQQQQQQPQQ",
    "......PPLPPPPPPPQQ",
    "......QPPPPPPPPPQQ",
    ".......QQPPPPPPQQ",
    ".......QQQQQQQQQQ",
] + ["........NNn.NNn"] * 4 + ["........NNn..NNn"] * 7 + [
    ".......BBBB..BBBBb",
    ".......BGBB..BGBBb",
    ".......BGBBB.BGBBBb",
    ".......BBBBB.BBBBBb",
    ".......bbbbb.bbbbbb",
]
SIDE = [
    ".......H..HH.H",
    "......HHMHHHHHH",
    ".....HMMHHHHHHHH",
    "....HMHHHHHHHHHHH",
    "....HHHHHMHHHHHHHH",
    "....HHHHHHHHHMHHHHH",
    "....HHHHHHHsssHHHHH",
    "....DHHHHHssKKsHHH",
    ".....DHHHsstsksstH",
    ".....DHHHssssssss",
    "......DHHsssssust",
    ".......DDssssss",
    "..........sssst",
    "..........ut",
    "........GGutP",
    "......PPGGgPPP",
    ".....PLPgHgPPPQ",
    "....PLPPPPPPPPQ",
    "....PLPPQPPPPPQ",
    "....PLPPQPPPPPPQ",
    ".....LPPQPPQPPPQ",
    ".....PLPPQPPQPPQ",
    "......LPPPQQQPPPQ",
    "......PLPPPPPPPPQ",
    "......PPLPPPPPPQQ",
    ".......PPPPPPPPQQ",
    ".......QQPPPPPPQ",
    "........QQQQQQQ",
] + [".........NNNNn"] * 5 + [".........nn.NNn"] * 7 + [
    ".........bbb.BBBb",
    ".........bbb.BGBb",
    ".........bbbbBGBBb",
    ".........bbbbBBBBBb",
    ".........bbbbbbbbbb",
]
VIEWS = {'front': FRONT, 'q': Q, 'side': SIDE}


# ---------------------------------------------------------------- portrait
import portrait as P


def portrait(expr='rest'):
    back = P.new()                                         # choppy hair behind the cheeks, cut unevenly
    back.spans(18, [(11, 44)] * 12 + [(11, 43), (12, 43), (12, 44), (11, 42), (12, 42), (13, 43), (12, 41), (14, 41)], 'n1')
    back.pxs('n1', (11, 38), (15, 38), (40, 38), (43, 37), (16, 39))
    body = P.new()
    body.rect(24, 38, 7, 9, 's2'); body.spans(41, [(24, 30), (25, 30), (26, 30)], 's1')
    hood = [(17, 38), (13, 42), (10, 44), (8, 46), (6, 48), (5, 50), (4, 51), (3, 52), (3, 52), (2, 53), (2, 53)]
    body.spans(45, hood, 'p2')
    body.rim('p2', 'p1', [(1, 0)], 5)
    body.spans(44, [(18, 36), (15, 39), (14, 40), (14, 40), (16, 38)], 'p2')              # the hood bunched round the neck
    body.spans(44, [(18, 26), (15, 21), (14, 18)], 'p3'); body.spans(47, [(15, 39), (17, 37)], 'p1')
    body.spans(44, [(23, 31), (24, 30), (25, 29)], 's2'); body.spans(46, [(24, 30)], 'p0'); body.px(27, 45, 's1')
    body.line(25, 49, 24, 55, 'p3'); body.line(30, 49, 31, 55, 'p3'); body.pxs('l2', (24, 55), (31, 55))       # the cords
    body.spans(46, [(7, 12), (5, 10), (4, 8)], 'p3')
    for x0, sh, pad in ((10, 0, 5), (39, 1, 0)):           # headphones round the neck: the one sharp colour
        body.spans(39 + sh, [(x0 + 1, x0 + 5), (x0, x0 + 6), (x0, x0 + 6), (x0, x0 + 6), (x0, x0 + 6), (x0, x0 + 6), (x0, x0 + 6),
                             (x0, x0 + 6), (x0 + 1, x0 + 5)], 'l2')
        body.vline(x0 + 6, 40 + sh, 46 + sh, 'l1'); body.hline(x0 + 1, x0 + 5, 47 + sh, 'l1')
        body.pxs('l3', (x0 + 1, 40 + sh), (x0 + 2, 40 + sh), (x0 + 1, 41 + sh))
        body.rect(x0 + pad, 40 + sh, 2, 7, 'n1'); body.vline(x0 + pad, 41 + sh, 45 + sh, 'n2')    # the pad, turned to the neck
    body.spans(47, [(17, 22), (33, 38)], 'n2'); body.spans(48, [(18, 23), (32, 37)], 'n1')        # the band behind
    head = P.new()
    head.sym(P.CX - 1, 12, [6, 8, 9, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 10, 10, 9, 9, 8, 7,
                            6, 5, 4, 3], 's3')
    P.skin(head, 's', 3)
    f = head
    # one eye in sight, low under a flat brow, looking up from under it
    eye = {'rest': ["KKKKKK", "KEkEiK", ".iiii.", ".pppp."], 'joy': ["......", ".KKKK.", "K....K", ".pppp."],
           'surprise': ["KKKKKK", "KiEkiK", "KiEkiK", ".iiii.", ".pppp."], 'sadness': ["KKKK..", "KEkKKK", ".iiii.", ".pppp."],
           'anger': ["..KKKK", "KKKkEK", ".iiii.", ".pppp."]}[expr]
    f.stamp(17, 26, eye, {'K': 'x0', 'E': 'p3', 'k': 'x0', 'i': 'w3', 'p': 's2'})
    brow = {'rest': [(16, 23), (17, 23), (18, 24), (19, 24), (20, 24), (21, 24), (22, 25), (23, 25), (24, 25)],
            'joy': [(16, 22), (17, 21), (18, 21), (19, 21), (20, 21), (21, 21), (22, 22), (23, 22)],
            'surprise': [(16, 21), (17, 20), (18, 20), (19, 20), (20, 20), (21, 20), (22, 21), (23, 21)],
            'sadness': [(16, 25), (17, 25), (18, 24), (19, 24), (20, 23), (21, 23), (22, 22), (23, 22)],
            'anger': [(16, 22), (17, 22), (18, 23), (19, 23), (20, 24), (21, 24), (22, 25), (23, 25), (24, 25)]}[expr]
    f.pxs('n1', *brow); f.pxs('n0', *[(x, y + 1) for x, y in brow[::2]])
    f.pxs('s2', (27, 31), (27, 32), (28, 33)); f.pxs('s1', (26, 34), (27, 34)); f.px(26, 32, 's4')
    if expr == 'rest':                                     # pressed shut, one corner pulled into a smirk
        f.hline(23, 29, 37, 's0'); f.pxs('s0', (30, 36), (31, 35)); f.hline(25, 28, 38, 's2'); f.px(22, 37, 's1'); f.px(32, 35, 's2')
    elif expr == 'joy':
        f.hline(23, 29, 37, 's0'); f.pxs('s0', (22, 36), (30, 36), (31, 35)); f.hline(24, 28, 38, 'z0')
    elif expr == 'surprise':
        f.spans(36, [(25, 28), (24, 29), (25, 28)], 's0'); f.hline(25, 28, 37, 'r0')
    elif expr == 'sadness':
        f.hline(24, 29, 37, 's0'); f.pxs('s0', (23, 38), (30, 38)); f.hline(25, 28, 39, 's2')
    elif expr == 'anger':
        f.hline(23, 30, 37, 's0'); f.hline(24, 29, 36, 'x1'); f.hline(23, 30, 35, 's0'); f.pxs('s0', (22, 36), (31, 36), (26, 36))
    # hair: a dark choppy cap; the long fringe sweeps over the other eye
    hair = P.new()
    hair.sym(P.CX, 4, [5, 9, 12, 14, 15, 16, 16, 17, 17, 17, 17, 17, 17, 17], 'n1')
    for x, h in [(15, 2), (21, 3), (27, 2), (33, 3), (38, 2)]:
        for j in range(h):
            hair.hline(x - j, x + j, 5 - h + j, 'n1')
    edge = {14: 21, 15: 21, 16: 22, 17: 22, 18: 23, 19: 23, 20: 24, 21: 25, 22: 25, 23: 26, 24: 27, 25: 27, 26: 28, 27: 28,
            28: 29, 29: 29, 30: 30, 31: 30, 32: 31, 33: 31, 34: 30}
    tips = {33: 39, 34: 39, 35: 37, 36: 38, 37: 40, 38: 40, 39: 38, 40: 37}
    for y in range(14, 41):
        if y < 35:
            hair.hline(11, 15 if y < 30 else 14 if y < 33 else 13, y, 'n1')        # the short side
        if y in edge:
            hair.hline(edge[y], 44, y, 'n1')
        else:
            for x, yy in tips.items():
                if y <= yy:
                    hair.px(x, y, 'n1')
            hair.hline(41, 44, y, 'n1') if y < 37 else None
    hair.pxs('n1', (16, 14), (17, 14), (18, 14), (19, 14), (20, 14), (16, 15), (17, 15), (18, 15), (16, 16), (16, 17), (12, 35), (14, 34))
    hair.rim('n1', 'n0', [(1, 0)], 2)
    for x0, y0, x1, y1 in [(22, 6, 34, 30), (26, 5, 38, 28), (31, 6, 42, 24), (20, 7, 14, 16), (17, 7, 12, 20)]:
        hair.line(x0, y0, x1, y1, 'n0')
    for x0, y0, x1, y1 in [(20, 6, 23, 12), (24, 5, 29, 14), (16, 8, 14, 12), (29, 16, 33, 24)]:
        hair.line(x0, y0, x1, y1, 'n2')
    hair.pxs('n3', (21, 7), (22, 9), (25, 6), (26, 8), (27, 10))
    c = P.stack(back, body, head, hair)
    P.cast(c, 'n', 's', 2)
    P.jaw(c, 's', 'n', dirs=((1, 0),))
    return c
