// Савелий Петрович of С16 (pixel art) as a 3D character that is shown only as a sprite.
// The form: simple volumes on SOMA's joints (the indie constructor's way, as Р4), sized on the drawn sprite's own
// grid — 1 unit here is 1 pixel of the sprite (front, three-quarter and side maps of styles/s16-pixel/tools/chars/
// savely.py). It moves by Kimodo's motions. It is never shown as a 3D render: every frame it is rendered small and
// unseen (material, light, depth), and pixel.js decides each pixel by the style's rules; the face's signs are put
// on the head as pixels at points that turn with the head.
import * as THREE from 'three';
import { lerp, clamp, smooth, smin, cone, add, sub, surfaceNets, sph, ell, rbox, inter, capsule, horn } from './forms.js';
import { MATS, MID, resolve, keysOf, outline, backdrop, box, paste, draw, hexOf } from './pixel.js';
import { PFACE, PATCH, PBODY } from './data.js';
import { Live } from './live.js';

const S = 0.04;                                   // one sprite pixel in metres: 37 px tall → 1.48 m
const P = (x, y, z = 0) => [x * S, y * S, z * S]; // x: his left (the picture's right), y up from the floor, z forward
const TOP = 37;                                   // the drawn sprite's height; row r is y = TOP - r - 0.5
const row = r => TOP - r - 0.5;

// ———————————— the skeleton: SOMA's joints (no fingers), placed on the sprite ————————————
const PARENT = {
  Hips: null, Spine1: 'Hips', Spine2: 'Spine1', Chest: 'Spine2', Neck1: 'Chest', Neck2: 'Neck1', Head: 'Neck2', HeadEnd: 'Head', Jaw: 'Head', LeftEye: 'Head', RightEye: 'Head',
  LeftShoulder: 'Chest', LeftArm: 'LeftShoulder', LeftForeArm: 'LeftArm', LeftHand: 'LeftForeArm',
  RightShoulder: 'Chest', RightArm: 'RightShoulder', RightForeArm: 'RightArm', RightHand: 'RightForeArm',
  LeftLeg: 'Hips', LeftShin: 'LeftLeg', LeftFoot: 'LeftShin', LeftToeBase: 'LeftFoot', LeftToeEnd: 'LeftToeBase',
  RightLeg: 'Hips', RightShin: 'RightLeg', RightFoot: 'RightShin', RightToeBase: 'RightFoot', RightToeEnd: 'RightToeBase',
  RightProp: 'RightHand',                         // not SOMA's: the watch in the right hand, kept upright
};
const HC = [0, 30.5, 2];                          // the head's centre: rows 0–12, a little forward (he stoops)
const JU = {
  Hips: [0, 15, -0.3], Spine1: [0, 17.4, -0.2], Spine2: [0, 19.8, 0], Chest: [0, 22, 0.2], Neck1: [0, 23.4, 0.8], Neck2: [0, 24.2, 1.2], Head: [0, 25, 1.6],
  HeadEnd: [0, 37, 2], Jaw: [0, 26.5, 5], LeftEye: [3, 30.5, 6], RightEye: [-3, 30.5, 6],
};
for (const [s, k] of [['Left', 1], ['Right', -1]]) {
  JU[s + 'Shoulder'] = [k * 2, 23, 0.2]; JU[s + 'Arm'] = [k * 5.9, 22.1, 0.2]; JU[s + 'ForeArm'] = [k * 6.1, 18.8, 0]; JU[s + 'Hand'] = [k * 6.2, 15.3, 0.6];
  JU[s + 'Leg'] = [k * 2.5, 14, -0.5]; JU[s + 'Shin'] = [k * 2.5, 8, -0.3]; JU[s + 'Foot'] = [k * 2.5, 2, -0.6]; JU[s + 'ToeBase'] = [k * 2.6, 0.7, 1.6]; JU[s + 'ToeEnd'] = [k * 2.7, 0.5, 3.4];
}
JU.RightProp = JU.RightHand;
const J = Object.fromEntries(Object.entries(JU).map(([b, p]) => [b, P(...p)]));
const BONES = Object.keys(PARENT), BI = Object.fromEntries(BONES.map((b, i) => [b, i]));
const chain = names => (x, y) => {
  const hs = names.map(n => J[n][1]);
  if (y <= hs[0]) return { [names[0]]: 1 };
  for (let i = 0; i < names.length - 1; i++) if (y <= hs[i + 1]) { const t = smooth((y - hs[i]) / (hs[i + 1] - hs[i])); return { [names[i]]: 1 - t, [names[i + 1]]: t }; }
  return { [names[names.length - 1]]: 1 };
};
const bodyW = chain(['Hips', 'Spine1', 'Spine2', 'Chest']);

