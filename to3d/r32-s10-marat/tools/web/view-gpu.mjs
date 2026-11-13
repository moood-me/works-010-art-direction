// The viewer: Марат moving by Kimodo's motions through the engine (engine/src, as it is: only its file
// reading is pointed at this folder's body pack), with the live face (face.mjs, life.mjs), drawn as clear line:
// flat colour, and one even dark line where a form stands in front of another or one piece meets another.
// The line is found on the screen from each pixel's piece and depth (as the С10 drawing's own renderer does),
// so it is even in width; Freestyle in the renders works on the mesh's edges instead (see notes.md).
// This is the page's fast variant (fast.html; view.html and view.mjs beside it are the page as it was): the face
// (face-gpu.mjs) and the skinning (engine-gpu/src/gpuskin.js) are worked out in the vertex shader of both looks; the
// processor works out the joints, the floor from a probe of the skin, and the face's numbers.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Face, EXPRESSIONS, PARAMS, mix } from './face-gpu.mjs';
import { lifeTrack, headFacing } from './life.mjs';
import { GpuSkin } from '../../../../engine-gpu/src/gpuskin.js';

const ENGINE = new URL('../../../../engine/', import.meta.url);
const DATA = new URL('data/', import.meta.url);
const ID = 'marat', RU_NAME = 'Марат';
const { createEngine } = await import(new URL('src/engine.js', ENGINE).href);
const { resolve } = await import(new URL('src/character.js', ENGINE).href);
const { qRot } = await import(new URL('src/math.js', ENGINE).href);
const { newSample } = await import(new URL('src/motion.js', ENGINE).href);

const read = async url => {
  const u = new URL(url), m = u.pathname.match(new RegExp(`/data/(bodies|topology)/${ID}\\.(json|bin)$`));
  const r = await fetch(m ? new URL(`${m[1]}/${ID}.${m[2]}`, DATA) : u);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.arrayBuffer();
};
const E = await createEngine({ root: ENGINE, read });
// 'dqs': the engine's dual-quaternion skinning — its default ('cor') needs ~15 s to prepare this many vertices
const spec = resolve({ format: 'engine/character', version: 1, id: ID, label: { ru: RU_NAME },
  body: ID, skinning: { method: 'dqs', clavicleShare: 0, seam: null } });
const fig = await E.figure(spec, { position: [0, 0, 0], heading: 0 });
const body = fig.body, N = body.N, J = body.skeleton.J;
const gs = new GpuSkin(THREE, fig.skinner);
const faceData = await (await fetch(new URL('face.json', DATA))).json();
const look = await (await fetch(new URL('look.json', DATA))).json();
const face = new Face(body, faceData);
const HI = body.skeleton.index.Head, HIPS = body.skeleton.index.Hips;

// ------------------------------------------------------------------ three.js
const stage = document.getElementById('stage');
THREE.ColorManagement.enabled = false;          // the drawing's colours as they are: flat, no light, no conversion
const renderer = new THREE.WebGLRenderer({ antialias: false });
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
renderer.setPixelRatio(Math.min(2, devicePixelRatio));
stage.appendChild(renderer.domElement);
document.getElementById('msg').remove();
const PAPER = new THREE.Color(look.panel), FLOORC = new THREE.Color(look.panel).lerp(new THREE.Color('#7a6a58'), 0.25), INK = new THREE.Color('#1b1714');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(22, 1, 0.1, 100);
camera.position.set(-2.6, 1.6, 6.2);       // a big man: a little farther off
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.05, 0); controls.enableDamping = true; controls.update();

const geo = face.attributes(THREE, gs.attributes(new THREE.BufferGeometry()));      // the rest; each vertex's joints and weights, and its piece of the face
const col = new Float32Array(N * 3), ids = new Float32Array(N);
const pal = look.palette.map(c => new THREE.Color(c));
for (let i = 0; i < N; i++) {
  const c = pal[look.colour[i]]; col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
  ids[i] = look.line[i] ? look.id[i] : 0;           // 0: ink marks, they make no line of their own
}
geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
geo.setAttribute('pid', new THREE.BufferAttribute(ids, 1));
geo.setIndex(new THREE.BufferAttribute(body.triangles, 1));
geo.computeBoundingSphere();

