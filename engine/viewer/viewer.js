// The engine's own viewer: characters in Kimodo's motions, travelling along Kimodo's path over a floor with a metre
// grid, their paths drawn on it; chains joined where Kimodo joined them. Several figures at once, side by side: the
// panel edits the chosen one. Everything comes from the engine's data by id.
// URL: ?c=<character>[,<character>…]&m=<motion or chain id>&t=<frame>&paused&follow=0 — and window.__viewer for tools.
// ?bodies adds the bodies' panel (stage 1): the base body of the chosen figure, and its deformers — each a preset with
// its strength, on the rest (its frames kept or turned) or as a pose layer — added, changed, taken away; &b=<body id>
// sets the base body, &d=<preset>:<strength>[:pose],… the deformers.
import * as THREE from 'three';
import { createEngine } from '../src/engine.js';
import { makeStage, figureView, joinBounds } from '../src/view3d.js';

const q = new URLSearchParams(location.search);
const msg = document.getElementById('msg'), canvas = document.getElementById('cv');
const E = await createEngine();
const [chars, motions] = await Promise.all([E.characters(), E.motions()]);
const BODIES = q.has('bodies');
if (BODIES) document.body.classList.add('bodies');
const [bodyIndex, presetIndex] = BODIES ? await Promise.all([E.bodies(), E.presets()]) : [null, null];
const presetOf = ref => presetIndex.presets.find(p => p.id === ref.split('@')[0]);
// presets whose changes give their own skin weights (the pictograms) are changes of the rest only
const REST_ONLY = new Set(['pictogram']);
const stage = makeStage(THREE, canvas, { pixelRatio: Math.min(devicePixelRatio || 1, 2) });
// the figures in the middle of what the panel leaves free (on a wide screen)
const fit = () => { const p = document.getElementById('vpPanel'), w = p && innerWidth > 760 ? p.offsetWidth + 12 : 0; stage.size(innerWidth, innerHeight, w / 2); };
addEventListener('resize', fit); fit();

// what plays: a motion, or a chain (motions/index.json)
const CLIPS = [...motions.motions.filter(m => !m.after).map(m => ({ id: m.id, label: m.label.ru })),
  ...motions.chains.map(c => ({ id: c.id, label: c.label.ru, chain: true }))];
const LAYERS = [['armsOff', 'руки от тела'], ['armsOutOfHead', 'руки из головы'], ['amplifyLimbs', 'размах конечностей'], ['dampHeadSpine', 'тише голова и спина']];
const SPACING = 0.9;   // metres between figures side by side

const S = { clip: q.get('m') ?? 'walk', t: +(q.get('t') || 0), playing: !q.has('paused'), follow: q.get('follow') !== '0', joints: false, capsules: false, cur: 0 };
// each figure: its character and what the panel changed over its description
const figs = (q.get('c') || chars.characters[0].id).split(',').map(char => ({ char, over: {} }));
if (BODIES && q.get('b')) { const b = bodyIndex.bodies.find(b => b.id === q.get('b')); if (!b) throw new Error(`no body ${q.get('b')}`); figs[0].over.body = b.pin; }
if (BODIES && q.has('d')) figs[0].over.rows = q.get('d').split(',').filter(Boolean).map(s => {
  const [id, k = '1', where = 'rest'] = s.split(':'), p = presetIndex.presets.find(p => p.id === id); if (!p) throw new Error(`no preset ${id}`);
  return { where, c: { kind: 'preset', id: p.pin, strength: +k }, frames: 'keep' };
});
const cam = { yaw: 0.55, pitch: 0.1, dist: 4.6, target: [0, 0.85, 0] };
let clip = null;

