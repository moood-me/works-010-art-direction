// The viewer: Савелий Петрович moving by Kimodo's motions through the engine (engine/src as it is; its file reading pointed at
// this folder's data/), with the live face (face.mjs, life.mjs), lit as a puppet on a small set: a warm key with soft
// shadows, a cool rim, physical materials for resin skin, sculpted hair, glass eyes, gold wire and woven cloth (the
// cloth's weave and the hair's strands are drawn in the shader from the paint coordinates).
// Drag to turn, wheel to come closer. ?shots=1 hides the controls (window.A for scripted pictures).
// This is the page's fast variant (fast.html; view.html and view.mjs beside it are the page as it was): the skin is
// skinned in the vertex shader (engine-gpu/src/gpuskin.js), in the puppet's materials and in the shadow's; the
// processor works out the joints, the floor from a probe of the skin, and the face — its vertices and their normals
// at rest (the head is rigid on its joint), and only when the face's numbers changed.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { Face } from './face.mjs';
import { lifeTrack, headFacing, FACES } from './life.mjs';
import { GpuSkin } from '../../../../engine-gpu/src/gpuskin.js';

const ENGINE = new URL('../../../../engine/', import.meta.url);
const DATA = new URL('../../data/', import.meta.url);
const TEX = new URL('tex/', import.meta.url);
const E_ = p => import(new URL('src/' + p, ENGINE).href);
const { createEngine } = await E_('engine.js');
const { resolve } = await E_('character.js');
const { qRot } = await E_('math.js');
const { newSample } = await E_('motion.js');
const { loadPack } = await E_('pack.js');

const read = async url => {
  const u = new URL(url), m = u.pathname.match(/\/data\/(bodies|topology)\/savely8\.(json|bin)$/);
  const r = await fetch(m ? new URL(`${m[1]}/savely8.${m[2]}`, DATA) : u);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.arrayBuffer();
};
const shots = new URLSearchParams(location.search).has('shots');
if (shots) document.body.classList.add('shots');
const E = await createEngine({ root: ENGINE, read });
// the engine's dual-quaternion skinning here (its default, centres of rotation, takes long to prepare 50 000
// vertices in a browser); the films use the default
const spec = resolve({ format: 'engine/character', version: 1, id: 'savely8', label: { ru: 'Савелий Петрович' }, body: 'savely8',
  skinning: { method: 'dqs', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: { armsOutOfHead: { margin: 0.03 } } } });
const fig = await E.figure(spec, { position: [0, 0, 0], heading: 0 });
const body = fig.body, N = body.N, HI = body.skeleton.index.Head, HIPS = body.skeleton.index.Hips;
const face = new Face(await loadPack(new URL('face.json', DATA).href, read));
const look = await loadPack(new URL('look.json', DATA).href, read);
const rest = body.positions, disp = new Float32Array(rest.length);
const gs = new GpuSkin(THREE, fig.skinner);

// ------------------------------------------------------------------ three.js: the set
const stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: shots });
renderer.setPixelRatio(Math.min(2, devicePixelRatio));
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
stage.appendChild(renderer.domElement);
document.getElementById('msg').remove();
const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;
scene.environmentIntensity = 0.25;

// the backdrop: the drawing's set — dark blue-grey, a warm pool of light, out-of-focus lamps (painted once)
function backdrop() {
  const c = document.createElement('canvas'); c.width = 1024; c.height = 640; const g = c.getContext('2d');
  const lg = g.createLinearGradient(0, 0, 0, 640); lg.addColorStop(0, '#1c1410'); lg.addColorStop(0.75, '#2a1e18'); lg.addColorStop(1, '#2a2220');
  g.fillStyle = lg; g.fillRect(0, 0, 1024, 640);
  const rg = g.createRadialGradient(330, 200, 10, 330, 200, 520); rg.addColorStop(0, 'rgba(224,160,80,0.5)'); rg.addColorStop(0.5, 'rgba(224,160,80,0.14)'); rg.addColorStop(1, 'rgba(224,160,80,0)');
  g.fillStyle = rg; g.fillRect(0, 0, 1024, 640);
  let s = 5; const R = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const cols = ['255,207,138', '255,176,112', '255,224,176', '154,184,255', '255,154,112'];
  g.filter = 'blur(6px)';
  for (let i = 0; i < 22; i++) {
    const x = R() * 1024, y = R() * 560, r = 14 + R() * 38;
    g.fillStyle = `rgba(${cols[Math.floor(R() * cols.length)]},${0.12 + R() * 0.3})`;
    g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
  }
  g.filter = 'none';
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
scene.background = backdrop();
const camera = new THREE.PerspectiveCamera(26, 1, 0.05, 50);
camera.position.set(-0.9, 0.95, 2.6);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.62, 0); controls.enableDamping = !shots; controls.minDistance = 0.4; controls.maxDistance = 6; controls.update();

