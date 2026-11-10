// Кира of С14 — the character's own: styles/s14-paper/tools/kira.py carried into space. The numbers are the drawing's
// (figure units, feet at 0, heights up; head units for the head: 0.56 of a figure unit). The drawing's figure is one
// S-curve slouch seen three-quarters; here she is built standing straight and the slouch is a pose of the spine,
// kept on every motion.
import { ell, strip, crescent, corner, curve, mix, dark, lite, through, clip, slab, loft, tube, ringAt, merge, transform, patch, U, V } from './paper.js';
import { headShape, onHead, noseGeo, earGeo } from './face.js';
import { proportion, limbPiece, hand, faceHand, shoe, shell } from './body.js';

const HAIR = '#2b2330', SKIN = '#ecd3bf', HOOD = '#5b2f57', TROU = '#37343c', LIME = '#c9e32f';
const HS = .56, hu = HS * U;
const HEAD = [0, 492 * U, .012];

const inPoly = (poly, x, y) => { let c = false; for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) { const a = poly[i], b = poly[j]; if ((a[1] > y) !== (b[1] > y) && x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]) c = !c; } return c; };
const tri = t => Math.abs(((t % 1) + 1) % 1 - .5) * 2;                    // a zigzag 0..1: scissors' points

export const C = {
  id: 'kira', title: 'Кира', hu,
  bg: '#d5d9c4', sheet: '#ece9d7', groundColor: '#c4c6b5',
  spec: {
    skin: SKIN, rx: 70, ry: 98, jaw: .56, chin: .09, eye_y: 12, eye_gap: 31, eye_w: 14.5, eye_h: 11.5,
    iris: '#6d6688', lid: '#c9a3ab', lash: true, lash_col: '#231b26', brow: HAIR, brow_w: 7, brow_len: 28, brow_y: -23,
    nose: 'wedge', nose_y: 40, nose_s: .85, mouth_y: 66, mouth_w: 15, lip: '#a9566a',
    cheek: '#dc8a9c', cheek_r: 13, cheek_op: .22, cheek_x: .3, neck_w: 19, ear: 1,
    rest: { open: .62, tilt: -.2, brow: -.3, brow_dy: 4, mouth: 'flat', look: .9 },
    on: { joy: { mouth: 'smirk', open: .7, low: 0, brow: -.05, brow_dy: 0, look: .6 },      // she never smiles openly
      surprise: { mouth: 'pout', open: 1, eye: 1.1 }, sad: { look_y: .8 }, angry: { mouth: 'frown' } },
  },
  exprs: [['calm', 'как всегда'], ['joy', 'усмешка'], ['surprise', 'удивление'], ['sad', 'грусть'], ['angry', 'злость']],
  motions: [{ id: 'walk', label: 'идёт' }, { id: 'sneak', label: 'крадётся' }],
  hold: ['LeftShoulder'],                                  // the hand in the pocket: kept on every motion
  breath: 1, headTurn: 12,
  view: { yaw: 0, pitch: .03, dist: 9.5, h: .85, fov: 13 },

  joints: sk => proportion(sk, { hip: .785, leg: .75, legX: .04, knee: .40, ankle: .075, shoulder: 1.25, shoulderX: .118, upper: .26, fore: .255, hand: .8, neck: 1.292, head: 1.335, top: 1.66, foot: .12 }),

  build(fig) {
    const sp = fig.spec;
    // ---- legs: long and thin; heavy boots, toes turned in, lime laces
    for (const S of ['Left', 'Right']) {
      limbPiece(fig, S + 'Leg', S + 'Shin', 10.5, 9, { color: TROU });
      limbPiece(fig, S + 'Shin', S + 'Foot', 9, 7.5, { color: TROU });
      shoe(fig, S, { L: 54, h: 42, w: 25, color: '#2d2a31', sole: '#1e1b20', boot: true, lace: LIME, toeOut: -6 });
    }
    // ---- the hoodie: too big for her — one shell from the shoulders to under the hips, a darker band at the hem
    const hood = fig.hoodie = shell([[443, 26, 16, -18], [432, 45, 24, -25], [414, 57, 31, -31], [340, 63, 37, -36], [262, 61, 39, -36], [226, 57, 37, -34]]);
    const sm = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
    const W = p => { const h = p[1] / U, up = sm(318, 395, h), mid = sm(262, 318, h) * (1 - up); return [['Chest', up], ['Spine1', mid], ['Hips', 1 - up - mid]].filter(x => x[1] > 1e-4); };
    fig.piece({ name: 'hoodie', geo: clip(hood.mesh(), p => (p[2] > 0 && p[1] / U > 428 - Math.abs(p[0] / U) * .9 && Math.abs(p[0] / U) < 17) ? -1 : 1), color: HOOD, kind: 'paint', v: 1, weights: W });
    const band = shell([[244, 62.5, 40.5, -37.5], [236, 61, 40, -37], [224, 58, 38.5, -35.5]]);
    fig.piece({ name: 'hem', geo: band.mesh({ capTop: false }), color: dark(HOOD, .18), kind: 'paint', v: 1, weights: W });
    fig.piece({ name: 'pocket', geo: hood.on([[-33, -312, 1], [33, -312, 1], [45, -254, 1], [-45, -254, 1]], 1), color: dark(HOOD, .12), kind: 'paint', v: 1, weights: W });
    fig.piece({ name: 'stringL', geo: hood.on(strip([[-9, -416], [-11, -356]], 3.5), 1.2), color: lite(HOOD, .55), kind: 'card', weights: W });
    fig.piece({ name: 'stringR', geo: hood.on(strip([[9, -416], [10, -368]], 3.5), 1.2), color: lite(HOOD, .55), kind: 'card', weights: W });
    // the hood heaped on the back, behind the neck
    const heap = []; for (let i = 0; i <= 8; i++) { const a = -Math.PI / 2 + Math.PI * (i + (i === 0 ? .25 : i === 8 ? -.25 : 0)) / 8, c = Math.cos(a); heap.push(ringAt((432 + 26 * Math.sin(a)) * U, 44 * c * U, (-14 + 20 * c) * U, (-14 - 30 * c) * U, 24, .9)); }
    fig.piece({ name: 'hood', joint: 'Chest', geo: loft(heap, { cap0: true, cap1: true }), color: dark(HOOD, .2), kind: 'paint', v: 1 });
    // ---- headphones round the neck: the band behind, two lime cups in front
    const hy = 420, hx = 21, zc = hood.z(hx, hy) + 3.5;
    for (const s of [-1, 1]) {
      const at = (x, y, t) => [(s * hx + x * Math.cos(.35) * 1) * U + s * t * Math.sin(.35), (hy - y) * U, (zc - s * x * Math.sin(.35)) * U + t * Math.cos(.35)];
      fig.piece({ name: 'cup' + s, joint: 'Chest', geo: slab([[-7.5, -11], [7.5, -11], [8.6, 11], [-8.6, 11]], at, { thick: .011 }), color: LIME, kind: 'card' });
      fig.piece({ name: 'cupIn' + s, joint: 'Chest', geo: slab(ell(0, 1, 4.5, 6.8, 0, 10), (x, y, t) => at(x, y, t + .0062), { thick: .0008 }), color: '#2a2428', kind: 'flat' });
    }
    const arc = []; for (let i = 0; i <= 20; i++) { const a = Math.PI * (-.08 + 1.16 * i / 20); arc.push([hx * 1.05 * Math.cos(a), -9 * Math.sin(a) + zc - 20]); }
    const bandG = { pos: [], idx: [], uv: [] };
    arc.forEach(([x, z], i) => { for (const dy of [3.2, -3.2]) { bandG.pos.push(x * U, (hy + 9 + dy + 13 * Math.sin(Math.PI * i / 20)) * U, z * U); bandG.uv.push(i * 4, dy); } if (i) { const a = (i - 1) * 2; bandG.idx.push(a, a + 2, a + 1, a + 2, a + 3, a + 1); } });
    fig.piece({ name: 'phonesBand', joint: 'Chest', geo: bandG, color: dark(LIME, .25), kind: 'card' });
    // ---- arms: sleeves too long, each a strip per bone (the drawing has no brads on her); a hand lost in the sleeve
    for (const S of ['Left', 'Right']) {
      limbPiece(fig, S + 'Arm', S + 'ForeArm', 15, 13.5, { color: S === 'Left' ? dark(HOOD, .12) : HOOD, kind: 'paint', v: 1 });
      const e = fig.R(S + 'ForeArm'), w = fig.R(S + 'Hand'), d = V.norm(V.sub(w, e));
      limbPiece(fig, S + 'ForeArm', S + 'Hand', 13.5, 12, { to: V.add(w, V.mul(d, 9 * U)), color: S === 'Left' ? dark(HOOD, .12) : HOOD, kind: 'paint', v: 2 });
      if (S === 'Left') continue;                          // her left hand is in the pocket: never seen
      hand(fig, S, { skin: SKIN, s: .9, spread: 3, thumb: 0 });
      // the hand sits deep in the sleeve: only the fingers show
      for (const n of [S + 'Palm']) { const p = fig.rigid.find(r => r.p.name === n).p; p.geo = transform(p.geo, q => V.add(q, V.mul(d, 9 * U))); fig.look.setGeo(p.mesh, p.geo); }
    }
    // ---- the head
    fig.group('head', 'Head', HEAD);
    const H = fig.head = headShape(sp), G = g => transform(g, p => [p[0] * hu, -p[1] * hu, p[2] * hu]);
    fig.piece({ name: 'neck', joint: 'Neck1', geo: tube([0, 404 * U, .004], [0, 470 * U, 0], sp.neck_w * HS * U, sp.neck_w * HS * U, { flat: .9 }), color: mix(SKIN, '#c0705c', .20), kind: 'card' });
    fig.piece({ name: 'face', group: 'head', geo: G(H.shell(1, 0, 96, 72)), color: SKIN, kind: 'card' });
    for (const s of [-1, 1]) { const [a, b] = earGeo(H, hu, sp, s); fig.piece({ name: 'ear' + s, group: 'head', geo: a, color: mix(SKIN, '#d98a6c', .18), kind: 'card' }); fig.piece({ name: 'earIn' + s, group: 'head', geo: b, color: mix(SKIN, '#c0705c', .42), kind: 'flat' }); }
    fig.piece({ name: 'nose', group: 'head', geo: noseGeo(H, hu, sp), color: mix(SKIN, '#d98a6c', .32), kind: 'card' });
    // hair, cut in sharp points: the back (darker, a jagged hem), a lock down her left temple, and the fringe —
    // the drawing's own outline — standing off the face over her right eye
    const ang = p => Math.atan2(p[0], -p[2]);
    fig.piece({ name: 'hairBack', group: 'head', geo: G(clip(H.shell(1.03, 4, 72, 44, 22), p => p[2] < 4 ? (34 + 26 * tri(ang(p) * 2.1 + .25)) - p[1] : p[2] < 44 ? -68 - p[1] : -1)), color: dark(HAIR, .15), kind: 'paint', v: 1 });
    const xin = through([[-110, 30], [-98, 34], [-40, 54], [16, 64], [30, 66]]);
    fig.piece({ name: 'hairSide', group: 'head', geo: G(clip(H.shell(1.04, 6, 72, 48, 23), p => (p[2] > -30 && p[0] > xin(p[1]) && p[1] < 2 + 26 * tri((p[0] - 64) / 15 + (p[2] < 0 ? -p[2] / 30 : 0))) ? 1 : -1)), color: HAIR, kind: 'paint', v: 1 });
    const fr = curve([[42, -96], [-28, -110], [-74, -82], [-88, -30], [-85, 14], [-80, 46, 1], [-68, 8, 1], [-57, 40, 1], [-46, 12, 1], [-34, 32, 1], [-20, 4, 1], [-4, -28], [22, -64]], 6);
    // from the side the fringe is cut shorter (the drawing's profile): the eye shows under its points
    const sideLine = through([[-34, 42], [0, 12], [30, -4], [60, -30]]);
    fig.piece({ name: 'fringe', group: 'head', geo: G(clip(H.shell(1.05, 8, 110, 72, 25), p => {
      if (p[2] <= -30 - (p[1] + 60) * .28) return -1;
      const low = p[1] < sideLine(p[2]) + 14 * tri(p[2] / 19 + .3);
      return ((inPoly(fr, p[0], p[1]) && (p[2] > 30 || low)) || (p[0] < -40 && low && p[1] > -80)) ? 1 : -1;
    })), color: HAIR, kind: 'paint', v: 1 });
  },
  // the drawn stand: one S-curve — hips forward, the back rounded, shoulders up, the head hung forward; her left hand
  // in the pocket (the elbow out), the right arm hanging in its sleeve
  stand(fig, pose) {
    if (!fig.straight) slouch(fig, pose, 1);
    for (const S of ['Left', 'Right']) { const f = S === 'Left' ? .1 : -.05; fig.aim(pose, S + 'Leg', S + 'Shin', [S === 'Left' ? .05 : -.05, -1, f]); fig.aim(pose, S + 'Shin', S + 'Foot', [0, -1, f - .04]); fig.aim(pose, S + 'Foot', S + 'ToeBase', [S === 'Left' ? -.1 : .1, -.45, 1]); }
    fig.aim(pose, 'LeftArm', 'LeftForeArm', [.55, -.75, -.35]); fig.aim(pose, 'LeftForeArm', 'LeftHand', [-.55, -.62, .5]);
    fig.aim(pose, 'RightArm', 'RightForeArm', [-.14, -1, .16]); fig.aim(pose, 'RightForeArm', 'RightHand', [.03, -1, .2]);
    fig.aim(pose, 'RightHand', 'RightHandMiddle1', [.05, -1, .15]); faceHand(fig, pose, 'Right', [.4, 0, 1]);
  },
  // on a motion the slouch stays: the back rounded and the head down, a look from under the brows
  onMotion(fig, pose) { slouch(fig, pose, fig.motionId === 'sneak' ? .25 : .8); },   // Kimodo's sneak crouches by itself
};

function slouch(fig, pose, k) {
  const X = [1, 0, 0];
  if (k === 1) fig.turn(pose, 'Hips', X, -9);
  fig.turn(pose, 'Spine1', X, 4 * k); fig.turn(pose, 'Spine2', X, 8 * k); fig.turn(pose, 'Chest', X, 9 * k);
  fig.turn(pose, 'LeftShoulder', [0, 0, 1], 10 * k); fig.turn(pose, 'RightShoulder', [0, 0, 1], -10 * k);
  fig.turn(pose, 'Neck1', X, 15 * k); fig.turn(pose, 'Neck2', X, 8 * k); fig.turn(pose, 'Head', X, -26 * k);
}
