// Марат in 3D, printed every frame as a woodblock print (С13). The form (tools/build.py's pack) moves on the engine's
// skeleton, skinning and Kimodo retargeting; it is never shaded. Each frame is a sheet:
//   1. the colour blocks: the figure rendered flat — each part in its block's one colour, the cloth's pattern printed
//      on it in the cloth's own flat coordinates (waves on the apron, checks on the trousers, stripes on the towel),
//      bokashi wiped along hems — no light, no shade;
//   2. the key block: lines found on the 3D — silhouettes (where the surface turns away) and open edges (hems, the
//      apron's sides), kept where seen, chained, smoothed and drawn with the drawing's brush (print.js = kit.py):
//      the weight changes with the stroke's direction, heavier on cloth than on skin; the beard's edge grows hairs;
//   3. the face — eyes, brows, nose, mouth, the cheeks' blush — drawn with the drawing's parts (parts.py) in its
//      front units, laid on the 3D head through a grid (build.py), so it turns with the head;
//   4. lines and signs of the form: the apron's folds and waist, the jacket's front edge, buttons, the curls' hooks;
//   5. the sheet: toned ground with bokashi along the top, border, the name's slip and the seal; paper, wood grain
//      and age lie over it (still, as the sheet's own).
//   view.html — by hand (ui.js); view.html?pack=<url> — driven by tools/shots.mjs
//   window.A.set({clip, t, time, pose, expr, talk, cam, …}) then A.render()
import * as THREE from 'three';
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { qAxisAngle, qBetween, qRot, getQ, getV, normalize, sub } from '../../../../engine/src/math.js';
import * as K from './print.js';
import { LiveFace } from './face.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack') || '../../data/marat.json', location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const sk = E.skeleton, J = sk.J, I = sk.index;

const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const rest = Float32Array.from(a.positions);
const spec = { skinning: { method: q.get('skin') || 'dqs', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
const NV = rest.length / 3, TRI = a.triangles, NT = TRI.length / 3;
const NONE = 0xFFFFFFFF;
const G = H.groups, PN = H.pieceNames, vpid = a.pid, HU = H.face.k;
const PI = Object.fromEntries(PN.map((n, i) => [n, i]));

// ---------------------------------------------------------------- the blocks' colours (styles/s13-ukiyo-e/tools/marat.py)
const hex = h => { const v = parseInt(h.slice(1), 16); return new THREE.Vector3((v >> 16) / 255, ((v >> 8) & 255) / 255, (v & 255) / 255); };
const COL = { [G.skin]: K.SKIN, [G.black]: K.HAIR, [G.white]: K.WHITE, [G.terra]: K.TERRA, [G.checks]: '#e6dfd0', [G.towel]: K.WHITE, [G.shoe]: '#2a2426' };
const BOK = { [G.skin]: K.SKIN, [G.black]: K.HAIR, [G.white]: '#cfc9bd', [G.terra]: K.TERRA_D, [G.checks]: '#b9b6b0', [G.towel]: K.WHITE, [G.shoe]: '#2a2426' };
// line weights by piece, in the drawing's units (marat.py: jacket 4.0, apron 3.8, towel 2.8, trousers 3.4, shoes 2.6, skin 2.0–2.2)
const LW = { arms: 2.3, head: 2.1, beard: 1.4, hair: 1.6, jacket: 4.0, collar: 3.0, sleeveLeft: 3.6, sleeveRight: 3.6, apron: 3.8, towel: 2.8, legs: 3.4, shoeLeft: 2.6, shoeRight: 2.6 };
const NIB = { arms: 0.3, head: 0.3, beard: 0.2, hair: 0.2 };

// ---------------------------------------------------------------- two renders: the unseen one (block and depth), the colour blocks
const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true, premultipliedAlpha: false });
renderer.setPixelRatio(1); renderer.setClearColor(0x000000, 0);
const g = new THREE.BufferGeometry();
g.setAttribute('position', new THREE.BufferAttribute(fig.positions, 3));
g.setAttribute('normal', new THREE.BufferAttribute(fig.normals, 3));
g.setAttribute('grp', new THREE.BufferAttribute(Float32Array.from(a.grp), 1));
g.setAttribute('pid', new THREE.BufferAttribute(Float32Array.from(a.pid), 1));
g.setAttribute('puv', new THREE.BufferAttribute(a.puv, 2));
g.setAttribute('bok', new THREE.BufferAttribute(Float32Array.from(a.bok, v => v / 255), 1));
g.setIndex(new THREE.BufferAttribute(a.triangles, 1));
const U = { dn: { value: 0 }, df: { value: 10 } };
const idMat = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.DoubleSide,
  vertexShader: `attribute float grp; attribute float pid; varying float vG; varying float vD; varying float vP;
    void main() { vG = grp; vP = pid; vec4 mv = modelViewMatrix * vec4(position, 1.0); vD = -mv.z; gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `uniform float dn; uniform float df; varying float vG; varying float vD; varying float vP;
    void main() { float z = clamp((vD - dn) / (df - dn), 0.0, 1.0) * 65535.0; float hi = floor(z / 256.0), lo = z - hi * 256.0;
      gl_FragColor = vec4(floor(vG + 0.5) / 255.0, hi / 255.0, lo / 255.0, (floor(vP + 0.5) + 1.0) / 255.0); }`,
});
const cols = [], boks = []; for (let i = 0; i < 8; i++) { cols.push(hex(COL[i] || '#000000')); boks.push(hex(BOK[i] || '#000000')); }
const UC = { col: { value: cols }, bokc: { value: boks }, wave: { value: hex('#e08e5c') }, check: { value: hex('#3f4a5a') }, stripe: { value: hex(K.TERRA) }, plain: { value: 0 } };
const colMat = new THREE.ShaderMaterial({
  uniforms: UC, side: THREE.DoubleSide,
  vertexShader: `attribute float grp; attribute vec2 puv; attribute float bok; varying float vG; varying vec2 vU; varying float vB;
    void main() { vG = grp; vU = puv; vB = bok; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `uniform vec3 col[8]; uniform vec3 bokc[8]; uniform vec3 wave; uniform vec3 check; uniform vec3 stripe; uniform float plain;
    varying float vG; varying vec2 vU; varying float vB;
    // seigaiha: rows of overlapping arcs, three to a wave (kit.py seigaiha)
    float waves(vec2 p, float r, float lw) {
      vec2 c0 = floor(p / (2.0 * r)); float d = 1e3;
      for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) for (int s = 0; s < 2; s++) {
        vec2 c = (c0 + vec2(float(i), float(j))) * 2.0 * r + (s == 0 ? vec2(0.0, r) : vec2(r, 0.0));
        vec2 v = p - c; if (v.y < 0.0) continue; float l = length(v);
        d = min(d, min(abs(l - r), min(abs(l - 0.7 * r), abs(l - 0.4 * r))));
      }
      float aa = fwidth(p.x) + fwidth(p.y);
      return 1.0 - smoothstep(lw * 0.5 - aa * 0.5, lw * 0.5 + aa * 0.5, d);
    }
    void main() {
      int gi = int(floor(vG + 0.5)); vec3 c = col[gi];
      if (plain < 0.5) {
        if (gi == ${G.terra}) c = mix(c, wave, waves(vU, 0.030, 0.0030));
        if (gi == ${G.checks}) { vec2 k = vU / 0.0175; vec2 fw = fwidth(k); vec2 t = abs(fract(k * 0.5) - 0.5) * 2.0;       // ichimatsu
          vec2 s = smoothstep(0.5 - fw, 0.5 + fw, t); float on = s.x * s.y + (1.0 - s.x) * (1.0 - s.y); on = mix(on, 0.5, smoothstep(0.3, 0.8, max(fw.x, fw.y))); c = mix(c, check, on); }
        if (gi == ${G.towel}) { float k = vU.x / 0.035 + 0.5; float fw = fwidth(k); float t = abs(fract(k) - 0.5);
          c = mix(c, stripe, 1.0 - smoothstep(0.145 - fw, 0.145 + fw, t)); }
        c = mix(c, bokc[gi], vB * 0.62);
      }
      gl_FragColor = vec4(c, 1.0);
    }`,
});
const scene = new THREE.Scene();
const mesh = new THREE.Mesh(g, idMat); mesh.frustumCulled = false; scene.add(mesh);
const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 100);
const persp = new THREE.PerspectiveCamera(24, 1, 0.05, 200);
let camera = ortho, rt = null, buf = null, W = 0, Hh = 0, pxm = 400;

