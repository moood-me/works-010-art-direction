// Аня of С16 for the 3D: her parts typed pixel by pixel after the style's sprite (styles/s16-pixel/tools/chars/anya.py:
// FRONT — the only view drawn); the side and the back are typed here by the same rules. SOMA's joints at the
// sprite's places; the face's pixels by the head's turn. Columns and rows are the sprite's own.
export const NAME = 'anya';
export const LEG = { s: 's3', t: 's2', u: 's1', h: 's4', k: 'x0', i: 'x1', p: 'x2', j: 'x3', m: 'r0',
  A: 'a1', B: 'a2', C: 'a3', D: 'a4', Y: 't2', y: 't1', Z: 't3', W: 'w3', w: 'w2', T: 'e2', d: 'e1', L: 'e3', O: 'b2', o: 'b1', R: 'r2', q: 'r1', F: 'r4' };
export const CX = 11.5, CZ = 11.5, FLOOR = 43;
export const STEP = 30;
export const MIX = 1.6;          // her head is hair all round a small face: its sides are read from the side map while the face is still read from the front

const rep = (row, n) => Array(n).fill(row);
export const PARTS = [
  // the long hair behind the shoulders, and the two locks that lie on them in front: they stay with the chest
  { name: 'hairBack', bone: 'Chest', at: [5, 13, 5], steady: true,
    front: ["BBBAABBBAABBA", ...rep("BBBBBBBBBBBBA", 6), ".BBBBBBBBBBA.", "..BBABBBABA.."],
    back: [...rep("CBBBBBBBBBBBA", 2), ...rep("CBBABBBBBABBA", 3), ...rep("BBBABBBABBBBA", 2), ".BBABBBABBBA.", "..BA.BBA.BA.."].map((r, i) => i === 8 ? "..BBABBBABA.." : r),
    side: [...rep("BBB", 7), "BBA", ".BA"] },
  { name: 'trunk', bone: 'Chest', at: [5, 13, 8], steady: true,
    front: ["......uuu....", "..YYWsssWYY..", ".YYZWWsWWYyy.", "yYYYWWWWWYyyy", "yYYYYWWWYYyyy", "yYYYYWWWYYyyy", "yYYYYYWYYYyyy", "yYYYYYWYYYyyy", "yYYYYYYYYYyyy", "yYYYYYYYYYyyy", "yyYYYYYYYyyy.", ".TTTTTTTTTdd."],
    back: ["......uuu....", "..YYYYYYYYY..", ".YYYYYYYYYyy.", ...rep("YYYYYYYYYYyyy", 7), "yyYYYYYYYyyy.", ".TTTTTTTTTdd."],
    side: ["...uuu.", ".YYYYWw", "YYYYYWw", "YYYYYYW", "YYYYYYW", "YYYYYYW", ...rep("YYYYYYy", 5), "TTTTTTd"] },
  { name: 'lockR', bone: 'Chest', at: [4, 13, 6], steady: true, round: 6,
    front: ["CBBA", "CBB.", "CBB.", ".BB.", ".BA.", "..A."],
    side: ["BBBBBBBBB", "BBBBBBBBB", ".BBBBBBBB", ".....BBBB", "......BBA", ".......BA"] },
  { name: 'lockL', bone: 'Chest', at: [15, 13, 6], steady: true, round: 6,
    front: ["BBBA", ".BBA", ".BBA", ".BA.", ".A.."],
    side: ["BBBBBBBBB", "BBBBBBBBB", ".BBBBBBBB", ".....BBBA", "......BAA"] },
  // the book she holds to her chest
  { name: 'book', bone: 'Chest', at: [8, 17, 15], steady: true, round: 12,
    front: ["RRRRRRq", "RFFRRRq", "RRRRRRq", "RRRRRRq", "RRRRRRq", "qqqqqqq"],
    back: rep("qqqqqqq", 6), side: ["wR", "wR", "wR", "wR", "wR", "wq"] },
  { name: 'head', bone: 'Head', at: [4, 0, 4], steady: true,
    front: [
      "....BBBBBBB....",
      "..BBCCCCCBBBB..",
      ".BCCDDCCCBBBBB.",
      "BCCDCCCCBBBBBBA",
      "BCCCCBBsBBBBBBA",
      "CCBBBssssBBBBBA",
      "CBBssssssssBBBA",
      "CBBsssssssstBBA",
      "CBBsssssssstBBA",
      "CBBsssssssstBBA",
      "CBBsssssssstBBA",
      "CBBBsssssstBBBA",
      "CBBBAsssssABBBA",
    ],
    side: [
      "....BBBBBBB....",
      "..BBCCCCCBBBB..",
      ".BCCDDCCCBBBBB.",
      "BCCDCCCCBBBBBBA",
      "BCCCCBBBBBBBBBs",
      "CBBBBBBBBBssss.",
      "BBBBBBBBBBssss.",
      "BBBBBBBBBAssss.",
      "BBBBBBBBBAsssst",
      "BBBBBBBBBAssss.",
      "BBBBBBBBBAssss.",
      "BBBBBBBBBBAsst.",
      "BBBBBBBBBBAAt..",
    ],
    back: ["....BBBBBBB....", "..BBCCCCCBBBB..", ".BCCDDCCCBBBBB.", "BCCDCCCCBBBBBBA", "BCCCCBBBBBBBBBA", "CCBBBBBBBBBBBBB", ...rep("CBBBBBBBBBBBBBB", 7)] },
  // the skirt: a stiff bell on the hips; the thighs move inside it
  { name: 'skirt', bone: 'Hips', at: [3, 24, 6], steady: true,
    front: [
      "...TTTTTTTTTdd...",
      "...TLTTTTTTTdd...",
      "..TTLTTTTTTTTdd..",
      "..TLTTTTTTTTTdd..",
      ".TTLTTTTdTTTTddd.",
      ".TLTTTTTdTTTTTdd.",
      ".TLTTTTdTTTTTTdd.",
      "TTLTTTTdTTTTTTddd",
      "TTTTTTdTTTTTTTTdd",
      "dTTTddTTTTddTTddd",
    ],
    side: ["..TLTTTTd..", "..TLTTTTd..", ".TTLTTTTTd.", ".TTLTTTTTd.", ".TLTTTTTTd.", ".TLTTTdTTd.", ".TLTTTdTTd.", "TTLTTTdTTdd", "TTTTTdTTTdd", "dTTddTTTddd"] },
  { name: 'thighR', bone: 'RightLeg', at: [8, 25, 11], front: rep("st", 9), side: rep("st", 9) },
  { name: 'thighL', bone: 'LeftLeg', at: [13, 25, 11], front: rep("st", 9), side: rep("st", 9) },
  { name: 'shinR', bone: 'RightShin', at: [8, 33, 11], front: [...rep("st", 6), "Ww", "Ww"], side: [...rep("st", 6), "Ww", "Ww"] },
  { name: 'shinL', bone: 'LeftShin', at: [13, 33, 11], front: [...rep("st", 6), "Ww", "Ww"], side: [...rep("st", 6), "Ww", "Ww"] },
  { name: 'shoeR', bone: 'RightFoot', at: [7, 41, 10], front: ["OOo", "OOo"], side: ["OOOo.", "OOOOo"], back: ["ooo", "ooo"] },
  { name: 'shoeL', bone: 'LeftFoot', at: [13, 41, 10], front: ["OOo", "oOO"], side: ["OOOo.", "OOOOo"], back: ["ooo", "ooo"] },
  // arms in the cardigan's sleeves, hanging at rest
  { name: 'armR', bone: 'RightArm', at: [3, 15, 10], front: rep("YY", 6), side: rep("YYy", 6) },
  { name: 'foreR', bone: 'RightForeArm', at: [3, 20, 11], front: rep("YY", 4), side: rep("YY", 4) },
  { name: 'handR', bone: 'RightHand', at: [3, 23, 11], front: ["YY", "ss", "st"], side: ["YY", "ss", "st"] },
  { name: 'armL', bone: 'LeftArm', at: [18, 15, 10], front: rep("yy", 6), side: rep("YYy", 6) },
  { name: 'foreL', bone: 'LeftForeArm', at: [18, 20, 11], front: rep("yy", 4), side: rep("Yy", 4) },
  { name: 'handL', bone: 'LeftHand', at: [18, 23, 11], front: ["yy", "ss", "st"], side: ["Yy", "ss", "st"] },
];
export const FACE_ON = 'head';

