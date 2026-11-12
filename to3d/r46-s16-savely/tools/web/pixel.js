// From the 3D to a sprite: the rules of С16 (styles/s16-pixel) applied to what the 3D gives.
// The 3D is rendered small and unseen, a few samples to a pixel: for each sample which material it is, how it is
// turned to the light, how far it is. Here every pixel is then decided, as the style demands: one material, one step
// of that material's ramp, no stray pixels, the face's signs put by hand-made rule, the coloured selective outline
// (px.py's `outline`, line for line). The result is a grid of colour keys of the style's palette (pal.py) — the
// same thing the style's own drawings are.
import { RAMPS } from './data.js';

export const hexOf = k => RAMPS[k[0]][+k[1]];

// materials: id (as rendered), keys [shade, base, light], thr [below → shade, above → light] of the light term
// (-1…1), pri — weight when several materials share a pixel (small things must not be lost), small — may stay a
// lone pixel
export const MATS = [
  null,
  { name: 'skin', keys: ['s2', 's3', 's4'], thr: [-0.1, 0.93], pri: 1 },
  { name: 'hand', keys: ['s2', 's3', 's3'], thr: [-0.1, 2], pri: 1.3 },
  { name: 'hair', keys: ['w2', 'w3', 'w3'], thr: [-0.1, 2], pri: 1.2 },
  { name: 'shirt', keys: ['w2', 'w3', 'w3'], thr: [-0.1, 2], pri: 1 },
  { name: 'vest', keys: ['g1', 'g2', 'g2'], thr: [-0.1, 2], pri: 1 },
  { name: 'trousers', keys: ['b1', 'b2', 'b2'], thr: [-0.1, 2], pri: 1 },
  { name: 'shoes', keys: ['b1', 'b1', 'b1'], thr: [0, 2], pri: 1 },
  { name: 'strap', keys: ['n2', 'n2', 'n2'], thr: [0, 2], pri: 2.5, small: true },
  { name: 'loupe', keys: ['n1', 'n1', 'n1'], thr: [0, 2], pri: 2, small: true },
  { name: 'bow', keys: ['r2', 'r2', 'r2'], thr: [0, 2], pri: 3, small: true },
  { name: 'watch', keys: ['t2', 't3', 't3'], thr: [-0.1, 2], pri: 2.5, small: true },
  { name: 'moustache', keys: ['w2', 'w3', 'w3'], thr: [-0.3, 2], pri: 2.2, small: true },
  { name: 'lens', keys: ['u2', 'u3', 'u4'], thr: [-2, 0.97], pri: 4, small: true },
];
export const MID = Object.fromEntries(MATS.map((m, i) => [m ? m.name : '', i]));

// buf: RGBA bytes of the unseen render, (W·ss)×(H·ss), rows bottom-up as WebGL gives them: R material, G light
// (0…255 for -1…1), B depth (0 near … 255 far), A the light for the shine. Decides each pixel's material: a pixel is filled when at least
// `cover` of its samples hit the figure; its material is the one with most samples, weighted.
export function resolve(buf, W, H, ss, cover = 0.5) {
  const id = new Uint8Array(W * H), li = new Float32Array(W * H), lh = new Float32Array(W * H), z = new Float32Array(W * H).fill(1e9);
  const cnt = new Float32Array(MATS.length), ls = new Float32Array(MATS.length), hs = new Float32Array(MATS.length), zs = new Float32Array(MATS.length), n = new Uint16Array(MATS.length);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    cnt.fill(0); ls.fill(0); hs.fill(0); zs.fill(0); n.fill(0);
    let hit = 0;
    for (let j = 0; j < ss; j++) for (let i = 0; i < ss; i++) {
      const o = (((H - 1 - y) * ss + (ss - 1 - j)) * W * ss + x * ss + i) * 4, m = buf[o];
      if (!m || m >= MATS.length) continue;
      hit++; cnt[m] += MATS[m].pri; n[m]++; ls[m] += buf[o + 1]; zs[m] += buf[o + 2]; hs[m] += buf[o + 3];
    }
    if (hit < cover * ss * ss) continue;
    let best = 0; for (let m = 1; m < MATS.length; m++) if (cnt[m] > cnt[best]) best = m;
    const q = y * W + x; id[q] = best; li[q] = ls[best] / n[best] / 127.5 - 1; lh[q] = hs[best] / n[best] / 127.5 - 1; z[q] = zs[best] / n[best];
  }
  return { W, H, id, li, lh, z };
}

