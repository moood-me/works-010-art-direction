// Тим of С16 for the 3D: his parts typed pixel by pixel after the style's sprite (styles/s16-pixel/tools/chars/tim.py:
// FRONT, Q, SIDE), each from the front and from the side; SOMA's joints at the sprite's places; the face's pixels by
// the head's turn. Columns and rows are the sprite's own (FRONT's columns, SIDE's columns for depth).
export const NAME = 'tim';
export const LEG = { s: 's3', t: 's2', u: 's1', h: 's4', k: 'x0', i: 'x1', p: 'x2', j: 'x3',
  H: 't2', I: 't3', J: 't4', G: 't1', R: 'r2', q: 'r1', W: 'w3', w: 'w2', U: 'u2', v: 'u1', P: 'c2', N: 'r2', n: 'r1', m: 'r0' };
export const CX = 12.5, CZ = 11.5, FLOOR = 32;   // the figure's middle (front columns, side columns), the row under the soles

const arm = (name, bone, at, front, side = front) => ({ name, bone, at, front, side });
export const PARTS = [
  { name: 'hips', bone: 'Hips', at: [7, 21, 8], steady: true,
    front: [".UUUUUUUvv.", ".UUUUUUUvv.", "UUUUUUUUUvv"],
    side: [".UUUUUv", ".UUUUUv", "UUUUUUv"] },
  { name: 'trunk', bone: 'Chest', at: [8, 12, 9], steady: true,
    front: [".tsssstt.", "RRRuuuRRq", "WWWWWWWWw", "RRRRRRRRq", "WWWWWWWWw", "RRRRRRRRq", "WWWWWWWWw", "RRRRRRRRq", "WWWWWWWWw", "UUUUUUUvv"],
    back: [".tsssstt.", "RRRRRRRRq", "WWWWWWWWw", "RRRRRRRRq", "WWWWWWWWw", "RRRRRRRRq", "WWWWWWWWw", "RRRRRRRRq", "WWWWWWWWw", "UUUUUUUvv"],
    side: ["tsssss", "RRRRRq", "WWWWWw", "RRRRRq", "WWWWWw", "RRRRRq", "WWWWWw", "RRRRRq", "WWWWWw", "UUUUUv"] },
  { name: 'head', bone: 'Head', at: [5, 0, 4], steady: true,
    front: [
      "....H...H.......",
      "...HIH.HIH..H...",
      "..HIIIHIIHHHH...",
      ".HIIJIIIHHHHHG..",
      "HIIJIIHHHHHHHHG.",
      "HIIHHHsHHsHHHHG.",
      "HIHsssssssssHHG.",
      "HHsssssssssstHG.",
      ".GsssssssssstG..",
      ".sssssssssssst..",
      "..sssssssssst...",
      "...sssssssst....",
      "....tsssstt.....",
    ],
    side: [
      ".....H...H......",
      "....HIH.HIH..H..",
      "...HIIIHIIHHHH..",
      "..HIIJIIIHHHHHG.",
      ".HIIJIIHHHHHHHHG",
      "HIIHHHHHHsHHHG..",
      "HIHHHHHsssssss..",
      "HHHHHHssssssss..",
      "HHHGstsssssssst.",
      "HHGGstssssssss..",
      ".GGGssssssssst..",
      "....ssssssssst..",
      ".....tssssst....",
    ],
    back: [
      ".......H...H....",
      "...H..HIH.HIH...",
      "...HIIIHIIHHHH..",
      "..HIIJIIIHHHHHG.",
      ".HIIJIIHHHHHHHHG",
      ".HIIHHHHHHHHHHHG",
      ".HIHHHHHHHHHHHHG",
      ".HHHHHHHHHHHHHGG",
      "..HHHHHHHHHHHGG.",
      "..GHHHHHHHHHGGG.",
      "...GGHHHHHGGGG..",
      "....ssssssstt...",
      ".....tsssstt....",
    ] },
  // ears that stick out: their own small volumes, or the whole head would be a pixel wider at their rows
  { name: 'earR', bone: 'Head', at: [5, 8, 8], steady: true, front: ["s", "s"], side: ["st", "st"] },
  { name: 'earL', bone: 'Head', at: [19, 8, 8], steady: true, front: ["t.", "st"], side: ["st", "st"] },
  // legs: a thigh in its leg of the shorts, a shin with the sock, a shoe
  { name: 'thighR', bone: 'RightLeg', at: [7, 22, 10], front: [".UUUU", "UUUUU", ".UUUU", ".UUUv", "..sP."], side: ["UUUv", "UUUv", "UUUv", "UUUv", ".st."] },
  { name: 'thighL', bone: 'LeftLeg', at: [13, 22, 10], front: ["UUvv.", "UUUvv", "UUUvv", "UUUvv", ".st.."], side: ["UUUv", "UUUv", "UUUv", "UUUv", ".st."] },
  { name: 'shinR', bone: 'RightShin', at: [9, 26, 11], front: ["sP", "st", "st", "Ww"], side: ["st", "st", "st", "Ww"] },
  { name: 'shinL', bone: 'LeftShin', at: [14, 26, 11], front: ["st", "st", "st", "Ww"], side: ["st", "st", "st", "Ww"] },
  { name: 'shoeR', bone: 'RightFoot', at: [7, 30, 10], front: [".NNN", "iNNN"], side: ["NNNN.", "NNNNi"], back: ["nnn.", "nnni"] },
  { name: 'shoeL', bone: 'LeftFoot', at: [14, 30, 10], front: ["NNN.", "NNNi"], side: ["NNNN.", "NNNNi"], back: [".nnn", "innn"] },
  // arms, hanging at rest: a short sleeve, a forearm, a hand of a few pixels
  arm('armR', 'RightArm', [6, 13, 11], ["RR", "RR", "ss", "ss"], ["qq", "qq", "ss", "ss"]),
  arm('foreR', 'RightForeArm', [6, 16, 11], ["ss", "ss", "ss", "ss"]),
  arm('handR', 'RightHand', [5, 19, 11], [".ss", "sss", "sst"], ["ss", "ss", "st"]),
  arm('armL', 'LeftArm', [17, 13, 11], ["Rq", "Rq", "st", "st"], ["qq", "qq", "ss", "ss"]),
  arm('foreL', 'LeftForeArm', [17, 16, 11], ["st", "st", "st", "st"], ["ss", "ss", "ss", "ss"]),
  arm('handL', 'LeftHand', [17, 19, 11], ["st.", "sss", "sst"], ["ss", "ss", "st"]),
];
export const FACE_ON = 'head';