// ———————————— the forms. A part: [group, bone | [bone, bone] | weights(x, y, z), distance]; a group is one
// material of pixel.js ————————————
const headForm = rbox(P(...HC), P(5.5, 6.5, 5.2), 4.5 * S);
const grow = (f, d) => (x, y, z) => f(x, y, z) - d * S;
const slab = (y0, y1) => (x, y, z) => Math.max(y0 * S - y, y - y1 * S);
function parts() {
  const out = [], a = (g, b, f) => out.push([g, b, f]);
  const h = (x, y, z) => [HC[0] + x, HC[1] + y, HC[2] + z];
  // head: a rounded block 11 × 13 × 10.4 (the sprite's skull: flat sides, a dome, a narrower chin); the nose a small
  // bump that shows in profile
  a('skin', 'Head', headForm);
  a('nose', 'Head', ell(P(...h(0, row(8) - HC[1], 5.3)), P(1.15, 1.0, 1.3)));
  // white tufts: at the back corners of the bald head and across its back — beside the head from the front, behind
  // it from the side, as the two drawn views have them
  for (const k of [-1, 1]) a('hair', 'Head', ell(P(...h(k * 5.8, -0.3, -5.7)), P(2.6, 3.1, 2.7)));
  a('hair', 'Head', ell(P(...h(0, -0.8, -6.0)), P(5.4, 2.8, 2.3)));
  // the moustache: two lobes from under the nose out and down
  for (const k of [-1, 1]) a('moustache', 'Head', horn(P(...h(k * 1.35, row(9) - HC[1] + 0.05, 5.5)), P(...h(k * 3.9, row(9) - HC[1] + 0.25, 5.1)), P(...h(k * 5.0, row(10) - HC[1] - 0.2, 3.3)), 0.72 * S, 0.62 * S, 6));
  // the loupe's strap round the head on row 3, the loupe pushed up on the forehead over his left eye, its lens
  a('strap', 'Head', inter(grow(headForm, 0.35), slab(row(3) - 0.5, row(3) + 0.5), 0.05 * S));
  a('loupe', 'Head', rbox(P(...h(2.5, 4.5, 4.0)), P(1.05, 1.05, 1.5), 0.3 * S));
  a('lens', 'Head', rbox(P(...h(2.0, 5.0, 5.4)), P(0.55, 0.55, 0.3), 0.15 * S));
  // the vest: a rounded block with an old man's belly; the shirt's collar, the V under it, the bow tie
  a('vest', bodyW, rbox(P(0, 19.6, -0.2), P(4.5, 4.45, 4.2), 2.4 * S));
  a('vest', bodyW, ell(P(0, 18.6, 1.0), P(4.45, 3.6, 4.5)));
  a('shirt', bodyW, rbox(P(0, 23.45, 0.3), P(4.6, 0.62, 4.1), 0.6 * S));
  a('shirt', bodyW, cone(P(-0.5, 22.9, 4.3), P(0, 21.7, 5.1), 0.95 * S, 0.4 * S));
  a('bow', bodyW, rbox(P(-0.5, 23.5, 4.75), P(1.0, 0.5, 0.5), 0.2 * S));
  // trousers: hips, legs four pixels wide with one pixel between them; shoes with the toes a little out
  a('trousers', 'Hips', rbox(P(0, 14.2, -0.4), P(4.2, 2.2, 3.4), 1.6 * S));
  for (const [s, k] of [['Left', 1], ['Right', -1]]) {
    a('trousers', [s + 'Leg', s + 'Shin'], capsule(P(k * 2.5, 13.5, -0.4), P(k * 2.5, 2.6, -0.4), 2.0 * S));
    a('shoes', s + 'Foot', rbox(P(k * 2.6, 1.0, 0.7), P(2.05, 1.0, 3.1), 0.9 * S, k * 0.1));
    a('shoes', s + 'Foot', rbox(P(k * 3.0, 0.5, 1.2), P(2.45, 0.5, 3.0), 0.45 * S, k * 0.1));
    // shirt sleeves three pixels wide, the hands small lumps
    a('shirt', s + 'Arm', capsule(P(k * 5.7, 22.0, 0.2), J[s + 'ForeArm'], 1.5 * S));
    a('shirt', s + 'ForeArm', capsule(J[s + 'ForeArm'], add(J[s + 'Hand'], P(0, 1.3, 0)), 1.45 * S));
    a('hand', s + 'Hand', ell(add(J[s + 'Hand'], P(0, -0.7, 0)), P(1.4, 2.0, 1.5)));
  }
  // the pocket watch in the right hand: a gold disc, face to the front (held upright on the hand's own joint)
  a('watch', 'RightProp', ell(add(J.RightHand, P(...WATCH_AT)), P(1.6, 1.6, 0.7)));
  return out;
}
const WATCH_AT = [3.3, 1.0, 1.5];        // the watch from the hand's joint: over the palm, before the belly
const GROUP_MAT = { nose: 'skin', lens: 'lens' };
const GRID = { moustache: 0.11, strap: 0.12, loupe: 0.12, lens: 0.08, bow: 0.1, watch: 0.12, nose: 0.12, hand: 0.15, shoes: 0.18 };
const BLEND = { hair: 1.2, shirt: 0.35, trousers: 0.5, vest: 0.8 };
function build(ps0) {
  const groups = {};
  for (const p of ps0) (groups[p[0]] ??= []).push(p);
  const out = [];
  for (const [g, ps] of Object.entries(groups)) {
    const k = (BLEND[g] ?? 0.2) * S;
    const sdf = (x, y, z) => { let d = 1e9; for (const p of ps) { const v = p[2](x, y, z); d = d === 1e9 ? v : smin(d, v, k); } return d; };
    const lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9], st = 0.02;
    for (let x = -0.46; x <= 0.46; x += st) for (let y = -0.04; y <= 1.6; y += st) for (let z = -0.46; z <= 0.5; z += st)
      if (sdf(x, y, z) < st) { lo[0] = Math.min(lo[0], x); lo[1] = Math.min(lo[1], y); lo[2] = Math.min(lo[2], z); hi[0] = Math.max(hi[0], x); hi[1] = Math.max(hi[1], y); hi[2] = Math.max(hi[2], z); }
    if (lo[0] > hi[0]) { console.warn('empty group', g); continue; }
    const m = surfaceNets(sdf, lo.map(v => v - 2 * st), hi.map(v => v + 2 * st), (GRID[g] ?? 0.3) * S);
    const nv = m.pos.length / 3, si = new Uint16Array(nv * 4), sw = new Float32Array(nv * 4), acc = new Float32Array(BONES.length);
    for (let v = 0; v < nv; v++) {
      const x = m.pos[v * 3], y = m.pos[v * 3 + 1], z = m.pos[v * 3 + 2];
      const ds = ps.map(p => p[2](x, y, z)), dmin = Math.min(...ds);
      acc.fill(0);
      ps.forEach((p, i) => {
        const w = Math.exp(-Math.max(ds[i] - dmin, 0) / (0.3 * S));
        if (typeof p[1] === 'function') { for (const [b, t] of Object.entries(p[1](x, y, z))) acc[BI[b]] += w * t; }
        else if (Array.isArray(p[1])) {
          const [b0, b1] = p[1], a = J[b0], j = J[b1], e = J[b1.replace('Shin', 'Foot').replace('ForeArm', 'Hand')];
          const L = Math.hypot(...sub(e, a)), t = ((x - a[0]) * (e[0] - a[0]) + (y - a[1]) * (e[1] - a[1]) + (z - a[2]) * (e[2] - a[2])) / (L * L);
          const tj = Math.hypot(...sub(j, a)) / L, f = smooth(clamp((t - tj) / 0.24 + 0.5, 0, 1));
          acc[BI[b0]] += w * (1 - f); acc[BI[b1]] += w * f;
        } else acc[BI[p[1]]] += w;
      });
      const order = [...acc.keys()].sort((a, b) => acc[b] - acc[a]).slice(0, 4);
      let s = 0; for (const b of order) s += acc[b];
      order.forEach((b, i) => { si[v * 4 + i] = b; sw[v * 4 + i] = acc[b] / s; });
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(m.pos, 3));
    geo.setAttribute('normal', new THREE.BufferAttribute(m.nor, 3));
    geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(si, 4));
    geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));
    geo.setIndex(nv > 65535 ? new THREE.Uint32BufferAttribute(m.idx, 1) : new THREE.Uint16BufferAttribute(m.idx, 1));
    out.push({ g, geo });
  }
  return out;
}

