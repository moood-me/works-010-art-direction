// Савелий Петрович in the symbolic style (С6) — the 3D figure, its life and its light.
//
// The body: the drawing's own solids (styles/s6-symbolic cast.savely) as 3D hulls on SOMA's skeleton (tools/build.py).
// The motion: Kimodo's, carried by the engine as it is (engine/src: retarget, build, Skinner). On top of it, layers
// on the joints' turns, all the drawing's numbers or slow small life:
//   - the mood: the posture of the drawing's moods (stoop, neck forward, head, arms behind the back or at the watch),
//     each a set of joint turns from build.py, mixed and followed by critically damped springs;
//   - breathing: uneven breaths (3.4–5 s, the in-breath shorter than the out), the chest and the collarbones rising;
//   - talking: the jaw drops on the syllables of a phrase (only the chin's edge shows it: the face is not drawn).
// The look: one ink form; a rim cut from its own edge on the side of the lamp (the drawing's rule, made in screen
// space from the figure's mask, so it is always exactly one thin line on the silhouette); the warm signs (the watch,
// its chain, the loupe's glint) with their glows; a dusk world of fog layers, a street lamp, its pool of light and the
// figure's long shadow from it; grain and a vignette over everything.
import * as THREE from 'three';
import { makeSkeleton } from '../../../../engine/src/skeleton.js';
import { loadPack, readJSON } from '../../../../engine/src/pack.js';
import { makeBody } from '../../../../engine/src/body.js';
import { loadMotion, newSample } from '../../../../engine/src/motion.js';
import { makeRetarget, build } from '../../../../engine/src/retarget.js';
import { Skinner, normalsOf } from '../../../../engine/src/skin.js';
import { qMul, qConj, qAxisAngle, qRot, qNorm, getQ, setQ, getV } from '../../../../engine/src/math.js';

THREE.ColorManagement.enabled = false;
const DATA = new URL('data/', import.meta.url);

// the drawing's palette (scenes.py EMBER) and ink
export const PAL = {
  ink: '#10131b', top: '#1c1420', hor: '#6b4446', fog: '#8a5b55', ground: '#22171c', rim: '#f0b48a', warm: '#ffcf86',
  watch: '#f2b85c', chain: '#d9a557', glint: '#f3d9a4',
};
export const MOTIONS = [
  { id: 'walk', label: 'идёт', loop: true },
  { id: 'idle', label: 'стоит', loop: true },
  { id: 'bow', label: 'кланяется' },
  { id: 'wave', label: 'машет' },
  { id: 'stomp', label: 'топает' },
  { id: 'sit', label: 'садится' },
];

const col = s => new THREE.Color(s);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }

