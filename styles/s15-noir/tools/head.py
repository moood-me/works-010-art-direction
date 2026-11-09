"""The head in three views (three-quarter 'q', front 'f', side 's'), all facing the viewer's left, lit from the left.
Units: crown y=-100, chin y=+100. A character is a dict `p` (see DEFAULT) with its own hair/extras functions;
an expression is a dict `e` (see EXPR)."""
from noir import *

WHITE = '#ece6d6'

EXPR = {
    'calm':     dict(brow=0, tilt=0, op=1.0, mouth='neutral'),
    'joy':      dict(brow=3, tilt=-2, op=0.55, mouth='grin', cheeks=1),
    'surprise': dict(brow=9, tilt=-3, op=1.45, mouth='o'),
    'sadness':  dict(brow=2, tilt=-7, op=0.75, mouth='sad', look=(0, 2)),
    'anger':    dict(brow=-5, tilt=7, op=0.7, mouth='angry'),
    'smile':    dict(brow=2, tilt=-1, op=0.85, mouth='smile'),
    'laugh':    dict(brow=4, tilt=-3, op=0.0, mouth='grin', cheeks=1),
    'smirk':    dict(brow=-2, tilt=3, op=0.7, mouth='smirk'),
    'stern':    dict(brow=-2, tilt=3, op=0.75, mouth='tight'),
}

DEFAULT = dict(
    skin='#d9b999', lip='#8e3b34', iris='#1b1a22', browcol=BLACK, white=WHITE, rim='auto',
    # outlines per view: name -> point; override single points through p['q'], p['f'], p['s']
    q=dict(crown=(12, -100, 's'), backtop=(64, -78, 's'), back=(88, -28, 's'), occ=(78, 18, 's'), nape=(56, 50),
           jaw=(38, 70), chinr=(-6, 99), chinl=(-34, 100), muzzle=(-52, 72, 's'), cheek=(-63, 36), socket=(-58, 10),
           brow=(-63, -8), fore=(-54, -56, 's')),
    f=dict(crown=(0, -100, 's'), tr=(52, -78, 's'), templer=(66, -20, 's'), cheekr=(62, 30), jawr=(46, 72), chinr=(18, 100),
           chinl=(-18, 100), jawl=(-46, 72), cheekl=(-62, 30), templel=(-66, -20, 's'), tl=(-52, -78, 's')),
    s=dict(crown=(20, -100, 's'), backtop=(78, -78, 's'), back=(100, -24, 's'), occ=(86, 24, 's'), nape=(58, 52),
           jaw=(26, 74), chinb=(-36, 100), chin=(-58, 92), chinfold=(-54, 76), lipl=(-62, 68), mouth=(-56, 62), lipu=(-64, 56),
           nosebase=(-58, 46), tip=(-84, 40), root=(-60, 4), brow=(-64, -10), fore=(-52, -60, 's')),
    eye_y=8, eye=dict(w=30, h=9, r=6.5, lid=3.6, lash=0, kind='m'),
    brow=dict(t=7, len=1.0, y=0),
    nose=dict(tip=(-73, 40), base=(-54, 48), wing=(-35, 44), root=(-43, 2), kind='wedge'),
    mouth=dict(x=-40, y=65, w=20, lips=0),
    side=None, socket=1, ear=1.0, neck=dict(w=1.0), hair=None, extras=None, sex='m',
)


def P(base, over=None, **kw):
    """A character: DEFAULT with its own values put over (nested dicts are merged)."""
    out = {}
    for k, v in base.items():
        out[k] = dict(v) if isinstance(v, dict) else v
    for src in (over or {}), kw:
        for k, v in src.items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k].update(v)
            else:
                out[k] = v
    return out


# ---------- features (shared by the views) ----------

