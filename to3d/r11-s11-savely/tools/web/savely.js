// Савелий Петрович, rubber-hose 1930s (style С11), in 3D on moood's SOMA skeleton.
// Not Anny: his proportions (a ball head as wide as his shoulders, 2.7 heads tall, limbs as bending hoses, gloves,
// big shoes) are built with the expressive constructor of experiments/toon (gallery П2): the limbs are sweeps along
// an arc through shoulder–elbow–wrist (hip–knee–ankle) rebuilt every frame from the posed joints; the body is a loft
// of the drawing's own widths and depths; the head is the drawing's two balls (skull and jowls) with the features laid
// on it as the drawing's Head.project() lays them. The skeleton is SOMA's 77 joints with the drawing's bone lengths
// and Anny's joint frames, so the engine (engine/src: retarget, corrections) carries Kimodo's motions onto it.
// Units: the drawing's (styles/s11-rubberhose/tools/savely.py: head radius 64, soles at y 350), 1 unit = S metres.
import * as THREE from 'three';
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { makeRetarget, build as buildPose, turnUnder } from '../../../../engine/src/retarget.js';
import { newSample } from '../../../../engine/src/motion.js';
import { qAxisAngle, qRot, qMul, qBetween, getQ, setQ, getV, normalize, sub } from '../../../../engine/src/math.js';
import { sweep, hosePath, circle, keys, loft, pillow, outline, cloud, merge, ball, bezier, through, geom, lerp, clamp, sst } from './geo.js';
import { drawFace, X0, X1, Y0, Y1, PX, EXPR, vecExpr, mixExpr, exprVec, INK as INKC } from './face.js';
import { FaceLive } from './live.js';
const V3 = THREE.Vector3;

export const S = 0.004, FEET = 350, XC = 3;              // metres per drawing unit; soles; the body's middle in x
const W = (x, y, z = 0) => new V3((x - XC) * S, (FEET - y) * S, z * S);   // drawing (x, y down, z forward) → world
// the drawing's paints (savely.py, lib.py)
const C = { skin: '#f3d2b4', nose: '#e8957c', hair: '#f4f0e6', hairSh: '#cfc8b8', shirt: '#f1ead8', vest: '#c9952f', pants: '#6b4a35',
  shoe: '#2a221e', sole: '#1b1714', brass: '#d9a93a', tie: '#7a2c24', glove: '#fbf7ee', strap: '#3b2e28', loupe: '#2f2622', glass: '#9fb7b9', ink: '#1b1714' };

// ———————————————————— the skeleton: SOMA's joints at the drawing's places, Anny's frames ————————————————————
// A joint's bone keeps Anny's rest direction (what Kimodo's rotations are measured against) and gets the drawing's
// length; the trunk's own offsets (hip width, shoulders) are set where the drawing has them.
function restJoints(old, sk) {
  const J = sk.J, R = old.joints, out = new Float64Array(J * 3), ix = sk.index;
  const len = { spine: 92 / 211, neck: 0.57, upperArm: 52 * S / 0.2754, foreArm: 50 * S / 0.2504, hand: 1.05, thigh: 40 * S / 0.4012, shin: 43 * S / 0.4371, foot: 0.92 };
  const groupOf = n => /^(Spine1|Spine2|Chest)$/.test(n) ? len.spine * 1000 * S : /^(Neck1|Neck2|Head)$/.test(n) ? len.neck
    : /ForeArm$/.test(n) ? len.upperArm : /Hand$/.test(n) && !/Hand[A-Z]/.test(n) ? len.foreArm : /Hand/.test(n) ? len.hand
    : /Shin$/.test(n) ? len.thigh : /Foot$/.test(n) ? len.shin : /Toe/.test(n) ? len.foot : 1;
  const set = (n, v) => { const j = ix[n]; out[j * 3] = v.x; out[j * 3 + 1] = v.y; out[j * 3 + 2] = v.z; };
  for (let j = 0; j < J; j++) {
    const n = sk.names[j], p = sk.parent[j];
    if (p < 0) { set(n, W(XC, 232, 0)); continue; }
    const k = groupOf(n);
    for (let d = 0; d < 3; d++) out[j * 3 + d] = out[p * 3 + d] + (R[j * 3 + d] - R[p * 3 + d]) * k;
    if (/^(Left|Right)Shoulder$/.test(n)) set(n, W(XC + (n[0] === 'L' ? 1 : -1) * 12, 112, 4));
    if (/^(Left|Right)Arm$/.test(n)) set(n, W(XC + (n[0] === 'L' ? 1 : -1) * 40, 113, 0));
    if (/^(Left|Right)Leg$/.test(n)) set(n, W(XC + (n[0] === 'L' ? 1 : -1) * 23, 244, 2));
  }
  return out;
}

