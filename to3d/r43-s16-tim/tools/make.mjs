// The pictures and films of the page → ../pics.  node make.mjs stills | films | <name> …
import path from 'node:path';
import { ch, pal, fig, stage, player, life, D, img, sheet, blank, blit, write, film, FPS, CACHE, WHO } from './lib.mjs';
import { paint } from './web/vox.js';
import { rest } from './web/rig.js';

const clip = id => ch.CLIPS.find(c => c.id === id), STAND = clip('stand'), DOWN = {};
const poseOf = (c, t = 0) => player.at(c, t).pose;
const BGC = pal.rgb[pal.idx.d1];
const views = Object.keys(stage.sprites);                      // the drawing's views: front, and q, side where drawn
const rgbOf = (key, w, h) => paint(pal, key, w, h, 1, BGC);
const up = (im, k) => { const out = blank(im.w * k, im.h * k); for (let r = 0; r < out.h; r++) for (let c = 0; c < out.w; c++) out.rgba.set(im.rgba.subarray((((r / k) | 0) * im.w + ((c / k) | 0)) * 4, (((r / k) | 0) * im.w + ((c / k) | 0)) * 4 + 4), (r * out.w + c) * 4); return out; };
const figW = WHO.frame?.w || 34, figH = WHO.frame?.h || 46, figBy = 70 - 4 - figH;   // a window of the plain backdrop that holds the figure

