# The hairstyles of experiments/hair (В1) that this page repeats with Blender's hair tools: the guide curves (the
# groom an artist would draw with Blender's curve sculpt tools, here written as numbers), the hairline, the parts
# (each its own Curves object on its own piece of scalp, as artists split fringe / sides / back) and the settings of
# Blender's node groups (build.py). Coordinates are three.js's (Y up, the face toward +Z, +X the person's left).
import math
import numpy as np
from scene import strand, sph, hairline

def grid(line, rows, cols, top=1.4, jitter=0.5, seed=1, keep=lambda th, ph: True, th0=-math.pi, th1=math.pi):
    rng = np.random.default_rng(seed); out = []
    for j in range(cols):
        th = th0 + (j + 0.5 + jitter * rng.uniform(-0.5, 0.5)) * (th1 - th0) / cols
        lo = line(th) + 0.03
        for i in range(rows):
            ph = lo + (top - lo) * (i / max(1, rows - 1)) ** 0.8
            if keep(th, ph): out.append((th, ph))
    return out

def gwen(c, r, ey):
    """Gwen: a blonde chin-length bob, a side part on her left, the fringe swept over her right brow."""
    line = hairline(0.62, 0.05, -0.62)
    fr = lambda th, ph: abs(th - 0.1) < 0.95 and ph > 0.5
    fringe = [strand(c, r, th, ph, 0.42, ey + 0.035 - 0.05 * max(0, -th - 0.2), lift=0.07, sweep=-0.55 + 0.2 * th,
                     flare=0.012, curl=0.004, swing=-0.015) for th, ph in grid(line, 4, 26, keep=fr)]
    rest = []
    for th, ph in grid(line, 4, 22, keep=lambda th, ph: not fr(th, ph)):
        tip = ey - 0.115 + 0.03 * (abs(th) / math.pi) ** 2
        rest.append(strand(c, r, th, ph, -0.05, tip, lift=0.09, sweep=0.25 * math.sin(th) if ph > 1.0 else 0, flare=0.025, curl=0.02))
    return dict(skin=0xf1cdb4, line=line, melanin=(0.1, 0.35), scalp=0xb89a60, dist=1.15 * 1.3,
                parts=[dict(region=fr, guides=fringe, clump=0.03), dict(region=lambda th, ph: not fr(th, ph), guides=rest)])

def alva(c, r, ey):
    """Alva: long straight brown hair, a centre part, down to the chest; in front of the shoulders at the sides."""
    line = hairline(0.62, 0.02, -0.7)
    FRONT = 1.5
    parts = []
    for sgn in (1, -1):   # the front halves, each side of the part
        G = []
        for th, ph in grid(line, 4, 9, th0=0.03 if sgn > 0 else -FRONT, th1=FRONT if sgn > 0 else -0.03, seed=2 + sgn):
            a = abs(th)
            sweep = sgn * max(0.0, 1.0 - a)                # off the face to the side, as it comes down
            out = np.array([sgn * 0.75, 0, 0.66]); tip = ey - 0.34 + 0.05 * a
            G.append(strand(c, r, th, ph, -0.2, tip, lift=0.08, sweep=sweep, flare=0.03 + 0.03 * a, n=32, out=out / np.linalg.norm(out)))
        parts.append(dict(region=(lambda th, ph: 0 < th < FRONT) if sgn > 0 else (lambda th, ph: -FRONT < th <= 0), guides=G))
    G = []
    for th, ph in grid(line, 4, 16, th0=FRONT, th1=2 * math.pi - FRONT, seed=7):
        th = (th + math.pi) % (2 * math.pi) - math.pi; a = abs(th)
        out = np.array([math.sin(th) * 0.5, 0, math.cos(th)])
        sweep = (0.35 * math.copysign(1, th) * (a - FRONT) / (math.pi - FRONT)) if ph > 0.9 else 0.0
        G.append(strand(c, r, th, ph, -0.15, ey - 0.43 + 0.04 * (math.pi - a), lift=0.08, flare=0.03, n=32, out=out / np.linalg.norm(out)))
    parts.append(dict(region=lambda th, ph: abs(th) >= FRONT, guides=G))
    return dict(skin=0xf0c8b0, line=line, melanin=(0.42, 0.6), scalp=0x3a2412, dist=1.8 * 1.3, ty=-0.12,
                parts=parts, clump=0.05, clump_shape=0.45, tip_spread=0.004, shrink_on=['body', 'tshirt'], shrink=0.008)

