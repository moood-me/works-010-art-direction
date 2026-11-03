// Anny's bodies as the hair experiment (В1) puts them: the body moood bakes, its T-shirt, trousers and shoes riding the
// skin rigidly, the skin sunk under the clothes, a Kimodo motion with the same timeline and head turns as
// experiments/hair/live.js. Writes, for Blender: <out>/<who>-rest.json (rest points and triangles of body and
// garments, and the head joint) and <out>/<who>-<motion>-<turns>.pc2 (all points, every frame, 30 fps).
// node --experimental-default-type=module bodies.mjs <repo> <out> <who> [motion turns seconds]...
import fs from 'fs';
const [repo, out, who, ...jobs] = process.argv.slice(2);
const THREE = await import(process.env.THREE || 'three');
const E = repo + '/experiments/';
const { person, Pose, parseGarment, fitted, skinInto } = await import(E + 'cloth/people.js');
const { nearestOn } = await import(E + 'cloth/wardrobe.js');
const bytes = async name => { const m = await import(E + 'data/' + name + '.js'); return Uint8Array.from(Buffer.from(m.default, 'base64')).buffer; };
const META = JSON.parse(fs.readFileSync(E + 'data/meta.json'));
const WEAR = { woman: ['tshirt', 'pants', 'flats'], man: ['tshirt', 'pants', 'boots'], child: ['tshirt', 'pants', 'flats'] };
const body = await person(THREE, bytes, META, who);
const garments = [];
for (const g of WEAR[who]) {
  const G = parseGarment(await bytes(g)), pos = fitted(G, body.rest), near = nearestOn(body.rest, pos), n = pos.length / 3, J = new Uint8Array(n * 4), Wt = new Uint8Array(n * 4);
  for (let i = 0; i < n; i++) for (let k = 0; k < 4; k++) { J[i * 4 + k] = body.joint[near[i] * 4 + k]; Wt[i * 4 + k] = body.weight[near[i] * 4 + k]; }
  garments.push({ name: g, rest: Float32Array.from(pos), tris: G.tris, J, W: Wt });
}
const smooth01 = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const all = Float32Array.from(garments.flatMap(g => Array.from(g.rest))), nearB = nearestOn(all, body.rest);
const sink = Float32Array.from(nearB, (j, i) => {
  const R = body.rest, n = body.nrm, dx = R[i * 3] - all[j * 3], dy = R[i * 3 + 1] - all[j * 3 + 1], dz = R[i * 3 + 2] - all[j * 3 + 2], d = Math.hypot(dx, dy, dz);
  const near01 = 1 - smooth01(0.012, 0.03, d), o = dx * n[i * 3] + dy * n[i * 3 + 1] + dz * n[i * 3 + 2];
  return near01 * Math.min(0.03, Math.max(0.007, o + 0.004 + (d < 0.03 ? 0.004 : 0)));
});
const headJ = body.names.indexOf('Head');
const sunk = (P, Nn) => { for (let i = 0; i < sink.length; i++) if (sink[i]) for (let c = 0; c < 3; c++) P[i * 3 + c] -= Nn[i * 3 + c] * sink[i]; return P; };
// rest (standing, as `moment` gives before the motion starts)
const pose0 = new Pose(THREE, body), r0 = pose0.skin(pose0.at(null));
const rest = { body: { pos: Array.from(sunk(r0.pos, r0.nrm)), tris: Array.from(body.tris) }, garments: garments.map(g => { const p = new Float32Array(g.rest.length); skinInto(g.rest, null, g.J, g.W, 255, r0.E, p, null); return { name: g.name, pos: Array.from(p), tris: Array.from(g.tris) }; }),
  head: body.J[headJ].toArray(), headE: Array.from(r0.E[headJ]), eyes: META.people[who].eyes, height: body.height };
