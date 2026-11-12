// Кира's model drawn through the engine: the pack (tools/model.py) becomes an engine body (makeBody), a Figure moves it
// by a Kimodo motion (the engine's retargeting and skinning), and a paper shader paints it the way С14 draws:
//   every part is a piece of paper of one colour — smooth card, or paper painted by brush before cutting (streaks
//   along the piece, fixed to it); the sheet's thickness shows as a light cut edge; pieces throw soft plum shadows on
//   what lies under them (a shadow map from the picture's top left, as the drawing's rule says); no outline, no gloss.
// The face's small pieces (eyes with lids, brows, cheeks, mouth) are drawn each frame by the drawing's own code
// (face.js) into a picture the head takes from the front.
// window.A.set({...}) / A.render() — driven by shots.mjs and ui.js.
import * as THREE from 'three';
import { loadSkeleton } from '../../../../engine/src/skeleton.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadMotion, clipOf } from '../../../../engine/src/motion.js';
import { resolve } from '../../../../engine/src/character.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { qMul, qConj, qRot } from '../../../../engine/src/math.js';
import { LiveFace } from './face.js';

const ENG = new URL('../../../../engine/', import.meta.url).href;
const q = new URLSearchParams(location.search);
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setClearColor(0x000000, 0);
const scene = new THREE.Scene();
const persp = new THREE.PerspectiveCamera(22, 1, 0.05, 100), ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.05, 100);
let camera = persp;

// the papers (styles/s14-paper/tools/kira.py): colour, and how strongly the brush streaks show (0: smooth card)
const mixc = (a, b, t) => '#' + [1, 3, 5].map(i => Math.round(parseInt(a.slice(i, i + 2), 16) * (1 - t) + parseInt(b.slice(i, i + 2), 16) * t).toString(16).padStart(2, '0')).join('');
const dark = (c, t = 0.2) => mixc(c, '#2b1b2c', t), lite = (c, t = 0.2) => mixc(c, '#fff6e6', t);
const HAIR = '#2b2330', SKIN = '#ecd3bf', HOOD = '#5b2f57', TROU = '#37343c', LIME = '#c9e32f';
const PAPER = {
  skin: [SKIN, 0], skin_d: [mixc(SKIN, '#c0705c', 0.30), 0], ear: [mixc(SKIN, '#d98a6c', 0.18), 0], nose: [mixc(SKIN, '#d98a6c', 0.32), 0],
  hair: [HAIR, 1], hair_d: [dark(HAIR, 0.15), 1], hood: [HOOD, 1], hood_d: [dark(HOOD, 0.2), 1], pocket: [dark(HOOD, 0.12), 1],
  band: [dark(HOOD, 0.18), 1], string: [lite(HOOD, 0.55), 0], trou: [TROU, 0.35], boot: ['#2d2a31', 0], sole: ['#1e1b20', 0],
  lime: [LIME, 0], lime_d: [dark(LIME, 0.25), 0], cup: ['#2a2428', 0], clay: ['#d9d3c8', 0], white: ['#fbf6ea', 0],
};
const hex = c => new THREE.Color().setRGB(...[1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16) / 255));

