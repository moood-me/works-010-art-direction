// Тим (style С5, «инди») in 3D: the indie constructor's simple forms on SOMA's joints, built from the very numbers
// the drawing was made of (styles/s5-indie/tools/cast.py `tim`: stacks of elliptic rings, tubes, spheres), coloured
// with the drawing's paints, the face signs drawn by the drawing's own code. Everything shared with the style's other
// characters is in core.js (the figure) and face.js / live.js (the face); here are only his numbers.
import { S, P, rings, ringTable, surf, lineRound, chain, start } from './core.js';
import { clamp, ell, oell, sph, rbox, inter, capsule, horn, add, sub, mul } from './forms.js';
import { makeFace, mouths, EXPR_RU } from './face.js';

const HEAD_Y = -205;                       // the head's centre in the drawing (cast.tim: translate(0,-205))
// the drawing's paints (cast.tim, geo.py)
const C = {
  hair: '#d8893d', cap: '#3d6db0', brim: '#335d99', tee: '#d65a43', stripe: '#f3e3c4', shorts: '#c39a6a', shoe: '#d2463b', sock: '#f3efe6',
  skin: '#f7d7bf', skinSh: '#efbfa6', line: '#4a3036', wood: '#9a6a3c', plaster: '#f1d3a6',
};
// cast.tim's volumes
const HEAD = [[-64, 0, 0, 0, -2], [-58, 38, 36, 0, -2], [-40, 62, 58, 0, -2], [-14, 70, 64, 0, -1], [10, 70, 62, 0, 2],
  [30, 64, 56, 0, 5], [46, 48, 42, 0, 8], [56, 26, 26, 0, 9], [59, 0, 0, 0, 9]];
const HAIRLINE = [[-2.6, 30], [-2.1, 20], [-1.8, -6], [-1.45, -8], [-1.3, -20], [-1.05, -18], [-0.9, -30], [-0.72, -14], [-0.55, -30],
  [-0.36, -10], [-0.18, -30], [0, -12], [0.18, -30], [0.36, -12], [0.55, -30], [0.72, -14], [0.9, -30], [1.05, -18],
  [1.3, -20], [1.45, -8], [1.8, -6], [2.1, 20], [2.6, 30]];
const CAPLINE = [[-3.0, -8.5], [-2.4, -12], [-1.6, -28], [-0.8, -36], [0, -38], [0.8, -36], [1.6, -28], [2.4, -12], [3.0, -8.5]];
const BRIM = [[-16, 0, 0, 0, -62], [-14, 30, 18, 0, -72], [-9, 32, 22, 0, -80], [-6, 0, 0, 0, -84]];
const TEE = [[-150, 0, 0], [-147, 30, 22], [-138, 40, 28], [-110, 41, 30], [-86, 44, 31], [-80, 0, 0]];
const SHORTS = [[-92, 0, 0], [-90, 40, 29], [-76, 42, 30], [-70, 0, 0]];
const shoe = X => [[-24, 0, 0, X, 4], [-21, 13, 14, X, 4], [-10, 15, 20, X, 8], [-2, 15, 22, X, 10], [1, 0, 0, X, 10]];
const HO = [0, HEAD_Y, 0], headT = ringTable(HEAD);

// the skeleton: SOMA's joints (no fingers), placed on the drawing (units). The arms as drawn: behind his back
const JU = {
  Hips: [0, -80, 0], Spine1: [0, -98, 0], Spine2: [0, -114, 0], Chest: [0, -130, 0], Neck1: [0, -144, 1], Neck2: [0, -148, 2], Head: [0, -152, 2],
  HeadEnd: [0, -274, -2], Jaw: [0, -165, 30], LeftEye: [27, -195, 58], RightEye: [-27, -195, 58],
};
for (const [s, k] of [['Left', 1], ['Right', -1]]) {
  JU[s + 'Shoulder'] = [k * 14, -142, 0]; JU[s + 'Arm'] = [k * 38, -140, 2]; JU[s + 'ForeArm'] = [k * 48, -110, -10]; JU[s + 'Hand'] = [k * 18, -96, -40];
  JU[s + 'Leg'] = [k * 17, -78, 0]; JU[s + 'Shin'] = [k * 17.7, -44, 0]; JU[s + 'Foot'] = [k * 18.4, -18, 0]; JU[s + 'ToeBase'] = [k * 18.7, -5, 16]; JU[s + 'ToeEnd'] = [k * 18.7, -3, 30];
}
// keep what is above (keep = 1) or below (−1) a height of the drawing
const level = (Y, keep) => (x, y, z) => keep * (-Y * S - y);
const slab = (Y, h) => (x, y, z) => Math.abs(-y / S - Y) * S - h * S;

