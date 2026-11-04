// Painted features: a face drawn on the skin (Г1's and Г3's drawings, experiments/heads-anime, heads-wrap) — eyes,
// brows, a mouth from its own lines or a grin, marks, blush, bags under the eyes, a nose's tint, a mask over the lower
// face. Drawn on any 2D canvas context, in head units (src/head/frame.js) seen from the front: the picture covers
// x, y ∈ [−SPAN, SPAN] around (0, CY); every vertex of the face takes its place there as its texture coordinate at the
// rest (src/head/features.js), so the drawing follows the skin wherever the mesh goes — in motion and in expressions.
//   paintFace(g, size, features, skin, state)   state: what the expressions ask of the drawing, each 0..1:
//                     close (the eyes shut), happy (the lower lids lifted by a smile; smiley eyes as arcs),
//                     smile (the mouth's corners up), open (the mouth parted), up, down (the brows)
// A feature drawn as volume (as: 'volume') is drawn here too: its relief takes the same picture (src/head/features.js).
import { lerp, clamp } from '../math.js';

export const SPAN = 1.15, CY = -0.4;

export function paintFace(g, size, features, skin, state = {}) {
  const FX = x => (0.5 + x / (2 * SPAN)) * size, FY = y => (0.5 - (y - CY) / (2 * SPAN)) * size, KS = size / (2 * SPAN);
  const P = { g, FX, FY, KS };
  g.fillStyle = skin; g.fillRect(0, 0, size, size);
  const by = kind => features.filter(f => f.kind === kind);
  for (const f of by('blush')) for (const s of [-1, 1]) radial(P, s * (f.x ?? 0.52), f.y ?? -0.56, (f.r ?? 0.24), `rgba(240,120,120,${0.45 * f.amount})`, 'rgba(240,120,120,0)');
  for (const f of by('eye')) if (f.bags) for (const s of [-1, 1]) radial(P, s * f.x, f.y - 0.12, 0.3, f.bags + 'aa', f.bags + '00');
  for (const f of by('tint')) radial(P, f.x ?? 0, f.y ?? -0.64, f.r ?? 0.16, f.color, f.color + '00');
  for (const f of by('mask')) drawMask(P, f);
  for (const f of by('eye')) for (const s of [-1, 1]) drawEye(P, f, s, state);
  // (a brow as volume is a relief: it moves with the skin's own morph, its drawing stays where the relief is)
  for (const f of by('brow')) for (const s of [-1, 1]) drawBrow(P, f, s, f.as === 'volume' ? { ...state, up: 0, down: 0 } : state);
  for (const f of by('marks')) drawMarks(P, f.lines);
  for (const f of by('mouth')) drawMouth(P, f, state);
}

function radial({ g, FX, FY, KS }, x, y, r, a, b) {
  const gr = g.createRadialGradient(FX(x), FY(y), 0, FX(x), FY(y), r * KS); gr.addColorStop(0, a); gr.addColorStop(1, b); g.fillStyle = gr; g.fillRect(0, 0, g.canvas.width, g.canvas.height);
}

