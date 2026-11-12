// Тим, С15 «Нуар»: his own numbers. The head is the drawing's outlines (tim_drawing.json, from
// styles/s15-noir/tools/cast.py by drawing.py), rounder than a grown-up's; the body is the drawing's figure
// (figures.tim: 520 units tall, a striped shirt, shorts, thin bare legs, red shoes, a slingshot) in flat-faced forms.
import { S, box8, chain, limb, ringAt, headKit, skull, nose, ears, cap, lerp } from './build.js';
import { makeFace } from './face.js';
import { start } from './noir.js';

const D = await (await fetch(new URL('./tim_drawing.json', import.meta.url))).json();
const C = { skin: D.skin, cream: '#e6dcc4', red: '#c23b2c', shorts: '#2f4466', shoe: '#c23b2c', hair: '#d8b055', wood: '#8a5a34' };
const HEAD = { c: [0, 452, 5], s: 0.68 };
const K = headKit(D, HEAD, { ang: 0.72 });

const side = (s, p) => [s * p[0], p[1], p[2]];
const J = {
  Hips: [0, 204, 0], Spine1: [0, 226, 0], Spine2: [0, 262, 1], Chest: [0, 310, 1], Neck1: [0, 382, 0], Neck2: [0, 391, 1], Head: [0, 400, 2], HeadEnd: [0, 518, 2],
  Jaw: [0, 410, 10], LeftEye: [18, 440, 45], RightEye: [-18, 440, 45],
};
for (const [s, k] of [['Left', 1], ['Right', -1]]) Object.assign(J, {
  [s + 'Shoulder']: side(k, [12, 372, 0]), [s + 'Arm']: side(k, [38, 374, 0]), [s + 'ForeArm']: side(k, [44, 322, -1]), [s + 'Hand']: side(k, [46, 272, 3]),
  [s + 'Leg']: side(k, [19, 200, 0]), [s + 'Shin']: side(k, [24, 110, 1]), [s + 'Foot']: side(k, [28, 24, -2]), [s + 'ToeBase']: side(k, [28, 7, 22]), [s + 'ToeEnd']: side(k, [28, 7, 36]),
});
const SOLE = s => [[-9, 0, -13], [9, 0, -13], [8, 0, 32], [-8, 0, 32]].map(p => [p[0] + s * 28, p[1], p[2]]);
// the shirt's bands, bottom to top: red and cream by turns (the drawing: a red band of 14 every 30)
const BANDS = [250, 264, 280, 294, 310, 324, 340, 354, 370, 384];
const trunkW = y => y < 320 ? lerp(37, 40, (y - 250) / 70) : y < 372 ? lerp(40, 41, (y - 320) / 52) : lerp(41, 36, (y - 372) / 12);