// ---------------------------------------------------------------- poses
function turnTo(pose, j, child, dir) { turnUnder(pose, sk, j, qBetween(normalize(sub(getV(pose.P, child), getV(pose.P, j))), normalize(dir))); build(pose, body, getV(pose.P, I.Hips)); }
function turn(pose, j, axis, ang) { if (!ang) return; turnUnder(pose, sk, j, qAxisAngle(axis, ang)); build(pose, body, getV(pose.P, I.Hips)); }
function standPose(o = {}) {
  const pose = fig.restPose();
  const out = o.out ?? 0.44, fwd = o.fwd ?? 0.05;
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    turnTo(pose, I[s + 'Arm'], I[s + 'ForeArm'], [sg * out, -1, fwd]);
    turnTo(pose, I[s + 'ForeArm'], I[s + 'Hand'], [sg * (out - 0.34), -1, fwd + 0.30]);
  }
  if (o.figure) {
    // the drawing's figure: leaning back, the belly forward; his left arm up with the ladle, the right thrown open
    turn(pose, I.Spine1, [1, 0, 0], -0.10); turn(pose, I.Chest, [1, 0, 0], -0.06);
    turnTo(pose, I.LeftArm, I.LeftForeArm, [1, 0.0, -0.3]); turnTo(pose, I.LeftForeArm, I.LeftHand, [-0.3, 1, 0.15]);
    turnTo(pose, I.RightArm, I.RightForeArm, [-0.1, -0.25, 1]); turnTo(pose, I.RightForeArm, I.RightHand, [-0.5, 0.2, 1]);
    turn(pose, I.RightForeArm, normalize(sub(getV(pose.P, I.RightHand), getV(pose.P, I.RightForeArm))), -1.3);
  }
  if (o.headTurn) turn(pose, I.Neck2, [0, 1, 0], o.headTurn);
  if (o.headTilt) turn(pose, I.Neck2, [0, 0, 1], o.headTilt);
  if (o.headNod) turn(pose, I.Neck2, [1, 0, 0], o.headNod);
  return pose;
}
// the apron's skirt and the jacket's hem kept off the legs (Р1's): each point inside a leg's capsule is put on its
// surface, the push spread over its neighbours
const hang = [];
for (const k of ['apron', 'jacket']) for (let i = H.pieces[k][0]; i < H.pieces[k][1]; i++) if (rest[i * 3 + 1] < 1.0) hang.push(i);
const hangSet = new Int32Array(NV).fill(-1); hang.forEach((i, k) => { hangSet[i] = k; });
const hangNb = hang.map(() => new Set());
for (let t = 0; t < NT; t++) for (let c = 0; c < 3; c++) { const i = TRI[t * 3 + c], j = TRI[t * 3 + (c + 1) % 3]; if (hangSet[i] >= 0 && hangSet[j] >= 0) { hangNb[hangSet[i]].add(hangSet[j]); hangNb[hangSet[j]].add(hangSet[i]); } }
const hangN = hangNb.map(s => [...s]);
const CAPS = [['LeftLeg', 'LeftShin', 0.118], ['LeftShin', 'LeftFoot', 0.098], ['RightLeg', 'RightShin', 0.118], ['RightShin', 'RightFoot', 0.098]].map(([p, b, r]) => [I[p], I[b], r]);
const fadeK = Float64Array.from(hang, i => { const u = Math.max(0, Math.min(1, (1.0 - rest[i * 3 + 1]) / 0.16)); return u * u * (3 - 2 * u); });
const dsp = new Float64Array(hang.length * 3), dsp2 = new Float64Array(hang.length * 3);
function pushHang(P, pose) {
  const caps = CAPS.map(([p, b, r], k) => { const A = getV(pose.P, p), B = getV(pose.P, b); return [k % 2 ? A : A.map((v, c) => v + (B[c] - v) * 0.15), B, r + 0.012]; });
  hang.forEach((i, k) => {
    let x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
    for (const [A, B, r] of caps) {
      const ab = [B[0] - A[0], B[1] - A[1], B[2] - A[2]], l2 = ab[0] ** 2 + ab[1] ** 2 + ab[2] ** 2;
      let u = ((x - A[0]) * ab[0] + (y - A[1]) * ab[1] + (z - A[2]) * ab[2]) / l2; u = Math.max(0, Math.min(1, u));
      const cx = A[0] + ab[0] * u, cy = A[1] + ab[1] * u, cz = A[2] + ab[2] * u, dx = x - cx, dy = y - cy, dz = z - cz, d = Math.hypot(dx, dy, dz);
      if (d < r && d > 1e-6) { const s = r / d; x = cx + dx * s; y = cy + dy * s; z = cz + dz * s; }
    }
    dsp[k * 3] = x - P[i * 3]; dsp[k * 3 + 1] = y - P[i * 3 + 1]; dsp[k * 3 + 2] = z - P[i * 3 + 2];
  });
  for (let it = 0; it < 8; it++) {
    hangN.forEach((nb, k) => { for (let c = 0; c < 3; c++) { let s = dsp[k * 3 + c]; for (const m of nb) s += dsp[m * 3 + c]; dsp2[k * 3 + c] = s / (nb.length + 1); } });
    for (let k = 0; k < hang.length; k++) for (let c = 0; c < 3; c++) { const x = dsp[k * 3 + c], y = dsp2[k * 3 + c]; dsp[k * 3 + c] = Math.abs(y) > Math.abs(x) ? y : (x + y) / 2 + (x - y) / 4; }
  }
  hang.forEach((i, k) => { const w = fadeK[k]; P[i * 3] += w * dsp[k * 3]; P[i * 3 + 1] += w * dsp[k * 3 + 1]; P[i * 3 + 2] += w * dsp[k * 3 + 2]; });
}
// where the head looks over a clip (yaw, pitch at 100 Hz) — for the eyes to lead its turns (Р1's)
function headTrack(c) {
  const dt = 0.01, n = Math.floor((c.frames - 1) / c.fps / dt) + 1, yaw = new Float32Array(n), pitch = new Float32Array(n);
  const smp = { q: new Float64Array(J * 4), p: new Float64Array(J * 3), lowest: 0 };
  let prev = 0;
  for (let i = 0; i < n; i++) {
    const pose = fig.retarget.pose(c.sample(i * dt * c.fps, smp)), f = qRot(getQ(pose.Q, I.Head), [0, 0, 1]);
    let y = Math.atan2(f[0], f[2]); while (y - prev > Math.PI) y -= 2 * Math.PI; while (y - prev < -Math.PI) y += 2 * Math.PI;
    yaw[i] = prev = y; pitch[i] = Math.asin(Math.max(-1, Math.min(1, f[1])));
  }
  return { dt, yaw, pitch };
}