// a part: [group, bone | [bone, bone] | weights(x,y,z), distance, paint, shade paint?]
function parts(J) {
  const out = [], put = (g, b, f, c, sh) => out.push([g, b, f, c, sh]);
  const bodyW = chain(J, ['Hips', 'Spine1', 'Spine2', 'Chest']);
  // head: the drawing's ring stack; a small nose that shows in profile (cast.small_nose)
  put('head', 'Head', rings(HEAD, { o: HO }), C.skin, C.skinSh);
  put('head', 'Head', ell(P(0, HEAD_Y + 22, 60), [4.5 * S, 5.5 * S, 5.5 * S]), C.skin, C.skinSh);
  // ears that stick out: a disc on each side of the head, turned outward, a line inside (cast.tim: 9 wide from the
  // front, 15 from the side, 15 high; set a little further back than by the numbers, as the drawing's turn sets them)
  for (const k of [-1, 1]) {
    const e = surf(headT, k * 1.8, 10, -3, HO), a = 0.95, c = [e[0] + k * 10, e[1], e[2]];
    const n = [k * Math.sin(a), 0, Math.cos(a)], t = [k * Math.cos(a), 0, -Math.sin(a)];
    put('ears', 'Head', oell(P(...c), n, [0, 1, 0], 3.6 * S, 15 * S, 15 * S), C.skin, C.skinSh);
    const q = (u, v) => P(c[0] + n[0] * 3.3 + t[0] * u, c[1] + v, c[2] + n[2] * 3.3 + t[2] * u);
    put('earline', 'Head', horn(q(1, -7), q(8, -1), q(1, 6), 0.8 * S, 0.8 * S, 8), C.line);
  }
  // short ginger hair: the head grown by 6 units, kept above the hairline with its tufts
  const hairY = lineRound(HAIRLINE), capY = lineRound(CAPLINE);
  // how far a place is above a line round the head (hairline, cap's edge): the height over the line, made a true
  // distance where the line runs steeply (the tufts); and a thin dark tube along such a line — the drawing's stroke
  const over = (line, x, y, z) => {
    const X = x / S, Y = -y / S - HEAD_Y, Z = z / S, [w, d, cx, cz] = headT.at(clamp(Y, headT.y0, headT.y1));
    const phi = Math.atan2((X - cx) / Math.max(w, 1), (Z - cz) / Math.max(d, 1)), e = 0.012;
    const sl = (line(phi + e) - line(phi - e)) / (2 * e * Math.max((w + d) / 2, 8));
    return [(Y - line(phi)) / Math.hypot(1, sl), Y, phi];
  };
  const above = line => (x, y, z) => over(line, x, y, z)[0] * S;
  const edge = (line, shell, r) => (x, y, z) => Math.hypot(over(line, x, y, z)[0] * S, shell(x, y, z)) - r * S;
  // (the hair thins toward its edge, so the tufts lie on the forehead as drawn and don't stand as a step)
  const cap6 = rings(HEAD, { out: 6, o: HO });
  const thin = (x, y, z) => { const [dl] = over(hairY, x, y, z), t = clamp(-dl / 12, 0, 1); return cap6(x, y, z) + 4.2 * S * (1 - t) * (1 - t); };
  put('hair', 'Head', inter(thin, above(hairY), 0.6 * S), C.hair);
  put('edges', 'Head', edge(hairY, rings(HEAD, { out: 1.6, o: HO }), 1.15), C.line);
  put('edges', 'Head', edge(capY, rings(HEAD, { out: 8.6, o: HO }), 1.15), C.line);
  // the cap, worn backwards: a dome over the hair, its brim out at the back, a button on top
  put('cap', 'Head', inter(rings(HEAD, { out: 9, o: HO }), above(capY), 1.2 * S), C.cap);
  put('cap', 'Head', ell(P(0, HEAD_Y - 72.5, -2), [6.5 * S, 2.6 * S, 6.5 * S]), C.cap);
  put('brim', 'Head', rings(BRIM, { o: HO }), C.brim);
  // the tee with two stripes, the shorts
  put('tee', bodyW, rings(TEE), C.tee);
  for (const Y of [-118, -104]) put('stripes', bodyW, inter(rings(TEE, { out: 0.5 }), slab(Y, 3.5), 0.3 * S), C.stripe);
  put('shorts', 'Hips', rings(SHORTS), C.shorts);
  // the slingshot out of the back pocket
  for (const [a, b] of [[[24, -86], [24, -104]], [[24, -104], [16, -120]], [[24, -104], [32, -120]]])
    put('sling', bodyW, capsule(P(a[0], a[1], -33.5), P(b[0], b[1], -33.5), 2.6 * S), C.wood);
  for (const [s, k] of [['Left', 1], ['Right', -1]]) {
    const X = k * 17;
    // the shorts' legs (cut straight at the hem), bare legs, socks, sneakers with a white sole line
    put('shorts', s + 'Leg', inter(capsule(P(k * 19, -78, 0), P(k * 19 * 1.08, -52, 0), 13 * S), level(-56, 1), 0.8 * S), C.shorts);
    put('legs', [s + 'Leg', s + 'Shin'], capsule(J[s + 'Leg'], J[s + 'Foot'], 7.5 * S), C.skin, C.skinSh);
    put('socks', s + 'Shin', inter(capsule(P(X * 1.075, -26, 0), P(X * 1.08, -14, 0), 8.3 * S), level(-27, -1), 0.5 * S), C.sock);
    put('shoes', s + 'Foot', rings(shoe(X * 1.1)), C.shoe);
    put('soles', s + 'Foot', inter(rings(shoe(X * 1.1), { out: 0.5 }), slab(-3, 2), 0.3 * S), C.sock);
    // arms: bare tubes 15 wide, a short sleeve at the shoulder, round hands (cast.tim)
    put('arms', s + 'Arm', capsule(J[s + 'Arm'], J[s + 'ForeArm'], 7.5 * S), C.skin, C.skinSh);
    put('arms', s + 'ForeArm', capsule(J[s + 'ForeArm'], J[s + 'Hand'], 7.5 * S), C.skin, C.skinSh);
    put('sleeves', s + 'Arm', capsule(P(k * 38, -140, 2), P(k * 44, -126, -2), 9.5 * S), C.tee);
    const dir = sub(J[s + 'Hand'], J[s + 'ForeArm']), L = Math.hypot(...dir);
    put('hands', s + 'Hand', sph(add(J[s + 'Hand'], mul(dir, 6 * S / L)), 9.5 * S), C.skin, C.skinSh);
  }
  // a plaster on his right knee
  put('plaster', ['RightLeg', 'RightShin'], rbox(P(-17.7, -42, 7.4), [6 * S, 4 * S, 1.2 * S], 1.1 * S), C.plaster);
  return out;
}

