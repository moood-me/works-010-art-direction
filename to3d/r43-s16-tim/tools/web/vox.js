// С16 in 3D: a figure of small typed volumes, drawn straight onto the sprite's own pixel grid.
//
// A part (head, trunk, thigh…) is typed as the style types a sprite — an ASCII map, one character a pixel — twice:
// seen from the front and from the side (and from the back where it differs). The two maps make a volume one voxel
// a pixel (in every row: the front's pixels × the side's pixels, the corners rounded off, both silhouettes kept
// exactly). Each part hangs on a SOMA joint. A picture is made by looking through every pixel's centre: the first
// volume met gives the pixel, its colour is read from the map drawn for the nearest view (front, back, a side), so
// from the front the standing figure is the drawing pixel for pixel. The light is the drawing's (above, left, fixed
// on the picture): where a form has turned against the view its map was drawn for, the colour goes one step up or
// down its ramp. Then the face is stamped (a dozen typed pixels, by the head's turn), and the style's coloured
// selective outline is put round the figure by the style's own rule (px.py: outline).
import { qmat, qsnap, qrot, sub, clamp } from './rig.js';

export function Palette(ramps) {
  const letters = Object.keys(ramps), idx = {}, hex = [null], rgb = [[0, 0, 0]];
  letters.forEach((r, ri) => ramps[r].forEach((h, s) => { idx[r + s] = ri * 5 + s + 1; hex.push(h); rgb.push([1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16))); }));
  const ramp = k => letters[((k - 1) / 5) | 0], step = k => (k - 1) % 5;
  const FIXED = new Set(['x', 'z'].map(r => letters.indexOf(r)));
  return { idx, hex, rgb, ramp, step, letters,
    key: k => k ? ramp(k) + step(k) : '..',
    shift: (k, d) => { const ri = ((k - 1) / 5) | 0; if (!d || FIXED.has(ri)) return k; return ri * 5 + clamp(step(k) + d, 1, 4) + 1; },
    grid: rows => rows.map(r => { const a = new Uint8Array(r.length / 2); for (let i = 0; i < a.length; i++) { const k = r.slice(i * 2, i * 2 + 2); a[i] = k === '..' ? 0 : idx[k]; } return a; }),
  };
}

const PAD = 2;
function blur(src, nx, ny, nz) {
  const out = new Float32Array(src.length), at = (i, j, k) => (i < 0 || j < 0 || k < 0 || i >= nx || j >= ny || k >= nz) ? 0 : src[i + nx * (j + ny * k)];
  for (let k = 0; k < nz; k++) for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
    let s = 0;
    for (let c = -1; c <= 1; c++) for (let b = -1; b <= 1; b++) for (let a = -1; a <= 1; a++) s += at(i + a, j + b, k + c);
    out[i + nx * (j + ny * k)] = s / 27;
  }
  return out;
}