// ———— the panel ————
const panel = document.createElement('div'); panel.id = 'vpPanel';
panel.innerHTML = `
  <div class="row"><span class="lab">Фигуры</span><span class="mv" id="figs"></span><button id="add" title="ещё фигура рядом">＋</button><button id="del" title="убрать выбранную">✕</button></div>
  <div class="row"><span class="lab">Персонаж</span><select id="char" aria-label="Персонаж" title="описание персонажа (characters/): тело, его изменения, слои позы, вид"></select></div>
  <div class="row"><span class="lab">Движение</span></div><div class="mv" id="moves"></div>
  <div class="row"><button id="play" aria-label="Пауза">❚❚</button><input id="time" type="range" min="0" max="0" step="0.01" value="0" aria-label="Время"><span id="flab"></span></div>
  <div class="row"><span class="lab">Камера</span><button id="follow">следует</button><button data-view="front">спереди</button><button data-view="side">сбоку</button><button id="joints">суставы</button><button id="capsules">капсулы</button></div>
  <details id="skin"${BODIES ? '' : ' open'}><summary>Скиннинг и слои позы</summary>
  <div class="row"><span class="lab">Скиннинг</span><button data-method="cor">центры вращения</button><button data-method="dqs">двойные кватернионы</button><button data-method="lbs">линейный</button></div>
  <div class="row"><span class="lab">Т7</span><button id="clav">ключица ⅓</button><button id="seam">шов сглажен</button></div>
  <div class="row"><span class="lab">Слои позы</span><span class="mv" id="layers"></span></div>
  </details>
  ${BODIES ? `<div class="sep"></div>
  <div class="row"><span class="lab">Тело-основа</span><select id="base" aria-label="Тело-основа" title="тело Anny, с которого персонаж начинается (data/bodies/)"></select></div>
  <div class="row"><span class="lab">Деформеры</span><span class="hint">по порядку; сила, покой или слой позы</span></div>
  <div id="defs" style="display:grid;gap:4px"></div>
  <div class="row"><select id="addDef" aria-label="Добавить деформер"></select></div>` : ''}
  <div class="hint">мышь: вращать · колесо: ближе · Shift или правая кнопка: сдвинуть</div>`;
const $ = s => panel.querySelector(s);
for (const c of chars.characters) { const o = document.createElement('option'); o.value = c.id; o.textContent = c.label.ru; $('#char').appendChild(o); }
const addBtn = (box, id, label, on) => { const b = document.createElement('button'); b.textContent = label; b.dataset.id = id; b.onclick = on; box.appendChild(b); return b; };
addBtn($('#moves'), '', 'покой', () => setClip(''));
for (const c of CLIPS) addBtn($('#moves'), c.id, (c.chain ? '⛓ ' : '') + c.label, () => setClip(c.id));
for (const [id, label] of LAYERS) addBtn($('#layers'), id, label, () => toggleLayer(id));

