"""The painted layers' data from the drawing (kira.kira, kira.kira_person): the face layer — blush, the brows' build,
the lips' shapes (face.mouth_curves and draw_mouth at rest) — in the drawing's front coordinates of the head
(x her left, y down, head centre 0; the layer maps them u = (x + 60) / 120, v = (y + 60) / 120), and the hoodie's
front (kira.py hoodie_deco): the kangaroo pocket and its seams, the hood's cords with their tips, the folds — in the
drawing's person units. web/paint.js draws them (the face every frame: the brows move)."""
import json, math
from drawing import C, P
from common import HERE
import face, char
import kira
from pix import mix

d = {k: C[k] for k in ['eye_x', 'eye_y', 'eye_w', 'eye_h', 'brow_h', 'brow_len', 'brow_w', 'brow_arch', 'brow_col', 'blush', 'blush_a',
                       'lip', 'mouth_y', 'mouth_w', 'lip_up', 'lip_low', 'skin', 'skin_sh', 'nostril', 'nose_y']}
d['blush_x'] = C.get('blush_x', 23); d['blush_y'] = C.get('blush_y', 19)
d['spots'] = [list(s) for s in C.get('spots', [])]
d['lines'] = [[[list(p) for p in path], a] for path, a in C.get('lines', [])]
d['brow_up'] = 0.8          # the brows this much higher than drawn: in 3D the upper lid's fold is where the drawing paints them
ex = face.expr()
lt, lb, my, mw = face.mouth_curves(C, ex)
ub = [(x, y - C['lip_up'] * (1 - abs(x / mw) ** 1.8) * (1 - 0.35 * math.exp(-((x / mw) / 0.13) ** 2)) - 0.15) for x, y in lt]
lbn = [(x, y + C['lip_low'] * (1 - abs(x / mw) ** 1.6) * 0.95) for x, y in lb]
d['lip_soft'] = False
d['lips'] = dict(up=[list(p) for p in lt + ub[::-1]], low=[list(p) for p in lb + lbn[::-1]], line=[list(p) for p in lt])
K = kira.K
d['cloth'] = dict(
    box=[-64, 60, 128, 260],
    patch=[(-17, 214), (17, 214), (30, 250), (30, 272), (-30, 272), (-30, 250)], patch_col=mix(K['plum'], '#000000', 0.25),
    seams=[dict(pts=[(-30, 270), (-30, 250), (-17, 214), (17, 214), (30, 250), (30, 270)], col=K['plum_sh'], w=1.6, a=0.8, blur=0)]
    + [dict(pts=[(sd * 29, 268), (sd * 28, 250), (sd * 21, 228)], col=K['plum_sh'], w=5, a=0.6, blur=1.6) for sd in (-1, 1)]
    + [dict(pts=[(sd * 6, 92), (sd * 7, 120), (sd * 9, 148 + 8 * (sd > 0))], col='#b9b0c2', w=1.7, a=0.95, blur=0) for sd in (-1, 1)]
    + [dict(pts=[(-38, 130), (-30, 170), (-36, 205)], col=K['plum_sh'], w=7, a=0.4, blur=3), dict(pts=[(36, 150), (27, 185), (33, 215)], col=K['plum_sh'], w=7, a=0.4, blur=3)],
    dots=[(sd * 9, 150 + 8 * (sd > 0), 2.0, '#d9d2e0') for sd in (-1, 1)])
json.dump(d, open(f'{HERE}/web/data/paint.json', 'w'), indent=1)
print('paint.json')
