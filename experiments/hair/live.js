// The hair page in motion: a hairstyle on a body (Anny's woman, man or child, as moood bakes them) through Kimodo
// motions, with wind and head turns; the hair simulated (motion.js) and drawn with the hair shading (shade.js).
import * as THREE from 'three';
import { STYLES, NAMES } from './styles.js';
import { buildHair, headSDF } from './hair.js';
import { hairMaterial, inkMaterial } from './shade.js';
import { fitHead, bodyCapsules } from './fit.js';
import { HairRig, FPS } from './motion.js';
import { person, Pose, parseGarment, fitted, skinInto } from '../cloth/people.js';
import { moment } from '../cloth/sim.js';
import { nearestOn } from '../cloth/wardrobe.js';

const qs = new URLSearchParams(location.search);
const SHOTS = qs.has('shots');
const cache = {};
const bytes = name => (cache[name] ??= import('../data/' + name + '.js').then(m => Uint8Array.from(atob(m.default), c => c.charCodeAt(0)).buffer));
const META = await (await fetch('../data/meta.json')).json();

// ———— what can be chosen ————
const PEOPLE = {
  woman: { ru: 'женщина', wear: [['tshirt', '#e6e0d4'], ['pants', '#3f4452'], ['flats', '#2b211d']] },
  man: { ru: 'мужчина', wear: [['tshirt', '#cfc6b4'], ['pants', '#3e4a5c'], ['boots', '#2e231c']] },
  child: { ru: 'ребёнок', wear: [['tshirt', '#e8d9a8'], ['pants', '#4b5a6e'], ['flats', '#3a2c25']] },
};
// who wears each hairstyle first
const WHO = { gwen: 'woman', gogo: 'woman', jack: 'man', marco: 'child', ginger: 'child', ariel: 'woman', doll: 'child', kbuns: 'woman', kbraid: 'woman', kpony: 'woman', giulia: 'woman', alva: 'woman', nimona: 'woman', anime: 'woman' };
const MOTIONS = [
  { id: 'idle', ru: 'стоит', file: 'cloth/motions/idle', cyclic: true },
  { id: 'walk', ru: 'идёт', file: 'cloth/motions/walk', cyclic: true },
  { id: 'run', ru: 'бежит', file: 'cloth/motions/run', cyclic: true },
  { id: 'wave', ru: 'машет', file: 'indie/motions/wave' },
  { id: 'jump', ru: 'прыгает', file: 'cloth/motions/jump' },
  { id: 'dance', ru: 'танцует', file: 'cloth/motions/dance', cyclic: true },
  { id: 'bow', ru: 'кланяется', file: 'indie/motions/bow' },
  { id: 'sneak', ru: 'крадётся', file: 'indie/motions/sneak', cyclic: true },
  { id: 'stomp', ru: 'топает', file: 'indie/motions/stomp' },
  { id: 'sit', ru: 'садится на пол', file: 'cloth/motions/sit' },
  { id: 'lie', ru: 'ложится', file: 'cloth/motions/lie' },
  { id: 'roll', ru: 'кувырок', file: 'cloth/motions/roll' },
  { id: 'rollover', ru: 'перекатывается', file: 'cloth/motions/rollover' },
];
const WINDS = [{ id: 0, ru: 'нет' }, { id: 3, ru: 'лёгкий' }, { id: 12, ru: 'сильный' }];
const TURNS = [{ id: 'none', ru: 'прямо' }, { id: 'look', ru: 'оглядывается' }, { id: 'snap', ru: 'резко оборачивается' }];
const VIEWS = [{ id: 'head', ru: 'голова' }, { id: 'body', ru: 'в рост' }];
const state = { style: qs.get('s') && STYLES[qs.get('s')] ? qs.get('s') : 'alva', who: null, motion: MOTIONS.find(m => m.id === qs.get('m')) || MOTIONS[0], wind: +(qs.get('wind') || 0), turns: qs.get('turns') || 'none', view: qs.get('view') || 'head' };
state.who = PEOPLE[qs.get('who')] ? qs.get('who') : WHO[state.style];

