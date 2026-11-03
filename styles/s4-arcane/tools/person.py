"""A head-and-shoulders person in the Arcane-like style: head mesh + wrapped features + ears + hair + bust."""
import math
import random
import numpy as np
from arc import *
from face import *

NEUTRAL = dict(brow_in=0, brow_out=0, knit=0, lid=0, low=0, smile=0, open=0, wide=0, teeth=0, sad=0, snarl=0,
               gx=0, gy=0, squint=0)


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


class Person:
    def __init__(self, **k):
        self.__dict__.update(k)

    # ------------------------------------------------------------------ mesh
    def head(self, jaw=0.0):
        """The head loft; jaw opens the lower face downward."""
        def sh(tab):
            return [(y + (jaw * min(1, (y - 60) / 30) if y > 60 else 0), v) for y, v in tab]
        bumps = [(u, (y + jaw if y > 70 else y), su, sy, a) for (u, y, su, sy, a) in self.bumps]
        return Head(zf=sh(self.zf), zb=sh(self.zb), a=sh(self.a), p=self.p, bumps=bumps, pf=sh(self.pf) if getattr(self, 'pf', None) else None)

    def nose(self, head):
        return Nose(head, **self.nose_k).orient()

    def neck(self):
        return Loft(**self.neck_k)

# ---------------------------------------------------------------------- drawing


def regions_path(R, key):
    return poly_path(R[key]) if key in R else ''


def shade_layers(doc, R, pal, clip=None, brush=True, glow=True, rim=True, hi=True, base=True):
    """Lit fill + warm terminator + textured shadow + deep + highlight + rim, as SVG."""
    s = ''
    sil = poly_path(R['sil'])
    if not sil:
        return ''
    if base:
        s += path(sil, pal['lit'])
    shd = poly_path(R['shadow'])
    if glow and shd and pal.get('glow'):
        s += path(poly_path(R['shadow'].buffer(5)), pal['glow'], op=pal.get('glow_op', 0.35), extra=' filter="url(#soft)" style="mix-blend-mode:multiply"')
    if shd:
        s += path(shd, pal['shadow'], extra=' style="mix-blend-mode:multiply"' + (' filter="url(#brush)"' if brush else ' filter="url(#edge)"'))
    if R['deep'] is not None and not R['deep'].is_empty:
        s += path(poly_path(R['deep']), pal.get('deep', pal['shadow']), op=0.45, extra=' filter="url(#soft)" style="mix-blend-mode:multiply"')
    if rim and pal.get('rim') and not R['rim'].is_empty:
        s += path(poly_path(R['rim']), pal['rim'], op=pal.get('rim_op', 0.5), extra=' filter="url(#edge)"')
    if hi and pal.get('hi') and not R['hi'].is_empty:
        s += path(poly_path(R['hi']), pal['hi'], op=pal.get('hi_op', 0.45), extra=' filter="url(#soft)"')
    return s


def clip_def(doc, d):
    cid = doc.uid('c')
    doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d))
    return cid


