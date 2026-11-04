// Аня in 3D, Ghibli style: the character pack (tools/build.py) on the engine's skeleton, skinning and Kimodo
// retargeting; drawn as a cel: flat colour, one shade tone of a warm multiply with a hard edge (the light from the
// picture's upper left, as in the drawing), one even dark-brown outline (inverted hull), and the face drawn live on a
// canvas from the drawing's own face parts (face.js), projected from the front.
//   view.html — by hand (ui.js); view.html?pack=<url> — driven by tools/shots.mjs
//   window.A.set({clip, t, time, pose, expr, exprTrack, talk, talkFrom, cam, …}) then A.render()
import * as THREE from 'three';
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { normalsOf } from '../../../../engine/src/skin.js';
import { qAxisAngle, qBetween, qRot, getQ, getV, normalize, sub } from '../../../../engine/src/math.js';
import { LiveFace, draw as drawFace, EXPR_NAMES } from './face.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack') || '../../data/anya.json', location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const sk = E.skeleton;

const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const rest = Float32Array.from(a.positions);
const spec = { skinning: { method: H.skinning || 'cor', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });

// ---------------------------------------------------------------- the stage
const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Number(q.get('dpr') || 1));
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
scene.background = new THREE.Color(q.get('bg') || '#efe6d4');

const g = new THREE.BufferGeometry();
g.setAttribute('position', new THREE.BufferAttribute(fig.positions, 3));
g.setAttribute('normal', new THREE.BufferAttribute(fig.normals, 3));
for (const [k, n, norm] of [['col', 3, true], ['shd', 3, true], ['lin', 3, true], ['ow', 1, true], ['uv', 2, false], ['tex', 1, false],
  ['pn', 3, false], ['pw', 1, true], ['pj', 1, false], ['two', 1, false], ['band', 1, false], ['ob', 1, false]])
  g.setAttribute(k, new THREE.BufferAttribute(a[k], n, norm));
g.setIndex(new THREE.BufferAttribute(a.triangles, 1));

