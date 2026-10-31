// ———— the wrap: Anny's own head, fitted onto the drawn head (landmarks first, then the surface, as one smooth field) ————
const R = 0.088 * (CH.hs || 1.1) * (J[JI.HeadEnd].y - J[JI.Head].y) / 0.151;
const O = J[JI.Head].clone().add(new V3(0, 0.62 * R, -0.03 * R));
const hsdf = headSDF(H);
const toL = (x, y, z) => [(x - O.x) / R, (y - O.y) / R, (z - O.z) / R], toW = (x, y, z) => [O.x + x * R, O.y + y * R, O.z + z * R];
const NBR = (() => { const s = Array.from({ length: N }, () => new Set()); for (let t = 0; t < bs.tris.length; t += 3) { const a = bs.tris[t], b = bs.tris[t + 1], c = bs.tris[t + 2]; s[a].add(b).add(c); s[b].add(a).add(c); s[c].add(a).add(b); } return s.map(q => Int32Array.from(q)); })();
const diffuse = (f, its, keepFn) => { let a = Float32Array.from(f), b = new Float32Array(f.length), dim = f.length / N; for (let it = 0; it < its; it++) { for (let i = 0; i < N; i++) { const ns = NBR[i]; for (let c = 0; c < dim; c++) { if (!ns.length || (keepFn && keepFn(i))) { b[i * dim + c] = a[i * dim + c]; continue; } let s = 0; for (const j of ns) s += a[j * dim + c]; b[i * dim + c] = 0.5 * a[i * dim + c] + 0.5 * s / ns.length; } } [a, b] = [b, a]; } return a; };
const sdfGrad = (x, y, z) => { const e = 0.004; return [hsdf(x + e, y, z) - hsdf(x - e, y, z), hsdf(x, y + e, z) - hsdf(x, y - e, z), hsdf(x, y, z + e) - hsdf(x, y, z - e)].map(v => v / (2 * e)); };
const surfZ = (x, y) => { let z = 2.5; for (let k = 0; k < 120; k++) { const d = hsdf(x, y, z); if (d < 0.001) break; z -= Math.max(d, 0.004); } return z; };
// how much of each point is head: the head fully, fading down the neck
const used = new Uint8Array(N); for (const v of bs.tris) used[v] = 1;
const jawW = Float32Array.from({ length: N }, (_, i) => wOf(bs.joint, bs.weight, i, /^Jaw$/));
let omega = diffuse(Float32Array.from(headW, w => clamp(w * 1.25, 0, 1)), 8);
// Anny's landmarks, found on her own surface
const L0 = toL(0, 0, 0), front = (x, y, rx = 0.006, ry = 0.006) => { let best = -1, bz = -9; for (let i = 0; i < N; i++) { if (!used[i] || headW[i] < 0.3) continue; const X = at[i * 3], Y = at[i * 3 + 1], Z = at[i * 3 + 2]; if (Math.abs(X - x) < rx && Math.abs(Y - y) < ry && Z > bz) { bz = Z; best = i; } } return best; };
const eL = J[JI.LeftEye], src = [], dst = [];
const add = (i, t) => { if (i < 0) return; src.push([at[i * 3], at[i * 3 + 1], at[i * 3 + 2]]); dst.push(toW(...t)); };
const E = CH.face.eye, M = CH.face.mouth, F = H.face, yChin = F.W[F.W.length - 1][0];
let tipI = -1, tz = -9; for (let i = 0; i < N; i++) if (used[i] && headW[i] > 0.5 && Math.abs(at[i * 3]) < 0.004 && at[i * 3 + 1] < eL.y && at[i * 3 + 1] > J[JI.Jaw].y - 0.02 && at[i * 3 + 2] > tz) { tz = at[i * 3 + 2]; tipI = i; }
// the lip seam: where the jaw's weight changes, in front
const seam = []; for (let i = 0; i < N; i++) if (used[i] && jawW[i] > 0.25 && jawW[i] < 0.75 && at[i * 3 + 2] > at[tipI * 3 + 2] - 0.03 && at[i * 3 + 1] < at[tipI * 3 + 1] - 0.005 && Math.abs(at[i * 3]) < 0.03) seam.push(i);
let mL = seam[0], mC = seam[0]; for (const i of seam) { if (at[i * 3] > at[mL * 3]) mL = i; if (Math.abs(at[i * 3]) < 0.003 && at[i * 3 + 2] > at[mC * 3 + 2] - 1) mC = Math.abs(at[i * 3]) < Math.abs(at[mC * 3]) + 0.002 && at[i * 3 + 2] >= at[mC * 3 + 2] ? i : mC; }
let chinI = -1, cy = 9; for (let i = 0; i < N; i++) if (used[i] && headW[i] > 0.5 && Math.abs(at[i * 3]) < 0.004 && at[i * 3 + 2] > J[JI.Jaw].z + 0.035 && at[i * 3 + 1] < cy) { cy = at[i * 3 + 1]; chinI = i; }
let earI = -1, ex = 0; for (let i = 0; i < N; i++) if (used[i] && headW[i] > 0.6 && at[i * 3] > ex && at[i * 3 + 1] < eL.y + 0.01) { ex = at[i * 3]; earI = i; }
let topI = -1, ty = 0; for (let i = 0; i < N; i++) if (used[i] && at[i * 3 + 1] > ty) { ty = at[i * 3 + 1]; topI = i; }
let backI = -1, bz = 9; for (let i = 0; i < N; i++) if (used[i] && headW[i] > 0.6 && Math.abs(at[i * 3 + 1] - eL.y) < 0.006 && Math.abs(at[i * 3]) < 0.01 && at[i * 3 + 2] < bz) { bz = at[i * 3 + 2]; backI = i; }
const mir = i => { let best = -1, bd = 9; for (let j = 0; j < N; j++) { if (!used[j]) continue; const d = Math.hypot(at[j * 3] + at[i * 3], at[j * 3 + 1] - at[i * 3 + 1], at[j * 3 + 2] - at[i * 3 + 2]); if (d < bd) { bd = d; best = j; } } return best; };
const eyeAnny = { w: 0.03, h: 0.012 };
for (const s of [1, -1]) {
  const ex0 = s * Math.abs(eL.x), ey0 = eL.y;
  for (const [ux, uy] of [[0, 0], [-0.5, 0], [0.5, 0], [0, 0.5], [0, -0.5]]) { const i = front(ex0 + s * ux * eyeAnny.w, ey0 + uy * eyeAnny.h); const x = s * (E.x + ux * E.w), y = E.y + uy * E.h; add(i, [x, y, surfZ(x, y)]); }
  add(s > 0 ? mL : mir(mL), [s * M.w / 2 * 1.05, M.y, surfZ(s * M.w / 2 * 1.05, M.y)]);
  add(s > 0 ? earI : mir(earI), [s * (H.ears.x + 0.08), H.ears.y, H.ears.z]);
  const ns = s > 0 ? front(0.006 * s + 0.0, at[tipI * 3 + 1] - 0.006) : front(-0.006, at[tipI * 3 + 1] - 0.006);
}
const tipL = F.nose.ridge ? [0, ...F.nose.ridge[F.nose.ridge.length - 1]] : F.nose.tip;
add(tipI, [0, tipL[1], surfZ(0, tipL[1])]);
add(mC, [0, M.y, surfZ(0, M.y)]);
add(chinI, [0, yChin + 0.05, surfZ(0, yChin + 0.05) - 0.02]);
add(topI, [0, 1.08 * H.ch + 0.02, 0]);
add(backI, [0, -0.3, -surfZ(0, -0.3) * 0 - 1.05 * H.cd]);
// the neck stays Anny's: points well down the neck hold still
for (let i = 0; i < N; i += 37) if (used[i] && omega[i] < 0.02 && at[i * 3 + 1] > J[JI.Chest].y && at[i * 3 + 1] < J[JI.Neck2].y + 0.02) { src.push([at[i * 3], at[i * 3 + 1], at[i * 3 + 2]]); dst.push([at[i * 3], at[i * 3 + 1], at[i * 3 + 2]]); }
// a smooth warp through the landmarks (biharmonic radial basis plus an affine part)
const rbf = (() => { const n = src.length, A = Array.from({ length: n + 4 }, () => new Float64Array(n + 4)), B = [0, 1, 2].map(() => new Float64Array(n + 4));
  for (let i = 0; i < n; i++) { for (let j = 0; j < n; j++) A[i][j] = Math.hypot(src[i][0] - src[j][0], src[i][1] - src[j][1], src[i][2] - src[j][2]); A[i][n] = 1; A[i][n + 1] = src[i][0]; A[i][n + 2] = src[i][1]; A[i][n + 3] = src[i][2]; for (let k = 0; k < 4; k++) A[n + k][i] = A[i][n + k]; for (let c = 0; c < 3; c++) B[c][i] = dst[i][c] - src[i][c]; }
  const solve = (A0, b0) => { const m = A0.length, a = A0.map(r => Float64Array.from(r)), b = Float64Array.from(b0); for (let i = 0; i < m; i++) { let p = i; for (let r = i + 1; r < m; r++) if (Math.abs(a[r][i]) > Math.abs(a[p][i])) p = r; [a[i], a[p]] = [a[p], a[i]]; [b[i], b[p]] = [b[p], b[i]]; const d = a[i][i] || 1e-12; for (let r = 0; r < m; r++) { if (r === i) continue; const f = a[r][i] / d; if (!f) continue; for (let c = i; c < m; c++) a[r][c] -= f * a[i][c]; b[r] -= f * b[i]; } } return Float64Array.from(b, (v, i) => v / (a[i][i] || 1e-12)); };
  const W = B.map(b => solve(A, b));
  return (x, y, z) => [0, 1, 2].map(c => { const w = W[c]; let v = w[n] + w[n + 1] * x + w[n + 2] * y + w[n + 3] * z; for (let i = 0; i < n; i++) v += w[i] * Math.hypot(x - src[i][0], y - src[i][1], z - src[i][2]); return v; }); })();