// ———————————— the unseen render: material, light, depth; or (for the page's steps) the plain 3D in the palette's
// colours ————————————
const VS = `
#include <common>
#include <skinning_pars_vertex>
varying vec3 vN;
void main() {
  #include <skinbase_vertex>
  #include <beginnormal_vertex>
  #include <skinnormal_vertex>
  #include <defaultnormal_vertex>
  #include <begin_vertex>
  #include <skinning_vertex>
  #include <project_vertex>
  vN = normalize(transformedNormal);
}`;
const FS = `
uniform vec3 uL; uniform vec3 uLh; uniform float uId; uniform float uMode; uniform vec3 uLo; uniform vec3 uBase; uniform vec3 uHi; uniform vec2 uThr;
varying vec3 vN;
void main() {
  vec3 n = normalize(vN); if (!gl_FrontFacing) n = -n;
  float l = dot(n, uL), lh = dot(n, uLh);
  if (uMode < 0.5) gl_FragColor = vec4(uId / 255.0, l * 0.5 + 0.5, gl_FragCoord.z, lh * 0.5 + 0.5);
  else if (uMode < 1.5) gl_FragColor = vec4(l < uThr.x ? uLo : lh > uThr.y ? uHi : uBase, 1.0);
  else gl_FragColor = vec4(vec3(0.80, 0.77, 0.83) * (0.5 + 0.5 * max(l, 0.0)) + vec3(0.05, 0.04, 0.08), 1.0);
}`;
// the light is held to the view, from the upper left, as a sprite's is in every view. Two readings of it: the shade
// sits on a form's right side (the sprite's one column of shade; undersides stay lit), the shine on what faces up-left
const LIGHT = new THREE.Vector3(-0.75, 0.15, 0.65).normalize(), SHINE = new THREE.Vector3(-0.5, 0.68, 0.53).normalize();
const MODE = { value: 0 };
const hex3 = k => { const h = hexOf(k); return new THREE.Vector3(parseInt(h.slice(1, 3), 16) / 255, parseInt(h.slice(3, 5), 16) / 255, parseInt(h.slice(5, 7), 16) / 255); };
function matOf(g) {
  const id = MID[GROUP_MAT[g] || g], m = MATS[id];
  return new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, side: THREE.DoubleSide, uniforms: {
    uL: { value: LIGHT }, uLh: { value: SHINE }, uId: { value: id }, uMode: MODE, uLo: { value: hex3(m.keys[0]) }, uBase: { value: hex3(m.keys[1]) }, uHi: { value: hex3(m.keys[2]) }, uThr: { value: new THREE.Vector2(...m.thr) } } });
}

const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
const renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true, preserveDrawingBuffer: true });
renderer.outputColorSpace = THREE.LinearSRGBColorSpace; renderer.toneMapping = THREE.NoToneMapping;
renderer.setClearColor(0x000000, 0);
const scene = new THREE.Scene();
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 50);
const SS = 4, ZR = 51;                            // samples a pixel's side; the depth range in pixels
let target = null;

// ———————————— the figure ————————————
const MESHES = build(parts());
const bones = {}, root = new THREE.Group();
for (const b of BONES) { bones[b] = new THREE.Bone(); bones[b].name = b; }
for (const b of BONES) { const p = PARENT[b], pp = p ? J[p] : [0, 0, 0]; bones[b].position.set(...sub(J[b], pp)); if (p) bones[p].add(bones[b]); else root.add(bones[b]); }
const skel = new THREE.Skeleton(BONES.map(b => bones[b]));
root.updateMatrixWorld(true); skel.calculateInverses();
const meshes = [];
for (const { g, geo } of MESHES) { const m = new THREE.SkinnedMesh(geo, matOf(g)); m.frustumCulled = false; m.bind(skel); m.userData.g = g; root.add(m); meshes.push(m); }
scene.add(root);