// ------------------------------------------------------------------ data
export async function loadSavely() {
  const sk = makeSkeleton(await readJSON(new URL('skeleton.json', DATA)));
  const { header: h, arrays: a } = await loadPack(new URL('savely.json', DATA));
  const body = makeBody({
    id: h.id, label: h.label, source: h.source, topology: h.topology, skeleton: sk,
    positions: a.positions, triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
    parts: { names: h.parts, weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
  });
  const poses = await readJSON(new URL('poses.json', DATA));
  return { sk, body, poses, part: a.part, partNames: h.parts };
}
const motionCache = new Map();
export function getMotion(id, sk) {
  if (!motionCache.has(id)) motionCache.set(id, loadMotion(new URL(`motions/${id}.json`, DATA), sk));
  return motionCache.get(id);
}

// ------------------------------------------------------------------ life: breathing, talking, moods
export const PHRASES = ['Так-так.', 'Опять отстают, голубчики.', 'Пружину бы сменить, да где ж её взять.', 'Ну ничего, ничего — подкрутим.', 'Время, оно ведь не ждёт.'];
const VOWEL = { а: 1, я: 1, о: .8, ё: .8, у: .55, ю: .55, е: .7, э: .7, и: .5, ы: .55 };

export class Life {
  constructor(data, seed = 7) {
    this.d = data; this.r = rng(seed);
    this.t = 0;
    // breathing: a list of breaths [start, length, depth]
    this.breaths = []; let b = 0; while (b < 600) { const L = 3.4 + 1.6 * this.r(); this.breaths.push([b, L, .75 + .35 * this.r()]); b += L; }
    // moods: current weights (springs) and targets
    this.keys = Object.keys(data.poses.moods);
    this.w = Object.fromEntries(this.keys.map(k => [k, 0])); this.v = Object.fromEntries(this.keys.map(k => [k, 0]));
    this.target = {};
    // talking
    this.talk = false; this.jaw = 0; this.jv = 0; this.seq = []; this.si = 0; this.left = 0; this.phrase = 0; this.nod = 0; this.nv = 0; this.nodKick = 0;
  }
  setMood(m, snap = false) {
    this.target = typeof m === 'string' ? (m ? { [m]: 1 } : {}) : (m || {});
    if (snap) for (const k of this.keys) { this.w[k] = this.target[k] || 0; this.v[k] = 0; }
  }
  breath(t = this.t) {
    // the chest's rise 0..1: in-breath ~40 % of the cycle (eased), out-breath slower, a short rest at the end
    let i = 0; while (i < this.breaths.length - 1 && this.breaths[i + 1][0] <= t) i++;
    const [s, L, dpt] = this.breaths[i], u = (t - s) / L;
    const v = u < .38 ? smooth(0, .38, u) : u < .9 ? 1 - smooth(.38, .9, u) : 0;
    return v * dpt;
  }
  readPhrase() {
    const txt = PHRASES[this.phrase++ % PHRASES.length].toLowerCase(), seq = [];
    let first = true;
    for (const ch of txt) {
      if (VOWEL[ch]) { seq.push([VOWEL[ch], .09 + .07 * this.r(), first]); first = false; }
      else if ('мбп'.includes(ch)) seq.push([0, .07 + .03 * this.r()]);
      else if (/[а-яё]/.test(ch)) seq.push([.25, .05 + .03 * this.r()]);
      else if (ch === ' ') seq.push([.2, .03]);
      else if (ch === ',' || ch === '—') seq.push([null, .25 + .1 * this.r()]);
      else if ('.?!'.includes(ch)) seq.push([null, .7 + .4 * this.r()]);
    }
    return seq;
  }
  step(dt) {
    const sub = Math.max(1, Math.ceil(dt / (1 / 240))), h = dt / sub;
    for (let k = 0; k < sub; k++) this.tick(h);
  }
  tick(dt) {
    this.t += dt;
    // moods: critically damped springs (ω 5 — a slow old man's change of posture)
    const om = 5;
    for (const k of this.keys) {
      const x = this.w[k], tg = this.target[k] || 0, a = om * om * (tg - x) - 2 * om * this.v[k];
      this.v[k] += a * dt; this.w[k] += this.v[k] * dt;
    }
    // talking: the jaw follows the syllables by a fast spring; a small nod on a phrase's first stress
    let goal = 0;
    if (this.talk) {
      if (this.si >= this.seq.length) { this.seq = this.readPhrase(); this.si = 0; this.left = this.seq[0][1]; }
      const [open, , first] = this.seq[this.si];
      goal = open == null ? 0 : open;
      if (first && this.left === this.seq[this.si][1]) this.nodKick = 1;
      this.left -= dt;
      if (this.left <= 0) { this.si++; if (this.si < this.seq.length) this.left = this.seq[this.si][1]; }
    }
    const oj = 38; { const a = oj * oj * (goal - this.jaw) - 2 * oj * this.jv; this.jv += a * dt; this.jaw += this.jv * dt; }
    const on = 9; { const a = on * on * (this.nodKick - this.nod) - 2 * on * this.nv; this.nv += a * dt; this.nod += this.nv * dt; this.nodKick = Math.max(0, this.nodKick - dt * 6); }
  }
}

// ------------------------------------------------------------------ poses
const X = [1, 0, 0], Z = [0, 0, 1];
function nlerpQs(list) {           // [[q, w]] → the weighted mean turn (signs to the first's side)
  let s = [0, 0, 0, 0], ref = null;
  for (const [q, w] of list) { if (!w) continue; ref ??= q; const sg = q[0] * ref[0] + q[1] * ref[1] + q[2] * ref[2] + q[3] * ref[3] < 0 ? -w : w; for (let i = 0; i < 4; i++) s[i] += sg * q[i]; }
  return ref ? qNorm(s) : [0, 0, 0, 1];
}
function slerpish(a, b, t) { return nlerpQs([[a, 1 - t], [b, t]]); }

export class Poser {
  constructor(data) {
    this.d = data; const { sk, body } = data;
    this.sk = sk; this.body = body; this.J = sk.J;
    this.retarget = makeRetarget(body, {});
    this.skinner = new Skinner(body, { method: 'lbs' });
    this.sample = newSample(sk.J);
    this.L = new Float64Array(sk.J * 4);
    this.positions = new Float32Array(body.N * 3);
    this.normals = new Float32Array(body.N * 3);
    const I = n => sk.index[n];
    this.trunk = ['Spine1', 'Spine2', 'Chest', 'Neck1', 'Neck2', 'Head'].map(I);
    this.arms = ['Left', 'Right'].flatMap(s => ['Shoulder', 'Arm', 'ForeArm', 'Hand'].map(n => I(s + n)));
    this.handKids = ['Left', 'Right'].map(s => sk.names.map((n, j) => j).filter(j => sk.names[j].startsWith(s + 'Hand') && sk.names[j] !== s + 'Hand'));
  }
  // a static pose from poses.json ({Q, hips})
  staticPose(p) {
    const J = this.J, pose = { Q: Float64Array.from(p.Q.flat()), P: new Float64Array(J * 3), floor: this.body.measures.floor };
    build(pose, this.body, p.hips);
    return pose;
  }
  locals(pose) {
    const { sk, L } = this;
    for (let j = 0; j < this.J; j++) { const p = sk.parent[j]; setQ(L, j, p < 0 ? getQ(pose.Q, j) : qMul(qConj(getQ(pose.Q, p)), getQ(pose.Q, j))); }
  }
  compose(pose) {
    const { sk, L } = this;
    for (let j = 0; j < this.J; j++) { const p = sk.parent[j]; setQ(pose.Q, j, p < 0 ? getQ(L, j) : qMul(getQ(pose.Q, p), getQ(L, j))); }
  }
  // layers on a pose's turns: moods (weights), breath (0..1), jaw (0..1), nod (0..1)
  layer(pose, life, opts = {}) {
    const { sk, L } = this, moods = this.d.poses.moods;
    this.locals(pose);
    const W = life ? life.w : (opts.moods || {});
    // trunk: the moods' turns added to the motion's
    let total = 0; for (const k in W) total += Math.max(0, W[k]);
    for (const j of this.trunk) {
      const name = sk.names[j];
      const list = [[[0, 0, 0, 1], Math.max(0, 1 - total)]];
      for (const k in W) if (W[k] > 0) list.push([moods[k].trunk[name], W[k]]);
      setQ(L, j, qMul(nlerpQs(list), getQ(L, j)));
    }
    // arms: where a mood holds them (behind the back, at the watch), they leave the motion's
    let aw = 0; for (const k in W) if (W[k] > 0) aw += W[k] * moods[k].arms;
    if (aw > 1e-3) {
      for (const j of this.arms) {
        const name = sk.names[j], list = [];
        for (const k in W) if (W[k] > 0 && moods[k].arms > 0) list.push([moods[k].armLocals[name], W[k] * moods[k].arms]);
        setQ(L, j, slerpish(getQ(L, j), nlerpQs(list), clamp(aw, 0, 1)));
      }
      // fingers: none of ours (the hand is one drop) — keep them on the hand
    }
    // breathing: the chest straightens a little and the collarbones lift on the in-breath; the head stays
    const br = life ? life.breath() : (opts.breath || 0), D = Math.PI / 180;
    if (br) {
      const tw = (n, ax, deg) => { const j = sk.index[n]; setQ(L, j, qMul(qAxisAngle(ax, deg * D * br), getQ(L, j))); };
      tw('Spine2', X, -1.1); tw('Chest', X, -1.6); tw('Neck1', X, 2.0); tw('Head', X, .7);
      tw('LeftShoulder', Z, 2.2); tw('RightShoulder', Z, -2.2);
      tw('LeftArm', Z, -2.2); tw('RightArm', Z, 2.2);
    }
    const jaw = life ? life.jaw : (opts.jaw || 0), nod = life ? life.nod : 0;
    if (jaw) { const j = sk.index.Jaw; setQ(L, j, qMul(qAxisAngle(X, jaw * 9 * D), getQ(L, j))); }
    if (nod) { const j = sk.index.Head; setQ(L, j, qMul(qAxisAngle(X, nod * 4 * D), getQ(L, j))); }
    this.compose(pose);
  }
  // the figure at a moment: a motion (clip, t frames) or a static pose; placed; skinned; on the floor
  frame({ clip = null, t = 0, stat = null, life = null, place = { position: [0, 0, 0], heading: 0 }, opts = {}, normals = false }) {
    let pose, hip;
    Object.assign(this.retarget.place, place);
    if (clip) {
      pose = this.retarget.pose(clip.sample(t, this.sample));
      hip = getV(pose.P, this.sk.index.Hips);
    } else {
      pose = this.staticPose(stat);
      hip = getV(pose.P, this.sk.index.Hips);
    }
    this.layer(pose, life, opts);
    build(pose, this.body, hip);
    this.retarget.placed(pose);
    this.skinner.skin(pose, this.positions);
    // on the floor: the lowest point where Kimodo's was (a static pose: on the ground)
    let lo = Infinity; const P = this.positions; for (let i = 1; i < P.length; i += 3) if (P[i] < lo) lo = P[i];
    const floor = clip ? pose.floor : place.position[1];
    const sh = floor - lo; for (let i = 1; i < P.length; i += 3) P[i] += sh;
    for (let j = 0; j < this.J; j++) pose.P[j * 3 + 1] += sh;
    if (normals) normalsOf(P, this.body.triangles, this.normals);
    this.pose = pose;
    return pose;
  }
  // a point at rest on a joint, now
  at(rest, joint) {
    const j = this.sk.index[joint], r = getV(this.body.joints, j), q = getQ(this.pose.Q, j);
    const v = qRot(q, [rest[0] - r[0], rest[1] - r[1], rest[2] - r[2]]);
    return [this.pose.P[j * 3] + v[0], this.pose.P[j * 3 + 1] + v[1], this.pose.P[j * 3 + 2] + v[2]];
  }
  dirOn(d, joint) { return qRot(getQ(this.pose.Q, this.sk.index[joint]), d); }
}

// ------------------------------------------------------------------ the stage
const VS_FIG = `varying float vDist; void main(){ vec4 w = modelMatrix * vec4(position,1.); vec4 mv = viewMatrix * w; vDist = -mv.z; gl_Position = projectionMatrix * mv; }`;
const FS_INK = `uniform vec3 ink; uniform vec3 fogCol; uniform float fogNear; uniform float fogFar; varying float vDist;
void main(){ float f = clamp((vDist - fogNear) / (fogFar - fogNear), 0., 1.); gl_FragColor = vec4(mix(ink, fogCol, f * .55), 1.); }`;
const FS_MASK = `varying float vDist; void main(){ gl_FragColor = vec4(1., vDist, 0., 1.); }`;
const VS_SHADED = `varying vec3 vN; varying float vDist; void main(){ vN = normalize(mat3(modelMatrix) * normal); vec4 mv = viewMatrix * modelMatrix * vec4(position,1.); vDist = -mv.z; gl_Position = projectionMatrix * mv; }`;
const FS_SHADED = `uniform vec3 base; varying vec3 vN; varying float vDist; void main(){ vec3 n = normalize(vN); float l = .45 + .45 * max(dot(n, normalize(vec3(.4,.8,.6))), 0.) + .12 * max(dot(n, normalize(vec3(-.6,.2,-.4))), 0.); gl_FragColor = vec4(base * l, 1.); }`;
// the figure's shadow from the lamp, flattened onto the ground
const VS_SHADOW = `uniform vec3 lamp; varying float vK; void main(){ vec4 w = modelMatrix * vec4(position,1.); float h = max(lamp.y - w.y, .05); float s = lamp.y / h; vec3 g = lamp + (w.xyz - lamp) * s; g.y = .002; vK = clamp(1. - (s - 1.) * .18, 0., 1.); gl_Position = projectionMatrix * viewMatrix * vec4(g, 1.); }`;
const FS_SHADOW = `uniform float alpha; varying float vK; void main(){ gl_FragColor = vec4(0.,0.,0., alpha * (.35 + .65 * vK)); }`;

const VS_SKY = `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position,1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; gl_Position.z = gl_Position.w; }`;
const FS_SKY = `uniform vec3 top; uniform vec3 hor; uniform vec3 fog; uniform vec3 cam; varying vec3 vW;
float h(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7))) * 43758.5453); }
void main(){ vec3 d = normalize(vW - cam); float e = d.y;
  vec3 c = mix(hor, top, smoothstep(-.02, .42, e));
  c = mix(c, fog, .35 * exp(-abs(e) * 14.));
  // a few dim stars high up
  vec2 g = vec2(atan(d.z, d.x) * 90., e * 90.); vec2 cell = floor(g); vec2 f = fract(g) - .5;
  float s = step(.985, h(cell)) * smoothstep(.12, 0., length(f)) * smoothstep(.2, .5, e);
  c += vec3(.75,.72,.78) * s * .5 * h(cell + 3.1);
  gl_FragColor = vec4(c, 1.); }`;
const VS_GROUND = `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position,1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`;
const FS_GROUND = `uniform vec3 ground; uniform vec3 fog; uniform vec3 warm; uniform vec3 lamp; uniform vec3 cam; uniform float pool; varying vec3 vW;
void main(){ float d = length(vW.xz - cam.xz);
  vec3 c = ground;
  float r = length(vW.xz - lamp.xz);
  c += warm * pool * (.28 * exp(-r * r / 2.6) + .07 * exp(-r * r / 22.));
  c = mix(c, fog, smoothstep(6., 70., d) * .8);
  gl_FragColor = vec4(c, 1.); }`;
const VS_BAND = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position,1.); }`;
const FS_BAND = `uniform vec3 c; uniform float op; varying vec2 vUv; void main(){ float s = sin(3.14159 * vUv.y); gl_FragColor = vec4(c, op * s * s); }`;

// the composite: the scene, the rim from the figure's mask, the glows, grain and vignette
const VS_Q = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`;
const FS_COMP = `precision highp float;
uniform sampler2D tScene; uniform sampler2D tFig; uniform vec2 res;
uniform vec2 lampPx; uniform float useLampDir; uniform vec2 lightDir; uniform float rimPx; uniform vec3 rimCol; uniform float rimK;
uniform vec4 glow[4]; uniform vec3 glowCol[4]; uniform float glowDepth[4]; uniform float glowBehind[4]; uniform int nGlow;
uniform float vign; uniform float grain; uniform float seed;
varying vec2 vUv;
float m(vec2 px){ return texture2D(tFig, px / res).r; }
float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233)) + seed) * 43758.5453); }
void main(){
  vec2 px = vUv * res;
  vec3 c = texture2D(tScene, vUv).rgb;
  vec4 F = texture2D(tFig, vUv);
  float mask = F.r;
  // the rim: the figure minus itself moved away from the light (the drawing's own way), softened over three steps
  vec2 dir = useLampDir > .5 ? normalize(lampPx - px + vec2(1e-4)) : normalize(lightDir);
  if (mask > 0.) {
    float o = 0.;
    o += 1. - m(px + dir * rimPx * .45);
    o += 1. - m(px + dir * rimPx * .8);
    o += 1. - m(px + dir * rimPx * 1.15);
    float rim = mask * clamp(o / 3., 0., 1.);
    c = mix(c, rimCol, clamp(rim * rimK, 0., 1.));
  }
  // glows: the lamp's behind the figure, the watch's and the glint's in front of it (unless the body hides them)
  for (int i = 0; i < 4; i++) {
    if (i >= nGlow) break;
    vec2 gp = glow[i].xy; float r = glow[i].z, k = glow[i].w;
    float d = length(px - gp) / r;
    float a = d < .25 ? mix(.55, .22, d / .25) : mix(.22, 0., clamp((d - .25) / .75, 0., 1.));
    float vis = 1.;
    if (glowBehind[i] > .5) vis = 1. - mask * .92;
    else { vec4 G = texture2D(tFig, gp / res); vis = (G.r > .5 && G.g < glowDepth[i] - .015) ? 0. : 1.; }
    c += glowCol[i] * a * k * vis;
  }
  // vignette and grain
  vec2 q = (vUv - .5) / .75; float dv = length(q);
  c *= 1. - vign * clamp((dv - .55) / .45, 0., 1.);
  float g = h(floor(px)) * .6 + h(floor(px * .5) + 7.) * .4;
  c += (g - .5) * grain;
  gl_FragColor = vec4(c, 1.);
}`;

