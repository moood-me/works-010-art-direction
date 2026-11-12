"""A whole figure from a description: the skeleton (body3d.Body), the head module, the garments, the hands, and
items drawn at given stages. The order: hair behind; the far arm when it is behind the body; legs and shoes; a skirt
or a coat's tails; the head with its neck; the torso's garments as one shape with the arms that hang at its sides;
the lines of those arms and their hands; arms in front of the body; the hair in front; items in front."""
import math
from pen import *
from body3d import *


def neutralize(d):
    """The same figure standing with its arms down and the head straight (for turnarounds and expression sheets)."""
    B = d['B']; j = dict(B.j); H = d['H']
    for side, sg in (('r', -1), ('l', 1)):
        sx, sy, sz = j['sh_' + side]
        j['el_' + side] = (sx * 1.1, sy + 0.18 * H, -0.06)
        j['wr_' + side] = (sx * 1.04, sy + 0.32 * H, 0.06)
    d = dict(d)
    d['B'] = Body(j, B.sections, B.spine, B.twist)
    A = dict(d['arms']); A['front'] = []; A['behind'] = []; A['front_from'] = {}
    A['hands'] = dict(r=dict(pose='relaxed', twist=90, size=A['hands']['r']['size'] if A['hands']['r'] else 0.6),
                      l=dict(pose='relaxed', twist=90, size=A['hands']['l']['size'] if A['hands']['l'] else 0.6))
    d['arms'] = A
    hd = dict(d.get('head', {})); hd.update(yaw_rel=0, pitch=0, roll=0)
    d['head'] = hd
    return d


