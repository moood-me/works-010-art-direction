"""Тим, about 8 — mischievous, curious. Sandy tousled hair, ears that stick out, a striped shirt, a plaster on the
knee; he waves."""
LEG = {'H': 't2', 'I': 't3', 'J': 't4', 'G': 't1', 'R': 'r2', 'q': 'r1', 'W': 'w3', 'w': 'w2',
       'U': 'u2', 'v': 'u1', 'P': 'c2', 'N': 'r2', 'n': 'r1'}

FRONT = [
    ".........H...H",
    "........HIH.HIH..H",
    ".......HIIIHIIHHHH",
    "......HIIJIIIHHHHHG",
    ".....HIIJIIHHHHHHHHG",
    ".....HIIHHHsHHsHHHHG",
    ".s.s.HIHsssssssssHHG",
    ".sss.HHssiksssikstHG",
    ".sst.sGsskkssskkstGt",
    "..ss.sssspsssssspstst",
    "...ss..sssuiiiusst",
    "....ss..sssssssst",
    ".....RR..tsssstt",
    "......RRRRRuuuRRqR",
    "........WWWWWWWWwRR",
    "........RRRRRRRRq.ss",
    "........WWWWWWWWw..ss",
    "........RRRRRRRRq...s",
    "........WWWWWWWWw.ss",
    "........RRRRRRRRsss",
    "........WWWWWWWWss",
    "........UUUUUUUvv",
    "........UUUUUUUvv",
    ".......UUUUUUUUUvv",
    "........UUUU.UUUvv",
    "........UUUv.UUUvv",
    ".........sP...st",
    ".........st...st",
    ".........st...st",
    ".........Ww...Ww",
    "........NNN...NNN",
    ".......iNNN...NNNi",
]
Q = FRONT[:5] + [
    "....HIIHHHHsHHsHHHG",
    ".s.sHIHHHssssssssHG",
    ".sssHHHHssiksssskst",
    ".sstHHGssskksssskst",
    "..ssHGGssspsssssspt",
    "...ssGGsssssuiiiust",
    "....ss.sssssssssst",
    ".....RR.tssssstt",
    "......RRRRRuuuRqR",
    "........WWWWWWWwRR",
    "........RRRRRRRq.s",
    "........WWWWWWWw.ss",
    "........RRRRRRRq..s",
    "........WWWWWWWw.s",
    "........RRRRRRRss",
    "........WWWWWWWs",
    "........UUUUUUvv",
    "........UUUUUUvv",
    ".......UUUUUUUUvv",
    "........UUUUUUUvv",
    "........UUUv.UUvv",
    ".........sP..st",
    ".........st..st",
    ".........st..st",
    ".........Ww..Ww",
    ".........NNN.NNN",
    ".........NNNiNNNi",
]
SIDE = FRONT[:5] + [
    "....HIIHHHHHHsHHHG",
    "....HIHHHHHsssssss",
    "....HHHHHHssssikss",
    "....HHHGstsssskksst",
    "....HHGGstssssspss",
    ".....GGGsssssuiist",
    "........ssssssssst",
    ".........tssssst",
    ".........RRRuRR",
    ".........WqqqWw",
    ".........RqqqRq",
    ".........WWssWw",
    ".........RRRssq",
    ".........WWWssw",
    ".........RRRRss",
    ".........WWWWWw",
    ".........UUUUUv",
    ".........UUUUUv",
    "........UUUUUUv",
    "........UUUvUUv",
    "........UUv.UUv",
    ".........st.sP",
    ".........st.st",
    ".........st.st",
    ".........Ww.Ww",
    ".........NN.NNN",
    ".........NNiNNNi",
]
VIEWS = {'front': FRONT, 'q': Q, 'side': SIDE}


# ---------------------------------------------------------------- portrait
import portrait as P

EYE = {'rest': [".KKKK.", "KEkkEK", "iEkkEi", ".EEEE."],
       'joy': ["......", ".KKKK.", "K....K", "......"],
       'surprise': [".KKKK.", "KiEEiK", "iEkkEi", "iEkkEi", ".iEEi."],
       'sadness': ["......", "KKKKK.", "iEkkEK", ".EEEEi"],
       'anger': ["..KKK.", "KKkkEi", "iEkkEi", ".EEEE."]}


