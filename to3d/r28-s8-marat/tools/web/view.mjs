// The viewer: Марат moving by Kimodo's motions through the engine (engine/src as it is; its file reading pointed at
// this folder's data/), with the live face (face.mjs, life.mjs), lit as a puppet on a small set: a warm key with soft
// shadows, a cool rim, physical materials for resin skin, sculpted hair, glass eyes, gold wire and woven cloth (the
// cloth's weave and the hair's strands are drawn in the shader from the paint coordinates).
// Drag to turn, wheel to come closer. ?shots=1 hides the controls (window.A for scripted pictures).
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { Face } from './face.mjs';
import { lifeTrack, headFacing, FACES } from './life.mjs';

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
  const u = new URL(url), m = u.pathname.match(/\/data\/(bodies|topology)\/marat8\.(json|bin)$/);
  const r = await fetch(m ? new URL(`${m[1]}/marat8.${m[2]}`, DATA) : u);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.arrayBuffer();
};
const shots = new URLSearchParams(location.search).has('shots');
if (shots) document.body.classList.add('shots');
const E = await createEngine({ root: ENGINE, read });
// the engine's dual-quaternion skinning here (its default, centres of rotation, takes long to prepare 50 000
// vertices in a browser); the films use the default
const spec = resolve({ format: 'engine/character', version: 1, id: 'marat8', label: { ru: 'Марат' }, body: 'marat8',
  skinning: { method: 'dqs', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: { armsOutOfHead: { margin: 0.03 } } } });
const fig = await E.figure(spec, { position: [0, 0, 0], heading: 0 });
const body = fig.body, N = body.N, HI = body.skeleton.index.Head, HIPS = body.skeleton.index.Hips;
const face = new Face(await loadPack(new URL('face.json', DATA).href, read));
const look = await loadPack(new URL('look.json', DATA).href, read);
const rest = body.positions, disp = new Float32Array(rest.length);

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
  const lg = g.createLinearGradient(0, 0, 0, 640); lg.addColorStop(0, '#1c120e'); lg.addColorStop(0.75, '#2a1c16'); lg.addColorStop(1, '#2c221c');
  g.fillStyle = lg; g.fillRect(0, 0, 1024, 640);
  const rg = g.createRadialGradient(330, 200, 10, 330, 200, 520); rg.addColorStop(0, 'rgba(232,164,88,0.5)'); rg.addColorStop(0.5, 'rgba(232,164,88,0.14)'); rg.addColorStop(1, 'rgba(232,164,88,0)');
  g.fillStyle = rg; g.fillRect(0, 0, 1024, 640);
  let s = 14; const R = () => (s = (s * 16807) % 2147483647) / 2147483647;
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
camera.position.set(-1.0, 1.05, 3.0);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.7, 0); controls.enableDamping = !shots; controls.minDistance = 0.4; controls.maxDistance = 6; controls.update();

