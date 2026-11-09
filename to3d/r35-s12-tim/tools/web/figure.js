// A С12 character in 3D, drawn every frame in pen and watercolour — Р12's renderer (to3d/r12-s12-anya/tools/web/anya.js)
// made to take any character of the style: what is the character's own (its washes, its face, its poses, its props)
// is in char.js. The form (tools/build.py's pack) moves on the engine's skeleton, skinning and Kimodo retargeting; it
// is not shaded. Each frame:
//   1. the figure is rendered once, unseen, into a picture of which wash each pixel belongs to and how far it is;
//   2. lines are found on the 3D: silhouettes (where the surface turns away) and open edges (a hem, a collar, the hair
//      round the face), kept where that picture says they are seen, chained, smoothed, broken into strokes as a hand
//      would — and drawn with the drawing's own pen (pen.js = kit.py);
//   3. the washes are the seen parts as masks, each painted with the drawing's watercolour filter and moved a little
//      off the line;
//   4. the face — eyes, brows, mouth, freckles, cheeks — is drawn with the drawing's parts (parts.py) in its front
//      units, laid on the 3D head (a grid on the head, build.py), so it turns and foreshortens with the head;
//   5. lines and marks that belong to the form (folds, buttons, curls), where they are seen.
//   view.html — by hand (ui.js); view.html?pack=<url> — driven by tools/shots.mjs
//   window.A.set({clip, t, time, pose, expr, talk, cam, …}) then await A.render()
import * as THREE from 'three';
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { qAxisAngle, qBetween, qRot, getQ, getV, normalize, sub } from '../../../../engine/src/math.js';
import * as K from './pen.js';
import { LiveFace } from './face.js';
import * as CH from './char.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack') || '../../data/' + CH.PACK, location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const sk = E.skeleton, J = sk.J, I = sk.index;