def portrait(expr='rest'):
    S = {'K': 'b1', 'i': 'w3', 'E': 'b3', 'k': 'x0'}
    body = P.new()
    body.rect(24, 37, 8, 7, 's2'); body.spans(39, [(24, 31), (25, 31)], 's1')
    rows = [(21, 34), (17, 38), (14, 41), (12, 43), (11, 44), (10, 45), (9, 46), (9, 46), (8, 47), (8, 47), (8, 47), (8, 47)]
    for j, (a, b) in enumerate(rows):                     # the striped shirt
        k = ('r2', 'r1') if j % 4 < 2 else ('w3', 'w2')
        body.hline(a, b, 44 + j, k[0]); body.hline(b - 4, b, 44 + j, k[1])
    body.spans(43, [(23, 32), (24, 31), (25, 30)], 's3'); body.hline(28, 31, 43, 's2'); body.hline(25, 30, 45, 's2')
    body.pxs('r1', (22, 44), (33, 44), (23, 45), (32, 45), (24, 46), (31, 46))   # the neck of the shirt
    head = P.new()
    head.sym(P.CX, 11, [7, 10, 12, 13, 14, 14, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 14, 14, 13,
                        13, 12, 11, 9, 7], 's3')
    head.spans(23, [(11, 12), (10, 12), (10, 12), (10, 12), (10, 12), (11, 12)], 's3')    # ears that stick out
    head.spans(23, [(43, 44), (43, 45), (43, 45), (43, 45), (43, 45), (43, 44)], 's2')
    head.pxs('s2', (11, 25), (11, 26), (12, 27)); head.pxs('s1', (44, 25), (44, 26), (43, 27))
    P.skin(head, 's')
    f = head
    P.eyes(f, 17, 23, EYE[expr], S)
    if expr in ('rest', 'surprise', 'sadness', 'anger'):
        gy = 24 if expr != 'surprise' else 25
        f.pxs('x1', (19, gy), (35, gy)); f.pxs('x1', (18, gy)) if expr == 'rest' else None
        f.pxs('x1', (34, gy)) if expr == 'rest' else None
    bl = {'rest': [(17, 20), (18, 19), (19, 19), (20, 19), (21, 19), (22, 20)],
          'joy': [(17, 19), (18, 18), (19, 18), (20, 18), (21, 18), (22, 19)],
          'surprise': [(17, 18), (18, 17), (19, 17), (20, 17), (21, 17), (22, 18)],
          'sadness': [(17, 21), (18, 21), (19, 20), (20, 20), (21, 19), (22, 19)],
          'anger': [(17, 19), (18, 19), (19, 20), (20, 20), (21, 21), (22, 21), (23, 22)]}[expr]
    br = P.mirror_pts(bl)
    if expr == 'rest':                                     # one brow cocked
        br = [(x, y - 2) for x, y in br]
    f.pxs('t1', *bl); f.pxs('t1', *br)
    f.pxs('s2', (28, 30), (29, 30), (29, 29)); f.pxs('s4', (27, 28), (27, 29))
    P.blob(f, 15, 30, ['.###.', '#####', '.###.'], 'z0', 's3'); P.blob(f, 36, 30, ['.###.', '#####', '.###.'], 'z0', 's3')
    f.pxs('s2', (17, 29), (20, 29), (22, 31), (35, 29), (38, 29), (33, 31))        # freckles
    if expr == 'rest':                                     # a lopsided grin with a gap in the teeth
        f.pxs('r0', (22, 33), (23, 34), (33, 32), (32, 33), (33, 33))
        f.hline(23, 32, 34, 'r0'); f.hline(24, 31, 35, 'x1'); f.px(27, 35, 'r0'); f.hline(25, 31, 36, 'r0')
        f.hline(24, 32, 33, 's3'); f.hline(24, 32, 34, 'x1'); f.px(27, 34, 'r0'); f.pxs('r0', (23, 34), (33, 34))
        f.hline(24, 32, 33, 'r0'); f.hline(24, 31, 35, 'r1'); f.hline(26, 30, 35, 'x3'); f.pxs('r0', (24, 35), (32, 35))
        f.hline(25, 31, 36, 'r0')
    elif expr == 'joy':
        f.pxs('r0', (21, 32), (34, 32)); f.hline(22, 33, 33, 'r0'); f.hline(23, 32, 34, 'x1'); f.px(27, 34, 'r0')
        f.pxs('r0', (22, 34), (33, 34), (23, 35), (32, 35), (24, 36), (31, 36)); f.hline(24, 31, 35, 'r1')
        f.hline(25, 30, 36, 'x3'); f.hline(25, 30, 37, 'r0')
    elif expr == 'surprise':
        f.spans(33, [(26, 29), (25, 30), (25, 30), (25, 30), (26, 29)], 'r0'); f.spans(34, [(26, 29), (26, 29)], 'r1')
        f.hline(26, 29, 34, 'x1')
    elif expr == 'sadness':
        f.pxs('r0', (23, 36), (24, 35), (31, 35), (32, 36)); f.hline(25, 30, 34, 'r0'); f.hline(26, 29, 36, 's2')
    elif expr == 'anger':
        f.hline(24, 31, 34, 'r0'); f.hline(24, 31, 35, 'x1'); f.hline(24, 31, 36, 'r0'); f.pxs('r0', (23, 35), (32, 35), (26, 35), (29, 35))
    # hair: a tousled cap, spikes on top, a jagged fringe
    hair = P.new()
    hair.sym(P.CX, 5, [7, 11, 13, 15, 16, 16, 17, 17, 17, 17], 't2')
    for x in range(11, 45):
        edge = 15 + [0, 1, 2, 4, 2, 1][(x - 13) % 6] if 14 <= x <= 41 else 22
        hair.vline(x, 15, edge, 't2')
    for x, h in [(17, 2), (22, 4), (29, 5), (35, 3), (40, 2)]:        # spikes
        for j in range(h):
            hair.hline(x - j, x + j + (1 if x % 2 else 0), 5 - h + j + 1, 't2')
    hair.rim('t2', 't1', [(1, 0)], 2); hair.rim('t2', 't1', [(0, 1)], 1)
    for x, y, n in [(18, 7, 6), (15, 8, 8), (14, 9, 7), (13, 10, 5), (12, 11, 3), (27, 6, 5), (29, 7, 6), (32, 8, 4),
                    (20, 2, 2), (27, 1, 2), (16, 14, 2), (22, 14, 2), (28, 14, 2)]:
        hair.hline(x, x + n - 1, y, 't3')
    hair.pxs('t4', (17, 8), (18, 8), (19, 8), (16, 9), (30, 7), (31, 7))
    for x0, y0, x1, y1 in [(24, 6, 20, 14), (31, 6, 36, 14), (37, 8, 42, 16)]:
        hair.line(x0, y0, x1, y1, 't1')
    c = P.stack(body, head, hair)
    P.cast(c, 't', 's', 2)
    return c
