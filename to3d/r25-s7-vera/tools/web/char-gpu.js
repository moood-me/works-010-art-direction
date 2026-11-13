// A character of the Ghibli style (С7) in 3D: the character pack (tools/build.py) on the engine's skeleton, skinning and Kimodo
// retargeting; drawn as a cel: flat colour, one shade tone of a warm multiply with a hard edge (the light from the
// picture's upper left, as in the drawing), one even dark-brown outline (inverted hull), and the face drawn live on a
// canvas from the drawing's own face parts (face.js), projected from the front.
// This is the page's fast variant (fast.html; view.html and char.js beside it are the page as it was): the skin is
// skinned in the vertex shader (engine-gpu/src/gpuskin.js), the processor works out only the joints and the floor from a
// probe of the skin; the face's canvas is redrawn and sent to the video card only when it changed.
//   fast.html — by hand (ui.js); fast.html?pack=<url> — driven by tools/shots.mjs
//   window.A.set({clip, t, time, pose, expr, exprTrack, talk, talkFrom, cam, …}) then A.render()
import * as THREE from 'three';
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { GpuSkin } from '../../../../engine-gpu/src/gpuskin.js';
import { qAxisAngle, qBetween, qRot, getQ, getV, normalize, sub } from '../../../../engine/src/math.js';
import { LiveFace, draw as drawFace, configure as configureFace } from './face.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack') || document.documentElement.dataset.pack, location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const sk = E.skeleton;

