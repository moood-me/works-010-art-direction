// С15 «Нуар: чёрное пятно» in 3D — what every character of the style shares: the look (a paint where the light falls,
// black where the form is turned from it or another form covers it, a thin cool rim that parts black from black, the
// drawn face on the head), SOMA's skeleton with Kimodo's motions retargeted as experiments/indie does (taken from
// to3d/r22-s5-kira/tools/web/core.js), the night scene and the camera.
// A character's file gives `def` and calls start(def); then window.A.set({...}) and window.A.render() (see shots.mjs).
import * as THREE from 'three';
import { S, hex, lerp, clamp, PARENT, BONES, BI, Forms } from './build.js';
import { RECT } from './face.js';
import { FaceLive } from './live.js';

export const BLACK = '#07070b', NIGHT = '#11121b', RIM = '#3b4566';
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];

// ———————————— the look ————————————
// The light is one, from the side and a little above, and stands in the world: turn the figure and the black shape
// travels over it. A face of the mesh is lit when it looks at the light and nothing stands between (a depth picture
// taken from the light: the jaw's shadow on the neck, an arm's on the trunk, the figure's on the ground).
const VS = `
#include <common>
#include <skinning_pars_vertex>
attribute vec4 aux; attribute vec3 rp; uniform float uFloor;
varying vec3 vN; varying vec3 vC; varying vec4 vAux; varying vec3 vWP; varying vec3 vRp;
void main() {
  #include <skinbase_vertex>
  #include <beginnormal_vertex>
  #include <skinnormal_vertex>
  #include <begin_vertex>
  #include <skinning_vertex>
  vec4 wp = modelMatrix * vec4(transformed, 1.0);
  wp.y = max(wp.y, uFloor);
  vWP = wp.xyz; vN = normalize(mat3(modelMatrix) * objectNormal); vC = color; vAux = aux; vRp = rp;
  gl_Position = projectionMatrix * viewMatrix * wp;
}`;
const FS = `
uniform vec3 uL; uniform float uThr; uniform sampler2D uFace; uniform float uUseFace; uniform float uMode; uniform vec4 uHead; uniform vec4 uRect;
uniform sampler2D uShadow; uniform mat4 uSM; uniform float uSZ; uniform float uUseShadow; uniform vec3 uBlack;
uniform float uIsFloor; uniform vec3 uFadeC; uniform vec2 uFadeR; uniform vec3 uNight;
varying vec3 vN; varying vec3 vC; varying vec4 vAux; varying vec3 vWP; varying vec3 vRp;
float tap(vec2 uv, float z) { return step(z, texture2D(uShadow, uv).r); }
void main() {
  vec3 n = normalize(vN); if (!gl_FrontFacing) n = -n;
  float l = dot(n, uL);
  vec3 c;
  if (uMode > 0.5) { c = vec3(0.80, 0.78, 0.74) * (0.42 + 0.58 * max(l, 0.0)) + vec3(0.05); }
  else {
    float e = fwidth(l) * 1.0 + 1e-4;
    float lit = smoothstep(uThr - e, uThr + e, l);
    if (uUseShadow > 0.5 && lit > 0.0) {
      vec4 sp = uSM * vec4(vWP + n * (0.012 + 0.03 * (1.0 - clamp(l, 0.0, 1.0))), 1.0);
      vec3 sc = sp.xyz / sp.w * 0.5 + 0.5;
      if (sc.x > 0.002 && sc.x < 0.998 && sc.y > 0.002 && sc.y < 0.998 && sc.z < 1.0) {
        float z = sc.z - 0.0009;
        vec2 t = sc.xy * uSZ - 0.5, f = fract(t), b = (floor(t) + 0.5) / uSZ; float d = 1.0 / uSZ;
        // the shadow's edge: 4 × 4 depths weighed into a soft step, then cut hard again — a clean line, not the picture's stairs
        float s = 0.0;
        for (int j = -1; j <= 2; j++) for (int i = -1; i <= 2; i++) {
          float wx = i == -1 ? 1.0 - f.x : (i == 2 ? f.x : 1.0), wy = j == -1 ? 1.0 - f.y : (j == 2 ? f.y : 1.0);
          s += wx * wy * tap(b + vec2(float(i), float(j)) * d, z);
        }
        lit *= smoothstep(0.42, 0.58, s / 9.0);
      }
    }
    c = mix(uBlack, vC, lit);
    if (vAux.x > 0.5) c = vC;
    if (uIsFloor > 0.5) {
      // paving: thin joints, so that a walk is seen to travel; the ground goes into the night far from the figure
      vec2 q = abs(fract(vWP.xz / 1.4) - 0.5);
      c *= 1.0 - 0.25 * step(0.49, max(q.x, q.y));
      c = mix(c, uNight, smoothstep(uFadeR.x, uFadeR.y, distance(vWP.xz, uFadeC.xz)));
    }
    if (uUseFace > 0.5 && vAux.y > 0.5) {
      vec2 hu = vec2((vRp.x - uHead.x) / uHead.w, -(vRp.y - uHead.y) / uHead.w);
      vec2 uv = vec2((hu.x - uRect.x) / uRect.z, 1.0 - (hu.y - uRect.y) / uRect.w);
      vec4 f = texture2D(uFace, uv);
      c = mix(c, f.rgb, f.a);
    }
  }
  gl_FragColor = vec4(c, 1.0);
}`;
// the rim: the form's back faces pushed out a little, in the cool colour — only where the form is black
const LVS = `
#include <common>
#include <skinning_pars_vertex>
attribute vec3 smoothN; attribute vec4 aux; uniform float uW; uniform float uFloor; uniform vec3 uL; uniform float uAll;
void main() {
  vec3 objectNormal = smoothN;
  #include <skinbase_vertex>
  #include <skinnormal_vertex>
  #include <begin_vertex>
  #include <skinning_vertex>
  vec3 wn = normalize(mat3(modelMatrix) * objectNormal);
  float dark = max(uAll, smoothstep(0.25, -0.05, dot(wn, uL)));
  vec4 wp = modelMatrix * vec4(transformed, 1.0);
  wp.xyz += wn * uW * aux.z * dark;
  wp.y = max(wp.y, uFloor);
  gl_Position = projectionMatrix * viewMatrix * wp;
}`;
const LFS = `uniform vec3 uCol; void main() { gl_FragColor = vec4(uCol, 1.0); }`;

