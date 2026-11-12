// what the pictures and films share: the character loaded, pictures as RGBA, sheets, films through ffmpeg
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { Palette, Figure, paint } from './web/vox.js';
import { Stage, Player, Life, FPS } from './web/stage.js';
import { save } from './png.mjs';

export const HERE = path.dirname(fileURLToPath(import.meta.url));
export const WHO = JSON.parse(fs.readFileSync(path.join(HERE, 'character.json')));
export const CACHE = WHO.cache, PICS = path.join(HERE, '../pics');
fs.mkdirSync(CACHE, { recursive: true });
export const ch = await import(`./web/${WHO.key}.js`);
export const D = JSON.parse(fs.readFileSync(path.join(HERE, 'web/drawing.json')));
export const pal = Palette(D.ramps), fig = Figure(ch, pal), stage = Stage(ch, pal, D, fig);
const motions = {};
for (const c of ch.CLIPS) if (c.motion && !motions[c.motion]) motions[c.motion] = JSON.parse(fs.readFileSync(path.join(HERE, 'motions', c.motion + '.json')));
export const player = Player(ch, fig, motions), life = Life(WHO.seed || 7);
export { FPS };

// a picture: {rgba, w, h}
export const img = (key, w, h, scale = 8) => ({ rgba: paint(pal, key, w, h, scale, [0, 0, 0]), w: w * scale, h: h * scale });
export function blank(w, h, col = [29, 22, 36]) { const rgba = new Uint8ClampedArray(w * h * 4); for (let i = 0; i < w * h; i++) rgba.set([col[0], col[1], col[2], 255], i * 4); return { rgba, w, h }; }
export function blit(dst, src, x, y) { for (let r = 0; r < src.h; r++) { const Y = y + r; if (Y < 0 || Y >= dst.h) continue; for (let c = 0; c < src.w; c++) { const X = x + c; if (X < 0 || X >= dst.w) continue; dst.rgba.set(src.rgba.subarray((r * src.w + c) * 4, (r * src.w + c) * 4 + 4), (Y * dst.w + X) * 4); } } return dst; }
export function sheet(cells, cols = cells.length, gap = 8, bg = [29, 22, 36]) {
  const rows = Math.ceil(cells.length / cols), cw = Math.max(...cells.map(c => c.w)), chh = Math.max(...cells.map(c => c.h));
  const out = blank(cols * cw + (cols + 1) * gap, rows * chh + (rows + 1) * gap, bg);
  cells.forEach((c, i) => blit(out, c, gap + (i % cols) * (cw + gap) + ((cw - c.w) >> 1), gap + Math.floor(i / cols) * (chh + gap) + (chh - c.h)));
  return out;
}
export const crop = (im, x, y, w, h) => { const out = blank(w, h); for (let r = 0; r < h; r++) out.rgba.set(im.rgba.subarray(((y + r) * im.w + x) * 4, ((y + r) * im.w + x + w) * 4), r * w * 4); return out; };
export const write = (name, im) => { const f = path.isAbsolute(name) ? name : path.join(PICS, name); save(f, im.rgba, im.w, im.h); console.log(f, im.w + '×' + im.h); };
// a film: draw(i, t) → picture, for every drawing of `seconds`; each drawing is held (12 a second), the file is 24 a second
export function film(name, seconds, draw, fps = FPS) {
  const dir = path.join(CACHE, 'film-' + name); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const n = Math.round(seconds * fps); let im;
  for (let i = 0; i < n; i++) { im = draw(i, i / fps); save(path.join(dir, String(i).padStart(4, '0') + '.png'), im.rgba, im.w, im.h); }
  const out = path.join(PICS, name + '.mp4');
  execFileSync('flock', [`/home/user/cache/heavy.${Math.floor(Math.random() * 3)}.lock`, 'ffmpeg', '-y', '-loglevel', 'error', '-framerate', String(fps), '-i', path.join(dir, '%04d.png'),
    '-vf', 'fps=24', '-sws_flags', 'neighbor', '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '14', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
  console.log(out, n, 'drawings', (fs.statSync(out).size / 1024).toFixed(0) + ' KB');
  return dir;
}