const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const rest = Float32Array.from(a.positions);
const spec = { skinning: { method: H.skinning, clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
const gs = new GpuSkin(THREE, fig.skinner);

// ---------------------------------------------------------------- the stage
const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Number(q.get('dpr') || 1));
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
scene.background = new THREE.Color(q.get('bg') || '#efe6d4');

const g = gs.attributes(new THREE.BufferGeometry());
for (const [k, n, norm] of [['col', 3, true], ['shd', 3, true], ['lin', 3, true], ['ow', 1, true], ['uv', 2, false], ['tex', 1, false],
  ['pn', 3, false], ['pw', 1, true], ['pj', 1, false], ['two', 1, false], ['ob', 1, false]])
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
configureFace(FB.params, FB.expr);
const EXPR_NAMES = Object.keys(FB.expr);
const face = new LiveFace(Number(q.get('seed') ?? 7));
const U = {
  L: { value: new THREE.Vector3(-0.5, 0.55, 0.65).normalize() },
  thr: { value: Number(q.get('thr') ?? 0.0) },
  face: { value: faceTex },
  width: { value: Number(q.get('line') ?? 0.0032) },
  paint: { value: 1 }, clay: { value: 0 },
  R: { value: Array.from({ length: sk.J }, () => new THREE.Matrix3()) },
  ...gs.uniforms,
};
const srgb = c => new THREE.Color().setRGB(c[0] / 255, c[1] / 255, c[2] / 255, THREE.SRGBColorSpace);
// vertex colours are the drawing's sRGB hexes: turned linear here so they come out on screen exactly as drawn
for (const k of ['col', 'shd', 'lin']) {
  const src = a[k], f = new Float32Array(src.length);
  for (let i = 0; i < src.length; i += 3) { const c = srgb([src[i], src[i + 1], src[i + 2]]); f[i] = c.r; f[i + 1] = c.g; f[i + 2] = c.b; }
  g.setAttribute(k, new THREE.BufferAttribute(f, 3));
}
const toon = new THREE.ShaderMaterial({
  uniforms: U,
  vertexShader: `
    attribute vec3 col; attribute vec3 shd; attribute float tex; attribute vec3 pn; attribute float pw; attribute float pj; attribute float two;
    uniform mat3 R[${sk.J}];
    ${gs.glsl}
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec2 vUv; varying float vTex; varying float vTwo; varying float vPw;
    void main() { vec3 P, N; skinVertex(position, normal, P, N);
      vPw = pw; vN = normalize(mix(N, R[int(pj + 0.5)] * pn, pw)); vCol = col; vShd = shd; vUv = uv; vTex = tex; vTwo = two;
      gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0); }`,
  fragmentShader: `
    uniform vec3 L; uniform float thr; uniform sampler2D face; uniform float paint; uniform float clay;
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec2 vUv; varying float vTex; varying float vTwo; varying float vPw;
    void main() {
      if (!gl_FrontFacing && vTwo < 0.5) discard;
      float d = dot(normalize(vN), L);
      float lit = smoothstep(thr - 0.012, thr + 0.012, d);
      vec3 c = mix(vShd, vCol, lit);
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
    ${gs.glsl}
    void main() { vec3 P, N; skinVertex(position, normal, P, N);
      vC = lin; vOw = ow; vec4 mv = viewMatrix * vec4(P + N * width * ow, 1.0); mv.z -= ob + 0.002;
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
const HEAD_FWD = H.headFwd;      // the face's direction at rest (a head drawn bowed is bowed at rest)
// the drawing's 'stand' pose (the character's POSES.stand, in the pack's header): upper arm, forearm, hand directions
// (the drawing paints the arms over the body; in 3D they hang just outside it: a little more out, by `out`)
const ST = H.stand, outw = v => [v[0] + ST.out, v[1], v[2]];
const STAND = { upper: outw(ST.upper), fore: outw(ST.fore), hand: ST.hand };
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
    // which side the palm is: where the thumb lies off the plane of the knuckles (joints 2; joints 1 are in the wrist)
    const dirM = normalize(sub(V3(pose, J_('Middle3')), V3(pose, J_('Middle2'))));
    const across = normalize(sub(V3(pose, J_('Index2')), V3(pose, J_('Pinky2'))));
    let palm = sub(V3(pose, J_('ThumbEnd')), V3(pose, J_('Middle2')));
    palm = normalize(sub(sub(palm, dirM.map(v => v * dot3(palm, dirM))), across.map(v => v * dot3(palm, across))));
    // together: each finger turned at its knuckle toward the middle finger's direction
    for (const f of ['Index', 'Ring', 'Pinky']) {
      const d = normalize(sub(V3(pose, J_(f + '3')), V3(pose, J_(f + '2'))));
      const tg = normalize(d.map((v, i) => v * 0.15 + dirM[i] * 0.85));
      turnUnder(pose, sk, J_(f + '2'), qBetween(d, tg)); re();
    }
    // bent toward the palm, a little more at the middle joints; the little finger's side a little more than the index's
    FINGERS.forEach((f, fi) => { for (const [n, ang] of [[2, 0.35], [3, 0.45], [4, 0.3]]) {
      const j = J_(f + n), c = n < 4 ? J_(f + (n + 1)) : J_(f + 'End');
      const d = normalize(sub(V3(pose, c), V3(pose, j)));
      const ax = normalize(cross3(d, palm));
      turnUnder(pose, sk, j, qAxisAngle(ax, ang * k * (0.8 + 0.15 * fi))); re();
    } });
    // the thumb down along the hand, not sticking out
    { const d = normalize(sub(V3(pose, J_('ThumbEnd')), V3(pose, J_('Thumb1')))), u = Math.min(1, 0.75 * k);
      turnUnder(pose, sk, J_('Thumb1'), qBetween(d, normalize(d.map((v, i) => v * (1 - u) + dirM[i] * u)))); re(); }
    { const j = J_('Thumb2'), d = normalize(sub(V3(pose, J_('Thumb3')), V3(pose, j)));
      turnUnder(pose, sk, j, qAxisAngle(normalize(cross3(d, palm)), 0.25 * k)); re(); }
  }
}
// the palm turned as drawn (toward the thigh: palm (−1, 0, 0.2) for the left hand, mirrored), about the hand's axis
function palmIn(pose, s, sg) {
  const J_ = n => I[`${s}Hand${n}`], H_ = I[s + 'Hand'];
  const ax = normalize(sub(V3(pose, J_('Middle2')), V3(pose, H_)));
  const across = normalize(sub(V3(pose, J_('Index2')), V3(pose, J_('Pinky2'))));
  let palm = sub(V3(pose, J_('ThumbEnd')), V3(pose, J_('Middle2')));
  palm = normalize(sub(sub(palm, ax.map(v => v * dot3(palm, ax))), across.map(v => v * dot3(palm, across))));
  let want = [ST.palm[0] * sg, ST.palm[1], ST.palm[2]]; want = normalize(sub(want, ax.map(v => v * dot3(want, ax))));
  const ang = Math.atan2(dot3(cross3(palm, want), ax), dot3(palm, want));
  turnUnder(pose, sk, H_, qAxisAngle(ax, ang)); build(pose, body, getV(pose.P, I.Hips));
}
function standPose() {
  const pose = fig.restPose();
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    const m = v => [v[0] * sg, v[1], v[2]];
    aim(pose, I[s + 'Arm'], I[s + 'ForeArm'], m(STAND.upper));
    aim(pose, I[s + 'ForeArm'], I[s + 'Hand'], m(STAND.fore));
    aim(pose, I[s + 'Hand'], I[s + 'HandMiddle2'], m(STAND.hand));
    palmIn(pose, s, sg);
  }
  return pose;
}

const S = { clip: null, clipIds: null, t: 0, time: 0, pose: 'stand', relax: 0.6, linePx: 1.9,
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
// the face's line width follows how big the head is on screen (the drawing draws its lines one width in pixels)
// the pack as it lies, unskinned: every joint where it is at rest, unturned
const rawPose = { Q: new Float64Array(J * 4), P: Float64Array.from(body.joints) };
for (let j = 0; j < J; j++) rawPose.Q[j * 4 + 3] = 1;
let pxPerM = 500, faceWas = '';
function frame() {
  const E_ = face.at(S.time, { headT: S.clip ? S.t / clip.fps : null });
  const lw = Math.max(0.014, Math.min(0.045, S.linePx * 1.1 / (pxPerM * 0.12)));
  let pose;
  if (S.clip) { pose = fig.retarget.pose(clip.sample(S.t, fig.sample)); fig.retarget.placed(pose); }
  else if (S.pose === 'raw') pose = null;
  else pose = S.pose === 'rest' ? fig.restPose() : standPose();
  if (!pose) { gs.setPose(rawPose); fig.pose = fig.restPose(); }
  else {
    if (S.relax) relaxHands(pose, S.relax);
    if (E_.jaw > 0) turnUnder(pose, sk, I.Jaw, qAxisAngle(qRot(getQ(pose.Q, I.Head), [1, 0, 0]), E_.jaw * 0.12));
    if (S.clip) {          // on the floor as the engine's Figure does (motion.floor 'lowest')
      const shift = pose.floor - gs.lowest(pose); for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
    }
    gs.setPose(pose);
    fig.pose = pose;
  }
  const Q = fig.pose.Q;
  for (let j = 0; j < J; j++) { const [x, y, z, w] = [Q[j * 4], Q[j * 4 + 1], Q[j * 4 + 2], Q[j * 4 + 3]];
    U.R.value[j].set(1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)); }
  // how the face is turned from the camera: the nose's hook is drawn on the far side, in profile only its wing
  const c = S.cam, cd = [Math.sin(c.yaw) * Math.cos(c.pitch), Math.sin(c.pitch), Math.cos(c.yaw) * Math.cos(c.pitch)], cr = [Math.cos(c.yaw), 0, -Math.sin(c.yaw)];
  const hf = qRot(getQ(Q, I.Head), HEAD_FWD), turn = Math.atan2(dot3(hf, cr), dot3(hf, cd)) * 180 / Math.PI;
  const noseSide = turn >= -2 ? 1 : -1, profile = Math.abs(turn) > 70, fk = JSON.stringify([E_, lw, noseSide, profile]);
  if (fk !== faceWas) { drawFace(faceCtx, E_, FB, PX, { lw, shadow: FB.shadow, noseSide, profile }); faceTex.needsUpdate = true; faceWas = fk; }      // the face is redrawn only when its numbers changed
  const Pp = fig.pose.P; shadow.position.x = Pp[I.Hips * 3]; shadow.position.z = Pp[I.Hips * 3 + 2];
}
function facing() {
  const qh = getQ(fig.pose.Q, I.Hips);
  const x = 2 * (qh[0] * qh[2] + qh[1] * qh[3]), z = 1 - 2 * (qh[0] * qh[0] + qh[1] * qh[1]);
  return Math.atan2(x, z);
}

window.A = {
  H, body, fig, gs, sk, facing, face, S, EXPR_NAMES, faceCanvas, clipInfo: () => clip && { frames: clip.frames, fps: clip.fps },
  async set(o) {
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; face.setHead(clip ? headTrack(clip) : null); }
      S.clip = !!ids;
    }
    for (const k of ['t', 'pose', 'relax', 'linePx']) if (o[k] !== undefined) S[k] = o[k];
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
let cw = 0, ch = 0;      // the size the renderer was last given: given anew each frame, the browser allocates the picture anew
function placeCamera() {
  const w = canvas.clientWidth, h = canvas.clientHeight; if (w !== cw || h !== ch) { renderer.setSize(w, h, false); cw = w; ch = h; }
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
  U.width.value = Math.max(0.0012, S.linePx / pxPerM);
}
await window.A.set({});
window.A.render();
window.__ready = true;

if (!q.has('pack')) (await import('./ui.js')).ui(window.A, canvas);
