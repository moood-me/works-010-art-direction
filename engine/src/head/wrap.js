// The wrap (Г3, experiments/heads-wrap): Anny's own head mesh laid onto a designed form (src/head/forms.js) — its
// topology, bones and weights kept, so it stays one skin with the neck (no seam) and moves with the skeleton. In order:
//   the neck slimmed (drawn necks are thin) → Anny's landmarks found on her own surface (eyes, mouth corners and
//   middle, ears, chin, top, back) and moved to where the form has them; her midline from the root of the nose over
//   its tip to the mouth laid point by point along the form's profile; her lips' seam along the drawn mouth's line;
//   points down the neck held → one smooth warp through them (biharmonic, with an affine part) → the nose's sides move
//   with its midline → onto the form in rounds, each round's pull smoothed over the mesh as one field → exactly onto
//   it, the spacing evened along it, the join with the neck eased → folds (triangles facing away from the form) eased
//   until none is left. The strength blends Anny's head and the wrapped one.
// Its parameters: form (src/head/forms.js), marks — where the form has the eyes ({x, y, w, h}) and the mouth
// ({y, w, sag, wide: a grin's width}) in head units (a solid's: in its face units) — a head's features are usually
// drawn there too —, neckSlim, onto — where down the neck the skin is laid fully on the form (from the head's share
// onto[0], nothing, to onto[1], all: Г3's 0.35–0.95; Г2 set it on nearly all the way down, 0.02–0.17).
// All lengths that are Anny's (how near a point must be to a landmark) are scaled by the head's own size against
// moood's woman, whose head they were found on.
import { register } from '../deform.js';
import { headFrame, headShares } from './frame.js';
import { formOf, FORM_SCHEMA } from './forms.js';
import { gradOf, frontZ, projectOn } from './shapes.js';
import { smoothField } from '../regions.js';
import { neighboursOf } from '../mesh.js';
import { lerp, clamp, sst } from '../math.js';

const num = (min, max) => ({ type: 'number', min, max });
export const MARKS_SCHEMA = { type: 'object', required: ['eye', 'mouth'], props: {
  eye: { type: 'object', required: ['x', 'y', 'w', 'h'], props: { x: num(0, 2), y: num(-2, 2), w: num(0, 2), h: num(0, 2) } },
  mouth: { type: 'object', required: ['y', 'w'], props: { y: num(-3, 0), w: num(0, 2), sag: num(-1, 1), wide: { type: 'boolean' } } } } };

