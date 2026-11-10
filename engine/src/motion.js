// Kimodo's motions (motions/<id>.json, tools/motions.py) and clips: what plays — one motion, or a chain of motions
// each made by Kimodo to go on from the one before (`after`), joined where Kimodo joined them, without a seam.
//
// A clip, whatever it is made of: {fps, frames, joins: [frame…], sample(t, out)} — t in frames (fractional: mixed
// between two), out = {q: Float64Array 77×4, p: Float64Array 77×3, lowest} — at that moment every SOMA joint's
// rotation in the world and its place (metres, Kimodo's space: y up; at the clip's frame 0 the pelvis over the origin,
// facing +z), and the lowest point of SOMA's skin then.
import { readJSON } from './pack.js';

export async function loadMotion(url, skeleton, read) {
  const m = await readJSON(url, read);
  if (m.format !== 'engine/motion' || m.version !== 1) throw new Error(`${url}: not a motion of version 1`);
  if (m.skeleton !== skeleton.id) throw new Error(`${url}: on skeleton ${m.skeleton}, not ${skeleton.id}`);
  const n = m.frames, J = skeleton.J;
  const bytes = b64 => { const s = atob(b64), a = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) a[i] = s.charCodeAt(i); return a.buffer; };
  const q16 = new Int16Array(bytes(m.data.q)), p16 = new Int16Array(bytes(m.data.p));
  // the motion's joints in the skeleton's order
  const col = skeleton.names.map(nm => { const c = m.data.names.indexOf(nm); if (c < 0) throw new Error(`${url}: no ${nm}`); return c; });
  const JM = m.data.names.length;
  const q = new Float64Array(n * J * 4), p = new Float64Array(n * J * 3);
  for (let f = 0; f < n; f++) for (let j = 0; j < J; j++) {
    const s = (f * JM + col[j]), o = f * J + j;
    let x = q16[s * 4], y = q16[s * 4 + 1], z = q16[s * 4 + 2], w = q16[s * 4 + 3];
    const l = Math.hypot(x, y, z, w) || 1; q[o * 4] = x / l; q[o * 4 + 1] = y / l; q[o * 4 + 2] = z / l; q[o * 4 + 3] = w / l;
    for (let k = 0; k < 3; k++) p[o * 3 + k] = p16[s * 3 + k] / 1000;
  }
  return { id: m.id, label: m.label, kimodo: m.kimodo, fps: m.fps, frames: n, J, q, p, lowest: Float64Array.from(m.derived.lowest) };
}

// one motion, or a chain: each next one made with `after` the one before it — it begins as that one ended (its first
// `after.frames` frames are that one's last), its origin at `startsAt` in that one's space, facing as that one did
export function clipOf(motions) {
  if (!motions.length) throw new Error('a clip of no motions');
  const segs = [];
  let start = 0, off = [0, 0];
  motions.forEach((m, i) => {
    let from = 0;
    if (i > 0) {
      const a = m.kimodo?.after, prev = motions[i - 1];
      if (!a || a.motion !== prev.id) throw new Error(`${m.id} was not made to go on from ${prev.id}: Kimodo has to make it so (make_motion with after)`);
      if (!m.kimodo.startsAt) throw new Error(`${m.id}: where it starts in ${prev.id}'s space is not known (startsAt)`);
      from = a.frames;
      off = [off[0] + m.kimodo.startsAt.x, off[1] + m.kimodo.startsAt.z];
    }
    segs.push({ m, start, from, off: off.slice() });
    start += m.frames - from;
  });
  const frames = start, J = motions[0].J, fps = motions[0].fps;
  if (motions.some(m => m.fps !== fps)) throw new Error('motions of a chain at different frame rates');
  const at = g => { let i = segs.length - 1; while (i > 0 && g < segs[i].start) i--; const s = segs[i]; return [s, g - s.start + s.from]; };
  const A = { q: new Float64Array(J * 4), p: new Float64Array(J * 3) }, B = { q: new Float64Array(J * 4), p: new Float64Array(J * 3) };
  const frame = (g, out) => {
    const [s, f] = at(g), m = s.m;
    out.q.set(m.q.subarray(f * J * 4, (f + 1) * J * 4));
    for (let j = 0; j < J; j++) { const o = (f * J + j) * 3; out.p[j * 3] = m.p[o] + s.off[0]; out.p[j * 3 + 1] = m.p[o + 1]; out.p[j * 3 + 2] = m.p[o + 2] + s.off[1]; }
    out.lowest = m.lowest[f];
  };
  return {
    fps, frames, J, motions: motions.map(m => m.id), joins: segs.slice(1).map(s => s.start),
    sample(t, out) {
      t = Math.max(0, Math.min(frames - 1, t));
      const f0 = Math.floor(t), f1 = Math.min(frames - 1, f0 + 1), u = t - f0;
      frame(f0, A); if (u === 0 || f1 === f0) { out.q.set(A.q); out.p.set(A.p); out.lowest = A.lowest; return out; }
      frame(f1, B);
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
