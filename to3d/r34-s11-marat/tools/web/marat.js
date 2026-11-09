// Марат, rubber-hose 1930s (style С11), in 3D on moood's SOMA skeleton — built the way Р11 (Савелий Петрович,
// to3d/r11-s11-savely) is: the expressive constructor of experiments/toon (gallery П2). He is the biggest of the cast:
// a barrel of a torso and a long apron as lofts of the drawing's own widths and depths, short thick legs and thick
// forearms as sweeps along an arc through the joints, rebuilt every frame (the forearm swells below the rolled-up
// sleeve); the head is the drawing's ball, and over it one form of hair and beard — the cap of curls and the beard's
// deeper lower ball, absent where the bare face is — with curls as bumps. The skeleton is SOMA's 77 joints with the
// drawing's bone lengths and Anny's joint frames (the engine's man), so the engine carries Kimodo's motions onto it.
// Units: the drawing's (styles/s11-rubberhose/tools/marat.py: head radius 68 × 1.08, soles at y 516), 1 unit = S metres.
import * as THREE from 'three';
import { makeBody } from '../../../../engine/src/body.js';
import { makeRetarget, build as buildPose, turnUnder } from '../../../../engine/src/retarget.js';
import { newSample } from '../../../../engine/src/motion.js';
import { qAxisAngle, qRot, qMul, qBetween, getQ, getV, normalize, sub } from '../../../../engine/src/math.js';
import { sweep, hosePath, circle, keys, loft, pillow, outline, merge, ball, bezier, through, lerp, clamp, sst } from './geo.js';
import { drawFace, X0, X1, Y0, Y1, PX, EXPR, vecExpr, exprVec, FACE_LOOP, mouthOpen } from './face.js';
import { FaceLive } from './live.js';
import { Part, paintMat, raw, createStage as stage } from './stage.js';
const V3 = THREE.Vector3;

export const S = 0.004, FEET = 516, XC = 4, HS = 1.08;   // metres per drawing unit (as Р11); soles; the body's middle in x; the head's scale
const W = (x, y, z = 0) => new V3(x * S, (FEET - y) * S, z * S);   // drawing (x from the body's middle, y down, z forward) → world
// the drawing's paints (marat.py, lib.py)
const C = { skin: '#f0c9a6', skinSh: '#dba27f', nose: '#e59a7c', hair: '#33262a', jacket: '#f6f0e0', apron: '#d0673a', apronSh: '#a94e2a', pants: '#4d443f',
  shoe: '#2a221e', sole: '#1b1714', towel: '#f1e3bd', brass: '#d9a93a', glove: '#fbf7ee', ink: '#1b1714' };

// ———————————————————— the skeleton: SOMA's joints at the drawing's places, Anny's frames ————————————————————
function restJoints(old, sk) {
  const J = sk.J, R = old.joints, out = new Float64Array(J * 3), ix = sk.index;
  const at = n => [R[ix[n] * 3], R[ix[n] * 3 + 1], R[ix[n] * 3 + 2]], dist = (a, b) => Math.hypot(...sub(at(a), at(b)));
  const len = { spine: 208 * S / (at('Chest')[1] - at('Hips')[1]), neck: 102 * S / (at('Head')[1] - at('Chest')[1]),
    upperArm: 77 * S / dist('LeftForeArm', 'LeftArm'), foreArm: 73 * S / dist('LeftHand', 'LeftForeArm'), hand: 1.3,
    thigh: 43 * S / dist('LeftShin', 'LeftLeg'), shin: 43 * S / dist('LeftFoot', 'LeftShin'), foot: 1.2 };
  const groupOf = n => /^(Spine1|Spine2|Chest)$/.test(n) ? len.spine : /^(Neck1|Neck2|Head)$/.test(n) ? len.neck
    : /ForeArm$/.test(n) ? len.upperArm : /Hand$/.test(n) && !/Hand[A-Z]/.test(n) ? len.foreArm : /Hand/.test(n) ? len.hand
    : /Shin$/.test(n) ? len.thigh : /Foot$/.test(n) ? len.shin : /Toe/.test(n) ? len.foot : 1;
  const set = (n, v) => { const j = ix[n]; out[j * 3] = v.x; out[j * 3 + 1] = v.y; out[j * 3 + 2] = v.z; };
  for (let j = 0; j < J; j++) {
    const n = sk.names[j], p = sk.parent[j];
    if (p < 0) { set(n, W(0, 378, -2)); continue; }
    const k = groupOf(n);
    for (let d = 0; d < 3; d++) out[j * 3 + d] = out[p * 3 + d] + (R[j * 3 + d] - R[p * 3 + d]) * k;
    if (/^(Spine1|Spine2|Chest|Neck1|Neck2|Head)$/.test(n)) out[j * 3 + 2] = out[p * 3 + 2] * 0.5;   // an upright barrel: the spine's own curve is not his
    if (/^(Left|Right)Shoulder$/.test(n)) set(n, W((n[0] === 'L' ? 1 : -1) * 40, 100, 2));
    if (/^(Left|Right)Arm$/.test(n)) set(n, W((n[0] === 'L' ? 1 : -1) * 102, 122, 0));
    if (/^(Left|Right)Leg$/.test(n)) set(n, W((n[0] === 'L' ? 1 : -1) * 42, 400, -2));
  }
  return out;
}