def eye(cx, cy, w, h, s, p, e, far=False):
    """An eye. s = +1: inner corner on the left (near eye in 3/4, right eye in front); -1: mirrored."""
    ek = p['eye']; op = e.get('op', 1.0); kind = ek['kind']
    X = lambda t: cx + s * t
    out = []
    if op <= 0.15:   # laughing, shut: an arc
        out.append(shape([(X(-w / 2), cy + 2), (X(-w / 6), cy - h * 0.55, 's'), (X(w / 4), cy - h * 0.5, 's'), (X(w / 2 + 2), cy + 3),
                          (X(w / 4), cy - h * 0.5 + ek['lid'] + 1, 's'), (X(-w / 6), cy - h * 0.55 + ek['lid'], 's')], BLACK))
        return ''.join(out)
    hh = h * op
    if kind == 'kid':
        alm = [(X(-w / 2), cy + 1, 's'), (X(-w / 5), cy - hh, 's'), (X(w / 4), cy - hh * 0.95, 's'), (X(w / 2), cy, 's'),
               (X(w / 5), cy + hh * 0.8, 's'), (X(-w / 4), cy + hh * 0.75, 's')]
    else:
        alm = [(X(-w / 2), cy + 2), (X(-w / 6), cy - hh, 's'), (X(w / 4), cy - hh * 0.92, 's'), (X(w / 2), cy - 1),
               (X(w / 8), cy + hh * 0.55, 's')]
    lk = e.get('look', (0, 0))
    ix, iy = X(-w * 0.06) + lk[0] - (2 if not far else 0), cy - hh * 0.12 + lk[1]
    r = ek['r'] * (0.9 if far else 1)
    inner = f'<ellipse cx="{ix:.1f}" cy="{iy:.1f}" rx="{r * (0.8 if far else 1):.1f}" ry="{r * 1.08:.1f}" fill="{p["iris"]}"/>'
    if kind in ('kid', 'f') and op > 0.5:
        inner += f'<circle cx="{ix - r * 0.35:.1f}" cy="{iy - r * 0.4:.1f}" r="{r * 0.28:.1f}" fill="{WHITE}"/>'
    out.append(shape(alm, p['white']))
    out.append(clip(alm, inner))
    # upper lid: a black band growing to the outer corner
    t = ek['lid']
    lid = [(X(-w / 2 - 1), cy + 2.5), (X(-w / 6), cy - hh - t * 0.55, 's'), (X(w / 4), cy - hh * 0.92 - t * 0.9, 's')]
    if ek['lash']:
        lid += [(X(w / 2 + 6), cy - hh * 0.5 - 6), (X(w / 2 + 1), cy)]
    else:
        lid += [(X(w / 2 + 2), cy - 1.5)]
    lid += [(X(w / 2), cy - 0.5), (X(w / 4), cy - hh * 0.92 + 0.6, 's'), (X(-w / 6), cy - hh + 0.4, 's')]
    out.append(shape(lid, BLACK))
    if ek.get('lower') and not far:
        out.append(wedge((X(w / 2 - 1), cy), (X(0), cy + hh * 0.55 + 1), 1.8, 0.6, BLACK, bend=-s * 1.5))
    return ''.join(out)


def brow(a, b, t, p, e, s=1):
    """Brow from the inner end a to the outer end b; e['tilt'] > 0 pulls the inner end down (anger)."""
    r, tl = e.get('brow', 0), e.get('tilt', 0)
    a = (a[0], a[1] - r + tl); b = (b[0], b[1] - r - tl * 0.5)
    mx, my = (a[0] * 0.4 + b[0] * 0.6), (a[1] * 0.4 + b[1] * 0.6) - 4 - max(0, -tl) * 0.3
    pts = [(a[0], a[1] - t * 0.5), (mx, my - t * 0.55, 's'), (b[0], b[1]), (mx, my + t * 0.35, 's'), (a[0], a[1] + t * 0.5)]
    return shape(pts, p['browcol'])


