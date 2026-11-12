// К2 — the body against things: the back on a wall, the feet on steps and a hand sliding along a rail, the body lying
// on a bed, the forearms on a table while sitting. A copy of К1's page (experiments/contacts/contacts.js), changed:
// the things are boxes written by tools/scenes.py (a box may be tilted about its own x — a rail along a flight of
// stairs), a hand's place may be a line (a rail: the palm on its top wherever along it Kimodo's palm is), and besides
// the hands the page measures "touches" — how near a part of the body (the back, the pelvis, the feet, the forearms)
// is to the face of the thing it rests on, and whether it goes into it.
// URL: ?s=<scene>&t=<frame>&paused&raw (no correction)&lite (a smaller shadow map) — and window.__contacts for tools (pictures, numbers).
import * as THREE from 'three';
import { createEngine } from '../../engine/src/engine.js';
import { loadMotion, clipOf } from '../../engine/src/motion.js';
import { makeStage, figureMesh } from '../../engine/src/view3d.js';
import { readJSON } from '../../engine/src/pack.js';
import { qRot, qAxisAngle, sub, add, scale, dot, len, clamp } from '../../engine/src/math.js';
import { ContactFigure } from './contact-figure.js';

const here = new URL('./', import.meta.url);
const q = new URLSearchParams(location.search);
const msg = document.getElementById('msg'), canvas = document.getElementById('cv');
const E = await createEngine();
const SC = await readJSON(new URL('scenes.json', here));
const stage = makeStage(THREE, canvas, { pixelRatio: Math.min(devicePixelRatio || 1, 2) });
Object.assign(stage.key.shadow.camera, { left: -5, right: 5, top: 5, bottom: -3, far: 20 }); stage.key.shadow.camera.updateProjectionMatrix();
// (?lite: a smaller shadow map — for the headless pictures, where software WebGL draws a 4096² one slowly)
stage.key.shadow.mapSize.set(...(q.has('lite') ? [1024, 1024] : [4096, 4096]));
const fit = () => { const p = document.getElementById('panel'), w = p && innerWidth > 760 ? p.offsetWidth + 12 : 0; stage.size(innerWidth, innerHeight, w / 2); };
addEventListener('resize', fit); fit();

const S = { scene: q.get('s') || SC.scenes[0].id, t: +(q.get('t') || 0), playing: !q.has('paused'), correct: !q.has('raw'), marks: true, follow: false };
const cam = { yaw: 0.9, pitch: 0.18, dist: 4.4, target: [0, 0.8, 0] };
let cur = null;

// ———— things: a thing {kind, at, heading, boxes: [{c, s, part, rx?}]} — boxes in the thing's frame (x across, y up,
// z ahead), a box tilted by rx about its own x through its centre ————
const turnY = (h, v) => qRot(qAxisAngle([0, 1, 0], h), v);
function toLocal(p, x) { return turnY(-p.heading, sub(x, p.at)); }
function inBox(b, xl) {           // a point of the thing's frame in the box's own frame
  let d = sub(xl, b.c);
  if (b.rx) d = qRot(qAxisAngle([1, 0, 0], -b.rx), d);
  return d;
}
// signed distance from a point (thing's frame) to a box: > 0 outside (how far), < 0 inside (how deep)
function boxDistance(b, xl) {
  const d = inBox(b, xl);
  const o = [0, 1, 2].map(k => Math.abs(d[k]) - b.s[k] / 2);
  const out = Math.hypot(Math.max(o[0], 0), Math.max(o[1], 0), Math.max(o[2], 0));
  return out > 0 ? out : Math.max(o[0], o[1], o[2]);
}

const MAT = {
  wood: { color: '#8a6a4f', roughness: 0.8 }, cloth: { color: '#6f7f6a', roughness: 0.95 }, wall: { color: '#e6dfd3', roughness: 0.95 },
  stone: { color: '#b9b1a5', roughness: 0.9 }, metal: { color: '#5b5650', roughness: 0.4, metalness: 0.5 }, sheet: { color: '#d9d4ca', roughness: 0.95 },
};
function propMesh(p) {
  const g = new THREE.Group();
  for (const b of p.boxes) {
    const mat = new THREE.MeshStandardMaterial(MAT[b.mat || 'wood']);
    const geo = b.round ? new THREE.CylinderGeometry(b.s[0] / 2, b.s[0] / 2, b.s[2], 16).rotateX(Math.PI / 2) : new THREE.BoxGeometry(...b.s);
    const m = new THREE.Mesh(geo, mat);
    m.position.set(...b.c); if (b.rx) m.rotation.x = b.rx;
    m.castShadow = m.receiveShadow = true; g.add(m);
  }
  g.position.set(...p.at); g.rotation.y = p.heading;
  return g;
}