const raw0 = h => { const c = new THREE.Color(); c.setStyle(h, THREE.LinearSRGBColorSpace); return c.toArray(); };
// ———————————————————— the look: flat paint, a second tone, a shine, painted marks; an ink hull ————————————————————
const VS = `
attribute vec3 rp;
varying vec3 vN; varying vec3 vRp; varying vec3 vCol;
void main() {
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  vN = normalize(normalMatrix * normal); vRp = rp;
#ifdef VCOL
  vCol = color;
#else
  vCol = vec3(1.0);
#endif
  gl_Position = projectionMatrix * mv;
}`;
const FS = `
uniform vec3 uColor; uniform float uShade, uShine, uPaint, uBW; uniform sampler2D uMap; uniform vec4 uMapBox;
varying vec3 vN; varying vec3 vRp; varying vec3 vCol;
const vec3 INK = vec3(${raw0(C.ink).map(v => v.toFixed(4)).join(',')});
float seg(vec2 p, vec2 a, vec2 b) { vec2 pa = p - a, ba = b - a; float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0); return length(pa - ba * h); }
vec3 srgb(vec3 c) { return c; }
void main() {
  vec3 c = uColor * vCol;
  vec2 p = vRp.xy;
  if (uPaint > 0.5 && uPaint < 1.5 && vRp.z > 0.0) {          // the waistcoat: shirt in the V, ink lines, pocket
    vec3 shirt = vec3(${raw0(C.shirt).map(v => v.toFixed(4)).join(',')});
    float vl = mix(-7.0, 3.0, clamp((p.y - 106.0) / 44.0, 0.0, 1.0)), vr = mix(11.0, 3.0, clamp((p.y - 104.0) / 46.0, 0.0, 1.0));
    bool inV = p.y < 150.0 && p.x > vl && p.x < vr;
    if (p.y < 100.0 || inV) c = shirt;
    float d = min(seg(p, vec2(-7.0, 106.0), vec2(3.0, 150.0)), seg(p, vec2(11.0, 104.0), vec2(3.0, 150.0)));
    d = min(d, max(seg(p, vec2(-60.0, 101.0), vec2(-7.0, 105.0)), 0.0) + (p.y < 108.0 ? 0.0 : 99.0));
    d = min(d, seg(p, vec2(11.0, 103.0), vec2(60.0, 101.0)) + (p.y < 108.0 ? 0.0 : 99.0));
    if (d < 1.6) c = INK;
    if (seg(p, vec2(2.0, 150.0), vec2(4.0, 232.0)) < 1.1) c = INK;
    if (seg(p, vec2(32.0, 196.0), vec2(46.0, 196.0)) < 1.2) c = INK;
  } else if (uPaint > 1.5 && uPaint < 2.5 && vRp.z > 0.0) {   // the trousers' fly
    if (seg(p, vec2(-1.0, 240.0), vec2(-1.0, 262.0)) < 1.0) c = INK;
  } else if (uPaint > 2.5) {                                    // the head: the painted face, from the front
    vec2 uv = vec2((p.x - uMapBox.x) / (uMapBox.y - uMapBox.x), 1.0 - (p.y - uMapBox.z) / (uMapBox.w - uMapBox.z));
    vec4 f = texture2D(uMap, uv);
    float k = smoothstep(4.0, 16.0, vRp.z);
    c = mix(c, f.rgb, f.a * k);
  }
  vec3 n = normalize(vN);
  float lam = dot(n, normalize(vec3(-0.45, 0.6, 0.65)));
  c *= mix(1.0 - uShade, 1.0, smoothstep(-0.05, 0.05, lam));
  if (uShine > 0.0) { float s = dot(n, normalize(vec3(-0.5, 0.62, 0.6))); if (s > 1.0 - uShine) c = mix(c, vec3(1.0), 0.72); }
  gl_FragColor = vec4(c, 1.0);
}`;
const HVS = `
uniform float uLine;
void main() { gl_Position = projectionMatrix * modelViewMatrix * vec4(position + normal * uLine, 1.0); }`;
const HFS = `void main() { gl_FragColor = vec4(${raw0(C.ink).map(v => v.toFixed(4)).join(',')}, 1.0); }`;

function paintMat(color, o = {}) {
  const m = new THREE.ShaderMaterial({
    vertexShader: VS, fragmentShader: FS, defines: o.vc ? { VCOL: 1 } : {}, vertexColors: !!o.vc,
    uniforms: { uColor: { value: raw(color) }, uShade: { value: o.shade ?? 0.1 }, uShine: { value: o.shine ?? 0 }, uPaint: { value: o.paint ?? 0 },
      uBW: { value: 0 }, uMap: { value: o.map || null }, uMapBox: { value: new THREE.Vector4(X0, X1, Y0, Y1) } },
  });
  return m;
}
const raw = h => { const c = new THREE.Color(); c.setStyle(h, THREE.LinearSRGBColorSpace); return c; };   // paints as written: the shaders work in the drawing's sRGB numbers
const hullMat = line => new THREE.ShaderMaterial({ vertexShader: HVS, fragmentShader: HFS, side: THREE.BackSide, uniforms: { uLine: { value: line } } });

// a part: a mesh in its paint, and its ink hull sharing the geometry
class Part {
  constructor(parent, mat, line, geo = new THREE.BufferGeometry()) {
    this.mesh = new THREE.Mesh(geo, mat); this.hull = new THREE.Mesh(geo, line > 0 ? hullMat(line) : null);
    this.mesh.frustumCulled = this.hull.frustumCulled = false;
    parent.add(this.mesh); if (line > 0) parent.add(this.hull);
  }
  set(geo) {
    if (!geo.attributes.rp) geo.setAttribute('rp', new THREE.Float32BufferAttribute(new Float32Array(geo.attributes.position.count * 3), 3));
    const old = this.mesh.geometry; this.mesh.geometry = this.hull.geometry = geo; old.dispose();
  }
}

// ———————————————————— the head: the drawing's skull ball and jowl ball, in head units (y up, centre 0) ————————————————————
const HR = 64, MUZ = { c: [0, -36, 22], a: [62, 46, 40] };          // Head(64).muzzle(36, 62, 46, 40, 22)
function headR(d) {   // the head's surface along a direction from its centre: the two balls joined softly
  const [cx, cy, cz] = MUZ.c, [ax, ay, az] = MUZ.a;
  const A = (d[0] / ax) ** 2 + (d[1] / ay) ** 2 + (d[2] / az) ** 2, B = -2 * (d[0] * cx / ax ** 2 + d[1] * cy / ay ** 2 + d[2] * cz / az ** 2), Cc = (cx / ax) ** 2 + (cy / ay) ** 2 + (cz / az) ** 2 - 1;
  const t = (-B + Math.sqrt(B * B - 4 * A * Cc)) / (2 * A), k = 14;
  return 0.5 * (HR + t + Math.sqrt((HR - t) ** 2 + k * k)) - 0.5 * k * 0.5;
}
// the head's front surface at (x, y): z, found along the line of sight from the front
function frontZ(x, y) {
  let lo = 0, hi = 140;
  const inside = z => { const l = Math.hypot(x, y, z); return l < headR([x / l, y / l, z / l]); };
  if (!inside(0)) return 0;
  for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; if (inside(m)) lo = m; else hi = m; }
  return lo;
}
function headNormal(x, y) { const e = 0.8, z = frontZ(x, y); const zx = (frontZ(x + e, y) - frontZ(x - e, y)) / (2 * e), zy = (frontZ(x, y + e) - frontZ(x, y - e)) / (2 * e); return new V3(-zx, -zy, 1).normalize(); }
const DR = (x, y) => [x, -y];   // a drawing point on the head (y down) → head units (y up)