// ———————————— Kimodo's motions (Р4's retargeting, from experiments/indie): each SOMA joint turns as in the motion,
// a fixed turn first brings our bone to SOMA's rest direction; the pelvis goes as high and as far as our legs make
// it; the feet are put on the floor ————————————
const MOTION = {};
const motion = name => MOTION[name] ??= fetch(new URL(`../motions/${name}.json`, import.meta.url)).then(r => r.json()).then(prepare);
const CHAIN = { LeftLeg: 'LeftShin', LeftShin: 'LeftFoot', LeftFoot: 'LeftToeBase', RightLeg: 'RightShin', RightShin: 'RightFoot', RightFoot: 'RightToeBase',
  LeftShoulder: 'LeftArm', LeftArm: 'LeftForeArm', LeftForeArm: 'LeftHand', LeftHand: 'LeftHandMiddle1', RightShoulder: 'RightArm', RightArm: 'RightForeArm', RightForeArm: 'RightHand', RightHand: 'RightHandMiddle1' };
function prepare(M) {
  M.C = Object.fromEntries(Object.entries(CHAIN).map(([b, c]) => {
    const ours = /Hand$/.test(b) ? sub(J[b], J[PARENT[b]]) : sub(J[c], J[b]);
    return [b, new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(...ours).normalize(), new THREE.Vector3(...sub(M.rest[c], M.rest[b])).normalize())];
  }));
  const fw = new THREE.Vector3(), q = new THREE.Quaternion();
  let lean = 0;
  for (let f = 0; f < M.n; f++) { const d = M.D.Chest; q.set(d[f * 4], d[f * 4 + 1], d[f * 4 + 2], d[f * 4 + 3]); fw.set(0, 0, 1).applyQuaternion(q); lean += Math.asin(clamp(fw.y, -1, 1)) * 180 / Math.PI; }
  M.lean = lean / M.n;
  // which way he faces at the clip's start (Kimodo's clips start turned any way): the figure is turned to face front
  const d0 = M.D.Hips; q.set(d0[0], d0[1], d0[2], d0[3]); fw.set(0, 0, 1).applyQuaternion(q); M.yaw0 = Math.atan2(fw.x, fw.z);
  return M;
}
const _qa = new THREE.Quaternion(), _qb = new THREE.Quaternion(), _v = new THREE.Vector3(), _w = new THREE.Vector3();
function dq(M, b, f) {
  const d = M.D[b], i = Math.floor(f), j = Math.min(i + 1, M.n - 1), t = f - i;
  _qa.set(d[i * 4], d[i * 4 + 1], d[i * 4 + 2], d[i * 4 + 3]); _qb.set(d[j * 4], d[j * 4 + 1], d[j * 4 + 2], d[j * 4 + 3]);
  return _qa.clone().slerp(_qb, t);
}
const hipsAt = (M, f, k) => { const i = Math.floor(f), j = Math.min(i + 1, M.n - 1), t = f - i; return lerp(M.hips[i * 3 + k], M.hips[j * 3 + k], t); };
const atF = (arr, f, n) => { const i = Math.floor(clamp(f, 0, n - 1)), j = Math.min(i + 1, n - 1); return lerp(arr[i], arr[j], clamp(f, 0, n - 1) - i); };
function setLocal(W) { for (const b of BONES) { const p = PARENT[b]; if (W[b]) bones[b].quaternion.copy(p ? W[p].clone().invert().multiply(W[b]) : W[b]); } root.updateMatrixWorld(true); }
const UPPER = new Set(BONES.filter(b => { for (let p = b; p; p = PARENT[p]) if (p === 'Spine1') return true; return false; }));
const dirQ = (from, to) => new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(...from).normalize(), new THREE.Vector3(...to).normalize());
// the drawn pose: the right hand brought before the belly with the watch in it (the upper arm a little forward,
// the forearm in and forward) — turns of the two arm bones from their rest
const WATCH_ARM = dirQ(sub(JU.RightForeArm, JU.RightArm), [-0.2, -3.2, 1.3]);
const WATCH_FORE = dirQ(sub(JU.RightHand, JU.RightForeArm), [2.3, -1.5, 2.8]);
// M: a motion or null (the rest); o: { travel, offset, upright, watch }
function pose(M, f, o = {}) {
  const W = {};
  for (const b of BONES) {
    const p = PARENT[b];
    let w;
    if (M && M.D[b]) { w = dq(M, b, f); if (M.C[b]) w.multiply(M.C[b]); }
    else w = p ? W[p].clone() : new THREE.Quaternion();
    W[b] = w;
  }
  if (M && o.upright && M.lean) {            // Kimodo's waiting motion stoops ~25°: most of that average lean taken out
    const ax = new THREE.Vector3(1, 0, 0).applyQuaternion(W.Hips), fix = new THREE.Quaternion().setFromAxisAngle(ax, 0.7 * M.lean * Math.PI / 180);
    for (const b of UPPER) W[b].premultiply(fix);
  }
  if (M) {
    // arms off the body: the upper arm keeps out to its side (the vest is wide, the arms are short)
    for (const [s, k] of [['Left', 1], ['Right', -1]]) {
      const side = _w.set(k, 0, 0).applyQuaternion(W.Chest);
      const d2 = new THREE.Vector3(...sub(M.rest[s + 'ForeArm'], M.rest[s + 'Arm'])).normalize().applyQuaternion(dq(M, s + 'Arm', f));
      const out = d2.dot(side), need = 0.1;
      if (out < need) { const ax = new THREE.Vector3().crossVectors(d2, side).normalize(), fix = new THREE.Quaternion().setFromAxisAngle(ax, Math.asin(need) - Math.asin(Math.max(-1, out))); for (const b of [s + 'Arm', s + 'ForeArm', s + 'Hand', s + 'Prop']) if (W[b]) W[b].premultiply(fix); }
    }
  }
  if (M && o.calm) {
    // a big head: the neck's and head's turn against the chest taken in part (Kimodo's wave tips the head ~30° to the
    // side, which on a head a third of the figure reads as a broken neck)
    for (const b of ['Neck1', 'Neck2', 'Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye']) W[b] = W.Chest.clone().slerp(W[b], o.calm);
  }
  if (o.watch) {
    W.RightArm = W.Chest.clone().multiply(WATCH_ARM); W.RightForeArm = W.Chest.clone().multiply(WATCH_FORE); W.RightHand = W.RightForeArm.clone();
  }
  setLocal(W);
  if (M) {
    // and out of the big head: a hand or elbow that would go into it swings the arm outward until it clears
    const head = new THREE.Vector3(), hp = new THREE.Vector3(), fwd = new THREE.Vector3(), R = 7.2 * S;
    for (const [s, k] of [['Left', 1], ['Right', -1]]) for (let it = 0; it < 14; it++) {
      if (o.watch && s === 'Right') break;
      bones.Head.updateWorldMatrix(true, false); head.set(...sub(P(...HC), J.Head)).applyMatrix4(bones.Head.matrixWorld);
      let inside = false;
      for (const b of [s + 'Hand', s + 'ForeArm']) { bones[b].getWorldPosition(hp); if (hp.distanceTo(head) < R + 1.5 * S) inside = true; }
      if (!inside) break;
      fwd.set(0, 0, 1).applyQuaternion(W.Chest);
      const fix = new THREE.Quaternion().setFromAxisAngle(fwd, k * -0.12);
      for (const b of [s + 'Arm', s + 'ForeArm', s + 'Hand']) W[b].premultiply(fix);
      setLocal(W);
    }
  }
  if (M) {
    const kr = J.Hips[1] / M.hipY, off = o.offset || [0, 0];
    bones.Hips.position.set(o.travel ? (hipsAt(M, f, 0) - M.hips[0]) * kr + off[0] : 0, hipsAt(M, f, 1) * kr, J.Hips[2] + (o.travel ? (hipsAt(M, f, 2) - M.hips[2]) * kr + off[1] : 0));
  } else bones.Hips.position.set(...J.Hips);
  root.rotation.y = M ? -M.yaw0 : 0;
  root.updateMatrixWorld(true);
  // the watch stays upright, turned only as he is
  _v.set(0, 0, 1).applyQuaternion(W.Chest); _qb.setFromAxisAngle(_w.set(0, 1, 0), Math.atan2(_v.x, _v.z));
  _qb.premultiply(root.quaternion); bones.RightProp.parent.getWorldQuaternion(_qa); bones.RightProp.quaternion.copy(_qa.invert().multiply(_qb));
  root.updateMatrixWorld(true);
  if (M) {
    let low = 1e9;
    for (const m of meshes) {
      if (m.userData.g !== 'shoes') continue;
      const pos = m.geometry.attributes.position;
      for (let i = 0; i < pos.count; i += 3) { _v.fromBufferAttribute(pos, i); m.applyBoneTransform(i, _v); _v.applyMatrix4(m.matrixWorld); if (_v.y < low) low = _v.y; }
    }
    bones.Hips.position.y += atF(M.foot, f, M.n) * kr0(M) - low;
    root.updateMatrixWorld(true);
  }
}
const kr0 = M => J.Hips[1] / M.hipY;

