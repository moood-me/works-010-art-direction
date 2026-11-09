"""The painted layers' data from the drawing (cast.vera, cast.vera_person): the face layer — blush, the brows' build,
the lips' shapes (face.mouth_curves and draw_mouth at rest), her lines — in the drawing's front coordinates of the
head (x her left, y down, head centre 0; the layer maps them u = (x + 60) / 120, v = (y + 60) / 120), and the coat's
front — the turtleneck's wedge, the lapels, the seam, the buttons — in the drawing's person units.
web/paint.js draws them (the face every frame: the brows move)."""
import json, math
from drawing import C, P
from common import HERE
import face, char

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
d['lip_soft'] = bool(C.get('lips_soft'))
d['lips'] = dict(up=[list(p) for p in lt + ub[::-1]], low=[list(p) for p in lb + lbn[::-1]], line=[list(p) for p in lt])
d['cloth'] = dict(
    box=[-64, 60, 128, 440],
    wedge=[(-13, 80), (-9, 130), (0, 158), (9, 130), (13, 80), (6, 77), (-6, 77)], wedge_col='#93334a',
    lapel=[(13, 80), (25, 92), (21, 108), (29, 118), (10, 160), (7, 140)], lapel_col='#7b8794', line_col='#3f4a57',
    seam=[(4, y) for y in range(160, 470, 30)], buttons=[(-8, 175), (-8, 205), (-8, 270)], button_col='#2a2a2e')
json.dump(d, open(f'{HERE}/web/data/paint.json', 'w'), indent=1)
print('paint.json', len(d['lips']['up']))