def mouth(mx, my, wn, wf, p, e):
    """Mouth around (mx, my); wn / wf — half widths on the near and the far side (equal in front view)."""
    kind = e.get('mouth', 'neutral'); lips = p['mouth'].get('lips', 0); lip = p['lip']
    out = []
    if kind in ('grin', 'o', 'angry_open'):
        if kind == 'grin':
            wn2, wf2 = wn * 1.35, wf * 1.35
            hole = [(mx - wf2, my - 5), (mx, my - 1, 's'), (mx + wn2, my - 7), (mx + wn2 * 0.55, my + 13, 's'), (mx - wf2 * 0.3, my + 17, 's')]
            teeth = [(mx - wf2, my - 8), (mx + wn2, my - 9), (mx + wn2, my + 0.5), (mx, my + 4.5, 's'), (mx - wf2, my + 1)]
            tongue = [(mx - wf2 * 0.6, my + 18), (mx - wf2 * 0.2, my + 10, 's'), (mx + wn2 * 0.5, my + 10, 's'), (mx + wn2 * 0.7, my + 18)]
        else:
            hole = [(mx - wf * 0.6, my + 2, 's'), (mx, my - 6, 's'), (mx + wn * 0.55, my + 1, 's'), (mx + wn * 0.35, my + 14, 's'), (mx - wf * 0.3, my + 15, 's')]
            teeth = [(mx - wf * 0.5, my - 8), (mx + wn * 0.5, my - 8), (mx + wn * 0.45, my - 1.5), (mx - wf * 0.45, my - 1)]
            tongue = [(mx - wf * 0.6, my + 18), (mx - wf * 0.1, my + 9, 's'), (mx + wn * 0.4, my + 10, 's'), (mx + wn * 0.6, my + 18)]
        out.append(shape(hole, '#1a0d10'))
        out.append(clip(hole, shape(teeth, WHITE) + shape(tongue, lip)))
        if lips:
            out.append(shape([(hole[0][0] - 1, hole[0][1] + 1), (mx - wf * 0.4, my - 9 if kind == 'o' else my - 8, 's'), (mx, my - 5 if kind == 'grin' else my - 9, 's'),
                              (mx + wn * 0.5, my - 10, 's'), (hole[2][0] + 1, hole[2][1] + 1), (mx, hole[1][1] + 0.5, 's')], lip))
        return ''.join(out)
    c = {'neutral': 0, 'smile': -5, 'sad': 5, 'angry': 4, 'tight': 1.5, 'smirk': 0}[kind]
    a = (mx - wf, my + c); b = (mx + wn, my + c + (-6 if kind == 'smirk' else 0)); m = (mx, my + (1.5 if kind == 'smile' else -1 if kind in ('sad', 'angry') else 0))
    if kind in ('tight', 'angry'):
        a = (mx - wf * 0.85, a[1]); b = (mx + wn * 0.85, b[1])
    if lips:
        up = [a, (mx - wf * 0.45, m[1] - 4.5 * lips, 's'), (mx - 1, m[1] - 3 * lips), (mx + wn * 0.45, m[1] - 5 * lips, 's'), b, (mx + wn * 0.5, m[1] + 0.8, 's'), (m[0], m[1] + 1.2, 's'), (mx - wf * 0.5, m[1] + 0.8, 's')]
        lo = [a, (mx - wf * 0.5, m[1] + 0.5, 's'), (m[0], m[1] + 1, 's'), (mx + wn * 0.5, m[1] + 0.5, 's'), b, (mx + wn * 0.45, m[1] + 6 * lips, 's'), (mx - wf * 0.4, m[1] + 6.5 * lips, 's')]
        out.append(shape(lo, p.get('lip2', lip)))
        out.append(shape(up, p.get('lipdark', BLACK) if p.get('lipblack') else lip))
        out.append(line([a, (mx - wf * 0.5, m[1] + 0.6, 's'), (m[0], m[1] + 1, 's'), (mx + wn * 0.5, m[1] + 0.6, 's'), b], BLACK, 1.6))
        out.append(shape([(mx - wf * 0.35, m[1] + 6.5 * lips + 1.5), (mx + wn * 0.4, m[1] + 6 * lips + 1.5), (mx + wn * 0.2, m[1] + 6 * lips + 4.5), (mx - wf * 0.2, m[1] + 6.5 * lips + 4.5)], BLACK))
    else:
        out.append(shape([a, (m[0], m[1] - 1.6, 's'), b, (mx + wn * 0.4, m[1] + 1.8, 's'), (mx - wf * 0.4, m[1] + 1.6, 's')], BLACK))
        out.append(shape([(mx - wf * 0.45, m[1] + 9), (mx + wn * 0.5, m[1] + 8.5), (mx + wn * 0.25, m[1] + 12.5), (mx - wf * 0.3, m[1] + 12.5)], BLACK))
    if kind in ('smile', 'smirk'):   # the corner goes into the cheek
        out.append(wedge(b, (b[0] + 4, b[1] - 6), 2.4, 0.5, BLACK, bend=1.5))
    if kind == 'smile':
        out.append(wedge(a, (a[0] - 2, a[1] - 5), 2, 0.5, BLACK, bend=-1))
    return ''.join(out)