// the face's drawn layer: a canvas drawn every frame (face.js), head-local box from the pack
const FB = H.face, PX = 340;
const faceCanvas = document.createElement('canvas');
faceCanvas.width = Math.round((FB.x1 - FB.x0) * PX); faceCanvas.height = Math.round((FB.y1 - FB.y0) * PX);
const faceCtx = faceCanvas.getContext('2d');
const faceTex = new THREE.CanvasTexture(faceCanvas);
faceTex.colorSpace = THREE.NoColorSpace;      // premultiplied sRGB: decoded in the shader after un-premultiplying faceTex.anisotropy = 8;
faceTex.premultiplyAlpha = true;
const face = new LiveFace(Number(q.get('seed') ?? 7));
const U = {
  L: { value: new THREE.Vector3(-0.5, 0.55, 0.65).normalize() },
  thr: { value: Number(q.get('thr') ?? 0.0) },
  face: { value: faceTex },
  width: { value: Number(q.get('line') ?? 0.0032) },
  paint: { value: 1 }, clay: { value: 0 }, shoe: { value: new THREE.Vector3(0.42, 0.275, 0.196) }, shoeS: { value: new THREE.Vector3(0.361, 0.215, 0.165) },
  R: { value: Array.from({ length: sk.J }, () => new THREE.Matrix3()) },
};
const srgb = c => new THREE.Color().setRGB(c[0] / 255, c[1] / 255, c[2] / 255, THREE.SRGBColorSpace);
// vertex colours are the drawing's sRGB hexes: turned linear here so they come out on screen exactly as drawn
for (const k of ['col', 'shd', 'lin']) {
  const src = a[k], f = new Float32Array(src.length);
  for (let i = 0; i < src.length; i += 3) { const c = srgb([src[i], src[i + 1], src[i + 2]]); f[i] = c.r; f[i + 1] = c.g; f[i + 2] = c.b; }
  g.setAttribute(k, new THREE.BufferAttribute(f, 3));
}
{ const s = srgb([0x6b, 0x46, 0x32]), d = srgb([0x5c, 0x37, 0x2a]); U.shoe.value.set(s.r, s.g, s.b); U.shoeS.value.set(d.r, d.g, d.b); }
const toon = new THREE.ShaderMaterial({
  uniforms: U,
  vertexShader: `
    attribute vec3 col; attribute vec3 shd; attribute float tex; attribute vec3 pn; attribute float pw; attribute float pj; attribute float two; attribute float band;
    uniform mat3 R[${sk.J}];
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec2 vUv; varying float vTex; varying float vTwo; varying float vPw; varying float vBand;
    void main() { vBand = band; vPw = pw; vN = normalize(mix(normal, R[int(pj + 0.5)] * pn, pw)); vCol = col; vShd = shd; vUv = uv; vTex = tex; vTwo = two;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `
    uniform vec3 L; uniform float thr; uniform sampler2D face; uniform float paint; uniform float clay; uniform vec3 shoe; uniform vec3 shoeS;
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec2 vUv; varying float vTex; varying float vTwo; varying float vPw; varying float vBand;
    void main() {
      if (!gl_FrontFacing && vTwo < 0.5) discard;
      float d = dot(normalize(vN), L);
      float lit = smoothstep(thr - 0.012, thr + 0.012, d);
      vec3 base = vCol, sh = vShd;
      if (vBand > -0.5 && vBand < 0.0) { base = shoe; sh = shoeS; }
      vec3 c = mix(sh, base, lit);
      if (clay > 0.5) c = vec3(0.86, 0.84, 0.8) * (0.55 + 0.45 * max(d, 0.0)) + 0.08;
      if (vTex > 0.5 && paint > 0.5) { vec4 t = texture2D(face, vUv); if (t.a > 0.002) { vec3 s = t.rgb / t.a; s = mix(s / 12.92, pow((s + 0.055) / 1.055, vec3(2.4)), step(0.04045, s)); c = mix(c, s, t.a); } }
      gl_FragColor = vec4(c, 1.0);
      #include <colorspace_fragment>
    }`,
  side: THREE.DoubleSide,
});
// the outline: the hull pushed out along the normals, drawn from behind; 'ob' moves it back from the camera (hair: the
// locks' own edges over the hair mass are not drawn, only where the hair ends against something further)
const hull = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.BackSide,
  vertexShader: `
    attribute vec3 lin; attribute float ow; attribute float ob; uniform float width; varying vec3 vC; varying float vOw;
    void main() { vC = lin; vOw = ow; vec4 mv = modelViewMatrix * vec4(position + normal * width * ow, 1.0); mv.z -= ob + 0.002;
      gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `varying vec3 vC; varying float vOw; void main() { if (vOw < 0.35) discard; gl_FragColor = vec4(vC, 1.0);
      #include <colorspace_fragment>
    }`,
});
const mesh = new THREE.Mesh(g, toon), line = new THREE.Mesh(g, hull);
mesh.frustumCulled = line.frustumCulled = false;
scene.add(mesh, line);
const shadow = new THREE.Mesh(new THREE.CircleGeometry(0.26, 48), new THREE.MeshBasicMaterial({ color: '#2a3a20', transparent: true, opacity: 0.22, depthWrite: false }));
shadow.rotation.x = -Math.PI / 2; shadow.scale.set(1, 0.4, 1); shadow.position.y = 0.0005; scene.add(shadow);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshBasicMaterial({ color: q.get('floor') || '#d9cdb4' }));
floor.rotation.x = -Math.PI / 2; floor.visible = q.has('floor'); scene.add(floor);

const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 100);
const persp = new THREE.PerspectiveCamera(24, 1, 0.05, 200);
let camera = ortho;

