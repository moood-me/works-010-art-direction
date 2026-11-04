// Вера in 3D, the Arcane look: the character pack (tools/build.py) on the engine's skeleton, skinning and Kimodo
// retargeting; lit the way the drawing's rules say — one warm key light from the upper left, the shadow one graphic
// shape with a clear, brushed edge, a warm saturated band along the shadow's edge, red-brown shadows on the skin,
// csh shadows (shadow map), a cool rim on the shadow side, painterly strokes in the shade and the half-tones, the
// face's painted layer (faces.py), real eyeballs with a painted iris and a glint; then the drawing's own backdrop
// (a light glow falling into dark), canvas and grain over the whole frame.
//   view.html?pack=<url of vera.json>;   window.A.set({clip, t, pose, expr, face, cam, draw, light}) then A.render()
import * as THREE from 'three';
THREE.ColorManagement.enabled = false;
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { qAxisAngle, getV, qBetween, sub, add, scale, dot, cross, len, normalize } from '../../../../engine/src/math.js';
import { normalsOf } from '../../../../engine/src/skin.js';
import { Face, mix as faceMix } from './face.js';
import { lifeTrack, headFacing } from './life.js';
import { qRot } from '../../../../engine/src/math.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack') || 'data/vera.json', location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const faceData = await (await fetch(new URL('face.json', packUrl))).json();
const sk = E.skeleton;
const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const spec = { skinning: { method: 'cor', clavicleShare: 0.33, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
const face = new Face(body, faceData, H);
const K = H.K, FEET = H.FEET, ZOFF = H.ZOFF;
const Wd = (x, y, z) => [x * K, (FEET - y) * K, z * K + ZOFF];       // drawing units → world (rest)

// ---------------------------------------------------------------- the stage
const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, alpha: true });
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
renderer.setClearColor(0x000000, 0);
const scene = new THREE.Scene();
const g = new THREE.BufferGeometry();
g.setAttribute('position', new THREE.BufferAttribute(fig.positions, 3));
g.setAttribute('normal', new THREE.BufferAttribute(fig.normals, 3));
g.setAttribute('rest', new THREE.BufferAttribute(Float32Array.from(a.positions), 3));
for (const [k, n, norm] of [['col', 3, true], ['shd', 3, true], ['glw', 3, true], ['rim', 3, true], ['mat', 1, false], ['uv', 2, false], ['tw', 1, true],
  ['pn', 3, false], ['pw', 1, true], ['two', 1, false], ['hs', 1, false], ['hg', 1, true], ['dr', 3, false]])
  g.setAttribute(k, new THREE.BufferAttribute(a[k], n, norm));
g.setIndex(new THREE.BufferAttribute(a.triangles, 1));
const MATS = H.materials, MI = n => MATS.indexOf(n);

const faceImg = await new Promise((ok, no) => new THREE.TextureLoader().load(new URL('face.png', packUrl).href, ok, undefined, no));
faceImg.colorSpace = THREE.NoColorSpace; faceImg.anisotropy = 8;

const SM = 4096;
const smTarget = new THREE.WebGLRenderTarget(SM, SM);
smTarget.depthTexture = new THREE.DepthTexture(SM, SM); smTarget.depthTexture.type = THREE.UnsignedIntType;
const lightCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 10);
const depthMat = new THREE.ShaderMaterial({
  side: THREE.DoubleSide, colorWrite: false,
  vertexShader: 'attribute float mat; varying float vM; void main(){ vM = mat; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: `varying float vM; void main(){ if (abs(vM - ${MI('frame').toFixed(1)}) < 0.5) discard; }`,   // the glasses csh no shadow
});

