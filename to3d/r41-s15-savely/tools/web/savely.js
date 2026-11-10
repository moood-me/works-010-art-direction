// Савелий Петрович, С15 «Нуар»: his own numbers. The head is the drawing's front and side outlines
// (sav_drawing.json, from styles/s15-noir/tools/cast.py by drawing.py); the body is the drawing's figure
// (figures.sav: a long stooped trunk in a waistcoat on short legs, 640 units tall) turned into flat-faced forms.
import * as THREE from 'three';
import { Forms, S, box8, chain, limb, headKit, skull, nose, ears, curtain, lerp } from './build.js';
import { makeFace } from './face.js';
import { start } from './noir.js';

const D = await (await fetch(new URL('./sav_drawing.json', import.meta.url))).json();
const C = { skin: D.skin, shirt: '#cfc9b8', vest: '#3f5a48', trous: '#4a4038', shoe: '#2a2320', tie: '#7a2e2a', hair: '#d6d3c8', mous: '#e4e1d6', brass: '#b08a3e', gold: '#c9a243', dial: '#efe7cf' };
const HEAD = { c: [0, 570, 10], s: 0.72 };
const K = headKit(D, HEAD);

const side = (s, p) => [s * p[0], p[1], p[2]];
const J = {
  Hips: [0, 268, 0], Spine1: [0, 300, 0], Spine2: [0, 350, 2], Chest: [0, 410, 2], Neck1: [0, 494, 0], Neck2: [0, 506, 2], Head: [0, 518, 4], HeadEnd: [0, 640, 4],
  Jaw: [0, 530, 12], LeftEye: [18, 566, 50], RightEye: [-18, 566, 50],
};
for (const [s, k] of [['Left', 1], ['Right', -1]]) Object.assign(J, {
  [s + 'Shoulder']: side(k, [16, 482, 0]), [s + 'Arm']: side(k, [50, 478, 0]), [s + 'ForeArm']: side(k, [62, 392, -2]), [s + 'Hand']: side(k, [63, 314, 4]),
  [s + 'Leg']: side(k, [20, 262, 0]), [s + 'Shin']: side(k, [21, 142, 2]), [s + 'Foot']: side(k, [21, 24, -3]), [s + 'ToeBase']: side(k, [21, 8, 28]), [s + 'ToeEnd']: side(k, [21, 8, 46]),
});

// the trunk by height: half width, half depth, how far forward its middle is, the half width of the shirt's strip
const TRUNK = [[240, 50, 33, 6, 9], [296, 53, 39, 11, 9], [340, 54, 41, 13, 5], [400, 55, 39, 9, 4], [450, 56, 35, 2, 9], [484, 54, 30, -3, 17], [504, 34, 23, -4, 21], [514, 18, 16, -3, 9]];
const SOLE = s => [[-13, 0, -16], [13, 0, -16], [11, 0, 42], [-11, 0, 42]].map(p => [p[0] + s * 21, p[1], p[2]]);