const key = new THREE.DirectionalLight('#ffe2c2', 3.2); key.position.set(-1.6, 2.2, 1.6); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); key.shadow.camera.left = -1; key.shadow.camera.right = 1; key.shadow.camera.top = 1.6;
key.shadow.camera.bottom = -0.4; key.shadow.camera.near = 0.5; key.shadow.camera.far = 6; key.shadow.radius = 5; key.shadow.bias = -0.0004;
key.shadow.normalBias = 0.01;
const rim = new THREE.DirectionalLight('#a8c4ff', 1.3); rim.position.set(1.4, 1.4, -1.6);
const fill = new THREE.HemisphereLight('#c8c4d8', '#2a2018', 0.4);
const rig = new THREE.Group(); rig.add(key, rim, key.target, rim.target); scene.add(rig, fill);

// the floor: dark boards fading into the set
const floorMat = new THREE.MeshStandardMaterial({ color: '#1c1818', roughness: 0.85, envMapIntensity: 0.2, transparent: true });
floorMat.onBeforeCompile = sh => {
  sh.fragmentShader = sh.fragmentShader.replace('#include <dithering_fragment>',
    '#include <dithering_fragment>\n gl_FragColor.a *= smoothstep(4.0, 1.2, length(vFloorW.xz - floorC));');
  sh.vertexShader = 'varying vec3 vFloorW;\n' + sh.vertexShader.replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\n vFloorW = (modelMatrix * vec4(transformed, 1.0)).xyz;');
  sh.fragmentShader = 'varying vec3 vFloorW; uniform vec2 floorC;\n' + sh.fragmentShader;
  sh.uniforms.floorC = floorC;
};
const floorC = { value: new THREE.Vector2() };
const floor = new THREE.Mesh(new THREE.CircleGeometry(5, 96), floorMat);
floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);