// the form as it is laid on this body: the form, its distance with the body's neck, the frame
export function formOnBody(form, body, neckSlim = 0.78) {
  const F = headFrame(body.rig, form.size ?? 1.1), sh = headShares(body.mesh, body.rig.skeleton), P = body.mesh.positions, N = body.mesh.N;
  // the neck where it meets the head: the ring of skin half head, half neck (after the slimming)
  const slim = slimmed(P, body, sh, neckSlim);
  let cx = 0, cy = 0, cz = 0, n = 0;
  for (let i = 0; i < N; i++) { const w = sh.head[i] + sh.neck[i]; if (w > 0.4 && w < 0.7) { cx += slim[i * 3]; cy += slim[i * 3 + 1]; cz += slim[i * 3 + 2]; n++; } }
  cx /= n; cy /= n; cz /= n;
  let r = 0, m = 0;
  for (let i = 0; i < N; i++) { const w = sh.head[i] + sh.neck[i]; if (w > 0.4 && w < 0.7 && Math.abs(slim[i * 3 + 1] - cy) < 0.02) { r += Math.hypot(slim[i * 3] - cx, slim[i * 3 + 2] - cz); m++; } }
  r /= m;
  const neck = { c: [(cx - F.O[0]) / F.R, (cy - 0.07 - F.O[1]) / F.R, (cz - F.O[2]) / F.R], r: r * 1.14 / F.R };
  return { ...formOf(form, { neck, place: form.kind === 'solid' ? form.place ?? placeOnCranium(form, body, sh, F) : null }), frame: F, shares: sh, slim };
}
// a solid's marks are in its face units: in head units
function marksOnHead({ eye, mouth }, G) {
  const s = G.toHead([1, 0, 0])[0] - G.toHead([0, 0, 0])[0], e = G.toHead([eye.x, eye.y, 0]), m = G.toHead([0, mouth.y, 0]);
  return { eye: { x: e[0], y: e[1], w: eye.w * s, h: eye.h * s }, mouth: { ...mouth, y: m[1], w: mouth.w * s, ...(mouth.sag ? { sag: mouth.sag * s } : {}) } };
}
// a solid's face units laid on the body (Г2's way, experiments/heads-mesh/py/build.py): its cranium on Anny's cranium (a
// quadric fitted to her skin above the eyes), scaled by the cranium's width — as {at, scale} in head units — and her
// neck measured for its underside to ease into
function placeOnCranium(form, body, sh, F) {
  const P = body.mesh.positions, sk = body.rig.skeleton, J = body.rig.joints, used = body.mesh.isUsed, N = body.mesh.N;
  const ey = (J[sk.index.LeftEye * 3 + 1] + J[sk.index.RightEye * 3 + 1]) / 2;
  let chinY = Infinity; for (let i = 0; i < N; i++) if (used[i] && sh.head[i] > 0.6 && Math.abs(P[i * 3]) < 0.006 && P[i * 3 + 2] > J[sk.index.Jaw * 3 + 2]) chinY = Math.min(chinY, P[i * 3 + 1]);
  const U = ey - chinY, A = Array.from({ length: 5 }, () => new Float64Array(5)), b = new Float64Array(5);
  for (let i = 0; i < N; i++) {
    if (!used[i] || sh.head[i] <= 0.9 || P[i * 3 + 1] <= ey + 0.25 * U) continue;
    const x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2], r = [x * x, y * y, z * z, y, z];
    for (let a = 0; a < 5; a++) { b[a] += r[a]; for (let c = 0; c < 5; c++) A[a][c] += r[a] * r[c]; }
  }
  const c = solve(A, b), cy = -c[3] / (2 * c[1]), cz = -c[4] / (2 * c[2]), g = 1 + c[1] * cy * cy + c[2] * cz * cz, rx = Math.sqrt(g / c[0]);
  const cr = form.cranium ?? { at: [0, 0.2, -0.85], r: [0.9, 0.95, 1] }, Ut = rx * (form.size ?? 1) / cr.r[0];
  const O = [-Ut * cr.at[0], cy - Ut * cr.at[1], cz - Ut * cr.at[2]];
  // her neck, measured (two sections below the chin), for the solid's underside to ease into: an elliptic capsule
  const sec = [chinY - 0.2 * U, chinY - 0.6 * U].map(yy => {
    let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity;
    for (let i = 0; i < N; i++) if (used[i] && sh.head[i] < 0.5 && Math.abs(P[i * 3 + 1] - yy) < 0.04 * U && Math.abs(P[i * 3]) < 0.07 && P[i * 3 + 2] > J[sk.index.LeftEye * 3 + 2] - 0.2) { x0 = Math.min(x0, P[i * 3]); x1 = Math.max(x1, P[i * 3]); z0 = Math.min(z0, P[i * 3 + 2]); z1 = Math.max(z1, P[i * 3 + 2]); }
    return { y: yy, z: (z0 + z1) / 2, rx: (x1 - x0) / 2, rz: (z1 - z0) / 2 };
  });
  const toH = (y, z) => [0, (y - F.O[1]) / F.R, (z - F.O[2]) / F.R], lo = toH(sec[1].y, sec[1].z), hi = toH(sec[0].y, sec[0].z), dn = [0, hi[1] - lo[1], hi[2] - lo[2]];
  const neck = { a: [0, lo[1] - 2 * dn[1], lo[2] - 2 * dn[2]], b: [0, hi[1] + 1.2 * dn[1], hi[2] + 1.2 * dn[2]], rx: sec[0].rx / F.R, rz: sec[0].rz / F.R };
  return { at: [(O[0] - F.O[0]) / F.R, (O[1] - F.O[1]) / F.R, (O[2] - F.O[2]) / F.R], scale: Ut / F.R, neck };
}
// the neck slimmed about its own line (Neck2's), fading out where neck and head end
function slimmed(P, body, sh, k) {
  const out = Float32Array.from(P), sk = body.rig.skeleton, J = body.rig.joints, j = sk.index.Neck2, nx = J[j * 3], nz = J[j * 3 + 2];
  for (let i = 0; i < body.mesh.N; i++) { const h = Math.min(1, sh.neck[i] + sh.head[i]), w = h * k + (1 - h); out[i * 3] = nx + (P[i * 3] - nx) * w; out[i * 3 + 2] = nz + (P[i * 3 + 2] - nz) * w; }
  return out;
}

