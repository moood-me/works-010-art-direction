// The 3D figure of a С5 («инди») character — the part every character of the style shares, taken from Вера's page
// (to3d/r4-s5-vera/tools/web/vera.js) and split from her own numbers: the drawing's ring stacks as distances, the
// mesher's groups skinned to SOMA's joints, the flat two-tone look with a warm outline, the drawn face carried by the
// head, Kimodo's motions retargeted as experiments/indie does, the scene and the camera.
// A character's file (tim.js) gives its numbers as `def` and calls start(def); then window.A.set({...}) sets what is
// shown and window.A.render() draws (see shots.mjs).
import * as THREE from 'three';
import { lerp, clamp, smooth, smin, sub, surfaceNets } from './forms.js';
import { FaceLive } from './live.js';

// ———————————— the drawing's units → metres ————————————
// the drawing: units, y down, the ground at y = 0. Here: metres, y up, 1 unit = 2.5 mm (the same for the whole cast)
export const S = 1 / 400;
export const P = (X, Y, Z = 0) => [X * S, -Y * S, Z * S];
export const hex = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255);
const mixc = (a, b, t) => a.map((x, i) => x + (b[i] - x) * t);
const shadeOf = h => mixc(hex(h), hex('#2a1f3d'), 0.28);   // geo.shade_of: darker, toward violet

// ———————————— a stack of elliptic rings (the drawing's volume) as a distance ————————————
const cr = (a, b, c, d, t) => 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t * t * t);
export function ringTable(rings, out = 0) {
  let R = rings.map(r => [r[0], r[1], r[2], r[3] || 0, r[4] || 0]);
  if (out) { R = R.map(r => [r[0], r[1] ? r[1] + out : 0, r[2] ? r[2] + out : 0, r[3], r[4]]); R[0][0] -= out; }
  // smooth through the rings as the drawing's outline does (Catmull-Rom), then a dense table along y
  const D = [];
  for (let i = 0; i < R.length - 1; i++) {
    const p0 = R[Math.max(i - 1, 0)], p1 = R[i], p2 = R[i + 1], p3 = R[Math.min(i + 2, R.length - 1)];
    for (let j = 0; j < 16; j++) D.push(p1.map((_, k) => cr(p0[k], p1[k], p2[k], p3[k], j / 16)));
  }
  D.push(R[R.length - 1].slice());
  for (let i = 1; i < D.length; i++) D[i][0] = Math.max(D[i][0], D[i - 1][0] + 1e-4);
  for (const d of D) { d[1] = Math.max(d[1], 0); d[2] = Math.max(d[2], 0); }
  const y0 = D[0][0], y1 = D[D.length - 1][0], N = 400, T = new Float32Array(N * 4);
  let j = 0;
  for (let i = 0; i < N; i++) {
    const y = y0 + (y1 - y0) * i / (N - 1);
    while (j < D.length - 2 && D[j + 1][0] < y) j++;
    const a = D[j], b = D[j + 1], t = clamp((y - a[0]) / (b[0] - a[0]), 0, 1);
    for (let k = 0; k < 4; k++) T[i * 4 + k] = lerp(a[k + 1], b[k + 1], t);
  }
  const at = y => { const f = clamp((y - y0) / (y1 - y0), 0, 1) * (N - 1), i = Math.min(Math.floor(f), N - 2), t = f - i; return [0, 1, 2, 3].map(k => lerp(T[i * 4 + k], T[i * 4 + 4 + k], t)); };
  return { y0, y1, at };
}
// o: where the stack's own (0,0,0) is, in drawing units
export function rings(rs, { out = 0, o = [0, 0, 0] } = {}) {
  const tb = ringTable(rs, out), dy = (tb.y1 - tb.y0) / 399;
  return (x, y, z) => {
    const X = x / S - o[0], Y = -y / S - o[1], Z = z / S - o[2];
    const Yc = clamp(Y, tb.y0, tb.y1), [w, d, cx, cz] = tb.at(Yc);
    const px = X - cx, pz = Z - cz, W = Math.max(w, 0.3), Dd = Math.max(d, 0.3);
    const k0 = Math.hypot(px / W, pz / Dd), k1 = Math.hypot(px / (W * W), pz / (Dd * Dd));
    let dh = k1 < 1e-9 ? -Math.min(W, Dd) : k0 * (k0 - 1) / k1;
    if (Y < tb.y0 || Y > tb.y1) return Math.hypot(Math.max(dh, 0), Y - Yc) * S;
    // a slanted wall: the level distance is longer than the true one
    const a = tb.at(Yc - 2 * dy), b = tb.at(Yc + 2 * dy), sl = Math.max(Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1])) / (4 * dy);
    return dh / Math.hypot(1, sl) * S;
  };
}
// a point on a ring stack at angle phi (0 = front, + toward +X) and height y, pushed out by `out` (geo.surf)
export function surf(tb, phi, y, out = 0, o = [0, 0, 0]) {
  const [w, d, cx, cz] = tb.at(y);
  return [o[0] + cx + (w + out) * Math.sin(phi), o[1] + y, o[2] + cz + (d + out) * Math.cos(phi)];
}

