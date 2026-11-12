// Тим's face: cast.tim's signs and expressions as numbers for face.js (see there)
import { makeFace, mouths } from './face.js';

export const HEAD_Y = -205;                // the head's centre in the drawing (cast.tim: translate(0,-205))
// cast.tim's head
export const HEAD = [[-64, 0, 0, 0, -2], [-58, 38, 36, 0, -2], [-40, 62, 58, 0, -2], [-14, 70, 64, 0, -1], [10, 70, 62, 0, 2],
  [30, 64, 56, 0, 5], [46, 48, 42, 0, 8], [56, 26, 26, 0, 9], [59, 0, 0, 0, 9]];
const M = mouths(9);
const E0 = { happy: 0, big: 1, iris: 0.78, tear: 0 };
export const face = makeFace({
  head: HEAD, rect: [-76, -70, 152, 136],
  eye: { phi: 0.42, y: 10, rx: 10.5, ry: 13 }, brow: { y: -13, w: 18, col: '#9b5a2a', th: 1.6, arch: 3 },
  cheek: { phi: 0.62, y: 26, r: 11, col: '#f08a7a', op: 0.5 }, nose: { y: 24 }, mouth: { phi: 0.08, y: 38, w: 9, lw: 1.13 },
  irisCol: '#2f2426', lash: 1.2, flick: false, bags: false,
  // freckles under the eyes; a plaster on the cheek
  under(ctx, surf) {
    ctx.fillStyle = '#b86a3e';
    for (const [p, y] of [[-0.5, 22], [-0.38, 27], [-0.62, 28], [0.5, 22], [0.38, 27], [0.62, 28]]) { const [x, yy] = surf(p, y); ctx.beginPath(); ctx.arc(x, yy, 1.7, 0, 7); ctx.fill(); }
  },
  over(ctx, surf, sw) {
    const [x, y, f] = surf(0.8, 31);
    ctx.save(); ctx.translate(x, y); ctx.rotate(-25 * Math.PI / 180); ctx.scale(Math.max(f, 0.4), 1);
    ctx.beginPath(); ctx.roundRect(-10, -5, 20, 10, 4); ctx.fillStyle = '#f1d3a6'; ctx.fill(); ctx.lineWidth = sw * 0.7; ctx.strokeStyle = '#4a3036'; ctx.stroke();
    ctx.fillStyle = '#e3b986'; ctx.fillRect(-3.5, -3.5, 7, 7);
    ctx.restore();
  },
  // lids (inner, outer), look (the highlights' shift), brows (his right: height, tilt; his left: height, tilt)
  expr: {
    neutral: { ...E0, lid: [0.05, 0.22], look: [3, 0], brow: [-2, 0, -7, -4], mouth: M.smirk },     // one brow up: up to something
    joy: { ...E0, lid: [0, 0], happy: 1, look: [3, 0], brow: [-4, 3], mouth: M.grin },
    surprise: { ...E0, lid: [0, 0], big: 1.15, iris: 0.72, look: [3, -1], brow: [-12, 0], mouth: M.o },
    sad: { ...E0, lid: [0.1, 0.45], look: [3, 2], brow: [-3, -9], mouth: M.frown, tear: 1 },
    anger: { ...E0, lid: [0.48, 0.1], look: [3, 0], brow: [4, 9], mouth: M.clench },
  },
  phrases: ['А спорим, попаду?', 'Это не я. Честно.', 'Ну… почти не я.', 'Тихо! Кто-то идёт.', 'Бежим!'],
});

