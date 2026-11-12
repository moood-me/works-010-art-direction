// Аня's model drawn through the engine: the pack (tools/model.py) becomes an engine body (makeBody), a Figure moves it
// by a Kimodo motion (retargeting, skinning by centres of rotation), and a gouache shader paints it: flat paints, a
// second tone of the same paint where the form turns from the light, the dress's printed dots, the face picture.
// Then (optionally) it is laid onto the drawing's backdrop and passed through the drawing's own SVG gouache filter.
// window.A.set({...}) / A.render() — driven by shots.mjs.
import * as THREE from 'three';
import { loadSkeleton } from '../../../../engine/src/skeleton.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadMotion, clipOf } from '../../../../engine/src/motion.js';
import { resolve } from '../../../../engine/src/character.js';
import { loadPack } from '../../../../engine/src/pack.js';

const ENG = new URL('../../../../engine/', import.meta.url).href;
import { LiveFace } from './face.js';
import { qMul, qConj, qRot } from '../../../../engine/src/math.js';
const q = new URLSearchParams(location.search);
const canvas = document.getElementById('c'), svg = document.getElementById('out');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setClearColor(0x000000, 0);
const scene = new THREE.Scene();
const persp = new THREE.PerspectiveCamera(22, 1, 0.05, 100), ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.05, 100);
let camera = persp;

// the paints (figure-anya's colours, styles/s9-midcentury/tools/anya.py): [paint, its second tone]
const PAINT = {
  skin: ['#f6d7bf', '#ecc3a8'], skin_d: ['#e9b89c', '#dca88c'], hair: ['#3a231f', '#2c1a17'], hair_l: ['#6a4034', '#553228'], band: ['#2f8f8a', '#26756f'],
  dress: ['#e8b33a', '#d39c28'], belt: ['#c98f22', '#b47d1b'], cardi: ['#2f8f8a', '#226e6a'], collar: ['#fbf6ea', '#e9e0cc'], shoe: ['#b8352b', '#9c2b23'],
  clay: ['#d9d3c8', '#a9a196'], ink: ['#2a201c', '#2a201c'], white: ['#fbf6ea', '#e9e0cc'], nose: ['#f6d7bf', '#f6d7bf'], nose_d: ['#c98f78', '#c98f78'],
};
const hex = c => new THREE.Color().setRGB(...[1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16) / 255));