// ---------------------------------------------------------------- poses
const J = sk.J, I = sk.index;
// the drawing's 'stand' pose (styles/s7-ghibli/tools/anya.py POSES.stand): upper arm, forearm, hand directions
// (the drawing paints the hands over the skirt; in 3D they hang just outside it: the arms a little more out)
const STAND = { upper: [0.13, -1, 0.02], fore: [0.2, -1, 0.14], hand: [0.08, -1, 0.1] };
function aim(pose, j, child, dir) {
  const cur = normalize(sub(getV(pose.P, child), getV(pose.P, j)));
  turnUnder(pose, sk, j, qBetween(cur, normalize(dir)));
  build(pose, body, getV(pose.P, I.Hips));
}
// the hand as the drawing's relaxed hand (a pose layer on top of any motion): fingers together and a little bent
// toward the palm (Anny's rest has them spread straight)
const FINGERS = ['Index', 'Middle', 'Ring', 'Pinky'];
const V3 = (p, j) => getV(p.P, j);
const cross3 = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const dot3 = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
function relaxHands(pose, k = 1) {
  const re = () => build(pose, body, getV(pose.P, I.Hips));
  for (const s of ['Left', 'Right']) {
    const J_ = n => I[`${s}Hand${n}`];
    // which side the palm is: where the thumb lies off the plane of the knuckles
    const dirM = normalize(sub(V3(pose, J_('Middle2')), V3(pose, J_('Middle1'))));
    const across = normalize(sub(V3(pose, J_('Index1')), V3(pose, J_('Pinky1'))));
    let palm = sub(V3(pose, J_('ThumbEnd')), V3(pose, J_('Middle1')));
    palm = normalize(sub(sub(palm, dirM.map(v => v * dot3(palm, dirM))), across.map(v => v * dot3(palm, across))));
    // together: each finger's base turned toward the middle finger's direction
    for (const f of ['Index', 'Ring', 'Pinky']) {
      const d = normalize(sub(V3(pose, J_(f + '2')), V3(pose, J_(f + '1'))));
      const tg = normalize(d.map((v, i) => v * 0.25 + dirM[i] * 0.75));
      turnUnder(pose, sk, J_(f + '1'), qBetween(d, tg)); re();
    }
    // bent toward the palm, a little more at the middle joints
    for (const f of FINGERS) for (const [n, ang] of [[1, 0.35], [2, 0.45], [3, 0.3]]) {
      const j = J_(f + n), c = I[`${s}Hand${f}${n + 1}`] ?? J_(f + 'End');
      const d = normalize(sub(V3(pose, c), V3(pose, j)));
      const ax = normalize(cross3(d, palm));
      turnUnder(pose, sk, j, qAxisAngle(ax, ang * k)); re();
    }
    { const j = J_('Thumb2'), d = normalize(sub(V3(pose, J_('Thumb3')), V3(pose, j)));
      turnUnder(pose, sk, j, qAxisAngle(normalize(cross3(d, palm)), 0.25 * k)); re(); }
  }
}
// the palm turned toward the thigh, as drawn (palm (−1, 0, 0.2) for the left hand, mirrored)
function palmIn(pose, s, sg) {
  const J_ = n => I[`${s}Hand${n}`], H_ = I[s + 'Hand'];
  const ax = normalize(sub(V3(pose, J_('Middle1')), V3(pose, H_)));
  const across = normalize(sub(V3(pose, J_('Index1')), V3(pose, J_('Pinky1'))));
  let palm = sub(V3(pose, J_('ThumbEnd')), V3(pose, J_('Middle1')));
  palm = normalize(sub(sub(palm, ax.map(v => v * dot3(palm, ax))), across.map(v => v * dot3(palm, across))));
  let want = [-sg, 0, 0.25]; want = normalize(sub(want, ax.map(v => v * dot3(want, ax))));
  const ang = Math.atan2(dot3(cross3(palm, want), ax), dot3(palm, want));
  turnUnder(pose, sk, H_, qAxisAngle(ax, ang)); build(pose, body, getV(pose.P, I.Hips));
}
function standPose() {
  const pose = fig.restPose();
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    const m = v => [v[0] * sg, v[1], v[2]];
    aim(pose, I[s + 'Arm'], I[s + 'ForeArm'], m(STAND.upper));
    aim(pose, I[s + 'ForeArm'], I[s + 'Hand'], m(STAND.fore));
    aim(pose, I[s + 'Hand'], I[s + 'HandMiddle1'], m(STAND.hand));
    palmIn(pose, s, sg);
  }
  return pose;
}

