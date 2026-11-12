// Марат in the low-poly style (С19) — the 3D figure and its look.
//
// The body: the drawing's own convex facet pieces (styles/s19-lowpoly marat.figure) on SOMA's skeleton
// (tools/build.py). The motion: Kimodo's, carried by the engine as it is (engine/src: retarget, build, Skinner —
// linear blending: almost every piece is rigid on one bone, so its facets stay flat). The look is the drawing's rule,
// number for number (poly.Light): every facet one flat colour from its normal — a warm key from the upper left,
// a cool shadow, a faint fill from the right — computed here per triangle each frame, in the viewer's space as in
// the drawing (turning him is turning a figurine under a lamp). No outline, no gradients. The face's features are a
// drawn layer on the head's front facets (face.js). A flat cast shadow on the ground from the same key light.
import * as THREE from 'three';
import { makeSkeleton } from '../../../../engine/src/skeleton.js';
import { loadPack, readJSON } from '../../../../engine/src/pack.js';
import { makeBody } from '../../../../engine/src/body.js';
import { loadMotion, clipOf, newSample } from '../../../../engine/src/motion.js';
import { makeRetarget, build } from '../../../../engine/src/retarget.js';
import { Skinner } from '../../../../engine/src/skin.js';
import { qMul, qConj, qAxisAngle, qRot, getQ, setQ, getV } from '../../../../engine/src/math.js';
import { makeFace, BOX } from './face.js';
import { FaceLive } from './live.js';

THREE.ColorManagement.enabled = false;
const DATA = new URL('data/', import.meta.url);
const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255);
const mix3 = (a, b, t) => a.map((v, i) => v * (1 - t) + b[i] * t);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
const D = Math.PI / 180;

export const MOTIONS = { stand: 'стоит, как на рисунке', idle: 'стоит (Kimodo)', walk: 'идёт', wave: 'машет', bow: 'кланяется', stomp: 'топает', dance: 'танцует' };

// ------------------------------------------------------------------ the drawing's light (poly.Light)
const unit = v => { const l = Math.hypot(...v); return v.map(x => x / l); };
const LIGHT = { key: unit([-0.72, 0.52, 0.45]), fill: unit([0.85, -0.05, 0.5]), warm: hex('#fff1dc'), cool: hex('#5a5f8c'), wrap: 0.15, fillK: 0.22 };
const TINT0 = mix3(LIGHT.cool, [1, 1, 1], 0.25);
const MATS = { skin: [hex('#d9b2bd'), 0.80, 0.10], decal: [hex('#d9b2bd'), 0.85, 0.05], cloth: [TINT0, 0.72, 0.06], hair: [TINT0, 0.70, 0.05], metal: [TINT0, 0.65, 0.25] };
// a facet's colour is base · A + B (out: A.rgb, B.rgb), n in the viewer's space
function shadeAB(nx, ny, nz, mat, out) {
  const L = LIGHT, [tint, depth, wt] = MATS[mat] || MATS.cloth;
  let k = clamp((nx * L.key[0] + ny * L.key[1] + nz * L.key[2] + L.wrap) / (1 + L.wrap), 0, 1); k = k * k * (3 - 2 * k);
  const f = Math.max(nx * L.fill[0] + ny * L.fill[1] + nz * L.fill[2], 0) * L.fillK * (1 - k);
  for (let c = 0; c < 3; c++) { out[c] = (1 - k) * tint[c] * depth + k * 1.06 * (1 - wt) + f; out[3 + c] = k * wt * L.warm[c]; }
  return out;
}

// ------------------------------------------------------------------ data
export async function loadMarat() {
  const sk = makeSkeleton(await readJSON(new URL('skeleton.json', DATA)));
  const { header: h, arrays: a } = await loadPack(new URL('marat.json', DATA));
  const body = makeBody({
    id: h.id, label: h.label, source: h.source, topology: h.topology, skeleton: sk,
    positions: a.positions, triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
    parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
  });
  const poses = await readJSON(new URL('poses.json', DATA)), face = await readJSON(new URL('face.json', DATA));
  return { sk, body, poses, face, pieces: h.pieces, a };
}
const motions = new Map();
export function getClip(id, sk) {
  if (!motions.has(id)) motions.set(id, loadMotion(new URL(`motions/${id}.json`, DATA), sk).then(m => clipOf([m])));
  return motions.get(id);
}

