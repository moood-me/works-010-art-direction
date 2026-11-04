// How hair takes the light (three.js passed in: src/view3d.js draws a mesh with `hair` by it). В1's hair shading
// (experiments/hair/shade.js), with the stage's own lights: the strand direction from each lock, fine and coarse
// strands that gather towards the tip, darker roots, an occlusion term baked from the hair's own volume (grooves and
// inner layers dark), the diffuse light taken partly along the strands (a strand lit from its side, Kajiya-Kay: so a
// lock reads as many strands, not as a smooth body), a two-lobe highlight band along the strands — the first narrow and
// near white, shifted toward the tip, the second broader, tinted by the hair and broken by the strands —, light
// coming through the thin edges against the light, and the colour richer where the light is weaker.
//   hairMaterial(THREE, hair, {inner}) — hair: the mesh's `hair` (shading: spec, spec2, shift, inner, strands)
//   hairInk(THREE, width) — the outline: back faces pushed out by each point's own width (thinner where a lock thins)
export function hairMaterial(THREE, hair) {
  const s = hair.shading, inner = hair.layer === 'inner';
  const m = new THREE.ShaderMaterial({
    lights: true, side: THREE.DoubleSide,
    uniforms: THREE.UniformsUtils.merge([THREE.UniformsLib.lights, {
      inner: { value: inner ? s.inner : 1 }, spec1: { value: s.spec }, spec2: { value: s.spec2 }, shift: { value: s.shift }, strands: { value: s.strands * (inner ? 0.5 : 1) },
    }]),
    vertexShader: `
attribute vec3 hairT; attribute vec2 hairUV; attribute float seed; attribute float ao; attribute vec3 color;
varying vec3 vN; varying vec3 vT; varying vec3 vP; varying vec2 vUV; varying float vSeed; varying float vAO; varying vec3 vCol;
void main() {
  vec4 wp = modelMatrix * vec4(position, 1.0); vP = wp.xyz;
  vN = normalize(mat3(modelMatrix) * normal); vT = normalize(mat3(modelMatrix) * hairT);
  vUV = hairUV; vSeed = seed; vAO = ao; vCol = color;
  gl_Position = projectionMatrix * viewMatrix * wp;
}`,
    fragmentShader: `
#include <common>
#include <lights_pars_begin>
uniform float inner; uniform float spec1; uniform float spec2; uniform float shift; uniform float strands;
varying vec3 vN; varying vec3 vT; varying vec3 vP; varying vec2 vUV; varying float vSeed; varying float vAO; varying vec3 vCol;
float h1(float x) { return fract(sin(x * 127.1) * 43758.5453); }
float n1(float x) { float i = floor(x), f = fract(x); f = f * f * (3.0 - 2.0 * f); return mix(h1(i), h1(i + 1.0), f); }
// a strand's highlight: how near the half vector lies to the plane across the strand
float kk(vec3 T, vec3 H, float e) { float t = dot(T, H); return pow(max(0.0, sqrt(max(0.0, 1.0 - t * t))), e); }
void main() {
  vec3 N = normalize(vN); if (!gl_FrontFacing) N = -N;
  vec3 T = vT - N * dot(vT, N); T = length(T) > 1e-4 ? normalize(T) : vec3(0.0, -1.0, 0.0);
  vec3 V = normalize(cameraPosition - vP);
  float a = vUV.x, s = vUV.y;
  // strands: fine lines across the lock, coarser bundles, both running along it, gathering toward the tip; each scale
  // fades to its mean where it would be finer than a pixel
  float fw = fwidth(a) + 1e-6, g = a * (1.0 + 0.6 * s);
  float fine = mix(n1(g * 1400.0 + vSeed * 91.0 + s * 2.0), 0.5, clamp(fw * 1400.0 - 1.0, 0.0, 1.0));
  float mid = mix(n1(g * 520.0 + vSeed * 37.0 + s * 1.2), 0.5, clamp(fw * 520.0 - 1.0, 0.0, 1.0));
  float big = mix(n1(g * 140.0 + vSeed * 13.0), 0.5, clamp(fw * 140.0 - 1.0, 0.0, 1.0));
  float str = mix(0.5, fine * 0.45 + mid * 0.35 + big * 0.2, strands);
  float ao = vAO, deep = smoothstep(0.35, 0.95, ao);
  // the colour: darker at the root and inside, each lock its own shade, the strands' value broken
  vec3 alb = vCol * mix(0.55, 1.0, smoothstep(0.0, 0.45, s)) * (0.8 + 0.4 * str) * (0.88 + 0.24 * h1(vSeed * 71.0 + 3.0)) * mix(inner, 1.0, deep);
  // where little light reaches, the colour is richer (light scattered through hair takes its colour)
  vec3 rich = pow(max(alb, vec3(1e-4)), vec3(1.25)) * 1.25;
  vec3 col = vec3(0.0);
  vec3 irr = vec3(0.0);
  #if NUM_HEMI_LIGHTS > 0
  irr = mix(hemisphereLights[0].groundColor, hemisphereLights[0].skyColor, 0.5 * N.y + 0.5) * mix(0.35, 1.0, ao);
  #endif
  col += mix(rich, alb, ao) * irr / 3.14159 * 3.14159 * 0.32;
  float sh = (str - 0.5) * 0.6;
  vec3 tint = mix(vec3(1.0), vCol / max(max(vCol.r, vCol.g), max(vCol.b, 0.02)), 0.4);
  #pragma unroll_loop_start
  for (int i = 0; i < NUM_DIR_LIGHTS; i++) { {
    vec3 L = directionalLights[i].direction, C = directionalLights[i].color;
    float nl = dot(N, L), tl = dot(T, L);
    // diffuse: half the lock's own face, half a strand's side (Kajiya-Kay), wrapped a little
    float dif = mix(clamp((nl + 0.3) / 1.3, 0.0, 1.0), sqrt(max(0.0, 1.0 - tl * tl)) * clamp(nl + 0.6, 0.0, 1.0), 0.45);
    col += mix(rich, alb, smoothstep(0.0, 0.6, dif)) * C * dif * mix(0.5, 1.0, ao) / 3.14159 * 3.14159 * 0.36;
    // the two highlights along the strands
    vec3 H = normalize(L + V);
    float b1 = kk(normalize(T + N * (shift + sh)), H, 140.0);
    float b2 = kk(normalize(T + N * (shift - 0.24 + sh)), H, 26.0) * smoothstep(0.3, 0.75, mid);
    float lit = smoothstep(-0.1, 0.35, nl) * ao * ao;
    col += C * (b1 * spec1 * tint * (0.45 + 0.9 * fine) * 0.22 + b2 * spec2 * vCol * 0.55) * lit * inner;
    // light through the thin edges, against the light
    float back = pow(clamp(dot(-V, L), 0.0, 1.0), 4.0) * pow(1.0 - abs(dot(N, V)), 2.0);
    col += C * vCol * back * 0.35 * ao;
  } }
  #pragma unroll_loop_end
  gl_FragColor = vec4(col, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`,
  });
  return m;
}
export function hairInk(THREE, color = '#24161a') {
  const m = new THREE.ShaderMaterial({ side: THREE.BackSide, uniforms: { ink: { value: new THREE.Color(color) } },
    vertexShader: 'attribute float inkw; varying float vk; void main() { vk = inkw; gl_Position = projectionMatrix * modelViewMatrix * vec4(position + normal * inkw, 1.0); }',
    // (where the width has gone to nothing, no outline: it would only fight with the surface)
    fragmentShader: 'uniform vec3 ink; varying float vk; void main() { if (vk < 1.5e-4) discard; gl_FragColor = vec4(ink, 1.0); }' });
  m.toneMapped = false;
  return m;
}