const key = new THREE.DirectionalLight('#ffe2c2', 3.2); key.position.set(-1.6, 2.2, 1.6); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); key.shadow.camera.left = -1; key.shadow.camera.right = 1; key.shadow.camera.top = 1.8;
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
// a shader addition: the paint coordinates (tuv, pat) in, a bump from a height function h(tuv, pat), a colour change
function sculpted(mat, { height, colour }) {
  mat.onBeforeCompile = sh => {
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
const P = (o) => new THREE.MeshPhysicalMaterial(o);
const cloth = (color, weave, o = {}) => sculpted(P({ color, roughness: 0.88, sheen: 0.4, sheenRoughness: 0.5, sheenColor: '#ffffff', ...o }), {
  height: `0.0005 * sin((vPat.x + vPat.y) * ${weave}.0) * sin(vPat.z * ${weave}.0)` });
const hairy = color => sculpted(P({ color, roughness: 0.55, clearcoat: 0.1, clearcoatRoughness: 0.4 }), {
  height: '0.0012 * sin(vTuv.x * 28.3) + 0.0005 * sin(vTuv.x * 37.0)' });
const MATS = {
  skin: P({ map: tex('face.png'), bumpMap: tex('bump.png', false), bumpScale: 1.5, roughness: 0.48, clearcoat: 0.15, clearcoatRoughness: 0.4, sheen: 0.25, sheenColor: '#ff9a70', vertexColors: true }),
  curl: sculpted(P({ color: '#2e2320', roughness: 0.5, clearcoat: 0.2, clearcoatRoughness: 0.35 }), {
    height: '0.0016 * sin(vTuv.x + vTuv.y * 15.0)', colour: 'diffuseColor.rgb *= 0.55 + 0.45 * (0.5 + 0.5 * sin(vTuv.x + vTuv.y * 15.0));' }),
  hairmass: P({ color: '#0c0808', roughness: 0.7 }), brow: hairy('#1e1614'),
  eye: P({ map: tex('iris.png'), roughness: 0.25, clearcoat: 1.0, clearcoatRoughness: 0.02 }),
  jacket: cloth('#ece2d0', 1500, { roughness: 0.8, sheen: 0.3 }), apron: cloth('#c4582c', 1100), aprontie: cloth('#a84a24', 1100),
  towel: sculpted(P({ color: '#f7f2e8', roughness: 0.95, sheen: 0.7, sheenRoughness: 0.6 }), { height: '0.0',
    colour: 'if ((vPat.y > 1.3 && vPat.y < 1.335) || (vPat.y > 1.365 && vPat.y < 1.385)) diffuseColor.rgb = vec3(0.55, 0.1, 0.025);' }),
  trousers: cloth('#56504e', 1200),
  shoe: P({ color: '#3a2a22', roughness: 0.4, clearcoat: 0.35 }), sole: P({ color: '#1c1410', roughness: 0.7 }),
  lip: P({ color: '#b25a50', roughness: 0.4, clearcoat: 0.2 }), mouth: P({ color: '#3a1418', roughness: 0.6 }),
  tongue: P({ color: '#a8444a', roughness: 0.4, clearcoat: 0.2 }),
  teeth: P({ color: '#f1e8dc', roughness: 0.3, clearcoat: 0.3 }), lash: P({ color: '#1c1210', roughness: 0.5 }),
};
const matList = Object.values(MATS), matIndex = Object.fromEntries(Object.keys(MATS).map((k, i) => [k, i]));

const geo = new THREE.BufferGeometry();
const pos = new Float32Array(N * 3); pos.set(rest);
geo.setAttribute('position', new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage));
geo.setAttribute('uv', new THREE.BufferAttribute(look.arrays.uv, 2));
geo.setAttribute('pat', new THREE.BufferAttribute(look.arrays.pat, 3));
const col = new Float32Array(N * 3), tintC = new THREE.Color('#f0a898');
for (let i = 0; i < N; i++) { const t = look.arrays.tint[i]; col[i * 3] = 1 + (tintC.r - 1) * t; col[i * 3 + 1] = 1 + (tintC.g - 1) * t; col[i * 3 + 2] = 1 + (tintC.b - 1) * t; }
geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
geo.setIndex(new THREE.BufferAttribute(body.triangles, 1));
{ let t0 = 0; look.header.pieces.forEach((p, k) => { const n = look.header.tris[k] * 3; geo.addGroup(t0, n, matIndex[p.mat]); t0 += n; }); }
geo.computeVertexNormals();
const mesh = new THREE.Mesh(geo, matList); mesh.castShadow = true; mesh.receiveShadow = true; mesh.frustumCulled = false;
scene.add(mesh);

function resize() {
  const w = stage.clientWidth, h = stage.clientHeight;
  renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
}
addEventListener('resize', resize); resize();

// ------------------------------------------------------------------ motion, face, controls
const index = await E.motions();
const sel = document.getElementById('motion');
const SHOW = ['wave', 'walk', 'dance', 'stomp', 'bow', 'idle', 'sit', 'jump', 'run', 'sneak'];
for (const id of SHOW) { const m = index.motions.find(x => x.id === id); if (!m) continue;
  const o = document.createElement('option'); o.value = id; o.textContent = m.label.ru; sel.appendChild(o); }
const RU = { calm: 'спокоен', beam: 'сияет', laugh: 'хохочет', surprise: 'удивление', sad: 'грусть', anger: 'злость' };
const REST = 'beam';          // his resting face is a wide smile
const exprBox = document.getElementById('expr');
let target = REST;
const ew = Object.fromEntries(FACES.map(k => [k, k === REST ? 1 : 0])), ev = Object.fromEntries(FACES.map(k => [k, 0]));
for (const k of FACES) {
  const b = document.createElement('button'); b.textContent = RU[k]; b.dataset.k = k; if (k === REST) b.classList.add('on');
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
await choose('wave');

const follow = new THREE.Vector3();
function placeCamera() {
  const hx = fig.pose ? fig.pose.P[HIPS * 3] : 0, hz = fig.pose ? fig.pose.P[HIPS * 3 + 2] : 0;
  const hy = fig.pose ? fig.pose.P[HI * 3 + 1] : 0.85;
  if (near) { const fx = fig.pose ? fig.pose.P[HI * 3] : hx, fz = fig.pose ? fig.pose.P[HI * 3 + 2] : hz;
    controls.target.set(fx, hy + 0.1, fz); camera.position.set(fx - 0.45, hy + 0.16, fz + 1.55); }
  else { controls.target.set(hx, 0.7, hz); camera.position.set(hx - 1.0, 1.05, hz + 3.0); }
  controls.update();
}
let last = performance.now();
function step(dt) {
  if (playing) { t += dt; if (t > (clip.frames - 1) / fps) t = 0; time.value = t * fps / (clip.frames - 1); }
  // the expression follows the buttons with a critically damped spring (smooth changes, mixes on the way)
  for (const k of FACES) { const w = 9, a = w * w * ((k === target ? 1 : 0) - ew[k]) - 2 * w * ev[k]; ev[k] += a * dt; ew[k] += ev[k] * dt; }
  fig.frame(clip, t * fps);
  const st = life.at(t); st.e = { ...ew };
  face.apply(st, rest, disp);
  face.onto(fig.positions, rest, disp, fig.skinner.matrix(fig.pose, HI));
  pos.set(fig.positions); geo.attributes.position.needsUpdate = true; geo.computeVertexNormals();
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
