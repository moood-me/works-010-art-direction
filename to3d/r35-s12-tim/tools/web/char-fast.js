// Тим of С12 (styles/s12-ink-watercolour/tools/tim.py): what is his own for the pen-and-wash renderer (figure.js) —
// the washes and their colours, his face as head_front draws it, his sheet's expressions, the pose of his figure.
import * as K from './pen-fast.js';
export const PACK = 'tim.json';
export const HAIR = '#e2862e', JUMPER = '#d9453a', SHORTS = '#4b6fae', SNEAKER = '#3d6fb6';

// parts.py's EXPR: his rest is the smirk; then the sheet's four
export const NAMES = ['smirk', 'joy', 'surprise', 'sad', 'anger'];
export const LABELS = { smirk: 'хитрит', joy: 'радость', surprise: 'удивление', sad: 'грусть', anger: 'гнев' };
export const EXPR = {
  smirk: { lift: 2, tilt: -2, lid: 0.1, look: [-1, 0], mouth: 'grin', eye: 1.0 },
  joy: { lift: 7, tilt: 0, lid: 0.0, look: [0, 0], mouth: 'laugh', eye: 0.9, squint: true, ms: 1.6, tilt_head: -10 },
  surprise: { lift: 17, tilt: 3, lid: 0.0, look: [0, 0], mouth: 'O', eye: 1.3, ms: 1.5, tilt_head: -4, extra: 'start' },
  sad: { lift: 3, tilt: 11, lid: 0.5, look: [0, 1.5], mouth: 'down', eye: 1.0, ms: 1.4, tilt_head: 12, extra: 'tear' },
  anger: { lift: -7, tilt: -12, lid: 0.3, look: [0, 0], mouth: 'shout', eye: 1.0, ms: 1.6, tilt_head: 6, extra: 'flush' },
};

// the washes, in painting order (tim.py's colours and strengths; dx, dy — how far off the line)
export const washes = G => [
  { groups: [G.skin], color: K.SKIN, op: 0.5, dx: 4, dy: 3 },
  { groups: [G.hair], color: HAIR, op: 0.7, dx: -2, dy: 1 },
  { groups: [G.jumper, G.stripe], color: JUMPER, op: 0.22, dx: 1, dy: 4 },
  { groups: [G.stripe], color: JUMPER, op: 0.72, dx: 2, dy: 1, angle: 0 },
  { groups: [G.shorts], color: SHORTS, op: 0.66, dx: 3, dy: 3 },
  { groups: [G.shoe], color: SNEAKER, op: 0.75, dx: 1, dy: 1, rough: 'S' },
  { groups: [G.sock], color: JUMPER, op: 0.7, dx: 0, dy: 0, rough: 'S' },
];
export const family = G => [[G.stripe, G.jumper], [G.sock, G.white]];
// which wash a point of the form is, where the mesh does not say: socks with a red band and sneakers by the legs'
// rest height; the jumper's stripes by the coordinate down the body and along the sleeves
export const glsl = G => `
  if (vB > -0.5) { if (vB < 0.040) gg = ${G.shoe}.0; else if (vB < 0.084) gg = ${G.white}.0; else if (vB < 0.098) gg = ${G.sock}.0; }
  if (vS > -0.2 && fract(vS) < 0.44) gg = ${G.stripe}.0;`;
export const FLAT = { skin: '#f0c09a', hair: '#e2862e', jumper: '#f3c4bf', stripe: '#d9453a', shorts: '#4b6fae', shoe: '#3d6fb6', white: '#f4efe6', sock: '#d9453a' };
export const lineW = { hair: 2.1 };
export const sharp = ['hair'];        // its silhouette is made of points: the pen keeps them
export const thinMin = 14, thinEvery = 2;
export const STAND = { out: 0.1, fwd: 0.02 };