const side = (s, x, m) => Object.fromEntries(Object.entries(m).map(([b, [dx, y, z]]) => [s + b, [11.5 + x * dx, y, z]]));
const LIMBS = { Shoulder: [2.5, 15, 11.5], Arm: [7.5, 15.5, 12], ForeArm: [7.5, 20.5, 12], Hand: [7.5, 24, 12], Leg: [2.5, 25.5, 12], Shin: [2.5, 33.5, 12], Foot: [2.5, 41, 12], ToeBase: [2.5, 42.5, 13.5], ToeEnd: [2.5, 42.5, 15] };
export const J = {
  Hips: [11.5, 25, 11.5], Spine1: [11.5, 23, 11.5], Spine2: [11.5, 21, 11.5], Chest: [11.5, 18, 11.5], Neck1: [11.5, 14, 11.5], Neck2: [11.5, 13.5, 11.5],
  Head: [11.5, 13, 11.5], HeadEnd: [11.5, 0, 11.5], Jaw: [11.5, 10, 14], LeftEye: [13.5, 8, 17], RightEye: [9.5, 8, 17],
  ...side('Left', 1, LIMBS), ...side('Right', -1, LIMBS),
};
export const SOLE = [['RightFoot', [8.5, 43, 10]], ['RightFoot', [8.5, 43, 15]], ['LeftFoot', [14.5, 43, 10]], ['LeftFoot', [14.5, 43, 15]]];
export const HEAD = { c: [11.5, 6.5, 11.5], r: 9.5 };
export const SHADOW = [9, 7];

