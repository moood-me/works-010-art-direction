"""The face layer's data from the drawing (cast.tim): freckles, blush, the brows' build, lip and nose tints — in the
drawing's front coordinates (x his left, y down, head centre 0), which the face layer maps to its picture
(u = (x + 60) / 120, v = (y + 60) / 120). web/paint.js draws it every frame (the brows move)."""
import json
from drawing import C
from common import HERE

keys = ['eye_x', 'eye_y', 'eye_w', 'eye_h', 'brow_h', 'brow_len', 'brow_w', 'brow_arch', 'brow_col', 'blush', 'blush_a',
        'blush_x', 'blush_y', 'lip', 'mouth_y', 'mouth_w', 'lip_up', 'lip_low', 'skin', 'skin_sh', 'nostril', 'nose_y']
d = {k: C[k] for k in keys}
d['spots'] = [list(s) for s in C['spots']]
json.dump(d, open(f'{HERE}/web/data/paint.json', 'w'), indent=1)
print(d['spots'][:3])