const VS = `
attribute float mat; attribute vec3 pat; attribute vec3 fuv;
varying float vMat; varying vec3 vPat; varying vec3 vFuv; varying vec3 vN; varying vec3 vVN;
void main(){ vMat = mat; vPat = pat; vFuv = fuv; vN = normalize(normal); vVN = normalize(normalMatrix * normal);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
const FS = `
precision highp float;
uniform vec3 base[16]; uniform vec3 shade[16]; uniform sampler2D face; uniform float hasFace; uniform vec3 L; uniform float clay;
uniform float dotMat, dotStep, dotR; uniform vec3 dotCol;
varying float vMat; varying vec3 vPat; varying vec3 vFuv; varying vec3 vN; varying vec3 vVN;
float h(vec3 p){ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float noise(vec3 p){ vec3 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
  return mix(mix(mix(h(i), h(i+vec3(1,0,0)), f.x), mix(h(i+vec3(0,1,0)), h(i+vec3(1,1,0)), f.x), f.y),
             mix(mix(h(i+vec3(0,0,1)), h(i+vec3(1,0,1)), f.x), mix(h(i+vec3(0,1,1)), h(i+vec3(1,1,1)), f.x), f.y), f.z); }
void main(){
  int m = int(vMat + 0.5);
  vec3 b = base[0], s = shade[0];
  for (int i = 0; i < 16; i++) if (i == m) { b = base[i]; s = shade[i]; }
  vec3 n = normalize(vVN); float inside = gl_FrontFacing ? 0.0 : 1.0; if (!gl_FrontFacing) n = -n;
  float d = dot(n, normalize(L));
  if (clay > 0.5) { float k = 0.35 + 0.65 * max(d, 0.0); gl_FragColor = vec4(vec3(0.85, 0.82, 0.77) * k + 0.08, 1.0); return; }
  if (m == int(dotMat + 0.5)) {   // printed dots on a staggered grid (kit.py pattern_dots), in the cloth's own flat coordinates
    float row = floor(vPat.y / (dotStep * 0.87) + 0.5); vec2 g = vec2(vPat.x - mod(row, 2.0) * dotStep * 0.5, vPat.y);
    vec2 c = vec2((floor(g.x / dotStep + 0.5)) * dotStep, row * dotStep * 0.87);
    float k = 1.0 - smoothstep(dotR * 0.85, dotR * 1.15, length(g - c)); b = mix(b, dotCol, k); s = mix(s, dotCol * 0.93, k); }
  if (hasFace > 0.5 && vFuv.z > 0.01) { vec4 f = texture2D(face, vFuv.xy); float a = f.a * smoothstep(0.05, 0.4, vFuv.z);
    b = mix(b, f.rgb, a); s = mix(s, f.rgb * 0.97, a); }
  float th = (m == 0 || m == 1) ? -0.42 : 0.04;      // the skin stays one paint until it turns well away from the light
  float t = smoothstep(th - 0.04, th + 0.04, d);
  vec3 col = mix(s, b, t * (1.0 - inside));
  // gouache: uneven density of the paint over the form
  float nn = noise(vPat * 38.0) * 0.6 + noise(vPat * 110.0) * 0.4;
  col *= 0.965 + 0.07 * nn;
  gl_FragColor = vec4(col, 1.0);
}`;

const uniforms = {
  base: { value: Array.from({ length: 16 }, () => new THREE.Color()) }, shade: { value: Array.from({ length: 16 }, () => new THREE.Color()) },
  face: { value: null }, hasFace: { value: 0 }, L: { value: new THREE.Vector3(-0.45, 0.55, 0.75) }, clay: { value: 0 },
  dotMat: { value: -1 }, dotStep: { value: 0.045 }, dotR: { value: 0.0055 }, dotCol: { value: hex('#fbf0d4') },
};
const material = new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, uniforms, side: THREE.DoubleSide });

let sk, figure, mesh, geom, model, clips = {}, faces = {};
// the ground he walks on, painted like the drawing's ground band: one flat paint with blotches of a darker and a
// lighter one fixed to the ground (so it slides under him as he goes), and a soft shadow-spot under his feet
const ground = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.ShaderMaterial({
  uniforms: { spot: { value: new THREE.Vector3(0, 0, 0.3) } },
  vertexShader: `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
  fragmentShader: `precision highp float; varying vec3 vW; uniform vec3 spot;
    float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    float n(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f); return mix(mix(h(i), h(i+vec2(1,0)), f.x), mix(h(i+vec2(0,1)), h(i+vec2(1,1)), f.x), f.y); }
    void main(){ vec2 p = vW.xz; vec3 c = vec3(0.851, 0.475, 0.435);
      float m = n(p * 0.9) * 0.6 + n(p * 2.6) * 0.4; c *= 0.95 + 0.07 * m;
      float d = smoothstep(0.78, 0.82, n(p * 3.0 + 7.0)); c = mix(c, c * 0.9, d * 0.7);
      float r = length((p - spot.xy) / vec2(1.0, 0.8)) / spot.z; c *= 1.0 - 0.18 * (1.0 - smoothstep(0.35, 1.0, r));
      gl_FragColor = vec4(c, 1.0); }`,
}));
ground.rotation.x = -Math.PI / 2; ground.position.y = -0.001; ground.visible = false; scene.add(ground);
// the live face: drawn every frame into a canvas the head takes (face.js)
const faceCanvas = document.createElement('canvas'); faceCanvas.width = faceCanvas.height = 1024;
const faceCtx = faceCanvas.getContext('2d');
const faceTexture = new THREE.CanvasTexture(faceCanvas); faceTexture.flipY = false; faceTexture.anisotropy = 4;
const live = new LiveFace({ seed: +(q.get('seed') || 7), length: 600 });
// where the head turns: its yaw in the world each frame of a clip; the eyes lead it, fast turns call a blink
const turns = new Map();
function headTurns(c) {
  const key = c.motions.join('+');
  if (turns.has(key)) return turns.get(key);
  const H = sk.index.Head, fr = [figure.body.frames[H * 4], figure.body.frames[H * 4 + 1], figure.body.frames[H * 4 + 2], figure.body.frames[H * 4 + 3]];
  const s = { q: new Float64Array(sk.J * 4), p: new Float64Array(sk.J * 3), lowest: 0 }, yaw = [];
  for (let f = 0; f < c.frames; f++) {
    c.sample(f, s);
    const qh = [s.q[H * 4], s.q[H * 4 + 1], s.q[H * 4 + 2], s.q[H * 4 + 3]], Q = qMul(qh, qConj(fr)), d = qRot(Q, [0, 0, 1]);
    let a = Math.atan2(d[0], d[2]); if (yaw.length) { while (a - yaw[yaw.length - 1] > Math.PI) a -= 2 * Math.PI; while (a - yaw[yaw.length - 1] < -Math.PI) a += 2 * Math.PI; }
    yaw.push(a);
  }
  const at = f => { f = Math.max(0, Math.min(c.frames - 1, f)); const i = Math.floor(f), u = f - i; return yaw[i] * (1 - u) + yaw[Math.min(i + 1, c.frames - 1)] * u; };
  const fps = c.fps, blinks = []; let last = -9;
  for (let f = 1; f < c.frames; f++) { const v = (yaw[f] - yaw[f - 1]) * fps; if (Math.abs(v) > 1.6 && f / fps - last > 0.9) { blinks.push(f / fps); last = f / fps; } }
  const r = { lead: tsec => at(tsec * fps + 0.28 * fps) - at(tsec * fps), blinks };
  turns.set(key, r); return r;
}
const state = { pose: 'rest', t: 0, motion: null };

