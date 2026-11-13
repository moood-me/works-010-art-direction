// Аня, нуар (С15) in 3D: the character pack (tools/build.py) on the engine's skeleton, skinning and Kimodo retargeting.
// The look is the drawing's: flat colour or black, nothing between. One hard key light from the picture's left.
//   · the head and the hair: the black shapes are designed, not shaded — the drawing's own edges of the side shadow
//     (head.py's `side_f`, the hair's zigzag in cast.py) are polylines in the head's frame; the light test is made on
//     a form whose side plane begins at that edge, so the terminator stands on the drawn line while the light moves,
//     and crosses the face only when the light goes far round; the jaw's cast shadow on the neck is the drawn shape;
//   · the body: the terminator of smooth shells (straight edges down the limbs) and real cast shadows (a shadow map,
//     hard): the head on the shoulders, the arm on the jacket, the skirt on the legs, the figure on the floor;
//   · no outline on the lit side; where black meets black or the night, a thin cool rim (an inverted hull drawn only
//     where the form is turned from the light);
//   · the face's eyes, brows, lips: drawn live on a canvas from the drawing's own parts (face.js), front projection.
// This is the page's fast variant (fast.html; view.html and anya.js beside it are the page as it was): the skin is
// skinned in the vertex shader (engine-gpu/src/gpuskin.js), the processor works out only the joints, the floor from a
// probe of the skin, and the skirt's points; the face's canvas is sent to the video card only when it changed.
//   fast.html — by hand (ui.js); fast.html?pack=<url> — driven by tools/shots.mjs
//   window.A.set({clip, t, time, pose, expr, exprTrack, talk, talkFrom, cam, …}) then A.render()
import * as THREE from 'three';
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { GpuSkin } from '../../../../engine-gpu/src/gpuskin.js';
import { qAxisAngle, qBetween, qRot, getQ, getV, normalize, sub } from '../../../../engine/src/math.js';
import { LiveFace, draw as drawFace, X0, X1, Y0, Y1, PX, EXPR_NAMES } from './face.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack') || '../../data/anya.json', location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const sk = E.skeleton;