const SHADOW_GLSL = `
uniform sampler2D shadowMap; uniform mat4 shadowMatrix; uniform float shadowSoft; uniform vec3 L;
float unpackD(vec4 v){ return dot(v, vec4(1.0, 1.0/255.0, 1.0/65025.0, 1.0/16581375.0)); }
float h1(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
// how much of the light is cut off at a point of the world (0…1), softly: taps on a disc turned by a noise of the place
float shadowAt(vec3 w, vec3 n){
  vec4 sc = shadowMatrix * vec4(w + n * 0.004, 1.0); vec3 c = sc.xyz * 0.5 + 0.5;
  if (c.x < 0.0 || c.x > 1.0 || c.y < 0.0 || c.y > 1.0) return 0.0;
  float a0 = h1(floor(w.xy * 900.0) + w.z) * 6.2832, s = 0.0;
  for (int i = 0; i < 12; i++) { float fi = float(i); float r = sqrt((fi + 0.5) / 12.0) * shadowSoft; float a = a0 + fi * 2.39996;
    float d = unpackD(texture2D(shadowMap, c.xy + vec2(cos(a), sin(a)) * r)); s += (c.z - 0.0010 > d) ? 1.0 : 0.0; }
  return s / 12.0;
}`;
const VS = `
attribute float mat; attribute vec3 pat; attribute vec3 fuv; attribute float edge;
varying float vMat; varying vec3 vPat; varying vec3 vFuv; varying vec3 vN; varying vec3 vW; varying float vEdge;
void main(){ vMat = mat; vPat = pat; vFuv = fuv; vN = normalize(normal); vW = position; vEdge = edge;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
const FS = `
precision highp float;
uniform vec3 base[24]; uniform float streak[24]; uniform sampler2D face; uniform float hasFace; uniform float clay; uniform float dbg; uniform vec3 shadowCol;
varying float vMat; varying vec3 vPat; varying vec3 vFuv; varying vec3 vN; varying vec3 vW; varying float vEdge;
${SHADOW_GLSL}
float h(vec3 p){ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float noise(vec3 p){ vec3 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
  return mix(mix(mix(h(i), h(i+vec3(1,0,0)), f.x), mix(h(i+vec3(0,1,0)), h(i+vec3(1,1,0)), f.x), f.y),
             mix(mix(h(i+vec3(0,0,1)), h(i+vec3(1,0,1)), f.x), mix(h(i+vec3(0,1,1)), h(i+vec3(1,1,1)), f.x), f.y), f.z); }
void main(){
  int m = int(vMat + 0.5);
  vec3 b = base[0]; float st = 0.0;
  for (int i = 0; i < 24; i++) if (i == m) { b = base[i]; st = streak[i]; }
  vec3 n = normalize(vN); float inside = gl_FrontFacing ? 0.0 : 1.0; if (!gl_FrontFacing) n = -n;
  float d = dot(n, normalize(L));
  if (clay > 0.5) { float k = 0.35 + 0.65 * max(d, 0.0); gl_FragColor = vec4(vec3(0.85, 0.82, 0.77) * k + 0.08, 1.0); return; }
  // paper painted by brush before cutting: long streaks down the piece, fine across it (kit.py: paint)
  if (st > 0.0) { vec3 p = vPat * vec3(70.0, 3.5, 70.0);
    float s = noise(p) * 0.6 + noise(p * vec3(2.3, 1.3, 2.3) + 7.0) * 0.3 + noise(p * vec3(5.1, 1.9, 5.1) + 3.0) * 0.1;
    b *= 1.0 + st * (clamp(2.6 * s - 0.8, -0.2, 1.4) * 0.34 - 0.15); }
  // the face's pieces
  if (hasFace > 0.5 && vFuv.z > 0.01) { vec4 f = texture2D(face, vFuv.xy); float v = smoothstep(0.05, 0.3, vFuv.z); b = b * (1.0 - f.a * v) + f.rgb * v; }
  // the cut edge: the sheet's lighter core
  b = mix(b, mix(b, vec3(1.0, 0.965, 0.9), 0.5), vEdge * (1.0 - inside));
  // light: paper is matt — a soft turn from the light and the shadows other pieces throw
  float lit = smoothstep(-0.25, 0.45, d) * (1.0 - shadowAt(vW, n));
  lit = mix(lit, lit * 0.35, inside);
  vec3 col = mix(mix(b, shadowCol, 0.42) * 0.94, b, lit);
  // the paper's grain: fine tooth and fibres, fixed to the piece
  float g = noise(vPat * 1400.0) * 0.6 + noise(vPat * vec3(2600.0, 300.0, 2600.0)) * 0.4;
  col *= 0.955 + 0.09 * g;
  if (dbg > 0.5) col = vec3(shadowAt(vW, n), unpackD(texture2D(shadowMap, (shadowMatrix * vec4(vW, 1.0)).xy * 0.5 + 0.5)), (shadowMatrix * vec4(vW, 1.0)).z * 0.5 + 0.5);
  gl_FragColor = vec4(col, 1.0);
}`;

const uniforms = {
  base: { value: Array.from({ length: 24 }, () => new THREE.Color()) }, streak: { value: new Array(24).fill(0) },
  face: { value: null }, hasFace: { value: 0 }, L: { value: new THREE.Vector3(-0.5, 0.75, 0.55).normalize() }, clay: { value: 0 }, dbg: { value: +(q.get('dbg') || 0) },
  shadowMap: { value: null }, shadowMatrix: { value: new THREE.Matrix4() }, shadowSoft: { value: 0.0022 }, shadowCol: { value: hex('#2b1b2c') },
};
const material = new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, uniforms, side: THREE.DoubleSide });

// the shadow map: the figure seen from the light, depth packed in colour
const SM = +(q.get('sm') || 2048);
const shadowTarget = new THREE.WebGLRenderTarget(SM, SM, { minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
const depthMat = new THREE.ShaderMaterial({ side: THREE.DoubleSide,
  vertexShader: `void main(){ gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `precision highp float; void main(){ float z = gl_FragCoord.z; vec4 e = fract(z * vec4(1.0, 255.0, 65025.0, 16581375.0)); e -= e.yzww * vec4(1.0/255.0, 1.0/255.0, 1.0/255.0, 0.0); gl_FragColor = e; }` });
