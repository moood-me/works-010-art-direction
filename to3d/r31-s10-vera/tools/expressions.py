"""Facial expressions on the fitted head, made in 3D (the drawing makes them with marks; here the form moves):
  lids — the upper and lower lid turn over the eyeball about its centre (as a lid rig does), weighted by
         nearness to the ball, so the eye closes in a smile, opens wide in surprise;
  jaw  — the lower lip, chin and the inside of the mouth turn about a jaw pivot below the ear: the mouth opens and
         its dark inside shows;
  corners — the mouth's corners (and the moustache's ends with them) pulled up and back for a smile, down for a frown;
  brows — the skin of the brow ridge lifted or lowered (the drawn brows follow it);
  look — the irises turned on the balls.
The five expressions are those of the drawing's sheet (features.EXPR): calm, joy, surprise, sad, anger.
Writes CACHE/expr.bin/json: frames in move.mjs's format (one per expression), from the stand pose with the head's
pieces replaced.
usage: python3 expressions.py CACHE
"""
import sys, os, json
import numpy as np

C = sys.argv[1]
K = 1.60 / 1114
FLOOR = 1030.0
sc = np.load(os.path.join(C, 'scene.npz'))
hf = np.load(os.path.join(C, 'head_fit.npz'))
offs = json.load(open(os.path.join(C, 'engine/offsets.json')))
sj = json.load(open(os.path.join(C, 'stand.json')))
stand = np.fromfile(os.path.join(C, 'stand.bin'), np.float32).reshape(sj['N'], 3)

EYES = [hf['scleraL_v'].mean(0), hf['scleraR_v'].mean(0)]
RB = float(np.linalg.norm(hf['scleraL_v'] - EYES[0], axis=1).mean())
MOUTH_Y = 81.0
JAW = np.array([0.0, 30.0, -25.0])

EXPRS = {
    'calm': dict(),
    'joy': dict(up=34, low=14, jaw=7, smile=1.0, brow=2.5, look=(0, 0)),
    'surprise': dict(up=-14, low=-8, jaw=6, smile=0.0, brow=7, iris=0.82),
    'sad': dict(up=16, low=0, jaw=0, smile=-1.0, brow=1.5, inner=4, look=(0, 7)),
    'anger': dict(up=12, low=6, jaw=5, smile=-0.8, brow=-4, inner=-5),
}


def rot_x(P, c, deg, w):
    a = np.radians(deg) * w
    q = P - c
    y = q[:, 1] * np.cos(a) + q[:, 2] * np.sin(a)
    z = -q[:, 1] * np.sin(a) + q[:, 2] * np.cos(a)
    return np.stack([P[:, 0], c[1] + y, c[2] + z], 1)


def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def deform(name, V, e):
    V = V.copy()
    if not e:
        return V
    if name == 'head':
        for c in EYES:
            d = np.linalg.norm(V - c, axis=1)
            near = 1 - smooth(d, RB + 2.0, RB + 6.5)
            front = smooth(V[:, 2] - c[2], -2, 3)
            w = near * front
            upper = V[:, 1] < c[1]
            V[upper] = rot_x(V[upper], c, e.get('up', 0), w[upper])
            V[~upper] = rot_x(V[~upper], c, -e.get('low', 0), w[~upper])
        # jaw: below the mouth line, in front of the ears, above the neck
        wj = smooth(V[:, 1], MOUTH_Y - 1, MOUTH_Y + 4) * (1 - smooth(V[:, 1], 125, 150)) * smooth(V[:, 2], -20, 10)
        V = rot_x(V, JAW, e.get('jaw', 0), wj)
    if name in ('head', 'stache0', 'stache1'):
        s = e.get('smile', 0)
        for side in (1, -1):
            c = np.array([side * 15, MOUTH_Y - 1, 72])
            g = np.exp(-np.sum(((V - c) / [9, 7, 12]) ** 2, 1))
            V += g[:, None] * np.array([side * 2.0 * max(s, 0), -4.5 * s, -2.0 * abs(s)])
    if name == 'head':
        b, inner = e.get('brow', 0), e.get('inner', 0)
        for side in (1, -1):
            for x0, amt in ((side * 32, b), (side * 16, b + inner)):
                c = np.array([x0, 6.0, 70])
                g = np.exp(-np.sum(((V - c) / [11, 8, 30]) ** 2, 1))
                V[:, 1] -= g * amt
    if name.startswith('iris') or name.startswith('sclera'):
        c = EYES[0] if name.endswith('L') else EYES[1]
        if name.startswith('iris'):
            lx, ly = e.get('look', (0, 0))
            V = rot_x(V, c, -ly, 1.0)
            k = e.get('iris', 1.0)
            if k != 1.0:
                axis = np.array([0, 0, 1.0])
                q = V - c
                along = q @ axis
                V = c + axis * along[:, None] + (q - axis * along[:, None]) * k
    return V


frames = []
for ename, e in EXPRS.items():
    P = stand.copy()
    for name in ('head', 'scleraL', 'scleraR', 'irisL', 'irisR', 'stache0', 'stache1'):
        i0, i1 = offs[name]
        V = sc['obj_' + name + '_v']
        D = deform(name, V, e)
        P[i0:i1] = np.stack([D[:, 0] * K, (FLOOR - D[:, 1]) * K, D[:, 2] * K], 1)
    frames.append(P)
np.stack(frames).astype(np.float32).tofile(os.path.join(C, 'expr.bin'))
json.dump(dict(frames=len(frames), N=sj['N'], times=list(range(len(frames))), hips=[sj['hips'][0]] * len(frames),
               names=list(EXPRS)), open(os.path.join(C, 'expr.json'), 'w'))
print('expressions', list(EXPRS))