function bandCylinder(radius, y0, y1, color, op, seg = 96) {
  const g = new THREE.CylinderGeometry(radius, radius, y1 - y0, seg, 1, true);
  g.translate(0, (y0 + y1) / 2, 0);
  const m = new THREE.ShaderMaterial({ vertexShader: VS_BAND, fragmentShader: FS_BAND, uniforms: { c: { value: col(color) }, op: { value: op } }, transparent: true, depthWrite: false, side: THREE.BackSide });
  return new THREE.Mesh(g, m);
}
function hillsRing(radius, base, amp, color, seed, step = .05) {
  const r = rng(seed), pts = [];
  let a = 0; while (a < Math.PI * 2 + step) { pts.push([a, base + amp * r()]); a += step * (.6 + .8 * r()); }
  // smooth the tops (the drawing's quadratic hills)
  const n = 360, verts = [], idx = [];
  const topAt = th => { let i = 0; while (i < pts.length - 2 && pts[i + 1][0] < th) i++; const [a0, y0] = pts[i], [a1, y1] = pts[i + 1]; const u = smooth(0, 1, (th - a0) / (a1 - a0)); return y0 + (y1 - y0) * u; };
  for (let i = 0; i <= n; i++) {
    const th = i / n * Math.PI * 2, x = Math.cos(th) * radius, z = Math.sin(th) * radius;
    verts.push(x, -2, z, x, topAt(th), z);
    if (i < n) { const o = i * 2; idx.push(o, o + 1, o + 2, o + 1, o + 3, o + 2); }
  }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3)); g.setIndex(idx);
  return new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: col(color), side: THREE.DoubleSide, fog: false }));
}

