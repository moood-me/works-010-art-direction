// Аня, rubber-hose 1930s (style С11), in 3D on moood's SOMA skeleton — built the way Р11 (Савелий Петрович,
// to3d/r11-s11-savely) is: the expressive constructor of experiments/toon (gallery П2). The limbs are sweeps along an
// arc through shoulder–elbow–wrist (hip–knee–ankle) rebuilt every frame from the posed joints; the dress is a loft of
// the drawing's own widths and depths, its polka dots painted on it row by row; the head is the drawing's two balls
// (skull and cheeks) with the features laid on it as the drawing's Head.project() lays them; the hair is the drawing's
// "ball minus the bare face" grown into the bob. The skeleton is SOMA's 77 joints with the drawing's bone lengths and
// Anny's joint frames (the engine's woman), so the engine (engine/src: retarget, corrections) carries Kimodo's motions.
// Units: the drawing's (styles/s11-rubberhose/tools/anya.py: head radius 70, soles at y 423), 1 unit = S metres.
import * as THREE from 'three';
import { makeBody } from '../../../../engine/src/body.js';
import { makeRetarget, build as buildPose, turnUnder } from '../../../../engine/src/retarget.js';
import { newSample } from '../../../../engine/src/motion.js';
import { qAxisAngle, qRot, qMul, qBetween, getQ, getV, normalize, sub } from '../../../../engine/src/math.js';
import { sweep, hosePath, circle, keys, loft, pillow, outline, merge, ball, bezier, through, geom, lerp, clamp, sst } from './geo.js';
import { drawFace, X0, X1, Y0, Y1, PX, EXPR, vecExpr, exprVec, FACE_LOOP } from './face.js';
import { FaceLive } from './live.js';
import { Part, paintMat, createStage as stage } from './stage.js';
const V3 = THREE.Vector3;

export const S = 0.004, FEET = 423;                      // metres per drawing unit (as Р11: the cast keeps its sizes); soles
const W = (x, y, z = 0) => new V3(x * S, (FEET - y) * S, z * S);   // drawing (x, y down, z forward) → world
// the drawing's paints (anya.py, lib.py)
const C = { skin: '#f6dcc4', skinSh: '#e9bfa3', hair: '#8d3a1f', hairHi: '#b5552e', dress: '#4f86b5', dressSh: '#3c6d97', dot: '#fbf7ee', bow: '#d4402f',
  shoe: '#b8352a', sole: '#1b1714', glove: '#fbf7ee', ink: '#1b1714' };

// ———————————————————— the skeleton: SOMA's joints at the drawing's places, Anny's frames ————————————————————
// A joint's bone keeps Anny's rest direction (what Kimodo's rotations are measured against) and gets the drawing's
// length; the trunk's own offsets (hip width, shoulders) are set where the drawing has them.
function restJoints(old, sk) {
  const J = sk.J, R = old.joints, out = new Float64Array(J * 3), ix = sk.index;
  const at = n => [R[ix[n] * 3], R[ix[n] * 3 + 1], R[ix[n] * 3 + 2]], dist = (a, b) => Math.hypot(...sub(at(a), at(b)));
  const len = { spine: 88 * S / (at('Chest')[1] - at('Hips')[1]), neck: 70 * S / (at('Head')[1] - at('Chest')[1]),
    upperArm: 43 * S / dist('LeftForeArm', 'LeftArm'), foreArm: 46 * S / dist('LeftHand', 'LeftForeArm'), hand: 0.95,
    thigh: 78 * S / dist('LeftShin', 'LeftLeg'), shin: 78 * S / dist('LeftFoot', 'LeftShin'), foot: 0.8 };
  const groupOf = n => /^(Spine1|Spine2|Chest)$/.test(n) ? len.spine : /^(Neck1|Neck2|Head)$/.test(n) ? len.neck
    : /ForeArm$/.test(n) ? len.upperArm : /Hand$/.test(n) && !/Hand[A-Z]/.test(n) ? len.foreArm : /Hand/.test(n) ? len.hand
    : /Shin$/.test(n) ? len.thigh : /Foot$/.test(n) ? len.shin : /Toe/.test(n) ? len.foot : 1;
  const set = (n, v) => { const j = ix[n]; out[j * 3] = v.x; out[j * 3 + 1] = v.y; out[j * 3 + 2] = v.z; };
  for (let j = 0; j < J; j++) {
    const n = sk.names[j], p = sk.parent[j];
    if (p < 0) { set(n, W(0, 238, 0)); continue; }
    const k = groupOf(n);
    for (let d = 0; d < 3; d++) out[j * 3 + d] = out[p * 3 + d] + (R[j * 3 + d] - R[p * 3 + d]) * k;
    if (/^(Left|Right)Shoulder$/.test(n)) set(n, W((n[0] === 'L' ? 1 : -1) * 8, 116, 2));
    if (/^(Left|Right)Arm$/.test(n)) set(n, W((n[0] === 'L' ? 1 : -1) * 30, 120, 0));
    // her legs stand straighter than Anny's: knee and ankle where the drawing has them
    if (/^(Left|Right)Shin$/.test(n)) out[j * 3] = (n[0] === 'L' ? 1 : -1) * 16.5 * S;
    if (/^(Left|Right)Foot$/.test(n)) out[j * 3] = (n[0] === 'L' ? 1 : -1) * 21.5 * S;
    if (/^(Left|Right)Leg$/.test(n)) set(n, W((n[0] === 'L' ? 1 : -1) * 15, 248, 0));
  }
  return out;
}

