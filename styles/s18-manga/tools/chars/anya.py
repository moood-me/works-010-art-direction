"""Аня, about 20: warm, trusting, dreamy. An oval face with a soft jaw, a small slightly upturned nose, full lower lip;
light-brown hair to below the shoulders, parted on one side, a lock falling by the cheek; eyes a little larger than
the others', a lash at the outer corner, looking a little up and away."""
from features import *
from hair import Hair

HEAD = dict(
    sections=sections(cranium=0.97, cheek=0.97, jaw=0.9, chin=0.85, depth=0.97, face=0.96, hollow=0.0),
    nose=dict(profile=[(0.0, 0.006, 0.026), (0.08, 0.03, 0.03), (0.165, 0.085, 0.04), (0.185, 0.08, 0.045), (0.21, 0.015, 0.045)],
              tip=0.17, wing=0.05, bridge_from=0.55),
    eye=dict(x=0.135, y=0.0, w=0.07, h=0.041, crease=0.75, lash=1, iris=0.52, peak=-0.2),
    brow=dict(x0=0.05, x1=0.235, y=-0.09, arch=0.025, th=0.75, slope=0.01),
    mouth=dict(y=0.29, w=0.082, lower=0.03, upper_line=1, lip=0.02),
    ear=dict(y=0.07, h=0.22, w=0.11),
    neck=dict(rx=0.13, rz=0.15),
    jaw=dict(angle_y=0.40),
    rest=dict(smile=0.18, look=(-0.15, -0.25), open=0.95),
    shade=dict(level=0.14),
)
HAIR = Hair(mode='tone', part=-28, n=170, width=0.075, thick=0.055, top_thick=0.07,
            hl=[(0, -0.31), (35, -0.28), (70, -0.17), (95, -0.06), (120, 0.0), (180, 0.08)],
            end=[(0, -0.31), (62, -0.17), (80, 0.2), (105, 0.62), (135, 0.95), (180, 1.0)],
            end_neg=[(0, -0.31), (62, -0.17), (100, -0.02), (118, 0.6), (140, 0.95), (180, 1.0)],
            hl_neg=[(0, -0.31), (35, -0.28), (70, -0.17), (95, -0.08), (115, 0.0), (180, 0.08)],
            hang_out=0.12, wave=0.02, waves=1.5, tone_level=0.15, flow=0.8, streaks=1.2, edge=0.05, sweep=6, seed=21)
EXTRAS = [cheek_blush(0.8)]


# ---------------------------------------------------------------- the figure
from body3d import *

HEIGHT = 7.1


def skeleton():
    H = HEIGHT
    j = stand(H, sw=0.58, hw=0.32, female=True)
    # weight on the right leg (the one nearer us in the three-quarter view), the hip out to that side
    j['pelvis'] = (-0.08, j['pelvis'][1] - 0.03, 0)
    j['crotch'] = (-0.08, j['crotch'][1] - 0.03, 0)
    j['hip_r'] = (-0.40, j['hip_r'][1] - 0.06, 0.0); j['hip_l'] = (0.24, j['hip_l'][1] + 0.02, 0.0)
    j['kn_r'] = (-0.30, j['kn_r'][1], 0.04); j['kn_l'] = (0.12, j['kn_l'][1] + 0.05, 0.22)
    j['an_r'] = (-0.24, j['an_r'][1], -0.06); j['an_l'] = (0.24, j['an_l'][1], 0.12)
    j['heel_r'] = (-0.24, 0, -0.18); j['toe_r'] = (-0.36, 0, 0.82)
    j['heel_l'] = (0.24, 0, 0.0); j['toe_l'] = (0.52, 0, 0.95)
    j['waist'] = (-0.03, j['waist'][1], -0.02)
    j['chest'] = (0.02, j['chest'][1], 0.0)
    j['neck'] = (0.03, j['neck'][1], -0.04)
    # shoulders tilt against the hips
    j['sh_r'] = (-0.57, j['sh_r'][1] + 0.05, -0.04); j['sh_l'] = (0.60, j['sh_l'][1] - 0.03, -0.04)
    # right arm hanging loose, left arm holding a book to the chest
    j['el_r'] = (-0.70, j['el_r'][1] + 0.05, -0.1); j['wr_r'] = (-0.66, j['wr_r'][1] + 0.05, 0.1)
    j['el_l'] = (0.66, -4.5, 0.18); j['wr_l'] = (0.05, -4.9, 0.62)
    B = Body(j, scale_sections(FEMALE, 0.95), spine_of(j, H), twist=[(0, -6), (1, 6)])
    return B