// ———— the page ————
document.head.insertAdjacentHTML('beforeend', `<style>
html,body{margin:0;background:#d8d2c8;overflow:hidden;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
#stage{position:fixed;inset:0;touch-action:none;cursor:grab}#stage:active{cursor:grabbing}
#panel{position:fixed;left:12px;top:12px;max-width:min(560px,calc(100vw - 24px));display:grid;gap:6px;background:rgba(246,242,236,.86);border-radius:8px;padding:10px 12px;box-shadow:0 1px 6px rgba(0,0,0,.12);font-size:13px;color:#2a2622}
#panel .row{display:flex;flex-wrap:wrap;gap:4px;align-items:center}#panel .label{width:72px;color:#6e675e}
#panel button{font:inherit;font-size:12.5px;color:#2a2622;background:transparent;border:1px solid #c9c1b5;border-radius:999px;padding:3px 9px;cursor:pointer}
#panel button[aria-pressed=true]{background:#2a2622;color:#f6f2ec;border-color:#2a2622}
#msg{position:fixed;inset:0;display:grid;place-items:center;color:#4a4640;font-size:20px;font-style:italic;pointer-events:none}
[hidden]{display:none!important}
@media (max-width:560px){#panel .label{width:100%}}
</style>`);
document.body.insertAdjacentHTML('beforeend', `<div id="stage"></div><div id="panel"${SHOTS ? ' hidden' : ''}></div><div id="msg">собирается…</div>`);
const stage = document.getElementById('stage'), panel = document.getElementById('panel'), msg = document.getElementById('msg');
const W0 = +(qs.get('w') || innerWidth), H0 = +(qs.get('h') || innerHeight);
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(SHOTS ? 1 : Math.min(devicePixelRatio || 1, 2)); renderer.setSize(W0, H0); stage.appendChild(renderer.domElement);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const scene = new THREE.Scene(); scene.background = new THREE.Color(0xd8d2c8);
const camera = new THREE.PerspectiveCamera(22, W0 / H0, 0.05, 60);
// the same lights as the still hairstyles (the hair shading has them built in)
scene.add(new THREE.HemisphereLight(0xfff6ea, 0x6d6070, 1.25));
const key = new THREE.DirectionalLight(0xffffff, 2.1); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, { left: -1.2, right: 1.2, top: 1.2, bottom: -1.2, near: 0.2, far: 8 }); key.shadow.bias = -0.0005; key.shadow.normalBias = 0.01;
scene.add(key, key.target);
const rim = new THREE.DirectionalLight(0xdfe8ff, 1.1); scene.add(rim, rim.target);
const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({ color: 0xcbc3b6, roughness: 1 }));
ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);
const grid = new THREE.GridHelper(400, 400, 0xb9b0a3, 0xc0b7aa); grid.position.y = 0.0005; scene.add(grid);
const group = new THREE.Group(); scene.add(group);
addEventListener('resize', () => { if (SHOTS) return; renderer.setSize(innerWidth, innerHeight); camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); });