const wrapped = Float32Array.from(at);
for (let i = 0; i < N; i++) { if (omega[i] < 0.001) continue; const d = rbf(at[i * 3], at[i * 3 + 1], at[i * 3 + 2]); for (let c = 0; c < 3; c++) wrapped[i * 3 + c] += d[c] * omega[i]; }
// onto the drawn surface: each round, where every point wants to go, smoothed over the mesh as one field
const inHead = i => used[i] && omega[i] > 0.02;
for (let round = 0; round < 14; round++) {
  const disp = new Float32Array(N * 3), smoothIts = Math.round(lerp(30, 4, round / 13));
  for (let i = 0; i < N; i++) { if (!inHead(i)) continue; const [x, y, z] = toL(wrapped[i * 3], wrapped[i * 3 + 1], wrapped[i * 3 + 2]); if (y < yChin - 0.6) continue; const d = hsdf(x, y, z), g = sdfGrad(x, y, z), gl = Math.hypot(...g) || 1; const k = clamp(d, -0.15, 0.15) * R / gl; for (let c = 0; c < 3; c++) disp[i * 3 + c] = -g[c] * k / gl * omega[i] ** 2; }
  const sm = diffuse(disp, smoothIts, i => !used[i]);
  for (let i = 0; i < N * 3; i++) wrapped[i] += sm[i] * 0.9;
}
// last: exactly onto the surface along the normal, then a light relaxation of the spacing
for (let i = 0; i < N; i++) { if (!inHead(i) || omega[i] < 0.9) continue; let [x, y, z] = toL(wrapped[i * 3], wrapped[i * 3 + 1], wrapped[i * 3 + 2]); if (y < yChin - 0.3) continue; for (let k = 0; k < 4; k++) { const d = hsdf(x, y, z), g = sdfGrad(x, y, z), gl = Math.hypot(...g) || 1; x -= g[0] / gl * d; y -= g[1] / gl * d; z -= g[2] / gl * d; } const w = toW(x, y, z); wrapped.set(w, i * 3); }
at.set(wrapped);
// ———— openings: the eyes and the mouth are cut where the drawing puts them, their rims laid on its curves ————
const eyeShape = (s) => { const cx = s * E.x, cyy = E.y, hw = E.w / 2, hu = E.h * 0.55, hl = E.h * 0.45, tilt = (E.tilt || 0) * s;
  return { cx, cy: cyy, hw, up: u => hu * Math.pow(Math.max(0, 1 - u * u), E.sharp ? 0.5 : 0.65) * (E.sharp ? (1 + 0.25 * u * s) : 1), lo: u => -hl * Math.pow(Math.max(0, 1 - u * u), 0.8), tilt }; };
