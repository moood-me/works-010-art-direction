"""Scenes of the steps along the way, for one sheet: what each base gave and what was done to it.
  1 the base head as it is (Human Base Meshes, realistic for animation, CC0), only scaled to the drawing's size;
  2 the base head fitted to the drawing's head (fit_head.py), its eyes;
  3 with the drawing's hair, brows, glasses and marks (assemble.py);
  4 Anny's body as it is (who.BASE_BODY);
  5 Anny fitted to the drawing's proportions (body.py);
  6 dressed, with the head (the stand pose through the engine).
Writes CACHE/steps/scene_<n>.npz/json and job_steps.json (render.py) for 1–5; 6 is the stand render.
usage: python3 steps.py CACHE
"""
import sys, os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import who
C = os.path.abspath(sys.argv[1])
K, FLOOR = who.K, who.FLOOR
os.makedirs(os.path.join(C, 'steps'), exist_ok=True)
hb = np.load(os.path.join(C, 'hbm_head.npz'))
hf = np.load(os.path.join(C, 'head_fit.npz'))
b = np.load(os.path.join(C, 'body.npz'))
sc = np.load(os.path.join(C, 'scene.npz'))
meta = json.load(open(os.path.join(C, 'scene.json')))
SKIN = who.colours()['skin']


def write(n, objs, marks=None):
    arr, ob = {}, []
    for name, V, F, col in objs:
        arr['obj_' + name + '_v'] = np.asarray(V, float)
        arr['obj_' + name + '_f'] = np.asarray(F)
        ob.append(dict(name=name, colour=col, subsurf=1 if name == 'head' else 0, line=not name.startswith('mouth')))
    np.savez(os.path.join(C, f'steps/scene_{n}.npz'), **arr)
    json.dump(dict(objects=ob, marks=marks or {}, k=K, floor=FLOOR, skip=meta['skip']),
              open(os.path.join(C, f'steps/scene_{n}.json'), 'w'))


# 1: the base head, scaled about its eyes to the drawing's eye distance and set where the drawing's eyes are
V0 = hb['head_v']
eL, eR = hb['scleraL_v'].mean(0), hb['scleraR_v'].mean(0)
s = 2 * who.EYE[0] / np.linalg.norm(eL - eR)
c = (eL + eR) / 2
EYD = who.EYE[1] + who.DROP


def place(P):
    q = (P - c) * s
    return np.stack([q[:, 0], EYD - q[:, 2], 50 - q[:, 1]], 1)


write(1, [('head', place(V0), hb['head_f'], SKIN), ('scleraL', place(hb['scleraL_v']), hb['scleraL_f'], '#fbf8ee'),
          ('scleraR', place(hb['scleraR_v']), hb['scleraR_f'], '#fbf8ee'),
          ('irisL', place(hb['irisL_v'] + [0, -0.0024, 0]), hb['irisL_f'], '#1b1714'),
          ('irisR', place(hb['irisR_v'] + [0, -0.0024, 0]), hb['irisR_f'], '#1b1714')])
# 2: fitted
eyes = [(n, sc['obj_' + n + '_v'], sc['obj_' + n + '_f'], c_) for n, c_ in
        (('scleraL', SKIN), ('scleraR', SKIN), ('irisL', '#1b1714'), ('irisR', '#1b1714'))]
write(2, [('head', hf['v'], hf['f'], SKIN)] + eyes)
# 3: with the drawing's pieces
hair = [(n, sc['obj_' + n + '_v'], sc['obj_' + n + '_f'], o['colour']) for o in meta['objects']
        for n in [o['name']] if n in who.HEAD_PIECES]
mouth = [(o['name'], sc['obj_' + o['name'] + '_v'], sc['obj_' + o['name'] + '_f'], o['colour']) for o in meta['objects']
         if o.get('keep_still')]                       # the drawn mouth's own pieces
write(3, [('head', sc['obj_head_v'], sc['obj_head_f'], SKIN)] + eyes + hair + mouth, marks=meta['marks'])
# 4, 5: Anny as it is, and fitted (y of the raw one put on the same floor)
T = b['anny_tri']
F4 = np.hstack([T, -np.ones((len(T), 1), int)])
write(4, [('body', b['anny_raw'], F4, SKIN)])
write(5, [('body', b['anny_fit'], F4, SKIN)])

views_h = dict(yaw=-30, s=1.25, cx=150, cy=165, W=300, H=400, lw=2.0, bg=who.PANEL)
_sb = 520 / (FLOOR + 90)
views_b = dict(yaw=-30, s=_sb, cx=190, cy=560 - FLOOR * _sb, W=360, H=600, lw=1.6, bg=who.PANEL)
jobs = []
for n in (1, 2, 3):
    jobs.append(dict(scene=os.path.join(C, f'steps/scene_{n}.npz'), out=os.path.join(C, 'steps'), samples=12,
                     views=[dict(views_h, name=f'step{n}')]))
for n in (4, 5):
    jobs.append(dict(scene=os.path.join(C, f'steps/scene_{n}.npz'), out=os.path.join(C, 'steps'), samples=12,
                     views=[dict(views_b, name=f'step{n}')]))
jobs.append(dict(scene=os.path.join(C, 'scene.npz'), out=os.path.join(C, 'steps'), samples=12,
                 frames=os.path.join(C, 'stand.bin'), offsets=os.path.join(C, 'engine/offsets.json'), still_marks=True,
                 views=[dict(views_b, name='step6')]))
for i, j in enumerate(jobs):
    json.dump(j, open(os.path.join(C, f'steps/job{i + 1}.json'), 'w'))
print('steps', len(jobs))