function headGeometry() {
  const g = new THREE.SphereGeometry(1, 144, 108), p = g.attributes.position, rp = new Float32Array(p.count * 3);
  for (let i = 0; i < p.count; i++) {
    const d = [p.getX(i), p.getY(i), p.getZ(i)], r = headR(d);
    p.setXYZ(i, d[0] * r, d[1] * r, d[2] * r); rp[i * 3] = d[0] * r; rp[i * 3 + 1] = -d[1] * r; rp[i * 3 + 2] = d[2] * r;
  }
  g.deleteAttribute('uv'); g.computeVertexNormals(); g.setAttribute('rp', new THREE.Float32BufferAttribute(rp, 3));
  return g;
}
// a cloud of white hair as a lump of balls (the drawing's scalloped clouds, seen round)
function cloudBall(c, r, out, n = 7, seg = 16) {
  const gs = [ball(c, [r[0] * 0.8, r[1] * 0.8, r[2] * 0.8], seg)];
  for (let i = 0; i < n; i++) {
    const a = -Math.PI * 0.5 + Math.PI * (i + 0.5) / n;
    for (const z of [-0.45, 0.45]) {
      const dir = new V3(Math.cos(a) * out.x, Math.sin(a), 0).normalize(), q = new V3(dir.x * r[0] * 0.62, dir.y * r[1] * 0.62, z * r[2] * 0.8);
      gs.push(ball([c[0] + q.x, c[1] + q.y, c[2] + q.z], r[0] * 0.42, seg));
    }
    const dir = new V3(Math.cos(a) * out.x, Math.sin(a), 0);
    gs.push(ball([c[0] + dir.x * r[0] * 0.66, c[1] + dir.y * r[1] * 0.66, c[2]], r[0] * 0.44, seg));
  }
  return merge(gs);
}
// a pillow on the face: a shape drawn on the front of the head (drawing coordinates, y down) puffed out of the skin
const onFace = (lift = 0) => (u, v, h) => { const [x, y] = DR(u, v), z = frontZ(x, y); return [x, y, z + lift + h]; };

// ———————————————————— the character ————————————————————
export class Savely {
  constructor(E, old) {
    this.E = E; this.sk = E.skeleton;
    const sk = this.sk;
    this.R = restJoints(old, sk);
    this.root = new THREE.Group();
    this.live = new FaceLive(5);
    this.dyn = { sy: 0, v: 0, lastY: null, lastV: 0 };
    this.buildRest();
    // the body the engine retargets onto: our rest mesh, SOMA's joints at our places, Anny's frames
    this.body = makeBody({ id: 'savely-s11', label: { ru: 'Савелий Петрович (С11)' }, skeleton: sk, positions: this.restPositions, triangles: this.restTriangles,
      joints: this.R, frames: Float64Array.from(old.frames), skin: null, parts: { names: ['head'], weights: this.restHead } });
    // the engine's own corrections: the arms a little off the body (his belly), and out of his big head
    this.retarget = makeRetarget(this.body, { corrections: { armsOff: { degrees: 15 }, armsOutOfHead: { margin: 0.06 } } });
    this.sample = newSample(sk.J);
  }
  J(n) { const j = this.sk.index[n]; return new V3(this.R[j * 3], this.R[j * 3 + 1], this.R[j * 3 + 2]); }