// the pack as an engine body: positions, triangles, skin, joints and frames (SOMA's), nothing else asked of it
const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const rest = Float32Array.from(a.positions);
const spec = { skinning: { method: H.skinning || 'cor', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
const gs = new GpuSkin(THREE, fig.skinner);

// ---------------------------------------------------------------- the stage
const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const NIGHT = '#11121b';
scene.background = new THREE.Color(q.get('bg') || NIGHT);

const g = gs.attributes(new THREE.BufferGeometry());
g.setAttribute('col', new THREE.BufferAttribute(a.col, 3, true));
g.setAttribute('lin', new THREE.BufferAttribute(a.lin, 3, true));
g.setAttribute('ow', new THREE.BufferAttribute(a.ow, 1, true));
g.setAttribute('uv', new THREE.BufferAttribute(a.uv, 2));
g.setAttribute('tex', new THREE.BufferAttribute(a.tex, 1));
g.setAttribute('pn', new THREE.BufferAttribute(a.pn, 3));
g.setAttribute('pw', new THREE.BufferAttribute(a.pw, 1, true));
g.setAttribute('pj', new THREE.BufferAttribute(a.pj, 1));
g.setAttribute('two', new THREE.BufferAttribute(a.two, 1));
g.setAttribute('hp', new THREE.BufferAttribute(a.hp ?? new Float32Array(a.positions.length), 3));
g.setAttribute('kind', new THREE.BufferAttribute(a.kind ?? new Uint8Array(a.positions.length / 3), 1));
g.setIndex(new THREE.BufferAttribute(a.triangles, 1));

// the face's drawn layer: a canvas drawn every frame (face.js)
const faceCanvas = document.createElement('canvas');
faceCanvas.width = (X1 - X0) * PX; faceCanvas.height = (Y1 - Y0) * PX;
const faceCtx = faceCanvas.getContext('2d');
const faceTex = new THREE.CanvasTexture(faceCanvas);
faceTex.colorSpace = THREE.NoColorSpace; faceTex.anisotropy = 8;
faceTex.premultiplyAlpha = true;      // filtered premultiplied: no dark fringe where the painting ends
const face = new LiveFace(Number(q.get('seed') ?? 7));

// the key's shadow map: the figure seen from the light (hard cast shadows on the body and the floor)
const SM = 2048;
const shadowRT = new THREE.WebGLRenderTarget(SM, SM, { depthTexture: new THREE.DepthTexture(SM, SM, THREE.UnsignedIntType) });
shadowRT.depthTexture.minFilter = shadowRT.depthTexture.magFilter = THREE.NearestFilter;
const shadowCam = new THREE.OrthographicCamera(-1.5, 1.5, 1.5, -1.5, 0.5, 14);
const depthMat = new THREE.ShaderMaterial({ uniforms: gs.uniforms, side: THREE.DoubleSide,
  vertexShader: `${gs.glsl}
    void main() { vec3 P, N; skinVertex(P, N); gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0); }`,
  fragmentShader: `void main() { gl_FragColor = vec4(1.0); }` });

const BLACK = new THREE.Color('#07070b'), RIM = new THREE.Color('#3b4566');
const U = {
  L: { value: new THREE.Vector3(-0.6, 0.5, 0.6).normalize() },       // to the light, world
  Lh: { value: new THREE.Vector3(-0.6, 0.5, 0.6).normalize() },      // to the light, in the head's own frame
  thr: { value: Number(q.get('thr') ?? 0.1) },
  face: { value: faceTex }, smap: { value: shadowRT.depthTexture }, SMx: { value: new THREE.Matrix4() }, casts: { value: 1 },
  width: { value: Number(q.get('line') ?? 0.0042) },
  paint: { value: 1 }, clay: { value: 0 }, black: { value: BLACK }, rim: { value: RIM },
  R: { value: Array.from({ length: sk.J }, () => new THREE.Matrix3()) },
  ...gs.uniforms,
};
U.black.value.convertLinearToSRGB(); U.rim.value.convertLinearToSRGB();     // colours go out as written
// the drawn edges, head units: x of the edge at heights y (head.py head_f's side shadow for ANYA; the hair's shadow
// zigzag of cast.py anya_hair, front and back forms, one line from the crown to the ends; below the jaw the hair
// behind the neck is black from the middle on — the drawing's second shape there)
const poly = (name, pts) => `float ${name}(float y) { ${pts.slice(0, -1).map(([y0, x0], i) => { const [y1, x1] = pts[i + 1];
  return `if (y < ${y1.toFixed(1)}) return ${x0.toFixed(1)} + (clamp(y, ${y0.toFixed(1)}, ${y1.toFixed(1)}) - ${y0.toFixed(1)}) * ${((x1 - x0) / (y1 - y0)).toFixed(4)};`; }).join(' ')} return ${pts[pts.length - 1][1].toFixed(1)}; }`;
const EDGES = poly('faceEdge', [[-80, 47.6], [-14, 43.6], [34, 37.6], [56, 23.6], [84, 21], [98, 12.5]]) + '\n' +
  poly('hairEdge', [[-112, 40], [-82, 50], [-66, 42], [-58, 62], [-30, 56], [8, 80], [40, 40], [56, 34], [62, 2], [180, 2]]);
const LIGHT = `
    uniform vec3 L; uniform vec3 Lh; uniform float thr;
    ${EDGES}
    // the form the light is tested on, in the head's frame: flat towards the front inside the drawn edge, the side
    // plane beyond it (the picture's right when the light is on the left, and the other way round)
    vec3 designed(vec3 hp, vec3 pn, float xs, float front) {
      float sg = Lh.x < 0.0 ? 1.0 : -1.0, u = sg * hp.x / xs;
      float nx = 0.1 * u + 1.7 * smoothstep(0.93, 1.07, u) - 0.5 * smoothstep(0.93, 1.07, -u);
      vec3 n = normalize(vec3(sg * nx, pn.y, pn.z));
      return normalize(mix(pn, n, front));
    }
    float seg(vec2 p, vec2 a, vec2 b, out float t) { vec2 ab = b - a; t = clamp(dot(p - a, ab) / dot(ab, ab), 0.0, 1.0); return length(p - a - ab * t); }
    // 1 in the light, 0 in the black
    float lightAt(float kind, vec3 hp, vec3 pn, vec3 vn) {
      float d;
      if (kind > 1.5) {
        d = dot(designed(hp, pn, hairEdge(hp.y), 1.0), Lh) + 0.1;
        // away from the drawn edge the hair's terminator is cut in straight teeth, as the drawing cuts it
        d += 0.2 * (abs(fract(hp.y / 26.0 + hp.z / 55.0) - 0.5) * 2.0 - 0.5);
        // the hair's own black shapes of the drawing: the wedge at the parting, the fringe's underside along its edge
        if (hp.z > 0.0) {
          float t; float dp = seg(hp.xy, vec2(15.0, -108.0), vec2(25.0, -75.0), t);
          float df = min(seg(hp.xy, vec2(-10.0, -66.0), vec2(-45.0, -44.0), t), min(seg(hp.xy, vec2(-45.0, -44.0), vec2(-63.0, -13.0), t), seg(hp.xy, vec2(-63.0, -13.0), vec2(-74.0, 4.0), t)));
          float dp2 = seg(hp.xy, vec2(15.0, -108.0), vec2(25.0, -75.0), t);
          if (dp2 < 1.0 + 4.5 * (1.0 - abs(t - 0.45) / 0.55) || df < 5.0) d = -1.0;
        }
      }
      else if (kind > 0.5) {
        // under the jaw's line (the profile's: chin — jaw's angle — nape)
        float jaw = hp.z > 55.0 ? 100.0 : hp.z > -5.0 ? 70.0 + (hp.z + 5.0) * 0.5 : 70.0 + (hp.z + 5.0) * 0.69;
        if (hp.y > jaw + 2.0) {           // the neck: the jaw's cast shadow, as drawn
          float sg = Lh.x < 0.0 ? 1.0 : -1.0, x = sg * hp.x;
          float yl = x < -8.7 ? 107.0 + (x + 33.8) * 0.6 : 122.0 + (x + 8.7) * 0.73;
          d = (x < 5.5 && hp.y > yl && Lh.z > -0.1) ? dot(vn, L) : -1.0;
        } else d = dot(designed(hp, pn, faceEdge(hp.y), smoothstep(-22.0, 6.0, hp.z)), Lh) + 0.3;     // the face is the light's island: it goes black last
      } else d = dot(vn, L);
      float w = fwidth(d) * 0.7 + 1e-4;
      return smoothstep(thr - w, thr + w, d);
    }`;
const toon = new THREE.ShaderMaterial({
  uniforms: U,
  vertexShader: `
    attribute vec3 col; attribute float tex; attribute vec3 pn; attribute float pw; attribute float pj; attribute float two;
    attribute vec3 hp; attribute float kind;
    uniform mat3 R[${sk.J}]; uniform mat4 SMx;
    ${gs.glsl}
    varying vec3 vN; varying vec3 vCol; varying vec2 vUv; varying float vTex; varying float vTwo; varying vec3 vHp; varying vec3 vPn; varying float vKind; varying vec4 vS;
    void main() { vec3 P, N; skinVertex(P, N);
      vN = normalize(mix(N, R[int(pj + 0.5)] * pn, pw)); vCol = col; vUv = uv; vTex = tex; vTwo = two; vHp = hp; vPn = pn; vKind = kind;
      vS = SMx * vec4(P + N * 0.012, 1.0);
      gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0); }`,
  fragmentShader: `
    uniform sampler2D face; uniform sampler2D smap; uniform float paint; uniform float clay; uniform float casts; uniform vec3 black;
    varying vec3 vN; varying vec3 vCol; varying vec2 vUv; varying float vTex; varying float vTwo; varying vec3 vHp; varying vec3 vPn; varying float vKind; varying vec4 vS;
    ${LIGHT}
    float shadowed() {
      vec3 s = vS.xyz / vS.w; float k = 0.0, t = 0.5 / ${SM}.0;
      for (int i = 0; i < 4; i++) { vec2 o = vec2(i == 0 || i == 3 ? -t : t, i < 2 ? -t : t); k += texture2D(smap, s.xy + o).r < s.z - 0.0015 ? 1.0 : 0.0; }
      return step(1.5, k);
    }
    void main() {
      if (!gl_FrontFacing) { if (vTwo < 0.5) discard; gl_FragColor = vec4(black, 1.0); return; }
      float lit = lightAt(vKind, vHp, normalize(vPn), normalize(vN));
      if (vKind < 0.5 && casts > 0.5) lit *= 1.0 - shadowed();
      vec3 base = vCol;
      vec3 c = mix(black, base, lit);
      if (clay > 0.5) c = vec3(0.86, 0.84, 0.8) * (0.55 + 0.45 * max(dot(normalize(vN), L), 0.0)) + 0.08;
      if (vTex > 0.5 && paint > 0.5) { vec4 t = texture2D(face, vUv);
        // in the black the whites of the eyes stay (the drawing's eyes in shadow), the lips go dark
        float keep = mix(mix(0.3, 1.0, smoothstep(0.55, 0.8, t.g / max(t.a, 0.01))), 1.0, lit);
        c = c * (1.0 - t.a) + t.rgb * keep; }
      gl_FragColor = vec4(c, 1.0);
    }`,
  side: THREE.DoubleSide,
});
// the rim: the hull shows only where the form is turned from the light — the lit side has no outline
const hull = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.BackSide,
  vertexShader: `
    attribute float ow; attribute vec3 pn; attribute float pw; attribute float pj; attribute vec3 hp; attribute float kind;
    uniform float width; uniform mat3 R[${sk.J}]; varying float vOw; varying vec3 vN; varying vec3 vHp; varying vec3 vPn; varying float vKind;
    ${gs.glsl}
    void main() { vec3 P, N; skinVertex(P, N);
      vOw = ow; vN = normalize(mix(N, R[int(pj + 0.5)] * pn, pw)); vHp = hp; vPn = pn; vKind = kind;
      gl_Position = projectionMatrix * viewMatrix * vec4(P + N * width * ow, 1.0);
      gl_Position.z += 0.0004 * gl_Position.w; }`,
  fragmentShader: `uniform vec3 rim; uniform float clay; varying float vOw; varying vec3 vN; varying vec3 vHp; varying vec3 vPn; varying float vKind;
    ${LIGHT}
    void main() { if (vOw < 0.35 || clay > 0.5) discard; if (dot(normalize(vN), L) > thr + 0.12) discard; gl_FragColor = vec4(rim, 1.0); }`,
});
const mesh = new THREE.Mesh(g, toon), line = new THREE.Mesh(g, hull);
mesh.frustumCulled = line.frustumCulled = false;
scene.add(mesh, line);
// the floor: night, a pool of light on it, the figure's black shadow in the pool (the same shadow map)
const floor = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.ShaderMaterial({
  uniforms: { smap: U.smap, SMx: U.SMx, dark: { value: new THREE.Color('#1a1c28').convertLinearToSRGB() }, pool: { value: new THREE.Color('#2a2738').convertLinearToSRGB() }, black: U.black, c0: { value: new THREE.Vector2(0, 0) }, fp: { value: new THREE.Vector2(0, 0) }, fwd: { value: new THREE.Vector2(0, -1) }, rgt: { value: new THREE.Vector2(1, 0) }, wall: { value: 1.0 } },
  vertexShader: `uniform mat4 SMx; varying vec4 vS; varying vec3 vW; void main() { vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; vS = SMx * w; gl_Position = projectionMatrix * viewMatrix * w; }`,
  fragmentShader: `uniform sampler2D smap; uniform vec3 dark; uniform vec3 pool; uniform vec3 black; uniform vec2 c0; uniform vec2 fp; uniform vec2 fwd; uniform vec2 rgt; uniform float wall; varying vec4 vS; varying vec3 vW;
    void main() {
      if (dot(vW.xz - fp, fwd) > wall) discard;            // the floor ends at the wall behind the figure
      vec3 s = vS.xyz / vS.w; float sh = (s.x > 0.0 && s.x < 1.0 && s.y > 0.0 && s.y < 1.0 && texture2D(smap, s.xy).r < s.z - 0.002) ? 1.0 : 0.0;
      // the window's light on the floor: from the wall towards the viewer, slanting to the picture's right
      vec2 q = vW.xz - c0; float dz = wall - dot(q, fwd), lx = dot(q, rgt);
      float a = lx - (-0.29 + 0.35 * dz), b = (0.345 + 0.9 * dz) - lx, w = fwidth(lx) + 1e-4;
      float in_ = smoothstep(-w, w, a) * smoothstep(-w, w, b);
      gl_FragColor = vec4(mix(dark, mix(pool, black, sh * 0.85), in_), 1.0); }`,
}));
floor.rotation.x = -Math.PI / 2; scene.add(floor);
// the backdrop: a lighter flat shape behind the figure, always behind it for the camera — the black side of the
// silhouette reads against it (the drawing's window, or the sheet's disc)
const backdrop = new THREE.Group(); scene.add(backdrop);
const bdMat = new THREE.MeshBasicMaterial({ color: '#3b3350', depthWrite: false }), barMat = new THREE.MeshBasicMaterial({ color: NIGHT, depthWrite: false });
const bdRect = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), bdMat), bdDisc = new THREE.Mesh(new THREE.CircleGeometry(0.5, 96), bdMat);
const bar1 = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), barMat), bar2 = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), barMat);
backdrop.add(bdRect, bdDisc, bar1, bar2); backdrop.renderOrder = -1;
for (const m of [bdRect, bdDisc, bar1, bar2]) { m.renderOrder = -1; m.frustumCulled = false; }