const eyes = faceData.eyes;   // drawing units
const U = {
  L: { value: new THREE.Vector3() }, Lr: { value: new THREE.Vector3() }, Vd: { value: new THREE.Vector3() },
  key: { value: new THREE.Color('#fff1dc') }, kLit: { value: 0.12 },
  thr: { value: 0.12 }, edgeN: { value: 0.035 },
  face: { value: faceImg },
  R: { value: Array.from({ length: sk.J }, () => new THREE.Matrix3()) }, headJ: { value: sk.index.Head },
  smap: { value: smTarget.depthTexture }, smMat: { value: new THREE.Matrix4() }, smTexel: { value: 1 / SM }, smBlur: { value: 2.0 },
  smBias: { value: 0.002 },
  eyeL: { value: new THREE.Vector3(...eyes[0]) }, eyeR: { value: new THREE.Vector3(...eyes[1]) }, irisR: { value: faceData.iris_r },
  look: { value: new THREE.Vector4(0, 0, 0, 0) },
};
const M = n => MI(n).toFixed(1);
const toon = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.DoubleSide,
  vertexShader: `
    attribute vec3 col; attribute vec3 shd; attribute vec3 glw; attribute vec3 rim; attribute float mat; attribute float tw;
    attribute vec3 pn; attribute float pw; attribute float two; attribute float hs; attribute float hg; attribute vec3 dr; attribute vec3 rest;
    uniform mat3 R[${sk.J}]; uniform int headJ; uniform mat4 smMat;
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec3 vGlw; varying vec3 vRim; varying vec2 vUv; varying float vTw;
    varying float vTwo; varying float vMat; varying float vHs; varying float vHg; varying vec3 vDr; varying vec3 vRest; varying vec4 vSm;
    varying vec3 vWp;
    void main() {
      vec3 n = normalize(normal);
      if (pw > 0.0) n = normalize(mix(n, R[headJ] * pn, pw));
      vN = n; vCol = col; vShd = shd; vGlw = glw; vRim = rim; vUv = uv; vTw = tw; vTwo = two; vMat = mat; vHs = hs; vHg = hg;
      vDr = dr; vRest = rest; vWp = position;
      vSm = smMat * vec4(position, 1.0);
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }`,
  fragmentShader: `
    uniform vec3 L; uniform vec3 Lr; uniform vec3 Vd; uniform vec3 key; uniform float kLit; uniform float thr; uniform float edgeN;
    uniform sampler2D face; uniform sampler2D smap; uniform float smTexel; uniform float smBlur; uniform float smBias;
    uniform vec3 eyeL; uniform vec3 eyeR; uniform float irisR; uniform vec4 look;
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec3 vGlw; varying vec3 vRim; varying vec2 vUv; varying float vTw;
    varying float vTwo; varying float vMat; varying float vHs; varying float vHg; varying vec3 vDr; varying vec3 vRest; varying vec4 vSm;
    varying vec3 vWp;
    const vec2 PD[12] = vec2[12](vec2(-0.326,-0.406), vec2(-0.840,-0.074), vec2(-0.696,0.457), vec2(-0.203,0.621),
      vec2(0.962,-0.195), vec2(0.473,-0.480), vec2(0.519,0.767), vec2(0.185,-0.893), vec2(0.507,0.064),
      vec2(0.896,0.412), vec2(-0.322,-0.933), vec2(-0.792,-0.598));
    float h3(vec3 p){ return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
    float vn3(vec3 p){ vec3 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
      return mix(mix(mix(h3(i), h3(i+vec3(1,0,0)), f.x), mix(h3(i+vec3(0,1,0)), h3(i+vec3(1,1,0)), f.x), f.y),
                 mix(mix(h3(i+vec3(0,0,1)), h3(i+vec3(1,0,1)), f.x), mix(h3(i+vec3(0,1,1)), h3(i+vec3(1,1,1)), f.x), f.y), f.z); }
    float fbm(vec3 p){ return 0.55 * vn3(p) + 0.3 * vn3(p * 2.1) + 0.15 * vn3(p * 4.3); }
    float lit_by_map() {
      vec3 p = vSm.xyz / vSm.w * 0.5 + 0.5;
      if (p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0) return 1.0;
      float s = 0.0;
      for (int i = 0; i < 12; i++) { float d = texture2D(smap, p.xy + PD[i] * smTexel * smBlur).r; s += (p.z - smBias > d) ? 0.0 : 1.0; }
      return s / 12.0;
    }
    bool is(float m) { return abs(vMat - m) < 0.5; }
    // the coat's front, from its rest place in the drawing's units: lapels, the shirt's V, the seam, the brooch, the waist seam
    void coatFront(inout vec3 base, inout vec3 bshd, inout vec3 glw, vec3 dw) {
      if (dw.z < 0.0) return;
      float ax = abs(dw.x), y = dw.y;
      float xin = y < 260.0 ? mix(16.0, 3.0, clamp((y - 160.0) / 100.0, 0.0, 1.0)) : mix(3.0, 7.0, clamp((y - 260.0) / 160.0, 0.0, 1.0));
      float xout = y < 205.0 ? mix(40.0, 78.0, clamp((y - 165.0) / 40.0, 0.0, 1.0)) : mix(78.0, 7.0, clamp((y - 205.0) / 215.0, 0.0, 1.0));
      if (y > 158.0 && y < 420.0 && ax > xin && ax < xout) {           // the lapels: a darker cloth, a fine light edge
        base = vec3(0.165, 0.204, 0.259); bshd = vec3(0.10, 0.125, 0.16);
        if (ax > xout - 1.6) base *= 1.35;
      }
      if (y > 110.0 && y < 205.0 && ax < mix(11.0, 1.5, clamp((y - 130.0) / 75.0, 0.0, 1.0))) { base = vec3(0.925, 0.902, 0.871); bshd = vec3(0.61, 0.59, 0.65); glw = vec3(0.85, 0.75, 0.72); }
      if (y > 200.0 && y < 425.0 && ax < 0.9) { base *= 0.55; bshd *= 0.6; }              // the front edge
      if (abs(y - 428.0) < 1.6) { base *= 0.62; bshd *= 0.7; }                             // the waist seam
      vec2 b = vec2(dw.x, y - 166.0);
      if (length(b) < 4.6) { base = vec3(0.54, 0.17, 0.21); bshd = vec3(0.29, 0.09, 0.13);
        if (length(b - vec2(-1.3, -1.4)) < 1.4) base = vec3(1.0, 0.82, 0.82); }
    }
    void main() {
      vec3 n = normalize(vN);
      bool back = !gl_FrontFacing;
      if (back) { if (vTwo < 0.5) discard; n = -n; }
      vec3 base = vCol, bshd = vShd, glw = vGlw;
      float lensA = 0.0;
      if (is(${M('lens')})) {                      // the glasses' glass: only a glint, screen-door transparent
        vec3 rf = reflect(-Vd, n);
        float gl = smoothstep(0.86, 0.97, dot(rf, normalize(L + vec3(0.0, 0.3, 0.0))));
        float stripe = smoothstep(0.35, 0.0, abs(fract((vDr.x - vDr.y * 0.9) * 0.09) - 0.5) - 0.12);
        float al = 0.55 * gl * stripe;
        if (h3(vec3(gl_FragCoord.xy, 0.0)) > al) discard;
        if (gl < 0.05) discard;
        gl_FragColor = vec4(mix(vec3(0.85, 0.9, 0.95), vec3(1.0), gl), 1.0); return;
      }
      vec3 dw = vec3(vRest.x / ${K.toFixed(6)}, ${FEET.toFixed(1)} - vRest.y / ${K.toFixed(6)}, (vRest.z - ${ZOFF.toFixed(6)}) / ${K.toFixed(6)});
      if (is(${M('coat')})) coatFront(base, bshd, glw, dw);
      if (is(${M('skin')}) && dw.y > 127.0 && dw.z > -10.0) {          // the shirt's white band in front of the neck
        float wv = 6.0 + (dw.y - 127.0) * 0.12;
        if (abs(dw.x) < wv) { base = vec3(0.925, 0.902, 0.871); bshd = vec3(0.61, 0.59, 0.65); glw = vec3(0.85, 0.75, 0.72);
          if (abs(dw.x) < 0.5 && dw.y > 150.0) base *= 0.7; }
      }
      // the eye: the iris painted on its disc (pupil, a dark ring, light below, the lid's shade above)
      if (is(${M('iris')})) {
        vec3 e = vDr.x > 0.0 ? eyeL : eyeR;
        vec2 d = (vDr.xy - e.xy - vec2(0.0, -0.2)) / irisR;
        float r = length(d);
        vec3 c1 = vec3(0.114, 0.157, 0.204), c2 = vec3(0.302, 0.416, 0.51), c3 = vec3(0.651, 0.729, 0.776);
        vec3 ic = mix(c2, c3, smoothstep(-0.1, 0.7, d.y) * 0.85);
        ic = mix(ic, c1, smoothstep(0.7, 0.95, r));
        float spokes = vn3(vec3(atan(d.y, d.x) * 6.0, r * 3.0, 0.0));
        ic *= 0.85 + 0.3 * spokes;
        ic = mix(ic, vec3(0.04, 0.045, 0.06), 1.0 - smoothstep(0.34, 0.40, r));
        base = ic; bshd = ic * 0.55;
      }
      float d = dot(n, L);
      // the shadow's edge: a clear shape, its border brushed (noise on the surface, not on the screen)
      vec3 np = vRest * vec3(38.0, 30.0, 38.0);
      float brush = fbm(np) - 0.5 + 0.35 * (vn3(vRest * vec3(160.0, 20.0, 160.0)) - 0.5);
      float t = thr + edgeN * brush;
      float lam = smoothstep(t - 0.015, t + 0.015, d);
      float sh = lit_by_map();
      float csh = smoothstep(0.25, 0.75, sh);
      if (is(${M('hair')})) csh = mix(1.0, csh, 0.7);
      float l = lam * csh;
      vec3 litc = mix(base, base * key * 1.08, kLit);
      // half-tone inside the light: a little darker toward the shadow (mixing, not a second step)
      litc *= mix(0.9, 1.04, smoothstep(t, t + 0.6, d));
      vec3 c = mix(bshd, litc, l);
      // the warm band along the shadow's edge, on the shadow's side
      float band = (1.0 - lam) * smoothstep(t - 0.22, t - 0.01, d) * csh + (1.0 - csh) * lam * smoothstep(0.0, 0.5, sh) * 0.7;
      c = mix(c, glw, 0.42 * band);
      // deep shade where the form turns right away
      c *= 1.0 - 0.18 * smoothstep(-0.3, -0.7, d);
      // painterly strokes in the shade and the half-tones: streaks along the form
      float strokes = vn3(vRest * vec3(90.0, 28.0, 90.0)) * 0.6 + vn3(vRest * vec3(260.0, 60.0, 260.0)) * 0.4;
      c *= 1.0 + (strokes - 0.5) * mix(0.16, 0.05, l);
      // hair: strands sweeping to the bun, dark partings between locks, a streaky light where it turns to the light
      if (is(${M('hair')})) {
        float s1 = vn3(vec3(vHs * 38.0, vDr.y * 0.02, 0.0));
        float s2 = vn3(vec3(vHs * 130.0, vDr.y * 0.05, 1.0));
        float lock = smoothstep(0.15, 0.6, s1);
        vec3 hb = mix(base, vec3(0.42, 0.38, 0.41), vHg * 0.9);
        vec3 hl = mix(vec3(0.36, 0.31, 0.33), vec3(0.74, 0.70, 0.73), vHg);
        c = mix(mix(bshd, hb, l), c, 0.0);
        c *= 0.7 + 0.45 * lock * (0.7 + 0.6 * s2);
        vec3 hh = normalize(L + Vd);
        float shine = smoothstep(0.80, 0.95, dot(n, hh)) * l * (0.4 + 0.6 * s2) * lock;
        c = mix(c, hl, shine * 0.75);
        c = mix(c, hl * 0.8, vHg * l * 0.25);
      }
      // rim: a cool light along the edge on the shadow's side
      float edge = smoothstep(0.55, 0.85, 1.0 - abs(dot(n, Vd)));
      float rs = smoothstep(-0.05, 0.45, dot(n, Lr));
      c = mix(c, vRim, edge * rs * 0.5 * (1.0 - l * 0.7) * (back ? 0.0 : 1.0));
      if (back) c = vShd * 0.7;
      // the face's painted layer (brows, lids, lips, blush, lines), in shade a little dimmer and warmer
      if (vTw > 0.0 && !back) {
        vec4 tx = texture2D(face, vUv);
        vec3 pc = tx.rgb * mix(vec3(0.78, 0.66, 0.66), vec3(1.0), l);
        c = mix(c, pc, tx.a * vTw);
      }
      // glints on the eyes: the key's reflection on the wet ball, sharp
      if (is(${M('iris')}) || is(${M('sclera')})) {
        vec3 rf = reflect(-Vd, n);
        float gl = smoothstep(0.985, 0.995, dot(rf, L)) * csh;
        float g2 = smoothstep(0.990, 0.997, dot(rf, normalize(vec3(-L.x, -0.4, L.z)))) * 0.6;
        c = mix(c, vec3(1.0), max(gl, g2));
      }
      if (is(${M('frame')})) { vec3 rf = reflect(-Vd, n); c = mix(c, vec3(0.75, 0.78, 0.85), smoothstep(0.8, 0.95, dot(rf, L)) * 0.8); }
      gl_FragColor = vec4(c, 1.0);
    }`,
});
const mesh = new THREE.Mesh(g, toon); mesh.frustumCulled = false;
scene.add(mesh);