export class Stage {
  constructor(canvas, data) {
    this.d = data; this.canvas = canvas;
    const r = this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, stencil: true });
    r.outputColorSpace = THREE.LinearSRGBColorSpace; r.toneMapping = THREE.NoToneMapping;
    r.setPixelRatio(1);
    this.poser = new Poser(data);
    this.size = [800, 800];
    const P = PAL;
    // --- the figure
    const g = this.geo = new THREE.BufferGeometry();
    this.posAttr = new THREE.BufferAttribute(this.poser.positions, 3); this.posAttr.setUsage(THREE.DynamicDrawUsage);
    this.nrmAttr = new THREE.BufferAttribute(this.poser.normals, 3); this.nrmAttr.setUsage(THREE.DynamicDrawUsage);
    g.setAttribute('position', this.posAttr); g.setAttribute('normal', this.nrmAttr);
    g.setIndex(new THREE.BufferAttribute(data.body.triangles, 1));
    this.inkMat = new THREE.ShaderMaterial({ vertexShader: VS_FIG, fragmentShader: FS_INK, uniforms: { ink: { value: col(P.ink) }, fogCol: { value: col(P.fog) }, fogNear: { value: 8 }, fogFar: { value: 60 } } });
    this.maskMat = new THREE.ShaderMaterial({ vertexShader: VS_FIG, fragmentShader: FS_MASK });
    this.shadedMat = new THREE.ShaderMaterial({ vertexShader: VS_SHADED, fragmentShader: FS_SHADED, uniforms: { base: { value: col('#b9b3ad') } } });
    this.fig = new THREE.Mesh(g, this.inkMat); this.fig.frustumCulled = false;
    this.shadowMat = new THREE.ShaderMaterial({ vertexShader: VS_SHADOW, fragmentShader: FS_SHADOW, uniforms: { lamp: { value: new THREE.Vector3() }, alpha: { value: .5 } }, transparent: true, depthWrite: false,
      stencilWrite: true, stencilRef: 1, stencilFunc: THREE.NotEqualStencilFunc, stencilZPass: THREE.ReplaceStencilOp });
    this.shadow = new THREE.Mesh(g, this.shadowMat); this.shadow.frustumCulled = false; this.shadow.renderOrder = 1;
    // --- the signs
    this.watch = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 12), new THREE.MeshBasicMaterial({ color: col(P.watch) }));
    this.glint = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 10), new THREE.MeshBasicMaterial({ color: col(P.glint) }));
    this.beads = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 8, 6), new THREE.MeshBasicMaterial({ color: col(P.chain) }), 24);
    this.beads.frustumCulled = false;
    // --- the skeleton (for the steps)
    this.bones = new THREE.LineSegments(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0xd8322a, depthTest: false }));
    this.bones.renderOrder = 5; this.bones.visible = false;
    this.joints = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ color: 0xd8322a, size: 6, sizeAttenuation: false, depthTest: false }));
    this.joints.renderOrder = 5; this.joints.visible = false;
    // --- the world
    this.world = new THREE.Group();
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(300, 32, 16), new THREE.ShaderMaterial({ vertexShader: VS_SKY, fragmentShader: FS_SKY, side: THREE.BackSide, depthWrite: false,
      uniforms: { top: { value: col(P.top) }, hor: { value: col(P.hor) }, fog: { value: col(P.fog) }, cam: { value: new THREE.Vector3() } } }));
    this.sky.renderOrder = -10; this.world.add(this.sky);
    const mix = (a, b, t) => col(a).lerp(col(b), t).getStyle();
    // fog layers: far hills pale, near ones dark, a band of fog over each
    this.world.add(hillsRing(160, 6, 14, mix(P.hor, P.fog, .55), 3, .09));
    this.world.add(bandCylinder(150, 2, 22, P.fog, .45));
    this.world.add(hillsRing(95, 1, 7, mix(P.fog, P.ground, .45), 7, .07));
    this.world.add(bandCylinder(88, -1, 9, P.fog, .4));
    this.world.add(hillsRing(55, -.2, 2.6, mix(P.ground, P.fog, .22), 11, .05));
    this.world.add(bandCylinder(50, -1, 3.5, P.fog, .32));
    this.groundMat = new THREE.ShaderMaterial({ vertexShader: VS_GROUND, fragmentShader: FS_GROUND,
      uniforms: { ground: { value: col(P.ground) }, fog: { value: col(P.fog) }, warm: { value: col(P.warm) }, lamp: { value: new THREE.Vector3() }, cam: { value: new THREE.Vector3() }, pool: { value: 1 } } });
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), this.groundMat); ground.rotation.x = -Math.PI / 2; this.world.add(ground);
    // the street lamp: a dark post, an arm, a head with a warm bulb
    this.lampG = new THREE.Group();
    const inkM = new THREE.MeshBasicMaterial({ color: col(P.ink) });
    const post = new THREE.Mesh(new THREE.CylinderGeometry(.03, .045, 3.0, 12), inkM); post.position.y = 1.5; this.lampG.add(post);
    const arm = new THREE.Mesh(new THREE.BoxGeometry(.55, .035, .035), inkM); arm.position.set(-.26, 2.98, 0); this.lampG.add(arm);
    const head = new THREE.Mesh(new THREE.CylinderGeometry(.06, .16, .09, 20), inkM); head.position.set(-.5, 2.93, 0); this.lampG.add(head);
    const bulb = new THREE.Mesh(new THREE.SphereGeometry(.1, 20, 10), new THREE.MeshBasicMaterial({ color: col(P.warm) })); bulb.scale.set(1, .42, 1); bulb.position.set(-.5, 2.875, 0); this.lampG.add(bulb);
    this.bulbLocal = new THREE.Vector3(-.5, 2.86, 0);
    this.world.add(this.lampG);
    // --- the flat plate (the drawing's own sheet: a sky gradient, the floor band, a band of fog) for the drawing's views
    this.plate = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({ vertexShader: VS_Q, depthWrite: false, depthTest: false,
      fragmentShader: `uniform vec3 top; uniform vec3 hor; uniform vec3 ground; uniform vec3 fog; uniform float horY; uniform float fbH; varying vec2 vUv;
      void main(){ float y = 1. - vUv.y; vec3 c = y < horY ? mix(top, hor, y / horY) : ground;
        float u = (y - (horY - fbH * .5)) / fbH; if (u > 0. && u < 1.) { float a = u < .5 ? u * 2. : 2. - u * 2.; c = mix(c, fog, a * .4); }
        gl_FragColor = vec4(c, 1.); }`,
      uniforms: { top: { value: col(P.top) }, hor: { value: col(P.hor) }, ground: { value: col(P.ground) }, fog: { value: col(P.fog) }, horY: { value: .86 }, fbH: { value: .09 } } }));
    this.plate.frustumCulled = false; this.plate.renderOrder = -20;
    // --- scenes and targets
    this.scene = new THREE.Scene(); this.scene.add(this.world, this.plate, this.shadow, this.fig, this.watch, this.glint, this.beads, this.bones, this.joints);
    this.figScene = new THREE.Scene(); this.figMask = new THREE.Mesh(g, this.maskMat); this.figMask.frustumCulled = false; this.figScene.add(this.figMask);
    this.persp = new THREE.PerspectiveCamera(30, 1, .05, 1000);
    this.ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, -50, 50);
    this.comp = new THREE.ShaderMaterial({ vertexShader: VS_Q, fragmentShader: FS_COMP, depthTest: false, depthWrite: false, uniforms: {
      tScene: { value: null }, tFig: { value: null }, res: { value: new THREE.Vector2() }, lampPx: { value: new THREE.Vector2() }, useLampDir: { value: 1 }, lightDir: { value: new THREE.Vector2(1, .3) },
      rimPx: { value: 2 }, rimCol: { value: col(P.rim) }, rimK: { value: 1 },
      glow: { value: [0, 1, 2, 3].map(() => new THREE.Vector4()) }, glowCol: { value: [0, 1, 2, 3].map(() => new THREE.Color()) }, glowDepth: { value: [0, 0, 0, 0] }, glowBehind: { value: [0, 0, 0, 0] }, nGlow: { value: 0 },
      vign: { value: .5 }, grain: { value: .07 }, seed: { value: 0 } } });
    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.comp); this.quad.frustumCulled = false;
    this.qScene = new THREE.Scene(); this.qScene.add(this.quad); this.qCam = new THREE.Camera();
    this.opts = {};
  }
  resize(w, h) {
    if (this.size[0] === w && this.size[1] === h && this.rtS) return;
    this.size = [w, h]; this.renderer.setSize(w, h, false);
    this.rtS?.dispose(); this.rtF?.dispose();
    this.rtS = new THREE.WebGLRenderTarget(w, h, { samples: 4, stencilBuffer: true });
    this.rtF = new THREE.WebGLRenderTarget(w, h, { type: THREE.HalfFloatType, samples: 0, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter });
  }
  // put the figure (skinned positions are already in the poser), the signs and the camera; then draw
  draw(o) {
    const P = PAL, poser = this.poser, A = this.d.poses.accents;
    const [w, h] = this.size;
    const look = { world: true, rim: true, signs: true, grain: true, shaded: false, skeleton: false, ink: true, shadow: true, ...(o.look || {}) };
    // the figure
    this.posAttr.needsUpdate = true; if (look.shaded) this.nrmAttr.needsUpdate = true;
    this.geo.computeBoundingSphere();
    this.fig.material = look.shaded ? this.shadedMat : this.inkMat;
    this.fig.visible = look.ink || look.shaded;
    // signs: the watch in the left hand, its chain to the waistcoat pocket, the loupe's glint
    const wp = poser.at(A.watch.rest, A.watch.joint), pk = poser.at(A.pocket.rest, A.pocket.joint), gp = poser.at(A.glint.rest, A.glint.joint);
    const gd = poser.dirOn(A.glint.dir, 'Head');
    this.watch.position.set(...wp); this.watch.scale.setScalar(A.watch.r * .75);
    this.glint.position.set(...gp); this.glint.scale.setScalar(A.glint.r * .55);
    this.watch.visible = this.glint.visible = this.beads.visible = look.signs;
    // the chain: a sagging curve of fixed length from the pocket to the watch
    {
      const a = new THREE.Vector3(...pk), b = new THREE.Vector3(...wp), L = A.chain.length, d = a.distanceTo(b);
      const sag = d < L ? Math.sqrt(Math.max(0, (L * L - d * d))) * .5 : 0, n = 22, M = new THREE.Matrix4();
      for (let i = 0; i < n; i++) {
        const u = (i + .5) / n, p = a.clone().lerp(b, u); p.y -= sag * 4 * u * (1 - u);
        M.makeScale(.0028, .0028, .0028).setPosition(p); this.beads.setMatrixAt(i, M);
      }
      this.beads.count = n; this.beads.instanceMatrix.needsUpdate = true;
    }
    // the skeleton
    this.bones.visible = this.joints.visible = look.skeleton;
    if (look.skeleton) {
      const sk = this.d.sk, Pj = poser.pose.P, seg = [], pts = [];
      const keep = j => !/Hand(Thumb|Index|Middle|Ring|Pinky)|Eye|Jaw|ToeEnd/.test(sk.names[j]);
      for (let j = 0; j < sk.J; j++) { if (!keep(j)) continue; pts.push(Pj[j * 3], Pj[j * 3 + 1], Pj[j * 3 + 2]); const p = sk.parent[j]; if (p >= 0) seg.push(Pj[p * 3], Pj[p * 3 + 1], Pj[p * 3 + 2], Pj[j * 3], Pj[j * 3 + 1], Pj[j * 3 + 2]); }
      this.bones.geometry.setAttribute('position', new THREE.Float32BufferAttribute(seg, 3));
      this.joints.geometry.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
    }
    // the camera
    const v = o.view || { type: 'persp' };
    let cam;
    if (v.type === 'ortho') {
      // the drawing's projection: k px per cm, the feet at (cx, feetY) px, the figure turned by yaw (done by placing)
      const k = v.k * 100;     // px per metre
      cam = this.ortho;
      cam.left = -v.cx / k; cam.right = (w - v.cx) / k; cam.top = v.feetY / k; cam.bottom = -(h - v.feetY) / k;
      cam.position.set(0, 0, 20); cam.lookAt(0, 0, 0); cam.near = -50; cam.far = 100;
      cam.updateProjectionMatrix();
    } else {
      cam = this.persp;
      cam.fov = v.fov || 30; cam.aspect = w / h; cam.near = .05; cam.far = 1000; cam.updateProjectionMatrix();
      cam.position.set(...v.pos); cam.up.set(0, 1, 0); cam.lookAt(...v.target);
    }
    cam.updateMatrixWorld();
    // the world or the plate
    const plate = !!o.plate;
    this.world.visible = look.world && !plate;
    this.plate.visible = plate;
    if (plate) { this.plate.material.uniforms.horY.value = o.plate.horY; this.plate.material.uniforms.fbH.value = o.plate.fbH ?? .09; }
    const lamp = new THREE.Vector3(...(o.lamp || [1.2, 0, -1.6]));
    this.lampG.position.copy(lamp); this.lampG.rotation.y = o.lampYaw || 0; this.lampG.updateMatrixWorld();
    const bulb = this.bulbLocal.clone().applyMatrix4(this.lampG.matrixWorld);
    this.lampG.visible = look.world && !plate && o.lampVisible !== false;
    this.sky.position.copy(cam.position); this.sky.material.uniforms.cam.value.copy(cam.position);
    this.groundMat.uniforms.lamp.value.copy(bulb); this.groundMat.uniforms.cam.value.copy(cam.position);
    this.shadow.visible = look.world && !plate && look.shadow && this.fig.visible && !look.shaded;
    this.shadowMat.uniforms.lamp.value.copy(bulb);
    // --- passes
    const r = this.renderer;
    r.setClearColor(new THREE.Color(plate ? P.top : (look.world ? P.top : '#e9e4dc')), 1);
    r.setRenderTarget(this.rtS); r.clear(true, true, true); r.render(this.scene, cam);
    r.setClearColor(0x000000, 0); r.setRenderTarget(this.rtF); r.clear(true, true, true);
    if (this.fig.visible && !look.shaded) r.render(this.figScene, cam);
    // composite uniforms
    const U = this.comp.uniforms, toPx = p => { const q = new THREE.Vector3(...p).project(cam); return [(q.x * .5 + .5) * w, (q.y * .5 + .5) * h]; };
    const depthOf = p => new THREE.Vector3(...p).applyMatrix4(cam.matrixWorldInverse).z * -1;
    U.tScene.value = this.rtS.texture; U.tFig.value = this.rtF.texture; U.res.value.set(w, h);
    const lp = toPx(bulb.toArray());
    U.lampPx.value.set(lp[0], lp[1]);
    U.useLampDir.value = o.lightDir ? 0 : 1;
    if (o.lightDir) U.lightDir.value.set(o.lightDir[0], o.lightDir[1]);
    // the rim's width: the drawing's ~0.55 cm at the figure's distance, never under 1.2 px
    const hips = getV(poser.pose.P, this.d.sk.index.Hips);
    let pxPerM;
    if (v.type === 'ortho') pxPerM = v.k * 100;
    else pxPerM = h / (2 * Math.tan(cam.fov * Math.PI / 360) * Math.max(.5, depthOf(hips)));
    U.rimPx.value = clamp(.0055 * pxPerM * (o.rimScale || 1), 1.2, 9);
    // the rim is as bright as the lamp is behind him and near
    let rimK = 1;
    if (!o.lightDir) {
      const toLamp = bulb.clone().sub(new THREE.Vector3(...hips)), dist = toLamp.length();
      const view = new THREE.Vector3(...hips).sub(cam.position).normalize();
      const back = toLamp.normalize().dot(view);
      rimK = (.55 + .45 * smooth(-.7, .5, back)) * clamp(3.2 / dist, .55, 1.15);
    }
    U.rimK.value = look.rim ? rimK : 0;
    // glows
    const G = []; const pxPerMAt = p => v.type === 'ortho' ? v.k * 100 : h / (2 * Math.tan(cam.fov * Math.PI / 360) * Math.max(.3, depthOf(p)));
    if (look.world && !plate && o.lampVisible !== false) G.push([lp, 2.6 * pxPerMAt(bulb.toArray()), P.warm, 1.0, depthOf(bulb.toArray()), 1]);
    if (look.signs) {
      G.push([toPx(wp), A.watch.r * 9 * pxPerMAt(wp), P.watch, .9 * (o.watchGlow ?? 1), depthOf(wp), 0]);
      const camDir = new THREE.Vector3().subVectors(cam.position, new THREE.Vector3(...gp)).normalize();
      const facing = v.type === 'ortho' ? gd[2] : camDir.dot(new THREE.Vector3(...gd));
      if (facing > -.1) G.push([toPx(gp), A.glint.r * 6 * pxPerMAt(gp), P.glint, .8 * smooth(-.1, .4, facing), depthOf(gp), 0]);
    }
    U.nGlow.value = G.length;
    G.forEach(([p, rad, c, k, dpt, behind], i) => { U.glow.value[i].set(p[0], p[1], rad, k); U.glowCol.value[i].set(c); U.glowDepth.value[i] = dpt; U.glowBehind.value[i] = behind; });
    U.vign.value = look.grain ? (o.vign ?? .5) : 0; U.grain.value = look.grain ? (o.grain ?? .07) : 0; U.seed.value = (o.seed ?? 0) % 1000;
    r.setRenderTarget(o.target || null); r.render(this.qScene, this.qCam);
  }
}
