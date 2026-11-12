"""The drawing as numbers: Аня's noir drawing (styles/s15-noir/tools: head.py, cast.py, figures.py) turned into the
silhouettes the 3D is fitted to. Units here: Р1's — the eye line y=0, y down, shoe soles at y=1378, x to the picture's
right; a head unit of С15 (crown −100, chin +98, eye line +12) is HS units; a unit of the figure (soles 0, up negative)
is FS units. 3D: metres, y up, the figure faces +z, its left +x. Front view: x → 3D x; the profile (drawn facing
left) is turned to face +z: z = −(x − ZC) · HS."""
import os, re, sys
import numpy as np

S15 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'styles', 's15-noir', 'tools')
sys.path.insert(0, S15)
import noir, head as NH, cast as NC  # noqa: E402

P = NC.ANYA
HS = 1.37               # units per head unit: the drawing's head is 1/5.6 of the figure (Р1's Аня: 1/6.4)
EYE = P['eye_y']        # 12
ZC = 17.0               # the profile's x where the neck's axis stands
FLOOR = 1378.0          # shoe soles
CROWN = (-112 - EYE) * HS   # top of the hair (head y −112)
K = 1.62 / (1378 + 142)     # metres per unit (Р1's)
HEIGHT = (FLOOR - CROWN) * K
SKULL = (-100 - EYE) * HS      # the skull's crown
CHIN = (98 - EYE) * HS         # the chin
FS = (FLOOR - SKULL) / 734.0   # units per figure unit: the skull's crown is 734 figure units over the soles
hu = lambda x, y: (x * HS, (y - EYE) * HS)                 # head units → units (front)
side = lambda x, y: (-(x - ZC) * HS, (y - EYE) * HS)       # head units of the profile → (z, y) units
fy = lambda y: FLOOR + y * FS                              # a figure height (negative up) → units


def to3(xd, yd):
    return np.asarray(xd) * K, (FLOOR - np.asarray(yd)) * K


def to_d(y3):
    return FLOOR - np.asarray(y3) / K


def sample(d, n=24):
    """An absolute SVG path (M L C Q Z) → list of closed/open polylines (arrays N×2)."""
    toks = re.findall(r'[MLCQZmlcqz]|-?\d+(?:\.\d+)?', d)
    out, cur, i, cmd, p0 = [], [], 0, None, None
    pos = np.zeros(2)
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t; i += 1
            if cmd in 'Zz':
                if cur:
                    cur.append(cur[0].copy()); out.append(np.array(cur)); cur = []
                pos = p0.copy() if p0 is not None else pos
                continue
        if cmd == 'M':
            if cur: out.append(np.array(cur))
            pos = np.array([num(), num()]); p0 = pos.copy(); cur = [pos.copy()]; cmd = 'L'
        elif cmd == 'L':
            pos = np.array([num(), num()]); cur.append(pos.copy())
        elif cmd == 'C':
            c1 = np.array([num(), num()]); c2 = np.array([num(), num()]); e = np.array([num(), num()])
            for s in np.linspace(0, 1, n + 1)[1:]:
                cur.append((1 - s) ** 3 * pos + 3 * (1 - s) ** 2 * s * c1 + 3 * (1 - s) * s * s * c2 + s ** 3 * e)
            pos = e
        elif cmd == 'Q':
            c1 = np.array([num(), num()]); e = np.array([num(), num()])
            for s in np.linspace(0, 1, n + 1)[1:]:
                cur.append((1 - s) ** 2 * pos + 2 * (1 - s) * s * c1 + s * s * e)
            pos = e
        else:
            raise ValueError(cmd)
    if cur: out.append(np.array(cur))
    return out


def span(polys, y):
    """Where a horizontal line at drawing-y crosses the shapes: (min x, max x) or None."""
    xs = []
    for P in polys:
        a, b = P[:-1], P[1:]
        m = (a[:, 1] - y) * (b[:, 1] - y) <= 0
        for p, q in zip(a[m], b[m]):
            if p[1] == q[1]: xs += [p[0], q[0]]
            else: xs.append(p[0] + (y - p[1]) / (q[1] - p[1]) * (q[0] - p[0]))
    return (min(xs), max(xs)) if xs else None


def profile(d, ys, n=24):
    P = sample(d, n)
    r = [span(P, y) for y in ys]
    return np.array([[np.nan, np.nan] if s is None else s for s in r])


# ---------------------------------------------------------------- the shapes
def _path(pts, conv):
    return noir.d([tuple(conv(*p[:2])) + tuple(p[2:]) for p in pts])


_fo = NH.front_outline(P)
_so = NH.side_outline(P)
F_ORDER = ['crown', 'tr', 'templer', 'cheekr', 'jawr', 'chinr', 'chinl', 'jawl', 'cheekl', 'templel', 'tl']
S_ORDER = ['crown', 'backtop', 'back', 'occ', 'nape', 'jaw', 'chinb', 'chin', 'chinfold', 'lipl', 'mouth', 'lipu', 'nosebase', 'tip', 'root', 'brow', 'fore']
FRONT = dict(face=_path([_fo[k] for k in F_ORDER], hu))
SIDE = dict(face=_path([_so[k] for k in S_ORDER], side))

# the hair (cast.py anya_hair), head units: the outer mass in front (the back and the front forms), the profile's; the
# face's window — the hairline: a side parting on the picture's right, the fringe swept to the picture's left; below
# the temples the hair goes behind the ears
HAIR_BACK_F = [(-72, -40, 's'), (-52, -100, 's'), (0, -112, 's'), (56, -100, 's'), (80, -40, 's'), (86, 60, 's'), (98, 150), (64, 172), (-58, 174), (-94, 150), (-82, 60, 's')]
HAIR_FRONT_F = [(14, -108, 's'), (56, -98, 's'), (76, -50, 's'), (78, 6), (66, -22, 's'), (52, -56, 's'), (26, -74), (-8, -64, 's'), (-44, -42, 's'), (-62, -12), (-73, 4),
                (-76, -50, 's'), (-52, -96, 's'), (-14, -112, 's')]
HAIR_BACK_S = [(10, -106, 's'), (78, -92, 's'), (110, -40, 's'), (108, 50, 's'), (118, 130), (94, 174), (66, 150), (44, 178), (34, 100), (46, 40)]
HAIR_FRONT_S = [(-44, -84, 's'), (10, -108, 's'), (72, -96, 's'), (106, -40, 's'), (102, 30), (74, 46), (60, 10, 's'), (46, -22, 's'), (22, -28), (14, -54, 's'), (-18, -60),
                (-48, -38, 's'), (-63, -16), (-62, -56, 's')]
HAIR = dict(back_f=_path(HAIR_BACK_F, hu), front_f=_path(HAIR_FRONT_F, hu), back_s=_path(HAIR_BACK_S, side), front_s=_path(HAIR_FRONT_S, side))
# the window's two edges from the parting down: (head y, head x)
WIN_R = [(-74, 26), (-56, 52), (-22, 66), (6, 78)]                    # the picture's right edge (the character's left)
WIN_L = [(-74, 26), (-64, -8), (-42, -44), (-12, -62), (4, -73)]      # the fringe's edge

# the figure (figures.py anya, drawn in three-quarter, in a pose): its heights; the turn sheet's bust gives the
# shoulders in front (±108 head units)
Y_SH, Y_ARMPIT, Y_WAIST, Y_JHEM, Y_HEM = fy(-552), fy(-500), fy(-440), fy(-420), fy(-222)
Y_V, Y_TOP = fy(-506), fy(-536)      # where the jacket's V closes; the blue top's neckline in it
