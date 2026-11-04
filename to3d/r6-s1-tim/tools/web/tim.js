// Тим (С1) in 3D: the model pack (tools/build.py) made an engine body (makeBody), moved by Kimodo's motions through
// the engine's Figure (retargeting, corrections, skinning by centres of rotation), his face moved by face.js on top,
// drawn with the С1 look (look.js). window.A.set({...}) / A.render() — driven by shots.mjs and ui.js.
import * as THREE from 'three';
import { loadSkeleton } from '../../../../engine/src/skeleton.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadMotion, clipOf } from '../../../../engine/src/motion.js';
import { resolve } from '../../../../engine/src/character.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { normalsOf } from '../../../../engine/src/skin.js';
import { makeMaterial, KeyShadow } from './look.js';
import { FaceRig } from './face.js';
import { Life } from './life.js';
import { FacePaint } from './paint.js';

const ENG = new URL('../../../../engine/', import.meta.url).href;
const HERE = new URL('./', import.meta.url).href;
const q = new URLSearchParams(location.search);
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setClearColor(0x000000, 0);
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
const scene = new THREE.Scene();
const persp = new THREE.PerspectiveCamera(22, 1, 0.05, 100), ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.05, 100);
let camera = persp;
const shadow = new KeyShadow(renderer, 2048);

// the floor: his soft shadow and a contact darkening under him, over the page's backdrop (alpha)
const groundMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false,
  uniforms: { shadowTex: { value: null }, shadowMat: { value: new THREE.Matrix4() }, spot: { value: new THREE.Vector3(0, 0, 0.22) }, eye: { value: new THREE.Vector3() }, opaque: { value: 0 } },
  vertexShader: `uniform mat4 shadowMat; varying vec3 vW; varying vec4 vS; void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; vS = shadowMat * w; gl_Position = projectionMatrix * viewMatrix * w; }`,
  fragmentShader: `precision highp float; uniform sampler2D shadowTex; uniform vec3 spot; uniform vec3 eye; uniform float opaque; varying vec3 vW; varying vec4 vS;
    float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    float n(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f); return mix(mix(h(i), h(i+vec2(1,0)), f.x), mix(h(i+vec2(0,1)), h(i+vec2(1,1)), f.x), f.y); }
    void main(){ vec3 p = vS.xyz / vS.w * 0.5 + 0.5; float s = 0.0;
      if (p.x > 0.0 && p.x < 1.0 && p.y > 0.0 && p.y < 1.0) { float r = 2.5 / 2048.0;
        for (int i = -2; i <= 2; i++) for (int j = -2; j <= 2; j++) { float d = texture2D(shadowTex, p.xy + vec2(float(i), float(j)) * r).r; s += (p.z - 0.004 > d) ? 1.0 : 0.0; }
        s /= 25.0; }
      float rr = length((vW.xz - spot.xy) / vec2(1.0, 0.7)) / spot.z; float blob = 1.0 - smoothstep(0.2, 1.0, rr);
      // the floor: a soft cool paper tone with faint patches fixed to the ground (so his travel shows), fading far away
      vec3 c = vec3(0.80, 0.85, 0.89) * (0.96 + 0.05 * n(vW.xz * 1.3) + 0.03 * n(vW.xz * 5.0));
      c *= 1.0 - 0.32 * s - 0.2 * blob;
      float d = length(vW.xz - eye.xz); float a = opaque * (1.0 - smoothstep(4.0, 9.0, d));
      gl_FragColor = vec4(pow(c, vec3(1.0)), max(a, s * 0.3 + blob * 0.22)); }`,
});
const ground = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), groundMat);
ground.rotation.x = -Math.PI / 2; scene.add(ground);

let sk, figure, mesh, geom, material, model, rig, life, paint, clips = {};
const state = { t: 0, motion: null, expr: [{ t: 0, w: { calm: 1 } }], talk: [], lightCam: true, still: false };