const S = { clip: null, clipIds: null, t: 0, time: 0, pose: 'stand', poseOpts: {}, push: true, seed: 1, sheet: true, name: true, noColour: false, noLine: false, noFace: false, plain: false, ladle: false,
  ground: ['#8fa3ab', '#4f6c80', '#b9a67c'], cam: { mode: 'ortho', yaw: 0, pitch: 0, cx: 0, cy: 0.98, h: 2.3, dist: 6, target: null, follow: false } };
const face = new LiveFace(Number(q.get('seed') ?? 7));
let clip = null, fp = null;
function frame() {
  fp = face.at(S.time, { headT: S.clip ? S.t / clip.fps : null });
  let pose;
  if (S.clip) { pose = fig.retarget.pose(clip.sample(S.t, fig.sample)); fig.retarget.placed(pose); }
  else if (S.pose === 'raw') pose = null;
  else pose = S.pose === 'rest' ? fig.restPose() : standPose(S.poseOpts || {});
  if (!pose) { fig.positions.set(rest); fig.pose = fig.restPose(); }
  else {
    // the feeling in the body: the laugh throws the head back and shakes head and chest; sadness and anger bow it
    const side = qRot(getQ(pose.Q, I.Hips), [1, 0, 0]);
    turn(pose, I.Chest, side, -0.035 * fp.ha + 0.3 * fp.lean);
    turn(pose, I.Neck2, qRot(getQ(pose.Q, I.Chest), [1, 0, 0]), fp.lean * 1.6 - 0.05 * fp.ha);
    fig.skinner.skin(pose, fig.positions);
    if (S.clip) {
      const P = fig.positions; let lo = Infinity; for (let i = 1; i < P.length; i += 3) if (P[i] < lo) lo = P[i];
      const shift = pose.floor - lo; for (let i = 1; i < P.length; i += 3) P[i] += shift; for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
    }
    if (S.push) pushHang(fig.positions, pose);
    fig.pose = pose;
  }
  g.attributes.position.needsUpdate = true;
}

