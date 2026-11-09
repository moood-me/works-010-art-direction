"""Марат, about 35, a cook — huge, loud, merry, generous. Dark curls, a thick black beard, a laugh with teeth;
a white jacket with rolled sleeves, a terracotta apron, a towel on the shoulder, a ladle held high."""
import px

LEG = {'s': 'm3', 't': 'm2', 'u': 'm1', 'h': 'm4', 'K': 'b1', 'B': 'b2', 'D': 'b0', 'q': 'r0', 'j': 'r2'}

HEAD = [
    "...KKBKK.KBKK",
    ".KKBKKBKKKKKBKKK",
    "KBKKKBKKBKKKKBKKKD",
    "KKBKKKKKKKBKKKKKKKD",
    "KBKKKsssssssssKKBKD",
    "KKKsssssssssssssKKD",
    "KKKsKKKsssssKKKtKKD",
    "KBKsskssssssskstKKD",
    "KKKskskssssskskttKD",
    ".KKKppssthtssppKKD",
    ".KKKKKKKKuKKKKKKKD",
    ".KBKKKiiiiiiiKKKKD",
    ".KKKBKqjjjjjqKKKKD",
    "..KKKBKKKKKKKKKKD",
    "...KKKKBKKKKBKKD",
    "....KKBKKKKKKKD",
    "......KKKKKKD",
]


