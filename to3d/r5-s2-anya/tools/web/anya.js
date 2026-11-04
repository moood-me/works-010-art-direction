// Аня in 3D, the Klaus look: the character pack (tools/build.py) on the engine's skeleton, skinning and Kimodo
// retargeting; lit the way the drawing is — one warm key light against a pink-lilac shadow, a soft but readable edge
// of the shadow, cast shadows (hair on the face, the nose on the cheek) from a shadow map, a thin warm rim on the edge
// away from the light, a light band on the hair, the face's painted layer from the drawing; then the drawing's own
// finish over the whole frame: the backdrop with its glow, fine grain, broad mottling and a vignette.
//   view.html?pack=<url of the pack .json>;   window.A.set({clip, t, pose, expr, cam, light}) then A.render()
import * as THREE from 'three';
THREE.ColorManagement.enabled = false;   // the drawing's colours are used as their numbers
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { qAxisAngle, getV } from '../../../../engine/src/math.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack'), location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const sk = E.skeleton;
const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const spec = { skinning: { method: 'cor', clavicleShare: 0.33, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });

// ---------------------------------------------------------------- the stage
const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, alpha: true });
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;   // colours are the drawing's sRGB numbers, written as they are
renderer.setClearColor(0x000000, 0);
const scene = new THREE.Scene();
const g = new THREE.BufferGeometry();
g.setAttribute('position', new THREE.BufferAttribute(fig.positions, 3));
g.setAttribute('normal', new THREE.BufferAttribute(fig.normals, 3));
for (const [k, n, norm] of [['col', 3, true], ['shd', 3, true], ['rim', 3, true], ['uv', 2, false], ['tw', 1, true], ['pn', 3, false], ['pw', 1, true], ['two', 1, false], ['hair', 1, false], ['cardi', 1, false], ['rp', 3, false]])
  g.setAttribute(k, new THREE.BufferAttribute(a[k], n, norm));
g.setIndex(new THREE.BufferAttribute(a.triangles, 1));

const loader = new THREE.TextureLoader();
const faceTex = {};
async function texture(name) {
  if (!faceTex[name]) faceTex[name] = await new Promise((ok, no) => loader.load(new URL(`${H.faces}/face-${name}.png`, packUrl).href, ok, undefined, no));
  const t = faceTex[name]; t.colorSpace = THREE.NoColorSpace; t.anisotropy = 8; return t;
}

// the shadow map: depth from the key light
const SM = 4096;
const smTarget = new THREE.WebGLRenderTarget(SM, SM);
smTarget.depthTexture = new THREE.DepthTexture(SM, SM); smTarget.depthTexture.type = THREE.UnsignedIntType;
const lightCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 10);
const depthMat = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide, colorWrite: false });