// ---------------------------------------------------------------- per-frame geometry
const fn = new Float32Array(NT * 3), facing = new Uint8Array(NT), vn = new Float32Array(NV * 3);
const scr = new Float32Array(NV * 3);
let noseLine = false;
let camPos = [0, 0, 0], viewDir = [0, 0, -1], isOrtho = true;
const mvp = new THREE.Matrix4(), vm = new THREE.Matrix4();
function normals() {
  const P = fig.positions; vn.fill(0);
  for (let t = 0; t < NT; t++) {
    const i = TRI[t * 3] * 3, j = TRI[t * 3 + 1] * 3, k = TRI[t * 3 + 2] * 3;
    const ux = P[j] - P[i], uy = P[j + 1] - P[i + 1], uz = P[j + 2] - P[i + 2], wx = P[k] - P[i], wy = P[k + 1] - P[i + 1], wz = P[k + 2] - P[i + 2];
    const nx = uy * wz - uz * wy, ny = uz * wx - ux * wz, nz = ux * wy - uy * wx;
    fn[t * 3] = nx; fn[t * 3 + 1] = ny; fn[t * 3 + 2] = nz;
    for (const m of [i, j, k]) { vn[m] += nx; vn[m + 1] += ny; vn[m + 2] += nz; }
    let d;
    if (isOrtho) d = -(nx * viewDir[0] + ny * viewDir[1] + nz * viewDir[2]);
    else d = nx * (camPos[0] - P[i]) + ny * (camPos[1] - P[i + 1]) + nz * (camPos[2] - P[i + 2]);
    facing[t] = d > 0 ? 1 : 0;
  }
  for (let i = 0; i < NV; i++) { const l = Math.hypot(vn[i * 3], vn[i * 3 + 1], vn[i * 3 + 2]) || 1; vn[i * 3] /= l; vn[i * 3 + 1] /= l; vn[i * 3 + 2] /= l; }
}
const e = mvp.elements, ve = vm.elements;
function project(x, y, z, out, o = 0) {
  const w = e[3] * x + e[7] * y + e[11] * z + e[15];
  out[o] = ((e[0] * x + e[4] * y + e[8] * z + e[12]) / w * 0.5 + 0.5) * W;
  out[o + 1] = (1 - ((e[1] * x + e[5] * y + e[9] * z + e[13]) / w * 0.5 + 0.5)) * Hh;
  out[o + 2] = -(ve[2] * x + ve[6] * y + ve[10] * z + ve[14]);
}
function projectAll() { const P = fig.positions; for (let i = 0; i < NV; i++) project(P[i * 3], P[i * 3 + 1], P[i * 3 + 2], scr, i * 3); }
const depthAt = (x, y) => { x = Math.round(x); y = Math.round(y); if (x < 0 || y < 0 || x >= W || y >= Hh) return Infinity;
  const k = ((Hh - 1 - y) * W + x) * 4; if (buf[k] === 0) return Infinity; return U.dn.value + (buf[k + 1] * 256 + buf[k + 2]) / 65535 * (U.df.value - U.dn.value); };
const grpAt = (x, y) => { x = Math.round(x); y = Math.round(y); if (x < 0 || y < 0 || x >= W || y >= Hh) return 0; return buf[((Hh - 1 - y) * W + x) * 4] & 7; };
function seen(x, y, z, eps = 0.006, r = 1) {
  for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (depthAt(x + dx, y + dy) >= z - eps) return true;
  return false;
}

