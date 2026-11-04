// Tim's model drawn through the engine: the pack (tools/model.py) becomes an engine body (makeBody), a Figure moves it
// by a Kimodo motion (retargeting, skinning by centres of rotation), and a gouache shader paints it: flat paints, a
// second tone of the same paint where the form turns from the light, the shirt's stripes, the face picture.
// Then (optionally) it is laid onto the drawing's backdrop and passed through the drawing's own SVG gouache filter.
// window.A.set({...}) / A.render() — driven by shots.mjs.
import * as THREE from 'three';
import { loadSkeleton } from '/works-010-art-direction/engine/src/skeleton.js';
import { makeBody } from '/works-010-art-direction/engine/src/body.js';
import { Figure } from '/works-010-art-direction/engine/src/figure.js';
import { loadMotion, clipOf } from '/works-010-art-direction/engine/src/motion.js';
import { resolve } from '/works-010-art-direction/engine/src/character.js';
import { loadPack } from '/works-010-art-direction/engine/src/pack.js';

const ENG = '/works-010-art-direction/engine/';
const q = new URLSearchParams(location.search);
const canvas = document.getElementById('c'), svg = document.getElementById('out');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setClearColor(0x000000, 0);
const scene = new THREE.Scene();
const persp = new THREE.PerspectiveCamera(22, 1, 0.05, 100), ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.05, 100);
let camera = persp;

// the paints (figure-tim's colours, styles/s9-midcentury/tools/tim.py): [paint, its second tone]
const PAINT = {
  skin: ['#f7d6bb', '#ecbea2'], skin_d: ['#e8b096', '#dba086'], hair: ['#d0642c', '#b65222'], shirt: ['#c8402f', '#b03526'],
  shorts: ['#2c4a6e', '#233d5c'], sock: ['#f6eedd', '#e3d8c2'], shoe: ['#b8352b', '#9c2b23'], sole: ['#f6eedd', '#e3d8c2'],
  ear: ['#f7d6bb', '#ecbea2'], collar: ['#f6eedd', '#e3d8c2'], clay: ['#d9d3c8', '#a9a196'], ink: ['#2a201c', '#2a201c'], hair_d: ['#a8481c', '#963e17'],
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
uniform float stripe0, stripeP, stripeW, stripeTop; uniform vec3 cream, creamS, sockBand; uniform vec2 sockY;
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
  if (m == 3 && vPat.y < stripeTop) { float k = fract((vPat.y - stripe0) / stripeP); if (k < stripeW) { b = cream; s = creamS; } }
  if (m == 5) { if (vPat.y > sockY.x && vPat.y < sockY.y) { b = sockBand; s = sockBand * 0.88; } }
  if (hasFace > 0.5 && vFuv.z > 0.01) { vec4 f = texture2D(face, vFuv.xy); float a = f.a * smoothstep(0.05, 0.4, vFuv.z);
    b = mix(b, f.rgb, a); s = mix(s, f.rgb * 0.97, a); }
  float th = (m == 0 || m == 8) ? -0.12 : 0.04;
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
  stripe0: { value: 0 }, stripeTop: { value: 9 }, stripeP: { value: 0.03 }, stripeW: { value: 0.42 }, cream: { value: hex('#f6eedd') }, creamS: { value: hex('#e3d8c2') },
  sockBand: { value: hex('#c8402f') }, sockY: { value: new THREE.Vector2(-1, -1) },
};
const material = new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, uniforms, side: THREE.DoubleSide });

let sk, figure, mesh, geom, model, clips = {}, faces = {};
const state = { pose: 'rest', t: 0, motion: null };

async function loadModel(url) {
  const { header: h, arrays: a } = await loadPack(new URL(url, location.href).href);
  h.mats.forEach((m, i) => { const p = PAINT[m]; uniforms.base.value[i] = hex(p[0]); uniforms.shade.value[i] = hex(p[1]); });
  if (h.stripes) { uniforms.stripe0.value = h.stripes.y0; uniforms.stripeP.value = h.stripes.period; uniforms.stripeW.value = h.stripes.width; uniforms.stripeTop.value = h.stripes.top ?? 9; }
  if (h.sockBand) uniforms.sockY.value.set(...h.sockBand);
  const body = makeBody({ id: h.id, skeleton: sk, positions: a.positions, triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
    parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames) });
  const spec = resolve({ format: 'engine/character', version: 1, id: 'tim', body: h.id, skinning: { method: q.get('skin') || 'cor' } });
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
    geom.attributes.position.needsUpdate = true; geom.attributes.normal.needsUpdate = true;
    if (o.w) { renderer.setSize(o.w, o.h, false); canvas.style.width = o.w + 'px'; canvas.style.height = o.h + 'px'; }
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
};

sk = await loadSkeleton(new URL(`${ENG}data/skeleton.json`, location.href));
if (q.get('model')) await A.set({ model: q.get('model') });
window.__ready = true;
