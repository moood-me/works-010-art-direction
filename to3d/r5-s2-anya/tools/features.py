"""The face's painted layer: Аня's eyes, brows, nose lines, mouth and blush from the drawing's front view
(styles/s2-klaus/tools: anya.head_front, parts.eye/brow), on a transparent sheet in the head view's frame (500×600),
one sheet per expression. Light and shadow are not here — the 3D gives them.
  python3 features.py outdir"""
import os, sys, subprocess
import drawing  # noqa: F401  (puts the Klaus tools on the path)
import anya
from kit import Doc, Light, mix
from parts import eye, brow, INK

SKIN, ROSE, HAIR = anya.SKIN, anya.ROSE, anya.HAIR
LINE = '#5a2030'
X0, Y0, W, H = 150, 180, 200, 180     # the sheet: this part of the head frame (units), drawn ×S
S = 6


def mouth(d, kind):
    lipc = '#b85a5e'
    if kind == 'smile':
        return [d.tone('M236,326 C244,322 256,322 264,326 C256,330 244,330 236,326Z', lipc, 1),
                f'<path d="M230,324 C240,332 260,332 270,324" fill="none" stroke="{LINE}" stroke-width="2" stroke-linecap="round"/>',
                d.tone('M240,331 C246,336 254,336 260,331 C258,339 242,339 240,331Z', '#d27a74', 0.8, 1.2)]
    if kind == 'open_smile':
        return [f'<path d="M228,322 C240,328 260,328 272,322 C268,338 258,346 250,346 C242,346 232,338 228,322Z" fill="#4a1a24"/>',
                f'<path d="M231,324 C242,329 258,329 269,324 L267,330 C256,333 244,333 233,330Z" fill="#f4ece4"/>',
                d.tone('M240,340 C246,336 254,336 260,340 C254,345 246,345 240,340Z', '#c45a64', 0.9, 1),
                f'<path d="M226,321 C228,323 229,324 231,324 M274,321 C272,323 271,324 269,324" fill="none" stroke="{LINE}" stroke-width="2" stroke-linecap="round"/>']
    if kind == 'o':
        return [f'<path d="M242,322 C246,316 254,316 258,322 C261,334 256,344 250,344 C244,344 239,334 242,322Z" fill="#4a1a24"/>',
                d.tone('M244,337 C247,333 253,333 256,337 C253,343 247,343 244,337Z', '#c45a64', 0.9, 1),
                f'<path d="M242,322 C246,316 254,316 258,322" fill="none" stroke="{LINE}" stroke-width="1.6"/>']
    if kind == 'sad':
        return [d.tone('M238,328 C244,325 256,325 262,328 C256,330 244,331 238,328Z', lipc, 1),
                f'<path d="M232,333 C240,325 260,325 268,333" fill="none" stroke="{LINE}" stroke-width="2" stroke-linecap="round"/>',
                d.tone('M241,333 C246,336 254,336 259,333 C256,339 244,339 241,333Z', '#d27a74', 0.6, 1.2)]
    if kind == 'angry':
        return [f'<path d="M234,325 C242,320 258,320 266,325 C262,333 238,333 234,325Z" fill="#4a1a24"/>',
                f'<path d="M236,324 C244,321 256,321 264,324 L263,327 C254,325 246,325 237,327Z" fill="#f4ece4"/>',
                f'<path d="M230,328 C240,318 260,318 270,328" fill="none" stroke="{LINE}" stroke-width="2" stroke-linecap="round"/>']
    raise ValueError(kind)


def sheet(expr='calm'):
    e = anya.EXPR[expr]
    d = Doc(W * S, H * S, Light(-0.85, -0.5, key='#ffc47a', shade='#3a2a5a'))
    o = []
    # blush and the eye sockets' warm tone, the nose tip's rose
    o += [d.tone('M196,282 C204,272 222,274 226,288 C222,300 202,300 196,292Z', ROSE, 0.4, 6),
          d.tone('M274,288 C278,274 296,272 304,282 C304,292 282,300 276,298Z', ROSE, 0.4, 6),
          d.tone('M196,234 C206,224 232,226 240,240 C234,256 210,258 198,250Z', '#9a4c5c', 0.16, 4),
          d.tone('M260,240 C268,226 294,224 304,234 C302,250 278,258 262,256Z', '#9a4c5c', 0.16, 4),
          d.tone('M242,286 C246,280 254,280 258,286 C256,296 244,296 242,286Z', ROSE, 0.3, 3)]
    look = (e['look'][0] * 0.3, e['look'][1])
    for cx, wing in ((218, -1), (282, 1)):
        o.append(eye(d, cx, 248, 16, 15, lid=e['lid'], look=look, tilt=1.5, skin=SKIN, iris='#7a4424', wing=wing,
                     crease=0.3, irr=0.9, low_lid=e.get('low', 0)))
    b = e['brow']; bc = mix(HAIR, INK, 0.35)
    if e.get('sad'):
        o += [brow((236, 214 + b - 10), (214, 208 + b - 4), (192, 222 + b), 4, bc), brow((264, 214 + b - 10), (286, 208 + b - 4), (308, 222 + b), 4, bc)]
    elif e.get('angry'):
        o += [brow((236, 224 + b - 2), (214, 214 + b - 6), (192, 212 + b - 10), 4, bc), brow((264, 224 + b - 2), (286, 214 + b - 6), (308, 212 + b - 10), 4, bc)]
    else:
        o += [brow((236, 222 + b), (214, 210 + b), (192, 222 + b), 4, bc), brow((264, 222 + b), (286, 210 + b), (308, 222 + b), 4, bc)]
    nl = mix(SKIN, INK, 0.5)
    o.append(d.tone('M246,286 C248,284 251,284 253,286 C251,288 248,288 246,286Z', '#fff4e0', 0.7, 0.8))
    o += mouth(d, e['mouth'])
    d.add(f'<g transform="scale({S}) translate({-X0},{-Y0})">'); [d.add(s) for s in o]; d.add('</g>')
    return d


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    files = []
    for ex in anya.EXPR:
        p = os.path.join(out, f'face-{ex}.svg'); sheet(ex).save(p); files.append(p)
    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(['node', os.path.join(here, 'svg2png.mjs'), out] + files, check=True)