// ---------------------------------------------------------------- lines on the form
// where two parts run into each other (the collar on the jacket, a sleeve into it, a trouser leg into the shoe, the
// neck into the collar) there is no silhouette: that line is taken from the unseen picture — the border between the
// two parts' pixels where the depth does not jump
const JOIN = new Uint8Array(32 * 32);
for (const [p, q2] of [['collar', 'jacket'], ['sleeveLeft', 'jacket'], ['sleeveRight', 'jacket'], ['legs', 'shoeLeft'], ['legs', 'shoeRight'], ['head', 'collar'], ['towel', 'jacket'], ['towel', 'collar']]) { JOIN[PI[p] * 32 + PI[q2]] = 1; JOIN[PI[q2] * 32 + PI[p]] = 1; }
function joins() {
  const nxt = new Map(), w1 = W + 1, segs = [];
  const pidAt = k => buf[k * 4 + 3] - 1, zAt = k => buf[k * 4 + 1] * 256 + buf[k * 4 + 2], zt = 0.02 / (U.df.value - U.dn.value) * 65535;
  for (let y = 0; y < Hh - 1; y++) { const row = (Hh - 1 - y) * W, rowD = (Hh - 2 - y) * W;
    for (let x = 0; x < W - 1; x++) {
      const k = row + x, pa = pidAt(k); if (pa < 0) continue;
      const pb = pidAt(k + 1), pc = pidAt(rowD + x);
      if (pb >= 0 && pb !== pa && JOIN[pa * 32 + pb] && Math.abs(zAt(k) - zAt(k + 1)) < zt) segs.push([(y) * w1 + x + 1, (y + 1) * w1 + x + 1, Math.min(pa, pb) * 32 + Math.max(pa, pb)]);
      if (pc >= 0 && pc !== pa && JOIN[pa * 32 + pc] && Math.abs(zAt(k) - zAt(rowD + x)) < zt) segs.push([(y + 1) * w1 + x, (y + 1) * w1 + x + 1, Math.min(pa, pc) * 32 + Math.max(pa, pc)]);
    } }
  const adj = new Map(); segs.forEach((s, i) => { for (const c of [s[0], s[1]]) { let l = adj.get(c); if (!l) adj.set(c, l = []); l.push(i); } });
  const used = new Uint8Array(segs.length), out = [];
  const walk = (i0, c0) => { const pts = [c0]; let i = i0, c = c0;
    while (true) { used[i] = 1; const n = segs[i][0] === c ? segs[i][1] : segs[i][0]; pts.push(n); const l = adj.get(n); let ni = -1; for (const j of l) if (!used[j] && segs[j][2] === segs[i][2]) { ni = j; break; } if (ni < 0) break; i = ni; c = n; }
    return { pair: segs[i0][2], P: pts.map(c2 => [c2 % w1, Math.floor(c2 / w1)]) }; };
  for (const [c, l] of adj) if (l.length === 1 && !used[l[0]]) out.push(walk(l[0], c));
  segs.forEach((s, i) => { if (!used[i]) out.push(walk(i, s[0])); });
  return out;
}
const INNER = a.inner, EV = a.edges, ET = a.edgeTris, EDROP = a.edgeDrop, NE = EV.length / 2;
function contours() {
  const keep = new Uint8Array(NE), adj = new Map();
  const addAdj = (v, k) => { let l = adj.get(v); if (!l) adj.set(v, l = []); l.push(k); };
  for (let k = 0; k < NE; k++) {
    if (EDROP[k]) continue;
    const f0 = ET[k * 2], f1 = ET[k * 2 + 1], open = f1 === NONE;
    if (!open && facing[f0] === facing[f1]) continue;
    const i = EV[k * 2], j = EV[k * 2 + 1];
    const mx = (scr[i * 3] + scr[j * 3]) / 2, my = (scr[i * 3 + 1] + scr[j * 3 + 1]) / 2, mz = (scr[i * 3 + 2] + scr[j * 3 + 2]) / 2;
    if (!seen(mx, my, mz, open ? 0.004 : 0.006)) continue;
    if (!open && INNER[i] === 2 && INNER[j] === 2 && !noseLine) continue;      // the nose's own contour: only near profile
    if (!open && !(INNER[i] && INNER[j])) {        // on the face: only where skin meets something else
      const tx = scr[j * 3] - scr[i * 3], ty = scr[j * 3 + 1] - scr[i * 3 + 1], l = Math.hypot(tx, ty) || 1, nx = -ty / l * 3, ny = tx / l * 3;
      if (grpAt(mx + nx, my + ny) === G.skin && grpAt(mx - nx, my - ny) === G.skin) continue;
    }
    keep[k] = 1; addAdj(i, k); addAdj(j, k);
  }
  const used = new Uint8Array(NE), chains = [];
  const walk = (k0, v0) => {
    const vs = [v0]; let k = k0, v = v0;
    while (true) {
      used[k] = 1; const w = EV[k * 2] === v ? EV[k * 2 + 1] : EV[k * 2]; vs.push(w);
      const l = adj.get(w); if (!l || l.length !== 2) break;
      const nk = l[0] === k ? l[1] : l[0]; if (used[nk]) break; k = nk; v = w;
    }
    return vs;
  };
  for (const [v, l] of adj) if (l.length !== 2) for (const k of l) if (!used[k]) chains.push(walk(k, v));
  for (let k = 0; k < NE; k++) if (keep[k] && !used[k]) chains.push(walk(k, EV[k * 2]));
  return chains;
}
function resample(P, step) {
  const out = [P[0]]; let acc = 0;
  for (let i = 1; i < P.length; i++) {
    let [x0, y0] = P[i - 1]; const [x1, y1] = P[i]; let d = Math.hypot(x1 - x0, y1 - y0);
    while (acc + d >= step) { const t = (step - acc) / d; x0 += (x1 - x0) * t; y0 += (y1 - y0) * t; out.push([x0, y0]); d = Math.hypot(x1 - x0, y1 - y0); acc = 0; }
    acc += d;
  }
  if (Math.hypot(out[out.length - 1][0] - P[P.length - 1][0], out[out.length - 1][1] - P[P.length - 1][1]) > step * 0.3) out.push(P[P.length - 1]);
  return out;
}
// a chain of vertices → smoothed picture points; broken where it turns sharply (the brush lifts at a corner)
function chainPts(vs, sm = 5, corner = 1.0) {
  let P = vs.map(v => [scr[v * 3], scr[v * 3 + 1]]);
  P = P.filter((p, i) => i === 0 || Math.hypot(p[0] - P[i - 1][0], p[1] - P[i - 1][1]) > 0.3);
  if (P.length < 2) return [];
  P = resample(P, 2.5);
  for (let it = 0; it < sm; it++) P = P.map((p, i) => i === 0 || i === P.length - 1 ? p : [(P[i - 1][0] + 2 * p[0] + P[i + 1][0]) / 4, (P[i - 1][1] + 2 * p[1] + P[i + 1][1]) / 4]);
  const out = []; let cur = [P[0]];
  for (let i = 2; i < P.length - 2; i++) {
    cur.push(P[i - 1]);
    const a0 = Math.atan2(P[i][1] - P[i - 2][1], P[i][0] - P[i - 2][0]), a1 = Math.atan2(P[i + 2][1] - P[i][1], P[i + 2][0] - P[i][0]);
    let da = Math.abs(a1 - a0); if (da > Math.PI) da = 2 * Math.PI - da;
    if (da > corner && cur.length > 2) { cur.push(P[i]); out.push(cur); cur = [P[i]]; i += 2; cur.push(P[i - 1]); }
  }
  for (let i = Math.max(1, P.length - 3); i < P.length; i++) if (cur[cur.length - 1] !== P[i]) cur.push(P[i]);
  out.push(cur);
  return out;
}
const plen = P => { let s = 0; for (let i = 1; i < P.length; i++) s += Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]); return s; };