function forms(F) {
  // ——— head: skull and face in planes, the nose's wedge, ears, the white hair round the back, the neck
  skull(F, K, { col: C.skin });
  nose(F, K, { col: C.skin, set: 'soft' });
  ears(F, K, { col: C.skin, set: 'soft' });
  curtain(F, K, [[80, -44, -28], [91, -54, -14], [103, -60, -8], [113, -63, -4], [121, -65, 26], [130, -67, 12], [141, -68, 38], [153, -65, 18], [166, -61, 34], [180, -58, 22],
    [194, -61, 34], [207, -65, 18], [219, -68, 38], [230, -67, 12], [239, -65, 26], [247, -63, -4], [257, -60, -8], [269, -54, -14], [280, -44, -28]], { col: C.hair, thick: 14, yHold: 16 });
  const neckW = chain(J, ['Neck1', 'Neck2', 'Head']);
  F.loft(F.part({ col: C.skin, w: neckW }), [box8(0, 498, -1, 19, 17, 0.5), box8(0, 516, 2, 19, 17, 0.5), box8(0, 536, 6, 20, 18, 0.5)]);
  // ——— the trunk: the shirt, and the waistcoat as its faces painted green — the strip in the middle stays shirt
  const tw = chain(J, ['Hips', 'Spine1', 'Spine2', 'Chest']);
  const ring = ([y, w, d, zc, g]) => { const a = Math.max(w * 0.6, g + 4), b = d * 0.55; return [[g, d], [a, d], [w, b], [w, -b], [a, -d], [-a, -d], [-w, -b], [-w, b], [-a, d], [-g, d]].map(([x, z]) => [x, y, zc + z]); };
  F.loft(F.part({ col: C.shirt, w: tw }), TRUNK.map(ring), { cols: (i, j) => (i === 0 || i === TRUNK.length - 2 || j === 9) ? C.shirt : C.vest });
  // the bow tie: a dark red rhombus under the chin
  F.slab(F.part({ col: C.tie, w: 'Chest', rim: 0 }), [[-13, 486, 31], [0, 499, 29], [13, 486, 31], [0, 473, 35]], [0, 0, -4]);
  // ——— arms in shirt sleeves, angular hands; the watch in his left
  for (const [s, k] of [['Left', 1], ['Right', -1]]) {
    const a = J[s + 'Arm'], e = J[s + 'ForeArm'], h = J[s + 'Hand'];
    limb(F, { col: C.shirt }, J, [s + 'Arm', s + 'ForeArm'], [a, e, h], [[14, 15], [15, 15], [12, 12]]);
    const hp = F.part({ col: C.skin, w: s + 'Hand' });
    F.loft(hp, [box8(h[0], h[1] + 2, h[2], 6, 9, 0.3), box8(h[0], h[1] - 16, h[2] + 1, 7, 11, 0.3), box8(h[0] - k * 1, h[1] - 36, h[2] + 2, 4, 7, 0.3)]);
    F.bar(F.part({ col: C.skin, w: s + 'Hand' }), [h[0] - k * 2, h[1] - 6, h[2] + 9], [h[0] - k * 4, h[1] - 22, h[2] + 17], 6, 6);
    // legs, shoes
    limb(F, { col: C.trous }, J, [s + 'Leg', s + 'Shin'], [[J[s + 'Leg'][0], 270, 0], J[s + 'Shin'], [J[s + 'Foot'][0], 14, J[s + 'Foot'][2]]], [[20, 21], [16, 16], [13.5, 14]]);
    const x = k * 21, shoe = F.part({ col: C.shoe, w: s + 'Foot' });
    const sec = (z, w, hh) => [[x - w, 0, z], [x + w, 0, z], [x + w, hh, z], [x - w, hh, z]];
    F.loft(shoe, [sec(-16, 12, 22), sec(8, 13, 22), sec(42, 11, 7)]);
  }
  // the watch: a brass disc with a pale dial, in its own colours (a sign, as the drawing's accent)
  {
    const h = J.LeftHand, c = [h[0] - 5, h[1] - 22, h[2] + 15], n = [0, -0.26, 0.966], u = [1, 0, 0], v = [0, 0.966, 0.26];
    const circ = (r, off) => Array.from({ length: 16 }, (_, i) => { const a = i / 16 * 2 * Math.PI; return [0, 1, 2].map(q => c[q] + n[q] * off + u[q] * r * Math.cos(a) + v[q] * r * Math.sin(a)); });
    const wp = F.part({ col: C.gold, w: 'LeftHand', unlit: 1, set: 'props', rim: 0 });
    F.loft(wp, [circ(15, -2), circ(15, 2)]);
    const dp = F.part({ col: C.dial, w: 'LeftHand', unlit: 1, set: 'props', rim: 0 });
    F.poly(dp, circ(11, 2.4), c);
    const at = (a, b, off = 2.8) => [0, 1, 2].map(q => c[q] + n[q] * off + u[q] * a + v[q] * b);
    const hd = F.part({ col: '#07070b', w: 'LeftHand', unlit: 1, set: 'props', rim: 0 });
    F.quad(hd, at(-0.8, 0), at(0.8, 0), at(0.8, 8), at(-0.8, 8), c); F.quad(hd, at(0, -0.8), at(5, -3.8), at(5.6, -2.4), at(0.6, 0.8), c);
  }
  // ——— glasses: brass rings, the bridge, the temples to the ears (the lenses are laid on in attach)
  const ey = D.eye_y + 2, zg = K.frontZ(27, ey) + 10;
  const gp = F.part({ col: C.brass, w: 'Head', unlit: 1, set: 'props', rim: 0 });
  for (const sg of [-1, 1]) {
    const pt = (r, i) => { const a = i / 20 * 2 * Math.PI; return K.to(sg * 27 + r * Math.cos(a), ey + r * Math.sin(a), zg); };
    for (let i = 0; i < 20; i++) F.quad(gp, pt(14.2, i), pt(17.4, i), pt(17.4, i + 1), pt(14.2, i + 1));
    F.bar(gp, K.to(sg * 43.5, ey - 2, zg), K.to(sg * (K.dims(ey).w + 2), ey - 5, K.ZS - 36), 2.6 * HEAD.s, 2 * HEAD.s, [0, 1, 0]);
  }
  F.bar(gp, K.to(-10.5, ey - 2, zg), K.to(0, ey - 6, zg + 2), 2.6 * HEAD.s, 2 * HEAD.s, [0, 1, 0]); F.bar(gp, K.to(0, ey - 6, zg + 2), K.to(10.5, ey - 2, zg), 2.6 * HEAD.s, 2 * HEAD.s, [0, 1, 0]);
  // ——— the moustache: two white wings that the mouth moves
  const my = D.mouth.y;
  for (const [name, sg] of [['mouL', 1], ['mouR', -1]]) {
    const part = F.part({ col: C.mous, w: 'Head', set: name });
    const shp = [[0, my - 15, 9], [16, my - 13, 8], [32, my, 5], [39, my + 15, 3], [20, my + 5, 6], [0, my + 2, 8]];
    const front = shp.map(([x, y, o]) => K.to(sg * x, y, K.frontZ(Math.min(x, K.dims(y).w * 0.86), y) + o));
    const back = shp.map(([x, y]) => K.to(sg * x, y, K.frontZ(Math.min(x, K.dims(y).w * 0.86), y) - 4));
    const ins = K.to(sg * 16, my, K.frontZ(16, my) - 10);
    // two planes: the upper slope and the lower one, meeting along the wing's ridge
    const ridge = [K.to(sg * 1, my - 6, K.frontZ(0, my - 6) + 12), K.to(sg * 18, my - 3, K.frontZ(18, my - 3) + 10), front[3]];
    F.tri(part, front[0], front[1], ridge[0], ins); F.tri(part, front[1], ridge[1], ridge[0], ins); F.tri(part, front[1], front[2], ridge[1], ins); F.tri(part, front[2], front[3], ridge[1], ins);
    F.tri(part, ridge[0], ridge[1], front[5], ins); F.tri(part, ridge[1], front[4], front[5], ins); F.tri(part, ridge[1], front[3], front[4], ins);
    for (let i = 0; i < shp.length; i++) { const j = (i + 1) % shp.length; F.quad(part, front[i], front[j], back[j], back[i], ins); }
  }
}

