// A hairstyle onto a head. Hairstyles are designed round the neutral head of the design space (src/hair/build.js: its
// cranium an ellipsoid, CRANIUM; its whole form headSDF); a head's own cranium is fitted with an ellipsoid too — through
// its designed form where it has one (a wrap's: the form's surface found along rays from its middle), else through its
// skin — its points above the brows. Every point of the hairstyle is carried over as В1 carried it
// (experiments/hair/fit.js): what lies on the designed skull lands on the head's, what lies off it keeps its direction
// from it and its distance, grown with the head (a bigger head, a bigger hairstyle). Then, near the skull, the head is
// not an ellipsoid: each point is moved along the skull's normal until it lies as far from the head's real surface (its
// form, else its skin) as it lay from the designed head's, grown with the head — so the roots and the hairline sit on the
// scalp as designed (under it as deep, over it as high) and the locks keep their lift off the head's own form. That
// fades out by FADE head units off the skull (what hangs free keeps its carried place).
//   fitOn({frame, form, body, sk}, design) → {map(x, y, z, out) → rest point (metres), scale, skull}
// body: the head's body (its skin at its rest, or as a change of the rest has it: src/hair/hair.js grows the hair with it);
// design: the hairstyle's designed head (build.js headSDF(style.head).sdf)
import { CRANIUM } from './build.js';
import { headShares } from '../head/frame.js';
import { normalsOf } from '../mesh.js';
import { surfaceDistance } from '../solids.js';
import { sst, clamp } from '../math.js';

// (in the skull's own units: a share of its radius) the correction is whole up to NEAR off the skull, gone by FADE; it
// moves a point at most REACH
const NEAR = 0.1, FADE = 0.55, REACH = 0.35, AZ = 48, EL = 32;

export function fitOn({ frame: F, form, body, sk }, designed) {
  const J = body.rig.joints, eyeY = (J[sk.index.LeftEye * 3 + 1] + J[sk.index.RightEye * 3 + 1]) / 2;
  // the head's surface: on its form (head units → metres), or its skin
  const skin = form ? null : skinOf(body, sk), surface = form ? formPoints(form, F) : skin.points;
  const top = surface.filter(p => p[1] > eyeY + 0.34 * F.R);
  const c0 = CRANIUM.c, r0 = CRANIUM.r;
  const E = fitEllipsoid(top, [F.O[1], F.O[2], r0[0], r0[1], r0[2]]), C = E.c, R = E.r;
  const r0m = (r0[0] + r0[1] + r0[2]) / 3, scale = (R[0] + R[1] + R[2]) / 3 / r0m;
  // how far a point lies from the head's real surface
  const real = form ? (x, y, z) => form.full((x - F.O[0]) / F.R, (y - F.O[1]) / F.R, (z - F.O[2]) / F.R) * F.R : skin.distance;
  const map = (x, y, z, out = [0, 0, 0]) => {
    const qx = (x - c0[0]) / r0[0], qy = (y - c0[1]) / r0[1], qz = (z - c0[2]) / r0[2], k = Math.hypot(qx, qy, qz) || 1;
    const sx = c0[0] + r0[0] * qx / k, sy = c0[1] + r0[1] * qy / k, sz = c0[2] + r0[2] * qz / k;   // on the designed skull
    const tx = C[0] + R[0] * qx / k, ty = C[1] + R[1] * qy / k, tz = C[2] + R[2] * qz / k;           // on the head's
    out[0] = tx + (x - sx) * scale; out[1] = ty + (y - sy) * scale; out[2] = tz + (z - sz) * scale;
    const off = k - 1, w = 1 - sst(clamp((off - NEAR) / (FADE - NEAR), 0, 1));
    if (w <= 0) return out;
    // along the head's skull normal there (the ellipsoid's, outward), to the designed distance from the real surface
    let nx = (tx - C[0]) / (R[0] * R[0]), ny = (ty - C[1]) / (R[1] * R[1]), nz = (tz - C[2]) / (R[2] * R[2]); const nl = Math.hypot(nx, ny, nz) || 1; nx /= nl; ny /= nl; nz /= nl;
    const want = designed(x, y, z) * scale, f = t => real(out[0] + nx * t, out[1] + ny * t, out[2] + nz * t) - want, lim = REACH * F.R;
    // (a secant along the normal, from the carried place; a surface out of reach of a skin's points is left as it is)
    let a = 0, fa = f(0); if (!Number.isFinite(fa)) return out;
    let b = -fa, fb = f(b);
    for (let it = 0; it < 4 && Number.isFinite(fb) && Math.abs(fb) > 1e-5 && fb !== fa; it++) { const c = clamp(b - fb * (b - a) / (fb - fa), -lim, lim); a = b; fa = fb; b = c; fb = f(b); }
    const t = Number.isFinite(fb) && Math.abs(fb) < Math.abs(f(0)) ? b : 0;
    out[0] += nx * t * w; out[1] += ny * t * w; out[2] += nz * t * w;
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
// the head's skin: its vertices mostly on the head's joints, and its distance (the body's rest, or the rest it is given)
function skinOf(body, sk) {
  const { head } = headShares(body.mesh, sk), P = body.mesh.positions, N = normalsOf(P, body.mesh.triangles, undefined, body.mesh.used), points = [], pn = [];
  for (const i of body.mesh.used) if (head[i] > 0.5) { points.push([P[i * 3], P[i * 3 + 1], P[i * 3 + 2]]); pn.push(N[i * 3], N[i * 3 + 1], N[i * 3 + 2]); }
  return { points, distance: surfaceDistance(Float32Array.from(points.flat()), Float32Array.from(pn)) };
}
// an axis-aligned ellipsoid (its middle on x = 0: the head is symmetric) through points, by shrinking steps on each
// parameter (q: [y, z, rx, ry, rz])
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