// ———— a hairstyle on a body ————
let cur = null;   // { S, body, rig, pose, meshes, hair, garments, M, run }
const BODY = {};
async function bodyOf(who) {
  if (BODY[who]) return BODY[who];
  const body = await person(THREE, bytes, META, who), fit = fitHead(body, META.people[who].eyes), caps = bodyCapsules(body);
  // the hair meets the T-shirt, not the skin under it
  for (const c of caps) if (/trunk|shoulder|arm/.test(c.name) && c.name !== 'forearm') c.r += 0.007;
  const garments = [];
  for (const [g, color] of PEOPLE[who].wear) {
    const G = parseGarment(await bytes(g)), pos = fitted(G, body.rest), near = nearestOn(body.rest, pos), n = pos.length / 3, J = new Uint8Array(n * 4), Wt = new Uint8Array(n * 4);
    for (let i = 0; i < n; i++) for (let k = 0; k < 4; k++) { J[i * 4 + k] = body.joint[near[i] * 4 + k]; Wt[i * 4 + k] = body.weight[near[i] * 4 + k]; }
    garments.push({ rest: Float32Array.from(pos), tris: G.tris, J, W: Wt, color });
  }
  // the skin under the clothes drawn sunk a few millimetres (as on the cloth page): the clothes ride the skin rigidly here,
  // and between their points the skin's own bulges would show through
  const all = Float32Array.from(garments.flatMap(g => Array.from(g.rest))), near = nearestOn(all, body.rest);
  // (and wherever the skin stands near or past the cloth, by as much as it takes to lie 4 mm under it)
  const sink = Float32Array.from(near, (j, i) => {
    const R = body.rest, n = body.nrm, dx = R[i * 3] - all[j * 3], dy = R[i * 3 + 1] - all[j * 3 + 1], dz = R[i * 3 + 2] - all[j * 3 + 2], d = Math.hypot(dx, dy, dz);
    const near01 = 1 - smooth01(0.012, 0.03, d), out = dx * n[i * 3] + dy * n[i * 3 + 1] + dz * n[i * 3 + 2];
    return near01 * Math.min(0.03, Math.max(0.007, out + 0.004 + (d < 0.03 ? 0.004 : 0)));
  });
  return BODY[who] = { body, fit, caps, garments, sink };
}
const smooth01 = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const BUILT = {};
function meshFrom(pos, nor, tris, mat, ink) {
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); if (nor) g.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
  g.setIndex(new THREE.BufferAttribute(tris, 1));
  const m = new THREE.Mesh(g, mat); m.frustumCulled = false; group.add(m);
  if (ink) { const g2 = new THREE.BufferGeometry(); g2.setAttribute('position', g.attributes.position); g2.setAttribute('normal', g.attributes.normal); g2.setAttribute('inkw', new THREE.BufferAttribute(ink, 1)); g2.setIndex(g.index); const o = new THREE.Mesh(g2, inkMaterial(THREE)); o.frustumCulled = false; group.add(o); m.userData.ink = g2; }
  return m;
}
async function load(style, who) {
  msg.textContent = 'собирается…'; msg.hidden = false; await new Promise(r => setTimeout(r, 30));
  const S = STYLES[style], B = await bodyOf(who), { body, fit, caps } = B;
  const built = BUILT[style] ??= buildHair(S, headSDF(S.head || {}).sdf);
  const rig = new HairRig(built, fit, body, caps);
  while (group.children.length) { const c = group.children.pop(); c.geometry?.dispose(); }
  const pose = new Pose(THREE, body), N = body.N;
  const bodyPos = new Float32Array(N * 3), bodyNrm = new Float32Array(N * 3);
  const skinMat = new THREE.MeshStandardMaterial({ color: S.skin || 0xe9c2a6, roughness: 0.6 });
  const bodyMesh = meshFrom(bodyPos, bodyNrm, body.tris, skinMat, new Float32Array(N).fill(0.0012)); bodyMesh.castShadow = bodyMesh.receiveShadow = true;
  const garments = B.garments.map(g => { const m = meshFrom(new Float32Array(g.rest.length), new Float32Array(g.rest.length), g.tris, new THREE.MeshStandardMaterial({ color: g.color, roughness: 0.85, side: THREE.DoubleSide })); m.castShadow = m.receiveShadow = true; return { g, m }; });
  // the hair: each surface drawn from the rig's skinned points
  const hair = rig.meshes.map((R, mi) => {
    const e = R.e, m = e.mesh, nv = R.nv, pos = new Float32Array(nv * 3), nor = new Float32Array(nv * 3), tan = new Float32Array(nv * 3), ao = m.ao ? Float32Array.from(m.ao) : null;
    rig.skin(mi, pos, nor, tan, m.ao, ao);
    let mesh, inner = null;
    if (e.plain) mesh = meshFrom(pos, nor, Uint32Array.from(m.idx), new THREE.MeshStandardMaterial({ color: e.part.color, roughness: e.rough ?? 0.8 }), new Float32Array(nv).fill(0.0012));
    else {
      const ink = new Float32Array(nv), th = e.ink ?? (e.lockLayer ? 0.0006 : 0.0009);
      for (let v = 0; v < nv; v++) ink[v] = th * (m.wd ? Math.min(1, Math.max(0.1, m.wd[v] / 0.006)) : 1);
      mesh = meshFrom(pos, nor, Uint32Array.from(m.idx), hairMaterial(THREE, S, { inner: e.inner }), ink);
      if (e.inner) inner = { ink0: Float32Array.from(ink), ink, moved: new Float32Array(nv), wide: new Float32Array(nv), idx: m.idx };
      const g = mesh.geometry;
      g.setAttribute('hairT', new THREE.BufferAttribute(tan, 3)); g.setAttribute('hairUV', new THREE.BufferAttribute(m.uv, 2));
      g.setAttribute('seed', new THREE.BufferAttribute(m.seed, 1)); g.setAttribute('ao', new THREE.BufferAttribute(ao, 1)); g.setAttribute('color', new THREE.BufferAttribute(m.col, 3));
    }
    mesh.castShadow = true;
    return { mesh, pos, nor, tan, mi, ao0: m.ao, ao, inner };
  });
  // standing at rest, the hair lies over the shoulders and back of this body (not through them): that is its rest
  const E0 = pose.skin(pose.at(null), bodyPos, bodyNrm).E, J0 = rig.jointsOf(E0);
  window.__sag = rig.groom(J0); rig.reset();
  // ?dbg=caps: the solids the hair meets, drawn over the body
  const dbg = qs.get('dbg') === 'caps' ? caps.map(c => { const m = new THREE.Mesh(new THREE.CapsuleGeometry(c.r, 1, 6, 16), new THREE.MeshBasicMaterial({ color: 0x2a7fff, transparent: true, opacity: 0.35, depthTest: false })); m.renderOrder = 9; group.add(m); return m; })
    .concat([fit.skull, fit.face].map(E => { const m = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16), new THREE.MeshBasicMaterial({ color: 0xff7f2a, transparent: true, opacity: 0.35, depthTest: false })); m.renderOrder = 9; group.add(m); return m; })) : null;
  cur = { style, who, S, body, rig, pose, bodyPos, bodyNrm, bodyMesh, garments, hair, B, dbg };
  await start();
  msg.hidden = true;
}
const MOT = {};
async function motionOf(m) {
  if (MOT[m.id]) return MOT[m.id];
  const M = await (await fetch('../' + m.file + '.json')).json();
  // (the earlier conversions have no lowest point of the whole skin: upright motions, the feet are it)
  M.low ??= M.foot.slice();
  return MOT[m.id] = M;
}
// ———— the head turned on top of the motion ————
const HEADSET = ['Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'];
function turnAngle(kind, t) {
  const t0 = t - 0.6; if (kind === 'none' || t0 <= 0) return 0;
  const ramp = Math.min(1, t0 / 0.8);
  if (kind === 'look') return ramp * 0.95 * Math.sin(t0 * 2 * Math.PI / 3.6);
  // quick turns: a look to one side, held, then a snap to the other
  const seq = [0, 1.1, -1.1, 0.0, -1.1, 1.1], seg = 1.3, k = Math.floor(t0 / seg), u = t0 - k * seg;
  const a = seq[k % seq.length], b = seq[(k + 1) % seq.length], s = Math.min(1, Math.max(0, (u - 0.85) / 0.28)), e = s * s * (3 - 2 * s);
  return a + (b - a) * e;
}
function turnHead(W, names, t) {
  const a = turnAngle(state.turns, t); if (!a) return;
  const neck = W[names.indexOf('Neck2')], axis = new THREE.Vector3(0, 1, 0).applyQuaternion(neck);
  for (let j = 0; j < names.length; j++) {
    const n = names[j], f = n === 'Neck1' ? 0.2 : n === 'Neck2' ? 0.5 : HEADSET.includes(n) ? 1 : 0;
    if (f) W[j].premultiply(new THREE.Quaternion().setFromAxisAngle(axis, a * f));
  }
}
// ———— running ————
async function start() {
  const c = cur; if (!c) return;
  c.M = await motionOf(state.motion); c.cyclic = !!state.motion.cyclic;
  c.pose = new Pose(THREE, c.body); c.rig.reset();
  c.run = { t: 0, JA: null, end: c.cyclic ? Infinity : 0.5 + 0.9 + c.M.n / FPS + 1.2 };
  c.wind = state.wind ? { speed: state.wind, dir: [0.42, 0, -0.91] } : null;
  frameAt(0); c.rig.place(c.run.JA); draw();
}
function frameAt(t) {
  const c = cur, st = moment(c.pose, c.M, t, c.cyclic);
  turnHead(st.W, c.body.names, t);
  const { E } = c.pose.skin(st, c.bodyPos, c.bodyNrm);
  c.E = E; c.run.JA = c.rig.jointsOf(E);
  const sk = c.B.sink, P = c.bodyPos, Nn = c.bodyNrm; for (let i = 0; i < sk.length; i++) if (sk[i]) { P[i * 3] -= Nn[i * 3] * sk[i]; P[i * 3 + 1] -= Nn[i * 3 + 1] * sk[i]; P[i * 3 + 2] -= Nn[i * 3 + 2] * sk[i]; }
}
function stepFrame() {
  const c = cur, r = c.run;
  if (r.t + 1 / FPS > r.end) { start(); return; }
  const JA = r.JA; r.t += 1 / FPS; frameAt(r.t);
  c.rig.step(JA, r.JA, c.wind);
}
function draw() {
  const c = cur;
  if (c.dbg) {
    const J = c.run.JA, a = [0, 0, 0], b = [0, 0, 0], V = THREE.Vector3;
    c.B.caps.forEach((cp, k) => { c.rig.carry(J, cp.ja, cp.a, a); c.rig.carry(J, cp.jb, cp.b, b); const m = c.dbg[k], A = new V(...a), Bv = new V(...b), d = Bv.clone().sub(A), L = d.length();
      m.position.copy(A).add(Bv).multiplyScalar(0.5); m.scale.set(1, Math.max(1e-4, L), 1); m.geometry.dispose(); m.geometry = new THREE.CapsuleGeometry(cp.r, Math.max(1e-4, L), 6, 16); m.scale.set(1, 1, 1);
      m.quaternion.setFromUnitVectors(new V(0, 1, 0), d.normalize()); });
    const hs = J[c.rig.headJ], q = new THREE.Quaternion(...hs.q), Jh = c.body.J[c.rig.headJ];
    [c.B.fit.skull, c.B.fit.face].forEach((E, k) => { const m = c.dbg[c.B.caps.length + k]; m.scale.set(...E.r); m.quaternion.copy(q); m.position.set(...E.c).sub(Jh).applyQuaternion(q).add(new THREE.Vector3(...hs.p)); });
  }
  c.bodyMesh.geometry.attributes.position.needsUpdate = true; c.bodyMesh.geometry.attributes.normal.needsUpdate = true;
  for (const { g, m } of c.garments) { const a = m.geometry.attributes.position; skinInto(g.rest, null, g.J, g.W, 255, c.E, a.array, null); a.needsUpdate = true; m.geometry.computeVertexNormals(); }
  for (const h of c.hair) {
    c.rig.skin(h.mi, h.pos, h.nor, h.tan, h.ao0, h.ao, h.inner?.moved); const g = h.mesh.geometry;
    if (h.inner) {
      // the inner layer's outline fades where it (or anything near it) has moved off where it lay: where it parts or
      // folds between locks, the outline's back would show through
      const I = h.inner, ix = I.idx, M = I.moved, Wd = I.wide;
      for (let pass = 0; pass < 3; pass++) {
        Wd.set(M);
        for (let t = 0; t < ix.length; t += 3) { const a = ix[t], b = ix[t + 1], d = ix[t + 2], m = Math.max(M[a], M[b], M[d]); if (m > Wd[a]) Wd[a] = m; if (m > Wd[b]) Wd[b] = m; if (m > Wd[d]) Wd[d] = m; }
        M.set(Wd);
      }
      for (let v = 0; v < M.length; v++) I.ink[v] = I.ink0[v] * (1 - Math.min(1, M[v] * 3));
      h.mesh.userData.ink.attributes.inkw.needsUpdate = true;
    }
    if (g.attributes.ao) g.attributes.ao.needsUpdate = true;
    g.attributes.position.needsUpdate = true; g.attributes.normal.needsUpdate = true; if (g.attributes.hairT) g.attributes.hairT.needsUpdate = true;
  }
}
// ———— the camera: on the head, or on the whole body; following it ————
const cam = { yaw: +(qs.get('yaw') || 0.55), pitch: +(qs.get('pitch') || 0.06), dist: null, target: new THREE.Vector3(), snap: true };
function follow() {
  const c = cur; if (!c?.run?.JA) return cam.target.clone();
  const hp = c.run.JA[c.rig.headJ].p;
  if (state.view === 'head') return new THREE.Vector3(hp[0], hp[1] - 0.03, hp[2]);
  const hip = c.E[c.body.names.indexOf('Hips')], J = c.body.J[c.body.names.indexOf('Hips')];
  const hy = hip[1] * J.x + hip[5] * J.y + hip[9] * J.z + hip[13];
  return new THREE.Vector3(hip[0] * J.x + hip[4] * J.y + hip[8] * J.z + hip[12], Math.max(0.35, hy * 0.8 + c.body.height * 0.15), hip[2] * J.x + hip[6] * J.y + hip[10] * J.z + hip[14]);
}
function place() {
  const f = follow(), dist = cam.dist ?? (state.view === 'head' ? (cur?.S.dist || 1.15) * 1.3 : 4.6);
  if (cam.snap) cam.target.copy(f); else cam.target.lerp(f, 0.12);
  const cp = Math.cos(cam.pitch);
  camera.position.set(cam.target.x + Math.sin(cam.yaw) * cp * dist, cam.target.y + Math.sin(cam.pitch) * dist, cam.target.z + Math.cos(cam.yaw) * cp * dist);
  camera.lookAt(cam.target);
  // on a wide window the person stands in the middle of what the controls leave free
  const W = renderer.domElement.clientWidth, H = renderer.domElement.clientHeight, pr = SHOTS ? 0 : panel.getBoundingClientRect().right;
  if (pr && W > pr * 1.5) camera.setViewOffset(W, H, -pr / 2, 0, W, H); else camera.clearViewOffset();
  key.position.copy(cam.target).add(new THREE.Vector3(1.2, 2.2, 2.4)); key.target.position.copy(cam.target);
  rim.position.copy(cam.target).add(new THREE.Vector3(-1.6, 1.4, -2.0)); rim.target.position.copy(cam.target);
}
let drag = null;
stage.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY }; stage.setPointerCapture(e.pointerId); });
stage.addEventListener('pointermove', e => { if (!drag) return; cam.yaw -= (e.clientX - drag.x) * 0.008; cam.pitch = Math.min(1.2, Math.max(-0.5, cam.pitch + (e.clientY - drag.y) * 0.005)); drag = { x: e.clientX, y: e.clientY }; });
stage.addEventListener('pointerup', () => drag = null); stage.addEventListener('pointercancel', () => drag = null);
stage.addEventListener('wheel', e => { e.preventDefault(); const d = cam.dist ?? (state.view === 'head' ? (cur?.S.dist || 1.15) * 1.3 : 4.6); cam.dist = Math.min(10, Math.max(0.5, d * Math.exp(e.deltaY * 0.001))); }, { passive: false });