const U = {
  L: { value: new THREE.Vector3() }, Lr: { value: new THREE.Vector3() }, Vd: { value: new THREE.Vector3() },
  key: { value: new THREE.Color('#ffc47a') }, kLit: { value: 0.3 },
  thr: { value: 0.22 }, soft: { value: 0.14 },
  face: { value: await texture('calm') },
  R: { value: Array.from({ length: sk.J }, () => new THREE.Matrix3()) }, headJ: { value: sk.index.Head },
  smap: { value: smTarget.depthTexture }, smMat: { value: new THREE.Matrix4() }, smTexel: { value: 1 / SM }, smBlur: { value: 3.0 },
  smBias: { value: 0.003 },
};
const toon = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.DoubleSide,
  vertexShader: `
    attribute vec3 col; attribute vec3 shd; attribute vec3 rim; attribute float tw; attribute vec3 pn; attribute float pw;
    attribute float two; attribute float hair; attribute float cardi; attribute vec3 rp;
    varying float vCardi; varying vec3 vRp;
    uniform mat3 R[${sk.J}]; uniform int headJ; uniform mat4 smMat;
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec3 vRim; varying vec2 vUv; varying float vTw;
    varying float vTwo; varying float vHair; varying vec4 vSm; varying vec3 vW;
    void main() {
      vec3 n = normalize(normal);
      if (pw > 0.0) n = normalize(mix(n, R[headJ] * pn, pw));
      vN = n; vCol = col; vShd = shd; vRim = rim; vUv = uv; vTw = tw; vTwo = two; vHair = hair; vW = position; vCardi = cardi; vRp = rp;
      vSm = smMat * vec4(position, 1.0);
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }`,
  fragmentShader: `
    uniform vec3 L; uniform vec3 Lr; uniform vec3 Vd; uniform vec3 key; uniform float kLit; uniform float thr; uniform float soft;
    uniform sampler2D face; uniform sampler2D smap; uniform float smTexel; uniform float smBlur; uniform float smBias;
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec3 vRim; varying vec2 vUv; varying float vTw;
    varying float vTwo; varying float vHair; varying vec4 vSm; varying vec3 vW; varying float vCardi; varying vec3 vRp;
    const vec2 PD[12] = vec2[12](vec2(-0.326,-0.406), vec2(-0.840,-0.074), vec2(-0.696,0.457), vec2(-0.203,0.621),
      vec2(0.962,-0.195), vec2(0.473,-0.480), vec2(0.519,0.767), vec2(0.185,-0.893), vec2(0.507,0.064),
      vec2(0.896,0.412), vec2(-0.322,-0.933), vec2(-0.792,-0.598));
    float lit_by_map() {
      vec3 p = vSm.xyz / vSm.w * 0.5 + 0.5;
      if (p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0) return 1.0;
      float s = 0.0;
      for (int i = 0; i < 12; i++) { float d = texture2D(smap, p.xy + PD[i] * smTexel * smBlur).r; s += (p.z - smBias > d) ? 0.0 : 1.0; }
      return s / 12.0;
    }
    void main() {
      vec3 n = normalize(vN);
      vec3 base = vCol, bshd = vShd;
      // the cardigan's opening (in its rest place): the blouse in a V, the two knitted edges, two buttons
      if (vCardi > 0.5 && vRp.z > 0.0) {
        float w = clamp((vRp.y - 1.17) / 0.16, 0.0, 1.0) * 0.034;
        float ax = abs(vRp.x - 0.002);
        if (ax < w) { base = vec3(0.937, 0.886, 0.812); bshd = mix(base, vec3(0.227, 0.165, 0.353), 0.45); }
        float e = abs(ax - w);
        if (vRp.y > 0.92 && vRp.y < 1.34 && e < 0.0035) { base *= 0.62; bshd *= 0.75; }
        for (int k = 0; k < 2; k++) { float by = 1.13 - 0.06 * float(k);
          if (length(vec2(vRp.x + 0.006, vRp.y - by)) < 0.0055) { base = vec3(0.45, 0.30, 0.18); bshd = base * 0.6; } }
      }
      bool back = !gl_FrontFacing;
      if (back) { if (vTwo < 0.5) discard; n = -n; }
      float d = dot(n, L);
      float lam = smoothstep(thr - soft, thr + soft, d);
      float sh = lit_by_map();
      float l = lam * mix(1.0, smoothstep(0.15, 0.85, sh), vHair > 0.5 ? 0.45 : 1.0);
      vec3 litc = mix(base, key, kLit);
      vec3 c = mix(bshd, litc, l);
      // the hair's light band: where its surface turns to the light and up
      if (vHair > 0.5) {
        vec3 h = normalize(L + Vd);
        float b = smoothstep(0.94, 0.985, dot(n, h)) * smoothstep(0.3, 0.6, n.y) * l;
        c = mix(c, mix(vCol, vec3(1.0, 0.88, 0.66), 0.55), b * 0.85);
      }
      // rim: a thin warm edge where the form turns away from the eye on the far side from the key
      float edge = smoothstep(0.62, 0.86, 1.0 - abs(dot(n, Vd)));
      float rs = smoothstep(-0.1, 0.4, dot(n, Lr));
      c = mix(c, vRim, edge * rs * 0.65 * (back ? 0.0 : 1.0));
      if (back) c = vShd * 0.8;
      // the painted layer (eyes, brows, mouth, blush), over the shade as in the drawing, a little dimmer in shadow
      if (vTw > 0.0 && !back) { vec4 t = texture2D(face, vUv); c = mix(c, t.rgb * (0.86 + 0.14 * l), t.a * vTw); }
      gl_FragColor = vec4(c, 1.0);
    }`,
});
const mesh = new THREE.Mesh(g, toon); mesh.frustumCulled = false;
scene.add(mesh);
// the soft shadow on the floor under the figure
const ground = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 0.7), new THREE.ShaderMaterial({
  transparent: true, depthWrite: false,
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: 'varying vec2 vUv; void main(){ float r = length((vUv - 0.5) * vec2(2.0, 2.0)); gl_FragColor = vec4(0.08, 0.05, 0.13, 0.55 * (1.0 - smoothstep(0.15, 0.6, r))); }',
}));
ground.rotation.x = -Math.PI / 2; ground.position.y = 0.001; ground.renderOrder = -1; scene.add(ground);
// a floor for the films (the drawing's dark ground band, as a plane)
const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, uniforms: { c: { value: new THREE.Vector2(0, 2.6) } },
  vertexShader: 'varying vec3 vP; void main(){ vP = (modelMatrix * vec4(position, 1.0)).xyz; gl_Position = projectionMatrix * viewMatrix * vec4(vP, 1.0); }',
  fragmentShader: 'uniform vec2 c; varying vec3 vP; void main(){ float d = length(vP.xz - c); gl_FragColor = vec4(0.14, 0.09, 0.19, 0.7 * (1.0 - smoothstep(3.0, 9.0, d))); }',
}));
floor.rotation.x = -Math.PI / 2; floor.renderOrder = -2; floor.visible = false; scene.add(floor);

