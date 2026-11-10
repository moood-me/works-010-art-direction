// quick sheets to look at while working → the cache
import { ch, pal, fig, stage, player, img, sheet, write, CACHE } from './lib.mjs';
import path from 'node:path';
const out = n => path.join(CACHE, n);
const stand = ch.CLIPS[0], plain = {};
// the turn: the drawing above, the 3D below
{
  const w = 96, h = ch.FLOOR + 10, by = 67 - h, top = stage.ground('backdrop', w, h, 0, by);
  ['front', 'q', 'side'].forEach((v, i) => stage.sprites[v] && stage.drawn(top, w, h, v, 16 + i * 32, by));
  const cells = [img(top, w, h)];
  for (const yaws of [[0, 22.5, 90], [0, 45, 90]]) {
    let k = stage.ground('backdrop', w, h, 0, by);
    yaws.forEach((yaw, i) => { const f = stage.frame({ clear: true, w, h, by, x: 16 + i * 32, pose: player.at(stand, 0).pose, yaw, shadow: false }); stage.shadow(k, w, h, 16 + i * 32, 62 - by); for (let j = 0; j < w * h; j++) if (f.key[j]) k[j] = f.key[j]; });
    cells.push(img(k, w, h));
  }
  write(out('turn.png'), sheet(cells, 1));
}
// all round
for (const [nm, clip] of [['around', plain], ['around-drawn', stand]]) {
  const cells = [];
  for (let i = 0; i < 16; i++) { const f = stage.frame({ w: 34, h: ch.FLOOR + 10, by: 57 - ch.FLOOR, x: 17, pose: player.at(clip, 0).pose, yaw: i * 22.5 }); cells.push(img(f.key, 34, ch.FLOOR + 10, 6)); }
  write(out(nm + '.png'), sheet(cells, 8, 4));
}
// faces
{
  const cells = [];
  for (const expr of [...ch.EXPRS, 'blink', 'open', 'round', 'closed']) for (const yaw of [0, 22.5, 45, 67.5, 90, -45, -90]) {
    const face = ch.EXPRS.includes(expr) ? { expr } : expr === 'blink' ? { blink: true } : { mouth: expr };
    const f = stage.frame({ w: 24, h: 18, by: 60 - ch.FLOOR, x: 12, pose: player.at(plain, 0).pose, yaw, face, shadow: false });
    cells.push(img(f.key, 24, 18, 8));
  }
  write(out('faces.png'), sheet(cells, 7, 4));
  const ps = [...ch.EXPRS.map(expr => ({ expr })), { blink: true }, { mouth: 'open' }, { mouth: 'round' }].map(f => { const p = stage.portrait(f); return img(p.key, p.w, p.h, 4); });
  write(out('portraits.png'), sheet(ps, 8, 4));
}