// ———————————————————— the head: the drawing's skull ball and cheek ball, in head units (y up, centre 0) ————————————————————
const HR = 70, MUZ = { c: [0, -40, 24], a: [62, 46, 46] };          // Head(70).muzzle(40, 62, 46, 46, 24)
function headR(d) {   // the head's surface along a direction from its centre: the two balls joined softly
  const [cx, cy, cz] = MUZ.c, [ax, ay, az] = MUZ.a;
  const A = (d[0] / ax) ** 2 + (d[1] / ay) ** 2 + (d[2] / az) ** 2, B = -2 * (d[0] * cx / ax ** 2 + d[1] * cy / ay ** 2 + d[2] * cz / az ** 2), Cc = (cx / ax) ** 2 + (cy / ay) ** 2 + (cz / az) ** 2 - 1;
  const D = B * B - 4 * A * Cc, t = D > 0 ? Math.max(0, (-B + Math.sqrt(D)) / (2 * A)) : 0, k = 14;   // (the centre is just outside the cheek ball)
  return 0.5 * (HR + t + Math.sqrt((HR - t) ** 2 + k * k)) - 0.5 * k * 0.5;
}
function frontOf(surf) {   // a surface given along directions → its front z at (x, y), found along the line of sight
  return (x, y) => {
    let lo = 0, hi = 160;
    const inside = z => { const l = Math.hypot(x, y, z) || 1e-6; return l < surf([x / l, y / l, z / l]); };
    if (!inside(0)) return 0;
    for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; if (inside(m)) lo = m; else hi = m; }
    return lo;
  };
}
const frontZ = frontOf(headR);
function headGeometry() {
  const g = new THREE.SphereGeometry(1, 144, 108), p = g.attributes.position, rp = new Float32Array(p.count * 3);
  for (let i = 0; i < p.count; i++) {
    const d = [p.getX(i), p.getY(i), p.getZ(i)], r = headR(d);
    p.setXYZ(i, d[0] * r, d[1] * r, d[2] * r); rp[i * 3] = d[0] * r; rp[i * 3 + 1] = -d[1] * r; rp[i * 3 + 2] = d[2] * r;
  }
  g.deleteAttribute('uv'); g.computeVertexNormals(); g.setAttribute('rp', new THREE.Float32BufferAttribute(rp, 3));
  return g;
}
// The hair. The drawing makes it "the ball grown by 10, minus the bare face" (Head.cap) over a bob drawn behind the
// head: a blob wider than the head at the jaw, its ends rolled under. Here: a body of revolution with the bob's
// outline (the radius from the head's centre by the angle from the crown), absent where the face is — it sinks under
// the skin over 10 units from the hairline of the drawing's face loop, so the bare face is exactly the drawn one.
const BOB = [[0, 80], [60, 80.6], [94, 81], [120, 101], [136, 117], [147, 112.6], [156, 89.5], [180, 82]];
const LOOP = outline(FACE_LOOP, 10);
function loopDist(x, y) {   // signed distance to the face loop (drawing coordinates): > 0 outside the bare face
  let inside = false, best = 1e9;
  for (let i = 0, n = LOOP.length; i < n; i++) {
    const a = LOOP[i], b = LOOP[(i + 1) % n];
    if ((a[1] > y) !== (b[1] > y) && x < a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1])) inside = !inside;
    const dx = b[0] - a[0], dy = b[1] - a[1], t = clamp(((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy), 0, 1);
    best = Math.min(best, Math.hypot(x - a[0] - dx * t, y - a[1] - dy * t));
  }
  return inside ? -best : best;
}
const ss2 = (a, b, x) => sst(clamp((x - a) / (b - a), 0, 1));
function hairR(d) {
  const phi = Math.acos(clamp(d[1], -1, 1)) * 180 / Math.PI;
  // the rolled ends are at the sides (the drawing's two curls); behind the neck and under the chin the hair ends higher
  const lat = Math.abs(d[0]) / (Math.hypot(d[0], d[2]) || 1), roll = lerp(d[2] > 0 ? 0 : 0.12, 1, ss2(0.3, 0.8, lat));
  let r = lerp(Math.min(keys(BOB, phi), 83 + 3 * ss2(100, 125, phi)), keys(BOB, phi), roll);
  // the bob stays behind the cheeks: toward the front its bulge goes back to the cap
  const az = Math.atan2(d[2], Math.abs(d[0])) * 180 / Math.PI;
  r = lerp(r, Math.min(r, 81), ss2(8, 38, az) * ss2(86, 100, phi));
  // (the hairline is tested where the hair itself is, so from the front it stands on the drawn line)
  const skin = headR(d); let q = r;
  for (let i = 0; i < 10; i++) { const t = Math.max(skin, q); q = 0.5 * q + 0.5 * lerp(skin - 2.5, r, Math.max(ss2(0, 10, loopDist(d[0] * t, -d[1] * t)), 1 - ss2(0, 12, d[2] * t))); }
  return q;
}
const hairZ = frontOf(hairR);
function hairGeometry() {
  const g = new THREE.SphereGeometry(1, 200, 150), p = g.attributes.position;
  for (let i = 0; i < p.count; i++) { const d = [p.getX(i), p.getY(i), p.getZ(i)], r = hairR(d); p.setXYZ(i, d[0] * r, d[1] * r, d[2] * r); }
  g.deleteAttribute('uv'); g.computeVertexNormals(); return g;
}