def FIGURE(v, e=None, lw=2.0):
    """Standing at ease with her weight on one leg, a book held to her chest, the other hand loose; the head tilted,
    looking up and away. A knitted cardigan over a blouse, an A-line skirt below the knee, flat shoes."""
    me = __import__('chars.anya', fromlist=['x'])
    B = skeleton(); j = B.j; H = HEIGHT
    o = []
    hv = dict(yaw_rel=6, pitch=-5, roll=-8, e=e, lw=lw)
    pit = add3(j['neck'], (0, 0.02, 0.06))
    o.append(head3d(v, me, pit, part='back', **hv))
    near = 'r' if v.yaw >= 0 else 'l'
    far = 'l' if near == 'r' else 'r'
    knit = 0.12
    def arm_svg(side):
        pts, rad = arm_chain(j, side, (0.15, 0.13, 0.105, 0.115, 0.07))
        sp, sr = arm_chain(j, side, (0.15, 0.13, 0.105, 0.115, 0.07), grow=0.04, until=0.93)
        P, C, N, rr = chain_outline(v, sp, sr)
        g = group([P], lw, base=knit, dark=0.4, s=v.s)
        g += fold_lines(C, N, rr, len(C) // 2, lw * 0.7, side=1, seed=3)
        g += stroke(ring_around(v, sp[-2], sp[-1], 0.85, sr[-1] * 0.95), lw * 0.6)
        g += hand_at(v, pts[-1], pts[-2], 0.56, 'relaxed' if side == 'r' else 'loose', twist=95 if side == 'r' else 20, lw=lw)
        return g
    def leg_svg(side):
        pts, rad = leg_chain(j, side, (0.27, 0.2, 0.12, 0.14, 0.065))
        P, C, N, rr = chain_outline(v, pts, rad)
        g = group([P], lw, base=0, dark=0.15, s=v.s)
        hull, sole = shoe3d(v, j['heel_' + side], j['toe_' + side], width=0.15, height=0.24, toe_h=0.09)
        g += group([hull], lw, base=0.0, dark=0.3, s=v.s) + stroke(sole, lw * 0.5)
        return g
    o.append(leg_svg(far)); o.append(leg_svg(near))
    o.append(head3d(v, me, pit, **hv))
    # skirt: from the waist, a cone flaring to below the knee
    f_w = frac(H, -0.615 * H, j)
    f_hem = frac(H, -2.0, j)
    flare = lambda f: max(0.0, (f_w - f)) * 0.42
    P, hem, _ = torso_outline(B, v, f_hem, f_w, grow=0.03, flare=flare)
    sk = group([P], lw, base=0.2, dark=0.45, s=v.s, off=0.07)
    rnd = random.Random(4)
    for a in (-60, -25, 5, 35, 65):
        p0 = surf(B, f_w - 0.05, a, 0.03); p1 = surf(B, f_hem + 0.02, a + rnd.uniform(-8, 8), 0.03 + flare(f_hem))
        if v.facing((math.sin(math.radians(a)), 0, math.cos(math.radians(a)))) > 0.1:
            sk += seams(v, [p0, lerp3(p0, p1, 0.5), p1], lw, 0.55)
    o.append(sk)
    # blouse and cardigan: one torso shell; the cardigan's open front shows the blouse
    f_c = frac(H, -3.85, j)
    P, hem, _ = torso_outline(B, v, f_c, 1.0, grow=0.05)
    card = group([P], lw, base=knit, dark=0.42, s=v.s, extra=hatch(None, (0, 0, 1, 1)) if False else '')
    # the opening: between two front edges, the blouse
    edge_r = [surf(B, f, -6 - max(0, f - 0.6) * 60, 0.05) for f in [0.99, 0.85, 0.7, 0.55, f_c + 0.02]]
    edge_l = [surf(B, f, 6 + max(0, f - 0.6) * 60, 0.05) for f in [0.99, 0.85, 0.7, 0.55, f_c + 0.02]]
    opening = [v(p) for p in edge_r] + [v(p) for p in edge_l[::-1]]
    card += fillpath(opening, PAPER) + stroke([v(p) for p in edge_r], lw * 0.9) + stroke([v(p) for p in edge_l], lw * 0.9)
    card += seams(v, [surf(B, 0.97, -30, 0.06), surf(B, 0.99, 0, 0.0), surf(B, 0.97, 30, 0.06)], lw, 0.7)
    for f in (0.78, 0.6, 0.45):
        card += button(v, surf(B, f, -10, 0.06), lw)
    # knit texture: rows of short verticals
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    card = card.replace('</g>', '', 0)
    o.append(card + clip(P, hatch(None, (min(xs), min(ys), max(xs), max(ys)), angle=90, gap=lw * 2.3, w=lw * 0.3, length=(0.03, 0.06), seed=6), smooth=False))
    # the book on the chest, then the far arm over it
    bk = [surf(B, 0.8, -25, 0.12), surf(B, 0.82, 35, 0.12), surf(B, 0.5, 38, 0.14), surf(B, 0.48, -22, 0.14)]
    o.append(group([[v(p) for p in bk]], lw, base=0.45, dark=0.75, s=v.s, off=0.03))
    o.append(arm_svg('r'))
    o.append(arm_svg('l'))
    o.append(head3d(v, me, pit, part='front', **hv))
    return ''.join(o)