async function loadModel(url) {
  const { header: h, arrays: a } = await loadPack(new URL(url, location.href).href);
  h.mats.forEach((m, i) => { const p = PAINT[m]; uniforms.base.value[i] = hex(p[0]); uniforms.shade.value[i] = hex(p[1]); });
  if (h.dots) { uniforms.dotMat.value = h.mats.indexOf(h.dots.mat); uniforms.dotStep.value = h.dots.step; uniforms.dotR.value = h.dots.r; }
  const body = makeBody({ id: h.id, skeleton: sk, positions: a.positions, triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
    parts: { names: h.parts || [], weights: a.parts || new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames) });
  // a hand or an elbow that would go into the head or the bob is swung out (the engine's correction)
  const spec = resolve({ format: 'engine/character', version: 1, id: 'anya', body: h.id, skinning: { method: q.get('skin') || 'cor' }, motion: { corrections: { armsOutOfHead: { margin: 0.03 } } } });
  figure = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
  figure.frame(null, 0);
  if (mesh) { scene.remove(mesh); geom.dispose(); }
  geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.BufferAttribute(figure.positions, 3));
  geom.setAttribute('normal', new THREE.BufferAttribute(figure.normals, 3));
  geom.setAttribute('mat', new THREE.BufferAttribute(Float32Array.from(a.mat), 1));
  geom.setAttribute('pat', new THREE.BufferAttribute(a.pat, 3));
  geom.setAttribute('fuv', new THREE.BufferAttribute(a.fuv, 3));
  geom.setIndex(new THREE.BufferAttribute(a.triangles, 1));
  mesh = new THREE.Mesh(geom, material); mesh.frustumCulled = false; scene.add(mesh);
  model = { h, body };
}

async function clip(ids) {
  const key = ids.join('+');
  if (!clips[key]) clips[key] = clipOf(await Promise.all(ids.map(id => loadMotion(new URL(id.startsWith('/') ? id : `${ENG}motions/${id}.json`, location.href), sk))));
  return clips[key];
}
async function faceTex(url) {
  if (!faces[url]) faces[url] = await new THREE.TextureLoader().loadAsync(url);
  const t = faces[url]; t.flipY = false; t.anisotropy = 4; t.needsUpdate = true; return t;
}

