// SOMA's skin (data/soma/soma.bin: Kimodo's SOMA mesh, as moood converted it; Apache-2.0, data/soma/NOTICE) — for the
// lowest point of SOMA's posed skin at a moment the studio did not give (a blended join: src/motion.js), computed as
// tools/motions.py computes `derived.lowest` for the studio's frames.
//   bin: V, F, J (uint32); bind V×3 (float32); faces F×3 (uint16); joint V×8, weight V×8 (uint8, /255);
//        inverse binds J×3×4 (float32); parents J (uint8)
export async function loadSoma(url, read) {
  const b = await read(url), dv = new DataView(b);
  const V = dv.getUint32(0, true), F = dv.getUint32(4, true), J = dv.getUint32(8, true);
  let at = 12;
  const bind = new Float32Array(b.slice(at, at + V * 12)); at += V * 12;
  at += F * 6;
  const joint = new Uint8Array(b.slice(at, at + V * 8)); at += V * 8;
  const weight = new Uint8Array(b.slice(at, at + V * 8)); at += V * 8;
  const inv = new Float32Array(b.slice(at, at + J * 48)); at += J * 48;
  const parent = Int16Array.from(new Uint8Array(b.slice(at, at + J)), v => (v === 255 ? -1 : v));
  // each joint's rest frame R0 (its axes, columns) and place P0: inv = [R0ᵀ | −R0ᵀ P0]
  const R0 = new Float64Array(J * 9), P0 = new Float64Array(J * 3);
  for (let j = 0; j < J; j++) {
    const I = k => inv[j * 12 + k];
    for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) R0[j * 9 + r * 3 + c] = I(c * 4 + r);
    for (let r = 0; r < 3; r++) P0[j * 3 + r] = -(R0[j * 9 + r * 3] * I(3) + R0[j * 9 + r * 3 + 1] * I(7) + R0[j * 9 + r * 3 + 2] * I(11));
  }
  // R0 as a quaternion, its conjugate: q · frameConj is a joint's turn from SOMA's rest
  const frameConj = Array.from({ length: J }, (_, j) => { const q = matQuat(R0.subarray(j * 9, j * 9 + 9)); return [-q[0], -q[1], -q[2], q[3]]; });
  const Ry = new Float64Array(J * 3), Ty = new Float64Array(J);
  return {
    V, J, R0, P0, parent, frameConj,
    // q: J×4 world rotations (x y z w), p: J×3 places (metres) → the posed skin's lowest y
    lowest(q, p) {
      for (let j = 0; j < J; j++) {
        const x = q[j * 4], y = q[j * 4 + 1], z = q[j * 4 + 2], w = q[j * 4 + 3];
        const m0 = 2 * (x * y + z * w), m1 = 1 - 2 * (x * x + z * z), m2 = 2 * (y * z - x * w);   // row 1 of the rotation
        for (let c = 0; c < 3; c++) Ry[j * 3 + c] = m0 * R0[j * 9 + c * 3] + m1 * R0[j * 9 + c * 3 + 1] + m2 * R0[j * 9 + c * 3 + 2];   // row 1 of q·R0ᵀ
        Ty[j] = p[j * 3 + 1] - (Ry[j * 3] * P0[j * 3] + Ry[j * 3 + 1] * P0[j * 3 + 1] + Ry[j * 3 + 2] * P0[j * 3 + 2]);
      }
      let lo = Infinity;
      for (let i = 0; i < V; i++) {
        const bx = bind[i * 3], by = bind[i * 3 + 1], bz = bind[i * 3 + 2];
        let yv = 0;
        for (let k = 0; k < 8; k++) { const w = weight[i * 8 + k]; if (!w) continue; const j = joint[i * 8 + k]; yv += w / 255 * (Ry[j * 3] * bx + Ry[j * 3 + 1] * by + Ry[j * 3 + 2] * bz + Ty[j]); }
        if (yv < lo) lo = yv;
      }
      return lo;
    },
  };
}

// a rotation matrix (rows) as a quaternion x y z w
function matQuat(m) {
  const [a, b, c, d, e, f, g, h, i] = m, t = a + e + i;
  let x, y, z, w;
  if (t > 0) { const s = Math.sqrt(t + 1) * 2; w = s / 4; x = (h - f) / s; y = (c - g) / s; z = (d - b) / s; }
  else if (a > e && a > i) { const s = Math.sqrt(1 + a - e - i) * 2; w = (h - f) / s; x = s / 4; y = (b + d) / s; z = (c + g) / s; }
  else if (e > i) { const s = Math.sqrt(1 + e - a - i) * 2; w = (c - g) / s; x = (b + d) / s; y = s / 4; z = (f + h) / s; }
  else { const s = Math.sqrt(1 + i - a - e) * 2; w = (d - b) / s; x = (c + g) / s; y = (f + h) / s; z = s / 4; }
  const l = Math.hypot(x, y, z, w); return [x / l, y / l, z / l, w / l];
}