  buildRest() {
    const root = this.root, sk = this.sk;
    const line = 2.6 * S;
    // torso: shirt and waistcoat, the drawing's widths (front) and depths (profile) at each height
    const TW = [[86, 22], [96, 32], [112, 40], [140, 48], [165, 52], [190, 53], [210, 50], [226, 40], [236, 24], [241, 6]];
    const TF = [[86, 12], [96, 18], [112, 24], [126, 33], [150, 46], [172, 54], [195, 54], [214, 47], [228, 35], [238, 16], [241, 4]];
    const TB = [[86, 14], [96, 21], [140, 31], [200, 29], [226, 22], [236, 14], [241, 4]];
    const ring = (yw, yf, yb, y0, y1, Kn, nexp = 2.3) => (k, a) => {
      const y = lerp(y0, y1, k / Kn), w = keys(yw, y), df = keys(yf, y), db = keys(yb, y), c = Math.cos(a), s = Math.sin(a);
      const x = w * Math.sign(c) * Math.abs(c) ** (2 / nexp), z = (s > 0 ? df : db) * Math.sign(s) * Math.abs(s) ** (2 / nexp);
      return [x, y, z];
    };
    const drawingLoft = (fn, Kn, Rn) => { const g = loft(Kn, Rn, (k, a) => fn(k, a), { flip: true }); return toWorldRP(g); };
    const toWorldRP = g => {   // geometry made in drawing units (x, y down, z) → world, keeping the drawing coordinates for painting
      const p = g.attributes.position, rp = new Float32Array(p.count * 3);
      for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i); rp[i * 3] = x; rp[i * 3 + 1] = y; rp[i * 3 + 2] = z; const w = W(x + XC, y, z); p.setXYZ(i, w.x, w.y, w.z); }
      g.setAttribute('rp', new THREE.Float32BufferAttribute(rp, 3)); g.computeVertexNormals(); return g;
    };
    this.torsoFront = (x, y) => { const w = keys(TW, y), df = keys(TF, y), n = 2.3, u = Math.min(1, Math.abs(x) / w); return df * Math.pow(Math.max(0, 1 - u ** n), 1 / n); };
    // skinned pieces: [geometry at rest (world), weights by height over the spine]
    this.skinned = [];
    const spine = ['Hips', 'Spine1', 'Spine2', 'Chest', 'Neck1'].map(n => sk.index[n]);
    const spineY = spine.map(j => this.R[j * 3 + 1]);
    const byHeight = (y) => {   // two joints and their weights for a rest height (world)
      if (y <= spineY[0]) return [[spine[0], 1]];
      for (let k = 0; k < spine.length - 1; k++) if (y <= spineY[k + 1]) { const t = sst((y - spineY[k]) / (spineY[k + 1] - spineY[k])); return [[spine[k], 1 - t], [spine[k + 1], t]]; }
      return [[spine[spine.length - 1], 1]];
    };
    const addSkinned = (geo, mat, weights, ln = line) => {
      const part = new Part(root, mat, ln, geo); part.set(geo);
      const p = geo.attributes.position, wts = [];
      for (let i = 0; i < p.count; i++) wts.push(weights(p.getX(i), p.getY(i), p.getZ(i)));
      this.skinned.push({ part, rest: Float32Array.from(p.array), wts });
      return part;
    };
    const torso = drawingLoft(ring(TW, TF, TB, 86, 241, 56), 56, 44);
    addSkinned(torso, paintMat(C.vest, { paint: 1 }), (x, y) => byHeight(y));
    // trousers: the top as a loft (rigid on the pelvis); the legs are hoses
    const PW = [[204, 42], [220, 44], [245, 46], [262, 45], [270, 34], [275, 8]], PF = [[204, 30], [240, 31], [262, 30], [270, 22], [275, 5]], PB = [[204, 28], [240, 30], [262, 29], [270, 22], [275, 5]];
    const pants = drawingLoft(ring(PW, PF, PB, 204, 275, 30, 2.6), 30, 44);
    addSkinned(pants, paintMat(C.pants, { paint: 2 }), () => [[sk.index.Hips, 1]]);
    // collar points, tie, buttons, watch chain: on the waistcoat's front
    const onTorso = (lift = 0) => (u, v, h) => { const z = this.torsoFront(u - XC, v); return [u - XC, v, z + lift + h]; };
    const dpiece = (g) => toWorldRP(g);
    const cx = 5;
    const collar = merge([-1, 1].map(sd => pillow(outline([[cx + sd * 14, 96], [cx + sd * 2, 100], [cx + sd * 6, 111]], 6), onTorso(0.5), { thick: 2.2, sink: 1.5, rings: 4, flip: sd > 0 })));
    addSkinned(dpiece(collar), paintMat(C.shirt), (x, y) => byHeight(y));
    const tie = pillow(outline([[cx - 4, 102], [cx + 4, 102], [cx + 6, 132], [cx, 140], [cx - 6, 132]], 6), onTorso(0.6), { thick: 2.5, sink: 1.5, rings: 5 });
    addSkinned(dpiece(tie), paintMat(C.tie), (x, y) => byHeight(y));
    const buttons = merge([166, 188, 210].map(y => { const x = cx + 7 - XC; return ball([x, y, this.torsoFront(x, y) + 1.2], [3.2, 3.2, 2], 12); }));
    addSkinned(dpiece(buttons), paintMat(C.brass, { shine: 0.06 }), (x, y) => byHeight(y), 1.6 * S);
    const chainPts = through([[cx + 7, 188], [cx + 22, 201], [cx + 36, 195]].map(([u, v]) => new V3(u - XC, v, this.torsoFront(u - XC, v) + 1.2)), 8);
    addSkinned(dpiece(sweep(chainPts, circle(() => 1.1), { radial: 8 })), paintMat(C.brass), (x, y) => byHeight(y), 0.8 * S);

    // limbs (rebuilt every frame): arms and legs as hoses, gloves, shoes
    this.arms = { Left: new Part(root, paintMat(C.shirt), line), Right: new Part(root, paintMat(C.shirt), line) };
    this.legs = { Left: new Part(root, paintMat(C.pants), line), Right: new Part(root, paintMat(C.pants), line) };
    this.gloves = { Left: new Part(root, paintMat(C.glove, { shade: 0.08 }), line), Right: new Part(root, paintMat(C.glove, { shade: 0.08 }), line) };
    // shoes: rigid on the foot, made at rest around the ankle (the drawing's side shoe, its front width)
    this.shoes = {};
    for (const sd of ['Left', 'Right']) {
      const ank = this.J(sd + 'Foot'), toe = this.J(sd + 'ToeEnd'), sg = sd === 'Left' ? 1 : -1;
      const fwd = new V3(toe.x - ank.x, 0, toe.z - ank.z).normalize().applyAxisAngle(new V3(0, 1, 0), sg * 0.16), side = new V3().crossVectors(new V3(0, 1, 0), fwd);
      const top = [[-22, 8], [-18, 2], [-10, -4], [6, -5], [16, -3], [34, -5], [46, 1], [51, 9], [52, 14]], bot = 21;
      const wid = [[-22, 12], [-14, 17], [4, 19], [26, 25], [40, 26], [48, 21], [52, 10]];
      const u0 = -23, u1 = 52.5, K = 40, ankY = ank.y / S;   // ankle height in units over the rest floor
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
      const place = g => {   // shoe units (x across, y down from the ankle, z forward) → world at rest
        const p = g.attributes.position;
        for (let i = 0; i < p.count; i++) {
          const x = p.getX(i), y = p.getY(i), u = p.getZ(i);
          const w = ank.clone().addScaledVector(side, -x * S * sg).addScaledVector(fwd, u * S); w.y = (ankY - 3 - y) * S + 0;
          p.setXYZ(i, w.x, w.y, w.z);
        }
        g.computeVertexNormals(); return g;
      };
      // the sole's bottom at y 27 under the ankle-3 line: set the ankle line so the sole touches the floor
      const grp = new THREE.Group(); root.add(grp);
      const shoeP = new Part(grp, paintMat(C.shoe, { shine: 0.035, shade: 0.12 }), line); shoeP.set(place(shoeG));
      const soleP = new Part(grp, paintMat(C.sole, { shade: 0 }), line); soleP.set(place(soleG));
      // lift so the lowest point is the floor
      let lo = Infinity; for (const g of [shoeP.mesh.geometry, soleP.mesh.geometry]) { const p = g.attributes.position; for (let i = 0; i < p.count; i++) lo = Math.min(lo, p.getY(i)); }
      for (const g of [shoeP.mesh.geometry, soleP.mesh.geometry]) { g.translate(0, -lo, 0); g.computeBoundingSphere(); }
      this.shoes[sd] = { grp, parts: [shoeP, soleP], rest: ank };
    }
    // the head: a group on the Head joint, in head units (×S), centred at the head's centre
    this.headPivot = this.J('Head');
    this.headC = W(XC + 1, 31, 11);
    this.head = new THREE.Group(); root.add(this.head);
    this.faceCanvas = document.createElement('canvas'); this.faceCanvas.width = (X1 - X0) * PX; this.faceCanvas.height = (Y1 - Y0) * PX;
    this.faceTex = new THREE.CanvasTexture(this.faceCanvas); this.faceTex.colorSpace = THREE.NoColorSpace; this.faceTex.anisotropy = 4;
    const hl = 2.6;
    const ball0 = new Part(this.head, paintMat(C.skin, { paint: 3, map: this.faceTex, shade: 0.09, shine: 0.012 }), hl); ball0.set(headGeometry());
    // ears (behind the tufts), flat cushions facing forward-out
    const earG = merge([-1, 1].map(sd => {
      const o = outline([[0, -18], [16, -14], [18, 6], [8, 18], [-2, 14]].map(([u, v]) => [u * sd, v]), 6), b = 0.6;
      const n = new V3(sd * Math.sin(b), 0, Math.cos(b)), out = new V3(sd * Math.cos(b), 0, -Math.sin(b));
      return pillow(o, (u, v, h) => new V3(sd * 57, -(14 + v), -2).addScaledVector(out, u * sd).addScaledVector(n, h).toArray(), { thick: 4, sink: 4, rings: 5, flip: sd > 0 });
    }));
    new Part(this.head, paintMat(C.skin, { shade: 0.12 }), hl).set(earG);
    const earLines = merge([-1, 1].map(sd => {
      const b = 0.6, n = new V3(sd * Math.sin(b), 0, Math.cos(b)), out = new V3(sd * Math.cos(b), 0, -Math.sin(b));
      return sweep(through([[4, -8], [11, -4], [9, 8]].map(([u, v]) => new V3(sd * 57, -(14 + v), -2).addScaledVector(out, u).addScaledVector(n, 3.2 - Math.abs(u - 8) * 0.12)), 6), circle(() => 1), { radial: 6 });
    }));
    new Part(this.head, paintMat(C.ink, { shade: 0 }), 0).set(earLines);
    // white tufts over the ears
    const tufts = merge([-1, 1].map(sd => cloudBall([sd * 66, 6, 2], [22, 24, 21], { x: sd })));
    new Part(this.head, paintMat(C.hair, { shade: 0.12 }), hl).set(tufts);
    // the nose: a big round ball with a shine
    const noseG = ball([0, -28, 75], [15, 13.5, 15], 28);
    new Part(this.head, paintMat(C.nose, { shine: 0.05, shade: 0.12 }), hl).set(noseG);
    // brows and moustache: pillows rebuilt when the face changes
    this.brows = new Part(this.head, paintMat(C.hair, { shade: 0.12 }), hl);
    this.stache = new Part(this.head, paintMat(C.hair, { shade: 0.1 }), hl);
    this.stacheLines = new Part(this.head, paintMat(C.hairSh, { shade: 0 }), 0);
    // spectacles: two rings, a bridge, arms to the ears; a group that slides up the forehead in surprise
    this.glasses = new THREE.Group(); this.head.add(this.glasses);
    const ringG = [], glintG = [];
    for (const sd of [-1, 1]) {
      const cx2 = sd * 20, cy2 = -10, n = headNormal(cx2, cy2), cz = frontZ(cx2, cy2) + 5;
      const ex = new V3(1, 0, 0).addScaledVector(n, -n.x).normalize(), ey = new V3().crossVectors(n, ex);
      const pts = []; for (let k = 0; k <= 48; k++) { const a = k / 48 * Math.PI * 2; pts.push(new V3(cx2, cy2, cz).addScaledVector(ex, Math.cos(a) * 16).addScaledVector(ey, Math.sin(a) * 15)); }
      ringG.push(sweep(pts, circle(() => 1.25), { radial: 8, capStart: false, capEnd: false }));
      const gl = ball([0, 0, 0], [3, 5, 0.6], 10); const m = new THREE.Matrix4().makeBasis(ex, ey, n).setPosition(new V3(cx2, cy2, cz).addScaledVector(ex, -4).addScaledVector(ey, 5)); gl.applyMatrix4(m); glintG.push(gl);
      const outer = new V3(cx2, cy2, cz).addScaledVector(ex, sd * 16);
      const back = [outer, new V3(sd * 46, -8, frontZ(sd * 46, -8) + 2.5), new V3(sd * 56, -7, frontZ(sd * 56, -7) + 1), new V3(sd * 60, -7, 6)];
      ringG.push(sweep(through(back, 6), circle(() => 1), { radial: 6 }));
    }
    const bz = frontZ(0, -6) + 7;
    ringG.push(sweep(through([new V3(-4, -9, frontZ(-4, -9) + 5), new V3(0, -5, bz), new V3(4, -9, frontZ(4, -9) + 5)], 6), circle(() => 1.2), { radial: 6 }));
    new Part(this.glasses, paintMat(C.ink, { shade: 0 }), 0).set(merge(ringG));
    new Part(this.glasses, paintMat('#ffffff', { shade: 0 }), 0).set(merge(glintG));
    // the jeweller's loupe on its strap, pushed up on the forehead
    this.loupe = new THREE.Group(); this.head.add(this.loupe);
    const tilt = -0.42, nrm = new V3(0, Math.cos(tilt), Math.sin(tilt)), dd = 30, rr = Math.sqrt(66 ** 2 - dd * dd);
    const e1 = new V3(1, 0, 0), e2 = new V3().crossVectors(nrm, e1).normalize();
    const strap = []; for (let k = 0; k <= 96; k++) { const a = k / 96 * Math.PI * 2; const d = nrm.clone().multiplyScalar(dd).addScaledVector(e1, Math.cos(a) * rr).addScaledVector(e2, Math.sin(a) * rr); const r = headR(d.clone().normalize().toArray()) + 1.4; strap.push(d.normalize().multiplyScalar(r)); }
    new Part(this.loupe, paintMat(C.strap, { shade: 0.1 }), hl).set(sweep(strap, (i, a) => [Math.cos(a) * 2.6, Math.sin(a) * 1.4], { radial: 10, capStart: false, capEnd: false, up: nrm }));
    {
      const at = (() => { let best = null, bd = 1e9; for (const p of strap) { if (p.z < 0 || p.y < 0) continue; const d = Math.abs(p.x - 16); if (d < bd) { bd = d; best = p; } } return best; })();
      const n = at.clone().normalize(), down0 = new V3(0, -1, 0).addScaledVector(n, n.y).normalize();
      const down = down0.clone().multiplyScalar(Math.cos(0.6)).addScaledVector(n, Math.sin(0.6)).normalize();   // tipped forward: the lens shows
      const base = at.clone().addScaledVector(n, 6).addScaledVector(down0, -5);
      const body = sweep([base, base.clone().addScaledVector(down, 15)], circle(i => i ? 11 : 9), { radial: 24, capDepth: 0.25 });
      new Part(this.loupe, paintMat(C.loupe, { shine: 0.04, shade: 0.12 }), hl).set(body);
      const lm = new THREE.Matrix4().makeBasis(new V3().crossVectors(down, n).normalize(), n, down).multiply(new THREE.Matrix4().makeScale(10.5, 10.5, 1.5));
      const lensG = new THREE.SphereGeometry(1, 24, 12); lensG.applyMatrix4(lm); lensG.translate(...base.clone().addScaledVector(down, 15.6).toArray());
      new Part(this.loupe, paintMat(C.glass, { shine: 0.1, shade: 0 }), hl).set(lensG);
    }
    // shadow on the floor (the drawing's soft ellipse)
    const sc = document.createElement('canvas'); sc.width = sc.height = 128; const sg2 = sc.getContext('2d'); const grd = sg2.createRadialGradient(64, 64, 10, 64, 64, 64); grd.addColorStop(0, 'rgba(27,23,20,0.26)'); grd.addColorStop(0.7, 'rgba(27,23,20,0.2)'); grd.addColorStop(1, 'rgba(27,23,20,0)'); sg2.fillStyle = grd; sg2.fillRect(0, 0, 128, 128);
    this.shadow = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(sc), transparent: true, depthWrite: false }));
    this.shadow.rotation.x = -Math.PI / 2; this.shadow.scale.set(150 * S * 1.6, 60 * S * 1.6, 1); this.shadow.renderOrder = -1;
    // what the engine measures the body by: our rest mesh
    this.setFace(exprVec(EXPR.neutral) && vecExpr(exprVec(EXPR.neutral)), { look: [0, 0], blink: 0 }, true);
    const restPose = this.standPose(false);
    this.apply(restPose, true);
    const pos = [], tri = [], hd = []; let off = 0;
    this.root.updateMatrixWorld(true);
    this.root.traverse(o => { if (o.isMesh && o.material?.uniforms?.uColor && o.geometry.index) { const g = o.geometry, p = g.attributes.position, v = new V3(), h = o.parent === this.head && o.geometry.attributes.rp && o.material.uniforms.uPaint.value > 2.5; for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i).applyMatrix4(o.matrixWorld); pos.push(v.x, v.y, v.z); hd.push(h ? 255 : 0); } for (const i of g.index.array) tri.push(i + off); off += p.count; } });
    this.restPositions = Float32Array.from(pos); this.restTriangles = Uint32Array.from(tri); this.restHead = Uint8Array.from(hd);   // the skull's skin: the engine's head ball
  }

  // ———— poses ————
  // a still standing pose made from the rest (not a motion): arms let down along the body, a soft bend at the elbows
  standPose(arms = true, o = {}) {
    const sk = this.sk, J = sk.J, pose = { Q: new Float64Array(J * 4), P: Float64Array.from(this.R), floor: 0 };
    for (let j = 0; j < J; j++) pose.Q[j * 4 + 3] = 1;
    if (arms) for (const [sd, sg] of [['Left', 1], ['Right', -1]]) {
      const A = sk.index[sd + 'Arm'], F = sk.index[sd + 'ForeArm'], H = sk.index[sd + 'Hand'];
      const a = normalize(sub(getV(this.R, F), getV(this.R, A)));
      const want = normalize([sg * Math.sin(0.27), -Math.cos(0.27), 0.03]);
      turnUnder(pose, sk, A, qBetween(a, want)); buildPose(pose, this.body || { skeleton: sk, joints: this.R }, getV(pose.P, sk.index.Hips));
      const f = normalize(sub(getV(pose.P, H), getV(pose.P, F)));
      const wantF = normalize([sg * Math.sin(0.02), -Math.cos(0.02), 0.12]);
      turnUnder(pose, sk, F, qBetween(f, wantF)); buildPose(pose, this.body || { skeleton: sk, joints: this.R }, getV(pose.P, sk.index.Hips));
      // the hand turned so the palm faces the leg, fingers down
      const Hq = getQ(pose.Q, H), mid = normalize(qRot(Hq, sub(getV(this.R, sk.index[sd + 'HandMiddle1']), getV(this.R, H))));
      turnUnder(pose, sk, H, qBetween(mid, wantF)); buildPose(pose, this.body || { skeleton: sk, joints: this.R }, getV(pose.P, sk.index.Hips));
    }
    if (o.head) { const Hh = sk.index.Head, fwd = qRot(getQ(pose.Q, Hh), [0, 0, 1]); turnUnder(pose, sk, Hh, qMul(qAxisAngle([0, 1, 0], o.head[0] * Math.PI / 180), qAxisAngle([1, 0, 0], o.head[1] * Math.PI / 180))); buildPose(pose, { skeleton: sk, joints: this.R }, getV(pose.P, sk.index.Hips)); }
    pose.floor = 0;
    return pose;
  }
  // a Kimodo clip's moment through the engine (retarget + corrections), placed
  clipPose(clip, f) { const p = this.retarget.pose(clip.sample(f, this.sample)); this.retarget.placed(p); return p; }

  // ———— putting a pose on the forms ————
  apply(pose, rest = false) {
    const sk = this.sk, P = i => new V3(pose.P[i * 3], pose.P[i * 3 + 1], pose.P[i * 3 + 2]), Qj = i => new THREE.Quaternion(pose.Q[i * 4], pose.Q[i * 4 + 1], pose.Q[i * 4 + 2], pose.Q[i * 4 + 3]);
    const ix = sk.index, J = n => P(ix[n]);
    // skinned pieces (linear blend over the spine joints)
    const Rj = j => new V3(this.R[j * 3], this.R[j * 3 + 1], this.R[j * 3 + 2]);
    const M = new Map();
    const mat = j => { if (!M.has(j)) { const q = Qj(j), r = Rj(j), p = P(j); M.set(j, { q, t: p.sub(r.applyQuaternion(q)) }); } return M.get(j); };
    const v = new V3(), acc = new V3();
    for (const s of this.skinned) {
      const pa = s.part.mesh.geometry.attributes.position, a = pa.array;
      for (let i = 0; i < s.wts.length; i++) {
        acc.set(0, 0, 0);
        for (const [j, w] of s.wts[i]) { const m = mat(j); v.set(s.rest[i * 3], s.rest[i * 3 + 1], s.rest[i * 3 + 2]).applyQuaternion(m.q).add(m.t); acc.addScaledVector(v, w); }
        a[i * 3] = acc.x; a[i * 3 + 1] = acc.y; a[i * 3 + 2] = acc.z;
      }
      pa.needsUpdate = true; s.part.mesh.geometry.computeVertexNormals();
    }
    // hoses: arms (shirt sleeves) and legs (trousers, then the leg below the knickerbockers' cuff)
    for (const sd of ['Left', 'Right']) {
      const ap = hosePath(J(sd + 'Arm'), J(sd + 'ForeArm'), J(sd + 'Hand'), 1.0);
      this.arms[sd].set(sweep(ap, circle(i => lerp(9.5, 8.6, i / 36) * S), { radial: 20 }));
      const lp = hosePath(J(sd + 'Leg'), J(sd + 'Shin'), J(sd + 'Foot'), 1.0);
      const LR = [[0, 21], [0.25, 19.5], [0.58, 18.6], [0.63, 17.6], [0.69, 13.4], [0.8, 12.6], [1, 11.2]];
      this.legs[sd].set(sweep(lp, circle(i => keys(LR, i / 36) * S), { radial: 24, capEnd: false }));
      this.gloves[sd].set(this.glove(pose, sd, P, Qj));
      const sh = this.shoes[sd], j = ix[sd + 'Foot'], q = Qj(j);
      sh.grp.quaternion.copy(q); sh.grp.position.copy(P(j).sub(sh.rest.clone().applyQuaternion(q)));
    }
    // the head: rigid on the Head joint, squashed and stretched about its centre
    const hj = ix.Head, hq = Qj(hj);
    this.head.quaternion.copy(hq);
    this.head.position.copy(P(hj).add(this.headC.clone().sub(this.headPivot).applyQuaternion(hq)));
    const sq = this.sq || [1, 1];
    this.head.scale.set(S * sq[0], S * sq[1], S * sq[0]);
    // the shadow under him
    const hips = J('Hips'); this.shadow.position.set(hips.x, (pose.floor ?? 0) + 0.002, hips.z + 0.02);
    this.pose = pose;
  }
  // a white glove: palm, three fat fingers and a thumb along the posed finger joints, a rolled cuff (П2's hand)
  glove(pose, sd, P, Qj) {
    const ix = this.sk.index, J = n => P(ix[n]);
    const wrist = J(sd + 'Hand'), fore = J(sd + 'ForeArm'), dir = wrist.clone().sub(fore).normalize();
    const gs = [], rf = 5.6 * S;
    const pc = wrist.clone().lerp(J(sd + 'HandMiddle1'), 0.62), a1 = J(sd + 'HandMiddle1').sub(wrist), a2 = J(sd + 'HandIndex1').sub(J(sd + 'HandPinky1'));
    const palm = new THREE.SphereGeometry(1, 22, 14), m = new THREE.Matrix4();
    const ex = a2.clone().normalize(), ey = a1.clone().normalize(), ez = new V3().crossVectors(ex, ey).normalize(); ex.crossVectors(ey, ez);
    m.makeBasis(ex.clone().multiplyScalar(13 * S), ey.clone().multiplyScalar(a1.length() * 0.75 + 2 * S), ez.clone().multiplyScalar(7.5 * S)).setPosition(pc); palm.applyMatrix4(m);
    gs.push(palm);
    for (const f of ['Index', 'Middle', 'Ring', 'Thumb']) {
      const ids = f === 'Thumb' ? [1, 2, 3, 'End'] : [1, 2, 3, 4, 'End'];
      let pts = ids.map(i => J(sd + 'Hand' + f + i));
      if (f !== 'Thumb') pts = [pts[0].clone().lerp(pts[1], 0.3), ...pts.slice(1)];
      // cartoon fingers: shorter than a person's, a little curled, spread from the knuckle
      const fl = f === 'Thumb' ? 0.85 : 0.78, segs = []; for (let r = 1; r < pts.length; r++) segs.push(pts[r].clone().sub(pts[r - 1]).multiplyScalar(fl));
      for (let r = 1; r < pts.length; r++) pts[r] = pts[r - 1].clone().add(segs[r - 1]);
      const curve = bezier(pts, 10);
      gs.push(sweep(curve, circle(i => rf * (f === 'Thumb' ? 1.0 : 1) * (0.94 + 0.1 * (i / 10))), { radial: 12 }));
    }
    const c0 = wrist.clone().addScaledVector(dir, -9 * S), c1 = wrist.clone().addScaledVector(dir, 2.5 * S);
    gs.push(sweep([c0, c0.clone().lerp(c1, 0.5), c1], circle(i => [11.5, 13.8, 12.6][i] * S), { radial: 24 }));
    return merge(gs);
  }

  // the face: paint the canvas, rebuild brows and moustache, place spectacles and loupe, squash the head
  setFace(e, live, force = false) {
    drawFace(this.faceCanvas, e, live); this.faceTex.needsUpdate = true;
    const key = [e.brow, e.browY, e.droop, e.mouth.pts[4][1] - e.mouth.pts[1][1]].map(v => v.toFixed(3)).join(',');
    if (force || key !== this.faceKey) {
      this.faceKey = key;
      const gs = [];
      for (const [sd, x] of [[-1, -20], [1, 20]]) {
        const ang = sd * e.brow * 18 * Math.PI / 180, ca = Math.cos(ang), sa = Math.sin(ang);
        const o = cloud(40, 26, 4).map(([u, v]) => [x + sd * 4 + u * ca - v * sa, -12 + e.browY + u * sa + v * ca]);
        gs.push(pillow(o, onFace(0.5), { thick: 8, sink: 4, rings: 7, centre: [x + sd * 4, -10 + e.browY] }));
      }
      this.brows.set(merge(gs));
      // the walrus moustache (savely.moustache): a soft mass under the nose, ends drooping, three lobes underneath;
      // it rides on the mouth: the opening lifts it a little
      const open = Math.max(0, e.mouth.pts[4][1] - e.mouth.pts[1][1]);
      const cx = 0, cy = 40 - Math.min(5, open * 0.18), hw = 35, dr = (e.droop - open * 0.04) * 6;
      const pts = [[cx, cy - 12], [cx + hw * 0.55, cy - 13], [cx + hw * 0.95, cy - 2], [cx + hw * 1.08, cy + 14 + dr], [cx + hw * 0.82, cy + 18 + dr], [cx + hw * 0.55, cy + 12 + dr * 0.5], [cx + hw * 0.3, cy + 17 + dr * 0.3],
        [cx, cy + 11], [cx - hw * 0.3, cy + 17 + dr * 0.3], [cx - hw * 0.55, cy + 12 + dr * 0.5], [cx - hw * 0.82, cy + 18 + dr], [cx - hw * 1.08, cy + 14 + dr], [cx - hw * 0.95, cy - 2], [cx - hw * 0.55, cy - 13]];
      const st = pillow(outline(pts, 6, 0.9), onFace(1), { thick: 9, sink: 5, rings: 9, centre: [0, cy] });
      this.stache.set(st);
      const ln = [];
      for (const sd of [-1, 1]) {
        const lp = [[cx + sd * hw * 0.2, cy - 4], [cx + sd * hw * 0.55, cy + 3], [cx + sd * hw * 0.8, cy + 10 + dr]].map(([u, v]) => { const [x, y] = DR(u, v); return new V3(x, y, frontZ(x, y) + 1 + 9 * Math.sqrt(Math.max(0, 1 - ((u / (hw * 1.15)) ** 2))) * 0.9); });
        ln.push(sweep(through(lp, 6), circle(() => 0.9), { radial: 6 }));
      }
      this.stacheLines.set(merge(ln));
    }
    // spectacles slide up to the forehead (surprise), the loupe's strap is pushed back with them
    const g = clamp(e.glasses, 0, 1.2);
    this.glasses.rotation.x = -0.98 * g; this.glasses.scale.setScalar(1 + 0.05 * g);
    this.loupe.rotation.x = -0.5 * g;
    this.sq = [e.sq[0] - this.dyn.sy * 0.5, e.sq[1] + this.dyn.sy + Math.max(0, e.mouth.pts[4][1] - e.mouth.pts[1][1]) * 0.0015];
  }
}