def kpony(c, r, ey):
    """K-pop ponytail: combed back to a high tie at the back of the crown, the tail down the back; two thin locks in
    front of the ears."""
    line = hairline(0.62, 0.05, -0.62)
    T = sph(c, r, math.pi, 0.62, 1.12)                      # the tie
    back = np.array([0, 0, -1.0])
    side = lambda th, ph: abs(abs(th) - 1.25) < 0.22 and ph < 0.45
    G = []
    rng = np.random.default_rng(5)
    for th, ph in grid(line, 5, 24, keep=lambda th, ph: not side(th, ph)):
        a0 = (sph(c, r, th, ph) - c) / r; a1 = (T - c) / r / 1.12; a0 /= np.linalg.norm(a0); a1 /= np.linalg.norm(a1)
        w = math.acos(max(-1, min(1, a0 @ a1))); pts = []
        for i in range(14):   # over the skull to the tie, slerp on the skull
            t = i / 13
            d = a0 if w < 1e-4 else (math.sin((1 - t) * w) * a0 + math.sin(t * w) * a1) / math.sin(w)
            pts.append(c + r * d * (1 + 0.035 * math.sin(t * math.pi) + 0.12 * t ** 4))
        off = rng.normal(0, 0.012, 3); off[1] *= 0.3
        for i in range(1, 22):  # the tail: out from the tie, then down, a light S
            t = i / 21
            pts.append(T + back * (0.05 * math.sin(t * math.pi * 0.7) + 0.02 * t) + np.array([0, -0.40 * t ** 1.1, 0]) + off * (0.5 + 2.5 * t))
        G.append(np.array(pts))
    locks = [strand(c, r, th, ph, 0.0, ey - 0.13, lift=0.03, flare=0.012, curl=0.006, n=18)
             for th, ph in grid(line, 2, 20, keep=side)]
    return dict(skin=0xf3cdb8, line=line, melanin=(0.08, 0.2, 0xd23a5a), scalp=0x5a1020, dist=1.8 * 1.3, ty=-0.1,
                parts=[dict(region=lambda th, ph: not side(th, ph), guides=G, clump=0.03, clump_shape=0.6, tip_spread=0.004, guides_k=3),
                       dict(region=side, guides=locks, clump=0.02, density=900000)],
                tie=T, tie_dir=back * 0.4 + np.array([0, -1, 0]))

def marco(c, r, ey):
    """Marco: a boy's short brown mushroom cut, a straight fringe to the brows in scalloped locks."""
    line = hairline(0.6, 0.0, -0.55)
    G = []
    for th, ph in grid(line, 4, 30):
        a = abs(th) / math.pi
        tip = ey + 0.03 - 0.07 * min(1, a * 2.2) - 0.02 * max(0, a - 0.5) * 2
        leave = 0.42 if a < 0.2 else 0.15
        G.append(strand(c, r, th, ph, leave, tip, lift=0.12, flare=0.018, curl=0.012, n=20))
    return dict(skin=0xf0c8a6, line=line, melanin=(0.82, 0.5), scalp=0x1a0e08, dist=1.15 * 1.3,
                parts=[dict(guides=G)], clump=0.03, clump_shape=0.5, tip_spread=0.002)

STYLES = {'gwen': gwen, 'alva': alva, 'kpony': kpony, 'marco': marco}
