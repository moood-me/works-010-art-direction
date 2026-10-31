// Hair shading, shared by the hair page's still and moving views.
// ———— hair shading: strands along each lock, an anisotropic highlight band, darker roots and inner layers ————
export const HAIR_V = `
attribute vec3 hairT; attribute vec2 hairUV; attribute float seed; attribute float ao; attribute vec3 color;
varying vec3 vN; varying vec3 vT; varying vec3 vP; varying vec2 vUV; varying float vSeed; varying float vAO; varying vec3 vCol;
void main() {
  vec4 wp = modelMatrix * vec4(position, 1.0); vP = wp.xyz;
  vN = normalize(mat3(modelMatrix) * normal); vT = normalize(mat3(modelMatrix) * hairT);
  vUV = hairUV; vSeed = seed; vAO = ao; vCol = color;
  gl_Position = projectionMatrix * viewMatrix * wp;
}`;
export const HAIR_F = `
uniform vec3 keyDir; uniform vec3 keyCol; uniform vec3 rimDir; uniform vec3 rimCol; uniform vec3 sky; uniform vec3 ground;
uniform float inner; uniform float spec1; uniform float spec2; uniform float shift; uniform float strands;
varying vec3 vN; varying vec3 vT; varying vec3 vP; varying vec2 vUV; varying float vSeed; varying float vAO; varying vec3 vCol;
float h1(float x) { return fract(sin(x * 127.1) * 43758.5453); }
float n1(float x) { float i = floor(x), f = fract(x); f = f * f * (3.0 - 2.0 * f); return mix(h1(i), h1(i + 1.0), f); }
float kk(vec3 T, vec3 H, float e) { float t = dot(T, H); return pow(max(0.0, sqrt(max(0.0, 1.0 - t * t))), e); }
void main() {
  vec3 N = normalize(vN); if (!gl_FrontFacing) N = -N;
  vec3 T = vT - N * dot(vT, N); T = length(T) > 1e-4 ? normalize(T) : vec3(0.0, -1.0, 0.0);
  vec3 V = normalize(cameraPosition - vP);
  float a = vUV.x, s = vUV.y;
  // strands: fine lines across the lock, coarser bundles, both running along it
  // each scale fades to its mean where it would be finer than a pixel
  float fw = fwidth(a) + 1e-6;
  float fine = mix(n1(a * 1400.0 + vSeed * 91.0 + s * 2.0), 0.5, clamp(fw * 1400.0 - 1.0, 0.0, 1.0));
  float mid = mix(n1(a * 520.0 + vSeed * 37.0 + s * 1.2), 0.5, clamp(fw * 520.0 - 1.0, 0.0, 1.0));
  float big = mix(n1(a * 160.0 + vSeed * 13.0), 0.5, clamp(fw * 160.0 - 1.0, 0.0, 1.0));
  float str = mix(0.5, fine * 0.5 + mid * 0.35 + big * 0.15, strands * (inner < 0.99 ? 0.5 : 1.0));
  vec3 alb = vCol * mix(0.5, 1.0, smoothstep(0.0, 0.4, s)) * (0.88 + 0.24 * str) * (0.9 + 0.2 * h1(vSeed * 71.0 + 3.0)) * mix(inner, 1.0, smoothstep(0.55, 0.95, vAO));
  float ao = vAO;
  vec3 irr = mix(ground, sky, 0.5 * N.y + 0.5) * mix(0.45, 1.0, ao);
  float nl = dot(N, keyDir);
  irr += keyCol * clamp((nl + 0.25) / 1.25, 0.0, 1.0) * mix(0.55, 1.0, ao);
  irr += rimCol * clamp(dot(N, rimDir), 0.0, 1.0) * ao;
  vec3 col = alb * irr / 3.14159;
  // the highlight band: two lobes along the strands (Kajiya-Kay), the second tinted and broken by the strands
  vec3 H = normalize(keyDir + V);
  float sh = (str - 0.5) * 0.5;
  float b1 = kk(normalize(T + N * (shift + sh)), H, 90.0);
  float b2 = kk(normalize(T + N * (shift - 0.22 + sh)), H, 22.0) * smoothstep(0.35, 0.75, mid);
  float lit = smoothstep(-0.05, 0.35, nl) * ao * ao;
  vec3 tint = mix(vec3(1.0), vCol / max(max(vCol.r, vCol.g), max(vCol.b, 0.02)), 0.45);
  col += keyCol * (b1 * spec1 * tint * (0.5 + 0.9 * fine) * 0.1 + b2 * spec2 * vCol * 0.5) * lit * inner;
  vec3 Hr = normalize(rimDir + V);
  col += rimCol * kk(normalize(T + N * (shift + sh)), Hr, 60.0) * spec1 * 0.05 * tint * clamp(dot(N, rimDir) + 0.3, 0.0, 1.0) * ao * inner;
  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;
const L3 = (THREE, v) => new THREE.Vector3(...v).normalize();
// S: the hairstyle; o.inner: the inner layer (darker); strands: 0 to leave the strand lines out
export function hairMaterial(THREE, S, o, strands = 1) {
  return new THREE.ShaderMaterial({ vertexShader: HAIR_V, fragmentShader: HAIR_F, side: THREE.DoubleSide, uniforms: {
    keyDir: { value: L3(THREE, [1.2, 2.2, 2.4]) }, keyCol: { value: new THREE.Color(0xffffff).multiplyScalar(2.1) },
    rimDir: { value: L3(THREE, [-1.6, 1.4, -2.0]) }, rimCol: { value: new THREE.Color(0xdfe8ff).multiplyScalar(1.1) },
    sky: { value: new THREE.Color(0xfff6ea).multiplyScalar(1.25) }, ground: { value: new THREE.Color(0x6d6070).multiplyScalar(1.25) },
    inner: { value: o.inner ? (S.innerDark ?? 0.8) : 1 }, spec1: { value: S.spec ?? 1 }, spec2: { value: S.spec2 ?? 0.6 },
    shift: { value: S.shift ?? 0.12 }, strands: { value: strands } } });
}
// the ink outline of a moving surface: its back faces pushed out along the normal by each point's own width (`inkw`)
export function inkMaterial(THREE, color = 0x24161a) {
  return new THREE.ShaderMaterial({ side: THREE.BackSide, uniforms: { ink: { value: new THREE.Color(color) } },
    vertexShader: `attribute float inkw; varying float vk; void main() { vk = inkw; gl_Position = projectionMatrix * modelViewMatrix * vec4(position + normal * inkw, 1.0); }`,
    // (where the width has gone to nothing, no outline: it would only fight with the surface)
    fragmentShader: `uniform vec3 ink; varying float vk; void main() { if (vk < 1.5e-4) discard; gl_FragColor = vec4(ink, 1.0); }` });
}