def front():
    c = px.Canvas(38, 56)
    Y = 8            # the head's top row; the ladle rises above it
    J, j2, j1 = 'c3', 'c2', 'c1'
    A, a1, a3 = 'o2', 'o1', 'o3'
    # jacket: a barrel
    c.spans(Y + 15, [(7, 12), (5, 30), (4, 30), (4, 30), (4, 30), (5, 30), (5, 30), (5, 30), (5, 30), (5, 30),
                     (5, 31), (5, 31), (5, 31), (5, 31), (6, 30), (6, 30)], J)
    c.spans(Y + 15, [(24, 29)], J)
    for y in range(Y + 17, Y + 31):
        c.hline(28, 31, y, j2) if y >= Y + 25 else c.hline(28, 30, y, j2)
    c.hline(13, 22, Y + 17, j2)                      # shadow of the beard
    # trousers and clogs
    for y in range(Y + 43, Y + 48):
        c.hline(11, 16, y, 'n2'); c.hline(20, 25, y, 'n2'); c.px(16, y, 'n1'); c.hline(24, 25, y, 'n1')
    c.spans(Y + 48, [(9, 16), (8, 16)], 'b2'); c.spans(Y + 48, [(20, 27), (20, 28)], 'b2')
    c.hline(8, 16, Y + 49, 'b1'); c.hline(20, 28, Y + 49, 'b1'); c.pxs('b3', (10, Y + 48), (11, Y + 48), (21, Y + 48), (22, Y + 48))
    # apron: bib, straps, a long skirt over the belly
    c.pxs(A, (12, Y + 17), (11, Y + 16), (23, Y + 17), (24, Y + 16))
    c.spans(Y + 18, [(12, 23)] * 7, A)
    c.spans(Y + 25, [(8, 27), (7, 28), (7, 28), (7, 28), (7, 28), (7, 28), (7, 28), (7, 28), (7, 28), (8, 28),
                     (8, 27), (8, 27), (8, 27), (8, 27), (8, 27), (9, 27), (9, 27), (9, 26)], A)
    c.hline(8, 27, Y + 25, a1)                        # the tie
    c.pxs('c3', (17, Y + 25), (18, Y + 25), (16, Y + 26), (19, Y + 27))   # its knot and ends
    for y in range(Y + 18, Y + 43):                   # shade on the right, light on the left of the belly
        r = c.get(27, y) == A and 27 or (c.get(26, y) == A and 26 or 23)
        c.hline(r - 2, r, y, a1) if y > Y + 25 else c.px(23, y, a1)
    for y in range(Y + 27, Y + 37):
        c.px(9, y, a3)
    c.vline(10, Y + 28, Y + 33, a3)
    c.vline(14, Y + 37, Y + 42, a1); c.vline(21, Y + 35, Y + 42, a1)      # folds
    c.rect(14, Y + 30, 7, 1, a1); c.vline(14, Y + 30, Y + 34, a1); c.vline(20, Y + 30, Y + 34, a1)  # pocket
    # towel over his left shoulder
    c.spans(Y + 14, [(25, 28), (25, 29), (25, 29), (25, 29), (25, 29), (25, 29), (25, 29), (25, 29), (25, 29)], 'w3')
    c.vline(29, Y + 15, Y + 22, 'w2'); c.hline(25, 29, Y + 20, 'r2'); c.pxs('w3', (25, Y + 23), (27, Y + 23), (29, Y + 23))
    # his left arm: fist on the hip
    c.spans(Y + 17, [(31, 33), (32, 34), (32, 35), (33, 35), (33, 36), (33, 36)], J)
    c.vline(36, Y + 21, Y + 22, j2); c.vline(35, Y + 19, Y + 20, j2)
    c.spans(Y + 23, [(32, 36)], j2)                   # the rolled cuff
    c.spans(Y + 24, [(32, 36), (31, 35), (30, 34)], 'm3')
    c.pxs('m2', (36, Y + 24), (35, Y + 25), (34, Y + 26), (33, Y + 26))
    c.spans(Y + 27, [(28, 32), (28, 32), (29, 31)], 'm3'); c.hline(29, 32, Y + 29, 'm2'); c.pxs('m2', (30, Y + 27), (32, Y + 28))
    # his right arm: up, with the ladle
    c.spans(Y + 11, [(1, 5), (1, 5), (1, 6), (2, 6), (2, 7), (3, 7), (3, 7)], J)
    c.vline(6, Y + 13, Y + 15, j2); c.hline(1, 5, Y + 11, j2)
    c.spans(Y + 6, [(2, 5), (1, 5), (1, 5), (1, 5), (1, 5)], 'm3'); c.vline(5, Y + 6, Y + 10, 'm2')
    c.spans(Y + 2, [(1, 5), (0, 5), (0, 5), (1, 5)], 'm3')           # the fist
    c.pxs('m2', (5, Y + 3), (5, Y + 4), (5, Y + 5), (2, Y + 4), (3, Y + 4), (4, Y + 4)); c.pxs('m4', (1, Y + 2), (2, Y + 2))
    c.vline(3, Y - 3, Y + 1, 'w2'); c.px(3, Y + 6, 'w2')             # the handle through the fist
    c.spans(Y - 9, [(2, 5), (1, 6), (1, 6), (1, 6), (2, 5)], 'w2')   # the bowl, turned to us, full of soup
    c.hline(2, 5, Y - 9, 'w3'); c.hline(2, 5, Y - 5, 'w1'); c.vline(6, Y - 7, Y - 6, 'w1')
    c.spans(Y - 8, [(2, 5), (2, 5), (3, 4)], 'o2'); c.hline(2, 4, Y - 8, 'o3'); c.px(1, Y - 8, 'w3')
    c.px(3, Y - 4, 'w2')
    # the head over all
    c.stamp(8, Y, HEAD, dict(__import__('sprite').BASE, **LEG))
    return c


VIEWS = {'front': front}


# ---------------------------------------------------------------- portrait
import portrait as P


