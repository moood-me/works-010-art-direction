// A hairstyle onto a head. Hairstyles are designed round the neutral head of the design space (src/hair/build.js:
// its cranium an ellipsoid, CRANIUM); a head's own cranium is fitted with an ellipsoid too — through its designed
// form where it has one (a wrap's: the form's surface found along rays from its middle), else through its skin — its
// points above the brows. Then every point of the hairstyle is carried over as В1 carried it (experiments/hair/fit.js):
// what lies on the designed skull lands on the head's, what lies off it keeps its direction from it and its distance,
// grown with the head (a bigger head, a bigger hairstyle). Last, the head is not an ellipsoid: how far its real surface
// lies from the fitted one in each direction is added along that direction to what lies on or near the skull (fading
// out by 5 cm off it), so the roots sit on the scalp and the locks keep their lift off the head's own form.
//   fitOn({frame, form, body, sk}) → {map(x, y, z, out) → rest point (metres), scale}
import { CRANIUM } from './build.js';
import { headShares } from '../head/frame.js';
import { sst, clamp } from '../math.js';

const AZ = 48, EL = 32;

export function fitOn({ frame: F, form, body, sk }) {
  const J = body.rig.joints, eyeY = (J[sk.index.LeftEye * 3 + 1] + J[sk.index.RightEye * 3 + 1]) / 2;
  // the head's surface: on its form (head units → metres), or its skin
  const surface = form ? formPoints(form, F) : skinPoints(body, sk);
  const top = surface.filter(p => p[1] > eyeY + 0.03);
  const c0 = CRANIUM.c, r0 = CRANIUM.r;
  const E = fitEllipsoid(top, [F.O[1], F.O[2], r0[0], r0[1], r0[2]]), C = E.c, R = E.r;
  const scale = (R[0] + R[1] + R[2]) / (r0[0] + r0[1] + r0[2]);
  // how far the head's real surface lies off the fitted ellipsoid, by direction from its middle (smoothed over the
  // directions; directions no point lies in take their neighbours')
  const real = new Float64Array(AZ * EL).fill(NaN), bin = (dx, dy, dz) => { const az = Math.atan2(dx, dz), el = Math.asin(clamp(dy / (Math.hypot(dx, dy, dz) || 1), -1, 1)); return [Math.min(AZ - 1, Math.floor((az / Math.PI + 1) / 2 * AZ)), Math.min(EL - 1, Math.floor((el / Math.PI + 0.5) * EL))]; };
  const ellR = (dx, dy, dz) => { const l = Math.hypot(dx, dy, dz) || 1; return l / Math.hypot(dx / R[0], dy / R[1], dz / R[2]); };
  for (const p of surface) {
    const dx = p[0] - C[0], dy = p[1] - C[1], dz = p[2] - C[2], [a, e] = bin(dx, dy, dz), k = a + AZ * e, d = Math.hypot(dx, dy, dz) - ellR(dx, dy, dz);
    real[k] = Number.isNaN(real[k]) ? d : Math.max(real[k], d);
  }
  let delta = Float64Array.from(real);
  for (let it = 0; it < 6; it++) {
    const next = new Float64Array(delta.length);
    for (let e = 0; e < EL; e++) for (let a = 0; a < AZ; a++) {
      let s = 0, n = 0;
      for (const [da, de, w] of [[0, 0, 2], [1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1]]) { const ee = e + de; if (ee < 0 || ee >= EL) continue; const v = delta[(a + da + AZ) % AZ + AZ * ee]; if (!Number.isNaN(v)) { s += v * w; n += w; } }
      next[a + AZ * e] = n ? s / n : NaN;
    }
    delta = next;
  }
  for (let k = 0; k < delta.length; k++) delta[k] = Number.isNaN(delta[k]) ? 0 : clamp(delta[k], -0.03, 0.03);
  const deltaAt = (dx, dy, dz) => { const [a, e] = bin(dx, dy, dz); return delta[a + AZ * e]; };
  const map = (x, y, z, out = [0, 0, 0]) => {
    const qx = (x - c0[0]) / r0[0], qy = (y - c0[1]) / r0[1], qz = (z - c0[2]) / r0[2], k = Math.hypot(qx, qy, qz) || 1;
    const sx = c0[0] + r0[0] * qx / k, sy = c0[1] + r0[1] * qy / k, sz = c0[2] + r0[2] * qz / k;   // on the designed skull
    const tx = C[0] + R[0] * qx / k, ty = C[1] + R[1] * qy / k, tz = C[2] + R[2] * qz / k;           // on the head's
    const off = (k - 1) * (r0[0] + r0[1] + r0[2]) / 3, w = 1 - sst(clamp((off - 0.01) / 0.04, 0, 1));
    const nx = tx - C[0], ny = ty - C[1], nz = tz - C[2], nl = Math.hypot(nx, ny, nz) || 1, d = w ? deltaAt(nx, ny, nz) * w : 0;
    out[0] = tx + (x - sx) * scale + nx / nl * d; out[1] = ty + (y - sy) * scale + ny / nl * d; out[2] = tz + (z - sz) * scale + nz / nl * d;
    return out;
  };
  return { map, scale, skull: E };
}

// the designed form's surface along rays from the head's middle (every few degrees), in metres
function formPoints(form, F) {
  const out = [];
  for (let e = 0; e < EL; e++) for (let a = 0; a < AZ; a++) {
    const el = ((e + 0.5) / EL - 0.5) * Math.PI, az = ((a + 0.5) / AZ * 2 - 1) * Math.PI, d = [Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el)];
    const t = rayOut(form.full, d);
    if (t) out.push(F.toW(d[0] * t, d[1] * t, d[2] * t));
  }
  return out;
}
// how far along d from the middle the form's surface lies (the last crossing from inside out within 3 head units)
function rayOut(f, d) {
  let prev = f(0, 0, 0), t0 = 0, hit = 0;
  for (let t = 0.02; t <= 3; t += 0.02) { const s = f(d[0] * t, d[1] * t, d[2] * t); if (prev < 0 && s >= 0) { let a = t0, b = t; for (let k = 0; k < 20; k++) { const m = (a + b) / 2; if (f(d[0] * m, d[1] * m, d[2] * m) < 0) a = m; else b = m; } hit = (a + b) / 2; } prev = s; t0 = t; }
  return hit;
}
// the head's skin: its vertices mostly on the head's joints
function skinPoints(body, sk) {
  const { head } = headShares(body.mesh, sk), P = body.mesh.positions, out = [];
  for (const i of body.mesh.used) if (head[i] > 0.5) out.push([P[i * 3], P[i * 3 + 1], P[i * 3 + 2]]);
  return out;
}
// an axis-aligned ellipsoid (its middle on x = 0) through points, by shrinking steps on each parameter
// (q: [y, z, rx, ry, rz])
function fitEllipsoid(P, x0) {
  const err = q => { let e = 0; for (const p of P) { const k = Math.hypot(p[0] / q[2], (p[1] - q[0]) / q[3], (p[2] - q[1]) / q[4]); e += (k - 1) ** 2; } return e; };
  let q = x0.slice(), e = err(q), st = 0.01;
  for (let it = 0; it < 400 && st > 1e-5; it++) {
    let better = false;
    for (let j = 0; j < 5; j++) for (const s of [1, -1]) { const t = q.slice(); t[j] += s * st; const et = err(t); if (et < e) { e = et; q = t; better = true; } }
    if (!better) st *= 0.5;
  }
  return { c: [0, q[0], q[1]], r: [q[2], q[3], q[4]] };
}
