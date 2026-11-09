// Кира's face: kira.py's signs and expressions as numbers for face.js (see there)
import { makeFace, mouths } from './face.js';

export const HEAD_Y = -300;                // the head's centre in the drawing (kira.py: translate(…,-300))
// kira.py's head: a longer face than a child's, a small chin
export const HEAD = [[-62, 0, 0, 0, -3], [-56, 32, 32, 0, -3], [-40, 53, 52, 0, -3], [-16, 61, 57, 0, -2], [6, 62, 56, 0, 1],
  [24, 58, 51, 0, 4], [40, 47, 41, 0, 8], [52, 31, 28, 0, 11], [59, 13, 14, 0, 12], [61, 0, 0, 0, 12]];
const M = mouths(6.5);
const E0 = { happy: 0, big: 1, iris: 0.78, tear: 0 };
export const face = makeFace({
  head: HEAD, rect: [-68, -68, 136, 136],
  eye: { phi: 0.42, y: 13, rx: 8.5, ry: 11.5 }, brow: { y: -5, w: 18, col: '#2f2937', th: 1.9, arch: 1 },
  cheek: { phi: 0.62, y: 28, r: 9, col: '#e98a7c', op: 0.3 }, nose: { y: 28 }, mouth: { phi: 0.05, y: 43, w: 6.5, lw: 1.15 },
  irisCol: '#2a2226', lash: 1.7, flick: true, bags: false,
  // lids (inner, outer), look (the highlights' shift: sideways, from under the brows), brows (height, tilt)
  expr: {
    neutral: { ...E0, lid: [0.4, 0.26], look: [-3, 1], brow: [3, 5], mouth: M.tight },          // the mouth pressed shut
    joy: { ...E0, lid: [0.2, 0.12], look: [-2, 0], brow: [-3, 1], mouth: M.half },              // never an open smile: a half-smirk
    surprise: { ...E0, lid: [0, 0], big: 1.1, iris: 0.72, look: [-3, 0], brow: [-12, 0], mouth: M.o },
    sad: { ...E0, lid: [0.22, 0.52], look: [-3, 5], brow: [-2, -8], mouth: M.frown },           // she hides it: no tear
    anger: { ...E0, lid: [0.5, 0.12], look: [-3, 1], brow: [4, 9], mouth: M.clench },
  },
  phrases: ['Ну и что.', 'Не трогайте меня.', 'Мне всё равно. Правда.', 'Отстань.', '…Ладно. Спасибо.'],
});