const eyeUV = (sh, x, y) => { const u = (x - sh.cx) / sh.hw, v = y - sh.cy - sh.tilt * (x - sh.cx); return [u, v]; };
const insideEye = (sh, x, y) => { const [u, v] = eyeUV(sh, x, y); return Math.abs(u) < 1 && v < sh.up(u) && v > sh.lo(u); };
const SH = [eyeShape(1), eyeShape(-1)];
const local = i => toL(at[i * 3], at[i * 3 + 1], at[i * 3 + 2]);
const cut = new Uint8Array(bs.tris.length / 3), isRim = new Int8Array(N).fill(-1);
for (let t = 0; t < cut.length; t++) { const v = [0, 1, 2].map(k => bs.tris[t * 3 + k]); if (v.some(i => omega[i] < 0.9)) continue; const c = v.map(local).reduce((a, p) => [a[0] + p[0] / 3, a[1] + p[1] / 3, a[2] + p[2] / 3], [0, 0, 0]); if (c[2] < 0) continue;
  for (let e = 0; e < 2; e++) if (insideEye(SH[e], c[0], c[1])) cut[t] = 1 + e;
  if (expr === 'jaw' || expr === 'smile') { const j = v.map(i => jawW[i]); if (Math.max(...j) - Math.min(...j) > 0.35 && Math.abs(c[0]) < M.w * 0.6 && Math.abs(c[1] - M.y) < 0.12) cut[t] = 3; } }
