// The С18 face on the 3D head: styles/s18-manga/tools/head.py (eye, brow, nose, mouth, ear's inner lines) and
// features.py (glasses, wrinkles) ported. As there, every feature is a 3D curve on the head's surface (head units:
// y down from the eye line, z to the viewer) — here the "view" is the moving 3D head in the camera: v.pt(p) gives the
// picture point and its depth, v.facing(n) how much a direction of the head looks at the camera, v.yaw the head's turn
// from the camera (degrees, + to the picture's right), v.s the pixels of one head unit, v.seen(pt) whether nothing
// stands in front (a hand, the hair). A line is split where it is hidden.
import { stroke, outline, fillPoly, toneFill, INK, PAPER } from './pen.js';

export const EXPR = {
  rest: { open: 1.0, squint: 0.0, brow_in: 0.0, brow_out: 0.0, knit: 0.0, smile: 0.0, mopen: 0.0, mwide: 0.0, frown: 0.0, jaw: 0.0, smirk: 0.0, look: [0, 0], small: 0 },
  joy: { open: 0.75, squint: 0.6, brow_in: 0.3, brow_out: 0.2, smile: 1.0, mopen: 0.35, mwide: 0.2, jaw: 0.2 },
  surprise: { open: 1.25, brow_in: 1.0, brow_out: 1.0, mopen: 0.45, mwide: -0.3, jaw: 0.5, small: 1 },
  sadness: { open: 0.75, brow_in: 1.0, brow_out: -0.5, frown: 0.6, look: [0, 0.5], knit: 0.3 },
  anger: { open: 0.9, squint: 0.3, brow_in: -0.9, knit: 1.0, frown: 0.5, mopen: 0.18, mwide: 0.2, jaw: 0.1 },
};
export function interpTable(tab, y) {
  const n = tab.length;
  if (y <= tab[0][0]) return tab[0].slice(1);
  if (y >= tab[n - 1][0]) return tab[n - 1].slice(1);
  for (let i = 0; i < n - 1; i++) {
    const a = tab[i], b = tab[i + 1];
    if (a[0] <= y && y <= b[0]) {
      const t = (y - a[0]) / (b[0] - a[0]), p0 = tab[Math.max(i - 1, 0)], p3 = tab[Math.min(i + 2, n - 1)], out = [];
      for (let j = 1; j < a.length; j++) { const v0 = p0[j], v1 = a[j], v2 = b[j], v3 = p3[j]; out.push(0.5 * ((2 * v1) + (-v0 + v2) * t + (2 * v0 - 5 * v1 + 4 * v2 - v3) * t * t + (-v0 + 3 * v1 - 3 * v2 + v3) * t ** 3)); }
      return out;
    }
  }
  return tab[n - 1].slice(1);
}

export class Head {
  constructor(p) { this.p = p; this.tab0 = p.sections; this.setExpr({}); }
  // the expression: numbers of EXPR over the character's rest
  setExpr(e) {
    this.e = { ...EXPR.rest, ...(this.p.rest || {}), ...e };
    const jaw = (this.e.jaw || 0) * 0.07;
    this.tab = jaw ? this.tab0.map(r => [r[0] + jaw * Math.max(0, Math.min(1, (r[0] - 0.26) / 0.12)), ...r.slice(1)]) : this.tab0;
    this.bottom = this.tab[this.tab.length - 1][0];
  }
  sec(y) { return interpTable(this.tab, y); }
  zsurf(x, y) { const [w, zf, , z0, nf] = this.sec(y), u = Math.min(1, Math.abs(x) / Math.max(w, 1e-4)); return z0 + (zf - z0) * (1 - u ** nf) ** (1 / nf); }
  on(x, y, dz = 0) { return [x, y, this.zsurf(x, y) + dz]; }

  // a line of 3D points, drawn where it is seen
  line(ctx, v, pts3, w, o = {}) {
    const runs = []; let cur = [];
    for (const p of pts3) { const q = v.pt(p); if (o.all || v.seen(q)) cur.push(q); else { if (cur.length > 1) runs.push(cur); cur = []; } }
    if (cur.length > 1) runs.push(cur);
    for (const r of runs) {
      let ww = w;
      if (Array.isArray(w) && r.length !== pts3.length) ww = w;        // the weights stretch over the seen part
      stroke(ctx, r, ww, o);
    }
  }