const N4 = [[0, 1], [1, 0], [0, -1], [-1, 0]];
// the grid of colour keys from the decided pixels. opts: { rules: false → the bare sampling, for the page's steps }
export function keysOf(R, opts = {}) {
  const { W, H, id, li, lh, z } = R, rules = opts.rules !== false;
  const at = (x, y) => (x >= 0 && y >= 0 && x < W && y < H ? id[y * W + x] : 0);
  if (rules) {
    // a lone pixel of a material among others (not a thing that is small by itself) takes its neighbours' material
    for (let pass = 0; pass < 2; pass++) for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const m = at(x, y); if (!m || MATS[m].small) continue;
      const c = {}; let same = 0, filled = 0;
      for (const [dx, dy] of N4) { const k = at(x + dx, y + dy); if (k) { filled++; c[k] = (c[k] || 0) + 1; if (MATS[k].keys[1][0] === MATS[m].keys[1][0]) same++; } }
      if (same || !filled) continue;
      const k = +Object.keys(c).sort((a, b) => c[b] - c[a])[0];
      if (MATS[k].small) continue;
      id[y * W + x] = k;
    }
    // a pixel that sticks out of the silhouette alone (one neighbour or none) is dropped
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const m = at(x, y); if (!m || MATS[m].small) continue;
      let filled = 0; for (const [dx, dy] of N4) if (at(x + dx, y + dy)) filled++;
      if (filled <= 1 && !(opts.keepSpurs)) id[y * W + x] = 0;
    }
  }
  const step = new Int8Array(W * H);
  for (let q = 0; q < W * H; q++) { const m = id[q]; if (m) step[q] = li[q] < MATS[m].thr[0] ? 0 : lh[q] > MATS[m].thr[1] ? 2 : 1; }
  if (rules) {
    // shade and light come as clusters: a pixel whose step differs from every neighbour of its own material takes theirs
    for (let pass = 0; pass < 2; pass++) for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const q = y * W + x, m = id[q]; if (!m) continue;
      const c = [0, 0, 0]; let n = 0, same = 0;
      for (const [dx, dy] of N4) if (at(x + dx, y + dy) === m) { const s = step[q + dx + dy * W]; c[s]++; n++; if (s === step[q]) same++; }
      if (n >= 2 && !same) step[q] = c.indexOf(Math.max(...c));
    }
  }
  if (rules) {
    // the white tufts are shaded as the style shades them (portrait.py's rim, the sprite's `w`): a band of shade
    // along the lower edge and where the hair meets the face
    const band = opts.hairBand ?? 1;
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      if (at(x, y) !== MID.hair) continue;
      let sh = at(x - 1, y) === MID.skin || at(x + 1, y) === MID.skin;
      for (let k = 1; k <= band; k++) if (at(x, y + k) !== MID.hair) sh = true;
      if (sh) step[y * W + x] = 0;
    }
  }
  const g = Array.from({ length: H }, () => new Array(W).fill(''));
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const q = y * W + x, m = id[q]; if (m) g[y][x] = MATS[m].keys[step[q]]; }
  if (rules) {
    // one form before another of the same ramp (an arm on the shirt, a leg passing a leg): the farther one gets a
    // line of its shade along the edge, so the nearer reads — the style's "forms are parted by colour"
    const dz = opts.dz ?? 12, sameKey = (m, k) => MATS[k].keys[1] === MATS[m].keys[1];
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const q = y * W + x, m = id[q]; if (!m || m === MID.hair) continue;      // (the tufts have their own shade)
      for (const [dx, dy] of N4) { const k = at(x + dx, y + dy); if (k && sameKey(m, k) && z[q] - z[q + dx + dy * W] >= dz) { g[y][x] = MATS[m].keys[0]; break; } }
    }
  }
  return g;
}

// px.py's outline: one pixel round the drawing, step 0 of the ramp of the pixel it hugs; where the light falls
// (above and to the left of the form) one step lighter for the ramps that have room
export function outline(g, skip = '') {
  const H = g.length, W = g[0].length, add = [];
  const get = (x, y) => (x >= 0 && y >= 0 && x < W && y < H ? g[y][x] : '');
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    if (g[y][x]) continue;
    for (const [dx, dy] of N4) {
      const n = get(x + dx, y + dy);
      if (n && !skip.includes(n[0])) {
        const lit = (dx === 0 && dy === 1 || dx === 1 && dy === 0) && +n[1] >= 3;
        add.push([x, y, n[0] + (lit && 'satwco'.includes(n[0]) ? '1' : '0')]); break;
      }
    }
  }
  for (const [x, y, k] of add) g[y][x] = k;
  return g;
}

// sheets.py's backdrop and stand: the dusk wall, the floor with its dithered edge; the shadow under the feet
export function backdrop(W, H, floor) {
  const g = Array.from({ length: H }, (_, y) => new Array(W).fill(y >= floor ? 'd2' : 'd1'));
  for (let j = 0; j < 3; j++) for (let x = 0; x < W; x++) if ((x + j) % 2 === 0) g[floor - 3 + j][x] = 'd2';
  for (let x = 0; x < W; x++) g[floor][x] = 'd3';
  return g;
}
// portrait.py's framed: the dialogue box
export function box(W, H) {
  const g = Array.from({ length: H + 6 }, () => new Array(W + 6).fill('x0'));
  const rect = (x, y, w, h, k) => { for (let j = y; j < y + h; j++) for (let i = x; i < x + w; i++) g[j][i] = k; };
  rect(1, 1, W + 4, H + 4, 'd3'); rect(2, 2, W + 2, H + 2, 'x0'); rect(3, 3, W, H, 'd1'); rect(3, 3 + 34, W, H - 34, 'd2');
  for (let j = 0; j < 4; j++) for (let i = 0; i < W; i++) if ((i + j) % 2 === 0) g[3 + 30 + j][3 + i] = 'd2';
  return g;
}
export function paste(dst, src, ox = 0, oy = 0, x0 = 0, y0 = 0, x1 = 1e9, y1 = 1e9) {
  for (let y = 0; y < src.length; y++) for (let x = 0; x < src[0].length; x++) {
    const X = x + ox, Y = y + oy;
    if (src[y][x] && X >= Math.max(0, x0) && Y >= Math.max(0, y0) && X < Math.min(dst[0].length, x1) && Y < Math.min(dst.length, y1)) dst[Y][X] = src[y][x];
  }
  return dst;
}
export function draw(ctx, g, scale, ox = 0, oy = 0) {
  for (let y = 0; y < g.length; y++) for (let x = 0; x < g[0].length; x++) if (g[y][x]) { ctx.fillStyle = hexOf(g[y][x]); ctx.fillRect(ox + x * scale, oy + y * scale, scale, scale); }
}