// ———————————— the face: cast.tim's signs and expressions ————————————
const M = mouths(9);
const E0 = { happy: 0, big: 1, iris: 0.78, tear: 0 };
const face = makeFace({
  head: HEAD, rect: [-76, -70, 152, 136],
  eye: { phi: 0.42, y: 10, rx: 10.5, ry: 13 }, brow: { y: -13, w: 18, col: '#9b5a2a', th: 1.6, arch: 3 },
  cheek: { phi: 0.62, y: 26, r: 11, col: '#f08a7a', op: 0.5 }, nose: { y: 24 }, mouth: { phi: 0.08, y: 38, w: 9, lw: 1.13 },
  irisCol: '#2f2426', lash: 1.2, flick: false, bags: false,
  // freckles under the eyes; a plaster on the cheek
  under(ctx, surf) {
    ctx.fillStyle = '#b86a3e';
    for (const [p, y] of [[-0.5, 22], [-0.38, 27], [-0.62, 28], [0.5, 22], [0.38, 27], [0.62, 28]]) { const [x, yy] = surf(p, y); ctx.beginPath(); ctx.arc(x, yy, 1.7, 0, 7); ctx.fill(); }
  },
  over(ctx, surf, sw) {
    const [x, y, f] = surf(0.8, 31);
    ctx.save(); ctx.translate(x, y); ctx.rotate(-25 * Math.PI / 180); ctx.scale(Math.max(f, 0.4), 1);
    ctx.beginPath(); ctx.roundRect(-10, -5, 20, 10, 4); ctx.fillStyle = '#f1d3a6'; ctx.fill(); ctx.lineWidth = sw * 0.7; ctx.strokeStyle = '#4a3036'; ctx.stroke();
    ctx.fillStyle = '#e3b986'; ctx.fillRect(-3.5, -3.5, 7, 7);
    ctx.restore();
  },
  // lids (inner, outer), look (the highlights' shift), brows (his right: height, tilt; his left: height, tilt)
  expr: {
    neutral: { ...E0, lid: [0.05, 0.22], look: [3, 0], brow: [-2, 0, -7, -4], mouth: M.smirk },     // one brow up: up to something
    joy: { ...E0, lid: [0, 0], happy: 1, look: [3, 0], brow: [-4, 3], mouth: M.grin },
    surprise: { ...E0, lid: [0, 0], big: 1.15, iris: 0.72, look: [3, -1], brow: [-12, 0], mouth: M.o },
    sad: { ...E0, lid: [0.1, 0.45], look: [3, 2], brow: [-3, -9], mouth: M.frown, tear: 1 },
    anger: { ...E0, lid: [0.48, 0.1], look: [3, 0], brow: [4, 9], mouth: M.clench },
  },
  phrases: ['А спорим, попаду?', 'Это не я. Честно.', 'Ну… почти не я.', 'Тихо! Кто-то идёт.', 'Бежим!'],
});