// ———————————————————— the head, in head units (y up, centre 0) ————————————————————
const HR = 68, BEARD = { c: [0, -44, 24], a: [70, 56, 54] };        // Head(68); the beard's volume: muzzle(44, 70, 56, 54, 24)
const CAP = HR + 4;
function frontOf(surf) {   // a surface given along directions → its front z at (x, y), found along the line of sight
  return (x, y) => {
    let lo = 0, hi = 170;
    const inside = z => { const l = Math.hypot(x, y, z) || 1e-6; return l < surf([x / l, y / l, z / l]); };
    if (!inside(0)) return 0;
    for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; if (inside(m)) lo = m; else hi = m; }
    return lo;
  };
}
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
// The hair and the beard as one form over the skin ball: the cap of the drawing (the ball grown by 4) joined softly
// with the beard's deeper, wider lower ball; where the bare face is (the drawing's hairline and the beard's upper
// edge) it sinks under the skin over 7 units, so the face is exactly the drawn one.
function beardR(d) {
  const [cx, cy, cz] = BEARD.c, [ax, ay, az] = BEARD.a;
  const A = (d[0] / ax) ** 2 + (d[1] / ay) ** 2 + (d[2] / az) ** 2, B = -2 * (d[0] * cx / ax ** 2 + d[1] * cy / ay ** 2 + d[2] * cz / az ** 2), Cc = (cx / ax) ** 2 + (cy / ay) ** 2 + (cz / az) ** 2 - 1;
  return (-B + Math.sqrt(B * B - 4 * A * Cc)) / (2 * A);
}
function hairFull(d) { const t = beardR(d), k = 10; return 0.5 * (CAP + t + Math.sqrt((CAP - t) ** 2 + k * k)) - 0.5 * k * 0.5; }
function hairK(d, r) { return Math.max(ss2(0, 7, loopDist(d[0] * r, -d[1] * r)), 1 - ss2(0, 12, d[2] * r)); }
function hairR(d) { const r = hairFull(d); return lerp(HR - 2.5, r, hairK(d, r)); }
const hairZ = frontOf(hairR), skinZ = (x, y) => Math.sqrt(Math.max(0, HR * HR - x * x - y * y));
function ballGeometry(surf, w, h) {
  const g = new THREE.SphereGeometry(1, w, h), p = g.attributes.position, rp = new Float32Array(p.count * 3);
  for (let i = 0; i < p.count; i++) {
    const d = [p.getX(i), p.getY(i), p.getZ(i)], r = surf(d);
    p.setXYZ(i, d[0] * r, d[1] * r, d[2] * r); rp[i * 3] = d[0] * r; rp[i * 3 + 1] = -d[1] * r; rp[i * 3 + 2] = d[2] * r;
  }
  g.deleteAttribute('uv'); g.computeVertexNormals(); g.setAttribute('rp', new THREE.Float32BufferAttribute(rp, 3));
  return g;
}
// curls: bumps over the cap (the drawing's scalloped ring round the skull) and over the beard (its curly edge) — spread
// evenly, so the outline is scalloped from every side; the front of the cap and the beard round the mouth stay smooth,
// as drawn (the ticks and the mouth are painted there)
function fib(n) { const out = []; for (let i = 0; i < n; i++) { const y = 1 - 2 * (i + 0.5) / n, r = Math.sqrt(1 - y * y), a = i * 2.399963; out.push([Math.cos(a) * r, y, Math.sin(a) * r]); } return out; }
function curlsGeometry() {
  const gs = [];
  fib(150).forEach((d, i) => {
    const p = d.map(v => v * (HR + 1));
    if (hairK(d, CAP) < 0.98 || p[1] < -12) return;
    if (p[2] > 14 && Math.hypot(p[0], p[1]) < HR - 13) return;
    gs.push(ball(p, 9 + 1.5 * (i % 2), 12));
  });
  const [cx, cy, cz] = BEARD.c, [ax, ay, az] = BEARD.a;
  fib(120).forEach((d, i) => {
    const p = [cx + d[0] * (ax - 5), cy + d[1] * (ay - 5), cz + d[2] * (az - 5)], l = Math.hypot(...p);
    if (d[1] > 0.3 && l < HR + 16) return;                      // the upper part is inside the skull or under the sideburns
    if (l < HR + 4) return;
    if (p[2] > 0 && Math.abs(p[0]) < 50 && p[1] > -96 && Math.hypot(p[0] / (ax - 14), (p[1] - cy) / (ay - 14)) < 1) return;   // the front, round the mouth
    if (p[2] > 0 && loopDist(p[0], -p[1]) < 12) return;
    gs.push(ball(p, 12.5 + 1.5 * (i % 2), 12));
  });
  return merge(gs);
}

