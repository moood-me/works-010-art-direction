// A Klaus character in 3D (after Р5's anya.js): the pack (tools/build.py) on the engine's skeleton, skinning and
// Kimodo retargeting; lit the way the drawing is — one warm key light against a cool shadow, a soft but readable edge
// of the shadow, cast shadows from a shadow map (the brows on the eyes, the nose on the moustache), a thin warm rim on
// the edge away from the light, a sheen where a glossy form turns to the light; the face's painted layers from the
// drawing (skin tones + mouth, eyes) and the forms that move on the face (brows, moustache); then the drawing's
// finish over the frame: the backdrop with its glow, grain, mottling, a vignette.
// The face lives by its own clock (life()): blinks at uneven intervals, the eyes hold and jump, speech as syllables.
// This is the page's fast variant (fast.html; view.html and klaus.js beside it are the page as they were): the skin is
// skinned and its normals found on the video card (engine-gpu/src/gpuskin.js), the processor works out only the
// joints, the floor from a probe of the skin, and the offsets of the forms that move on the face.
//   fast.html?pack=<pack .json>   window.A.set({clip, t, time, expr, talk, cam, light, …}); A.render()
import * as THREE from 'three';
THREE.ColorManagement.enabled = false;   // the drawing's colours are used as their numbers
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { qAxisAngle, getV } from '../../../../engine/src/math.js';
import { clavicleShare } from '../../../../engine/src/skin.js';
import { GpuSkin } from '../../../../engine-gpu/src/gpuskin.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack') || '../../data/marat.json', location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const sk = E.skeleton;
const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const spec = { skinning: { method: 'dqs', clavicleShare: 0.33, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
const gs = new GpuSkin(THREE, fig.skinner);
const rest = Float32Array.from(a.positions);

// ---------------------------------------------------------------- the stage
const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, alpha: true });
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
renderer.setClearColor(0x000000, 0);
const scene = new THREE.Scene();
const g = gs.attributes(new THREE.BufferGeometry());
// the offsets of the forms that move on the face: added in the shaders after the skin, as the page was (it moves them
// after its normals are found, so they keep the unmoved skin's normals)
const mvD = new THREE.BufferAttribute(new Float32Array(body.N * 3), 3); mvD.setUsage(THREE.DynamicDrawUsage); g.setAttribute('mvD', mvD);
for (const [k, n, norm] of [['col', 3, true], ['shd', 3, true], ['rim', 3, true], ['gloss', 1, true], ['uv', 2, false], ['tw', 1, true], ['pn', 3, false], ['pw', 1, true], ['two', 1, false], ['mat', 1, false]])
  g.setAttribute(k, new THREE.BufferAttribute(a[k], n, norm));
g.setAttribute('rp', new THREE.BufferAttribute(rest, 3));
g.setIndex(new THREE.BufferAttribute(a.triangles, 1));

const loader = new THREE.TextureLoader();
const texs = {};
function texture(name) {
  if (!texs[name]) {
    const t = loader.load(new URL(`${H.faces}/${name}.png`, packUrl).href, () => { t.ready = true; });
    t.colorSpace = THREE.NoColorSpace; t.anisotropy = 8; texs[name] = t;
  }
  return texs[name];
}
const loaded = name => new Promise(ok => { const t = texture(name); const w = () => t.ready ? ok(t) : setTimeout(w, 15); w(); });

const SM = 4096;
const smTarget = new THREE.WebGLRenderTarget(SM, SM);
smTarget.depthTexture = new THREE.DepthTexture(SM, SM); smTarget.depthTexture.type = THREE.UnsignedIntType;
const lightCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 10);
const depthMat = new THREE.ShaderMaterial({ uniforms: gs.uniforms, side: THREE.DoubleSide, colorWrite: false,
  vertexShader: `attribute vec3 mvD; ${gs.glsl}
    void main() { vec3 P, N; skinVertex(P, N); P += mvD; gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0); }`,
  fragmentShader: `void main() { gl_FragColor = vec4(1.0); }` });