# ---------- the three-quarter view ----------

def head_q(p, e):
    o = p['q']; ey = p['eye_y']; ek = p['eye']; nz = p['nose']; mo = p['mouth']
    order = ['crown', 'backtop', 'back', 'occ', 'nape', 'jaw', 'chinr', 'chinl', 'muzzle', 'cheek', 'socket', 'brow', 'fore']
    outl = [o[k] for k in order]
    hair = p.get('hair'); s = []
    if hair:
        s.append(hair('q', 'back', p, e))
    # ear
    k = p['ear']; ex, e_y = o['nape'][0] + 2, ey + 16
    earp = [(ex - 8, e_y - 20 * k), (ex + 9 * k, e_y - 24 * k, 's'), (ex + 14 * k, e_y - 6 * k, 's'), (ex + 4 * k, e_y + 16 * k), (ex - 6, e_y + 12 * k)]
    s.append(form(earp, p['skin'], lit=(-3, -2), shadows=[[(ex - 2, e_y - 14 * k), (ex + 8 * k, e_y - 12 * k), (ex + 2, e_y + 8 * k)]], rim=p['rim']))
    # the planes turned from the light
    side = p['side'] or [(36, -66), (30, -16), (24, 22), (4, 50), (6, 84), o['chinr'], (60, 130), (120, 60), (110, -90)]
    sh = [side]
    br = p['brow']; by = ey - 15 + br['y']
    near_in, near_out = (-28, by + 1), (-28 + 46 * br['len'], by - 5)
    far_in, far_out = (-45, by + 1), (o['brow'][0] + 3, by - 2)
    if p['socket']:
        d0 = e.get('brow', 0) * 0.6
        sh.append([(near_in[0], near_in[1] - d0), (near_out[0], near_out[1] - d0), (near_out[0] + 2, ey + 4), (ex - 20, ey + 6), (-24, ey + 5)])
        sh.append([(far_in[0], far_in[1] - d0), (far_out[0] - 6, far_out[1] - d0), (o['socket'][0] - 6, ey + 6), (-42, ey + 5)])
    if p.get('folds'):
        sh += p['folds']('q', p, e)
    lights = p['lights']('q', p, e) if p.get('lights') else []
    if e.get('cheeks') and p.get('cheekfold', 1):
        sh.append([(mo['x'] + mo['w'] * 1.5, mo['y'] - 20), (mo['x'] + mo['w'] * 1.9, mo['y'] - 8, 's'), (mo['x'] + mo['w'] * 1.55, mo['y'] + 6), (mo['x'] + mo['w'] * 1.72, mo['y'] - 8, 's')])
    s.append(form(outl, p['skin'], lit=(-4, -2.5), shadows=sh, lights=lights, rim=p['rim']))
    # nose: its own piece of light with the black side plane
    tip, base, wing, root = nz['tip'], nz['base'], nz['wing'], nz['root']
    s.append(shape([(root[0] - 1, root[1] - 6), tip, base, wing, (wing[0] + 2, root[1] + 10)], p['skin']))
    if nz['kind'] == 'wedge':
        s.append(shape([(root[0] + 3, root[1]), (tip[0] + 9, tip[1] - 2), (tip[0] + 5, tip[1] + 3), base, (wing[0], wing[1] + 1),
                        (wing[0] + 3, wing[1] - 8, 's'), (wing[0] - 3, wing[1] - 16)], BLACK))
    else:
        s.append(shape([(tip[0] + 4, tip[1] + 2), base, (wing[0], wing[1] + 1), (wing[0] + 2, wing[1] - 5, 's'), (wing[0] - 5, wing[1] - 3, 's')], BLACK))
        if nz['kind'] == 'line':
            s.append(wedge((root[0] + 4, root[1] + 6), (tip[0] + 10, tip[1] - 6), 0.6, 2.2, BLACK, bend=-1.5))
    # eyes, brows
    dn = e.get('cheeks', 0) * -1.5
    if not p.get('hide_far_eye'):
        s.append(eye(-49.5, ey + 1 + dn, ek['w'] * 0.5, ek['h'], -1, p, e, far=True))
        s.append(brow(far_in, far_out, br['t'] * 0.85, p, e))
    if not p.get('hide_near_eye'):
        s.append(eye(-7, ey + dn, ek['w'], ek['h'], 1, p, e))
        s.append(brow(near_in, near_out, br['t'], p, e))
    if p.get('beard'):
        s.append(p['beard']('q', p, e))
    s.append(mouth(mo['x'], mo['y'], mo['w'], mo['w'] * 0.55, p, e))
    if p.get('extras'):
        s.append(p['extras']('q', p, e))
    if hair:
        s.append(hair('q', 'front', p, e))
    return ''.join(s)


