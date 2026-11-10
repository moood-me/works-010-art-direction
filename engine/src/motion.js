// Kimodo's motions (motions/<id>.json, tools/motions.py) and clips: what plays — one motion, or a chain of motions
// each made by Kimodo to go on from the one before (`after`).
//
// A motion keeps the studio's data unchanged and the whole ask it was made by (kimodo.ask: prompts, seconds, heading,
// transition_frames, seed, steps, cfg, constraints, after…), so it can be made again or made otherwise.
//
// A clip, whatever it is made of: {fps, frames, motions, joins: [{at, frames, blend}], sample(t, out)} — t in frames
// (fractional: mixed between two), out = {q: Float64Array 77×4, p: Float64Array 77×3, lowest} — every SOMA joint's
// rotation in the world and its place (metres, Kimodo's space of the clip's first motion: y up; at its frame 0 the
// pelvis about over the origin, facing +z), and the lowest point of SOMA's skin then.
//
// A chain (clipOf): the next motion begins with the previous one's last `after.frames` frames (Kimodo was given them).
// Where it stands and which way it faces in the previous one's space is measured from those shared frames — the same
// pose in both, a turn about the vertical and a move apart — and checked against the studio's `startsAt`; a motion
// whose first frames are not the previous one's last is refused. The chain plays the previous one whole, then the next
// from its frame `after.frames`. Each join says how it is treated (`joins`):
//   {blend: 'cut'}                     Kimodo's frames as they are
//   {blend: 'dead', frames: n}         where Kimodo's own first frames after the given ones move away fast (a foot
//                                      flicked over two or three frames), they are blended in over n frames from the
//                                      given frames carried on — dead blending (Holden 2023): the last given frame
//                                      goes on at its own speed, slowing down (half of it gone in n/4 frames), and is
//                                      crossfaded into Kimodo's frames (smoothstep over n), joint by joint on the turns
//                                      against their parents and on the pelvis's place; SOMA's lowest point is
//                                      computed again for those frames
import { readJSON } from './pack.js';
import { hashOf } from './hash.js';
import { qMul, qConj, qNorm, qAxisAngle, qRot, qSlerp } from './math.js';

export async function loadMotion(url, skeleton, read) {
  const m = await readJSON(url, read);
  if (m.format !== 'engine/motion' || m.version !== 2) throw new Error(`${url}: not a motion of version 2`);
  if (m.skeleton !== skeleton.id) throw new Error(`${url}: on skeleton ${m.skeleton}, not ${skeleton.id}`);
  const n = m.frames, J = skeleton.J;
  const bytes = b64 => { const s = atob(b64), a = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) a[i] = s.charCodeAt(i); return a.buffer; };
  const q16 = new Int16Array(bytes(m.data.q)), p16 = new Int16Array(bytes(m.data.p));
  const col = skeleton.names.map(nm => { const c = m.data.names.indexOf(nm); if (c < 0) throw new Error(`${url}: no ${nm}`); return c; });
  const JM = m.data.names.length;
  if (q16.length !== n * JM * 4 || p16.length !== n * JM * 3) throw new Error(`${url}: its data is not ${n} frames of ${JM} joints`);
  const q = new Float64Array(n * J * 4), p = new Float64Array(n * J * 3);
  for (let f = 0; f < n; f++) for (let j = 0; j < J; j++) {
    const s = (f * JM + col[j]), o = f * J + j;
    const x = q16[s * 4], y = q16[s * 4 + 1], z = q16[s * 4 + 2], w = q16[s * 4 + 3];
    const l = Math.hypot(x, y, z, w) || 1; q[o * 4] = x / l; q[o * 4 + 1] = y / l; q[o * 4 + 2] = z / l; q[o * 4 + 3] = w / l;
    for (let k = 0; k < 3; k++) p[o * 3 + k] = p16[s * 3 + k] / 1000;
  }
  return { id: m.id, label: m.label, kimodo: m.kimodo, after: m.after ?? null, fps: m.fps, frames: n, J, q, p,
    lowest: Float64Array.from(m.derived.lowest), hash: hashOf([m]) };
}

// the turn about y and the move that carries `next`'s first k frames onto `prev`'s last k (each joint's rotation and
// place); refused when they are not the same pose
export function overlapOf(prev, next, k) {
  const J = prev.J, f0 = prev.frames - k, H = 0;
  const qa = i => prev.q.subarray((f0 + i) * J * 4, (f0 + i + 1) * J * 4), qb = i => next.q.subarray(i * J * 4, (i + 1) * J * 4);
  const g = (A, j) => [A[j * 4], A[j * 4 + 1], A[j * 4 + 2], A[j * 4 + 3]];
  const D = qMul(g(qa(0), H), qConj(g(qb(0), H)));
  const yaw = 2 * Math.atan2(D[1], D[3]), r = qAxisAngle([0, 1, 0], yaw);
  let worstTurn = 0, worstMove = 0;
  const pa = (i, j) => [...prev.p.subarray(((f0 + i) * J + j) * 3, ((f0 + i) * J + j) * 3 + 3)], pb = (i, j) => [...next.p.subarray((i * J + j) * 3, (i * J + j) * 3 + 3)];
  const h0 = qRot(r, pb(0, H)), move = [pa(0, H)[0] - h0[0], pa(0, H)[1] - h0[1], pa(0, H)[2] - h0[2]];
  for (let i = 0; i < k; i++) for (let j = 0; j < J; j++) {
    const e = qMul(g(qa(i), j), qConj(qMul(r, g(qb(i), j))));
    worstTurn = Math.max(worstTurn, 2 * Math.acos(Math.min(1, Math.abs(e[3]))));
    const x = qRot(r, pb(i, j)), y = pa(i, j);
    worstMove = Math.max(worstMove, Math.hypot(x[0] + move[0] - y[0], x[1] + move[1] - y[1], x[2] + move[2] - y[2]));
  }
  return { yaw, move, worstTurn, worstMove };
}