// the face in head_front's units, its numbers from the live face (F.fp)
export function drawFace(d, F) {
  const e = F.fp, sq = e.squint, { faceMap, frameAt, useFrame } = F;
  d.map = faceMap;
  // which way the face looks in the picture (for the mouth's near corner)
  const c = faceMap(0, 20), l = faceMap(-30, 20), r = faceMap(30, 20);
  let side = -1;
  if (c && l && r) side = Math.hypot(l[0] - c[0], l[1] - c[1]) < Math.hypot(r[0] - c[0], r[1] - c[1]) ? -1 : 1;
  else if (!l && r) side = -1; else if (l && !r) side = 1;
  for (const [bx, sd] of [[-44, 31], [44, 32]]) {
    const f0 = frameAt(d, bx, 34, 0.5); if (!f0) continue;
    const f = frameAt(d, bx - side * 14 * (1 - Math.min(1, f0.r)), 34, 0.5) || f0;
    useFrame(d, f, bx, 34); K.blot(d, bx, 34, 15, K.BLUSH, 0.45, sd);
  }
  d.T = [[1, 0, 0, 1, 0, 0]]; d.map = faceMap;
  if (e.flush > 0) K.extra(d, { extra: 'flush' }, 0, 0, side < 0 ? -44 : 44, 34, -40, e.flush);
  for (const [x, y] of [[-22, 14], [-16, 20], [-28, 22], [16, 14], [22, 20], [28, 16]]) K.dotAt(d, x, y, 0.95 * d.lw, x * 7 + y);
  // eyes and brows: each in its own frame (foreshortened, but kept an eye); one brow cocked higher — he's up to something
  for (const [sx, sd, bl] of [[-32, 61, 4], [32, 62, -2]]) {
    const f0 = frameAt(d, sx, -2, 0.7); if (!f0) continue;
    const ex = sx - side * 9 * (1 - Math.min(1, f0.r)), f = frameAt(d, ex, -2, 0.7) || f0;
    // the far eye, as head34 draws it: smaller, and inside the face's contour (moved in the picture toward the near cheek)
    const far = Math.sign(sx) === side, t = 1 - Math.min(1, f.r), es = far ? 1 - 0.3 * t : 1 + 0.05 * t;
    if (far) { const k = -side * 12 * t; f.c = [f.c[0] + f.ax[0] * k, f.c[1] + f.ax[1] * k]; }
    useFrame(d, f, sx, -2);
    const turn = side * t * 1.1;
    K.eye(d, sx, -2, 1.2 * e.eye * es, [e.look[0] + turn, e.look[1]], e.lid, { side: sx < 0 ? -1 : 1, squint: sq, seed: sd });
    K.brow(d, sx, -26, 22 * es, e.lift + bl, e.tilt, { side: sx < 0 ? -1 : 1, w: 1.5, seed: sd + 2 });
    if (e.extra === 'tear' && e.extraK > 0.5 && (sx < 0) !== (side < 0)) K.extra(d, { extra: 'tear' }, sx, -2, 0, 0, -40, 1);
  }
  // the button nose from the front — the nostrils' curve and two dots — while the face looks at us; turned, the 3D's
  // contour draws it
  d.T = [[1, 0, 0, 1, 0, 0]]; d.map = faceMap;
  const dl = c && l ? Math.hypot(l[0] - c[0], l[1] - c[1]) : 0, dr = c && r ? Math.hypot(r[0] - c[0], r[1] - c[1]) : 0;
  const front = dl && dr ? Math.min(dl, dr) / Math.max(dl, dr) : 0;
  if (front > 0.7) {
    const al = 0.93 * Math.min(1, (front - 0.7) / 0.1);
    K.ink(d, [[-10, 22], [-4, 27], [4, 27], [10, 22]], { w: 1.5, start: 0.6, end: 0.6, seed: 41, alpha: al });
    K.ink(d, [[-2, 6], [-6, 16]], { w: 1.0, seed: 42, alpha: al });
    if (al > 0.6) { K.dotAt(d, -5, 24, 1.3 * d.lw, 44); K.dotAt(d, 5, 24, 1.3 * d.lw, 45); }
  }
  // the mouth: in its frame, moved toward the seen cheek as the face turns (the near corner stays inside the contour)
  const fm0 = frameAt(d, 0, 46, 0.5, true);
  if (fm0) {
    const mx = -side * 13 * (1 - Math.min(1, fm0.r)), fm = frameAt(d, mx, 46, 0.5);
    if (fm) {
      // turned, the mouth is drawn from the profile inward: moved in the picture toward the seen cheek
      const k = -side * 30 * (1 - Math.min(1, fm.r)); fm.c = [fm.c[0] + fm.ax[0] * k, fm.c[1] + fm.ax[1] * k];
      useFrame(d, fm, mx, 46);
      if (e.talk) K.mouth(d, mx, 46, 'talk', 1, { side, open: e.open, dw: e.dw, round: e.round, lips: false, seed: 43 });
      else if (e.mouth === 'grin') {      // his lopsided grin with a gap tooth (tim.py head_front), its high corner to the far side
        const g = ([x, y]) => [mx - side * x, y];
        K.wash(d, [[-22, 46], [0, 50], [24, 42], [14, 52], [-8, 54]].map(g), '#c4473f', 0.55, { rough: 'S', seed: 46 });
        K.ink(d, [[-30, 40], [-10, 48], [14, 47], [32, 34]].map(g), { w: 1.9, start: 0.6, end: 0.2, seed: 43 });
        K.ink(d, [[-22, 46], [-4, 54], [16, 50]].map(g), { w: 1.0, retrace: 0, seed: 47 });
        K.ink(d, [[-2, 48], [-2, 52]].map(g), { w: 0.9, retrace: 0, seed: 48 });
      } else K.mouth(d, mx, 46, e.mouth, e.ms, { side, lips: false, seed: 43 });
    }
  }
  const fs = frameAt(d, 0, -2);
  if (fs && e.extra === 'start' && e.extraK > 0.5) { useFrame(d, fs, 0, -2); K.extra(d, { extra: 'start' }, 0, -2, 0, 0, -44, 1); }
  d.T = [[1, 0, 0, 1, 0, 0]];
  d.map = null;
}

// the viewer's two views: the whole figure, the face close
export const VIEW = { far: { dist: 4.4, cy: 0.66 }, near: { dist: 1.5, up: 0.07 } };
