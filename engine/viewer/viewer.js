// The engine's own viewer: a character in Kimodo's motions, travelling along Kimodo's path over a floor with a metre
// grid, the path drawn on it; chains joined where Kimodo joined them. Everything comes from the engine's data by id.
// URL: ?c=<character>&m=<motion or chain id>&t=<frame>&paused&follow=0 — and window.__viewer for tools (pictures).
import * as THREE from 'three';
import { createEngine } from '../src/engine.js';
import { makeStage, figureMesh } from '../src/view3d.js';
import { resolve } from '../src/character.js';

const q = new URLSearchParams(location.search);
const msg = document.getElementById('msg'), canvas = document.getElementById('cv');
const E = await createEngine();
const [chars, motions] = await Promise.all([E.characters(), E.motions()]);
const stage = makeStage(THREE, canvas, { pixelRatio: Math.min(devicePixelRatio || 1, 2) });
// the figure in the middle of what the panel leaves free (on a wide screen)
const fit = () => { const p = document.getElementById('vpPanel'), w = p && innerWidth > 760 ? p.offsetWidth + 12 : 0; stage.size(innerWidth, innerHeight, w / 2); };
addEventListener('resize', fit); fit();

// what plays: a motion, or a chain (motions/index.json)
const CLIPS = [...motions.motions.filter(m => !m.after).map(m => ({ id: m.id, label: m.label.ru, ids: [m.id] })),
  ...motions.chains.map(c => ({ id: c.id, label: c.label.ru, ids: c.motions, chain: true }))];
const CORR = [['armsOff', 'руки от тела', { degrees: 7 }], ['armsOutOfHead', 'руки из головы', { margin: 0.02 }],
  ['amplifyLimbs', 'размах конечностей', { factor: 1.3 }], ['dampHeadSpine', 'тише голова и спина', { spine: 0.7, head: 0.7 }]];

const S = { char: q.get('c') || chars.characters[0].id, clip: q.get('m') ?? 'walk', t: +(q.get('t') || 0), playing: !q.has('paused'),
  follow: q.get('follow') !== '0', joints: false, method: null, clav: null, seam: null, corr: {} };
const cam = { yaw: 0.55, pitch: 0.1, dist: 4.6, target: [0, 0.85, 0] };
let fig = null, view = null, clip = null, base = null;

// ———— the panel ————
const panel = document.createElement('div'); panel.id = 'vpPanel';
panel.innerHTML = `
  <div class="row"><span class="lab">Тело</span><select id="char" aria-label="Тело"></select></div>
  <div class="row"><span class="lab">Движение</span></div><div class="mv" id="moves"></div>
  <div class="row"><button id="play" aria-label="Пауза">❚❚</button><input id="time" type="range" min="0" max="0" step="0.01" value="0" aria-label="Время"><span id="flab"></span></div>
  <div class="row"><span class="lab">Камера</span><button id="follow">следует</button><button data-view="front">спереди</button><button data-view="side">сбоку</button><button id="joints">суставы</button></div>
  <div class="sep"></div>
  <div class="row"><span class="lab">Скиннинг</span><button data-method="cor">центры вращения</button><button data-method="dqs">двойные кватернионы</button><button data-method="lbs">линейный</button></div>
  <div class="row"><span class="lab">Т7</span><button id="clav">ключица ⅓</button><button id="seam">шов сглажен</button></div>
  <div class="row"><span class="lab">Поправки</span><span class="mv" id="corr"></span></div>
  <div class="hint">мышь: вращать · колесо: ближе · Shift или правая кнопка: сдвинуть</div>`;
const $ = s => panel.querySelector(s);
for (const c of chars.characters) { const o = document.createElement('option'); o.value = c.id; o.textContent = c.label.ru; $('#char').appendChild(o); }
const addBtn = (box, id, label, on) => { const b = document.createElement('button'); b.textContent = label; b.dataset.id = id; b.onclick = on; box.appendChild(b); return b; };
addBtn($('#moves'), '', 'покой', () => setClip(''));
for (const c of CLIPS) addBtn($('#moves'), c.id, (c.chain ? '⛓ ' : '') + c.label, () => setClip(c.id));
for (const [id, label] of CORR) addBtn($('#corr'), id, label, () => { S.corr[id] = !S.corr[id]; rebuild(); });

