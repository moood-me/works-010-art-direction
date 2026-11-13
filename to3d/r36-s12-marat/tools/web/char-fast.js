// Марат of С12 (styles/s12-ink-watercolour/tools/marat.py): what is his own for the pen-and-wash renderer (figure.js) —
// the washes and their colours, his face as head_front draws it (the grin with teeth and a tongue, the moustache, the
// thick brows), his sheet's expressions, the jaw that drops with the laugh.
import * as K from './pen-fast.js';
export const PACK = 'marat.json';
export const SKIN_M = '#e9ac80', HAIR = '#2a211e', APRON = '#d76a36', SHADE = '#c9bba6', TROUS = '#59606e', CLOG = '#4a3a34';

// parts.py's EXPR: his rest is a wide smile ('merry'); joy is the laugh with the whole face
export const NAMES = ['merry', 'joy', 'surprise', 'sad', 'anger'];
export const LABELS = { merry: 'улыбается', joy: 'хохочет', surprise: 'удивление', sad: 'грусть', anger: 'гнев' };
export const EXPR = {
  merry: { lift: 5, tilt: 0, lid: 0.15, look: [0, 0], mouth: 'smile', eye: 0.95, op: 0.3 },
  joy: { lift: 7, tilt: 0, lid: 0.0, look: [0, 0], mouth: 'laugh', eye: 0.9, squint: true, ms: 1.6, tilt_head: -10, op: 1.0 },
  surprise: { lift: 17, tilt: 3, lid: 0.0, look: [0, 0], mouth: 'O', eye: 1.3, ms: 1.5, tilt_head: -4, extra: 'start', op: 0.35 },
  sad: { lift: 3, tilt: 11, lid: 0.5, look: [0, 1.5], mouth: 'down', eye: 1.0, ms: 1.4, tilt_head: 12, extra: 'tear', op: 0 },
  anger: { lift: -7, tilt: -12, lid: 0.3, look: [0, 0], mouth: 'shout', eye: 1.0, ms: 1.6, tilt_head: 6, extra: 'flush', op: 0.45 },
};

// the washes, in painting order (marat.py's colours and strengths). Dark hair takes two layers. The white jacket is
// bare paper: only its shaded side gets a warm grey
export const washes = G => [
  { groups: [G.skin], color: SKIN_M, op: 0.5, dx: 4, dy: 3 },
  { groups: [G.jacket, G.towel], shade: true, shrink: 2, color: SHADE, op: 0.34, dx: -2, dy: 2 },
  { groups: [G.apron], color: APRON, op: 0.7, dx: 3, dy: 3 },
  { groups: [G.tstripe], color: APRON, op: 0.75, dx: 0, dy: 0, rough: 'S' },
  { groups: [G.trousers], color: TROUS, op: 0.56, dx: 2, dy: 2 },
  { groups: [G.shoe], color: CLOG, op: 0.75, dx: 1, dy: 1, rough: 'S' },
  { groups: [G.hair], color: HAIR, op: 0.85, dx: -2, dy: 0 },
  { groups: [G.hair], color: HAIR, op: 0.5, dx: -2, dy: 0, angle: 20 },
];
export const family = G => [[G.tstripe, G.towel]];
// the towel's two stripes near its end, by the coordinate along it
export const glsl = G => `
  if (abs(gg - ${G.towel}.0) < 0.5 && ((vS > 0.05 && vS < 0.11) || (vS > 0.15 && vS < 0.19))) gg = ${G.tstripe}.0;`;
export const FLAT = { skin: '#e9b48c', hair: '#2a211e', jacket: '#f6f1e6', apron: '#d76a36', trousers: '#59606e', shoe: '#4a3a34', towel: '#efe8da', tstripe: '#d76a36' };
export const lineW = { hair: 1.8, beard: 1.8, jacket: 2.1, apron: 1.7, sleeveLeft: 2.0, sleeveRight: 2.0 };
export const thinMin = 12, thinEvery = 2;
export const STAND = { out: 0.2, fwd: 0.04 };
export const VIEW = { far: { dist: 6.6, cy: 0.98 }, near: { dist: 2.3, up: 0.06 } };

// how far the jaw is down: marat.py's OPEN for his two mouths, the other mouths a little, speech by its syllables
function jawOpen(e) {
  let s = 0, z = 0; for (const n of NAMES) { s += (e.w[n] || 0) * EXPR[n].op; z += e.w[n] || 0; }
  let op = s / (z || 1);
  if (e.talk) op = Math.max(0.12, Math.min(1, 0.15 + e.open * 1.1));
  return op;
}
export function poseHook(pose, e, T) {
  const ax = T.qRot(T.getQ(pose.Q, T.I.Head), [1, 0, 0]);
  T.turnUnder(pose, T.sk, T.I.Jaw, T.qAxisAngle(ax, 0.2 * jawOpen(e)));
}