// the frame's finish: backdrop, glow, grain, mottling, vignette (as kit.py's bg() and grain())
const rt = new THREE.WebGLRenderTarget(16, 16, { samples: 4 });
const post = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
  uniforms: { img: { value: rt.texture }, top: { value: new THREE.Color('#2c2744') }, bot: { value: new THREE.Color('#4c3150') },
    glow: { value: new THREE.Color('#e8985a') }, gpos: { value: new THREE.Vector3(0.15, 0.35, 0.65) }, asp: { value: 1 },
    floorY: { value: -1 }, floorC: { value: new THREE.Color('#2a1b33') }, grain: { value: 0.12 } },
  depthTest: false, depthWrite: false,
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }',
  fragmentShader: `
    uniform sampler2D img; uniform vec3 top; uniform vec3 bot; uniform vec3 glow; uniform vec3 gpos; uniform float asp;
    uniform float floorY; uniform vec3 floorC; uniform float grain; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
      return mix(mix(h(i), h(i+vec2(1,0)), f.x), mix(h(i+vec2(0,1)), h(i+vec2(1,1)), f.x), f.y); }
    void main() {
      vec2 s = vec2(vUv.x, 1.0 - vUv.y);
      vec3 bg = mix(top, bot, s.y);
      float r = length(s - gpos.xy) / gpos.z;
      bg = mix(bg, glow, 0.75 * clamp(1.0 - r, 0.0, 1.0));
      if (s.y > floorY) bg = mix(bg, floorC, 0.6);
      vec4 f = texture2D(img, vUv);
      vec3 c = mix(bg, f.rgb / max(f.a, 1e-3), f.a);
      vec2 px = gl_FragCoord.xy;
      float m = vn(px * 0.018) * 0.6 + vn(px * 0.04) * 0.4;
      c = mix(c, c * (0.86 + 0.28 * m), 0.3);                      // broad mottling (soft-light-ish)
      c *= 1.0 - grain * 0.6 * h(px + 0.37);                       // fine grain (multiply)
      float v = smoothstep(0.6, 1.0, length(s - vec2(0.5, 0.45)) / 0.75);
      c = mix(c, vec3(0.078, 0.047, 0.125), 0.45 * v);
      gl_FragColor = vec4(c, 1.0);
    }`,
}));
const postScene = new THREE.Scene(); postScene.add(post);
const postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);