const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 100);
const persp = new THREE.PerspectiveCamera(24, 1, 0.05, 200);
let camera = ortho;

// ---------------------------------------------------------------- poses
const J = sk.J, I = sk.index;
// standing as drawn: the rest with the arms let down along the body (a pose layer, for the drawing's views)
function standPose(o = {}) {
  const pose = fig.restPose();
  const out = o.out ?? 0.13, fwd = o.fwd ?? 0.03;
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    const A = I[s + 'Arm'], Hd = I[s + 'Hand'];
    const cur = normalize(sub(getV(pose.P, Hd), getV(pose.P, A)));
    turnUnder(pose, sk, A, qBetween(cur, normalize([sg * out, -1, fwd])));
    build(pose, body, getV(pose.P, I.Hips));
    if (o.twist) turnUnder(pose, sk, A, qAxisAngle(normalize(sub(getV(pose.P, Hd), getV(pose.P, A))), sg * o.twist));
    build(pose, body, getV(pose.P, I.Hips));
  }
  return pose;
}

const S = { clip: null, clipIds: null, t: 0, time: 0, pose: 'stand', push: true,
  cam: { mode: 'ortho', yaw: 0, pitch: 0, cx: 0, cy: 0.83, h: 1.8, dist: 6, target: null, follow: false },
  light: [-0.74, 0.47, 0.48], back: { kind: 'window', w: 0.78, h: 1.96, y: 1.05, x: 0.04, col: '#3b3350' } };