// ------------------------------------------------------------------ the puppet's materials
const tl = new THREE.TextureLoader();
const tex = (n, srgb = true) => { const t = tl.load(new URL(n, TEX).href); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; };
// the skinning in a material's vertex shader: the skinned place and normal where the rest's were taken
function skinInto(sh) {
  sh.uniforms.skinTex = gs.uniforms.skinTex;
  sh.vertexShader = gs.glsl + '\n' + sh.vertexShader
    .replace('#include <beginnormal_vertex>', '#include <beginnormal_vertex>\n vec3 skinP; skinVertex(position, normal, skinP, objectNormal);')
    .replace('#include <begin_vertex>', '#include <begin_vertex>\n transformed = skinP;');
}
// a shader addition: the paint coordinates (tuv, pat) in, a bump from a height function h(tuv, pat), a colour change
function sculpted(mat, { height, colour }) {
  mat.onBeforeCompile = sh => {
    skinInto(sh);
    sh.vertexShader = 'attribute vec3 pat; varying vec3 vPat; varying vec2 vTuv;\n' + sh.vertexShader
      .replace('#include <uv_vertex>', '#include <uv_vertex>\n vPat = pat; vTuv = uv;');
    sh.fragmentShader = 'varying vec3 vPat; varying vec2 vTuv;\n' + sh.fragmentShader
      .replace('#include <color_fragment>', `#include <color_fragment>\n${colour || ''}`)
      .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
        { float h = ${height};
          vec3 dpx = dFdx(-vViewPosition), dpy = dFdy(-vViewPosition);
          vec3 r1 = cross(dpy, normal), r2 = cross(normal, dpx);
          float det = dot(dpx, r1);
          vec3 grad = sign(det) * (dFdx(h) * r1 + dFdy(h) * r2);
          normal = normalize(abs(det) * normal - grad); }`);
  };
  return mat;
}
const P = (o) => { const m = new THREE.MeshPhysicalMaterial(o); m.onBeforeCompile = skinInto; return m; };
const cloth = (color, weave, o = {}) => sculpted(P({ color, roughness: 0.88, sheen: 0.4, sheenRoughness: 0.5, sheenColor: '#ffffff', ...o }), {
  height: '0.0' });      // the weave of the renders is finer than a screen pixel here: left out (it turned to moiré)
const hairy = color => sculpted(P({ color, roughness: 0.6, clearcoat: 0.1, clearcoatRoughness: 0.4 }), {
  height: '0.0012 * sin(vTuv.x * 28.3) + 0.0005 * sin(vTuv.x * 37.0)' });
const MATS = {
  skin: P({ map: tex('face.png'), bumpMap: tex('bump.png', false), bumpScale: 1.5, roughness: 0.48, clearcoat: 0.15, clearcoatRoughness: 0.4, sheen: 0.25, sheenColor: '#ff9a80', vertexColors: true }),
  hair: hairy('#e8e2d8'), whisker: hairy('#ece6dc'),
  eye: P({ map: tex('iris.png'), roughness: 0.25, clearcoat: 1.0, clearcoatRoughness: 0.02 }),
  gold: P({ color: '#c89a4a', metalness: 1.0, roughness: 0.3 }), chain: P({ color: '#d8a840', metalness: 1.0, roughness: 0.35 }),
  lens: P({ color: '#eef4ff', roughness: 0.05, transparent: true, opacity: 0.16, clearcoat: 1.0, side: THREE.DoubleSide, depthWrite: false }),
  vest: cloth('#6e4c34', 1400), shirt: cloth('#e2d6bc', 2200, { roughness: 0.75, sheen: 0.2 }), collar: cloth('#efe4cc', 2200, { roughness: 0.7, sheen: 0.2 }),
  tie: cloth('#7a2a2a', 1800, { roughness: 0.45, sheen: 0.5 }), trousers: cloth('#4a4a52', 1200),
  button: P({ color: '#3a2418', roughness: 0.3, clearcoat: 0.5 }), dark: P({ color: '#120c0a', roughness: 0.9 }),
  shoe: P({ color: '#3a2418', roughness: 0.35, clearcoat: 0.4 }), sole: P({ color: '#1c1410', roughness: 0.7 }),
  lip: P({ color: '#b05a58', roughness: 0.4, clearcoat: 0.15 }), mouth: P({ color: '#3a1418', roughness: 0.6 }),
  teeth: P({ color: '#f1e8dc', roughness: 0.3, clearcoat: 0.3 }), lash: P({ color: '#3a2420', roughness: 0.5 }),
};
const matList = Object.values(MATS), matIndex = Object.fromEntries(Object.keys(MATS).map((k, i) => [k, i]));

const geo = gs.attributes(new THREE.BufferGeometry());      // the rest's normals, each vertex's joints and weights
const pos = new Float32Array(N * 3); pos.set(rest);          // the rest with the face's shapes on it
geo.setAttribute('position', new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage));
const nor = geo.attributes.normal.array; geo.attributes.normal.setUsage(THREE.DynamicDrawUsage);
geo.setAttribute('uv', new THREE.BufferAttribute(look.arrays.uv, 2));
geo.setAttribute('pat', new THREE.BufferAttribute(look.arrays.pat, 3));
const col = new Float32Array(N * 3), tintC = new THREE.Color('#f0a898');
for (let i = 0; i < N; i++) { const t = look.arrays.tint[i]; col[i * 3] = 1 + (tintC.r - 1) * t; col[i * 3 + 1] = 1 + (tintC.g - 1) * t; col[i * 3 + 2] = 1 + (tintC.b - 1) * t; }
geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
geo.setIndex(new THREE.BufferAttribute(body.triangles, 1));
{ let t0 = 0; look.header.pieces.forEach((p, k) => { const n = look.header.tris[k] * 3; geo.addGroup(t0, n, matIndex[p.mat]); t0 += n; }); }
const mesh = new THREE.Mesh(geo, matList); mesh.castShadow = true; mesh.receiveShadow = true; mesh.frustumCulled = false;
mesh.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking });      // the shadow's, skinned too
mesh.customDepthMaterial.onBeforeCompile = sh => {
  sh.uniforms.skinTex = gs.uniforms.skinTex;
  sh.vertexShader = gs.glsl + '\n' + sh.vertexShader
    .replace('#include <begin_vertex>', '#include <begin_vertex>\n { vec3 skinN; skinVertex(position, normal, transformed, skinN); }');
};
scene.add(mesh);

function resize() {
  const w = stage.clientWidth, h = stage.clientHeight;
  renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
}
addEventListener('resize', resize); resize();

// ------------------------------------------------------------------ motion, face, controls
const index = await E.motions();
const sel = document.getElementById('motion');
const SHOW = ['walk', 'bow', 'idle', 'wave', 'stomp', 'sit', 'sneak', 'dance', 'jump', 'run'];
for (const id of SHOW) { const m = index.motions.find(x => x.id === id); if (!m) continue;
  const o = document.createElement('option'); o.value = id; o.textContent = m.label.ru; sel.appendChild(o); }
const RU = { calm: 'спокоен', stern: 'строг', grumpy: 'ворчит', tired: 'устал', joy: 'радость', surprise: 'удивление', sad: 'грусть', anger: 'злость' };
const exprBox = document.getElementById('expr');
let target = 'calm';
const ew = Object.fromEntries(FACES.map(k => [k, k === 'calm' ? 1 : 0])), ev = Object.fromEntries(FACES.map(k => [k, 0]));
for (const k of FACES) {
  const b = document.createElement('button'); b.textContent = RU[k]; b.dataset.k = k; if (k === 'calm') b.classList.add('on');
  b.onclick = () => { target = k; exprBox.querySelectorAll('button').forEach(x => x.classList.toggle('on', x.dataset.k === k)); };
  exprBox.appendChild(b);
}
const talk = document.getElementById('talk'), time = document.getElementById('time'), playB = document.getElementById('play');
let clip, life, t = 0, playing = true, fps = 30, near = false;
const smp = newSample(body.skeleton.J);
async function choose(id) { clip = await E.clip([id]); fps = clip.fps ?? 30; t = 0; makeLife(); }
function makeLife() {
  const head = s => headFacing(fig.retarget.pose(clip.sample(Math.min(clip.frames - 1, s * fps), smp)), HI, qRot);
  life = lifeTrack(head, { seconds: clip.frames / fps, seed: 7, talk: talk.checked, expr: { calm: 1 } });
}
sel.onchange = () => choose(sel.value);
talk.onchange = () => makeLife();
playB.onclick = () => { playing = !playing; playB.textContent = playing ? '❚❚' : '▶'; playB.classList.toggle('on', playing); };
time.oninput = () => { t = +time.value * (clip.frames - 1) / fps; };
document.getElementById('close').onclick = e => { near = !near; e.target.classList.toggle('on', near); placeCamera(); };
await choose('walk');

const follow = new THREE.Vector3();
function placeCamera() {
  const hx = fig.pose ? fig.pose.P[HIPS * 3] : 0, hz = fig.pose ? fig.pose.P[HIPS * 3 + 2] : 0;
  const hy = fig.pose ? fig.pose.P[HI * 3 + 1] : 0.85;
  if (near) { const fx = fig.pose ? fig.pose.P[HI * 3] : hx, fz = fig.pose ? fig.pose.P[HI * 3 + 2] : hz;
    controls.target.set(fx, hy + 0.1, fz); camera.position.set(fx - 0.45, hy + 0.16, fz + 1.55); }
  else { controls.target.set(hx, 0.62, hz); camera.position.set(hx - 0.9, 0.95, hz + 2.6); }
  controls.update();
}
// The face moves its vertices at rest: the head is rigid on its joint, so the shader's skinning carries the moved
// rest as the old page's turn of (displaced − rest) after skinning did. The normals of the moved vertices and of
// those in a triangle with one are found again from the rest's triangles (the rest of the skin keeps the rest's).
const moved = Int32Array.from(face.moved), tris = body.triangles, touch = new Uint8Array(N);
for (const i of moved) touch[i] = 1;
for (let k = 0; k < tris.length; k += 3) if ((touch[tris[k]] | touch[tris[k + 1]] | touch[tris[k + 2]]) & 1) { touch[tris[k]] |= 2; touch[tris[k + 1]] |= 2; touch[tris[k + 2]] |= 2; }
const nearV = Int32Array.from(touch.keys()).filter(i => touch[i]);
const nearT = Int32Array.from(tris).filter((_, k) => { const o = k - k % 3; return touch[tris[o]] || touch[tris[o + 1]] || touch[tris[o + 2]]; });
const span = v => { let a = Infinity, b = -Infinity; for (const i of v) { if (i < a) a = i; if (i > b) b = i; } return [a * 3, (b - a + 1) * 3]; };
const movedSpan = span(moved), nearSpan = span(nearV);
function faceNormals() {
  for (const i of nearV) nor[i * 3] = nor[i * 3 + 1] = nor[i * 3 + 2] = 0;
  for (let k = 0; k < nearT.length; k += 3) {
    const a = nearT[k] * 3, b = nearT[k + 1] * 3, c = nearT[k + 2] * 3;
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2];
    const vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    if (touch[nearT[k]]) { nor[a] += nx; nor[a + 1] += ny; nor[a + 2] += nz; }
    if (touch[nearT[k + 1]]) { nor[b] += nx; nor[b + 1] += ny; nor[b + 2] += nz; }
    if (touch[nearT[k + 2]]) { nor[c] += nx; nor[c + 1] += ny; nor[c + 2] += nz; }
  }
  for (const i of nearV) { const o = i * 3, l = Math.hypot(nor[o], nor[o + 1], nor[o + 2]) || 1; nor[o] /= l; nor[o + 1] /= l; nor[o + 2] /= l; }
}
const J = body.skeleton.J;
let faceWas = '';
let last = performance.now();
function step(dt) {
  if (playing) { t += dt; if (t > (clip.frames - 1) / fps) t = 0; time.value = t * fps / (clip.frames - 1); }
  // the expression follows the buttons with a critically damped spring (smooth changes, mixes on the way)
  for (const k of FACES) { const w = 9, a = w * w * ((k === target ? 1 : 0) - ew[k]) - 2 * w * ev[k]; ev[k] += a * dt; ew[k] += ev[k] * dt; }
  const pose = fig.retarget.placed(fig.retarget.pose(clip.sample(t * fps, fig.sample)));
  const shift = pose.floor - gs.lowest(pose);                // on the floor, as motion.floor 'lowest'
  for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
  gs.setPose(pose); fig.pose = pose;
  const st = life.at(t); st.e = { ...ew };
  const fk = JSON.stringify(st);
  if (fk !== faceWas) {                                      // the face is worked out and sent only when its numbers changed
    face.apply(st, rest, disp);
    for (const i of moved) { pos[i * 3] = disp[i * 3]; pos[i * 3 + 1] = disp[i * 3 + 1]; pos[i * 3 + 2] = disp[i * 3 + 2]; }
    faceNormals();
    const pa = geo.attributes.position, na = geo.attributes.normal;
    pa.clearUpdateRanges(); pa.addUpdateRange(...movedSpan); pa.needsUpdate = true;
    na.clearUpdateRanges(); na.addUpdateRange(...nearSpan); na.needsUpdate = true;
    faceWas = fk;
  }
  // the camera and the lamps go along with him
  follow.set(fig.pose.P[HIPS * 3], 0, fig.pose.P[HIPS * 3 + 2]);
  const d = new THREE.Vector3(follow.x - floorC.value.x, 0, follow.z - floorC.value.y);
  controls.target.add(d); camera.position.add(d); floorC.value.set(follow.x, follow.z);
  rig.position.set(follow.x, 0, follow.z); key.target.position.set(0, 0.6, 0); rim.target.position.set(0, 0.6, 0);
  floor.position.set(follow.x, 0, follow.z);
}
function frame(now) {
  const dt = Math.min(0.05, (now - last) / 1000); last = now;
  step(dt); controls.update(); renderer.render(scene, camera);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
window.A = { async set(o) { if (o.motion) await choose(o.motion); if (o.t != null) t = o.t; if (o.expr) { target = o.expr; for (const k of FACES) { ew[k] = k === o.expr ? 1 : 0; ev[k] = 0; } }
  if (o.talk != null) { talk.checked = o.talk; makeLife(); } if (o.near != null) { near = o.near; } playing = false; step(0); placeCamera(); controls.update(); renderer.render(scene, camera); } };
window.__ready = true;
