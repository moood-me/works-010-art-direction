// The look and the stage of the rubber-hose characters (style С11), shared by the character's own file: flat paint
// with a faint second tone and a hard shine, painted marks from a canvas (the head's face by a straight projection
// from the front; clothes by their own (u, v)), an ink hull, and the film pass (ink wobble, grain, vignette,
// black-and-white). Taken from Р11 (to3d/r11-s11-savely/tools/web/savely.js) and made independent of the character.
import * as THREE from 'three';
import { createEngine } from '../../../../engine/src/engine.js';
const V3 = THREE.Vector3;
export const INK_HEX = '#1b1714';
const C = { ink: INK_HEX };
const raw0 = h => { const c = new THREE.Color(); c.setStyle(h, THREE.LinearSRGBColorSpace); return c.toArray(); };
// ———————————————————— the look: flat paint, a second tone, a shine, painted marks; an ink hull ————————————————————
const VS = `
attribute vec3 rp;
varying vec3 vN; varying vec3 vRp; varying vec3 vCol;
void main() {
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  vN = normalize(normalMatrix * normal); vRp = rp;
#ifdef VCOL
  vCol = color;
#else
  vCol = vec3(1.0);
#endif
  gl_Position = projectionMatrix * mv;
}`;
const FS = `
uniform vec3 uColor; uniform float uShade, uShine, uPaint, uBW; uniform sampler2D uMap; uniform vec4 uMapBox;
varying vec3 vN; varying vec3 vRp; varying vec3 vCol;
const vec3 INK = vec3(${raw0(C.ink).map(v => v.toFixed(4)).join(',')});
float seg(vec2 p, vec2 a, vec2 b) { vec2 pa = p - a, ba = b - a; float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0); return length(pa - ba * h); }
vec3 srgb(vec3 c) { return c; }
void main() {
  vec3 c = uColor * vCol;
  vec2 p = vRp.xy;
  if (uPaint > 3.5) {                                           // clothes: a canvas by the form's own (u, v)
    c = texture2D(uMap, p).rgb;
  } else if (uPaint > 2.5) {                                    // the head: the painted face, from the front
    vec2 uv = vec2((p.x - uMapBox.x) / (uMapBox.y - uMapBox.x), 1.0 - (p.y - uMapBox.z) / (uMapBox.w - uMapBox.z));
    vec4 f = texture2D(uMap, uv);
    float k = smoothstep(4.0, 16.0, vRp.z);
    c = mix(c, f.rgb, f.a * k);
  }
  vec3 n = normalize(vN);
  float lam = dot(n, normalize(vec3(-0.45, 0.6, 0.65)));
  c *= mix(1.0 - uShade, 1.0, smoothstep(-0.05, 0.05, lam));
  if (uShine > 0.0) { float s = dot(n, normalize(vec3(-0.5, 0.62, 0.6))); if (s > 1.0 - uShine) c = mix(c, vec3(1.0), 0.72); }
  gl_FragColor = vec4(c, 1.0);
}`;
const HVS = `
uniform float uLine;
void main() { gl_Position = projectionMatrix * modelViewMatrix * vec4(position + normal * uLine, 1.0); }`;
const HFS = `void main() { gl_FragColor = vec4(${raw0(C.ink).map(v => v.toFixed(4)).join(',')}, 1.0); }`;

export function paintMat(color, o = {}) {
  const m = new THREE.ShaderMaterial({
    vertexShader: VS, fragmentShader: FS, defines: o.vc ? { VCOL: 1 } : {}, vertexColors: !!o.vc,
    uniforms: { uColor: { value: raw(color) }, uShade: { value: o.shade ?? 0.1 }, uShine: { value: o.shine ?? 0 }, uPaint: { value: o.paint ?? 0 },
      uBW: { value: 0 }, uMap: { value: o.map || null }, uMapBox: { value: o.box || new THREE.Vector4(-96, 96, -96, 100) } },
  });
  return m;
}
export const raw = h => { const c = new THREE.Color(); c.setStyle(h, THREE.LinearSRGBColorSpace); return c; };   // paints as written: the shaders work in the drawing's sRGB numbers
export const hullMat = line => new THREE.ShaderMaterial({ vertexShader: HVS, fragmentShader: HFS, side: THREE.BackSide, uniforms: { uLine: { value: line } } });

