// Аня of С13 (styles/s13-ukiyo-e/tools/anya.py): what is her own for the print renderer (print.js) — the colour blocks
// and their patterns, her face as parts.head draws it, her sheet's expressions, her sheet (ground, name).
import * as K from './kit.js';
export const PACK = 'anya.json';
export const HAIR = '#2c1a17', SHEEN = '#b98a62', CARD = '#d8a23a', DRESS = '#6f8fa8', SHOE = '#8a3b2c';
export const SHEET = { ground: '#e2d2a2', top: '#c9a35a', bottom: '#b9a67c', name: 'Аня' };

// parts.P(...) of anya.py: the long oval and the narrow eye of the shin-hanga beauties
const Pn = K.P({ long: 1.08, eye: { w: 42, h: 8.6, iris: 7.6, lid: 3.8, slant: -1.5, lower: 0.4, lash: 1.0, color: '#3a2a1e', crease: 0.35 },
  brow: { kind: 'arc', w: 2.6, len: 42, arch: 6, y: -28 }, nose: { kind: 'soft', s: 0.82 }, mouth: { w: 23, y: 62, full: 1.15 }, blush: ['#e79a86', 0.26] });
const MY = Pn.mouth.y * Pn.long;

// parts.EXPR in the live face's words: eye — how far it is open (0: the arc of a laugh), look in eye units
export const NAMES = ['dream', 'joy', 'surprise', 'sad', 'anger'];
export const LABELS = { dream: 'мечтает', joy: 'радость', surprise: 'удивление', sad: 'грусть', anger: 'злость' };
export const EXPR = {
  dream: { lift: 1, tilt: 1, lid: 0, eye: 0.8, look: [-0.6, -0.5], mouth: 'smile' },
  joy: { lift: 3, tilt: 0, lid: 0, eye: 0, squint: true, look: [0, 0], mouth: 'laugh', blush: 0.5, tilt_head: -5 },
  surprise: { lift: 11, tilt: 2, lid: 0, eye: 1.6, look: [0, 0.25], mouth: 'o', tilt_head: -3 },
  sad: { lift: 1, tilt: 8, lid: 0, eye: 0.7, look: [-0.4, 1.2], mouth: 'sad', tilt_head: 9 },
  anger: { lift: -7, tilt: -9, lid: 0, eye: 0.85, look: [0, 0], mouth: 'frown', tilt_head: 4 },
};

// the colour blocks (anya.py's colours); a pattern is printed flat over its block and travels with a joint of the body
export const blocks = G => [
  { groups: [G.skin], color: K.SKIN },
  { groups: [G.dress], color: DRESS, pattern: { kind: 'blossoms', args: ['#f3ead6', 38, 4.4, '#d8a23a'], rot: 20, joint: 'Hips' } },
  { groups: [G.card], color: CARD, pattern: { kind: 'asanoha', args: ['#b9812a', 30, 1.2], joint: 'Chest' } },
  { groups: [G.shoe], color: SHOE },
  { groups: [G.hair], color: HAIR },
];
// the slipper: the foot below its low cut
export const glsl = G => `
  if (abs(gg - ${G.skin}.0) < 0.5 && vB >= 0.0 && vB < 0.04) gg = ${G.shoe}.0;`;
export const FLAT = { skin: '#f4e7d0', hair: HAIR, card: CARD, dress: DRESS, shoe: SHOE };
// the key block's weights (kit.py: lines on cloth are heavier and follow direction more than lines on skin): [w, nib]
export const lineW = { body: [1.9, 0.3], head: [2.0, 0.3], chest: [2.0, 0.3], dress: [3.4, 0.6], cardigan: [3.3, 0.6],
  sleeveLeft: [3.1, 0.6], sleeveRight: [3.1, 0.6], hair: [1.6, 0.3] };
export const STAND = { out: 0.1, fwd: 0.03 };
export const VIEW = { far: { dist: 6.2, cy: 0.86 }, near: { dist: 1.9, up: 0.03 } };