// ———— the scene ————
async function figureOf(who) {
  const spec = await E.character(who.character);
  const body = await E.body(spec.body);
  const fig = new ContactFigure(body, spec, who.place);
  const motions = await Promise.all(who.motions.map(id => loadMotion(new URL(`motions/${id}.json`, here), E.skeleton)));
  const clip = clipOf(motions);
  const view = figureMesh(THREE, fig, spec.look);
  // each vertex's body part (the one it belongs to most)
  const PN = body.parts.names, NP = PN.length, partOf = new Array(body.N);
  for (let i = 0; i < body.N; i++) { let best = -1, bk = 0; for (let k = 0; k < NP; k++) { const w = body.parts.weights[i * NP + k]; if (w > best) { best = w; bk = k; } } partOf[i] = PN[bk]; }
  const ofParts = names => { const out = []; for (let i = 0; i < body.N; i++) if (names.includes(partOf[i])) out.push(i); return out; };
  const hands = { Left: ofParts(['Lhand']), Right: ofParts(['Rhand']) };
  return { fig, clip, view, hands, who, partOf, ofParts };
}

const smooth = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);
// a contact's weight over time: in over `ramp` frames before `from`, held, out over `ramp` after `to`
const weightOf = c => t => smooth((t - (c.frames[0] - c.ramp)) / c.ramp) * (c.frames[1] >= 1e8 ? 1 : 1 - smooth((t - c.frames[1]) / c.ramp));

async function setScene(id) {
  msg.style.display = 'grid'; await new Promise(r => setTimeout(r, 20));
  if (cur) { for (const o of cur.objects) stage.scene.remove(o); cur.A.view.dispose(); }
  const scene = SC.scenes.find(s => s.id === id);
  S.scene = id;
  const A = await figureOf(scene.person);
  const objects = [A.view.mesh];
  const props = scene.props;
  for (const p of props) objects.push(propMesh(p));
  const marks = new THREE.Group(); objects.push(marks);
  A.fig.contacts = scene.contacts.map(c => {
    const k = { side: c.side, def: c, weight: weightOf(c), surface: c.surface, over: c.over, verts: A.hands[c.side] };
    if (c.at) k.target = () => c.at;
    else if (c.rail) {
      // a rail (its axis from a to b, radius r): the palm on its top, where along it Kimodo's palm is now — the hand
      // slides with Kimodo's, only brought onto the rail. The palm's middle over the rail's top by the palm's own
      // thickness (2.2 cm, as plan.py asks Kimodo): Kimodo's fingers are curled, and on a rail they curl round it —
      // there is no grip, so they go into it a little; that is what holding a rail looks like here (measured)
      const a = c.rail.a, ab = sub(c.rail.b, a), L2 = dot(ab, ab);
      k.target = (t, pose) => {
        if (!pose) return null;
        const p = A.fig.palm(pose, c.side), u = clamp(dot(sub(p, a), ab) / L2, 0, 1), x = add(a, scale(ab, u));
        return [x[0], x[1] + c.rail.r + c.rail.palm, x[2]];
      };
    }
    return k;
  });
  for (const c of scene.contacts) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.018, 16, 12), new THREE.MeshBasicMaterial({ color: '#e0592a', depthTest: false, transparent: true, opacity: 0.85 }));
    m.renderOrder = 10; marks.add(m);
  }
  // feet standing on steps (К2): what is under a point of the floor — the highest step over it, or the floor
  A.fig.feet = (scene.feet || []).map(f => {
    const p = props[f.prop], tops = p.boxes.filter(b => f.boxes.includes(b.part));
    const top = (x, z) => { const l = toLocal(p, [x, 0, z]); let y = 0; for (const b of tops) if (Math.abs(l[0] - b.c[0]) <= b.s[0] / 2 && Math.abs(l[2] - b.c[2]) <= b.s[2] / 2) y = Math.max(y, b.c[1] + b.s[1] / 2); return y; };
    return { side: f.side, name: f.name, verts: A.ofParts([f.side === 'Left' ? 'Lfoot' : 'Rfoot']), top };
  });
  const touches = (scene.touches || []).map(t => ({ ...t, verts: A.ofParts(t.parts), prop: props[t.prop], boxes: props[t.prop].boxes.filter(b => t.boxes.includes(b.part)) }));
  for (const o of objects) stage.scene.add(o);
  cur = { scene, A, props, marks, objects, touches };
  cur.frames = A.clip.frames;
  $('#time').max = cur.frames - 1;
  $('#about').textContent = scene.about;
  if (S.t > cur.frames - 1) S.t = 0;
  stage.showPath([], []);
  Object.assign(cam, scene.camera || {}, { target: (scene.look || [0, 0.8, 1]).slice() });
  draw(); press();
  msg.style.display = 'none';
}

