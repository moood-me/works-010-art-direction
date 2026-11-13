// Марат of С13 (styles/s13-ukiyo-e/tools/marat.py): what is his own for the print renderer (print.js) — the colour
// blocks and their patterns, his face as parts.head draws it (eyes closed into arcs by the laugh, the open mouth with
// teeth and tongue on the black beard, heavy brows, the broad nose), his sheet's expressions, the jaw that drops with
// the laugh, the beard's edge of separate hairs, his sheet (ground, name).
import * as K from './kit-fast.js';
export const PACK = 'marat.json';
export const HAIR = '#1f1a1a', SHEEN = '#8a8684', WHITE = '#f8f2e2', TERRA = '#c8683a', TERRA_D = '#9c4a26', SKIN = '#f1d7b6';
export const SHEET = { ground: '#8fa3ab', top: '#4f6c80', bottom: '#b9a67c', name: 'Марат' };

const Pn = K.P({ skin: SKIN, long: 0.98, eye: { w: 32, h: 8.5, iris: 6.2, lid: 4.0, slant: 0, lower: 0.6, color: '#2a2220' },
  brow: { kind: 'thick', w: 9.5, len: 44, arch: 7, y: -24 }, nose: { kind: 'broad', s: 1.12 }, mouth: { w: 40, y: 66, lip: null, full: 1.2 }, blush: ['#e2876a', 0.45] });
const MY = Pn.mouth.y * Pn.long;

// marat.py's EXPR in the live face's words; his rest is the grin; op — how far the jaw is down
export const NAMES = ['grin', 'joy', 'surprise', 'sad', 'anger'];
export const LABELS = { grin: 'улыбается', joy: 'хохочет', surprise: 'удивление', sad: 'грусть', anger: 'злость' };
export const EXPR = {
  grin: { lift: 3, tilt: 0, lid: 0, eye: 0, squint: true, look: [0, 0], mouth: 'grin', blush: 0.5, op: 0.45 },
  joy: { lift: 5, tilt: 1, lid: 0, eye: 0, squint: true, look: [0, 0], mouth: 'grin', blush: 0.6, op: 1.0, tilt_head: -8 },
  surprise: { lift: 12, tilt: 2, lid: 0, eye: 1.6, look: [0, 0], mouth: 'gasp', op: 0.4, tilt_head: -3 },
  sad: { lift: 0, tilt: 9, lid: 0, eye: 0.7, look: [-0.4, 1.2], mouth: 'sad', op: 0, tilt_head: 10 },
  anger: { lift: -8, tilt: -10, lid: 0, eye: 0.9, look: [0, 0], mouth: 'snarl', op: 0.25, tilt_head: 5 },
};

// the colour blocks (marat.py's colours); a pattern is printed flat over its block and travels with a joint of the body
export const blocks = G => [
  { groups: [G.skin], color: SKIN },
  { groups: [G.jacket], color: WHITE },
  { groups: [G.towel], color: WHITE, pattern: { kind: 'stripes', args: [TERRA, 28, 8], joint: 'LeftShoulder' } },
  { groups: [G.apron], color: TERRA, pattern: { kind: 'seigaiha', args: ['#e08e5c', 24, 1.8], joint: 'Hips' } },
  { groups: [G.trousers], color: '#e6dfd0', pattern: { kind: 'checks', args: ['#3f4a5a', 14], joint: 'Hips' } },
  { groups: [G.shoe], color: '#2a2426' },
  { groups: [G.hair], color: HAIR },
];
export const glsl = G => '';
export const FLAT = { skin: SKIN, hair: HAIR, jacket: WHITE, apron: TERRA, trousers: '#e6dfd0', shoe: '#2a2426', towel: '#efe8da' };
// the key block's weights: [w, nib]
export const lineW = { body: [2.2, 0.3], head: [2.0, 0.3], jacket: [4.0, 0.6], sleeveLeft: [3.6, 0.6], sleeveRight: [3.6, 0.6],
  trousersLeft: [3.4, 0.6], trousersRight: [3.4, 0.6], apron: [3.8, 0.6], bib: [3.8, 0.6], strap0: [1.6, 0.3], strap1: [1.6, 0.3],
  towel: [2.8, 0.6], hair: [2.0, 0.3], beard: [1.2, 0.2] };
export const minLen = { head: 22, body: 8, towel: 16 };
// the curls' round bumps over the hair itself: a short light arc each (marat.py: SHEEN)
export const thinMin = 8, thinEvery = 1, thinW = 1.1, thinColor = SHEEN, thinOp = 0.7;
export const bodyLine = 1.25, headPieces = ['head', 'hair', 'beard'];
export const STAND = { out: 0.24, fwd: 0.04 };
export const MOTIONS = [['', 'стоит'], ['idle', 'стоит, оглядывается'], ['walk', 'шаг'], ['wave', 'машет'], ['stomp', 'топает'], ['bow', 'поклон'], ['dance', 'танец']];
export const VIEW = { far: { dist: 7.4, cy: 0.98 }, near: { dist: 2.4, up: 0.05 } };

