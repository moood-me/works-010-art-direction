"""Build the sheets: python3 build.py [name…] → ../svg/<name>.svg

Sheets: portrait-<who>, figure-<who>, turn-<who>, expr-<who>, cast (the four), cast6 (all six), rule-* diagrams.
"""
import os
import sys
import math
import importlib
import numpy as np
from poly import Doc, Camera, Light, render, press, Ry
import scenery as SC

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('SVG') or os.path.join(HERE, '..', 'svg')

WHO = ['anya', 'savely', 'tim', 'vera', 'marat', 'kira']
NAMES = {'anya': 'Аня', 'savely': 'Савелий Петрович', 'tim': 'Тим', 'vera': 'Вера', 'marat': 'Марат', 'kira': 'Кира'}
EXPR_RU = {'joy': 'радость', 'surprise': 'удивление', 'sad': 'грусть', 'anger': 'злость'}
TURNS = ['anya', 'tim', 'marat', 'kira', 'savely', 'vera']
INK = '#3b3a48'


def mod(who):
    return importlib.import_module(who)


def light_for(who=None):
    return Light()


def stand(pieces, r=30.0, color='#5f5b6b', y=0.0, x=0.0, z=0.0, shadow=(22, 14)):
    """Put a plinth under the feet, with a soft contact shadow pressed on it."""
    pl = SC.plinth(r, 4.0, color, 12, y, x, z)[0]
    rx, rz = shadow
    press(pl, [(x + rx * math.sin(2 * math.pi * i / 10), y + 50, z + rz * math.cos(2 * math.pi * i / 10)) for i in range(10)],
          '#1b1726', 0.28, dir=(0, 1, 0), lift=0.05)
    return pieces + [pl]


def head_cam(sk, yaw, scale, ox, oy, pitch=3.0, f=520.0, up=0.0):
    t = sk.head + np.array([0, up, 0])
    return Camera(yaw=yaw, pitch=pitch, f=f, scale=scale, ox=ox, oy=oy, target=t)


def caption(doc, x, y, s, size=24, opacity=0.85):
    doc.text(x, y, s, size=size, color=INK, opacity=opacity)


# ---------------------------------------------------------------------------------------------------------- sheets

def portrait(who):
    M = mod(who)
    d = Doc(800, 960)
    SC.backdrop(d, 800, 960, *SC.BG[who], seed=sum(map(ord, who)) % 97)
    ps, sk = M.figure(getattr(M, 'PORTRAIT_POSE', 'stand'), getattr(M, 'PORTRAIT_EXPR', 'rest'))
    yaw, up, sc = getattr(M, 'PORTRAIT_CAM', (18, -6, 14.0))
    cam = head_cam(sk, yaw, sc, 400, 430, up=up)
    d.add(render(ps, cam, light_for(who)))
    return d


def figure(who):
    M = mod(who)
    d = Doc(800, 1000)
    SC.backdrop(d, 800, 1000, *SC.BG[who], seed=sum(map(ord, who)) % 89)
    ps, sk = M.figure('stand', getattr(M, 'FIGURE_EXPR', 'rest'))
    ps = stand(ps, r=getattr(M, 'PLINTH', 34.0), color=getattr(M, 'PLINTH_COL', '#5f5b6b'))
    yaw = getattr(M, 'FIGURE_YAW', 16)
    H = sk.head[1] + 14
    sc = min(800.0 / (H + 12), 5.6) if H > 150 else 640.0 / (H + 12)   # the child stays a child on his sheet
    cam = Camera(yaw=yaw, pitch=7, f=1600, scale=sc, ox=400, oy=915, target=(0, 0, 0))
    d.add(render(ps, cam, light_for(who)))
    caption(d, 400, 975, NAMES[who])
    return d


def turn(who):
    M = mod(who)
    d = Doc(1500, 720)
    SC.backdrop(d, 1500, 720, *SC.BG[who], seed=sum(map(ord, who)) % 83)
    for i, (yaw, label) in enumerate([(0, 'анфас'), (38, 'три четверти'), (90, 'профиль')]):
        ps, sk = M.figure('turn', 'rest')
        ps = stand(ps, r=getattr(M, 'PLINTH', 34.0), color=getattr(M, 'PLINTH_COL', '#5f5b6b'))
        H = sk.head[1] + 14
        sc = min(560.0 / (H + 10), 3.1)
        cam = Camera(yaw=yaw, pitch=6, f=1600, scale=sc, ox=250 + i * 500, oy=640, target=(0, 0, 0))
        d.add(render(ps, cam, light_for(who)))
        caption(d, 250 + i * 500, 698, label, size=21, opacity=0.7)
    return d


def expr(who):
    M = mod(who)
    d = Doc(1600, 560)
    SC.backdrop(d, 1600, 560, *SC.BG[who], seed=sum(map(ord, who)) % 79)
    for i, e in enumerate(['joy', 'surprise', 'sad', 'anger']):
        ps, sk = M.figure('turn', e)
        if hasattr(M, 'expr_pose'):
            ps, sk = M.expr_pose(e)
        cam = head_cam(sk, 14, 10.0, 200 + i * 400, 268, up=-5)
        d.add(render(ps, cam, light_for(who)))
    d.add('<rect x="0" y="500" width="1600" height="60" fill="#f4efe8" fill-opacity="0.82"/>')
    for i, e in enumerate(['joy', 'surprise', 'sad', 'anger']):
        caption(d, 200 + i * 400, 538, EXPR_RU[e], size=21, opacity=0.8)
    return d