// ———————————————————— the stage: camera, the film look ————————————————————
const POST_VS = `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;
const POST_FS = `
uniform sampler2D tCol, tNoise; uniform vec2 uRes; uniform float uWob, uGrain, uVig, uBW, uSeed;
varying vec2 vUv;
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233)) + uSeed * 0.37) * 43758.5453); }
void main() {
  float k = uRes.y / 900.0;                                       // the drawing's sheets are 900 px tall
  vec2 n = texture2D(tNoise, vUv * uRes / (28.0 * k * 64.0) + vec2(uSeed * 0.131, uSeed * 0.071)).rg - 0.5;
  vec2 uv = vUv + n * uWob * k / uRes;
  vec3 c = texture2D(tCol, uv).rgb;
  float g = hash(floor(vUv * uRes / max(1.0, k)));
  c *= 1.0 - uGrain * (g - 0.5);
  vec2 q = vUv - vec2(0.5, 0.52); q.x *= uRes.x / uRes.y;
  float v = smoothstep(0.42, 0.95, length(q) / 0.72);
  c = mix(c, vec3(0.165, 0.114, 0.063), v * uVig);
  if (uBW > 0.5) { float l = dot(c, vec3(0.30, 0.55, 0.15)); l = 1.12 * pow(l, 0.8) - 0.04; c = vec3(l); c = mix(c, vec3(0.0), v * 0.35); }
  gl_FragColor = vec4(c, 1.0);
}`;

export async function createStage(canvas, o = {}) {
  const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
  const old = await E.body('moood-oldman');
  const ch = new Savely(E, old);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(o.pixelRatio || Math.min(2, devicePixelRatio));
  renderer.outputColorSpace = THREE.LinearSRGBColorSpace;   // no conversions: every shader here writes the drawing's own numbers
  const scene = new THREE.Scene(); scene.background = new THREE.Color().setStyle('#efe2c4', THREE.LinearSRGBColorSpace);
  scene.add(ch.root); scene.add(ch.shadow);
  const persp = new THREE.PerspectiveCamera(24, 1, 0.05, 60), ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.05, 60);
  // the film: a target, then the pass that wobbles the ink, adds grain and darkens the corners
  const rt = new THREE.WebGLRenderTarget(4, 4, { samples: 4, type: THREE.UnsignedByteType });
  const nz = new Uint8Array(64 * 64 * 4); for (let i = 0; i < nz.length; i++) nz[i] = Math.random() * 255;
  const noise = new THREE.DataTexture(nz, 64, 64); noise.wrapS = noise.wrapT = THREE.RepeatWrapping; noise.magFilter = noise.minFilter = THREE.LinearFilter; noise.needsUpdate = true;
  const post = new THREE.ShaderMaterial({ vertexShader: POST_VS, fragmentShader: POST_FS, uniforms: { tCol: { value: rt.texture }, tNoise: { value: noise }, uRes: { value: new THREE.Vector2() }, uWob: { value: 2.4 }, uGrain: { value: 0.12 }, uVig: { value: 0.42 }, uBW: { value: 0 }, uSeed: { value: 0 } } });
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), post), qscene = new THREE.Scene(); qscene.add(quad); const qcam = new THREE.Camera();
  const st = {
    THREE, E, ch, renderer, scene, persp, ortho, post,
    cam: { mode: 'persp', yaw: 25, pitch: 6, dist: 4.2, target: new V3(0, 0.75, 0), fov: 24, ortho: { h: 2, cx: 0, cy: 0.8 }, follow: false, pad: 0 },
    film: true, seed: 0,
    size(w, h) { renderer.setSize(w, h, false); const pr = renderer.getPixelRatio(); rt.setSize(w * pr, h * pr); post.uniforms.uRes.value.set(w * pr, h * pr); this.w = w; this.h = h; },
    camera() {
      const c = this.cam, yaw = c.yaw * Math.PI / 180, pit = c.pitch * Math.PI / 180;
      const dir = new V3(Math.sin(yaw) * Math.cos(pit), Math.sin(pit), Math.cos(yaw) * Math.cos(pit));
      if (c.mode === 'ortho') {
        const a = this.w / this.h, hh = c.ortho.h / 2; Object.assign(ortho, { left: -hh * a, right: hh * a, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
        const right = new V3(Math.cos(yaw), 0, -Math.sin(yaw)), t = c.target.clone().addScaledVector(right, -(c.ortho.dx || 0)); ortho.position.copy(t).addScaledVector(dir, 20); ortho.up.set(0, 1, 0); ortho.lookAt(t);
        // shift the view so the target sits at (cx, cy) of the frame (frame units: world)
        ortho.updateMatrixWorld(); return ortho;
      }
      persp.fov = c.fov; persp.aspect = this.w / this.h;
      persp.setViewOffset(this.w, this.h + c.pad, 0, c.pad, this.w, this.h); persp.updateProjectionMatrix();
      persp.position.copy(c.target).addScaledVector(dir, c.dist); persp.lookAt(c.target); return persp;
    },
    render() {
      const cam = this.camera();
      if (this.film) {
        renderer.setRenderTarget(rt); renderer.render(scene, cam); renderer.setRenderTarget(null);
        post.uniforms.uSeed.value = this.seed; renderer.render(qscene, qcam);
      } else { renderer.setRenderTarget(null); renderer.render(scene, cam); }
    },
  };
  return st;
}
