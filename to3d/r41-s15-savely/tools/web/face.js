// The drawn face: the style's own eye, brow and mouth (styles/s15-noir/tools/head.py: eye, brow, mouth of the front
// view), ported to a canvas and drawn from a few numbers each time they change. The canvas lies on the head's front
// planes; the black of the head's side, the nose's wedge and the jaw's shadow are NOT drawn here — the light makes them.
// Canvas: head units, x −80…80, y −110…110.
export const RECT = [-80, -110, 160, 220];
const BLACK = '#07070b', WHITE = '#ece6d6';

// noir.d: a path through points; [x, y] a hard corner, [x, y, 's'] passed smoothly
export function pathOf(pts, closed = true) {
  const n = pts.length, p = new Path2D();
  const tan = i => { if (pts[i].length < 3 || (!closed && (i === 0 || i === n - 1))) return [0, 0]; const a = pts[(i - 1 + n) % n], b = pts[(i + 1) % n]; return [(b[0] - a[0]) / 6, (b[1] - a[1]) / 6]; };
  p.moveTo(pts[0][0], pts[0][1]);
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const j = (i + 1) % n, a = pts[i], b = pts[j], t0 = tan(i), t1 = tan(j);
    if (!t0[0] && !t0[1] && !t1[0] && !t1[1]) p.lineTo(b[0], b[1]);
    else p.bezierCurveTo(a[0] + t0[0], a[1] + t0[1], b[0] - t1[0], b[1] - t1[1], b[0], b[1]);
  }
  if (closed) p.closePath();
  return p;
}
const shape = (g, pts, fill) => { g.fillStyle = fill; g.fill(pathOf(pts)); };
function wedge(g, a, b, w0, w1, fill = BLACK, bend = 0) {
  const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy) || 1, nx = -dy / L, ny = dx / L;
  const mx = (a[0] + b[0]) / 2 + nx * bend, my = (a[1] + b[1]) / 2 + ny * bend, wm = (w0 + w1) / 2;
  shape(g, [[a[0] + nx * w0 / 2, a[1] + ny * w0 / 2], [mx + nx * wm / 2, my + ny * wm / 2, 's'], [b[0] + nx * w1 / 2, b[1] + ny * w1 / 2], [b[0] - nx * w1 / 2, b[1] - ny * w1 / 2],
    [mx - nx * wm / 2, my - ny * wm / 2, 's'], [a[0] - nx * w0 / 2, a[1] - ny * w0 / 2]], fill);
}
const mixp = (A, B, t) => A.map((p, i) => [p[0] + (B[i][0] - p[0]) * t, p[1] + (B[i][1] - p[1]) * t, ...(p.length > 2 ? ['s'] : [])]);