const dark = (d, poly, op, o) => { K.wash(d, poly, HAIR, op, o); K.wash(d, poly, HAIR, op * 0.6, { ...o, seed: (o.seed || 1) + 1 }); };
// marat.py's grin(): teeth are paper left white under the upper lip, the dark of the mouth below them, a tongue when
// he laughs. xa, xb: the corners; ups / los: the lips' lines at five points
function grin(d, xa, xb, y, op, ups, los) {
  const T = [0, 0.2, 0.52, 0.84, 1], X = T.map(t => xa + (xb - xa) * t), drop = 26 * op;
  const up = X.map((x, i) => [x, y + ups[i]]);
  const lo = X.map((x, i) => [x, y + los[i] + drop * Math.sin(Math.PI * T[i]) ** 0.7]);
  const th = 8 + 3 * op;
  const tb = X.map((x, i) => [x, up[i][1] + th * Math.sin(Math.PI * T[i]) ** 0.6]);
  if (op > 0.6) {
    const tt = [1, 2, 3].map(i => [X[i], lo[i][1] - 11 * Math.sin(Math.PI * T[i])]);
    K.wash(d, [...tb.slice(1, 4), ...tt.slice().reverse()], '#7c2424', 0.85, { rough: 'S', seed: 51 });
    K.wash(d, [tt[0], [X[2], tt[1][1] - 4], tt[2], lo[3], lo[2], lo[1]], '#e2716c', 0.7, { rough: 'S', seed: 52 });
    K.ink(d, [tt[0], [X[2], tt[1][1] - 4], tt[2]], { w: 1.0, start: 0.4, end: 0.3, retrace: 0, seed: 53 });
    K.ink(d, [[X[2], tt[1][1] - 2], [X[2] + 1, lo[2][1] - 4]], { w: 0.7, retrace: 0, seed: 54 });
  } else K.wash(d, [...tb.slice(1, 4), lo[3], lo[2], lo[1]], '#7c2424', 0.85, { rough: 'S', seed: 51 });
  K.paper(d, [...up, ...tb.slice().reverse().slice(1, 4)]);
  K.ink(d, up, { w: 1.9, start: 0.5, end: 0.3, seed: 55 });
  K.ink(d, [up[0], ...lo.slice(1, 4), up[4]], { w: 2.1, start: 0.4, end: 0.3, seed: 56 });
  K.ink(d, tb.slice(1, 4), { w: 0.8, start: 0.4, end: 0.4, jit: 0.3, retrace: 0, seed: 57 });
  for (const i of [1, 2, 3]) { const x = xa + (xb - xa) * (0.2 + 0.16 * i); K.ink(d, [[x, y + ups[2] + 1], [x, y + ups[2] + th - 2]], { w: 0.6, jit: 0.2, retrace: 0, alpha: 0.7, seed: 58 + i }); }
}
function thickBrow(d, x, y, length, e, side, seed) {
  K.brow(d, x, y, length, e.lift, e.tilt, { side, w: 2.9, arch: 5, seed });
  K.brow(d, x, y + 3, length * 0.8, e.lift, e.tilt, { side, w: 2.0, arch: 4, seed: seed + 5 });
}

