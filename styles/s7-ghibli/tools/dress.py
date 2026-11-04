"""Putting a character together: skin, garments, hands, shoes, neck, head and hair, drawn far to near.

A character file gives `B` (body measures), poses, a garment `spec` and a `head_fn`; `draw_figure` does the rest.
Garment kinds: top (blouse/shirt/tee/sweater with sleeves, collar, buttons), over (cardigan/vest/jacket — an
opening at the front), bottom (skirt / trousers / shorts), apron, shoes. Small marks (folds, pockets, cuffs) are
lines laid on the 3D surface, drawn only where it faces the camera."""
import numpy as np
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union
from geo import tube, shift, smooth, polys, lines
from svgdoc import INK, mix, shade
from body import Loft, unit

LIGHT = (-1, -0.6)


def shadow_of(g, k):
    return g.difference(shift(g, LIGHT[0] * k, LIGHT[1] * k))


def fill_part(d, g, c, k, extra=None, line=True, w=None):
    if g is None or g.is_empty:
        return None
    sh = shadow_of(g, k)
    if extra is not None and not extra.is_empty:
        sh = sh.union(extra.intersection(g))
    sh = smooth(sh, 0.4).intersection(g)
    d.fill(g, c)
    d.fill(sh, shade(c))
    if line:
        d.outline(g, w)
    return sh


def patch(d, region, c, sh):
    """re-paint a region in a garment's colours without lines — joins a sleeve into its shoulder."""
    if region.is_empty:
        return
    d.fill(region, c)
    if sh is not None:
        d.fill(sh.intersection(region), shade(c))


def surface_line(d, view, loft, ts, ys, w, push=0.35, min_face=0.1, c=INK, clip=None):
    pts3 = [loft.pt(t, y, push) for t, y in zip(ts, ys)]
    fac = [loft.facing(view, t, y) for t, y in zip(ts, ys)]
    xy = view.xy(np.array(pts3))
    run = []
    for p, f in zip(xy, fac):
        if f > min_face:
            run.append(p)
        else:
            if len(run) > 1:
                _emit(d, run, w, c, clip)
            run = []
    if len(run) > 1:
        _emit(d, run, w, c, clip)


def _emit(d, run, w, c, clip):
    if clip is None:
        d.line(np.array(run), w, c)
        return
    for s in lines(LineString(run).intersection(clip)):
        d.line(np.asarray(s.coords), w, c)


def draw_figure(d, view, F, spec, head_fn):
    """F: a posed Figure. head_fn(d, view, F, back) places the head (back='prepare'), draws the hair behind
    (back=True) or the head and front hair (back=False)."""
    B, J, S = F.B, F.J, spec
    lw = d.lw
    k_sh = 0.10 * view.s * 10      # shadow offset for body parts, px
    skin = S['skin']
    torso = F.torso_loft()
    tz = float(view.depth(np.array([J['pelvis'] * 0.5 + (J['shl'] + J['shr']) * 0.25]))[0])
    items = []          # (depth, order, fn)

    # ---- place the head (its outline casts a shadow on the neck), hair behind everything
    head_fn(d, view, F, 'prepare')
    items.append((-1e9, 0, lambda: head_fn(d, view, F, True)))

    # ---- legs (under a skirt they always go first)
    bot = S.get('bottom', {})
    for side in ('l', 'r'):
        dz = float(view.depth(np.array([J['kn' + side]]))[0])
        items.append((dz - 1000, 1, lambda side=side: draw_leg(d, view, F, S, side, k_sh)))
    # ---- torso and the garments on it
    items.append((tz, 2, lambda: draw_torso(d, view, F, S, torso, k_sh)))
    # ---- arms
    for side in ('l', 'r'):
        dz = float(view.depth(np.array([(J['el' + side] + J['wr' + side]) / 2]))[0])
        # an arm hanging close beside the body: in front of the torso if its elbow is nearer than the side of
        # the chest at that height
        items.append((dz + 0.5, 3, lambda side=side: draw_arm(d, view, F, S, side, torso, k_sh)))
    if S.get('prop'):
        # a held thing goes in front of the body and behind the hands that hold it
        dz = min(float(view.depth(np.array([(J['el' + s_] + J['wr' + s_]) / 2]))[0]) for s_ in ('l', 'r'))
        items.append((dz + 0.49, 2.5, lambda: S['prop'](d, view, F)))
    items.sort(key=lambda x: (x[0], x[1]))
    for _, _, fn in items:
        fn()
    # ---- neck, then the head and front hair
    head_fn(d, view, F, False)