// ———— controls ————
let playing = true;
function buttons(label, items, isOn, pick) {
  const row = document.createElement('div'); row.className = 'row'; row.setAttribute('role', 'group'); row.setAttribute('aria-label', label);
  row.innerHTML = `<span class="label">${label}</span>`;
  for (const it of items) { const b = document.createElement('button'); b.textContent = it.ru; b.setAttribute('aria-pressed', String(isOn(it))); b.addEventListener('click', () => pick(it)); row.append(b); }
  panel.append(row);
}
function controls() {
  panel.innerHTML = '';
  buttons('Причёска', Object.keys(STYLES).map(id => ({ id, ru: NAMES[id].split(':')[0] })), it => it.id === state.style, it => { state.style = it.id; state.who = WHO[it.id]; controls(); load(state.style, state.who); });
  buttons('Кто', Object.entries(PEOPLE).map(([id, p]) => ({ id, ru: p.ru })), it => it.id === state.who, it => { state.who = it.id; controls(); load(state.style, state.who); });
  buttons('Движение', MOTIONS, it => it.id === state.motion.id, it => { state.motion = it; controls(); start(); });
  buttons('Ветер', WINDS, it => it.id === state.wind, it => { state.wind = it.id; controls(); start(); });
  buttons('Голова', TURNS, it => it.id === state.turns, it => { state.turns = it.id; controls(); start(); });
  buttons('Вид', [...VIEWS, { id: 'pause', ru: playing ? 'пауза' : 'дальше' }], it => it.id === state.view, it => { if (it.id === 'pause') playing = !playing; else { state.view = it.id; cam.dist = null; } controls(); });
}
controls();
let last = performance.now(), acc = 0;
(function loop(now) {
  if (SHOTS) return;
  requestAnimationFrame(loop);
  if (cur?.run && playing) { acc += Math.min(0.1, (now - last) / 1000); let k = 0; while (acc >= 1 / FPS && k < 3) { stepFrame(); acc -= 1 / FPS; k++; } if (k) draw(); if (acc > 1 / FPS) acc = 0; }
  last = now;
  place(); cam.snap = false; renderer.render(scene, camera);
})(performance.now());
await load(state.style, state.who);