const U = {
  ...gs.uniforms,
  L: { value: new THREE.Vector3() }, Lr: { value: new THREE.Vector3() }, Vd: { value: new THREE.Vector3() },
  thr: { value: 0.16 }, soft: { value: 0.16 },
  skinT: { value: await loaded('skin-' + ((H.expr.calm || {}).mouth || 'none')) }, eyeT: { value: await loaded('eyes-calm-oc') },
  Rh: { value: new THREE.Matrix3() },
  smap: { value: smTarget.depthTexture }, smMat: { value: new THREE.Matrix4() }, smTexel: { value: 1 / SM }, smBlur: { value: 3.0 },
  smBias: { value: 0.004 }, uFlat: { value: 0 }, noCast: { value: 0 },
};
const toon = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.DoubleSide,
  vertexShader: `
    attribute vec3 col; attribute vec3 shd; attribute vec3 rim; attribute float gloss; attribute float tw; attribute vec3 pn; attribute float pw;
    attribute float two; attribute float mat; attribute vec3 rp; attribute vec3 mvD;
    uniform mat3 Rh; uniform mat4 smMat;
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec3 vRim; varying vec2 vUv; varying float vTw;
    varying float vTwo; varying float vGloss; varying vec4 vSm; varying float vMat; varying vec3 vRp;
    ${gs.glsl}
    void main() {
      vec3 P, N; skinVertex(P, N); P += mvD;
      vec3 n = normalize(N);
      if (pw > 0.0) n = normalize(mix(n, Rh * pn, pw));
      vN = n; vCol = col; vShd = shd; vRim = rim; vUv = uv; vTw = tw; vTwo = two; vGloss = gloss; vMat = mat; vRp = rp;
      vSm = smMat * vec4(P, 1.0);
      gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0);
    }`,
  fragmentShader: `
    uniform vec3 L; uniform vec3 Lr; uniform vec3 Vd; uniform float thr; uniform float soft; uniform float uFlat; uniform float noCast;
    uniform sampler2D skinT; uniform sampler2D eyeT; uniform sampler2D smap; uniform float smTexel; uniform float smBlur; uniform float smBias;
    varying vec3 vN; varying vec3 vCol; varying vec3 vShd; varying vec3 vRim; varying vec2 vUv; varying float vTw;
    varying float vTwo; varying float vGloss; varying vec4 vSm; varying float vMat; varying vec3 vRp;
    const vec2 PD[12] = vec2[12](vec2(-0.326,-0.406), vec2(-0.840,-0.074), vec2(-0.696,0.457), vec2(-0.203,0.621),
      vec2(0.962,-0.195), vec2(0.473,-0.480), vec2(0.519,0.767), vec2(0.185,-0.893), vec2(0.507,0.064),
      vec2(0.896,0.412), vec2(-0.322,-0.933), vec2(-0.792,-0.598));
    float lit_by_map(float nl) {
      vec3 p = vSm.xyz / vSm.w * 0.5 + 0.5;
      if (p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0) return 1.0;
      float bias = smBias * (1.0 + 2.0 * (1.0 - clamp(nl, 0.0, 1.0)));
      float s = 0.0;
      for (int i = 0; i < 12; i++) { float d = texture2D(smap, p.xy + PD[i] * smTexel * smBlur).r; s += (p.z - bias > d) ? 0.0 : 1.0; }
      return s / 12.0;
    }
    ${H.deco || 'void deco(vec3 rp, vec2 uv, float m, inout vec3 base, inout vec3 bshd) {}'}
    void main() {
      vec3 n = normalize(vN);
      vec3 base = vCol, bshd = vShd;
      deco(vRp, vUv, vMat, base, bshd);
      bool back = !gl_FrontFacing;
      if (back) { if (vTwo < 0.5) discard; n = -n; }
      float d = dot(n, L);
      float lam = smoothstep(thr - soft, thr + soft, d);
      float sh = noCast > 0.5 ? 1.0 : lit_by_map(d);
      float l = lam * smoothstep(0.2, 0.8, sh);
      if (uFlat > 0.5) l = 1.0;
      vec3 c = mix(bshd, base, l);
      // the sheen of a glossy form (the dome, the nose, brass, glass)
      vec3 h = normalize(L + Vd);
      float sp = smoothstep(0.90, 0.985, dot(n, h)) * l * vGloss * (1.0 - uFlat);
      c = mix(c, mix(base, vec3(1.0, 0.95, 0.86), 0.75), sp * 0.6);
      // rim: a thin warm edge where the form turns away from the eye on the far side from the key
      float edge = smoothstep(0.62, 0.9, 1.0 - abs(dot(n, Vd)));
      float rs = smoothstep(-0.1, 0.4, dot(n, Lr));
      c = mix(c, vRim, edge * rs * 0.55 * (back ? 0.0 : 1.0) * (1.0 - uFlat));
      if (back) c = mix(bshd, base, l * 0.5) * 0.85;
      // the painted layers (skin tones and mouth, then the eyes), a little dimmer in shadow
      if (vTw > 0.0 && !back) {
        float dim = uFlat > 0.5 ? 1.0 : 0.74 + 0.26 * l;
        vec4 t = texture2D(skinT, vUv); c = mix(c, t.rgb * dim, t.a * vTw);
        t = texture2D(eyeT, vUv); c = mix(c, t.rgb * dim, t.a * vTw);
      }
      gl_FragColor = vec4(c, 1.0);
    }`,
});
const mesh = new THREE.Mesh(g, toon); mesh.frustumCulled = false;
scene.add(mesh);
const ground = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 0.8), new THREE.ShaderMaterial({
  transparent: true, depthWrite: false,
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: 'varying vec2 vUv; void main(){ float r = length((vUv - 0.5) * vec2(2.0, 2.0)); gl_FragColor = vec4(0.08, 0.05, 0.13, 0.55 * (1.0 - smoothstep(0.15, 0.6, r))); }',
}));
ground.rotation.x = -Math.PI / 2; ground.position.y = 0.001; ground.renderOrder = -1; scene.add(ground);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, uniforms: { c: { value: new THREE.Vector2(0, 0) } },
  vertexShader: 'varying vec3 vP; void main(){ vP = (modelMatrix * vec4(position, 1.0)).xyz; gl_Position = projectionMatrix * viewMatrix * vec4(vP, 1.0); }',
  fragmentShader: `uniform vec2 c; varying vec3 vP; void main(){ float d = length(vP.xz - c);
    vec2 gq = abs(fract(vP.xz / 0.6) - 0.5); float ln = smoothstep(0.47, 0.5, max(gq.x, gq.y));
    gl_FragColor = vec4(mix(vec3(0.14, 0.09, 0.16), vec3(0.24, 0.15, 0.2), ln * 0.6), 0.75 * (1.0 - smoothstep(2.5, 7.0, d))); }`,
}));
floor.rotation.x = -Math.PI / 2; floor.renderOrder = -2; floor.visible = false; scene.add(floor);