export function strokeStyle(st) {
  if (st.kind === 'sheen') return { w: 0.9, prof: 'swell', color: SHEEN, op: 0.5, nib: 0.15, min: 24 };
  return { w: 3.0, prof: 'taper', nib: 0.3 };
}
export const minLen = { head: 16, body: 8 };
// the hairline: separate hairs out of its edge onto the forehead (anya.py: d.fringe(…, 6, 0.9, HAIR, lean 0.9))
export function fringe(d, P, st, F) {
  const l = F.jointAt('LeftEye'), r = F.jointAt('RightEye'), c = [(l[0] + r[0]) / 2, (l[1] + r[1]) / 2];
  const m = P[P.length >> 1], a = P[Math.max(0, (P.length >> 1) - 2)], b = P[Math.min(P.length - 1, (P.length >> 1) + 2)];
  const side = Math.sign(-(b[1] - a[1]) * (c[0] - m[0]) + (b[0] - a[0]) * (c[1] - m[1])) || 1;
  K.fringe(d, P, { length: 6.5 * F.ppu, w: 0.9, color: HAIR, lean: 0.9, step: Math.max(2, 3.2 * F.ppu), side, seed: st.v[0], layer: 'col' });
}

// the face in parts.head's front units, its numbers from the live face (F.fp)
export function drawFace(d, F) {
  const e = F.fp, { frameAt, useFrame } = F, { side, front } = F.sideOf();
  const ex = { open: e.squint ? 0 : e.eye, closed: e.blink || 0, lift: e.lift, tilt: e.tilt, look: [e.look[0] * 2.4, e.look[1] * 2.0],
    mouth: e.talk ? 'talk' : e.mouth, talkOpen: e.open || 0, talkRound: e.round || 0 };
  // the cheeks: a soft round patch of bokashi
  const bo = Pn.blush[1] + (e.blush || 0) * 0.5;
  for (const bx of [-46, 46]) {
    const f0 = frameAt(d, bx, 36, 0.5); if (!f0) continue;
    const t = 1 - Math.min(1, f0.r), far = Math.sign(bx) === side;
    const f = frameAt(d, bx - side * 12 * t, 36, 0.5) || f0;
    useFrame(d, f, bx, 36); d.blush(bx, 36, far ? 28 - 9 * t : 28, Pn.blush[0], bo);
  }
  // the eyes and the brows: the far eye of a turned face is shorter and keeps inside the contour
  for (const sx of [-33, 33]) {
    const f0 = frameAt(d, sx, 0, 0.72); if (!f0) continue;
    const sg = Math.sign(sx), far = sg === side, t0 = 1 - Math.min(1, f0.r);
    const f = frameAt(d, sx - side * 8 * t0, 0, 0.72) || f0, t = 1 - Math.min(1, f.r), k = far ? 1 - 0.32 * t : 1;
    const tn = far ? 0 : Math.max(0, 0.5 - front) / 0.5;        // the near eye, as the face nears the profile
    { const s = -side * (far ? 13 * t : 4 * t + 16 * tn); f.c = [f.c[0] + f.ax[0] * s, f.c[1] + f.ax[1] * s]; }
    useFrame(d, f, sx, 0);
    K.eye(d, Pn, sx, 0, k, -sg, { ...ex, look: [ex.look[0] + side * t * 2, ex.look[1]] });
    K.brow(d, Pn, sx + sg, k, -sg, ex);
  }
  // the nose: parts.nose's stroke — down with a hook at the tip, and the nostril — laid on the 3D nose, on its far
  // side, so it turns with the head; in profile the head's own contour carries the nose
  if (front > 0.12) {
    d.map = (x, y) => F.faceMap(x, y, true); d.T = [[1, 0, 0, 1, 0, 0]];
    K.noseFront(d, Pn, Math.min(1, (front - 0.12) / 0.15), front > 0.93 ? 1 : -side);
    d.map = null;
  }
  // the mouth, moved toward the seen cheek as the face turns
  const fm0 = frameAt(d, 0, MY, 0.5, true);
  if (fm0) {
    const t = 1 - Math.min(1, fm0.r), fm = frameAt(d, -side * 9 * t, MY, 0.55);
    if (fm) {
      const s = -side * 10 * t; fm.c = [fm.c[0] + fm.ax[0] * s, fm.c[1] + fm.ax[1] * s];
      useFrame(d, fm, 0, MY);
      const sh = 0.08 * t * side;                 // the far half of the mouth is the shorter one
      K.mouth(d, Pn, ex, 0, MY, 0.5 + sh, 0.5 - sh);
    }
  }
  d.T = [[1, 0, 0, 1, 0, 0]];
}