def neck_q(p, w=1.0, length=60):
    """Neck under the three-quarter head: almost all in the head's shadow, a strip of light on the throat."""
    o = p['q']; k = p['neck']['w'] * w
    a = (o['chinr'][0] - 6, o['chinr'][1] - 14); b = (o['nape'][0] - 2, o['nape'][1] - 6)
    pts = [a, b, (b[0] + 4 * k, b[1] + length), (a[0] - 14 * k + 10, a[1] + length + 10)]
    bot = a[1] + length + 20
    cast = [(a[0] - 30, a[1] - 4), (b[0] + 30, b[1]), (b[0] + 30, bot), (a[0] + 20, bot), (a[0] + 16, a[1] + 18), (a[0] - 30, a[1] + 9)]
    return form(pts, p['skin'], lit=(-3, 0), shadows=[cast], rim=p['rim'])


# ---------- the front view ----------

def front_outline(p):
    q = p['q']; f = dict(DEFAULT['f']); 
    jx, jy = q['jaw'][0], q['jaw'][1]; cw = (q['chinr'][0] - q['chinl'][0]) / 2 + 4; cy = q['chinl'][1]
    wide = (q['jaw'][0] - 38) * 0.6
    soft = len(q['cheek']) > 2
    f.update(jawr=(jx + 9, jy + 2), jawl=(-jx - 9, jy + 2), chinr=(cw, cy), chinl=(-cw, cy),
             cheekr=(62 + wide, q['cheek'][1], 's') if soft else (62 + wide, q['cheek'][1]),
             cheekl=(-62 - wide, q['cheek'][1], 's') if soft else (-62 - wide, q['cheek'][1]),
             templer=(66 + wide, -20, 's'), templel=(-66 - wide, -20, 's'))
    f.update(p.get('f_over', {}))
    return f