// the face's own signs: the black under the brows (the drawing's sockets), the lines of the forehead and from the
// nose to the mouth
const face = makeFace({
  D,
  expr: {
    neutral: { op: 0.75, brow: -2, tilt: 3, up: 0, mouth: [1.5, 0, 0, 0.85, 0, 0] },
    joy: { op: 0.55, brow: 3, tilt: -2, cheeks: 1, up: 1, mouth: [-5, 0, 0, 1, 1.5, 0] },
    surprise: { op: 1.45, brow: 9, tilt: -3, up: 0.4, mouth: [0, 0, 0.75, 0.8, 0, 0] },
    sad: { op: 0.75, brow: 2, tilt: -7, look: [0, 2], up: -0.8, mouth: [5, 0, 0, 1, -1, 0] },
    anger: { op: 0.7, brow: -5, tilt: 7, up: -0.3, mouth: [4, 0, 0, 0.85, -1, 0] },
  },
  phrases: ['Часы не любят спешки, голубчик.', 'Так, посмотрим… пружина цела, а вот ось — погнута.', 'Приходите в четверг, будет ходить как новая.'],
  under(g, e, { shape, r }) {
    const ey = D.eye_y, by = ey - 15 + D.brow.y, d0 = r * 0.6;
    for (const sg of [-1, 1]) shape(g, [[sg * 9, by - d0], [sg * 46, by - 4 - d0], [sg * 46, ey + 5], [sg * 10, ey + 6]], '#07070b');
    shape(g, [[-16, -52], [18, -54], [18, -51], [-16, -49]], '#07070b'); shape(g, [[-20, -40], [22, -42], [22, -39.5], [-20, -37]], '#07070b');
    for (const sg of [-1, 1]) shape(g, [[sg * 26, 40], [sg * 36, 50, 's'], [sg * 38, 66], [sg * 33.5, 52, 's']], '#07070b');
  },
});