def draw_leg(d, view, F, S, side, k):
    """the bare (or stockinged) leg and the shoe; trousers are drawn with the torso, as one piece."""
    B, J = F.B, F.J
    lw = d.lw
    bot = S.get('bottom', {})
    legc = S.get('legs', S['skin'])
    g, pts = F.leg_shape(view, side)
    if 'shoes' in S:
        draw_shoe(d, view, F, S, side)
    if bot.get('kind') == 'trousers':
        return
    fill_part(d, g, legc, k * 0.5)
    if S.get('socks'):
        sg, _ = F.leg_shape(view, side, ease=0.25, start=0.86)
        fill_part(d, sg, S['socks'], k * 0.4)


def trousers(d, view, F, S, k):
    """the pelvis and both legs as one flat piece; the nearer leg keeps its inner line below the crotch."""
    B, J = F.B, F.J
    lw = d.lw
    bot = S['bottom']
    e = bot.get('ease', 1.2)
    upto = 1.0 if bot['kind'] == 'trousers' else bot.get('upto', 0.42)
    pel = F.torso_loft(push=e).shape(view, B['torso'][0][0], bot['waist'])
    legs = {}
    for side in ('l', 'r'):
        tg, _ = F.leg_shape(view, side, ease=e, upto=upto)
        if bot['kind'] == 'trousers':
            kn, an = J['kn' + side], J['an' + side]
            low = tube(view, [kn, an + [0, -1.5, 0]], [B['leg_r'][len(B['leg_r']) // 2] + e + 0.3, B['leg_r'][-1] + e + 1.6])
            tg = unary_union([tg, low])
        else:
            # the hem of shorts: a little flare
            kn, hp = J['kn' + side], J['hp' + side]
            hem = hp + (kn - hp) * upto
            tg = unary_union([tg, tube(view, [hem + (hp - kn) * 0.12, hem], [B['leg_r'][2] + e + 0.8] * 2)])
        legs[side] = tg
    g = smooth(unary_union([pel, legs['l'], legs['r']]), 0.5)
    sh = fill_part(d, g, bot['c'], k * 0.9)
    near = max(('l', 'r'), key=lambda s_: float(view.depth(np.array([J['kn' + s_]]))[0]))
    crotch = view.xy(np.array([[0, B['torso'][0][0] + 2, 0]]))[0][1]
    inner = g.buffer(-lw * 0.8)
    from shapely.geometry import box as _box
    cut = inner.intersection(_box(-1e4, crotch, 1e4, 1e4))
    for s_ in lines(legs[near].boundary.intersection(cut)):
        c = np.asarray(s_.coords)
        if len(c) > 2:
            d.line(c, lw)
    # folds: one at each knee, a break over the shoe
    for side in ('l', 'r'):
        kn = J['kn' + side]
        a = view.xy(np.array([kn + [-2.5, 2, 4.5], kn + [1, 0, 5.5]]))
        if upto > 0.8:
            d.line(a, lw * 0.5)


def draw_shoe(d, view, F, S, side):
    sh = S['shoes']
    g = F.shoe(view, side, sh)
    fill_part(d, g, sh['c'], 3)
    if sh.get('sole'):
        b = g.bounds
        sole = g.intersection(box(b[0], b[3] - (b[3] - b[1]) * 0.18, b[2], b[3]))
        d.fill(sole, sh['sole'])
        d.outline(g)


def draw_torso(d, view, F, S, torso, k):
    B, J = F.B, F.J
    lw = d.lw
    top, over, bot = S.get('top'), S.get('over'), S.get('bottom', {})
    # the neck first: the garments' necklines cut across it
    draw_neck(d, view, F, S, F.head_g)
    # skin under the neckline
    y_neck = B['torso'][-1][0]
    skin_t = torso.shape(view, B['chest_y'], y_neck)
    fill_part(d, skin_t, S['skin'], k * 0.4)
    # bottom garment
    if bot.get('kind') == 'skirt':
        sk = Loft(bot['rings'], 2.2, bot.get('wave'))
        g = sk.shape(view, n=30)
        sh = fill_part(d, g, bot['c'], k * 1.4)
        for t in bot.get('folds', []):
            ys = np.linspace(sk.y0 + 1, sk.y0 + (sk.y1 - sk.y0) * 0.55, 8)
            surface_line(d, view, sk, [t] * len(ys), ys, lw * 0.55, push=0.1, clip=g.buffer(-lw))
    elif bot.get('kind') in ('trousers', 'shorts'):
        trousers(d, view, F, S, k)
    # the top
    if top:
        g = F.torso_loft(push=top.get('ease', 0.7)).shape(view, top['hem'], y_neck)
        if top.get('tucked') and bot.get('kind') in ('trousers', 'shorts', 'skirt'):
            g = g.difference(box(-1e4, view.xy(np.array([[0, bot['waist'], 0]]))[0][1], 1e4, 1e4))
        if top.get('neck_cut'):
            g = g.difference(neck_cut(view, F, top['neck_cut']))
        sh = fill_part(d, g, top['c'], k)
        tl = F.torso_loft(push=top.get('ease', 0.7))
        for (ya, yb) in top.get('stripes', []):
            band = tl.shape(view, ya, yb, n=8, push=0.05).intersection(g).buffer(-lw * 0.5)
            d.fill(band, top['stripe_c'])
            d.fill(band.intersection(shadow_of(g, k)), shade(top['stripe_c']))
        if top.get('buttons'):
            for y in top['buttons']:
                if tl.facing(view, 0.0, y) > 0.2:
                    p = view.xy(tl.pt(0.0, y, 0.4)[None])[0]
                    b = Point(p).buffer(0.55 * view.s, 12)
                    d.fill(b, mix(top['c'], '#ffffff', 0.5)); d.outline(b, lw * 0.4)
        for m in top.get('marks', []):
            m(d, view, F, g)
    if over:
        lo = F.torso_loft(push=over.get('ease', 1.4))
        g = lo.shape(view, over['hem'], y_neck - 0.5)
        if over.get('open'):
            g = g.difference(front_open(view, lo, over['open'], over['hem'], y_neck))
        sh = fill_part(d, g, over['c'], k)
        if over.get('buttons'):
            side_t = over['open'][0] + 0.03 if over.get('open') else 0.0
            for y in over['buttons']:
                if lo.facing(view, side_t, y) > 0.2:
                    p = view.xy(lo.pt(side_t, y, 0.4)[None])[0]
                    b = Point(p).buffer(0.6 * view.s, 12)
                    d.fill(b, mix(over['c'], '#000000', 0.3)); d.outline(b, lw * 0.4)
        for m in over.get('marks', []):
            m(d, view, F, g)
    if top and top.get('collar'):
        collar(d, view, F, top['collar'], top['c'], k)
    if top and top.get('turtle'):
        # a turtleneck: the collar is a short wide tube round the neck, folded once
        y1 = B['torso'][-1][0]
        r = B['neck_r'] + 0.8
        n0 = J['neck0']
        dirn = (J['neck1'] - J['neck0']) / np.linalg.norm(J['neck1'] - J['neck0'])
        g = tube(view, [n0, n0 + dirn * (y1 - n0[1] + top['turtle'])], [r + 0.3, r])
        fill_part(d, g, top['c'], k * 0.5)
        fold = view.xy(np.array([n0 + dirn * (y1 - n0[1] + top['turtle'] * 0.45) + np.array([x, 0, z])
                                 for x, z in [(-r, 0.0), (-r * 0.7, r * 0.7), (0, r), (r * 0.7, r * 0.7), (r, 0)]]))
        from geo import spline as _sp
        d.line(_sp(fold, 20), lw * 0.6)
    if S.get('apron'):
        S['apron'](d, view, F)


def collar(d, view, F, size, c, k):
    """a shirt collar: two flaps lying on the shoulders and pointing down the front."""
    lo = F.torso_loft(push=1.0)
    y1 = F.B['torso'][-1][0]
    for s in (1, -1):
        ts = [s * 0.04, s * 0.08, s * 0.36, s * 0.70, s * 0.78, s * 0.55, s * 0.25]
        ys = [y1 - 1.2, y1 - size, y1 - size * 0.75, y1 - 1.6, y1 - 0.4, y1 + 0.1, y1 - 0.1]
        fac = lo.facing(view, s * 0.5, y1 - size * 0.5)
        if fac < 0.05:
            continue
        g = lo.region(view, ts, ys, push=1.0)
        fill_part(d, g, mix(c, '#ffffff', 0.15), k * 0.4)


def neck_cut(view, F, cut):
    """a V or scoop opening at the front of the neck, as a flat region over the torso surface."""
    lo = F.torso_loft(push=0.8)
    y1 = F.B['torso'][-1][0]
    depth, wid = cut
    ts = [-wid, -wid * 0.6, 0.0, wid * 0.6, wid, wid + 0.4, -wid - 0.4]
    ys = [y1 - 1, y1 - depth * 0.6, y1 - depth, y1 - depth * 0.6, y1 - 1, y1 + 6, y1 + 6]
    return lo.region(view, ts, ys, push=0.8)


def front_open(view, lo, w, y0, y1):
    """the opening of a cardigan or jacket: narrow at the hem, wider at the neck; (w0, w1, y_from) opens only above
    y_from (a vest's V)."""
    w0, w1 = w[:2]
    if len(w) > 2:
        y0 = w[2]
    n = 12
    ys = np.linspace(y0 - (3 if len(w) < 3 else 0), y1 + 4, n)
    ts_r = np.linspace(w0, w1, n)
    T = list(ts_r) + list(-ts_r[::-1])
    Y = list(ys) + list(ys[::-1])
    return lo.region(view, T, Y, push=1.6)


def draw_arm(d, view, F, S, side, torso, k):
    B, J = F.B, F.J
    lw = d.lw
    top, over = S.get('top'), S.get('over')
    sleeve_src = over if over and over.get('sleeve') else top
    sl = sleeve_src.get('sleeve', {}) if sleeve_src else {}
    c = sleeve_src['c'] if sleeve_src else S['skin']
    arm, pts = F.arm_shape(view, side)
    hand_parts = F.hand(view, side, F.pose['arm' + side].get('hand_kind', 'relaxed'))

    def draw_hand():
        hk = 0.12 * view.s
        whole = unary_union(hand_parts)
        hsh = shadow_of(whole, hk * 3)
        for g in hand_parts:
            d.fill(g, S['skin'])
            d.fill(hsh.intersection(g), shade(S['skin']))
            d.outline(g, lw * 0.75)
    upto = sl.get('upto', 1.0)
    order_hand_first = F.pose['arm' + side].get('hand_behind', False)
    if order_hand_first:
        draw_hand()
    sg, _ = F.arm_shape(view, side, ease=sl.get('ease', 0.9), upto=min(upto + 0.02, 1.0) if upto < 1 else 0.97)
    if upto >= 0.98:
        # a long sleeve ends in a cuff a little wider than the wrist
        w = J['wr' + side]
        e = J['el' + side]
        cuff = tube(view, [w + unit(e - w) * 3.5, w + unit(w - e) * 0.3], [B['arm_r'][-1] + sl.get('ease', 0.9) + 0.6] * 2)
        sg = unary_union([sg, cuff])
    # the top of the sleeve follows the slope of the shoulder: cut what rises above the torso near the joint
    shp = view.xy(np.array([J['sh' + side]]))[0]
    tor = F.torso_loft(push=(sleeve_src or {}).get('ease', 0.7)).shape(view, B['chest_y'] - 6, B['torso'][-1][0])
    R = B['arm_r'][0] * view.s * 2.2
    above = box(shp[0] - R, shp[1] - R * 1.5, shp[0] + R, shp[1] + R * 0.25)
    sg = sg.difference(above.difference(tor))
    sg = unary_union([p for p in polys(sg) if p.area > 4]) if polys(sg) else sg
    arm_cut = arm.difference(above.difference(tor))
    if upto < 0.98:
        fill_part(d, arm_cut, S['skin'], k * 0.4)
    sh = fill_part(d, sg, c, k * 0.9)
    # join the sleeve into the shoulder
    blob = Point(shp).buffer(B['arm_r'][0] * view.s * 1.6)
    reg = sg.intersection(tor).intersection(blob).buffer(-lw * 0.6)
    patch(d, reg, c, sh)
    # an elbow fold
    if upto > 0.6:
        e = J['el' + side]
        u = unit(J['wr' + side] - e)
        f = view.xy(np.array([e - u * 2.5 + [0, 0, B['arm_r'][1] * 0.6], e + u * 1.5 + [0, 0, B['arm_r'][1] * 0.9]]))
        d.line(f, lw * 0.5)
    if not order_hand_first:
        draw_hand()
    for fn in getattr(F, 'after_hands', []):
        fn()
    F.after_hands = []


def draw_neck(d, view, F, S, head_g):
    B, J = F.B, F.J
    r = B['neck_r']
    g = tube(view, [J['neck0'], J['neck1']], [r * 1.05, r])
    k = view.s * 1.0
    cast = shift(head_g, 0.2 * k, 1.2 * k).intersection(g)
    fill_part(d, g, S['skin'], 0.5 * k, extra=cast)
    return g


def head_drawer(head, hair, skin, hair_c, iris_c, E, head_c=None, extra=None):
    """the usual head_fn: back hair first; then neck, face, front hair. `extra(d, view, F, head, skin_g)` draws
    things on top (glasses, a loupe, a hat)."""
    state = {}

    def fn(d, view, F, back):
        J = F.J
        p = F.pose
        head.place(J['head'], F.B['head_h'], *p.get('head_rot', (0, 0, 0)))
        if 'hair' not in state:
            state['hair'] = hair.build(view) if hair else (None, None, [])
        Fh, Bh, st = state['hair']
        if back == 'prepare':
            F.head_g = head.skull(view)
            return
        if back:
            if Bh is not None:
                hair.draw(d, view, Bh, hair_c)
            return
        sk = head.draw_face(d, view, E, skin, hair_c, iris_c, hair_front=Fh)
        if Fh is not None:
            hair.draw(d, view, Fh, hair_c, st)
        if extra:
            extra(d, view, F, head, sk)
    return fn