const lightCam = new THREE.OrthographicCamera(-1.15, 1.15, 1.15, -1.15, 3.4, 6.6);
uniforms.shadowMap.value = shadowTarget.texture;

let sk, figure, mesh, geom, model, clips = {};
// the floor: a sheet of paper that takes the figure's shadow. mode 1 — the sheet's own colour; 2 — only the shadow
// (for laying the picture on the drawing's backdrop)
const groundU = { mode: { value: 1 }, col: { value: hex('#c4c8b1') }, shadowMap: uniforms.shadowMap, shadowMatrix: uniforms.shadowMatrix, shadowSoft: { value: 0.006 }, L: uniforms.L, shadowCol: uniforms.shadowCol };
const ground = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.ShaderMaterial({ uniforms: groundU, transparent: true,
  vertexShader: `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
  fragmentShader: `precision highp float; varying vec3 vW; uniform float mode; uniform vec3 col; uniform vec3 shadowCol; ${SHADOW_GLSL}
    float n2(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f); return mix(mix(h1(i), h1(i+vec2(1,0)), f.x), mix(h1(i+vec2(0,1)), h1(i+vec2(1,1)), f.x), f.y); }
    void main(){ float s = shadowAt(vW, vec3(0.0, 1.0, 0.0));
      if (mode > 1.5) { gl_FragColor = vec4(shadowCol, 0.34 * s); return; }
      vec3 c = col * (0.96 + 0.08 * (n2(vW.xz * 700.0) * 0.6 + n2(vW.xz * vec2(1300.0, 150.0)) * 0.4));
      gl_FragColor = vec4(mix(c, shadowCol, 0.36 * s), 1.0); }`,
}));
ground.rotation.x = -Math.PI / 2; ground.visible = false; scene.add(ground);

// the live face: drawn every frame into a canvas the head takes (face.js)
const faceCanvas = document.createElement('canvas'); faceCanvas.width = faceCanvas.height = +(q.get('face') || 1024);
const faceCtx = faceCanvas.getContext('2d');
const faceTexture = new THREE.CanvasTexture(faceCanvas); faceTexture.flipY = false; faceTexture.anisotropy = 8; faceTexture.premultiplyAlpha = true;
const live = new LiveFace({ seed: +(q.get('seed') || 14), length: 600 });
// where the head turns: its yaw in the world each frame of a clip; the eyes lead it, fast turns call a blink
const turns = new Map();
function headTurns(c) {
  const key = c.motions.join('+');
  if (turns.has(key)) return turns.get(key);
  const H = sk.index.Head, fr = [0, 1, 2, 3].map(k => figure.body.frames[H * 4 + k]);
  const s = { q: new Float64Array(sk.J * 4), p: new Float64Array(sk.J * 3), lowest: 0 }, yaw = [];
  for (let f = 0; f < c.frames; f++) {
    c.sample(f, s);
    const qh = [0, 1, 2, 3].map(k => s.q[H * 4 + k]), d = qRot(qMul(qh, qConj(fr)), [0, 0, 1]);
    let a = Math.atan2(d[0], d[2]); if (yaw.length) { while (a - yaw[yaw.length - 1] > Math.PI) a -= 2 * Math.PI; while (a - yaw[yaw.length - 1] < -Math.PI) a += 2 * Math.PI; }
    yaw.push(a);
  }
  const at = f => { f = Math.max(0, Math.min(c.frames - 1, f)); const i = Math.floor(f), u = f - i; return yaw[i] * (1 - u) + yaw[Math.min(i + 1, c.frames - 1)] * u; };
  const fps = c.fps, blinks = []; let last = -9;
  for (let f = 1; f < c.frames; f++) { const v = (yaw[f] - yaw[f - 1]) * fps; if (Math.abs(v) > 1.6 && f / fps - last > 0.9) { blinks.push(f / fps); last = f / fps; } }
  const r = { lead: tsec => at(tsec * fps + 0.25 * fps) - at(tsec * fps), blinks };
  turns.set(key, r); return r;
}
const state = { t: 0, motion: null, lightYaw: 0, camYaw: 0 };

async function loadModel(url) {
  const { header: h, arrays: a } = await loadPack(new URL(url, location.href).href);
  h.mats.forEach((m, i) => { const p = PAPER[m]; uniforms.base.value[i] = hex(p[0]); uniforms.streak.value[i] = p[1]; });
  const body = makeBody({ id: h.id, skeleton: sk, positions: a.positions, triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
    parts: { names: h.parts || [], weights: a.parts || new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames) });
  const spec = resolve({ format: 'engine/character', version: 1, id: 'kira', body: h.id, skinning: { method: q.get('skin') || 'dqs' },
    motion: { corrections: { dampHeadSpine: { spine: +(q.get('spine') || 0.6), head: +(q.get('head') || 0.5) }, armsOutOfHead: { margin: 0.02 } } } });
  figure = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
  figure.frame(null, 0);
  if (mesh) { scene.remove(mesh); geom.dispose(); }
  geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.BufferAttribute(figure.positions, 3));
  geom.setAttribute('normal', new THREE.BufferAttribute(figure.normals, 3));
  geom.setAttribute('mat', new THREE.BufferAttribute(Float32Array.from(a.mat), 1));
  geom.setAttribute('pat', new THREE.BufferAttribute(a.pat, 3));
  geom.setAttribute('fuv', new THREE.BufferAttribute(a.fuv, 3));
  geom.setAttribute('edge', new THREE.BufferAttribute(Float32Array.from(a.edge, v => v / 255), 1));
  geom.setIndex(new THREE.BufferAttribute(a.triangles, 1));
  mesh = new THREE.Mesh(geom, material); mesh.frustumCulled = false; scene.add(mesh);
  model = { h, body };
}

async function clip(ids) {
  const key = ids.join('+');
  if (!clips[key]) clips[key] = clipOf(await Promise.all(ids.map(id => loadMotion(new URL(id.startsWith('/') ? id : `${ENG}motions/${id}.json`, location.href), sk))));
  return clips[key];
}

const A = window.A = {
  async set(o) {
    if (o.model && o.model !== state.model) { await loadModel(o.model); state.model = o.model; }
    if ('clay' in o) uniforms.clay.value = o.clay ? 1 : 0;
    if (o.motion !== undefined) state.motion = o.motion;
    if (o.t !== undefined) state.t = o.t;
    if (o.heading !== undefined) figure.place = { heading: o.heading };
    const c = state.motion ? await clip(state.motion) : null;
    figure.frame(c, state.t);
    if ('expr' in o) live.setExpressions(typeof o.expr === 'string' ? [{ t: 0, name: o.expr }] : o.expr);
    if ('talk' in o) live.talking = !!o.talk;
    if ('still' in o) live.still = !!o.still;
    if ('ground' in o) { ground.visible = !!o.ground; groundU.mode.value = o.ground === 'shadow' ? 2 : 1; }
    if (o.groundCol) groundU.col.value = hex(o.groundCol);
    ground.position.y = (figure.pose.floor ?? 0) - 0.0005;
    if (o.face === false) uniforms.hasFace.value = 0;
    else {
      const tr = c ? headTurns(c) : null;
      live.lead = tr ? tr.lead : null; live.setHeadTurns(tr ? tr.blinks : []);
      live.draw(faceCtx, o.faceTime ?? (c ? state.t / c.fps : 0)); faceTexture.needsUpdate = true;
      uniforms.face.value = faceTexture; uniforms.hasFace.value = 1;
    }
    geom.attributes.position.needsUpdate = true; geom.attributes.normal.needsUpdate = true;
    if (o.w && (o.w !== canvas.width || o.h !== canvas.height)) { renderer.setSize(o.w, o.h, false); canvas.style.width = o.w + 'px'; canvas.style.height = o.h + 'px'; }
    if (o.cam) A.camera(o.cam);
  },
  // cam: {yaw (0: from the front, −π/2: from her right), pitch, target [x,y,z] | joint + offset | follow, dist, height (ortho: metres top to bottom), fov}
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
    // the light comes from the picture's top left, wherever the picture is taken from (the drawing's rule)
    const ly = yaw + (c.lightYaw ?? -0.5), le = c.lightUp ?? 0.6;
    uniforms.L.value.set(Math.sin(ly) * Math.cos(le), Math.sin(le), Math.cos(ly) * Math.cos(le));
  },
  render() {
    // the shadow map round the figure
    const P = figure.pose.P, H = sk.index.Hips, c = new THREE.Vector3(P[H * 3], (figure.pose.floor ?? 0) + 0.8, P[H * 3 + 2]);
    lightCam.position.copy(c).addScaledVector(uniforms.L.value, 5); lightCam.up.set(0, 1, 0); lightCam.lookAt(c); lightCam.updateMatrixWorld(); lightCam.updateProjectionMatrix();
    uniforms.shadowMatrix.value.multiplyMatrices(lightCam.projectionMatrix, lightCam.matrixWorldInverse);
    const gv = ground.visible; ground.visible = false; scene.overrideMaterial = depthMat;
    renderer.setRenderTarget(shadowTarget); renderer.setClearColor(0xffffff, 1); renderer.clear(); renderer.render(scene, lightCam);
    renderer.setRenderTarget(null); renderer.setClearColor(0x000000, 0); scene.overrideMaterial = null; ground.visible = gv;
    renderer.render(scene, camera);
  },
  info() { return { joints: Array.from(figure.pose.P), N: model.body.N, floor: figure.pose.floor }; },
  clipInfo() { const c = state.motion ? clips[state.motion.join('+')] : null; return c ? { frames: c.frames, fps: c.fps } : null; },
  live,
};

sk = await loadSkeleton(new URL(`${ENG}data/skeleton.json`, location.href));
await A.set({ model: q.get('model') || new URL('../../data/kira.json', import.meta.url).href });
window.__ready = true;