// a line round the head: keys (phi, y), closed, smoothed as the drawing smooths it (a hairline, a cap's edge)
export function lineRound(K) {
  const ext = [...K.map(([p, y]) => [p - 2 * Math.PI, y]), ...K, ...K.map(([p, y]) => [p + 2 * Math.PI, y])];
  const D = [];
  for (let i = 1; i < ext.length - 2; i++) for (let j = 0; j < 8; j++) D.push([0, 1].map(k => cr(ext[i - 1][k], ext[i][k], ext[i + 1][k], ext[i + 2][k], j / 8)));
  D.sort((a, b) => a[0] - b[0]);
  const at = phi => { let i = 0; while (i < D.length - 2 && D[i + 1][0] < phi) i++; const a = D[i], b = D[i + 1]; return lerp(a[1], b[1], clamp((phi - a[0]) / (b[0] - a[0]), 0, 1)); };
  const N = 1440, T = new Float32Array(N + 1);
  for (let i = 0; i <= N; i++) T[i] = at(-Math.PI + 2 * Math.PI * i / N);
  return phi => { const f = (phi + Math.PI) / (2 * Math.PI) * N, i = clamp(Math.floor(f), 0, N - 1); return lerp(T[i], T[i + 1], f - i); };
}
// SOMA's joints (no fingers) and their parents
export const PARENT = {
  Hips: null, Spine1: 'Hips', Spine2: 'Spine1', Chest: 'Spine2', Neck1: 'Chest', Neck2: 'Neck1', Head: 'Neck2', HeadEnd: 'Head', Jaw: 'Head', LeftEye: 'Head', RightEye: 'Head',
  LeftShoulder: 'Chest', LeftArm: 'LeftShoulder', LeftForeArm: 'LeftArm', LeftHand: 'LeftForeArm',
  RightShoulder: 'Chest', RightArm: 'RightShoulder', RightForeArm: 'RightArm', RightHand: 'RightForeArm',
  LeftLeg: 'Hips', LeftShin: 'LeftLeg', LeftFoot: 'LeftShin', LeftToeBase: 'LeftFoot', LeftToeEnd: 'LeftToeBase',
  RightLeg: 'Hips', RightShin: 'RightLeg', RightFoot: 'RightShin', RightToeBase: 'RightFoot', RightToeEnd: 'RightToeBase',
};
export const BONES = Object.keys(PARENT), BI = Object.fromEntries(BONES.map((b, i) => [b, i]));
// weights along a chain of joints by height (a shirt, a coat): each point between the two nearest joints
export const chain = (J, names) => (x, y) => {
  const hs = names.map(n => J[n][1]);
  if (y <= hs[0]) return { [names[0]]: 1 };
  for (let i = 0; i < names.length - 1; i++) if (y <= hs[i + 1]) { const t = smooth((y - hs[i]) / (hs[i + 1] - hs[i])); return { [names[i]]: 1 - t, [names[i + 1]]: t }; }
  return { [names[names.length - 1]]: 1 };
};

// ———————————— the look: the drawing's flat paint and one shade, light from the upper left (held to the view, as a
// drawing's is), a warm outline around each big form ————————————
const VS = `
#include <common>
#include <skinning_pars_vertex>
attribute vec3 shade; attribute float fmask; attribute vec3 hp; uniform float uFloor;
varying vec3 vN; varying vec3 vC; varying vec3 vS; varying vec2 vUv; varying float vM; varying vec3 vHp;
void main() {
  #include <skinbase_vertex>
  #include <beginnormal_vertex>
  #include <skinnormal_vertex>
  #include <defaultnormal_vertex>
  #include <begin_vertex>
  #include <skinning_vertex>
  transformed.y = max(transformed.y, uFloor);
  #include <project_vertex>
  vN = normalize(transformedNormal); vC = color; vS = shade; vUv = uv; vM = fmask; vHp = hp;
}`;
// the face: the drawing turns the face on the head a little further than the skull (cast.fs: 0.38·sin(yaw)), so that
// in three-quarter and profile it doesn't sink into the edge. uCheat is that turn for the eye that looks now: the
// drawn signs slide round the head by it (hp: the place's angle round the head, the head's half-width there, its
// middle). With uCheat = 0 the face lies on the head as projected from the front
const FS = `
uniform vec3 uL; uniform float uThr; uniform sampler2D uFace; uniform float uUseFace; uniform float uMode; uniform float uCheat; uniform vec2 uFx;
varying vec3 vN; varying vec3 vC; varying vec3 vS; varying vec2 vUv; varying float vM; varying vec3 vHp;
void main() {
  vec3 n = normalize(vN); if (!gl_FrontFacing) n = -n;
  float l = dot(n, normalize(uL));
  vec3 c;
  if (uMode > 0.5) { c = vec3(0.86, 0.82, 0.77) * (0.55 + 0.45 * max(l, 0.0)) + vec3(0.06); }
  else {
    float e = fwidth(l) * 1.2;
    c = mix(vS, vC, smoothstep(uThr - e, uThr + e, l));
    if (uUseFace > 0.5 && vM > 0.0) {
      float pa = vHp.x + uCheat * clamp(2.6 - abs(vHp.x), 0.0, 1.0);
      vec2 uv = vec2((vHp.z + vHp.y * sin(pa) - uFx.x) / uFx.y, vUv.y);
      vec4 f = texture2D(uFace, uv);
      // the drawn face fades where the head turns away from the eye, so signs don't creep round its edge
      c = mix(c, f.rgb, f.a * vM * smoothstep(0.0, 0.22, cos(pa)) * smoothstep(0.08, 0.3, n.z));
    }
  }
  gl_FragColor = vec4(c, 1.0);
}`;
const LVS = `
#include <common>
#include <skinning_pars_vertex>
uniform float uW; uniform float uFloor;
void main() {
  #include <skinbase_vertex>
  #include <beginnormal_vertex>
  #include <skinnormal_vertex>
  #include <begin_vertex>
  #include <skinning_vertex>
  transformed += normalize(objectNormal) * uW;
  transformed.y = max(transformed.y, uFloor);
  #include <project_vertex>
}`;
const LFS = `uniform vec3 uCol; void main() { gl_FragColor = vec4(uCol, 1.0); }`;
const minJerk = t => t * t * t * (10 - 15 * t + 6 * t * t);

