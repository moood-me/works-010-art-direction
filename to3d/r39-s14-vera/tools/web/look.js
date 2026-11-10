// С14 in 3D — the look: every piece is drawn flat in its own colour (painted paper with brush streaks along the piece),
// together with "which piece, how far"; then one pass over the picture does what styles/s14-paper/tools/kit.py's
// filters do to each piece of the drawing: a crisp contact shadow and a soft cast shadow down-right on whatever lies
// further from the eye (three lengths — the further below, the longer and softer), a light rim along the lit edge
// (the thickness of the sheet), and the sheet's grain over all. The light is fixed top-left on the picture, as in the
// drawing: turning the figure does not move it.
import * as THREE from 'three';
import { U } from './paper.js';

THREE.ColorManagement.enabled = false;
const SS = 2;                                    // the pieces are drawn at twice the size: clean scissor edges

const VERT = `precision highp float;
in vec3 position; in vec2 puv;
uniform mat4 modelViewMatrix, projectionMatrix;
out vec2 vUv; out float vDepth;
void main() { vec4 mv = modelViewMatrix * vec4(position, 1.); vUv = puv; vDepth = -mv.z; gl_Position = projectionMatrix * mv; }`;

const NOISE = `
float hash(vec2 p) { p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
float vnoise(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
  return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y); }
float fbm(vec2 p) { return (vnoise(p) * 4. + vnoise(p * 2. + 7.3) * 2. + vnoise(p * 4. + 1.7)) / 7.; }`;

const FRAG = `precision highp float;
in vec2 vUv; in float vDepth;
uniform vec3 color; uniform float id, paint, near, far; uniform vec2 freq; uniform float seed, curlR; uniform vec2 curlC;
layout(location = 0) out vec4 gColor; layout(location = 1) out vec4 gId;
${NOISE}
void main() {
  vec3 c = color;
  if (paint > .5) { float n = clamp(2.6 * fbm(vUv * freq + seed) - .8, 0., 1.); c *= .80 + .46 * n; }
  gColor = vec4(c, 1.);
  float t = clamp((vDepth - near) / (far - near), 0., .999999);
  vec3 e = fract(t * vec3(1., 255., 65025.)); e -= e.yzz * vec3(1. / 255., 1. / 255., 0.);
  gId = vec4(id / 255., e);
}`;

const POST = `precision highp float;
uniform sampler2D tC, tI; uniform vec2 res; uniform float s, near, far, grain, shadowK, flatLook; uniform vec3 bg; uniform vec2 hole;
out vec4 o;
${NOISE}
const vec3 SH = vec3(.169, .106, .173);
float dep(vec4 i) { return near + (far - near) * dot(i.gba, vec3(1., 1. / 255., 1. / 65025.)); }
float idn(vec4 i) { return floor(i.r * 255. + .5); }
bool casts(float id) { return id > 1.5 && id < 127.5; }
vec4 I(vec2 px) { return texture(tI, px / res); }
// one point of the picture: the piece's colour, its contact shadow and its lit rim
vec3 point(vec2 px) {
  vec4 i = I(px); float id = idn(i), d = dep(i);
  vec3 c = id < .5 ? bg : texture(tC, px / res).rgb;
  if (flatLook > .5) return c;
  vec4 q = I(px + vec2(-.7, 1.) * s * shadowK); float qi = idn(q);
  if (casts(qi) && qi != id && dep(q) < d - .0004) c = mix(c, SH, .5);
  else if (casts(id)) { q = I(px + vec2(-.9, 1.1) * max(s * shadowK, .75)); if (idn(q) != id && dep(q) > d + .0004) c = mix(c, vec3(1.), .42); }
  return c;
}
float soft(vec2 px, float id, float d, vec2 off, float blur, float thr) {
  float a = 0.;
  for (int k = 0; k < 14; k++) {
    float fk = float(k) + .5, r = sqrt(fk / 14.) * blur * 2., t = fk * 2.39996;
    vec4 q = I(px + (vec2(-off.x, off.y) + r * vec2(cos(t), sin(t))) * s * shadowK); float qi = idn(q);
    if (casts(qi) && qi != id && dep(q) < d - thr) a += 1.;
  }
  return a / 14.;
}
void main() {
  vec2 px = gl_FragCoord.xy;
  vec3 c = (point(px + vec2(-.25, -.25)) + point(px + vec2(.25, -.25)) + point(px + vec2(-.25, .25)) + point(px + vec2(.25, .25))) / 4.;
  if (flatLook < .5) {
    vec4 i = I(px); float id = idn(i), d = dep(i);
    float back = id < 1.5 ? 1. : 0.;                                   // the sheet behind and the ground: shadows stay short
    float sh = .40 * soft(px, id, d, vec2(1.3, 2.2), 1.3, .0004);
    sh = max(sh, .36 * soft(px, id, d, vec2(2.8, 4.6), 2.8, mix(.012, .0004, back)));
    if (back < .5) sh = max(sh, .32 * soft(px, id, d, vec2(5.5, 9.5), 5.5, .07));
    c = mix(c, SH, sh);
  }
  // the sheet's grain: fine tooth and fibres, fixed on the picture
  if (grain > 0.) {
    float fine = clamp(1.5 * fbm(px * .85 * 1.6) - .25, 0., 1.), fibre = clamp(1.2 * fbm(px * vec2(.9, .05) * 1.6 + 31.) - .1, 0., 1.);
    c *= mix(1., .88 + .24 * fine, grain); c *= mix(1., .94 + .12 * fibre, grain);
  }
  o = vec4(c, 1.);
}`;