let clip = null;
// where the head looks over a clip (yaw, pitch at 100 Hz) — for the eyes to lead its turns
function headTrack(c) {
  const dt = 0.01, n = Math.floor((c.frames - 1) / c.fps / dt) + 1, yaw = new Float32Array(n), pitch = new Float32Array(n);
  const smp = { q: new Float64Array(J * 4), p: new Float64Array(J * 3), lowest: 0 };
  let prev = 0;
  for (let i = 0; i < n; i++) {
    const pose = fig.retarget.pose(c.sample(i * dt * c.fps, smp)), f = qRot(getQ(pose.Q, I.Head), [0, 0, 1]);
    let y = Math.atan2(f[0], f[2]); while (y - prev > Math.PI) y -= 2 * Math.PI; while (y - prev < -Math.PI) y += 2 * Math.PI;
    yaw[i] = prev = y; pitch[i] = Math.asin(Math.max(-1, Math.min(1, f[1])));
  }
  return { dt, yaw, pitch };
}
// the skirt kept off the legs: each skirt point inside a leg's capsule (thigh, shin) is put on its surface
const dressR = H.pieces?.dress ?? [0, 0], skirt = [];      // a pack without a dress has no skirt to keep off the legs
for (let i = dressR[0]; i < dressR[1]; i++) if (rest[i * 3 + 1] < 0.9) skirt.push(i);
const CAPS = [['LeftLeg', 'LeftShin', 0.058], ['LeftShin', 'LeftFoot', 0.05], ['RightLeg', 'RightShin', 0.058], ['RightShin', 'RightFoot', 0.05]]
  .map(([a, b, r]) => [I[a], I[b], r]);