// two looks of the same mesh: its flat colour, and its piece and depth (for the line)
const flatMat = new THREE.ShaderMaterial({ vertexColors: true, side: THREE.DoubleSide,
  vertexShader: `varying vec3 vC; void main(){ vC = color; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `varying vec3 vC; void main(){ gl_FragColor = vec4(vC, 1.0); }` });
const idMat = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
  vertexShader: `attribute float pid; varying float vI; varying float vD;
    void main(){ vI = pid; vec4 mv = modelViewMatrix * vec4(position, 1.0); vD = -mv.z; gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `varying float vI; varying float vD; void main(){ gl_FragColor = vec4(vI, vD, 0.0, 1.0); }` });
// the same two looks for the skin: the face laid on the rest, then skinned, in the shader
const flatSkin = new THREE.ShaderMaterial({ uniforms: { ...gs.uniforms, ...face.uniforms }, vertexColors: true, side: THREE.DoubleSide,
  vertexShader: `${gs.glsl}${face.glsl}
    varying vec3 vC; void main(){ vec3 P, N; skinVertex(faceAt(position), normal, P, N); vC = color; gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0); }`,
  fragmentShader: flatMat.fragmentShader });
const idSkin = new THREE.ShaderMaterial({ uniforms: { ...gs.uniforms, ...face.uniforms }, side: THREE.DoubleSide,
  vertexShader: `${gs.glsl}${face.glsl}
    attribute float pid; varying float vI; varying float vD;
    void main(){ vec3 P, N; skinVertex(faceAt(position), normal, P, N); vI = pid; vec4 mv = viewMatrix * vec4(P, 1.0); vD = -mv.z; gl_Position = projectionMatrix * mv; }`,
  fragmentShader: idMat.fragmentShader });
const mesh = new THREE.Mesh(geo, flatSkin);
mesh.frustumCulled = false;
scene.add(mesh);
// the floor: a large flat disc, its far edge makes the floor line of the drawing's panels
const floorGeo = new THREE.CircleGeometry(30, 96); floorGeo.rotateX(-Math.PI / 2);
floorGeo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(floorGeo.attributes.position.count * 3).map((_, i) => [FLOORC.r, FLOORC.g, FLOORC.b][i % 3]), 3));
floorGeo.setAttribute('pid', new THREE.BufferAttribute(new Float32Array(floorGeo.attributes.position.count).fill(9000), 1));
const floor = new THREE.Mesh(floorGeo, flatMat); scene.add(floor);