// def: {name, bone, at: [column of the front map's first character, its top row, column of the side map's first
// character], front, side, back (as seen from behind; without it the front's rows serve), round (the exponent of the
// rounding, 2.5), steady (the part moves by whole pixels and turns by whole steps: its pixels don't crawl)}
export function buildPart(def, leg, pal) {
  const map = rows => { const w = Math.max(...rows.map(r => r.length)); return rows.map(r => { const a = new Uint8Array(w); for (let i = 0; i < r.length; i++) if (r[i] !== '.' && r[i] !== ' ') { const k = pal.idx[leg[r[i]]]; if (!k) throw new Error(`${def.name}: no colour for '${r[i]}'`); a[i] = k; } return a; }); };
  const F = map(def.front), S = map(def.side), B = def.back ? map(def.back) : F, h = F.length, w = F[0].length, d = S[0].length;
  if (S.length !== h || B.length !== h || B[0].length !== w) throw new Error(`${def.name}: the maps differ in size`);
  const nx = w + 2 * PAD, ny = h + 2 * PAD, nz = d + 2 * PAD, occ = new Float32Array(nx * ny * nz), p = def.round ?? 2.5;
  const I = (i, j, k) => i + PAD + nx * (j + PAD + ny * (k + PAD));
  for (let j = 0; j < h; j++) {
    const xs = [], zs = [];
    for (let i = 0; i < w; i++) if (F[j][i]) xs.push(i);
    for (let k = 0; k < d; k++) if (S[j][k]) zs.push(k);
    if (!xs.length || !zs.length) { if (xs.length || zs.length) throw new Error(`${def.name}: row ${j} is drawn in one map only`); continue; }
    const cx = (xs[0] + xs[xs.length - 1] + 1) / 2, hw = (xs[xs.length - 1] - xs[0] + 1) / 2, cz = (zs[0] + zs[zs.length - 1] + 1) / 2, hd = (zs[zs.length - 1] - zs[0] + 1) / 2;
    const near = (a, c) => a.slice().sort((u, v) => Math.abs(u + 0.5 - c) - Math.abs(v + 0.5 - c));
    for (const i of xs) for (const k of zs) if (Math.abs((i + 0.5 - cx) / hw) ** p + Math.abs((k + 0.5 - cz) / hd) ** p <= 1) occ[I(i, j, k)] = 1;
    for (const i of xs) if (!zs.some(k => occ[I(i, j, k)])) occ[I(i, j, near(zs, cz)[0])] = 1;     // both silhouettes are kept whole
    for (const k of zs) if (!xs.some(i => occ[I(i, j, k)])) occ[I(near(xs, cx)[0], j, k)] = 1;
  }
  const soft = blur(blur(occ, nx, ny, nz), nx, ny, nz);
  let n = 0; for (const v of occ) n += v;
  const top = {};      // the lightest step each ramp is drawn with in this part: the light doesn't go above it
  for (const G of [F, S, B]) for (const r of G) for (const k of r) if (k) { const ri = ((k - 1) / 5) | 0; top[ri] = Math.max(top[ri] || 0, (k - 1) % 5); }
  return { def, top, name: def.name, bone: def.bone, at: def.at, F, S, B, w, h, d, nx, ny, nz, occ, soft, steady: !!def.steady, voxels: n };
}

// trilinear reading of a field; a voxel's centre is at whole + 0.5
function tri(f, P, x, y, z) {
  x += PAD - 0.5; y += PAD - 0.5; z += PAD - 0.5;
  const i = Math.floor(x), j = Math.floor(y), k = Math.floor(z);
  if (i < 0 || j < 0 || k < 0 || i >= P.nx - 1 || j >= P.ny - 1 || k >= P.nz - 1) return 0;
  const a = x - i, b = y - j, c = z - k, o = i + P.nx * (j + P.ny * k), sx = 1, sy = P.nx, sz = P.nx * P.ny;
  const l = (u, v, t) => u + (v - u) * t;
  return l(l(l(f[o], f[o + sx], a), l(f[o + sy], f[o + sy + sx], a), b), l(l(f[o + sz], f[o + sz + sx], a), l(f[o + sz + sy], f[o + sz + sy + sx], a), b), c);
}
function texel(G, i, j) { // the drawn pixel, or the nearest drawn one of the row (a point on a rounded-off corner)
  j = clamp(j, 0, G.length - 1); const r = G[j], w = r.length; i = clamp(i, 0, w - 1);
  if (r[i]) return r[i];
  for (let e = 1; e < w; e++) { if (i - e >= 0 && r[i - e]) return r[i - e]; if (i + e < w && r[i + e]) return r[i + e]; }
  for (let e = 1; e < G.length; e++) for (const jj of [j - e, j + e]) if (jj >= 0 && jj < G.length) { const k = texel0(G[jj], i); if (k) return k; }
  return 0;
}
function texel0(r, i) { if (r[i]) return r[i]; for (let e = 1; e < r.length; e++) { if (i - e >= 0 && r[i - e]) return r[i - e]; if (i + e < r.length && r[i + e]) return r[i + e]; } return 0; }

const LIGHT = (() => { const v = [-0.55, 0.62, 0.56], l = Math.hypot(...v); return v.map(x => x / l); })();
const level = (x, y, z) => { const d = x * LIGHT[0] + y * LIGHT[1] + z * LIGHT[2]; return d > 0.74 ? 2 : d > -0.08 ? 1 : 0; };
const levelM = (x, y, z) => { const d = -x * LIGHT[0] + y * LIGHT[1] + z * LIGHT[2]; return d > 0.74 ? 2 : d > -0.08 ? 1 : 0; };