const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 100);
const persp = new THREE.PerspectiveCamera(24, 1, 0.05, 200);
let camera = ortho;

// ---------------------------------------------------------------- poses
const J = sk.J, I = sk.index;
function standPose(o = {}) {
  const pose = fig.restPose();
  const down = o.down ?? 0.6;
  for (const [s, sg] of [['Left', -1], ['Right', 1]]) {
    turnUnder(pose, sk, I[s + 'Arm'], qAxisAngle([0, 0, 1], sg * down));
    if (o.fwd) turnUnder(pose, sk, I[s + 'Arm'], qAxisAngle([1, 0, 0], -o.fwd));
    turnUnder(pose, sk, I[s + 'ForeArm'], qAxisAngle([1, 0, 0], o.straighten ?? 0.45));
  }
  // fingers a little curled, as a hand at rest
  const curl = o.curl ?? 0.35;
  for (const s of ['Left', 'Right']) {
    const P0 = body.joints, jp = n => [P0[I[s + n] * 3], P0[I[s + n] * 3 + 1], P0[I[s + n] * 3 + 2]];
    const ix = jp('HandIndex1'), pk = jp('HandPinky1');
    const ax = [pk[0] - ix[0], pk[1] - ix[1], pk[2] - ix[2]];
    for (const f of ['Index', 'Middle', 'Ring', 'Pinky']) for (const k of [1, 2, 3])
      turnUnder(pose, sk, I[s + 'Hand' + f + k], qAxisAngle(ax, (s === 'Left' ? 1 : -1) * (o.curlSign ?? 1) * curl * (k === 1 ? 0.6 : 1)));
  }
  if (o.headTilt) turnUnder(pose, sk, I.Head, qAxisAngle([0, 0, 1], o.headTilt));
  if (o.headNod) turnUnder(pose, sk, I.Head, qAxisAngle([1, 0, 0], o.headNod));
  build(pose, body, getV(pose.P, I.Hips));
  return pose;
}

const S = { clip: null, clipIds: null, t: 0, pose: 'stand', poseOpts: {}, expr: 'calm',
  cam: { mode: 'ortho', yaw: 0, pitch: 0, cx: 0, cy: 0.85, h: 1.8, dist: 6, follow: false },
  light: [-0.55, 0.5, 0.67], lightSpace: 'camera', shadowBox: null };
let clip = null;
function frame() {
  if (S.clip) fig.frame(clip, S.t);
  else {
    const pose = S.pose === 'rest' ? fig.restPose() : standPose(S.poseOpts);
    fig.skinner.skin(pose, fig.positions); fig.pose = pose;
  }
  if (!S.clip) normals();
  g.attributes.position.needsUpdate = true; g.attributes.normal.needsUpdate = true;
  const Q = fig.pose.Q;
  for (let j = 0; j < J; j++) { const [x, y, z, w] = [Q[j * 4], Q[j * 4 + 1], Q[j * 4 + 2], Q[j * 4 + 3]];
    U.R.value[j].set(1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)); }
  const P = fig.pose.P; ground.position.x = P[I.Hips * 3]; ground.position.z = P[I.Hips * 3 + 2];
}
import { normalsOf } from '../../../../engine/src/skin.js';
function normals() { normalsOf(fig.positions, body.triangles, fig.normals); }

