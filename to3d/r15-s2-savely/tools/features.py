"""The face's painted layers, from the drawing's own parts (styles/s2-klaus/tools: parts.eye, kit.Doc.tone) laid out
for the front view: Савелий's small heavy-lidded eyes, the warm sockets, ruddy cheeks, the forehead's wrinkles, the
chin's tone, the mouth under the moustache. Two sheets a state, transparent, in head units (x from the middle + 250):
  eyes-<expr>-<lid><look>.png   lid: o open, h half, s shut;  look: l, c, r (the iris left, middle, right)
  skin-<mouth>.png              the tones and wrinkles + the mouth: none, smile, a, o (speaking)
Light and shadow are not here — the 3D gives them.     python3 features.py outdir"""
import os, sys, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'styles', 's2-klaus', 'tools'))
import savely
from kit import Doc, Light, mix
from parts import eye, INK

SKIN, ROSE = savely.SKIN, savely.ROSE
X0, Y0, W, H = 140, 150, 220, 300     # the sheet: this part of the head frame (units), drawn ×S
S = 4
EYE_X, EYE_Y = 37, 262

# calm and kind are the drawing's; the other three are made in its manner (the drawing has no sheet for him)
EXPR = {
    'calm':     dict(lid=0.52, low=0.12, look=0.1, mouth='none', brow=(0, 0), mou=0),
    'kind':     dict(lid=0.45, low=0.3, look=0.0, mouth='smile', brow=(-3, -4), mou=-9),
    'surprise': dict(lid=0.12, low=0.0, look=0.0, mouth='o', brow=(-13, -8), mou=3),
    'sad':      dict(lid=0.6, low=0.1, look=0.35, mouth='none', brow=(-2, -16), mou=6),
    'anger':    dict(lid=0.5, low=0.25, look=0.05, mouth='none', brow=(7, 12), mou=2),
}
LOOKS = {'l': -0.42, 'c': 0.0, 'r': 0.42}


def doc(): return Doc(W * S, H * S, Light(-0.85, -0.5, key='#ffc47a', shade='#3a2a5a'))


def wrap(d, o):
    d.add(f'<g transform="scale({S}) translate({-X0},{-Y0})">'); [d.add(s) for s in o]; d.add('</g>')
    return d


def eyes(expr, lid, look):
    e = EXPR[expr]; d = doc(); o = []
    lv = {'o': e['lid'], 'h': e['lid'] + (1 - e['lid']) * 0.55}.get(lid)
    for sx in (1, -1):
        o.append(eye(d, 250 + sx * EYE_X, EYE_Y, 12.5, 10.5, lid=lv or 0.5, look=(LOOKS[look], e['look']), tilt=-2, skin=SKIN,
                     iris='#4a5a6a', crease=0.4, wing=0.3 * sx, low_lid=e['low'], shut=lid == 's'))
    return wrap(d, o)


def skin(mouth):
    d = doc(); o = []
    for sx in (1, -1):
        m = lambda x: 250 + sx * x
        # deep warm sockets under the brows, ruddy cheeks
        o.append(d.tone(f'M{m(14)},250 C{m(24)},238 {m(58)},238 {m(66)},254 C{m(62)},276 {m(30)},282 {m(16)},272Z', '#7a3048', 0.42, 5))
        o.append(d.tone(f'M{m(24)},296 C{m(36)},282 {m(72)},284 {m(80)},306 C{m(72)},326 {m(40)},328 {m(26)},316Z', ROSE, 0.5, 8))
        wl = mix(SKIN, '#5a2030', 0.5)
        o.append(f'<path d="M{m(26)},288 C{m(36)},294 {m(50)},294 {m(60)},288 M{m(64)},264 C{m(70)},272 {m(72)},282 {m(70)},290" fill="none" '
                 f'stroke="{wl}" stroke-width="1.5" stroke-linecap="round" opacity="0.7"/>')
    wl = mix(SKIN, '#5a2030', 0.5)
    o.append(f'<path d="M214,186 C232,179 268,179 286,186 M220,202 C236,196 264,196 280,202" fill="none" stroke="{wl}" '
             f'stroke-width="1.6" stroke-linecap="round" opacity="0.7"/>')
    sk = mix(SKIN, '#4a1838', 0.6)
    o.append(d.tone('M226,420 C238,430 262,430 274,420 C268,434 232,434 226,420Z', sk, 0.55, 2))
    if mouth == 'smile':
        o.append('<path d="M226,404 C238,414 262,414 274,404" fill="none" stroke="#5a2030" stroke-width="2.2" stroke-linecap="round"/>')
    elif mouth in ('a', 'o'):
        w, h = (15, 9) if mouth == 'a' else (9, 12)
        o.append(f'<path d="M{250-w},400 C{250-w},{404+h} {250+w},{404+h} {250+w},400Z" fill="#4a1a24"/>')
        o.append(d.tone(f'M{250-w*0.6},{401+h*0.55} C{250-w*0.3},{400+h*0.3} {250+w*0.3},{400+h*0.3} {250+w*0.6},{401+h*0.55} C{250+w*0.3},{402+h*0.8} {250-w*0.3},{402+h*0.8} {250-w*0.6},{401+h*0.55}Z', '#c45a64', 0.9, 0.8))
    return wrap(d, o)


def all_sheets():
    out = {}
    for ex in EXPR:
        for lk in LOOKS:
            for lid in 'oh': out[f'eyes-{ex}-{lid}{lk}'] = eyes(ex, lid, lk)
        out[f'eyes-{ex}-sc'] = eyes(ex, 's', 'c')
    for m in ('none', 'smile', 'a', 'o'): out[f'skin-{m}'] = skin(m)
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