// ———————————— the face's signs: pixels at points of the head. A point is given where the drawn front sprite has it
// (x, row) and at the depth the drawn side sprite has it; it turns with the head, is seen while its side of the head
// is turned to the eye and nothing is before it, and is put only on the head's skin ————————————
const EXPR_RU = { rest: 'спокоен', joy: 'радость', surprise: 'удивление', sadness: 'грусть', anger: 'злость' };
// brows of one side (the right eye, x < 0; mirrored for the left): [x, row]
const BROW = {
  rest: [[-4, 5], [-3, 5], [-2, 6]],
  joy: [[-4, 5], [-3, 4], [-2, 5]],
  surprise: [[-4, 4], [-3, 4], [-2, 4]],
  sadness: [[-4, 6], [-3, 5], [-2, 4]],
  anger: [[-4, 4], [-3, 5], [-2, 6], [-1, 6]],
};
const ZF = x => 5.2 - 0.62 * Math.abs(x);        // the depth of a sign of the face by its x (eye: 3 → 3.3; cheek: 4 → 2.7)
function faceSigns(F) {
  const e = F.expr || 'rest', out = [], h = (x, r, z, key, on, extra) => out.push({ p: [HC[0] + x, row(r), HC[2] + z], d: [x, z], key, on: on || ['skin'], bone: 'Head', ...extra });
  for (const k of [-1, 1]) {
    for (const [x, r] of BROW[e]) h(-k * x, r, ZF(x), 'w3');
    if (F.blink) h(k * 3, 6, ZF(3), 's2');
    else if (e === 'joy') h(k * 3, 6, ZF(3), 's1');
    else { h(k * 3, 6, ZF(3), 'x0'); if (e === 'surprise') h(k * 3, 5, ZF(3), 'x0'); }
    h(k * 4, 8, 1.4, 'x2');                                              // a pink pixel on the cheek
    h(k * 5.6, 6.5, -0.6, 's2', null, { side: 0.75, tall: 2 });          // the ear: two pixels of shade, in profile only
  }
  // the nose: its tip red, a light pixel on the lit side and shade on the other (put where there is skin)
  out.push({ p: [HC[0], row(8), HC[2] + 5.0], d: [0, 1], key: 'x2', on: ['skin'], bone: 'Head', nose: true, side: -0.3 });
  // the mouth under the moustache: three pixels of shade; open in speech or surprise, the middle one dark
  const open = F.mouth || (e === 'surprise' ? 2 : e === 'joy' ? 1 : 0);
  for (const x of [-1, 0, 1]) h(x, 10, 4.9, x === 0 && open ? 'r0' : open === 2 ? 'r0' : 's1');
  h(0, 9, 5.2, 's1');
  // on the vest: the pocket's light edge and the watch chain; the watch's white face
  out.push({ p: [-3, row(16), 4.0], d: [-0.3, 1], key: 'g3', on: ['vest'], bone: 'Spine2', tall: 2 });
  for (const x of [2, 3]) out.push({ p: [x, row(18), 4.2], d: [0.3, 1], key: 't2', on: ['vest'], bone: 'Spine2' });
  out.push({ p: [JU.RightHand[0] + WATCH_AT[0], JU.RightHand[1] + WATCH_AT[1], JU.RightHand[2] + WATCH_AT[2] + 0.8], d: [0, 1], key: 'x1', on: ['watch'], bone: 'RightProp' });
  return out;
}