// def: the character — see tim.js for every field
export function start(def) {
  const C = def.C, HEAD_Y = def.HEAD_Y, HO = [0, HEAD_Y, 0], headT = ringTable(def.HEAD), FACE = def.face;
  const [FX0, FY0, FW, FH] = FACE.rect;
  const J = Object.fromEntries(Object.entries(def.JU).map(([b, p]) => [b, P(...p)]));
  // the head's own frame in the rest pose (a head drawn pushed forward and bowed has its own): world metres → the
  // head's drawing units, and back for directions
  const headInv = def.headInv || ((x, y, z) => [x / S, -y / S - HEAD_Y, z / S]);
  const headDir = def.headDir || (v => v);                     // a direction in the head's frame → the rest pose's
  const headUnDir = def.headUnDir || (v => v);
  const headC = def.headC ? P(...def.headC) : P(0, HEAD_Y, 0);  // the head's centre, rest pose

  // ———————————— building: one mesh per group, skinned to its bones (the constructor's buildParts, with weights by
  // height for long things, a shade paint per part, and the face's place on the head) ————————————
  function build(parts) {
    const groups = {};
    for (const p of parts) (groups[p[0]] ??= []).push(p);
    const out = [], B = def.bounds;
    for (const [g, ps] of Object.entries(groups)) {
      const k = def.BLEND[g] ?? 0.6 * S;
      const sdf = (x, y, z) => { let d = 1e9; for (const p of ps) { const v = p[2](x, y, z); d = d === 1e9 ? v : smin(d, v, k); } return d; };
      const lo = [1e9, 1e9, 1e9], hi = [-1e9, -1e9, -1e9], st = 0.012;
      for (let x = B[0][0]; x <= B[1][0]; x += st) for (let y = B[0][1]; y <= B[1][1]; y += st) for (let z = B[0][2]; z <= B[1][2]; z += st)
        if (sdf(x, y, z) < st) { lo[0] = Math.min(lo[0], x); lo[1] = Math.min(lo[1], y); lo[2] = Math.min(lo[2], z); hi[0] = Math.max(hi[0], x); hi[1] = Math.max(hi[1], y); hi[2] = Math.max(hi[2], z); }
      if (lo[0] > hi[0]) { console.warn('nothing of', g); continue; }
      const m = surfaceNets(sdf, lo.map(v => v - 2 * st), hi.map(v => v + 2 * st), def.GRID[g] ?? 0.003);
      const nv = m.pos.length / 3;
      const si = new Uint16Array(nv * 4), sw = new Float32Array(nv * 4), col = new Float32Array(nv * 3), shd = new Float32Array(nv * 3);
      const cols = ps.map(p => hex(p[3])), shs = ps.map(p => p[4] ? hex(p[4]) : shadeOf(p[3]));
      const acc = new Float32Array(BONES.length);
      for (let v = 0; v < nv; v++) {
        const x = m.pos[v * 3], y = m.pos[v * 3 + 1], z = m.pos[v * 3 + 2];
        const ds = ps.map(p => p[2](x, y, z)), dmin = Math.min(...ds);
        acc.fill(0);
        ps.forEach((p, i) => {
          const w = Math.exp(-Math.max(ds[i] - dmin, 0) / 0.012);
          if (typeof p[1] === 'function') { for (const [b, t] of Object.entries(p[1](x, y, z))) acc[BI[b]] += w * t; }
          else if (Array.isArray(p[1])) {
            const [b0, b1] = p[1], a = J[b0], j = J[b1], e = J[b1.replace('Shin', 'Foot').replace('ForeArm', 'Hand')];
            const L = Math.hypot(...sub(e, a)), t = ((x - a[0]) * (e[0] - a[0]) + (y - a[1]) * (e[1] - a[1]) + (z - a[2]) * (e[2] - a[2])) / (L * L);
            const tj = Math.hypot(...sub(j, a)) / L, f = smooth(clamp((t - tj) / 0.24 + 0.5, 0, 1));
            acc[BI[b0]] += w * (1 - f); acc[BI[b1]] += w * f;
          } else acc[BI[p[1]]] += w;
        });
        const order = [...acc.keys()].sort((a, b) => acc[b] - acc[a]).slice(0, 4);
        let s = 0; for (const b of order) s += acc[b];
        order.forEach((b, i) => { si[v * 4 + i] = b; sw[v * 4 + i] = acc[b] / s; });
        const c = [0, 0, 0], h = [0, 0, 0]; let ws = 0;
        ps.forEach((p, i) => { const w = Math.exp(-Math.max(ds[i] - dmin, 0) / 0.0015); for (let q = 0; q < 3; q++) { c[q] += cols[i][q] * w; h[q] += shs[i][q] * w; } ws += w; });
        for (let q = 0; q < 3; q++) { col[v * 3 + q] = c[q] / ws; shd[v * 3 + q] = h[q] / ws; }
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(m.pos, 3));
      geo.setAttribute('normal', new THREE.BufferAttribute(m.nor, 3));
      geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
      geo.setAttribute('shade', new THREE.BufferAttribute(shd, 3));
      geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(si, 4));
      geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));
      // the face's place: the height in the texture, and round the head — the angle, the half-width, the middle
      const uv = new Float32Array(nv * 2), fm = new Float32Array(nv), hp = new Float32Array(nv * 3);
      if (g === 'head') for (let v = 0; v < nv; v++) {
        const [X, Y, Z] = headInv(m.pos[v * 3], m.pos[v * 3 + 1], m.pos[v * 3 + 2]);
        const nz = headUnDir([m.nor[v * 3], m.nor[v * 3 + 1], m.nor[v * 3 + 2]])[2];
        const [w, d, cx, cz] = headT.at(clamp(Y, headT.y0, headT.y1));
        uv[v * 2] = (X - FX0) / FW; uv[v * 2 + 1] = 1 - (Y - FY0) / FH; fm[v] = smooth(clamp((nz + 0.25) / 0.3, 0, 1));
        hp[v * 3] = Math.atan2((X - cx) / Math.max(w, 1), (Z - cz) / Math.max(d, 1)); hp[v * 3 + 1] = Math.hypot(X - cx, (Z - cz) * w / Math.max(d, 1)); hp[v * 3 + 2] = cx;
      }
      geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
      geo.setAttribute('fmask', new THREE.BufferAttribute(fm, 1));
      geo.setAttribute('hp', new THREE.BufferAttribute(hp, 3));
      geo.setIndex(nv > 65535 ? new THREE.Uint32BufferAttribute(m.idx, 1) : new THREE.Uint16BufferAttribute(m.idx, 1));
      out.push({ g, geo });
    }
    return out;
  }

  // nothing goes under the floor: what would (sitting on the ground) lies on it
  const FLOOR = { value: -0.003 };
  const LIGHT = new THREE.Vector3(-0.42, 0.3, 0.86);
  function bodyMat(face) {
    return new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, vertexColors: true, extensions: { derivatives: true },
      uniforms: { uFloor: FLOOR, uL: { value: LIGHT }, uThr: { value: 0.28 }, uFace: { value: face || null }, uUseFace: { value: face ? 1 : 0 }, uMode: { value: 0 }, uCheat: { value: 0 }, uFx: { value: new THREE.Vector2(FX0, FW) } } });
  }
  const LINE_MAT = new THREE.ShaderMaterial({ vertexShader: LVS, fragmentShader: LFS, side: THREE.BackSide, uniforms: { uFloor: FLOOR, uW: { value: 2.1 * S }, uCol: { value: new THREE.Color().setRGB(...hex(C.line)) } } });
  // thin things get a thin line of their own
  const THIN_MAT = LINE_MAT.clone(); THIN_MAT.uniforms.uFloor = FLOOR; THIN_MAT.uniforms.uW = { value: 1.2 * S }; THIN_MAT.uniforms.uCol = LINE_MAT.uniforms.uCol;
  const NO_LINE = def.NO_LINE || new Set(), THIN = def.THIN || new Set(), FREE = def.FREE || new Set(), HOLD = def.HOLD || new Set();

  // ———————————— the scene ————————————
  const cv = document.getElementById('cv');
  const renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.LinearSRGBColorSpace;   // paints go to the screen as written
  const scene = new THREE.Scene();
  const BG = '#ece5d9';
  scene.background = new THREE.Color().setRGB(...hex(BG));
  // the floor fades into the background far off, as a drawing's ground does
  scene.fog = new THREE.Fog(new THREE.Color().setRGB(...hex(BG)), 3.5, 9);
  const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 50), persp = new THREE.PerspectiveCamera(22, 1, 0.05, 60);
  let camera = ortho;
  // a soft round shadow under the figure (the drawing's ground ellipse); a quiet floor of big tiles for scenes in motion
  const shadowMat = new THREE.MeshBasicMaterial({ color: new THREE.Color().setRGB(...hex('#2a1f3d')), transparent: true, opacity: 0.13, depthWrite: false });
  const floor = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');
    g.fillStyle = '#e6dece'; g.fillRect(0, 0, 256, 256); g.strokeStyle = '#d8cebd'; g.lineWidth = 3; g.strokeRect(0, 0, 256, 256);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(800, 800); t.anisotropy = 8;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshBasicMaterial({ map: t, fog: true }));
    m.rotation.x = -Math.PI / 2; m.position.y = -0.0005; m.visible = false; scene.add(m);
    return m;
  })();
  const MESHES = build(def.parts(J));

  // the face: drawn on a canvas each time it changes (face.js), carried by the head
  const FPX = 6;
  let faceSW = 2.4;
  function faceCanvas() {
    const c = document.createElement('canvas'); c.width = FW * FPX; c.height = FH * FPX;
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace; t.anisotropy = 4;
    return { c, g: c.getContext('2d'), t };
  }

  function instance(free) {
    const bones = {}, root = new THREE.Group();
    for (const b of BONES) { bones[b] = new THREE.Bone(); bones[b].name = b; }
    for (const b of BONES) { const p = PARENT[b], pp = p ? J[p] : [0, 0, 0]; bones[b].position.set(...sub(J[b], pp)); if (p) bones[p].add(bones[b]); else root.add(bones[b]); }
    const skel = new THREE.Skeleton(BONES.map(b => bones[b]));
    root.updateMatrixWorld(true); skel.calculateInverses();
    const fc = faceCanvas();
    const meshes = [], outlines = [], mats = [];
    let headMat = null;
    for (const { g, geo } of MESHES) {
      if ((free ? HOLD : FREE).has(g)) continue;
      const mat = bodyMat(g === 'head' ? fc.t : null); mats.push(mat); if (def.THR && def.THR[g] !== undefined) mat.uniforms.uThr.value = def.THR[g]; if (g === 'head') headMat = mat;
      const m = new THREE.SkinnedMesh(geo, mat); m.frustumCulled = false; m.bind(skel); m.userData.g = g; root.add(m); meshes.push(m);
      if (!NO_LINE.has(g)) { const o = new THREE.SkinnedMesh(geo, THIN.has(g) ? THIN_MAT : LINE_MAT); o.frustumCulled = false; o.bind(skel); root.add(o); outlines.push(o); }
    }
    const shadow = new THREE.Mesh(new THREE.CircleGeometry(1, 48), shadowMat); shadow.rotation.x = -Math.PI / 2; shadow.scale.set(def.shadow[0] * S, def.shadow[1] * S, 1); shadow.position.y = 0.001; shadow.renderOrder = -1;
    scene.add(shadow);
    return { root, bones, meshes, outlines, mats, headMat, shadow, fc, free };
  }
  function drawFaceOn(I, F) { FACE.drawFace(I.fc.g, F, FPX, faceSW); I.fc.t.needsUpdate = true; I.lastF = F; }

  // ———————————— Kimodo's motions (experiments/indie's retargeting): each SOMA joint turns as in the motion, a fixed
  // turn first brings our bone to SOMA's rest direction; the pelvis goes as high and as far as our legs make it; the
  // feet are put back on the floor. Arms that are not free take no turns of their own and go with the chest; free,
  // they turn as SOMA's, kept off the body and out of the big head ————————————
  const MOTION = {};
  const motion = name => MOTION[name] ??= fetch(`../motions/${name}.json`).then(r => r.json()).then(prepare);
  const CHAIN = { LeftLeg: 'LeftShin', LeftShin: 'LeftFoot', LeftFoot: 'LeftToeBase', RightLeg: 'RightShin', RightShin: 'RightFoot', RightFoot: 'RightToeBase',
    LeftShoulder: 'LeftArm', LeftArm: 'LeftForeArm', LeftForeArm: 'LeftHand', LeftHand: 'LeftHandMiddle1', RightShoulder: 'RightArm', RightArm: 'RightForeArm', RightForeArm: 'RightHand', RightHand: 'RightHandMiddle1' };
  const ARM = /Shoulder|Arm|Hand/;
  function prepare(M) {
    M.C = Object.fromEntries(Object.entries(CHAIN).map(([b, c]) => {
      const ours = /Hand$/.test(b) ? sub(J[b], J[PARENT[b]]) : sub(J[c], J[b]);
      return [b, new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(...ours).normalize(), new THREE.Vector3(...sub(M.rest[c], M.rest[b])).normalize())];
    }));
    // where the head points, every frame (degrees, in the motion's own frame): for the eyes to lead it
    const fw = new THREE.Vector3(), q = new THREE.Quaternion();
    M.hyaw = new Float32Array(M.n); M.hpitch = new Float32Array(M.n);
    // how far the chest leans forward on average (Kimodo's waiting motion stoops by ~25°)
    let lean = 0;
    for (let f = 0; f < M.n; f++) { const d = M.D.Chest; q.set(d[f * 4], d[f * 4 + 1], d[f * 4 + 2], d[f * 4 + 3]); fw.set(0, 0, 1).applyQuaternion(q); lean += Math.asin(clamp(fw.y, -1, 1)) * 180 / Math.PI; }
    M.lean = lean / M.n;
    for (let f = 0; f < M.n; f++) { const d = M.D.Head; q.set(d[f * 4], d[f * 4 + 1], d[f * 4 + 2], d[f * 4 + 3]); fw.set(0, 0, 1).applyQuaternion(q); M.hyaw[f] = Math.atan2(fw.x, fw.z) * 180 / Math.PI; M.hpitch[f] = Math.asin(clamp(fw.y, -1, 1)) * 180 / Math.PI; }
    return M;
  }
  const _qa = new THREE.Quaternion(), _qb = new THREE.Quaternion(), _v = new THREE.Vector3(), _w = new THREE.Vector3();
  function dq(M, b, f) { // a joint's turn at a fractional frame
    const d = M.D[b], i = Math.floor(f), j = Math.min(i + 1, M.n - 1), t = f - i;
    _qa.set(d[i * 4], d[i * 4 + 1], d[i * 4 + 2], d[i * 4 + 3]); _qb.set(d[j * 4], d[j * 4 + 1], d[j * 4 + 2], d[j * 4 + 3]);
    return _qa.clone().slerp(_qb, t);
  }
  const hipsAt = (M, f, k) => { const i = Math.floor(f), j = Math.min(i + 1, M.n - 1), t = f - i; return lerp(M.hips[i * 3 + k], M.hips[j * 3 + k], t); };
  const atF = (arr, f, n) => { const i = Math.floor(clamp(f, 0, n - 1)), j = Math.min(i + 1, n - 1); return lerp(arr[i], arr[j], clamp(f, 0, n - 1) - i); };
  const restPos = b => { const p = PARENT[b]; return sub(J[b], p ? J[p] : [0, 0, 0]); };
  function setLocal(I, W) { for (const b of BONES) { const p = PARENT[b]; if (W[b]) I.bones[b].quaternion.copy(p ? W[p].clone().invert().multiply(W[b]) : W[b]); } I.root.updateMatrixWorld(true); }
  const UPPER = new Set(BONES.filter(b => { for (let p = b; p; p = PARENT[p]) if (p === 'Spine1') return true; return false; }));
  const GROUND = new Set(def.GROUND || ['shoes', 'legs']);
  // look: an extra turn of the head about the upright, split between the neck (40 %) and the head (60 %), degrees
  function poseFromMotion(I, M, f, travel, look = 0, offset = [0, 0], upright = 0) {
    const W = {};
    for (const b of BONES) {
      const p = PARENT[b];
      let w;
      if (M.D[b] && (I.free || !ARM.test(b))) { w = dq(M, b, f); if (M.C[b]) w.multiply(M.C[b]); }
      else w = p ? W[p].clone() : new THREE.Quaternion();
      if (look && (b === 'Neck2' || b === 'Head')) w.premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), look * (b === 'Head' ? 1 : 0.4) * Math.PI / 180));
      W[b] = w;
    }
    // upright: the clip's average stoop taken out (the whole upper body turned back about the waist), its movement kept
    if (upright && M.lean) {
      const ax = new THREE.Vector3(1, 0, 0).applyQuaternion(W.Hips), fix = new THREE.Quaternion().setFromAxisAngle(ax, upright * M.lean * Math.PI / 180);
      for (const b of UPPER) W[b].premultiply(fix);
    }
    if (I.free) {
      // arms off the body: the upper arm keeps out to its side
      for (const [s, k] of [['Left', 1], ['Right', -1]]) {
        const side = _w.set(k, 0, 0).applyQuaternion(W.Chest);
        const d2 = new THREE.Vector3(...sub(M.rest[s + 'ForeArm'], M.rest[s + 'Arm'])).normalize().applyQuaternion(dq(M, s + 'Arm', f));
        const out = d2.dot(side), need = def.armOut ?? 0.42;
        if (out < need) { const ax = new THREE.Vector3().crossVectors(d2, side).normalize(), fix = new THREE.Quaternion().setFromAxisAngle(ax, Math.asin(need) - Math.asin(Math.max(-1, out))); for (const b of [s + 'Arm', s + 'ForeArm', s + 'Hand']) if (W[b]) W[b].premultiply(fix); }
      }
    }
    setLocal(I, W);
    if (I.free) {
      // and out of the big head: a hand or elbow that would go into it swings the arm outward until it clears
      const head = new THREE.Vector3(), hp = new THREE.Vector3(), fwd = new THREE.Vector3(), R = def.headR * S;
      for (const [s, k] of [['Left', 1], ['Right', -1]]) for (let it = 0; it < 14; it++) {
        I.bones.Head.updateWorldMatrix(true, false); head.set(...sub(headC, J.Head)).applyMatrix4(I.bones.Head.matrixWorld);
        let inside = false;
        for (const b of [s + 'Hand', s + 'ForeArm']) { I.bones[b].getWorldPosition(hp); if (hp.distanceTo(head) < R + 10 * S) inside = true; }
        if (!inside) break;
        fwd.set(0, 0, 1).applyQuaternion(W.Chest);
        const fix = new THREE.Quaternion().setFromAxisAngle(fwd, k * -0.12);
        for (const b of [s + 'Arm', s + 'ForeArm', s + 'Hand']) if (W[b]) W[b].premultiply(fix);
        setLocal(I, W);
      }
    }
    const kr = J.Hips[1] / M.hipY;
    I.bones.Hips.position.set(travel ? (hipsAt(M, f, 0) - M.hips[0]) * kr + offset[0] : 0, hipsAt(M, f, 1) * kr, travel ? (hipsAt(M, f, 2) - M.hips[2]) * kr + offset[1] : 0);
    I.root.updateMatrixWorld(true);
    let low = 1e9;
    for (const m of I.meshes) {
      if (!GROUND.has(m.userData.g)) continue;
      const pos = m.geometry.attributes.position;
      for (let i = 0; i < pos.count; i += 5) { _v.fromBufferAttribute(pos, i); m.applyBoneTransform(i, _v); _v.applyMatrix4(m.matrixWorld); if (_v.y < low) low = _v.y; }
    }
    I.bones.Hips.position.y += atF(M.foot, f, M.n) * kr - (low - I.root.position.y) + 0.5 * S;
    I.root.updateMatrixWorld(true);
  }
  // the head's tilt on each expression of the sheet (the drawing: rotate(tilt) about the head's centre, clockwise)
  const TILT = def.TILT, TILT0 = def.tiltRest ?? 0;
  const tiltOf = w => { let s = 0, t = 0; for (const [k, v] of Object.entries(w)) { s += v; t += v * (TILT[k] ?? 0); } return s ? t / s : TILT.neutral; };
  const tiltAxis = new THREE.Vector3(...headDir([0, 0, 1])).normalize(), tiltC = new THREE.Vector3(...sub(headC, J.Head));

  // ———————————— clips: Kimodo's motions as they are, and a look round (the waiting motion with the head turned to
  // one side and the other, as a person looks: a quick turn with a smooth start and stop, a rest, the next) ————————————
  const LOOK_KEYS = def.LOOK_KEYS || [[0, 0], [0.9, 0], [1.45, -50], [2.5, -50], [3.15, 42], [4.0, 42], [4.6, 8], [5.0, 8]];
  function lookAt(t) {
    const K = LOOK_KEYS;
    if (t <= K[0][0]) return K[0][1];
    for (let i = 0; i < K.length - 1; i++) if (t <= K[i + 1][0]) return lerp(K[i][1], K[i + 1][1], minJerk((t - K[i][0]) / (K[i + 1][0] - K[i][0])));
    return K[K.length - 1][1];
  }
  const CLIPS = def.CLIPS;

  // ———————————— what is shown ————————————
  let placed = [], overlay = null;
  const state = { view: 'style', cheat: def.cheat ?? 0.38 };
  // a figure: {x, z, yaw (deg), ex | exprW, clip | motion, f, travel, free, live, talk, seed, shadow}
  async function place(F) {
    const clip = CLIPS[F.clip || 'stand'] || {}, mo = F.motion || clip.motion, free = F.free ?? clip.free ?? false;
    const I = instance(free);
    I.F = F; I.clip = clip; I.M = mo ? await motion(mo) : null; I.travel = F.travel ?? clip.travel ?? false; I.look = clip.look;
    I.root.position.set((F.x || 0) * S, 0, (F.z || 0) * S); I.root.rotation.y = (F.yaw || 0) * Math.PI / 180;
    scene.add(I.root);
    I.exprW = F.exprW || { [F.ex || 'neutral']: 1 };
    I.shadow.visible = F.shadow !== false;
    if (F.live) { I.live = new FaceLive(FACE, F.seed ?? 11); I.live.setExpr(I.exprW); I.live.x = FACE.mixExpr(I.exprW); I.live.setTalk(!!F.talk); }
    I.tilt = tiltOf(I.exprW);
    return I;
  }
  // pose and face at time t (seconds into the clip), the face stepped by dt
  function update(I, t, dt) {
    const M = I.M;
    let headYaw = 0, headPitch = 0, aheadYaw = 0, aheadPitch = 0;
    for (const b of BONES) I.bones[b].position.set(...restPos(b));
    if (M) {
      const n = M.n, fr = t * M.fps, loop = Math.floor(fr / n), f = fr - loop * n;
      // a clip that travels goes on from where its last loop ended
      const kr = J.Hips[1] / M.hipY, off = I.travel ? [(M.hips[(n - 1) * 3] - M.hips[0]) * kr * loop, (M.hips[(n - 1) * 3 + 2] - M.hips[2]) * kr * loop] : [0, 0];
      const lk = I.look ? lookAt(t % (n / M.fps)) : 0, upr = I.clip.upright || 0;
      poseFromMotion(I, M, f, I.travel, lk, off, upr);
      const fa = Math.min(f + 0.3 * M.fps, n - 1), y0 = M.hyaw[0];
      const up = -upr * M.lean;
      headYaw = atF(M.hyaw, f, n) - y0 + lk; headPitch = atF(M.hpitch, f, n) + up;
      aheadYaw = atF(M.hyaw, fa, n) - y0 + (I.look ? lookAt((t + 0.3) % (n / M.fps)) : 0); aheadPitch = atF(M.hpitch, fa, n) + up;
    } else {
      for (const b of BONES) I.bones[b].quaternion.identity();
      I.root.updateMatrixWorld(true);
    }
    // the head's tilt of the expression, on top: about the head's own centre, as the drawing turns it
    const tilt = I.live ? tiltOf(I.live.target) : I.tilt;
    I.tiltNow = I.live ? lerp(I.tiltNow ?? tilt, tilt, 1 - Math.exp(-dt / 0.15)) : tilt;
    const hb = I.bones.Head, q = new THREE.Quaternion().setFromAxisAngle(tiltAxis, -(I.tiltNow - TILT0) * Math.PI / 180);
    const tr = tiltC.clone().sub(tiltC.clone().applyQuaternion(q)).applyQuaternion(hb.quaternion);
    hb.position.add(tr); hb.quaternion.multiply(q);
    I.root.updateMatrixWorld(true);
    I.bones.Hips.getWorldPosition(_v); I.shadow.position.x = _v.x; I.shadow.position.z = _v.z; I.shadow.position.x = camera === ortho ? I.root.position.x : _v.x;
    if (I.live) { I.live.step(dt, { yaw: headYaw, pitch: headPitch, aheadYaw, aheadPitch }); drawFaceOn(I, I.live.face()); }
    else if (!I.drawn) { drawFaceOn(I, { e: FACE.vecExpr(FACE.mixExpr(I.exprW)) }); I.drawn = true; }
  }
  // the camera: a drawing's viewBox (orthographic, from the front), or a camera at a place, or one that orbits a point
  // on the figure (follow: the point goes with the hips, softly)
  const cam = { yaw: 25, pitch: 6, dist: 3.2, ty: 0.55, fov: 22, follow: false, at: [0, 0.55, 0] };
  function setCam(c) {
    if (c.vb) {
      const [x, y, w, h] = c.vb; camera = ortho;
      Object.assign(ortho, { left: x * S, right: (x + w) * S, top: -y * S, bottom: -(y + h) * S });
      ortho.position.set(0, 0, 10); ortho.lookAt(0, 0, 0); ortho.updateProjectionMatrix();
      layShadows();
      return;
    }
    camera = persp; layShadows();
    if (c.pos) { cam.fixed = c; } else { cam.fixed = null; Object.assign(cam, c); }
    aimCam(true);
  }
  // the ground shadow: a round one on the floor; for a drawing's view from the front (where a floor is seen edge-on),
  // the drawing's flat ellipse behind the feet
  function layShadows() {
    for (const I of placed) {
      const sh = I.shadow, flat = camera === ortho;
      sh.rotation.x = flat ? 0 : -Math.PI / 2; sh.position.y = flat ? -2 * S : 0.001; if (flat) sh.position.z = I.root.position.z - 1;
      sh.scale.set(def.shadow[0] * S, (flat ? def.shadow[0] * 0.16 : def.shadow[1]) * S, 1);
    }
  }
  function aimCam(snap) {
    if (camera !== persp) return;
    persp.aspect = cv.width / cv.height;
    if (cam.fixed) { persp.fov = cam.fixed.fov || 22; persp.position.set(...cam.fixed.pos); persp.lookAt(...cam.fixed.at); persp.updateProjectionMatrix(); return; }
    const I = placed[0];
    let at = [0, cam.ty, 0];
    // followY: how much the aim goes down and up with the hips (sitting down, a jump)
    if (I && cam.follow) { I.bones.Hips.getWorldPosition(_v); at = [_v.x, cam.ty + (cam.followY || 0) * (_v.y - J.Hips[1]), _v.z]; }
    cam.at = snap || !cam.at ? at : cam.at.map((a, i) => lerp(a, at[i], 0.12));
    const yw = cam.yaw * Math.PI / 180, pt = cam.pitch * Math.PI / 180;
    persp.fov = cam.fov;
    persp.position.set(cam.at[0] + cam.dist * Math.sin(yw) * Math.cos(pt), cam.at[1] + cam.dist * Math.sin(pt), cam.at[2] + cam.dist * Math.cos(yw) * Math.cos(pt));
    persp.lookAt(...cam.at);
    // pad: pixels at the bottom covered by the viewer's controls; the picture is centred in what is left above them
    if (cam.pad) persp.setViewOffset(cv.width, cv.height + cam.pad, 0, cam.pad, cv.width, cv.height); else persp.clearViewOffset();
    persp.updateProjectionMatrix();
  }
  async function set(o) {
    if (o.size) { renderer.setSize(o.size[0], o.size[1], false); cv.style.width = o.size[0] + 'px'; cv.style.height = o.size[1] + 'px'; }
    if (o.view) state.view = o.view;
    if (o.cheat !== undefined) state.cheat = o.cheat;
    if (o.floor !== undefined) floor.visible = o.floor;
    // line: the outline's width in drawing units (the drawing: 2.4 on a figure, 2.0 on the expression sheet, 1.35 on
    // the portrait); the face's lines go with it
    if (o.line) { LINE_MAT.uniforms.uW.value = o.line * S; THIN_MAT.uniforms.uW.value = o.line * 0.57 * S; faceSW = 2.4 * o.line / 2.1; for (const I of placed) if (I.lastF) drawFaceOn(I, I.lastF); }
    if (o.figures) {
      for (const I of placed) { scene.remove(I.root); scene.remove(I.shadow); I.fc.t.dispose(); for (const m of I.mats) m.dispose(); }
      placed = [];
      for (const F of o.figures) { const I = await place(F); update(I, F.t ?? (F.f || 0) / (I.M ? I.M.fps : 30), 0); placed.push(I); }
    }
    if (o.cam) setCam(o.cam);
    layShadows();
    applyView();
  }
  function applyView() {
    for (const I of placed) {
      for (const m of I.meshes) m.visible = state.view !== 'skel';
      I.shadow.visible = I.F.shadow !== false && state.view !== 'skel';
      for (const m of I.mats) m.uniforms.uMode.value = state.view === 'clay' ? 1 : 0;
      for (const m of I.mats) if (m.uniforms.uFace.value) m.uniforms.uUseFace.value = state.view === 'style' || state.view === 'bones' ? 1 : 0;
      for (const o2 of I.outlines) o2.visible = state.view !== 'clay' && state.view !== 'skel';
    }
    bonesView(state.view === 'bones' || state.view === 'skel');
  }
  // a moment of a film or of the viewer: {t (seconds), dt, expr: weights | name, talk}
  function frame(o) {
    for (const I of placed) {
      if (I.live) { if (o.expr) I.live.setExpr(o.expr); if (o.talk !== undefined) I.live.setTalk(o.talk); }
      update(I, o.t ?? 0, o.dt ?? 1 / 30);
    }
    aimCam(false);
    if (overlay) bonesView(true);
  }
  // the skeleton drawn over the figure
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
    const ln = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: '#c8413b', depthTest: false, transparent: true }));
    const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.Float32BufferAttribute(d, 3));
    const pt = new THREE.Points(pg, new THREE.PointsMaterial({ color: '#c8413b', size: 7, sizeAttenuation: false, depthTest: false, transparent: true }));
    ln.renderOrder = pt.renderOrder = 10;
    overlay.add(ln, pt); scene.add(overlay);
  }
  // the face's turn on the head for the eye that looks now (see the shader), then the picture
  const _c = new THREE.Vector3(), _h = new THREE.Vector3(), _q = new THREE.Quaternion();
  function render() {
    for (const I of placed) {
      if (!I.headMat) continue;
      I.bones.Head.getWorldQuaternion(_q); _h.copy(tiltC).applyMatrix4(I.bones.Head.matrixWorld);
      if (camera === ortho) _c.set(0, 0, 1); else _c.copy(camera.position).sub(_h).normalize();
      _c.applyQuaternion(_q.invert());
      const l = headUnDir([_c.x, _c.y, _c.z]), n = Math.hypot(l[0], l[2]) || 1;
      I.headMat.uniforms.uCheat.value = state.cheat * -l[0] / n;
    }
    renderer.render(scene, camera);
  }
  window.A = { set, frame, render, cam, setCam, aimCam, S, J, CLIPS, EXPR_RU: def.EXPR_RU, name: def.name, placed: () => placed, renderer, state, applyView, motion };
  window.__ready = true;
}