// for pictures: load, start, run frames, look
window.__hair = {
  STYLES, MOTIONS, state, cam, now: () => cur,
  async load(o) { Object.assign(state, { style: o.style, who: o.who || WHO[o.style] }); await load(state.style, state.who); },
  async start(o) { cur.rig.rigid = !!o.rigid; state.motion = MOTIONS.find(m => m.id === o.motion); state.wind = o.wind || 0; state.turns = o.turns || 'none'; await start(); },
  run(n) { for (let i = 0; i < n; i++) stepFrame(); draw(); return cur.run.t; },
  ink(on, which) { group.traverse(o => { if (!o.material?.uniforms?.ink) return; const h = cur.hair.find(h => h.mesh.userData.ink === o.geometry); if (!which || (which === 'inner') === !!h?.inner) o.visible = on; }); },
  look(v) { Object.assign(cam, v); state.view = v.view || state.view; cam.snap = true; place(); renderer.render(scene, camera); },
  // how the chains are: the largest speed, any point not a number, the deepest point in the head's skull
  stats() { const r = cur.rig; let bad = 0, vmax = 0; for (let i = 0; i < r.x.length; i++) { if (!Number.isFinite(r.x[i])) bad++; } for (let i = 0; i < r.v.length; i += 3) vmax = Math.max(vmax, Math.hypot(r.v[i], r.v[i + 1], r.v[i + 2])); return { bad, vmax, t: cur.run.t }; },
};
window.__ready = true;