// the folder she holds: a card folder (ochre, light pages showing at the edge), carried by the left hand
const folderGeo = new THREE.BoxGeometry(0.155, 0.215, 0.01);
const folderMat = new THREE.ShaderMaterial({
  uniforms: U,
  vertexShader: 'varying vec3 vN; varying vec3 vP; void main(){ vN = normalize(mat3(modelMatrix) * normal); vP = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: `uniform vec3 L; varying vec3 vN; varying vec3 vP;
    void main(){ vec3 n = normalize(vN); float d = dot(n, L);
      vec3 base = abs(vP.z) > 0.0045 ? vec3(0.72, 0.635, 0.478) : vec3(0.937, 0.91, 0.855);
      vec3 sh = base * vec3(0.55, 0.5, 0.58);
      vec3 c = mix(sh, base, smoothstep(0.08, 0.12, d));
      gl_FragColor = vec4(c, 1.0); }`,
});
const folder = new THREE.Mesh(folderGeo, folderMat); folder.matrixAutoUpdate = false; folder.frustumCulled = false;
scene.add(folder);

const ground = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.6), new THREE.ShaderMaterial({
  transparent: true, depthWrite: false,
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: 'varying vec2 vUv; void main(){ float r = length((vUv - 0.5) * vec2(2.0, 2.0)); gl_FragColor = vec4(0.05, 0.05, 0.07, 0.5 * (1.0 - smoothstep(0.1, 0.55, r))); }',
}));
ground.rotation.x = -Math.PI / 2; ground.position.y = 0.001; ground.renderOrder = -1; scene.add(ground);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, uniforms: { c: { value: new THREE.Vector2(0, 0) } },
  vertexShader: 'varying vec3 vP; void main(){ vP = (modelMatrix * vec4(position, 1.0)).xyz; gl_Position = projectionMatrix * viewMatrix * vec4(vP, 1.0); }',
  fragmentShader: 'uniform vec2 c; varying vec3 vP; void main(){ float d = length(vP.xz - c); gl_FragColor = vec4(0.07, 0.08, 0.1, 0.75 * (1.0 - smoothstep(2.0, 7.0, d))); }',
}));
floor.rotation.x = -Math.PI / 2; floor.renderOrder = -2; floor.visible = false; scene.add(floor);

// the frame's finish: the drawing's backdrop (a radial glow falling into dark), canvas, grain
const rt = new THREE.WebGLRenderTarget(16, 16, { samples: 4 });
const post = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
  uniforms: { img: { value: rt.texture }, c1: { value: new THREE.Color('#9fb4c8') }, c2: { value: new THREE.Color('#4a5668') }, c3: { value: new THREE.Color('#191c24') },
    gpos: { value: new THREE.Vector2(0.36, 0.3) }, asp: { value: 1 }, grain: { value: 0.07 }, res: { value: new THREE.Vector2(1, 1) } },
  depthTest: false, depthWrite: false,
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }',
  fragmentShader: `
    uniform sampler2D img; uniform vec3 c1; uniform vec3 c2; uniform vec3 c3; uniform vec2 gpos; uniform float asp; uniform float grain; uniform vec2 res;
    varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
      return mix(mix(h(i), h(i+vec2(1,0)), f.x), mix(h(i+vec2(0,1)), h(i+vec2(1,1)), f.x), f.y); }
    void main() {
      vec2 s = vec2(vUv.x, 1.0 - vUv.y);
      vec2 px = s * res;
      float r = length(px - gpos * res) / (0.8 * max(res.x, res.y));
      vec3 bg = r < 0.45 ? mix(c1, c2, r / 0.45) : mix(c2, c3, (r - 0.45) / 0.55);
      vec4 f = texture2D(img, vUv);
      vec3 c = mix(bg, f.rgb / max(f.a, 1e-3), f.a);
      vec2 fc = gl_FragCoord.xy;
      float canvasT = vn(fc * vec2(0.9, 0.12)) * 0.5 + vn(fc * vec2(0.12, 0.9)) * 0.5;
      c *= 1.0 + (canvasT - 0.5) * 0.06;
      float m = vn(fc * 0.02) * 0.6 + vn(fc * 0.05) * 0.4;
      c *= 1.0 + (m - 0.5) * 0.05;
      c *= 1.0 + (h(fc + 0.37) - 0.5) * grain;
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
  build(pose, body, getV(pose.P, I.Hips));
  // the arms hang at the sides: each wrist put by the thigh, the elbow a little back
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    const Sh = getV(pose.P, I[s + 'Arm']), Wr = getV(pose.P, I[s + 'Hand']), El = getV(pose.P, I[s + 'ForeArm']);
    const L = len(sub(El, Sh)) + len(sub(Wr, El));
    reach(pose, s, [Sh[0] + sg * (o.out ?? 0.05), Sh[1] - L * 0.985, Sh[2] + (o.fwd ?? 0.02)], [sg * 0.2, 0, -1]);
    turnUnder(pose, sk, I[s + 'ForeArm'], qAxisAngle(normalize(sub(getV(pose.P, I[s + 'Hand']), getV(pose.P, I[s + 'ForeArm']))), sg * (o.twist ?? 0.9)));
  }
  build(pose, body, getV(pose.P, I.Hips));
  if (o.hold !== false) {           // the left arm holds the folder at the chest, as drawn: the hand put there (two-bone reach)
    const T = Wd(...(o.holdAt ?? [34, 350, 0]));
    T[2] = chestZ(T[1], T[0]) + (o.holdOut ?? 0.055);
    reach(pose, 'Left', T, o.pole ?? [0.6, -0.5, -0.45]);
    turnUnder(pose, sk, I.LeftHand, qAxisAngle([0, 0, 1], o.wristZ ?? 0.5));
    turnUnder(pose, sk, I.LeftHand, qAxisAngle([0, 1, 0], o.wristY ?? -0.9));
    turnUnder(pose, sk, I.LeftHand, qAxisAngle([1, 0, 0], o.wristX ?? 0.0));
  }
  const curl = o.curl ?? 0.3;
  for (const s of ['Left', 'Right']) {
    const P0 = body.joints, jp = n => [P0[I[s + n] * 3], P0[I[s + n] * 3 + 1], P0[I[s + n] * 3 + 2]];
    const ix = jp('HandIndex1'), pk = jp('HandPinky1');
    const ax = [pk[0] - ix[0], pk[1] - ix[1], pk[2] - ix[2]];
    const c = s === 'Left' && o.hold !== false ? 0.75 : curl;
    for (const f of ['Index', 'Middle', 'Ring', 'Pinky']) for (const k of [1, 2, 3])
      turnUnder(pose, sk, I[s + 'Hand' + f + k], qAxisAngle(ax, (s === 'Left' ? 1 : -1) * c * (k === 1 ? 0.6 : 1)));
  }
  if (o.head) turnUnder(pose, sk, I.Head, qAxisAngle(o.head.axis, o.head.a));
  build(pose, body, getV(pose.P, I.Hips));
  return pose;
}

