// Кира (style С5, «инди») in 3D: the indie constructor's simple forms on SOMA's joints, built from the very numbers
// the drawing was made of (styles/s5-indie/tools/kira.py: stacks of elliptic rings, limbs, spheres), coloured with the
// drawing's paints, the face signs drawn by the drawing's own code. Everything shared with the style's other
// characters is in core.js (the figure) and face.js / live.js (the face); here are only her numbers.
// Her slouch is in the rest pose: the drawing leans the upper body (extra.lean) and pushes the head forward and down;
// here the same turns are made in space — the forms are built upright from the numbers and then turned.
import { S, P, rings, ringTable, surf, lineRound, chain, start } from './core.js';
import { clamp, lerp, ell, oell, sph, torus, inter, cone, capsule, horn, add, sub, mul } from './forms.js';
import { EXPR_RU } from './face.js';
import { face, HEAD, HEAD_Y } from './face_def.js';

// the drawing's paints (kira.py)
const C = {
  hair: '#2f2937', hoodie: '#5b3558', hood: '#4c2b4b', trous: '#3d3a45', boot: '#35303a', sole: '#1f1c23', acid: '#d2ea3e', pad: '#2b2730',
  skin: '#f7d7bf', skinSh: '#efbfa6', line: '#4a3036', cord: '#e9e1d4', ring: '#b9c0c6',
};
// kira.py's volumes
const BACK = [[-48, 0, 0, 0, -4], [-44, 54, 54, 0, -5], [-20, 67, 62, 0, -8], [10, 69, 60, 0, -10], [30, 65, 52, 0, -12], [44, 52, 40, 0, -12], [50, 0, 0, 0, -12]];
const HAIRLINE = [[-3.1, 40], [-2.6, 38], [-2.1, 30], [-1.85, 10], [-1.6, -10], [-1.4, -4], [-1.25, 8], [-1.12, -8], [-0.95, -24], [-0.78, -36],
  [-0.62, -30], [-0.5, -18], [-0.4, -24], [-0.26, -6], [-0.16, -14], [-0.02, 6], [0.08, -4], [0.2, 18], [0.3, 8], [0.44, 27],
  [0.54, 17], [0.68, 31], [0.8, 20], [0.95, 33], [1.08, 16], [1.22, 30], [1.4, 10], [1.6, 28], [1.8, 14], [2.1, 32], [2.6, 38], [3.1, 40]];
const HOODIE = [[-264, 0, 0, 0, -5], [-260, 28, 25, 0, -5], [-250, 41, 32, 0, -6], [-224, 47, 37, 0, -4], [-190, 52, 39, 3, 2],
  [-164, 56, 41, 5, 6], [-150, 54, 39, 6, 7], [-146, 0, 0, 6, 7]];
const HOOD = [[-276, 0, 0, 0, -20], [-270, 30, 18, 0, -26], [-254, 42, 24, 0, -32], [-236, 36, 20, 0, -30], [-226, 0, 0, 0, -26]];
const NK = [[-270, 34, 29, 0, -6], [-250, 43, 34, 0, -6], [-224, 49, 39, 0, -4]];
const boot = (X, Z) => [[-48, 0, 0, X, Z + 1], [-45, 13, 13, X, Z + 1], [-32, 14, 15, X, Z + 2], [-20, 16, 21, X, Z + 7], [-9, 17, 26, X, Z + 10], [-7, 0, 0, X, Z + 10]];
const sole = (X, Z) => [[-10, 0, 0, X, Z + 10], [-9, 18.5, 27.5, X, Z + 10], [0, 18.5, 27.5, X, Z + 10], [1, 0, 0, X, Z + 10]];
const HO = [0, HEAD_Y, 0], headT = ringTable(HEAD), backT = ringTable(BACK), hoodieT = ringTable(HOODIE), nkT = ringTable(NK);