def cast_sheet(names, w, h, spacing, name_y, seed):
    d = Doc(w, h)
    SC.backdrop(d, w, h, '#e7d9c8', '#b9aeb4', seed=seed)
    n = len(names)
    tile_w = spacing * (n + 0.2)
    cam = Camera(yaw=0, pitch=11, f=2600, scale=1.0, ox=w / 2, oy=h - 135, target=(0, 0, 0))
    scale = (w * 0.9) / tile_w
    cam.scale = scale
    d.add(render(SC.diorama(w=tile_w, d=150, h=24, seed=seed), cam, light_for()))
    xs = [(-(n - 1) / 2 + i) * spacing for i in range(n)]
    for who, x in zip(names, xs):
        M = mod(who)
        ps, sk = M.figure('stand', getattr(M, 'FIGURE_EXPR', 'rest'))
        yaw = getattr(M, 'CAST_YAW', {}).get(len(names), 0)
        ps = [p.moved(Ry(yaw), (x, 0, 0)) for p in ps]
        c = Camera(yaw=0, pitch=11, f=2600, scale=scale, ox=w / 2, oy=h - 135, target=(0, 0, 0))
        d.add(render(ps, c, light_for(who)))
    for who, x in zip(names, xs):
        d.text(w / 2 + x * scale, h - name_y, NAMES[who], size=22, color='#efe6d8', opacity=0.85)
    return d


def cast():
    return cast_sheet(['savely', 'tim', 'anya', 'vera'], 1600, 900, 92, 30, 7)


def cast6():
    return cast_sheet(['tim', 'savely', 'kira', 'anya', 'vera', 'marat'], 2000, 960, 92, 30, 11)


def rule_planes():
    """How a face is built: the planes with their edges, the same planes lit, then the tiny features on them."""
    M = mod('anya')
    d = Doc(1500, 620)
    SC.backdrop(d, 1500, 620, '#ece4d8', '#cfc6c0', seed=5)
    labels = ['плоскости', 'свет на плоскостях', 'черты лица']
    for i in range(3):
        ps, sk = M.figure('turn', 'rest')
        ps = [p for p in ps if p.name in ('head', 'nose', 'ear') or i == 2 or p.mat == 'hair']
        if i < 2:
            ps = [p for p in ps if p.mat != 'hair' and p.name in ('head', 'nose', 'ear')]
        cam = head_cam(sk, 30, 11.0, 250 + i * 500, 300, up=0)
        if i == 0:
            d.add(render(ps, cam, light_for(), edges='#3b3a48', decals=False, flat='#efe3d6'))
        elif i == 1:
            d.add(render(ps, cam, light_for(), edges='#00000033', decals=False))
        else:
            d.add(render(ps, cam, light_for()))
    d.add('<rect x="0" y="555" width="1500" height="65" fill="#f4efe8" fill-opacity="0.85"/>')
    for i in range(3):
        caption(d, 250 + i * 500, 596, labels[i], size=22, opacity=0.8)
    return d


def rule_heights():
    """The six in a row, on one scale: heights and builds."""
    names = ['tim', 'savely', 'kira', 'anya', 'vera', 'marat']
    d = Doc(1600, 760)
    SC.backdrop(d, 1600, 760, '#e9e3da', '#c8c1bc', seed=9)
    for y in range(80, 700, 40):
        d.add('<line x1="60" x2="1540" y1="%d" y2="%d" stroke="#3b3a48" stroke-opacity="0.08"/>' % (y, y))
    for i, who in enumerate(names):
        M = mod(who)
        ps, sk = M.figure('turn', 'rest')
        x = 170 + i * 252
        cam = Camera(yaw=24, pitch=4, f=2600, scale=3.15, ox=x, oy=680, target=(0, 0, 0))
        d.add(render(ps, cam, light_for(who)))
        caption(d, x, 730, NAMES[who], size=21, opacity=0.8)
    return d


def sheets():
    S = {}
    for w in WHO:
        S['portrait-' + w] = (portrait, w)
        S['figure-' + w] = (figure, w)
        S['expr-' + w] = (expr, w)
    for w in TURNS:
        S['turn-' + w] = (turn, w)
    S['cast'] = (cast, None)
    S['cast6'] = (cast6, None)
    S['rule-planes'] = (rule_planes, None)
    S['rule-heights'] = (rule_heights, None)
    return S


if __name__ == '__main__':
    S = sheets()
    names = sys.argv[1:] or list(S)
    os.makedirs(OUT, exist_ok=True)
    for n in names:
        fn, arg = S[n]
        doc = fn(arg) if arg else fn()
        doc.save(os.path.join(OUT, n + '.svg'))
        print('svg', n)