register({
  kind: 'wrap', of: 'skin', ownFolds: true,
  params: { form: FORM_SCHEMA, marks: MARKS_SCHEMA, neckSlim: num(0.3, 1.5), onto: { type: 'array', min: 2, max: 2, items: num(0, 1) } },
  defaults: { neckSlim: 0.78, onto: [0.35, 0.95] },
  rest(p, R, { body }) {
    const wrapped = wrapHead(body, p.form, p.marks, p.neckSlim, p.onto), P0 = body.mesh.positions, k = p.strength;
    const positions = Float32Array.from(P0, (v, i) => v + (wrapped[i] - v) * k);
    return { positions };
  },
});

export function wrapHead(body, form, marks, neckSlim = 0.78, onto = [0.35, 0.95]) {
  const G = formOnBody(form, body, neckSlim), { toL, toW, R: HR } = G.frame, hsdf = G.sdf, sk = body.rig.skeleton, J = body.rig.joints;
  const mesh = body.mesh, N = mesh.N, used = mesh.isUsed, nbr = neighboursOf(mesh), { head: headW, jaw: jawW, omega } = G.shares;
  const at = Float32Array.from(G.slim), u = (J[sk.index.HeadEnd * 3 + 1] - J[sk.index.Head * 3 + 1]) / 0.151;   // Anny's lengths, scaled
  const jt = n => { const j = sk.index[n]; return [J[j * 3], J[j * 3 + 1], J[j * 3 + 2]]; };
  const g = [0, 0, 0], grad = (x, y, z) => gradOf(hsdf, x, y, z, 0.004, g), surfZ = (x, y) => frontZ(hsdf, x, y);
  const { eye: E, mouth: M } = G.toHead ? marksOnHead(marks, G) : marks, yChin = G.chin, ears = G.ears ?? { x: 0.92, y: -0.32, z: -0.12 };   // (a solid's ears: src/head/forms.js)
  const MH = M.wide ? M.w : M.w / 2, MS = M.wide ? { w: 0.8 * M.w, y: M.y + 0.005, sag: 0.2 * M.w } : { w: Math.max(MH * 1.05, 0.14), y: M.y, sag: M.sag ?? 0 };
  const front = (x, y, rx = 0.006 * u, ry = 0.006 * u) => { let best = -1, bz = -9; for (let i = 0; i < N; i++) { if (!used[i] || headW[i] < 0.3) continue; const X = at[i * 3], Y = at[i * 3 + 1], Z = at[i * 3 + 2]; if (Math.abs(X - x) < rx && Math.abs(Y - y) < ry && Z > bz) { bz = Z; best = i; } } return best; };
  const eL = jt('LeftEye'), jaw = jt('Jaw'), chest = jt('Chest'), neck2 = jt('Neck2');
  const src = [], dst = [], pinned = new Uint8Array(N);
  const add = (i, t) => { if (i < 0) return; pinned[i] = 1; src.push([at[i * 3], at[i * 3 + 1], at[i * 3 + 2]]); dst.push(toW(...t)); };
  const X = i => at[i * 3], Y = i => at[i * 3 + 1], Z = i => at[i * 3 + 2];
  let tipI = -1; for (let i = 0, tz = -9; i < N; i++) if (used[i] && headW[i] > 0.5 && Math.abs(X(i)) < 0.004 * u && Y(i) < eL[1] && Y(i) > jaw[1] - 0.02 * u && Z(i) > tz) { tz = Z(i); tipI = i; }
  // the lip seam: where the jaw's weight changes, in front
  const seam = []; for (let i = 0; i < N; i++) if (used[i] && jawW[i] > 0.25 && jawW[i] < 0.75 && Z(i) > Z(tipI) - 0.03 * u && Y(i) < Y(tipI) - 0.005 * u && Math.abs(X(i)) < 0.03 * u) seam.push(i);
  let mL = seam[0], mC = seam[0]; for (const i of seam) { if (X(i) > X(mL)) mL = i; if (Math.abs(X(i)) < 0.003 * u && Z(i) > Z(mC) - 1) mC = Math.abs(X(i)) < Math.abs(X(mC)) + 0.002 * u && Z(i) >= Z(mC) ? i : mC; }
  let chinI = -1; for (let i = 0, cy = 9; i < N; i++) if (used[i] && headW[i] > 0.5 && Math.abs(X(i)) < 0.004 * u && Z(i) > jaw[2] + 0.035 * u && Y(i) < cy) { cy = Y(i); chinI = i; }
  let earI = -1; for (let i = 0, ex = 0; i < N; i++) if (used[i] && headW[i] > 0.6 && X(i) > ex && Y(i) < eL[1] + 0.01 * u) { ex = X(i); earI = i; }
  let topI = -1; for (let i = 0, ty = 0; i < N; i++) if (used[i] && Y(i) > ty) { ty = Y(i); topI = i; }
  let backI = -1; for (let i = 0, bz = 9; i < N; i++) if (used[i] && headW[i] > 0.6 && Math.abs(Y(i) - eL[1]) < 0.006 * u && Math.abs(X(i)) < 0.01 * u && Z(i) < bz) { bz = Z(i); backI = i; }
  const mir = i => { let best = -1, bd = 9; for (let j = 0; j < N; j++) { if (!used[j]) continue; const d = Math.hypot(X(j) + X(i), Y(j) - Y(i), Z(j) - Z(i)); if (d < bd) { bd = d; best = j; } } return best; };
  const eyeAnny = { w: 0.03 * u, h: 0.012 * u };
  for (const s of [1, -1]) {
    const ex0 = s * Math.abs(eL[0]), ey0 = eL[1];
    for (const [ux, uy] of [[0, 0], [-0.5, 0], [0.5, 0], [0, 0.5], [0, -0.5]]) { const i = front(ex0 + s * ux * eyeAnny.w, ey0 + uy * eyeAnny.h); const x = s * (E.x + ux * E.w), y = E.y + uy * E.h; add(i, [x, y, surfZ(x, y)]); }
    add(s > 0 ? mL : mir(mL), [s * MS.w, MS.y, surfZ(s * MS.w, MS.y)]);   // the lips' seam keeps room to open, however small the drawn mouth
    add(s > 0 ? earI : mir(earI), [s * (ears.x + 0.08), ears.y, ears.z]);
  }
  add(mC, [0, MS.y - MS.sag, surfZ(0, MS.y - MS.sag)]);
  add(chinI, [0, yChin + 0.05, surfZ(0, yChin + 0.05) - 0.02]);
  const top = form.kind === 'curves' ? 1.08 * (form.cranium?.h ?? 1) + 0.02 : (() => { let y = 2; while (hsdf(0, y, 0) > 0 && y > 0) y -= 0.005; return y; })();
  add(topI, [0, top, 0]);
  const back = form.kind === 'curves' ? -1.05 * (form.cranium?.d ?? 1.05) : (() => { let z = -2.5; while (hsdf(0, -0.3, z) > 0 && z < 0) z += 0.005; return z; })();
  add(backI, [0, -0.3, back]);
  // the profile, point by point: Anny's midline from the root of the nose over its tip down to the mouth is laid along
  // the form's own profile — root to root, tip to tip, mouth to mouth, and between them by length along the curve
  const mids = []; let midTop = 0;
  {
    const mid = []; for (let i = 0; i < N; i++) if (used[i] && headW[i] > 0.5 && Math.abs(X(i)) < 0.0015 * u && Z(i) > jaw[2] + 0.02 * u && Y(i) < eL[1] + 0.006 * u && Y(i) > Y(mC) + 0.0015 * u) mid.push(i);
    mid.sort((a, b) => Y(b) - Y(a));
    let aRoot = mid[0]; for (const i of mid) if (Y(i) > Y(tipI) && Z(i) < Z(aRoot)) aRoot = i;
    const annyUp = mid.filter(i => Y(i) <= Y(aRoot) && Y(i) >= Y(tipI)), annyDn = mid.filter(i => Y(i) < Y(tipI));
    const prof = []; for (let y = E.y + 0.02; y >= MS.y - MS.sag; y -= 0.004) prof.push([y, surfZ(0, y)]);
    let dTip = 0; for (let k = 0; k < prof.length; k++) if (prof[k][1] > prof[dTip][1]) dTip = k;
    let dRoot = 0; for (let k = 0; k < dTip; k++) if (prof[k][1] < prof[dRoot][1]) dRoot = k;
    // under the tip the form turns back in: follow it as a curve, not a jump
    const under = []; { const tip = prof[dTip]; for (let k = 1; k <= 12; k++) { const y = tip[0] - k * 0.006; let z = tip[1]; for (let it = 0; it < 80; it++) { if (hsdf(0, y, z) >= -0.002) break; z -= 0.004; } under.push([y, z]); if (y < M.y) break; } }
    const lengths = Q => { const L = [0]; for (let k = 1; k < Q.length; k++) L.push(L[k - 1] + Math.hypot(Q[k][0] - Q[k - 1][0], Q[k][1] - Q[k - 1][1])); return L; };
    const along = (Q, t) => { const L = lengths(Q), T = t * L[L.length - 1]; let k = 1; while (k < L.length - 1 && L[k] < T) k++; const f = (T - L[k - 1]) / Math.max(1e-9, L[k] - L[k - 1]); return [lerp(Q[k - 1][0], Q[k][0], f), lerp(Q[k - 1][1], Q[k][1], f)]; };
    const annyAlong = I => { const L = lengths(I.map(i => [Y(i), Z(i)])); return L.map(l => l / Math.max(1e-9, L[L.length - 1])); };
    const lay = (I, Q) => { const t = annyAlong(I); I.forEach((i, k) => { const [y, z] = along(Q, t[k]); const w = toW(0, y, z); mids.push([Y(i), w[1] - Y(i), w[2] - Z(i)]); if (k % 2) return; add(i, [0, y, z]); }); };
    lay(annyUp, prof.slice(dRoot, dTip + 1));
    lay(annyDn, [prof[dTip], ...under.filter(q => q[0] > MS.y - MS.sag), [MS.y - MS.sag, surfZ(0, MS.y - MS.sag)]]);
    midTop = Y(aRoot);
  }
  // the mouth: Anny's lips' seam laid along the drawn mouth's line, end to end, so it opens where the drawing is
  {
    const S = new Set(), T = mesh.triangles;
    for (let t = 0; t < T.length; t += 3) {
      const v = [T[t], T[t + 1], T[t + 2]], j = v.map(i => jawW[i]); if (Math.max(...j) - Math.min(...j) < 0.5) continue;
      if (v.some(i => !used[i] || headW[i] < 0.5 || Z(i) < Z(tipI) - 0.035 * u || Math.abs(Y(i) - Y(mC)) > 0.012 * u || Math.abs(X(i)) > 0.03 * u)) continue; v.forEach(i => S.add(i));
    }
    let xA = 0; for (const i of S) xA = Math.max(xA, Math.abs(X(i)));
    for (const i of S) { if (pinned[i]) continue; const f = X(i) / xA, x = f * MS.w, y = MS.y + (jawW[i] > 0.5 ? -0.0015 : 0.0015) - MS.sag * (1 - f * f); add(i, [x, y, surfZ(x, y) - 0.004 * (1 - f * f)]); }
  }
  // the neck stays Anny's: points well down the neck hold still
  for (let i = 0; i < N; i += 37) if (used[i] && omega[i] < 0.02 && Y(i) > chest[1] && Y(i) < neck2[1] + 0.02 * u) { src.push([X(i), Y(i), Z(i)]); dst.push([X(i), Y(i), Z(i)]); }
  const warp = biharmonic(src, dst), wrapped = Float32Array.from(at), d3 = [0, 0, 0];
  for (let i = 0; i < N; i++) { if (omega[i] < 0.001) continue; warp(X(i), Y(i), Z(i), d3); for (let c = 0; c < 3; c++) wrapped[i * 3 + c] += d3[c] * omega[i]; }
  // the nose goes as one piece with its midline: its sides move as the ridge at their height moves, fading out to the
  // cheeks, so a long nose takes its own skin with it and the cheeks stay where they are
  if (mids.length > 4) {
    const md = mids.sort((a, b) => b[0] - a[0]), nW = 0.017 * u;
    const dAt = y => { if (y >= md[0][0]) return md[0]; if (y <= md[md.length - 1][0]) return md[md.length - 1]; let k = 1; while (md[k][0] > y) k++; const f = (md[k - 1][0] - y) / Math.max(1e-9, md[k - 1][0] - md[k][0]); return [y, lerp(md[k - 1][1], md[k][1], f), lerp(md[k - 1][2], md[k][2], f)]; };
    for (let i = 0; i < N; i++) {
      if (!used[i] || headW[i] < 0.5) continue; const x = X(i), y = Y(i), z = Z(i);
      if (y > midTop + 0.004 * u || y < md[md.length - 1][0] - 0.002 * u || z < Z(tipI) - 0.045 * u) continue;
      const f = Math.exp(-((x / nW) ** 2) * 2.2) * sst(clamp((midTop + 0.004 * u - y) / (0.012 * u), 0, 1)); if (f < 0.01) continue;
      const d = dAt(y); wrapped[i * 3] = lerp(wrapped[i * 3], x * (1 + 0.6 * f), f); wrapped[i * 3 + 1] = lerp(wrapped[i * 3 + 1], y + d[1], f); wrapped[i * 3 + 2] = lerp(wrapped[i * 3 + 2], z + d[2], f);
    }
  }
  // onto the form: each round, where every point wants to go, smoothed over the mesh as one field
  const inHead = i => used[i] && omega[i] > 0.02, keepOut = Uint8Array.from(used, v => v ? 1 : 0);
  for (let round = 0; round < 14; round++) {
    const disp = new Float32Array(N * 3), its = Math.round(lerp(30, 4, round / 13));
    for (let i = 0; i < N; i++) {
      if (!inHead(i)) continue; const [x, y, z] = toL(wrapped[i * 3], wrapped[i * 3 + 1], wrapped[i * 3 + 2]); if (y < yChin - 0.6) continue;
      const d = hsdf(x, y, z); grad(x, y, z); const gl = Math.hypot(g[0], g[1], g[2]) || 1, k = clamp(d, -0.15, 0.15) * HR / gl;
      for (let c = 0; c < 3; c++) disp[i * 3 + c] = -g[c] * k / gl * omega[i] ** 2;
    }
    smoothField(disp, 3, nbr, its, keepOut);
    for (let i = 0; i < N * 3; i++) wrapped[i] += disp[i] * 0.9;
  }
  // last: exactly onto the form along the normal, the spacing evened along it, the join with the neck eased
  {
    const fin = Float32Array.from(wrapped);
    for (let i = 0; i < N; i++) { if (!inHead(i)) continue; const q = projectOn(hsdf, toL(wrapped[i * 3], wrapped[i * 3 + 1], wrapped[i * 3 + 2]), 4), f = sst(clamp((omega[i] - onto[0]) / (onto[1] - onto[0]), 0, 1)), w = toW(...q); for (let c = 0; c < 3; c++) fin[i * 3 + c] = lerp(wrapped[i * 3 + c], w[c], f); }
    for (let it = 0; it < 60; it++) {
      const nx = Float32Array.from(fin);
      for (let i = 0; i < N; i++) {
        if (!used[i] || omega[i] < 0.95 || pinned[i]) continue; let ax = 0, ay = 0, az = 0; const a = nbr.start[i], b = nbr.start[i + 1];
        for (let q = a; q < b; q++) { const j = nbr.list[q]; ax += fin[j * 3]; ay += fin[j * 3 + 1]; az += fin[j * 3 + 2]; }
        const n = b - a; nx.set(toW(...projectOn(hsdf, toL(lerp(fin[i * 3], ax / n, 0.5), lerp(fin[i * 3 + 1], ay / n, 0.5), lerp(fin[i * 3 + 2], az / n, 0.5)), 3)), i * 3);
      }
      fin.set(nx);
    }
    // where the head fades into the neck: the difference smoothed, so the join has no crease
    const dd = Float32Array.from(fin, (v, i) => v - at[i]), band = Uint8Array.from(omega, (w, i) => used[i] && w <= 0.97 && w >= 0.005 ? 1 : 0);
    smoothField(dd, 3, nbr, 40, band);
    for (let i = 0; i < N * 3; i++) wrapped[i] = at[i] + dd[i];
  }
  at.set(wrapped);
  // folds: a triangle that faces away from the form (or edge-on to it) is a pleat — its points and their neighbours are
  // eased toward their neighbours' middle and laid back onto the form, until no pleat is left
  const T = mesh.triangles;
  for (let round = 0; round < 200; round++) {   // (Г3 stopped at 40 and left a few three-deep pleats under the eyes)
    const bad = new Uint8Array(N); let nb = 0;
    for (let t = 0; t < T.length; t += 3) {
      const a = T[t], b = T[t + 1], c = T[t + 2]; if (Math.min(omega[a], omega[b], omega[c]) < 0.9) continue;
      const ux = X(b) - X(a), uy = Y(b) - Y(a), uz = Z(b) - Z(a), vx = X(c) - X(a), vy = Y(c) - Y(a), vz = Z(c) - Z(a);
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx, nl = Math.hypot(nx, ny, nz);
      if (nl < 1e-14) { bad[a] = bad[b] = bad[c] = 1; nb++; continue; }
      grad(...toL((X(a) + X(b) + X(c)) / 3, (Y(a) + Y(b) + Y(c)) / 3, (Z(a) + Z(b) + Z(c)) / 3)); const gl = Math.hypot(g[0], g[1], g[2]) || 1;
      if ((nx * g[0] + ny * g[1] + nz * g[2]) / (nl * gl) < 0.85) { bad[a] = bad[b] = bad[c] = 1; nb++; }
    }
    if (!nb) break;
    let grow = bad;
    for (let r = 0; r < 2; r++) { const g2 = Uint8Array.from(grow); for (let i = 0; i < N; i++) if (grow[i]) for (let q = nbr.start[i]; q < nbr.start[i + 1]; q++) { const j = nbr.list[q]; if (omega[j] > 0.9) g2[j] = 1; } grow = g2; }
    if (round < 6) for (let i = 0; i < N; i++) if (pinned[i]) grow[i] = 0;
    for (let it = 0; it < 6; it++) {
      const nx = Float32Array.from(at);
      for (let i = 0; i < N; i++) {
        if (!grow[i]) continue; let ax = 0, ay = 0, az = 0; const a = nbr.start[i], b = nbr.start[i + 1], n = b - a;
        for (let q = a; q < b; q++) { const j = nbr.list[q]; ax += at[j * 3]; ay += at[j * 3 + 1]; az += at[j * 3 + 2]; }
        nx.set(toW(...projectOn(hsdf, toL(lerp(X(i), ax / n, 0.6), lerp(Y(i), ay / n, 0.6), lerp(Z(i), az / n, 0.6)), 3)), i * 3);
      }
      at.set(nx);
    }
  }
  return at;
}

