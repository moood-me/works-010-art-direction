// The look of С1 (Pixar / Disney 3D): soft light, warm skin that lets light through, modelled eyes with a big
// catchlight, hair clumps with a sheen, soft cast shadows and baked occlusion; no outline.
// One shader for every material (mat attribute), lit by a warm key from the upper left, a cool fill, a sky/ground
// ambient and a rim; the key casts a soft shadow (our own shadow pass); ACES-like tone map to sRGB.
import * as THREE from 'three';

const lin = h => { const c = new THREE.Color(h); return new THREE.Vector3(c.r, c.g, c.b); };

export const VS = `
attribute float mat; attribute vec3 pat; attribute vec4 aux; attribute float ao;
uniform mat4 shadowMat;
varying float vMat; varying vec3 vPat; varying vec4 vAux; varying float vAO; varying vec3 vN; varying vec3 vW; varying vec4 vS;
void main(){ vMat = mat; vPat = pat; vAux = aux; vAO = ao;
  vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; vN = normalize(mat3(modelMatrix) * normal);
  vS = shadowMat * w;
  gl_Position = projectionMatrix * viewMatrix * w; }`;

export const FS = `
precision highp float;
uniform vec3 base[16]; uniform sampler2D faceTex; uniform float hasFace; uniform sampler2D shadowTex; uniform float shadowOn;
uniform vec3 L; uniform vec3 keyCol; uniform vec3 fillDir; uniform vec3 fillCol; uniform vec3 sky; uniform vec3 ground;
uniform vec3 camPos; uniform float clay; uniform sampler2D clothTex; uniform float K; uniform float floorY; uniform vec3 irisCol; uniform float irisR; uniform vec3 lashCol;
uniform vec3 eyeL; uniform vec3 eyeR; uniform float pupil; uniform vec3 hairLight; uniform vec3 hairDark; uniform float exposure;
varying float vMat; varying vec3 vPat; varying vec4 vAux; varying float vAO; varying vec3 vN; varying vec3 vW; varying vec4 vS;
float h1(float n){ return fract(sin(n) * 43758.5453); }
float shadowAt(){
  if (shadowOn < 0.5) return 1.0;
  vec3 p = vS.xyz / vS.w * 0.5 + 0.5;
  if (p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0) return 1.0;
  float s = 0.0; float r = 1.6 / 2048.0;
  for (int i = -2; i <= 2; i++) for (int j = -2; j <= 2; j++) {
    float d = texture2D(shadowTex, p.xy + vec2(float(i), float(j)) * r).r;
    s += (p.z - 0.0025 > d) ? 0.0 : 1.0; }
  return s / 25.0;
}
vec3 aces(vec3 x){ return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0); }
void main(){
  int m = int(vMat + 0.5);
  vec3 alb = base[0];
  for (int i = 0; i < 16; i++) if (i == m) alb = base[i];
  // skin → lip → the mouth's inside (mats 0, 1, 2) blend continuously across their triangles
  if (vMat < 2.2) { float u = clamp(vMat, 0.0, 2.0); alb = u < 1.0 ? mix(base[0], base[1], smoothstep(0.55, 1.0, u)) : mix(base[1], base[2], smoothstep(1.0, 1.12, u)); m = vMat < 1.4 ? 0 : 2; }
  vec3 n = normalize(vN); if (!gl_FrontFacing) n = -n;
  vec3 v = normalize(camPos - vW);
  if (clay > 0.5) { float k = 0.3 + 0.7 * max(dot(n, L), 0.0); gl_FragColor = vec4(pow(vec3(0.8, 0.78, 0.74) * k * (1.0 - 0.6 * vAO), vec3(1.0/2.2)), 1.0); return; }
  float rough = 0.6, specK = 0.04, wrap = 0.0; vec3 sss = vec3(0.0);
  bool skin = (m == 0 || m == 1);
  if (skin) { rough = 0.45; specK = 0.035; sss = vec3(0.5, 0.18, 0.1); }
  // the coat: its belt all round, and on its front the drawing's layer (lapels, the turtleneck's wedge, buttons, seam)
  if (m == 5) {
    if (vAux.y > 226.0 && vAux.y < 238.0) alb *= 0.86;
    vec4 f = texture2D(clothTex, vec2((vAux.x + 64.0) / 128.0, (vAux.y - 60.0) / 440.0)); alb = mix(alb, f.rgb, f.a * smoothstep(0.05, 0.3, vAux.z));
  }
  if (m == 8) { rough = 0.3; specK = 0.08; }
  float lash = 0.0;
  if (m == 0 || m == 1) {
    lash = smoothstep(0.32, 0.68, vAux.w);
    if (hasFace > 0.5 && vAux.z > 0.02) { vec4 f = texture2D(faceTex, vAux.xy); alb = mix(alb, f.rgb, f.a * smoothstep(0.02, 0.25, vAux.z)); }
    alb = mix(alb, lashCol, lash);
  }
  // hair: clumps darker at their roots and edges, lighter along their middle
  if (m == 4 || m == 12) {
    float along = vAux.x, across = abs(vAux.y);
    if (vAux.z < -0.5) {
      // the sleek cap and the bun: fine strands along the combing (aux.y counts them round the bun), darker toward the bun
      float st = vAux.y * (vAux.z < -1.5 ? 46.0 : 150.0);
      float a = h1(floor(st)), b = h1(floor(st) + 1.0), fr = fract(st);
      alb *= 0.86 + 0.26 * mix(a, b, fr * fr * (3.0 - 2.0 * fr));
      alb = mix(alb, hairDark, 0.35 * (1.0 - smoothstep(0.0, 0.3, along)));
    } else { alb = mix(alb, hairDark, 0.55 * smoothstep(0.55, 1.0, across) + 0.35 * (1.0 - smoothstep(0.0, 0.35, along)));
      alb = mix(alb, hairLight, 0.18 * (1.0 - across) * smoothstep(0.2, 0.7, along) * vAux.w);
      float str = h1(floor(vAux.y * 9.0 + vAux.z * 13.0)); alb *= 0.9 + 0.2 * str; }
    rough = vAux.z < -0.5 ? 0.56 : 0.34; specK = vAux.z < -0.5 ? 0.035 : 0.07;
  }
  // the eye: sclera, iris (procedural on the ball's own direction), pupil
  float eyeSpec = 0.0;
  if (m == 3) {
    vec3 d = normalize(vAux.xyz); float r = length(d.xy) * sign(d.z) + (d.z < 0.0 ? 2.0 : 0.0);
    float IR = irisR, PR = 0.4 * irisR * pupil;
    vec3 sclera = vec3(0.93, 0.9, 0.88);
    float ang = atan(d.y, d.x);
    float rays = 0.5 + 0.5 * sin(ang * 23.0 + sin(ang * 7.0) * 2.0) * 0.6 + 0.2 * sin(ang * 51.0);
    vec3 irisC = irisCol;
    vec3 iris = mix(irisC * 0.5, irisC * 1.25, smoothstep(0.9, 0.35, r / IR) * (0.6 + 0.4 * rays));
    // the light pools in the iris on the side away from the light (a concave iris under a clear cornea)
    iris += (irisC * 0.5 + vec3(0.06)) * smoothstep(0.0, 1.0, -d.y * 2.0 + 0.2) * smoothstep(IR, PR, r) * 0.9;
    iris = mix(iris, irisC * 0.18, smoothstep(IR * 0.86, IR, r));      // the dark ring
    vec3 c = mix(sclera, iris, 1.0 - smoothstep(IR - 0.012, IR + 0.012, r));
    c = mix(vec3(0.015, 0.01, 0.01), c, smoothstep(PR - 0.01, PR + 0.01, r));
    // the white darker toward its edges and corners
    c *= mix(1.0, 0.72, smoothstep(0.55, 1.0, r) * step(IR, r));
    alb = c; rough = 0.08; specK = 0.0; eyeSpec = 1.0;
  }
  if (m == 2) alb *= 0.35 + 0.5 * (1.0 - vAO);          // the mouth's inside goes dark
  if (m == 11) { alb = vec3(0.88, 0.85, 0.78); }
  float sh = shadowAt();
  float NL = dot(n, L);
  // key: wrapped, with the skin's red terminator (light that went under the skin)
  vec3 dif;
  if (skin) {
    vec3 w3 = vec3(0.42, 0.22, 0.16);
    dif = clamp((vec3(NL) + w3) / (1.0 + w3), 0.0, 1.0);
    dif = dif * dif * (3.0 - 2.0 * dif) * 0.6 + dif * 0.4;
    vec3 shTint = mix(vec3(0.62, 0.36, 0.3), vec3(1.0), sh);
    dif *= shTint * mix(0.35, 1.0, sh);
  } else {
    float w = (m == 4 || m == 12) ? 0.25 : 0.12;
    float d = clamp((NL + w) / (1.0 + w), 0.0, 1.0);
    dif = vec3(d * mix(0.22, 1.0, sh));
  }
  vec3 col = alb * keyCol * dif;
  // fill and ambient (occluded)
  float occ = 1.0 - vAO * (m == 11 ? 0.45 : 0.85);
  float NF = clamp((dot(n, fillDir) + 0.3) / 1.3, 0.0, 1.0);
  col += alb * fillCol * NF * occ;
  col += alb * mix(ground, sky, n.y * 0.5 + 0.5) * occ;
  if (skin) col += alb * sss * 0.18 * occ;
  // specular (key) and rim
  vec3 hv = normalize(L + v);
  float NH = max(dot(n, hv), 0.0);
  float fres = pow(1.0 - max(dot(n, v), 0.0), 5.0);
  float e = 2.0 / (rough * rough * rough * rough) - 2.0;
  col += keyCol * (specK + (1.0 - specK) * fres * 0.25) * pow(NH, e) * (e + 2.0) / 8.0 * max(NL, 0.0) * sh * (1.0 - lash);
  if (eyeSpec > 0.5) {
    // the catchlights: the key's sharp one and a small soft one opposite; the wet surface reflects the sky a little
    col += vec3(1.0) * pow(NH, 900.0) * 9.0 * sh;
    vec3 h2 = normalize(normalize(vec3(-L.x, L.y * 0.2, L.z)) + v);
    col += vec3(0.8) * pow(max(dot(n, h2), 0.0), 600.0) * 1.6;
    col += sky * fres * 0.6;
  }
  float rim = pow(1.0 - max(dot(n, v), 0.0), 3.0) * clamp(dot(n, -L) * 0.5 + 0.6, 0.0, 1.0);
  col += (skin ? vec3(1.0, 0.75, 0.6) : vec3(0.75, 0.82, 1.0)) * rim * 0.22 * occ;
  col *= exposure;
  gl_FragColor = vec4(pow(aces(col), vec3(1.0 / 2.2)), 1.0);
}`;