// ———— one moment ————
function poseAt(t) { const { A } = cur; A.fig.correct = S.correct; A.fig.frame(A.clip, Math.min(t, A.clip.frames - 1)); }
function measure(t) {
  const { A, props, touches } = cur, pos = A.fig.positions, out = { t, contacts: [], touches: [], into: [] };
  const P = i => [pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]];
  A.fig.contacts.forEach((c, k) => {
    const r = A.fig.reach[k], hv = A.hands[c.side];
    const o = { side: c.side, name: c.def.name, w: +r.w.toFixed(2), palmBefore: r.before, palmAfter: r.after };
    if (c.def.surface != null) { let lo = Infinity; for (const i of hv) lo = Math.min(lo, pos[i * 3 + 1]); o.gap = lo - c.def.surface; }
    if (c.def.rail) {      // the hand's skin to the rail: the nearest point of the hand to the rail's surface (− inside)
      const a = c.def.rail.a, ab = sub(c.def.rail.b, a), L2 = dot(ab, ab); let g = Infinity;
      for (const i of hv) { const x = P(i), u = clamp(dot(sub(x, a), ab) / L2, 0, 1); g = Math.min(g, len(sub(x, add(a, scale(ab, u)))) - c.def.rail.r); }
      o.gap = g;
    }
    out.contacts.push(o);
  });
  // a part of the body resting on a thing: the nearest of its skin to the thing's faces (− how deep inside)
  for (const tc of touches) {
    let g = Infinity;
    for (const i of tc.verts) { const xl = toLocal(tc.prop, P(i)); for (const b of tc.boxes) g = Math.min(g, boxDistance(b, xl)); }
    out.touches.push({ name: tc.name, gap: g });
  }
  out.feet = A.fig.stand.map((f, k) => ({ side: f.side, name: A.fig.feet[k].name, before: f.before, after: f.after }));
  // the body into the things: the deepest vertex in each part
  for (const p of props) for (const b of p.boxes) {
    let deep = 0, n = 0, who = -1;
    for (let i = 0; i < A.fig.body.N; i++) { const d = -boxDistance(b, toLocal(p, P(i))); if (d > 0) { n++; if (d > deep) { deep = d; who = i; } } }
    if (n) out.into.push({ thing: p.kind, part: b.part, vertices: n, deepest: deep, by: A.partOf[who] });
  }
  return out;
}

const cm = x => x == null ? '—' : (x * 100).toFixed(1) + ' см';
function draw() {
  const t = S.t; poseAt(t);
  const { A, marks } = cur;
  A.view.update();
  A.fig.contacts.forEach((c, k) => { const x = A.fig.reach[k].target; marks.children[k].visible = S.marks && !!x && A.fig.reach[k].w > 0.01; if (x) marks.children[k].position.set(...x); });
  const P = A.fig.pose.P; stage.light([P[0], 0, P[2]]);
  if (S.follow) { cam.target[0] = P[0]; cam.target[2] = P[2]; }
  $('#time').value = t; $('#flab').textContent = `${Math.floor(t)}/${cur.frames - 1}`;
  const m = measure(t), lines = [];
  for (const c of m.contacts) {
    lines.push(`${c.name}: ладонь от места ${c.w > 0.01 ? cm(c.palmAfter) : '—'}${c.w > 0.01 && S.correct ? ` (Kimodo: ${cm(c.palmBefore)})` : ''}` +
      (c.gap != null && c.w > 0.5 ? `, кожа ${c.gap < 0 ? 'внутри на ' + cm(-c.gap) : 'до поверхности ' + cm(c.gap)}` : ''));
  }
  const on = g => g < 0 ? 'в ступени на ' + cm(-g) : 'над ступенью ' + cm(g);
  for (const f of m.feet) lines.push(`${f.name}: ${on(f.after)}${S.correct && Math.abs(f.after - f.before) > 1e-4 ? ` (Kimodo: ${on(f.before)})` : ''}`);
  for (const x of m.touches) lines.push(`${x.name}: ${x.gap < 0 ? 'внутри на ' + cm(-x.gap) : 'до поверхности ' + cm(x.gap)}`);
  const deep = m.into.filter(x => x.deepest > 0.005);
  lines.push(deep.length ? 'входит: ' + deep.map(x => `${PART[x.part] || x.part} ${cm(x.deepest)}`).join(', ') : 'в предметы не входит');
  $('#meter').textContent = lines.join('\n');
}
const PART = { wall: 'стена', step: 'ступень', rail: 'перила', post: 'стойка перил', top: 'столешница', leg: 'ножка', seat: 'сиденье', back: 'спинка',
  mattress: 'матрас', frame: 'кровать', head: 'изголовье', box: 'ящик', base: 'низ' };

