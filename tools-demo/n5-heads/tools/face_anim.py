"""Frames of a face going through its expressions with the rig's own controls (eased in-between poses).
usage: blender -b FILE -P face_anim.py -- char outdir"""
import bpy, sys, os, json, math
char, out = sys.argv[sys.argv.index('--') + 1:][:2]
sys.path.insert(0, os.path.dirname(__file__)); from poses import RAIN, SNOW
P = {'rain': RAIN, 'snow': SNOW}[char]
seq = ['neutral', 'smile', 'neutral', 'surprise', 'blink', 'neutral', 'anger', 'neutral']
def lerp_pose(a, b, t):
    r = {}
    for k in set(a) | set(b):
        A, B = a.get(k, {}), b.get(k, {}); r[k] = {}
        for ch in ('loc', 'rot'):
            if ch in A or ch in B:
                va, vb = A.get(ch, [0, 0, 0]), B.get(ch, [0, 0, 0]); r[k][ch] = [x + (y - x) * t for x, y in zip(va, vb)]
    return r
shots, f = [], 0
for i in range(len(seq) - 1):
    a, b = P[seq[i]], P[seq[i + 1]]
    for j in range(10):
        t = (1 - math.cos(math.pi * j / 10)) / 2
        shots.append({'out': f'{out}/f{f:04d}.png', 'view': 'front', 'pose': lerp_pose(a, b, t), 'res': [540, 540]}); f += 1
    for j in range(8):
        shots.append({'out': f'{out}/f{f:04d}.png', 'view': 'front', 'pose': b, 'res': [540, 540]}); f += 1
sys.argv = [sys.argv[0], '--', json.dumps({'char': char, 'engine': 'WB_MAT', 'shots': shots})]
exec(open(os.path.join(os.path.dirname(__file__), 'render.py')).read())
