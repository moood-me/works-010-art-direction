import fs from 'node:fs';
import { Palette, Figure, paint, put } from './web/vox.js';
import { rest } from './web/rig.js';
import * as ch from './web/tim.js';
import { save } from './png.mjs';
const D = JSON.parse(fs.readFileSync(new URL('./web/drawing.json', import.meta.url)));
const pal = Palette(D.ramps), fig = Figure(ch, pal);
console.log(fig.parts.map(p => p.name + ':' + p.voxels).join(' '));
const yaws = [0, 22.5, 45, 67.5, 90, 135, 180, 225, 270, 315, -45], w = 30, h = 36, W = w * yaws.length, sheet = new Uint8Array(W * h).fill(pal.idx.d1);
const t0 = Date.now();
yaws.forEach((yaw, i) => { const f = fig.outline(fig.render({ pose: rest(fig.J), yaw, w, h, ox: 3, oy: 2 })); put(sheet, W, h, f.key, w, h, i * w, 0); });
console.log('ms a picture', (Date.now() - t0) / yaws.length);
save(process.argv[2], paint(pal, sheet, W, h, 5), W * 5, h * 5);
// against the drawing, from the front
const f = fig.render({ pose: rest(fig.J), yaw: 0, w: 24, h: 32, ox: 0, oy: 0, face: {} }), raw = pal.grid(D.raw.front);
let out = '';
for (let r = 0; r < 32; r++) { let a = '', b = ''; for (let c = 0; c < 22; c++) { const k = f.key[r * 24 + c], d = raw[r][c] || 0; a += k ? pal.key(k) : '..'; b += k === d ? '  ' : (d ? pal.key(d) : '--'); } out += a + '   ' + b + '\n'; }
console.log(out);
