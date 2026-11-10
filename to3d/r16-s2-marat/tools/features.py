"""The face's painted layers, from the drawing's own parts (styles/s2-klaus/tools: marat.mouth, marat.thick_brow,
marat.smile_eye, parts.eye, kit.Doc.tone) in the front view's layout (marat.head_front): Марат's dark eyes narrowed
by the cheeks, thick black brows, ruddy cheeks, the warm sockets, and the mouth
in the beard — teeth and a tongue in every open one. Transparent sheets in head units (the frame's x, y):
  eyes-<expr>-<lid><look>.png   lid: o open, h half, s shut;  look: l, c, r
  skin-<mouth>.png              tones + the mouth: smile, laugh, o, sad, angry, a (a smaller laugh, for speech)
Light and shadow are not here — the 3D gives them.     python3 features.py outdir"""
import os, sys, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'styles', 's2-klaus', 'tools'))
import marat
from kit import Doc, Light, mix
from parts import eye, INK

SKIN, ROSE = marat.SKIN, marat.ROSE
X0, Y0, W, H = 140, 190, 220, 260
S = 4
EYE_X, EYE_Y = 38, 262

# the drawing's sheet; mou: the moustache's tips (up with a smile), jaw: the beard dropped by an open mouth (units)
EXPR = {k: dict(v, look=v.get('look', (0, 0))[1]) for k, v in marat.EXPR.items()}
for k, mou, jaw in (('calm', -5, 0), ('joy', -8, 12), ('surprise', 2, 8), ('sad', 6, 0), ('anger', 0, 0)): EXPR[k].update(mou=mou, jaw=jaw)
LOOKS = {'l': -0.4, 'c': 0.0, 'r': 0.4}


def doc(): return Doc(W * S, H * S, Light(-0.85, -0.5, key='#ffc47a', shade='#3a2a5a'))


def wrap(d, o):
    d.add(f'<g transform="scale({S}) translate({-X0},{-Y0})">'); [d.add(s) for s in o]; d.add('</g>')
    return d


def eyes(expr, lid, look):
    e = EXPR[expr]; d = doc(); o = []
    b = e['brows'][0]
    for sx in (1, -1):
        cx = 250 + sx * EYE_X; m = lambda x: 250 + sx * x
        if e.get('shut'):
            o.append(marat.smile_eye(d, cx, 263, 16.5, 12, sx))
        else:
            lv = {'o': e['lid'], 'h': e['lid'] + (1 - e['lid']) * 0.55}.get(lid)
            o.append(eye(d, cx, EYE_Y, 16, 13.5, lid=lv or 0.5, look=(LOOKS[look], e['look']), tilt=1, skin=SKIN, iris='#3a2218',
                         wing=sx, crease=0.35, low_lid=e['low'], irr=0.86, shut=lid == 's'))
        if e.get('sad'): o.append(marat.thick_brow((m(14), 228 + b), (m(38), 226 + b), (m(68), 244 + b), 10))
        elif e.get('angry'): o.append(marat.thick_brow((m(12), 242 + b), (m(38), 226 + b), (m(68), 222 + b), 11))
        else: o.append(marat.thick_brow((m(14), 238 + b), (m(38), 220 + b), (m(66), 236 + b), 10))
    return wrap(d, o)


def skin(mouth):
    d = doc(); o = []
    for sx in (1, -1):
        m = lambda x: 250 + sx * x
        o.append(d.tone(f'M{m(10)},254 C{m(18)},240 {m(52)},238 {m(64)},250 C{m(60)},268 {m(32)},276 {m(14)},272Z', '#7a3048', 0.3, 4))
        o.append(d.tone(f'M{m(34)},304 C{m(40)},284 {m(74)},280 {m(86)},296 C{m(84)},314 {m(56)},326 {m(38)},320Z', ROSE, 0.55, 8))
    if mouth == 'a':
        o.append('<g transform="translate(250,364) scale(0.8,0.62) translate(-250,-364)">'); o.append(marat.mouth(d, 'laugh', x0=196, x1=304, y=364)); o.append('</g>')
    else:
        o.append(marat.mouth(d, mouth, x0=196, x1=304, y=364))
    return wrap(d, o)


def all_sheets():
    out = {}
    for ex, e in EXPR.items():
        if e.get('shut'):
            d = eyes(ex, 'o', 'c')
            for n in ('ol', 'oc', 'or', 'hl', 'hc', 'hr', 'sc'): out[f'eyes-{ex}-{n}'] = d
            continue
        for lk in LOOKS:
            for lid in 'oh': out[f'eyes-{ex}-{lid}{lk}'] = eyes(ex, lid, lk)
        out[f'eyes-{ex}-sc'] = eyes(ex, 's', 'c')
    for m in ('smile', 'laugh', 'o', 'sad', 'angry', 'a'): out[f'skin-{m}'] = skin(m)
    return out


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    files = []
    for name, d in all_sheets().items():
        p = os.path.join(out, name + '.svg'); d.save(p); files.append(p)
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(['node', os.path.join(here, 'svg2png.mjs'), out] + files, check=True)
    for f in files: os.remove(f)
    print(len(files), 'sheets')