def head_f(p, e):
    o = front_outline(p); ey = p['eye_y']; ek = p['eye']; nz = p['nose']; mo = p['mouth']
    order = ['crown', 'tr', 'templer', 'cheekr', 'jawr', 'chinr', 'chinl', 'jawl', 'cheekl', 'templel', 'tl']
    outl = [o[k] for k in order]
    hair = p.get('hair'); s = []
    if hair:
        s.append(hair('f', 'back', p, e))
    k = p['ear']
    for sg in (-1, 1):
        ex = sg * (abs(o['templer'][0]) - 2)
        earp = [(ex, ey - 6), (ex + sg * 12 * k, ey - 12 * k, 's'), (ex + sg * 14 * k, ey + 8 * k, 's'), (ex + sg * 4, ey + 32 * k), (ex - sg * 2, ey + 28)]
        s.append(form(earp, p['skin'], lit=(-3, -2) if sg < 0 else None, shadows=[earp] if sg > 0 else [], rim=p['rim']))
    cx = o['cheekr'][0]
    sh = [p.get('side_f') or [(cx - 12, -80), (cx - 16, -14), (cx - 22, o['cheekr'][1] - 4), (cx - 36, 56), (o['jawr'][0] - 22, 84), o['chinr'], (60, 130), (120, 0), (100, -100)]]
    br = p['brow']; by = ey - 15 + br['y']
    if p['socket']:
        for sg in (-1, 1):
            sh.append([(sg * 9, by), (sg * 46, by - 4), (sg * 46, ey + 5), (sg * 10, ey + 6)])
    if p.get('folds'):
        sh += p['folds']('f', p, e)
    if e.get('cheeks') and p.get('cheekfold', 1):
        w = mo['w'] * 1.1
        sh.append([(w * 1.5, mo['y'] - 20), (w * 1.9, mo['y'] - 8, 's'), (w * 1.55, mo['y'] + 6), (w * 1.72, mo['y'] - 8, 's')])
        sh.append([(-w * 1.5, mo['y'] - 20), (-w * 1.8, mo['y'] - 8, 's'), (-w * 1.55, mo['y'] + 6), (-w * 1.68, mo['y'] - 8, 's')])
    s.append(form(outl, p['skin'], lit=(-4, -2.5), shadows=sh, rim=p['rim']))
    ty = nz['tip'][1]; nw = (nz['wing'][0] - nz['base'][0]) * 0.75
    if nz['kind'] == 'wedge':
        s.append(shape([(1, ey - 6), (5, ty - 10), (nw + 3, ty), (nw, ty + 7), (5, ty + 9, 's'), (-nw * 0.8, ty + 7), (-nw * 0.9, ty + 3), (-2, ty + 2)], BLACK))
    else:
        s.append(shape([(-nw * 0.75, ty + 4), (0, ty + 1, 's'), (nw * 0.9, ty + 2), (nw * 0.7, ty + 7), (2, ty + 9, 's'), (-nw * 0.6, ty + 7)], BLACK))
        if nz['kind'] == 'line':
            s.append(wedge((3, ey + 4), (5, ty - 6), 0.6, 2.2, BLACK, bend=-1))
    dn = e.get('cheeks', 0) * -1.5
    w = ek['w'] * 0.92
    if not p.get('hide_far_eye'):
        s.append(eye(-27, ey + dn, w, ek['h'], -1, p, e)); s.append(brow((-9, by + 1), (-9 - 37 * br['len'], by - 4), br['t'], p, e))
    s.append(eye(27, ey + dn, w, ek['h'], 1, p, e)); s.append(brow((9, by + 1), (9 + 37 * br['len'], by - 4), br['t'], p, e))
    if p.get('beard'):
        s.append(p['beard']('f', p, e))
    s.append(mouth(0, mo['y'], mo['w'] * 0.95, mo['w'] * 0.95, p, e))
    if p.get('extras'):
        s.append(p['extras']('f', p, e))
    if hair:
        s.append(hair('f', 'front', p, e))
    return ''.join(s)