// a smooth warp through points (src → dst): biharmonic radial basis (|r|) plus an affine part — as a function
// (x, y, z, out) → the move there
export function biharmonic(src, dst) {
  const n = src.length, m = n + 4, A = Array.from({ length: m }, () => new Float64Array(m)), B = [0, 1, 2].map(() => new Float64Array(m));
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) A[i][j] = Math.hypot(src[i][0] - src[j][0], src[i][1] - src[j][1], src[i][2] - src[j][2]);
    A[i][n] = 1; A[i][n + 1] = src[i][0]; A[i][n + 2] = src[i][1]; A[i][n + 3] = src[i][2];
    for (let k = 0; k < 4; k++) A[n + k][i] = A[i][n + k];
    for (let c = 0; c < 3; c++) B[c][i] = dst[i][c] - src[i][c];
  }
  const W = B.map(b => solve(A, b)), S = Float64Array.from(src.flat());
  return (x, y, z, out = [0, 0, 0]) => {
    for (let c = 0; c < 3; c++) {
      const w = W[c]; let v = w[n] + w[n + 1] * x + w[n + 2] * y + w[n + 3] * z;
      for (let i = 0; i < n; i++) v += w[i] * Math.hypot(x - S[i * 3], y - S[i * 3 + 1], z - S[i * 3 + 2]);
      out[c] = v;
    }
    return out;
  };
}
// Gauss–Jordan with partial pivoting
export function solve(A0, b0) {
  const m = A0.length, a = A0.map(r => Float64Array.from(r)), b = Float64Array.from(b0);
  for (let i = 0; i < m; i++) {
    let p = i; for (let r = i + 1; r < m; r++) if (Math.abs(a[r][i]) > Math.abs(a[p][i])) p = r;
    [a[i], a[p]] = [a[p], a[i]]; [b[i], b[p]] = [b[p], b[i]];
    const d = a[i][i] || 1e-12;
    for (let r = 0; r < m; r++) { if (r === i) continue; const f = a[r][i] / d; if (!f) continue; for (let c = i; c < m; c++) a[r][c] -= f * a[i][c]; b[r] -= f * b[i]; }
  }
  return Float64Array.from(b, (v, i) => v / (a[i][i] || 1e-12));
}