export function strokeStyle(st) {
  if (st.kind === 'fold') return { w: 3.0, prof: 'taper', nib: 0.3, color: TERRA_D };
  if (st.kind === 'collar') return { w: 3.0, prof: 'even', nib: 0.5, min: 20 };
  return { w: 3.0, prof: 'taper', nib: 0.3 };
}
export function mark(d, mk, x, y, ppu, F) {
  if (mk.kind === 'button') {
    const r = mk.r * ppu;
    d.put(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}" fill="${WHITE}" stroke="${K.INK}" stroke-width="${(1.4 * d.wk).toFixed(2)}"/>`, 'key');
  } else if (mk.kind === 'curl') {
    const s = mk.r / 6 * ppu, a = mk.rot * Math.PI / 180, c = Math.cos(a), sn = Math.sin(a);
    const P = K.curve([[-6, 3], [-2, -5], [5, -3], [4, 3]].map(([u, v]) => [x + (u * c - v * sn) * s, y + (u * sn + v * c) * s]), false, 6);
    K.stroke(d, P, 1.1, 'swell', { nib: 0, color: SHEEN, op: 0.7, layer: 'col', seed: mk.v });
  }
}
// the beard's edge is separate hairs growing out of it (marat.py: d.fringe(out, 9, 1.3, HAIR, lean 0.5)), wherever it
// is seen: against the cheek, the jacket, the ground
export function onContour(d, pn, P, F, seed) {
  if (pn !== 'beard') return false;
  const G = F.fig && 2, i = P.length >> 1, a = P[Math.max(0, i - 2)], b = P[Math.min(P.length - 1, i + 2)];
  const tx = b[0] - a[0], ty = b[1] - a[1], l = Math.hypot(tx, ty) || 1, nx = -ty / l * 3, ny = tx / l * 3;
  const ga = F.grpAt(P[i][0] + nx, P[i][1] + ny), gb = F.grpAt(P[i][0] - nx, P[i][1] - ny);
  if (ga === gb) return true;
  const side = ga === G ? -1 : 1;           // the hairs grow away from the dark
  K.fringe(d, P, { length: 8 * F.ppu, w: 1.2, color: HAIR, lean: 0.5 * side, step: Math.max(2.2, 3.4 * F.ppu), side, seed, layer: 'col' });
  return true;
}

// how far the jaw is down: the sheet's mouths by their numbers, speech by its syllables
const jawOpen = e => e.talk ? Math.max(0.12, Math.min(1, 0.15 + (e.open || 0) * 1.1)) : (e.jaw || 0);
export function poseHook(pose, e, T) {
  const ax = T.qRot(T.getQ(pose.Q, T.I.Head), [1, 0, 0]);
  T.turnUnder(pose, T.sk, T.I.Jaw, T.qAxisAngle(ax, 0.17 * jawOpen(e)));
}

// the face in parts.head's front units, its numbers from the live face (F.fp)
export function drawFace(d, F) {
  const e = F.fp, { frameAt, useFrame } = F, { side, front } = F.sideOf();
  const ex = { open: e.squint ? 0 : e.eye, closed: e.blink || 0, lift: e.lift, tilt: e.tilt, look: [e.look[0] * 2.2, e.look[1] * 2.0],
    mouth: e.talk ? 'talk' : e.mouth, talkOpen: e.open || 0, talkRound: e.round || 0, jaw: jawOpen(e) };
  const bo = Pn.blush[1] + (e.blush || 0) * 0.5;
  for (const bx of [-46, 46]) {
    const f0 = frameAt(d, bx, 30, 0.5); if (!f0) continue;
    const t = 1 - Math.min(1, f0.r), far = Math.sign(bx) === side;
    const f = frameAt(d, bx - side * 12 * t, 30, 0.5) || f0;
    useFrame(d, f, bx, 30); d.blush(bx, 30, far ? 26 - 9 * t : 26, Pn.blush[0], bo);
  }
  for (const sx of [-33, 33]) {
    const sg = Math.sign(sx), far = sg === side;
    let f0 = null, back = 0;
    for (; back <= (far ? 24 : 0) && !f0; back += 6) f0 = frameAt(d, sx - side * back, 0, 0.72);
    if (!f0) continue;
    back -= 6; const t0 = 1 - Math.min(1, f0.r);
    const f = frameAt(d, sx - side * Math.max(back, 8 * t0), 0, 0.72) || f0, t = 1 - Math.min(1, f.r);
    const tn = far ? 0 : Math.max(0, 0.55 - front) / 0.55, k = far ? 1 - 0.32 * t : 1 - 0.3 * tn;
    if (far && front < 0.22) continue;
    { const s = -side * (far ? 13 * t + back * 0.7 : 4 * t + 18 * tn); f.c = [f.c[0] + f.ax[0] * s, f.c[1] + f.ax[1] * s]; }
    useFrame(d, f, sx, 0);
    K.eye(d, Pn, sx, 0, k, -sg, { ...ex, look: [ex.look[0] + side * t * 2, ex.look[1]] });
    K.brow(d, Pn, sx + sg - side * (far ? 8 * t : 10 * tn), k * (far ? 0.85 : 1 - 0.25 * tn), -sg, ex);       // the far brow keeps on the face
  }
  if (front > 0.12) {
    d.map = (x, y) => F.faceMap(x, y, true); d.T = [[1, 0, 0, 1, 0, 0]];
    K.noseFront(d, Pn, Math.min(1, (front - 0.12) / 0.15), front > 0.93 ? 1 : -side);
    d.map = null;
  }
  // the mouth on the beard: its place on the head under the beard, moved toward the seen cheek as the face turns
  const fm0 = frameAt(d, 0, MY, 0.5, true);
  if (fm0) {
    const t = 1 - Math.min(1, fm0.r), fm = frameAt(d, -side * 9 * t, MY, 0.55, true);
    if (fm) {
      const s = -side * (16 * t + 14 * Math.max(0, 0.5 - front) / 0.5); fm.c = [fm.c[0] + fm.ax[0] * s, fm.c[1] + fm.ax[1] * s];
      useFrame(d, fm, 0, MY);
      const fs = 0.5 - 0.08 * t - 0.36 * Math.max(0, 0.5 - front) / 0.5, ns = 0.5 + 0.08 * t;
      K.mouth(d, Pn, ex, 0, MY, side < 0 ? fs : ns, side < 0 ? ns : fs);
    }
  }
  d.T = [[1, 0, 0, 1, 0, 0]];
}
