// Вера in 3D, drawn every frame as black-and-white manga (С18). The form (tools/build.py's pack) moves on the engine's
// skeleton, skinning and Kimodo retargeting; it is never shown shaded. Each frame (the way is Р12's, the pen is С18's):
//   1. the figure is rendered once, unseen: which tone each pixel has (skin, hair, coat, blouse, lapel, skirt, legs,
//      shoes), whether its surface is turned from the light, and how far it is;
//   2. the tone: every pixel becomes black or white — paper for skin, solid black for hair, screentone dots on a 45°
//      grid fixed to the page for cloth and for shadow (form shadow where the surface turns from the upper-left light;
//      cast shadow where something nearer stands up-left of the pixel; a black band on the lower-right of every form —
//      the drawing's «black copy moved under the white one»);
//   3. lines from the form: silhouettes and open edges kept where seen, chained, smoothed and drawn by pen.js's
//      `stroke` (pressure, taper), heavier where the contour faces away from the light — pen.py's `outline` rule;
//   4. the face — eyes, brows, nose, mouth, wrinkles, glasses — by head.js (head.py ported), on the 3D head's frame;
//   5. lines that belong to the form: the coat's front edges and lapels, white streaks of light in the hair, the
//      hairline's teeth, the loose strand at the temple.
//   view.html — by hand (ui.js); view.html?pack=<url> — driven by tools/shots.mjs
//   window.A.set({clip, t, time, pose, expr, talk, cam, …}) then A.render()
import * as THREE from 'three';
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { qAxisAngle, qBetween, qRot, getQ, getV, normalize, sub } from '../../../../engine/src/math.js';
import * as K from './pen.js';
import { Head } from './head.js';
import { LiveFace } from './face.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack') || '../../data/vera.json', location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const sk = E.skeleton, J = sk.J, I = sk.index;