// ch: the character (see tim.js): CX, CZ, FLOOR, J, PARTS, LEG, face()
export function Figure(ch, pal) {
  const leg = ch.LEG, parts = ch.PARTS.map(d => buildPart(d, leg, pal));
  const headI = parts.findIndex(p => p.name === ch.FACE_ON);
  const toW = ([X, Y, Z]) => [X - ch.CX, ch.FLOOR - Y, Z - ch.CZ];
  const J = Object.fromEntries(Object.entries(ch.J).map(([b, p]) => [b, toW(p)]));
  const STEP = (ch.STEP ?? 20) * Math.PI / 180;

  // o: pose {W, P}, yaw (degrees: the figure turned to the picture's right), w, h (the picture, pixels), ox, oy (where
  // the figure's own column 0 and row 0 fall), cam: [x, y] whole pixels the view is moved by, steady (true),
  // relight (true), face: {expr, blink, mouth}
  function render(o) {
    const { W, P } = o.pose, w = o.w, h = o.h, ox = o.ox ?? 0, oy = o.oy ?? 0, cam = o.cam || [0, 0], steady = o.steady !== false, relight = o.relight !== false, res = o.res || 1;
    const ya = (o.yaw || 0) * Math.PI / 180, cy = Math.cos(ya), sy = Math.sin(ya);
    const Rv = [cy, 0, sy, 0, 1, 0, -sy, 0, cy];
    const mul = (A, B) => { const C = new Array(9); for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) C[r * 3 + c] = A[r * 3] * B[c] + A[r * 3 + 1] * B[3 + c] + A[r * 3 + 2] * B[6 + c]; return C; };
    const mv = (A, v) => [A[0] * v[0] + A[1] * v[1] + A[2] * v[2], A[3] * v[0] + A[4] * v[1] + A[5] * v[2], A[6] * v[0] + A[7] * v[1] + A[8] * v[2]];
    const key = new Uint8Array(w * h), base = new Uint8Array(w * h), part = new Int8Array(w * h).fill(-1), zb = new Float32Array(w * h).fill(-1e9), lum = o.lum ? new Float32Array(w * h) : null;
    parts.forEach((p, pi) => {
      let q = W[p.bone];
      if (steady && p.steady) q = qsnap(q, STEP);
      const M = mul(Rv, qmat(q)), Jb = J[p.bone];
      let cb = mv(Rv, P[p.bone]);
      if (steady && p.steady) { const cr = mv(Rv, Jb); cb = [cr[0] + Math.round(cb[0] - cr[0]), cr[1] + Math.round(cb[1] - cr[1]), cb[2]]; }
      const mj = mv(M, Jb), t = [cb[0] - mj[0], cb[1] - mj[1], cb[2] - mj[2]];
      // the part's box on the picture
      let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
      for (let c = 0; c < 8; c++) {
        const g = [c & 1 ? p.w + 0.5 : -0.5, c & 2 ? p.h + 0.5 : -0.5, c & 4 ? p.d + 0.5 : -0.5];
        const r = [g[0] + p.at[0] - ch.CX, ch.FLOOR - g[1] - p.at[1], g[2] + p.at[2] - ch.CZ], v = mv(M, r);
        const X = v[0] + t[0], Y = v[1] + t[1];
        x0 = Math.min(x0, X); x1 = Math.max(x1, X); y0 = Math.min(y0, Y); y1 = Math.max(y1, Y);
      }
      const c0 = Math.max(0, Math.floor((x0 + ch.CX + ox - cam[0]) * res)), c1 = Math.min(w - 1, Math.ceil((x1 + ch.CX + ox - cam[0]) * res));
      const r0 = Math.max(0, Math.floor((ch.FLOOR - y1 + oy + cam[1]) * res)), r1 = Math.min(h - 1, Math.ceil((ch.FLOOR - y0 + oy + cam[1]) * res));
      // a point of the view → the part's grid: g = A·(view − t) + off, A = Mᵀ with the row of y turned over
      const A = [M[0], M[3], M[6], -M[1], -M[4], -M[7], M[2], M[5], M[8]];
      const off = [ch.CX - p.at[0], ch.FLOOR - p.at[1], ch.CZ - p.at[2]], dg = [A[2], A[5], A[8]];
      const lim = [p.w, p.h, p.d], vz = [M[6], M[7], M[8]];     // the eye's direction in the part's own frame
      // the part's colours are read from one map — the one drawn for the view nearest to the eye's (front, back,
      // right side, left side): no two drawings are mixed on one form
      const view = Math.abs(vz[2]) >= Math.abs(vz[0]) - 1e-6 ? (vz[2] >= 0 ? 0 : 1) : (vz[0] < 0 ? 2 : 3);
      for (let r = r0; r <= r1; r++) for (let c = c0; c <= c1; c++) {
        const vx = (c + 0.5) / res - ch.CX - ox + cam[0] - t[0], vy = ch.FLOOR - ((r + 0.5) / res - oy) + cam[1] - t[1];
        const g0 = [A[0] * vx + A[1] * vy - A[2] * t[2] + off[0], A[3] * vx + A[4] * vy - A[5] * t[2] + off[1], A[6] * vx + A[7] * vy - A[8] * t[2] + off[2]];
        // the stretch of the ray inside the part's box
        let sa = -1e9, sb = 1e9, miss = false;
        for (let a = 0; a < 3; a++) {
          if (Math.abs(dg[a]) < 1e-9) { if (g0[a] < -0.5 || g0[a] > lim[a] + 0.5) { miss = true; break; } continue; }
          let u = (-0.5 - g0[a]) / dg[a], v = (lim[a] + 0.5 - g0[a]) / dg[a]; if (u > v) [u, v] = [v, u];
          sa = Math.max(sa, u); sb = Math.min(sb, v);
        }
        if (miss || sa > sb) continue;
        const o2 = r * w + c;
        if (sb <= zb[o2]) continue;
        let s = sb, hit = false, prev = sb;
        for (; s >= sa; s -= 0.2) { if (tri(p.occ, p, g0[0] + s * dg[0], g0[1] + s * dg[1], g0[2] + s * dg[2]) >= 0.5) { hit = true; break; } prev = s; }
        if (!hit) continue;
        let lo = s, hi = prev;
        for (let it = 0; it < 5; it++) { const m = (lo + hi) / 2; if (tri(p.occ, p, g0[0] + m * dg[0], g0[1] + m * dg[1], g0[2] + m * dg[2]) >= 0.5) lo = m; else hi = m; }
        s = lo;
        if (s <= zb[o2]) continue;
        zb[o2] = s; part[o2] = pi;
        const gx = g0[0] + s * dg[0], gy = g0[1] + s * dg[1], gz = g0[2] + s * dg[2];
        // the form's normal, in the part's own frame (x to the figure's left, y up, z forward)
        let nx = -(tri(p.soft, p, gx + 1, gy, gz) - tri(p.soft, p, gx - 1, gy, gz)), ny = tri(p.soft, p, gx, gy + 1, gz) - tri(p.soft, p, gx, gy - 1, gz), nz = -(tri(p.soft, p, gx, gy, gz + 1) - tri(p.soft, p, gx, gy, gz - 1));
        const nl = Math.hypot(nx, ny, nz) || 1; nx /= nl; ny /= nl; nz /= nl;
        const i = Math.floor(gx), j = Math.floor(gy), k = Math.floor(gz);
        let kk, baked;
        if (view === 0) { kk = texel(p.F, i, j); baked = level(nx, ny, nz); }
        else if (view === 1) { kk = texel(p.B, p.w - 1 - i, j); baked = level(-nx, ny, -nz); }
        else if (view === 2) { kk = texel(p.S, k, j); baked = level(nz, ny, -nx); }
        else { kk = texel(p.S, k, j); baked = levelM(-nz, ny, nx); }
        base[o2] = kk;
        const nc = mv(M, [nx, ny, nz]);
        if (lum) lum[o2] = nc[0] * LIGHT[0] + nc[1] * LIGHT[1] + nc[2] * LIGHT[2];
        if (relight && !p.def.flat) { const k2 = pal.shift(kk, clamp(level(nc[0], nc[1], nc[2]) - baked, -1, 1)); if ((k2 - 1) % 5 <= p.top[((kk - 1) / 5) | 0]) kk = k2; }
        key[o2] = kk;
      }
    });
    // a pixel that the light alone has made single goes back to its drawn colour: no noise of lone pixels
    for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) {
      const o2 = r * w + c, k = key[o2];
      if (!k || k === base[o2]) continue;
      if (!((c > 0 && key[o2 - 1] === k) || (c < w - 1 && key[o2 + 1] === k) || (r > 0 && key[o2 - w] === k) || (r < h - 1 && key[o2 + w] === k))) key[o2] = base[o2];
    }
    // the face: typed pixels, chosen by where the head looks
    let look = null;
    if (ch.face && headI >= 0 && o.face !== false && res === 1) {
      const hp = parts[headI];
      let q = W[hp.bone]; if (steady && hp.steady) q = qsnap(q, STEP);
      const f = mv(Rv, qrot(q, [0, 0, 1]));
      const psi = Math.atan2(f[0], f[2]) * 180 / Math.PI, pitch = Math.asin(clamp(f[1], -1, 1)) * 180 / Math.PI;
      const cb = mv(Rv, P[hp.bone]), cr = mv(Rv, J[hp.bone]);
      const dx = Math.round(cb[0] - cr[0]), dy = Math.round(cb[1] - cr[1]);
      look = { psi, pitch, dx, dy };
      for (const st of ch.face({ psi, pitch, ...(o.face || {}) })) st.rows.forEach((row, jj) => { for (let ii = 0; ii < row.length; ii++) {
        if (row[ii] === '.' || row[ii] === ' ') continue;
        const c = st.x + ii + dx + ox - cam[0], r = st.y + jj - dy + oy + cam[1];
        if (c < 0 || r < 0 || c >= w || r >= h || part[r * w + c] !== headI) continue;
        key[r * w + c] = pal.idx[leg[row[ii]]];
      } });
    }
    return { key, part, w, h, look, lum };
  }

  // the style's outline (px.py: outline): one pixel round the drawing, step 0 of the ramp it hugs, a step lighter
  // above and to the left of light forms
  function outline(fig) {
    const { key, w, h } = fig, out = key.slice(), LITE = new Set([...'satwco']);
    for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) {
      if (key[r * w + c]) continue;
      for (const [dx, dy] of [[0, 1], [1, 0], [0, -1], [-1, 0]]) {
        const x = c + dx, y = r + dy; if (x < 0 || y < 0 || x >= w || y >= h) continue;
        const n = key[y * w + x]; if (!n) continue;
        const ra = pal.ramp(n), lit = (dy === 1 || dx === 1) && pal.step(n) >= 3 && LITE.has(ra);
        out[r * w + c] = pal.idx[ra + (lit ? '1' : '0')]; break;
      }
    }
    return { ...fig, key: out };
  }
  return { parts, J, render, outline, toW };
}

// pictures: a grid of colour numbers → RGBA, enlarged a whole number of times
export function paint(pal, key, w, h, scale = 1, bg = null) {
  const out = new Uint8ClampedArray(w * scale * h * scale * 4);
  for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) {
    const k = key[r * w + c], col = k ? pal.rgb[k] : bg, a = k || bg ? 255 : 0;
    for (let y = 0; y < scale; y++) for (let x = 0; x < scale; x++) { const o = ((r * scale + y) * w * scale + c * scale + x) * 4; if (col) { out[o] = col[0]; out[o + 1] = col[1]; out[o + 2] = col[2]; } out[o + 3] = a; }
  }
  return out;
}
export function put(dst, dw, dh, src, sw, sh, x, y) { // lay one grid of colour numbers on another (0 is empty)
  for (let r = 0; r < sh; r++) for (let c = 0; c < sw; c++) { const k = src[r * sw + c], X = x + c, Y = y + r; if (k && X >= 0 && Y >= 0 && X < dw && Y < dh) dst[Y * dw + X] = k; }
}
