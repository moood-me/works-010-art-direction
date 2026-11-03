# The hairstyles of experiments/hair (В1) that this page repeats with Blender's hair tools: the guide curves (the
# groom an artist would draw with Blender's curve sculpt tools, here written as numbers), the hairline, and the
# settings of Blender's node groups. Coordinates are three.js's (Y up, the face toward +Z, +X the person's left).
import math
import numpy as np
from scene import strand, sph, hairline

def grid(c, r, line, rows, cols, top=1.35, jitter=0.0, seed=1):
    rng = np.random.default_rng(seed); out = []
    for j in range(cols):
        th = -math.pi + (j + 0.5) * 2 * math.pi / cols
        lo = line(th) + 0.03
        for i in range(rows):
            ph = lo + (top - lo) * (i / max(1, rows - 1)) ** 0.8
            out.append((th + jitter * rng.uniform(-1, 1) / cols, ph))
    return out

def gwen(c, r, ey):
    """Gwen: a blonde chin-length bob, a side part on her left, the fringe swept over her right brow."""
    line = hairline(0.62, 0.05, -0.62)
    G = []
    for th, ph in grid(c, r, line, 4, 22, jitter=0.5):
        a = abs(th)
        tip = ey - 0.115 + 0.03 * (a / math.pi) ** 2          # chin at the sides, a little higher at the nape
        if a < 0.9 and ph > 0.45:                              # the fringe: swept toward her right
            G.append(strand(c, r, th, ph, 0.42, ey + 0.035 - 0.04 * max(0, -th - 0.2), lift=0.07, sweep=-0.55 + 0.2 * th, flare=0.012, curl=0.004, swing=-0.015))
        else:
            sw = 0.25 * math.sin(th) if ph > 1.0 else 0.0
            G.append(strand(c, r, th, ph, -0.05, tip, lift=0.09, sweep=sw, flare=0.025, curl=0.02))
    return dict(who='woman', skin=0xf1cdb4, line=line, guides=G, color=0xead08f, tip=0xf3e2b0, dist=1.15 * 1.3,
                density=500000, clump=0.035, clump2=0.01, radius=0.0014, clump_shape=0.6, tip_spread=0.0, length='short')

STYLES = {'gwen': gwen}