// ———————————— the picture ————————————
// view: { W, H (sprite pixels), yaw (deg, the camera round him; 0 = from the front), zoom (pixels of the picture to
// a pixel of the sprite: 1 the sprite, 2.6 the portrait), ax, ay (where the point `at` falls, in pixels from the
// picture's top left), at: 'floor' | 'head' | [x, y, z] in pixels }
const V = { W: 58, H: 70, yaw: 0, zoom: 1, ax: 29.5, ay: 62, at: 'floor', mode: 'sprite', bg: 'figure', scale: 8, floor: 58, face: 'sprite', rules: true, bones: false };
const st = { clip: 'stand', M: null, t: 0, watch: true, expr: 'rest', talk: false, live: null, lock: [0, 0], scroll: 0, F: { expr: 'rest' } };
const CLIPS = {
  stand: { ru: 'смотрит на часы', watch: true },
  walk: { ru: 'идёт', motion: 'walk', travel: true },
  idle: { ru: 'ждёт', motion: 'idle', upright: true, watch: true },
  wave: { ru: 'машет', motion: 'wave', calm: 0.45 },
  bow: { ru: 'кланяется', motion: 'bow' },
  stomp: { ru: 'топает', motion: 'stomp' },
};
const FPS = 12;                                    // a sprite's animation is drawn in few frames: 12 a second
function atPoint() {
  if (V.at === 'head') return new THREE.Vector3(...P(...HC));
  if (Array.isArray(V.at)) return new THREE.Vector3(...P(...V.at));
  return new THREE.Vector3(st.lock[0], 0, st.lock[1]);
}
function aim() {
  const yw = V.yaw * Math.PI / 180, at = atPoint(), k = S / V.zoom;
  camera.left = -V.ax * k; camera.right = (V.W - V.ax) * k; camera.top = V.ay * k; camera.bottom = -(V.H - V.ay) * k;
  camera.near = 5 - ZR / 2 * S; camera.far = 5 + ZR / 2 * S;
  camera.position.set(at.x + 5 * Math.sin(yw), at.y, at.z + 5 * Math.cos(yw)); camera.lookAt(at); camera.updateProjectionMatrix(); camera.updateMatrixWorld(true);
  return { at, right: new THREE.Vector3(Math.cos(yw), 0, -Math.sin(yw)), to: new THREE.Vector3(Math.sin(yw), 0, Math.cos(yw)) };
}
const _m = new THREE.Matrix4(), _p = new THREE.Vector3(), _d = new THREE.Vector3();
function boneMat(b) { return _m.multiplyMatrices(bones[b].matrixWorld, skel.boneInverses[BI[b]]); }
function project(c, p) { const r = p.clone().sub(c.at); return [V.ax + V.zoom * r.dot(c.right) / S, V.ay - V.zoom * r.y / S, r.dot(c.to) / S]; }

