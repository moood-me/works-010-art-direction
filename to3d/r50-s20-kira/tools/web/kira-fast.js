// Кира in 3D, drawn every frame as the С20 drawing is drawn (Soviet animation of the 60–70s). The form (tools/build.py's
// pack: shells from the drawing's own numbers on SOMA) moves on the engine's skeleton, skinning and Kimodo retargeting;
// it is never shown shaded. Each frame (the way of Р12, to3d/r12-s12-anya, with this style's medium):
//   1. the figure is rendered once, unseen, into a picture of which paint each pixel belongs to and how far it is;
//   2. paint: the seen part of each colour (hoodie, hair, trousers, boots, lime, the paper of face and hands) as a mask,
//      laid OFF REGISTER — shifted up-right from the line as kit.py's OFF() — under the gouache-streak filter; pencil
//      hatching on the hoodie's shaded side;
//   3. the line: silhouettes (where the surface turns away) and open edges (the hair's choppy edge, a cuff) found on the
//      3D, kept where seen, chained, smoothed and drawn by the drawing's pen (kit.js ink = kit.py ink): pressure —
//      heavier where the contour looks down-right —, thin ends, a wobble;
//   4. the face — ring eyes by the nose with the lid's line, brows, the nose over the contour, the mouth, crayon blush —
//      by face.py's parts in head units, each in its own frame on the turned head;
//   5. lines that belong to the form: the pocket, the hood's strings, laces, the headphones' band, a light line in the hair.
// This is the page's fast variant (fast.html; view.html and kira.js beside it are the page as it was): the unseen
// picture is read back, and the paint's masks are made, only in the figure's rectangle of the picture, not over the
// whole page, and the page does not wait for the video card to give it: the drawing goes on when it has come (so
// A.render() gives a promise, and A.set() waits for a drawing begun before it).
//   fast.html — by hand (ui.js); fast.html?pack=<url> — driven by tools/shots.mjs
//   window.A.set({clip, t, time, pose, expr, talk, cam, …}) then A.render()
import * as THREE from 'three';
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { qBetween, qRot, getQ, getV, normalize, sub } from '../../../../engine/src/math.js';
import * as K from './kit.js';
import { LiveFace } from './face.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack') || '../../data/kira.json', location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const sk = E.skeleton, J = sk.J, I = sk.index;