def portrait(expr='rest'):
    body = P.new()                                         # the jacket fills the frame from edge to edge
    body.spans(42, [(10, 45), (6, 49), (3, 52), (1, 54)] + [(0, 55)] * 10, 'c3')
    body.rim('c3', 'c2', [(1, 0)], 6)
    body.spans(42, [(19, 36), (18, 37), (18, 37), (19, 36)], 'c2')                # the standing collar
    body.hline(18, 37, 45, 'c1'); body.vline(27, 46, 55, 'c1'); body.vline(28, 46, 55, 'c2')
    body.pxs('c1', (20, 50), (21, 50), (20, 54), (21, 54), (34, 50), (35, 50), (34, 54), (35, 54))   # two rows of buttons
    for (x0, x1) in ((14, 18), (37, 33)):                  # the apron's straps
        body.line(x0, 44, x1, 55, 'o2'); body.line(x0 + 1, 44, x1 + 1, 55, 'o2'); body.line(x0 + 2, 44, x1 + 2, 55, 'o1')
    body.spans(43, [(40, 50), (39, 52), (39, 53), (39, 54)] + [(39, 55)] * 9, 'w3')   # the towel on the shoulder
    body.vline(39, 44, 55, 'c1'); body.hline(40, 55, 51, 'r2'); body.hline(40, 55, 52, 'r2'); body.spans(45, [(50, 54)] + [(51, 55)] * 10, 'w2')
    head = P.new()
    head.sym(P.CX, 8, [8, 11, 13, 14, 15, 16, 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17,
                       17, 17, 17, 16, 16, 15, 14, 13, 12, 10], 'm3')
    head.spans(24, [(9, 10), (8, 10), (8, 10), (8, 10), (8, 10), (9, 10)], 'm3')
    head.spans(24, [(45, 46), (45, 47), (45, 47), (45, 47), (45, 47), (45, 46)], 'm2')
    head.pxs('m2', (9, 26), (9, 27)); head.pxs('m1', (46, 26), (46, 27))
    P.skin(head, 'm', 3)
    f = head
    # brows: thick; eyes that narrow in a laugh
    brow = {'rest': [(15, 20), (16, 19), (17, 18), (18, 18), (19, 18), (20, 18), (21, 18), (22, 19), (23, 19)],
            'joy': [(15, 19), (16, 18), (17, 17), (18, 17), (19, 17), (20, 17), (21, 17), (22, 18), (23, 18)],
            'surprise': [(15, 17), (16, 16), (17, 15), (18, 15), (19, 15), (20, 15), (21, 15), (22, 16), (23, 16)],
            'sadness': [(15, 21), (16, 21), (17, 20), (18, 20), (19, 19), (20, 19), (21, 18), (22, 18), (23, 17)],
            'anger': [(15, 18), (16, 18), (17, 19), (18, 19), (19, 20), (20, 20), (21, 21), (22, 21), (23, 22), (24, 22)]}[expr]
    P.both(f, 'b1', brow); P.both(f, 'b0', [(x, y + 1) for x, y in brow])
    eye = {'rest': [".KKKK.", "KikkiK", "..tt.."], 'joy': [".KKKK.", "K....K", "......"],
           'surprise': [".KKKK.", "KikkiK", "KikkiK", ".iiii."], 'sadness': ["KKK...", ".ikKKK", ".ikki."],
           'anger': ["...KKK", "KKKkki", ".ikki."]}[expr]
    P.eyes(f, 16, 23, eye, {'K': 'b0', 'i': 'w3', 'k': 'x0', 't': 'm2'})
    if expr in ('rest', 'surprise'):
        f.pxs('x1', (18, 24), (36, 24))
    if expr in ('rest', 'joy'):
        P.both(f, 'm2', [(14, 23), (13, 22), (14, 25), (16, 26), (17, 27), (18, 27), (19, 27), (20, 27), (21, 26)])   # laugh lines
    # the nose: broad
    f.vline(31, 23, 28, 'm2'); f.spans(28, [(25, 30), (24, 31), (23, 32), (23, 32)], 'm3')
    f.pxs('m2', (22, 30), (22, 31), (33, 30), (33, 31), (32, 29), (27, 32), (28, 32)); f.pxs('m1', (24, 32), (25, 32), (30, 32), (31, 32), (33, 32))
    f.pxs('m4', (25, 29), (26, 29), (25, 30), (20, 12), (21, 12), (22, 11), (23, 11), (19, 13), (20, 13))
    P.blob(f, 13, 28, ['.####.', '######', '######', '.####.'], 'z1', 'm3'); P.blob(f, 37, 28, ['.####.', '######', '######', '.####.'], 'z1', 'm3')
    # the beard
    b = P.new()
    b.spans(23, [(11, 12), (11, 13), (11, 13), (11, 13), (11, 14), (11, 14), (11, 15), (11, 16), (11, 18), (11, 20)], 'b1')
    b.spans(23, [(43, 44), (42, 44), (42, 44), (42, 44), (41, 44), (41, 44), (40, 44), (39, 44), (37, 44), (35, 44)], 'b1')
    b.spans(33, [(11, 44)] * 7, 'b1'); b.sym(P.CX, 40, [17, 16, 16, 15, 14, 12, 10, 7], 'b1')
    b.pxs('b1', (21, 32), (22, 32), (33, 32), (34, 32), (19, 31), (36, 31))
    b.rim('b1', 'b0', [(1, 0)], 3); b.rim('b1', 'b0', [(0, 1)], 1)
    for x, y in [(14, 30), (13, 34), (16, 37), (14, 40), (18, 42), (22, 44), (27, 45), (20, 34), (24, 41), (30, 43),
                 (33, 41), (36, 37), (38, 33), (17, 33), (31, 34), (25, 34), (35, 44), (39, 40), (12, 26), (42, 28)]:
        b.pxs('b2', (x, y), (x + 1, y - 1), (x + 2, y))              # curls: small arcs
    f.paste(b)
    if expr in ('rest', 'joy'):                            # the laugh: teeth, the mouth's dark, a tongue
        top = 35 if expr == 'rest' else 34
        f.spans(top, [(21, 34), (21, 34)] + [(22, 33)] * (38 - top) + [(23, 32), (25, 30)], 'r0')
        f.spans(top, [(22, 33), (22, 33)], 'x1'); f.pxs('w2', (22, top + 1), (33, top + 1), (33, top))
        f.spans(39, [(25, 30), (25, 30)], 'r2'); f.hline(24, 31, 38, 'r2'); f.pxs('x3', (25, 38), (26, 38), (27, 39)); f.vline(28, 38, 39, 'r1')
        f.hline(24, 31, 41, 'm2'); f.hline(25, 30, 41, 'm3')
    elif expr == 'surprise':
        f.spans(36, [(26, 29), (25, 30), (24, 31), (24, 31), (25, 30), (26, 29)], 'r0'); f.hline(25, 30, 37, 'x1'); f.hline(26, 29, 40, 'r2')
        f.hline(26, 29, 42, 'm2')
    elif expr == 'sadness':
        f.hline(24, 31, 37, 'm1'); f.pxs('m1', (23, 38), (32, 38)); f.hline(25, 30, 38, 'm3'); f.hline(25, 30, 39, 'm2')
    elif expr == 'anger':
        f.spans(36, [(22, 33), (22, 33), (23, 32)], 'r0'); f.hline(23, 32, 37, 'x1'); f.pxs('w2', (25, 37), (28, 37), (31, 37))
        f.hline(25, 30, 39, 'm2')
    # hair: a cloud of dark curls
    hair = P.new()
    for cx, cy, r in [(13, 15, 4), (15, 10, 4), (19, 6, 4), (25, 4, 4), (31, 4, 4), (37, 6, 4), (41, 10, 4), (43, 15, 4),
                      (11, 20, 3), (44, 20, 3), (22, 9, 5), (33, 9, 5), (28, 8, 5)]:
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 1:
                    hair.px(x, y, 'b1')
    hair.spans(12, [(14, 42), (13, 43), (17, 21), (14, 17)], 'b1'); hair.spans(14, [(35, 42), (38, 42), (40, 43), (41, 44), (42, 44), (42, 44), (43, 44)], 'b1')
    hair.spans(16, [(11, 15), (11, 14), (11, 13), (11, 13), (11, 12), (11, 12), (11, 12)], 'b1')
    hair.rim('b1', 'b0', [(1, 0)], 3); hair.rim('b1', 'b0', [(0, 1)], 1)
    for x, y in [(12, 13), (15, 8), (19, 4), (24, 2), (30, 2), (18, 10), (23, 7), (28, 6), (14, 17), (21, 12), (26, 10),
                 (33, 5), (36, 9), (31, 11), (39, 13), (16, 14), (35, 3)]:
        hair.pxs('b2', (x, y), (x + 1, y - 1), (x + 2, y - 1), (x + 3, y))
    for x, y in [(15, 8), (19, 4), (24, 2), (18, 10), (23, 7)]:
        hair.pxs('b3', (x + 1, y - 1), (x + 2, y - 1))
    c = P.stack(body, head, hair)
    P.cast(c, 'b', 'm', 2)
    return c
