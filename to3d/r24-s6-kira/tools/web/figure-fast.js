// A character of the symbolic style (С6) in 3D — the figure, its life and its light. The way of Р8 (Савелий
// Петрович, to3d/r8-s6-savely), made to take any character of the style: what is the character's own is in
// character.js (palette, world, motions, phrases, how it breathes and looks about) and in data/poses.json (moods).
//
// The body: the drawing's own solids as 3D hulls on SOMA's skeleton (tools/build.py).
// The motion: Kimodo's, carried by the engine as it is (engine/src: retarget, build, Skinner). On top of it, layers
// on the joints' turns, all the drawing's numbers or slow small life:
//   - the mood: the posture of the drawing's moods, each a set of joint turns from build.py, mixed and followed by
//     critically damped springs. Standing, a mood is the whole body (legs too: a squat, a kick); on a motion it is
//     the trunk and the arms it holds, the legs stay Kimodo's;
//   - breathing: uneven breaths, the in-breath shorter than the out, the chest and the collarbones rising;
//   - looking about: now and then the head turns aside and comes back (the face is not drawn — the profile says it);
//   - talking: the jaw drops on the syllables of a phrase (only the chin's edge shows it).
// The look: one ink form; a rim cut from its own edge on the side of the light (the drawing's rule, made in screen
// space from the figure's mask, so it is always exactly one thin line on the silhouette); the signs in their one
// colour; a world of fog layers and one light (a street lamp, a lit window, a far town), its pool on the ground and
// the figure's long shadow from it; grain and a vignette over everything.
//
// This is the fast variant (fast.html, app-fast.js; view.html, app.js and figure.js beside it are the page as it was):
// the scene's picture is not multisampled. It is drawn twice larger and averaged down already (four samples a
// pixel), and four more samples on each of those cost the video card nearly all of a frame's time.
import * as THREE from 'three';
import { makeSkeleton } from '../../../../engine/src/skeleton.js';
import { loadPack, readJSON } from '../../../../engine/src/pack.js';
import { makeBody } from '../../../../engine/src/body.js';
import { loadMotion, newSample } from '../../../../engine/src/motion.js';
import { makeRetarget, build } from '../../../../engine/src/retarget.js';
import { Skinner, normalsOf } from '../../../../engine/src/skin.js';
import { qMul, qConj, qAxisAngle, qRot, qNorm, getQ, setQ, getV } from '../../../../engine/src/math.js';
import { CHAR } from './character.js';

THREE.ColorManagement.enabled = false;
const DATA = new URL('data/', import.meta.url);
export const PAL = { ink: '#10131b', ...CHAR.pal };
export const MOTIONS = CHAR.motions;

const col = s => new THREE.Color(s);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }

