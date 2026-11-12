// strips of a clip's drawings to look at → the cache:  node look2.mjs walk [yaw] [steady 0/1]
import { ch, stage, player, life, img, sheet, write, CACHE, FPS } from './lib.mjs';
import path from 'node:path';
const [id, yawS, st] = process.argv.slice(2), clip = ch.CLIPS.find(c => c.id === id), yaw = yawS !== undefined ? +yawS : clip.yaw || 0;
const n = Math.min(48, Math.round(player.dur(clip) * FPS)), cells = [];
for (let i = 0; i < n; i++) { const a = player.at(clip, i / FPS); const f = stage.frame({ bg: 'street', w: 56, h: 52, by: 44, bx: 60, x: 28, pose: a.pose, lift: a.lift, yaw, follow: true, steady: st !== '0', face: life(i / FPS) }); cells.push(img(f.key, 56, 52, 4)); }
write(path.join(CACHE, `clip-${id}.png`), sheet(cells, 8, 4));