// ------------------------------------------------------------------ facets: flat triangles coloured on the CPU
const VS = `attribute vec3 color; varying vec3 vC; void main(){ vC = color; gl_Position = projectionMatrix * viewMatrix * vec4(position, 1.); }`;
const FS = `varying vec3 vC; void main(){ gl_FragColor = vec4(clamp(vC, 0., 1.), 1.); }`;
// the head's front: the drawn layer over the skin, each shaded as the drawing shades skin and decals
const VS_FACE = `attribute vec3 color; attribute vec3 dA; attribute vec3 dB; attribute vec3 fuv; varying vec3 vC; varying vec3 vA; varying vec3 vB; varying vec3 vUv;
void main(){ vC = color; vA = dA; vB = dB; vUv = fuv; gl_Position = projectionMatrix * viewMatrix * vec4(position, 1.); }`;
const FS_FACE = `uniform sampler2D tFace; varying vec3 vC; varying vec3 vA; varying vec3 vB; varying vec3 vUv;
void main(){ vec3 c = vC; if (vUv.z > .5) { vec4 t = texture2D(tFace, vUv.xy); if (t.a > 0.) c = mix(c, (t.rgb / t.a) * vA + vB, t.a); } gl_FragColor = vec4(clamp(c, 0., 1.), 1.); }`;
const VS_SHADOW = `uniform vec3 dir; uniform float y0; varying vec3 vG; void main(){ float s = (position.y - y0) / dir.y; vec3 g = position - dir * s; g.y = y0 + .003; vG = g; gl_Position = projectionMatrix * viewMatrix * vec4(g, 1.); }`;
const FS_SHADOW = `uniform vec4 col; uniform vec4 disc; varying vec3 vG; void main(){ if (disc.w > 0. && length(vG.xz - disc.xz) > disc.w) discard; gl_FragColor = col; }`;

class Facets {
  // tris: [[i0, i1, i2, base rgb, mat, polygon id or −1]] over the shared vertex array
  constructor(tris, { decal = false, face = null } = {}) {
    this.tris = tris; const n = tris.length;
    this.pos = new Float32Array(n * 9); this.col = new Float32Array(n * 9);
    const g = this.geometry = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(this.pos, 3)); g.setAttribute('color', new THREE.BufferAttribute(this.col, 3));
    let material;
    if (face) {
      this.dA = new Float32Array(n * 9); this.dB = new Float32Array(n * 9); this.fuv = new Float32Array(n * 9); this.face = face;
      g.setAttribute('dA', new THREE.BufferAttribute(this.dA, 3)); g.setAttribute('dB', new THREE.BufferAttribute(this.dB, 3)); g.setAttribute('fuv', new THREE.BufferAttribute(this.fuv, 3));
      material = new THREE.ShaderMaterial({ vertexShader: VS_FACE, fragmentShader: FS_FACE, uniforms: { tFace: { value: face.texture } } });
    } else material = new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, side: decal ? THREE.DoubleSide : THREE.FrontSide, polygonOffset: decal, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
    this.mesh = new THREE.Mesh(g, material); this.mesh.frustumCulled = false;
    this.ab = new Float64Array(6); this.ab2 = new Float64Array(6);
  }
  // P: the vertices now; R: the viewer's rotation (rows, 3×3); polyN: normals of whole decals (by polygon id)
  update(P, R, polyN, flat = null) {
    const { tris, pos, col, ab, ab2 } = this;
    for (let t = 0; t < tris.length; t++) {
      const T = tris[t], a = T[0] * 3, b = T[1] * 3, c = T[2] * 3, o = t * 9;
      pos[o] = P[a]; pos[o + 1] = P[a + 1]; pos[o + 2] = P[a + 2]; pos[o + 3] = P[b]; pos[o + 4] = P[b + 1]; pos[o + 5] = P[b + 2]; pos[o + 6] = P[c]; pos[o + 7] = P[c + 1]; pos[o + 8] = P[c + 2];
      let nx, ny, nz;
      if (T[5] >= 0) { nx = polyN[T[5] * 3]; ny = polyN[T[5] * 3 + 1]; nz = polyN[T[5] * 3 + 2]; }
      else {
        const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], vx = P[c] - P[a], vy = P[c + 1] - P[a + 1], vz = P[c + 2] - P[a + 2];
        nx = uy * vz - uz * vy; ny = uz * vx - ux * vz; nz = ux * vy - uy * vx;
        const l = Math.hypot(nx, ny, nz) || 1; nx /= l; ny /= l; nz /= l;
      }
      const vx = R[0] * nx + R[1] * ny + R[2] * nz, vy = R[3] * nx + R[4] * ny + R[5] * nz, vz = R[6] * nx + R[7] * ny + R[8] * nz;
      const base = flat || T[3];
      shadeAB(vx, vy, vz, flat ? 'cloth' : T[4], ab);
      for (let k = 0; k < 3; k++) for (let c2 = 0; c2 < 3; c2++) col[o + k * 3 + c2] = base[c2] * ab[c2] + ab[3 + c2];
      if (this.face) {
        shadeAB(vx, vy, vz, 'decal', ab2);
        const front = this.face.front(T, nx, ny, nz) && !flat ? 1 : 0;
        for (let k = 0; k < 3; k++) {
          for (let c2 = 0; c2 < 3; c2++) { this.dA[o + k * 3 + c2] = ab2[c2]; this.dB[o + k * 3 + c2] = ab2[3 + c2]; }
          const uv = this.face.uv(T[k]); this.fuv[o + k * 3] = uv[0]; this.fuv[o + k * 3 + 1] = uv[1]; this.fuv[o + k * 3 + 2] = front;
        }
      }
    }
    const g = this.geometry; g.attributes.position.needsUpdate = true; g.attributes.color.needsUpdate = true;
    if (this.face) { g.attributes.dA.needsUpdate = true; g.attributes.dB.needsUpdate = true; g.attributes.fuv.needsUpdate = true; }
  }
}