function drawEye({ g, FX, FY, KS }, E, s, st) {
  const close = clamp(st.close ?? 0, 0, 1), happy = (st.happy ?? 0) > 0.5;
  const w = E.w * KS, h = E.h * KS, lw = E.lashW * KS;
  g.save(); g.translate(FX(s * E.x), FY(E.y)); g.scale(s, 1); g.rotate(-(E.tilt || 0));
  if (close >= 0.98 || (happy && E.smiley)) {
    // a closed eye: one lash curve; happy — an upturned arc
    g.strokeStyle = E.lash; g.lineCap = 'round'; g.lineWidth = lw * 0.8; g.beginPath();
    if (happy && close < 0.98) { g.moveTo(-w * 0.55, h * 0.1); g.quadraticCurveTo(0, -h * 0.9, w * 0.55, h * 0.1); }
    else { g.moveTo(-w * 0.55, -h * 0.05); g.quadraticCurveTo(0, h * 0.35, w * 0.55, -h * 0.05); }
    g.stroke(); g.restore(); return;
  }
  if (E.smiley) { g.strokeStyle = E.lash; g.lineWidth = lw; g.lineCap = 'round'; g.beginPath(); g.moveTo(-w * 0.5, 0); g.quadraticCurveTo(0, -h * 1.2 * (1 - close), w * 0.5, 0); g.stroke(); if (close < 0.5) { g.fillStyle = E.iris[0]; g.beginPath(); g.ellipse(w * 0.02, -h * 0.05, w * 0.16, h * 0.42 * (1 - 2 * close), 0, 0, 7); g.fill(); } g.restore(); return; }
  const look = (E.look || 0) * w * 0.28;
  // the lids: closing, the upper comes down to the lower (its height shrinks, the lash line follows it)
  const lidTop = h * 0.55 * (1 - close) - h * 0.5 * close * 0.9, lidBot = h * 0.5;
  const lowLid = u => lidBot * (0.98 - 0.32 * (1 - u * u) ** 1.5) + h * 0.04 * u;
  g.save(); if (happy) { g.beginPath(); g.moveTo(-w, -h * 2); g.lineTo(w, -h * 2); for (let k = 0; k <= 20; k++) { const u = 1 - k / 10; g.lineTo(u * w * 0.6, lowLid(u)); } g.closePath(); g.clip(); }
  const white = () => {
    g.beginPath();
    if (E.sharp) { g.moveTo(-w * 0.5, h * 0.1); g.quadraticCurveTo(-w * 0.1, -lidTop * 1.25, w * 0.55, -lidTop * 0.35); g.quadraticCurveTo(w * 0.3, lidBot * 0.9, -w * 0.5, h * 0.1); }
    else if (E.round) g.ellipse(0, h * 0.02 + (h * 0.55 - lidTop) * 0.5, w * 0.5, Math.max(0.5, (lidTop + lidBot) * 0.52), 0, 0, 7);
    else { g.moveTo(-w * 0.5, 0); g.bezierCurveTo(-w * 0.35, -lidTop * 1.15, w * 0.35, -lidTop * 1.2, w * 0.52, -lidTop * 0.25); g.bezierCurveTo(w * 0.45, lidBot * 0.9, -w * 0.35, lidBot * 1.05, -w * 0.5, 0); }
    g.closePath();
  };
  if (lidTop + lidBot > 0.5) {
    white(); g.fillStyle = '#fbfbff'; g.fill(); g.save(); g.clip();
    // the iris: tall, dark at the top, light below
    const ix = look * s, iw = w * (E.ringed ? 0.24 : 0.33) * (E.irisScale || 1), ih = h * (E.ringed ? 0.42 : 0.62) * (E.irisScale || 1);
    const gr = g.createLinearGradient(0, -ih, 0, ih); gr.addColorStop(0, E.iris[0]); gr.addColorStop(1, E.iris[1]);
    g.fillStyle = gr; g.beginPath(); g.ellipse(ix, h * 0.05, iw, ih, 0, 0, 7); g.fill();
    if (E.ringed) { g.strokeStyle = '#ffffff'; g.lineWidth = iw * 0.28; g.beginPath(); g.ellipse(ix, h * 0.05, iw * 0.62, ih * 0.62, 0, 0, 7); g.stroke(); g.fillStyle = '#1a1220'; g.beginPath(); g.ellipse(ix, h * 0.05, iw * 0.28, ih * 0.28, 0, 0, 7); g.fill(); }
    else { g.fillStyle = 'rgba(10,10,25,0.85)'; g.beginPath(); g.ellipse(ix, h * 0.0, iw * 0.42, ih * 0.5, 0, 0, 7); g.fill(); g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(-w, -h, 2 * w, Math.max(0, lidTop) * 0.55 + (h - Math.max(0, lidTop))); }
    for (let k = 0; k < (E.glints || 0); k++) { g.fillStyle = k ? 'rgba(255,255,255,0.75)' : '#ffffff'; g.beginPath(); const gx = ix + iw * (k === 0 ? -0.35 : k === 1 ? 0.35 : -0.05), gy = h * (k === 0 ? -0.22 : k === 1 ? 0.3 : 0.42), gs = iw * (k === 0 ? 0.3 : 0.16); g.ellipse(gx, gy, gs, gs * 1.1, 0, 0, 7); g.fill(); }
    g.restore();
  }
  g.restore();
  if (happy) { g.strokeStyle = E.lash; g.globalAlpha = 0.5; g.lineWidth = lw * 0.3; g.lineCap = 'round'; g.beginPath(); for (let k = 0; k <= 16; k++) { const u = -0.45 + k / 16 * 1.05; const X = u * w * 0.6, Y = lowLid(u); k ? g.lineTo(X, Y) : g.moveTo(X, Y); } g.stroke(); g.globalAlpha = 1; }
  // the upper lash line, thick, with a wing at the outer corner
  g.fillStyle = E.lash; g.beginPath();
  if (E.sharp) { g.moveTo(-w * 0.52, h * 0.12); g.quadraticCurveTo(-w * 0.1, -lidTop * 1.3, w * 0.55, -lidTop * 0.38); g.lineTo(w * (0.6 + E.wing), -lidTop * (0.5 + E.wing)); g.quadraticCurveTo(-w * 0.1, -lidTop * 1.3 - lw * 1.6, -w * 0.55, h * 0.02); }
  else { g.moveTo(-w * 0.53, h * 0.02); g.bezierCurveTo(-w * 0.35, -lidTop * 1.2, w * 0.35, -lidTop * 1.25, w * 0.53, -lidTop * 0.28); g.lineTo(w * (0.56 + E.wing), -lidTop * (0.4 + E.wing * 1.6)); g.bezierCurveTo(w * 0.3, -lidTop * 1.25 - lw * 1.3, -w * 0.35, -lidTop * 1.2 - lw * 0.9, -w * 0.56, -h * 0.02); }
  g.closePath(); g.fill();
  const open = 1 - close;
  if (E.lashes && open > 0.3) for (let k = 0; k < E.lashes; k++) { g.strokeStyle = E.lash; g.lineWidth = lw * 0.35; g.lineCap = 'round'; const t = 0.55 + k * 0.15; g.beginPath(); g.moveTo(w * (t - 0.3), -lidTop * (1.0 - k * 0.2)); g.lineTo(w * (t - 0.2), -lidTop * (1.45 - k * 0.15) - (1 - open) * h * 0.2); g.stroke(); }
  if (E.crease) { g.strokeStyle = E.lash; g.globalAlpha = 0.55; g.lineWidth = lw * 0.25; const c = h * 0.55; g.beginPath(); g.moveTo(-w * 0.2, -c * 1.45); g.quadraticCurveTo(w * 0.2, -c * 1.75, w * 0.52, -c * 1.0); g.stroke(); g.globalAlpha = 1; }
  if (E.lower && !happy && open > 0.3) { g.strokeStyle = E.lash; g.globalAlpha = 0.6; g.lineWidth = lw * 0.35; g.beginPath(); g.moveTo(w * 0.05, lidBot * 0.95); g.quadraticCurveTo(w * 0.35, lidBot * 0.85, w * (0.25 + 0.3 * E.lower), lidBot * 0.6); g.stroke(); g.globalAlpha = 1; }
  if (E.ringed && !happy) { g.strokeStyle = E.lash; g.lineWidth = lw * 0.6; g.beginPath(); g.moveTo(-w * 0.48, h * 0.1); g.bezierCurveTo(-w * 0.3, lidBot * 1.2, w * 0.3, lidBot * 1.2, w * 0.5, -h * 0.02); g.stroke(); }
  g.restore();
}