export function makeMaterial(mats, h) {
  const PAINT = h.paint;
  const uniforms = {
    base: { value: Array.from({ length: 16 }, () => new THREE.Vector3()) }, faceTex: { value: null }, hasFace: { value: 0 },
    shadowTex: { value: null }, shadowOn: { value: 0 }, shadowMat: { value: new THREE.Matrix4() },
    L: { value: new THREE.Vector3(-0.5, 0.6, 0.62).normalize() }, keyCol: { value: new THREE.Vector3(1.0, 0.93, 0.84).multiplyScalar(1.85) },
    fillDir: { value: new THREE.Vector3(0.7, 0.1, 0.5).normalize() }, fillCol: { value: new THREE.Vector3(0.42, 0.5, 0.66).multiplyScalar(0.55) },
    sky: { value: new THREE.Vector3(0.5, 0.58, 0.72).multiplyScalar(0.45) }, ground: { value: new THREE.Vector3(0.5, 0.42, 0.36).multiplyScalar(0.35) },
    camPos: { value: new THREE.Vector3() }, clay: { value: 0 }, clothTex: { value: null }, irisCol: { value: lin(h.iris.col) }, irisR: { value: h.iris.r }, lashCol: { value: lin(h.lash).multiplyScalar(0.6) },
    K: { value: 0.0028 }, floorY: { value: 0 }, eyeL: { value: new THREE.Vector3() }, eyeR: { value: new THREE.Vector3() },
    hairLight: { value: lin(h.hair.light) }, hairDark: { value: lin(h.hair.dark) }, exposure: { value: 1.0 }, pupil: { value: 1.0 },
  };
  mats.forEach((m, i) => { const c = new THREE.Color(PAINT[m] || '#ff00ff'); uniforms.base.value[i].set(c.r, c.g, c.b); });
  return new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, uniforms, side: THREE.DoubleSide });
}