function pass(mode) {
  const w = V.W * SS, h = V.H * SS;
  if (!target || target.width !== w || target.height !== h) { target?.dispose(); target = new THREE.WebGLRenderTarget(w, h, { minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, depthBuffer: true }); }
  MODE.value = mode;
  renderer.setRenderTarget(target); renderer.clear(); renderer.render(scene, camera);
  const buf = new Uint8Array(w * h * 4); renderer.readRenderTargetPixels(target, 0, 0, w, h, buf); renderer.setRenderTarget(null);
  return buf;
}
// the sprite's own marks on the 3D's pixels: the face's signs and the marks on the vest
function signs(g, R, c, F) {
  const zOf = q => -(R.z[q] / 255 - 0.5) * ZR;      // how far toward the eye the seen surface is, in pixels
  for (const s of faceSigns(F)) {
    const M = boneMat(s.bone);
    _p.set(...P(...s.p)).applyMatrix4(M); _d.set(s.d[0], 0, s.d[1]).normalize().transformDirection(M);
    if (_d.dot(c.to) < (s.side ?? 0.1)) continue;
    const [u, v, zc] = project(c, _p), x = Math.floor(u), y = Math.floor(v);
    for (let j = 0; j < (s.tall || 1); j++) {
      const yy = y + j, q = yy * V.W + x;
      if (x < 0 || yy < 0 || x >= V.W || yy >= V.H || !s.on.includes(MATS[R.id[q]]?.name) || zOf(q) - zc > 4.5) continue;
      g[yy][x] = s.key;
      if (s.nose) {
        if (x > 0 && R.id[q - 1] === MID.skin && g[yy][x - 1][0] === 's') g[yy][x - 1] = 's4';
        if (x < V.W - 1 && R.id[q + 1] === MID.skin && g[yy][x + 1][0] === 's') g[yy][x + 1] = 's2';
      }
    }
  }
}
const HEADG = new Set(['skin', 'nose', 'hair', 'moustache', 'strap', 'loupe', 'lens']);
const NECK = 4;                                    // the portrait has a neck the small sprite has not: the body sits lower
// the sprite of this moment: a grid of colour keys (figure only, with its outline)
function sprite() {
  const F = st.F;
  if (V.face !== 'portrait') {
    const c = aim();
    for (const m of meshes) m.visible = !(m.userData.g === 'watch' && !st.watchNow);
    const R = resolve(pass(0), V.W, V.H, SS), g = keysOf(R, { rules: V.rules });
    if (V.rules) signs(g, R, c, F);
    return V.rules ? outline(g) : g;
  }
  // the portrait is put together in layers, as the style's portrait is: the body (lower by the neck), the neck,
  // the head; then the portrait's own face (portrait(expr) of the style's code) laid on the head where its middle falls
  const ay = V.ay;
  V.ay = ay + NECK; aim();
  for (const m of meshes) m.visible = !HEADG.has(m.userData.g) && m.userData.g !== 'watch';
  const Rb = resolve(pass(0), V.W, V.H, SS), g = keysOf(Rb, { rules: V.rules });
  if (V.rules) {
    // the portrait's shirt front, bow tie and buttons, laid on the 3D chest where its bow tie falls
    _p.set(...P(-0.5, 23.5, 4.75)).applyMatrix4(boneMat('Chest'));
    const [u, v] = project(aim(), _p), ox = Math.round(u - 28), oy = Math.round(v - 46.5);
    for (let y = 40; y < 56; y++) for (let x = 0; x < 56; x++) { const k = PBODY[y][x], X = x + ox, Y = y + oy; if (k && g[Y]?.[X] && ['vest', 'shirt', 'bow'].includes(MATS[Rb.id[Y * V.W + X]].name)) g[Y][X] = k; }
  }
  V.ay = ay; const c = aim();
  for (const m of meshes) m.visible = HEADG.has(m.userData.g) && !(V.rules && (m.userData.g === 'moustache' || m.userData.g === 'nose'));
  const R = resolve(pass(0), V.W, V.H, SS), gh = keysOf(R, { rules: V.rules, hairBand: 2 });
  _p.set(...P(...HC)).applyMatrix4(boneMat('Head'));
  const [u, v] = project(c, _p), ox = Math.round(u - 28), oy = Math.round(v - 24.5);
  for (let y = 36; y < 46 + NECK; y++) for (let x = 23; x <= 32; x++) if (g[y + oy]?.[x + ox] === '') g[y + oy][x + ox] = y < 44 ? 's1' : 's2';
  if (V.rules) {
    const L = PFACE[F.expr || 'rest'].map(r => r.slice());
    for (const name of [F.blink && 'blink', F.look, F.mouth && 'm' + F.mouth]) if (name) for (const [x, y, k] of PATCH[(F.expr || 'rest') + ':' + name] || []) L[y][x] = k;
    for (let y = 0; y < 56; y++) for (let x = 0; x < 56; x++) {
      const X = x + ox, Y = y + oy; if (!L[y][x] || X < 0 || Y < 0 || X >= V.W || Y >= V.H) continue;
      const m = MATS[R.id[Y * V.W + X]]?.name;
      if (L[y][x][0] === 'w' ? m && m !== 'skin' && m !== 'hair' : m !== 'skin') continue;   // skin's marks only on skin; brows and moustache may go over the tufts and past the cheek
      gh[Y][X] = L[y][x];
    }
    // portrait.py's jaw: a darker line where the skin meets the white hair on the shaded side
    for (let y = 0; y < V.H; y++) for (let x = 0; x < V.W - 1; x++) if (gh[y][x][0] === 's' && R.id[y * V.W + x] === MID.skin && R.id[y * V.W + x + 1] === MID.hair) gh[y][x] = 's1';
  }
  paste(g, gh);
  return V.rules ? outline(g) : g;
}
// the whole picture: the backdrop, the shadow under the feet, the sprite
function picture() {
  const g = sprite();
  let bgd;
  if (V.bg === 'box') { bgd = box(V.W, V.H); return paste(bgd, g, 3, 3, 3, 3, 3 + V.W, 3 + V.H); }
  if (V.bg === 'none') return g;
  bgd = backdrop(V.W, V.H, V.floor);
  // marks on the floor that go by as he walks (whole pixels)
  const sc = Math.round(st.scroll);
  for (let x = 0; x < V.W; x++) { const u = ((x + sc) % 24 + 24) % 24; if (u < 5) bgd[Math.min(V.H - 1, V.floor + 5)][x] = 'd1'; if ((u + 12) % 24 < 3 && V.floor + 9 < V.H) bgd[V.floor + 9][x] = 'd1'; }
  // sheets.py's stand: a two-row shadow under the feet, as wide as the figure's feet
  let x0 = 1e9, x1 = -1;
  for (let y = Math.round(V.ay) - 3; y < Math.round(V.ay) + 1; y++) for (let x = 0; x < V.W; x++) if (g[y]?.[x]) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); }
  if (x1 >= 0) { const b = Math.round(V.ay); for (let x = x0 - 1; x <= x1 + 1; x++) { if (bgd[b]?.[x]) bgd[b][x] = 'd1'; if (x > x0 && x < x1 && bgd[b + 1]?.[x]) bgd[b + 1][x] = 'd1'; } }
  return paste(bgd, g);
}
function render() {
  const sc = V.scale;
  if (V.mode === 'solid' || V.mode === 'clay') {
    // the plain 3D, large and smooth — what the sprite is decided from (for the page's steps)
    const c = aim(), w = V.W * sc, h = V.H * sc;
    for (const m of meshes) m.visible = !(m.userData.g === 'watch' && !st.watchNow);
    if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
    renderer.setSize(w, h, false); MODE.value = V.mode === 'solid' ? 1 : 2; renderer.setRenderTarget(null); renderer.clear(); renderer.render(scene, camera);
    ctx.fillStyle = hexOf('d1'); ctx.fillRect(0, 0, w, h); ctx.fillStyle = hexOf('d2'); ctx.fillRect(0, V.floor * sc, w, h);
    ctx.drawImage(renderer.domElement, 0, 0);
    if (V.bones) {
      ctx.strokeStyle = ctx.fillStyle = '#f6b84a'; ctx.lineWidth = 2;
      const pt = b => { bones[b].getWorldPosition(_p); const [u, v] = project(c, _p); return [u * sc, v * sc]; };
      for (const b of BONES) { if (b === 'RightProp') continue; const a = pt(b), p = PARENT[b]; if (p) { const q = pt(p); ctx.beginPath(); ctx.moveTo(...q); ctx.lineTo(...a); ctx.stroke(); } ctx.beginPath(); ctx.arc(a[0], a[1], 3.5, 0, 7); ctx.fill(); }
    }
    return;
  }
  const g = picture(), w = g[0].length * sc, h = g.length * sc;
  if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
  ctx.clearRect(0, 0, w, h); draw(ctx, g, sc);
  lastGrid = g;
}
let lastGrid = null;