const rt = new THREE.WebGLRenderTarget(16, 16, { samples: 4 });
const back = H.back || { top: '#2c2744', bottom: '#4c3150', glow: '#e8985a' };
const post = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
  uniforms: { img: { value: rt.texture }, top: { value: new THREE.Color(back.top) }, bot: { value: new THREE.Color(back.bottom) },
    glow: { value: new THREE.Color(back.glow) }, gpos: { value: new THREE.Vector3(0.15, 0.35, 0.65) },
    floorY: { value: 2 }, grain: { value: 0.12 }, plain: { value: 0 } },
  depthTest: false, depthWrite: false,
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }',
  fragmentShader: `
    uniform sampler2D img; uniform vec3 top; uniform vec3 bot; uniform vec3 glow; uniform vec3 gpos;
    uniform float floorY; uniform float grain; uniform float plain; varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
      return mix(mix(h(i), h(i+vec2(1,0)), f.x), mix(h(i+vec2(0,1)), h(i+vec2(1,1)), f.x), f.y); }
    void main() {
      vec2 s = vec2(vUv.x, 1.0 - vUv.y);
      vec3 bg = mix(top, bot, s.y);
      float r = length(s - gpos.xy) / gpos.z;
      bg = mix(bg, glow, 0.75 * clamp(1.0 - r, 0.0, 1.0));
      if (s.y > floorY) bg = mix(bg, bot * 0.75, 0.6);
      vec4 f = texture2D(img, vUv);
      if (plain > 0.5) { gl_FragColor = vec4(mix(vec3(1.0), f.rgb / max(f.a, 1e-3), f.a), 1.0); return; }
      vec3 c = mix(bg, f.rgb / max(f.a, 1e-3), f.a);
      vec2 px = gl_FragCoord.xy;
      float m = vn(px * 0.018) * 0.6 + vn(px * 0.04) * 0.4;
      c = mix(c, c * (0.86 + 0.28 * m), 0.3);
      c *= 1.0 - grain * 0.6 * h(px + 0.37);
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
  const down = o.down ?? 0.62;
  for (const [s, sg] of [['Left', -1], ['Right', 1]]) {
    const od = (o[s] || {});
    turnUnder(pose, sk, I[s + 'Arm'], qAxisAngle([0, 0, 1], sg * (od.down ?? down)));
    if (od.fwd ?? o.fwd) turnUnder(pose, sk, I[s + 'Arm'], qAxisAngle([1, 0, 0], -(od.fwd ?? o.fwd)));
    if (od.out) turnUnder(pose, sk, I[s + 'Arm'], qAxisAngle([0, 1, 0], sg * od.out));
    turnUnder(pose, sk, I[s + 'ForeArm'], qAxisAngle(od.axis || [1, 0, 0], od.bend ?? o.straighten ?? 0.45));
  }
  const curl = o.curl ?? 0.45;
  for (const s of ['Left', 'Right']) {
    const P0 = body.joints, jp = n => [P0[I[s + n] * 3], P0[I[s + n] * 3 + 1], P0[I[s + n] * 3 + 2]];
    const ix = jp('HandIndex1'), pk = jp('HandPinky1');
    const ax = [pk[0] - ix[0], pk[1] - ix[1], pk[2] - ix[2]];
    const cu = (o[s] || {}).curl ?? curl;
    for (const f of ['Index', 'Middle', 'Ring', 'Pinky']) for (const k of [1, 2, 3])
      turnUnder(pose, sk, I[s + 'Hand' + f + k], qAxisAngle(ax, (s === 'Left' ? 1 : -1) * cu * (k === 1 ? 0.6 : 1)));
  }
  if (o.headTurn) turnUnder(pose, sk, I.Head, qAxisAngle([0, 1, 0], o.headTurn));
  if (o.headTilt) turnUnder(pose, sk, I.Head, qAxisAngle([0, 0, 1], o.headTilt));
  if (o.headNod) turnUnder(pose, sk, I.Head, qAxisAngle([1, 0, 0], o.headNod));
  if (o.lean) turnUnder(pose, sk, I.Spine1, qAxisAngle([1, 0, 0], o.lean));
  build(pose, body, getV(pose.P, I.Hips));
  return pose;
}

// ---------------------------------------------------------------- the face's life: schedules from a seeded stream
function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return (s >>> 0) / 4294967296; }; }
const ease = t => t * t * (3 - 2 * t);
const LIFE = (() => {
  const R = rng(H.seed || 11), T = 600;
  const blinks = [];
  for (let b = 0.6 + R() * 2; b < T;) {
    blinks.push(b);
    const ln = Math.exp(Math.log(3.0) + 0.45 * Math.sqrt(-2 * Math.log(R() + 1e-9)) * Math.cos(2 * Math.PI * R()));
    b += Math.max(0.8, ln);
  }
  const looks = [];   // [t, 'l'|'c'|'r']: the eyes hold and jump
  for (let t = 0, cur = 'c'; t < T;) {
    looks.push([t, cur]);
    t += cur === 'c' ? 0.9 + R() * 2.6 : 0.4 + R() * 1.1;
    const r = R(); cur = cur === 'c' ? (r < 0.5 ? 'l' : 'r') : (r < 0.8 ? 'c' : (cur === 'l' ? 'r' : 'l'));
  }
  const syl = [];     // [t0, t1, shape]: phrases of syllables with pauses
  for (let s = 0.3; s < T;) {
    const end = s + 1.0 + R() * 1.8;
    while (s < end) { const d = 0.13 + R() * 0.14; syl.push([s, s + d, R() < 0.55 ? 'a' : 'o']); s += d + (R() < 0.25 ? 0.05 : 0); }
    s += 0.35 + R() * 0.6;
  }
  const at = (arr, t, key = x => x[0]) => { let lo = 0, hi = arr.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (key(arr[m]) <= t) lo = m; else hi = m - 1; } return arr[lo]; };
  return {
    // how shut the eyes are (0 open … 1 shut) at time t: close ~75 ms, hold 25, open ~160
    blink(t, changes) {
      let k = 0;
      const one = b0 => { const s = t - b0; if (s < 0 || s > 0.26) return 0; return s < 0.075 ? ease(s / 0.075) : s < 0.1 ? 1 : 1 - ease((s - 0.1) / 0.16); };
      const b = at(blinks, t, x => x); k = Math.max(k, one(b));
      for (const c of changes) k = Math.max(k, one(c - 0.08));
      return k;
    },
    look(t) { return at(looks, t)[1]; },
    lookChange(t) { return at(looks, t)[0]; },
    mouth(t) { const s = at(syl, t); return t < s[1] ? { shape: s[2], open: Math.sin(Math.PI * (t - s[0]) / (s[1] - s[0])) } : { shape: null, open: 0 }; },
  };
})();

// ---------------------------------------------------------------- state
const S = { clip: null, clipIds: null, t: 0, time: 0, pose: 'stand', poseOpts: {}, expr: 'calm', exprAt: -10, talk: false, live: true,
  lid: null, look: null, mouth: null,
  cam: { mode: 'ortho', yaw: 0, pitch: 0, cx: 0, cy: 0.85, h: 1.8, dist: 6, follow: false },
  light: [-0.55, 0.5, 0.67], lightSpace: 'camera', shadowBox: null };
let clip = null;
const mv = {};       // the movers' present values (followed with a spring in time)
for (const k in H.movers || {}) mv[k] = { dy: 0, rot: 0, bend: 0, t: 0 };
let prevExpr = 'calm';
const mvOn = {};     // the movers whose offset is on the video card now

function faceNow() {
  const e = H.expr[S.expr] || {}, time = S.time;
  // the eyes: the lid's stage and where they look; an expression's change comes with a blink
  let k = S.live ? LIFE.blink(time, [S.exprAt]) : 0;
  const lid = S.lid || (k > 0.75 ? 's' : k > 0.3 ? 'h' : 'o');
  const look = S.look || (S.live ? LIFE.look(time) : 'c');
  const ex = (S.live && time < S.exprAt + 0.04) ? prevExpr : S.expr;
  const eyeName = lid === 's' ? `eyes-${ex}-sc` : `eyes-${ex}-${lid}${look}`;
  let mouth = S.mouth || e.mouth || 'none', open = 0;
  if (S.talk) { const m = LIFE.mouth(time); open = m.open; if (m.shape && m.open > 0.35) mouth = m.shape; }
  return { eyeName, skinName: `skin-${mouth}`, open, e };
}
// a mover's points are moved on the video card: their offset on top of the skin (mvD), sent for its points only
function movers(dt) {
  const f = faceNow(), e = f.e, D = mvD.array, Q = fig.pose.Q, h = I.Head;
  const [x, y, z, w] = [Q[h * 4], Q[h * 4 + 1], Q[h * 4 + 2], Q[h * 4 + 3]];
  const R = [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)];
  U.Rh.value.set(...R);
  const tgt = (H.moves ? H.moves(e, f) : null) || moveTargets(e, f);
  const a1 = dt === null ? 1 : 1 - Math.exp(-Math.max(0, dt) * 14);
  for (const k in mv) {
    const m = mv[k], tg = tgt[k] || {};
    for (const c of ['dy', 'rot', 'bend']) m[c] += ((tg[c] || 0) - m[c]) * a1;
    const on = Math.abs(m.dy) + Math.abs(m.rot) + Math.abs(m.bend) >= 1e-4;
    if (!on && !mvOn[k]) continue;
    const pv = H.movers[k].pivot, K = H.K, cs = Math.cos(m.rot), sn = Math.sin(m.rot), O = H.headOrigin;
    for (const [b0, n] of H.movers[k].ranges) {
      if (on) for (let i = b0; i < b0 + n; i++) {
        const rx = rest[i * 3] - O[0], ry = rest[i * 3 + 1] - O[1];
        const px = rx - pv[0], py = ry - pv[1];
        const dx = cs * px - sn * py - px, dyy = sn * px + cs * py - py + (-m.dy - m.bend * Math.min(1, (rx / (80 * K)) ** 2)) * K;
        D[i * 3] = R[0] * dx + R[1] * dyy; D[i * 3 + 1] = R[3] * dx + R[4] * dyy; D[i * 3 + 2] = R[6] * dx + R[7] * dyy;
      } else D.fill(0, b0 * 3, (b0 + n) * 3);
      mvD.addUpdateRange(b0 * 3, n * 3); mvD.needsUpdate = true;
    }
    mvOn[k] = on;
  }
  U.skinT.value = texture(f.skinName).ready ? texture(f.skinName) : U.skinT.value;
  U.eyeT.value = texture(f.eyeName).ready ? texture(f.eyeName) : U.eyeT.value;
  return f;
}
// brows: (inner end, outer end) of the drawing's units, down positive → a lift and a turn; the moustache's tips
function moveTargets(e, f) {
  const b = e.brow || [0, 0], dy = (b[0] + b[1]) / 2, rot = (b[1] - b[0]) / 70;
  const out = { browL: { dy, rot: -rot }, browR: { dy, rot } };
  out.moustache = { dy: f.open * 2.5, bend: (e.mou || 0) + f.open * 3 };
  out.beard = { dy: (e.jaw || 0) * 0.5 + f.open * 4 };
  return out;
}
let lastTime = null;
function frame() {
  let pose;
  if (S.clip) {          // as the engine's Figure.frame: the collarbone's share, the place, on the floor ('lowest')
    pose = fig.retarget.pose(clip.sample(S.t, fig.sample));
    clavicleShare(pose, body, spec.skinning.clavicleShare); build(pose, body, getV(pose.P, I.Hips));
    fig.retarget.placed(pose);
    const shift = pose.floor - gs.lowest(pose); for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
  } else pose = S.pose === 'rest' ? fig.restPose() : standPose(S.poseOpts);
  gs.setPose(pose); fig.pose = pose;
  gs.update(renderer);
  const dt = (lastTime === null || !S.live) ? null : S.time - lastTime; lastTime = S.time;
  movers(dt !== null && dt >= 0 && dt < 0.2 ? dt : null);
  const P = fig.pose.P; ground.position.x = P[I.Hips * 3]; ground.position.z = P[I.Hips * 3 + 2];
  floor.material.uniforms.c.value.set(P[I.Hips * 3], P[I.Hips * 3 + 2]);
}

window.A = {
  H, body, fig, gs, sk, S, texture: loaded,
  async set(o) {
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; }
      S.clip = !!ids;
    }
    for (const k of ['t', 'time', 'pose', 'poseOpts', 'light', 'lightSpace', 'shadowBox', 'talk', 'live', 'lid', 'look', 'mouth', 'blur']) if (o[k] !== undefined) S[k] = o[k];
    if (o.expr && o.expr !== S.expr) { prevExpr = S.expr; S.expr = o.expr; S.exprAt = S.time + 0.08; }
    if (o.cam) Object.assign(S.cam, o.cam);
    for (const k of ['thr', 'soft', 'noCast']) if (o[k] !== undefined) U[k].value = o[k];
    if (o.flat !== undefined) U.uFlat.value = o.flat;
    if (o.ground !== undefined) S.groundOn = o.ground;
    if (o.floor3d !== undefined) floor.visible = o.floor3d;
    if (o.floorY !== undefined) post.material.uniforms.floorY.value = o.floorY;
    if (o.plain !== undefined) post.material.uniforms.plain.value = o.plain;
    if (o.wait) { const f = faceNow(); await loaded(f.eyeName); await loaded(f.skinName); }
    frame();
  },
  clipInfo: () => clip ? { frames: clip.frames, fps: clip.fps || 30 } : null,
  hips: () => getV(fig.pose.P, I.Hips),
  facing() { const Q = fig.pose.Q, h = I.Hips; const [x, y, z, w] = [Q[h * 4], Q[h * 4 + 1], Q[h * 4 + 2], Q[h * 4 + 3]]; return Math.atan2(2 * (x * z + y * w), 1 - 2 * (x * x + y * y)); },
  render() {
    const w = canvas.clientWidth, h = canvas.clientHeight; if (canvas.width !== w || canvas.height !== h) renderer.setSize(w, h, false);      // setting the size anew each frame makes the browser allocate the picture anew
    rt.setSize(w, h);
    const c = S.cam, cp = Math.cos(c.pitch);
    let tg = c.target || [c.cx, c.cy, 0];
    if (c.follow && fig.pose) { const P = fig.pose.P; tg = [P[I.Hips * 3], c.cy, P[I.Hips * 3 + 2]]; }
    if (c.focus && fig.pose) { const P = fig.pose.P, j = I[c.focus]; tg = [P[j * 3], P[j * 3 + 1] + (c.up || 0), P[j * 3 + 2]]; }
    const yaw = c.yaw + (c.facing ? this.facing() : 0);
    const dir = [Math.sin(yaw) * cp, Math.sin(c.pitch), Math.cos(yaw) * cp];
    if (c.mode === 'ortho') {
      camera = ortho; const hh = c.h / 2, ww = hh * w / h;
      Object.assign(ortho, { left: -ww, right: ww, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
      ortho.position.set(tg[0] + dir[0] * 20, tg[1] + dir[1] * 20, tg[2] + dir[2] * 20);
    } else {
      camera = persp; persp.aspect = w / h; persp.fov = c.fov || 24; persp.updateProjectionMatrix();
      persp.position.set(tg[0] + dir[0] * c.dist, tg[1] + dir[1] * c.dist, tg[2] + dir[2] * c.dist);
    }
    if (c.sx) { const rx = Math.cos(yaw), rz = -Math.sin(yaw); tg = [tg[0] - rx * c.sx, tg[1], tg[2] - rz * c.sx]; camera.position.x -= rx * c.sx; camera.position.z -= rz * c.sx; }
    camera.lookAt(tg[0], tg[1], tg[2]); camera.updateMatrixWorld();
    const e = camera.matrixWorld.elements, l = S.light;
    const Lw = S.lightSpace === 'camera'
      ? new THREE.Vector3(e[0] * l[0] + e[4] * l[1] + e[8] * l[2], e[1] * l[0] + e[5] * l[1] + e[9] * l[2], e[2] * l[0] + e[6] * l[1] + e[10] * l[2]).normalize()
      : new THREE.Vector3(...l).normalize();
    U.L.value.copy(Lw);
    const Vd = new THREE.Vector3(); camera.getWorldDirection(Vd); U.Vd.value.copy(Vd).negate();
    const right = new THREE.Vector3(e[0], e[1], e[2]);
    const side = Lw.dot(right) > 0 ? -1 : 1;
    U.Lr.value.copy(right).multiplyScalar(side).addScaledVector(Vd, 0.6).add(new THREE.Vector3(0, 0.2, 0)).normalize();
    const P = fig.pose.P, hip = [P[I.Hips * 3], P[I.Hips * 3 + 1], P[I.Hips * 3 + 2]];
    const box = S.shadowBox ? (S.shadowBox.joint ? { c: [P[I[S.shadowBox.joint] * 3], P[I[S.shadowBox.joint] * 3 + 1] + (S.shadowBox.up || 0), P[I[S.shadowBox.joint] * 3 + 2]], r: S.shadowBox.r } : S.shadowBox)
      : { c: [hip[0], hip[1] * 0.2 + 0.72, hip[2]], r: 1.15 };
    lightCam.left = -box.r; lightCam.right = box.r; lightCam.top = box.r; lightCam.bottom = -box.r;
    lightCam.near = 0.1; lightCam.far = 4 + 2 * box.r; lightCam.updateProjectionMatrix();
    lightCam.position.set(box.c[0] + Lw.x * 3, box.c[1] + Lw.y * 3, box.c[2] + Lw.z * 3);
    lightCam.lookAt(box.c[0], box.c[1], box.c[2]); lightCam.updateMatrixWorld();
    U.smMat.value.multiplyMatrices(lightCam.projectionMatrix, lightCam.matrixWorldInverse);
    U.smTexel.value = 1 / SM; U.smBlur.value = (S.blur ?? (0.003 + 0.006 * box.r)) / (2 * box.r / SM);
    U.smBias.value = 0.0015 + 0.0035 * box.r;
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
if (!q.has('shots')) { const { ui } = await import('./ui.js'); ui(window.A, canvas); }