fs.mkdirSync(out, { recursive: true });
fs.writeFileSync(`${out}/${who}-rest.json`, JSON.stringify(rest));
// the timeline and head turns, as live.js
const SETTLE = 0.5, INTO = 0.9, MIX = 10, FPS = 30;
function moment(pose, M, t, cyclic) {
  if (!M || t < SETTLE) return pose.at(null);
  if (t < SETTLE + INTO) { const s = (t - SETTLE) / INTO; return pose.at(M, 0, s * s * (3 - 2 * s)); }
  const g = (t - SETTLE - INTO) * FPS;
  if (!cyclic) return pose.at(M, Math.min(g, M.n - 1));
  const C = M.n - MIX, c = Math.floor(g / C), f = g - c * C, D = [M.hips[C * 3] - M.hips[0], M.hips[C * 3 + 2] - M.hips[2]];
  const now = pose.at(M, f, 1, [D[0] * c, D[1] * c]);
  if (c === 0 || f >= MIX) return now;
  const was = pose.at(M, f + C, 1, [D[0] * (c - 1), D[1] * (c - 1)]), u = f / MIX, s = u * u * (3 - 2 * u);
  return { W: was.W.map((q, j) => q.clone().slerp(now.W[j], s)), hips: was.hips.clone().lerp(now.hips, s), low: was.low + (now.low - was.low) * s };
}
const HEADSET = ['Head', 'HeadEnd', 'Jaw', 'LeftEye', 'RightEye'];
function turnAngle(kind, t) {
  const t0 = t - 0.6; if (kind === 'none' || t0 <= 0) return 0;
  const ramp = Math.min(1, t0 / 0.8);
  if (kind === 'look') return ramp * 0.95 * Math.sin(t0 * 2 * Math.PI / 3.6);
  const seq = [0, 1.1, -1.1, 0.0, -1.1, 1.1], seg = 1.3, k = Math.floor(t0 / seg), u = t0 - k * seg;
  const a = seq[k % seq.length], b = seq[(k + 1) % seq.length], s = Math.min(1, Math.max(0, (u - 0.85) / 0.28)), e = s * s * (3 - 2 * s);
  return a + (b - a) * e;
}
const CYC = { idle: true, walk: true, run: true, dance: true };
for (let i = 0; i < jobs.length; i += 3) {
  const [motion, turns, secs] = [jobs[i], jobs[i + 1], +jobs[i + 2]];
  const M = JSON.parse(fs.readFileSync(E + 'cloth/motions/' + motion + '.json')); M.low ??= M.foot.slice();
  const pose = new Pose(THREE, body), n = Math.round(secs * FPS), V = body.N + garments.reduce((s, g) => s + g.rest.length / 3, 0);
  const head = Buffer.alloc(32); head.write('POINTCACHE2\0', 0); head.writeInt32LE(1, 12); head.writeInt32LE(V, 16); head.writeFloatLE(0, 20); head.writeFloatLE(1, 24); head.writeInt32LE(n, 28);
  const fd = fs.openSync(`${out}/${who}-${motion}-${turns}.pc2`, 'w'); fs.writeSync(fd, head);
  const heads = [];
  for (let f = 0; f < n; f++) {
    const t = f / FPS, st = moment(pose, M, t, !!CYC[motion]), a = turnAngle(turns, t);
    if (a) { const neck = st.W[body.names.indexOf('Neck2')], ax = new THREE.Vector3(0, 1, 0).applyQuaternion(neck);
      body.names.forEach((nm, j) => { const k = nm === 'Neck1' ? 0.2 : nm === 'Neck2' ? 0.5 : HEADSET.includes(nm) ? 1 : 0; if (k) st.W[j].premultiply(new THREE.Quaternion().setFromAxisAngle(ax, a * k)); }); }
    const s = pose.skin(st), buf = new Float32Array(V * 3); buf.set(sunk(s.pos, s.nrm)); let at = body.N * 3;
    for (const g of garments) { const p = new Float32Array(g.rest.length); skinInto(g.rest, null, g.J, g.W, 255, s.E, p, null); buf.set(p, at); at += p.length; }
    fs.writeSync(fd, Buffer.from(buf.buffer)); heads.push(Array.from(s.E[headJ]));
  }
  fs.closeSync(fd);
  fs.writeFileSync(`${out}/${who}-${motion}-${turns}-head.json`, JSON.stringify(heads));
  console.log(who, motion, turns, n, 'frames', V, 'points');
}