// ———————————— the slouch: turns in space (metres, y up) ————————————
const rad = a => a * Math.PI / 180;
const Rx = a => [[1, 0, 0], [0, Math.cos(a), -Math.sin(a)], [0, Math.sin(a), Math.cos(a)]];       // + : the top goes forward
const Rz = a => [[Math.cos(a), -Math.sin(a), 0], [Math.sin(a), Math.cos(a), 0], [0, 0, 1]];       // + : the top goes to her right
const mm = (A, B) => A.map((r, i) => [0, 1, 2].map(j => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j]));
const mv = (A, v) => A.map(r => r[0] * v[0] + r[1] * v[1] + r[2] * v[2]);
const tr = A => [0, 1, 2].map(i => [0, 1, 2].map(j => A[j][i]));
// kira.py, neutral: lean(side −3.5°, forward 7°) about (6, −150); the head at translate(13 in profile, −300), turned by
// the tilt 7° seen from the front and 4° forward seen from the side
const LEAN = mm(Rx(rad(7)), Rz(rad(3.5))), PIV = P(6, -150, 6);
const TILT0 = 7, HEADR = mm(Rx(rad(4)), Rz(rad(-TILT0))), C0 = P(0, HEAD_Y, 0), FWD = P(0, 0, 13);
const lean = p => add(PIV, mv(LEAN, sub(p, PIV)));
const HR = mm(LEAN, HEADR), HRt = tr(HR), LEANt = tr(LEAN);
const headPlace = p => lean(add(add(C0, FWD), mv(HEADR, sub(p, C0))));       // the upright drawing's head → where it is
const headBack = p => add(C0, mv(tr(HEADR), sub(sub(add(PIV, mv(LEANt, sub(p, PIV))), FWD), C0)));
const up = f => (x, y, z) => { const q = add(PIV, mv(LEANt, sub([x, y, z], PIV))); return f(q[0], q[1], q[2]); };   // an upper-body form, leaned
const hd = f => (x, y, z) => { const q = headBack([x, y, z]); return f(q[0], q[1], q[2]); };                          // a head form, placed

// the skeleton: SOMA's joints (no fingers), placed on the drawing (units), the upper ones leaned with the body
const UP = {
  Spine1: [5, -176, 4], Spine2: [3, -200, 1], Chest: [1, -226, -2], Neck1: [0, -244, -3], Neck2: [0, -248, 0], Head: [0, -252, 4],
  LeftShoulder: [14, -252, -2], LeftArm: [41, -250, -2], LeftForeArm: [63, -200, 0], LeftHand: [60, -150, 12],
  RightShoulder: [-14, -252, -2], RightArm: [-41, -250, -2], RightForeArm: [-66, -204, -6], RightHand: [-28, -176, 38],
};
const HEADJ = { HeadEnd: [0, -368, -3], Jaw: [0, -262, 30], LeftEye: [24, -287, 50], RightEye: [-24, -287, 50] };
// the legs as drawn: the weight on her left, the right knee out
const JU = {
  Hips: [5, -154, 5],
  LeftLeg: [22, -152, 4], LeftShin: [24, -96, 4], LeftFoot: [22, -36, 0], LeftToeBase: [22, -6, 18], LeftToeEnd: [22, -4, 36],
  RightLeg: [-12, -152, 4], RightShin: [-33, -98, 14], RightFoot: [-36, -36, 2], RightToeBase: [-36, -6, 20], RightToeEnd: [-36, -4, 38],
};
const unP = p => [p[0] / S, -p[1] / S, p[2] / S];
for (const [b, p] of Object.entries(UP)) JU[b] = unP(lean(P(...p)));
for (const [b, p] of Object.entries(HEADJ)) JU[b] = unP(headPlace(P(...p)));

const slabY = (Y, h) => (x, y, z) => Math.abs(-y / S - Y) * S - h * S;