// ---------------------------------------------------------------- the face, drawn on the head
const FG = H.face, FTRI = a.faceTri, FBAR = a.faceBar, NF = FTRI.length;
const fsc = new Float32Array(NF * 3), fok = new Uint8Array(NF);
function faceGrid() {
  const P = fig.positions;
  for (let k = 0; k < NF; k++) {
    fok[k] = 0; const t = FTRI[k]; if (t === NONE) continue;
    let x = 0, y = 0, z = 0, nx = 0, ny = 0, nz = 0;
    for (let c = 0; c < 3; c++) { const v = TRI[t * 3 + c], b = FBAR[k * 3 + c]; x += b * P[v * 3]; y += b * P[v * 3 + 1]; z += b * P[v * 3 + 2]; nx += b * vn[v * 3]; ny += b * vn[v * 3 + 1]; nz += b * vn[v * 3 + 2]; }
    project(x, y, z, fsc, k * 3);
    const toCam = isOrtho ? [-viewDir[0], -viewDir[1], -viewDir[2]] : normalize([camPos[0] - x, camPos[1] - y, camPos[2] - z]);
    const fc = (nx * toCam[0] + ny * toCam[1] + nz * toCam[2]) / (Math.hypot(nx, ny, nz) || 1);
    if (fc < 0.04) continue;
    if (!seen(fsc[k * 3], fsc[k * 3 + 1], fsc[k * 3 + 2], 0.006, 1)) continue;
    fok[k] = 1;
  }
}
function faceMap(x, y) {
  const gx = (x - FG.gx[0]) / FG.gx[1], gy = (y - FG.gy[0]) / FG.gy[1];
  const i = Math.floor(gx), j = Math.floor(gy), nx = FG.gx[2];
  if (i < 0 || j < 0 || i >= nx - 1 || j >= FG.gy[2] - 1) return null;
  const u = gx - i, v = gy - j, k00 = j * nx + i, k10 = k00 + 1, k01 = k00 + nx, k11 = k01 + 1;
  if ([k00, k10, k01, k11].some(k => FTRI[k] === NONE)) return null;
  return [0, 1].map(c => (1 - v) * ((1 - u) * fsc[k00 * 3 + c] + u * fsc[k10 * 3 + c]) + v * ((1 - u) * fsc[k01 * 3 + c] + u * fsc[k11 * 3 + c]));
}
function seenNear(x, y, r = 1) {
  const i = Math.round((x - FG.gx[0]) / FG.gx[1]), j = Math.round((y - FG.gy[0]) / FG.gy[1]), nx = FG.gx[2];
  for (let dj = -r; dj <= r; dj++) for (let di = -r; di <= r; di++) { const k = (j + dj) * nx + i + di; if (k >= 0 && k < NF && fok[k]) return true; }
  return false;
}
// a feature's own frame at (cx, cy): where it is on the turned head and its axes — the vertical as the head carries
// it, the horizontal foreshortened as the head turns but never below `min` of the vertical (the far eye of the
// drawing's three-quarter head is 0.6 of the near one, not a sliver); null when that point of the face is not seen
function frameAt(cx, cy, min = 0.6, raw = false, span = 3) {
  const c = faceMap(cx, cy); if (!c || (!raw && !seenNear(cx, cy))) return null;
  const xl = faceMap(cx - span, cy), xr = faceMap(cx + span, cy), yu = faceMap(cx, cy - span), yd = faceMap(cx, cy + span);
  if (!xl || !xr || !yu || !yd) return null;
  const ay = [(yd[0] - yu[0]) / (2 * span), (yd[1] - yu[1]) / (2 * span)], ly = Math.hypot(...ay);
  let ax = [(xr[0] - xl[0]) / (2 * span), (xr[1] - xl[1]) / (2 * span)]; const lx = Math.hypot(...ax);
  const r = lx / ly, k = Math.max(r, min) / (r || 1);
  if (lx < 1e-6) ax = [-ay[1] * min, ay[0] * min]; else ax = [ax[0] * k, ax[1] * k];
  return { c, ax, ay, r, s: ly };
}
function inFrame(d, f, cx, cy, fnc) {
  d.open([f.ax[0], f.ax[1], f.ay[0], f.ay[1], f.c[0] - f.ax[0] * cx - f.ay[0] * cy, f.c[1] - f.ax[1] * cx - f.ay[1] * cy]);
  const lw = d.lw; d.lw = (1 / f.s) ** 0.55; fnc(); d.lw = lw; d.close();
}
// which way the face is turned in the picture (side: +1 — to the picture's right) and how far (front 1 … profile 0 … away −1)
function headTurn() {
  const fw = qRot(getQ(fig.pose.Q, I.Head), [0, 0, 1]), P = fig.pose.P, hp = [P[I.Head * 3], P[I.Head * 3 + 1], P[I.Head * 3 + 2]];
  const tc = isOrtho ? [-viewDir[0], -viewDir[1], -viewDir[2]] : normalize(sub(camPos, hp));
  const rt = normalize([tc[2], 0, -tc[0]]);       // the picture's right, in the world
  return { side: fw[0] * rt[0] + fw[2] * rt[2] > 0 ? 1 : -1, front: fw[0] * tc[0] + fw[1] * tc[1] + fw[2] * tc[2] };
}
function drawFace(d) {
  const ex = fp, { side, front } = headTurn();
  const [bc, bo] = K.P.blush, bop = bo + ex.blush * 0.5;
  for (const sx of [-46, 46]) { const f0 = frameAt(sx, 36, 0.5, true); if (f0 && seenNear(sx, 30, 3)) inFrame(d, f0, sx, 36, () => d.blush(sx, 36, 28, bc, bop)); }
  for (const [sx, inner] of [[33, -1], [-33, 1]]) {
    const f0 = frameAt(sx, 0, 0.6); if (!f0 || (f0.r < 0.3 && Math.sign(sx) === side)) continue;
    const shift = side * 8 * (1 - Math.min(1, f0.r)) * (Math.sign(sx) === side ? 1 : 0.4), f = frameAt(sx - shift, 0, 0.6) || f0;
    const turnLook = side * (1 - Math.min(1, f.r)) * 3;
    inFrame(d, f, sx, 0, () => { K.eye(d, sx, 0, 1, inner, { ...ex, look: [ex.look[0] + turnLook, ex.look[1]] }); K.brow(d, sx + Math.sign(sx), 1, inner, ex); });
  }
  // the nose: the front drawing's while the face looks at us; the three-quarter drawing's one hooked stroke as it
  // turns (drawn upright in the head's own scale, not foreshortened: it is a profile laid on the face); near profile
  // the 3D's contour is the nose
  const fnz = frameAt(0, 30, 0.75, true, 4), kf = Math.max(0, Math.min(1, (front - 0.86) / 0.07)), kq = Math.min(1 - kf, Math.max(0, Math.min(1, (front - 0.22) / 0.12)));
  if (fnz && kf > 0) inFrame(d, fnz, 0, 30, () => K.noseFront(d, side < 0 ? 1 : -1, kf));
  const fq = frameAt(0, 2, 1, true, 4);
  if (fq && kq > 0) inFrame(d, { ...fq, ax: [-fq.ay[1] * side, fq.ay[0] * side] }, 9 * Math.min(1, (1 - front) / 0.4), 0, () => K.noseQ(d, kq));
  const my = K.P.mouth.y * K.P.long, fm0 = frameAt(0, my, 0.62, true, 4);
  if (fm0) {
    const mx = -side * 10 * (1 - Math.min(1, fm0.r)), fm = frameAt(mx, my, 0.62, false, 4);
    if (fm) inFrame(d, fm, mx, my, () => K.mouth(d, mx, my, ex, { onDark: true }));
  }
}
// a ladle in his raised hand, as the drawing's figure holds it (marat.py ladle): drawn there, not modelled
function ladle(d, s) {
  const PJ = fig.pose.P, hp = new Float32Array(3), up = new Float32Array(3), k = I.LeftHandMiddle1, w = I.LeftHand;
  project(PJ[k * 3], PJ[k * 3 + 1], PJ[k * 3 + 2], hp); project(PJ[w * 3], PJ[w * 3 + 1], PJ[w * 3 + 2], up);
  const x1 = hp[0] + 6 * s, y1 = hp[1] + 26 * s, x2 = x1 - 34 * s, y2 = y1 - 150 * s, r = 30 * s, ov = (cx, cy, rx, ry) => Array.from({ length: 12 }, (_, i) => [cx + rx * Math.cos(i * Math.PI / 6), cy + ry * Math.sin(i * Math.PI / 6)]);
  d.line([[x1, y1], [x2, y2]], 7.0 * s, 'even', { color: '#8a6a3a', nib: 0 });
  d.fill(ov(x2, y2 - r * 0.7, r, r * 0.8), '#b9b4a8'); d.contour(ov(x2, y2 - r * 0.7, r, r * 0.8), 2.6, { nib: 0.5 });
  d.fill(ov(x2, y2 - r * 0.8, r * 0.74, r * 0.5), '#8f8a80');
  d.line([[x2 - r * 0.7, y2 - r * 0.8], [x2, y2 - r * 1.25], [x2 + r * 0.7, y2 - r * 0.8]], 1.6, 'swell');
}

