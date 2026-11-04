// Аня in 3D, flat graphic style: the character pack (tools/build.py) on the engine's skeleton, skinning and Kimodo
// retargeting; drawn with flat colour, one stepped shade, a coloured outline (inverted hull) and the face drawn live
// on a canvas from the drawing's own parts (face.js), projected from the front.
//   view.html — by hand (ui.js); view.html?pack=<url> — driven by tools/shots.mjs
//   window.A.set({clip, t, time, pose, expr, exprMix, exprAt, talk, talkFrom, cam, …}) then A.render()
import * as THREE from 'three';
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { normalsOf } from '../../../../engine/src/skin.js';
import { qAxisAngle, qBetween, qRot, getQ, getV, normalize, sub } from '../../../../engine/src/math.js';
import { LiveFace, draw as drawFace, X0, X1, Y0, Y1, PX, EXPR_NAMES } from './face.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack') || '../../data/anya.json', location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const sk = E.skeleton;

// the pack as an engine body: positions, triangles, skin, joints and frames (SOMA's), nothing else asked of it
const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const rest = Float32Array.from(a.positions);
const spec = { skinning: { method: H.skinning || 'cor', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
// expressions as shape changes (morphs) on the rest, before skinning: {name: Float32Array N×3}
const morphs = {};
for (const k of Object.keys(a)) if (k.startsWith('morph_')) morphs[k.slice(6)] = a[k];

// ---------------------------------------------------------------- the stage
const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
scene.background = new THREE.Color(q.get('bg') || '#f1e6d6');

const g = new THREE.BufferGeometry();
g.setAttribute('position', new THREE.BufferAttribute(fig.positions, 3));
g.setAttribute('normal', new THREE.BufferAttribute(fig.normals, 3));
g.setAttribute('col', new THREE.BufferAttribute(a.col, 3, true));
g.setAttribute('shd', new THREE.BufferAttribute(a.shd, 3, true));
g.setAttribute('lin', new THREE.BufferAttribute(a.lin, 3, true));
g.setAttribute('ow', new THREE.BufferAttribute(a.ow, 1, true));
g.setAttribute('uv', new THREE.BufferAttribute(a.uv, 2));
g.setAttribute('tex', new THREE.BufferAttribute(a.tex, 1));
g.setAttribute('pn', new THREE.BufferAttribute(a.pn, 3));
g.setAttribute('pw', new THREE.BufferAttribute(a.pw, 1, true));
g.setAttribute('pj', new THREE.BufferAttribute(a.pj, 1));
g.setAttribute('two', new THREE.BufferAttribute(a.two, 1));
g.setAttribute('band', new THREE.BufferAttribute(a.band, 1));
g.setIndex(new THREE.BufferAttribute(a.triangles, 1));

// the face's drawn layer: a canvas drawn every frame (face.js)
const faceCanvas = document.createElement('canvas');
faceCanvas.width = (X1 - X0) * PX; faceCanvas.height = (Y1 - Y0) * PX;
const faceCtx = faceCanvas.getContext('2d');
const faceTex = new THREE.CanvasTexture(faceCanvas);
faceTex.colorSpace = THREE.NoColorSpace; faceTex.anisotropy = 8;
faceTex.premultiplyAlpha = true;      // filtered premultiplied: no dark fringe where the painting ends
const face = new LiveFace(Number(q.get('seed') ?? 7));
const U = {
  L: { value: new THREE.Vector3(0.55, 0.62, 0.56).normalize() },
  thr: { value: Number(q.get('thr') ?? -0.18) },
  face: { value: faceTex },
  width: { value: Number(q.get('line') ?? 0.0028) },
  paint: { value: 1 }, clay: { value: 0 },
  R: { value: Array.from({ length: sk.J }, () => new THREE.Matrix3()) },
};
const toon = new THREE.ShaderMaterial({
  uniforms: U,
  vertexShader: `
    attribute vec3 col; attribute vec3 shd; attribute float tex; attribute vec3 pn; attribute float pw; attribute float pj; attribute float two; attribute float band; varying float vBand;
    uniform mat3 R[${sk.J}];
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec2 vUv; varying float vTex; varying float vTwo; varying float vPw;
    void main() { vBand = band; vPw = pw; vN = normalize(mix(normal, R[int(pj + 0.5)] * pn, pw)); vCol = col; vShd = shd; vUv = uv; vTex = tex; vTwo = two;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `
    uniform vec3 L; uniform float thr; uniform sampler2D face; uniform float paint; uniform float clay;
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec2 vUv; varying float vTex; varying float vTwo; varying float vPw; varying float vBand;
    void main() {
      if (!gl_FrontFacing) { if (vTwo < 0.5) discard; gl_FragColor = vec4(vShd * 0.92, 1.0); return; }
      float d = dot(normalize(vN), L);
      float th = thr - 0.22 * vPw; float lit = smoothstep(th - 0.015, th + 0.015, d);
      vec3 base = vCol, sh = vShd;
      // the legs: the shoe and the sock cut at the drawing's heights (shoe top 0.06 m, sock top 0.134 m)
      if (vBand > -0.5) { if (vBand < 0.06) { base = vec3(0.42, 0.227, 0.165); sh = vec3(0.333, 0.188, 0.122); }
        else if (vBand < 0.134) { base = vec3(0.965, 0.933, 0.886); sh = vec3(0.886, 0.839, 0.769); } }
      vec3 c = mix(sh, base, lit);
      if (clay > 0.5) c = vec3(0.86, 0.84, 0.8) * (0.55 + 0.45 * max(d, 0.0)) + 0.08;
      if (vTex > 0.5 && paint > 0.5) { vec4 t = texture2D(face, vUv); c = c * (1.0 - t.a) + t.rgb; }
      gl_FragColor = vec4(c, 1.0);
    }`,
  side: THREE.DoubleSide,
});
const hull = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.BackSide,
  vertexShader: `
    attribute vec3 lin; attribute float ow; uniform float width; varying vec3 vC; varying float vOw;
    void main() { vC = lin; vOw = ow; gl_Position = projectionMatrix * modelViewMatrix * vec4(position + normal * width * ow, 1.0);
      gl_Position.z += 0.0004 * gl_Position.w; }`,
  fragmentShader: `varying vec3 vC; varying float vOw; void main() { if (vOw < 0.35) discard; gl_FragColor = vec4(vC, 1.0); }`,
});
const mesh = new THREE.Mesh(g, toon), line = new THREE.Mesh(g, hull);
mesh.frustumCulled = line.frustumCulled = false;
scene.add(mesh, line);
// a soft round shadow on the floor, as in the drawing
const shadow = new THREE.Mesh(new THREE.CircleGeometry(0.26, 48), new THREE.MeshBasicMaterial({ color: '#000', transparent: true, opacity: 0.1, depthWrite: false }));
shadow.rotation.x = -Math.PI / 2; shadow.scale.set(1, 0.6, 1); shadow.position.y = 0.0005; scene.add(shadow);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshBasicMaterial({ color: q.get('floor') || '#e6d6bf' }));
floor.rotation.x = -Math.PI / 2; floor.visible = q.has('floor'); scene.add(floor);

const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 100);
const persp = new THREE.PerspectiveCamera(24, 1, 0.05, 200);
let camera = ortho;

// ---------------------------------------------------------------- poses
const J = sk.J, I = sk.index;
// standing as drawn: the rest with the arms let down along the body (a pose layer, for the drawing's views)
function standPose(o = {}) {
  const pose = fig.restPose();
  const out = o.out ?? 0.13, fwd = o.fwd ?? 0.03;
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    const A = I[s + 'Arm'], Hd = I[s + 'Hand'];
    const cur = normalize(sub(getV(pose.P, Hd), getV(pose.P, A)));
    turnUnder(pose, sk, A, qBetween(cur, normalize([sg * out, -1, fwd])));
    build(pose, body, getV(pose.P, I.Hips));
    if (o.twist) turnUnder(pose, sk, A, qAxisAngle(normalize(sub(getV(pose.P, Hd), getV(pose.P, A))), sg * o.twist));
    build(pose, body, getV(pose.P, I.Hips));
  }
  return pose;
}

const S = { clip: null, clipIds: null, t: 0, time: 0, pose: 'stand', morph: {}, push: true,
  cam: { mode: 'ortho', yaw: 0, pitch: 0, cx: 0, cy: 0.81, h: 1.75, dist: 6, target: null, follow: false } };
let clip = null;
function applyMorphs() {
  const P = body.positions; P.set(rest);
  for (const [k, w] of Object.entries(S.morph)) { const m = morphs[k]; if (!m || !w) continue; for (let i = 0; i < P.length; i++) P[i] += w * m[i]; }
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
// the skirt kept off the legs: each skirt point inside a leg's capsule (thigh, shin) is put on its surface
const dressR = H.pieces.dress, skirt = [];
for (let i = dressR[0]; i < dressR[1]; i++) if (rest[i * 3 + 1] < 0.62) skirt.push(i);
const CAPS = [['LeftLeg', 'LeftShin', 0.06], ['LeftShin', 'LeftFoot', 0.048], ['RightLeg', 'RightShin', 0.06], ['RightShin', 'RightFoot', 0.048]]
  .map(([a, b, r]) => [I[a], I[b], r]);
function pushSkirt(P, pose) {
  const caps = CAPS.map(([a, b, r], k) => { const A = getV(pose.P, a), B = getV(pose.P, b); return [k % 2 ? A : A.map((v, c) => (v + B[c]) / 2), B, r]; });
  for (const i of skirt) {
    let x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
    for (const [A, B, r] of caps) {
      const ab = [B[0] - A[0], B[1] - A[1], B[2] - A[2]], l2 = ab[0] ** 2 + ab[1] ** 2 + ab[2] ** 2;
      let u = ((x - A[0]) * ab[0] + (y - A[1]) * ab[1] + (z - A[2]) * ab[2]) / l2; u = Math.max(0, Math.min(1, u));
      const cx = A[0] + ab[0] * u, cy = A[1] + ab[1] * u, cz = A[2] + ab[2] * u, dx = x - cx, dy = y - cy, dz = z - cz, d = Math.hypot(dx, dy, dz);
      if (d < r && d > 1e-6) { const k = r / d; x = cx + dx * k; y = cy + dy * k; z = cz + dz * k; }
    }
    P[i * 3] = x; P[i * 3 + 1] = y; P[i * 3 + 2] = z;
  }
}
function frame() {
  applyMorphs();
  const fp = face.at(S.time, { headT: S.clip ? S.t / clip.fps : null });
  drawFace(faceCtx, fp); faceTex.needsUpdate = true;
  let pose;
  if (S.clip) { pose = fig.retarget.pose(clip.sample(S.t, fig.sample)); fig.retarget.placed(pose); }
  else if (S.pose === 'raw') pose = null;
  else pose = S.pose === 'rest' ? fig.restPose() : standPose(S.poseOpts || {});
  if (!pose) { fig.positions.set(body.positions); fig.pose = fig.restPose(); }
  else {
    // the jaw opens a little with the drawn mouth
    if (fp.jaw > 0) turnUnder(pose, sk, I.Jaw, qAxisAngle(qRot(getQ(pose.Q, I.Head), [1, 0, 0]), fp.jaw * 0.11));
    fig.skinner.skin(pose, fig.positions);
    if (S.clip) {          // on the floor as the engine's Figure does (motion.floor 'lowest')
      const P = fig.positions; let lo = Infinity; for (let i = 1; i < P.length; i += 3) if (P[i] < lo) lo = P[i];
      const shift = pose.floor - lo; for (let i = 1; i < P.length; i += 3) P[i] += shift; for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
    }
    if (S.push) pushSkirt(fig.positions, pose);
    fig.pose = pose;
  }
  normalsOf(fig.positions, body.triangles, fig.normals);
  g.attributes.position.needsUpdate = true; g.attributes.normal.needsUpdate = true;
  const Q = fig.pose.Q;
  for (let j = 0; j < J; j++) { const [x, y, z, w] = [Q[j * 4], Q[j * 4 + 1], Q[j * 4 + 2], Q[j * 4 + 3]];
    U.R.value[j].set(1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)); }
  const P = fig.pose.P; shadow.position.x = P[I.Hips * 3]; shadow.position.z = P[I.Hips * 3 + 2];
}
function facing() { // where the pelvis faces now (yaw about y; 0 — +z)
  const qh = getQ(fig.pose.Q, I.Hips);
  const x = 2 * (qh[0] * qh[2] + qh[1] * qh[3]), z = 1 - 2 * (qh[0] * qh[0] + qh[1] * qh[1]);
  return Math.atan2(x, z);
}

window.A = {
  H, body, fig, sk, facing, face, S, EXPR_NAMES, clipInfo: () => clip && { frames: clip.frames, fps: clip.fps },
  async set(o) {
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; face.setHead(clip ? headTrack(clip) : null); }
      S.clip = !!ids;
    }
    for (const k of ['t', 'pose', 'poseOpts', 'morph', 'push']) if (o[k] !== undefined) S[k] = o[k];
    // the face's clock (seconds): given, or the clip's time
    if (o.time !== undefined) S.time = o.time; else if (o.t !== undefined && clip && !S.liveClock) S.time = o.t / clip.fps;
    if (o.liveClock !== undefined) S.liveClock = o.liveClock;
    if (o.exprTrack) { face.exprKeys = [{ t: -10, w: { dream: 1 } }]; for (const [t, w] of o.exprTrack) face.setExpr(t, typeof w === 'string' ? { [w]: 1 } : w); }
    if (o.expr) face.setExpr(S.time, typeof o.expr === 'string' ? { [o.expr]: 1 } : o.expr);
    if (o.talk !== undefined) { face.talk(o.talk ? (o.talkFrom ?? S.time) : null); face.talkTo = o.talkTo ?? null; }
    if (o.cam) Object.assign(S.cam, o.cam);
    if (o.light) S.light = o.light;
    if (o.thr !== undefined) U.thr.value = o.thr;
    if (o.width !== undefined) U.width.value = o.width;
    if (o.bg) scene.background = new THREE.Color(o.bg);
    if (o.floor !== undefined) { floor.visible = !!o.floor; if (o.floor) floor.material.color.set(o.floor); }
    if (o.shadow !== undefined) shadow.visible = o.shadow;
    if (o.show !== undefined) {           // only these pieces (names from the pack's header), or all
      const all = a.triangles; let idx = all;
      if (o.show) { const parts = []; for (const n of o.show) { const [s0, s1] = H.trianglePieces[n]; parts.push(all.subarray(s0 * 3, s1 * 3)); }
        idx = new Uint32Array(parts.reduce((k, p) => k + p.length, 0)); let k = 0; for (const p of parts) { idx.set(p, k); k += p.length; } }
      g.setIndex(new THREE.BufferAttribute(idx, 1));
    }
    if (o.paint !== undefined) U.paint.value = o.paint ? 1 : 0;
    if (o.flat !== undefined) U.clay.value = o.flat ? 1 : 0;
    frame();
  },
  frames: () => clip ? clip.frames : 0,
  render() {
    const w = canvas.clientWidth, h = canvas.clientHeight; renderer.setSize(w, h, false);
    const c = S.cam, cp = Math.cos(c.pitch);
    let tg = c.target || [c.cx, c.cy, 0];
    if (c.follow && fig.pose) { const P = fig.pose.P; tg = [P[I.Hips * 3], c.cy, P[I.Hips * 3 + 2]]; }
    if (c.focus && fig.pose) { const P = fig.pose.P, k = I[c.focus]; tg = [P[k * 3], P[k * 3 + 1] + (c.up || 0), P[k * 3 + 2]]; }
    const dir = [Math.sin(c.yaw) * cp, Math.sin(c.pitch), Math.cos(c.yaw) * cp];
    if (c.mode === 'ortho') {
      camera = ortho; const hh = c.h / 2, ww = hh * w / h;
      Object.assign(ortho, { left: -ww, right: ww, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
      ortho.position.set(tg[0] + dir[0] * 20, tg[1] + dir[1] * 20, tg[2] + dir[2] * 20);
    } else {
      camera = persp; persp.aspect = w / h; persp.fov = c.fov || 24; persp.updateProjectionMatrix();
      persp.position.set(tg[0] + dir[0] * c.dist, tg[1] + dir[1] * c.dist, tg[2] + dir[2] * c.dist);
    }
    camera.lookAt(tg[0], tg[1], tg[2]);
    // the light as in the drawing: from above, in front, from the picture's right
    camera.updateMatrixWorld();
    const e = camera.matrixWorld.elements, l = S.light || [0.55, 0.62, 0.56];
    U.L.value.set(e[0] * l[0] + e[4] * l[1] + e[8] * l[2], e[1] * l[0] + e[5] * l[1] + e[9] * l[2], e[2] * l[0] + e[6] * l[1] + e[10] * l[2]).normalize();
    renderer.render(scene, camera);
  },
};
await window.A.set({});
window.A.render();
window.__ready = true;

if (!q.has('pack')) (await import('./ui.js')).ui(window.A, canvas);