// the coat's front (rest) at a height and side: where the folder lies against the chest
function chestZ(y, x) {
  let zf = -1; const rp = a.positions;
  for (let i = 0; i < body.N; i++) { if (a.mat[i] !== MI('coat')) continue; const yy = rp[i * 3 + 1], xx = rp[i * 3];
    if (Math.abs(yy - y) < 0.02 && Math.abs(xx - x) < 0.03) zf = Math.max(zf, rp[i * 3 + 2]); }
  return zf;
}
// two bones (upper arm, forearm) turned so the wrist reaches T, the elbow toward the pole
function reach(pose, s, T, pole) {
  const jS = I[s + 'Arm'], jE = I[s + 'ForeArm'], jW = I[s + 'Hand'];
  const S0 = getV(pose.P, jS), E0 = getV(pose.P, jE), W0 = getV(pose.P, jW);
  const l1 = len(sub(E0, S0)), l2 = len(sub(W0, E0));
  let dv = sub(T, S0); let d = len(dv); d = Math.min(d, (l1 + l2) * 0.999); const ax = normalize(dv);
  const cosA = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), sinA = Math.sqrt(Math.max(0, 1 - cosA * cosA));
  const pp = normalize(sub(pole, scale(ax, dot(pole, ax))));
  const E1 = add(S0, add(scale(ax, l1 * cosA), scale(pp, l1 * sinA)));
  turnUnder(pose, sk, jS, qBetween(normalize(sub(E0, S0)), normalize(sub(E1, S0))));
  build(pose, body, getV(pose.P, I.Hips));
  const E2 = getV(pose.P, jE), W2 = getV(pose.P, jW);
  turnUnder(pose, sk, jE, qBetween(normalize(sub(W2, E2)), normalize(sub(T, E2))));
  build(pose, body, getV(pose.P, I.Hips));
}