const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const rest = Float32Array.from(a.positions);
const spec = { skinning: { method: H.skinning || 'dqs', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
const NV = rest.length / 3, TRI = a.triangles, NT = TRI.length / 3, NONE = 0xFFFFFFFF;
const G = H.groups, KH = H.KH, PN = H.pieceNames, vpid = a.pid;
const LAPEL = 8, SKIRT = 9;
// tone levels: [in the light, in shadow] (styles/s18-manga/tools/chars/vera.py: coat 0.6 / 0.9, legs 0.1 / 0.3, shoes 0.7 / 0.9,
// the skirt in the coat's opening 0.5, lapels 0.75, the folder 0.1 / 0.35; skin: paper, its shadow 0.16; hair: black)
const LV = { [G.skin]: [0, 0.16, 0.3], [G.hair]: [1, 1, 1], [G.coat]: [0.6, 0.9, 0.9], [G.leg]: [0.1, 0.3, 0.3], [G.shoe]: [0.7, 0.9, 0.9],
  [G.blouse]: [0, 0.16, 0.3], [G.folder]: [0.1, 0.35, 0.35], [LAPEL]: [0.75, 0.9, 0.9], [SKIRT]: [0.5, 0.75, 0.75] };
const CLOTH = new Set([G.coat, G.shoe, G.folder, LAPEL, SKIRT]);

// ---------------------------------------------------------------- the unseen picture: tone group, shade, depth
const stage = document.getElementById('stage');
const out = document.getElementById('out'), ctx = out.getContext('2d');
const glc = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas: glc, antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
const g = new THREE.BufferGeometry();
g.setAttribute('position', new THREE.BufferAttribute(fig.positions, 3));
g.setAttribute('normal', new THREE.BufferAttribute(fig.normals, 3));
g.setAttribute('grp', new THREE.BufferAttribute(Float32Array.from(a.grp), 1));
g.setAttribute('rp', new THREE.BufferAttribute(rest, 3));
g.setIndex(new THREE.BufferAttribute(a.triangles, 1));
const C = H.coat;
const U = { dn: { value: 0 }, df: { value: 10 }, L: { value: new THREE.Vector3(0, 0, 1) }, show: { value: 0 }, folder: { value: 0 } };
const f4 = x => x.toFixed(4);
const idMat = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.DoubleSide,
  vertexShader: `attribute float grp; attribute vec3 rp; varying float vG; varying float vD; varying vec3 vN; varying vec3 vR;
    void main() { vG = grp; vR = rp; vN = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position, 1.0); vD = -mv.z; gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `uniform float dn; uniform float df; uniform vec3 L; uniform float show; uniform float folder;
    varying float vG; varying float vD; varying vec3 vN; varying vec3 vR;
    float wb(float y) { return y > ${f4(C.yl1)} ? mix(${f4(C.wmid)}, ${f4(C.wtop)}, (y - ${f4(C.yl1)}) / ${f4(C.ytop - C.yl1)}) : ${f4(C.wmid)} * clamp((y - ${f4(C.yv)}) / ${f4(C.yl1 - C.yv)}, 0.0, 1.0); }
    void main() {
      float gg = floor(vG + 0.5);
      if (gg == ${G.folder}.0 && folder < 0.5) discard;
      // the coat's front, found from where the point is on the resting figure: the blouse, the skirt below it, lapels
      if (gg == ${G.coat}.0 && vR.z > 0.03 && abs(vR.x) < 0.16) {
        float ax = abs(vR.x), y = vR.y;
        if (y > ${f4(C.cy0)} + 0.012 * (1.0 - ax / ${f4(C.cw0)}) && ax < mix(${f4(C.cw0)}, ${f4(C.cw1)}, (y - ${f4(C.cy0)}) / ${f4(C.ytop - C.cy0)})) gg = ${G.blouse}.0;
        else if (y > ${f4(C.yv)} && ax < wb(y)) gg = y > ${f4(C.yl1 - 0.06)} ? ${G.blouse}.0 : ${SKIRT}.0;
        else if (y <= ${f4(C.yv)} && ax < (${f4(C.gap)} + (${f4(C.yv)} - y) * 0.012) * clamp((${f4(C.yv)} - y) / 0.05, 0.0, 1.0)) gg = ${SKIRT}.0;
        else if (y < ${f4(C.ytop)} && y > ${f4(C.yl1)}) {
          float xo = y > ${f4(C.yl0)} ? mix(${f4(C.lap)}, wb(${f4(C.ytop)}) + 0.012, (y - ${f4(C.yl0)}) / ${f4(C.ytop - C.yl0)}) : mix(wb(${f4(C.yl1)}), ${f4(C.lap)}, (y - ${f4(C.yl1)}) / ${f4(C.yl0 - C.yl1)});
          if (ax < xo) gg = ${LAPEL}.0;
        }
      }
      vec3 n = normalize(vN); if (n.z < 0.0) n = -n;
      float shade = dot(n, L) > -0.12 ? 0.0 : 16.0;
      float z = clamp((vD - dn) / (df - dn), 0.0, 1.0) * 65535.0;
      float hi = floor(z / 256.0), lo = z - hi * 256.0;
      gl_FragColor = vec4((gg + shade) / 255.0, hi / 255.0, lo / 255.0, 1.0);
      if (show > 0.5) {      // to look at the form: plain grey clay, lit
        float d = 0.35 + 0.65 * max(0.0, dot(n, normalize(vec3(-0.45, 0.55, 0.7))));
        gl_FragColor = vec4(vec3(0.86, 0.85, 0.83) * d, 1.0);
      }
    }`,
});
const scene = new THREE.Scene();
scene.background = new THREE.Color(0, 1, 1);
const mesh = new THREE.Mesh(g, idMat); mesh.frustumCulled = false; scene.add(mesh);
const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 100);
const persp = new THREE.PerspectiveCamera(24, 1, 0.05, 200);
let camera = ortho, rt = null, buf = null, W = 0, Hh = 0, grpA = null, depA = null;

// ---------------------------------------------------------------- poses
function aim(pose, j, child, dir) {
  turnUnder(pose, sk, j, qBetween(normalize(sub(getV(pose.P, child), getV(pose.P, j))), normalize(dir)));
  build(pose, body, getV(pose.P, I.Hips));
}
// fingers a little curled, as a hand at rest (a pose layer over the rest pose or Kimodo's): each finger joint turned
// about the axis across the finger in the palm's plane
const FING = ['Index', 'Middle', 'Ring', 'Pinky'];
function relaxHands(pose, k = 1) {
  const cr = (u, w) => [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]];
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    const P = n => getV(pose.P, I[s + 'Hand' + n]), Hd = getV(pose.P, I[s + 'Hand']);
    const pn = normalize(cr(sub(P('Pinky1'), P('Index1')), sub(P('Middle1'), Hd)));
    const turns = [];
    FING.forEach((f, fi) => { for (let j = 3; j >= 1; j--) {
      const d = normalize(sub(P(f + (j + 1)), P(f + j)));
      turns.push([I[s + 'Hand' + f + j], qAxisAngle(normalize(cr(d, pn)), -sg * k * [0.22, 0.5, 0.42][j - 1] * (1 + fi * 0.18))]);
    } });
    for (const [j, r] of turns) turnUnder(pose, sk, j, r);
  }
  build(pose, body, getV(pose.P, I.Hips));
}
// the forearm turned about its own axis (the palm to the thigh)
function twist(pose, s, ang) {
  turnUnder(pose, sk, I[s + 'ForeArm'], qAxisAngle(normalize(sub(getV(pose.P, I[s + 'Hand']), getV(pose.P, I[s + 'ForeArm']))), ang));
  build(pose, body, getV(pose.P, I.Hips));
}
function standPose(o = {}) {
  const pose = fig.restPose();
  const outw = o.out ?? 0.15, fwd = o.fwd ?? 0.04;
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    aim(pose, I[s + 'Arm'], I[s + 'ForeArm'], [sg * outw, -1, -0.02]);
    aim(pose, I[s + 'ForeArm'], I[s + 'Hand'], [sg * outw * 0.4, -1, fwd + 0.12]);
    twist(pose, s, sg * (o.twist ?? 1.0));
  }
  if (o.figure) {
    // the drawing's figure: the right hand holds a folder against the hip, the left hand is at the glasses
    aim(pose, I.RightArm, I.RightForeArm, [-0.12, -1, -0.12]);
    aim(pose, I.RightForeArm, I.RightHand, [-0.02, -1, 0.3]);
    const hd = headFrame(pose), T = hd.at([0.26, 0.05, 0.36]);
    const Sh = getV(pose.P, I.LeftArm), L1 = Math.hypot(...sub(getV(pose.P, I.LeftForeArm), Sh)), L2 = Math.hypot(...sub(getV(pose.P, I.LeftHand), getV(pose.P, I.LeftForeArm))) + 0.11;
    let best = null;
    for (let a1 = -0.2; a1 <= 1.3; a1 += 0.05) for (let a2 = 0.0; a2 <= 1.5; a2 += 0.05) {
      const d = [Math.sin(a1) * Math.cos(a2), -Math.cos(a1) * Math.cos(a2), Math.sin(a2)], El = [Sh[0] + d[0] * L1, Sh[1] + d[1] * L1, Sh[2] + d[2] * L1];
      const err = Math.abs(Math.hypot(...sub(T, El)) - L2) + 0.05 * Math.abs(a1 - 0.3) + 0.03 * Math.abs(a2 - 0.8);
      if (!best || err < best[0]) best = [err, d, El];
    }
    aim(pose, I.LeftArm, I.LeftForeArm, best[1]);
    aim(pose, I.LeftForeArm, I.LeftHand, sub(T, getV(pose.P, I.LeftForeArm)));
  }
  for (const [k, ax] of [['headTurn', [0, 1, 0]], ['headTilt', [0, 0, 1]], ['headNod', [1, 0, 0]]]) if (o[k]) { turnUnder(pose, sk, I.Neck2, qAxisAngle(ax, o[k])); build(pose, body, getV(pose.P, I.Hips)); }
  return pose;
}
// the head's frame from a pose alone (before skinning): the rest frame carried by the Head joint
const MK = H.pieces.marks[0];
const mrest = [0, 1, 2, 3].map(k => [rest[(MK + k) * 3], rest[(MK + k) * 3 + 1], rest[(MK + k) * 3 + 2]]);
function headFrame(pose) {
  const qh = getQ(pose.Q, I.Head), jp = getV(pose.P, I.Head), jr = getV(body.joints, I.Head);
  const tr = p => { const r = qRot(qh, sub(p, jr)); return [jp[0] + r[0], jp[1] + r[1], jp[2] + r[2]]; };
  const m = mrest.map(tr);
  return { at: p => [0, 1, 2].map(c => m[0][c] + p[0] * (m[1][c] - m[0][c]) + p[1] * (m[2][c] - m[0][c]) + p[2] * (m[3][c] - m[0][c])) };
}
// the coat's lower shell kept off the legs (Р1's way): a point inside a leg's capsule is put on its surface, spread
const skR = H.pieces.skirt, RING = H.skirt.cols, skirt = [];
for (let i = skR[0]; i < skR[1]; i++) if (rest[i * 3 + 1] < 0.98) skirt.push(i);
const CAPS = [['LeftLeg', 'LeftShin', 0.062], ['LeftShin', 'LeftFoot', 0.046], ['RightLeg', 'RightShin', 0.062], ['RightShin', 'RightFoot', 0.046]].map(([p, b, r]) => [I[p], I[b], r]);
const skirtSet = new Int32Array(NV).fill(-1); skirt.forEach((i, k) => { skirtSet[i] = k; });
const skirtNb = skirt.map(i => { const k = i - skR[0], r = Math.floor(k / RING), c = k % RING;
  return [r * RING + (c + 1) % RING, r * RING + (c + RING - 1) % RING, (r - 1) * RING + c, (r + 1) * RING + c].map(m => m + skR[0]).filter(m => m >= skR[0] && m < skR[1] && skirtSet[m] >= 0).map(m => skirtSet[m]); });
const fadeK = Float64Array.from(skirt, i => { const u = Math.max(0, Math.min(1, (0.98 - rest[i * 3 + 1]) / 0.14)); return u * u * (3 - 2 * u); });
const dsp = new Float64Array(skirt.length * 3), dsp2 = new Float64Array(skirt.length * 3);
function pushSkirt(P, pose) {
  const caps = CAPS.map(([p, b, r], k) => { const A = getV(pose.P, p), B = getV(pose.P, b); return [k % 2 ? A : A.map((v, c) => (v + B[c]) / 2), B, r + 0.01]; });
  skirt.forEach((i, k) => {
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
    skirtNb.forEach((nb, k) => { for (let c = 0; c < 3; c++) { let s = dsp[k * 3 + c]; for (const m of nb) s += dsp[m * 3 + c]; dsp2[k * 3 + c] = s / (nb.length + 1); } });
    for (let k = 0; k < skirt.length; k++) for (let c = 0; c < 3; c++) { const x = dsp[k * 3 + c], y = dsp2[k * 3 + c]; dsp[k * 3 + c] = Math.abs(y) > Math.abs(x) ? y : (x + y) / 2 + (x - y) / 4; }
  }
  skirt.forEach((i, k) => { const w = fadeK[k]; P[i * 3] += w * dsp[k * 3]; P[i * 3 + 1] += w * dsp[k * 3 + 1]; P[i * 3 + 2] += w * dsp[k * 3 + 2]; });
}
// where the head looks over a clip (yaw, pitch at 100 Hz) — for the eyes to lead its turns
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

const S = { clip: null, clipIds: null, t: 0, time: 0, pose: 'stand', poseOpts: {}, push: true, lw: null, show: null, ground: true,
  cam: { mode: 'ortho', yaw: 0, pitch: 0, cx: 0, cy: 0.81, h: 1.75, dist: 6, target: null, follow: false } };
const face = new LiveFace(H.head.rest, Number(q.get('seed') ?? 7));
const head = new Head(H.head);
const JAWK = a.jawk, hd0 = H.pieces.head[0], hd1 = H.pieces.head[1];
let clip = null, fe = null;
function frame() {
  fe = face.at(S.time, { headT: S.clip ? S.t / clip.fps : null });
  head.setExpr(fe);
  let pose;
  if (S.clip) { pose = fig.retarget.pose(clip.sample(S.t, fig.sample)); fig.retarget.placed(pose); }
  else pose = S.pose === 'rest' ? fig.restPose() : standPose(S.poseOpts || {});
  relaxHands(pose, S.curl ?? 1);
  fig.skinner.skin(pose, fig.positions);
  const P = fig.positions;
  if (S.clip) {
    let lo = Infinity; for (let i = 1; i < P.length; i += 3) if (P[i] < lo) lo = P[i];
    const shift = pose.floor - lo; for (let i = 1; i < P.length; i += 3) P[i] += shift; for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
  }
  // the jaw: the chin goes down with the open mouth (head.py: the sections below the mouth move by jaw·0.07)
  const jaw = (fe.jaw || 0) * 0.07;
  if (jaw) {
    const d = [0, 1, 2].map(c => (P[(MK + 2) * 3 + c] - P[MK * 3 + c]) * jaw);
    for (let i = hd0; i < hd1; i++) { const k = JAWK[i]; if (k > 0) { P[i * 3] += d[0] * k; P[i * 3 + 1] += d[1] * k; P[i * 3 + 2] += d[2] * k; } }
  }
  if (S.poseOpts?.figure && !S.clip) {
    // the folder of the drawn pose: a board facing forward at the right wrist, the hand over its lower inner corner
    const hp = getV(pose.P, I.RightHand), F0 = H.pieces.folder[0], w = 0.215, hh = 0.3, c = [hp[0] - 0.035, hp[1] + 0.045, hp[2] - 0.028];
    [[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1], [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]].forEach(([x, y, z], k) => {
      P[(F0 + k) * 3] = c[0] + x * w / 2 + y * 0.012; P[(F0 + k) * 3 + 1] = c[1] + y * hh / 2; P[(F0 + k) * 3 + 2] = c[2] + z * 0.004 - x * 0.02; });
  }
  if (S.push && S.pose !== 'rest') pushSkirt(P, pose);
  fig.pose = pose;
  g.attributes.position.needsUpdate = true;
}

// ---------------------------------------------------------------- per-frame geometry
const fn = new Float32Array(NT * 3), facing = new Uint8Array(NT), vn = new Float32Array(NV * 3);
const scr = new Float32Array(NV * 3);
let camPos = [0, 0, 0], viewDir = [0, 0, -1], camR = [1, 0, 0], camU = [0, 1, 0], isOrtho = true;
const mvp = new THREE.Matrix4(), vm = new THREE.Matrix4();
function normals() {
  const P = fig.positions; vn.fill(0);
  for (let t = 0; t < NT; t++) {
    const i = TRI[t * 3] * 3, j = TRI[t * 3 + 1] * 3, k = TRI[t * 3 + 2] * 3;
    const ux = P[j] - P[i], uy = P[j + 1] - P[i + 1], uz = P[j + 2] - P[i + 2], wx = P[k] - P[i], wy = P[k + 1] - P[i + 1], wz = P[k + 2] - P[i + 2];
    const nx = uy * wz - uz * wy, ny = uz * wx - ux * wz, nz = ux * wy - uy * wx;
    fn[t * 3] = nx; fn[t * 3 + 1] = ny; fn[t * 3 + 2] = nz;
    for (const m of [i, j, k]) { vn[m] += nx; vn[m + 1] += ny; vn[m + 2] += nz; }
    const d = isOrtho ? -(nx * viewDir[0] + ny * viewDir[1] + nz * viewDir[2]) : nx * (camPos[0] - P[i]) + ny * (camPos[1] - P[i + 1]) + nz * (camPos[2] - P[i + 2]);
    facing[t] = d > 0 ? 1 : 0;
  }
  for (let i = 0; i < NV; i++) { const l = Math.hypot(vn[i * 3], vn[i * 3 + 1], vn[i * 3 + 2]) || 1; vn[i * 3] /= l; vn[i * 3 + 1] /= l; vn[i * 3 + 2] /= l; }
  fig.normals.set(vn); g.attributes.normal.needsUpdate = true;
}
const e = mvp.elements, ve = vm.elements;
function project(x, y, z, o, k = 0) {
  const w = e[3] * x + e[7] * y + e[11] * z + e[15];
  o[k] = ((e[0] * x + e[4] * y + e[8] * z + e[12]) / w * 0.5 + 0.5) * W;
  o[k + 1] = (1 - ((e[1] * x + e[5] * y + e[9] * z + e[13]) / w * 0.5 + 0.5)) * Hh;
  o[k + 2] = -(ve[2] * x + ve[6] * y + ve[10] * z + ve[14]);
  return o;
}
function projectAll() { const P = fig.positions; for (let i = 0; i < NV; i++) project(P[i * 3], P[i * 3 + 1], P[i * 3 + 2], scr, i * 3); }
const depthAt = (x, y) => { x = Math.round(x); y = Math.round(y); if (x < 0 || y < 0 || x >= W || y >= Hh) return Infinity; const k = y * W + x; return grpA[k] ? depA[k] : Infinity; };
const grpAt = (x, y) => { x = Math.round(x); y = Math.round(y); if (x < 0 || y < 0 || x >= W || y >= Hh) return 0; return grpA[y * W + x] & 15; };
function seen(x, y, z, eps = 0.006, r = 1) {
  for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (depthAt(x + dx, y + dy) >= z - eps) return true;
  return false;
}

// ---------------------------------------------------------------- lines on the form
const INNER = a.inner, EV = a.edges, ET = a.edgeTris, EDROP = a.edgeDrop, NE = EV.length / 2;
const skinLike = gid => gid === G.skin;
function contours() {
  const keep = new Uint8Array(NE), adj = new Map();
  const addAdj = (v, k) => { let l = adj.get(v); if (!l) adj.set(v, l = []); l.push(k); };
  for (let k = 0; k < NE; k++) {
    if (EDROP[k]) continue;
    const f0 = ET[k * 2], f1 = ET[k * 2 + 1], open = f1 === NONE;
    if (!open && facing[f0] === facing[f1]) continue;
    const i = EV[k * 2], j = EV[k * 2 + 1];
    if (a.grp[i] === G.folder && !U.folder.value) continue;
    const mx = (scr[i * 3] + scr[j * 3]) / 2, my = (scr[i * 3 + 1] + scr[j * 3 + 1]) / 2, mz = (scr[i * 3 + 2] + scr[j * 3 + 2]) / 2;
    if (!seen(mx, my, mz, open ? 0.004 : 0.006)) continue;
    if (!open && !(INNER[i] && INNER[j])) {      // on the face: only where skin meets something else
      const tx = scr[j * 3] - scr[i * 3], ty = scr[j * 3 + 1] - scr[i * 3 + 1], l = Math.hypot(tx, ty) || 1, nx = -ty / l * 3, ny = tx / l * 3;
      if (skinLike(grpAt(mx + nx, my + ny)) && skinLike(grpAt(mx - nx, my - ny))) continue;
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
// a chain of vertices → smoothed picture points with the contour's weight at each (heavier where the form's outward
// direction on the page points away from the light); broken where it turns sharply
function chainPts(vs, k) {
  let P = [];
  for (const v of vs) {
    const p = [scr[v * 3], scr[v * 3 + 1]];
    if (P.length && Math.hypot(p[0] - P[P.length - 1][0], p[1] - P[P.length - 1][1]) < 0.3) continue;
    const nx = vn[v * 3] * camR[0] + vn[v * 3 + 1] * camR[1] + vn[v * 3 + 2] * camR[2], ny = -(vn[v * 3] * camU[0] + vn[v * 3 + 1] * camU[1] + vn[v * 3 + 2] * camU[2]), l = Math.hypot(nx, ny) || 1;
    p.push(1 + k * -(nx / l * K.LIGHT[0] + ny / l * K.LIGHT[1]));
    P.push(p);
  }
  if (P.length < 2) return [];
  P = resample(P, 2.5);
  for (let it = 0; it < 4; it++) P = P.map((p, i) => i === 0 || i === P.length - 1 ? p : [(P[i - 1][0] + 2 * p[0] + P[i + 1][0]) / 4, (P[i - 1][1] + 2 * p[1] + P[i + 1][1]) / 4, (P[i - 1][2] + 2 * p[2] + P[i + 1][2]) / 4]);
  const outp = []; let cur = [P[0]];
  for (let i = 1; i < P.length - 1; i++) {
    cur.push(P[i]);
    const a0 = Math.atan2(P[i][1] - P[i - 1][1], P[i][0] - P[i - 1][0]), a1 = Math.atan2(P[i + 1][1] - P[i][1], P[i + 1][0] - P[i][0]);
    let da = Math.abs(a1 - a0); if (da > Math.PI) da = 2 * Math.PI - da;
    if (da > 1.0) { outp.push(cur); cur = [P[i]]; }
  }
  cur.push(P[P.length - 1]); outp.push(cur);
  return outp;
}
function resample(P, step) {
  const o = [P[0]]; let acc = 0;
  for (let i = 1; i < P.length; i++) {
    let p0 = P[i - 1]; const p1 = P[i]; let d = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]);
    while (acc + d >= step) { const t = (step - acc) / d; p0 = [p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, p0[2] + (p1[2] - p0[2]) * t]; o.push(p0); d = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]); acc = 0; }
    acc += d;
  }
  const l = o[o.length - 1], z = P[P.length - 1];
  if (Math.hypot(l[0] - z[0], l[1] - z[1]) > step * 0.3) o.push(z);
  return o;
}
const plen = P => { let s = 0; for (let i = 1; i < P.length; i++) s += Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]); return s; };

// ---------------------------------------------------------------- the tone: every pixel black or white
const fcv = document.createElement('canvas'), fctx = fcv.getContext('2d');
let img = null;
function tones(s) {
  const n = W * Hh, pitch = S.pitch || K.PITCH;
  for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++) {
    const k = ((Hh - 1 - y) * W + x) * 4, i = y * W + x, v = buf[k];
    grpA[i] = v; depA[i] = v ? U.dn.value + (buf[k + 1] * 256 + buf[k + 2]) / 65535 * (U.df.value - U.dn.value) : Infinity;
  }
  const b1 = Math.max(1, Math.round(0.007 * s)), b2 = Math.max(2, Math.round(0.034 * s)), cx = Math.round(0.05 * s), cy = Math.round(0.09 * s);
  const D = img.data, [pr, pg, pb] = K.PAPER_RGB, [ir, ig, ib] = K.INK_RGB;
  const src = (x, y) => (x < 0 || y < 0) ? -1 : y * W + x;
  for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++) {
    const i = y * W + x, v = grpA[i], gid = v & 15, d = depA[i];
    let ink = -1;
    // the black band on the shadow side of a form: a nearer form stands just up-left of this pixel
    const s1 = src(x - b1, y - b1), s2 = src(x - b2, y - b2);
    if (s1 >= 0 && grpA[s1] && d > depA[s1] + 0.03 && (gid === 0 || (grpA[s1] & 15) !== G.hair)) ink = 1;
    else if (s2 >= 0 && CLOTH.has(grpA[s2] & 15) && d > depA[s2] + 0.05) ink = 1;
    else if (gid) {
      const lv = LV[gid]; let level = v & 16 ? lv[1] : lv[0];
      const sc = src(x - cx, y - cy);
      if (sc >= 0 && grpA[sc] && d > depA[sc] + 0.04) level = Math.max(level, lv[2]);       // a cast shadow
      ink = K.toneAt(x, y, level, pitch);
    }
    const o = i * 4;
    if (ink < 0) { D[o + 3] = 0; continue; }
    D[o] = pr + (ir - pr) * ink; D[o + 1] = pg + (ig - pg) * ink; D[o + 2] = pb + (ib - pb) * ink; D[o + 3] = 255;
  }
  fctx.putImageData(img, 0, 0);
}

// ---------------------------------------------------------------- the picture
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
  } else { camera = persp; persp.aspect = w / h; persp.fov = c.fov || 24; persp.updateProjectionMatrix(); dist = c.dist; }
  camera.position.set(tg[0] + dir[0] * dist, tg[1] + dir[1] * dist, tg[2] + dir[2] * dist);
  camera.lookAt(tg[0], tg[1], tg[2]); camera.updateMatrixWorld();
  isOrtho = c.mode === 'ortho'; camPos = [camera.position.x, camera.position.y, camera.position.z];
  viewDir = normalize([-dir[0], -dir[1], -dir[2]]);
  const m = camera.matrixWorld.elements; camR = [m[0], m[1], m[2]]; camU = [m[4], m[5], m[6]];
  vm.copy(camera.matrixWorldInverse); mvp.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  U.dn.value = dist - 3; U.df.value = dist + 3;
  U.L.value.set(-0.45, 0.55, 0.70).normalize();      // head.py LIGHT3, in the camera's frame: from the upper left, in front
}
// the head as head.js sees it
function headView(s0) {
  const P = fig.positions, m = [0, 1, 2, 3].map(k => [P[(MK + k) * 3], P[(MK + k) * 3 + 1], P[(MK + k) * 3 + 2]]);
  const ax = [1, 2, 3].map(k => sub(m[k], m[0]));
  const at = p => [0, 1, 2].map(c => m[0][c] + p[0] * ax[0][c] + p[1] * ax[1][c] + p[2] * ax[2][c]);
  const toCam = isOrtho ? [-viewDir[0], -viewDir[1], -viewDir[2]] : normalize(sub(camPos, m[0]));
  const fwd = normalize(ax[2]);
  const dot = (u, w) => u[0] * w[0] + u[1] * w[1] + u[2] * w[2];
  const v = {
    pt: p => { const w = at(p); return project(w[0], w[1], w[2], [0, 0, 0]); },
    facing: n => dot(normalize([0, 1, 2].map(c => n[0] * ax[0][c] + n[1] * ax[1][c] + n[2] * ax[2][c])), toCam),
    across: p => { const w = at(p); return dot(w, camR); },
    seen: p => seen(p[0], p[1], p[2], 0.02, 1),
    yaw: Math.atan2(dot(fwd, camR), dot(fwd, [-viewDir[0], -viewDir[1], -viewDir[2]])) * 180 / Math.PI,
    pitch: S.pitch || K.PITCH, at,
  };
  const p0 = v.pt([0, 0, 0]), p1 = v.pt([0, 1, 0]); v.s = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]);
  return v;
}
function draw() {
  const w = Math.round(stage.clientWidth || innerWidth), h = Math.round(stage.clientHeight || innerHeight);
  if (w !== W || h !== Hh) {
    W = w; Hh = h; rt?.dispose(); rt = new THREE.WebGLRenderTarget(W, Hh, { depthBuffer: true }); buf = new Uint8Array(W * Hh * 4);
    renderer.setSize(W, Hh, false); out.width = W; out.height = Hh; fcv.width = W; fcv.height = Hh; img = fctx.createImageData(W, Hh);
    grpA = new Uint8Array(W * Hh); depA = new Float32Array(W * Hh);
  }
  const T0 = performance.now(), prof = {};
  setCamera(W, Hh); normals();
  U.folder.value = S.poseOpts?.figure && !S.clip ? 1 : 0;
  renderer.setRenderTarget(rt); renderer.render(scene, camera); renderer.readRenderTargetPixels(rt, 0, 0, W, Hh, buf); renderer.setRenderTarget(null);
  prof.gl = performance.now() - T0;
  if (S.clay) { const bg = scene.background; scene.background = new THREE.Color().setStyle(K.PAPER, THREE.LinearSRGBColorSpace); U.show.value = 1; renderer.render(scene, camera); U.show.value = 0; scene.background = bg; document.body.classList.add('clay'); return; }
  document.body.classList.remove('clay');
  projectAll();
  const v = headView(), s = v.s, lw = S.lw ?? Math.min(3.2, 1.0 + s / 240);
  ctx.fillStyle = K.PAPER; ctx.fillRect(0, 0, W, Hh);
  if (S.sky) {      // the drawing's backdrop (build.py `sky`): a graded tone, light at the top left
    const bg = ctx.getImageData(0, 0, W, Hh), D = bg.data, [pr, pg, pb] = K.PAPER_RGB, [ir, ig, ib] = K.INK_RGB;
    for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++) {
      const c = S.sky[0] + (S.sky[1] - S.sky[0]) * Math.max(0, Math.min(1, y / Hh * 0.7 + x / W * 0.3)) ** 1.4;
      if (c <= 0.015) continue;
      const ink = K.toneAt(x, y, c, v.pitch), o = (y * W + x) * 4;
      D[o] = pr + (ir - pr) * ink; D[o + 1] = pg + (ig - pg) * ink; D[o + 2] = pb + (ib - pb) * ink;
    }
    ctx.putImageData(bg, 0, 0);
  }
  // the shadow on the ground (build.py ground_shadow of the style): an ellipse of tone under her
  if (S.ground) {
    const PJ = fig.pose.P, c = project(PJ[I.Hips * 3], fig.pose.floor ?? 0, PJ[I.Hips * 3 + 2], [0, 0, 0]), e0 = project(PJ[I.Hips * 3] + camR[0] * 0.2, fig.pose.floor ?? 0, PJ[I.Hips * 3 + 2] + camR[2] * 0.2, [0, 0, 0]);
    const rx = Math.hypot(e0[0] - c[0], e0[1] - c[1]) * 1.05, ry = Math.max(rx * 0.19, rx * Math.abs(viewDir[1]) * 1.0), el = [];
    for (let k = 0; k < 40; k++) el.push([c[0] + rx * 0.1 + rx * Math.cos(k / 40 * 6.2832), c[1] + ry * Math.sin(k / 40 * 6.2832)]);
    K.toneFill(ctx, el, 0.3, v.pitch);
  }
  if (!S.noTone) { tones(s); ctx.drawImage(fcv, 0, 0); }
  else { for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++) { const k = ((Hh - 1 - y) * W + x) * 4, i = y * W + x, vv = buf[k]; grpA[i] = vv; depA[i] = vv ? U.dn.value + (buf[k + 1] * 256 + buf[k + 2]) / 65535 * (U.df.value - U.dn.value) : Infinity; } }
  prof.tone = performance.now() - T0;
  if (!S.noLine) {
    for (const vs of contours()) {
      const pn = PN[vpid[vs[0]]];
      const base = pn === 'head' || pn === 'ears' || pn === 'neck' ? 1.25 : pn === 'hair' || pn === 'bun' ? 0.9 : 1.0;
      for (const P of chainPts(vs, 0.6)) {
        if (plen(P) < 5 * lw) continue;
        K.stroke(ctx, P, P.map(p => Math.max(0.35, lw * base * p[2])), { taper: [0.06, 0.08], smooth: false });
      }
    }
    // the coat's front edges and lapels: curves on the surface
    const P = fig.positions, CT = a.curveTri, CB = a.curveBar, tmp = [0, 0, 0];
    for (const cv of H.curves) {
      const runs = []; let cur = [];
      for (let k = cv.start; k < cv.start + cv.n; k++) {
        const t = CT[k]; let x = 0, y = 0, z = 0;
        for (let c = 0; c < 3; c++) { const vi = TRI[t * 3 + c], b = CB[k * 3 + c]; x += b * P[vi * 3]; y += b * P[vi * 3 + 1]; z += b * P[vi * 3 + 2]; }
        project(x, y, z, tmp);
        if (facing[t] && seen(tmp[0], tmp[1], tmp[2], 0.008, 1)) cur.push([tmp[0], tmp[1]]); else { if (cur.length > 2) runs.push(cur); cur = []; }
      }
      if (cur.length > 2) runs.push(cur);
      for (const r of runs) K.stroke(ctx, r, lw * cv.w, { taper: cv.taper, smooth: false });
    }
    hairLines(lw, s);
    head.draw(ctx, v, lw);
    // the loose strand at the temple
    const lk = H.lock, lp = []; for (let k = 0; k <= 12; k++) { const t = k / 12 * (lk.pts.length - 1), i = Math.min(lk.pts.length - 2, Math.floor(t)), f = t - i; lp.push([0, 1, 2].map(c => lk.pts[i][c] + (lk.pts[i + 1][c] - lk.pts[i][c]) * f)); }
    head.line(ctx, v, lp, [lw * 1.4, lw * 1.2, lw * 0.5], { taper: [0.05, 0.5] });
  }
  prof.all = performance.now() - T0; A.prof = prof;
}
// the hair: white streaks of light along the strands on the side turned to the light; short black teeth at the hairline
const hrand = (() => { let sd = 51; return () => { sd = (sd * 1664525 + 1013904223) >>> 0; return sd / 4294967296; }; })();
const teeth = H.hairline.map(() => 0.4 + hrand() * 1.0);
function hairLines(lw, s) {
  const NTR = H.hair.ntr;
  const lit = i => { const nx = vn[i * 3], ny = vn[i * 3 + 1], nz = vn[i * 3 + 2]; const f = -(nx * viewDir[0] + ny * viewDir[1] + nz * viewDir[2]); const l = -(nx * camR[0] + ny * camR[1] + nz * camR[2]) * 0.45 + (nx * camU[0] + ny * camU[1] + nz * camU[2]) * 0.55 + f * 0.7; return f > 0.12 && l > 0.52; };
  for (const st of H.streaks) {
    const runs = []; let cur = [];
    for (const i of st.v) { if (lit(i) && seen(scr[i * 3], scr[i * 3 + 1], scr[i * 3 + 2], 0.006, 0)) cur.push([scr[i * 3], scr[i * 3 + 1]]); else { if (cur.length > 2) runs.push(cur); cur = []; } }
    if (cur.length > 2) runs.push(cur);
    for (const r of runs) K.stroke(ctx, r, lw * st.w * 0.9, { taper: [0.45, 0.45], fill: K.PAPER });
  }
  H.hairline.forEach((i, k) => {
    const j = i + 2, x = scr[i * 3], y = scr[i * 3 + 1];
    const f = -(vn[j * 3] * viewDir[0] + vn[j * 3 + 1] * viewDir[1] + vn[j * 3 + 2] * viewDir[2]);
    if (f < 0.1 || !seen(x, y, scr[i * 3 + 2], 0.012, 1)) return;
    const dx = x - scr[j * 3], dy = y - scr[j * 3 + 1], l = Math.hypot(dx, dy) || 1, L = 0.034 * s * teeth[k];
    K.stroke(ctx, [[x - dx / l * 2, y - dy / l * 2], [x + dx / l * L, y + dy / l * L]], [lw * 1.9, lw * 0.3], { taper: [0, 0.6], smooth: false });
  });
}

function facingYaw() { const qh = getQ(fig.pose.Q, I.Hips); const x = 2 * (qh[0] * qh[2] + qh[1] * qh[3]), z = 1 - 2 * (qh[0] * qh[0] + qh[1] * qh[1]); return Math.atan2(x, z); }
const A = window.A = {
  H, body, fig, sk, face, S, facing: facingYaw, clipInfo: () => clip && { frames: clip.frames, fps: clip.fps },
  async set(o) {
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; face.setHead(clip ? headTrack(clip) : null); }
      S.clip = !!ids;
    }
    for (const k of ['t', 'pose', 'poseOpts', 'push', 'lw', 'pitch', 'noTone', 'noLine', 'clay', 'ground', 'curl', 'sky']) if (o[k] !== undefined) S[k] = o[k];
    if (o.time !== undefined) S.time = o.time; else if (o.t !== undefined && clip && !S.liveClock) S.time = o.t / clip.fps;
    if (o.liveClock !== undefined) S.liveClock = o.liveClock;
    if (o.still !== undefined) face.still = o.still;
    if (o.exprTrack) { face.exprKeys = [{ t: -10, w: { rest: 1 } }]; for (const [t, w] of o.exprTrack) face.setExpr(t, typeof w === 'string' ? { [w]: 1 } : w); }
    if (o.expr) face.setExpr(S.time, typeof o.expr === 'string' ? { [o.expr]: 1 } : o.expr);
    if (o.talk !== undefined) { face.talk(o.talk ? (o.talkFrom ?? S.time) : null); face.talkTo = o.talkTo ?? null; }
    if (o.cam) Object.assign(S.cam, o.cam);
    frame();
  },
  render() { draw(); },
};
await A.set({});
A.render();
window.__ready = true;

if (!q.has('pack')) (await import('./ui.js')).ui(A, stage);