  eyeCurves(side) {
    const E = this.p.eye, e = this.e, { x: ex, y: ey, w: ew, h: eh } = E, tilt = E.tilt || 0;
    const openness = e.open * (E.open ?? 1), squint = e.squint || 0, up = [], lo = [];
    for (let i = 0; i < 13; i++) {
      const u = -1 + 2 * i / 12, x = side * (ex + u * ew);
      const bu = (1 - u * u) * (1 + (E.peak ?? -0.25) * u), bl = (1 - u * u) * (1 + (E.lpeak ?? 0.2) * u), yy = ey - tilt * u * ew;
      let yu = yy - eh * openness * bu + (E.droop || 0) * Math.max(0, u) ** 2 * eh;
      const yl = yy + eh * 0.55 * bl * (1 - squint * 0.8) - squint * 0.25 * eh * (1 - u * u);
      yu = openness > 0.12 ? Math.min(yu, yl - 0.002) : yy - eh * 0.1 * bu;
      up.push(this.on(x, yu, -0.012)); lo.push(this.on(x, yl, -0.012));
    }
    return [up, lo, openness];
  }
  eye(ctx, v, side, lw) {
    const E = this.p.eye, e = this.e, { x: ex, y: ey, w: ew, h: eh } = E;
    if (v.facing([side * 0.6, 0, 0.8]) < 0.05) return;
    const [up, lo, openness] = this.eyeCurves(side);
    const UP = up.map(p => v.pt(p)), LO = lo.map(p => v.pt(p));
    if (!v.seen(UP[6]) && !v.seen(LO[6])) return;
    if (openness > 0.12) {
      const opening = UP.concat(LO.slice().reverse());
      const [gx, gy] = e.look || [0, 0];
      const ix = side * ex + gx * ew * 0.45, iy = ey - eh * 0.15 + gy * eh * 0.5, ir = (E.iris ?? 0.48) * eh * 2 * (1 - 0.15 * (e.small || 0));
      const RG = []; for (let k = 0; k < 24; k++) { const a = 2 * Math.PI * k / 24; RG.push(v.pt(this.on(ix + ir * 0.92 * Math.cos(a), iy + ir * Math.sin(a), -0.004))); }
      let cx = 0, cy = 0, x0 = Infinity, x1 = -Infinity; for (const p of RG) { cx += p[0] / 24; cy += p[1] / 24; x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0]); }
      const rad = (x1 - x0) / 2;
      ctx.save(); ctx.beginPath(); ctx.moveTo(opening[0][0], opening[0][1]); for (const p of opening) ctx.lineTo(p[0], p[1]); ctx.closePath(); ctx.clip();
      fillPoly(ctx, opening, PAPER); fillPoly(ctx, RG, INK);
      const circ = (x, y, r, f) => { ctx.beginPath(); ctx.arc(x, y, Math.max(0.1, r), 0, 6.2832); ctx.fillStyle = f; ctx.fill(); };
      const ring = []; for (let k = 0; k < 16; k++) ring.push([cx + rad * 0.12 + rad * 0.55 * Math.cos(k / 16 * 6.2832), cy + rad * 0.18 + rad * 0.55 * Math.sin(k / 16 * 6.2832)]);
      toneFill(ctx, ring, 0.72, v.pitch * 0.8);
      circ(cx, cy, rad * 0.42, INK);
      if (E.shine !== false) circ(cx - rad * 0.38, cy - rad * 0.38, Math.max(1.2, rad * 0.22), PAPER);
      toneFill(ctx, UP.concat(UP.slice().reverse().map(p => [p[0], p[1] + rad * 0.35])), 0.3, v.pitch * 0.8);
      ctx.restore();
    }
    const lash = (E.lash || 0) > 0;
    const wl = lash ? [0.5, 1.0, 1.5, 1.9, 2.2, 2.6, 2.8].map(k => k * lw) : [0.4, 0.9, 1.3, 1.5, 1.6, 1.7, 1.6].map(k => k * lw);
    stroke(ctx, openness > 0.12 ? UP.slice(1) : UP, wl, { taper: [0.05, 0.12] });
    if (lash && openness > 0.12) {
      const a = UP[12], b = UP[10], dx = a[0] - b[0], dy = a[1] - b[1], L = Math.hypot(dx, dy) || 1;
      stroke(ctx, [a, [a[0] + dx / L * lw * 3.2, a[1] + dy / L * lw * 3.2 - lw * 1.4]], [lw * 1.6, lw * 0.4], { taper: [0, 0.5] });
    }
    if (openness > 0.12) {
      stroke(ctx, LO.slice(5, 12), lw * 0.55, { taper: [0.4, 0.3] });
      stroke(ctx, LO.slice(2, 4), lw * 0.4, { taper: [0.5, 0.5] });
    }
    const cr = E.crease ?? 0.6;
    if (cr > 0) stroke(ctx, up.map((p, i) => v.pt(this.on(p[0], p[1] - eh * cr * (0.8 + 0.4 * (1 - Math.abs(-1 + 2 * i / 12))) * Math.max(0.5, openness), -0.01))).slice(3, 12), lw * 0.45, { taper: [0.4, 0.4] });
    if (E.bag) stroke(ctx, lo.slice(3, 12).map(p => v.pt(this.on(p[0], p[1] + eh * (0.55 + 0.35 * E.bag), -0.005))), lw * 0.4, { taper: [0.5, 0.5] });
    if ((e.squint || 0) > 0.5) {
      const x0 = side * (ex + ew);
      stroke(ctx, [this.on(x0, ey + eh * 0.1), this.on(x0 + side * ew * 0.35, ey + eh * 0.5)].map(p => v.pt(p)), lw * 0.4, { taper: [0.4, 0.5] });
      stroke(ctx, [this.on(x0 - side * ew * 0.05, ey + eh * 0.55), this.on(x0 + side * ew * 0.2, ey + eh * 1.0)].map(p => v.pt(p)), lw * 0.35, { taper: [0.4, 0.5] });
    }
  }
  brow(ctx, v, side, lw) {
    const B = this.p.brow, e = this.e;
    if (v.facing([side * 0.6, 0, 0.8]) < 0.0) return;
    const pts = [], n = 9;
    for (let i = 0; i < n; i++) {
      const u = i / (n - 1), x = side * (B.x0 + (B.x1 - B.x0) * u - e.knit * 0.012 * (1 - u));
      const arch = (B.arch ?? 0.02) * Math.sin(u * Math.PI) * (1 + (B.arch_out ?? 0.2) * u);
      const y = B.y - arch + (B.slope || 0) * u - e.brow_in * 0.035 * (1 - u) ** 1.2 - e.brow_out * 0.03 * u + e.knit * 0.02 * (1 - u) ** 2;
      pts.push(this.on(x, y, 0.004));
    }
    const th = B.th ?? 1;
    this.line(ctx, v, pts, [1.0, 2.2, 2.0, 1.4, 0.6].map(k => k * lw * th), { taper: [0.1, 0.4] });
  }
  nose(ctx, v, lw) {
    const n = this.p.nose, prof = n.profile, ytip = n.tip, ybase = prof[prof.length - 1][0], yaw = v.yaw, ay = Math.abs(yaw), sgn = yaw >= 0 ? 1 : -1;
    const ridge = [];
    for (let i = 0; i < 11; i++) { const y = prof[0][0] + (ytip - prof[0][0]) * i / 10, [pr] = interpTable(prof, y); ridge.push([0, y, this.zsurf(0, y) + pr]); }
    if (ay < 8) {
      const ln = []; for (let k = 0; k < 7; k++) { const y = prof[0][0] + 0.07 + k * (ytip - prof[0][0] - 0.08) / 6; ln.push([-0.035 * (n.w ?? 1), y, this.zsurf(-0.035, y) + 0.01]); }
      this.line(ctx, v, ln.slice(3), lw * 0.6, { taper: [0.5, 0.3] });
    } else if (ay < 70) {
      // the far side wall of the nose: at each level the point of the wedge furthest across the picture
      const side = [];
      for (let i = 0; i < 12; i++) {
        const y = prof[0][0] + 0.05 + (ytip + 0.02 - prof[0][0] - 0.05) * i / 11, [pr, hw] = interpTable(prof, y);
        let best = null;
        for (let k = -8; k <= 8; k++) { const t = k / 8, x = t * hw, p = [x, y, this.zsurf(x, y) + pr * (1 - Math.abs(t) ** 1.5)], X = v.across(p); if (!best || X * sgn > best[0] * sgn) best = [X, p]; }
        side.push(best[1]);
      }
      const k0 = Math.floor(side.length * (n.bridge_from ?? 0.35));
      this.line(ctx, v, side.slice(k0), [lw * 0.3, lw * 0.8, lw * 1.2], { taper: [0.4, 0.15], all: true });
    }
    const tw = n.wing ?? 0.055, yb = ybase - 0.01;
    for (const s of [-1, 1]) {
      const wing = [this.on(s * tw * 0.55, ytip + 0.035, prof[prof.length - 2][1] * 0.6 + 0.03), this.on(s * tw * 1.05, ytip + 0.01, 0.025), this.on(s * tw * 1.15, yb - 0.02, 0.02), this.on(s * tw * 0.75, yb + 0.005, 0.02)];
      const far = (s > 0) === (yaw >= 0) && ay >= 8;
      if (v.facing([s * 0.7, 0.1, 0.7]) > -0.25 && !(ay > 70 && far)) { const wl = lw * (far ? 0.8 : 1.1); this.line(ctx, v, wing, [wl * 0.5, wl * 1.2, wl * 1.0, wl * 0.4], { taper: [0.3, 0.3], all: !far }); }
      if (v.facing([s * 0.3, 0.6, 0.7]) > -0.1 && !(ay > 70 && far)) this.line(ctx, v, [this.on(s * tw * 0.15, yb + 0.004, 0.035), this.on(s * tw * 0.55, yb - 0.004, 0.03)], [lw * 0.6, lw * 1.6], { taper: [0.3, 0.4], all: !far });
    }
    if (ay >= 8) {
      const t1 = [0, ytip + 0.03, this.zsurf(0, ytip + 0.03) + interpTable(prof, ytip + 0.03)[0] * 0.8];
      this.line(ctx, v, [t1, [0, ybase - 0.005, this.zsurf(0, ybase) + 0.02], [sgn * -0.02, yb, this.zsurf(0, ybase) + 0.03]], lw * 0.7, { taper: [0.3, 0.4], all: true });
    }
  }
  mouth(ctx, v, lw) {
    const m = this.p.mouth, e = this.e, open = e.mopen || 0, y0 = m.y + (e.jaw || 0) * 0.02, hw = m.w * (1 + 0.25 * (e.mwide || 0) + 0.12 * (e.smile || 0));
    const mid = [], up = [], lo = [];
    for (let i = 0; i < 15; i++) {
      const u = -1 + 2 * i / 14, x = u * hw;
      const corner = (e.smile || 0) * 0.035 * u * u - (e.frown || 0) * 0.03 * u * u + (e.smirk || 0) * 0.03 * Math.max(0, u) ** 2 - (e.smirk || 0) * 0.008 * Math.max(0, -u);
      const bow = (m.bow ?? 0.006) * Math.cos(u * Math.PI / 2) ** 2, ym = y0 - corner + bow * 0.5, yo = open * 0.075 * (1 - u * u) ** 0.8;
      mid.push(this.on(x, ym, 0.012 * (1 - u * u))); up.push(this.on(x, ym - yo * 0.30, 0.012 * (1 - u * u))); lo.push(this.on(x, ym + yo * 0.70 + open * 0.004, 0.01 * (1 - u * u)));
    }
    const keep = mid.map(p => v.facing([p[0] * 2.5, 0, 0.9]) > 0.05 && v.seen(v.pt(p)));
    const vis = L => L.filter((_, i) => keep[i]).map(p => v.pt(p));
    if (open > 0.08) {
      const UP = vis(up), LO = vis(lo);
      if (UP.length > 2) {
        const hole = UP.concat(LO.slice().reverse());
        ctx.save(); ctx.beginPath(); ctx.moveTo(hole[0][0], hole[0][1]); for (const p of hole) ctx.lineTo(p[0], p[1]); ctx.closePath(); ctx.clip();
        fillPoly(ctx, hole, INK);
        if ((e.teeth ?? 1) && open > 0.15) {
          const tb = up.filter((_, i) => keep[i]).map(p => v.pt(this.on(p[0] * 0.92, p[1] + 0.012 + 0.006 * (1 - (p[0] / (m.w * 1.3)) ** 2), 0.004)));
          fillPoly(ctx, UP.concat(tb.slice().reverse()), PAPER); stroke(ctx, tb.slice(1, -1), lw * 0.35, { taper: [0.3, 0.3] });
        }
        if (open > 0.3) {
          const tg = lo.filter((_, i) => keep[i]).map(p => v.pt(this.on(p[0] * 0.75, p[1] - 0.018 - 0.01 * (1 - (p[0] / (m.w * 1.4)) ** 2), 0)));
          const shape = tg.concat(LO.slice().reverse().slice(1, -1));
          fillPoly(ctx, shape, PAPER); toneFill(ctx, shape, 0.25, v.pitch * 0.8); stroke(ctx, tg.slice(1, -1), lw * 0.45, { taper: [0.3, 0.3] });
        }
        ctx.restore();
        stroke(ctx, UP, [0.6, 1.4, 1.6, 1.4, 0.6].map(k => k * lw), { taper: [0.12, 0.12] });
        stroke(ctx, LO, [0.5, 1.0, 1.2, 1.0, 0.5].map(k => k * lw), { taper: [0.15, 0.15] });
      }
    } else {
      const M = vis(mid);
      if (M.length > 2) stroke(ctx, M, [0.4, 1.2, 1.5, 1.2, 0.4].map(k => k * lw), { taper: [0.12, 0.15] });
    }
    const ll = m.lower ?? 0.035;
    if (ll && v.facing([0, 0.3, 0.9]) > 0) {
      const ylo = m.y + (e.jaw || 0) * 0.02 + 0.02 + ll + open * 0.055;
      this.line(ctx, v, [-1, -0.4, 0.2, 0.8].map(u => this.on(u * m.w * 0.45, ylo + 0.004 * (1 - u * u), 0.008)), lw * 0.75, { taper: [0.4, 0.4] });
    }
    if (m.upper_line) this.line(ctx, v, [-0.9, -0.3, 0.3, 0.9].map(u => this.on(u * m.w * 0.7, y0 - 0.018 - 0.006 * Math.cos(u * 1.4), 0.012)), lw * 0.35, { taper: [0.4, 0.4] });
    if ((e.smile || 0) > 0.3) for (const s of [-1, 1]) {
      const c = s > 0 ? mid[14] : mid[0];
      if (v.facing([s * 0.8, 0, 0.6]) > 0) this.line(ctx, v, [this.on(c[0] + s * 0.012, c[1] - 0.012), this.on(c[0] + s * 0.02, c[1] + 0.01)], lw * 0.5, { taper: [0.4, 0.4] });
    }
  }
  // the ear's inner fold (its rim is the 3D plate's contour)
  ear(ctx, v, side, lw) {
    if (v.facing([side, 0, 0]) <= 0.2) return;
    const E = this.p.ear || {}, yc = E.y ?? 0.08, hh = E.h ?? 0.24, ww = E.w ?? 0.12, zc = E.z ?? -0.10, x0 = side * (interpTable(this.tab0, yc)[0] * 0.97 + 0.02);
    const P = (dy, dz) => [x0 + side * (0.03 * Math.max(0, -dz / ww) * 0.8 + 0.004), yc + dy * hh, zc + dz * ww];
    this.line(ctx, v, [P(-0.25, 0.1), P(-0.32, -0.12), P(-0.1, -0.28), P(0.18, -0.2), P(0.25, 0.0)], lw * 0.6, { taper: [0.3, 0.3] });
    this.line(ctx, v, [P(0.05, 0.2), P(0.18, 0.1)], lw * 0.8, { taper: [0.3, 0.3] });
  }
  // features.py wrinkles(naso=1, under=1, forehead=1)
  wrinkles(ctx, v, lw, o = { forehead: 1, naso: 1, under: 1 }) {
    const E = this.p.eye, m = this.p.mouth;
    for (let i = 0; i < (o.forehead || 0); i++) for (const s of [-1, 1]) {
      const y = -0.20 - i * 0.035;
      if (v.facing([s * 0.4, -0.3, 0.8]) > 0) this.line(ctx, v, [0.03, 0.08, 0.13, 0.18].map(x => this.on(s * x, y + 0.006 * Math.sin(x * 12 + i), 0.003)), lw * 0.4, { taper: [0.4, 0.4] });
    }
    for (const s of [-1, 1]) {
      if (v.facing([s * 0.8, 0, 0.5]) < 0.05) continue;
      if (o.naso) this.line(ctx, v, [this.on(s * 0.065, 0.17), this.on(s * 0.10, 0.25), this.on(s * (m.w + 0.025), 0.33 + 0.02 * o.naso)], [lw * 0.3, lw * 0.9, lw * 0.4], { taper: [0.3, 0.5] });
      if (o.under) this.line(ctx, v, [this.on(s * (E.x - E.w * 0.6), E.y + 0.06), this.on(s * (E.x + E.w * 0.4), E.y + 0.075)], lw * 0.35, { taper: [0.4, 0.4] });
    }
  }
  // features.py glasses('rect', r, rh, dz, thick)
  glasses(ctx, v, lw, o = { r: 0.07, rh: 0.042, dz: 0.05, thick: 1.0 }) {
    const E = this.p.eye, { r, rh, dz, thick } = o, zs = [];
    for (const s of [-1, 1]) {
      const cx = s * E.x, cy = E.y + 0.01, z = interpZ(this, cx, cy) + dz; zs.push(z);
      if (v.facing([s * 0.5, 0, 0.85]) <= -0.2) continue;
      const pts = [];
      for (let i = 0; i <= 36; i++) {
        const a = 2 * Math.PI * i / 36, c = Math.cos(a), sn = Math.sin(a);
        const dx = r * Math.sign(c) * Math.abs(c) ** 0.45, dy = rh * Math.sign(sn) * Math.abs(sn) ** 0.45;
        pts.push([cx + dx, cy + dy, z - (dx * s > 0 ? Math.abs(dx) * 0.25 : 0)]);
      }
      // the rim, its weight by the light, where it is seen
      const P = pts.map(p => v.pt(p)), n = P.length - 1;
      let area = 0; for (let i = 0; i < n; i++) area += P[i][0] * P[i + 1][1] - P[i + 1][0] * P[i][1];
      const sg = area > 0 ? 1 : -1; let run = [], ws = [];
      const flush = () => { if (run.length > 1) stroke(ctx, run, ws, { taper: [0.04, 0.04], smooth: false }); run = []; ws = []; };
      for (let i = 0; i <= n; i++) {
        const a = P[(i - 1 + n) % n], b = P[(i + 1) % n], ddx = b[0] - a[0], ddy = b[1] - a[1], l = Math.hypot(ddx, ddy) || 1, d = (-ddy / l * -0.55 + ddx / l * -0.83) * sg;
        if (v.seen(P[i])) { run.push(P[i]); ws.push(Math.max(0.35, lw * thick * (1 + 0.4 * d))); } else flush();
      }
      flush();
      this.line(ctx, v, [[cx - r * 0.55, cy - rh * 0.1, z], [cx - r * 0.1, cy - rh * 0.6, z]], lw * 0.35, { taper: [0.4, 0.4] });
    }
    this.line(ctx, v, [[-E.x + r * 0.95, E.y - 0.005, zs[0]], [0, E.y - 0.015, zs[0] + 0.015], [E.x - r * 0.95, E.y - 0.005, zs[1]]], lw * thick * 0.9, { taper: [0.1, 0.1] });
    for (const s of [-1, 1]) if (v.facing([s, 0, 0.15]) > 0.1) {
      const w = interpTable(this.tab0, E.y)[0], xo = s * (E.x + r);
      this.line(ctx, v, [[xo, E.y - 0.01, interpZ(this, xo, E.y) + dz * 0.8 - r * 0.25], [s * (w + 0.015), E.y - 0.01, 0.05], [s * (w + 0.01), E.y + 0.02, -0.12]], lw * thick * 0.8, { taper: [0.05, 0.3] });
    }
  }
  draw(ctx, v, lw) {
    for (const s of [-1, 1]) { this.eye(ctx, v, s, lw); this.brow(ctx, v, s, lw); }
    this.nose(ctx, v, lw); this.mouth(ctx, v, lw);
    this.wrinkles(ctx, v, lw); this.glasses(ctx, v, lw);
    for (const s of [-1, 1]) this.ear(ctx, v, s, lw);
  }
}
// the glasses sit on the resting face (they do not ride the jaw)
function interpZ(h, x, y) { const [w, zf, , z0, nf] = interpTable(h.tab0, y), u = Math.min(1, Math.abs(x) / Math.max(w, 1e-4)); return z0 + (zf - z0) * (1 - u ** nf) ** (1 / nf); }