export function start(def) {
  const J = Object.fromEntries(Object.entries(def.J).map(([b, p]) => [b, p.map(v => v * S)]));
  const FACE = def.face;
  // ———————————— the forms ————————————
  const F = new Forms();
  def.forms(F);
  const GEO = F.geometry();

  const U = {
    uFloor: { value: -0.002 }, uL: { value: new THREE.Vector3(...(def.light || [-0.62, 0.38, 0.68])).normalize() }, uThr: { value: 0.1 },
    uShadow: { value: null }, uSM: { value: new THREE.Matrix4() }, uSZ: { value: def.shadowSize || 4096 }, uUseShadow: { value: 1 }, uMode: { value: 0 },
    uBlack: { value: new THREE.Color().setRGB(...hex(BLACK)) }, uNight: { value: new THREE.Color().setRGB(...hex(NIGHT)) },
    uFadeC: { value: new THREE.Vector3() }, uFadeR: { value: new THREE.Vector2(2.2, 6.5) },
    uHead: { value: new THREE.Vector4(def.head.c[0], def.head.c[1], def.head.c[2], def.head.s) }, uRect: { value: new THREE.Vector4(...RECT) },
  };
  const mat = (face, floor) => new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, vertexColors: true, side: THREE.DoubleSide, extensions: { derivatives: true },
    uniforms: { ...U, uFace: { value: face || null }, uUseFace: { value: face ? 1 : 0 }, uIsFloor: { value: floor ? 1 : 0 } } });
  const RIM_U = { uFloor: U.uFloor, uL: U.uL, uW: { value: 0.0045 }, uCol: { value: new THREE.Color().setRGB(...hex(RIM)) }, uAll: { value: 0 } };
  const RIM_MAT = new THREE.ShaderMaterial({ vertexShader: LVS, fragmentShader: LFS, side: THREE.BackSide, uniforms: RIM_U });

  // ———————————— the scene: night, a ground that takes the figure's shadow, the town far off ————————————
  const cv = document.getElementById('cv');
  const renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.LinearSRGBColorSpace;   // paints go to the screen as written
  const scene = new THREE.Scene();
  scene.background = new THREE.Color().setRGB(...hex(NIGHT));
  const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 60), persp = new THREE.PerspectiveCamera(22, 1, 0.05, 80);
  let camera = persp;
  const floor = (() => {
    const g = new THREE.PlaneGeometry(80, 80); g.rotateX(-Math.PI / 2);
    const n = g.attributes.position.count, col = new Float32Array(n * 3), aux = new Float32Array(n * 4), rp = new Float32Array(n * 3);
    const c = hex(def.ground || '#262a3b'); for (let i = 0; i < n; i++) col.set(c, i * 3);
    g.setAttribute('color', new THREE.BufferAttribute(col, 3)); g.setAttribute('aux', new THREE.BufferAttribute(aux, 4)); g.setAttribute('rp', new THREE.BufferAttribute(rp, 3));
    const m = new THREE.Mesh(g, mat(null, true)); m.position.y = -0.002; scene.add(m); return m;
  })();
  // the town: flat dark houses with lit windows and the big pale disc behind (the style's street), on a wide drum
  const town = (() => {
    const c = document.createElement('canvas'); c.width = 2048; c.height = 1024; const g = c.getContext('2d');
    g.fillStyle = NIGHT; g.fillRect(0, 0, 2048, 1024);
    g.fillStyle = def.back[0]; g.beginPath(); g.arc(1024, 730, 250, 0, 7); g.fill();
    let s = 7; const r = () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
    for (let layer = 0; layer < 2; layer++) {
      let x = -40;
      while (x < 2048) {
        const w = 90 + r() * 150, h = (layer ? 150 : 260) + r() * (layer ? 160 : 220), y = 1024 - h, roof = r() < 0.6 ? 30 + r() * 40 : 0;
        g.fillStyle = layer ? '#1b1d2a' : '#161823';
        g.beginPath(); g.moveTo(x, 1024); g.lineTo(x, y); g.lineTo(x + w / 2, y - roof); g.lineTo(x + w, y); g.lineTo(x + w, 1024); g.fill();
        g.fillStyle = def.back[1];
        for (let k = 0; k < 3; k++) if (r() < 0.55) g.fillRect(x + 14 + r() * (w - 40), y + 24 + r() * (h - 110), 12, 18);
        x += w + (r() < 0.3 ? 30 + r() * 60 : 2);
      }
    }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace; t.wrapS = THREE.RepeatWrapping; t.repeat.set(6, 1); t.anisotropy = 4;
    const m = new THREE.Mesh(new THREE.CylinderGeometry(16, 16, 9, 64, 1, true), new THREE.MeshBasicMaterial({ map: t, side: THREE.BackSide }));
    m.position.y = 4.5 - 0.6; scene.add(m); return m;
  })();
  // the pale shape behind the figure in the drawing's views (a disc as in its portraits, a panel as in its sheets)
  const disc = new THREE.Mesh(new THREE.CircleGeometry(1, 96), new THREE.MeshBasicMaterial({ color: new THREE.Color().setRGB(...hex(def.back[0])) }));
  disc.position.z = -6; disc.visible = false; scene.add(disc);

  // the depth picture from the light
  const SZ = def.shadowSize || 4096;
  const shadowRT = new THREE.WebGLRenderTarget(SZ, SZ, { depthTexture: new THREE.DepthTexture(SZ, SZ) });
  shadowRT.depthTexture.minFilter = shadowRT.depthTexture.magFilter = THREE.NearestFilter;
  const lightCam = new THREE.OrthographicCamera(-2.3, 2.3, 2.3, -2.3, 0.5, 14);
  lightCam.layers.set(1);
  const depthMat = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide });
  U.uShadow.value = shadowRT.depthTexture;

  // the face: drawn on a canvas each time it changes, carried by the head
  const FPX = 6;
  function faceCanvas() {
    const c = document.createElement('canvas'); c.width = RECT[2] * FPX; c.height = RECT[3] * FPX;
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace; t.anisotropy = 4;
    return { c, g: c.getContext('2d'), t };
  }
  function instance() {
    const bones = {}, root = new THREE.Group();
    for (const b of BONES) { bones[b] = new THREE.Bone(); bones[b].name = b; }
    for (const b of BONES) { const p = PARENT[b], pp = p ? J[p] : [0, 0, 0]; bones[b].position.set(...sub(J[b], pp)); if (p) bones[p].add(bones[b]); else root.add(bones[b]); }
    const skel = new THREE.Skeleton(BONES.map(b => bones[b]));
    root.updateMatrixWorld(true); skel.calculateInverses();
    const fc = faceCanvas(), mats = [], meshes = [], I0 = [];
    const body = new THREE.SkinnedMesh(GEO.body, mat(fc.t)); body.frustumCulled = false; body.bind(skel); body.layers.enable(1); root.add(body); mats.push(body.material); meshes.push(body);
    const rim = new THREE.SkinnedMesh(GEO.body, RIM_MAT); rim.frustumCulled = false; rim.bind(skel); root.add(rim);
    // forms that take the light and shadow but throw none (the nose, the ears: their shadows would cut the face up)
    if (GEO.soft) { const m = new THREE.SkinnedMesh(GEO.soft, mat(null)); m.frustumCulled = false; m.bind(skel); root.add(m); mats.push(m.material); const r = new THREE.SkinnedMesh(GEO.soft, RIM_MAT); r.frustumCulled = false; r.bind(skel); root.add(r); I0.push(r); }
    let props = null;
    if (GEO.props) { props = new THREE.SkinnedMesh(GEO.props, mat(null)); props.frustumCulled = false; props.bind(skel); root.add(props); mats.push(props.material); meshes.push(props); }
    const I = { root, bones, skel, body, rim, props, mats, meshes, fc, extra: [], movers: {}, soft: I0 };
    // parts that move by the face's numbers (a moustache): their own meshes on a bone, turning about a pivot
    for (const [name, mv] of Object.entries(def.movers || {})) {
      const piv = mv.pivot.map(v => v * S), g = new THREE.Group(); g.position.set(...sub(piv, J[mv.bone]));
      const m = new THREE.Mesh(GEO[name], mat(null)); m.position.set(-piv[0], -piv[1], -piv[2]); m.frustumCulled = false; mats.push(m.material);
      const r = new THREE.Mesh(GEO[name], RIM_MAT); r.position.copy(m.position); r.frustumCulled = false;
      g.add(m, r); bones[mv.bone].add(g); I.movers[name] = g; I0.push(r);
    }
    if (def.attach) def.attach(I, { THREE, J, S, mat });
    return I;
  }
  function drawFaceOn(I, Fc) { FACE.drawFace(I.fc.g, Fc, FPX); I.fc.t.needsUpdate = true; I.lastF = Fc; if (def.onFace) def.onFace(I, Fc); }

  // ———————————— Kimodo's motions (experiments/indie's retargeting): each SOMA joint turns as in the motion, a fixed
  // turn first brings our bone to SOMA's rest direction; the pelvis goes as high and as far as our legs make it; the
  // feet are put back on the ground ————————————
  const MOTION = {};
  const motion = name => MOTION[name] ??= fetch(new URL(`../motions/${name}.json`, import.meta.url)).then(r => r.json()).then(prepare);
  const CHAIN = { LeftLeg: 'LeftShin', LeftShin: 'LeftFoot', LeftFoot: 'LeftToeBase', RightLeg: 'RightShin', RightShin: 'RightFoot', RightFoot: 'RightToeBase',
    LeftShoulder: 'LeftArm', LeftArm: 'LeftForeArm', LeftForeArm: 'LeftHand', LeftHand: 'LeftHandMiddle1', RightShoulder: 'RightArm', RightArm: 'RightForeArm', RightForeArm: 'RightHand', RightHand: 'RightHandMiddle1' };
  function prepare(M) {
    M.C = Object.fromEntries(Object.entries(CHAIN).map(([b, c]) => {
      const ours = /Hand$/.test(b) ? sub(J[b], J[PARENT[b]]) : sub(J[c], J[b]);
      return [b, new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(...ours).normalize(), new THREE.Vector3(...sub(M.rest[c], M.rest[b])).normalize())];
    }));
    const fw = new THREE.Vector3(), q = new THREE.Quaternion();
    M.hyaw = new Float32Array(M.n); M.hpitch = new Float32Array(M.n);
    let lean = 0;
    for (let f = 0; f < M.n; f++) { const d = M.D.Chest; q.set(d[f * 4], d[f * 4 + 1], d[f * 4 + 2], d[f * 4 + 3]); fw.set(0, 0, 1).applyQuaternion(q); lean += Math.asin(clamp(fw.y, -1, 1)) * 180 / Math.PI; }
    M.lean = lean / M.n;
    for (let f = 0; f < M.n; f++) { const d = M.D.Head; q.set(d[f * 4], d[f * 4 + 1], d[f * 4 + 2], d[f * 4 + 3]); fw.set(0, 0, 1).applyQuaternion(q); M.hyaw[f] = Math.atan2(fw.x, fw.z) * 180 / Math.PI; M.hpitch[f] = Math.asin(clamp(fw.y, -1, 1)) * 180 / Math.PI; }
    return M;
  }
  const _qa = new THREE.Quaternion(), _qb = new THREE.Quaternion(), _v = new THREE.Vector3();
  function dq(M, b, f) {
    const d = M.D[b], i = Math.floor(f), j = Math.min(i + 1, M.n - 1), t = f - i;
    _qa.set(d[i * 4], d[i * 4 + 1], d[i * 4 + 2], d[i * 4 + 3]); _qb.set(d[j * 4], d[j * 4 + 1], d[j * 4 + 2], d[j * 4 + 3]);
    return _qa.clone().slerp(_qb, t);
  }
  const hipsAt = (M, f, k) => { const i = Math.floor(f), j = Math.min(i + 1, M.n - 1), t = f - i; return lerp(M.hips[i * 3 + k], M.hips[j * 3 + k], t); };
  const atF = (arr, f, n) => { const i = Math.floor(clamp(f, 0, n - 1)), j = Math.min(i + 1, n - 1); return lerp(arr[i], arr[j], clamp(f, 0, n - 1) - i); };
  const restPos = b => { const p = PARENT[b]; return sub(J[b], p ? J[p] : [0, 0, 0]); };
  function setLocal(I, W) { for (const b of BONES) { const p = PARENT[b]; I.bones[b].quaternion.copy(p ? W[p].clone().invert().multiply(W[b]) : W[b]); } I.root.updateMatrixWorld(true); }
  const under = (b, a) => { for (let p = b; p; p = PARENT[p]) if (p === a) return true; return false; };
  const UPPER = BONES.filter(b => under(b, 'Spine1'));
  const restDir = (a, b) => new THREE.Vector3(...sub(J[b], J[a])).normalize();
  // I.clip: {upright, arms: name of def.armPoses, posture: on/off}
  function pose(I, M, f, travel, offset = [0, 0]) {
    const W = {}, clip = I.clip;
    for (const b of BONES) {
      const p = PARENT[b];
      let w;
      if (M && M.D[b]) { w = dq(M, b, f); if (M.C[b]) w.multiply(M.C[b]); }
      else w = p ? W[p].clone() : new THREE.Quaternion();
      W[b] = w;
    }
    const side = new THREE.Vector3(1, 0, 0).applyQuaternion(W.Hips);
    // the clip's average stoop taken out (Kimodo's waiting motions bow), its movement kept
    if (M && clip.upright && M.lean) { const fix = new THREE.Quaternion().setFromAxisAngle(side, clip.upright * M.lean * Math.PI / 180); for (const b of UPPER) W[b].premultiply(fix); }
    // the character's own carriage, on every motion: [joint, degrees forward] — the joint and all it carries
    for (const [jn, deg] of (clip.posture ?? def.posture ?? [])) { const fix = new THREE.Quaternion().setFromAxisAngle(side, deg * Math.PI / 180); for (const b of BONES) if (under(b, jn)) W[b].premultiply(fix); }
    // arms held in a pose of the drawing (a hand with the watch, a hand behind the back): directions in the chest's frame
    const AP = clip.arms ? def.armPoses[clip.arms] : null;
    if (AP) for (const s of ['Left', 'Right']) {
      const a = AP[s]; if (!a) continue;
      const up = W.Chest.clone().multiply(new THREE.Quaternion().setFromUnitVectors(restDir(s + 'Arm', s + 'ForeArm'), new THREE.Vector3(...a.arm).normalize()));
      const fo = W.Chest.clone().multiply(new THREE.Quaternion().setFromUnitVectors(restDir(s + 'ForeArm', s + 'Hand'), new THREE.Vector3(...a.fore).normalize()));
      if (a.roll) fo.multiply(new THREE.Quaternion().setFromAxisAngle(restDir(s + 'ForeArm', s + 'Hand'), a.roll * Math.PI / 180));
      W[s + 'Shoulder'] = W.Chest.clone(); W[s + 'Arm'] = up; W[s + 'ForeArm'] = fo; W[s + 'Hand'] = fo.clone();
    } else if (M) {
      // free arms keep off the trunk: the upper arm stays out to its side
      for (const [s, k] of [['Left', 1], ['Right', -1]]) {
        const sd = new THREE.Vector3(k, 0, 0).applyQuaternion(W.Chest);
        const d2 = new THREE.Vector3(...sub(M.rest[s + 'ForeArm'], M.rest[s + 'Arm'])).normalize().applyQuaternion(dq(M, s + 'Arm', f));
        const out = d2.dot(sd), need = def.armOut ?? 0.2;
        if (out < need) { const ax = new THREE.Vector3().crossVectors(d2, sd).normalize(), fix = new THREE.Quaternion().setFromAxisAngle(ax, Math.asin(need) - Math.asin(Math.max(-1, out))); for (const b of [s + 'Arm', s + 'ForeArm', s + 'Hand']) W[b].premultiply(fix); }
      }
    }
    setLocal(I, W);
    const kr = M ? J.Hips[1] / M.hipY : 1;
    if (M) I.bones.Hips.position.set(travel ? (hipsAt(M, f, 0) - M.hips[0]) * kr + offset[0] : 0, hipsAt(M, f, 1) * kr, travel ? (hipsAt(M, f, 2) - M.hips[2]) * kr + offset[1] : 0);
    else I.bones.Hips.position.set(...J.Hips);
    I.root.updateMatrixWorld(true);
    // the feet on the ground: the lowest point of the soles
    let low = 1e9;
    for (const [b, pts] of Object.entries(def.soles)) {
      const m = new THREE.Matrix4().multiplyMatrices(I.bones[b].matrixWorld, I.skel.boneInverses[BI[b]]);
      for (const p of pts) { _v.set(p[0] * S, p[1] * S, p[2] * S).applyMatrix4(m); if (_v.y < low) low = _v.y; }
    }
    I.bones.Hips.position.y += (M ? atF(M.foot, f, M.n) * kr : 0) - (low - I.root.position.y);
    I.root.updateMatrixWorld(true);
  }

  // ———————————— what is shown ————————————
  const CLIPS = def.CLIPS;
  let placed = [], overlay = null;
  const state = { view: 'style' };
  // a figure: {x, z (m), yaw (deg), ex | exprW, clip, f | t, travel, live, talk, seed}
  async function place(Fg) {
    const clip = CLIPS[Fg.clip || 'stand'] || {};
    const I = instance();
    I.F = Fg; I.clip = { ...clip, ...(Fg.over || {}) }; I.M = I.clip.motion ? await motion(I.clip.motion) : null; I.travel = Fg.travel ?? clip.travel ?? false;
    I.root.position.set(Fg.x || 0, 0, Fg.z || 0); I.root.rotation.y = (Fg.yaw || 0) * Math.PI / 180;
    scene.add(I.root);
    I.exprW = Fg.exprW || { [Fg.ex || 'neutral']: 1 };
    if (Fg.live) { I.live = new FaceLive(FACE, Fg.seed ?? 11); I.live.setExpr(I.exprW); I.live.x = FACE.mixExpr(I.exprW); I.live.setTalk(!!Fg.talk); }
    return I;
  }
  function update(I, t, dt) {
    const M = I.M;
    let headYaw = 0, headPitch = 0, aheadYaw = 0, aheadPitch = 0;
    for (const b of BONES) I.bones[b].position.set(...restPos(b));
    if (M) {
      const n = M.n, fr = t * M.fps * (I.clip.speed || 1), loop = Math.floor(fr / n), f = fr - loop * n, kr = J.Hips[1] / M.hipY;
      const off = I.travel ? [(M.hips[(n - 1) * 3] - M.hips[0]) * kr * loop, (M.hips[(n - 1) * 3 + 2] - M.hips[2]) * kr * loop] : [0, 0];
      pose(I, M, f, I.travel, off);
      const fa = Math.min(f + 0.3 * M.fps, n - 1), y0 = M.hyaw[0], up = -(I.clip.upright || 0) * M.lean;
      headYaw = atF(M.hyaw, f, n) - y0; headPitch = atF(M.hpitch, f, n) + up; aheadYaw = atF(M.hyaw, fa, n) - y0; aheadPitch = atF(M.hpitch, fa, n) + up;
    } else pose(I, null, 0, false);
    if (I.live) { I.live.step(dt, { yaw: headYaw, pitch: headPitch, aheadYaw, aheadPitch }); drawFaceOn(I, I.live.face()); }
    else if (!I.drawn) { drawFaceOn(I, { e: FACE.vecExpr(FACE.mixExpr(I.exprW)) }); I.drawn = true; }
  }
  // the camera: straight from the front without perspective (the drawing's views: ortho [x, y of the middle, half
  // height] in metres), or one that orbits a point on the figure (follow: the point goes with the hips, softly)
  const cam = { yaw: 25, pitch: 6, dist: 3.2, ty: 0.8, fov: 22, follow: false, at: [0, 0.8, 0] };
  function setCam(c) {
    if (c.ortho) {
      const [x, y, hh] = c.ortho, a = cv.width / cv.height; camera = ortho;
      Object.assign(ortho, { left: x - hh * a, right: x + hh * a, top: y + hh, bottom: y - hh });
      ortho.position.set(0, 0, 20); ortho.lookAt(0, 0, 0); ortho.updateProjectionMatrix();
      return;
    }
    camera = persp;
    if (c.pos) cam.fixed = c; else { cam.fixed = null; Object.assign(cam, c); }
    aimCam(true);
  }
  function aimCam(snap) {
    if (camera !== persp) return;
    persp.aspect = cv.width / cv.height;
    if (cam.fixed) { persp.fov = cam.fixed.fov || 22; persp.position.set(...cam.fixed.pos); persp.lookAt(...cam.fixed.at); persp.updateProjectionMatrix(); return; }
    const I = placed[0];
    let at = [0, cam.ty, 0];
    if (I && cam.follow) { I.bones.Hips.getWorldPosition(_v); at = [_v.x, cam.ty + (cam.followY || 0) * (_v.y - J.Hips[1]), _v.z]; }
    cam.at = snap || !cam.at ? at : cam.at.map((a, i) => lerp(a, at[i], cam.soft ?? 0.12));   // soft: how fast the aim follows (1 — at once)
    const yw = cam.yaw * Math.PI / 180, pt = cam.pitch * Math.PI / 180;
    persp.fov = cam.fov;
    persp.position.set(cam.at[0] + cam.dist * Math.sin(yw) * Math.cos(pt), cam.at[1] + cam.dist * Math.sin(pt), cam.at[2] + cam.dist * Math.cos(yw) * Math.cos(pt));
    persp.lookAt(...cam.at);
    if (cam.pad) persp.setViewOffset(cv.width, cv.height, 0, cam.pad / 2, cv.width, cv.height); else persp.clearViewOffset();
    persp.updateProjectionMatrix();
  }
  async function set(o) {
    if (o.size) { renderer.setSize(o.size[0], o.size[1], false); cv.style.width = o.size[0] + 'px'; cv.style.height = o.size[1] + 'px'; }
    if (o.view) state.view = o.view;
    if (o.floor !== undefined) { floor.visible = o.floor; town.visible = o.floor; }
    // bg: {col, disc: [x, y, r] (m)} — the drawing's plain backs; none: the night street
    if (o.bg !== undefined) {
      scene.background = new THREE.Color().setRGB(...hex(o.bg?.col || NIGHT));
      disc.visible = !!o.bg?.disc; if (o.bg?.disc) { disc.position.set(o.bg.disc[0], o.bg.disc[1], -6); disc.scale.setScalar(o.bg.disc[2]); }
    }
    if (o.light) U.uL.value.set(...o.light).normalize();
    if (o.shadow !== undefined) U.uUseShadow.value = o.shadow ? 1 : 0;
    if (o.rim !== undefined) RIM_U.uW.value = o.rim;
    if (o.figures) {
      for (const I of placed) { scene.remove(I.root); I.fc.t.dispose(); for (const m of I.mats) m.dispose(); }
      placed = [];
      for (const Fg of o.figures) { const I = await place(Fg); update(I, Fg.t ?? (Fg.f || 0) / (I.M ? I.M.fps : 30), 0); placed.push(I); }
    }
    if (o.cam) setCam(o.cam);
    applyView();
  }
  // views: style — the look; flat — the paints without light (what is painted where); clay — the form alone, grey;
  // noface — the look without the drawn face; bones — the skeleton over the look
  function applyView() {
    const v = state.view;
    U.uMode.value = v === 'clay' ? 1 : 0;
    U.uThr.value = v === 'flat' ? -2 : 0.1;
    for (const I of placed) {
      I.body.material.uniforms.uUseFace.value = v === 'style' || v === 'bones' ? 1 : 0;
      I.rim.visible = v !== 'clay' && v !== 'flat';
      for (const r of I.soft) r.visible = I.rim.visible;
      for (const x of I.extra) x.visible = v !== 'clay';
      if (I.props) I.props.visible = v !== 'clay';
    }
    bonesView(v === 'bones');
  }
  function frame(o) {
    for (const I of placed) {
      if (I.live) { if (o.expr) I.live.setExpr(o.expr); if (o.talk !== undefined) I.live.setTalk(o.talk); }
      if (o.yaw !== undefined) I.root.rotation.y = o.yaw * Math.PI / 180;
      update(I, o.t ?? 0, o.dt ?? 1 / 30);
    }
    aimCam(false);
    if (overlay) bonesView(true);
  }
  function bonesView(on) {
    if (overlay) { scene.remove(overlay); overlay = null; }
    if (!on) return;
    overlay = new THREE.Group();
    const p = [], d = [], a = new THREE.Vector3(), b = new THREE.Vector3();
    for (const I of placed) for (const bn of BONES) {
      I.bones[bn].getWorldPosition(a); d.push(a.x, a.y, a.z);
      const pb = PARENT[bn]; if (pb) { I.bones[pb].getWorldPosition(b); p.push(b.x, b.y, b.z, a.x, a.y, a.z); }
    }
    const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(p, 3));
    const ln = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: '#e0b040', depthTest: false, transparent: true }));
    const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.Float32BufferAttribute(d, 3));
    const pt = new THREE.Points(pg, new THREE.PointsMaterial({ color: '#e0b040', size: 6, sizeAttenuation: false, depthTest: false, transparent: true }));
    ln.renderOrder = pt.renderOrder = 10;
    overlay.add(ln, pt); scene.add(overlay);
  }
  const _t = new THREE.Vector3();
  function render() {
    // the light's picture follows the figure
    const I = placed[0];
    if (I) I.bones.Hips.getWorldPosition(_t); else _t.set(0, 0.8, 0);
    _t.y = 0.8;
    U.uFadeC.value.copy(_t);
    lightCam.position.copy(_t).addScaledVector(U.uL.value, 7); lightCam.lookAt(_t); lightCam.updateMatrixWorld(true);
    U.uSM.value.multiplyMatrices(lightCam.projectionMatrix, lightCam.matrixWorldInverse);
    if (U.uUseShadow.value > 0.5) {
      const bg = scene.background; scene.background = null; scene.overrideMaterial = depthMat;
      renderer.setRenderTarget(shadowRT); renderer.clear(); renderer.render(scene, lightCam); renderer.setRenderTarget(null);
      scene.overrideMaterial = null; scene.background = bg;
    }
    renderer.render(scene, camera);
  }
  window.A = { set, frame, render, cam, setCam, aimCam, S, J, CLIPS, EXPR_RU: def.EXPR_RU, name: def.name, placed: () => placed, renderer, state, applyView, motion, U };
  window.__ready = true;
}