// joints: [front column, row, side column]
const side = (s, x, m) => Object.fromEntries(Object.entries(m).map(([b, [dx, y, z]]) => [s + b, [12.5 + x * dx, y, z]]));
export const J = {
  Hips: [12.5, 22, 12], Spine1: [12.5, 20, 12], Spine2: [12.5, 18, 12], Chest: [12.5, 16, 12], Neck1: [12.5, 13.5, 12], Neck2: [12.5, 13, 12],
  Head: [12.5, 12.5, 12], HeadEnd: [12.5, 0, 12], Jaw: [12.5, 10, 14], LeftEye: [14.5, 8, 17], RightEye: [10.5, 8, 17],
  ...side('Left', 1, { Shoulder: [2, 13.5, 12], Arm: [5.5, 13.5, 12], ForeArm: [5.5, 17, 12], Hand: [5.5, 20, 12], Leg: [2.5, 22.5, 12], Shin: [2.5, 27, 12], Foot: [2.5, 30, 12], ToeBase: [2.5, 31.5, 13.5], ToeEnd: [2.5, 31.5, 15] }),
  ...side('Right', -1, { Shoulder: [2, 13.5, 12], Arm: [5.5, 13.5, 12], ForeArm: [5.5, 17, 12], Hand: [5.5, 20, 12], Leg: [2.5, 22.5, 12], Shin: [2.5, 27, 12], Foot: [2.5, 30, 12], ToeBase: [2.5, 31.5, 13.5], ToeEnd: [2.5, 31.5, 15] }),
};
export const SOLE = [['RightFoot', [9, 32, 10]], ['RightFoot', [9, 32, 15]], ['LeftFoot', [16, 32, 10]], ['LeftFoot', [16, 32, 15]]];
export const HEAD = { c: [12.5, 6.5, 12], r: 9.5 };
export const SHADOW = [8, 6];        // half-widths of the two rows of shadow under the feet