window.A = {
  H, body, fig, sk,
  async set(o) {
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; }
      S.clip = !!ids;
    }
    for (const k of ['t', 'pose', 'poseOpts', 'light', 'lightSpace', 'shadowBox']) if (o[k] !== undefined) S[k] = o[k];
    if (o.expr && o.expr !== S.expr) { S.expr = o.expr; U.face.value = await texture(o.expr); }
    if (o.cam) Object.assign(S.cam, o.cam);
    for (const k of ['thr', 'soft', 'kLit', 'smBlur', 'smBias']) if (o[k] !== undefined) U[k].value = o[k];
    if (o.ground !== undefined) ground.visible = o.ground;
    if (o.floor3d !== undefined) floor.visible = o.floor3d;
    if (o.floorY !== undefined) post.material.uniforms.floorY.value = o.floorY;
    frame();
  },
  frames: () => clip ? clip.frames : 0,
  hips: () => getV(fig.pose.P, I.Hips),
  render() {
    const w = canvas.clientWidth, h = canvas.clientHeight; renderer.setSize(w, h, false);
    rt.setSize(w, h); post.material.uniforms.asp.value = w / h;
    const c = S.cam, cp = Math.cos(c.pitch);
    let tg = c.target || [c.cx, c.cy, 0];
    if (c.follow && fig.pose) { const P = fig.pose.P; tg = [P[I.Hips * 3], c.cy, P[I.Hips * 3 + 2]]; }
    const dir = [Math.sin(c.yaw) * cp, Math.sin(c.pitch), Math.cos(c.yaw) * cp];
    if (c.mode === 'ortho') {
      camera = ortho; const hh = c.h / 2, ww = hh * w / h;
      Object.assign(ortho, { left: -ww, right: ww, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
      ortho.position.set(tg[0] + dir[0] * 20, tg[1] + dir[1] * 20, tg[2] + dir[2] * 20);
    } else {
      camera = persp; persp.aspect = w / h; persp.fov = c.fov || 24; persp.updateProjectionMatrix();
      persp.position.set(tg[0] + dir[0] * c.dist, tg[1] + dir[1] * c.dist, tg[2] + dir[2] * c.dist);
    }
    camera.lookAt(tg[0], tg[1], tg[2]); camera.updateMatrixWorld();
    // the key light: given in the camera's frame (as the drawing's: from the upper left, in front) or in the world's
    const e = camera.matrixWorld.elements, l = S.light;
    const Lw = S.lightSpace === 'camera'
      ? new THREE.Vector3(e[0] * l[0] + e[4] * l[1] + e[8] * l[2], e[1] * l[0] + e[5] * l[1] + e[9] * l[2], e[2] * l[0] + e[6] * l[1] + e[10] * l[2]).normalize()
      : new THREE.Vector3(...l).normalize();
    U.L.value.copy(Lw);
    const Vd = new THREE.Vector3(); camera.getWorldDirection(Vd); U.Vd.value.copy(Vd).negate();
    // the rim's light: from behind, on the side away from the key
    const right = new THREE.Vector3(e[0], e[1], e[2]);
    const side = Lw.dot(right) > 0 ? -1 : 1;
    U.Lr.value.copy(right).multiplyScalar(side).addScaledVector(Vd, 0.6).add(new THREE.Vector3(0, 0.2, 0)).normalize();
    // the shadow map over the figure (or a smaller box, for close-ups)
    const P = fig.pose.P, hip = [P[I.Hips * 3], P[I.Hips * 3 + 1], P[I.Hips * 3 + 2]];
    const box = S.shadowBox || { c: [hip[0], 0.9, hip[2]], r: 1.05 };
    lightCam.left = -box.r; lightCam.right = box.r; lightCam.top = box.r; lightCam.bottom = -box.r;
    lightCam.near = 0.1; lightCam.far = 4 + 2 * box.r; lightCam.updateProjectionMatrix();
    lightCam.position.set(box.c[0] + Lw.x * 3, box.c[1] + Lw.y * 3, box.c[2] + Lw.z * 3);
    lightCam.lookAt(box.c[0], box.c[1], box.c[2]); lightCam.updateMatrixWorld();
    U.smMat.value.multiplyMatrices(lightCam.projectionMatrix, lightCam.matrixWorldInverse);
    U.smTexel.value = 1 / SM; U.smBlur.value = (S.blur ?? (0.003 + 0.008 * box.r)) / (2 * box.r / SM);
    mesh.material = depthMat; ground.visible = false; const fv = floor.visible; floor.visible = false;
    renderer.setRenderTarget(smTarget); renderer.clear(); renderer.render(scene, lightCam);
    mesh.material = toon; ground.visible = S.groundOn !== false; floor.visible = fv;
    renderer.setRenderTarget(rt); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera);
    renderer.setRenderTarget(null); renderer.render(postScene, postCam);
  },
};
await window.A.set({});
window.A.render();
window.__ready = true;