for (let t = 0; t < cut.length; t++) if (cut[t] && cut[t] < 3) for (let k = 0; k < 3; k++) isRim[bs.tris[t * 3 + k]] = cut[t] - 1;
// rim points onto the eye's curve, a little in, so the lid has an edge
for (let i = 0; i < N; i++) { if (isRim[i] < 0) continue; const sh = SH[isRim[i]]; let [x, y, z] = local(i); const [u, v] = eyeUV(sh, x, y), uu = clamp(u, -0.98, 0.98), top = v > (sh.up(uu) + sh.lo(uu)) / 2, vy = top ? sh.up(uu) : sh.lo(uu); x = sh.cx + uu * sh.hw; y = sh.cy + vy + sh.tilt * (x - sh.cx); z = surfZ(x, y) - 0.035; at.set(toW(x, y, z), i * 3); }
// the eyeballs, behind the openings
const eyeBall = SH.map(sh => { const r = Math.max(sh.hw, E.h * 0.6) * 1.05; return { c: [sh.cx, sh.cy + 0.01, surfZ(sh.cx, sh.cy) - r * 0.92 - 0.02], r }; });
// blink: the upper lid comes down over the ball
if (expr === 'blink') for (let i = 0; i < N; i++) { if (omega[i] < 0.9) continue; let [x, y, z] = local(i); for (let e = 0; e < 2; e++) { const sh = SH[e], [u, v] = eyeUV(sh, x, y); if (Math.abs(u) > 1.15 || z < 0) continue; const uu = clamp(u, -1, 1), up = sh.up(uu), lo = sh.lo(uu); if (v < (up + lo) / 2 - 0.004 || v > up + E.h * 0.9) continue; const f = clamp(1 - (v - up) / (E.h * 0.9), 0, 1) * clamp(1 - (Math.abs(u) - 0.85) / 0.3, 0, 1); const ny = y + (lo + 0.01 - up) * f; const B = eyeBall[e]; const zb = B.c[2] + Math.sqrt(Math.max(0, (B.r + 0.03) ** 2 - (x - B.c[0]) ** 2 - (ny - B.c[1]) ** 2)); const nz = lerp(z, Math.max(zb, Math.min(z, surfZ(x, ny))), f); at.set(toW(x, ny, nz), i * 3); } }
// smile: the corners of the mouth up and back, the cheeks rise
if (expr === 'smile') for (let i = 0; i < N; i++) { if (omega[i] < 0.5) continue; let [x, y, z] = local(i); let dx = 0, dy = 0, dz = 0; for (const s of [-1, 1]) { const r = Math.hypot(x - s * M.w * 0.55, y - M.y) / 0.22, f = Math.exp(-r * r); dx += s * 0.03 * f; dy += 0.07 * f; dz -= 0.03 * f; const rc = Math.hypot(x - s * 0.42, y + 0.55) / 0.3, fc = Math.exp(-rc * rc); dy += 0.035 * fc; dz += 0.02 * fc; } at.set(toW(x + dx * omega[i], y + dy * omega[i], z + dz * omega[i]), i * 3); }