const opts = { type: THREE.FloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter };
let rtC = new THREE.WebGLRenderTarget(1, 1, opts), rtI = new THREE.WebGLRenderTarget(1, 1, opts);
const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
  uniforms: { tC: { value: null }, tI: { value: null }, px: { value: new THREE.Vector2() }, r: { value: 1.2 },
    ink: { value: INK }, bg: { value: PAPER } },
  vertexShader: `varying vec2 vU; void main(){ vU = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
  fragmentShader: `
    uniform sampler2D tC, tI; uniform vec2 px; uniform float r; uniform vec3 ink, bg; varying vec2 vU;
    vec2 at(vec2 u){ vec4 s = texture2D(tI, u); return s.a < 0.5 ? vec2(-1.0, 1e4) : s.rg; }
    vec3 shade(vec2 u){
      vec4 c = texture2D(tC, u);
      vec3 base = c.a < 0.5 ? bg : c.rgb;
      vec2 m = at(u);
      float edge = 0.0;
      // a line where the piece changes, or where the depth jumps (a form in front of another, also of its own)
      for (int k = 0; k < 8; k++) {
        float a = float(k) * 0.785398;
        vec2 o = vec2(cos(a), sin(a)) * r * px;
        vec2 p = at(u + o), q = at(u - o);
        if (p.x != 0.0 && m.x != 0.0 && abs(p.x - m.x) > 0.5) edge = 1.0;
        float d2 = p.y + q.y - 2.0 * m.y;
        if (m.x != 0.0 && abs(d2) > 0.012 * m.y + 0.004 && max(p.y, q.y) < 1e3) edge = 1.0;
        if (m.x != 0.0 && (p.y > 1e3 || q.y > 1e3) && m.y < 1e3) edge = 1.0;
      }
      return mix(base, ink, edge);
    }
    void main(){
      // the targets are twice the screen: four samples per pixel, averaged (a smooth line)
      vec2 h = px * 0.5;
      gl_FragColor = vec4(0.25 * (shade(vU + vec2(-h.x, -h.y)) + shade(vU + vec2(h.x, -h.y)) + shade(vU + vec2(-h.x, h.y)) + shade(vU + vec2(h.x, h.y))), 1.0);
    }` }));
const post = new THREE.Scene(); post.add(quad);
const postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

function resize() {
  const w = stage.clientWidth, h = stage.clientHeight, pr = renderer.getPixelRatio();
  renderer.setSize(w, h, false);
  camera.aspect = w / h; camera.updateProjectionMatrix();
  const ss = 2 * pr;                         // supersampled targets
  rtC.setSize(w * ss, h * ss); rtI.setSize(w * ss, h * ss);
  quad.material.uniforms.px.value.set(1 / (w * ss), 1 / (h * ss));
  quad.material.uniforms.r.value = 2.4 * pr;
}
addEventListener('resize', resize); resize();

// ------------------------------------------------------------------ motion, face, controls
const index = await E.motions();
const sel = document.getElementById('motion');
const SHOW = ['walk', 'wave', 'bow', 'idle', 'sit', 'stomp', 'sneak', 'run', 'dance', 'jump'];
for (const id of SHOW) { const m = index.motions.find(x => x.id === id); if (!m) continue;
  const o = document.createElement('option'); o.value = id; o.textContent = m.label.ru; sel.appendChild(o); }
const RU = { calm: 'как всегда', joy: 'радость', surprise: 'удивление', sad: 'грусть', anger: 'злость' };
const exprBox = document.getElementById('expr'), exprW = { calm: 1, joy: 0, surprise: 0, sad: 0, anger: 0 };
for (const k of Object.keys(EXPRESSIONS)) {
  const l = document.createElement('label'); l.innerHTML = `${RU[k]} <input type="range" min="0" max="1" step="0.05" value="${exprW[k]}">`;
  const inp = l.querySelector('input'); inp.oninput = () => { exprW[k] = +inp.value; };
  l.ondblclick = () => { for (const j of Object.keys(exprW)) exprW[j] = j === k ? 1 : 0; exprBox.querySelectorAll('input').forEach((x, i) => x.value = exprW[Object.keys(exprW)[i]]); };
  exprBox.appendChild(l);
}
const talk = document.getElementById('talk'), time = document.getElementById('time'), playB = document.getElementById('play');
let clip, life, t = 0, playing = true, fps = 30;
const smp = newSample(body.skeleton.J);

async function choose(id) {
  clip = await E.clip([id]); fps = clip.fps ?? 30; t = 0;
  makeLife();
}
function makeLife() {
  const head = s => headFacing(fig.retarget.pose(clip.sample(Math.min(clip.frames - 1, s * fps), smp)), HI, qRot);
  life = lifeTrack(head, { seconds: clip.frames / fps, seed: 7, talk: talk.checked, expr: { calm: 1 } });
}
sel.onchange = () => choose(sel.value);
talk.onchange = () => makeLife();
playB.onclick = () => { playing = !playing; playB.textContent = playing ? '❚❚' : '▶'; playB.classList.toggle('on', playing); };
time.oninput = () => { t = +time.value * (clip.frames - 1) / fps; };
await choose('walk');

// the expression follows the sliders with a critically damped spring (smooth changes, any mix)
const ex = mix({ calm: 1 }), exv = {}; for (const k of PARAMS) exv[k] = 0;
let last = performance.now();
const follow = new THREE.Vector3();
function frame(now) {
  const dt = Math.min(0.05, (now - last) / 1000); last = now;
  if (playing) { t += dt; if (t > (clip.frames - 1) / fps) { t = 0; } time.value = t * fps / (clip.frames - 1); }
  const target = mix(exprW), w = 9;
  for (const k of PARAMS) { const a = w * w * (target[k] - ex[k]) - 2 * w * exv[k]; exv[k] += a * dt; ex[k] += exv[k] * dt; }
  const pose = fig.retarget.placed(fig.retarget.pose(clip.sample(t * fps, fig.sample)));
  const shift = pose.floor - gs.lowest(pose);                // on the floor, as motion.floor 'lowest'
  for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
  gs.setPose(pose); fig.pose = pose;
  const q = life.at(t), p = {};
  for (const k of PARAMS) p[k] = k === 'iris' ? q.iris * ex.iris : q[k] + ex[k];
  p.up = Math.min(42, p.up);
  face.set(p);
  // the camera's target goes with him
  follow.set(fig.pose.P[HIPS * 3], controls.target.y, fig.pose.P[HIPS * 3 + 2]);
  const d = follow.clone().sub(controls.target); controls.target.add(d); camera.position.add(d);
  controls.update();
  mesh.material = flatSkin; floor.material = flatMat;
  renderer.setRenderTarget(rtC); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera);
  mesh.material = idSkin; floor.material = idMat;
  renderer.setRenderTarget(rtI); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera);
  renderer.setRenderTarget(null);
  quad.material.uniforms.tC.value = rtC.texture; quad.material.uniforms.tI.value = rtI.texture;
  renderer.render(post, postCam);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