const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const rest = Float32Array.from(a.positions);
const spec = { skinning: { method: H.skinning || 'dqs', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
const NV = rest.length / 3, TRI = a.triangles, NT = TRI.length / 3;
const NONE = 0xFFFFFFFF, UNIT = H.unit;

// ---------------------------------------------------------------- colours (styles/s20-soviet/tools/kira.py, build.py)
const G = H.groups, BG = '#c9c19a';
const PAINT = {
  [G.skin]: { color: K.SKIN, tex: 'flat', off: true },
  [G.hair]: { color: '#221a24', tex: 'brush', off: true },
  [G.hoodie]: { color: '#4a2c49', tex: 'brush', off: true },
  [G.trousers]: { color: '#2e2c31', tex: 'brush', off: true },
  [G.boot]: { color: '#1c1a1d', tex: 'brush', off: true },
  [G.lime]: { color: '#c9e03b', tex: 'brush', off: true },
  [G.dark]: { color: '#2b2d18', tex: 'flat', off: false },
};

// ---------------------------------------------------------------- the unseen picture: paint group, shade, depth
const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
const g = new THREE.BufferGeometry();
g.setAttribute('position', new THREE.BufferAttribute(fig.positions, 3));
g.setAttribute('normal', new THREE.BufferAttribute(fig.normals, 3));
g.setAttribute('grp', new THREE.BufferAttribute(Float32Array.from(a.grp), 1));
g.setIndex(new THREE.BufferAttribute(a.triangles, 1));
const U = { dn: { value: 0 }, df: { value: 10 }, L: { value: new THREE.Vector3(0, 0, 1) }, show: { value: 0 } };
const idMat = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.DoubleSide,
  vertexShader: `attribute float grp; varying float vG; varying float vD; varying vec3 vN;
    void main() { vG = grp; vN = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position, 1.0); vD = -mv.z; gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `uniform float dn; uniform float df; uniform vec3 L; uniform float show; varying float vG; varying float vD; varying vec3 vN;
    void main() {
      float gg = floor(vG + 0.5);
      vec3 n = normalize(vN); if (n.z < 0.0) n = -n;       // the side we see
      float shade = dot(n, L) < -0.42 ? 16.0 : 0.0;
      float z = clamp((vD - dn) / (df - dn), 0.0, 1.0) * 65535.0;
      float hi = floor(z / 256.0), lo = z - hi * 256.0;
      gl_FragColor = vec4((gg + shade) / 255.0, hi / 255.0, lo / 255.0, 1.0);
      if (show > 0.5) {       // to look at the form itself: each paint its colour, the shaded side darker
        vec3 c = gg < 1.5 ? vec3(0.98, 0.95, 0.9) : gg < 2.5 ? vec3(0.13, 0.1, 0.14) : gg < 3.5 ? vec3(0.29, 0.17, 0.29) : gg < 4.5 ? vec3(0.18, 0.17, 0.19) : gg < 5.5 ? vec3(0.11, 0.1, 0.11) : gg < 6.5 ? vec3(0.79, 0.88, 0.23) : vec3(0.17, 0.18, 0.09);
        float l = 0.62 + 0.38 * clamp(dot(n, normalize(vec3(-0.4, 0.5, 0.75))), 0.0, 1.0);
        gl_FragColor = vec4(c * l + 0.06 * l, 1.0);
      }
    }`,
});
const scene = new THREE.Scene();
scene.background = new THREE.Color(0, 1, 1);           // background: group 0, the farthest depth
const mesh = new THREE.Mesh(g, idMat); mesh.frustumCulled = false; scene.add(mesh);
const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 100);
const persp = new THREE.PerspectiveCamera(24, 1, 0.05, 200);
let camera = ortho, rt = null, buf = null, W = 0, Hh = 0;
// a rectangle of the picture just rendered, taken from the video card without the page waiting for it: copied into a
// buffer on the card, and read when the card says it is done
const gl = renderer.getContext(), pack = gl.createBuffer();
let packSize = 0;
async function readBack(x, y, w, h, out) {
  const n = w * h * 4; if (!n) return;
  gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pack);
  if (n > packSize) { gl.bufferData(gl.PIXEL_PACK_BUFFER, n, gl.STREAM_READ); packSize = n; }
  gl.readPixels(x, y, w, h, gl.RGBA, gl.UNSIGNED_BYTE, 0);
  gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
  const sync = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0); gl.flush();
  while (gl.clientWaitSync(sync, 0, 0) === gl.TIMEOUT_EXPIRED) await new Promise(r => setTimeout(r, 2));
  gl.deleteSync(sync);
  gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pack); gl.getBufferSubData(gl.PIXEL_PACK_BUFFER, 0, out, 0, n); gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
}

// ---------------------------------------------------------------- poses
// The rest is the drawing's stand (build.py). 'act' — the figure sheet's gesture: arms crossed tight, legs crossed.
const aim = (pose, j, c, dir) => { turnUnder(pose, sk, I[j], qBetween(normalize(sub(getV(pose.P, I[c]), getV(pose.P, I[j]))), normalize(dir))); build(pose, body, getV(pose.P, I.Hips)); };
function actPose() {
  const pose = fig.restPose();
  aim(pose, 'LeftArm', 'LeftForeArm', [0.25, -1, 0.5]); aim(pose, 'LeftForeArm', 'LeftHand', [-1, 0.16, 0.42]);
  aim(pose, 'RightArm', 'RightForeArm', [-0.25, -1, 0.42]); aim(pose, 'RightForeArm', 'RightHand', [1, 0.3, 0.62]);
  aim(pose, 'LeftLeg', 'LeftShin', [-0.1, -1, 0.05]); aim(pose, 'LeftShin', 'LeftFoot', [-0.3, -1, 0.02]);
  aim(pose, 'RightLeg', 'RightShin', [0.12, -1, -0.02]); aim(pose, 'RightShin', 'RightFoot', [0.22, -1, -0.08]);
  return pose;
}
// where the head looks over a clip (yaw, pitch at 100 Hz) — for the eyes to lead its turns (Р1's)
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

const S = { clip: null, clipIds: null, t: 0, time: 0, pose: 'stand', lw: 1, seed: 1, boil: false, show: null, mask: 1, ground: true, grain: true, bg: BG,
  cam: { mode: 'ortho', yaw: 0, pitch: 0, cx: 0, cy: 0.81, h: 1.75, dist: 6, target: null, follow: false } };
const face = new LiveFace(Number(q.get('seed') ?? 7));
let clip = null, fp = null;
function frame() {
  fp = face.at(S.time, { headT: S.clip ? S.t / clip.fps : null });
  let pose;
  if (S.clip) { pose = fig.retarget.pose(clip.sample(S.t, fig.sample)); fig.retarget.placed(pose); }
  else pose = S.pose === 'act' ? actPose() : fig.restPose();
  fig.skinner.skin(pose, fig.positions);
  const P = fig.positions; let lo = Infinity; for (let i = 0; i < NT * 3; i++) { const y = P[TRI[i] * 3 + 1]; if (y < lo) lo = y; }
  const shift = (S.clip ? pose.floor : 0) - lo; for (let i = 1; i < P.length; i += 3) P[i] += shift; for (let j = 0; j < J; j++) pose.P[j * 3 + 1] += shift;
  fig.pose = pose;
  g.attributes.position.needsUpdate = true;
}

// ---------------------------------------------------------------- per-frame geometry
const fn = new Float32Array(NT * 3), facing = new Uint8Array(NT), vn = new Float32Array(NV * 3);
const scr = new Float32Array(NV * 3);          // picture x, y and depth
let camPos = [0, 0, 0], viewDir = [0, 0, -1], camR = [1, 0, 0], camU = [0, 1, 0], isOrtho = true;
const mvp = new THREE.Matrix4(), vm = new THREE.Matrix4();
function normals() {
  const P = fig.positions; vn.fill(0);
  for (let t = 0; t < NT; t++) {
    const i = TRI[t * 3] * 3, j = TRI[t * 3 + 1] * 3, k = TRI[t * 3 + 2] * 3;
    const ux = P[j] - P[i], uy = P[j + 1] - P[i + 1], uz = P[j + 2] - P[i + 2], wx = P[k] - P[i], wy = P[k + 1] - P[i + 1], wz = P[k + 2] - P[i + 2];
    const nx = uy * wz - uz * wy, ny = uz * wx - ux * wz, nz = ux * wy - uy * wx;
    fn[t * 3] = nx; fn[t * 3 + 1] = ny; fn[t * 3 + 2] = nz;
    for (const m of [i, j, k]) { vn[m] += nx; vn[m + 1] += ny; vn[m + 2] += nz; }
    let d;
    if (isOrtho) d = -(nx * viewDir[0] + ny * viewDir[1] + nz * viewDir[2]);
    else d = nx * (camPos[0] - P[i]) + ny * (camPos[1] - P[i + 1]) + nz * (camPos[2] - P[i + 2]);
    facing[t] = d > 0 ? 1 : 0;
  }
  for (let i = 0; i < NV; i++) { const l = Math.hypot(vn[i * 3], vn[i * 3 + 1], vn[i * 3 + 2]) || 1; vn[i * 3] /= l; vn[i * 3 + 1] /= l; vn[i * 3 + 2] /= l; }
  fig.normals.set(vn); g.attributes.normal.needsUpdate = true;
}
const e = mvp.elements, ve = vm.elements;
function project(x, y, z, out, o = 0) {
  const w = e[3] * x + e[7] * y + e[11] * z + e[15];
  out[o] = ((e[0] * x + e[4] * y + e[8] * z + e[12]) / w * 0.5 + 0.5) * W;
  out[o + 1] = (1 - ((e[1] * x + e[5] * y + e[9] * z + e[13]) / w * 0.5 + 0.5)) * Hh;
  out[o + 2] = -(ve[2] * x + ve[6] * y + ve[10] * z + ve[14]);
}
function projectAll() { const P = fig.positions; for (let i = 0; i < NV; i++) project(P[i * 3], P[i * 3 + 1], P[i * 3 + 2], scr, i * 3); }
// It is read back only in the figure's rectangle (box: left, top, width, height in the page's pixels); beyond it is
// the background
let box = [0, 0, 0, 0];
function figureBox() {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (let i = 0; i < NV; i++) { const x = scr[i * 3], y = scr[i * 3 + 1]; if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
  const pad = 8;       // what looks beside a point (seen) stays inside
  x0 = Math.max(0, Math.floor(x0) - pad); y0 = Math.max(0, Math.floor(y0) - pad);
  x1 = Math.min(W, Math.ceil(x1) + pad + 1); y1 = Math.min(Hh, Math.ceil(y1) + pad + 1);
  return [x0, y0, Math.max(0, x1 - x0), Math.max(0, y1 - y0)];
}
// where a page's pixel is in the read picture, −1 beyond the rectangle
const bufAt = (x, y) => { x -= box[0]; y -= box[1]; return x < 0 || y < 0 || x >= box[2] || y >= box[3] ? -1 : ((box[3] - 1 - y) * box[2] + x) * 4; };
const depthAt = (x, y) => { const k = bufAt(Math.round(x), Math.round(y));
  if (k < 0 || buf[k] === 0) return Infinity; return U.dn.value + (buf[k + 1] * 256 + buf[k + 2]) / 65535 * (U.df.value - U.dn.value); };
// seen: some pixel round the point is not in front of it
function seen(x, y, z, eps = 0.006, r = 1) {
  for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) if (depthAt(x + dx, y + dy) >= z - eps) return true;
  return false;
}

// ---------------------------------------------------------------- lines on the form
const EV = a.edges, ET = a.edgeTris, EDROP = a.edgeDrop, NE = EV.length / 2;
const vpid = a.pid, PN = H.pieceNames;
function contours() {
  const keep = new Uint8Array(NE), adj = new Map();
  const addAdj = (v, k) => { let l = adj.get(v); if (!l) adj.set(v, l = []); l.push(k); };
  for (let k = 0; k < NE; k++) {
    if (EDROP[k]) continue;
    const f0 = ET[k * 2], f1 = ET[k * 2 + 1], open = f1 === NONE;
    if (!open && facing[f0] === facing[f1]) continue;
    const i = EV[k * 2], j = EV[k * 2 + 1];
    const mx = (scr[i * 3] + scr[j * 3]) / 2, my = (scr[i * 3 + 1] + scr[j * 3 + 1]) / 2, mz = (scr[i * 3 + 2] + scr[j * 3 + 2]) / 2;
    if (!seen(mx, my, mz, open ? 0.004 : 0.006)) continue;
    keep[k] = 1; addAdj(i, k); addAdj(j, k);
  }
  const used = new Uint8Array(NE), chains = [];
  const walk = (k0, v0) => {
    const vs = [v0]; let k = k0, v = v0;
    while (true) {
      used[k] = 1; const w = EV[k * 2] === v ? EV[k * 2 + 1] : EV[k * 2]; vs.push(w);
      const l = adj.get(w); if (!l || l.length !== 2) break;
      const nk = l[0] === k ? l[1] : l[0]; if (used[nk]) break; k = nk; v = w;
    }
    return vs;
  };
  for (const [v, l] of adj) if (l.length !== 2) for (const k of l) if (!used[k]) chains.push(walk(k, v));
  for (let k = 0; k < NE; k++) if (keep[k] && !used[k]) chains.push(walk(k, EV[k * 2]));
  return chains;
}
// how much the contour at a vertex looks down-right in the picture (kit.py: the line is heavier there)
function heavy(v) {
  const nx = vn[v * 3], ny = vn[v * 3 + 1], nz = vn[v * 3 + 2];
  const sx = nx * camR[0] + ny * camR[1] + nz * camR[2], sy = -(nx * camU[0] + ny * camU[1] + nz * camU[2]), l = Math.hypot(sx, sy);
  if (l < 0.5) return 0.35;
  return Math.max(0, (sx * 0.55 + sy * 0.83) / l);
}
// a chain of vertices → smoothed picture points [x, y, heavy]; broken where it turns sharply (the pen lifts)
function chainPts(vs, corner) {
  let P = vs.map(v => [scr[v * 3], scr[v * 3 + 1], heavy(v)]);
  P = P.filter((p, i) => i === 0 || Math.hypot(p[0] - P[i - 1][0], p[1] - P[i - 1][1]) > 0.3);
  if (P.length < 2) return [];
  P = resample(P, 2.5);
  for (let it = 0; it < 4; it++) P = P.map((p, i) => i === 0 || i === P.length - 1 ? p : [0, 1, 2].map(c => (P[i - 1][c] + 2 * p[c] + P[i + 1][c]) / 4));
  const out = []; let cur = [P[0]];
  for (let i = 1; i < P.length - 1; i++) {
    cur.push(P[i]);
    const a0 = Math.atan2(P[i][1] - P[i - 1][1], P[i][0] - P[i - 1][0]), a1 = Math.atan2(P[i + 1][1] - P[i][1], P[i + 1][0] - P[i][0]);
    let da = Math.abs(a1 - a0); if (da > Math.PI) da = 2 * Math.PI - da;
    if (da > corner) { out.push(cur); cur = [P[i]]; }
  }
  cur.push(P[P.length - 1]); out.push(cur);
  return out;
}
function resample(P, step) {
  const out = [P[0]]; let acc = 0;
  for (let i = 1; i < P.length; i++) {
    let p0 = P[i - 1]; const p1 = P[i]; let d = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]);
    while (acc + d >= step) { const t = (step - acc) / d; p0 = p0.map((v, c) => v + (p1[c] - v) * t); out.push(p0); d = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]); acc = 0; }
    acc += d;
  }
  const l = out[out.length - 1], z = P[P.length - 1];
  if (Math.hypot(l[0] - z[0], l[1] - z[1]) > step * 0.3) out.push(z);
  return out;
}
const len = P => { let s = 0; for (let i = 1; i < P.length; i++) s += Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]); return s; };
// one confident line; a long one in two or three, the pen lifted and set down again a hair off
function strokes(d, P, lw, seed) {
  const r = K.rng(seed), L = len(P);
  if (L < 5 * d.lw) return;
  const cum = [0]; for (let i = 1; i < P.length; i++) cum.push(cum[i - 1] + Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]));
  let s0 = 0;
  while (s0 < L - 3) {
    let s1 = Math.min(L, s0 + r.uniform(260, 620) * d.S / 1.8); if (L - s1 < 70) s1 = L;
    const pts = P.filter((_, i) => cum[i] >= s0 && cum[i] <= s1);
    if (pts.length >= 2) K.ink(d, pts, { lw, raw: true, facing: pts.map(p => p[2]), taper: Math.min(0.22, 14 * d.S / (len(pts) + 1)), seed: r.int() });
    s0 = s1 + r.uniform(-4, 3);
  }
}

// ---------------------------------------------------------------- the face, drawn on the head
const FG = H.face, FTRI = a.faceTri, FBAR = a.faceBar, NF = FTRI.length;
const fsc = new Float32Array(NF * 3), fok = new Uint8Array(NF);
function faceGrid() {
  const P = fig.positions;
  for (let k = 0; k < NF; k++) {
    fok[k] = 0; const t = FTRI[k]; if (t === NONE) continue;
    let x = 0, y = 0, z = 0, nx = 0, ny = 0, nz = 0;
    for (let c = 0; c < 3; c++) { const v = TRI[t * 3 + c], b = FBAR[k * 3 + c]; x += b * P[v * 3]; y += b * P[v * 3 + 1]; z += b * P[v * 3 + 2]; nx += b * vn[v * 3]; ny += b * vn[v * 3 + 1]; nz += b * vn[v * 3 + 2]; }
    project(x, y, z, fsc, k * 3);
    const toCam = isOrtho ? [-viewDir[0], -viewDir[1], -viewDir[2]] : normalize([camPos[0] - x, camPos[1] - y, camPos[2] - z]);
    const fc = (nx * toCam[0] + ny * toCam[1] + nz * toCam[2]) / (Math.hypot(nx, ny, nz) || 1);
    if (fc < 0.04) continue;
    if (!seen(fsc[k * 3], fsc[k * 3 + 1], fsc[k * 3 + 2], 0.004, 0)) continue;
    fok[k] = 1;
  }
}
// head units → the picture [x, y, depth] (whether seen or not); null off the head
function faceMap(x, y) {
  const gx = (x - FG.gx[0]) / FG.gx[1], gy = (y - FG.gy[0]) / FG.gy[1];
  const i = Math.floor(gx), j = Math.floor(gy), nx = FG.gx[2];
  if (i < 0 || j < 0 || i >= nx - 1 || j >= FG.gy[2] - 1) return null;
  const u = gx - i, v = gy - j, k00 = j * nx + i, k10 = k00 + 1, k01 = k00 + nx, k11 = k01 + 1;
  if (FTRI[k00] === NONE || FTRI[k10] === NONE || FTRI[k01] === NONE || FTRI[k11] === NONE) return null;
  return [0, 1, 2].map(c => (1 - v) * ((1 - u) * fsc[k00 * 3 + c] + u * fsc[k10 * 3 + c]) + v * ((1 - u) * fsc[k01 * 3 + c] + u * fsc[k11 * 3 + c]));
}
function seenNear(x, y) {
  const i = Math.round((x - FG.gx[0]) / FG.gx[1]), j = Math.round((y - FG.gy[0]) / FG.gy[1]), nx = FG.gx[2];
  for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) { const k = (j + dj) * nx + i + di; if (k >= 0 && k < NF && fok[k]) return true; }
  return false;
}
// a part's own frame at (cx, cy) on the turned head: the vertical as the head carries it, the horizontal foreshortened
// but never below `min` of it (a drawn eye on a turned face is still an eye, as the drawing's three-quarter and profile)
function frameAt(cx, cy, min = 0.7) {
  const c = faceMap(cx, cy), xl = faceMap(cx - 2, cy), xr = faceMap(cx + 2, cy), yu = faceMap(cx, cy - 2), yd = faceMap(cx, cy + 2);
  if (!c || !xl || !xr || !yu || !yd) return null;
  const ay = [(yd[0] - yu[0]) / 4, (yd[1] - yu[1]) / 4], ly = Math.hypot(...ay);
  let ax = [(xr[0] - xl[0]) / 4, (xr[1] - xl[1]) / 4];
  const r = (ax[0] * ay[1] - ax[1] * ay[0]) / (ly * ly);        // how wide the part is seen (below 0: from behind)
  if (r < -0.2) return null;
  if (r < min) ax = [ay[1] * min, -ay[0] * min];                // edge-on: its own width, square to its vertical
  return { c, ax, ay, r: Math.max(0, r), s: ly };
}
function useFrame(d, f, cx, cy) {
  d.T = [f.ax[0], f.ax[1], f.ay[0], f.ay[1], f.c[0] - f.ax[0] * cx - f.ay[0] * cy, f.c[1] - f.ax[1] * cx - f.ay[1] * cy];
  d.Sc = f.s;
}
const sm = t => { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); };
// kira.py HEAD: eyes at ±13 on y −4 (r 4.7), brows y −14, nose y 10 (button × 1.1), mouth y 26 (w 8), blush r 6 at y 15
const HEADP = { eyeY: -4, gap: 13, r: 4.7, browY: -14, noseY: 10, noseS: 1.1, mouthY: 26, mouthW: 8, cheekY: 15, blushR: 6, blushOp: 0.35, lw: 2.3 };
function drawFace(d) {
  const p = fp, h = HEADP;
  const c = faceMap(0, 10), l = faceMap(-13, 10), r = faceMap(13, 10), u0 = faceMap(0, 0), u1 = faceMap(0, 20);
  if (!c || !l || !r || !u0 || !u1) return;
  // how far the face is turned from us, and to which side of the picture (+: to the right — we see her right side)
  const pu = Math.hypot(u1[0] - u0[0], u1[1] - u0[1]) / 20;
  const upx = (u1[0] - u0[0]) / 20 / pu, upy = (u1[1] - u0[1]) / 20 / pu;                // the head's down in the picture
  const dx = ((r[0] - l[0]) * upy - (r[1] - l[1]) * upx) / pu, dz = (r[2] - l[2]) / (UNIT * H.headScale);
  const yaw = Math.atan2(dz, dx), ay = Math.abs(yaw), sg = yaw >= 0 ? 1 : -1, near = -sg;
  if (ay > 2.0) return;
  // which way the nose points and the eyes look: to the picture's right while the face looks at us (as the front
  // drawing), to the left once the face is turned left; between, it passes through the middle
  const side = Math.max(-1, Math.min(1, (yaw + 0.09) / 0.07));
  const out = sm((ay - 0.45) / 0.95);                 // the near eye, brow and cheek go round to the side we see
  const eyes = [];
  for (const xs of [-1, 1]) {
    const isNear = xs === near, x = xs * h.gap, ax = x + (isNear ? xs * 21 * out : 0);
    if (!isNear && ay > 1.05) continue;
    if (!seenNear(ax, h.eyeY)) continue;
    const f = frameAt(ax, h.eyeY, 0.78); if (!f) continue;
    eyes.push({ xs, x, f, k: isNear ? 1 : 1 - 0.18 * sm(ay / 0.45), ax });
  }
  // cheeks first (under the lines)
  for (const xs of [-1, 1]) {
    const isNear = xs === near, x = xs * (h.gap + 3), ax = x + (isNear ? xs * 12 * out : 0);
    if ((!isNear && ay > 0.9) || !seenNear(ax, h.cheekY)) continue;
    const f = frameAt(ax, h.cheekY, 0.6); if (!f) continue;
    useFrame(d, f, x, h.cheekY); K.blush(d, x, h.cheekY, h.blushR, h.blushOp);
  }
  for (const { xs, x, f, k } of eyes) {
    useFrame(d, f, x, h.eyeY);
    // the pupil looks where the drawing's does (to the picture's right when the face is turned there)
    const lookx = p.look[0] * side, e2 = { ...p, look: [Math.max(-1, Math.min(1, lookx)), p.look[1]] };
    K.eye(d, x, h.eyeY, h.r * k, e2, xs, { lw: h.lw, profile: out, seed: 21 + xs });
    K.brow(d, x + xs * 1.5, h.browY, p, xs, { k, seed: 31 + xs });
  }
  // the mouth, moved toward the seen cheek as the face turns (its near corner stays inside the contour)
  const mxA = near * 15 * sm((ay - 0.5) / 0.9);
  const fm = frameAt(mxA, h.mouthY, 0.62);
  if (fm && (seenNear(mxA, h.mouthY) || seen(fm.c[0], fm.c[1], fm.c[2], 0.02, 1))) {
    useFrame(d, fm, 0, h.mouthY);
    const k = 1 - 0.3 * out;
    K.mouth(d, 0, h.mouthY, h.mouthW * k, p.talk != null && p.talk > 0.02 ? p : { ...p, talk: null }, { lw: h.lw, seed: 43 });
  }
  // the nose: the biggest feature, over the contour. Its place is the face's middle; it points where the face is turned
  // (to the picture's right when the face looks at us, as the front drawing has it)
  if (seen(c[0], c[1], c[2], 0.03, 1)) {
    const turn = sm((ay - 0.06) / 0.34);
    // upright in the head's own frame, not foreshortened: it is a sign, drawn the same size
    const ex = [upy * pu * side, -upx * pu * side], ey = [upx * pu, upy * pu];
    d.T = [ex[0], ex[1], ey[0], ey[1], c[0], c[1]]; d.Sc = pu;
    K.nose(d, -3 * sm((ay - 0.9) / 0.5), 0, h.noseS, turn, { lw: h.lw, seed: 51 });
  }
  d.T = [1, 0, 0, 1, 0, 0]; d.Sc = d.S;
}

// ---------------------------------------------------------------- paint from the unseen picture
const mcv = document.createElement('canvas'), mctx = mcv.getContext('2d', { willReadFrequently: true });      // kept in memory: its picture is taken (toDataURL) for every paint
function maskOf(test, color, sc) {
  // at the mask's scale, over the figure's rectangle and the pad round it only: gx0, gy0 — where that begins in the page
  const pad = 4, gx0 = Math.max(0, Math.floor(box[0] * sc) - pad), gy0 = Math.max(0, Math.floor(box[1] * sc) - pad);
  const w = Math.min(Math.ceil(W * sc), Math.ceil((box[0] + box[2]) * sc) + 1 + pad) - gx0, h = Math.min(Math.ceil(Hh * sc), Math.ceil((box[1] + box[3]) * sc) + 1 + pad) - gy0;
  if (w <= 0 || h <= 0) return null;
  let x0 = w, y0 = h, x1 = -1, y1 = -1;
  const m = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) {
    const Y = Math.min(Hh - 1, Math.round((y + gy0) / sc)) - box[1]; if (Y < 0 || Y >= box[3]) continue;
    const row = (box[3] - 1 - Y) * box[2];
    for (let x = 0; x < w; x++) {
      const X = Math.min(W - 1, Math.round((x + gx0) / sc)) - box[0]; if (X < 0 || X >= box[2]) continue;
      if (test(buf[(row + X) * 4])) { m[y * w + x] = 1; if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
    }
  }
  if (x1 < 0) return null;
  x0 = Math.max(0, x0 - pad); y0 = Math.max(0, y0 - pad); x1 = Math.min(w - 1, x1 + pad); y1 = Math.min(h - 1, y1 + pad);
  const bw = x1 - x0 + 1, bh = y1 - y0 + 1;
  mcv.width = bw; mcv.height = bh;
  const im = mctx.createImageData(bw, bh), hx = parseInt(color.slice(1), 16), R = hx >> 16, Gc = (hx >> 8) & 255, B = hx & 255;
  for (let y = 0; y < bh; y++) for (let x = 0; x < bw; x++) if (m[(y + y0) * w + x + x0]) { const k = (y * bw + x) * 4; im.data[k] = R; im.data[k + 1] = Gc; im.data[k + 2] = B; im.data[k + 3] = 255; }
  mctx.putImageData(im, 0, 0);
  return { href: mcv.toDataURL(), box: [(x0 + gx0) / sc, (y0 + gy0) / sc, bw / sc, bh / sc] };
}
function paints(d) {
  for (const [gs, spec] of Object.entries(PAINT)) {
    const gid = Number(gs);
    if (S.show && !S.show.includes(gid)) continue;
    const m = maskOf(v => (v & 15) === gid, spec.color, S.mask);
    if (m) K.paintImage(d, m.href, m.box, spec);
  }
  // kira.py: pencil hatching on the hoodie's shaded side
  const m = maskOf(v => (v & 15) === G.hoodie && (v & 16), '#ffffff', S.mask);
  if (m) K.hatchImage(d, m.href, m.box, { color: '#1a0c1a', angle: -1.2, step: 4.0, op: 0.5, seed: 61 });
}

// ---------------------------------------------------------------- the picture
const stage = document.getElementById('stage');
function setCamera(w, h) {
  const c = S.cam, cp = Math.cos(c.pitch);
  let tg = c.target || [c.cx, c.cy, 0];
  if (c.follow && fig.pose) { const P = fig.pose.P; tg = [P[I.Hips * 3], c.cy, P[I.Hips * 3 + 2]]; }
  if (c.focus && fig.pose) { const P = fig.pose.P, k = I[c.focus]; tg = [P[k * 3] + (c.dx || 0), P[k * 3 + 1] + (c.up || 0), P[k * 3 + 2] + (c.fwd || 0)]; }
  const dir = [Math.sin(c.yaw) * cp, Math.sin(c.pitch), Math.cos(c.yaw) * cp];
  let dist;
  if (c.mode === 'ortho') {
    camera = ortho; const hh = c.h / 2, ww = hh * w / h; dist = 20;
    Object.assign(ortho, { left: -ww, right: ww, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
  } else { camera = persp; persp.aspect = w / h; persp.fov = c.fov || 24; persp.updateProjectionMatrix(); dist = c.dist; }
  camera.position.set(tg[0] + dir[0] * dist, tg[1] + dir[1] * dist, tg[2] + dir[2] * dist);
  camera.lookAt(tg[0], tg[1], tg[2]); camera.updateMatrixWorld();
  isOrtho = c.mode === 'ortho'; camPos = [camera.position.x, camera.position.y, camera.position.z];
  viewDir = normalize([-dir[0], -dir[1], -dir[2]]);
  const m = camera.matrixWorld.elements; camR = [m[0], m[1], m[2]]; camU = [m[4], m[5], m[6]];
  vm.copy(camera.matrixWorldInverse); mvp.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  U.dn.value = dist - 3; U.df.value = dist + 3;
  U.L.value.set(-0.95, 0.22, 0.2).normalize();          // the light, in the camera's frame: from the left, a little above
}
let lastSvg = '', drawing = Promise.resolve();
async function draw() {
  const w = Math.round(stage.clientWidth || innerWidth), h = Math.round(stage.clientHeight || innerHeight);
  if (w !== W || h !== Hh) { W = w; Hh = h; rt?.dispose(); rt = new THREE.WebGLRenderTarget(W, Hh, { depthBuffer: true }); buf = new Uint8Array(W * Hh * 4); renderer.setSize(W, Hh, false); }
  setCamera(W, Hh);
  normals();
  projectAll(); box = figureBox();
  renderer.setRenderTarget(rt); renderer.render(scene, camera); const back = readBack(box[0], Hh - box[1] - box[3], box[2], box[3], buf); renderer.setRenderTarget(null);
  if (S.flat) { const bg = scene.background; scene.background = new THREE.Color().setStyle(S.bg, THREE.LinearSRGBColorSpace); U.show.value = 1; renderer.render(scene, camera); U.show.value = 0; scene.background = bg; }
  await back;
  faceGrid();
  // the picture's points per drawing unit, at the pelvis
  const PJ = fig.pose.P, h0 = new Float32Array(3), h1 = new Float32Array(3);
  project(PJ[I.Hips * 3], PJ[I.Hips * 3 + 1], PJ[I.Hips * 3 + 2], h0); project(PJ[I.Hips * 3], PJ[I.Hips * 3 + 1] + 0.1, PJ[I.Hips * 3 + 2], h1);
  const Sx = Math.hypot(h1[0] - h0[0], h1[1] - h0[1]) / 0.1 * UNIT;
  const d = new K.Doc(W, Hh, Sx, S.seed + (S.boil ? Math.round(S.t * 7 + S.time * 100) : 0)); d.lw = S.lw;
  if (S.ground) { const gp = new Float32Array(3); project(PJ[I.Hips * 3], fig.pose.floor ?? 0, PJ[I.Hips * 3 + 2], gp); K.ground(d, gp[0], gp[1] + 2 * Sx, 45 * Sx, Math.max(7 * Sx, 45 * Sx * Math.abs(Math.sin(S.cam.pitch)))); }
  if (!S.noPaint) paints(d);
  if (!S.noLine) {
    for (const vs of contours()) {
      const name = PN[vpid[vs[0]]];
      const lw = name === 'hair' ? 2.2 : name === 'head' ? 2.3 : name.startsWith('ear') ? 2.0 : name.startsWith('hand') ? 1.8 : name.startsWith('cup') ? 1.9 : name === 'hood' ? 2.0 : name.startsWith('boot') ? 1.8 : name === 'hoodie' ? 2.4 : 2.2;
      let mn = vs[0]; for (const v of vs) if (v < mn) mn = v;
      let k = 0;
      for (const P of chainPts(vs, name === 'hair' ? 0.8 : 1.0)) strokes(d, P, lw, (mn >> 3) * 7 + S.seed + (k++) + (S.boil ? d.seed : 0));
    }
    for (const st of H.strokes) {
      const runs = []; let cur = [];
      for (const v of st.v) {
        const x = scr[v * 3], y = scr[v * 3 + 1], z = scr[v * 3 + 2];
        if (seen(x, y, z, 0.006, 1)) cur.push([x, y]); else { if (cur.length > 1) runs.push(cur); cur = []; }
      }
      if (cur.length > 1) runs.push(cur);
      for (const r of runs) if (len(r) > 3 * Sx) K.ink(d, r, { lw: st.lw, color: st.color || K.INK, weight: st.color ? 0 : 0.55, taper: st.kind === 'band' ? 0.05 : 0.3, seed: st.v[0] + S.seed, raw: true });
    }
    drawFace(d);
  }
  lastSvg = K.svg(d, S.bg, S.grain);
  stage.innerHTML = lastSvg;
  document.body.classList.toggle('flat', !!S.flat);
}

function facingYaw() { const f = qRot(getQ(fig.pose.Q, I.Hips), [0, 0, 1]); return Math.atan2(f[0], f[2]); }
window.A = {
  H, body, fig, sk, face, S, facing: facingYaw, clipInfo: () => clip && { frames: clip.frames, fps: clip.fps }, svg: () => lastSvg,
  async set(o) {
    await drawing;          // a drawing begun is finished on the figure as it was
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; face.setHead(clip ? headTrack(clip) : null); }
      S.clip = !!ids;
    }
    for (const k of ['t', 'pose', 'lw', 'seed', 'boil', 'show', 'noPaint', 'noLine', 'flat', 'mask', 'ground', 'grain', 'bg']) if (o[k] !== undefined) S[k] = o[k];
    if (o.time !== undefined) S.time = o.time; else if (o.t !== undefined && clip && !S.liveClock) S.time = o.t / clip.fps;
    if (o.liveClock !== undefined) S.liveClock = o.liveClock;
    if (o.still !== undefined) face.still = o.still;
    if (o.exprTrack) { face.exprKeys = [{ t: -10, w: { calm: 1 } }]; for (const [t, w] of o.exprTrack) face.setExpr(t, typeof w === 'string' ? { [w]: 1 } : w); }
    if (o.expr) face.setExpr(S.time, typeof o.expr === 'string' ? { [o.expr]: 1 } : o.expr);
    if (o.talk !== undefined) { face.talk(o.talk ? (o.talkFrom ?? S.time) : null); face.talkTo = o.talkTo ?? null; }
    if (o.cam) Object.assign(S.cam, o.cam);
    frame();
  },
  render() { return drawing = drawing.then(draw); },
};
await window.A.set({});
await window.A.render();
window.__ready = true;

if (!q.has('pack')) (await import('./ui.js')).ui(window.A, stage);