const toWorld = g => { const p = g.attributes.position; for (let i = 0; i < p.count; i++) { const w = W(p.getX(i), p.getY(i), p.getZ(i)); p.setXYZ(i, w.x, w.y, w.z); } g.computeVertexNormals(); return g; };
const flipTris = g => { const ix = g.index.array; for (let k = 0; k < ix.length; k += 3) { const t = ix[k + 1]; ix[k + 1] = ix[k + 2]; ix[k + 2] = t; } return g; };

// ———————————————————— the character ————————————————————
export class Marat {
  constructor(E, old) {
    this.E = E; this.sk = E.skeleton;
    const sk = this.sk;
    this.R = restJoints(old, sk);
    this.root = new THREE.Group();
    this.live = new FaceLive(13);
    this.dyn = { sy: 0, v: 0, sway: [0, 0], swayV: [0, 0] };
    this.buildRest();
    this.body = makeBody({ id: 'marat-s11', label: { ru: 'Марат (С11)' }, skeleton: sk, positions: this.restPositions, triangles: this.restTriangles,
      joints: this.R, frames: Float64Array.from(old.frames), skin: null, parts: { names: ['head'], weights: this.restHead } });
    // the engine's own corrections: the arms off the barrel, and out of his big head
    this.retarget = makeRetarget(this.body, { corrections: { armsOff: { degrees: 20 }, armsOutOfHead: { margin: 0.08 } } });
    this.sample = newSample(sk.J);
  }
  J(n) { const j = this.sk.index[n]; return new V3(this.R[j * 3], this.R[j * 3 + 1], this.R[j * 3 + 2]); }