async function loadModel(url) {
  const { header: h, arrays: a } = await loadPack(new URL(url, location.href).href);
  material = makeMaterial(h.mats);
  material.uniforms.K.value = h.K;
  const body = makeBody({ id: h.id, skeleton: sk, positions: a.positions, triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
    parts: { names: h.parts, weights: a.parts }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames) });
  const spec = resolve({ format: 'engine/character', version: 1, id: 'tim', body: h.id, skinning: { method: q.get('skin') || 'cor' },
    motion: { corrections: { armsOutOfHead: { margin: 0.03 } } } });
  figure = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
  figure.frame(null, 0);
  geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.BufferAttribute(figure.positions, 3));
  geom.setAttribute('normal', new THREE.BufferAttribute(figure.normals, 3));
  geom.setAttribute('mat', new THREE.BufferAttribute(Float32Array.from(a.mat), 1));
  geom.setAttribute('pat', new THREE.BufferAttribute(a.pat, 3));
  geom.setAttribute('aux', new THREE.BufferAttribute(a.aux, 4));
  geom.setAttribute('ao', new THREE.BufferAttribute(a.ao, 1));
  geom.setIndex(new THREE.BufferAttribute(a.triangles, 1));
  mesh = new THREE.Mesh(geom, material); mesh.frustumCulled = false; scene.add(mesh);
  model = { h, a, body };
  rig = new FaceRig(h, a);
  life = new Life({ seed: +(q.get('seed') || 11) });
  paint = new FacePaint(await (await fetch(new URL('data/paint.json', HERE))).json());
  material.uniforms.faceTex.value = paint.texture; material.uniforms.hasFace.value = 1;
}

async function clip(ids) {
  const key = ids.join('+');
  if (!clips[key]) clips[key] = clipOf(await Promise.all(ids.map(id => loadMotion(new URL(id.includes('/') ? id : `${ENG}motions/${id}.json`, location.href), sk))));
  return clips[key];
}

// the head's yaw and pitch in the world over a clip, for the gaze leading head turns (life.js)
const tracks = new Map();
function headTrack(c) {
  const key = c.motions ? c.motions.join('+') : String(c.frames);
  if (tracks.has(key)) return tracks.get(key);
  const H = sk.index.Head, yaw = [], pitch = [];
  for (let f = 0; f < c.frames; f++) {
    const pose = figure.retarget.pose(c.sample(f, figure.sample));      // the pose only: no skinning needed here
    const M = figure.skinner.matrix(pose, H);
    const d = [M[2], M[6], M[10]];          // the head's forward (its rest +z) now
    let a = Math.atan2(d[0], d[2]); if (yaw.length) { while (a - yaw[yaw.length - 1] > Math.PI) a -= 2 * Math.PI; while (a - yaw[yaw.length - 1] < -Math.PI) a += 2 * Math.PI; }
    yaw.push(a); pitch.push(Math.asin(Math.max(-1, Math.min(1, d[1]))));
  }
  const r = { fps: c.fps, yaw, pitch }; tracks.set(key, r); return r;
}