const S = { clip: null, clipIds: null, t: 0, pose: 'stand', poseOpts: {}, face: {}, folder: true,
  cam: { mode: 'ortho', yaw: 0, pitch: 0, cx: 0, cy: 0.9, h: 1.9, dist: 6, follow: false },
  light: [-0.5, 0.55, 0.67], lightSpace: 'camera', shadowBox: null, draw: null };
let clip = null;
// the folder's place in the left hand's frame, set once from the standing pose (held flat against the chest)
let folderLocal = null;
// the skirt is not cloth: after skinning, every skirt point that is inside a leg (a capsule round the thigh and the
// shin) is put on the capsule's surface, so a stepping leg carries the skirt instead of going through it
const SK = H.ranges.skirt;
function pushSkirt() {
  const P = fig.pose.P, X = fig.positions;
  const caps = [];
  for (const s of ['Left', 'Right']) {
    const a0 = getV(P, I[s + 'Leg']), k = getV(P, I[s + 'Shin']), f = getV(P, I[s + 'Foot']);
    caps.push([a0, k, 0.078, 0.062], [k, f, 0.06, 0.046]);
  }
  for (let i = SK[0]; i < SK[1]; i++) {
    const p = [X[i * 3], X[i * 3 + 1], X[i * 3 + 2]];
    for (const [A, B, r0, r1] of caps) {
      const ab = sub(B, A), t = Math.max(0, Math.min(1, dot(sub(p, A), ab) / dot(ab, ab)));
      const c = add(A, scale(ab, t)), d = sub(p, c), l = len(d), r = r0 + (r1 - r0) * t;
      const wgt = Math.min(1, Math.max(0, (A[1] - 0.06 - p[1]) / 0.12));      // not round the hip joint itself
      if (l < r && l > 1e-6 && wgt > 0) { const q = add(c, scale(d, r / l)); p[0] += (q[0] - p[0]) * wgt; p[1] += (q[1] - p[1]) * wgt; p[2] += (q[2] - p[2]) * wgt; }
    }
    X[i * 3] = p[0]; X[i * 3 + 1] = p[1]; X[i * 3 + 2] = p[2];
  }
}
function headM(pose) { return fig.skinner.matrix(pose, I.Head); }
function frame() {
  if (S.clip) fig.frame(clip, S.t);
  else {
    const pose = S.pose === 'rest' ? fig.restPose() : standPose(S.poseOpts);
    fig.skinner.skin(pose, fig.positions); fig.pose = pose;
  }
  pushSkirt();
  // the face: its form moved by a few numbers, turned with the head; alive: from the life track at this moment
  if (S.life) S.face = S.life.at(S.clip ? S.t / 30 : S.t);
  face.update(S.face);
  face.apply(fig.positions, headM(fig.pose));
  normalsOf(fig.positions, body.triangles, fig.normals);
  g.attributes.position.needsUpdate = true; g.attributes.normal.needsUpdate = true;
  const Q = fig.pose.Q;
  for (let j = 0; j < J; j++) { const [x, y, z, w] = [Q[j * 4], Q[j * 4 + 1], Q[j * 4 + 2], Q[j * 4 + 3]];
    U.R.value[j].set(1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)); }
  const P = fig.pose.P; ground.position.x = P[I.Hips * 3]; ground.position.z = P[I.Hips * 3 + 2];
  floor.material.uniforms.c.value.set(P[I.Hips * 3], P[I.Hips * 3 + 2]);
  // the folder
  const hm = fig.skinner.matrix(fig.pose, I.LeftHand);
  const HM = new THREE.Matrix4().set(hm[0], hm[1], hm[2], hm[3], hm[4], hm[5], hm[6], hm[7], hm[8], hm[9], hm[10], hm[11], 0, 0, 0, 1);
  if (!folderLocal) {
    // the folder lies against the chest, behind the hand that holds it, upright and turned a little to her left
    const sp = standPose(S.poseOpts); const m = fig.skinner.matrix(sp, I.LeftHand);
    const M0 = new THREE.Matrix4().set(m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11], 0, 0, 0, 1);
    const hp = getV(sp.P, I.LeftHand);
    const fc = Wd(...(S.poseOpts.folderAt ?? [30, 335, 0]));
    const W0 = new THREE.Matrix4().compose(new THREE.Vector3(fc[0], fc[1], chestZ(fc[1], fc[0]) + 0.02),
      new THREE.Quaternion().setFromEuler(new THREE.Euler(-0.12, 0.3, 0.06)), new THREE.Vector3(1, 1, 1));
    folderLocal = new THREE.Matrix4().copy(M0).invert().multiply(W0);
  }
  folder.matrix.copy(HM).multiply(folderLocal); folder.matrixWorldNeedsUpdate = true;
  folder.visible = S.folder;
}