// ------------------------------------------------------------------ data
export async function loadFigure() {
  const sk = makeSkeleton(await readJSON(new URL('skeleton.json', DATA)));
  const { header: h, arrays: a } = await loadPack(new URL('figure.json', DATA));
  const body = makeBody({
    id: h.id, label: h.label, source: h.source, topology: h.topology, skeleton: sk,
    positions: a.positions, triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
    parts: { names: h.parts, weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
  });
  const poses = await readJSON(new URL('poses.json', DATA));
  // every mood's turns of each joint against its parent, and the same for the stands
  const localsOf = Q => Q.map((q, j) => { const p = sk.parent[j]; return p < 0 ? q : qMul(qConj(Q[p]), q); });
  for (const m of [poses.drawn, poses.rest, ...Object.values(poses.moods)]) m.L = localsOf(m.Q);
  return { sk, body, poses, part: a.part, partNames: h.parts };
}
const motionCache = new Map();
export function getMotion(id, sk) {
  if (!motionCache.has(id)) motionCache.set(id, loadMotion(new URL(`motions/${id}.json`, DATA), sk));
  return motionCache.get(id);
}

// ------------------------------------------------------------------ life: breathing, looking about, talking, moods
const VOWEL = { а: 1, я: 1, о: .8, ё: .8, у: .55, ю: .55, е: .7, э: .7, и: .5, ы: .55 };

export class Life {
  constructor(data, seed = 7) {
    this.d = data; this.r = rng(seed);
    this.t = 0;
    const lf = CHAR.life;
    // breathing: a list of breaths [start, length, depth]
    this.breaths = []; let b = 0; while (b < 600) { const L = lf.breath[0] + lf.breath[1] * this.r(); this.breaths.push([b, L, .75 + .35 * this.r()]); b += L; }
    // looking about: [start, length, turn aside (rad), nod (rad)], with quiet gaps between
    this.glances = []; let g = lf.glance.first ?? 2;
    while (g < 600) {
      const L = lf.glance.hold[0] + lf.glance.hold[1] * this.r(), side = (this.r() < (lf.glance.bias ?? .5) ? 1 : -1);
      this.glances.push([g, L, side * (lf.glance.yaw[0] + lf.glance.yaw[1] * this.r()) * Math.PI / 180, (lf.glance.nod[0] + lf.glance.nod[1] * this.r()) * Math.PI / 180]);
      g += L + lf.glance.gap[0] + lf.glance.gap[1] * this.r();
    }
    this.gy = 0; this.gyv = 0; this.gn = 0; this.gnv = 0; this.look = true;
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
    const P = CHAR.phrases, txt = P[this.phrase++ % P.length].toLowerCase(), seq = [];
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
    // moods: critically damped springs (how fast this character changes its posture)
    const om = CHAR.life.moodOmega;
    for (const k of this.keys) {
      const x = this.w[k], tg = this.target[k] || 0, a = om * om * (tg - x) - 2 * om * this.v[k];
      this.v[k] += a * dt; this.w[k] += this.v[k] * dt;
    }
    // looking about: the head goes to the glance's side quickly and comes back more slowly
    let gy = 0, gn = 0;
    if (this.look) for (const [s, L, y, n] of this.glances) { if (s > this.t) break; if (this.t < s + L) { gy = y; gn = n; } }
    { const o = gy ? 7 : 4.5, a = o * o * (gy - this.gy) - 2 * o * this.gyv; this.gyv += a * dt; this.gy += this.gyv * dt; }
    { const o = 5, a = o * o * (gn - this.gn) - 2 * o * this.gnv; this.gnv += a * dt; this.gn += this.gnv * dt; }
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
  // is a part of the figure seen now? (a part some moods show or hide: headphones on the head, the hands' pocket)
  shows(part) {
    const moods = this.d.poses.moods; let s = 0, h = 0;
    for (const k of this.keys) { const w = Math.max(0, this.w[k]); if (moods[k].show.includes(part)) s += w; if (moods[k].hide.includes(part)) h += w; }
    return this.d.poses.hidden.includes(part) ? s > .5 : h <= .5;
  }
}

// ------------------------------------------------------------------ poses
const X = [1, 0, 0], Y = [0, 1, 0], Z = [0, 0, 1];
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
    this.arms = ['Left', 'Right'].flatMap(s => ['Shoulder', 'Arm', 'ForeArm', 'Hand'].map(n => [I(s + n), s]));
  }
  locals(pose) {
    const { sk, L } = this;
    for (let j = 0; j < this.J; j++) { const p = sk.parent[j]; setQ(L, j, p < 0 ? getQ(pose.Q, j) : qMul(qConj(getQ(pose.Q, p)), getQ(pose.Q, j))); }
  }
  compose(pose) {
    const { sk, L } = this;
    for (let j = 0; j < this.J; j++) { const p = sk.parent[j]; setQ(pose.Q, j, p < 0 ? getQ(L, j) : qMul(getQ(pose.Q, p), getQ(L, j))); }
  }
  // standing: the whole body is the moods' mix over the stand (legs too), the pelvis where they put it
  stand(stat, W) {
    const J = this.J, moods = this.d.poses.moods, L = this.L;
    let total = 0; for (const k in W) total += Math.max(0, W[k]);
    const base = Math.max(0, 1 - total), sum = base + total, hip = [0, 0, 0];
    for (let i = 0; i < 3; i++) { hip[i] = stat.hips[i] * base; for (const k in W) if (W[k] > 0) hip[i] += moods[k].hips[i] * W[k]; hip[i] /= sum; }
    for (let j = 0; j < J; j++) {
      const list = [[stat.L[j], base]];
      for (const k in W) if (W[k] > 0) list.push([moods[k].L[j], W[k]]);
      setQ(L, j, nlerpQs(list));
    }
    return hip;
  }
  // on a motion: the moods' trunk turns added to the motion's; the arms a mood holds leave the motion's
  layer(W) {
    const { sk, L } = this, moods = this.d.poses.moods;
    let total = 0; for (const k in W) total += Math.max(0, W[k]);
    for (const j of this.trunk) {
      const name = sk.names[j];
      const list = [[[0, 0, 0, 1], Math.max(0, 1 - total)]];
      for (const k in W) if (W[k] > 0) list.push([moods[k].trunk[name], W[k]]);
      setQ(L, j, qMul(nlerpQs(list), getQ(L, j)));
    }
    for (const [j, side] of this.arms) {
      let aw = 0; const name = sk.names[j], list = [];
      for (const k in W) if (W[k] > 0 && moods[k].arms[side] > 0) { const w = W[k] * moods[k].arms[side]; aw += w; list.push([moods[k].armLocals[name], w]); }
      if (aw > 1e-3) setQ(L, j, slerpish(getQ(L, j), nlerpQs(list), clamp(aw, 0, 1)));
    }
  }
  // small life on the turns: breath (0..1), a glance aside, the jaw, a nod
  alive(life, opts = {}) {
    const { sk, L } = this, D = Math.PI / 180;
    const tw = (n, ax, rad) => { const j = sk.index[n]; setQ(L, j, qMul(qAxisAngle(ax, rad), getQ(L, j))); };
    // breathing: the chest straightens a little and the collarbones lift on the in-breath; the head stays
    const br = (life ? life.breath() : (opts.breath || 0)) * CHAR.life.breathDepth * D;
    if (br) {
      tw('Spine2', X, -1.1 * br); tw('Chest', X, -1.6 * br); tw('Neck1', X, 2.0 * br); tw('Head', X, .7 * br);
      tw('LeftShoulder', Z, 2.2 * br); tw('RightShoulder', Z, -2.2 * br);
      tw('LeftArm', Z, -2.2 * br); tw('RightArm', Z, 2.2 * br);
    }
    if (life && (life.gy || life.gn)) {
      tw('Neck1', Y, .2 * life.gy); tw('Neck2', Y, .25 * life.gy); tw('Head', Y, .55 * life.gy); tw('Head', X, life.gn);
    }
    const jaw = life ? life.jaw : (opts.jaw || 0), nod = life ? life.nod : 0;
    if (jaw) tw('Jaw', X, jaw * CHAR.life.jawDeg * D);
    if (nod) tw('Head', X, nod * 4 * D);
  }
  // the figure at a moment: a motion (clip, t frames) or a stand; placed; skinned; on the floor
  frame({ clip = null, t = 0, stat = null, life = null, quiet = false, place = { position: [0, 0, 0], heading: 0 }, opts = {}, normals = false }) {
    let pose, hip;
    Object.assign(this.retarget.place, place);
    const W = life ? life.w : (opts.moods || {});
    if (clip) {
      pose = this.retarget.pose(clip.sample(t, this.sample));
      hip = getV(pose.P, this.sk.index.Hips);
      this.locals(pose);
      this.layer(W);
    } else {
      pose = this.still ??= { Q: new Float64Array(this.J * 4), P: new Float64Array(this.J * 3), floor: this.body.measures.floor };
      pose.floor = this.body.measures.floor;
      hip = this.stand(stat, W);
    }
    if (!quiet) this.alive(life, opts);
    this.compose(pose);
    build(pose, this.body, hip);
    this.retarget.placed(pose);
    this.skinner.skin(pose, this.positions);
    // on the floor: the lowest point where Kimodo's was (a stand: on the ground)
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
  quatOf(joint) { return getQ(this.pose.Q, this.sk.index[joint]); }
}

// ------------------------------------------------------------------ the stage
const VS_FIG = `varying float vDist; void main(){ vec4 w = modelMatrix * vec4(position,1.); vec4 mv = viewMatrix * w; vDist = -mv.z; gl_Position = projectionMatrix * mv; }`;
const FS_INK = `uniform vec3 ink; uniform vec3 fogCol; uniform float fogNear; uniform float fogFar; varying float vDist;
void main(){ float f = clamp((vDist - fogNear) / (fogFar - fogNear), 0., 1.); gl_FragColor = vec4(mix(ink, fogCol, f * .55), 1.); }`;
// the figure's mask: r — the ink form, g — how far it is, b — a sign in its own colour lying over the form
const FS_MASK = `uniform float sign; varying float vDist; void main(){ gl_FragColor = vec4(1. - sign, vDist, sign, 1.); }`;
const VS_SHADED = `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position,1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`;
// the construction seen as it is: every hull flat-shaded by its own faces
const FS_SHADED = `uniform vec3 base; uniform vec3 camPos; varying vec3 vW; void main(){ vec3 n = normalize(cross(dFdx(vW), dFdy(vW))); if (dot(n, camPos - vW) < 0.) n = -n;
  float l = .42 + .5 * max(dot(n, normalize(vec3(.5,.75,.6))), 0.) + .14 * max(dot(n, normalize(vec3(-.6,.2,-.5))), 0.); gl_FragColor = vec4(base * l, 1.); }`;
// the figure's shadow from the lamp, flattened onto the ground
const VS_SHADOW = `uniform vec3 lamp; uniform float fade; varying float vK; void main(){ vec4 w = modelMatrix * vec4(position,1.); float h = max(lamp.y - w.y, .05); float s = lamp.y / h; vec3 g = lamp + (w.xyz - lamp) * s; g.y = .002; vK = clamp(1. - (s - 1.) * fade, 0., 1.); gl_Position = projectionMatrix * viewMatrix * vec4(g, 1.); }`;
const FS_SHADOW = `uniform float alpha; uniform float floorK; varying float vK; void main(){ gl_FragColor = vec4(0.,0.,0., alpha * (floorK + (1. - floorK) * vK) * smoothstep(0., .08, vK + floorK)); }`;

const VS_SKY = `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position,1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; gl_Position.z = gl_Position.w; }`;
const FS_SKY = `uniform vec3 top; uniform vec3 hor; uniform vec3 fog; uniform vec3 cam; varying vec3 vW;
float h(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7))) * 43758.5453); }
void main(){ vec3 d = normalize(vW - cam); float e = d.y;
  vec3 c = mix(hor, top, smoothstep(-.02, .42, e));
  c = mix(c, fog, .22 * exp(-abs(e) * 14.));
  // a few dim stars high up
  vec2 g = vec2(atan(d.z, d.x) * 90., e * 90.); vec2 cell = floor(g); vec2 f = fract(g) - .5;
  float s = step(.985, h(cell)) * smoothstep(.12, 0., length(f)) * smoothstep(.2, .5, e);
  c += vec3(.75,.72,.78) * s * .5 * h(cell + 3.1);
  gl_FragColor = vec4(c, 1.); }`;
const VS_GROUND = `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position,1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`;
const FS_GROUND = `uniform vec3 ground; uniform vec3 fog; uniform vec3 warm; uniform vec3 lamp; uniform vec3 cam; uniform float pool; uniform float poolR; varying vec3 vW;
void main(){ float d = length(vW.xz - cam.xz);
  vec3 c = ground;
  float r = length(vW.xz - lamp.xz);
  c += warm * pool * (.2 * exp(-r * r / (2.6 * poolR)) + .04 * exp(-r * r / (22. * poolR)));
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
uniform float vign; uniform float grain; uniform float seed; uniform vec3 contact; uniform float ss;
varying vec2 vUv;
float m(vec2 px){ return texture2D(tFig, px / res).r; }
float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233)) + seed) * 43758.5453); }
void main(){
  vec2 px = vUv * res;
  vec3 c = texture2D(tScene, vUv).rgb;
  vec4 F = texture2D(tFig, vUv);
  float mask = F.r;
  if (contact.z > 0.) { vec2 e = (px - contact.xy) / vec2(contact.z, contact.z * .12); float a = .45 * (1. - smoothstep(.8, 1.05, length(e))); c = mix(c, vec3(0.), a * (1. - mask)); }
  // the rim: the figure minus itself moved away from the light (the drawing's own way), softened over three steps
  vec2 dir = useLampDir > .5 ? normalize(lampPx - px + vec2(1e-4)) : lightDir;
  if (mask > 0.) {
    // a pixel is on the rim when the figure is not there a rim's width toward the light (bilinear: soft, not jagged)
    vec4 T = texture2D(tFig, (px + dir * rimPx) / res);
    float rim = mask * (1. - T.r) * (1. - T.b);
    c = mix(c, rimCol, clamp(rim * rimK, 0., 1.));
  }
  // glows: the lamp's behind the figure, the watch's and the glint's in front of it (unless the body hides them)
  for (int i = 0; i < 4; i++) {
    if (i >= nGlow) break;
    vec2 gp = glow[i].xy; float r = glow[i].z, k = glow[i].w;
    float d = length(px - gp) / r;
    float a = d < .25 ? mix(.55, .22, d / .25) : mix(.22, 0., clamp((d - .25) / .75, 0., 1.));
    float vis = 1.;
    if (glowBehind[i] > .5) vis = 1. - max(mask, F.b) * .92;
    else { vec4 G = texture2D(tFig, gp / res); vis = (G.r > .5 && G.g < glowDepth[i] - .015) ? 0. : 1.; }
    c += glowCol[i] * a * k * vis;
  }
  // vignette and grain
  vec2 q = (vUv - .5) / .75; float dv = length(q);
  c *= 1. - vign * clamp((dv - .55) / .45, 0., 1.);
  vec2 gp = floor(px / ss); float g = h(gp) * .6 + h(floor(gp * .5) + 7.) * .4;
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

// ------------------------------------------------------------------ the one light of the world
// each: {group, light (where the rim and the shadow come from, in the group), glow: {at, r (m), col, k}, turns}
function lightLamp(P, w) {
  // a street lamp 2.6 m high, as in the drawing: its head just over a man's head
  const g = new THREE.Group(), inkM = new THREE.MeshBasicMaterial({ color: col(P.ink) }), LH = 2.6;
  const post = new THREE.Mesh(new THREE.CylinderGeometry(.03, .045, LH, 12), inkM); post.position.y = LH / 2; g.add(post);
  const arm = new THREE.Mesh(new THREE.BoxGeometry(.5, .035, .035), inkM); arm.position.set(-.24, LH - .02, 0); g.add(arm);
  const head = new THREE.Mesh(new THREE.CylinderGeometry(.05, .14, .08, 20), inkM); head.position.set(-.46, LH - .07, 0); g.add(head);
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(.09, 20, 10), new THREE.MeshBasicMaterial({ color: col(w.col || P.warm) })); bulb.scale.set(1, .42, 1); bulb.position.set(-.46, LH - .12, 0); g.add(bulb);
  const at = new THREE.Vector3(-.46, LH - .14, 0);
  return { group: g, light: at, glow: { at, r: 2.3, col: w.col || P.warm, k: .85 }, turns: false };
}
function lightWindow(P, w) {
  // a tall lit window standing alone in the fog, as on the drawing's sheet: a pale warm sheet with a dark cross.
  // No wall: the style keeps only what speaks. It always faces us (a flat light, like the moon).
  const g = new THREE.Group(), inkM = new THREE.MeshBasicMaterial({ color: col(P.ink) });
  const W = w.w ?? 1.25, H = w.h ?? 2.5, y0 = w.y0 ?? .5;
  const pane = new THREE.Mesh(new THREE.PlaneGeometry(W, H), new THREE.MeshBasicMaterial({ color: col(w.col || '#f4dcc0') })); pane.position.y = y0 + H / 2; g.add(pane);
  const v = new THREE.Mesh(new THREE.PlaneGeometry(.035, H), inkM); v.position.set(0, y0 + H / 2, .004); g.add(v);
  const h = new THREE.Mesh(new THREE.PlaneGeometry(W, .035), inkM); h.position.set(0, y0 + H * .54, .004); g.add(h);
  return { group: g, light: new THREE.Vector3(0, y0 + H * .92, 0), glow: { at: new THREE.Vector3(0, y0 + H * .55, 0), r: w.glowR ?? 3.2, col: w.glow || '#ffe7c8', k: w.glowK ?? .7 }, turns: true };
}
function lightTown(P, w) {
  // the far blocks of a town with their lit windows and its glow over the roofs — the light she has turned from
  const g = new THREE.Group(), r = rng(8), blockCol = col(w.block || '#2a2238').lerp(col(P.fog), .12);
  const pos = [], colr = [], idx = [];
  const quad = (x, y, z, ww, hh, c) => { const o = pos.length / 3; pos.push(x, y, z, x + ww, y, z, x + ww, y + hh, z, x, y + hh, z); for (let i = 0; i < 4; i++) colr.push(c.r, c.g, c.b); idx.push(o, o + 1, o + 2, o, o + 2, o + 3); };
  let x = -(w.span ?? 30) / 2;
  while (x < (w.span ?? 30) / 2) {
    const bw = 2 + 2.8 * r(), bh = 3 + 7 * r() * r() + (r() < .22 ? 4.5 : 0);
    quad(x, -1, 0, bw, bh + 1, blockCol);
    const lit = col(w.lit || '#f2c88e');
    for (let k = 0; k < bh * .9; k++) { const c = blockCol.clone().lerp(lit, .45 + .45 * r()); quad(x + .3 + (bw - .95) * r(), .6 + (bh - 1.4) * r(), .02, .3, .3, c); }
    x += bw + (r() < .35 ? 1.2 + 3 * r() : .25);
  }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.Float32BufferAttribute(colr, 3)); geo.setIndex(idx);
  g.add(new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide })));
  const at = new THREE.Vector3(0, w.glowY ?? 7, 0);
  return { group: g, light: new THREE.Vector3(0, w.lightY ?? 12, 0), glow: { at, r: w.glowR ?? 17, col: w.glow || '#8f7fb4', k: w.glowK ?? .7 }, turns: true };
}
const LIGHTS = { lamp: lightLamp, window: lightWindow, town: lightTown };

export class Stage {
  constructor(canvas, data) {
    this.d = data; this.canvas = canvas;
    const r = this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, stencil: true });
    r.outputColorSpace = THREE.LinearSRGBColorSpace; r.toneMapping = THREE.NoToneMapping;
    r.setPixelRatio(1);
    this.poser = new Poser(data);
    this.size = [800, 800];
    const P = PAL, poses = data.poses, WLD = CHAR.world;
    // --- the figure: the ink form, the parts some moods show or hide, the signs in their own colour
    this.posAttr = new THREE.BufferAttribute(this.poser.positions, 3); this.posAttr.setUsage(THREE.DynamicDrawUsage);
    this.nrmAttr = new THREE.BufferAttribute(this.poser.normals, 3); this.nrmAttr.setUsage(THREE.DynamicDrawUsage);
    this.inkMat = new THREE.ShaderMaterial({ vertexShader: VS_FIG, fragmentShader: FS_INK, uniforms: { ink: { value: col(P.ink) }, fogCol: { value: col(P.fog) }, fogNear: { value: 8 }, fogFar: { value: 60 } } });
    const maskMat = sign => new THREE.ShaderMaterial({ vertexShader: VS_FIG, fragmentShader: FS_MASK, uniforms: { sign: { value: sign } } });
    this.maskInk = maskMat(0); this.maskSign = maskMat(1);
    this.shadedMat = new THREE.ShaderMaterial({ vertexShader: VS_SHADED, fragmentShader: FS_SHADED, uniforms: { base: { value: col('#b9b3ad') }, camPos: { value: new THREE.Vector3() } } });
    this.shadowMat = new THREE.ShaderMaterial({ vertexShader: VS_SHADOW, fragmentShader: FS_SHADOW, uniforms: { lamp: { value: new THREE.Vector3() }, alpha: { value: WLD.shadow?.alpha ?? .42 }, fade: { value: WLD.shadow?.fade ?? .18 }, floorK: { value: WLD.shadow?.floor ?? .35 } }, transparent: true, depthWrite: false,
      stencilWrite: true, stencilRef: 1, stencilFunc: THREE.NotEqualStencilFunc, stencilZPass: THREE.ReplaceStencilOp });
    const toggled = new Set(poses.hidden); for (const m of Object.values(poses.moods)) for (const p of [...m.show, ...m.hide]) toggled.add(p);
    const tri = data.body.triangles, part = data.part, byGroup = new Map();
    for (let i = 0; i < tri.length; i += 3) {
      const name = data.partNames[part[tri[i]]], key = poses.signParts[name] || toggled.has(name) ? name : 'ink';
      if (!byGroup.has(key)) byGroup.set(key, []);
      byGroup.get(key).push(tri[i], tri[i + 1], tri[i + 2]);
    }
    this.scene = new THREE.Scene(); this.figScene = new THREE.Scene();
    this.groups = [];
    for (const [name, list] of byGroup) {
      const g = new THREE.BufferGeometry(); g.setAttribute('position', this.posAttr); g.setAttribute('normal', this.nrmAttr); g.setIndex(list);
      const signCol = poses.signParts[name];
      const G = { name, geo: g, sign: !!signCol, toggled: toggled.has(name), signMat: signCol ? new THREE.MeshBasicMaterial({ color: col(signCol) }) : null };
      G.fig = new THREE.Mesh(g, this.inkMat); G.mask = new THREE.Mesh(g, signCol ? this.maskSign : this.maskInk); G.shadow = new THREE.Mesh(g, this.shadowMat); G.shadow.renderOrder = 1;
      for (const m of [G.fig, G.mask, G.shadow]) m.frustumCulled = false;
      this.scene.add(G.shadow, G.fig); this.figScene.add(G.mask);
      this.groups.push(G);
    }
    // --- the signs that are points of light (lenses, a glint): a small bright body on a joint
    this.lights = poses.accents.map(a => {
      const mat = new THREE.MeshBasicMaterial({ color: col(a.col), transparent: true, opacity: .9 }), geo = new THREE.SphereGeometry(1, 20, 12);
      const o = { a, mesh: new THREE.Mesh(geo, mat), mask: new THREE.Mesh(geo, this.maskSign) };
      o.mesh.renderOrder = 2; this.scene.add(o.mesh); this.figScene.add(o.mask);
      return o;
    });
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
    const hk = WLD.hills ?? 1;
    this.world.add(hillsRing(160, 6 * hk, 14 * hk, mix(P.hor, P.fog, .55), 3, .09));
    this.world.add(bandCylinder(150, 2, 22, P.fog, .45));
    this.world.add(hillsRing(95, 1 * hk, 7 * hk, mix(P.fog, P.ground, .45), 7, .07));
    this.world.add(bandCylinder(88, -1, 9, P.fog, .4));
    this.world.add(hillsRing(55, -.2, 2.6 * hk, mix(P.ground, P.fog, .22), 11, .05));
    this.world.add(bandCylinder(50, -1, 3.5, P.fog, .32));
    this.groundMat = new THREE.ShaderMaterial({ vertexShader: VS_GROUND, fragmentShader: FS_GROUND,
      uniforms: { ground: { value: col(P.ground) }, fog: { value: col(P.fog) }, warm: { value: col(WLD.poolCol || P.warm) }, lamp: { value: new THREE.Vector3() }, cam: { value: new THREE.Vector3() }, pool: { value: WLD.pool ?? 1 }, poolR: { value: WLD.poolR ?? 1 } } });
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), this.groundMat); ground.rotation.x = -Math.PI / 2; this.world.add(ground);
    this.light = LIGHTS[WLD.kind](P, WLD);
    this.lampG = this.light.group; this.world.add(this.lampG);
    // --- the flat plate (the drawing's own sheet: a sky gradient, the floor band, a band of fog) for the drawing's views
    this.plate = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({ vertexShader: VS_Q, depthWrite: false, depthTest: false,
      fragmentShader: `uniform vec3 top; uniform vec3 hor; uniform vec3 ground; uniform vec3 fog; uniform float horY; uniform float fbH; uniform float fbOp; varying vec2 vUv;
      void main(){ float y = 1. - vUv.y; vec3 c = y < horY ? mix(top, hor, y / horY) : ground;
        float u = (y - (horY - fbH * .5)) / fbH; if (u > 0. && u < 1.) { float a = u < .5 ? u * 2. : 2. - u * 2.; c = mix(c, fog, a * fbOp); }
        gl_FragColor = vec4(c, 1.); }`,
      uniforms: { top: { value: col(P.top) }, hor: { value: col(P.hor) }, ground: { value: col(P.ground) }, fog: { value: col(P.fog) }, horY: { value: .86 }, fbH: { value: .09 }, fbOp: { value: .4 } } }));
    this.plate.frustumCulled = false; this.plate.renderOrder = -20;
    // --- scenes and targets
    this.scene.add(this.world, this.plate, this.bones, this.joints);
    this.persp = new THREE.PerspectiveCamera(30, 1, .05, 1000);
    this.ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, -50, 50);
    this.comp = new THREE.ShaderMaterial({ vertexShader: VS_Q, fragmentShader: FS_COMP, depthTest: false, depthWrite: false, uniforms: {
      tScene: { value: null }, tFig: { value: null }, res: { value: new THREE.Vector2() }, lampPx: { value: new THREE.Vector2() }, useLampDir: { value: 1 }, lightDir: { value: new THREE.Vector2(1, .3) },
      rimPx: { value: 2 }, rimCol: { value: col(P.rim) }, rimK: { value: 1 },
      glow: { value: [0, 1, 2, 3].map(() => new THREE.Vector4()) }, glowCol: { value: [0, 1, 2, 3].map(() => new THREE.Color()) }, glowDepth: { value: [0, 0, 0, 0] }, glowBehind: { value: [0, 0, 0, 0] }, nGlow: { value: 0 },
      vign: { value: .5 }, grain: { value: .07 }, seed: { value: 0 }, ss: { value: 2 }, contact: { value: new THREE.Vector3() } } });
    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.comp); this.quad.frustumCulled = false;
    this.qScene = new THREE.Scene(); this.qScene.add(this.quad); this.qCam = new THREE.Camera();
    this.down = new THREE.ShaderMaterial({ vertexShader: VS_Q, fragmentShader: 'uniform sampler2D t; varying vec2 vUv; void main(){ gl_FragColor = vec4(texture2D(t, vUv).rgb, 1.); }', uniforms: { t: { value: null } }, depthTest: false, depthWrite: false });
    const dq = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.down); dq.frustumCulled = false; this.dScene = new THREE.Scene(); this.dScene.add(dq);
  }
  // ss: everything is drawn ss times larger and averaged down (the rim is cut from a mask: smooth only so)
  resize(w, h, ss = 2) {
    if (this.size[0] === w && this.size[1] === h && this.ss === ss && this.rtS) return;
    this.size = [w, h]; this.ss = ss; this.renderer.setSize(w, h, false);
    this.rtS?.dispose(); this.rtF?.dispose(); this.rtC?.dispose();
    const W = w * ss, H = h * ss;
    this.rtS = new THREE.WebGLRenderTarget(W, H, { stencilBuffer: true });
    this.rtF = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 0, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter });
    this.rtC = new THREE.WebGLRenderTarget(W, H, { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter });
  }
  // put the figure (skinned positions are already in the poser), the signs and the camera; then draw
  // o.shows(part) — is a part that moods show or hide seen now; o.pal — another sheet's colours (the plate, the rim)
  draw(o) {
    const P = { ...PAL, ...(o.pal || {}) }, poser = this.poser;
    const ss = this.ss, w = this.size[0] * ss, h = this.size[1] * ss;
    const look = { world: true, rim: true, signs: true, grain: true, shaded: false, skeleton: false, ink: true, shadow: true, ...(o.look || {}) };
    const v = o.view || { type: 'persp' }, plate = !!o.plate;
    // the figure
    this.posAttr.needsUpdate = true; if (look.shaded) this.nrmAttr.needsUpdate = true;
    const inWorld = look.world && !plate;
    let figSeen = false;
    for (const G of this.groups) {
      const seen = (look.ink || look.shaded) && (!G.toggled || !o.shows || o.shows(G.name)) && (!G.sign || look.signs);
      G.geo.computeBoundingSphere();
      G.fig.visible = seen; G.fig.material = G.sign ? G.signMat : (look.shaded ? this.shadedMat : this.inkMat);
      G.mask.visible = seen && !look.shaded;
      G.shadow.visible = seen && inWorld && look.shadow && !look.shaded;
      figSeen ||= seen;
    }
    // the camera
    let cam;
    if (v.type === 'ortho') {
      // the drawing's projection: k px per cm, the feet at (cx, feetY) px, the figure turned by yaw (done by placing)
      const k = v.k * 100 * ss;     // px per metre (drawn ss times larger)
      cam = this.ortho;
      const cx = v.cx * ss, fy = v.feetY * ss;
      cam.left = -cx / k; cam.right = (w - cx) / k; cam.top = fy / k; cam.bottom = -(h - fy) / k;
      cam.position.set(0, 0, 20); cam.lookAt(0, 0, 0); cam.near = -50; cam.far = 100;
      cam.updateProjectionMatrix();
    } else {
      cam = this.persp;
      cam.fov = v.fov || 30; cam.aspect = w / h; cam.near = .05; cam.far = 1000; cam.updateProjectionMatrix();
      cam.position.set(...v.pos); cam.up.set(0, 1, 0); cam.lookAt(...v.target);
    }
    cam.updateMatrixWorld();
    this.inkMat.uniforms.fogNear.value = v.type === 'ortho' ? 1e5 : 8; this.inkMat.uniforms.fogFar.value = v.type === 'ortho' ? 2e5 : 60;   // the drawing's sheet has no air
    this.shadedMat.uniforms.camPos.value.copy(v.type === 'ortho' ? new THREE.Vector3(0, 0, 1000) : cam.position);
    const pxPerMAt = p => v.type === 'ortho' ? v.k * 100 * ss : h / (2 * Math.tan(cam.fov * Math.PI / 360) * Math.max(.3, depthOf(p)));
    const depthOf = p => new THREE.Vector3(...p).applyMatrix4(cam.matrixWorldInverse).z * -1;
    // the lenses: a lens seen at an angle is a thin ellipse; facing us it would read as an eye, so only the thin
    // bright edge of the frame is left (the drawing's rule)
    for (const L of this.lights) {
      const a = L.a, p = poser.at(a.rest, a.joint), q = poser.quatOf(a.joint), fwd = poser.dirOn(a.dir, a.joint);
      const toCam = v.type === 'ortho' ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3().subVectors(cam.position, new THREE.Vector3(...p)).normalize();
      const c = Math.abs(toCam.dot(new THREE.Vector3(...fwd))), flat = smooth(.62, .88, c);
      const sy = a.kind === 'lens' ? a.r * .5 * (1 - flat) + .0022 * flat : a.r * .55, sx = a.kind === 'lens' ? a.r : a.r * .55;
      for (const m of [L.mesh, L.mask]) { m.position.set(...p); m.quaternion.set(...q); m.scale.set(sx, sy, a.kind === 'lens' ? a.r * .25 : sx); }
      L.mesh.material.opacity = a.kind === 'lens' ? .85 - .3 * flat : 1;
      L.mesh.visible = look.signs; L.mask.visible = look.signs && !look.shaded;
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
    // the world or the plate
    this.world.visible = inWorld;
    this.plate.visible = plate;
    if (plate) { const U = this.plate.material.uniforms; U.horY.value = o.plate.horY; U.fbH.value = o.plate.fbH ?? .09; U.fbOp.value = o.plate.fbOp ?? .4; for (const k of ['top', 'hor', 'ground', 'fog']) U[k].value.set(P[k]); }
    const lamp = new THREE.Vector3(...(o.lamp || [1.2, 0, -1.6]));
    this.lampG.position.copy(lamp);
    // a flat light faces us: the window turns with the camera, the town looks at the figure's place
    this.lampG.rotation.y = this.light.turns ? Math.atan2(cam.position.x - lamp.x, cam.position.z - lamp.z) : (o.lampYaw || 0);
    if (this.light.turns && CHAR.world.kind === 'town') this.lampG.rotation.y = Math.atan2(-lamp.x, -lamp.z);
    this.lampG.updateMatrixWorld();
    const bulb = this.light.light.clone().applyMatrix4(this.lampG.matrixWorld), glowAt = this.light.glow.at.clone().applyMatrix4(this.lampG.matrixWorld);
    this.lampG.visible = inWorld && o.lampVisible !== false;
    this.sky.position.copy(cam.position); this.sky.material.uniforms.cam.value.copy(cam.position);
    this.groundMat.uniforms.lamp.value.copy(bulb); this.groundMat.uniforms.cam.value.copy(cam.position);
    this.shadowMat.uniforms.lamp.value.copy(bulb);
    // --- passes
    const r = this.renderer;
    r.setClearColor(new THREE.Color(plate ? P.top : (look.world ? P.top : '#e9e4dc')), 1);
    r.setRenderTarget(this.rtS); r.clear(true, true, true); r.render(this.scene, cam);
    r.setClearColor(0x000000, 0); r.setRenderTarget(this.rtF); r.clear(true, true, true);
    if (figSeen && !look.shaded) r.render(this.figScene, cam);
    // composite uniforms
    const U = this.comp.uniforms, toPx = p => { const q = new THREE.Vector3(...p).project(cam); return [(q.x * .5 + .5) * w, (q.y * .5 + .5) * h]; };
    U.tScene.value = this.rtS.texture; U.tFig.value = this.rtF.texture; U.res.value.set(w, h);
    const lp = toPx(glowAt.toArray());
    U.lampPx.value.set(lp[0], lp[1]);
    U.useLampDir.value = o.lightDir ? 0 : 1;
    if (o.lightDir) U.lightDir.value.set(o.lightDir[0], o.lightDir[1]);
    U.rimCol.value.set(P.rim);
    // the rim's width: the drawing's ~0.55 cm at the figure's distance, never under 1.2 px
    const hips = getV(poser.pose.P, this.d.sk.index.Hips);
    let pxPerM;
    if (v.type === 'ortho') pxPerM = v.k * 100 * ss;
    else pxPerM = h / (2 * Math.tan(cam.fov * Math.PI / 360) * Math.max(.5, depthOf(hips)));
    U.rimPx.value = clamp(.0055 * pxPerM * (o.rimScale || 1), 1.2 * ss, 9 * ss);
    // the rim is as bright as the light is behind the figure and near
    let rimK = 1;
    if (!o.lightDir) {
      const toLamp = glowAt.clone().sub(new THREE.Vector3(...hips)), dist = toLamp.length();
      const view = new THREE.Vector3(...hips).sub(cam.position).normalize();
      const back = toLamp.normalize().dot(view);
      rimK = (.55 + .45 * smooth(-.7, .5, back)) * clamp(3.2 * (CHAR.world.rimGain ?? 1) / dist, .55, 1.15);
    }
    U.rimK.value = look.rim ? rimK : 0;
    // glows: the world's light, behind the figure
    const G = [];
    if (inWorld && o.lampVisible !== false) { const g = this.light.glow; G.push([lp, g.r * pxPerMAt(glowAt.toArray()), g.col, g.k, depthOf(glowAt.toArray()), 1]); }
    U.nGlow.value = G.length;
    G.forEach(([p, rad, c, k, dpt, behind], i) => { U.glow.value[i].set(p[0], p[1], rad, k); U.glowCol.value[i].set(c); U.glowDepth.value[i] = dpt; U.glowBehind.value[i] = behind; });
    // the drawing's contact shadow under the feet (on the flat sheet only; in the world the light's shadow does it)
    if (plate && figSeen) {
      const pts = ['LeftFoot', 'RightFoot', 'LeftToeBase', 'RightToeBase'].map(n => toPx(getV(poser.pose.P, this.d.sk.index[n])));
      let x0 = Infinity, x1 = -Infinity; const Pp = poser.positions; for (let i = 0; i < Pp.length; i += 3) { if (Pp[i] < x0) x0 = Pp[i]; if (Pp[i] > x1) x1 = Pp[i]; }
      const a = toPx([x0, 0, 0]), bq = toPx([x1, 0, 0]), o0 = toPx([o.contactX ?? 0, 0, 0]);
      const half = o.contactR ? o.contactR * (v.k * ss) : Math.abs(bq[0] - a[0]) * .55;
      U.contact.value.set(o.contactR ? o0[0] : (a[0] + bq[0]) / 2, o0[1] - ss, half);
    } else U.contact.value.set(0, 0, 0);
    U.vign.value = look.grain ? (o.vign ?? .5) : 0; U.grain.value = look.grain ? (o.grain ?? .07) : 0; U.seed.value = (o.seed ?? 0) % 1000; U.ss.value = ss;
    r.setRenderTarget(this.rtC); r.render(this.qScene, this.qCam);
    // down to the screen: one bilinear tap in the middle of each ss×ss block (2×2: their mean)
    this.down.uniforms.t.value = this.rtC.texture; r.setRenderTarget(o.target || null); r.render(this.dScene, this.qCam);
  }
}