const RING = 72;                    // the dress is a loft of rings of 72 points (build.py)
const skirtSet = new Int32Array(rest.length / 3).fill(-1); skirt.forEach((i, k) => { skirtSet[i] = k; });
const skirtNb = skirt.map(i => { const k = i - dressR[0], r = Math.floor(k / RING), c = k % RING;
  return [r * RING + (c + 1) % RING, r * RING + (c + RING - 1) % RING, (r - 1) * RING + c, (r + 1) * RING + c].map(m => m + dressR[0]).filter(m => m >= 0 && skirtSet[m] >= 0).map(m => skirtSet[m]); });
// the push fades in from the hips (rest 0.9 m) to 0.74 m, so no step where it begins
const fade = Float64Array.from(skirt, i => { const u = Math.max(0, Math.min(1, (0.9 - rest[i * 3 + 1]) / 0.16)); return u * u * (3 - 2 * u); });
const dsp = new Float64Array(skirt.length * 3), dsp2 = new Float64Array(skirt.length * 3);
// the skirt's points are skinned here too (only they), pushed out of the legs, and the push goes to the shader as an
// offset on top of its own skinning
const skirtSkin = gs.subset(skirt), skirtAt = new Float32Array(skirt.length * 3);
const skirtFirst = skirt.length ? skirt[0] : 0, skirtCount = skirt.length ? skirt[skirt.length - 1] - skirt[0] + 1 : 0;
let pushed = false;
// the neighbours as flat lists (the same as skirtNb), and the legs' capsules as numbers: the same sums, without objects
const nbStart = new Int32Array(skirt.length + 1), nbList = Int32Array.from(skirtNb.flat());
skirtNb.forEach((nb, k) => { nbStart[k + 1] = nbStart[k] + nb.length; });
const cap = new Float64Array(CAPS.length * 7);
function pushSkirt(pose) {
  const P = skirtSkin.skin(pose, skirtAt), D = gs.skinD, n = skirt.length, pp = pose.P;
  CAPS.forEach(([a, b, r], k) => {
    const f = k % 2 ? 0 : 0.2, o = k * 7;
    for (let c = 0; c < 3; c++) { const A = pp[a * 3 + c], B = pp[b * 3 + c]; cap[o + c] = A + (B - A) * f; cap[o + 3 + c] = B; }
    cap[o + 6] = r + 0.012;
  });
  // how far each point must go out of the legs …
  let any = false;
  for (let k = 0; k < n; k++) {
    let x = P[k * 3], y = P[k * 3 + 1], z = P[k * 3 + 2];
    for (let o = 0; o < cap.length; o += 7) {
      const ax = cap[o], ay = cap[o + 1], az = cap[o + 2], bx = cap[o + 3] - ax, by = cap[o + 4] - ay, bz = cap[o + 5] - az, r = cap[o + 6], l2 = bx * bx + by * by + bz * bz;
      let u = ((x - ax) * bx + (y - ay) * by + (z - az) * bz) / l2; u = Math.max(0, Math.min(1, u));
      const cx = ax + bx * u, cy = ay + by * u, cz = az + bz * u, dx = x - cx, dy = y - cy, dz = z - cz, d = Math.hypot(dx, dy, dz);
      if (d < r && d > 1e-6) { const sc = r / d; x = cx + dx * sc; y = cy + dy * sc; z = cz + dz * sc; any = true; }
    }
    dsp[k * 3] = x - P[k * 3]; dsp[k * 3 + 1] = y - P[k * 3 + 1]; dsp[k * 3 + 2] = z - P[k * 3 + 2];
  }
  if (!any) { noPush(); return; }       // no point is in a leg: nothing to spread
  // … spread over the cloth around them (no steps where single points were pushed), keeping the largest push
  for (let it = 0; it < 14; it++) {
    for (let k = 0; k < n; k++) {
      const q0 = nbStart[k], q1 = nbStart[k + 1], m = q1 - q0 + 1;
      let sx = dsp[k * 3], sy = dsp[k * 3 + 1], sz = dsp[k * 3 + 2];
      for (let q = q0; q < q1; q++) { const j = nbList[q] * 3; sx += dsp[j]; sy += dsp[j + 1]; sz += dsp[j + 2]; }
      dsp2[k * 3] = sx / m; dsp2[k * 3 + 1] = sy / m; dsp2[k * 3 + 2] = sz / m;
    }
    for (let i = 0; i < n * 3; i++) { const a = dsp[i], b = dsp2[i]; dsp[i] = Math.abs(b) > Math.abs(a) ? b : (a + b) / 2 + (a - b) / 2 * 0.5; }
  }
  for (let k = 0; k < n; k++) { const i = skirt[k] * 3, w = fade[k]; D[i] = w * dsp[k * 3]; D[i + 1] = w * dsp[k * 3 + 1]; D[i + 2] = w * dsp[k * 3 + 2]; }
  gs.displace(skirtFirst, skirtCount); pushed = true;
}
function noPush() { if (!pushed) return; for (const i of skirt) gs.skinD[i * 3] = gs.skinD[i * 3 + 1] = gs.skinD[i * 3 + 2] = 0; gs.displace(skirtFirst, skirtCount); pushed = false; }
// the pack as it lies, unskinned: every joint where it is at rest, unturned
const rawPose = { Q: new Float64Array(J * 4), P: Float64Array.from(body.joints) };
for (let j = 0; j < J; j++) rawPose.Q[j * 4 + 3] = 1;
let faceWas = '';
function frame() {
  const fp = face.at(S.time, { headT: S.clip ? S.t / clip.fps : null }), fk = JSON.stringify(fp);
  if (fk !== faceWas) { drawFace(faceCtx, fp); faceTex.needsUpdate = true; faceWas = fk; }      // the face is redrawn only when its numbers changed
  let pose;
  if (S.clip) { pose = fig.retarget.pose(clip.sample(S.t, fig.sample)); fig.retarget.placed(pose); }
  else if (S.pose === 'raw') pose = null;
  else pose = S.pose === 'rest' ? fig.restPose() : standPose(S.poseOpts || {});
  if (!pose) { gs.setPose(rawPose); noPush(); fig.pose = fig.restPose(); }
  else {
    // the jaw opens a little with the drawn mouth
    if (fp.jaw > 0) turnUnder(pose, sk, I.Jaw, qAxisAngle(qRot(getQ(pose.Q, I.Head), [1, 0, 0]), fp.jaw * 0.11));
    if (S.clip) {          // on the floor as the engine's Figure does (motion.floor 'lowest')
      const shift = pose.floor - gs.lowest(pose); for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
    }
    gs.setPose(pose);
    if (S.push && skirt.length) pushSkirt(pose); else noPush();
    fig.pose = pose;
  }
  gs.update(renderer);
  const Q = fig.pose.Q;
  for (let j = 0; j < J; j++) { const [x, y, z, w] = [Q[j * 4], Q[j * 4 + 1], Q[j * 4 + 2], Q[j * 4 + 3]];
    U.R.value[j].set(1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)); }
  // the light in the head's own frame (the designed shapes live there)
  const qh = getQ(Q, I.Head), l = U.L.value;
  U.Lh.value.fromArray(qRot([-qh[0], -qh[1], -qh[2], qh[3]], [l.x, l.y, l.z]));
}
function facing() { // where the pelvis faces now (yaw about y; 0 — +z)
  const qh = getQ(fig.pose.Q, I.Hips);
  const x = 2 * (qh[0] * qh[2] + qh[1] * qh[3]), z = 1 - 2 * (qh[0] * qh[0] + qh[1] * qh[1]);
  return Math.atan2(x, z);
}