// a part: [group, bone | [bone, bone] | weights(x,y,z), distance, paint, shade paint?]
function parts(J) {
  const out = [], put = (g, b, f, c, sh) => out.push([g, b, f, c, sh]);
  const bodyW = chain(J, ['Hips', 'Spine1', 'Spine2', 'Chest']);
  // head: the drawing's ring stack; a small nose that shows in profile (cast.small_nose)
  put('head', 'Head', hd(rings(HEAD, { o: HO })), C.skin, C.skinSh);
  put('head', 'Head', hd(ell(P(0, HEAD_Y + 26, 52), [4 * S, 5 * S, 5 * S])), C.skin, C.skinSh);
  // the ear on the open side (her right), two small rings in it
  {
    const e = surf(headT, -1.72, 12, 0.5, HO);
    put('ears', 'Head', hd(oell(P(...e), [-1, 0, 0.03], [0, 1, 0], 3.2 * S, 11 * S, 8.5 * S)), C.skin, C.skinSh);
    for (const dy of [-6, 1]) put('rings', 'Head', hd(torus(P(e[0] - 3.4, e[1] + dy, e[2] - 4.5), 2.3 * S, 0.75 * S, 'x')), C.ring);
  }
  // hair. Over the head: the head grown by 6 units, kept above the hairline — a parting on her right, the fringe in
  // choppy locks across the face and over her left eye; it thins toward its edge, and a dark line runs along it
  const hairY = lineRound(HAIRLINE);
  const over = (line, x, y, z) => {
    const X = x / S, Y = -y / S - HEAD_Y, Z = z / S, [w, d, cx, cz] = headT.at(clamp(Y, headT.y0, headT.y1));
    const phi = Math.atan2((X - cx) / Math.max(w, 1), (Z - cz) / Math.max(d, 1)), e = 0.012;
    const sl = (line(phi + e) - line(phi - e)) / (2 * e * Math.max((w + d) / 2, 8));
    return (Y - line(phi)) / Math.hypot(1, sl);
  };
  const cap6 = rings(HEAD, { out: 6, o: HO });
  const thin = (x, y, z) => { const t = clamp(-over(hairY, x, y, z) / 12, 0, 1); return cap6(x, y, z) + 4.2 * S * (1 - t) * (1 - t); };
  put('hair', 'Head', hd(inter(thin, (x, y, z) => over(hairY, x, y, z) * S, 0.6 * S)), C.hair);
  const shell = rings(HEAD, { out: 1.6, o: HO });
  put('edges', 'Head', hd((x, y, z) => Math.hypot(over(hairY, x, y, z) * S, shell(x, y, z)) - 1.1 * S), C.line);
  // (a smooth crown: the ring stack's own top is uneven where the rings shrink to a point)
  put('hair', 'Head', hd(ell(P(0, HEAD_Y - 58.6, -3), [24 * S, 9.4 * S, 24 * S])), C.hair);
  // the back of the hair: a mass behind the head (kept behind the ears: the drawing lays it behind the head), cut
  // unevenly — spikes stick out under it; two tufts on the crown
  put('hair', 'Head', hd(inter(rings(BACK, { o: HO }), (x, y, z) => z + 17 * S, 4 * S)), C.hair);
  for (const [phi, y, dx, dy, w] of [[-2.7, 32, 3, 20, 20], [-2.0, 30, 6, 19, 20], [2.0, 30, 6, 21, 20], [2.7, 32, 3, 19, 20], [3.14, 34, 0, 20, 22]]) {
    const b = surf(backT, phi, y - 6, -6, HO);
    put('hair', 'Head', hd(cone(P(...b), P(b[0] + Math.sin(phi) * (dx + 6), b[1] + dy + 6, b[2] + Math.cos(phi) * (dx + 6)), w / 2 * S, 1 * S)), C.hair);
  }
  for (const [phi, y, dx, dy] of [[-0.15, -62, 6, -13], [0.75, -55, 12, -9]]) {
    const b = surf(headT, phi, y, 5, HO);
    put('hair', 'Head', hd(cone(P(b[0], b[1] + 6, b[2]), P(b[0] + dx * 1.3, b[1] + dy, b[2]), 7.5 * S, 1 * S)), C.hair);
  }
  // an oversized hoodie on narrow shoulders, its hood on the back; the hem's line, two cords, a pouch pocket (its outline)
  const hoodie = rings(HOODIE);
  put('hoodie', bodyW, up(hoodie), C.hoodie);
  put('hood', bodyW, up(rings(HOOD)), C.hood);
  put('hem', bodyW, up((x, y, z) => Math.hypot(hoodie(x, y, z), (-y / S + 157) * S) - 0.8 * S), C.line);
  for (const [a, y2] of [[-0.2, -214], [0.16, -206]]) {
    const s1 = surf(hoodieT, a, -256, 1.2), s2 = surf(hoodieT, a * 1.1, y2, 1.2), m = surf(hoodieT, a * 1.05, (-256 + y2) / 2, 1.6);
    put('cords', bodyW, up(horn(P(...s1), P(m[0] - 1, m[1], m[2]), P(...s2), 1.3 * S, 1.3 * S, 8)), C.cord);
  }
  const pouch = (x, y, z) => {
    const X = x / S, Y = -y / S, Z = z / S, [w, d, cx, cz] = hoodieT.at(clamp(Y, hoodieT.y0, hoodieT.y1));
    const phi = Math.atan2((X - cx) / w, (Z - cz) / d), a = lerp(0.5, 0.66, clamp((Y + 194) / 8, 0, 1));
    return Math.max(Math.abs(Y + 179) - 19, (Math.abs(phi) - a) * w) * S;
  };
  const skin1 = rings(HOODIE, { out: 0.6 });
  put('hem', bodyW, up((x, y, z) => Math.hypot(skin1(x, y, z), pouch(x, y, z)) - 1.0 * S), C.line);
  // headphones round the neck — the one acid thing: a band behind the neck, a cup on each side of the chest
  const bandAt = p => P(...surf(nkT, p, -248 + 22 * Math.cos(p), 3.5));
  for (let p = 0.8; p < 5.45; p += 0.155) put('phones', bodyW, up(capsule(bandAt(p), bandAt(p + 0.155), 3.3 * S)), C.acid);
  for (const k of [-1, 1]) {
    const a = k * 0.8, [w, d] = nkT.at(-231), c = surf(nkT, a, -231, 4), n = [Math.sin(a) / w, 0, Math.cos(a) / d], l = Math.hypot(...n);
    const nn = n.map(v => v / l);
    put('phones', bodyW, up(oell(P(...c), nn, [0, 1, 0], 4.5 * S, 16 * S, 13 * S)), C.acid);
    put('pads', bodyW, up(oell(P(c[0] + nn[0] * 3.4, c[1], c[2] + nn[2] * 3.4), nn, [0, 1, 0], 2.4 * S, 9.5 * S, 7 * S)), C.pad);
  }
  // arms in sleeves that widen to the cuff. Her right hand is deep in the pocket: that arm goes with the body; when
  // a motion frees the arms, the same sleeve is on the arm's own bones with a hand at its end
  const A1 = [[-41, -250, -2], [-66, -204, -6], [-28, -176, 38]].map(p => P(...p)), A2 = [[41, -250, -2], [63, -200, 0], [60, -150, 12]].map(p => P(...p));
  put('armR', bodyW, up(cone(A1[0], A1[1], 10.5 * S, 12 * S)), C.hoodie);
  put('armR', bodyW, up(cone(A1[1], A1[2], 12 * S, 11.5 * S)), C.hoodie);
  put('armRF', 'RightArm', up(cone(A1[0], A1[1], 10.5 * S, 12 * S)), C.hoodie);
  put('armRF', 'RightForeArm', up(cone(A1[1], A1[2], 12 * S, 11.5 * S)), C.hoodie);
  put('handRF', 'RightHand', up(sph(add(A1[2], mul(sub(A1[2], A1[1]), 0.16)), 8.5 * S)), C.skin, C.skinSh);
  // the left arm hangs — a sleeve too long, the hand half in it (a ball and a thumb)
  put('armL', 'LeftArm', up(cone(A2[0], A2[1], 10.5 * S, 11.5 * S)), C.hoodie);
  put('armL', 'LeftForeArm', up(cone(A2[1], A2[2], 11.5 * S, 13.5 * S)), C.hoodie);
  put('handL', 'LeftHand', up(sph(P(61, -138, 14), 8.5 * S)), C.skin, C.skinSh);
  put('handL', 'LeftHand', up(sph(P(55, -141, 20), 4.25 * S)), C.skin, C.skinSh);
  // long thin legs, heavy boots with acid laces
  for (const [s, X, Z] of [['Left', 22, 0], ['Right', -36, 2]]) {
    put('legs', s + 'Leg', capsule(J[s + 'Leg'], J[s + 'Shin'], 6.5 * S), C.trous);
    put('legs', s + 'Shin', capsule(J[s + 'Shin'], J[s + 'Foot'], 6.5 * S), C.trous);
    const bt = ringTable(boot(X, Z));
    put('boots', s + 'Foot', rings(boot(X, Z)), C.boot);
    put('soles', s + 'Foot', rings(sole(X, Z)), C.sole);
    for (const y of [-39, -31, -23]) put('laces', s + 'Foot', horn(P(...surf(bt, -0.5, y, 0.6)), P(...surf(bt, 0, y + 1, 2.2)), P(...surf(bt, 0.5, y + 2, 0.6)), 1.2 * S, 1.2 * S, 6), C.acid);
  }
  return out;
}