const STREAK = [[.012, .22], [.2, .014], [.035, .06], [.016, .3]];   // kit.STREAKS: the brush's direction

export class Look {
  constructor(canvas) {
    this.r = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: false, preserveDrawingBuffer: true });
    this.r.setPixelRatio(1); this.r.autoClear = true;
    this.scene = new THREE.Scene();
    this.cam = new THREE.PerspectiveCamera(20, 1, .5, 30);
    this.rt = null; this.pieces = []; this.nCard = 2; this.nFlat = 128;
    this.post = new THREE.RawShaderMaterial({
      glslVersion: THREE.GLSL3, depthTest: false, depthWrite: false,
      vertexShader: 'precision highp float; in vec3 position; void main() { gl_Position = vec4(position.xy, 0., 1.); }', fragmentShader: POST,
      uniforms: { tC: { value: null }, tI: { value: null }, res: { value: new THREE.Vector2() }, s: { value: 1 }, near: { value: 1 }, far: { value: 10 }, grain: { value: 1 }, shadowK: { value: 1 }, flatLook: { value: 0 }, bg: { value: new THREE.Color('#e3d3d6') }, hole: { value: new THREE.Vector2() } },
    });
    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.post); this.quad.frustumCulled = false;
    this.qscene = new THREE.Scene(); this.qscene.add(this.quad); this.qcam = new THREE.Camera();
  }
  // a piece of paper: {geo: {pos, idx, uv}, color, kind: 'card' | 'paint' | 'flat' | 'ground', v: brush direction 0..3, id?}
  // flat: glued flush — no shadow or rim of its own. Returns the three.js mesh (mesh.userData.piece = the piece).
  add(p) {
    const flat = p.kind === 'flat', ground = p.kind === 'ground';
    const id = p.id ?? (ground ? 1 : flat ? this.nFlat++ : this.nCard++);
    if (this.nCard > 127 || this.nFlat > 255) throw new Error('too many pieces');
    const g = new THREE.BufferGeometry();
    const mat = new THREE.RawShaderMaterial({
      glslVersion: THREE.GLSL3, vertexShader: VERT, fragmentShader: FRAG, side: THREE.DoubleSide,
      uniforms: { color: { value: new THREE.Color(p.color) }, id: { value: id }, paint: { value: p.kind === 'paint' || p.paint ? 1 : 0 }, near: { value: 1 }, far: { value: 10 },
        freq: { value: new THREE.Vector2(...STREAK[(p.v ?? 0) % 4]) }, seed: { value: (p.seed ?? id) * 3.7 }, curlR: { value: 0 }, curlC: { value: new THREE.Vector2() } },
    });
    const m = new THREE.Mesh(g, mat); m.frustumCulled = false; m.matrixAutoUpdate = false; m.userData.piece = p; p.id = id; p.mesh = m;
    if (p.geo) this.setGeo(m, p.geo);
    (p.parent || this.scene).add(m); this.pieces.push(p);
    return m;
  }
  setGeo(m, geo) {
    const g = m.geometry;
    g.setAttribute('position', new THREE.BufferAttribute(Float32Array.from(geo.pos), 3));
    g.setAttribute('puv', new THREE.BufferAttribute(Float32Array.from(geo.uv), 2));
    g.setIndex(new THREE.BufferAttribute(Uint32Array.from(geo.idx), 1));
  }
  remove(p) { p.mesh.parent?.remove(p.mesh); p.mesh.geometry.dispose(); p.mesh.material.dispose(); this.pieces.splice(this.pieces.indexOf(p), 1); }
  resize(w, h) {
    if (this.w === w && this.h === h) return;
    this.w = w; this.h = h; this.r.setSize(w, h, false);
    this.rt?.dispose();
    this.rt = new THREE.WebGLMultipleRenderTargets(w * SS, h * SS, 2, { minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, depthBuffer: true });
    this.cam.aspect = w / h; this.cam.updateProjectionMatrix();
  }
  // view: {pos, target, fov}; o: {bg, grain, shadowK, flat}
  draw(view, o = {}) {
    const c = this.cam;
    c.fov = view.fov; c.position.set(...view.pos); c.up.set(0, 1, 0); c.lookAt(...view.target);
    const dist = c.position.distanceTo(new THREE.Vector3(...view.target));
    c.near = Math.max(.2, dist - 4); c.far = dist + 6; c.updateProjectionMatrix(); c.updateMatrixWorld();
    for (const p of this.pieces) { const u = p.mesh.material.uniforms; u.near.value = c.near; u.far.value = c.far; }
    this.r.setRenderTarget(this.rt); this.r.setClearColor(0x00ffff, 1); this.r.clear();
    this.r.render(this.scene, c);
    const u = this.post.uniforms;
    u.tC.value = this.rt.texture[0]; u.tI.value = this.rt.texture[1]; u.res.value.set(this.w, this.h);
    u.near.value = c.near; u.far.value = c.far;
    // how many pixels one unit of the drawing takes where the figure stands
    this.pxPerUnit = this.h / (2 * Math.tan(view.fov * Math.PI / 360)) / dist * U;
    u.s.value = this.pxPerUnit; u.grain.value = o.grain ?? 1; u.shadowK.value = o.shadowK ?? 1; u.flatLook.value = o.flat ? 1 : 0;
    u.bg.value.set(o.bg || '#e3d3d6');
    this.r.setRenderTarget(null); this.r.render(this.qscene, this.qcam);
  }
}