const S = { clip: null, clipIds: null, t: 0, time: 0, pose: 'stand', push: true, relax: 1,
  cam: { mode: 'ortho', yaw: 0, pitch: 0, cx: 0, cy: 0.84, h: 1.8, dist: 6, target: null, follow: false } };
let clip = null;
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
// the skirt kept off the legs: each skirt point inside a leg's capsule (thigh, shin) goes to its surface; the push is
// spread over the cloth around (no dents where single points moved)
const skR = H.pieces.skirt, skirt = [];
for (let i = skR[0]; i < skR[1]; i++) if (rest[i * 3 + 1] < 0.86) skirt.push(i);
const skIdx = new Int32Array(rest.length / 3).fill(-1); skirt.forEach((i, k) => { skIdx[i] = k; });
const skNb = skirt.map(() => new Set());
{ const T = a.triangles; for (let t = H.trianglePieces.skirt[0]; t < H.trianglePieces.skirt[1]; t++) for (let e = 0; e < 3; e++) {
  const u = skIdx[T[t * 3 + e]], v = skIdx[T[t * 3 + (e + 1) % 3]]; if (u >= 0 && v >= 0) { skNb[u].add(v); skNb[v].add(u); } } }
const skNbA = skNb.map(s => [...s]);
const CAPS = [['LeftLeg', 'LeftShin', 0.068], ['LeftShin', 'LeftFoot', 0.05], ['RightLeg', 'RightShin', 0.068], ['RightShin', 'RightFoot', 0.05]].map(([p, c, r]) => [I[p], I[c], r]);
const fade = Float64Array.from(skirt, i => { const u = Math.max(0, Math.min(1, (0.86 - rest[i * 3 + 1]) / 0.2)); return u * u * (3 - 2 * u); });
const dsp = new Float64Array(skirt.length * 3), dsp2 = new Float64Array(skirt.length * 3);
function pushSkirt(Pp, pose) {
  const caps = CAPS.map(([p, c, r], k) => { const A = getV(pose.P, p), B = getV(pose.P, c); return [k % 2 ? A : A.map((v, i) => (v + B[i]) / 2), B, r + 0.008]; });
  skirt.forEach((i, k) => {
    let x = Pp[i * 3], y = Pp[i * 3 + 1], z = Pp[i * 3 + 2];
    for (const [A, B, r] of caps) {
      const ab = [B[0] - A[0], B[1] - A[1], B[2] - A[2]], l2 = ab[0] ** 2 + ab[1] ** 2 + ab[2] ** 2;
      let u = ((x - A[0]) * ab[0] + (y - A[1]) * ab[1] + (z - A[2]) * ab[2]) / l2; u = Math.max(0, Math.min(1, u));
      const cx = A[0] + ab[0] * u, cy = A[1] + ab[1] * u, cz = A[2] + ab[2] * u, dx = x - cx, dy = y - cy, dz = z - cz, d = Math.hypot(dx, dy, dz);
      if (d < r && d > 1e-6) { const s = r / d; x = cx + dx * s; y = cy + dy * s; z = cz + dz * s; }
    }
    dsp[k * 3] = x - Pp[i * 3]; dsp[k * 3 + 1] = y - Pp[i * 3 + 1]; dsp[k * 3 + 2] = z - Pp[i * 3 + 2];
  });
  for (let it = 0; it < 8; it++) {
    skNbA.forEach((nb, k) => { for (let c = 0; c < 3; c++) { let s = dsp[k * 3 + c]; for (const m of nb) s += dsp[m * 3 + c]; dsp2[k * 3 + c] = s / (nb.length + 1); } });
    for (let k = 0; k < skirt.length; k++) for (let c = 0; c < 3; c++) { const x = dsp[k * 3 + c], y = dsp2[k * 3 + c]; dsp[k * 3 + c] = Math.abs(y) > Math.abs(x) ? y : (x + y) / 2 + (x - y) / 4; }
  }
  skirt.forEach((i, k) => { const w = fade[k]; Pp[i * 3] += w * dsp[k * 3]; Pp[i * 3 + 1] += w * dsp[k * 3 + 1]; Pp[i * 3 + 2] += w * dsp[k * 3 + 2]; });
}
// the face's line width follows how big the head is on screen (the drawing draws its lines one width in pixels)
let pxPerM = 500;
function frame() {
  const E_ = face.at(S.time, { headT: S.clip ? S.t / clip.fps : null });
  const lw = Math.max(0.014, Math.min(0.045, 2.1 / (pxPerM * 0.12)));
  drawFace(faceCtx, E_, FB, PX, { lw, shadow: FB.shadow });
  faceTex.needsUpdate = true;
  let pose;
  if (S.clip) { pose = fig.retarget.pose(clip.sample(S.t, fig.sample)); fig.retarget.placed(pose); }
  else if (S.pose === 'raw') pose = null;
  else pose = S.pose === 'rest' ? fig.restPose() : standPose();
  if (!pose) { fig.positions.set(body.positions); fig.pose = fig.restPose(); }
  else {
    if (S.relax) relaxHands(pose, S.relax);
    if (E_.jaw > 0) turnUnder(pose, sk, I.Jaw, qAxisAngle(qRot(getQ(pose.Q, I.Head), [1, 0, 0]), E_.jaw * 0.12));
    fig.skinner.skin(pose, fig.positions);
    if (S.clip) {
      const Pp = fig.positions; let lo = Infinity; for (let i = 1; i < Pp.length; i += 3) if (Pp[i] < lo) lo = Pp[i];
      const shift = pose.floor - lo; for (let i = 1; i < Pp.length; i += 3) Pp[i] += shift; for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
    }
    if (S.push) pushSkirt(fig.positions, pose);
    fig.pose = pose;
  }
  normalsOf(fig.positions, body.triangles, fig.normals);
  g.attributes.position.needsUpdate = true; g.attributes.normal.needsUpdate = true;
  const Q = fig.pose.Q;
  for (let j = 0; j < J; j++) { const [x, y, z, w] = [Q[j * 4], Q[j * 4 + 1], Q[j * 4 + 2], Q[j * 4 + 3]];
    U.R.value[j].set(1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)); }
  const Pp = fig.pose.P; shadow.position.x = Pp[I.Hips * 3]; shadow.position.z = Pp[I.Hips * 3 + 2];
}
function facing() {
  const qh = getQ(fig.pose.Q, I.Hips);
  const x = 2 * (qh[0] * qh[2] + qh[1] * qh[3]), z = 1 - 2 * (qh[0] * qh[0] + qh[1] * qh[1]);
  return Math.atan2(x, z);
}