// a brow: thick at its head (inner end), tapering to its tail, along an arc with its peak where the drawing has it
export function browLines(B, s, st = {}) {
  const upW = clamp(st.up ?? 0, 0, 1), dnW = clamp(st.down ?? 0, 0, 1);
  const up = 0.08 * upW - 0.05 * dnW, tilt = -0.08 * dnW + 0.04 * upW, n = 24, top = [], bot = [], pk = B.peak ?? 0.5;
  for (let k = 0; k <= n; k++) {
    const t = k / n, x = lerp(B.x0, B.x1, t), arc = B.arch * Math.sin(Math.PI * Math.min(1, t / (2 * pk))) * (t < pk ? 1 : 1 - 0.5 * ((t - pk) / (1 - pk)) ** 2);
    const y = lerp(B.y0, B.y1, t) + arc + up + tilt * (1 - t), w = lerp(B.w0, B.w1, t ** 0.8) * (t > 0.9 ? (1 - t) * 10 : 1) + 0.002;
    top.push([s * x, y + w * 0.5]); bot.push([s * x, y - w * 0.5]);
  }
  return { top, bot };
}
function drawBrow({ g, FX, FY }, B, s, st) {
  const { top, bot } = browLines(B, s, st);
  g.fillStyle = B.color; g.beginPath(); top.forEach(([x, y], i) => i ? g.lineTo(FX(x), FY(y)) : g.moveTo(FX(x), FY(y))); for (let k = bot.length - 1; k >= 0; k--) g.lineTo(FX(bot[k][0]), FY(bot[k][1])); g.closePath(); g.fill();
}
function drawMarks({ g, FX, FY, KS }, lines = []) {
  for (const m of lines) for (const s of m.mirror ? [-1, 1] : [1]) {
    g.strokeStyle = m.color; g.globalAlpha = m.alpha ?? 0.6; g.lineWidth = (m.w || 0.01) * KS; g.lineCap = 'round'; g.beginPath(); const pts = m.pts;
    g.moveTo(FX(s * pts[0][0]), FY(pts[0][1]));
    if (pts.length === 3) g.quadraticCurveTo(FX(s * pts[1][0]), FY(pts[1][1]), FX(s * pts[2][0]), FY(pts[2][1])); else for (const p of pts.slice(1)) g.lineTo(FX(s * p[0]), FY(p[1]));
    g.stroke(); g.globalAlpha = 1;
  }
}
function drawMask({ g, FX, FY, KS }, Mk) {
  const T = Mk.top ?? -0.48;
  // the lower face under a plated mask with a drawn jaw of teeth
  g.fillStyle = Mk.color; g.beginPath(); g.moveTo(FX(-1.2), FY(T)); g.quadraticCurveTo(FX(0), FY(T + 0.16), FX(1.2), FY(T)); g.lineTo(FX(1.2), FY(-1.6)); g.lineTo(FX(-1.2), FY(-1.6)); g.closePath(); g.fill();
  g.strokeStyle = Mk.dark; g.lineWidth = 0.025 * KS; g.beginPath(); g.moveTo(FX(-1.2), FY(T)); g.quadraticCurveTo(FX(0), FY(T + 0.16), FX(1.2), FY(T)); g.stroke();
  g.lineWidth = 0.02 * KS; g.beginPath(); const y0 = -0.8; g.moveTo(FX(-0.55), FY(y0));
  for (let k = 0; k <= 10; k++) { const x = -0.55 + k * 0.11; g.lineTo(FX(x), FY(y0 + (k % 2 ? 0.07 : -0.07))); } g.stroke();
  for (let k = 0; k < 9; k++) { const x = -0.44 + k * 0.11; g.beginPath(); g.moveTo(FX(x), FY(y0 - 0.12)); g.lineTo(FX(x), FY(y0 + 0.12)); g.stroke(); }
  g.fillStyle = Mk.dark; for (const s of [-1, 1]) { g.beginPath(); g.ellipse(FX(s * 0.7), FY(-0.62), 0.04 * KS, 0.04 * KS, 0, 0, 7); g.fill(); }
}