// the key light's shadow: depth seen from the light into a texture, sampled with a 5×5 filter
export class KeyShadow {
  constructor(renderer, size = 2048) {
    this.rt = new THREE.WebGLRenderTarget(size, size, { type: THREE.FloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
    this.cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 20);
    this.mat = new THREE.ShaderMaterial({
      // the glasses' thin rims (material 8) cast no shadow: on the face it reads as lines
      vertexShader: 'attribute float mat; varying float vMat; void main(){ vMat = mat; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
      fragmentShader: 'varying float vMat; void main(){ if (abs(vMat - 8.0) < 0.5) discard; gl_FragColor = vec4(gl_FragCoord.z, 0.0, 0.0, 1.0); }', side: THREE.DoubleSide,
    });
    this.renderer = renderer;
  }
  // light dir L (toward the light), around centre c with half-size r
  render(scene, L, c, r, uniforms) {
    const cam = this.cam;
    cam.left = -r; cam.right = r; cam.top = r; cam.bottom = -r; cam.near = 0.01; cam.far = 8;
    cam.position.set(c.x + L.x * 4, c.y + L.y * 4, c.z + L.z * 4); cam.up.set(0, 1, 0); cam.lookAt(c); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const keep = scene.overrideMaterial, bg = scene.background;
    scene.overrideMaterial = this.mat; scene.background = null;
    const old = this.renderer.getRenderTarget();
    this.renderer.setRenderTarget(this.rt); this.renderer.setClearColor(0xffffff, 1); this.renderer.clear(); this.renderer.render(scene, cam);
    this.renderer.setRenderTarget(old); this.renderer.setClearColor(0x000000, 0); scene.overrideMaterial = keep; scene.background = bg;
    const m = new THREE.Matrix4().multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse);
    uniforms.shadowMat.value.copy(m); uniforms.shadowTex.value = this.rt.texture; uniforms.shadowOn.value = 1;
  }
}