start({
  name: 'Кира', C, HEAD_Y, HEAD, JU, parts, face, EXPR_RU,
  bounds: [[-0.3, -0.02, -0.3], [0.3, 1.0, 0.3]],
  GRID: { hair: 0.0022, edges: 0.0013, ears: 0.002, rings: 0.0007, hem: 0.0011, cords: 0.0011, laces: 0.001, pads: 0.0015, phones: 0.002, handL: 0.002, handRF: 0.002 },
  BLEND: { head: 3 * S, hair: 2.5 * S, legs: 1.5 * S, armR: 2 * S, armRF: 2 * S, armL: 2 * S, handL: 1.5 * S, phones: 1.2 * S },
  NO_LINE: new Set(['edges', 'hem', 'cords', 'laces', 'rings']), THIN: new Set(['pads']),
  HOLD: new Set(['armR']), FREE: new Set(['armRF', 'handRF']),
  GROUND: ['boots', 'soles'],
  THR: { head: 0.1, ears: 0.1 },
  shadow: [60, 42], headR: 66, armOut: 0.36,
  // the head in the rest pose: pushed forward and bowed (see above)
  headInv: (x, y, z) => { const q = headBack([x, y, z]); return [q[0] / S, -q[1] / S - HEAD_Y, q[2] / S]; },
  headDir: v => mv(HR, v), headUnDir: v => mv(HRt, v), headC: unP(headPlace(C0)),
  // the head's tilt on each expression (kira.py); the neutral one is already in the rest pose
  TILT: { neutral: 7, joy: 4, surprise: -1, sad: 10, anger: 3 }, tiltRest: TILT0,
  // motions: Kimodo's, from engine/motions. cam: where the viewer looks [height, distance]
  CLIPS: {
    stand: { ru: 'стоит', cam: [0.47, 2.6] },
    walk: { ru: 'идёт, рука в кармане', motion: 'walk', travel: true, cam: [0.47, 2.8] },
    sneak: { ru: 'крадётся', motion: 'sneak', travel: true, free: true, cam: [0.45, 2.8] },
    idle: { ru: 'ждёт', motion: 'idle', upright: 0.8, cam: [0.47, 2.6] },
    look: { ru: 'оглядывается', motion: 'idle', look: true, upright: 0.8, cam: [0.62, 1.9] },
    sit: { ru: 'садится', motion: 'sit', travel: true, once: true, followY: 0.7, cam: [0.47, 2.7] },
  },
  LOOK_KEYS: [[0, 0], [1.0, 0], [1.5, 38], [2.9, 38], [3.5, -30], [4.1, -30], [4.6, 4], [5.0, 4]],
});