// the life of the face over the clip (blinks, gaze leading the head, speech, expressions): one track per clip
function makeLife(opts) {
  const seconds = opts.seconds ?? (clip ? clip.frames / 30 : 12);
  let head = () => ({ yaw: 0, pitch: 0 });
  if (clip) {
    const yaws = [], pitches = [], smp = fig.sample;
    for (let f = 0; f <= clip.frames; f++) {
      const pose = fig.retarget.pose(clip.sample(Math.min(f, clip.frames - 1), smp));
      const h = headFacing(pose, I.Head, qRot); yaws.push(h.yaw); pitches.push(h.pitch);
    }
    const pl = fig.place.heading || 0;
    head = t => { const x = Math.max(0, Math.min(clip.frames, t * 30)), i = Math.floor(x), j = Math.min(clip.frames, i + 1), f = x - i;
      return { yaw: yaws[i] + (yaws[j] - yaws[i]) * f, pitch: pitches[i] + (pitches[j] - pitches[i]) * f }; };
  }
  return lifeTrack(head, { seconds, seed: opts.seed ?? 7, talk: opts.talk, expr: opts.expr, talkFrom: opts.talkFrom, talkTo: opts.talkTo });
}

window.A = {
  H, body, fig, sk, face, standPose,
  async set(o) {
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; }
      S.clip = !!ids;
    }
    for (const k of ['t', 'pose', 'light', 'lightSpace', 'shadowBox', 'draw', 'folder']) if (o[k] !== undefined) S[k] = o[k];
    if (o.poseOpts !== undefined) { S.poseOpts = o.poseOpts; folderLocal = null; }
    if (o.face !== undefined) S.face = o.face;
    if (o.live !== undefined) S.life = o.live ? makeLife(o.live) : null;
    if (o.expr !== undefined) S.face = faceMix(typeof o.expr === 'string' ? { [o.expr]: 1 } : o.expr);
    if (o.cam) Object.assign(S.cam, o.cam);
    for (const k of ['thr', 'edgeN', 'kLit', 'smBlur', 'smBias']) if (o[k] !== undefined) U[k].value = o[k];
    if (o.ground !== undefined) ground.visible = o.ground;
    if (o.floor3d !== undefined) floor.visible = o.floor3d;
    frame();
  },
  frames: () => clip ? clip.frames : 0,
  hips: () => getV(fig.pose.P, I.Hips),
  render() {
    const w = canvas.clientWidth, h = canvas.clientHeight; renderer.setSize(w, h, false);
    rt.setSize(w, h); post.material.uniforms.res.value.set(w, h);
    const c = S.cam;
    let dir, tg;
    if (S.draw) {
      // the drawing's own camera: View(yaw, s, cx, cy) — the head's origin (eye line, middle) at pixel (cx, cy), s px per unit
      const D = S.draw, yaw = -D.yaw * Math.PI / 180;
      dir = [Math.sin(yaw), 0, Math.cos(yaw)];
      const right = [Math.cos(yaw), 0, -Math.sin(yaw)];
      const o0 = Wd(0, 0, 0), hj = I.Hips * 3; o0[0] -= body.joints[hj]; o0[2] -= body.joints[hj + 2]; o0[1] -= body.measures.floor;   // the rest put over the place (Figure.restPose)
      const dx = (w / 2 - D.cx) / D.s, dy = (h / 2 - D.cy) / D.s;
      tg = [o0[0] + right[0] * dx * K, o0[1] - dy * K, o0[2] + right[2] * dx * K];
      camera = ortho; const hh = h / D.s * K / 2, ww = w / D.s * K / 2;
      Object.assign(ortho, { left: -ww, right: ww, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
      ortho.position.set(tg[0] + dir[0] * 20, tg[1], tg[2] + dir[2] * 20);
    } else {
      const cp = Math.cos(c.pitch);
      tg = c.target || [c.cx, c.cy, 0];
      if (c.follow && fig.pose) { const P = fig.pose.P; tg = [P[I.Hips * 3] + (c.dx || 0), c.cy, P[I.Hips * 3 + 2] + (c.dz || 0)]; }
      dir = [Math.sin(c.yaw) * cp, Math.sin(c.pitch), Math.cos(c.yaw) * cp];
      if (c.mode === 'ortho') {
        camera = ortho; const hh = c.h / 2, ww = hh * w / h;
        Object.assign(ortho, { left: -ww, right: ww, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
        ortho.position.set(tg[0] + dir[0] * 20, tg[1] + dir[1] * 20, tg[2] + dir[2] * 20);
      } else {
        camera = persp; persp.aspect = w / h; persp.fov = c.fov || 24; persp.updateProjectionMatrix();
        persp.position.set(tg[0] + dir[0] * c.dist, tg[1] + dir[1] * c.dist, tg[2] + dir[2] * c.dist);
      }
    }
    camera.lookAt(tg[0], tg[1], tg[2]); camera.updateMatrixWorld();
    const e = camera.matrixWorld.elements, l = S.light;
    const Lw = S.lightSpace === 'camera'
      ? new THREE.Vector3(e[0] * l[0] + e[4] * l[1] + e[8] * l[2], e[1] * l[0] + e[5] * l[1] + e[9] * l[2], e[2] * l[0] + e[6] * l[1] + e[10] * l[2]).normalize()
      : new THREE.Vector3(...l).normalize();
    U.L.value.copy(Lw);
    const Vd = new THREE.Vector3(); camera.getWorldDirection(Vd); U.Vd.value.copy(Vd).negate();
    const right = new THREE.Vector3(e[0], e[1], e[2]);
    const side = Lw.dot(right) > 0 ? -1 : 1;
    U.Lr.value.copy(right).multiplyScalar(side).addScaledVector(Vd, 0.5).add(new THREE.Vector3(0, 0.15, 0)).normalize();
    const P = fig.pose.P, hip = [P[I.Hips * 3], P[I.Hips * 3 + 1], P[I.Hips * 3 + 2]];
    const box = S.shadowBox || { c: [hip[0], 0.9, hip[2]], r: 1.05 };
    lightCam.left = -box.r; lightCam.right = box.r; lightCam.top = box.r; lightCam.bottom = -box.r;
    lightCam.near = 0.1; lightCam.far = 4 + 2 * box.r; lightCam.updateProjectionMatrix();
    lightCam.position.set(box.c[0] + Lw.x * 3, box.c[1] + Lw.y * 3, box.c[2] + Lw.z * 3);
    lightCam.lookAt(box.c[0], box.c[1], box.c[2]); lightCam.updateMatrixWorld();
    U.smMat.value.multiplyMatrices(lightCam.projectionMatrix, lightCam.matrixWorldInverse);
    U.smTexel.value = 1 / SM; U.smBlur.value = (S.blur ?? (0.0015 + 0.004 * box.r)) / (2 * box.r / SM);
    mesh.material = depthMat; const gv = ground.visible, fv = floor.visible; ground.visible = false; floor.visible = false;
    const fm = folder.material; folder.material = depthMat;
    renderer.setRenderTarget(smTarget); renderer.clear(); renderer.render(scene, lightCam);
    mesh.material = toon; folder.material = fm; ground.visible = gv; floor.visible = fv;
    renderer.setRenderTarget(rt); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera);
    renderer.setRenderTarget(null); renderer.render(postScene, postCam);
  },
};
await window.A.set({});
window.A.render();
window.__ready = true;