// a mouth's own lines (in head units): the parting line, the upper lip's top with its bow, the lower lip's bottom
export function mouthLines(M, st = {}) {
  const sm = (M.smile ?? 0.012) * clamp(st.smile ?? 0, 0, 1), w = M.w / 2 * (1 + 0.08 * clamp(st.smile ?? 0, 0, 1));
  const cL = (M.cL ?? M.corners ?? 0) + sm, cR = (M.cR ?? M.corners ?? 0) + sm, sag = M.sag ?? 0.004, n = 24;
  const line = t => { const x = lerp(-w, w, t); return [x, M.y + lerp(cL, cR, t) - sag * Math.sin(Math.PI * t) - sm * 0.6 * Math.sin(Math.PI * t)]; };
  const path = f => Array.from({ length: n + 1 }, (_, k) => f(k / n));
  const L = path(line);
  const upper = path(t => { const [x, y] = line(t), b = (M.bow ?? 0) * Math.exp(-(((t - 0.5) / 0.09) ** 2)); return [x, y + (M.upper ?? 0) * Math.sin(Math.PI * t) ** 0.6 - b + (M.open ? 0.004 : 0)]; });
  const lower = path(t => { const [x, y] = line(t); return [x * 0.92, y - (M.open || 0) * Math.sin(Math.PI * t) - (M.lower ?? 0) * Math.sin(Math.PI * t) ** 0.7]; });
  const inner = path(t => { const [x, y] = line(t); return [x * 0.9, y - (M.open || 0) * Math.sin(Math.PI * t)]; });
  return { line: L, upper, lower, inner, sm };
}
function drawMouth(P, M, st) {
  const { g, FX, FY, KS } = P;
  if (M.type === 'none') return;
  const poly = pts => pts.forEach(([x, y], i) => i ? g.lineTo(FX(x), FY(y)) : g.moveTo(FX(x), FY(y)));
  const fill = (A, B, color) => { g.fillStyle = color; g.beginPath(); poly(A); for (let k = B.length - 1; k >= 0; k--) g.lineTo(FX(B[k][0]), FY(B[k][1])); g.closePath(); g.fill(); };
  const open = clamp(st.open ?? 0, 0, 1);
  if (M.type === 'grin') return drawGrin(P, M, st);
  const { line: L, upper, lower, inner, sm } = mouthLines(M, st);
  // the inside: where the lips part (drawn, or opened by the jaw — the skin there stretches over the opening, so its
  // picture is the mouth's dark inside)
  if (M.open || sm || open) fill(L, inner.map(([x, y], k) => [x, y - 0.006 * open * Math.sin(Math.PI * k / (inner.length - 1))]), M.inside ?? '#6a2a28');
  if (M.upper) fill(upper, L, M.lip);
  if (M.lower) fill(inner, lower, M.lip);
  g.strokeStyle = open > 0.3 ? (M.inside ?? '#4a1820') : (M.line || '#7a3a36'); g.lineCap = 'round'; g.lineJoin = 'round';
  for (let k = 0; k < L.length - 1; k++) { const t = k / (L.length - 1); g.lineWidth = (M.lineW ?? 0.014) * KS * (0.35 + 0.65 * Math.sin(Math.PI * (t * 0.9 + 0.05))) * (1 + open); g.beginPath(); g.moveTo(FX(L[k][0]), FY(L[k][1])); g.lineTo(FX(L[k + 1][0]), FY(L[k + 1][1])); g.stroke(); }
  if (sm && M.smileHooks) for (const k of [0, L.length - 1]) { const [x, y] = L[k], s = k ? 1 : -1; g.lineWidth = (M.lineW ?? 0.014) * 0.7 * KS; g.beginPath(); g.moveTo(FX(x - s * 0.012), FY(y + 0.016)); g.quadraticCurveTo(FX(x + s * 0.012), FY(y + 0.004), FX(x + s * 0.004), FY(y - 0.016)); g.stroke(); }
  if (M.lowerLine) { g.strokeStyle = M.line || '#7a3a36'; g.lineWidth = 0.01 * KS; g.globalAlpha = 0.5; g.beginPath(); const y = M.y - (M.lower || 0) - 0.035, w = M.w / 2; g.moveTo(FX(-w * M.lowerLine), FY(y)); g.quadraticCurveTo(FX(0), FY(y - 0.008), FX(w * M.lowerLine), FY(y)); g.stroke(); g.globalAlpha = 1; }
  if (M.dimple && !sm) { g.strokeStyle = M.line || '#7a3a36'; g.lineWidth = 0.009 * KS; g.beginPath(); const [x, y] = L[L.length - 1]; g.moveTo(FX(x + 0.005), FY(y + 0.02)); g.quadraticCurveTo(FX(x + 0.025), FY(y), FX(x + 0.008), FY(y - 0.022)); g.stroke(); }
}
// a wide grin: a dark crescent, the upper teeth along its top
function drawGrin({ g, FX, FY, KS }, M, st) {
  const smile = clamp(st.smile ?? 0, 0, 1), ww = M.w * (1 + 0.08 * smile), cr = (M.crooked || 0) * ww, lift = 0.05 * smile, n = 28;
  const qb = (a, c, b, t) => [0, 1].map(k => (1 - t) * (1 - t) * a[k] + 2 * (1 - t) * t * c[k] + t * t * b[k]);
  const A = [-ww, M.y + 0.12 * ww - cr + lift], B = [ww, M.y + 0.12 * ww + cr + lift], cu = [0, M.y - 0.25 * ww], cl = [0, M.y - 0.9 * ww];
  const top = [], bot = []; for (let k = 0; k <= n; k++) { const t = k / n; top.push(qb(A, cu, B, t)); bot.push(qb(A, cl, B, t)); }
  const shape = () => { g.beginPath(); top.forEach(([x, y], i) => i ? g.lineTo(FX(x), FY(y)) : g.moveTo(FX(x), FY(y))); for (let k = n; k >= 0; k--) g.lineTo(FX(bot[k][0]), FY(bot[k][1])); g.closePath(); };
  shape(); g.fillStyle = '#5a1e1e'; g.fill();
  g.save(); shape(); g.clip();
  const teethH = 0.05 * ww / 0.46;
  g.fillStyle = '#fbf6ef'; g.beginPath(); top.forEach(([x, y], i) => i ? g.lineTo(FX(x), FY(y + 0.01)) : g.moveTo(FX(x), FY(y + 0.01)));
  for (let k = n; k >= 0; k--) { const t = k / n, d = top[k][1] - bot[k][1]; g.lineTo(FX(top[k][0]), FY(top[k][1] - Math.min(d * 0.3, teethH) * Math.sin(Math.PI * t) ** 0.3)); } g.closePath(); g.fill();
  g.restore();
  g.strokeStyle = '#3a1210'; g.lineJoin = 'round'; g.lineCap = 'round'; g.lineWidth = 0.012 * KS; shape(); g.stroke();
}