// a part: a mesh in its paint, and its ink hull sharing the geometry
export class Part {
  constructor(parent, mat, line, geo = new THREE.BufferGeometry()) {
    this.mesh = new THREE.Mesh(geo, mat); this.hull = new THREE.Mesh(geo, line > 0 ? hullMat(line) : null);
    this.mesh.frustumCulled = this.hull.frustumCulled = false;
    parent.add(this.mesh); if (line > 0) parent.add(this.hull);
  }
  set(geo) {
    if (!geo.attributes.rp) geo.setAttribute('rp', new THREE.Float32BufferAttribute(new Float32Array(geo.attributes.position.count * 3), 3));
    const old = this.mesh.geometry; this.mesh.geometry = this.hull.geometry = geo; old.dispose();
  }
}
// ———————————————————— the stage: camera, the film look ————————————————————
const POST_VS = `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`;
const POST_FS = `
uniform sampler2D tCol, tNoise; uniform vec2 uRes; uniform float uWob, uGrain, uVig, uBW, uSeed;
varying vec2 vUv;
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233)) + uSeed * 0.37) * 43758.5453); }
void main() {
  float k = uRes.y / 900.0;                                       // the drawing's sheets are 900 px tall
  vec2 n = texture2D(tNoise, vUv * uRes / (28.0 * k * 64.0) + vec2(uSeed * 0.131, uSeed * 0.071)).rg - 0.5;
  vec2 uv = vUv + n * uWob * k / uRes;
  vec3 c = texture2D(tCol, uv).rgb;
  float g = hash(floor(vUv * uRes / max(1.0, k)));
  c *= 1.0 - uGrain * (g - 0.5);
  vec2 q = vUv - vec2(0.5, 0.52); q.x *= uRes.x / uRes.y;
  float v = smoothstep(0.42, 0.95, length(q) / 0.72);
  c = mix(c, vec3(0.165, 0.114, 0.063), v * uVig);
  if (uBW > 0.5) { float l = dot(c, vec3(0.30, 0.55, 0.15)); l = 1.12 * pow(l, 0.8) - 0.04; c = vec3(l); c = mix(c, vec3(0.0), v * 0.35); }
  gl_FragColor = vec4(c, 1.0);
}`;

export async function createStage(canvas, o = {}) {   // o.body: the engine body whose joint frames are used; o.make(E, body) → the character
  const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
  const old = await E.body(o.body);
  const ch = o.make(E, old);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(o.pixelRatio || Math.min(2, devicePixelRatio));
  renderer.outputColorSpace = THREE.LinearSRGBColorSpace;   // no conversions: every shader here writes the drawing's own numbers
  const scene = new THREE.Scene(); scene.background = new THREE.Color().setStyle('#efe2c4', THREE.LinearSRGBColorSpace);
  scene.add(ch.root); scene.add(ch.shadow);
  const persp = new THREE.PerspectiveCamera(24, 1, 0.05, 60), ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.05, 60);
  // the film: a target, then the pass that wobbles the ink, adds grain and darkens the corners
  const rt = new THREE.WebGLRenderTarget(4, 4, { samples: 4, type: THREE.UnsignedByteType });
  const nz = new Uint8Array(64 * 64 * 4); for (let i = 0; i < nz.length; i++) nz[i] = Math.random() * 255;
  const noise = new THREE.DataTexture(nz, 64, 64); noise.wrapS = noise.wrapT = THREE.RepeatWrapping; noise.magFilter = noise.minFilter = THREE.LinearFilter; noise.needsUpdate = true;
  const post = new THREE.ShaderMaterial({ vertexShader: POST_VS, fragmentShader: POST_FS, uniforms: { tCol: { value: rt.texture }, tNoise: { value: noise }, uRes: { value: new THREE.Vector2() }, uWob: { value: 2.4 }, uGrain: { value: 0.12 }, uVig: { value: 0.42 }, uBW: { value: 0 }, uSeed: { value: 0 } } });
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), post), qscene = new THREE.Scene(); qscene.add(quad); const qcam = new THREE.Camera();
  const st = {
    THREE, E, ch, renderer, scene, persp, ortho, post,
    cam: { mode: 'persp', yaw: 25, pitch: 6, dist: 4.2, target: new V3(0, 0.75, 0), fov: 24, ortho: { h: 2, cx: 0, cy: 0.8 }, follow: false, pad: 0 },
    film: true, seed: 0,
    size(w, h) { renderer.setSize(w, h, false); const pr = renderer.getPixelRatio(); rt.setSize(w * pr, h * pr); post.uniforms.uRes.value.set(w * pr, h * pr); this.w = w; this.h = h; },
    camera() {
      const c = this.cam, yaw = c.yaw * Math.PI / 180, pit = c.pitch * Math.PI / 180;
      const dir = new V3(Math.sin(yaw) * Math.cos(pit), Math.sin(pit), Math.cos(yaw) * Math.cos(pit));
      if (c.mode === 'ortho') {
        const a = this.w / this.h, hh = c.ortho.h / 2; Object.assign(ortho, { left: -hh * a, right: hh * a, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
        const right = new V3(Math.cos(yaw), 0, -Math.sin(yaw)), t = c.target.clone().addScaledVector(right, -(c.ortho.dx || 0)); ortho.position.copy(t).addScaledVector(dir, 20); ortho.up.set(0, 1, 0); ortho.lookAt(t);
        // shift the view so the target sits at (cx, cy) of the frame (frame units: world)
        ortho.updateMatrixWorld(); return ortho;
      }
      persp.fov = c.fov; persp.aspect = this.w / this.h;
      persp.setViewOffset(this.w, this.h + c.pad, 0, c.pad, this.w, this.h); persp.updateProjectionMatrix();
      persp.position.copy(c.target).addScaledVector(dir, c.dist); persp.lookAt(c.target); return persp;
    },
    render() {
      const cam = this.camera();
      if (this.film) {
        renderer.setRenderTarget(rt); renderer.render(scene, cam); renderer.setRenderTarget(null);
        post.uniforms.uSeed.value = this.seed; renderer.render(qscene, qcam);
      } else { renderer.setRenderTarget(null); renderer.render(scene, cam); }
    },
  };
  return st;
}