window.A = {
  H, body, fig, sk, facing, face, S, EXPR_NAMES, faceCanvas, clipInfo: () => clip && { frames: clip.frames, fps: clip.fps },
  async set(o) {
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; face.setHead(clip ? headTrack(clip) : null); }
      S.clip = !!ids;
    }
    for (const k of ['t', 'pose', 'push', 'relax']) if (o[k] !== undefined) S[k] = o[k];
    if (o.time !== undefined) S.time = o.time; else if (o.t !== undefined && clip && !S.liveClock) S.time = o.t / clip.fps;
    if (o.liveClock !== undefined) S.liveClock = o.liveClock;
    if (o.still !== undefined) face.still = o.still;
    if (o.exprTrack) { face.exprKeys = [{ t: -10, w: { calm: 1 } }]; for (const [t, w] of o.exprTrack) face.setExpr(t, typeof w === 'string' ? { [w]: 1 } : w); }
    if (o.expr) face.setExpr(S.time, typeof o.expr === 'string' ? { [o.expr]: 1 } : o.expr);
    if (o.talk !== undefined) { face.talk(o.talk ? (o.talkFrom ?? S.time) : null); face.talkTo = o.talkTo ?? null; }
    if (o.cam) Object.assign(S.cam, o.cam);
    if (o.light) S.light = o.light;
    if (o.thr !== undefined) U.thr.value = o.thr;
    if (o.width !== undefined) U.width.value = o.width;
    if (o.bg) scene.background = new THREE.Color(o.bg);
    if (o.floor !== undefined) { floor.visible = !!o.floor; if (o.floor) floor.material.color.set(o.floor); }
    if (o.shadow !== undefined) shadow.visible = o.shadow;
    if (o.show !== undefined) {
      const all = a.triangles; let idx = all;
      if (o.show) { const parts = []; for (const n of o.show) { const [s0, s1] = H.trianglePieces[n]; parts.push(all.subarray(s0 * 3, s1 * 3)); }
        idx = new Uint32Array(parts.reduce((k, p) => k + p.length, 0)); let k = 0; for (const p of parts) { idx.set(p, k); k += p.length; } }
      g.setIndex(new THREE.BufferAttribute(idx, 1));
    }
    if (o.paint !== undefined) U.paint.value = o.paint ? 1 : 0;
    if (o.flat !== undefined) U.clay.value = o.flat ? 1 : 0;
    if (o.outline !== undefined) line.visible = !!o.outline;
    placeCamera();
    frame();
  },
  frames: () => clip ? clip.frames : 0,
  render() { placeCamera(); renderer.render(scene, camera); },
};
function placeCamera() {
  const w = canvas.clientWidth, h = canvas.clientHeight; renderer.setSize(w, h, false);
  const c = S.cam, cp = Math.cos(c.pitch);
  let tg = c.target || [c.cx, c.cy, 0];
  if (c.follow && fig.pose) { const Pp = fig.pose.P; tg = [Pp[I.Hips * 3], c.cy, Pp[I.Hips * 3 + 2]]; }
  if (c.focus && fig.pose) { const Pp = fig.pose.P, k = I[c.focus]; tg = [Pp[k * 3], Pp[k * 3 + 1] + (c.up || 0), Pp[k * 3 + 2]]; }
  const dir = [Math.sin(c.yaw) * cp, Math.sin(c.pitch), Math.cos(c.yaw) * cp];
  if (c.mode === 'ortho') {
    camera = ortho; const hh = c.h / 2, ww = hh * w / h;
    Object.assign(ortho, { left: -ww, right: ww, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
    ortho.position.set(tg[0] + dir[0] * 20, tg[1] + dir[1] * 20, tg[2] + dir[2] * 20);
    pxPerM = h / c.h;
  } else {
    camera = persp; persp.aspect = w / h; persp.fov = c.fov || 24; persp.updateProjectionMatrix();
    persp.position.set(tg[0] + dir[0] * c.dist, tg[1] + dir[1] * c.dist, tg[2] + dir[2] * c.dist);
    pxPerM = h / (2 * c.dist * Math.tan((c.fov || 24) * Math.PI / 360));
  }
  camera.lookAt(tg[0], tg[1], tg[2]);
  camera.updateMatrixWorld();
  // the light as in the drawing: from the picture's upper left, a little in front (camera space)
  const e = camera.matrixWorld.elements, l = S.light || [-0.5, 0.55, 0.65];
  U.L.value.set(e[0] * l[0] + e[4] * l[1] + e[8] * l[2], e[1] * l[0] + e[5] * l[1] + e[9] * l[2], e[2] * l[0] + e[6] * l[1] + e[10] * l[2]).normalize();
  U.width.value = S.lineW ?? Math.max(0.0012, 1.9 / pxPerM);
}
await window.A.set({});
window.A.render();
window.__ready = true;

if (!q.has('pack')) (await import('./ui.js')).ui(window.A, canvas);
