"""The paints laid on as pictures, from the drawing's own numbers (cast.TIM, head.py blush/freckles/eye):
- face.png: the skin seen from the front (head units −0.5…0.5 both ways → 0…1), carried onto the head by a front
  projection: the blush on the cheeks, the freckles (the drawing's own seeded scatter), the warm socket tone round the
  eyes, a warm nose tip; the skin itself is the drawing's skin.
- iris.png: the glass eye's paint seen from the front (−1…1 of the ball's radius): the white with a cool shade at
  the edge, the iris with its dark ring and pupil (the drawing's radial stops).
Written to the folder's tools/web/tex (the viewer reads them) and used by the renders."""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import drawing
from drawing import P, H0
from common import HERE

OUT = os.path.join(HERE, 'web', 'tex')
os.makedirs(OUT, exist_ok=True)


def rgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def mix(a, b, t):
    return a * (1 - t) + b * t


def face(size=1024):
    S = size
    px = lambda x, y: ((x + 0.5) * S, (y + 0.5) * S)          # the drawing's head units (y down) → pixels
    img = np.tile(rgb(P['skin']), (S, S, 1))

    def layer(draw_fn, blur):
        m = Image.new('L', (S, S), 0); d = ImageDraw.Draw(m); draw_fn(d)
        if blur: m = m.filter(ImageFilter.GaussianBlur(blur))
        return np.asarray(m, float)[..., None] / 255

    # blush: an ellipse 0.07 × 0.045 at phi = ±eye_phi·1.15, y = eye_y + 0.1, soft
    def blush(d):
        for side in (-1, 1):
            x, y, _ = H0.surf(side * P['eye_phi'] * 1.15, P['eye_y'] + 0.1)
            a, b = 0.07 * 1.15, 0.045 * 1.15
            d.ellipse([*px(x - a, y - b), *px(x + a, y + b)], fill=255)
    a = layer(blush, S * 0.03) * P['blush'] * 1.1
    img = mix(img, rgb(P['blush_col']), a)
    # the socket tone round the eyes (the drawing: a soft darker skin under and over the lids)
    def socket(d):
        for side in (-1, 1):
            x, y, _ = H0.surf(side * P['eye_phi'], P['eye_y'])
            d.ellipse([*px(x - 0.13, y - 0.11), *px(x + 0.13, y + 0.09)], fill=255)
    a = layer(socket, S * 0.025) * P.get('socket_a', 0.2) * 0.8
    img = mix(img, mix(rgb(P['skin']), rgb('#7a4050'), 0.55), a)
    # the nose: a warm tip
    def nose(d):
        y = P['nose_tip'] - 0.01
        d.ellipse([*px(-0.05, y - 0.04), *px(0.05, y + 0.035)], fill=255)
    a = layer(nose, S * 0.015) * 0.35
    img = mix(img, rgb('#e07a6a'), a)
    # the chin and the jaw's underside a little warmer (light through resin)
    # freckles: the drawing's own scatter (head.freckles, seed 3) — on the face, not where the eyes are
    r = random.Random(3)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, 'RGBA')
    col = rgb('#9a5a3a')
    for i in range(P['freckles']):
        side = -1 if i % 2 else 1
        phi = side * (0.08 + r.random() * 0.45)
        y = P['eye_y'] + 0.06 + r.random() * 0.07
        rr = 0.004 + r.random() * 0.003
        al = 0.35 + r.random() * 0.3
        x, yy, _ = H0.surf(phi, y)
        cx, cy = px(x, yy)
        d.ellipse([cx - rr * S, cy - rr * S, cx + rr * S, cy + rr * S], fill=(*col.astype(int), int(al * 255)))
    im = im.filter(ImageFilter.GaussianBlur(0.8))
    im.save(os.path.join(OUT, 'face.png'))


def iris(size=512):
    S = size
    y, x = np.mgrid[0:S, 0:S]
    u = (x + 0.5) / S * 2 - 1; v = (y + 0.5) / S * 2 - 1
    r = np.hypot(u, v)
    white = rgb(P.get('white', '#efe6dc'))
    img = np.tile(mix(white, rgb('#ffffff'), 0.25), (S, S, 1))
    # the iris: radius iris_r of an eye_r ball (front view), radial stops of head.eye()
    ri = P['iris_r'] / P['eye_r']
    c = rgb(P['iris'])
    stops = [(0, mix(c, 0, 0.55)), (0.32, mix(c, 0, 0.3)), (0.55, c), (0.85, mix(c, 255, 0.12)), (0.93, mix(c, 0, 0.55)), (1, mix(c, 0, 0.7))]
    t = r / ri
    ic = np.zeros((S, S, 3))
    for k in range(3):
        ic[..., k] = np.interp(t, [s for s, _ in stops], [col[k] for _, col in stops])
    # fibres: fine radial streaks
    ang = np.arctan2(v, u)
    fib = 0.9 + 0.1 * np.sin(ang * 61) * np.sin(ang * 17 + 1.3)
    ic *= fib[..., None]
    a = np.clip((ri - r) / 0.012, 0, 1)[..., None]
    img = mix(img, ic, a)
    pu = 0.38 * ri
    img = mix(img, rgb('#120c0c'), np.clip((pu - r) / 0.01, 0, 1)[..., None])
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(OUT, 'iris.png'))


if __name__ == '__main__':
    face(); iris()
    print('paints in', OUT)