function forms(F) {
  // ——— head: a rounder skull, a small nose (only the plane under its tip goes black), big ears, the cap of hair
  skull(F, K, { col: C.skin });
  nose(F, K, { col: C.skin, set: 'soft', lean: -1.2, bridge: 2, rim: 0 });
  ears(F, K, { col: C.skin, set: 'soft', out: 11 });
  // fair hair: the fringe's teeth over the forehead, short over the ears, tufts down the nape; uneven — tufts
  const R = [[0, -42, 12], [13, -60, 16], [27, -40, 12], [41, -58, 17], [55, -30, 13], [69, -48, 18], [83, -24, 14], [98, -8, 19], [112, 20, 18], [127, 2, 25], [142, 28, 20], [157, 10, 27], [171, 30, 21]];
  const L = [[-14, -62, 16], [-28, -44, 12], [-43, -60, 17], [-57, -34, 13], [-71, -50, 18], [-85, -22, 14], [-99, -6, 19], [-113, 22, 18], [-128, 4, 26], [-143, 28, 20], [-158, 8, 26], [-172, 26, 21]];
  cap(F, K, [...R, [180, 12, 26], ...L.reverse()], { col: C.hair, apex: [0, -116, 0],
    spikes: [[20, -92, 16, 16, 12, 0.9], [-70, -84, 14, 14, 14, 0.7], [150, -80, 16, 15, 20, 0.6], [100, -60, 14, 13, 20, 0.3], [-140, -66, 15, 14, 22, 0.4], [180, -40, 14, 13, 24, 0.1], [130, -30, 13, 12, 24, 0], [-110, -34, 13, 12, 20, 0]] });
  F.loft(F.part({ col: C.skin, w: chain(J, ['Neck1', 'Neck2', 'Head']) }), [box8(0, 378, 0, 12, 11, 0.5), box8(0, 392, 1, 12, 11, 0.5), box8(0, 410, 3, 13, 12, 0.5)]);
  // ——— the striped shirt: its bands are the rings' own faces
  const tw = chain(J, ['Hips', 'Spine1', 'Spine2', 'Chest']);
  const rings = [...BANDS.map(y => box8(0, y, 1, trunkW(y), 23 - (y > 370 ? 2 : 0), 0.45)), box8(0, 395, 0, 15, 13, 0.45)];
  F.loft(F.part({ col: C.cream, w: tw }), rings, { cols: i => i % 2 === 0 && i < 9 ? C.red : C.cream });
  // shorts: the hips and a wide leg each, going with its thigh
  F.loft(F.part({ col: C.shorts, w: 'Hips' }), [box8(0, 200, 1, 37, 23, 0.4), box8(0, 257, 1, 38.5, 24.5, 0.4)]);
  for (const [s, k] of [['Left', 1], ['Right', -1]]) {
    F.loft(F.part({ col: C.shorts, w: s + 'Leg' }), [box8(k * 23.5, 166, 1, 18, 22, 0.4), box8(k * 19, 236, 1, 18, 22, 0.4)]);
    // thin bare legs, socks, red shoes
    limb(F, { col: C.skin }, J, [s + 'Leg', s + 'Shin'], [[k * 19, 226, 0], J[s + 'Shin'], [k * 28, 46, -1]], [[11, 12], [9, 9.5], [7, 7.5]]);
    F.loft(F.part({ col: C.cream, w: s + 'Shin' }), [box8(k * 28, 20, -1.5, 8.2, 8.6, 0.4), box8(k * 27, 52, -1, 8.4, 8.8, 0.4)]);
    const x = k * 28, shoe = F.part({ col: C.shoe, w: s + 'Foot' });
    const sec = (z, w, hh) => [[x - w, 0, z], [x + w, 0, z], [x + w, hh, z], [x - w, hh, z]];
    F.loft(shoe, [sec(-13, 9, 21), sec(6, 10, 21), sec(32, 8, 7)]);
    // bare arms out of short sleeves, fists
    const a = J[s + 'Arm'], e = J[s + 'ForeArm'], h = J[s + 'Hand'];
    limb(F, { col: C.skin }, J, [s + 'Arm', s + 'ForeArm'], [a, e, h], [[9, 9], [8, 8], [6.5, 6.5]]);
    const m = [0, 1, 2].map(q => lerp(a[q], e[q], 0.52));
    F.loft(F.part({ col: C.cream, w: s + 'Arm' }), [ringAt([a[0], a[1] + 3, a[2]], [1, 0, 0], [0, 0, 1], 12.5, 12.5, 6, Math.PI / 6), ringAt(m, [1, 0, 0], [0, 0, 1], 12, 12, 6, Math.PI / 6)]);
    F.loft(F.part({ col: C.skin, w: s + 'Hand' }), [box8(h[0], h[1] + 2, h[2], 6.5, 7.5, 0.3), box8(h[0], h[1] - 14, h[2] + 1, 8, 9.5, 0.3), box8(h[0], h[1] - 21, h[2] + 1, 6, 7.5, 0.3)]);
  }
  // the slingshot in his right fist: a fork of wood and its band
  {
    const h = J.RightHand, wp = F.part({ col: C.wood, w: 'RightHand', set: 'soft', rim: 0 }), z = h[2] + 3;
    F.bar(wp, [h[0], h[1] - 2, z], [h[0], h[1] - 40, z], 5, 5); F.bar(wp, [h[0], h[1] - 38, z], [h[0] - 11, h[1] - 62, z], 4.5, 4.5); F.bar(wp, [h[0], h[1] - 38, z], [h[0] + 11, h[1] - 62, z], 4.5, 4.5);
    const bp = F.part({ col: '#07070b', w: 'RightHand', set: 'soft', rim: 0, unlit: 1 });
    F.bar(bp, [h[0] - 11, h[1] - 61, z], [h[0], h[1] - 50, z + 3], 1.6, 1.6); F.bar(bp, [h[0], h[1] - 50, z + 3], [h[0] + 11, h[1] - 61, z], 1.6, 1.6);
  }
}

