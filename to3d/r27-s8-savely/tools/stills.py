"""The drawing's views of Тим in 3D, side by side with the drawing and overlaid on it:
turn (front, three-quarter, profile — turn-tim), portrait (portrait-tim, the grin), figure (figure-tim, waving),
expressions (expr-tim: joy, surprise, sad, anger). Each panel: the pose (a frame of a Kimodo motion of the engine,
the head turned on top as the drawing turns it against the body), the face (an expression of the sheet, the eyes on
the camera), a camera of the drawing's view (its yaw, size and place, styles/s8-stopmotion/tools/build.py) — then
move.mjs (engine) → render.py (Blender) → the sheet.
usage: python3 stills.py turn|portrait|figure|expr [samples]"""
import json, os, subprocess, sys, math
import numpy as np
from PIL import Image, ImageFilter
from common import CACHE, HERE, STYLE, FOLDER, HH, pack

BLENDER = '/home/user/cache/blender/blender'
OUT = os.path.join(CACHE, 'stills')
os.makedirs(OUT, exist_ok=True)
M = json.load(open(f'{CACHE}/model.json'))
PC = {p['name']: (p['start'], p['count']) for p in M['pieces']}
_, BA = pack.read(f'{CACHE}/engine/data/bodies/savely8.json')
REST = BA['positions'].astype(float)
O = np.array(M['O'])
HEADONLY = ['head', 'eyeL', 'eyeR', 'lipU', 'lipL', 'cav', 'teethU', 'teethL', 'brows', 'lashes', 'hair']


def kabsch(A, B_):
    ca, cb = A.mean(0), B_.mean(0)
    U, S, Vt = np.linalg.svd((A - ca).T @ (B_ - cb))
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    return R, cb - R @ ca


def head_centre(F):
    s, n = PC['head']
    R, t = kabsch(REST[s:s + n], F[s:s + n].astype(float))
    return R @ O + t


SHEETS = {
    # name: drawing picture, size, panels [(cx, cy, S, view yaw, head yaw on top, motion, frame, face, roll)]
    'turn': ('turn-tim.jpg', (1500, 620), [(250 + 500 * i, 255, 255, 0.8 * y, 0.2 * y, 'bow', 0, {'calm': 1}, 0) for i, y in enumerate((0, 40, 88))]),
    'portrait': ('portrait-tim.jpg', (700, 820), [(350, 335, 330, 0.55 * 28, 0.45 * 28, 'bow', 0, {'grin': 1}, 0)]),
    'figure': ('figure-tim.jpg', (560, 960), [(280, 900 - 2.86 * 215, 215, 0.6 * 22.4, 0.4 * 22.4, 'wave', 38, {'grin': 1}, 0)]),
    'expr': ('expr-tim.jpg', (1600, 540), [(200 + 400 * i, 280, 290, 18, 0, 'bow', 0, {e: 1}, r)
                                           for i, (e, r) in enumerate((('joy', -5), ('surprise', 0), ('sad', 6), ('anger', -3)))]),
}


def run(sheet, samples=48):
    pic, (W, H), panels = SHEETS[sheet]
    frames, views = [], []
    pw = W // len(panels)
    for k, (cx, cy, S, vy, hy, mot, fr, face, roll) in enumerate(panels):
        gaze = [vy - hy, 0.0]                  # the eyes on the camera (the drawing's at_camera)
        fy = math.radians(vy)
        mj = dict(out=f'{OUT}/{sheet}{k}.bin', motion=mot, frames=[fr],
                  head=dict(yaw=hy, roll=-roll, rollAxis=[-math.sin(fy), 0, math.cos(fy)], level=True),
                  face=dict(e=face, gaze=gaze))
        json.dump(mj, open(f'{OUT}/job-{sheet}{k}.json', 'w'))
        subprocess.run(['node', os.path.join(HERE, 'move.mjs'), f'{OUT}/job-{sheet}{k}.json'], check=True)
        F = np.fromfile(f'{OUT}/{sheet}{k}.bin', np.float32).reshape(-1, len(REST), 3)[0]
        frames.append(F)
        at = head_centre(F)
        views.append(dict(name=f'{sheet}{k}', W=pw, H=H, frame=k,
                          cam=dict(type='view', yaw=vy, S=S, cx=cx - k * pw, cy=cy, at=at.tolist(), fstop=3.2)))
    np.concatenate(frames).astype(np.float32).tofile(f'{OUT}/{sheet}.bin')
    job = dict(out=OUT, samples=samples, frames=f'{OUT}/{sheet}.bin', views=views,
               hide=[p for p in PC if p not in HEADONLY] if sheet == 'expr' else [])
    json.dump(job, open(f'{OUT}/render-{sheet}.json', 'w'))
    subprocess.run([BLENDER, '-b', '--python', os.path.join(HERE, 'render.py'), '--', f'{OUT}/render-{sheet}.json'],
                   check=True, stdout=subprocess.DEVNULL)
    R = Image.new('RGB', (W, H))
    for k in range(len(panels)):
        R.paste(Image.open(f'{OUT}/{sheet}{k}.png').convert('RGB'), (k * pw, 0))
    R.save(f'{OUT}/{sheet}-3d.png')
    D = Image.open(os.path.join(STYLE, 'pics', pic)).convert('RGB').resize((W, H))
    return D, R


def sheet_image(D, R, out, vertical=None):
    """the drawing, the 3D, and the 3D over the drawing (half and half)"""
    W, H = D.size
    ov = Image.blend(D, R, 0.5)
    if vertical is None: vertical = W > H
    if vertical:
        S = Image.new('RGB', (W, H * 3)); S.paste(D, (0, 0)); S.paste(R, (0, H)); S.paste(ov, (0, 2 * H))
    else:
        S = Image.new('RGB', (W * 3, H)); S.paste(D, (0, 0)); S.paste(R, (W, 0)); S.paste(ov, (2 * W, 0))
    S.save(out, quality=86)
    return S


if __name__ == '__main__':
    name = sys.argv[1]
    D, R = run(name, int(sys.argv[2]) if len(sys.argv) > 2 else 48)
    sheet_image(D, R, f'{OUT}/cmp-{name}.jpg')
    print('done', name)