  buildRest() {
    const root = this.root, sk = this.sk;
    const line = 2.6 * S, NE = 2.3;
    // the barrel (the jacket) and the apron: lofts of the drawing's widths (front view) and depths (profile)
    const TW = [[79, 44], [84, 68], [92, 84], [108, 97], [128, 106], [160, 111], [196, 114], [240, 108], [268, 98], [280, 74], [285, 30]];
    const TF = [[79, 24], [92, 44], [112, 62], [140, 78], [175, 85], [204, 86], [240, 78], [264, 68], [280, 48], [285, 20]];
    const TB = [[79, 30], [90, 56], [112, 72], [140, 82], [210, 80], [250, 74], [270, 66], [280, 46], [285, 20]];
    const AW = [[243, 109.5], [262, 105.5], [284, 102], [330, 101], [400, 94], [426, 89], [433, 84]];
    const AF = [[243, 79.5], [262, 76], [284, 77], [330, 78], [400, 71], [433, 62]];
    const AB = [[243, 76], [262, 73], [330, 76], [400, 71], [433, 64]];
    const sect = (Wk, Fk, Bk) => (y, a, grow = 0) => {
      const w = keys(Wk, y) + grow, df = keys(Fk, y) + grow, db = keys(Bk, y) + grow, c = Math.cos(a), s = Math.sin(a);
      return [w * Math.sign(c) * Math.abs(c) ** (2 / NE), y, (s > 0 ? df : db) * Math.sign(s) * Math.abs(s) ** (2 / NE)];
    };
    const front = (Wk, Fk) => (x, y) => { const w = keys(Wk, y), df = keys(Fk, y), u = Math.min(0.985, Math.abs(x) / w); return df * Math.pow(Math.max(0, 1 - u ** NE), 1 / NE); };
    const torso = sect(TW, TF, TB), apron = sect(AW, AF, AB);
    const torsoFront = front(TW, TF), torsoBack = front(TW, TB), apronFront = front(AW, AF);
    const hemT = y => clamp((y - 300) / (433 - 300), 0, 1);
    this.skinned = [];
    const spine = ['Hips', 'Spine1', 'Spine2', 'Chest', 'Neck1'].map(n => sk.index[n]);
    const spineY = spine.map(j => this.R[j * 3 + 1]);
    const byHeight = (y) => {   // two joints and their weights for a rest height (world)
      if (y <= spineY[0]) return [[spine[0], 1]];
      for (let k = 0; k < spine.length - 1; k++) if (y <= spineY[k + 1]) { const t = sst((y - spineY[k]) / (spineY[k + 1] - spineY[k])); return [[spine[k], 1 - t], [spine[k + 1], t]]; }
      return [[spine[spine.length - 1], 1]];
    };
    const addSkinned = (geo, mat, ln = line, sway = false) => {
      toWorld(geo);
      const part = new Part(root, mat, ln, geo); part.set(geo);
      const p = geo.attributes.position, wts = [], sw = [];
      for (let i = 0; i < p.count; i++) { wts.push(byHeight(p.getY(i))); sw.push(sway ? hemT(FEET - p.getY(i) / S) ** 2 : 0); }
      this.skinned.push({ part, rest: Float32Array.from(p.array), wts, sway: sway ? sw : null });
      return part;
    };
    addSkinned(flipTris(loft(60, 64, (k, a) => torso(lerp(79, 285, k / 60), a))), paintMat(C.jacket, { shade: 0.1 }));
    addSkinned(flipTris(loft(48, 64, (k, a) => apron(lerp(243, 433, k / 48), a), { tips: [[0, 243, 0], [0, 418, 0]] })), paintMat(C.apron, { shade: 0.1 }), line, true);
    // the waistband and its bow, a little to the side, with two tails
    addSkinned(flipTris(loft(8, 64, (k, a) => { const y = lerp(242, 270, k / 8); return apron(y, a, 0.6 + 1.8 * Math.sin(Math.PI * k / 8)); })), paintMat(C.apronSh, { shade: 0.1 }), 1.8 * S);
    const onApron = (lift = 0) => (u, v, h) => [u, v, apronFront(u, v) + lift + h];
    {
      const bx = 30, by = 258, z0 = 2.6;
      const lobes = [-1, 1].map(sd => pillow(outline([[bx, by - 3], [bx + sd * 18, by - 12], [bx + sd * 20, by + 8], [bx, by + 3]], 7), onApron(z0), { thick: 4.5, sink: 1, rings: 6, flip: sd < 0 }));
      const tails = [[[bx - 3, by + 4], [bx - 6, by + 17], [bx - 8, by + 30]], [[bx + 3, by + 4], [bx + 7, by + 15], [bx + 10, by + 26]]].map(ps => sweep(ps.map(([u, v]) => new V3(u, v, apronFront(u, v) + z0 + 1)), (i, a) => [Math.cos(a) * 3.2, Math.sin(a) * 1.6], { radial: 10, up: new V3(1, 0, 0), flip: true }));
      addSkinned(merge([...lobes, ...tails, flipTris(ball([bx, by, apronFront(bx, by) + z0 + 2.5], [5, 5, 4], 14))]), paintMat(C.apronSh, { shade: 0.1 }), 2 * S);
    }
    // the pocket (a flat patch: its outline is its ink), the apron's two folds, the jacket's flap, in ink
    addSkinned(pillow(outline([[-56, 322], [-12, 324], [-14, 366], [-34, 372], [-54, 366]], 6, 0.6), onApron(0.2), { thick: 1.6, sink: 1, rings: 4, profile: s => Math.min(1, (1 - s) * 6) }), paintMat(C.apron, { shade: 0.1 }), 2 * S, true);
    const inkOn = (surf, pts, r = 1) => sweep(through(pts.map(([u, v]) => new V3(u, v, surf(u, v) + 0.3)), 8), circle(() => r), { radial: 6, flip: true });
    addSkinned(merge([inkOn(apronFront, [[-38, 300], [-41, 365], [-44, 428]]), inkOn(apronFront, [[36, 300], [40, 365], [44, 426]])]), paintMat(C.ink, { shade: 0 }), 0, true);
    addSkinned(inkOn(torsoFront, [[-30, 86], [-40, 118], [-44, 150], [-42, 200], [-40, 243]], 1.1), paintMat(C.ink, { shade: 0 }), 0);
    // two rows of brass buttons
    addSkinned(merge([140, 178, 216].flatMap(y => [-22, 22].map(x => flipTris(ball([x, y, torsoFront(x, y) + 1.2], [4.4, 4.4, 2.4], 12))))), paintMat(C.brass, { shine: 0.06 }), 1.6 * S);
    // the striped towel over his right shoulder: a ribbon down the chest, over the top, a little down the back
    {
      const tx = -70, pts = [];
      for (let y = 198; y >= 92; y -= 6) pts.push(new V3(tx, y, torsoFront(tx, y) + 3));
      pts.push(new V3(tx, 82, 18), new V3(tx, 79, 0), new V3(tx, 84, -26));
      for (let y = 96; y <= 150; y += 6) pts.push(new V3(tx, y, -torsoBack(tx, y) - 3));
      const path = through(pts, 6), n = path.length, cT = raw(C.towel).toArray(), cS = raw(C.apron).toArray();
      let L = 0; const along = path.map((p, i) => (L += i ? p.distanceTo(path[i - 1]) : 0));
      const g = sweep(path, (i, a) => [Math.cos(a) * 18, Math.sin(a) * 2.4], { radial: 14, up: new V3(1, 0, 0), flip: true,
        color: i => ((along[i] > 24 && along[i] < 31) || (along[i] > 38 && along[i] < 45)) ? cS : cT });
      addSkinned(g, paintMat('#ffffff', { vc: true, shade: 0.1 }));
    }

    // limbs (rebuilt every frame)
    this.arms = {}; this.sleeves = {}; this.legs = {}; this.gloves = {};
    for (const sd of ['Left', 'Right']) {
      this.arms[sd] = new Part(root, paintMat(C.skin, { shade: 0.09 }), line);
      this.sleeves[sd] = new Part(root, paintMat(C.jacket, { shade: 0.1 }), line);
      this.legs[sd] = new Part(root, paintMat(C.pants, { shade: 0.1 }), line);
      this.gloves[sd] = new Part(root, paintMat(C.glove, { shade: 0.08 }), line);
    }
    // shoes: rigid on the foot, made at rest around the ankle (the drawing's side shoe, its front width), at 1.2
    this.shoes = {};
    const SS = 1.2;
    for (const sd of ['Left', 'Right']) {
      const ank = this.J(sd + 'Foot'), toe = this.J(sd + 'ToeEnd'), sg = sd === 'Left' ? 1 : -1;
      const fwd = new V3(toe.x - ank.x, 0, toe.z - ank.z).normalize().applyAxisAngle(new V3(0, 1, 0), sg * 0.16), side = new V3().crossVectors(new V3(0, 1, 0), fwd);
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
      const shoeP = new Part(grp, paintMat(C.shoe, { shine: 0.035, shade: 0.12 }), line); shoeP.set(sg > 0 ? flipTris(place(shoeG)) : place(shoeG));
      const soleP = new Part(grp, paintMat(C.sole, { shade: 0 }), line); soleP.set(sg > 0 ? flipTris(place(soleG)) : place(soleG));
      let lo = Infinity; for (const g of [shoeP.mesh.geometry, soleP.mesh.geometry]) { const p = g.attributes.position; for (let i = 0; i < p.count; i++) lo = Math.min(lo, p.getY(i)); }
      for (const g of [shoeP.mesh.geometry, soleP.mesh.geometry]) { g.translate(0, -lo, 0); g.computeBoundingSphere(); }
      this.shoes[sd] = { grp, parts: [shoeP, soleP], rest: ank };
    }
    // the head: a group on the Head joint, in head units (× HS × S), centred at the head's centre; no neck
    this.headPivot = this.J('Head');
    this.headC = W(0, -4, 8);
    this.head = new THREE.Group(); root.add(this.head);
    this.faceCanvas = document.createElement('canvas'); this.faceCanvas.width = (X1 - X0) * PX; this.faceCanvas.height = (Y1 - Y0) * PX;
    this.faceTex = new THREE.CanvasTexture(this.faceCanvas); this.faceTex.colorSpace = THREE.NoColorSpace; this.faceTex.anisotropy = 4;
    const hl = 2.6, box = new THREE.Vector4(X0, X1, Y0, Y1);
    new Part(this.head, paintMat(C.skin, { paint: 3, map: this.faceTex, shade: 0.08, box }), hl).set(ballGeometry(() => HR, 96, 72));
    new Part(this.head, paintMat(C.hair, { paint: 3, map: this.faceTex, shade: 0.14, box }), hl).set(ballGeometry(hairR, 200, 150));
    new Part(this.head, paintMat(C.hair, { shade: 0.14 }), hl).set(curlsGeometry());
    // ears: flat cushions out of the curls, with an inner line
    const earAt = (sd, u, v, h) => { const b = 0.6, n = new V3(sd * Math.sin(b), 0, Math.cos(b)), o = new V3(sd * Math.cos(b), 0, -Math.sin(b)); return new V3(sd * 65, -(4 + v), -4).addScaledVector(o, u).addScaledVector(n, h); };
    new Part(this.head, paintMat(C.skin, { shade: 0.12 }), hl).set(merge([-1, 1].map(sd => pillow(outline([[0, -17], [15, -14], [18, 4], [9, 16], [-2, 13]].map(([u, v]) => [u * sd, v]), 6), (u, v, h) => earAt(sd, u * sd, v, h).toArray(), { thick: 4, sink: 4, rings: 5, flip: sd > 0 }))));
    new Part(this.head, paintMat(C.ink, { shade: 0 }), 0).set(merge([-1, 1].map(sd => sweep(through([[4, -7], [11, -4], [9, 6]].map(([u, v]) => earAt(sd, u, v, 3.2 - Math.abs(u - 8) * 0.12)), 6), circle(() => 1), { radial: 6 }))));
    // the broad nose over the moustache
    new Part(this.head, paintMat(C.nose, { shine: 0.045, shade: 0.12 }), 2.3).set(ball([0, -22, 69], [17.5, 12.5, 14], 28));
    // shadow on the floor (the drawing's soft ellipse)
    const sc = document.createElement('canvas'); sc.width = sc.height = 128; const sg2 = sc.getContext('2d'); const grd = sg2.createRadialGradient(64, 64, 10, 64, 64, 64); grd.addColorStop(0, 'rgba(27,23,20,0.26)'); grd.addColorStop(0.7, 'rgba(27,23,20,0.2)'); grd.addColorStop(1, 'rgba(27,23,20,0)'); sg2.fillStyle = grd; sg2.fillRect(0, 0, 128, 128);
    this.shadow = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(sc), transparent: true, depthWrite: false }));
    this.shadow.rotation.x = -Math.PI / 2; this.shadow.scale.set(300 * S * 1.6, 110 * S * 1.6, 1); this.shadow.renderOrder = -1;
    // what the engine measures the body by: our rest mesh
    this.setFace(vecExpr(exprVec(EXPR.neutral)), { look: [0, 0], blink: 0 });
    this.apply(this.standPose(false), true);
    const pos = [], tri = [], hd = []; let off = 0;
    this.root.updateMatrixWorld(true);
    this.root.traverse(o => { if (o.isMesh && o.material?.uniforms?.uColor && o.geometry.index) { const g = o.geometry, p = g.attributes.position, v = new V3(), h = o.parent === this.head && o.material.uniforms.uPaint.value > 2.5; for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i).applyMatrix4(o.matrixWorld); pos.push(v.x, v.y, v.z); hd.push(h ? 255 : 0); } for (const i of g.index.array) tri.push(i + off); off += p.count; } });
    this.restPositions = Float32Array.from(pos); this.restTriangles = Uint32Array.from(tri); this.restHead = Uint8Array.from(hd);   // the head's ball and beard: the engine's head ball
  }

  // ———— poses ————
  // a still standing pose made from the rest (not a motion): the drawing's — heavy arms hanging off the barrel
  standPose(arms = true, o = {}) {
    const sk = this.sk, J = sk.J, pose = { Q: new Float64Array(J * 4), P: Float64Array.from(this.R), floor: 0 };
    for (let j = 0; j < J; j++) pose.Q[j * 4 + 3] = 1;
    const B = this.body || { skeleton: sk, joints: this.R }, hip = () => getV(pose.P, sk.index.Hips);
    if (arms) for (const [sd, sg] of [['Left', 1], ['Right', -1]]) {
      const A = sk.index[sd + 'Arm'], F = sk.index[sd + 'ForeArm'], H = sk.index[sd + 'Hand'];
      const a = normalize(sub(getV(this.R, F), getV(this.R, A)));
      turnUnder(pose, sk, A, qBetween(a, normalize([sg * Math.sin(0.49), -Math.cos(0.49), 0.04]))); buildPose(pose, B, hip());
      const f = normalize(sub(getV(pose.P, H), getV(pose.P, F))), wantF = normalize([sg * Math.sin(-0.15), -Math.cos(0.15), 0.14]);
      turnUnder(pose, sk, F, qBetween(f, wantF)); buildPose(pose, B, hip());
      const mid = normalize(qRot(getQ(pose.Q, H), sub(getV(this.R, sk.index[sd + 'HandMiddle1']), getV(this.R, H))));
      turnUnder(pose, sk, H, qBetween(mid, normalize([0, -1, 0.1]))); buildPose(pose, B, hip());
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
    // skinned pieces (linear blend over the spine joints); the apron's lower part sways (a spring, see app.js)
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
    this.head.scale.set(S * HS * sq[0], S * HS * sq[1], S * HS * sq[0]);
    // hoses: the arm swells in the forearm (bare skin) below the rolled-up sleeve with its cuff; thick trouser legs
    const AR = [[0, 16], [0.5, 22], [1, 13.5]], N = 36, cut = Math.round(N * 0.44);
    const SL = [[0, 20], [0.3, 22.5], [0.36, 23.5], [0.385, 28.5], [0.44, 28.5]];
    for (const sd of ['Left', 'Right']) {
      const ap = hosePath(J(sd + 'Arm'), J(sd + 'ForeArm'), J(sd + 'Hand'), 1.0, N);
      this.arms[sd].set(sweep(ap, circle(i => keys(AR, i / N) * S), { radial: 20 }));
      this.sleeves[sd].set(sweep(ap.slice(0, cut + 1), circle(i => keys(SL, i / N) * S), { radial: 22, capDepth: 0.12 }));
      const lp = hosePath(J(sd + 'Leg'), J(sd + 'Shin'), J(sd + 'Foot'), 1.0, N);
      this.legs[sd].set(sweep(lp, circle(i => lerp(25, 20, i / N) * S), { radial: 24, capEnd: false }));
      this.gloves[sd].set(this.glove(pose, sd, P));
      const sh = this.shoes[sd], j = ix[sd + 'Foot'], q = Qj(j);
      sh.grp.quaternion.copy(q); sh.grp.position.copy(P(j).sub(sh.rest.clone().applyQuaternion(q)));
    }
    const hips = J('Hips'); this.shadow.position.set(hips.x, (pose.floor ?? 0) + 0.002, hips.z + 0.02);
    this.pose = pose;
  }
  // a white glove: palm, three fat fingers and a thumb along the posed finger joints, a rolled cuff (П2's hand), at 1.2
  glove(pose, sd, P) {
    const ix = this.sk.index, J = n => P(ix[n]), GS = 1.2;
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
    this.sq = [e.sq[0] - this.dyn.sy * 0.5, e.sq[1] + this.dyn.sy + mouthOpen(e.mouth) * 0.0012];
  }
}

export const createStage = (canvas, o = {}) => stage(canvas, { ...o, body: 'moood-man', make: (E, old) => new Marat(E, old) });