def figure(v, d, e=None, lw=2.0, neutral=False, bust=False):
    if neutral:
        d = neutralize(d)
    B = d['B']; j = B.j; mod = d['mod']; H = d['H']
    near = 'r' if v.yaw >= 0 else 'l'
    far = 'l' if near == 'r' else 'r'
    o = []
    st = lambda name: ''.join(f(v, B, lw, near) for f in d.get('items', {}).get(name, []))
    hv = dict(d.get('head', {})); hv.update(e=e, lw=lw)
    hv.setdefault('hs', 1.08)
    pit_off = hv.pop('pit', (0, 0.02, 0.06))
    pit = add3(j['neck'], pit_off)
    o.append(st('back'))
    o.append(head3d(v, mod, pit, part='back', **hv))
    A = d['arms']
    arm_r = A['r']
    def arm_shapes(side):
        pts, rad = arm_chain(j, side, arm_r)
        sl = A.get('sleeve')
        if sl:
            sp, sr = arm_chain(j, side, arm_r, grow=sl.get('grow', 0.03), until=sl.get('until', 0.93))
        else:
            sp, sr = pts, rad
        P, C, N, rr = chain_outline(v, sp, sr, caps=(True, True))
        skin = None
        if sl and sl.get('until', 0.93) < 0.8:
            # bare forearm below a short or rolled sleeve
            Ps, Cs, Ns, rs = chain_outline(v, pts, rad, caps=(False, True))
            skin = (Ps, Cs, Ns, rs)
        return dict(pts=pts, rad=rad, P=P, C=C, N=N, rr=rr, sp=sp, sr=sr, skin=skin)
    arms = {s: arm_shapes(s) for s in ('r', 'l')}
    front_arms = A.get('front', [])
    behind = A.get('behind', [])

    ff = A.get('front_from', {})

    def arm_detail(side, merged):
        a = arms[side]; sl = A.get('sleeve') or {}
        g = ''
        if side in ff and merged:
            # the upper arm is merged at the side; the forearm comes across in front: draw it as its own shape
            t = ff[side]
            n = len(a['sp'])
            k = max(1, int(t * (n - 1)))
            sub, subr = a['sp'][k - 1:], a['sr'][k - 1:]
            P2, C2, N2, r2 = chain_outline(v, sub, subr, caps=(True, True))
            g += limb_lines(a['C'], a['N'], a['rr'], lw, start=0.3, end=t * 0.95)
            g += group([P2], lw, base=sl.get('tone', 0.0), dark=sl.get('dark', 0.35), black=sl.get('black', False), s=v.s)
            g += fold_lines(C2, N2, r2, 2, lw * 0.7, side=1, n=2, seed=9, ink=sl.get('fold_ink', INK))
            a = dict(a); a['C'], a['N'], a['rr'] = C2, N2, r2
            merged = None
        if a['skin']:
            Ps, Cs, Ns, rs = a['skin']
            g += group([Ps], lw, base=0, dark=A.get('skin_dark', 0.0), s=v.s, shadow=False)
            g += A.get('skin_extra', lambda *x: '')(v, Ps, lw)
        if merged:
            g += limb_lines(a['C'], a['N'], a['rr'], lw, start=0.3)
        elif merged is None:
            pass
        else:
            g += group([a['P']], lw, base=sl.get('tone', 0.0), dark=sl.get('dark', 0.35), black=sl.get('black', False), s=v.s)
            g += sl.get('extra', lambda *x: '')(v, a['P'], lw)
        if sl:
            g += fold_lines(a['C'], a['N'], a['rr'], int(len(a['C']) * 0.5), lw * 0.7, side=1 if side == near else -1, seed=3 + (side == 'l'),
                            ink=sl.get('fold_ink', INK))
            if sl.get('cuff', True):
                g += stroke(ring_around(v, a['sp'][-2], a['sp'][-1], 0.9, a['sr'][-1] * 0.98), lw * 0.7, fill=sl.get('fold_ink', INK))
        hd = A['hands'][side]
        if hd:
            if hd.get('hold_item'):
                g += hd['hold_item'](v, a['pts'], lw)
            g += hand_at(v, a['pts'][-1], a['pts'][-2], hd.get('size', 0.6), hd.get('pose', 'relaxed'), twist=hd.get('twist', 90),
                         side=hd.get('side', 1), lw=lw, turn=hd.get('turn', 0), tilt=hd.get('tilt', 0))
            if hd.get('over'):
                g += hd['over'](v, a['pts'], lw)
        return g

    for s in behind:
        o.append(arm_detail(s, False))
    # legs
    L = d['legs']
    def leg(side):
        pts, rad = leg_chain(j, side, L['r'], top=L.get('top'))
        g = ''
        gm = L.get('garment')
        if gm and gm.get('kind') == 'trousers':
            if gm.get('until', 1.0) < 1.0:
                P0, C0, N0, r0 = chain_outline(v, pts, rad)
                g += group([P0], lw, base=L.get('skin_tone', 0.0), dark=L.get('skin_dark', 0.12), s=v.s)
                if L.get('knee_extra'):
                    g += L['knee_extra'](v, side, j, lw)
            tp, tr = leg_chain(j, side, L['r'], grow=gm.get('grow', 0.04), top=L.get('top'), until=gm.get('until', 1.0))
            tr = [r + gm.get('flare', 0.0) * i / (len(tr) - 1) for i, r in enumerate(tr)]
            P, C, N, rr = chain_outline(v, tp, tr, caps=(True, gm.get('until', 1.0) < 1.0))
            g += group([P], lw, base=gm.get('tone', 0.0), dark=gm.get('dark', 0.35), black=gm.get('black', False), s=v.s)
            g += fold_lines(C, N, rr, int(len(C) * 0.5), lw * 0.6, side=-1, seed=5 + (side == 'l'))
            g += fold_lines(C, N, rr, int(len(C) * 0.85), lw * 0.55, side=1, n=2, seed=7 + (side == 'l'))
        else:
            P, C, N, rr = chain_outline(v, pts, rad)
            g += group([P], lw, base=L.get('skin_tone', 0.0), dark=L.get('skin_dark', 0.12), s=v.s)
        sh = L['shoe']
        hull, sole = shoe3d(v, j['heel_' + side], j['toe_' + side], width=sh.get('w', 0.16), height=sh.get('h', 0.24), toe_h=sh.get('toe_h', 0.09), kind=sh.get('kind', 'shoe'))
        g += group([hull], lw, base=sh.get('tone', 0.0), dark=sh.get('dark', 0.35), black=sh.get('black', False), s=v.s)
        g += stroke(sole, lw * 0.6, fill=PAPER if sh.get('black') else INK)
        if sh.get('extra'):
            g += sh['extra'](v, side, j, lw)
        return g
    if not bust:
        o.append(st('legs_back'))
        o.append(leg(far)); o.append(leg(near))
        o.append(st('legs'))
    # skirt / coat tails
    for sk in ([] if bust else d.get('skirts', [])):
        f_top = frac(H, sk['top'], j); f_hem = frac(H, sk['hem'], j)
        fl = sk.get('flare', 0.3)
        P, hem, _ = torso_outline(B, v, f_hem, f_top, grow=sk.get('grow', 0.03), flare=lambda f, f_top=f_top, fl=fl: max(0.0, f_top - f) * fl)
        g = group([P], lw, base=sk.get('tone', 0.2), dark=sk.get('dark', 0.45), black=sk.get('black', False), s=v.s, off=0.07)
        for a in sk.get('folds', (-60, -25, 5, 35, 65)):
            if v.facing((math.sin(math.radians(a)), 0, math.cos(math.radians(a)))) > 0.15:
                p0 = surf(B, f_top - 0.05, a, sk.get('grow', 0.03)); p1 = surf(B, f_hem + 0.01, a * 1.1, sk.get('grow', 0.03) + (f_top - f_hem) * fl)
                g += seams(v, [p0, lerp3(p0, p1, 0.6), p1], lw, 0.55, ink=sk.get('fold_ink', INK))
        o.append(g + (sk['extra'](v, B, lw, P) if sk.get('extra') else ''))
    o.append(st('mid'))
    # head
    o.append(head3d(v, mod, pit, **hv))
    o.append(st('neck'))
    # torso garments, merged with the arms at the sides
    T = d['torso']
    side_arms = [s for s in ('r', 'l') if s not in front_arms and s not in behind]
    for i, layer in enumerate(T):
        f_lo = frac(H, layer['bottom'], j)
        fl = layer.get('flare')
        flf = None
        if fl:
            f_w = frac(H, fl[0], j)
            flf = lambda f, f_w=f_w, k=fl[1]: max(0.0, f_w - f) * k
        P, hem, _ = torso_outline(B, v, f_lo, layer.get('top', 1.0), grow=layer.get('grow', 0.04), flare=flf, levels=60 if fl else 40)
        polys = [P]
        if layer.get('with_arms'):
            polys += [arms[s]['P'] for s in side_arms]
        g = group(polys, lw, base=layer.get('tone', 0.0), dark=layer.get('dark', 0.35), black=layer.get('black', False), s=v.s, off=layer.get('off', 0.06))
        if layer.get('extra'):
            g += layer['extra'](v, B, lw, P, polys)
        o.append(g)
    for s in side_arms:
        o.append(arm_detail(s, True))
    o.append(st('torso'))
    for s in front_arms:
        o.append(arm_detail(s, False))
    o.append(head3d(v, mod, pit, part='front', **hv))
    o.append(st('front'))
    return ''.join(o)
