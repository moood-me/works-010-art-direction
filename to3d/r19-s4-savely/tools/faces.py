"""The painted face layer, in the drawing's flat face coordinates (= the front view's x, y), projected onto the
fitted head from the front (build.py gives each head vertex uv = its rest x, y).
What is painted, by the style's rules (styles/s4-arcane/entry.json) and the character's own numbers (cast.py / cast2.py; drawing.FACE says what this face has):
  brows — the drawing's brow shape (person.brow_shape, the neutral expression), a dark block with hairs at the start;
  the upper lid's edge — the darkest, thickest line of the face, thicker to the outer corner, a short wing past it;
    it is laid along the fitted lids' real edge (where the ball shows from the front), so it rides on the lid;
  the lower lid — a thin line on its outer half; the crease — thin and pale, close above the edge;
  lips — the upper darker (it looks down), the lower lighter with a highlight, the mouth's line dark, corners short;
  blush on the cheeks, the nose's tip and the ears' line; the nostrils; the lines of a tired forty — nasolabial
  folds, a crease between the brows, soft bags under the eyes.
  age spots or freckles (P.freckles); brows are left out when they are 3D shells (drawing.FACE['brows3d']).
usage: python3 faces.py CACHE   → CACHE/out/face.png (6 px per drawing unit; x −80…80, y −125…130)"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drawing as DR, mesh as M  # noqa: E402
import person  # noqa: E402

C = sys.argv[1]
hf = np.load(os.path.join(C, 'head_fit.npz'))
fj = json.load(open(os.path.join(C, 'out', 'face.json')))
P = DR.person()
F = DR.FACE
HEAD, NOSE, NECK = DR.surfaces(P)
E = DR.NEUTRAL
PX = 6
X0, X1, Y0, Y1 = -80.0, 80.0, -125.0, 130.0
SS = 2                                                      # supersampling
Wp, Hp = int((X1 - X0) * PX), int((Y1 - Y0) * PX)


def to_px(pts):
    pts = np.asarray(pts, float)
    return [((x - X0) * PX * SS, (y - Y0) * PX * SS) for x, y in pts[:, :2]]


def rgba(h, a):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (int(a * 255),)


layer = Image.new('RGBA', (Wp * SS, Hp * SS), (0, 0, 0, 0))


def paint(fn, blur=0.0):
    """draw on a fresh layer with fn(draw), soften it by blur (units), composite onto the face"""
    global layer
    im = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(im))
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur * PX * SS))
    layer = Image.alpha_composite(layer, im)


def stroke(d, pts, w0, w1, col, wmid=None):
    """a tapered stroke: widths from w0 to w1 (units) along the points"""
    pts = np.asarray(pts, float)
    n = len(pts)
    ws = np.interp(np.linspace(0, 1, n), [0, 0.5, 1], [w0, wmid if wmid is not None else (w0 + w1) / 2, w1])
    tg = np.gradient(pts, axis=0); tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
    nr = np.c_[-tg[:, 1], tg[:, 0]]
    left = pts + nr * ws[:, None] / 2; right = pts - nr * ws[:, None] / 2
    d.polygon(to_px(np.r_[left, right[::-1]]), fill=col)


# ------------------------------------------------------------------ the eye openings as the fitted head shows them
V = hf['v']; T = hf['tris']
balls = [hf['scleraL_v'], hf['scleraR_v']]
bt = []
for s in 'LR':
    f = hf['sclera' + s + '_f']
    bt.append(np.array([[q[0], q[k], q[k + 1]] for q in f for k in range(1, len([x for x in q if x >= 0]) - 1)]))
VV = np.r_[V, balls[0], balls[1]]
TT = np.r_[T, bt[0] + len(V), bt[1] + len(V) + len(balls[0])]
col = np.r_[np.zeros((len(V), 3)), np.ones((len(balls[0]) + len(balls[1]), 3))]
box = (X0, X1, -Y1, -Y0)
img, _ = M.raster(VV * [1, -1, 1], TT, yaw=0.0, size=int((X1 - X0) * 3), box=box, col=col, light=(0, 0, 1))
ball = img[..., 0] > 128
RP = 3.0                                                    # raster px per unit
eyes = np.array(fj['eyes'])
margins = []
for k, (ex, ey, ez) in enumerate(eyes):
    xs = np.arange(ex - 24, ex + 24, 0.5)
    up, lo = [], []
    for x in xs:
        cx = int((x - X0) * RP)
        colm = ball[:, cx]
        rows = np.where(colm)[0]
        rows = rows[np.abs(Y0 + rows / RP - ey) < 16] if len(rows) else rows
        if len(rows) == 0:
            continue
        up.append((x, Y0 + rows.min() / RP)); lo.append((x, Y0 + rows.max() / RP))
    up, lo = np.array(up), np.array(lo)
    margins.append((up, lo))
    print('eye', k, 'opening x', up[:, 0].min(), up[:, 0].max(), 'top', up[:, 1].min().round(1), 'bottom', lo[:, 1].max().round(1))


def smooth_curve(c, it=3):
    c = c.copy()
    for _ in range(it):
        c[1:-1, 1] = 0.25 * c[:-2, 1] + 0.5 * c[1:-1, 1] + 0.25 * c[2:, 1]
    return c


pal = P.pal
# ------------------------------------------------------------------ soft tones first: blush, bags, lid shade, lines
def tones(d):
    for sd in (1, -1):
        bx, by, rx, ry, a = P.blush[0]
        d.ellipse(to_px([(sd * bx - rx, by - ry), (sd * bx + rx, by + ry)]), fill=rgba(pal['blush'], 0.22))
    ty = float(NOSE.tip)
    d.ellipse(to_px([(-7, ty - 11), (7, ty + 3)]), fill=rgba(pal['blush'], F.get('nose_blush', 0.2)))       # the nose's tip
    for sd in (1, -1):                                                      # the ears' line
        d.ellipse(to_px([(sd * 74 - 8, P.ear_y - 16), (sd * 74 + 8, P.ear_y + 18)]), fill=rgba(pal['blush'], F.get('ear_blush', 0.0)))


paint(tones, blur=4.0)


def lid_shade(d):
    for (up, lo), (ex, ey, ez) in zip(margins, eyes):
        c = smooth_curve(up)
        top = c.copy(); top[:, 1] -= 7.5 * np.sin(np.linspace(0.15, np.pi - 0.15, len(c))) + 1.0
        d.polygon(to_px(np.r_[c, top[::-1]]), fill=rgba(pal['lidshadow'], F.get('lid_shade', 0.35)))
        # bags: a soft darker arc under the eye (forty, tired)
        b = smooth_curve(lo); b2 = b.copy(); b[:, 1] += 2.5; b2[:, 1] += 2.5 + 4.5 * np.sin(np.linspace(0, np.pi, len(b)))
        d.polygon(to_px(np.r_[b, b2[::-1]]), fill=rgba('#a77a78', 0.22 * getattr(P, 'bags', 0.0) / 0.45))


paint(lid_shade, blur=1.6)


def lines(d):
    for pts, w, a in P.lines(E):
        stroke(d, pts, w * 0.6, w * 0.3, rgba(pal['mouthline'], a * 0.9), wmid=w)


paint(lines, blur=0.5)

# ------------------------------------------------------------------ lips (on the fitted mouth: its slit and corners)
MY, MW = fj['mouth']['y'], fj['mouth']['w']
mw = MW * F.get('mouth_w', 0.9)
ul, ll = P.ulip * F.get('ulip', 1.15), P.llip * 1.0
xs = np.linspace(-mw, mw, 41)
t = xs / mw
slit = MY + 0.4 * (1 - t ** 2) - 0.6 * t ** 2
up_edge = MY - ul * (1 - np.abs(t) ** 1.8) - 0.9 * np.exp(-(np.abs(t) - 0.28) ** 2 / 0.02) * (1 - np.abs(t)) + 0.9 * np.exp(-(t / 0.08) ** 2)
lo_edge = MY + ll * (1 - np.abs(t) ** 2.2) ** 0.8


def lips(d):
    d.polygon(to_px(np.r_[np.c_[xs, up_edge], np.c_[xs[::-1], slit[::-1]]]), fill=rgba(pal['lip_up'], 0.85))
    d.polygon(to_px(np.r_[np.c_[xs, slit], np.c_[xs[::-1], lo_edge[::-1]]]), fill=rgba(pal['lip_lo'], 0.8))


paint(lips, blur=0.45)


def lip_marks(d):
    # the highlight on the lower lip, the mouth's line, the corners
    hx = np.linspace(-mw * 0.4, mw * 0.25, 12)
    d.polygon(to_px(np.r_[np.c_[hx, MY + ll * 0.35 + 0.2 * (hx / mw) ** 2], np.c_[hx[::-1], MY + ll * 0.62 - 0.2 * (hx[::-1] / mw) ** 2]]), fill=rgba('#e8a8a0', F.get('lip_hi', 0.45)))
    stroke(d, np.c_[xs, slit], 0.5, 0.5, rgba(pal['mouth'], 0.85), wmid=1.1)
    for sd in (1, -1):
        stroke(d, [(sd * mw * 0.96, MY - 0.2), (sd * (mw + 2.2), MY + 1.2)], 0.8, 0.2, rgba(pal['mouthline'], 0.6))


paint(lip_marks, blur=0.3)

# ------------------------------------------------------------------ nostrils (where the fitted nose's holes are)
inner = hf['mouth_in'] * 0 + (np.linalg.norm(V[:, :1], axis=1) < 14)
nn = V[(V[:, 1] > 46) & (V[:, 1] < 60) & (np.abs(V[:, 0]) > 3) & (np.abs(V[:, 0]) < 13) & (V[:, 2] > 80)]


def nostrils(d):
    for sd in (1, -1):
        ny = float(NOSE.sub) - 1.0
        d.ellipse(to_px([(sd * 7.5 - 3.4, ny - 1.6), (sd * 7.5 + 3.4, ny + 1.6)]), fill=rgba(pal['nostril'], 0.7))


paint(nostrils, blur=0.6)

# ------------------------------------------------------------------ brows: the drawing's shape, a dark block, hairs at the start
def brows(d):
    for sd in (1, -1):
        pts = person.brow_shape(P, sd, E)
        d.polygon(to_px(pts), fill=rgba(pal['brow'], 0.92))


if not F.get('brows3d'):
    paint(brows, blur=0.35)


def brow_hairs(d):
    rnd = np.random.default_rng(3)
    for sd in (1, -1):
        for _ in range(F.get('brow_hairs', 26)):
            x = sd * rnd.uniform(9.5, 22); y = rnd.uniform(-22, -16)
            ang = np.radians(rnd.uniform(-75, -45)) * sd
            L = rnd.uniform(2.5, 4.5)
            stroke(d, [(x, y), (x + np.cos(ang) * L * sd * 0.6, y + np.sin(-abs(ang)) * L)], 0.45, 0.1, rgba(pal['brow'], 0.6))


if not F.get('brows3d'):
    paint(brow_hairs, blur=0.1)


def spots(d):
    for x, y, r in getattr(P, 'freckles', []):
        d.ellipse(to_px([(x - r, y - r), (x + r, y + r)]), fill=rgba(pal['freckle'], F.get('spots', 0.5)))


paint(spots, blur=0.25)


# ------------------------------------------------------------------ the lids' lines (on the real lid edges)
def lid_lines(d):
    for sd, (up, lo), (ex, ey, ez) in zip((1, -1), margins, eyes):
        c = smooth_curve(up, 4)
        c = c[np.argsort(sd * c[:, 0])]                     # from the inner corner outward
        n = len(c)
        w = np.interp(np.linspace(0, 1, n), [0, 0.35, 0.8, 1], [0.7, 1.6, 2.6, 2.2]) * P.lash_w[2] / 3.2
        tg = np.gradient(c, axis=0); tg /= np.linalg.norm(tg, axis=1, keepdims=True) + 1e-9
        nr = np.c_[-tg[:, 1], tg[:, 0]]; nr *= np.sign(-nr[:, 1:2] + 1e-9)        # pointing up
        inner_e = c + nr * 0.3                               # on the lid, just over the edge
        outer_e = c + nr * (0.3 + w)[:, None]
        # the wing: past the outer corner, a little up
        o = c[-1]; dvec = c[-1] - c[-4]; dvec /= np.linalg.norm(dvec)
        wing_tip = o + dvec * (P.eye_w * P.wing + 2.5) + np.array([0, -1.8]) if P.wing > 0 else o + dvec * 1.0
        d.polygon(to_px(np.r_[inner_e, [wing_tip], outer_e[::-1]]), fill=rgba(pal['lash'], 0.95))
        # the crease: thin, pale, close over the edge
        cr = c + nr * (P.crease + 3.2) * np.sin(np.linspace(0.25, np.pi - 0.25, n))[:, None]
        stroke(d, cr[2:-1], 0.25, 0.25, rgba(pal['mouthline'], 0.45), wmid=0.7)
        # the lower lid: thin, only the outer half
        b = smooth_curve(lo, 4); b = b[np.argsort(sd * b[:, 0])]
        half = b[len(b) // 2:]
        stroke(d, half + [0, 0.4], 0.1, 0.9, rgba(pal['lash'], 0.55), wmid=0.7)


paint(lid_lines, blur=0.25)

out = layer.resize((Wp, Hp), Image.LANCZOS)
out.save(os.path.join(C, 'out', 'face.png'))
print('face.png', out.size)