def neck_f(p, length=60):
    o = front_outline(p); k = p['neck']['w']; w = (o['jawr'][0] - 14) * k
    pts = [(-w, 70), (w, 70), (w + 3, 96 + length), (-w - 3, 96 + length)]
    return form(pts, p['skin'], lit=(-3, 0), shadows=[[(-w - 9, 60), (w + 9, 60), (w + 9, 200), (-w * 0.45, 200), (-w * 0.5, o['chinl'][1] + 18), (-w - 9, o['chinl'][1] + 4)]], rim=p['rim'])


# ---------- the side view ----------

def side_outline(p):
    q = p['q']; nz = p['nose']; mo = p['mouth']; s = dict(DEFAULT['s'])
    tx = -84 + (nz['tip'][0] + 73) * 1.3; ty = nz['tip'][1]; my = mo['y']; cy = q['chinl'][1]
    young = p['eye_y'] - 8
    s.update(tip=(tx, ty), nosebase=(-59, ty + 7), lipu=(-65, my - 7), mouth=(-57, my - 1), lipl=(-63, my + 6), chinfold=(-55, my + 13),
             chin=(-59, cy - 8), chinb=(-38, cy), jaw=(q['jaw'][0] - 12, q['jaw'][1] + 4), root=(-60 + young * 0.3, p['eye_y'] - 4), brow=(-64 + young * 0.2, p['eye_y'] - 18),
             nape=(q['nape'][0] + 2, q['nape'][1]))
    s.update(p.get('s_over', {}))
    return s