export function clipOf(motions, { joins = [], soma = null } = {}) {
  if (!motions.length) throw new Error('a clip of no motions');
  const J = motions[0].J, fps = motions[0].fps;
  if (motions.some(m => m.fps !== fps)) throw new Error('motions of a chain at different frame rates');
  if (joins.length !== motions.length - 1) throw new Error(`a chain of ${motions.length} motions says how each of its ${motions.length - 1} joins is treated (joins)`);
  // each motion's place in the first one's space: a turn about y and a move
  const segs = [];
  let yaw = 0, move = [0, 0, 0], start = 0;
  motions.forEach((m, i) => {
    let from = 0;
    if (i > 0) {
      const prev = motions[i - 1], a = m.after;
      if (!a || a.motion !== prev.id || m.kimodo.ask.after?.key !== prev.kimodo.key)
        throw new Error(`${m.id} was not made to go on from ${prev.id}: Kimodo has to make it so (make_motion with after)`);
      from = a.frames;
      const o = overlapOf(prev, m, from);
      if (o.worstTurn > 1.5 * Math.PI / 180 || o.worstMove > 0.006 || Math.abs(o.move[1]) > 0.003)
        throw new Error(`${m.id}: its first ${from} frames are not ${prev.id}'s last (apart by ${(o.worstTurn * 180 / Math.PI).toFixed(1)}°, ${(o.worstMove * 1000).toFixed(0)} mm)`);
      // the studio's own word on where it starts (said for a motion that keeps the previous one's heading)
      const st = m.kimodo.startsAt;
      if (st && Math.abs(o.yaw) < 0.01 && Math.hypot(st.x - o.move[0], st.z - o.move[2]) > 0.006)
        throw new Error(`${m.id}: the studio says it starts at (${st.x}, ${st.z}) in ${prev.id}'s space, its frames say (${o.move[0].toFixed(4)}, ${o.move[2].toFixed(4)})`);
      // compose: this one's space → the previous one's → the first one's
      const r = qAxisAngle([0, 1, 0], yaw), mv = qRot(r, o.move);
      move = [move[0] + mv[0], move[1] + mv[1], move[2] + mv[2]]; yaw += o.yaw;
    }
    segs.push({ m, start, from, yaw, move: move.slice() });
    start += m.frames - from;
  });
  const frames = start;
  // every frame of the clip, in the first motion's space
  const Q = new Float64Array(frames * J * 4), P = new Float64Array(frames * J * 3), L = new Float64Array(frames);
  for (const s of segs) {
    const r = qAxisAngle([0, 1, 0], s.yaw), q = [0, 0, 0, 0], o = [0, 0, 0, 0], v = [0, 0, 0];
    for (let f = s.from; f < s.m.frames; f++) {
      const g = s.start + f - s.from;
      for (let j = 0; j < J; j++) {
        const a = (f * J + j), b = (g * J + j);
        for (let c = 0; c < 4; c++) q[c] = s.m.q[a * 4 + c];
        qMul(r, q, o); for (let c = 0; c < 4; c++) Q[b * 4 + c] = o[c];
        qRot(r, [s.m.p[a * 3], s.m.p[a * 3 + 1], s.m.p[a * 3 + 2]], v);
        for (let c = 0; c < 3; c++) P[b * 3 + c] = v[c] + s.move[c];
      }
      L[g] = s.m.lowest[f];
    }
  }
  const joinsOut = segs.slice(1).map((s, i) => ({ at: s.start, ...joins[i] }));
  for (const jn of joinsOut) {
    if (jn.blend === 'cut') continue;
    if (jn.blend !== 'dead' || !Number.isInteger(jn.frames) || jn.frames < 1) throw new Error(`a join is treated by {blend: 'cut'} or {blend: 'dead', frames: n}, not ${JSON.stringify(jn)}`);
    if (!soma) throw new Error('a blended join needs SOMA\'s skin (for the lowest point of the frames it changes)');
    deadBlend(Q, P, L, J, jn.at, Math.min(jn.frames, frames - jn.at), soma);
  }
  const at = (f, out) => {
    out.q.set(Q.subarray(f * J * 4, (f + 1) * J * 4)); out.p.set(P.subarray(f * J * 3, (f + 1) * J * 3)); out.lowest = L[f];
  };
  const A = newSample(J), B = newSample(J);
  return {
    fps, frames, J, motions: motions.map(m => m.id), joins: joinsOut,
    sample(t, out) {
      t = Math.max(0, Math.min(frames - 1, t));
      const f0 = Math.floor(t), f1 = Math.min(frames - 1, f0 + 1), u = t - f0;
      if (u === 0 || f1 === f0) { at(f0, out); return out; }
      at(f0, A); at(f1, B);
      for (let j = 0; j < J; j++) {
        const o = j * 4, sg = A.q[o] * B.q[o] + A.q[o + 1] * B.q[o + 1] + A.q[o + 2] * B.q[o + 2] + A.q[o + 3] * B.q[o + 3] < 0 ? -1 : 1;
        let l = 0; for (let k = 0; k < 4; k++) { out.q[o + k] = A.q[o + k] * (1 - u) + sg * B.q[o + k] * u; l += out.q[o + k] ** 2; }
        l = Math.sqrt(l); for (let k = 0; k < 4; k++) out.q[o + k] /= l;
      }
      for (let i = 0; i < J * 3; i++) out.p[i] = A.p[i] * (1 - u) + B.p[i] * u;
      out.lowest = A.lowest * (1 - u) + B.lowest * u;
      return out;
    },
  };
}
export const newSample = J => ({ q: new Float64Array(J * 4), p: new Float64Array(J * 3), lowest: 0 });