const P = {
  // the drawing above, the 3D below: the same views, the same grid, the same backdrop
  compare() {
    const n = Math.max(views.length, 3), w = 32 * n, h = figH, by = figBy;
    const top = stage.ground('backdrop', w, h, 0, by);
    views.forEach((v, i) => stage.drawn(top, w, h, v, 16 + i * 32, by));
    const low = stage.ground('backdrop', w, h, 0, by), yaws = WHO.compareYaws || [0, 22.5, 90];
    yaws.forEach((yaw, i) => { const f = stage.frame({ clear: true, w, h, by, x: 16 + i * 32, pose: poseOf(STAND), yaw, shadow: false }); stage.shadow(low, w, h, 16 + i * 32, 62 - by); for (let j = 0; j < w * h; j++) if (f.fig.key[j]) low[j] = f.fig.key[j]; });
    write('compare.png', sheet([img(top, w, h), img(low, w, h)], 1));
  },
  // pixel against pixel, from the front: the drawing, the 3D in the drawing's pose, the 3D standing, and where they differ
  exact() {
    const w = figW, h = figH, by = figBy, x = w >> 1;
    const a = stage.ground('backdrop', w, h, 0, by); const left = stage.drawn(a, w, h, 'front', x, by);
    const cells = [img(a, w, h)], lines = [];
    const s = stage.sprites.front, dr = new Uint8Array(w * h); for (let r = 0; r < s.h; r++) for (let c = 0; c < s.w; c++) { const X = left + c, Y = 62 - by - s.h + 2 + r; if (X >= 0 && X < w && Y >= 0 && Y < h) dr[Y * w + X] = s.key[r * s.w + c]; }
    for (const [nm, c] of [['в позе рисунка', STAND], ['руки опущены', DOWN]]) {
      // the drawing's sprite is cropped to its own box: find the shift that fits best (whole pixels)
      let best = null;
      for (let dx = -8; dx <= 8; dx++) {
        const f = stage.frame({ w, h, by, x: x + dx, pose: poseOf(c), yaw: 0 }), fk = f.fig.key;
        let same = 0, all = 0; for (let j = 0; j < w * h; j++) if (fk[j] || dr[j]) { all++; if (fk[j] === dr[j]) same++; }
        if (!best || same > best.same) best = { same, all, f, fk };
      }
      cells.push(img(best.f.key, w, h));
      const m = blank(w, h, BGC); for (let j = 0; j < w * h; j++) { const k = best.fk[j], d = dr[j]; if (!k && !d) continue; const col = k === d ? pal.rgb[k].map(v => v * 0.35 + 30) : [255, 60, 200]; m.rgba.set([...col, 255], j * 4); }
      cells.push(up(m, 8));
      lines.push(`${nm}: совпало ${best.same} из ${best.all} пикселей (${(100 * best.same / best.all).toFixed(1)} %)`);
    }
    write('exact.png', sheet(cells, 5));
    console.log(lines.join('\n'));
  },
  around() {
    const cells = [];
    for (let i = 0; i < 16; i++) { const f = stage.frame({ w: figW, h: figH, by: figBy, x: figW >> 1, pose: poseOf(STAND), yaw: i * 22.5 }); cells.push(img(f.key, figW, figH, 6)); }
    write('around.png', sheet(cells, 8, 4));
  },
  // how it is built
  steps() {
    const w = figW, h = figH, by = figBy, x = w >> 1, ox = x - Math.floor(ch.CX), oy = 63 - by - ch.FLOOR, cells = [];
    // 1. the typed maps of every part: front and side
    { const parts = fig.parts, cols = 4, cw = 40, chh = Math.max(...parts.map(p => p.h)) + 3, rows = Math.ceil(parts.length / cols), key = new Uint8Array(cols * cw * rows * chh);
      parts.forEach((p, i) => { const X = (i % cols) * cw + 2, Y = Math.floor(i / cols) * chh + 2; for (const [G, dx] of [[p.F, 0], [p.S, p.w + 2]]) G.forEach((r, j) => r.forEach((k, c) => { if (k) key[(Y + j) * cols * cw + X + dx + c] = k; })); });
      write('step1-maps.png', img(key, cols * cw, rows * chh, 6)); }
    // 2. the volumes, seen close and plainly lit, with SOMA's joints
    for (const yaw of [0, 45, 90]) {
      const res = 8, f = fig.render({ pose: rest(fig.J), yaw, w: w * res, h: h * res, ox, oy, res, lum: true, relight: false });
      const im = blank(w * res, h * res, [40, 34, 52]);
      for (let j = 0; j < w * res * h * res; j++) if (f.key[j]) { const l = Math.max(0, f.lum[j]), c = pal.rgb[f.key[j]], g = 0.45 + 0.6 * l; im.rgba.set([c[0] * g * 0.5 + 110 * g, c[1] * g * 0.5 + 106 * g, c[2] * g * 0.5 + 104 * g, 255], j * 4); }
      const ya = yaw * Math.PI / 180;
      for (const p of Object.values(fig.J)) { const X = Math.round((Math.cos(ya) * p[0] + Math.sin(ya) * p[2] + ch.CX + ox) * res), Y = Math.round((ch.FLOOR - p[1] + oy) * res); for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) if (dx * dx + dy * dy <= 10) im.rgba.set(dx * dx + dy * dy <= 3 ? [255, 240, 120, 255] : [40, 20, 50, 255], ((Y + dy) * im.w + X + dx) * 4); }
      cells.push(im);
    }
    write('step2-volume.png', sheet(cells, 3));
    // 3–6. onto the grid: the maps' colours; the light; the face; the outline and the shadow
    const o = { w, h, by, x, pose: poseOf(DOWN), yaw: 22.5 }, cs = [];
    for (const yaw of [0, 22.5, 90]) {
      cs.push(img(stage.frame({ ...o, yaw, relight: false, face: false, outline: false, shadow: false }).key, w, h));
      cs.push(img(stage.frame({ ...o, yaw, face: false, outline: false, shadow: false }).key, w, h));
      cs.push(img(stage.frame({ ...o, yaw, outline: false, shadow: false }).key, w, h));
      cs.push(img(stage.frame({ ...o, yaw }).key, w, h));
    }
    write('step3-grid.png', sheet(cs, 4));
  },
  // what the rule forbids: a smooth picture shrunk by a machine — beside the same pose looked at pixel by pixel
  mush() {
    const w = 26, h = 22, by = figBy, x = 13, res = 8, cells = [];
    for (const yaw of [22.5]) {
      const a = player.at(clip('walk'), 0.5), ox = x - Math.floor(ch.CX), oy = 63 - by - ch.FLOOR;
      const f = fig.render({ pose: a.pose, yaw, w: w * res, h: h * res, ox, oy, res, lum: true, steady: false });
      const big = blank(w * res, h * res, BGC), small = blank(w, h, BGC), cols = new Set();
      for (let j = 0; j < f.key.length; j++) if (f.key[j]) { const g = 0.72 + 0.4 * Math.max(-0.3, f.lum[j]), c = pal.rgb[pal.shift(f.key[j], 0)]; big.rgba.set([c[0] * g, c[1] * g, c[2] * g, 255], j * 4); }
      for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) { const s = [0, 0, 0]; for (let y = 0; y < res; y++) for (let xx = 0; xx < res; xx++) { const o = ((r * res + y) * w * res + c * res + xx) * 4; s[0] += big.rgba[o]; s[1] += big.rgba[o + 1]; s[2] += big.rgba[o + 2]; } const v = s.map(q => Math.round(q / res / res)); small.rgba.set([...v, 255], (r * w + c) * 4); cols.add(v.join()); }
      const ours = stage.frame({ w, h, by, x, pose: a.pose, yaw, shadow: false, clear: true }), ok = ours.key.map(k => k || pal.idx.d1);
      cells.push(up(big, 2), up(small, 16), img(ok, w, h, 16));
      console.log('mush: colours in the shrunk picture', cols.size, '· in ours', new Set(ours.key).size - 1);
    }
    write('mush.png', sheet(cells, 3));
  },
  faces() {
    const cells = [], w = 26, h = 19, by = figBy;
    for (const expr of ch.EXPRS) for (const yaw of [0, 22.5, 90]) cells.push(img(stage.frame({ w, h, by, x: 13, pose: poseOf(DOWN), yaw, face: { expr }, shadow: false }).key, w, h, 8));
    write('faces.png', sheet(cells, 6, 4));
    const ps = [...ch.EXPRS.map(expr => ({ expr })), { blink: true }, { mouth: 'open' }, { mouth: 'round' }].map(f => { const p = stage.portrait(f); return img(p.key, p.w, p.h, 4); });
    write('portraits.png', sheet(ps, 4, 4));
  },
  hero() { write('hero.png', talkFrame(1.0, 'rest', 8)); },

  // ———— films
  turn() { const c = STAND; film('turn', 16 * 2 / 4, (i) => img(stage.frame({ bg: 'street', w: 64, h: 60, by: 38, bx: 78, x: 32, pose: poseOf(c), yaw: Math.floor(i / 3) * 22.5, face: life(i / FPS) }).key, 64, 60, 8), 6 * 2); },
  talk() { const E = ch.EXPRS; film('talk', E.length * 2.5, (i, t) => talkFrame(t, E[Math.floor(t / 2.5) % E.length], 6)); },
  // the same walk twice: as the 3D gives it (every part where the motion puts it, 24 pictures a second) and as the
  // sprite is made (whole pixels and whole steps for the head and the trunk, 12 drawings a second)
  steady() {
    const c = clip('walk');
    film('steady', 4, (i, t) => { const cells = [false, true].map(st => { const a = player.at(c, t, st ? FPS : 0); return img(stage.frame({ w: 40, h: 46, by: figBy, x: 20, pose: a.pose, yaw: 90, follow: true, steady: st, face: life(st ? Math.floor(t * FPS) / FPS : t) }).key, 40, 46, 10); }); return sheet(cells, 2, 8); }, 24);
  },
};
function talkFrame(t, expr, scale) {
  const w = 128, h = 76, by = 24, a = player.at(clip(WHO.talkClip || 'stand'), t), face = life(t, { talk: true, expr });
  const f = stage.frame({ bg: 'street', w, h, by, bx: 62, x: 38, pose: a.pose, yaw: 22.5, face });
  const p = stage.portrait(face);
  for (let r = 0; r < p.h; r++) for (let c = 0; c < p.w; c++) f.key[(r + 5) * w + c + 60] = p.key[r * p.w + c];
  return img(f.key, w, h, scale);
}
for (const c of ch.CLIPS) if (c.motion) P[c.id] = () => {
  const dur = Math.min(player.dur(c), c.cut || 5), strip = [];
  film(c.id, dur, (i, t) => { const a = player.at(c, t), f = stage.frame({ bg: 'street', w: 96, h: 64, by: 34, bx: c.travel ? 40 : 62, x: 48, pose: a.pose, lift: a.lift, yaw: c.yaw || 0, follow: !!c.travel, face: life(t, { expr: c.expr || 'rest' }) }); const im = img(f.key, 96, 64, 8); if (i % 6 === 0) strip.push(img(f.key, 96, 64, 3)); return im; });
  write(path.join(CACHE, `strip-${c.id}.png`), sheet(strip, 6, 4));
};
const STILLS = ['compare', 'exact', 'around', 'steps', 'mush', 'faces', 'hero'], FILMS = ['turn', 'talk', 'steady', ...ch.CLIPS.filter(c => c.motion).map(c => c.id)];
let names = process.argv.slice(2); if (!names.length) names = ['stills'];
names = names.flatMap(n => n === 'stills' ? STILLS : n === 'films' ? FILMS : n === 'all' ? [...STILLS, ...FILMS] : [n]);
for (const n of names) P[n]();