const A = window.A = {
  async set(o) {
    if (o.model && o.model !== state.model) { await loadModel(o.model); state.model = o.model; }
    if ('face' in o) { if (o.face) { uniforms.face.value = await faceTex(o.face); uniforms.hasFace.value = 1; } else uniforms.hasFace.value = 0; }
    if ('clay' in o) uniforms.clay.value = o.clay ? 1 : 0;
    if (o.motion !== undefined) state.motion = o.motion;
    if (o.t !== undefined) state.t = o.t;
    if (o.heading !== undefined) figure.place = { heading: o.heading };
    if (o.light) uniforms.L.value.set(...o.light);
    const c = state.motion ? await clip(state.motion) : null;
    figure.frame(c, state.t);
    if ('expr' in o) live.setExpressions(typeof o.expr === 'string' ? [{ t: 0, name: o.expr }] : o.expr);
    if ('talk' in o) live.talking = !!o.talk;
    if ('ground' in o) ground.visible = !!o.ground;
    if (ground.visible) { const P = figure.pose.P, H = sk.index.Hips; ground.material.uniforms.spot.value.set(P[H * 3], P[H * 3 + 2], 0.3); ground.position.y = figure.pose.floor ?? 0; }
    if (o.live !== false && !o.face) {
      const tr = c ? headTurns(c) : null;
      live.lead = tr ? tr.lead : null; live.setHeadTurns(tr ? tr.blinks : []);
      const ts = o.faceTime ?? (c ? state.t / c.fps : (state.clock || 0));
      live.draw(faceCtx, ts); faceTexture.needsUpdate = true;
      uniforms.face.value = faceTexture; uniforms.hasFace.value = 1;
    }
    geom.attributes.position.needsUpdate = true; geom.attributes.normal.needsUpdate = true;
    if (o.w && (o.w !== canvas.width || o.h !== canvas.height)) { renderer.setSize(o.w, o.h, false); canvas.style.width = o.w + 'px'; canvas.style.height = o.h + 'px'; }
    if (o.cam) A.camera(o.cam);
    state.backdrop = o.backdrop ?? state.backdrop;
  },
  // cam: {yaw (0: from the front, −π/2: from his right), pitch, target [x,y,z] or 'hips'|'head', dist, height (ortho: metres seen top to bottom), fov}
  camera(c) {
    const w = canvas.width, h = canvas.height;
    let t = c.target || [0, 0.6, 0];
    if (c.joint) { const P = figure.pose.P, j = sk.index[c.joint], o = c.offset || [0, 0, 0]; t = [P[j * 3] + o[0], P[j * 3 + 1] + o[1], P[j * 3 + 2] + o[2]]; }
    if (c.follow) { const P = figure.pose.P, H = sk.index.Hips; t = [P[H * 3] + (c.follow[0] || 0), c.follow[1], P[H * 3 + 2] + (c.follow[2] || 0)]; }
    const yaw = c.yaw || 0, pitch = c.pitch || 0, dist = c.dist || 6;
    if (c.height) { camera = ortho; const hh = c.height / 2; Object.assign(ortho, { left: -hh * w / h, right: hh * w / h, top: hh, bottom: -hh }); }
    else { camera = persp; persp.fov = c.fov || 22; persp.aspect = w / h; }
    camera.position.set(t[0] + Math.sin(yaw) * Math.cos(pitch) * dist, t[1] + Math.sin(pitch) * dist, t[2] + Math.cos(yaw) * Math.cos(pitch) * dist);
    camera.lookAt(t[0], t[1], t[2]); camera.updateProjectionMatrix(); camera.updateMatrixWorld();
  },
  render() { renderer.render(scene, camera); },
  // the render laid on the drawing's backdrop (an SVG made by the drawing's own code), through its gouache filter
  async compose(backdropUrl, opts = {}) {
    const w = canvas.width, h = canvas.height;
    const bd = backdropUrl ? await (await fetch(backdropUrl)).text() : '';
    const inner = bd.replace(/^[\s\S]*?<svg[^>]*>/, '').replace(/<\/svg>\s*$/, '');
    const paper = inner.match(/<rect[^>]*filter="url\(#paper\)"[^>]*\/>$/);
    const body = paper ? inner.slice(0, inner.length - paper[0].length) : inner;
    const img = canvas.toDataURL('image/png');
    svg.setAttribute('width', w); svg.setAttribute('height', h); svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
    svg.innerHTML = body + `<image href="${img}" x="0" y="0" width="${w}" height="${h}" ${opts.gouache === false ? '' : 'filter="url(#gouache)"'}/>` + (paper ? paper[0] : '');
    canvas.style.visibility = 'hidden';
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  },
  uncompose() { svg.innerHTML = ''; canvas.style.visibility = 'visible'; },
  info() { return { joints: Array.from(figure.pose.P), N: model.body.N }; },
  clipInfo() { const c = state.motion ? clips[state.motion.join('+')] : null; return c ? { frames: c.frames, fps: c.fps } : null; },
};

sk = await loadSkeleton(new URL(`${ENG}data/skeleton.json`, location.href));
await A.set({ model: q.get('model') || new URL('../../model/anya.json', import.meta.url).href });
window.__ready = true;