const cur = () => figs[S.cur];
const label = id => chars.characters.find(c => c.id === id)?.label.ru ?? id;
function press() {
  const f = cur(), spec = f.spec;
  $('#figs').innerHTML = '';
  figs.forEach((g, i) => { const b = addBtn($('#figs'), String(i), `${i + 1}. ${label(g.char)}`, () => { S.cur = i; press(); showRows(); }); b.setAttribute('aria-pressed', String(i === S.cur)); });
  $('#del').disabled = figs.length < 2;
  panel.querySelectorAll('#moves button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.id === S.clip)));
  panel.querySelectorAll('[data-method]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.method === spec.skinning.method)));
  panel.querySelectorAll('#layers button').forEach(b => b.setAttribute('aria-pressed', String(spec.pose.some(l => l.kind === b.dataset.id))));
  $('#clav').setAttribute('aria-pressed', String(spec.pose.some(l => l.kind === 'clavicleShare')));
  $('#seam').setAttribute('aria-pressed', String(!!spec.skinning.seam));
  for (const k of ['follow', 'joints', 'capsules']) $('#' + k).setAttribute('aria-pressed', String(S[k]));
  $('#play').textContent = S.playing ? '❚❚' : '▶';
  $('#char').value = f.char;
  if (BODIES && f.spec) $('#base').value = pinnedId(f.spec.body);
}

// a figure's description with what the panel changed over it — checked like any description
async function describe(f) {
  const d = structuredClone(await E.description(f.char)), o = f.over;
  if (o.method) d.skinning = { ...d.skinning, method: o.method };
  if (o.seam != null) d.skinning = { ...d.skinning, seam: o.seam ? {} : null };
  for (const [kind, on] of Object.entries(o.layers || {})) {
    d.pose = (d.pose || []).filter(l => l.kind !== kind);
    if (on) d.pose.push({ kind });
  }
  if (o.body) d.body = o.body;
  if (o.rows) {
    d.rest = o.rows.filter(r => r.where === 'rest').map(r => ({ ...r.c, frames: r.frames }));
    d.pose = [...(d.pose || []).filter(l => !isDeform(l)), ...o.rows.filter(r => r.where === 'pose').map(r => { const c = { ...r.c }; delete c.frames; return c; })];
  }
  return E.resolve(d);
}
const isDeform = l => l.kind === 'preset' || !['armsOff', 'armsOutOfHead', 'amplifyLimbs', 'dampHeadSpine', 'clavicleShare', 'turn', 'morph'].includes(l.kind);
// the figure's deformers as the panel's rows: its rest's, then its pose layers' that are deformers
async function rowsOf(f) {
  if (f.over.rows) return f.over.rows;
  const d = await E.description(f.char);
  return (f.over.rows = [...(d.rest || []).map(c => ({ where: 'rest', c, frames: c.frames ?? 'keep' })), ...(d.pose || []).filter(isDeform).map(c => ({ where: 'pose', c, frames: 'keep' }))]);
}
const rowLabel = c => c.kind === 'preset' ? (presetOf(c.id)?.label.ru ?? c.id) : c.kind;
async function showRows() {
  if (!BODIES) return;
  const f = cur(), rows = await rowsOf(f), box = $('#defs');
  box.innerHTML = '';
  rows.forEach((r, k) => {
    const el = document.createElement('div'); el.className = 'row';
    const g = r.c.kind === 'preset' ? presetOf(r.c.id)?.group : null, restOnly = REST_ONLY.has(g) || ['sign', 'turn', 'morph'].includes(r.c.kind);
    el.innerHTML = `<span title="${r.c.kind === 'preset' ? (presetOf(r.c.id)?.about?.ru ?? '') : ''}">${rowLabel(r.c)}</span><input type="range" min="0" max="2" step="0.05" value="${r.c.strength ?? 1}" aria-label="сила"><span class="s">${(r.c.strength ?? 1).toFixed(2)}</span>
      <button class="w" title="на покое или слоем позы"${restOnly ? ' disabled' : ''}>${r.where === 'rest' ? 'покой' : 'слой'}</button>${r.where === 'rest' ? `<button class="fr" title="кадры суставов: держать (форма едет в движении) или повернуть (анатомия)">${r.frames === 'keep' ? 'держать' : 'повернуть'}</button>` : ''}<button class="x" title="убрать">✕</button>`;
    const range = el.querySelector('input');
    range.oninput = () => { el.querySelector('.s').textContent = (+range.value).toFixed(2); };
    range.onchange = () => { r.c = { ...r.c, strength: +range.value }; rebuild([S.cur]); };
    el.querySelector('.w').onclick = () => { r.where = r.where === 'rest' ? 'pose' : 'rest'; rebuild([S.cur]); };
    el.querySelector('.fr')?.addEventListener('click', () => { r.frames = r.frames === 'keep' ? 'turn' : 'keep'; rebuild([S.cur]); });
    el.querySelector('.x').onclick = () => { rows.splice(k, 1); rebuild([S.cur]); };
    box.appendChild(el);
  });
  $('#base').value = pinnedId(f.spec.body);
}
const pinnedId = ref => ref.split('@')[0];
async function build(f, i) {
  f.spec = await describe(f);
  const fig = await E.figure(f.spec, { place: { position: [i * SPACING, 0, 0], heading: 0 } });
  if (f.view) { stage.scene.remove(f.view.group); f.view.dispose(); }
  f.fig = fig; f.view = figureView(THREE, fig, f.spec.look);
  f.view.dots.visible = S.joints; f.view.caps.visible = S.capsules;
  stage.scene.add(f.view.group);
}
async function rebuild(which = figs.map((_, i) => i)) {
  msg.style.display = 'grid'; await new Promise(r => setTimeout(r, 20));
  try { for (const i of which) await build(figs[i], i); }
  catch (e) { msg.textContent = 'не собралось: ' + e.message; throw e; }
  await setClip(S.clip, true);
  await showRows();
  msg.style.display = 'none';
}
function toggleLayer(kind) {
  const f = cur(); f.over.layers = { ...(f.over.layers || {}), [kind]: !f.spec.pose.some(l => l.kind === kind) };
  rebuild([S.cur]);
}

async function setClip(id, keepTime) {
  S.clip = id;
  clip = id ? await E.clip(id) : null;
  if (!keepTime) S.t = 0;
  $('#time').max = clip ? clip.frames - 1 : 0;
  stage.showPaths(clip ? figs.map(f => { const path = f.fig.path(clip, 1); return { points: path, marks: clip.joins.map(j => path[Math.min(path.length - 1, j.at)]) }; }) : []);
  for (const f of figs) f.fig.reset();
  draw(true);
  press();
}

const bounds = () => joinBounds(figs.map(f => f.fig.bounds()));
function draw(snap) {
  for (const f of figs) { f.fig.step(clip, S.t); f.view.update(); }
  const b = bounds();
  if (snap) cam.dist = stage.fit(b, cam).dist * 1.15;
  if (S.follow || snap) for (let k = 0; k < 3; k++) cam.target[k] = snap ? b.center[k] : cam.target[k] + (b.center[k] - cam.target[k]) * 0.15;
  stage.light(b);
  $('#time').value = S.t; $('#flab').textContent = clip ? `${Math.floor(S.t)}/${clip.frames - 1}` + (clip.joins.length ? ` · стык ${clip.joins.map(j => j.at).join(', ')}` : '') : '';
}

// ———— input ————
$('#char').onchange = () => { const f = cur(); f.char = $('#char').value; f.over = {}; rebuild([S.cur]); };
if (BODIES) {
  for (const g of bodyIndex.groups) {
    const og = document.createElement('optgroup'); og.label = g.label.ru; $('#base').appendChild(og);
    for (const b of bodyIndex.bodies.filter(b => b.group === g.id)) { const o = document.createElement('option'); o.value = b.id; o.textContent = `${b.label.ru} · ${b.height.toFixed(2)} м`; og.appendChild(o); }
  }
  $('#base').onchange = () => { const b = bodyIndex.bodies.find(b => b.id === $('#base').value); cur().over.body = b.pin; rebuild([S.cur]); };
  const add = $('#addDef'); add.innerHTML = '<option value="">＋ добавить деформер…</option>';
  for (const g of presetIndex.groups) {
    const og = document.createElement('optgroup'); og.label = g; add.appendChild(og);
    for (const p of presetIndex.presets.filter(p => p.group === g)) { const o = document.createElement('option'); o.value = p.pin; o.textContent = p.label.ru; o.title = p.about?.ru ?? ''; og.appendChild(o); }
  }
  add.onchange = async () => { if (!add.value) return; (await rowsOf(cur())).push({ where: 'rest', c: { kind: 'preset', id: add.value, strength: 1 }, frames: 'keep' }); add.value = ''; rebuild([S.cur]); };
}
$('#add').onclick = () => { figs.push({ char: cur().char, over: {} }); S.cur = figs.length - 1; rebuild([S.cur]); };
$('#del').onclick = () => {
  if (figs.length < 2) return;
  const [f] = figs.splice(S.cur, 1); stage.scene.remove(f.view.group); f.view.dispose();
  S.cur = Math.min(S.cur, figs.length - 1); rebuild();
};
$('#play').onclick = () => { S.playing = !S.playing; press(); };
$('#time').oninput = () => { S.t = +$('#time').value; S.playing = false; press(); draw(); };
$('#follow').onclick = () => { S.follow = !S.follow; press(); };
$('#joints').onclick = () => { S.joints = !S.joints; for (const f of figs) f.view.dots.visible = S.joints; press(); draw(); };
$('#capsules').onclick = () => { S.capsules = !S.capsules; for (const f of figs) f.view.caps.visible = S.capsules; press(); draw(); };
panel.querySelectorAll('[data-method]').forEach(b => b.onclick = () => { cur().over.method = b.dataset.method; rebuild([S.cur]); });
$('#clav').onclick = () => toggleLayer('clavicleShare');
$('#seam').onclick = () => { const f = cur(); f.over.seam = !f.spec.skinning.seam; rebuild([S.cur]); };
// front and side: from where the chosen figure faces now (its hips' line, turned a quarter)
const facing = (f = cur()) => { const sk = E.skeleton, P = f.fig.pose.P, l = sk.index.LeftLeg * 3, r = sk.index.RightLeg * 3; return Math.atan2(-(P[l + 2] - P[r + 2]), P[l] - P[r]); };
panel.querySelectorAll('[data-view]').forEach(b => b.onclick = () => { cam.yaw = facing() + (b.dataset.view === 'side' ? Math.PI / 2 : 0); cam.pitch = 0.06; cam.dist = stage.fit(bounds(), cam).dist * 1.15; });

let drag = null;
canvas.addEventListener('contextmenu', e => e.preventDefault());
canvas.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY, pan: e.button === 2 || e.shiftKey }; canvas.setPointerCapture(e.pointerId); });
canvas.addEventListener('pointermove', e => {
  if (!drag) return; const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.x = e.clientX; drag.y = e.clientY;
  if (drag.pan) { const s = cam.dist * 0.0012; cam.target[0] -= Math.cos(cam.yaw) * dx * s; cam.target[2] += Math.sin(cam.yaw) * dx * s; cam.target[1] += dy * s; S.follow = false; press(); }
  else { cam.yaw -= dx * 0.007; cam.pitch = Math.max(-0.4, Math.min(1.3, cam.pitch + dy * 0.005)); }
});
canvas.addEventListener('pointerup', () => drag = null); canvas.addEventListener('pointercancel', () => drag = null);
canvas.addEventListener('wheel', e => { e.preventDefault(); cam.dist = Math.max(0.4, Math.min(40, cam.dist * Math.exp(e.deltaY * 0.001))); }, { passive: false });
addEventListener('keydown', e => { if (e.key === ' ' && e.target === document.body) { e.preventDefault(); S.playing = !S.playing; press(); } });

// ———— run ————
await rebuild();
document.body.appendChild(panel); press(); fit(); draw(true);
window.__viewer = {
  E, S, cam, stage, figs, facing, bounds,
  async set(o) { Object.assign(S, o); if ('clip' in o) await setClip(S.clip, 't' in o); draw(true); press(); },
  render() { draw(false); stage.look(cam.target, cam); stage.render(); },
};
let last = performance.now();
(function loop(now) {
  const dt = Math.min(0.1, (now - last) / 1000); last = now;
  if (clip && S.playing) { S.t += dt * clip.fps; const wrap = S.t > clip.frames - 1; if (wrap) S.t = 0; draw(wrap); }
  stage.look(cam.target, cam); stage.render();
  requestAnimationFrame(loop);
})(last);