def eye_shapes(P, side, e):
    """Flat shapes of one eye (side +1 = figure's left)."""
    e = side_e(e, side)
    ex, ey, w, h = P.eye_x, P.eye_y, P.eye_w, P.eye_h
    tilt = P.eye_tilt
    open_ = 1 + e['lid'] * 0.45 - e['squint'] * 0.3
    low = e['low'] * 0.45 + e['squint'] * 0.3
    s = side
    xi, xo = s * (ex - w / 2), s * (ex + w / 2)
    yi, yo = ey + 1.5, ey - tilt

    def X(t):
        return xi + (xo - xi) * t

    def Y(t):
        return yi + (yo - yi) * t
    H = h * open_
    lidp = P.lid_peak
    upper = [(xi, yi, 1), (X(0.12), Y(0.12) - H * 0.55), (X(lidp), Y(lidp) - H * 1.0), (X(0.75), Y(0.75) - H * 0.82),
             (X(0.93), Y(0.93) - H * 0.35), (xo, yo, 1)]
    L = h * (0.5 - low)
    lower = [(xo, yo, 1), (X(0.75), Y(0.75) + L * 0.8), (X(0.45), Y(0.45) + L * 1.0), (X(0.15), Y(0.15) + L * 0.62)]
    white = upper + lower
    # iris
    ri = P.iris_r
    icx = s * ex + e['gx'] * s * 0 + e['gx']
    icy = ey - h * 0.1 + e['gy']
    iris = [(icx + ri * math.cos(a), icy + ri * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 28, endpoint=False)]
    pupil = [(icx + ri * 0.42 * math.cos(a), icy + ri * 0.42 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
    # lid shadow band on the eyeball
    band = upper + [(q[0], q[1] + H * 0.55) for q in upper[::-1][1:-1]]
    # lash line along the upper lid, with a wing past the outer corner
    lash_c = [upper[1][:2], upper[2][:2], upper[3][:2], upper[4][:2], (xo + s * w * P.wing, yo - h * 0.32 * P.wing / 0.12 if P.wing else yo)]
    # crease above
    cr = H * 0.55 + P.crease
    crease = [(X(0.1), Y(0.1) - H * 0.45 - cr * 0.6), (X(lidp), Y(lidp) - H - cr), (X(0.8), Y(0.8) - H * 0.8 - cr * 0.9), (xo + s * w * 0.04, yo - cr * 0.45)]
    lid_skin = [q[:2] for q in upper[1:5]] + crease[::-1]
    lowline = [(X(0.4), Y(0.4) + L * 1.02), (X(0.75), Y(0.75) + L * 0.82), (xo - s * 1, yo + 0.5)]
    bag = [(X(0.25), Y(0.25) + L + 4), (X(0.6), Y(0.6) + L + 5.5), (X(0.92), Y(0.92) + L * 0.5 + 4)]
    return dict(white=white, iris=iris, pupil=pupil, band=band, lash=lash_c, crease=crease, lid_skin=lid_skin,
                lowline=lowline, upper=upper, bag=bag, ic=(icx, icy), ri=ri)


def brow_shape(P, side, e):
    e = side_e(e, side)
    pts = []
    n = len(P.brow)
    for i, (x, y) in enumerate(P.brow):
        t = (abs(x) - P.brow_inner_x) / (P.brow_outer_x - P.brow_inner_x)
        t = min(max(t, 0), 1)
        dy = -(e['brow_in'] * (1 - t) + e['brow_out'] * t) * 6 + e['knit'] * 5 * (1 - t) ** 1.5
        dx = -e['knit'] * 3 * (1 - t)
        # sad brows: inner up, slanted
        pts.append((side * (x + dx), y + dy))
    return pts


def side_e(e, side):
    """Expression values for one side: a tuple value is (figure's left, figure's right)."""
    return {k: ((v[0] if side > 0 else v[1]) if isinstance(v, tuple) else v) for k, v in e.items()}


def mouth_shapes(P, e):
    eL, eR = side_e(e, 1), side_e(e, -1)
    smile_avg = (eL['smile'] + eR['smile']) / 2
    my = P.mouth_y
    mw = P.mouth_w * (1 + e['wide'] * 0.25 + smile_avg * 0.12)
    smL = eL['smile'] * 5 - eL['sad'] * 4
    smR = eR['smile'] * 5 - eR['sad'] * 4
    op = e['open']
    sn = e['snarl']
    ul, ll = P.ulip, P.llip
    cL, cR = my - smL, my - smR

    def sm(x):
        t = (x / mw + 1) / 2
        return smR + (smL - smR) * t
    up_edge = [(-mw, cR, 1), (-mw * 0.62, my - ul * 0.75 - sm(-mw) * 0.25), (-mw * 0.2, my - ul * 1.05), (0, my - ul * 0.82), (mw * 0.2, my - ul * 1.05),
               (mw * 0.62, my - ul * 0.75 - sm(mw) * 0.25), (mw, cL, 1)]
    m_up = [(mw, cL, 1), (mw * 0.55, my + 0.6 - sm(mw) * 0.3 - op * 0.15 - sn * 2), (0, my + 1.0 + sn * 1.5 - op * 0.25 - sn * 3),
            (-mw * 0.55, my + 0.6 - sm(-mw) * 0.3 - op * 0.15 - sn * 2), (-mw, cR, 1)]
    m_lo = [(-mw, cR, 1), (-mw * 0.55, my + 1 + op * 0.8 - sm(-mw) * 0.2), (0, my + 1.2 + op), (mw * 0.55, my + 1 + op * 0.8 - sm(mw) * 0.2), (mw, cL, 1)]
    upper_lip = up_edge + m_up[1:-1]
    lo_edge = [(mw, cL, 1), (mw * 0.55, my + op * 0.85 + ll * 0.85 - sm(mw) * 0.2), (0, my + op + ll * 1.05), (-mw * 0.55, my + op * 0.85 + ll * 0.85 - sm(-mw) * 0.2), (-mw, cR, 1)]
    lower_lip = m_lo[:-1] + lo_edge[:-1]
    opening = m_up[:-1] + m_lo[:-1] if op > 0.6 else None
    teeth = None
    if op > 0.6 and e['teeth']:
        tb = min(op * 0.45, 5) + sn * 2
        teeth = [(mw * 0.62, my + 0.4 - sm(mw) * 0.3 - sn * 2), (0, my + 0.8 - op * 0.2 - sn * 3), (-mw * 0.62, my + 0.4 - sm(-mw) * 0.3 - sn * 2),
                 (-mw * 0.55, my + tb - sm(-mw) * 0.2), (0, my + tb + 1), (mw * 0.55, my + tb - sm(mw) * 0.2)]
    return dict(upper=upper_lip, lower=lower_lip, opening=opening, teeth=teeth, line=m_up, cy=(cL + cR) / 2, cL=cL, cR=cR, mw=mw, my=my)


def ear_points(P, side, view, head):
    """An ear as a shape in a plane on the side of the head; returns screen paths (outer, inner) or None."""
    ax, ay, az = side * P.ear_x, P.ear_y, P.ear_z
    # plane axes: back (-z) and down (+y), flared outward by angle
    fl = math.radians(P.ear_flare)
    bx, bz = side * math.sin(fl), -math.cos(fl)  # 'back' direction in plane
    nx, nz = side * math.cos(fl), math.sin(fl)  # plane normal (outward)
    nx_, ny_, nz_ = view.rot(np.array([nx]), np.array([0.0]), np.array([nz]))
    face = float(nz_[0])
    shape = P.ear  # list of (back, down) in px
    inner = P.ear_inner

    def to3(pts):
        X = np.array([ax + bx * p[0] for p in pts])
        Y = np.array([ay + p[1] for p in pts])
        Z = np.array([az + bz * p[0] for p in pts])
        x, y, z = view.proj(X, Y, Z)
        return list(zip(x, y))
    return to3(shape), [to3(c) for c in inner], face


def lock_points(head, view, spec):
    """3D control points of a lock: ('s', u, v, out) on the head or (x, y, z) raw -> screen + depth + normal facing."""
    X, Y, Z, NX, NY, NZ = [], [], [], [], [], []
    for p in spec:
        if p[0] == 's':
            _, u, v, out = p
            P_, N_ = head.normals(np.array([u]), np.array([v]))
            X.append(P_[0, 0] + N_[0, 0] * out)
            Y.append(P_[0, 1] + N_[0, 1] * out)
            Z.append(P_[0, 2] + N_[0, 2] * out)
            NX.append(N_[0, 0]); NY.append(N_[0, 1]); NZ.append(N_[0, 2])
        else:
            x, y, z = p[:3]
            X.append(x); Y.append(y); Z.append(z)
            l = math.sqrt(x * x + z * z) + 1e-6
            NX.append(x / l); NY.append(0.0); NZ.append(z / l)
    X, Y, Z = np.array(X), np.array(Y), np.array(Z)
    x, y, z = view.proj(X, Y, Z)
    nx, ny, nz = view.rot(np.array(NX), np.array(NY), np.array(NZ))
    return list(zip(x, y)), z, (nx, ny, nz)


def ribbon_screen(pts, ws, closed_tip=True):
    """A tapered ribbon in screen space along points with a width profile."""
    P = np.array(pts, float)
    # smooth resample
    c = sample_curve([tuple(p) for p in P], False, 8)
    P = np.array(c)
    n = len(P)
    t = np.linspace(0, 1, n)
    w = np.interp(t, np.linspace(0, 1, len(ws)), ws)
    d = np.gradient(P, axis=0)
    l = np.hypot(d[:, 0], d[:, 1]) + 1e-9
    nx, ny = -d[:, 1] / l, d[:, 0] / l
    L = list(zip(P[:, 0] + nx * w / 2, P[:, 1] + ny * w / 2))
    R = list(zip(P[:, 0] - nx * w / 2, P[:, 1] - ny * w / 2))[::-1]
    pts2 = L + R
    return 'M' + 'L'.join('%s,%s' % (fmt(a), fmt(b)) for a, b in pts2) + 'Z', P


def draw_head(doc, P, view, e=None, bust=True, behind_hair=True):
    """Everything above the chest of a person P in a view; returns SVG."""
    E = dict(NEUTRAL)
    if e:
        E.update(e)
    e = E
    jaw = e['open'] * 0.7
    head = P.head(jaw)
    nose = P.nose(head)
    neck = P.neck()
    pal = P.pal
    out = []
    # ---- hair behind everything
    locks = P.hair_locks(head) if hasattr(P, 'hair_locks') else []
    drawn_locks = []
    for L in locks:
        sp, z, (nx, ny, nz) = lock_points(head, view, L['pts'])
        drawn_locks.append((L, sp, z, nx, ny, nz))
    back = [d for d in drawn_locks if (d[0].get('layer') == 'back') or np.mean(d[5]) < -0.25]
    front = [d for d in drawn_locks if d not in back]

    def lock_svg(d):
        L, sp, z, nx, ny, nz = d
        dl = nx * view.L[0] + ny * view.L[1] + nz * view.L[2]
        tone = L.get('tone', 0)
        hp = P.hair
        is_back = L.get('layer') == 'back' or np.mean(nz) < -0.25

        def col_at(i):
            if is_back:
                c = hp['dark']
            elif dl[i] < -0.05:
                c = hp['shadow']
            elif dl[i] > 0.5:
                c = mix(hp['base'], hp['light'], min(1, (dl[i] - 0.5) * 3))
            else:
                c = mix(hp['shadow'], hp['base'], min(1, (dl[i] + 0.05) * 4))
            if tone == 1:
                c = mix(c, hp['dark'], 0.4)
            elif tone == 2:
                c = mix(c, hp['light'], 0.35)
            if L.get('grey'):
                c = mix(c, '#b8b2b4', 0.6)
            return c
        ws = [w * view.s for w in L['w']]
        d_, C = ribbon_screen(sp, ws)
        gid = doc.uid('h')
        stops = ''.join('<stop offset="%s" stop-color="%s"/>' % (fmt(i / max(1, len(sp) - 1)), col_at(i)) for i in range(len(sp)))
        doc.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>'
                        % (gid, fmt(sp[0][0]), fmt(sp[0][1]), fmt(sp[-1][0]), fmt(sp[-1][1]), stops))
        s = path(d_, 'url(#%s)' % gid)
        # strands inside the lock: thin darker and lighter lines along it
        rnd = random.Random(int(abs(sp[0][0] * 7 + sp[0][1] * 13)))
        k = len(C)
        if k > 6 and not is_back:
            dC = np.gradient(C, axis=0)
            ln = np.hypot(dC[:, 0], dC[:, 1]) + 1e-9
            nrm = np.stack([-dC[:, 1] / ln, dC[:, 0] / ln], -1)
            wv = np.interp(np.linspace(0, 1, k), np.linspace(0, 1, len(ws)), ws)
            for j in range(L.get('strands', 3)):
                off = rnd.uniform(-0.32, 0.32)
                a = int(k * rnd.uniform(0.0, 0.35))
                b = int(k * rnd.uniform(0.6, 0.97))
                seg = C[a:b] + nrm[a:b] * (wv[a:b, None] * off)
                lightline = rnd.random() < 0.4 and float(np.mean(dl)) > 0.0
                s += path(lines_path(seg), 'none', hp['shine'] if lightline else hp['line'], 0.55 * max(1, view.s * 0.7), 0.45 if lightline else 0.35)
        if L.get('streak') and float(np.mean(dl)) > 0.1 and not is_back:
            a, b = int(k * L['streak'][0]), int(k * L['streak'][1])
            seg = C[a:b]
            if len(seg) > 3:
                s += path(lines_path(seg), 'none', hp['shine'], max(0.8, min(ws[:-1]) * 0.22 + 0.5), 0.5)
        if L.get('edge', True):
            # a dark separation line along one side
            dC = np.gradient(C, axis=0)
            ln = np.hypot(dC[:, 0], dC[:, 1]) + 1e-9
            nrm = np.stack([-dC[:, 1] / ln, dC[:, 0] / ln], -1)
            wv = np.interp(np.linspace(0, 1, k), np.linspace(0, 1, len(ws)), ws)
            seg = C + nrm * (wv[:, None] * 0.45)
            s += path(lines_path(seg[int(k * 0.05):]), 'none', hp['line'], 0.8 * max(1, view.s * 0.7), 0.5)
        return s

    for d in sorted(back, key=lambda d: np.mean(d[2])):
        out.append(lock_svg(d))
    if hasattr(P, 'bun') and abs(math.degrees(view.yaw)) < 60:
        out.append(P.bun(doc, view, None))
    # ---- neck
    Rn = regions(neck, view)
    Rh = regions(head, view, extra={'warm': lambda U, V, dl, nz: np.minimum(dl - 0.1, 0.55 - dl), 'half': lambda U, V, dl, nz: np.minimum(dl - 0.1, 0.28 - dl)})
    neck_svg = shade_layers(doc, Rn, pal['neck'])
    # cast shadow of the head on the neck
    cast = Rh['sil']
    cast = affinity.translate(cast, view.s * 6, view.s * 20).intersection(Rn['sil']).difference(Rh['sil'])
    if not cast.is_empty:
        neck_svg += path(poly_path(cast), pal['skin']['shadow'], extra=' style="mix-blend-mode:multiply" filter="url(#edge)"')
    out.append(neck_svg)
    # ---- bust
    if bust and hasattr(P, 'bust'):
        out.append(P.bust(doc, view, head))
    if bust and hasattr(P, 'collar'):
        out.append(P.collar(doc, view, head))
    # ---- ears (behind the head when facing away)
    ears = []
    for side in (1, -1):
        sh, inner, face = ear_points(P, side, view, head)
        ears.append((side, sh, inner, face))

    def ear_svg(sh, inner, face):
        s = path(smooth_path(sh), pal['skin']['lit'])
        dl_ear = face  # crude: ear lit when facing camera-left light
        s += path(smooth_path(sh), pal['blush'], op=0.35, extra=' style="mix-blend-mode:multiply" filter="url(#soft)"')
        for c in inner:
            s += path(smooth_path(c, False), 'none', pal['skin']['line'], 1.1 * view.s, 0.7)
        return s
    # ---- head
    hsil = poly_path(Rh['sil'])
    cid = clip_def(doc, hsil)
    out.append('<g filter="url(#paint)">' + path(hsil, pal['skin']['lit']) + '</g>')
    for side, sh, inner, face in ears:
        if face > -0.05:
            out.append(ear_svg(sh, inner, face))
    g = []
    # half-tones: a soft band before the terminator, cooler and darker toward it
    if pal['skin'].get('warm') and not Rh['warm'].is_empty:
        g.append(path(poly_path(Rh['warm']), pal['skin']['warm'], op=0.45, extra=' filter="url(#soft2)" style="mix-blend-mode:multiply"'))
    if not Rh['half'].is_empty:
        g.append(path(poly_path(Rh['half']), pal['skin']['shadow'], op=0.35, extra=' filter="url(#soft)" style="mix-blend-mode:multiply"'))
    # blush on cheeks, nose and chin
    for (bx, by, rx, ry, op_) in P.blush:
        for side in ((1, -1) if bx else (1,)):
            pts = [(side * bx + rx * math.cos(a), by + ry * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
            dd, nz = wrap_shape(head, view, pts, True, 1, 0.1, 2)
            if dd:
                g.append(path(dd, pal['blush'], op=op_, extra=' filter="url(#soft2)" style="mix-blend-mode:multiply"'))
    # freckles
    for (fx, fy, fr) in getattr(P, 'freckles', []):
        sp, nz = wrap(head, view, [(fx, fy)], 1)
        if nz[0] > 0.2:
            g.append('<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.45"/>' % (fmt(sp[0][0]), fmt(sp[0][1]), fmt(fr * view.s), pal['freckle']))
    # lips (colour first; shading falls over them)
    ms = mouth_shapes(P, e)
    if ms['opening']:
        dd, _ = wrap_shape(head, view, ms['opening'], True, 1.2, -0.5)
        g.append(path(dd, pal['mouth']))
        if ms['teeth']:
            dd, _ = wrap_shape(head, view, ms['teeth'], True, 1.3, -0.5)
            g.append(path(dd, '#f3ece6'))
            g.append(path(dd, '#b9a8a8', op=0.35, extra=' filter="url(#edge)" style="mix-blend-mode:multiply"'))
    dd_up, _ = wrap_shape(head, view, ms['upper'], True, 1.2, -0.5)
    dd_lo, _ = wrap_shape(head, view, ms['lower'], True, 1.2, -0.5)
    g.append(path(dd_up, pal['lip_up'], op=0.9, extra=' filter="url(#edge)"'))
    g.append(path(dd_lo, pal['lip_lo'], op=0.85, extra=' filter="url(#edge)"'))
    # lower-lip shine
    sh_pts = [(-ms['mw'] * 0.35, ms['my'] + e['open'] + P.llip * 0.55), (0, ms['my'] + e['open'] + P.llip * 0.42), (ms['mw'] * 0.3, ms['my'] + e['open'] + P.llip * 0.55)]
    dd, _ = wrap_shape(head, view, sh_pts, False, 1.3, -0.5)
    g.append(path(dd, 'none', '#fff4ee', 1.6 * view.s, 0.35))
    # eyes: whites and irises
    eyes = []
    for side in (1, -1):
        es = eye_shapes(P, side, e)
        dw, nzw = wrap_shape(head, view, es['white'], True, 0.8, 0.12)
        eyes.append((side, es, dw, nzw))
        if not dw:
            continue
        ec = clip_def(doc, dw)
        g.append(path(dw, pal['white']))
        di, _ = wrap_shape(head, view, es['iris'], True, 0.9, -1)
        dp, _ = wrap_shape(head, view, es['pupil'], True, 0.95, -1)
        sp, _ = wrap(head, view, [es['ic']], 1)
        gid = doc.uid('g')
        rr = es['ri'] * view.s
        doc.defs.append('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s" fx="%s" fy="%s">'
                        '<stop offset="0" stop-color="%s"/><stop offset="0.55" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>'
                        % (gid, fmt(sp[0][0]), fmt(sp[0][1] + rr * 0.35), fmt(rr * 1.25), fmt(sp[0][0]), fmt(sp[0][1] + rr * 0.6),
                           P.iris[2], P.iris[1], P.iris[0]))
        g.append('<g clip-path="url(#%s)">' % ec + path(di, 'url(#%s)' % gid) + path(di, 'none', P.iris[0], 1.0 * view.s, 0.8) + path(dp, '#16100f') +
                 path(poly_path_from(dw, es, head, view, 'band'), pal['lidshadow'], op=0.55, extra=' style="mix-blend-mode:multiply" filter="url(#edge)"') + '</g>')
    # soft socket shadow at the inner upper corner of each eye, and under the lower lip
    for side in (1, -1):
        sc = [(side * (P.eye_x - P.eye_w * 0.35) + side * k * 0, -P.eye_h * 0.9) for k in range(1)]
        pts = [(side * (P.eye_x - P.eye_w * 0.3) + 7 * math.cos(a) * 1.4, -P.eye_h * 0.75 + 5 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)]
        dd, nz = wrap_shape(head, view, pts, True, 1, 0.0, 2)
        if dd:
            g.append(path(dd, pal['skin']['shadow'], op=0.55, extra=' filter="url(#soft)" style="mix-blend-mode:multiply"'))
    pts = [(ms['mw'] * 0.55 * math.cos(a), ms['my'] + e['open'] + P.llip + 4 + 2.6 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 14, endpoint=False)]
    dd, nz = wrap_shape(head, view, pts, True, 1, -0.5, 2)
    g.append(path(dd, pal['skin']['shadow'], op=0.55, extra=' filter="url(#soft)" style="mix-blend-mode:multiply"'))
    # face shading from the mesh
    g.append(shade_layers(doc, Rh, pal['skin'], base=False))
    # brush strokes that follow the form: darker ones in the half-tones and shadow, lighter ones in the light
    g.append(skin_strokes(head, view, pal['skin'], seed=len(P.blush) * 7 + int(view.yaw * 100)))
    # lid skin, creases, lashes, highlights
    for side, es, dw, nzw in eyes:
        if not dw:
            continue
        dl, _ = wrap_shape(head, view, es['lid_skin'], True, 0.9, 0.0)
        g.append(path(dl, pal['lid'], op=0.35, extra=' filter="url(#edge)" style="mix-blend-mode:multiply"'))
        dc, _ = wrap_shape(head, view, es['crease'], False, 0.9, 0.0)
        g.append(path(dc, 'none', pal['skin']['line'], 1.1 * view.s, 0.55))
        # lash line as a tapered ribbon
        sp, nz = wrap(head, view, es['lash'], 1.0)
        dd, _ = ribbon_screen([q[:2] for q in sp], [P.lash_w[0] * view.s, P.lash_w[1] * view.s, P.lash_w[2] * view.s, P.lash_w[3] * view.s, 0.3])
        g.append(path(dd, pal['lash']))
        dd, _ = wrap_shape(head, view, es['lowline'], False, 0.9, 0.0)
        g.append(path(dd, 'none', pal['skin']['line'], 1.0 * view.s, 0.5))
        if getattr(P, 'bags', 0):
            dd, _ = wrap_shape(head, view, es['bag'], False, 0.9, 0.0)
            g.append(path(dd, 'none', pal['skin']['line'], 1.0 * view.s, P.bags))
        # catch-lights
        sp, _ = wrap(head, view, [(es['ic'][0] - es['ri'] * 0.35, es['ic'][1] - es['ri'] * 0.35), (es['ic'][0] + es['ri'] * 0.4, es['ic'][1] + es['ri'] * 0.35)], 1.2)
        if np.mean(nzw) > 0.25:
            g.append('<circle cx="%s" cy="%s" r="%s" fill="#fffaf2" opacity="0.95"/>' % (fmt(sp[0][0]), fmt(sp[0][1]), fmt(es['ri'] * 0.24 * view.s)))
            g.append('<circle cx="%s" cy="%s" r="%s" fill="#fffaf2" opacity="0.6"/>' % (fmt(sp[1][0]), fmt(sp[1][1]), fmt(es['ri'] * 0.1 * view.s)))
    # wrinkles and form lines: pairs of a dark line and a light line beside it
    for (pts, wdt, op_) in P.lines(e):
        dd, nz = wrap_shape(head, view, pts, False, 1.0, 0.05)
        if dd:
            g.append(path(dd, 'none', pal['skin']['line'], wdt * view.s, op_))
    # brows
    for side in (1, -1):
        bs = brow_shape(P, side, e)
        dd, nz = wrap_shape(head, view, bs, True, 1.5, 0.05)
        if dd:
            g.append(path(dd, pal['brow'], extra=' filter="url(#paint)"'))
            if P.brow_hairs:
                rnd = random.Random(11 + side)
                n = len(bs)
                half = n // 2 + 1
                top = bs[:half]
                bot = bs[half:][::-1]
                for k in range(P.brow_hairs):
                    t = rnd.uniform(0.02, 0.98)
                    tp = sample_curve(top, False, 4)
                    bt = sample_curve([bs[0]] + bot + [bs[half - 1]], False, 4)
                    a_ = tp[int(t * (len(tp) - 1))]
                    b_ = bt[int(t * (len(bt) - 1))]
                    x0, y0 = b_[0] + rnd.uniform(-1, 1), b_[1] + rnd.uniform(0, 2.5)
                    x1, y1 = a_[0] + side * rnd.uniform(2, 7), a_[1] - rnd.uniform(0, 3.5)
                    sp_, nz_ = wrap(head, view, [(x0, y0), ((x0 + x1) / 2 + side * 1.5, (y0 + y1) / 2), (x1, y1)], 1.6)
                    if min(nz_) > 0.05:
                        d2, _ = ribbon_screen([q[:2] for q in sp_], [1.4 * view.s, 1.0 * view.s, 0.1])
                        g.append(path(d2, rnd.choice([pal['brow'], pal.get('brow2', pal['brow'])]), op=0.9))
    if getattr(P, 'moustache', None):
        for side in (1, -1):
            pts = P.moustache if side > 0 else mirror(P.moustache)[::-1]
            dd, nz = wrap_shape(head, view, pts, True, 2.0, 0.0, 4)
            if dd:
                g.append(path(dd, P.hair['base'], extra=' filter="url(#paint)"'))
                g.append(path(dd, P.hair['shadow'], op=0.5, extra=' filter="url(#soft)" style="mix-blend-mode:multiply"') if side < 0 else '')
                rnd = random.Random(5 + side)
                for k in range(16):
                    x0 = side * rnd.uniform(1, 22)
                    y0 = rnd.uniform(58, 62) + abs(x0) * 0.15
                    x1 = x0 + side * rnd.uniform(1, 5)
                    y1 = y0 + rnd.uniform(6, 11)
                    sp_, nz_ = wrap(head, view, [(x0, y0), (x1, y1)], 2.2)
                    if min(nz_) > 0.05:
                        g.append(path(lines_path(sp_), 'none', rnd.choice([P.hair['light'], P.hair['shadow']]), 0.9 * view.s, 0.6))
    # mouth line + corners
    dd, _ = wrap_shape(head, view, ms['line'], False, 1.3, -0.5)
    g.append(path(dd, 'none', pal['mouthline'], 1.3 * view.s, 0.85))
    for side in (1, -1):
        es_ = side_e(e, side)
        cy_ = ms['cL'] if side > 0 else ms['cR']
        c = [(side * (ms['mw'] - 0.5), cy_), (side * (ms['mw'] + 2.5), cy_ - 1.5 - es_['smile'] * 1.5 + es_['sad'] * 2.5)]
        dd, nz = wrap_shape(head, view, c, False, 1.3, 0.1)
        g.append(path(dd, 'none', pal['skin']['line'], 1.1 * view.s, 0.6))
    out.append('<g clip-path="url(#%s)">' % cid + ''.join(g) + '</g>')
    # ---- nose
    Rno = regions(nose, view)
    nsil = poly_path(Rno['sil'])
    ncid = clip_def(doc, nsil) if nsil else None
    ns = shade_layers(doc, Rno, dict(pal['skin'], glow=None), brush=False, rim=False)
    if nsil:
        ns += path(nsil, pal['skin']['warm'], op=0.18, extra=' style="mix-blend-mode:multiply"')
    if nsil:
        # blush on the tip
        tip, _ = on_surface(nose, view, [(0, 0.8)], 1)
        ns += '<circle cx="%s" cy="%s" r="%s" fill="%s" opacity="0.4" filter="url(#soft)" style="mix-blend-mode:multiply"/>' % (fmt(tip[0][0]), fmt(tip[0][1]), fmt(7 * view.s), pal['blush'])
        # nostrils and wing creases on the nose surface
        for side in (1, -1):
            nos = [(side * 0.25, 0.9), (side * 0.55, 0.88), (side * 0.75, 0.94), (side * 0.6, 0.99), (side * 0.3, 0.97)]
            sp, nz = on_surface(nose, view, nos, 0.5)
            if np.mean(nz) > -0.6:
                ns += path(smooth_path(sp), pal['nostril'], op=0.9)
            wing = [(side * 0.98, 0.62), (side * 0.8, 0.74), (side * 0.78, 0.86), (side * 0.9, 0.95)]
            sp, nz = on_surface(nose, view, wing, 0.5)
            if np.mean(nz) > 0.05:
                ns += path(smooth_path(sp, False), 'none', pal['skin']['line'], 1.0 * view.s, 0.55)
        r0, _ = on_surface(nose, view, [(0, 0.05), (0, 0.42)], 0)
        mid = doc.uid('m')
        gid = doc.uid('mg')
        doc.defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>'
                        % (gid, fmt(r0[0][0]), fmt(r0[0][1]), fmt(r0[1][0]), fmt(r0[1][1])))
        doc.defs.append('<mask id="%s" maskUnits="userSpaceOnUse" x="0" y="0" width="%d" height="%d"><rect x="-5000" y="-5000" width="10000" height="10000" fill="url(#%s)"/></mask>' % (mid, 10000, 10000, gid))
        out.append('<g clip-path="url(#%s)" mask="url(#%s)">' % (ncid, mid) + ns + '</g>')
    # ---- front ears (drawn over the head edge when facing us)
    # ---- hair: cap then front locks
    if hasattr(P, 'hair_cap'):
        out.append(P.hair_cap(doc, view, head))
    if hasattr(P, 'bun') and abs(math.degrees(view.yaw)) >= 60:
        out.append(P.bun(doc, view, None))
    for d in sorted(front, key=lambda d: np.mean(d[2])):
        out.append(lock_svg(d))
    if getattr(P, 'glasses', None):
        out.append(glasses_svg(doc, view, head, P))
    if hasattr(P, 'extras'):
        out.append(P.extras(doc, view, head, e))
    return ''.join(out)


def poly_path_from(dw, es, head, view, key):
    dd, _ = wrap_shape(head, view, es[key], True, 0.85, -1)
    return dd


def lerp_pt(a, b, t, jit, rnd):
    if a[0] == 's':
        return ('s', a[1] + (b[1] - a[1]) * t + rnd.uniform(-jit, jit) * 0.02, a[2] + (b[2] - a[2]) * t + rnd.uniform(-jit, jit), a[3] + (b[3] - a[3]) * t + rnd.uniform(0, jit * 0.4))
    return tuple(a[i] + (b[i] - a[i]) * t + rnd.uniform(-jit, jit) for i in range(3))


def family(A, B, n, w, seed=1, jit=2.0, layer=None, streak=(0.25, 0.6), tones=(0, 0, 1, 2), wj=0.25, wave=0, period=60, strands=3):
    """n locks between guide locks A and B; raw points can wave sideways."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        t = (k + rnd.uniform(0.2, 0.8)) / n
        pts = [lerp_pt(a, b, t, jit * (i / max(1, len(A) - 1)) + 0.3, rnd) for i, (a, b) in enumerate(zip(A, B))]
        if wave:
            ph = rnd.uniform(-0.4, 0.4)
            pts = [p if p[0] == 's' else (p[0] + (wave if p[0] > 0 else -wave) * math.sin(2 * math.pi * p[1] / period + ph), p[1], p[2]) for p in pts]
        sc = 1 + rnd.uniform(-wj, wj)
        L = dict(pts=pts, w=[x * sc for x in w], tone=rnd.choice(tones), strands=strands, streak=(streak[0] + rnd.uniform(-.1, .1), streak[1] + rnd.uniform(-.1, .1)) if rnd.random() < 0.6 else None)
        if layer:
            L['layer'] = layer
        out.append(L)
    return out


def hair_cap(doc, view, head, P, hairline, thick):
    """The hair mass over the skull: an offset shell of the head masked above a hairline."""
    shell = Offset(head, thick)
    shell.nu, shell.nv = 160, 110
    hl_u = [t[0] for t in hairline] if not callable(hairline) else None
    hl_v = [t[1] for t in hairline] if not callable(hairline) else None

    def mask(U, V):
        return np.interp(np.abs(U), hl_u, hl_v) - V
    if callable(hairline):
        mask = hairline
    R = regions(shell, view, mask_fn=mask, shadow=0.05, deep=-0.4, hi=0.75, rim=0.6)
    hp = P.hair
    pal = dict(lit=hp['base'], shadow=hp['shadow'], glow=None, deep=hp['dark'], hi=hp['light'], rim=hp.get('rim', hp['light']), hi_op=0.55, rim_op=0.5)
    # colour shadow directly (hair is dark; multiply would muddy it)
    s = ''
    sil = poly_path(R['sil'])
    if not sil:
        return ''
    s += path(sil, hp['base'], extra=' filter="url(#paint)"')
    if not R['shadow'].is_empty:
        s += path(poly_path(R['shadow']), hp['shadow'], extra=' filter="url(#brush)"')
    if not R['deep'].is_empty:
        s += path(poly_path(R['deep']), hp['dark'], op=0.6, extra=' filter="url(#soft)"')
    if not R['hi'].is_empty:
        s += path(poly_path(R['hi']), hp['light'], op=0.5, extra=' filter="url(#brush)"')
    return s


def torso_female():
    return Loft(a=[(118, 28), (138, 44), (150, 74), (160, 98), (172, 112), (192, 118), (230, 112), (280, 104), (340, 102)],
                bf=[(118, 30), (150, 44), (180, 52), (220, 56), (260, 52), (340, 48)],
                bb=[(118, 30), (150, 44), (180, 52), (220, 54), (260, 50), (340, 48)], p=2.5,
                z0=[(118, -22), (150, -18), (200, -14), (340, -12)])


def torso_male(broad=1.0):
    k = broad
    return Loft(a=[(118, 32), (136, 50), (148, 86 * k), (160, 114 * k), (174, 126 * k), (196, 130 * k), (240, 122 * k), (290, 114 * k), (340, 110 * k)],
                bf=[(118, 34), (150, 48), (180, 56), (220, 60), (260, 58), (340, 56)],
                bb=[(118, 34), (150, 48), (180, 56), (220, 58), (260, 56), (340, 54)], p=2.6,
                z0=[(118, -22), (150, -18), (200, -14), (340, -12)])


def torso_child():
    return Loft(a=[(110, 24), (126, 36), (136, 60), (146, 76), (158, 84), (180, 86), (220, 82), (300, 80)],
                bf=[(110, 26), (140, 36), (180, 42), (220, 44), (300, 44)],
                bb=[(110, 26), (140, 36), (180, 42), (220, 42), (300, 42)], p=2.4,
                z0=[(110, -18), (150, -14), (300, -10)])


def draw_cloth(doc, view, surf, base, pieces, shadow='#8f7c8c', hi='#fff3e0', rim=None, lines=()):
    """A garment surface: base colour, flat-mapped pieces [(points, colour)] wrapped on it, then mesh shading."""
    R = regions(surf, view)
    sil = poly_path(R['sil'])
    if not sil:
        return ''
    cid = clip_def(doc, sil)
    s = path(sil, base, extra=' filter="url(#paint)"')
    g = ''
    for pts, col, *rest in pieces:
        dd, nz = wrap_shape(surf, view, pts, True, 0.5, -1.0, 3)
        op = rest[0] if rest else None
        g += path(dd, col, op=op, extra=' filter="url(#paint)"')
    for pts, col, w, op in lines:
        dd, nz = wrap_shape(surf, view, pts, False, 0.6, -1.0, 3)
        g += path(dd, 'none', col, w * view.s, op)
    if not R['shadow'].is_empty:
        g += path(poly_path(R['shadow'].buffer(4)), shadow, op=0.3, extra=' filter="url(#soft2)" style="mix-blend-mode:multiply"')
        g += path(poly_path(R['shadow']), shadow, extra=' filter="url(#brush)" style="mix-blend-mode:multiply"')
    if not R['deep'].is_empty:
        g += path(poly_path(R['deep']), shadow, op=0.5, extra=' filter="url(#soft)" style="mix-blend-mode:multiply"')
    if not R['hi'].is_empty:
        g += path(poly_path(R['hi']), hi, op=0.25, extra=' filter="url(#soft2)"')
    if rim and not R['rim'].is_empty:
        g += path(poly_path(R['rim']), rim, op=0.6, extra=' filter="url(#edge)"')
    return s + '<g clip-path="url(#%s)">' % cid + g + '</g>'


def background(doc, w, h, c1, c2, c3, seed=1, x=0, y=0):
    """A painted backdrop: a radial glow, a canvas grain and a few soft shapes."""
    gid = doc.uid('bg')
    doc.defs.append('<radialGradient id="%s" cx="0.38" cy="0.32" r="0.85"><stop offset="0" stop-color="%s"/><stop offset="0.55" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>' % (gid, c1, c2, c3))
    rnd = random.Random(seed)
    s = '<g transform="translate(%s,%s)">' % (fmt(x), fmt(y))
    s += '<rect width="%d" height="%d" fill="url(#%s)"/>' % (w, h, gid)
    for _ in range(7):
        cx, cy = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.uniform(w * 0.08, w * 0.25)
        s += '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" opacity="%.2f" filter="url(#soft2)"/>' % (fmt(cx), fmt(cy), fmt(r), fmt(r * rnd.uniform(0.4, 1)), rnd.choice([c1, c2, c3]), rnd.uniform(0.15, 0.4))
    s += '<rect width="%d" height="%d" filter="url(#canvas)" opacity="0.10" style="mix-blend-mode:overlay"/>' % (w, h)
    s += '</g>'
    return s


def grain(w, h, op=0.07):
    return '<rect width="%d" height="%d" filter="url(#grain)" opacity="%s" style="mix-blend-mode:overlay" pointer-events="none"/>' % (w, h, fmt(op))


def skin_strokes(surf, view, sp, seed=1, n=170, mask=None):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        u = rnd.uniform(-1.6, 1.6)
        v = rnd.uniform(surf.v0 + 20, surf.v1 - 5)
        P_, N_ = surf.normals(np.array([u]), np.array([v]))
        nx, ny, nz = view.rot(N_[:, 0], N_[:, 1], N_[:, 2])
        if nz[0] < 0.15:
            continue
        dl = float(nx[0] * view.L[0] + ny[0] * view.L[1] + nz[0] * view.L[2])
        if mask is not None and not mask(u, v):
            continue
        # strokes run around the form (constant v), slightly tilted
        length = rnd.uniform(0.12, 0.28)
        tilt = rnd.uniform(-6, 6)
        pts = [(u + t * length, v + t * tilt) for t in np.linspace(-0.5, 0.5, 6)]
        sp_, nz_ = on_surface(surf, view, pts, 0.8)
        if min(nz_) < 0.05:
            continue
        if dl < 0.32:
            col, op = sp['shadow'], rnd.uniform(0.10, 0.22)
            blend = ' style="mix-blend-mode:multiply"'
        elif dl > 0.6:
            col, op = sp['hi'], rnd.uniform(0.05, 0.12)
            blend = ''
        else:
            col, op = sp['warm'], rnd.uniform(0.06, 0.14)
            blend = ' style="mix-blend-mode:multiply"'
        w = rnd.uniform(2.5, 4.5) * view.s
        d, _ = ribbon_screen(sp_, [0.2, w, w * 0.9, 0.2])
        out.append(path(d, col, op=op, extra=blend))
    return ''.join(out)


def glasses_svg(doc, view, head, P):
    G = P.glasses
    out = []
    ue = flat_uv(head, np.array([P.eye_x]), np.array([P.eye_y]))
    _, _, ze = head.pos(ue, np.array([float(P.eye_y)]))
    z = float(ze[0]) + G.get('dz', 12)
    y = P.eye_y + G.get('dy', 0)
    rx, ry = G['rx'], G['ry']
    sq = G.get('square', 0)
    lenses = []
    for side in (1, -1):
        cx = side * (P.eye_x + G.get('dx', 0))
        pts3 = []
        for a in np.linspace(0, 2 * math.pi, 40, endpoint=False):
            c, s_ = math.cos(a), math.sin(a)
            # a squircle for rectangular frames
            k = 2 + sq * 6
            r = (abs(c) ** k + abs(s_) ** k) ** (-1 / k)
            x = cx + rx * r * c
            yy = y + ry * r * s_
            zz = z - 0.0035 * (x * x) * 0.4 * G.get('wrap', 1)
            pts3.append((x, yy, zz))
        X = np.array([p[0] for p in pts3]); Y = np.array([p[1] for p in pts3]); Z = np.array([p[2] for p in pts3])
        x2, y2, _ = view.proj(X, Y, Z)
        lenses.append(list(zip(x2, y2)))
    # temple arms: from the outer edge of each lens back to the ear
    for side, L in zip((1, -1), lenses):
        X0, Y0, Z0 = side * (P.eye_x + G.get('dx', 0) + rx), y - ry * 0.3, z - 0.0035 * (P.eye_x + rx) ** 2 * 0.4
        X1, Y1, Z1 = side * (P.ear_x + 2), P.ear_y - 14, P.ear_z + 4
        a0 = point3(view, X0, Y0, Z0)
        a1 = point3(view, X1, Y1, Z1)
        nxs, _, nzs = view.rot(np.array([side * 1.0]), np.array([0.0]), np.array([0.0]))
        if nzs[0] > -0.2:
            out.append(path('M%s,%sL%s,%s' % (fmt(a0[0]), fmt(a0[1]), fmt(a1[0]), fmt(a1[1])), 'none', G['color'], G.get('w', 1.4) * view.s, 0.95))
    for L in lenses:
        d = smooth_path(L)
        out.append(path(d, '#ffffff', op=0.10))
        # a glint across the lens
        out.append(path(d, 'none', G['color'], G.get('w', 1.4) * view.s, 0.95))
    # glints
    for L in lenses:
        xs = [p[0] for p in L]; ys = [p[1] for p in L]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        w_ = (max(xs) - min(xs)); h_ = (max(ys) - min(ys))
        out.append(path('M%s,%sL%s,%s' % (fmt(cx - w_ * 0.3), fmt(cy - h_ * 0.05), fmt(cx - w_ * 0.05), fmt(cy - h_ * 0.35)), 'none', '#ffffff', 2.2 * view.s, 0.35))
    # bridge
    b0 = point3(view, P.eye_x + G.get('dx', 0) - rx, y - ry * 0.25, z - 0.0035 * (P.eye_x - rx) ** 2 * 0.4)
    b1 = point3(view, 0, y - ry * 0.45, z + 2)
    b2 = point3(view, -(P.eye_x + G.get('dx', 0) - rx), y - ry * 0.25, z - 0.0035 * (P.eye_x - rx) ** 2 * 0.4)
    out.append(path('M%s,%sQ%s,%s %s,%s' % (fmt(b0[0]), fmt(b0[1]), fmt(b1[0]), fmt(b1[1]), fmt(b2[0]), fmt(b2[1])), 'none', G['color'], G.get('w', 1.4) * view.s, 0.95))
    return ''.join(out)