// the moment t (seconds): the pose of the clip at the sprite's 12 frames a second, the face's state
function frame(o = {}) {
  if (o.t !== undefined) st.t = o.t;
  if (o.expr) st.expr = o.expr;
  if (o.talk !== undefined) st.talk = o.talk;
  const clip = CLIPS[st.clip], M = st.M, tq = Math.floor(st.t * FPS + 1e-6) / FPS;
  const watch = !!clip.watch && V.face !== 'portrait';
  st.watchNow = watch;
  if (M) {
    const n = M.n, fr = tq * M.fps, loop = Math.floor(fr / n), f = fr - loop * n, kr = kr0(M);
    const off = clip.travel ? [(M.hips[(n - 1) * 3] - M.hips[0]) * kr * loop, (M.hips[(n - 1) * 3 + 2] - M.hips[2]) * kr * loop] : [0, 0];
    pose(M, f, { travel: clip.travel, offset: off, upright: clip.upright, watch, calm: clip.calm });
  } else pose(null, 0, { watch });
  // the figure is held to the pixel grid: the eye goes along with the pelvis exactly, the floor goes by in whole pixels
  if (clip.travel) { bones.Hips.getWorldPosition(_p); st.lock = [_p.x, _p.z]; const yw = V.yaw * Math.PI / 180; st.scroll = (st.lock[0] * Math.cos(yw) - st.lock[1] * Math.sin(yw)) / S * V.zoom; }
  else { st.lock = [0, 0]; st.scroll = 0; }
  st.F = st.live ? st.live.at(tq, st.expr, st.talk) : { expr: st.expr, blink: o.blink, mouth: o.mouth, look: o.look };
}
async function set(o) {
  for (const k of ['W', 'H', 'yaw', 'zoom', 'ax', 'ay', 'at', 'mode', 'bg', 'scale', 'floor', 'face', 'rules', 'bones']) if (o[k] !== undefined) V[k] = o[k];
  if (o.clip) { st.clip = o.clip; st.M = CLIPS[o.clip].motion ? await motion(CLIPS[o.clip].motion) : null; }
  if (o.live !== undefined) st.live = o.live ? new Live(o.seed ?? 16) : null;
  frame({ t: o.t ?? st.t, expr: o.expr, talk: o.talk, blink: o.blink, mouth: o.mouth, look: o.look });
}
// ready-made views
const VIEWS = {
  figure: { W: 58, H: 70, zoom: 1, ax: 29.5, ay: 62, at: 'floor', bg: 'figure', floor: 58, face: 'sprite' },
  portrait: { W: 56, H: 56, zoom: 2.6, ax: 28, ay: 24.5, at: 'head', bg: 'box', face: 'portrait' },
  stage: { W: 60, H: 56, zoom: 1, ax: 30.5, ay: 48, at: 'floor', bg: 'figure', floor: 44, face: 'sprite' },
};
window.A = { set, frame, render, V, st, CLIPS, VIEWS, EXPR_RU, grid: () => lastGrid, sprite, picture, duration: () => (st.M ? st.M.n / st.M.fps : 4), FPS, bones, J, S };
window.__ready = true;