start({
  name: 'Тим', C, HEAD_Y, HEAD, JU, parts, face, EXPR_RU,
  bounds: [[-0.26, -0.02, -0.3], [0.26, 0.74, 0.22]],
  GRID: { hair: 0.0016, edges: 0.0013, cap: 0.0022, ears: 0.002, earline: 0.0009, stripes: 0.0022, soles: 0.0018, sling: 0.0015, plaster: 0.0012, socks: 0.002, hands: 0.002, head: 0.0025 },
  BLEND: { head: 3 * S, arms: 1.5 * S, shorts: 2.5 * S, sling: 1 * S },
  NO_LINE: new Set(['edges', 'earline', 'stripes', 'soles']), THIN: new Set(['plaster']),
  GROUND: ['shoes', 'soles'],
  THR: { head: 0.1, ears: 0.1 },      // the skin's shade is a narrower crescent than the clothes' (the drawing: off .05 against .09)
  shadow: [52, 38], headR: 72, armOut: 0.3,
  // the head's tilt on each expression (cast.tim)
  TILT: { neutral: -6, joy: -3, surprise: -2, sad: 6, anger: -4 },
  // motions: Kimodo's, from engine/motions. cam: where the viewer looks [height, distance]
  CLIPS: {
    stand: { ru: 'стоит', cam: [0.36, 2.0] },
    walk: { ru: 'идёт', motion: 'walk', travel: true, free: true, cam: [0.36, 2.2] },
    run: { ru: 'бежит', motion: 'run', travel: true, free: true, cam: [0.36, 2.4] },
    sneak: { ru: 'крадётся', motion: 'sneak', travel: true, free: true, cam: [0.36, 2.2] },
    jump: { ru: 'прыгает', motion: 'jump', free: true, cam: [0.42, 2.5] },
    wave: { ru: 'машет', motion: 'wave', free: true, cam: [0.38, 2.1] },
    look: { ru: 'оглядывается', motion: 'idle', look: true, upright: 0.85, cam: [0.42, 1.6] },
  },
});