// the face in head_front's units, its numbers from the live face (F.fp)
export function drawFace(d, F) {
  const e = F.fp, sq = e.squint, { faceMap, frameAt, useFrame } = F;
  const op = jawOpen(e), open = e.talk || e.mouth === 'smile' || e.mouth === 'laugh';
  d.map = faceMap;
  const c = faceMap(0, 20), l = faceMap(-30, 20), r = faceMap(30, 20);
  let side = -1;
  if (c && l && r) side = Math.hypot(l[0] - c[0], l[1] - c[1]) < Math.hypot(r[0] - c[0], r[1] - c[1]) ? -1 : 1;
  else if (!l && r) side = -1; else if (l && !r) side = 1;
  for (const [bx, by, br, bo, sd] of [[-46, 22, 19, 0.48, 31], [46, 22, 19, 0.48, 32], [0, 30, 12, 0.35, 33]]) {
    const f0 = frameAt(d, bx, by, 0.5); if (!f0) continue;
    const f = frameAt(d, bx - side * 14 * (1 - Math.min(1, f0.r)), by, 0.5) || f0;
    useFrame(d, f, bx, by); K.blot(d, bx, by, br, K.BLUSH, bo, sd);
  }
  d.T = [[1, 0, 0, 1, 0, 0]]; d.map = faceMap;
  if (e.flush > 0) K.extra(d, { extra: 'flush' }, 0, 0, side < 0 ? -46 : 46, 22, -40, e.flush);
  const fc0 = frameAt(d, 0, 10, 0, true), tc = fc0 ? 1 - Math.min(1, fc0.r) : 1;      // how far the face is turned from us
  // eyes that narrow with the smile, crow's feet, thick brows
  for (const [sx, sd] of [[-36, 75], [36, 76]]) {
    const f0 = frameAt(d, sx, -4, 0.7); if (!f0) continue;
    const ex = sx - side * 9 * (1 - Math.min(1, f0.r)), f = frameAt(d, ex, -4, 0.7) || f0;
    const far = Math.sign(sx) === side, t = 1 - Math.min(1, f.r), es = far ? 1 - 0.25 * t : 1 + 0.05 * t, sg = sx < 0 ? -1 : 1;
    const tn = far ? 0 : Math.max(0, tc - 0.55) / 0.45;        // the near eye, as the face nears the profile
    { const k = -side * (far ? 20 * t : 14 * tn); f.c = [f.c[0] + f.ax[0] * k, f.c[1] + f.ax[1] * k]; }      // turned: the features keep inside the contour
    useFrame(d, f, sx, -4);
    K.eye(d, sx, -4, 1.15 * e.eye * es, [e.look[0] + side * t * 1.1, e.look[1]], e.lid, { side: sg, squint: sq, seed: sd });
    if (open && !e.talk) {
      K.ink(d, [[sx + sg * 14, 13], [sx, 9], [sx - sg * 14, 13]], { w: 1.0, start: 0.3, end: 0.3, retrace: 0, seed: sd + 10 });       // the cheek pushes the lower lid up
      if (t < 0.3) { K.ink(d, [[sx + sg * 17, -8], [sx + sg * 27, -12]], { w: 0.8, retrace: 0, seed: sd + 12 }); K.ink(d, [[sx + sg * 18, -2], [sx + sg * 28, -2]], { w: 0.8, retrace: 0, seed: sd + 14 }); }
    }
    thickBrow(d, sx + sg * 10 * tn, -30, 34 * es * (1 - 0.45 * tn), e, sg, sd + 2);
    if (e.extra === 'tear' && e.extraK > 0.5 && (sx < 0) !== (side < 0)) K.extra(d, { extra: 'tear' }, sx, -4, 0, 0, -40, 1);
  }
  // the broad nose from the front — the round tip and two wings — while the face looks at us; turned, the 3D's contour
  d.T = [[1, 0, 0, 1, 0, 0]]; d.map = faceMap;
  const dl = c && l ? Math.hypot(l[0] - c[0], l[1] - c[1]) : 0, dr = c && r ? Math.hypot(r[0] - c[0], r[1] - c[1]) : 0;
  const front = dl && dr ? Math.min(dl, dr) / Math.max(dl, dr) : 0;
  if (front > 0.7) {
    const al = 0.93 * Math.min(1, (front - 0.7) / 0.1);
    K.ink(d, [[-5, -6], [-9, 16]], { w: 1.1, start: 0.3, end: 0.2, seed: 41, alpha: al });
    K.ink(d, [[-22, 24], [-21, 36], [-9, 39], [0, 43], [10, 39], [21, 36], [22, 24]], { w: 1.9, start: 0.5, end: 0.5, seed: 42, alpha: al });
  }
  // the moustache and the mouth in the gap the beard leaves: in one frame, moved toward the seen cheek as the face turns
  const fm0 = frameAt(d, 0, 58, 0.5, true);
  if (fm0) {
    const t = 1 - Math.min(1, fm0.r), mx = -side * 13 * t, fm = frameAt(d, mx, 58, 0.5);
    if (fm) {
      const k = -side * 34 * t; fm.c = [fm.c[0] + fm.ax[0] * k, fm.c[1] + fm.ax[1] * k];
      useFrame(d, fm, 0, 58);
      const g = ([x, y]) => [-side * x, y];
      if (e.talk || open) grin(d, side * 42, -side * 42, 62, op, [-10, 0, 3, 0, -10], [-8, 8, 13, 8, -8]);
      else K.mouth(d, 0, 64, e.mouth, e.ms * 1.15, { side, lips: false, seed: 43 });
      dark(d, [[-50, 50], [-24, 44], [0, 48], [24, 44], [50, 50], [40, 60], [0, 62], [-40, 60]].map(g), 0.7, { rough: 'S', seed: 61 });
      K.ink(d, [[-48, 51], [-24, 44], [0, 49], [24, 44], [48, 51]].map(g), { w: 1.3, start: 0.3, end: 0.3, seed: 63 });
    }
  }
  const fs = frameAt(d, 0, -4);
  if (fs && e.extra === 'start' && e.extraK > 0.5) { useFrame(d, fs, 0, -4); K.extra(d, { extra: 'start' }, 0, -4, 0, 0, -52, 1); }
  d.T = [[1, 0, 0, 1, 0, 0]];
  d.map = null;
}
