// The viewer: Тим moving by Kimodo's motions through the engine (engine/src as it is; its file reading pointed at
// this folder's data/), with the live face (face.mjs, life.mjs), lit as a puppet on a small set: a warm key with soft
// shadows, a cool rim, physical materials for resin skin, sculpted hair, glass eyes, knitting and felt (the knit's
// stripes and ribs and the hair's strands are drawn in the shader from the paint coordinates, as in the renders).
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
  const u = new URL(url), m = u.pathname.match(/\/data\/(bodies|topology)\/tim8\.(json|bin)$/);
  const r = await fetch(m ? new URL(`${m[1]}/tim8.${m[2]}`, DATA) : u);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.arrayBuffer();
};
const shots = new URLSearchParams(location.search).has('shots');
if (shots) document.body.classList.add('shots');
const E = await createEngine({ root: ENGINE, read });
// the engine's dual-quaternion skinning here (its default, centres of rotation, takes long to prepare 50 000
// vertices in a browser); the films use the default
const spec = resolve({ format: 'engine/character', version: 1, id: 'tim8', label: { ru: 'Тим' }, body: 'tim8',
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
  const lg = g.createLinearGradient(0, 0, 0, 640); lg.addColorStop(0, '#171b24'); lg.addColorStop(0.75, '#1e2430'); lg.addColorStop(1, '#262224');
  g.fillStyle = lg; g.fillRect(0, 0, 1024, 640);
  const rg = g.createRadialGradient(330, 200, 10, 330, 200, 520); rg.addColorStop(0, 'rgba(216,154,96,0.5)'); rg.addColorStop(0.5, 'rgba(216,154,96,0.14)'); rg.addColorStop(1, 'rgba(216,154,96,0)');
  g.fillStyle = rg; g.fillRect(0, 0, 1024, 640);
  let s = 8; const R = () => (s = (s * 16807) % 2147483647) / 2147483647;
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
controls.target.set(0, 0.62, 0); controls.enableDamping = true; controls.minDistance = 0.4; controls.maxDistance = 6; controls.update();

const key = new THREE.DirectionalLight('#ffe2c2', 3.2); key.position.set(-1.6, 2.2, 1.6); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); key.shadow.camera.left = -1; key.shadow.camera.right = 1; key.shadow.camera.top = 1.6;
key.shadow.camera.bottom = -0.4; key.shadow.camera.near = 0.5; key.shadow.camera.far = 6; key.shadow.radius = 5; key.shadow.bias = -0.0004;
key.shadow.normalBias = 0.01;
const rim = new THREE.DirectionalLight('#a8c4ff', 2.0); rim.position.set(1.4, 1.4, -1.6);
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
const knit = (base, stripe, rib) => sculpted(P({ color: base, roughness: 0.9, sheen: 0.7, sheenRoughness: 0.5, sheenColor: '#ffffff' }), {
  height: `0.0016 * abs(sin(vTuv.x / ${rib} * 3.14159)) + 0.0007 * abs(fract(vTuv.y / ${rib * 0.45} + abs(fract(vTuv.x / ${rib}) - 0.5) * 1.2) - 0.5)`,
  colour: stripe ? `if (vPat.y > 0.0 && fract(vPat.y / ${2 * 0.09 * 0.342}) < 0.5) diffuseColor.rgb = vec3(${new THREE.Color(stripe).toArray().join(',')});
                    diffuseColor.rgb *= 0.72 + 0.28 * abs(sin(vTuv.x / ${rib} * 3.14159));` : `diffuseColor.rgb *= 0.75 + 0.25 * abs(sin(vTuv.x / ${rib} * 3.14159));` });
const MATS = {
  skin: P({ map: tex('face.png'), roughness: 0.48, clearcoat: 0.15, clearcoatRoughness: 0.4, sheen: 0.25, sheenColor: '#ff9a80', vertexColors: true }),
  hair: sculpted(P({ color: '#6a3e24', roughness: 0.5, clearcoat: 0.3, clearcoatRoughness: 0.35 }),
    { height: '0.0004 * sin(vTuv.x * 28.27)' }),
  eye: P({ map: tex('iris.png'), roughness: 0.25, clearcoat: 1.0, clearcoatRoughness: 0.02 }),
  sweater: knit('#2c4a72', '#f0e6d2', 0.013), cuff: knit('#24406a', null, 0.005), sock: knit('#e8e0d0', null, 0.006),
  shorts: P({ color: '#6a5a3a', roughness: 1.0, sheen: 0.9, sheenRoughness: 0.6, sheenColor: '#b0a080' }),
  shoe: P({ color: '#c83a2a', roughness: 0.38, clearcoat: 0.35 }), sole: P({ color: '#efe6d6', roughness: 0.7 }),
  lip: P({ color: '#c8706a', roughness: 0.35, clearcoat: 0.2 }), mouth: P({ color: '#3a1418', roughness: 0.6 }),
  teeth: P({ color: '#f1e8dc', roughness: 0.3, clearcoat: 0.3 }), brow: P({ color: '#5a3018', roughness: 0.6 }),
  lash: P({ color: '#2a1810', roughness: 0.5 }),
};
const matList = Object.values(MATS), matIndex = Object.fromEntries(Object.keys(MATS).map((k, i) => [k, i]));

const geo = new THREE.BufferGeometry();
const pos = new Float32Array(N * 3); pos.set(rest);
geo.setAttribute('position', new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage));
geo.setAttribute('uv', new THREE.BufferAttribute(look.arrays.uv, 2));
geo.setAttribute('pat', new THREE.BufferAttribute(look.arrays.pat, 3));
const col = new Float32Array(N * 3), tintC = new THREE.Color('#f2b8a6');
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
const SHOW = ['idle', 'walk', 'wave', 'jump', 'sit', 'bow', 'dance', 'run', 'sneak', 'stomp'];
for (const id of SHOW) { const m = index.motions.find(x => x.id === id); if (!m) continue;
  const o = document.createElement('option'); o.value = id; o.textContent = m.label.ru; sel.appendChild(o); }
const RU = { calm: 'спокоен', dream: 'мечтает', joy: 'радость', surprise: 'удивление', sad: 'грусть', anger: 'злость', grin: 'ухмылка' };
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
await choose('idle');

const follow = new THREE.Vector3();
function placeCamera() {
  const hx = fig.pose ? fig.pose.P[HIPS * 3] : 0, hz = fig.pose ? fig.pose.P[HIPS * 3 + 2] : 0;
  const hy = fig.pose ? fig.pose.P[HI * 3 + 1] : 0.85;
  if (near) { controls.target.set(hx, hy + 0.13, hz); camera.position.set(hx - 0.25, hy + 0.2, hz + 0.95); }
  else { controls.target.set(hx, 0.62, hz); camera.position.set(hx - 0.9, 0.95, hz + 2.6); }
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