window.A = {
  H, body, fig, gs, sk, facing, face, S, EXPR_NAMES, clipInfo: () => clip && { frames: clip.frames, fps: clip.fps },
  async set(o) {
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; face.setHead(clip ? headTrack(clip) : null); }
      S.clip = !!ids;
    }
    for (const k of ['t', 'pose', 'poseOpts', 'push']) if (o[k] !== undefined) S[k] = o[k];
    // the face's clock (seconds): given, or the clip's time
    if (o.time !== undefined) S.time = o.time; else if (o.t !== undefined && clip && !S.liveClock) S.time = o.t / clip.fps;
    if (o.liveClock !== undefined) S.liveClock = o.liveClock;
    if (o.still !== undefined) face.still = o.still;
    if (o.exprTrack) { face.exprKeys = [{ t: -10, w: { calm: 1 } }]; for (const [t, w] of o.exprTrack) face.setExpr(t, typeof w === 'string' ? { [w]: 1 } : w); }
    if (o.expr) face.setExpr(S.time, typeof o.expr === 'string' ? { [o.expr]: 1 } : o.expr);
    if (o.talk !== undefined) { face.talk(o.talk ? (o.talkFrom ?? S.time) : null); face.talkTo = o.talkTo ?? null; }
    if (o.cam) Object.assign(S.cam, o.cam);
    if (o.light) S.light = o.light;
    if (o.thr !== undefined) U.thr.value = o.thr;
    if (o.width !== undefined) U.width.value = o.width;
    if (o.bg) scene.background = new THREE.Color(o.bg);
    if (o.floor !== undefined) floor.visible = !!o.floor;
    if (o.back !== undefined) S.back = o.back && { ...S.back, ...o.back };
    if (o.cast !== undefined) U.casts.value = o.cast ? 1 : 0;
    if (o.pool) { floor.material.uniforms.c0.value.set(o.pool[0], o.pool[1]); S.poolFixed = true; }
    if (o.show !== undefined) {           // only these pieces (names from the pack's header), or all
      const all = a.triangles; let idx = all;
      if (o.show) { const parts = []; for (const n of o.show) { const [s0, s1] = H.trianglePieces[n]; parts.push(all.subarray(s0 * 3, s1 * 3)); }
        idx = new Uint32Array(parts.reduce((k, p) => k + p.length, 0)); let k = 0; for (const p of parts) { idx.set(p, k); k += p.length; } }
      g.setIndex(new THREE.BufferAttribute(idx, 1));
    }
    if (o.paint !== undefined) U.paint.value = o.paint ? 1 : 0;
    if (o.flat !== undefined) U.clay.value = o.flat ? 1 : 0;
    frame();
  },
  frames: () => clip ? clip.frames : 0,
  render() {
    const w = canvas.clientWidth, h = canvas.clientHeight; if (canvas.width !== w || canvas.height !== h) renderer.setSize(w, h, false);      // setting the size anew each frame makes the browser allocate the picture anew
    const c = S.cam, cp = Math.cos(c.pitch);
    let tg = c.target || [c.cx, c.cy, 0];
    if (c.follow && fig.pose) { const P = fig.pose.P; tg = [P[I.Hips * 3], c.cy, P[I.Hips * 3 + 2]]; }
    if (c.focus && fig.pose) { const P = fig.pose.P, k = I[c.focus]; tg = [P[k * 3], P[k * 3 + 1] + (c.up || 0), P[k * 3 + 2]]; }
    const dir = [Math.sin(c.yaw) * cp, Math.sin(c.pitch), Math.cos(c.yaw) * cp];
    if (c.mode === 'ortho') {
      camera = ortho; const hh = c.h / 2, ww = hh * w / h;
      Object.assign(ortho, { left: -ww, right: ww, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
      ortho.position.set(tg[0] + dir[0] * 20, tg[1] + dir[1] * 20, tg[2] + dir[2] * 20);
    } else {
      camera = persp; persp.aspect = w / h; persp.fov = c.fov || 24; persp.updateProjectionMatrix();
      persp.position.set(tg[0] + dir[0] * c.dist, tg[1] + dir[1] * c.dist, tg[2] + dir[2] * c.dist);
    }
    camera.lookAt(tg[0], tg[1], tg[2]);
    // the key as in the drawing: from the picture's left, above, in front — it turns with the camera
    camera.updateMatrixWorld();
    const e = camera.matrixWorld.elements, l = S.light;
    U.L.value.set(e[0] * l[0] + e[4] * l[1] + e[8] * l[2], e[1] * l[0] + e[5] * l[1] + e[9] * l[2], e[2] * l[0] + e[6] * l[1] + e[10] * l[2]).normalize();
    if (fig.pose) { const qh = getQ(fig.pose.Q, I.Head), L = U.L.value; U.Lh.value.fromArray(qRot([-qh[0], -qh[1], -qh[2], qh[3]], [L.x, L.y, L.z])); }
    // the shadow map: the figure from the light
    const hp = fig.pose ? [fig.pose.P[I.Hips * 3], 0.85, fig.pose.P[I.Hips * 3 + 2]] : [0, 0.85, 0], L = U.L.value;
    shadowCam.position.set(hp[0] + L.x * 6, hp[1] + L.y * 6, hp[2] + L.z * 6); shadowCam.lookAt(hp[0], hp[1], hp[2]); shadowCam.updateMatrixWorld();
    U.SMx.value.set(0.5, 0, 0, 0.5, 0, 0.5, 0, 0.5, 0, 0, 0.5, 0.5, 0, 0, 0, 1).multiply(shadowCam.projectionMatrix).multiply(shadowCam.matrixWorldInverse);
    line.visible = false; const fv = floor.visible, bv = backdrop.visible; floor.visible = false; backdrop.visible = false;
    scene.overrideMaterial = depthMat; renderer.setRenderTarget(shadowRT); renderer.clear(); renderer.render(scene, shadowCam);
    scene.overrideMaterial = null; renderer.setRenderTarget(null); line.visible = true; floor.visible = fv;
    // the backdrop behind the figure, facing the camera
    backdrop.visible = !!S.back;
    { const fu = floor.material.uniforms, n = Math.hypot(dir[0], dir[2]) || 1;
      fu.fwd.value.set(-dir[0] / n, -dir[2] / n); fu.rgt.value.set(e[0], e[2]); fu.fp.value.set(c.follow || c.focus ? tg[0] : 0, c.follow || c.focus ? tg[2] : 0);
      if (!S.poolFixed) fu.c0.value.copy(fu.fp.value); }      // the window and its light stay behind the figure the camera follows
    if (S.back) {
      // its sizes are given at the figure's distance: 3 m behind, a perspective camera sees it that much smaller
      const b = S.back, k = c.mode === 'ortho' ? 1 : (c.dist + 3) / c.dist;
      const bx = c.follow || c.focus ? tg[0] : 0, bz = c.follow || c.focus ? tg[2] : 0, by = c.focus ? tg[1] : tg[1] + (b.y - tg[1]) * k;
      const right = [e[0], e[1], e[2]];
      backdrop.position.set(bx - dir[0] * 3 + right[0] * b.x * k, by - dir[1] * 3 + right[1] * b.x * k, bz - dir[2] * 3 + right[2] * b.x * k);
      backdrop.quaternion.copy(camera.quaternion);
      bdMat.color.set(b.col); bdRect.visible = bar1.visible = bar2.visible = b.kind === 'window'; bdDisc.visible = b.kind === 'disc';
      bdRect.scale.set(b.w, b.h, 1); bdDisc.scale.set(b.w, b.w, 1);
      bar1.scale.set(0.02, b.h, 1); bar1.position.set(0.02, 0, 0.001); bar2.scale.set(b.w, 0.02, 1); bar2.position.set(0, b.h * 0.08, 0.001);
      backdrop.scale.setScalar(k);
    }
    renderer.render(scene, camera);
  },
};
await window.A.set({});
window.A.render();
window.__ready = true;

if (!q.has('pack')) (await import('./ui.js')).ui(window.A, canvas);