const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const rest = Float32Array.from(a.positions);
const spec = { skinning: { method: H.skinning || 'cor', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
const NV = rest.length / 3, TRI = a.triangles, NT = TRI.length / 3;
const NONE = 0xFFFFFFFF;

const G = H.groups;
const WASHES = CH.washes(G);        // [{groups: [ids], shade?, color, op, dx, dy, rough, angle?}] in painting order

// ---------------------------------------------------------------- the unseen picture: wash group and depth
const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
const g = new THREE.BufferGeometry();
g.setAttribute('position', new THREE.BufferAttribute(fig.positions, 3));
g.setAttribute('normal', new THREE.BufferAttribute(fig.normals, 3));
g.setAttribute('grp', new THREE.BufferAttribute(Float32Array.from(a.grp), 1));
g.setAttribute('band', new THREE.BufferAttribute(a.band, 1));
g.setAttribute('stripe', new THREE.BufferAttribute(a.stripe, 1));
g.setIndex(new THREE.BufferAttribute(a.triangles, 1));
const U = { dn: { value: 0 }, df: { value: 10 }, L: { value: new THREE.Vector3(0, 0, 1) }, show: { value: 0 } };
const idMat = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.DoubleSide,
  vertexShader: `attribute float grp; attribute float band; attribute float stripe; varying float vG; varying float vB; varying float vS; varying float vD; varying vec3 vN;
    void main() { vG = grp; vB = band; vS = stripe; vN = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position, 1.0); vD = -mv.z; gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `uniform float dn; uniform float df; uniform vec3 L; varying float vG; varying float vB; varying float vS; varying float vD; varying vec3 vN;
    void main() {
      float gg = floor(vG + 0.5);
      ${CH.glsl(G)}
      vec3 n = normalize(vN); if (n.z < 0.0) n = -n;       // the side we see (shells are two-sided)
      float lit = dot(n, L) > -0.05 ? 0.0 : 32.0;
      float z = clamp((vD - dn) / (df - dn), 0.0, 1.0) * 65535.0;
      float hi = floor(z / 256.0), lo = z - hi * 256.0;
      gl_FragColor = vec4((gg + lit) / 255.0, hi / 255.0, lo / 255.0, 1.0);
    }`,
});
const scene = new THREE.Scene();
scene.background = new THREE.Color(0, 1, 1);           // background: group 0, the farthest depth
const mesh = new THREE.Mesh(g, idMat); mesh.frustumCulled = false; scene.add(mesh);
const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 100);
const persp = new THREE.PerspectiveCamera(24, 1, 0.05, 200);
let camera = ortho, rt = null, buf = null, W = 0, Hh = 0;

// ---------------------------------------------------------------- poses
// standing: the arms down (out, fwd) or as asked (arms: {Left: {upper: dir, fore: dir}, …}), the trunk leaning
// (lean, radians forward), the head turned / tilted / nodding — the drawing's figure is such a pose
function standPose(o = {}) {
  const pose = fig.restPose();
  const rb = () => build(pose, body, getV(pose.P, I.Hips));
  const out = o.out ?? 0.13, fwd = o.fwd ?? 0.03;
  if (o.lean) { turnUnder(pose, sk, I.Spine1, qAxisAngle([1, 0, 0], o.lean)); rb(); }
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    const A = I[s + 'Arm'], F = I[s + 'ForeArm'], Hd = I[s + 'Hand'], ar = o.arms?.[s];
    if (ar) {
      turnUnder(pose, sk, A, qBetween(normalize(sub(getV(pose.P, F), getV(pose.P, A))), normalize(ar.upper))); rb();
      turnUnder(pose, sk, F, qBetween(normalize(sub(getV(pose.P, Hd), getV(pose.P, F))), normalize(ar.fore))); rb();
    } else {
      turnUnder(pose, sk, A, qBetween(normalize(sub(getV(pose.P, Hd), getV(pose.P, A))), normalize([sg * out, -1, fwd]))); rb();
    }
  }
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    const lg = o.legs?.[s]; if (!lg) continue;
    const Lg = I[s + 'Leg'], Sh = I[s + 'Shin'], Ft = I[s + 'Foot'];
    turnUnder(pose, sk, Lg, qBetween(normalize(sub(getV(pose.P, Sh), getV(pose.P, Lg))), normalize(lg.upper))); rb();
    if (lg.lower) { turnUnder(pose, sk, Sh, qBetween(normalize(sub(getV(pose.P, Ft), getV(pose.P, Sh))), normalize(lg.lower))); rb(); }
  }
  if (o.headTurn) { turnUnder(pose, sk, I.Neck2, qAxisAngle([0, 1, 0], o.headTurn)); rb(); }
  if (o.headTilt) { turnUnder(pose, sk, I.Neck2, qAxisAngle([0, 0, 1], o.headTilt)); rb(); }
  if (o.headNod) { turnUnder(pose, sk, I.Neck2, qAxisAngle([1, 0, 0], o.headNod)); rb(); }
  return pose;
}
// a skirt-like shell (the pack's header.skirt: {piece, ring, top, caps}) kept off the legs (Р1's): each of its points
// inside a leg's capsule is put on its surface, the push spread over the shell
const SK = H.skirt || null;
const dressR = SK ? H.pieces[SK.piece] : [0, 0], skirt = [];
for (let i = dressR[0]; i < dressR[1]; i++) if (rest[i * 3 + 1] < (SK?.top ?? 0)) skirt.push(i);
const CAPS = (SK?.caps || []).map(([p, b, r]) => [I[p], I[b], r]);
const RING = SK?.ring || 1, skirtSet = new Int32Array(NV).fill(-1); skirt.forEach((i, k) => { skirtSet[i] = k; });
const skirtNb = skirt.map(i => { const k = i - dressR[0], r = Math.floor(k / RING), c = k % RING;
  const nb = SK.closed === false ? [c + 1 < RING ? r * RING + c + 1 : -1, c > 0 ? r * RING + c - 1 : -1, (r - 1) * RING + c, (r + 1) * RING + c] : [r * RING + (c + 1) % RING, r * RING + (c + RING - 1) % RING, (r - 1) * RING + c, (r + 1) * RING + c];
  return nb.filter(m => m >= 0).map(m => m + dressR[0]).filter(m => m < dressR[1] && skirtSet[m] >= 0).map(m => skirtSet[m]); });
const fadeK = Float64Array.from(skirt, i => { const u = Math.max(0, Math.min(1, ((SK?.top ?? 0) - rest[i * 3 + 1]) / 0.14)); return u * u * (3 - 2 * u); });
const dsp = new Float64Array(skirt.length * 3), dsp2 = new Float64Array(skirt.length * 3);
function pushSkirt(P, pose) {
  if (!SK) return;
  const caps = CAPS.map(([p, b, r], k) => { const A = getV(pose.P, p), B = getV(pose.P, b); return [k % 2 ? A : A.map((v, c) => (v + B[c]) / 2), B, r + 0.008]; });
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
  for (let it = 0; it < 6; it++) {
    skirtNb.forEach((nb, k) => { for (let c = 0; c < 3; c++) { let s = dsp[k * 3 + c]; for (const m of nb) s += dsp[m * 3 + c]; dsp2[k * 3 + c] = s / (nb.length + 1); } });
    for (let k = 0; k < skirt.length; k++) for (let c = 0; c < 3; c++) { const x = dsp[k * 3 + c], y = dsp2[k * 3 + c]; dsp[k * 3 + c] = Math.abs(y) > Math.abs(x) ? y : (x + y) / 2 + (x - y) / 4; }
  }
  skirt.forEach((i, k) => { const w = fadeK[k]; P[i * 3] += w * dsp[k * 3]; P[i * 3 + 1] += w * dsp[k * 3 + 1]; P[i * 3 + 2] += w * dsp[k * 3 + 2]; });
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

const S = { clip: null, clipIds: null, t: 0, time: 0, pose: 'stand', poseOpts: {}, push: true, lw: 1, fade: null, seed: 1, show: null,
  cam: { mode: 'ortho', yaw: 0, pitch: 0, cx: 0, cy: 0.81, h: 1.75, dist: 6, target: null, follow: false } };
const face = new LiveFace(Number(q.get('seed') ?? 7), CH.EXPR, CH.NAMES);
let clip = null, fp = null;
function frame() {
  fp = face.at(S.time, { headT: S.clip ? S.t / clip.fps : null });
  let pose;
  if (S.clip) { pose = fig.retarget.pose(clip.sample(S.t, fig.sample)); fig.retarget.placed(pose); }
  else if (S.pose === 'raw') pose = null;
  else pose = S.pose === 'rest' ? fig.restPose() : standPose({ ...(CH.STAND || {}), ...(S.poseOpts || {}) });
  if (!pose) { fig.positions.set(rest); fig.pose = fig.restPose(); }
  else {
    if (fp.tiltHead) turnUnder(pose, sk, I.Neck2, qAxisAngle(qRot(getQ(pose.Q, I.Neck2), [0, 0, 1]), fp.tiltHead * Math.PI / 180 * 0.6));
    if (fp.tiltHead) build(pose, body, getV(pose.P, I.Hips));
    if (CH.poseHook) { CH.poseHook(pose, fp, { turnUnder, sk, I, getQ, qRot, qAxisAngle }); build(pose, body, getV(pose.P, I.Hips)); }      // the character's own (a jaw that drops)
    fig.skinner.skin(pose, fig.positions);
    if (S.clip || S.pose === 'stand') {
      if (!S.clip) pose.floor = 0;
      const P = fig.positions; let lo = Infinity; for (let i = 1; i < P.length; i += 3) if (P[i] < lo) lo = P[i];
      const shift = pose.floor - lo; for (let i = 1; i < P.length; i += 3) P[i] += shift; for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
    }
    if (S.push) pushSkirt(fig.positions, pose);
    fig.pose = pose;
  }
  g.attributes.position.needsUpdate = true;
}

// ---------------------------------------------------------------- per-frame geometry
const fn = new Float32Array(NT * 3), facing = new Uint8Array(NT), vn = new Float32Array(NV * 3);
const scr = new Float32Array(NV * 3);          // picture x, y (from the doc's origin) and depth
let camPos = [0, 0, 0], viewDir = [0, 0, -1], isOrtho = true, origin = [0, 0];
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
  fig.normals.set(vn); g.attributes.normal.needsUpdate = true;
}
const e = mvp.elements, ve = vm.elements;
function project(x, y, z, out, o = 0) {
  const w = e[3] * x + e[7] * y + e[11] * z + e[15];
  out[o] = ((e[0] * x + e[4] * y + e[8] * z + e[12]) / w * 0.5 + 0.5) * W - origin[0];
  out[o + 1] = (1 - ((e[1] * x + e[5] * y + e[9] * z + e[13]) / w * 0.5 + 0.5)) * Hh - origin[1];
  out[o + 2] = -(ve[2] * x + ve[6] * y + ve[10] * z + ve[14]);
}
function projectAll() { const P = fig.positions; for (let i = 0; i < NV; i++) project(P[i * 3], P[i * 3 + 1], P[i * 3 + 2], scr, i * 3); }
// the unseen picture: group (low 3 bits + 8 when in shade) and depth
const depthAt = (x, y) => { x = Math.round(x + origin[0]); y = Math.round(y + origin[1]); if (x < 0 || y < 0 || x >= W || y >= Hh) return Infinity;
  const k = ((Hh - 1 - y) * W + x) * 4; if ((buf[k] & 31) === 0) return Infinity; return U.dn.value + (buf[k + 1] * 256 + buf[k + 2]) / 65535 * (U.df.value - U.dn.value); };
const grpAt = (x, y) => { x = Math.round(x + origin[0]); y = Math.round(y + origin[1]); if (x < 0 || y < 0 || x >= W || y >= Hh) return 0; return buf[((Hh - 1 - y) * W + x) * 4] & 31; };
// seen: some pixel round the point is not in front of it
function seen(x, y, z, eps = 0.006, r = 1) {
  for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (depthAt(x + dx, y + dy) >= z - eps) return true;
  return false;
}

// ---------------------------------------------------------------- lines on the form
const INNER = a.inner, EV = a.edges, ET = a.edgeTris, EDROP = a.edgeDrop, NE = EV.length / 2;
const vpid = a.pid, PN = H.pieceNames;
const FAMILY = (() => { const f = Array.from({ length: 32 }, (_, i) => i); for (const [a_, b_] of CH.family ? CH.family(G) : []) f[a_] = b_; return f; })();     // washes that are one thing to the pen (a jumper and its stripes)
function contours() {
  // candidate edges: silhouettes and open edges, kept where seen. A silhouette of a part over itself (the same wash on
  // both sides) is a line only where the pack says so (inner: 0 no — the face's folds; 1 yes; 2 a thin one — the
  // hair's own spikes and curls over the hair)
  const keep = new Uint8Array(NE), adj = new Map();
  const addAdj = (v, k) => { let l = adj.get(v); if (!l) adj.set(v, l = []); l.push(k); };
  for (let k = 0; k < NE; k++) {
    if (EDROP[k]) continue;
    const f0 = ET[k * 2], f1 = ET[k * 2 + 1];
    const open = f1 === NONE;
    if (!open && facing[f0] === facing[f1]) continue;
    const i = EV[k * 2], j = EV[k * 2 + 1];
    const mx = (scr[i * 3] + scr[j * 3]) / 2, my = (scr[i * 3 + 1] + scr[j * 3 + 1]) / 2, mz = (scr[i * 3 + 2] + scr[j * 3 + 2]) / 2;
    if (!seen(mx, my, mz, open ? 0.004 : 0.006)) continue;
    let cls = 1;
    const inn = Math.min(INNER[i], INNER[j]) === 0 ? 0 : Math.max(INNER[i], INNER[j]);
    if (inn !== 1 && (!open || inn === 2)) {
      const tx = scr[j * 3] - scr[i * 3], ty = scr[j * 3 + 1] - scr[i * 3 + 1], l = Math.hypot(tx, ty) || 1, nx = -ty / l * 3, ny = tx / l * 3;
      const ga = FAMILY[grpAt(mx + nx, my + ny)], gb = FAMILY[grpAt(mx - nx, my - ny)];
      if (ga === gb && ga !== 0) { if (inn === 0) continue; cls = 2; }
    }
    keep[k] = cls; addAdj(i + (cls - 1) * NV, k); addAdj(j + (cls - 1) * NV, k);
  }
  // chains through vertices where exactly two kept edges (of one kind) meet
  const used = new Uint8Array(NE), chains = [];
  const walk = (k0, v0) => {
    const off = (keep[k0] - 1) * NV, vs = [v0]; let k = k0, v = v0;
    while (true) {
      used[k] = 1; const w = EV[k * 2] === v ? EV[k * 2 + 1] : EV[k * 2]; vs.push(w);
      const l = adj.get(w + off); if (!l || l.length !== 2) break;
      const nk = l[0] === k ? l[1] : l[0]; if (used[nk]) break; k = nk; v = w;
    }
    vs.thin = keep[k0] === 2;
    return vs;
  };
  for (const [v, l] of adj) if (l.length !== 2) for (const k of l) if (!used[k]) chains.push(walk(k, v % NV));
  for (let k = 0; k < NE; k++) if (keep[k] && !used[k]) chains.push(walk(k, EV[k * 2]));
  return chains;
}
// a chain of vertices → smoothed picture points; broken where it turns sharply
function chainPts(vs, sharp = false) {
  let P = vs.map(v => [scr[v * 3], scr[v * 3 + 1]]);
  // drop doubles
  P = P.filter((p, i) => i === 0 || Math.hypot(p[0] - P[i - 1][0], p[1] - P[i - 1][1]) > 0.3);
  if (P.length < 2) return [];
  P = resample(P, sharp ? 2.0 : 2.5);
  // the zig-zag of a mesh silhouette goes; a form made of points (spiky hair) keeps them
  for (let it = 0; it < (sharp ? 1 : 4); it++) P = P.map((p, i) => i === 0 || i === P.length - 1 ? p : [(P[i - 1][0] + 2 * p[0] + P[i + 1][0]) / 4, (P[i - 1][1] + 2 * p[1] + P[i + 1][1]) / 4]);
  // break where it turns sharply (a corner in the picture: the pen lifts)
  const out = []; let cur = [P[0]];
  const st = sharp ? 3 : 1;
  for (let i = 1; i < P.length - 1; i++) {
    cur.push(P[i]);
    const i0 = Math.max(0, i - st), i1 = Math.min(P.length - 1, i + st);
    const a0 = Math.atan2(P[i][1] - P[i0][1], P[i][0] - P[i0][0]), a1 = Math.atan2(P[i1][1] - P[i][1], P[i1][0] - P[i][0]);
    let da = Math.abs(a1 - a0); if (da > Math.PI) da = 2 * Math.PI - da;
    if (!sharp && da > 1.0) { out.push(cur); cur = [P[i]]; }
  }
  cur.push(P[P.length - 1]); out.push(cur);
  return out;
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
const len = P => { let s = 0; for (let i = 1; i < P.length; i++) s += Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]); return s; };
// is the line on the figure's outside (paper beyond it on one side)?
function outer(P) {
  let n = 0, o = 0;
  for (let i = 1; i < P.length; i += 3) {
    const tx = P[i][0] - P[i - 1][0], ty = P[i][1] - P[i - 1][1], l = Math.hypot(tx, ty) || 1, nx = -ty / l * 4, ny = tx / l * 4;
    n++; if (depthAt(P[i][0] + nx, P[i][1] + ny) === Infinity || depthAt(P[i][0] - nx, P[i][1] - ny) === Infinity) o++;
  }
  return n ? o / n : 0;
}
// a long line in a few strokes, as a hand draws it: the pen lifts every so often, the next stroke starts a hair off
function strokes(d, P, w, seed, o = {}) {
  const r = K.rng(seed), L = len(P);
  if (L < (o.min ?? 7)) return;
  let s0 = 0; const cum = [0]; for (let i = 1; i < P.length; i++) cum.push(cum[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]));
  while (s0 < L - 4) {
    const seg = (o.seg ? r.uniform(o.seg[0], o.seg[1]) : r.uniform(110, 260)) * d.lw;
    let s1 = Math.min(L, s0 + seg); if (L - s1 < 40 * d.lw) s1 = L;
    const pts = P.filter((_, i) => cum[i] >= s0 && cum[i] <= s1);
    if (pts.length >= 2) {
      const step = o.every ?? Math.max(1, Math.floor(pts.length / Math.max(2, Math.round(len(pts) / 9))));
      const sp = pts.filter((_, i) => i % step === 0 || i === pts.length - 1);
      K.ink(d, sp, { w, start: o.start ?? r.uniform(0.3, 0.7), end: o.end ?? r.uniform(0.05, 0.35), seed: r.int(), jit: o.jit ?? 0.9, retrace: o.retrace ?? 0.3, raw: true });
    }
    s0 = s1 + r.uniform(-3, 5) * d.lw;
  }
}

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
    if (!seen(fsc[k * 3], fsc[k * 3 + 1], fsc[k * 3 + 2], 0.004, 0)) continue;
    fok[k] = 1;
  }
}
function faceMap(x, y, raw = false) {
  const gx = (x - FG.gx[0]) / FG.gx[1], gy = (y - FG.gy[0]) / FG.gy[1];
  const i = Math.floor(gx), j = Math.floor(gy), nx = FG.gx[2];
  if (i < 0 || j < 0 || i >= nx - 1 || j >= FG.gy[2] - 1) return null;
  const u = gx - i, v = gy - j, k00 = j * nx + i, k10 = k00 + 1, k01 = k00 + nx, k11 = k01 + 1;
  if (raw) { if ([k00, k10, k01, k11].some(k => FTRI[k] === NONE)) return null; }
  else if (!(fok[k00] && fok[k10] && fok[k01] && fok[k11])) return null;
  return [0, 1].map(c => (1 - v) * ((1 - u) * fsc[k00 * 3 + c] + u * fsc[k10 * 3 + c]) + v * ((1 - u) * fsc[k01 * 3 + c] + u * fsc[k11 * 3 + c]));
}
// a feature's own frame at (cx, cy): where it is on the turned head, and its axes — the vertical as the head carries
// it, the horizontal foreshortened as the head turns but never below `min` of the vertical (a drawn eye in profile is
// still an eye, as in the drawing's head_side, not a sliver); null when that point of the face is not seen
function seenNear(x, y) {
  const i = Math.round((x - FG.gx[0]) / FG.gx[1]), j = Math.round((y - FG.gy[0]) / FG.gy[1]), nx = FG.gx[2];
  for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) { const k = (j + dj) * nx + i + di; if (k >= 0 && k < NF && fok[k]) return true; }
  return false;
}
function frameAt(d, cx, cy, min = 0.62, raw = false) {
  const c = faceMap(cx, cy, true); if (!c || (!raw && !seenNear(cx, cy))) return null;
  const xl = faceMap(cx - 2, cy, true), xr = faceMap(cx + 2, cy, true), yu = faceMap(cx, cy - 2, true), yd = faceMap(cx, cy + 2, true);
  if (!xl || !xr || !yu || !yd) return null;
  const ay = [(yd[0] - yu[0]) / 4, (yd[1] - yu[1]) / 4], ly = Math.hypot(...ay);
  let ax = [(xr[0] - xl[0]) / 4, (xr[1] - xl[1]) / 4]; const lx = Math.hypot(...ax);
  const r = lx / ly, k = Math.max(r, min) / (r || 1);
  if (lx < 1e-6) ax = [-ay[1], ay[0]]; else ax = [ax[0] * k, ax[1] * k];
  return { c, ax, ay, r };
}
function useFrame(d, f, cx, cy) {
  d.map = null;
  d.T = [[f.ax[0], f.ax[1], f.ay[0], f.ay[1], f.c[0] - f.ax[0] * cx - f.ay[0] * cy, f.c[1] - f.ax[1] * cx - f.ay[1] * cy]];
}
// what the character's own drawing code (char.js) draws with
const FACE = { faceMap, frameAt, useFrame, seenNear, project, K, get fp() { return fp; }, get fig() { return fig; }, I,
  get scr() { return scr; }, seen, pxPerMetre };
function pxPerMetre(z) { return isOrtho ? Hh / (ortho.top - ortho.bottom) : Hh / (2 * Math.tan(persp.fov * Math.PI / 360) * z); }

// ---------------------------------------------------------------- washes from the unseen picture
const mcv = document.createElement('canvas'), mctx = mcv.getContext('2d');
function washes(d) {
  const sc = 0.5, w = Math.ceil(W * sc), h = Math.ceil(Hh * sc);
  const gimg = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const X = Math.min(W - 1, Math.round(x / sc)), Y = Math.min(Hh - 1, Math.round(y / sc));
    gimg[y * w + x] = buf[((Hh - 1 - Y) * W + X) * 4];
  }
  WASHES.forEach((spec, wi) => {
    if (S.show && !S.show.includes(wi)) return;
    const inG = new Uint8Array(32); for (const gid of spec.groups) inG[gid] = 1;
    let x0 = w, y0 = h, x1 = -1, y1 = -1;
    const m = new Uint8Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const v = gimg[y * w + x]; if (!inG[v & 31] || (spec.shade && !(v & 32))) continue;
      m[y * w + x] = 1; if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
    }
    if (x1 < 0) return;
    if (spec.shrink) {       // a shade that keeps away from the part's edge: the mask eaten in by a few pixels
      const r = spec.shrink, m2 = new Uint8Array(m);
      for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) if (m[y * w + x]) {
        for (const [dx, dy] of [[r, 0], [-r, 0], [0, r], [0, -r]]) { const xx = x + dx, yy = y + dy; if (xx < 0 || yy < 0 || xx >= w || yy >= h || !m[yy * w + xx]) { m2[y * w + x] = 0; break; } }
      }
      m.set(m2);
    }
    const pad = 3; x0 = Math.max(0, x0 - pad); y0 = Math.max(0, y0 - pad); x1 = Math.min(w - 1, x1 + pad); y1 = Math.min(h - 1, y1 + pad);
    const bw = x1 - x0 + 1, bh = y1 - y0 + 1;
    mcv.width = bw; mcv.height = bh;
    const im = mctx.createImageData(bw, bh), hx = parseInt(spec.color.slice(1), 16);     // sRGB as written, no conversion
    const R = hx >> 16, Gc = (hx >> 8) & 255, B = hx & 255;
    for (let y = 0; y < bh; y++) for (let x = 0; x < bw; x++) if (m[(y + y0) * w + x + x0]) { const k = (y * bw + x) * 4; im.data[k] = R; im.data[k + 1] = Gc; im.data[k + 2] = B; im.data[k + 3] = 255; }
    mctx.putImageData(im, 0, 0);
    const box = [x0 / sc - origin[0], y0 / sc - origin[1], bw / sc, bh / sc];
    K.washImage(d, mcv.toDataURL(), box, spec.color, spec.op, { seed: wi * 3 + 3 + S.seed, angle: spec.angle ?? (((wi + 1) * 37) % 90) - 45, rough: spec.rough || 'L', dx: (spec.dx || 0) * d.lw, dy: (spec.dy || 0) * d.lw });
  });
}
// the unseen picture, to look at: each wash group its colour, the shaded side darker
function flatPicture() {
  mcv.width = W; mcv.height = Hh; const im = mctx.createImageData(W, Hh);
  for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++) {
    const v = buf[((Hh - 1 - y) * W + x) * 4], gid = v & 31, k = (y * W + x) * 4;
    const c = gid ? (CH.FLAT[Object.keys(G).find(n => G[n] === gid)] || '#888888') : '#fdfaf3', hx = parseInt(c.slice(1), 16), s = gid && (v & 32) ? 0.72 : 1;
    im.data[k] = (hx >> 16) * s; im.data[k + 1] = ((hx >> 8) & 255) * s; im.data[k + 2] = (hx & 255) * s; im.data[k + 3] = 255;
  }
  mctx.putImageData(im, 0, 0);
  return `<img src="${mcv.toDataURL()}" width="${W}" height="${Hh}" style="display:block">`;
}

// ---------------------------------------------------------------- the picture
const stage = document.getElementById('stage');
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
  } else {
    camera = persp; persp.aspect = w / h; persp.fov = c.fov || 24; persp.updateProjectionMatrix(); dist = c.dist;
    persp.position.set(tg[0] + dir[0] * dist, tg[1] + dir[1] * dist, tg[2] + dir[2] * dist);
  }
  camera.lookAt(tg[0], tg[1], tg[2]); camera.updateMatrixWorld();
  isOrtho = c.mode === 'ortho'; camPos = [camera.position.x, camera.position.y, camera.position.z];
  viewDir = normalize([-dir[0], -dir[1], -dir[2]]);
  vm.copy(camera.matrixWorldInverse); mvp.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  U.dn.value = dist - 3; U.df.value = dist + 3;
  // the light, as the hair's darker wash takes it: from above, in front, from the picture's right
  U.L.value.set(0.55, 0.62, 0.56).normalize();          // in the camera's frame, as the shader's normals are
}
let lastSvg = '';
function draw() {
  const w = Math.round(stage.clientWidth || innerWidth), h = Math.round(stage.clientHeight || innerHeight);
  if (w !== W || h !== Hh) { W = w; Hh = h; rt?.dispose(); rt = new THREE.WebGLRenderTarget(W, Hh, { depthBuffer: true }); buf = new Uint8Array(W * Hh * 4); renderer.setSize(W, Hh, false); }
  const T0 = performance.now(), prof = {};
  setCamera(W, Hh);
  normals(); prof.normals = performance.now() - T0;
  renderer.setRenderTarget(rt); renderer.render(scene, camera); renderer.readRenderTargetPixels(rt, 0, 0, W, Hh, buf); renderer.setRenderTarget(null);
  prof.gl = performance.now() - T0;
  // the doc's origin: where the hips are in the picture, so the paper's and pigment's grain travel with her
  origin = [0, 0];
  const hp = new Float32Array(3); const PJ = fig.pose.P; project(PJ[I.Hips * 3], PJ[I.Hips * 3 + 1], PJ[I.Hips * 3 + 2], hp);
  origin = S.cam.follow || S.cam.focus ? [0, 0] : [0, 0];
  if (S.anchorGrain) origin = [Math.round(hp[0]), Math.round(hp[1])];
  projectAll(); faceGrid();
  const d = new K.Doc(W, Hh, S.seed); d.lw = S.lw; d.origin = origin; if (S.fade) d.fade = S.fade;
  prof.proj = performance.now() - T0;
  if (!S.noWash) washes(d);
  prof.wash = performance.now() - T0;
  // contours
  if (!S.noLine) {
    const chains = contours();
    for (const vs of chains) {
      const pid = vpid[vs[0]];
      const sharp = CH.sharp?.includes(PN[pid]);
      for (const P of chainPts(vs, sharp)) {
        let mn = vs[0]; for (const v of vs) if (v < mn) mn = v;
        if (vs.thin) { if (len(P) > (CH.thinMin ?? 9) * d.lw && (!CH.thinEvery || mn % CH.thinEvery === 0)) K.ink(d, P.filter((_, i) => i % 3 === 0 || i === P.length - 1), { w: 0.9, start: 0.5, end: 0.1, jit: 0.5, retrace: 0, seed: mn, raw: true }); continue; }
        const o = outer(P);
        const w = (CH.lineW?.[PN[pid]] ?? 1.8) * (o > 0.5 ? 1.1 : 0.85);
        strokes(d, P, w, (mn >> 4) * 7 + S.seed, { min: (sharp ? 3 : 7) * d.lw, ...(sharp ? { jit: 0.3, retrace: 0, start: 0.7, end: 0.4, seg: [50, 120], every: 2 } : {}) });
      }
    }
    // lines that belong to the form
    for (const st of H.strokes) {
      const runs = []; let cur = [];
      for (const v of st.v) {
        const x = scr[v * 3], y = scr[v * 3 + 1], z = scr[v * 3 + 2];
        const nx = vn[v * 3], ny = vn[v * 3 + 1], nz = vn[v * 3 + 2];
        const fc = isOrtho ? -(nx * viewDir[0] + ny * viewDir[1] + nz * viewDir[2]) : 1;
        if (fc > 0.15 && seen(x, y, z, 0.004, 0)) cur.push([x, y]); else { if (cur.length > 1) runs.push(cur); cur = []; }
      }
      if (cur.length > 1) runs.push(cur);
      for (const r of runs) if (len(r) > 12 * d.lw) K.ink(d, r, { w: st.w, start: 0.3, end: 0.05, jit: st.jit ?? 0.9, seed: st.v[0], retrace: 0, raw: true });
    }
    // marks on the form (a button, a curl), drawn where their vertex is seen and faces us
    for (const mk of H.marks || []) {
      const v = mk.v, x = scr[v * 3], y = scr[v * 3 + 1], z = scr[v * 3 + 2];
      const fc = -(vn[v * 3] * viewDir[0] + vn[v * 3 + 1] * viewDir[1] + vn[v * 3 + 2] * viewDir[2]);
      if (!(fc > (mk.min ?? 0.3) && seen(x, y, z, 0.004, 0))) continue;
      const ppu = pxPerMetre(z) * H.units;          // picture pixels a drawing unit, there
      if (mk.kind === 'button') { const s = (mk.r ?? 4) * ppu; K.ink(d, [[x - s, y], [x, y - s * 0.8], [x + s, y], [x, y + s * 0.9], [x - s, y]], { w: 1.0, retrace: 0, seed: v, raw: true }); }
      else if (mk.kind === 'curl') K.curl(d, x, y, mk.r * ppu, mk.rot, { w: mk.w ?? 1.0, seed: v, raw: true });
    }
    prof.lines = performance.now() - T0;
    CH.drawFace(d, FACE);
    if (S.props && CH.props) CH.props(d, FACE, S.props);
    if (S.debugFace) for (let k = 0; k < NF; k++) if (FTRI[k] !== NONE) d.inks.push(`<circle cx="${fsc[k * 3].toFixed(1)}" cy="${fsc[k * 3 + 1].toFixed(1)}" r="0.8" fill="${fok[k] ? '#0a0' : '#c00'}"/>`);
  }
  prof.face = performance.now() - T0;
  lastSvg = S.flat ? flatPicture() : K.svg(d);
  stage.innerHTML = lastSvg;
  prof.dom = performance.now() - T0; A.prof = prof;
}

function facingYaw() { const qh = getQ(fig.pose.Q, I.Hips); const x = 2 * (qh[0] * qh[2] + qh[1] * qh[3]), z = 1 - 2 * (qh[0] * qh[0] + qh[1] * qh[1]); return Math.atan2(x, z); }
window.A = {
  H, body, fig, sk, face, S, facing: facingYaw, clipInfo: () => clip && { frames: clip.frames, fps: clip.fps }, svg: () => lastSvg,
  async set(o) {
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; face.setHead(clip ? headTrack(clip) : null); }
      S.clip = !!ids;
    }
    for (const k of ['t', 'pose', 'poseOpts', 'push', 'lw', 'fade', 'seed', 'show', 'noWash', 'noLine', 'anchorGrain', 'debugFace', 'props', 'flat']) if (o[k] !== undefined) S[k] = o[k];
    if (o.time !== undefined) S.time = o.time; else if (o.t !== undefined && clip && !S.liveClock) S.time = o.t / clip.fps;
    if (o.liveClock !== undefined) S.liveClock = o.liveClock;
    if (o.still !== undefined) face.still = o.still;
    if (o.exprTrack) { face.exprKeys = [{ t: -10, w: { [CH.NAMES[0]]: 1 } }]; for (const [t, w] of o.exprTrack) face.setExpr(t, typeof w === 'string' ? { [w]: 1 } : w); }
    if (o.expr) face.setExpr(S.time, typeof o.expr === 'string' ? { [o.expr]: 1 } : o.expr);
    if (o.talk !== undefined) { face.talk(o.talk ? (o.talkFrom ?? S.time) : null); face.talkTo = o.talkTo ?? null; }
    if (o.cam) Object.assign(S.cam, o.cam);
    frame();
  },
  render() { draw(); },
};
await window.A.set({});
window.A.render();
window.__ready = true;

if (!q.has('pack')) (await import('./ui.js')).ui(window.A, stage);