// ---------------------------------------------------------------- the picture
const stage = document.getElementById('stage'), tex = document.getElementById('tex'), bg = document.getElementById('bg');
function setCamera(w, h) {
  const c = S.cam, cp = Math.cos(c.pitch);
  let tg = c.target || [c.cx, c.cy, 0];
  if (c.follow && fig.pose) { const P = fig.pose.P; tg = [P[I.Hips * 3], c.cy, P[I.Hips * 3 + 2]]; }
  if (c.focus && fig.pose) { const P = fig.pose.P, k = I[c.focus]; tg = [P[k * 3] + (c.dx || 0), P[k * 3 + 1] + (c.up || 0), P[k * 3 + 2]]; }
  const dir = [Math.sin(c.yaw) * cp, Math.sin(c.pitch), Math.cos(c.yaw) * cp];
  let dist;
  if (c.mode === 'ortho') {
    camera = ortho; const hh = c.h / 2, ww = hh * w / h; dist = 20;
    Object.assign(ortho, { left: -ww, right: ww, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
    ortho.position.set(tg[0] + dir[0] * dist, tg[1] + dir[1] * dist, tg[2] + dir[2] * dist);
    pxm = h / c.h;
  } else {
    camera = persp; persp.aspect = w / h; persp.fov = c.fov || 24; persp.updateProjectionMatrix(); dist = c.dist;
    persp.position.set(tg[0] + dir[0] * dist, tg[1] + dir[1] * dist, tg[2] + dir[2] * dist);
    pxm = h / (2 * dist * Math.tan(persp.fov * Math.PI / 360));
  }
  camera.lookAt(tg[0], tg[1], tg[2]); camera.updateMatrixWorld();
  isOrtho = c.mode === 'ortho'; camPos = [camera.position.x, camera.position.y, camera.position.z];
  viewDir = normalize([-dir[0], -dir[1], -dir[2]]);
  vm.copy(camera.matrixWorldInverse); mvp.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  U.dn.value = dist - 3; U.df.value = dist + 3;
}
let lastSvg = '', texKey = '', groundKey = '';
function draw() {
  const w = Math.round(stage.clientWidth || innerWidth), h = Math.round(stage.clientHeight || innerHeight);
  if (w !== W || h !== Hh) { W = w; Hh = h; rt?.dispose(); rt = new THREE.WebGLRenderTarget(W, Hh, { depthBuffer: true }); buf = new Uint8Array(W * Hh * 4); renderer.setSize(W, Hh, false); }
  const T0 = performance.now(), prof = {};
  setCamera(W, Hh);
  normals();
  mesh.material = idMat;
  renderer.setRenderTarget(rt); renderer.setClearColor(0x000000, 1); renderer.clear(); renderer.render(scene, camera); renderer.readRenderTargetPixels(rt, 0, 0, W, Hh, buf); renderer.setRenderTarget(null);
  mesh.material = colMat; UC.plain.value = S.plain ? 1 : 0;
  renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera);
  prof.gl = performance.now() - T0;
  projectAll(); faceGrid();
  noseLine = headTurn().front < 0.34;
  const d = new K.Doc(W, Hh, S.seed), m = S.sheet ? Math.round(Math.min(26, Math.min(W, Hh) * 0.035)) : 0;
  if (S.sheet) d.ground(S.ground[0], S.ground[1], S.ground[2], m); else { d.margin = 0; d.groundSvg = `<rect width="${W}" height="${Hh}" fill="${S.ground[0]}"/>`; }
  const sh = pxm * HU, kw = (sh * 1.35) ** 0.45;        // lines keep some of their weight when the figure is small (kit.py lw)
  // the colour blocks (the canvas under the lines) lie a hair off the key block: a print's blocks never register exactly
  canvas.style.visibility = S.noColour ? 'hidden' : 'visible'; canvas.style.clipPath = `inset(${m}px)`;
  prof.col = performance.now() - T0;
  if (!S.noLine) {
    const chains = contours();
    for (const vs of chains) {
      const name = PN[vpid[vs[0]]], w0 = LW[name] ?? 3;
      const soft = name === 'hair' || name === 'beard';
      for (const P of chainPts(vs, soft ? 3 : 5, soft ? 1.4 : 1.0)) {
        const L = plen(P); if (L < 5) continue;
        let mn = vs[0]; for (const v of vs) if (v < mn) mn = v;
        d.line(P, w0 * kw, 'even', { raw: true, nib: NIB[name] ?? 0.55, seed: mn, ends: Math.min(L * 0.45, 9 * kw), hand: 0.6 });
        if (name === 'beard') {       // hairs grow out of the beard's edge, where skin, cloth or the ground lies beyond it
          const sideOf = i => { const tx = P[i][0] - P[i - 1][0], ty = P[i][1] - P[i - 1][1], l = Math.hypot(tx, ty) || 1, nx = -ty / l * 3.5, ny = tx / l * 3.5;
            const ga = grpAt(P[i][0] + nx, P[i][1] + ny), gb = grpAt(P[i][0] - nx, P[i][1] - ny);
            return ga !== G.black && gb === G.black ? 1 : gb !== G.black && ga === G.black ? -1 : 0; };
          d.fringe(P, 8.5 * sh, 1.3 * kw * 0.8, { side: sideOf, lean: 0.5, step: 3.4 * sh, seed: mn, color: K.HAIR });
        }
      }
    }
    for (const jn of joins()) {
      const pa = PN[Math.floor(jn.pair / 32)], pb = PN[jn.pair % 32], w0 = Math.min(LW[pa] ?? 3, LW[pb] ?? 3) * 0.85;
      let P = jn.P; if (P.length < 6) continue;
      P = resample(P, 3); for (let it = 0; it < 10; it++) P = P.map((p, i) => i === 0 || i === P.length - 1 ? p : [(P[i - 1][0] + 2 * p[0] + P[i + 1][0]) / 4, (P[i - 1][1] + 2 * p[1] + P[i + 1][1]) / 4]);
      const L = plen(P); if (L < 12) continue;
      d.line(P, w0 * kw, 'even', { raw: true, nib: 0.5, seed: jn.pair, ends: Math.min(L * 0.45, 9 * kw), hand: 0.5 });
    }
    const colOf = { ink: K.INK, terraD: K.TERRA_D };
    for (const st of H.strokes) {
      const runs = []; let cur = [];
      for (const v of st.v) {
        const x = scr[v * 3], y = scr[v * 3 + 1], z = scr[v * 3 + 2];
        const fc = -(vn[v * 3] * viewDir[0] + vn[v * 3 + 1] * viewDir[1] + vn[v * 3 + 2] * viewDir[2]);
        if (fc > 0.12 && seen(x, y, z, 0.006, 1)) cur.push([x, y]); else { if (cur.length > 1) runs.push(cur); cur = []; }
      }
      if (cur.length > 1) runs.push(cur);
      for (const r of runs) if (plen(r) > 14) d.line(resample(r, 6), st.w * kw, st.prof, { nib: 0.3, seed: st.v[0], color: colOf[st.color] });
    }
    for (const mk of H.marks) {
      const v = mk.v, x = scr[v * 3], y = scr[v * 3 + 1], z = scr[v * 3 + 2];
      const fc = -(vn[v * 3] * viewDir[0] + vn[v * 3 + 1] * viewDir[1] + vn[v * 3 + 2] * viewDir[2]);
      if (!seen(x, y, z, 0.006, 1)) continue;
      if (mk.kind === 'button' && fc > 0.3) { const r = 9.5 * sh; d.raw(`<ellipse cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" rx="${(r * Math.max(0.5, fc)).toFixed(1)}" ry="${r.toFixed(1)}" fill="${K.WHITE}" stroke="${K.INK}" stroke-width="${(1.5 * kw).toFixed(2)}"/>`); }
      if (mk.kind === 'curl' && fc > 0.38) { const s = sh * 1.0; d.line([[x - 6 * s, y + 3 * s], [x - 2 * s, y - 5 * s], [x + 5 * s, y - 3 * s], [x + 4 * s, y + 3 * s]], 1.1 * kw, 'swell', { color: K.SHEEN, nib: 0, op: 0.7, seed: v }); }
    }
  }
  prof.lines = performance.now() - T0;
  if (!S.noFace) drawFace(d);
  if (S.ladle) ladle(d, pxm * HU * 2 * 1.0);
  if (S.sheet && S.name) { const sz = Math.max(13, Math.min(26, W * 0.032)); d.cartouche('Марат', W - m - sz * 1.5 - Math.max(10, W * 0.03), m + Math.max(10, W * 0.03), sz); }
  const lay = d.layers(), gkey = W + 'x' + Hh + S.ground.join() + S.sheet;
  if (gkey !== groundKey) { groundKey = gkey; bg.innerHTML = lay.ground; }
  lastSvg = lay.over; stage.innerHTML = lastSvg;
  const key = W + 'x' + Hh + (S.noTexture ? 'n' : '');
  if (key !== texKey) { texKey = key; tex.innerHTML = S.noTexture ? '' : K.texture(W, Hh, 13); }
  prof.dom = performance.now() - T0; A.prof = prof;
}

function facingYaw() { const qh = getQ(fig.pose.Q, I.Hips); const x = 2 * (qh[0] * qh[2] + qh[1] * qh[3]), z = 1 - 2 * (qh[0] * qh[0] + qh[1] * qh[1]); return Math.atan2(x, z); }
const A = window.A = {
  H, body, fig, sk, face, S, facing: facingYaw, clipInfo: () => clip && { frames: clip.frames, fps: clip.fps }, svg: () => lastSvg,
  async set(o) {
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; face.setHead(clip ? headTrack(clip) : null); }
      S.clip = !!ids;
    }
    for (const k of ['t', 'pose', 'poseOpts', 'push', 'seed', 'sheet', 'name', 'noColour', 'noLine', 'noFace', 'noTexture', 'plain', 'ladle', 'ground']) if (o[k] !== undefined) S[k] = o[k];
    if (o.time !== undefined) S.time = o.time; else if (o.t !== undefined && clip && !S.liveClock) S.time = o.t / clip.fps;
    if (o.liveClock !== undefined) S.liveClock = o.liveClock;
    if (o.still !== undefined) face.still = o.still;
    if (o.exprTrack) { face.exprKeys = [{ t: -10, w: { grin: 1 } }]; for (const [t, w] of o.exprTrack) face.setExpr(t, typeof w === 'string' ? { [w]: 1 } : w); }
    if (o.expr) face.setExpr(S.time, typeof o.expr === 'string' ? { [o.expr]: 1 } : o.expr);
    if (o.talk !== undefined) { face.talk(o.talk ? (o.talkFrom ?? S.time) : null); face.talkTo = o.talkTo ?? null; }
    if (o.cam) Object.assign(S.cam, o.cam);
    frame();
  },
  render() { draw(); },
};
window.DBG = q.has('dbg');
await A.set({});
A.render();
window.__ready = true;

if (!q.has('pack')) (await import('./ui.js')).ui(A, stage);