// ------------------------------------------------------------------ the figure
export class Marat {
  constructor(data, { armsOff = 9 } = {}) {
    this.d = data; const { sk, body, pieces, a } = data;
    this.sk = sk; this.body = body; this.J = sk.J;
    this.retarget = makeRetarget(body, { corrections: armsOff ? { armsOff: { degrees: armsOff } } : {} });
    this.skinner = new Skinner(body, { method: 'lbs' });
    this.sample = newSample(sk.J); this.L = new Float64Array(sk.J * 4);
    this.P = new Float32Array(body.N * 3);
    this.faceDraw = makeFace(data.face); this.live = new FaceLive(this.faceDraw);
    this.texture = new THREE.CanvasTexture(this.faceDraw.canvas);
    this.texture.premultiplyAlpha = true; this.texture.generateMipmaps = true; this.texture.minFilter = THREE.LinearMipmapLinearFilter; this.texture.anisotropy = 4;
    // the jaw and beard's moves
    this.morph = []; for (let i = 0; i < body.N; i++) { let s = 0; for (let k = 0; k < 3; k++) s += Math.abs(a.dOpen[i * 3 + k]) + Math.abs(a.dDrop[i * 3 + k]); if (s > 1e-7) this.morph.push(i); }
    this.open = 1; this.drop = 0.48;
    // the meshes: the body, the head's skin (with the drawn face), decals, and what can be swapped
    const T = a.triangles, groups = {}; this.polys = [];
    pieces.forEach((pc, pi) => {
      const key = pc.decal ? (pc.group === 'body' ? 'decals' : 'decals-' + pc.group) : pc.face ? 'face' : pc.group === 'head' ? 'body' : pc.group;
      const poly = pc.decal ? this.polys.push(pc) - 1 : -1;
      for (let t = pc.t0; t < pc.t0 + pc.tn; t++) (groups[key] ??= []).push([T[t * 3], T[t * 3 + 1], T[t * 3 + 2], pc.color, pc.mat, poly]);
    });
    const hs = data.face.head_scale * 0.01, hc = data.face.head;
    const face = {
      texture: this.texture,
      uv: i => { const x = a.faceXY[i * 2], y = a.faceXY[i * 2 + 1] + this.drop * a.dDrop[i * 3 + 1] / hs; return [(x - BOX.x0) / (BOX.x1 - BOX.x0), (y - BOX.y0) / (BOX.y1 - BOX.y0)]; },
      front: T3 => { const P0 = body.positions, n = triN(P0, T3[0], T3[1], T3[2]); return n[2] > 1e-3; },
    };
    this.group = new THREE.Group(); this.parts = {};
    for (const [key, tris] of Object.entries(groups)) {
      const f = new Facets(tris, { decal: key.startsWith('decals'), face: key === 'face' ? face : null });
      this.parts[key] = f; this.group.add(f.mesh);
    }
    this.polyN = new Float32Array(this.polys.length * 3);
    this.hands = { L: 'fist', R: 'fist' }; this.ladle = false;
    // the cast shadow: every solid facet flattened onto the ground along the key light, drawn once (stencil)
    this.shadowU = { dir: { value: new THREE.Vector3(0, 1, 0) }, y0: { value: 0 }, col: { value: new THREE.Vector4(...hex('#2a2038'), 0.3) }, disc: { value: new THREE.Vector4(0, 0, 0, 0) } };
    const sm = new THREE.ShaderMaterial({ vertexShader: VS_SHADOW, fragmentShader: FS_SHADOW, uniforms: this.shadowU, transparent: true, depthWrite: false, side: THREE.DoubleSide,
      stencilWrite: true, stencilFunc: THREE.NotEqualStencilFunc, stencilRef: 1, stencilZPass: THREE.ReplaceStencilOp, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
    this.shadow = new THREE.Group(); this.shadowMeshes = {};
    for (const [key, f] of Object.entries(this.parts)) if (!key.startsWith('decals')) { const m = new THREE.Mesh(f.geometry, sm); m.frustumCulled = false; m.renderOrder = 2; this.shadowMeshes[key] = m; this.shadow.add(m); }
    this.setHands();
  }
  setHands(h = {}, ladle = this.ladle) {
    Object.assign(this.hands, h); this.ladle = ladle;
    const on = { ladle };
    for (const k of ['L', 'R']) for (const kind of ['fist', 'open']) on[kind + k] = this.hands[k] === kind;
    for (const [key, f] of Object.entries(this.parts)) { f.on = on[key.replace('decals-', '')] ?? true; if (this.shadowMeshes[key]) this.shadowMeshes[key].visible = f.on; }
  }
  staticPose(p) {
    const pose = { Q: Float64Array.from(p.Q.flat()), P: new Float64Array(this.J * 3), floor: 0 };
    build(pose, this.body, p.hips);
    return pose;
  }
  // small life on a standing pose: the chest rises with the breath, the collarbones lift, the head stays level
  breathe(pose, br) {
    const { sk, L } = this;
    for (let j = 0; j < this.J; j++) { const p = sk.parent[j]; setQ(L, j, p < 0 ? getQ(pose.Q, j) : qMul(qConj(getQ(pose.Q, p)), getQ(pose.Q, j))); }
    const tw = (n, ax, deg) => { const j = sk.index[n]; setQ(L, j, qMul(qAxisAngle(ax, deg * D * br), getQ(L, j))); };
    tw('Chest', [1, 0, 0], -1.5); tw('Neck1', [1, 0, 0], 0.9); tw('Head', [1, 0, 0], 0.6);
    tw('LeftShoulder', [0, 0, 1], 1.6); tw('RightShoulder', [0, 0, 1], -1.6); tw('LeftArm', [0, 0, 1], -1.6); tw('RightArm', [0, 0, 1], 1.6);
    for (let j = 0; j < this.J; j++) { const p = sk.parent[j]; setQ(pose.Q, j, p < 0 ? getQ(L, j) : qMul(getQ(pose.Q, p), getQ(L, j))); }
  }
  // the figure at a moment: a Kimodo clip at t (frames) or a drawn pose; → the pose (joints' turns and places)
  frame({ clip = null, t = 0, stat = null, place = { position: [0, 0, 0], heading: 0 }, breath = 0, open = this.open }) {
    let pose; Object.assign(this.retarget.place, place);
    if (clip) pose = this.retarget.pose(clip.sample(t, this.sample));
    else pose = this.staticPose(stat);
    const hip = getV(pose.P, this.sk.index.Hips);
    if (breath) { this.breathe(pose, breath); build(pose, this.body, hip); }
    if (clip) this.retarget.placed(pose);
    else { const r = qAxisAngle([0, 1, 0], place.heading || 0); for (let j = 0; j < this.J; j++) { setQ(pose.Q, j, qMul(r, getQ(pose.Q, j))); const v = qRot(r, getV(pose.P, j)); pose.P[j * 3] = v[0] + place.position[0]; pose.P[j * 3 + 1] = v[1] + place.position[1]; pose.P[j * 3 + 2] = v[2] + place.position[2]; } }
    const P = this.P; this.skinner.skin(pose, P);
    // the jaw and the beard: the drawing's `open` and `drop`, turned with the head
    this.open = open; this.drop = Math.max(0, open - 0.6) * 1.2;
    const { dOpen, dDrop } = this.d.a, qh = getQ(pose.Q, this.sk.index.Head);
    for (const i of this.morph) {
      const v = qRot(qh, [dOpen[i * 3] * open + dDrop[i * 3] * this.drop, dOpen[i * 3 + 1] * open + dDrop[i * 3 + 1] * this.drop, dOpen[i * 3 + 2] * open + dDrop[i * 3 + 2] * this.drop]);
      P[i * 3] += v[0]; P[i * 3 + 1] += v[1]; P[i * 3 + 2] += v[2];
    }
    // on the floor: in a clip the lowest point where Kimodo's was; a drawn pose stands where it was drawn
    let ground = place.position[1];
    if (clip) {
      let lo = Infinity; for (let i = 1; i < P.length; i += 3) if (P[i] < lo) lo = P[i];
      const sh = pose.floor - lo; for (let i = 1; i < P.length; i += 3) P[i] += sh;
      for (let j = 0; j < this.J; j++) pose.P[j * 3 + 1] += sh;
      ground = place.position[1];
    }
    this.ground = ground; this.pose = pose;
    return pose;
  }
  // colours for the viewer's rotation R (rows); flat: one grey for all (to show the forms)
  shade(R, flat = null) {
    const P = this.P, N = this.polyN;
    this.polys.forEach((pc, k) => {   // a decal is one flat sign: one normal for the whole of it (Newell)
      let nx = 0, ny = 0, nz = 0;
      for (let i = 0; i < pc.vn; i++) { const a = (pc.v0 + i) * 3, b = (pc.v0 + (i + 1) % pc.vn) * 3; nx += (P[a + 1] - P[b + 1]) * (P[a + 2] + P[b + 2]); ny += (P[a + 2] - P[b + 2]) * (P[a] + P[b]); nz += (P[a] - P[b]) * (P[a + 1] + P[b + 1]); }
      const l = Math.hypot(nx, ny, nz) || 1; N[k * 3] = nx / l; N[k * 3 + 1] = ny / l; N[k * 3 + 2] = nz / l;
    });
    for (const [key, f] of Object.entries(this.parts)) { f.mesh.visible = f.on && !(flat && key.startsWith('decals')); if (f.on) f.update(P, R, N, flat); }
  }
  drawFace(f) { this.faceDraw.draw(f.v, { blink: f.blink, look: f.look }); this.texture.needsUpdate = true; }
}
function triN(P, a, b, c) {
  a *= 3; b *= 3; c *= 3;
  const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2], vx = P[c] - P[a], vy = P[c + 1] - P[a + 1], vz = P[c + 2] - P[a + 2];
  return [uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx];
}

// ------------------------------------------------------------------ the stage
const VS_BG = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 1., 1.); }`;
const FS_BG = `uniform sampler2D t; varying vec2 vUv; void main(){ gl_FragColor = vec4(texture2D(t, vUv).rgb, 1.); }`;
const VS_GROUND = `attribute vec3 color; varying vec3 vC; varying vec3 vW; void main(){ vC = color; vW = position; gl_Position = projectionMatrix * viewMatrix * vec4(position, 1.); }`;
const FS_GROUND = `uniform vec3 centre; uniform vec2 fade; varying vec3 vC; varying vec3 vW; void main(){ float a = 1. - smoothstep(fade.x, fade.y, length(vW.xz - centre.xz)); gl_FragColor = vec4(vC, a); }`;

// the drawing's backdrop (scenery.backdrop): a soft gradient with a few large faint facets
function backdrop(w, h, top, bottom, seed = 5) {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h; const c = cv.getContext('2d'), r = rng(seed);
  const g = c.createLinearGradient(0, 0, 0, h); g.addColorStop(0, top); g.addColorStop(1, bottom); c.fillStyle = g; c.fillRect(0, 0, w, h);
  const cols = Math.round(w / 260) + 1, rows = Math.round(h / 260) + 1, u = (a, b) => a + (b - a) * r();
  const P = Array.from({ length: rows }, (_, j) => Array.from({ length: cols }, (_, i) => [i * w / (cols - 1) + (i > 0 && i < cols - 1 ? u(-60, 60) : 0), j * h / (rows - 1) + (j > 0 && j < rows - 1 ? u(-60, 60) : 0)]));
  for (let j = 0; j < rows - 1; j++) for (let i = 0; i < cols - 1; i++) {
    const a = P[j][i], b = P[j][i + 1], cc = P[j + 1][i + 1], d = P[j + 1][i];
    for (const tri of (i + j) % 2 ? [[a, b, cc], [a, cc, d]] : [[a, b, d], [b, cc, d]]) {
      const v = u(-1, 1); c.fillStyle = v > 0 ? `rgba(255,255,255,${Math.abs(v) * 0.04})` : `rgba(42,36,64,${Math.abs(v) * 0.04})`;
      c.beginPath(); c.moveTo(...tri[0]); c.lineTo(...tri[1]); c.lineTo(...tri[2]); c.closePath(); c.fill();
    }
  }
  return cv;
}

export async function createStage(canvas, { pixelRatio } = {}) {
  const data = await loadMarat(), ch = new Marat(data);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, stencil: true, alpha: true, preserveDrawingBuffer: true });
  renderer.outputColorSpace = THREE.LinearSRGBColorSpace; renderer.setPixelRatio(pixelRatio ?? Math.min(2, devicePixelRatio || 1));
  const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(24, 1, 0.3, 80);
  const bgU = { t: { value: null } };
  const bg = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({ vertexShader: VS_BG, fragmentShader: FS_BG, uniforms: bgU, depthTest: false, depthWrite: false }));
  bg.frustumCulled = false; bg.renderOrder = -10; scene.add(bg);
  // the ground: flat, of large faint facets, fading into the backdrop away from him
  const groundU = { centre: { value: new THREE.Vector3() }, fade: { value: new THREE.Vector2(3.5, 9) } };
  const ground = (() => {
    const r = rng(23), n = 44, cell = 0.9, pos = [], col = [], base = hex('#c9a088');
    const V = Array.from({ length: n + 1 }, (_, j) => Array.from({ length: n + 1 }, (_, i) => [(i - n / 2) * cell + (r() - 0.5) * 0.5, (j - n / 2) * cell + (r() - 0.5) * 0.5]));
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
      const a = V[j][i], b = V[j][i + 1], c = V[j + 1][i + 1], d = V[j + 1][i];
      for (const tri of (i + j) % 2 ? [[a, c, b], [a, d, c]] : [[a, d, b], [b, d, c]]) {
        const v = r() * 2 - 1, cc = mix3(base, v > 0 ? [1, 1, 1] : hex('#4a3040'), Math.abs(v) * 0.09);
        for (const p of tri) { pos.push(p[0], 0, p[1]); col.push(...cc); }
      }
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    const m = new THREE.Mesh(g, new THREE.ShaderMaterial({ vertexShader: VS_GROUND, fragmentShader: FS_GROUND, uniforms: groundU, transparent: true, depthWrite: false, side: THREE.DoubleSide }));
    m.frustumCulled = false; m.renderOrder = 1; return m;
  })();
  scene.add(ground);
  // the plinth of the drawing's sheets (scenery.plinth): a faceted round base, top at y = 0
  const plinth = (() => {
    const { r, h, color, n } = data.face.plinth, P = [], tris = [], c = hex(color), ring = (rad, y, ph) => { const o = P.length / 3; for (let i = 0; i < n; i++) { const a = 2 * Math.PI * (i + ph) / n; P.push(rad * Math.sin(a), y, rad * Math.cos(a)); } return o; };
    const t = ring(r, 0, 0), m = ring(r + 0.016, -h * 0.45, 0.5), b = ring(r + 0.012, -h, 0);
    for (let i = 1; i < n - 1; i++) tris.push([t, t + i, t + i + 1, c, 'cloth', -1]);
    for (let i = 0; i < n; i++) { const j = (i + 1) % n; tris.push([t + i, m + i, t + j, c, 'cloth', -1], [m + i, m + j, t + j, c, 'cloth', -1], [m + i, b + j, m + j, c, 'cloth', -1], [m + i, b + i, b + j, c, 'cloth', -1]); }
    const f = new Facets(tris); f.P = Float32Array.from(P); f.mesh.visible = false; return f;
  })();
  scene.add(plinth.mesh); scene.add(ch.shadow); scene.add(ch.group);

  const st = {
    data, ch, renderer, scene, camera, ground, plinth,
    // the camera, in the drawing's terms (poly.Camera): the model turned by yaw and pitch about `target`, seen from
    // `dist` away. mode 'draw': scale px per metre at the target, the target at (ox, oy) px — the drawing's sheets;
    // mode 'orbit': a field of view, the target in the middle (pad: px kept free at the bottom for the controls)
    cam: { mode: 'orbit', yaw: 20, pitch: 6, dist: 6, fov: 24, target: new THREE.Vector3(0, 0.9, 0), scale: 300, ox: 0, oy: 0, pad: 0 },
    look: { plinth: false, ground: true, shadow: true, flat: null, bg: true },
    w: 800, h: 800,
    size(w, h) { st.w = w; st.h = h; renderer.setSize(w, h, false); bgU.t.value?.dispose(); bgU.t.value = new THREE.CanvasTexture(backdrop(w, h, ...data.face.bg)); },
    R: new Float64Array(9),
    render() {
      const c = st.cam, cy = Math.cos(c.yaw * D), sy = Math.sin(c.yaw * D), cp = Math.cos(c.pitch * D), sp = Math.sin(c.pitch * D);
      // R = Rx(pitch) · Ry(yaw): world → the viewer's space
      const R = st.R; R[0] = cy; R[1] = 0; R[2] = sy; R[3] = sp * sy; R[4] = cp; R[5] = -sp * cy; R[6] = -cp * sy; R[7] = sp; R[8] = cp * cy;
      camera.quaternion.setFromRotationMatrix(new THREE.Matrix4().set(R[0], R[3], R[6], 0, R[1], R[4], R[7], 0, R[2], R[5], R[8], 0, 0, 0, 0, 1));
      const dist = c.mode === 'orbit' && c.pad ? c.dist * st.h / Math.max(200, st.h - c.pad) : c.dist;   // the figure whole above the controls
      camera.position.set(c.target.x + R[6] * dist, c.target.y + R[7] * dist, c.target.z + R[8] * dist);
      camera.aspect = st.w / st.h;
      if (c.mode === 'draw') { camera.fov = 2 * Math.atan(st.h / 2 / c.scale / c.dist) / D; camera.setViewOffset(st.w, st.h, st.w / 2 - c.ox, st.h / 2 - c.oy, st.w, st.h); }
      else { camera.fov = c.fov; if (c.pad) camera.setViewOffset(st.w, st.h, 0, c.pad / 2, st.w, st.h); else camera.clearViewOffset(); }
      camera.near = Math.max(0.2, dist - 6); camera.far = dist + 40; camera.updateProjectionMatrix(); camera.updateMatrixWorld(true);
      const L = st.look;
      ch.shade(R, L.flat);
      plinth.mesh.visible = L.plinth; if (L.plinth) plinth.update(plinth.P, R, null, L.flat);
      ground.visible = L.ground; bg.visible = L.bg;
      groundU.centre.value.set(c.target.x, 0, c.target.z);
      // the key light in the world: Rᵀ · key; the shadow falls along it onto the ground (on the plinth: its top only)
      const k = LIGHT.key, dx = R[0] * k[0] + R[3] * k[1] + R[6] * k[2], dy = R[1] * k[0] + R[4] * k[1] + R[7] * k[2], dz = R[2] * k[0] + R[5] * k[1] + R[8] * k[2];
      ch.shadow.visible = L.shadow && dy > 0.15;
      ch.shadowU.dir.value.set(dx, dy, dz); ch.shadowU.y0.value = ch.ground ?? 0;
      ch.shadowU.disc.value.set(0, 0, 0, L.plinth ? data.face.plinth.r : 0);
      renderer.setClearColor(0xffffff, L.bg ? 1 : 0); renderer.clear(true, true, true);
      renderer.render(scene, camera);
    },
  };
  return st;
}
