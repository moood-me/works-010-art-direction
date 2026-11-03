// The engine's own viewer: characters in Kimodo's motions, travelling along Kimodo's path over a floor with a metre
// grid, their paths drawn on it; chains joined where Kimodo joined them. Several figures at once, side by side: the
// panel edits the chosen one. Everything comes from the engine's data by id.
// URL: ?c=<character>[,<character>…]&m=<motion or chain id>&t=<frame>&paused&follow=0 — and window.__viewer for tools.
import * as THREE from 'three';
import { createEngine } from '../src/engine.js';
import { makeStage, figureView, joinBounds } from '../src/view3d.js';
import { resolve } from '../src/character.js';

const q = new URLSearchParams(location.search);
const msg = document.getElementById('msg'), canvas = document.getElementById('cv');
const E = await createEngine();
const [chars, motions] = await Promise.all([E.characters(), E.motions()]);
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
const cam = { yaw: 0.55, pitch: 0.1, dist: 4.6, target: [0, 0.85, 0] };
let clip = null;

// ———— the panel ————
const panel = document.createElement('div'); panel.id = 'vpPanel';
panel.innerHTML = `
  <div class="row"><span class="lab">Фигуры</span><span class="mv" id="figs"></span><button id="add" title="ещё фигура рядом">＋</button><button id="del" title="убрать выбранную">✕</button></div>
  <div class="row"><span class="lab">Тело</span><select id="char" aria-label="Тело"></select></div>
  <div class="row"><span class="lab">Движение</span></div><div class="mv" id="moves"></div>
  <div class="row"><button id="play" aria-label="Пауза">❚❚</button><input id="time" type="range" min="0" max="0" step="0.01" value="0" aria-label="Время"><span id="flab"></span></div>
  <div class="row"><span class="lab">Камера</span><button id="follow">следует</button><button data-view="front">спереди</button><button data-view="side">сбоку</button><button id="joints">суставы</button><button id="capsules">капсулы</button></div>
  <div class="sep"></div>
  <div class="row"><span class="lab">Скиннинг</span><button data-method="cor">центры вращения</button><button data-method="dqs">двойные кватернионы</button><button data-method="lbs">линейный</button></div>
  <div class="row"><span class="lab">Т7</span><button id="clav">ключица ⅓</button><button id="seam">шов сглажен</button></div>
  <div class="row"><span class="lab">Слои позы</span><span class="mv" id="layers"></span></div>
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
  figs.forEach((g, i) => { const b = addBtn($('#figs'), String(i), `${i + 1}. ${label(g.char)}`, () => { S.cur = i; press(); }); b.setAttribute('aria-pressed', String(i === S.cur)); });
  $('#del').disabled = figs.length < 2;
  panel.querySelectorAll('#moves button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.id === S.clip)));
  panel.querySelectorAll('[data-method]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.method === spec.skinning.method)));
  panel.querySelectorAll('#layers button').forEach(b => b.setAttribute('aria-pressed', String(spec.pose.some(l => l.kind === b.dataset.id))));
  $('#clav').setAttribute('aria-pressed', String(spec.pose.some(l => l.kind === 'clavicleShare')));
  $('#seam').setAttribute('aria-pressed', String(!!spec.skinning.seam));
  for (const k of ['follow', 'joints', 'capsules']) $('#' + k).setAttribute('aria-pressed', String(S[k]));
  $('#play').textContent = S.playing ? '❚❚' : '▶';
  $('#char').value = f.char;
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
  return resolve(d, E.skeleton);
}
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
  for (const i of which) await build(figs[i], i);
  await setClip(S.clip, true);
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