// ———— the face: two eyes of one column, a blush under each, a mouth of three pixels (the style's rule for a sprite).
// Places for the head seen from the front, at three quarters and from the side; a face looking left is the mirror.
const EYES = { // three columns round the eye's own; rows from 6
  rest: { a: ["...", ".k.", ".k."], b: ["...", ".k.", ".k."] },
  blink: { a: ["...", ".s.", ".k."], b: ["...", ".s.", ".k."] },
  joy: { a: ["...", ".k.", "ksk"], b: ["...", ".k.", "ksk"] },
  surprise: { a: [".k.", ".k.", ".s."], b: [".k.", ".k.", ".s."] },
  sadness: { a: ["..A", "Ak.", ".k."], b: ["A..", ".kA", ".k."] },
  anger: { a: ["A..", ".kA", ".k."], b: ["..A", "Ak.", ".k."] },
};
const MOUTH = { // three wide from row 10; the side view shows two
  rest: ["uuu"], joy: ["uiu", ".j."], surprise: ["sms", ".m."], sadness: ["sus", "usu"], anger: ["mmm"],
  closed: ["uuu"], open: ["umu", ".j."], round: ["sms", ".m."],
};
// a feature's place: its column in the front map and in the side map make a point on the head; the head's turn puts
// it on a whole pixel
export function face({ psi, pitch, expr = 'rest', blink = false, mouth = null }) {
  const t = Math.abs(psi), out = [], a = psi * Math.PI / 180;
  if (t > 112) return out;
  const E = EYES[blink && expr !== 'joy' ? 'blink' : expr] || EYES.rest, M = MOUTH[mouth || expr] || MOUTH.rest;
  const dy = pitch > 16 ? -1 : pitch < -16 ? 1 : 0, left = psi < 0, sideways = t > 62;
  const X = (x, z, w) => Math.round((x - CX) * Math.cos(a) + (z - CZ) * Math.sin(t * Math.PI / 180) * (left ? -1 : 1) + CX - w / 2);
  const near = left ? 13.5 : 9.5, far = left ? 9.5 : 13.5;         // the eye that stays in sight when she turns
  const half = rows => rows.map(r => left ? '.' + r.slice(1) : r.slice(0, 2) + '.');   // in profile the brow's far end is out of sight
  out.push({ x: X(near, 16.5, 3), y: 6 + dy, rows: sideways ? half(left ? E.b : E.a) : left ? E.b : E.a });
  if (t < 50) out.push({ x: X(far, 16.5, 3), y: 6 + dy, rows: left ? E.a : E.b });
  if (expr !== 'anger') { out.push({ x: X(left ? 14.5 : 8.5, 15.5, 1), y: 9 + dy, rows: ['p'] }); if (t < 40) out.push({ x: X(left ? 8.5 : 14.5, 15.5, 1), y: 9 + dy, rows: ['p'] }); }
  const m = sideways ? M.map(r => left ? r.slice(0, 2) : r.slice(-2)) : M;
  out.push({ x: X(11.5, sideways ? 17 : 17.5, sideways ? 2 : 3), y: 10 + dy, rows: m });
  return out;
}
export const EXPRS = ['rest', 'joy', 'surprise', 'sadness', 'anger'];
export const PORTRAIT = { eyes: [20, 27, 41, 32], mouth: [25, 38, 36, 43], talk: { open: 'joy', round: 'surprise' } };

// ———— held poses and clips. She holds the book to her chest in everything she does (directions of the upper arm and
// the forearm, against the chest); to wave, the right hand lets go
const BOOK = { RightArm: [-0.05, -1, 0.12], RightForeArm: [0.6, -0.12, 0.78], LeftArm: [0.05, -1, 0.12], LeftForeArm: [-0.6, -0.12, 0.78] };
export const HOLD = { book: BOOK };
const swing = t => { const a = [0.5, 0.15, -0.2, 0.15][Math.floor(t * 6) % 4]; return { ...BOOK, RightArm: [-0.8, 0.1, 0.3], RightForeArm: [-0.25 - a, 0.95, 0.2] }; };
export const CLIPS = [
  { id: 'stand', label: 'стоит', hold: 'book', yaw: 0, dur: 4 },
  { id: 'walk', label: 'идёт', motion: 'walk', travel: true, yaw: 90, arms: false, hold: 'book' },
  { id: 'run', label: 'бежит', motion: 'run', travel: true, yaw: 90, arms: false, hold: 'book' },
  { id: 'wave', label: 'машет', motion: 'wave', yaw: 0, arms: false, holdAt: swing },
];
export const COMPARE = [{ yaw: 0, clip: 'stand' }, { yaw: 22.5, clip: 'stand' }, { yaw: 90, clip: 'stand' }];