// a loft that keeps (u, v) for a painted canvas: ring(k, a) → [x, y, z], uv(k, a) → [u, v]; the seam is doubled
function loftUV(K, R, ring, uv, tips) {
  const pos = [], rp = [], idx = [], n = R + 1;
  for (let k = 0; k <= K; k++) for (let i = 0; i <= R; i++) { const a = i / R * Math.PI * 2; pos.push(...ring(k, a)); rp.push(...uv(k, i / R), 1); }
  for (let k = 0; k < K; k++) for (let i = 0; i < R; i++) { const p0 = k * n + i, p1 = p0 + 1, q0 = p0 + n, q1 = q0 + 1; idx.push(p0, p1, q0, p1, q1, q0); }
  for (const [k, flip] of [[0, true], [K, false]]) {
    const v = pos.length / 3; pos.push(...tips[k ? 1 : 0].p); rp.push(...tips[k ? 1 : 0].uv, 1);
    for (let i = 0; i < R; i++) flip ? idx.push(v, k * n + i, k * n + i + 1) : idx.push(v, k * n + i + 1, k * n + i);
  }
  const g = geom(pos, idx); g.setAttribute('rp', new THREE.Float32BufferAttribute(rp, 3)); return g;
}
const toWorld = g => { const p = g.attributes.position; for (let i = 0; i < p.count; i++) { const w = W(p.getX(i), p.getY(i), p.getZ(i)); p.setXYZ(i, w.x, w.y, w.z); } g.computeVertexNormals(); return g; };
const flipTris = g => { const ix = g.index.array; for (let k = 0; k < ix.length; k += 3) { const t = ix[k + 1]; ix[k + 1] = ix[k + 2]; ix[k + 2] = t; } return g; };

// ———————————————————— the character ————————————————————
export class Anya {
  constructor(E, old) {
    this.E = E; this.sk = E.skeleton;
    const sk = this.sk;
    this.R = restJoints(old, sk);
    this.root = new THREE.Group();
    this.live = new FaceLive(3);
    this.dyn = { sy: 0, v: 0, sway: [0, 0], swayV: [0, 0] };
    this.buildRest();
    // the body the engine retargets onto: our rest mesh, SOMA's joints at our places, Anny's frames
    this.body = makeBody({ id: 'anya-s11', label: { ru: 'Аня (С11)' }, skeleton: sk, positions: this.restPositions, triangles: this.restTriangles,
      joints: this.R, frames: Float64Array.from(old.frames), skin: null, parts: { names: ['head'], weights: this.restHead } });
    // the engine's own corrections: the arms a little off the body (the bell of the skirt), and out of her big head
    this.retarget = makeRetarget(this.body, { corrections: { armsOff: { degrees: 13 }, armsOutOfHead: { margin: 0.06 } } });
    this.sample = newSample(sk.J);
  }
  J(n) { const j = this.sk.index[n]; return new V3(this.R[j * 3], this.R[j * 3 + 1], this.R[j * 3 + 2]); }