// ———— the panel ————
const panel = document.createElement('div'); panel.id = 'panel';
panel.innerHTML = `
  <h1>Касания телом: стена, лестница, кровать, стол</h1>
  <div class="row" id="scenes"></div>
  <div class="about" id="about"></div>
  <div class="row"><button id="play" aria-label="Пауза">❚❚</button><input id="time" type="range" min="0" max="0" step="0.01" value="0" aria-label="Время"><span id="flab"></span></div>
  <div class="row"><span class="lab">Камера</span><button data-view="front">спереди</button><button data-view="side">сбоку</button><button data-view="close">касание близко</button><button data-view="whole">весь путь</button><button id="follow">следует</button></div>
  <div class="row"><span class="lab">Руки</span><button id="correct">с поправкой</button><button id="marks">места касания</button></div>
  <div class="sep"></div>
  <div id="meter"></div>
  <div class="hint">мышь: вращать · колесо: ближе · Shift или правая кнопка: сдвинуть · пробел: пауза</div>`;
const $ = s => panel.querySelector(s);
for (const s of SC.scenes) { const b = document.createElement('button'); b.textContent = s.label; b.dataset.id = s.id; b.onclick = () => { S.t = 0; setScene(s.id); }; $('#scenes').appendChild(b); }
function press() {
  panel.querySelectorAll('#scenes button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.id === S.scene)));
  $('#correct').setAttribute('aria-pressed', String(S.correct)); $('#follow').setAttribute('aria-pressed', String(S.follow)); $('#marks').setAttribute('aria-pressed', String(S.marks));
  $('#play').textContent = S.playing ? '❚❚' : '▶';
}
$('#play').onclick = () => { S.playing = !S.playing; press(); };
$('#time').oninput = () => { S.t = +$('#time').value; S.playing = false; press(); draw(); };
$('#correct').onclick = () => { S.correct = !S.correct; press(); draw(); };
$('#marks').onclick = () => { S.marks = !S.marks; press(); draw(); };
$('#follow').onclick = () => { S.follow = !S.follow; press(); draw(); };
panel.querySelectorAll('[data-view]').forEach(b => b.onclick = () => view(b.dataset.view));
function view(kind) {
  const v = (cur.scene.views || {})[kind];
  if (v) Object.assign(cam, { yaw: v.yaw, pitch: v.pitch, dist: v.dist, target: v.target.slice() });
  S.follow = !!(v && v.follow); press();
}

let drag = null;
canvas.addEventListener('contextmenu', e => e.preventDefault());
canvas.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY, pan: e.button === 2 || e.shiftKey }; canvas.setPointerCapture(e.pointerId); });
canvas.addEventListener('pointermove', e => {
  if (!drag) return; const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.x = e.clientX; drag.y = e.clientY;
  if (drag.pan) { S.follow = false; press(); const s = cam.dist * 0.0012; cam.target[0] -= Math.cos(cam.yaw) * dx * s; cam.target[2] += Math.sin(cam.yaw) * dx * s; cam.target[1] += dy * s; }
  else { cam.yaw -= dx * 0.007; cam.pitch = Math.max(-0.4, Math.min(1.3, cam.pitch + dy * 0.005)); }
});
canvas.addEventListener('pointerup', () => drag = null); canvas.addEventListener('pointercancel', () => drag = null);
canvas.addEventListener('wheel', e => { e.preventDefault(); cam.dist = Math.max(0.4, Math.min(40, cam.dist * Math.exp(e.deltaY * 0.001))); }, { passive: false });
addEventListener('keydown', e => { if (e.key === ' ' && e.target === document.body) { e.preventDefault(); S.playing = !S.playing; press(); } });

// ———— run ————
document.body.appendChild(panel); fit();
await setScene(S.scene);
window.__contacts = {
  S, cam, stage, get cur() { return cur; }, view,
  async set(o) { const sc = o.scene && o.scene !== S.scene; Object.assign(S, o); if (sc) await setScene(S.scene); press(); draw(); },
  render() { draw(); stage.look(cam.target, cam); stage.render(); },
  measureAll(step = 1) { const out = []; for (let t = 0; t < cur.frames; t += step) { S.t = t; poseAt(t); out.push(measure(t)); } return out; },
};
let last = performance.now();
(function loop(now) {
  const dt = Math.min(0.1, (now - last) / 1000); last = now;
  if (S.playing) { S.t += dt * 30; if (S.t > cur.frames - 1) S.t = 0; draw(); }
  stage.look(cam.target, cam); stage.render();
  requestAnimationFrame(loop);
})(last);