// cfg: {D: drawing.py's numbers, expr: {name: {op, brow, tilt, look, cheeks, up, mouth: [c, smirk, open, wid, mid, grin]}},
//       phrases, under(g, e): the character's own signs under the features (sockets, folds), over(g, e)}
export function makeFace(cfg) {
  const D = cfg.D, ek = D.eye, EXPR = cfg.expr;
  const NH = 10;
  const exprVec = e => [0, 0, e.op, e.brow, e.tilt, e.look?.[0] ?? 0, e.look?.[1] ?? 0, e.cheeks ?? 0, e.up ?? 0, 0, ...e.mouth];
  const vecExpr = v => ({ lid: [v[0], v[1]], op: v[2], brow: v[3], tilt: v[4], look: [v[5], v[6]], cheeks: v[7], up: v[8], mouth: v.slice(NH) });
  function mixExpr(wts) {
    let s = 0; const out = exprVec(EXPR.neutral).map(() => 0);
    for (const [k, w] of Object.entries(wts)) { if (!w || !EXPR[k]) continue; s += w; exprVec(EXPR[k]).forEach((x, i) => out[i] += x * w); }
    return s ? out.map(x => x / s) : exprVec(EXPR.neutral);
  }
  // mouth shapes of speech: [c, smirk, open, wid, mid, grin]
  const VISEME = { A: [0, 0, 0.85, 0.95, 0, 0.2], O: [0, 0, 0.7, 0.7, 0, 0], U: [0, 0, 0.4, 0.55, 0, 0], E: [0, 0, 0.5, 1.05, 0, 0.6], I: [-1, 0, 0.3, 1.1, 0, 0.8], M: [0.5, 0, 0, 0.92, 0, 0], F: [0, 0, 0.14, 0.95, 0, 0.3], C: [0, 0, 0.22, 0.95, 0, 0.3] };

  function eye(g, cx, cy, w, h, s, op, look) {
    const X = t => cx + s * t, kind = ek.kind;
    if (op <= 0.15) {
      shape(g, [[X(-w / 2), cy + 2], [X(-w / 6), cy - h * 0.55, 's'], [X(w / 4), cy - h * 0.5, 's'], [X(w / 2 + 2), cy + 3], [X(w / 4), cy - h * 0.5 + ek.lid + 1, 's'], [X(-w / 6), cy - h * 0.55 + ek.lid, 's']], BLACK);
      return;
    }
    const hh = h * op;
    const alm = kind === 'kid'
      ? [[X(-w / 2), cy + 1, 's'], [X(-w / 5), cy - hh, 's'], [X(w / 4), cy - hh * 0.95, 's'], [X(w / 2), cy, 's'], [X(w / 5), cy + hh * 0.8, 's'], [X(-w / 4), cy + hh * 0.75, 's']]
      : [[X(-w / 2), cy + 2], [X(-w / 6), cy - hh, 's'], [X(w / 4), cy - hh * 0.92, 's'], [X(w / 2), cy - 1], [X(w / 8), cy + hh * 0.55, 's']];
    const ap = pathOf(alm);
    g.fillStyle = D.white; g.fill(ap);
    g.save(); g.clip(ap);
    // the style looks to the side the head faces; here the eyes look where the gaze says
    const ix = cx + look[0], iy = cy - hh * 0.12 + look[1], r = ek.r;
    g.fillStyle = D.iris; g.beginPath(); g.ellipse(ix, iy, r, r * 1.08, 0, 0, 7); g.fill();
    if ((kind === 'kid' || kind === 'f') && op > 0.5) { g.fillStyle = WHITE; g.beginPath(); g.arc(ix - r * 0.35, iy - r * 0.4, r * 0.28, 0, 7); g.fill(); }
    g.restore();
    const t = ek.lid;
    const lid = [[X(-w / 2 - 1), cy + 2.5], [X(-w / 6), cy - hh - t * 0.55, 's'], [X(w / 4), cy - hh * 0.92 - t * 0.9, 's']];
    if (ek.lash) lid.push([X(w / 2 + 6), cy - hh * 0.5 - 6], [X(w / 2 + 1), cy]); else lid.push([X(w / 2 + 2), cy - 1.5]);
    lid.push([X(w / 2), cy - 0.5], [X(w / 4), cy - hh * 0.92 + 0.6, 's'], [X(-w / 6), cy - hh + 0.4, 's']);
    shape(g, lid, BLACK);
    if (ek.lower) wedge(g, [X(w / 2 - 1), cy], [X(0), cy + hh * 0.55 + 1], 1.8, 0.6, BLACK, -s * 1.5);
  }
  function brow(g, a, b, t, r, tl) {
    a = [a[0], a[1] - r + tl]; b = [b[0], b[1] - r - tl * 0.5];
    const mx = a[0] * 0.4 + b[0] * 0.6, my = a[1] * 0.4 + b[1] * 0.6 - 4 - Math.max(0, -tl) * 0.3;
    shape(g, [[a[0], a[1] - t * 0.5], [mx, my - t * 0.55, 's'], [b[0], b[1]], [mx, my + t * 0.35, 's'], [a[0], a[1] + t * 0.5]], D.browcol);
  }
  function mouth(g, mx, my, w0, m) {
    const [c, smirk, open, wid, mid, grin] = m, lips = D.mouth.lips || 0, lip = D.lip, w = w0 * wid;
    if (open > 0.1) {
      const k = Math.min(1, open / 0.85), w2 = w * (1 + 0.35 * grin);
      const ho = [[-w * 0.6, 2, 's'], [0, -6, 's'], [w * 0.55, 1, 's'], [w * 0.35, 14, 's'], [-w * 0.3, 15, 's']];
      const hg = [[-w2, -5], [0, -1, 's'], [w2, -7], [w2 * 0.55, 13, 's'], [-w2 * 0.3, 17, 's']].map(p => [p[0], p[1], 's']);
      const hole = mixp(ho, hg, grin).map(p => [mx + p[0], my + c * 0.5 + (p[1] < 3 ? p[1] * (0.5 + 0.5 * k) : p[1] * k), 's']);
      if (grin > 0.5) { hole[0].length = 2; hole[2].length = 2; }
      const hp = pathOf(hole);
      g.fillStyle = '#1a0d10'; g.fill(hp);
      g.save(); g.clip(hp);
      shape(g, [[mx - w2, my - 9], [mx + w2, my - 9], [mx + w2, my - 1.5 + 2 * grin], [mx, my - 1 + 5 * grin, 's'], [mx - w2, my - 1 + 2 * grin]], WHITE);
      shape(g, [[mx - w * 0.6, my + 18 * k], [mx - w * 0.15, my + 10 * k, 's'], [mx + w * 0.45, my + 10 * k, 's'], [mx + w * 0.65, my + 18 * k]], lip);
      g.restore();
      if (lips) shape(g, [[hole[0][0] - 1, hole[0][1] + 1], [mx - w * 0.4, hole[1][1] - 3, 's'], [mx, hole[1][1] - 3.5, 's'], [mx + w * 0.5, hole[1][1] - 3.5, 's'], [hole[2][0] + 1, hole[2][1] + 1], [mx, hole[1][1] + 0.5, 's']], lip);
      return;
    }
    const a = [mx - w, my + c], b = [mx + w, my + c - 6 * smirk], mm = [mx, my + mid];
    if (lips) {
      shape(g, [a, [mx - w * 0.5, mm[1] + 0.5, 's'], [mm[0], mm[1] + 1, 's'], [mx + w * 0.5, mm[1] + 0.5, 's'], b, [mx + w * 0.45, mm[1] + 6 * lips, 's'], [mx - w * 0.4, mm[1] + 6.5 * lips, 's']], D.lip2 || lip);
      shape(g, [a, [mx - w * 0.45, mm[1] - 4.5 * lips, 's'], [mx - 1, mm[1] - 3 * lips], [mx + w * 0.45, mm[1] - 5 * lips, 's'], b, [mx + w * 0.5, mm[1] + 0.8, 's'], [mm[0], mm[1] + 1.2, 's'], [mx - w * 0.5, mm[1] + 0.8, 's']], lip);
      g.strokeStyle = BLACK; g.lineWidth = 1.6; g.lineCap = 'round'; g.stroke(pathOf([a, [mx - w * 0.5, mm[1] + 0.6, 's'], [mm[0], mm[1] + 1, 's'], [mx + w * 0.5, mm[1] + 0.6, 's'], b], false));
      shape(g, [[mx - w * 0.35, mm[1] + 6.5 * lips + 1.5], [mx + w * 0.4, mm[1] + 6 * lips + 1.5], [mx + w * 0.2, mm[1] + 6 * lips + 4.5], [mx - w * 0.2, mm[1] + 6.5 * lips + 4.5]], BLACK);
    } else {
      shape(g, [a, [mm[0], mm[1] - 1.6, 's'], b, [mx + w * 0.4, mm[1] + 1.8, 's'], [mx - w * 0.4, mm[1] + 1.6, 's']], BLACK);
      shape(g, [[mx - w * 0.45, mm[1] + 9], [mx + w * 0.5, mm[1] + 8.5], [mx + w * 0.25, mm[1] + 12.5], [mx - w * 0.3, mm[1] + 12.5]], BLACK);
    }
    // a lifted corner goes into the cheek
    if (smirk > 0.3 || c < -2.5) wedge(g, b, [b[0] + 4, b[1] - 6], 2.4, 0.5, BLACK, 1.5);
    if (c < -2.5) wedge(g, a, [a[0] - 2, a[1] - 5], 2, 0.5, BLACK, -1);
  }

  // F: {e: vecExpr's numbers, gaze: [x, y], blink: [l, r] 0…1, browAdd}
  function drawFace(g, F, px) {
    const e = F.e, bl = F.blink || [0, 0], gz = F.gaze || [0, 0];
    g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, g.canvas.width, g.canvas.height);
    g.setTransform(px, 0, 0, px, -RECT[0] * px, -RECT[1] * px);
    const ey = D.eye_y, by = ey - 15 + D.brow.y, r = e.brow + (F.browAdd || 0), dn = e.cheeks * -1.5;
    if (cfg.under) cfg.under(g, e, { shape, wedge, r });
    const w = ek.w * 0.92, look = [e.look[0] + gz[0] * 2.2, e.look[1] + gz[1] * 1.6];
    [-1, 1].forEach((sg, i) => {
      const op = e.op * (1 - bl[i]) * (1 - (e.lid[i] || 0));
      eye(g, sg * 27, ey + dn, w, ek.h, sg, op, look);
      brow(g, [sg * 9, by + 1], [sg * (9 + 37 * D.brow.len), by - 4], D.brow.t, r, e.tilt);
    });
    mouth(g, 0, D.mouth.y, D.mouth.w * 0.95, e.mouth);
    if (cfg.over) cfg.over(g, e, { shape, wedge, r });
  }
  return { drawFace, EXPR, VISEME, exprVec, vecExpr, mixExpr, NH, phrases: cfg.phrases };
}