// ———— the face: a dozen pixels. Places are typed for the head seen from the front, at three quarters and from the
// side (the sprite's three drawn views) and go between them by whole pixels; a face looking left is the mirror, but
// the glint of the eye stays on the light's side
const EYES = { // two columns wide; rows from 6 (the brow's row) down
  rest: { a: ["..", "ik", "kk"], b: ["..", "ik", "kk"] },
  blink: { a: ["..", "ss", "kk"], b: ["..", "ss", "kk"] },
  joy: { a: ["..", "kk", "ss"], b: ["..", "kk", "ss"] },
  surprise: { a: ["ik", "kk", "ss"], b: ["ik", "kk", "ss"] },
  sadness: { a: [".G", "ks", "kk"], b: ["G.", "sk", "kk"] },
  anger: { a: ["G.", "sk", "kk"], b: [".G", "ks", "kk"] },
};
const MOUTH = { // five wide from row 10; the side view shows three
  rest: ["uiiiu"], joy: ["uiiiu", ".qqq."], surprise: ["sssss", ".mmm.", "..m.."].slice(0, 2), sadness: ["sssss", ".uuu.", "u...u"], anger: ["ummmu"],
  closed: [".uuu."], open: ["uiiiu", ".qqq."], round: ["sssss", ".mmm."],
};
const key3 = (a, t) => t <= 45 ? a[0] + (a[1] - a[0]) * t / 45 : a[1] + (a[2] - a[1]) * (t - 45) / 45;
export function face({ psi, pitch, expr = 'rest', blink = false, mouth = null }) {
  const t = Math.abs(psi), out = [];
  if (t > 120) return out;
  if (t > 100) { out.push({ x: psi < 0 ? 7 : 17, y: 7 + (pitch > 16 ? -1 : pitch < -16 ? 1 : 0), rows: ['k', 'k'] }); return out; }   // going away: one column of the eye is left
  const E = EYES[blink && expr !== 'joy' ? 'blink' : expr] || EYES.rest, M = MOUTH[mouth || expr] || MOUTH.rest;
  const dy = pitch > 16 ? -1 : pitch < -16 ? 1 : 0, left = psi < 0, sideways = t > 62;
  const X = (a, w) => { const x = Math.round(key3(a, Math.min(t, 90))); return left ? 24 - x - (w - 1) : x; };
  const eye = (rows, x) => out.push({ x, y: 6 + dy, rows });
  // the eye nearer to the viewer when the head turns, and the far one (it narrows to one column, then is gone)
  eye(left ? E.b : E.a, X([9, 10, 15], 2));
  if (!sideways) { const far = left ? E.a : E.b, w = t > 30 ? 1 : 2; eye(w === 2 ? far : far.map(r => r === '..' ? '.' : (left ? r[0] : r[1]) === 'i' ? 'k' : (left ? r[0] : r[1])), X(w === 2 ? [14, 15, 16] : [15, 16, 17], w)); }
  if (expr !== 'anger' && expr !== 'sadness') { out.push({ x: X([9, 10, 16], 1), y: 9 + dy, rows: ['p'] }); if (!sideways) out.push({ x: X([16, 17, 18], 1), y: 9 + dy, rows: ['p'] }); }
  const m = sideways ? M.map(r => left ? r.slice(-3) : r.slice(0, 3)) : M;
  out.push({ x: X(sideways ? [14, 14, 14] : [10, 12, 14], sideways ? 3 : 5), y: 10 + dy, rows: m });
  return out;
}
export const EXPRS = ['rest', 'joy', 'surprise', 'sadness', 'anger'];

// the portrait's parts that change in a dialogue (the framed 62×62 picture): the eyes' rows, the mouth; which drawn
// expression lends its mouth to a syllable
export const PORTRAIT = { eyes: [19, 26, 42, 30], mouth: [23, 34, 38, 41], talk: { open: 'joy', round: 'surprise' } };

// ———— held poses and clips
// the sprite's own pose: he waves with his right hand, the left is on the hip (directions of the upper arm and forearm)
export const HOLD = { drawn: { RightArm: [-0.86, 0.5, 0.1], RightForeArm: [-0.42, 0.9, 0.1], LeftArm: [0.62, -0.76, -0.2], LeftForeArm: [-0.72, -0.66, 0.22] } };
export const STEP = 30;         // the head and the trunk turn by whole steps of so many degrees
// his wave is the drawing's: the raised forearm swings (Kimodo's wave on arms this short ends at the cheek); the body
// under it is Kimodo's
const swing = t => { const a = [0.55, 0.2, -0.15, 0.2][Math.floor(t * 8) % 4]; return { ...HOLD.drawn, RightForeArm: [-0.42 - a, 0.9, 0.1] }; };
export const CLIPS = [
  { id: 'stand', label: 'стоит', hold: 'drawn', yaw: 0, dur: 4 },
  { id: 'walk', label: 'идёт', motion: 'walk', travel: true, yaw: 90 },
  { id: 'run', label: 'бежит', motion: 'run', travel: true, yaw: 90 },
  { id: 'sneak', label: 'крадётся', motion: 'sneak', travel: true, yaw: 90 },
  { id: 'jump', label: 'прыгает', motion: 'jump', yaw: 22.5 },
  { id: 'wave', label: 'машет', motion: 'wave', arms: false, holdAt: swing, yaw: 0 },
];
export const SAY = 'Тим';