const face = makeFace({
  D,
  expr: {
    neutral: { op: 0.85, brow: 2, tilt: -1, mouth: [-5, 0, 0, 1, 1.5, 0] },
    joy: { op: 0.55, brow: 3, tilt: -2, cheeks: 1, mouth: [0, 0, 0.85, 1, 0, 1] },
    surprise: { op: 1.45, brow: 9, tilt: -3, mouth: [0, 0, 0.75, 0.8, 0, 0] },
    sad: { op: 0.75, brow: 2, tilt: -7, look: [0, 2], mouth: [5, 0, 0, 1, -1, 0] },
    anger: { op: 0.7, brow: -5, tilt: 7, mouth: [4, 0, 0, 0.85, -1, 0] },
  },
  phrases: ['А я попаду вон в тот фонарь!', 'Спорим, не догонишь?', 'Это не я. Ну… почти не я.'],
  // freckles over the nose and cheeks
  over(g) {
    g.fillStyle = '#a9744c';
    for (const [x, y] of [[12, 41], [19, 46], [26, 41], [33, 47], [-13, 42], [-20, 46], [-27, 41], [-33, 46], [5, 37], [-5, 38]]) { g.beginPath(); g.arc(x, y, 1.5, 0, 7); g.fill(); }
  },
});

start({
  name: 'Тим', J, forms, face, head: HEAD,
  soles: { LeftFoot: SOLE(1), RightFoot: SOLE(-1) },
  back: ['#2b3550', '#c8553a'], ground: '#272b3d',
  // his carriage: the chest out, the chin up
  posture: [['Spine2', -3], ['Head', -4]],
  armPoses: {
    // the drawing's pose: a fist on the hip, the slingshot held up in the other hand
    sling: { Left: { arm: [0.52, -0.84, -0.15], fore: [-0.55, -0.8, 0.22] }, Right: { arm: [-0.5, -0.85, 0.16], fore: [-0.22, 0.92, 0.3] } },
  },
  armOut: 0.24,
  EXPR_RU: { neutral: 'улыбка', joy: 'радость', surprise: 'удивление', sad: 'грусть', anger: 'злость' },
  CLIPS: {
    stand: { ru: 'стоит с рогаткой', arms: 'sling', cam: [0.7, 4.0] },
    walk: { ru: 'идёт', motion: 'walk', travel: true, cam: [0.7, 4.4] },
    run: { ru: 'бежит', motion: 'run', travel: true, cam: [0.7, 4.6] },
    jump: { ru: 'прыгает', motion: 'jump', once: true, followY: 0.5, cam: [0.8, 5.0] },
    sneak: { ru: 'крадётся', motion: 'sneak', travel: true, upright: 0.4, cam: [0.65, 4.4] },
    wave: { ru: 'машет', motion: 'wave', once: true, cam: [0.7, 4.2] },
    talk: { ru: 'говорит', motion: 'idle', upright: 1, arms: 'sling', cam: [1.0, 2.4], hidden: true },
    rest: { ru: 'прямо', posture: [], hidden: true, cam: [0.7, 4.0] },
  },
});