// the lenses: pale grey-blue with a streak of glare, the eyes dim behind them (the drawing: 0.9 of the lens over the eye)
function lensTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d'), k = 4;
  g.beginPath(); g.arc(64, 64, 63, 0, 7); g.clip();
  g.fillStyle = '#93a5a8'; g.fillRect(0, 0, 128, 128);
  g.fillStyle = '#dfe6e0'; g.beginPath(); g.moveTo(64 - 14 * k, 64 + 7 * k); g.lineTo(64 + 2 * k, 64 - 15 * k); g.lineTo(64 + 10 * k, 64 - 13 * k); g.lineTo(64 - 9 * k, 64 + 12 * k); g.fill();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace; return t;
}
function attach(I, { J: Jm }) {
  const ey = D.eye_y + 2, zg = K.frontZ(27, ey) + 9.6, tex = lensTexture();
  for (const sg of [-1, 1]) {
    const m = new THREE.Mesh(new THREE.CircleGeometry(15 * HEAD.s * S, 28), new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity: 0.84, depthWrite: false }));
    const p = K.to(sg * 27, ey, zg); m.position.set(p[0] * S - Jm.Head[0], p[1] * S - Jm.Head[1], p[2] * S - Jm.Head[2]);
    I.bones.Head.add(m); I.extra.push(m);
  }
}
// the moustache goes with the mouth: lifts in a smile, its ends droop in sadness
function onFace(I, Fc) {
  const e = Fc.e, c = e.mouth[0], open = e.mouth[2];
  for (const [name, sg] of [['mouL', 1], ['mouR', -1]]) {
    const g = I.movers[name]; if (!g) continue;
    g.rotation.z = sg * (-c * 0.022 + open * 0.05);
    g.position.y = g.userData.y0 ?? (g.userData.y0 = g.position.y); g.position.y += (e.up * 1.6 + open * 2.2) * HEAD.s * S;
  }
}

start({
  name: 'Савелий Петрович', J, forms, face, head: HEAD, attach, onFace,
  movers: { mouL: { bone: 'Head', pivot: K.to(0, D.mouth.y - 8, K.frontZ(0, D.mouth.y)) }, mouR: { bone: 'Head', pivot: K.to(0, D.mouth.y - 8, K.frontZ(0, D.mouth.y)) } },
  soles: { LeftFoot: SOLE(1), RightFoot: SOLE(-1) },
  back: ['#2c3a36', '#b99a4e'], ground: '#262b38',
  // his carriage: the back bent, the neck forward, the head bowed over the watch
  posture: [['Spine2', 12], ['Neck1', 16], ['Head', -13]],
  armPoses: {
    // the drawing's pose: the watch held up before him in the left hand, the right hand behind the back
    watch: { Left: { arm: [0.14, -0.97, -0.1], fore: [-0.45, 0.62, 0.64], roll: 0 }, Right: { arm: [-0.12, -0.97, -0.2], fore: [0.9, -0.15, -0.38] } },
    back: { Left: { arm: [0.12, -0.97, -0.2], fore: [-0.9, -0.15, -0.38] }, Right: { arm: [-0.12, -0.97, -0.2], fore: [0.9, -0.22, -0.38] } },
  },
  EXPR_RU: { neutral: 'строгий', joy: 'радость', surprise: 'удивление', sad: 'грусть', anger: 'злость' },
  CLIPS: {
    stand: { ru: 'смотрит на часы', arms: 'watch', cam: [0.85, 4.6] },
    walk: { ru: 'идёт, часы в руке', motion: 'walk', travel: true, speed: 0.8, arms: 'watch', cam: [0.85, 5.0] },
    stroll: { ru: 'идёт, руки за спиной', motion: 'walk', travel: true, speed: 0.8, arms: 'back', cam: [0.85, 5.0] },
    bow: { ru: 'кланяется', motion: 'bow', once: true, posture: [['Neck1', 8], ['Head', -4]], cam: [0.85, 5.0] },
    talk: { ru: 'говорит', motion: 'idle', upright: 1, arms: 'watch', posture: [['Spine2', 8], ['Neck1', 8], ['Head', -8]], cam: [1.3, 2.4], hidden: true },
    idle: { ru: 'ждёт', motion: 'idle', upright: 0.8, arms: 'back', cam: [0.85, 4.6] },
    wave: { ru: 'машет', motion: 'wave', once: true, cam: [0.85, 5.0] },
    rest: { ru: 'прямо', posture: [], hidden: true, cam: [0.85, 4.6] },
  },
});