def head_s(p, e):
    o = side_outline(p); ey = p['eye_y']; ek = p['eye']; nz = p['nose']; mo = p['mouth']
    order = ['crown', 'backtop', 'back', 'occ', 'nape', 'jaw', 'chinb', 'chin', 'chinfold', 'lipl', 'mouth', 'lipu', 'nosebase', 'tip', 'root', 'brow', 'fore']
    outl = [o[k] for k in order]
    hair = p.get('hair'); s = []
    if hair:
        s.append(hair('s', 'back', p, e))
    sh = [p.get('side_s') or [(66, -70), (60, -10), (50, 40), (34, 62), (10, 70), (-14, 90), o['chinb'], (60, 130), (130, 60), (120, -90)],
          ]
    if p.get('hollow'):
        sh.append([(8, 30), (-22, 50), (-8, 54), (14, 44)])
    if p.get('folds'):
        sh += p['folds']('s', p, e)
    s.append(form(outl, p['skin'], lit=(-3, -2), shadows=sh, rim=p['rim']))
    # the plane under the nose, the lips
    tip, nb = o['tip'], o['nosebase']
    s.append(shape([(tip[0] + 5, tip[1] + 3), (nb[0] - 1, nb[1] + 1), (nb[0] + 14, nb[1] - 3), (nb[0] + 12, nb[1] - 9, 's'), (nb[0] + 4, nb[1] - 6, 's')], BLACK))
    kind = e.get('mouth', 'neutral'); m = o['mouth']
    if p['mouth'].get('lips'):
        s.append(shape([o['lipu'], (o['lipu'][0] + 2, o['lipu'][1] - 4), (m[0] + 12, m[1] - 1), m], p['lip']))
        s.append(shape([o['lipl'], m, (m[0] + 10, m[1] + 1), (o['lipl'][0] + 4, o['lipl'][1] + 3)], p.get('lip2', p['lip'])))
    c = {'smile': -5, 'smirk': -4, 'sad': 5, 'angry': 4, 'grin': -6}.get(kind, 0)
    if kind in ('grin', 'o'):
        hole = [(m[0] - 4, m[1] - 3), (m[0] + 18, m[1] - 8), (m[0] + 12, m[1] + 12), (m[0] - 3, m[1] + 10)]
        s.append(shape(hole, '#1a0d10') + clip(hole, shape([(m[0] - 6, m[1] - 9), (m[0] + 20, m[1] - 9), (m[0] + 20, m[1] - 2), (m[0] - 6, m[1])], WHITE)
                                               + shape([(m[0] - 2, m[1] + 12), (m[0] + 8, m[1] + 5), (m[0] + 16, m[1] + 12)], p['lip'])))
    else:
        s.append(wedge((m[0] - 1, m[1]), (m[0] + 17, m[1] + c), 2.6, 1.0, BLACK, bend=-c * 0.3))
    s.append(shape([(o['chinfold'][0] + 2, o['chinfold'][1] - 2), (o['chinfold'][0] + 14, o['chinfold'][1] - 3), (o['chinfold'][0] + 8, o['chinfold'][1] + 2)], BLACK))
    # ear
    k = p['ear']; ex, e_y = 36, ey + 14
    earp = [(ex - 8, e_y - 20 * k), (ex + 10 * k, e_y - 24 * k, 's'), (ex + 15 * k, e_y - 6 * k, 's'), (ex + 4 * k, e_y + 18 * k), (ex - 7, e_y + 12 * k)]
    s.append(form(earp, p['skin'], lit=(-3, -2), shadows=[[(ex - 2, e_y - 14 * k), (ex + 9 * k, e_y - 12 * k), (ex + 2, e_y + 8 * k)]]))
    # eye and brow
    if not p.get('hide_side_eye'):
        op = e.get('op', 1.0); hh = ek['h'] * op * 1.05; x0 = o['root'][0] + 9; dn = e.get('cheeks', 0) * -1.5; y = ey + dn
        if op <= 0.15:
            s.append(wedge((x0, y + 1), (x0 + 20, y + 2), 3.4, 1.5, BLACK, bend=-4))
        else:
            alm = [(x0, y - hh), (x0 + 19, y), (x0 + 2, y + hh * 0.55), (x0 - 2, y - hh * 0.2, 's')]
            s.append(shape(alm, p['white']) + clip(alm, f'<ellipse cx="{x0 + 3}" cy="{y - hh * 0.15:.1f}" rx="{ek["r"] * 0.55:.1f}" ry="{ek["r"] * 1.05:.1f}" fill="{p["iris"]}"/>'))
            lid = [(x0 - 2, y - hh - ek['lid'] * 0.6), (x0 + 21, y - 1)] + ([(x0 + 27, y - 7), (x0 + 20, y + 1)] if ek['lash'] else [(x0 + 21, y + 1)]) + [(x0 + 1, y - hh + ek['lid'] * 0.5)]
            s.append(shape(lid, BLACK))
        br = p['brow']; by = ey - 15 + br['y']
        s.append(brow((o['brow'][0] + 4, by + 2), (o['brow'][0] + 4 + 34 * br['len'], by - 3), br['t'], p, e))
    if p.get('beard'):
        s.append(p['beard']('s', p, e))
    if p.get('extras'):
        s.append(p['extras']('s', p, e))
    if hair:
        s.append(hair('s', 'front', p, e))
    return ''.join(s)


def neck_s(p, length=60):
    o = side_outline(p); k = p['neck']['w']
    a = (o['chinb'][0] + 14, o['chinb'][1] - 14); b = (o['nape'][0] - 2, o['nape'][1] - 6)
    pts = [a, b, (b[0] + 8, b[1] + length), (a[0] + 2 + 10 * (1 - k), a[1] + length + 14)]
    bot = a[1] + length + 30
    return form(pts, p['skin'], lit=(-3, 0), shadows=[[(a[0] - 30, a[1] - 4), (b[0] + 30, b[1]), (b[0] + 30, bot), (a[0] + 16, bot), (a[0] + 10, a[1] + 18), (a[0] - 30, a[1] + 9)]])


def neck(view, p, **kw):
    return {'q': neck_q, 'f': neck_f, 's': neck_s}[view](p, **kw)


def head(view, p, e=None):
    e = e if isinstance(e, dict) else EXPR[e or 'calm']
    if p.get('expr_fix'):
        e = p['expr_fix'](dict(e))
    return {'q': head_q, 'f': head_f, 's': head_s}[view](p, e)
