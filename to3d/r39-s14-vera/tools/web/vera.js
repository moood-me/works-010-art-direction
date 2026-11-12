// Вера of С14 — the character's own: styles/s14-paper/tools/vera.py carried into space. The numbers are the drawing's
// (figure units, feet at 0, heights up; head units for the head: 0.56 of a figure unit).
import { ell, strip, crescent, corner, rotP, moveP, mix, dark, lite, through, clip, slab, loft, tube, ringAt, merge, transform, U, V } from './paper.js';
import { headShape, onHead, noseGeo, earGeo, LAYER } from './face.js';
import { proportion, limbPiece, brad, hand, faceHand, shoe, shell } from './body.js';

const HAIR = '#3a2c33', SKIN = '#ebc7a8', COAT = '#3d6c76', SCARF = '#7a3558', FRAME = '#8a2f3c', STOCK = '#34323a';
const HS = .56, hu = HS * U;
const HEAD = [0, 516 * U, .012];                           // the face's centre at rest

export const C = {
  id: 'vera', title: 'Вера', hu,
  bg: '#e3d3d6', sheet: lite('#e3d3d6', .55), groundColor: dark('#e3d3d6', .10),
  spec: {
    skin: SKIN, rx: 72, ry: 100, jaw: .56, chin: .07, eye_y: 8, eye_gap: 31, eye_w: 14, eye_h: 9.5,
    iris: '#4c5a66', lash: true, lid: '#cfa59c', brow: HAIR, brow_w: 5, brow_len: 28, brow_y: -25,
    nose: 'long', nose_y: 40, nose_s: .78, mouth_y: 67, mouth_w: 16, lip: '#9c4048',
    cheek: '#d98888', cheek_r: 14, cheek_op: .24, neck_w: 22, ear: 1,
    rest: { open: .60, tilt: .14, brow: .06, brow_dy: -1, mouth: 'flat' },
    on: { joy: { mouth: 'smile', open: .7, low: .45, brow_dy: -4 } },
  },
  exprs: [['calm', 'спокойна'], ['joy', 'радость'], ['surprise', 'удивление'], ['sad', 'грусть'], ['angry', 'злость']],
  motions: [{ id: 'walk', label: 'идёт' }, { id: 'bow', label: 'поклон' }],
  hold: ['RightShoulder'],                                 // the arm that presses the papers to the chest: kept on every motion
  breath: 1, headTurn: 14,
  view: { yaw: 0, pitch: .03, dist: 9.5, h: .92, fov: 13 },
  drawnHead: { yaw: 24, tilt: 4 },                         // the drawing's figure: the head three-quarters, a little tilted

  joints: sk => proportion(sk, { hip: .90, leg: .825, legX: .046, knee: .45, ankle: .07, shoulder: 1.32, shoulderX: .144, upper: .225, fore: .21, hand: .8, neck: 1.375, head: 1.42, top: 1.74, foot: .1 }),

  build(fig) {
    const sp = fig.spec;
    // ---- legs: dark stockings, one strip per bone; shoes
    for (const S of ['Left', 'Right']) {
      limbPiece(fig, S + 'Leg', S + 'Shin', 10, 8.5, { color: STOCK });
      limbPiece(fig, S + 'Shin', S + 'Foot', 8.5, 7, { color: STOCK });
      shoe(fig, S, { L: 40, h: 19, w: 17, color: '#2a2428', toeOut: 26 });
    }
    // ---- the coat: one shell, heights in units — shoulders, chest, waist, hem
    const coat = fig.coat = shell([[466, 30, 15, -17], [452, 44, 22, -23], [430, 52, 28, -27], [380, 51, 31, -28], [330, 50, 29, -28], [220, 57, 37, -37], [100, 66, 47, -46]]);
    const sm = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
    const coatW = p => {                                  // which joints a point of the coat follows
      const h = p[1] / U, x = p[0] / U, w = [];
      const up = sm(330, 410, h), mid = sm(262, 330, h) * (1 - up), low = 1 - up - mid;
      const th = .94 * sm(305, 225, h), sh = .5 * sm(165, 100, h), L = sm(-10, 10, x);
      w.push(['Chest', up], ['Spine1', mid], ['Hips', low * (1 - th)], ['LeftLeg', low * th * L * (1 - sh)], ['RightLeg', low * th * (1 - L) * (1 - sh)], ['LeftShin', low * th * L * sh], ['RightShin', low * th * (1 - L) * sh]);
      return w.filter(x => x[1] > 1e-4);
    };
    fig.coatW = coatW;
    fig.piece({ name: 'coat', geo: coat.mesh(), color: COAT, kind: 'paint', v: 1, weights: coatW });
    fig.piece({ name: 'placket', geo: coat.on([[4, -330, 1], [16, -330, 1], [26, -100.5, 1], [2, -100.5, 1]], 1), color: dark(COAT, .14), kind: 'paint', v: 1, weights: coatW });
    for (let i = 0; i < 3; i++) fig.piece({ name: 'button' + i, geo: coat.on(ell(-8, -310 + i * 44, 4.5, 4.5, 0, 8), 1.2), color: dark(COAT, .4), kind: 'card', weights: coatW });
    // ---- the scarf: a band round the neck and its end down the chest
    const sc = [[474, 20, 19, -24], [464, 27, 26, -31], [450, 29, 29, -33], [438, 27, 30, -31], [432, 22, 27, -25]].map(([h, w, f, b]) => ringAt(h * U, w * U, f * U, b * U, 28, .9));
    fig.piece({ name: 'scarf', joint: 'Chest', geo: loft(sc, { cap0: true, cap1: true }), color: SCARF, kind: 'paint', v: 0 });
    fig.piece({ name: 'scarfEnd', geo: coat.on([[7, -440, 1], [23, -441, 1], [27, -391, 1], [20, -394, 1], [16.5, -388.5, 1], [10, -393, 1]], 2.4), color: SCARF, kind: 'paint', v: 3, weights: coatW });
    // ---- the papers pressed to the chest
    const zp = coat.z(-14, 376) + 3.5;
    ['#e8dcc0', '#fbf6ea', '#d9e3ea', '#fbf6ea'].forEach((c, i) => {
      const sheet = moveP(rotP(rotP([[-30, -40, 1], [30, -40, 1], [30, 40, 1], [-30, 40, 1]], -8 + i * 5), -6), -14, -376);
      fig.piece({ name: 'paper' + i, joint: 'Chest', geo: slab(sheet, (x, y, t) => [x * U, -y * U, (zp + i * .5) * U + t], { thick: .0012 }), color: c, kind: 'card' });
    });
    for (let i = 0; i < 4; i++) {
      const ln = moveP(rotP(strip([[-18, -22 + i * 11], [16 - (i % 2) * 10, -20 + i * 11]], 2.4), -6), -14, -376);
      fig.piece({ name: 'line' + i, joint: 'Chest', geo: slab(ln, (x, y, t) => [x * U, -y * U, (zp + 2.1) * U + t], { thick: .0004 }), color: '#9aa3ad', kind: 'flat' });
    }
    // ---- arms: sleeves as two strips with a brad in the elbow; hands cut from one piece
    for (const S of ['Left', 'Right']) {
      limbPiece(fig, S + 'Arm', S + 'ForeArm', 12, 10.5, { color: COAT, kind: 'paint', v: 1 });
      limbPiece(fig, S + 'ForeArm', S + 'Hand', 10.5, 9, { color: COAT, kind: 'paint', v: 2 });
      brad(fig, S + 'ForeArm', 3.2, 11 * U);
      hand(fig, S, { skin: SKIN, s: .95, spread: S === 'Left' ? 3 : 5, thumb: S === 'Left' ? -1 : 1 });
    }
    // ---- the head: its own space (head units → metres), riding the Head joint
    fig.group('head', 'Head', HEAD);
    const H = fig.head = headShape(sp), G = g => transform(g, p => [p[0] * hu, -p[1] * hu, p[2] * hu]);
    fig.piece({ name: 'neck', joint: 'Neck1', geo: tube([0, 440 * U, -.004], [0, 500 * U, .0], sp.neck_w * HS * U, sp.neck_w * HS * U, { flat: .9 }), color: mix(SKIN, '#c0705c', .20), kind: 'card' });
    fig.piece({ name: 'face', group: 'head', geo: G(H.shell(1, 0, 96, 72)), color: SKIN, kind: 'card' });
    for (const s of [-1, 1]) { const [a, b] = earGeo(H, hu, sp, s); fig.piece({ name: 'ear' + s, group: 'head', geo: a, color: mix(SKIN, '#d98a6c', .18), kind: 'card' }); fig.piece({ name: 'earIn' + s, group: 'head', geo: b, color: mix(SKIN, '#c0705c', .42), kind: 'flat' }); }
    fig.piece({ name: 'nose', group: 'head', geo: noseGeo(H, hu, sp), color: mix(SKIN, '#d98a6c', .32), kind: 'card' });
    // hair: a darker shell behind and a cap cut by scissors along the drawing's hairline (a parting peak over the brow)
    const line = through([[0, -77], [20, -73], [40, -62], [58, -40], [68, -8], [76, 16]]), zE = -6;
    fig.piece({ name: 'hairBack', group: 'head', geo: G(clip(H.shell(1.03, 3, 56, 36), p => (p[2] < -2 ? 24 + 22 * Math.min(1, Math.max(0, (-20 - p[2]) / 40)) - p[1] : -1))), color: dark(HAIR, .1), kind: 'paint', v: 1 });
    fig.piece({ name: 'hairCap', group: 'head', geo: G(clip(H.shell(1.06, 4, 72, 48), p => p[2] > zE ? line(Math.abs(p[0])) - p[1] : (16 - Math.max(0, -40 - p[2]) * .5) - p[1])), color: HAIR, kind: 'paint', v: 1 });
    fig.piece({ name: 'hairLight', group: 'head', geo: onHead(H, hu, crescent(8, -100, 60, -46, -10, 4), 1, { grow: 1.06, add: 4 }), color: '#9a8f96', kind: 'flat' });
    // the bun: a rolled strip — a ball, and the roll's turns facing the eye
    const bun = [0, -117, -38], br = 28;
    const ball = []; for (let i = 0; i <= 10; i++) { const a = -Math.PI / 2 + Math.PI * (i + (i === 0 ? .2 : i === 10 ? -.2 : 0)) / 10; ball.push(ringAt(bun[1] + br * Math.sin(a), br * Math.cos(a), bun[2] + br * Math.cos(a), bun[2] - br * Math.cos(a), 20, 1)); }
    fig.piece({ name: 'bun', group: 'head', geo: G(loft(ball, { cap0: true, cap1: true })), color: HAIR, kind: 'paint', v: 1 });
    fig.bill({ name: 'bunTurns', joint: 'Head', at: [HEAD[0] + bun[0] * hu, HEAD[1] - bun[1] * hu, HEAD[2] + bun[2] * hu], r: br * hu, out: br * hu * 1.04, flat: true, discs: [{ k: .62, color: dark(HAIR, .28), dx: .10, dy: -.12 }, { k: .36, color: lite(HAIR, .10), dx: -.02, dy: .02 }] });
    // glasses: rings of card standing before the eyes, a bridge, temples back to the ears
    const gy = sp.eye_y + 1, gz = H.z(sp.eye_gap, gy) + 6.5, flatAt = (x, y, t) => [x * hu, -y * hu, (gz - Math.abs(x) * .06) * hu + t], parts = [];
    for (const s of [-1, 1]) {
      const x = s * sp.eye_gap;
      parts.push(slab(ell(x, gy, 21, 16, 0, 14), flatAt, { thick: .0014, holes: [ell(x, gy, 17.8, 12.8, 0, 14).reverse()], maxEdge: 30 }));
      const a = [x + s * 20, gy - 2, gz - 3], b = [s * (H.hw(gy - 6) + 2), gy - 6, -4], d = V.sub(b, a);
      parts.push(slab([[0, -1.5, 1], [1, -1.5, 1], [1, 1.5, 1], [0, 1.5, 1]], (u, v, t) => [(a[0] + d[0] * u) * hu + s * t, -(a[1] + d[1] * u + v) * hu, (a[2] + d[2] * u) * hu], { thick: .0012, dense: true, maxEdge: 99 }));
    }
    parts.push(slab(crescent(-sp.eye_gap + 20, gy - 2, sp.eye_gap - 20, gy - 2, -3, 3), flatAt, { thick: .0014 }));
    fig.piece({ name: 'glasses', group: 'head', geo: merge(...parts), color: FRAME, kind: 'card' });
  },
  // what Вера has on her face besides the common pieces: the shadows of tiredness under the eyes
  extras(fig, e) {
    const sp = fig.spec;
    return [-1, 1].map(s => ({ key: 'bag' + s, pts: crescent(s * sp.eye_gap - 12, sp.eye_y + 13, s * sp.eye_gap + 12, sp.eye_y + 13, 4, 5), color: mix(SKIN, '#9a6f86', .3), kind: 'flat', layer: 1 }));
  },
  // the drawn stand: papers pressed to the chest with her right arm, the left hanging
  stand(fig, pose) {
    fig.aim(pose, 'LeftArm', 'LeftForeArm', [.16, -1, .02]); fig.aim(pose, 'LeftForeArm', 'LeftHand', [-.06, -1, .07]);
    fig.aim(pose, 'LeftHand', 'LeftHandMiddle1', [-.05, -1, .05]); faceHand(fig, pose, 'Left', [.5, 0, 1]);
    fig.aim(pose, 'RightArm', 'RightForeArm', [-.25, -1, .27]); fig.aim(pose, 'RightForeArm', 'RightHand', [.132, -.066, .06]);
    fig.aim(pose, 'RightHand', 'RightHandMiddle1', [1, -.25, .02]); faceHand(fig, pose, 'Right', [0, 0, 1]);
  },
};