  buildRest() {
    const root = this.root, sk = this.sk;
    const line = 2.6 * S;
    // the dress: bodice and bell skirt as one loft, the drawing's widths (front) and depths (profile) at each height
    const Y0d = 104, Y1d = 266, YV = 282;
    const DW = [[104, 19], [108, 25.5], [114, 28], [138, 31], [158, 25], [168, 22.5], [176, 24], [190, 33], [205, 41], [235, 54.5], [256, 61], [266, 58]];
    const DF = [[104, 10], [112, 14], [125, 19], [140, 21.5], [158, 17], [168, 15.5], [176, 17], [205, 30], [235, 40], [256, 45], [266, 43]];
    const DB = [[104, 10], [112, 14], [140, 16], [168, 14], [176, 15.5], [205, 28], [235, 38], [256, 43], [266, 41]];
    const NE = 2.3, hemT = y => clamp((y - 176) / (Y1d - 176), 0, 1);
    const section = (y, a, grow = 0) => {
      const w = keys(DW, y) + grow, df = keys(DF, y) + grow, db = keys(DB, y) + grow, c = Math.cos(a), s = Math.sin(a);
      const t = hemT(y), wave = 1 + 0.045 * t * t * Math.cos(7 * a + 0.6);        // the hem's soft waves
      return [w * Math.sign(c) * Math.abs(c) ** (2 / NE) * wave, y + 3.5 * t * t * Math.cos(7 * a + 0.6), (s > 0 ? df : db) * Math.sign(s) * Math.abs(s) ** (2 / NE) * wave];
    };
    this.torsoFront = (x, y) => { const w = keys(DW, y), df = keys(DF, y), u = Math.min(0.97, Math.abs(x) / w); return df * Math.pow(Math.max(0, 1 - u ** NE), 1 / NE); };
    const KD = 72, RD = 72, yOf = k => lerp(Y0d, Y1d, k / KD);
    // u goes round the dress by length, so the dots stay round
    const arcU = y => { const c = [0]; let p = section(y, 0); for (let i = 1; i <= RD; i++) { const q = section(y, i / RD * Math.PI * 2); c.push(c[i - 1] + Math.hypot(q[0] - p[0], q[2] - p[2])); p = q; } return c.map(v => v / c[RD]); };
    const arcs = []; for (let k = 0; k <= KD; k++) arcs.push(arcU(yOf(k)));
    this.arcAt = (y, a) => { const c = arcU(y), f = clamp(a / (2 * Math.PI), 0, 1) * RD, i = Math.min(RD - 1, Math.floor(f)); return lerp(c[i], c[i + 1], f - i); };
    const dressG = loftUV(KD, RD, (k, a) => section(yOf(k), a), (k, u) => [arcs[k][Math.round(u * RD)], 1 - (yOf(k) - Y0d) / (YV - Y0d)],
      [{ p: [0, Y0d, 0], uv: [0.5, 1] }, { p: [0, Y1d - 14, 0], uv: [0.5, 0.02] }]);
    this.dressCanvas = this.paintDress(section, Y0d, Y1d, YV);
    const dressTex = new THREE.CanvasTexture(this.dressCanvas); dressTex.colorSpace = THREE.NoColorSpace; dressTex.anisotropy = 4; dressTex.wrapS = THREE.RepeatWrapping;
    // skinned pieces: [geometry at rest (world), weights by height over the spine]
    this.skinned = [];
    const spine = ['Hips', 'Spine1', 'Spine2', 'Chest', 'Neck1'].map(n => sk.index[n]);
    const spineY = spine.map(j => this.R[j * 3 + 1]);
    const byHeight = (y) => {   // two joints and their weights for a rest height (world)
      if (y <= spineY[0]) return [[spine[0], 1]];
      for (let k = 0; k < spine.length - 1; k++) if (y <= spineY[k + 1]) { const t = sst((y - spineY[k]) / (spineY[k + 1] - spineY[k])); return [[spine[k], 1 - t], [spine[k + 1], t]]; }
      return [[spine[spine.length - 1], 1]];
    };
    const addSkinned = (geo, mat, weights, ln = line, sway = false) => {
      const part = new Part(root, mat, ln, geo); part.set(geo);
      const p = geo.attributes.position, wts = [], sw = [];
      for (let i = 0; i < p.count; i++) { wts.push(weights(p.getX(i), p.getY(i), p.getZ(i))); sw.push(sway ? hemT(FEET - p.getY(i) / S) ** 2 : 0); }
      this.skinned.push({ part, rest: Float32Array.from(p.array), wts, sway: sway ? sw : null });
      return part;
    };
    addSkinned(toWorld(dressG), paintMat('#ffffff', { paint: 4, map: dressTex, shade: 0.1 }), (x, y) => byHeight(y), line, true);
    // the belt: a red band over the waist
    const belt = toWorld(flipTris(loft(8, 56, (k, a) => { const y = lerp(162.5, 177.5, k / 8); return section(y, a, 0.6 + 1.6 * Math.sin(Math.PI * k / 8)); })));
    addSkinned(belt, paintMat(C.bow, { shade: 0.1 }), (x, y) => byHeight(y), 1.8 * S);
    // the collar: two white flaps on the bodice
    const onTorso = (lift = 0) => (u, v, h) => [u, v, this.torsoFront(u, v) + lift + h];
    const collar = merge([-1, 1].map(sd => pillow(outline([[sd * 2, 104], [sd * 27, 108], [sd * 24, 124], [sd * 4, 120], [0, 112]], 6), onTorso(0.4), { thick: 2.4, sink: 1.5, rings: 4, flip: sd < 0 })));
    addSkinned(toWorld(collar), paintMat(C.dot), (x, y) => byHeight(y), 2 * S);

    // limbs (rebuilt every frame): arms and legs as bare hoses, the neck, gloves, shoes
    const skin = () => paintMat(C.skin, { shade: 0.09 });
    this.neck = new Part(root, skin(), line);
    this.arms = { Left: new Part(root, skin(), line), Right: new Part(root, skin(), line) };
    this.legs = { Left: new Part(root, skin(), line), Right: new Part(root, skin(), line) };
    this.gloves = { Left: new Part(root, paintMat(C.glove, { shade: 0.08 }), line), Right: new Part(root, paintMat(C.glove, { shade: 0.08 }), line) };
    // puff sleeves: dotted balls on the shoulders
    const pc = document.createElement('canvas'); pc.width = 256; pc.height = 128; const pg = pc.getContext('2d');
    pg.fillStyle = C.dress; pg.fillRect(0, 0, 256, 128); pg.fillStyle = C.dot;
    for (let j = 0; j < 4; j++) for (let i = 0; i < 6; i++) { const y = 20 + j * 30, x = (i + (j % 2) * 0.5) * 256 / 6, rx = 9 / Math.max(0.35, Math.sin(Math.PI * y / 128)); pg.beginPath(); pg.ellipse(x, y, rx, 9, 0, 0, 7); pg.fill(); pg.beginPath(); pg.ellipse(x + 256, y, rx, 9, 0, 0, 7); pg.fill(); }
    const puffTex = new THREE.CanvasTexture(pc); puffTex.colorSpace = THREE.NoColorSpace; puffTex.wrapS = THREE.RepeatWrapping;
    this.puffs = {};
    for (const sd of ['Left', 'Right']) {
      const g = new THREE.SphereGeometry(1, 28, 20), uv = g.attributes.uv, rp = new Float32Array(uv.count * 3);
      for (let i = 0; i < uv.count; i++) { rp[i * 3] = uv.getX(i); rp[i * 3 + 1] = uv.getY(i); rp[i * 3 + 2] = 1; }
      g.scale(15.5 * S, 14.5 * S, 15 * S); g.setAttribute('rp', new THREE.Float32BufferAttribute(rp, 3));
      const grp = new THREE.Group(); root.add(grp); new Part(grp, paintMat('#ffffff', { paint: 4, map: puffTex, shade: 0.1 }), line).set(g);
      this.puffs[sd] = grp;
    }
    // shoes: rigid on the foot, made at rest around the ankle (the drawing's side shoe, its front width), at 0.8
    this.shoes = {};
    const SS = 0.8;
    for (const sd of ['Left', 'Right']) {
      const ank = this.J(sd + 'Foot'), toe = this.J(sd + 'ToeEnd'), sg = sd === 'Left' ? 1 : -1;
      const fwd = new V3(toe.x - ank.x, 0, toe.z - ank.z).normalize().applyAxisAngle(new V3(0, 1, 0), sg * 0.14), side = new V3().crossVectors(new V3(0, 1, 0), fwd);
      const top = [[-22, 8], [-18, 2], [-10, -4], [6, -5], [16, -3], [34, -5], [46, 1], [51, 9], [52, 14]], bot = 21;
      const wid = [[-22, 12], [-14, 17], [4, 19], [26, 25], [40, 26], [48, 21], [52, 10]];
      const u0 = -23, u1 = 52.5, K = 40;
      const shoeG = loft(K, 36, (k, a) => {
        const u = lerp(u0, u1, k / K), yt = keys(top, u), w = keys(wid, u), hh = (bot - yt) / 2, yc = (bot + yt) / 2;
        const c = Math.cos(a), s = Math.sin(a), x = w * Math.sign(c) * Math.abs(c) ** 0.8;
        const y = yc - hh * Math.sign(s) * Math.abs(s) ** (s < 0 ? 1 / 3 : 0.9);   // flat underneath
        return [x, y, u];
      }, { flip: true });
      const soleG = loft(K, 36, (k, a) => {
        const u = lerp(u0 + 1, u1 - 0.5, k / K), w = keys(wid, u) + 1.2, c = Math.cos(a), s = Math.sin(a);
        const lift = u > 44 ? (u - 44) * 0.5 : 0;
        return [w * Math.sign(c) * Math.abs(c) ** 0.6, 24.5 - lift - 3.2 * Math.sign(s) * Math.abs(s) ** 0.6, u];
      }, { flip: true });
      const place = g => {   // (mirrored for the left foot: its triangles are turned back after)  shoe units (x across, y down from the ankle, z forward) → world at rest
        const p = g.attributes.position;
        for (let i = 0; i < p.count; i++) {
          const x = p.getX(i) * SS, y = p.getY(i) * SS - 2, u = p.getZ(i) * SS;
          const w = ank.clone().addScaledVector(side, -x * S * sg).addScaledVector(fwd, u * S); w.y = ank.y - y * S;
          p.setXYZ(i, w.x, w.y, w.z);
        }
        g.computeVertexNormals(); return g;
      };
      const grp = new THREE.Group(); root.add(grp);
      const shoeP = new Part(grp, paintMat(C.shoe, { shine: 0.03, shade: 0.12 }), line); shoeP.set(sg > 0 ? flipTris(place(shoeG)) : place(shoeG));
      const soleP = new Part(grp, paintMat(C.sole, { shade: 0 }), line); soleP.set(sg > 0 ? flipTris(place(soleG)) : place(soleG));
      let lo = Infinity; for (const g of [shoeP.mesh.geometry, soleP.mesh.geometry]) { const p = g.attributes.position; for (let i = 0; i < p.count; i++) lo = Math.min(lo, p.getY(i)); }
      for (const g of [shoeP.mesh.geometry, soleP.mesh.geometry]) { g.translate(0, -lo, 0); g.computeBoundingSphere(); }
      this.shoes[sd] = { grp, parts: [shoeP, soleP], rest: ank };
    }
    // the head: a group on the Head joint, in head units (×S), centred at the head's centre
    this.headPivot = this.J('Head');
    this.headC = W(0, 0, 5);
    this.head = new THREE.Group(); root.add(this.head);
    this.faceCanvas = document.createElement('canvas'); this.faceCanvas.width = (X1 - X0) * PX; this.faceCanvas.height = (Y1 - Y0) * PX;
    this.faceTex = new THREE.CanvasTexture(this.faceCanvas); this.faceTex.colorSpace = THREE.NoColorSpace; this.faceTex.anisotropy = 4;
    const hl = 2.6;
    new Part(this.head, paintMat(C.skin, { paint: 3, map: this.faceTex, shade: 0.08, shine: 0, box: new THREE.Vector4(X0, X1, Y0, Y1) }), hl).set(headGeometry());
    new Part(this.head, paintMat(C.hair, { shade: 0.13 }), hl).set(hairGeometry());
    // the lighter strokes of the hair (anya.py): three on the crown, one on each rolled end of the bob
    const hi = [];
    for (const pts of [[[-6, -86], [-14, -70], [-16, -58]], [[22, -84], [34, -70], [40, -58]], [[-40, -76], [-50, -62], [-52, -48]],
      [[-83, 86], [-72, 77], [-62, 86]], [[62, 86], [72, 77], [83, 86]]]) {
      const ps = pts.map(([u, v]) => { const k = Math.min(1, 78.5 / Math.hypot(u, v)), x = v < 0 ? u * k : u, y = v < 0 ? -v * k : -v; return new V3(x, y, hairZ(x, y) + 0.4); });
      hi.push(sweep(through(ps, 8), circle(() => 1.25), { radial: 6 }));
    }
    new Part(this.head, paintMat(C.hairHi, { shade: 0 }), 0).set(merge(hi));
    // the button nose
    new Part(this.head, paintMat(C.skinSh, { shine: 0.035, shade: 0.08 }), 1.9).set(ball([0, -40, frontZ(0, -40) + 2], [5.2, 4.7, 4.8], 20));
    // the red bow on top, toward her left: two lobes and a knot
    {
      const c0 = new V3(30, 60, 0); c0.z = hairZ(c0.x, c0.y); const out = c0.clone().normalize(), c = c0.clone().addScaledVector(out, 5);
      const n = new V3(0.5, 0.25, 0.9).normalize(), rot = -25 * Math.PI / 180;
      let ex = new V3(1, 0, 0).addScaledVector(n, -n.x).normalize(), ey = new V3().crossVectors(n, ex);
      const ex2 = ex.clone().multiplyScalar(Math.cos(rot)).addScaledVector(ey, Math.sin(rot)), ey2 = new V3().crossVectors(n, ex2);
      const pl = (u, v, h) => c.clone().addScaledVector(ex2, u).addScaledVector(ey2, -v).addScaledVector(n, h).toArray();
      const lobes = [-1, 1].map(sd => pillow(outline([[4, -6], [24, -20], [29, 0], [22, 13], [4, 6]].map(([u, v]) => [u * sd, v]), 7), pl, { thick: 7, sink: 7, rings: 7, centre: [sd * 16, -1], flip: sd < 0 }));
      const knot = ball([0, 0, 0], [7.5, 7.5, 8.5], 16); knot.applyMatrix4(new THREE.Matrix4().makeBasis(ex2, ey2, n).setPosition(c));
      new Part(this.head, paintMat(C.bow, { shade: 0.12, shine: 0.012 }), hl).set(merge([...lobes, knot]));
      const folds = [-1, 1].map(sd => sweep([[sd * 19, -6], [sd * 13, -3.5], [sd * 8, -1]].map(([u, v]) => new V3(...pl(u, v, 7.2 * Math.sqrt(Math.max(0, 1 - ((Math.abs(u) - 16) / 13) ** 2)) + 0.3))), circle(() => 0.8), { radial: 6 }));
      new Part(this.head, paintMat(C.ink, { shade: 0 }), 0).set(merge(folds));
    }
    // shadow on the floor (the drawing's soft ellipse)
    const sc = document.createElement('canvas'); sc.width = sc.height = 128; const sg2 = sc.getContext('2d'); const grd = sg2.createRadialGradient(64, 64, 10, 64, 64, 64); grd.addColorStop(0, 'rgba(27,23,20,0.26)'); grd.addColorStop(0.7, 'rgba(27,23,20,0.2)'); grd.addColorStop(1, 'rgba(27,23,20,0)'); sg2.fillStyle = grd; sg2.fillRect(0, 0, 128, 128);
    this.shadow = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(sc), transparent: true, depthWrite: false }));
    this.shadow.rotation.x = -Math.PI / 2; this.shadow.scale.set(150 * S * 1.6, 60 * S * 1.6, 1); this.shadow.renderOrder = -1;
    // what the engine measures the body by: our rest mesh
    this.setFace(vecExpr(exprVec(EXPR.neutral)), { look: [0, 0], blink: 0 });
    this.apply(this.standPose(false), true);
    const pos = [], tri = [], hd = []; let off = 0;
    this.root.updateMatrixWorld(true);
    this.root.traverse(o => { if (o.isMesh && o.material?.uniforms?.uColor && o.geometry.index) { const g = o.geometry, p = g.attributes.position, v = new V3(), h = o.parent === this.head && o.material.uniforms.uPaint.value > 2.5; for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i).applyMatrix4(o.matrixWorld); pos.push(v.x, v.y, v.z); hd.push(h ? 255 : 0); } for (const i of g.index.array) tri.push(i + off); off += p.count; } });
    this.restPositions = Float32Array.from(pos); this.restTriangles = Uint32Array.from(tri); this.restHead = Uint8Array.from(hd);   // the skull's skin: the engine's head ball
  }

  // the dress's paint, unrolled: u round the body (0.25 is the front's middle), v down from the neckline. The polka
  // dots are the drawing's: rows 22.4 apart, 26 between dots, every other row shifted — each row gets as many dots as
  // go round the dress at its height.
  paintDress(section, y0, y1, yv) {
    const cv = document.createElement('canvas'); cv.width = 2048; cv.height = 1024; const g = cv.getContext('2d');
    const X = u => u * cv.width, Y = y => (y - y0) / (yv - y0) * cv.height;
    g.fillStyle = C.dress; g.fillRect(0, 0, cv.width, cv.height);
    const round = y => { let L = 0, p = section(y, 0); for (let i = 1; i <= 96; i++) { const q = section(y, i / 96 * Math.PI * 2); L += Math.hypot(q[0] - p[0], q[2] - p[2]); p = q; } return L; };
    g.fillStyle = C.dot;
    for (let j = 0; j < 9; j++) {
      const y = 90 + j * 26 * 0.86; if (y < y0 + 4 || y > y1 + 6) continue;
      const L = round(Math.min(y, y1)), n = Math.max(4, Math.round(L / 26)), rx = 5.2 / L * cv.width, ry = 5.2 / (yv - y0) * cv.height;
      for (let i = 0; i < n; i++) for (const wrap of [-1, 0, 1]) { g.beginPath(); g.ellipse(X(0.25 + (i + (j % 2 ? 0.5 : 0)) / n + wrap), Y(y), rx, ry, 0, 0, 7); g.fill(); }
    }
    // the skirt's two folds (ink), the dress's darker underside past the hem
    const uOf = (x, y) => { const w = section(y, 0)[0]; return this.arcAt(y, Math.acos(clamp(Math.sign(x) * (Math.abs(x) / w) ** (2.3 / 2), -1, 1))); };
    g.strokeStyle = C.ink; g.lineWidth = 2 / 172 * cv.height * 0.55; g.lineCap = 'round';
    for (const [a, b] of [[[-8, 200], [-14, 258]], [[18, 200], [26, 259]]]) { g.beginPath(); for (let i = 0; i <= 12; i++) { const y = lerp(a[1], b[1], i / 12), x = lerp(a[0], b[0], i / 12); i ? g.lineTo(X(uOf(x, y)), Y(y)) : g.moveTo(X(uOf(x, y)), Y(y)); } g.stroke(); }
    g.fillStyle = C.dressSh; g.fillRect(0, Y(y1 + 6.5), cv.width, cv.height);
    return cv;
  }

  // ———— poses ————
  // a still standing pose made from the rest (not a motion): the drawing's — arms hanging in soft arcs away from the skirt
  standPose(arms = true, o = {}) {
    const sk = this.sk, J = sk.J, pose = { Q: new Float64Array(J * 4), P: Float64Array.from(this.R), floor: 0 };
    for (let j = 0; j < J; j++) pose.Q[j * 4 + 3] = 1;
    const B = this.body || { skeleton: sk, joints: this.R }, hip = () => getV(pose.P, sk.index.Hips);
    if (arms) for (const [sd, sg] of [['Left', 1], ['Right', -1]]) {
      const A = sk.index[sd + 'Arm'], F = sk.index[sd + 'ForeArm'], H = sk.index[sd + 'Hand'];
      const a = normalize(sub(getV(this.R, F), getV(this.R, A)));
      turnUnder(pose, sk, A, qBetween(a, normalize([sg * Math.sin(0.5), -Math.cos(0.5), 0.1]))); buildPose(pose, B, hip());
      const f = normalize(sub(getV(pose.P, H), getV(pose.P, F))), wantF = normalize([sg * Math.sin(-0.02), -Math.cos(0.02), 0.2]);
      turnUnder(pose, sk, F, qBetween(f, wantF)); buildPose(pose, B, hip());
      // the hand turned so the palm faces the skirt, fingers down
      const mid = normalize(qRot(getQ(pose.Q, H), sub(getV(this.R, sk.index[sd + 'HandMiddle1']), getV(this.R, H))));
      turnUnder(pose, sk, H, qBetween(mid, wantF)); buildPose(pose, B, hip());
    }
    if (o.head) { turnUnder(pose, sk, sk.index.Head, qMul(qAxisAngle([0, 1, 0], o.head[0] * Math.PI / 180), qAxisAngle([1, 0, 0], o.head[1] * Math.PI / 180))); buildPose(pose, { skeleton: sk, joints: this.R }, hip()); }
    pose.floor = 0;
    return pose;
  }
  // a Kimodo clip's moment through the engine (retarget + corrections), placed
  clipPose(clip, f) { const p = this.retarget.pose(clip.sample(f, this.sample)); this.retarget.placed(p); return p; }

  // ———— putting a pose on the forms ————
  apply(pose) {
    const sk = this.sk, P = i => new V3(pose.P[i * 3], pose.P[i * 3 + 1], pose.P[i * 3 + 2]), Qj = i => new THREE.Quaternion(pose.Q[i * 4], pose.Q[i * 4 + 1], pose.Q[i * 4 + 2], pose.Q[i * 4 + 3]);
    const ix = sk.index, J = n => P(ix[n]);
    // skinned pieces (linear blend over the spine joints); the skirt's lower part sways (a spring, see app.js)
    const Rj = j => new V3(this.R[j * 3], this.R[j * 3 + 1], this.R[j * 3 + 2]);
    const M = new Map();
    const mat = j => { if (!M.has(j)) { const q = Qj(j), r = Rj(j), p = P(j); M.set(j, { q, t: p.sub(r.applyQuaternion(q)) }); } return M.get(j); };
    const v = new V3(), acc = new V3(), sw = this.dyn.sway;
    for (const s of this.skinned) {
      const pa = s.part.mesh.geometry.attributes.position, a = pa.array;
      for (let i = 0; i < s.wts.length; i++) {
        acc.set(0, 0, 0);
        for (const [j, w] of s.wts[i]) { const m = mat(j); v.set(s.rest[i * 3], s.rest[i * 3 + 1], s.rest[i * 3 + 2]).applyQuaternion(m.q).add(m.t); acc.addScaledVector(v, w); }
        if (s.sway) { acc.x += sw[0] * s.sway[i]; acc.z += sw[1] * s.sway[i]; }
        a[i * 3] = acc.x; a[i * 3 + 1] = acc.y; a[i * 3 + 2] = acc.z;
      }
      pa.needsUpdate = true; s.part.mesh.geometry.computeVertexNormals();
    }
    // the head: rigid on the Head joint, squashed and stretched about its centre
    const hj = ix.Head, hq = Qj(hj);
    this.head.quaternion.copy(hq);
    this.head.position.copy(P(hj).add(this.headC.clone().sub(this.headPivot).applyQuaternion(hq)));
    const sq = this.sq || [1, 1];
    this.head.scale.set(S * sq[0], S * sq[1], S * sq[0]);
    // the neck: a thin hose from the collar into the head
    const n1 = J('Neck1'), up = this.head.position.clone().sub(n1);
    this.neck.set(sweep(bezier([n1.clone().addScaledVector(up, -0.12), J('Neck2'), n1.clone().addScaledVector(up, 0.75)], 8), circle(() => 7.5 * S), { radial: 16 }));
    // hoses: bare arms and legs
    for (const sd of ['Left', 'Right']) {
      const ap = hosePath(J(sd + 'Arm'), J(sd + 'ForeArm'), J(sd + 'Hand'), 1.0);
      this.arms[sd].set(sweep(ap, circle(() => 7 * S), { radial: 16 }));
      const lp = hosePath(J(sd + 'Leg'), J(sd + 'Shin'), J(sd + 'Foot'), 1.0);
      const LR = [[0, 16], [0.5, 12], [1, 6]];
      this.legs[sd].set(sweep(lp, circle(i => keys(LR, i / 36) * S), { radial: 20, capEnd: false }));
      this.gloves[sd].set(this.glove(pose, sd, P));
      const sh = this.shoes[sd], j = ix[sd + 'Foot'], q = Qj(j);
      sh.grp.quaternion.copy(q); sh.grp.position.copy(P(j).sub(sh.rest.clone().applyQuaternion(q)));
      const pf = this.puffs[sd]; pf.quaternion.copy(Qj(ix.Chest)); pf.position.copy(J(sd + 'Arm').lerp(J(sd + 'ForeArm'), 0.04));
    }
    // the shadow under her
    const hips = J('Hips'); this.shadow.position.set(hips.x, (pose.floor ?? 0) + 0.002, hips.z + 0.02);
    this.pose = pose;
  }
  // a white glove: palm, three fat fingers and a thumb along the posed finger joints, a rolled cuff (П2's hand), at 0.72
  glove(pose, sd, P) {
    const ix = this.sk.index, J = n => P(ix[n]), GS = 0.92;
    const wrist = J(sd + 'Hand'), fore = J(sd + 'ForeArm'), dir = wrist.clone().sub(fore).normalize();
    const gs = [], rf = 5.6 * S * GS;
    const pc = wrist.clone().lerp(J(sd + 'HandMiddle1'), 0.62), a1 = J(sd + 'HandMiddle1').sub(wrist), a2 = J(sd + 'HandIndex1').sub(J(sd + 'HandPinky1'));
    const palm = new THREE.SphereGeometry(1, 22, 14), m = new THREE.Matrix4();
    const ex = a2.clone().normalize(), ey = a1.clone().normalize(), ez = new V3().crossVectors(ex, ey).normalize(); ex.crossVectors(ey, ez);
    m.makeBasis(ex.clone().multiplyScalar(13 * S * GS), ey.clone().multiplyScalar(a1.length() * 0.75 + 2 * S), ez.clone().multiplyScalar(7.5 * S * GS)).setPosition(pc); palm.applyMatrix4(m);
    gs.push(palm);
    for (const f of ['Index', 'Middle', 'Ring', 'Thumb']) {
      const ids = f === 'Thumb' ? [1, 2, 3, 'End'] : [1, 2, 3, 4, 'End'];
      let pts = ids.map(i => J(sd + 'Hand' + f + i));
      if (f !== 'Thumb') pts = [pts[0].clone().lerp(pts[1], 0.3), ...pts.slice(1)];
      const fl = f === 'Thumb' ? 0.85 : 0.78, segs = []; for (let r = 1; r < pts.length; r++) segs.push(pts[r].clone().sub(pts[r - 1]).multiplyScalar(fl));
      for (let r = 1; r < pts.length; r++) pts[r] = pts[r - 1].clone().add(segs[r - 1]);
      gs.push(sweep(bezier(pts, 10), circle(i => rf * (0.94 + 0.1 * (i / 10))), { radial: 12 }));
    }
    const c0 = wrist.clone().addScaledVector(dir, -8 * S * GS), c1 = wrist.clone().addScaledVector(dir, 2.5 * S * GS);
    gs.push(sweep([c0, c0.clone().lerp(c1, 0.5), c1], circle(i => [11.5, 13.8, 12.6][i] * S * GS), { radial: 24 }));
    return merge(gs);
  }

  // the face: paint the canvas, squash the head
  setFace(e, live) {
    drawFace(this.faceCanvas, e, live); this.faceTex.needsUpdate = true;
    this.sq = [e.sq[0] - this.dyn.sy * 0.5, e.sq[1] + this.dyn.sy + Math.max(0, e.mouth.pts[4][1] - e.mouth.pts[1][1]) * 0.0015];
  }
}

export const createStage = (canvas, o = {}) => stage(canvas, { ...o, body: 'moood-woman', make: (E, old) => new Anya(E, old) });