// Dead blending at clip frame g (the first of Kimodo's own frames after the given ones), over n frames: the given
// frames' last (g−1) carried on at its speed (from g−2 to g−1), the speed decaying, crossfaded into Kimodo's frames.
function deadBlend(Q, P, L, J, g, n, soma) {
  if (soma.J !== J) throw new Error(`SOMA's skin has ${soma.J} joints, the motions ${J}`);
  const parent = soma.parent, R0 = soma.P0;
  const qa = (f, j) => [Q[(f * J + j) * 4], Q[(f * J + j) * 4 + 1], Q[(f * J + j) * 4 + 2], Q[(f * J + j) * 4 + 3]];
  const loc = (f, j) => parent[j] < 0 ? qa(f, j) : qMul(qConj(qa(f, parent[j])), qa(f, j));   // against its parent
  const H = 0, ph = f => [P[(f * J + H) * 3], P[(f * J + H) * 3 + 1], P[(f * J + H) * 3 + 2]];
  const last = [], speed = [];
  for (let j = 0; j < J; j++) { last.push(loc(g - 1, j)); speed.push(logq(qMul(last[j], qConj(loc(g - 2, j))))); }
  const hip0 = ph(g - 1), hipV = ph(g - 1).map((v, c) => v - ph(g - 2)[c]);
  const lambda = Math.LN2 / Math.max(1, n / 4);                  // the speed's decay: half of it gone in n/4 frames
  const local = new Array(J);
  for (let s = 1; s <= n; s++) {
    const f = g + s - 1, carried = (1 - Math.exp(-lambda * s)) / lambda, u = s / (n + 1), w = u * u * (3 - 2 * u);
    for (let j = 0; j < J; j++) {
      const e = qMul(expq(speed[j].map(v => v * carried)), last[j]);
      local[j] = qSlerp(e, loc(f, j), w);
    }
    const hip = ph(f).map((v, c) => (hip0[c] + hipV[c] * carried) * (1 - w) + v * w);
    for (let j = 0; j < J; j++) {
      const p = parent[j], q = p < 0 ? local[j] : qNorm(qMul(qa(f, p), local[j]));
      for (let c = 0; c < 4; c++) Q[(f * J + j) * 4 + c] = q[c];
      if (p < 0) { for (let c = 0; c < 3; c++) P[(f * J + j) * 3 + c] = hip[c]; continue; }
      // the bone from the parent as SOMA's: its rest offset turned by the parent's turn from SOMA's rest (q · R0ᵀ)
      const v = qRot(qMul(qa(f, p), soma.frameConj[p]), [R0[j * 3] - R0[p * 3], R0[j * 3 + 1] - R0[p * 3 + 1], R0[j * 3 + 2] - R0[p * 3 + 2]]);
      for (let c = 0; c < 3; c++) P[(f * J + j) * 3 + c] = P[(f * J + p) * 3 + c] + v[c];
    }
    L[f] = soma.lowest(Q.subarray(f * J * 4, (f + 1) * J * 4), P.subarray(f * J * 3, (f + 1) * J * 3));
  }
}

// a turn as a rotation vector (axis × angle, the angle in (−π, π]) and back
function logq(q) {
  let [x, y, z, w] = q; if (w < 0) { x = -x; y = -y; z = -z; w = -w; }
  const s = Math.hypot(x, y, z); if (s < 1e-12) return [0, 0, 0];
  const a = 2 * Math.atan2(s, w); return [x / s * a, y / s * a, z / s * a];
}
function expq(v) { const a = Math.hypot(v[0], v[1], v[2]); return a < 1e-12 ? [0, 0, 0, 1] : qAxisAngle(v, a); }