function press() {
  panel.querySelectorAll('#moves button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.id === S.clip)));
  panel.querySelectorAll('[data-method]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.method === fig.spec.skinning.method)));
  panel.querySelectorAll('#corr button').forEach(b => b.setAttribute('aria-pressed', String(!!fig.spec.motion.corrections[b.dataset.id])));
  $('#clav').setAttribute('aria-pressed', String(fig.spec.skinning.clavicleShare > 0));
  $('#seam').setAttribute('aria-pressed', String(!!fig.spec.skinning.seam));
  $('#follow').setAttribute('aria-pressed', String(S.follow));
  $('#joints').setAttribute('aria-pressed', String(S.joints));
  $('#play').textContent = S.playing ? '❚❚' : '▶';
  $('#char').value = S.char;
}

// the character as described, with what the panel changed over it
async function rebuild() {
  msg.style.display = 'grid'; await new Promise(r => setTimeout(r, 20));
  base = await E.character(S.char);
  const sk = { ...base.skinning };
  if (S.method) sk.method = S.method;
  if (S.clav != null) sk.clavicleShare = S.clav ? 1 / 3 : 0;
  if (S.seam != null) sk.seam = S.seam ? { iterations: 10, rings: 3 } : null;
  const corr = { ...base.motion.corrections };
  for (const [id, , prm] of CORR) if (S.corr[id] != null) { if (S.corr[id]) corr[id] = corr[id] || prm; else delete corr[id]; }
  const spec = resolve({ format: 'engine/character', version: base.version, id: base.id, label: base.label, body: base.body, skinning: sk, motion: { ...base.motion, corrections: corr }, look: base.look });
  const f = await E.figure(spec);
  if (view) { stage.scene.remove(view.mesh, view.dots); view.dispose(); }
  fig = f; view = figureMesh(THREE, fig, spec.look); view.dots.visible = S.joints;
  stage.scene.add(view.mesh, view.dots);
  await setClip(S.clip, true);
  msg.style.display = 'none';
}

async function setClip(id, keepTime) {
  S.clip = id;
  const c = CLIPS.find(x => x.id === id);
  clip = c ? await E.clip(c.ids) : null;
  if (!keepTime) S.t = 0;
  $('#time').max = clip ? clip.frames - 1 : 0;
  if (clip) {
    const path = fig.path(clip, 1), marks = clip.joins.map(g => path[Math.min(path.length - 1, g)]);
    stage.showPath(path, marks);
  } else stage.showPath([], []);
  const h = fig.body.measures.height;
  cam.dist = Math.max(2.2, h * 2.9);
  draw(true);
  press();
}

function draw(snap) {
  fig.frame(clip, S.t); view.update();
  const P = fig.pose.P, h = fig.body.measures.height, want = [P[0], fig.pose.floor + h * 0.52, P[2]];
  if (S.follow || snap) for (let k = 0; k < 3; k++) cam.target[k] = snap ? want[k] : cam.target[k] + (want[k] - cam.target[k]) * 0.15;
  stage.light([P[0], 0, P[2]]);
  $('#time').value = S.t; $('#flab').textContent = clip ? `${Math.floor(S.t)}/${clip.frames - 1}` + (clip.joins.length ? ` · стык ${clip.joins.join(', ')}` : '') : '';
}

// ———— input ————
$('#char').onchange = () => { S.char = $('#char').value; S.method = S.clav = S.seam = null; S.corr = {}; rebuild(); };
$('#play').onclick = () => { S.playing = !S.playing; press(); };
$('#time').oninput = () => { S.t = +$('#time').value; S.playing = false; press(); draw(); };
$('#follow').onclick = () => { S.follow = !S.follow; press(); };
$('#joints').onclick = () => { S.joints = !S.joints; view.dots.visible = S.joints; press(); draw(); };
panel.querySelectorAll('[data-method]').forEach(b => b.onclick = () => { S.method = b.dataset.method; rebuild(); });
$('#clav').onclick = () => { S.clav = !(fig.spec.skinning.clavicleShare > 0); rebuild(); };
$('#seam').onclick = () => { S.seam = !fig.spec.skinning.seam; rebuild(); };
// front and side: from where the figure faces now (its hips' line, turned a quarter)
const facing = () => { const sk = fig.body.skeleton, P = fig.pose.P, l = sk.index.LeftLeg * 3, r = sk.index.RightLeg * 3; return Math.atan2(-(P[l + 2] - P[r + 2]), P[l] - P[r]); };
panel.querySelectorAll('[data-view]').forEach(b => b.onclick = () => { cam.yaw = facing() + (b.dataset.view === 'side' ? Math.PI / 2 : 0); cam.pitch = 0.06; });

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
document.body.appendChild(panel); press(); fit();
window.__viewer = {
  E, S, cam, stage, get fig() { return fig; }, get clip() { return clip; }, facing,
  async set(o) { Object.assign(S, o); if ('char' in o || 'method' in o || 'clav' in o || 'seam' in o || 'corr' in o) await rebuild(); else if ('clip' in o) await setClip(S.clip, 't' in o);
    view.dots.visible = S.joints; draw(true); press(); },
  render() { draw(false); stage.look(cam.target, cam); stage.render(); },
};
let last = performance.now();
(function loop(now) {
  const dt = Math.min(0.1, (now - last) / 1000); last = now;
  if (clip && S.playing) { S.t += dt * clip.fps; const wrap = S.t > clip.frames - 1; if (wrap) S.t = 0; draw(wrap); }
  stage.look(cam.target, cam); stage.render();
  requestAnimationFrame(loop);
})(last);
