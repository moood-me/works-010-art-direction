// Our heads as the engine's head presets: Г1's and Г3's heads (experiments/heads-anime, experiments/heads-wrap) read
// from their pages as they are, and one of Г2's solids fitted to a picture as a way of the form (chars.py), written as
// presets of parts — each head's form (form-<id>: a wrap onto its designed form), features (features-<id>), hair
// (hair-<id>) and headwear (wear-<id>: what is rigid on it), the expressions and lights they share — and a head preset
// taking them (head-<id>), with characters wearing them and the outfit each was drawn in (outfit-<id>: clothes) (characters/head-*.json, on the moood body each was drawn on). The pages'
// data are read by running their own lines that define it, alone in a context of their own (node:vm: nothing of node or
// of this tool reachable). Run again after their pages change, then `node engine/tools/characters.mjs presets` and
// `… pin head-…`.
//   node engine/tools/heads.mjs
import { readFile, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { runInNewContext } from 'node:vm';
import { fileURLToPath } from 'node:url';
import { HEAD_SIZE } from '../src/head/frame.js';

const ROOT = new URL('../../', import.meta.url), EN = new URL('../', import.meta.url);
const page = async p => (await readFile(new URL(p, ROOT), 'utf8')).split('\n');
const save = (url, d) => writeFile(url, JSON.stringify(d, null, 1) + '\n');
// the characters' data: Г3's page holds nine (its own versions), Г1's the two it never wrapped
const wrapPage = await page('experiments/heads-wrap/index.html'), animePage = await page('experiments/heads-anime/index.html');
const from = (lines, start, stop) => { const a = lines.findIndex(l => l.startsWith(start)), b = lines.findIndex((l, i) => i > a && l.startsWith(stop)); return lines.slice(a, b).join('\n'); };
const C = {}, C1 = {};
runInNewContext(from(wrapPage, 'const C = {};', '// ———— the head').replace('const C = {};', ''), { C });
runInNewContext(from(animePage, 'C.alva', 'const NRM'), { C: C1 });
const WRAPPED = Object.keys(C);   // Г3 wrapped these with its own form (no jaw rise, no neck softness of their own)
Object.assign(C, C1);

const NAMES = { anime: ['аниме-девушка', 'anime girl'], red: ['рыжая девушка', 'red-haired girl'], boy7: ['мальчик с каре', 'boy with a bob'], mask: ['девушка в маске', 'masked girl'], hood: ['женщина в капюшоне', 'hooded woman'],
  blond: ['блондин', 'blond boy'], tails: ['мальчик с хвостиками', 'boy with tails'], old: ['старик', 'old man'], semi: ['парень с длинным носом', 'long-nosed man'], alva: ['Альва', 'Alva'], jesper: ['Джеспер', 'Jesper'] };
const BODY = { woman: 'moood-woman', man: 'moood-man', child: 'moood-child', girl: 'moood-girl', oldman: 'moood-oldman', boy: 'moood-boy' };
const pick = (o, keys) => Object.fromEntries(keys.filter(k => o[k] !== undefined).map(k => [k, o[k]]));

function formOf(id, CH) {
  const h = CH.head, f = h.face, N = f.nose;
  const longNose = N.ridge && Math.max(...N.ridge.map(q => q[1])) - N.ridge[0][1] > 0.2, piece = !!(N.ball || longNose);
  const nose = N.ridge ? { ...pick(N, ['ridge', 'under', 'w', 'k', 'round', 'r']), ...(N.wings ? { wings: { y: N.wings[0], z: N.wings[1], r: N.wings.slice(2) } } : {}) }
    : { ...pick(N, ['root', 'tip', 'base', 'k']), radius: N.r };
  if (N.ball) nose.ball = { at: N.ball.slice(0, 3), r: N.ball[3], ...(N.bk ? { k: N.bk } : {}) };
  if (piece) nose.piece = true;
  const face = { ...pick(f, ['n', 'W', 'P']), nose };
  if (!WRAPPED.includes(id) && f.jawRise) face.jawRise = f.jawRise;
  if (f.lips) face.lips = f.lips.map(L => ({ at: [0, L[0], L[1]], r: L.slice(2, 5) }));
  if (f.masses) face.masses = f.masses.map(M => ({ at: M.slice(0, 3), r: [M[3], M[3] * (M[6] || 1), M[3] * (M[7] || 0.8)], k: M[4], ...(M[5] === 'mid' ? { mirror: false } : {}) }));
  const form = { kind: 'curves', size: CH.hs ?? HEAD_SIZE, face };
  const cr = pick(h, ['cw', 'ch', 'cd']); if (Object.keys(cr).length) form.cranium = { ...(cr.cw ? { w: cr.cw } : {}), ...(cr.ch ? { h: cr.ch } : {}), ...(cr.cd ? { d: cr.cd } : {}) };
  if (h.ears) form.ears = h.ears;
  form.neck = { r: h.neckR ?? 0.36, ...(!WRAPPED.includes(id) && h.neckK ? { k: h.neckK } : {}) };
  return { form, piece };
}
function featuresOf(CH) {
  const F = CH.face, out = [];
  out.push({ id: 'eyes', kind: 'eye', as: 'paint', ...F.eye });
  out.push({ id: 'brows', kind: 'brow', as: 'paint', ...F.brow });
  if (F.mask) out.push({ id: 'mask', kind: 'mask', ...F.mask });
  else out.push({ id: 'mouth', kind: 'mouth', as: 'paint', ...F.mouth });
  if (F.marks) out.push({ id: 'marks', kind: 'marks', lines: F.marks });
  if (F.blush) out.push({ id: 'blush', kind: 'blush', amount: F.blush });
  if (F.noseTint) out.push({ id: 'tint', kind: 'tint', color: F.noseTint });
  return out;
}
const hairOf = CH => [{ id: 'hair', kind: 'hair', color: CH.hairColor, ...(CH.hairInk ? { ink: CH.hairInk } : {}), parts: CH.hair }];
// what is rigid on the head stays with it (a hat, an ear device); what is cloth — a hood, the turtleneck, the outfit
// each was drawn in (MakeHuman's garments) — is the character's clothes (src/cloth/), an outfit preset of its own
const CLOTH = new Set(['hood', 'turtleneck']);
const wearOf = CH => (CH.extras || []).filter(([kind]) => !CLOTH.has(kind)).map(([kind, o]) => ({ id: kind, kind, ...o }));
// each garment of the pages in the fabric such a garment is made of (presets fabric-*)
const FABRIC = { tshirt: 'jersey', polo: 'jersey', sweater: 'fineknit', oversized: 'heavyjersey', dress: 'poplin', skirt: 'suiting', pants: 'twill', shorts: 'twill', boots: 'suiting', flats: 'suiting', hood: 'heavyjersey', turtleneck: 'fineknit' };
const outfitOf = CH => [...CH.outfit.map(([g, color]) => ({ id: g, kind: 'garment', pattern: `mh-${g}`, fabric: `fabric-${FABRIC[g]}` + PIN, color })),
  ...(CH.extras || []).filter(([kind]) => CLOTH.has(kind)).map(([kind, o]) => ({ id: kind, kind: 'garment', pattern: kind, fabric: `fabric-${FABRIC[kind]}` + PIN, color: o.color, ...(o.wide ? { wide: o.wide } : {}), ...(kind === 'hood' ? { strength: HOOD_HOLD } : {}) }))];
// a hood keeps the shell it was drawn as (over the hair, which it does not meet), as firmly as this
const HOOD_HOLD = 0.6;

// shared parts: the expressions every drawn head takes, and the lights
const PRESETS = {
  'expressions-drawn': { group: 'expressions', label: { ru: 'выражения: нарисованное лицо', en: 'expressions: a drawn face' },
    about: { ru: 'Г3 и Г1: моргание (веко над глазом), рот открыт (челюсть сустава Jaw), улыбка (уголки и щёки), брови вверх и вниз; нарисованные черты следуют за кожей и рисуются по выражению', en: 'Г3 and Г1: a blink (the lid over the eye), the mouth open (the Jaw joint), a smile (corners and cheeks), brows up and down; the painted features follow the skin and redraw as the expression asks' },
    expressions: [
      { name: 'blink', label: { ru: 'моргание', en: 'blink' }, mesh: [{ kind: 'lids', amount: 1 }], paint: { close: 1 } },
      { name: 'open', label: { ru: 'рот открыт', en: 'mouth open' }, jaw: 8, paint: { open: 1 } },
      { name: 'smile', label: { ru: 'улыбка', en: 'smile' }, mesh: [{ kind: 'corners', amount: 1 }, { kind: 'cheeks', amount: 1 }], paint: { smile: 1, happy: 1 } },
      { name: 'browsUp', label: { ru: 'брови вверх', en: 'brows up' }, mesh: [{ kind: 'brows', amount: 1 }], paint: { up: 1 } },
      { name: 'browsDown', label: { ru: 'брови вниз', en: 'brows down' }, mesh: [{ kind: 'brows', amount: -0.6 }], paint: { down: 1 } },
    ] },
  'light-toon-form': { group: 'face-light', label: { ru: 'свет: мультяшный, по форме', en: 'light: toon, by the form' },
    about: { ru: 'как у Г3: три мягких тона с контуром, тени лица — от придуманной формы, на лице нет падающих теней', en: "as Г3's: three soft tones with an outline, the face shaded by its designed form, no cast shadows on the face" },
    light: { toon: true, soft: 3, outline: 0.0012, outlineColor: '#2a1e24', design: 1, faceShadows: false } },
  'light-toon': { group: 'face-light', label: { ru: 'свет: мультяшный', en: 'light: toon' },
    about: { ru: 'три мягких тона с контуром, тени лица — от самой сетки', en: 'three soft tones with an outline, the face shaded by its own mesh' },
    light: { toon: true, soft: 3, outline: 0.0012, outlineColor: '#2a1e24', design: 0, faceShadows: true } },
  'light-soft-form': { group: 'face-light', label: { ru: 'свет: мягкий, по форме', en: 'light: soft, by the form' },
    about: { ru: 'обычный свет сцены, но тени лица — от придуманной формы, без падающих теней на лице', en: "the stage's usual light, the face shaded by its designed form, no cast shadows on it" },
    light: { toon: false, design: 1, faceShadows: false } },
  'light-plain': { group: 'face-light', label: { ru: 'свет: обычный', en: 'light: plain' },
    about: { ru: 'обычный свет сцены, как у тел', en: "the stage's usual light, as the bodies have" }, light: { toon: false, design: 0, faceShadows: true } },
};
const PIN = '@000000000000';
// the pictures heads were drawn after, with their landmarks marked on them (pixels; eL the person's left eye), for the
// overlay check (tools/overlay.mjs)
const REFS = { red: { image: 'cartoon-anatomical-2.png', points: { eL: [113, 79], eR: [83, 80], tip: [99, 95], mouth: [102, 105], mL: [107, 103], mR: [97, 104], chin: [102, 115] }, view: { yaw: -0.22, pitch: 0.18 } } };   // pinned by characters.mjs presets / pin
const preset = (id, group, ru, en, aboutRu, aboutEn, content) => save(new URL(`presets/${id}.json`, EN), { format: 'engine/preset', version: 4, id, group, label: { ru, en }, about: { ru: aboutRu, en: aboutEn }, ...content });
for (const [id, p] of Object.entries(PRESETS)) await save(new URL(`presets/${id}.json`, EN), { format: 'engine/preset', version: 4, id, ...p });
for (const [id, CH] of Object.entries(C)) {
  const { form, piece } = formOf(id, CH), [ru, en] = NAMES[id], mouth = CH.face.mouth;
  const marks = { eye: pick(CH.face.eye, ['x', 'y', 'w', 'h']), mouth: mouth.type === 'none' ? { y: -0.8, w: 0.1 } : { y: mouth.y, w: mouth.w, ...(mouth.sag ? { sag: mouth.sag } : {}), ...(mouth.type === 'grin' ? { wide: true, ...(mouth.crooked ? { crooked: mouth.crooked } : {}) } : {}) } };
  const was = WRAPPED.includes(id) && ['red', 'old', 'semi', 'hood'].includes(id) ? 'Г3' : 'Г1', wear = wearOf(CH);
  await preset(`form-${id}`, 'head-form', `форма: ${ru}`, `form: ${en}`, `${was}: голова Anny, обтянутая на придуманную форму из кривых рисунка`, `${was}: Anny's head wrapped onto a form designed from the drawing's curves`, { changes: [{ kind: 'wrap', form, marks, ...(CH.neckSlim ? { neckSlim: CH.neckSlim } : {}) }] });
  await preset(`features-${id}`, 'features', `черты: ${ru}`, `features: ${en}`, `${was}: глаза, брови, рот и пометки — нарисованы на коже`, `${was}: eyes, brows, mouth and marks — painted on the skin`, { features: featuresOf(CH) });
  await preset(`hair-${id}`, 'hair', `волосы: ${ru}`, `hair: ${en}`, 'волосы Г1, как они были нарисованы, — жёсткими кусками на голове, следуют за ней (волосы, что движутся, — этап волос)', "Г1's hair as it was drawn — rigid pieces on the head, following it (hair that moves is the hair stage)", { pieces: hairOf(CH) });
  if (wear.length) await preset(`wear-${id}`, 'headwear', `убор: ${ru}`, `headwear: ${en}`, 'головной убор, как нарисован, — грубой оболочкой на голове (одеждой, что не проходит сквозь тело, он станет на этапе одежды)', 'the headwear as it was drawn — a coarse shell on the head (the clothes stage makes it a garment that does not go through the body)', { pieces: wear });
  await preset(`outfit-${id}`, 'outfit', `наряд: ${ru}`, `outfit: ${en}`, `${was}: что надето, как нарисовано, — тканью (вещи MakeHuman${(CH.extras || []).some(([k]) => CLOTH.has(k)) ? ', капюшон или ворот' : ''})`, `${was}: what it was drawn wearing — as cloth (MakeHuman's garments${(CH.extras || []).some(([k]) => CLOTH.has(k)) ? ', a hood or a collar' : ''})`, { clothes: outfitOf(CH) });
  const head = {
    size: CH.hs ?? HEAD_SIZE, skin: CH.skin,
    form: [{ kind: 'preset', id: `form-${id}` + PIN }],
    features: [{ kind: 'preset', id: `features-${id}` + PIN }], expressions: [{ kind: 'preset', id: 'expressions-drawn' + PIN }],
    pieces: [...(piece ? [{ id: 'nose', kind: 'nose' }] : []), { kind: 'preset', id: `hair-${id}` + PIN }, ...(wear.length ? [{ kind: 'preset', id: `wear-${id}` + PIN }] : [])],
    light: { kind: 'preset', id: 'light-toon-form' + PIN },
    ...(REFS[id] ? { ref: REFS[id] } : {}),
  };
  await preset(`head-${id}`, 'head', `голова: ${ru}`, `head: ${en}`, `${was}: голова Anny, обтянутая на придуманную форму из кривых рисунка; черты нарисованы на коже; волосы Г1 — жёсткими кусками на голове`, `${was}: Anny's head wrapped onto a form designed from the drawing's curves; features painted on the skin; Г1's hair as rigid pieces on the head`, { head });
  await save(new URL(`characters/head-${id}.json`, EN), { format: 'engine/character', version: 5, id: `head-${id}`, label: { ru: `Голова: ${ru}`, en: `Head: ${en}` },
    body: BODY[CH.who] + PIN, head: { preset: `head-${id}` + PIN }, clothes: [{ kind: 'preset', id: `outfit-${id}` + PIN }], look: { skin: CH.skin, roughness: 0.65 } });
  console.log(`head-${id} (${was}, on ${BODY[CH.who]})`);
}

// —— Г2: a solid fitted to a picture (experiments/heads-mesh/py/chars.py: Giulia's), as a way of the form — not as a
// ready head: wrapped this way it keeps a crease at the throat and reads rougher than Г2's own build ——
const G2 = JSON.parse(execFileSync('python3', ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from chars import CH; print(json.dumps(CH))', fileURLToPath(new URL('experiments/heads-mesh/py', ROOT))], { encoding: 'utf8' }));
{
  const P = G2.giulia, e = P.eye, L = P.lips;
  const form = { kind: 'solid', size: P.size ?? 1, cranium: { at: P.cranium.c, r: P.cranium.r }, face: { ...pick(P.face, ['n', 'W', 'Z', 'D', 'B', 'top', 'topK', 'chinZ', 'jaw', 'chinK', 'chinFrontY']) },
    eye: pick(P.eye, ['x', 'y', 'z', 'r', 'skin', 'k']), nose: pick(P.nose, ['root', 'mid', 'tip', 'sub', 'rRoot', 'rMid', 'rTip', 'rSub', 'tipW', 'tipH', 'kTip', 'k']),
    lips: pick(P.lips, ['y', 'w', 'uh', 'lh', 'ud', 'ld', 'lw', 'depth', 'k', 'smile', 'groove', 'corner']),
    masses: (P.masses || []).map(m => ({ at: m.c, r: m.r, ...(m.k != null ? { k: m.k } : {}), ...(m.pair ? { mirror: true } : {}) })), ear: P.ear, ...(P.kCF != null ? { kCF: P.kCF } : {}),
    ...(P.neckR || P.neckK ? { neck: { ...(P.neckR ? { r: P.neckR } : {}), ...(P.neckK ? { k: P.neckK } : {}) } } : {}) };
  const marks = { eye: { x: e.x, y: e.y, w: e.outX - e.inX, h: e.up + e.lo }, mouth: { y: L.y, w: 2 * L.w * (L.corner ?? 0.92) } };
  await save(new URL('presets/form-solid-giulia.json', EN), { format: 'engine/preset', version: 4, id: 'form-solid-giulia', group: 'head-form', label: { ru: 'форма: тело по картинке (Джулия, Г2)', en: 'form: a solid fitted to a picture (Giulia, Г2)' },
    about: { ru: 'Г2: голова Anny, обтянутая на тело, подогнанное к картинке Джулии (её числа из картинки), без шеи тоньше; на горле остаётся складка — пример способа, не готовая голова', en: "Г2: Anny's head wrapped onto a solid fitted to Giulia's picture (its numbers read off the picture), the neck not slimmed; a crease stays at the throat — an example of the way, not a ready head" },
    changes: [{ kind: 'wrap', form, marks, neckSlim: 1, onto: [0.02, 0.17] }] });
  console.log('form-solid-giulia (Г2)');
}