const A = window.A = {
  async set(o) {
    if (o.model && o.model !== state.model) { await loadModel(o.model); state.model = o.model; }
    for (const k of ['motion', 't', 'lightCam', 'still', 'faceTime', 'expr', 'talk', 'look', 'clay', 'groundOn', 'params', 'light', 'floor']) if (k in o) state[k] = o[k];
    if (o.heading !== undefined) figure.place = { heading: o.heading };
    const c = state.motion ? await clip(state.motion) : null;
    const tr = c ? headTrack(c) : null;
    figure.frame(c, state.t);
    // the face: the life track (blinks, gaze, speech, expressions) at this moment, or fixed params
    const ts = state.faceTime ?? (c ? state.t / c.fps : 0);
    const p = state.params ? { ...state.params } : life.at(ts, { expr: state.expr, talk: state.talk, track: tr, still: state.still, look: state.look });
    rig.apply(p, figure, sk);
    normalsOf(figure.positions, model.body.triangles, figure.normals);
    paint.draw(p); material.uniforms.pupil.value = p.pupil ?? 1;
    material.uniforms.clay.value = +state.clay || 0;
    geom.attributes.position.needsUpdate = true; geom.attributes.normal.needsUpdate = true;
    if (o.w && (o.w !== canvas.width || o.h !== canvas.height)) { renderer.setSize(o.w, o.h, false); canvas.style.width = o.w + 'px'; canvas.style.height = o.h + 'px'; }
    if (o.cam) A.camera(o.cam);
    ground.visible = state.groundOn !== false;
    const P = figure.pose.P, Hp = sk.index.Hips;
    ground.position.y = figure.pose.floor ?? 0;
    groundMat.uniforms.spot.value.set(P[Hp * 3], P[Hp * 3 + 2], 0.2);
    state.centre = new THREE.Vector3(P[Hp * 3], P[Hp * 3 + 1] + 0.05, P[Hp * 3 + 2]);
  },
  // cam: {yaw (0: from the front, −π/2: from his right), pitch, target, joint+offset, follow, dist, height (ortho), fov}
  camera(c) {
    const w = canvas.width, h = canvas.height;
    let t = c.target || [0, 0.6, 0];
    const P = figure.pose.P;
    if (c.joint) { const j = sk.index[c.joint], o = c.offset || [0, 0, 0]; t = [P[j * 3] + o[0], P[j * 3 + 1] + o[1], P[j * 3 + 2] + o[2]]; }
    if (c.follow) { const H = sk.index.Hips; t = [P[H * 3] + (c.follow[0] || 0), c.follow[1], P[H * 3 + 2] + (c.follow[2] || 0)]; }
    const yaw = c.yaw || 0, pitch = c.pitch || 0, dist = c.dist || 6;
    if (c.height) { camera = ortho; const hh = c.height / 2; Object.assign(ortho, { left: -hh * w / h, right: hh * w / h, top: hh, bottom: -hh }); }
    else { camera = persp; persp.fov = c.fov || 22; persp.aspect = w / h; }
    camera.position.set(t[0] + Math.sin(yaw) * Math.cos(pitch) * dist, t[1] + Math.sin(pitch) * dist, t[2] + Math.cos(yaw) * Math.cos(pitch) * dist);
    camera.lookAt(t[0], t[1], t[2]); camera.updateProjectionMatrix(); camera.updateMatrixWorld();
    state.cam = c;
  },
  render() {
    const U = material.uniforms;
    // the light: from the upper left of the picture (the drawing's) — fixed to the camera, or to the world for films
    let Lw;
    if (state.light) Lw = new THREE.Vector3(...state.light).normalize();
    else if (state.lightCam) {
      const m = camera.matrixWorld; const r = new THREE.Vector3().setFromMatrixColumn(m, 0), u = new THREE.Vector3().setFromMatrixColumn(m, 1), f = new THREE.Vector3().setFromMatrixColumn(m, 2);
      Lw = r.multiplyScalar(-0.55).add(u.multiplyScalar(0.62)).add(f.multiplyScalar(0.56)).normalize();
      const F = new THREE.Vector3().setFromMatrixColumn(m, 0).multiplyScalar(0.75).add(new THREE.Vector3().setFromMatrixColumn(m, 2).multiplyScalar(0.55)).add(new THREE.Vector3(0, 0.1, 0)).normalize();
      U.fillDir.value.copy(F);
    } else Lw = new THREE.Vector3(-0.5, 0.62, 0.6).normalize();
    U.L.value.copy(Lw);
    U.camPos.value.copy(camera.position);
    if (ground.visible) ground.visible = false;
    shadow.render(scene, Lw, state.centre, 0.75, U);
    ground.visible = state.groundOn !== false;
    groundMat.uniforms.shadowTex.value = shadow.rt.texture; groundMat.uniforms.shadowMat.value.copy(U.shadowMat.value);
    groundMat.uniforms.eye.value.copy(camera.position); groundMat.uniforms.opaque.value = state.floor ? 1 : 0;
    renderer.render(scene, camera);
  },
  info() { return { joints: Array.from(figure.pose.P), N: model.body.N }; },
  clipInfo() { const c = state.motion ? clips[state.motion.join('+')] : null; return c ? { frames: c.frames, fps: c.fps } : null; },
};

sk = await loadSkeleton(new URL(`${ENG}data/skeleton.json`, location.href));
await A.set({ model: q.get('model') || new URL('data/tim.json', HERE).href });
window.__ready = true;
