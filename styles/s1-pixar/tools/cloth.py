"""cloth — marks on a garment (a sweep layer of person.py) and loose pieces of cloth; they follow the layer's bend."""
from pix import smooth_path, mix, f, spline, paint_volume, lock_ribbon
from body import section_pt


def on(L, x, y, lift=0.4):
    """front-view point (x, y) of a layer -> 3D point on its surface"""
    return section_pt(L["w"], L["zf"], L["zb"], y, x, n=L.get("n", 2.1), xoff=L.get("xoff"), zoff=L.get("zoff"), lift=lift)


def patch(cv, rig, L, pts, fill, lift=0.4, a=1.0, edge=None, edge_w=1.4, blur=0.0):
    """a flat shape on the garment: pts in the layer's front coordinates"""
    d = smooth_path([rig.P(on(L, x, y, lift)) for x, y in pts])
    fl = f' filter="url(#{cv.blur(blur * rig.s)})"' if blur else ""
    cv.add(f'<path d="{d}" fill="{fill}" opacity="{a}"{fl}/>')
    if edge:
        cv.add(f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="{f(edge_w * rig.s)}" opacity="0.7"/>')
    return d


def seam(cv, rig, L, pts, col, w=1.4, a=0.7, lift=0.5, blur=0.0, dash=None):
    """a line on the garment (a seam, a fold, an edge)"""
    d = smooth_path([rig.P(on(L, x, y, lift)) for x, y in pts], closed=False)
    fl = f' filter="url(#{cv.blur(blur * rig.s)})"' if blur else ""
    ds = f' stroke-dasharray="{f(dash[0] * rig.s)} {f(dash[1] * rig.s)}"' if dash else ""
    cv.add(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{f(w * rig.s)}" stroke-linecap="round" opacity="{a}"{fl}{ds}/>')


def band(cv, rig, L, y0, y1, col, a=1.0, lift=0.4):
    """a band across the visible front of the garment"""
    top, bot = [], []
    for i in range(25):
        t = -1 + 2 * i / 24
        top.append(rig.P(on(L, t * (spline(L["w"], y0) - 0.2), y0, lift)))
        bot.append(rig.P(on(L, t * (spline(L["w"], y1) - 0.2), y1, lift)))
    cv.add(f'<path d="{smooth_path(top + bot[::-1])}" fill="{col}" opacity="{a}"/>')


def dot(cv, rig, L, x, y, r, col, lift=1.0):
    p = rig.P(on(L, x, y, lift))
    cv.add(f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{f(r * rig.s)}" fill="{col}"/>')


def ribbon(cv, rig, centre, widths, normals, col, sh, size, stripes=(), lift=0.14):
    """a strip of cloth along 3D points (a towel, a strap): painted as a soft volume, with stripes across.
    stripes: (t0, t1, colour) along the strip, 0..1"""
    pts, z, c2 = lock_ribbon(rig, centre, widths, normals=normals)
    d = smooth_path(pts)
    k = paint_volume(cv, d, col, sh, size * rig.s, lift=lift, soft=0.1)
    n = len(centre)
    g = [f'<g clip-path="url(#{k})">']
    for t0, t1, c in stripes:
        i0, i1 = int(t0 * (n - 1)), max(int(t0 * (n - 1)) + 1, int(t1 * (n - 1)))
        q = pts[i0:i1 + 1] + pts[2 * n - 1 - i1:2 * n - i0]
        g.append(f'<path d="{smooth_path(q)}" fill="{c}" opacity="0.9"/>')
    g.append('</g>')
    cv.add("".join(g))
    return d
