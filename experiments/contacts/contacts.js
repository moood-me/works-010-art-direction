// К1 — contacts: a person comes to a place and touches it — the hands on a table, a hand on another's shoulder, the
// hands on an armchair's armrests. The motions are Kimodo's, ordered with the place given to it as a constraint
// (tools/plan.py); this page plays them on the early engine's bodies (engine/), with the things as simple forms, and
// measures the touch every frame: how far the palm is from its place, how far the hand's skin is from the surface,
// and whether anything of the body goes into the things or into the other person.
// URL: ?s=<scene>&t=<frame>&paused&raw (no correction) — and window.__contacts for tools (pictures, numbers).
import * as THREE from 'three';
import { createEngine } from '../../engine/src/engine.js';
import { loadMotion, clipOf } from '../../engine/src/motion.js';
import { makeStage, figureMesh } from '../../engine/src/view3d.js';
import { readJSON } from '../../engine/src/pack.js';
import { qRot, qAxisAngle, getQ, getV, sub, len } from '../../engine/src/math.js';
import { ContactFigure } from './contact-figure.js';

const here = new URL('./', import.meta.url);
const q = new URLSearchParams(location.search);
const msg = document.getElementById('msg'), canvas = document.getElementById('cv');
const E = await createEngine();
const SC = await readJSON(new URL('scenes.json', here));
const stage = makeStage(THREE, canvas, { pixelRatio: Math.min(devicePixelRatio || 1, 2) });
// the engine's stage casts shadows over 4.4 m around one figure; here two people and things stand farther apart, and
// the edge of that square showed on the floor in wide views: the same light over a wider square
Object.assign(stage.key.shadow.camera, { left: -5, right: 5, top: 5, bottom: -3, far: 20 }); stage.key.shadow.camera.updateProjectionMatrix();
stage.key.shadow.mapSize.set(4096, 4096);
const fit = () => { const p = document.getElementById('panel'), w = p && innerWidth > 760 ? p.offsetWidth + 12 : 0; stage.size(innerWidth, innerHeight, w / 2); };
addEventListener('resize', fit); fit();

const S = { scene: q.get('s') || SC.scenes[0].id, t: +(q.get('t') || 0), playing: !q.has('paused'), correct: !q.has('raw'), marks: true, follow: false };
const cam = { yaw: 0.9, pitch: 0.18, dist: 4.4, target: [0, 0.8, 0] };
let cur = null;   // {scene, A: {fig, view, clip}, B, props, marks}

// ———— things: boxes, turned about the vertical (their own frame: x across, y up, z ahead) ————
// A box: {c: [x, y, z] centre in the thing's frame, s: [w, h, d]}; a thing: {kind, at, heading, …} → its boxes
function boxesOf(p) {
  const B = [];
  if (p.kind === 'table') {
    const [w, d] = p.size, h = p.height, t = 0.035, l = 0.05;
    B.push({ c: [0, h - t / 2, 0], s: [w, t, d], part: 'top' });
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) B.push({ c: [sx * (w / 2 - 0.06), (h - t) / 2, sz * (d / 2 - 0.06)], s: [l, h - t, l], part: 'leg' });
  } else if (p.kind === 'armchair') {
    const { width: w, depth: d, seat, arm, back, armWidth: aw } = p;
    B.push({ c: [0, seat - 0.06, 0], s: [w - 2 * aw, 0.12, d], part: 'seat' });
    B.push({ c: [0, (seat + back) / 2 - 0.06, -d / 2 + 0.06], s: [w - 2 * aw, back - seat + 0.12, 0.12], part: 'back' });
    B.push({ c: [0, (seat - 0.12) / 2, 0], s: [w - 2 * aw, seat - 0.12, d], part: 'base' });
    for (const sx of [-1, 1]) B.push({ c: [sx * (w / 2 - aw / 2), arm / 2, 0.0], s: [aw, arm, d], part: 'arm' });
  }
  return B;
}
const turnY = (h, v) => qRot(qAxisAngle([0, 1, 0], h), v);
// a point in the world into a thing's frame
function toLocal(p, x) { const r = turnY(-p.heading, sub(x, p.at)); return r; }
function insideDepth(b, xl) {   // how deep a point (in the thing's frame) is inside a box; ≤ 0 — outside
  let d = Infinity;
  for (let k = 0; k < 3; k++) d = Math.min(d, b.s[k] / 2 - Math.abs(xl[k] - b.c[k]));
  return d;
}

function propMesh(p) {
  const g = new THREE.Group();
  const wood = new THREE.MeshStandardMaterial({ color: p.color || '#8a6a4f', roughness: 0.8 });
  const cloth = new THREE.MeshStandardMaterial({ color: p.cloth || '#6f7f6a', roughness: 0.95 });
  for (const b of boxesOf(p)) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(...b.s), ['seat', 'back', 'arm', 'base'].includes(b.part) ? cloth : wood);
    m.position.set(...b.c); m.castShadow = m.receiveShadow = true; g.add(m);
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
  // which vertices are the hands' (by the joint that carries most of each vertex)
  const sk = body.skeleton, under = s => new Set(sk.under(sk.index[s + 'Hand']));
  const hands = { Left: [], Right: [] }, Lh = under('Left'), Rh = under('Right');
  for (let i = 0; i < body.N; i++) {
    let best = 0, bj = -1; for (let k = 0; k < 4; k++) { const w = body.skin.weights[i * 4 + k]; if (w > best) { best = w; bj = body.skin.joints[i * 4 + k]; } }
    if (Lh.has(bj)) hands.Left.push(i); else if (Rh.has(bj)) hands.Right.push(i);
  }
  // each vertex's body part (the one it belongs to most), for saying what goes into a thing
  const PN = body.parts.names, NP = PN.length, partOf = new Array(body.N);
  for (let i = 0; i < body.N; i++) { let best = -1, bk = 0; for (let k = 0; k < NP; k++) { const w = body.parts.weights[i * NP + k]; if (w > best) { best = w; bk = k; } } partOf[i] = PN[bk]; }
  return { fig, clip, view, hands, who, partOf };
}

// a contact's weight over time: in over `ramp` frames before `from`, held, out over `ramp` after `to`
const smooth = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);
const weightOf = c => t => smooth((t - (c.frames[0] - c.ramp)) / c.ramp) * (c.frames[1] >= 1e8 ? 1 : 1 - smooth((t - c.frames[1]) / c.ramp));

async function setScene(id) {
  msg.style.display = 'grid'; await new Promise(r => setTimeout(r, 20));
  if (cur) { for (const o of cur.objects) stage.scene.remove(o); for (const f of [cur.A, cur.B]) f && f.view.dispose(); }
  const scene = SC.scenes.find(s => s.id === id);
  S.scene = id;
  const A = await figureOf(scene.person), B = scene.other ? await figureOf(scene.other) : null;
  const objects = [A.view.mesh];
  if (B) { B.view.mesh.material.color.set(scene.other.color || '#b9a48f'); objects.push(B.view.mesh); }
  const props = scene.props.map(p => ({ ...p, boxes: boxesOf(p) }));
  for (const p of props) objects.push(propMesh(p));
  // the places the palms are asked to come to (small rings), and where they are
  const marks = new THREE.Group(); objects.push(marks);
  A.fig.contacts = scene.contacts.map(c => {
    const k = { side: c.side, def: c, weight: weightOf(c), surface: c.surface, over: c.over, verts: A.hands[c.side] };
    // on the other person: a point of their skin, as they are now; the palm's middle over it by the hand's thickness
    k.target = c.at ? () => c.at : () => { const p = B.fig.positions, v = c.on.vertex; return [p[v * 3], p[v * 3 + 1] + (k.under || 0), p[v * 3 + 2]]; };
    // and kept out of the other's skin, on the way and while it lies there (Kimodo, making one person, knows nothing of
    // the other; and a hand turned as Kimodo turned it can dip its fingers into a sloping shoulder)
    if (c.on) k.outside = (pos, shift, move) => {
      const bp = B.fig.positions, bn = B.fig.normals, near = B.near || [];
      let deep = 0, dir = null;
      for (const i of k.verts) {
        const x = pos[i * 3] + move[0], y = pos[i * 3 + 1] + shift + move[1], z = pos[i * 3 + 2] + move[2];
        let bd = Infinity, bi = -1;
        for (const v of near) { const dx = x - bp[v * 3], dy = y - bp[v * 3 + 1], dz = z - bp[v * 3 + 2], d = dx * dx + dy * dy + dz * dz; if (d < bd) { bd = d; bi = v; } }
        if (bi < 0) continue;
        const s = (x - bp[bi * 3]) * bn[bi * 3] + (y - bp[bi * 3 + 1]) * bn[bi * 3 + 1] + (z - bp[bi * 3 + 2]) * bn[bi * 3 + 2];
        if (-s > deep) { deep = -s; dir = [bn[bi * 3], bn[bi * 3 + 1], bn[bi * 3 + 2]]; }
      }
      return deep > 0.002 ? dir.map(v => v * (deep + 0.002)) : null;
    };
    return k;
  });
  for (const c of scene.contacts) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.018, 16, 12), new THREE.MeshBasicMaterial({ color: '#e0592a', depthTest: false, transparent: true, opacity: 0.85 }));
    m.renderOrder = 10; marks.add(m);
  }
  for (const o of objects) stage.scene.add(o);
  cur = { scene, A, B, props, marks, objects };
  const frames = A.clip.frames;
  cur.frames = frames;
  $('#time').max = frames - 1;
  $('#about').textContent = scene.about;
  if (S.t > frames - 1) S.t = 0;
  stage.showPath([], []);
  Object.assign(cam, scene.camera || {}, { target: scene.look || [0, 0.8, 1] });
  draw();
  press();
  msg.style.display = 'none';
}

// ———— one moment: the figures, the marks, the numbers ————
function poseAt(t) {
  const { A, B } = cur;
  if (B) B.fig.frame(B.clip, Math.min(t, B.clip.frames - 1));
  A.fig.correct = S.correct;
  A.fig.frame(A.clip, Math.min(t, A.clip.frames - 1));
}
function measure(t) {
  const { A, B, props, scene } = cur, pos = A.fig.positions, out = { t, contacts: [], into: [] };
  A.fig.contacts.forEach((c, k) => {
    const r = A.fig.reach[k], target = c.target(t), hv = A.hands[c.side];
    const o = { side: c.side, name: c.def.name, w: +r.w.toFixed(2), palmBefore: r.before, palmAfter: r.after, surface: c.def.surface };
    if (c.def.at && c.def.surface != null) {      // the hand's lowest skin over the surface it lies on
      let lo = Infinity; for (const i of hv) lo = Math.min(lo, pos[i * 3 + 1]);
      o.gap = lo - c.def.surface;
    }
    if (c.def.on) {                                // the hand's skin to the other person's skin
      let best = Infinity; const bp = B.fig.positions, bn = B.fig.normals, near = B.near || [];
      let inside = 0;
      for (const i of hv) {
        let bd = Infinity, bi = -1;
        for (const v of near) { const dx = pos[i * 3] - bp[v * 3], dy = pos[i * 3 + 1] - bp[v * 3 + 1], dz = pos[i * 3 + 2] - bp[v * 3 + 2], d = dx * dx + dy * dy + dz * dz; if (d < bd) { bd = d; bi = v; } }
        const dd = Math.sqrt(bd); best = Math.min(best, dd);
        const s = (pos[i * 3] - bp[bi * 3]) * bn[bi * 3] + (pos[i * 3 + 1] - bp[bi * 3 + 1]) * bn[bi * 3 + 1] + (pos[i * 3 + 2] - bp[bi * 3 + 2]) * bn[bi * 3 + 2];
        if (s < 0) inside = Math.max(inside, dd);
      }
      o.gap = best; o.inside = inside;
    }
    out.contacts.push(o);
  });
  // the two bodies into each other: A's skin under B's (by B's nearest vertex and its normal), the deepest point
  if (B) {
    const bp = B.fig.positions, bn = B.fig.normals, NB = B.fig.body.N, lo = [9, 9, 9], hi = [-9, -9, -9];
    for (let i = 0; i < NB; i++) for (let k = 0; k < 3; k++) { lo[k] = Math.min(lo[k], bp[i * 3 + k]); hi[k] = Math.max(hi[k], bp[i * 3 + k]); }
    let deep = 0, by = null;
    for (let i = 0; i < A.fig.body.N; i++) {
      const x = pos[i * 3], y = pos[i * 3 + 1], z = pos[i * 3 + 2];
      if (x < lo[0] || x > hi[0] || y < lo[1] || y > hi[1] || z < lo[2] || z > hi[2]) continue;
      let bd = Infinity, bi = -1;
      for (let v = 0; v < NB; v += 2) { const dx = x - bp[v * 3], dy = y - bp[v * 3 + 1], dz = z - bp[v * 3 + 2], d = dx * dx + dy * dy + dz * dz; if (d < bd) { bd = d; bi = v; } }
      const s = (x - bp[bi * 3]) * bn[bi * 3] + (y - bp[bi * 3 + 1]) * bn[bi * 3 + 1] + (z - bp[bi * 3 + 2]) * bn[bi * 3 + 2];
      if (s < 0 && -s > deep) { deep = -s; by = A.partOf[i] + ' → ' + B.partOf[bi]; }
    }
    if (deep > 0) out.into.push({ thing: 'other', part: 'body', vertices: 1, deepest: deep, by });
  }
  // the body into the things: the deepest vertex in each part (the hands on a table top are allowed none either)
  for (const p of props) for (const b of p.boxes) {
    let deep = 0, n = 0, who = -1;
    for (let i = 0; i < A.fig.body.N; i++) { const d = insideDepth(b, toLocal(p, [pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]])); if (d > 0) { n++; if (d > deep) { deep = d; who = i; } } }
    if (n) out.into.push({ thing: p.kind, part: b.part, vertices: n, deepest: deep, by: A.partOf[who] });
  }
  return out;
}

const cm = x => x == null ? '—' : (x * 100).toFixed(1) + ' см';
function draw() {
  const t = S.t; poseAt(t);
  const { A, B, marks } = cur;
  A.view.update(); if (B) B.view.update();
  A.fig.contacts.forEach((c, k) => { const x = c.target(t); marks.children[k].visible = S.marks && !!x && A.fig.reach[k].w > 0.01; if (x) marks.children[k].position.set(...x); });
  const P = A.fig.pose.P; stage.light([P[0], 0, P[2]]);
  if (S.follow) { cam.target[0] = P[0]; cam.target[2] = P[2]; }
  $('#time').value = t; $('#flab').textContent = `${Math.floor(t)}/${cur.frames - 1}`;
  const m = measure(t), lines = [];
  for (const c of m.contacts) {
    const nm = c.name || (c.side === 'Left' ? 'левая' : 'правая');
    lines.push(`${nm}: ладонь от места ${c.w > 0.01 ? cm(c.palmAfter) : '—'}${c.w > 0.01 && S.correct ? ` (Kimodo: ${cm(c.palmBefore)})` : ''}` +
      (c.gap != null && c.w > 0.5 ? `, кожа ${c.inside ? 'внутри на ' + cm(c.inside) : (c.surface == null ? 'до кожи другого ' : 'до поверхности ') + cm(c.gap)}` : ''));
  }
  const deep = m.into.filter(x => !(x.part === 'seat' || x.part === 'back') || x.deepest > 0.03);
  lines.push(deep.length ? 'входит: ' + deep.map(x => `${PART[x.part] || x.part} ${cm(x.deepest)}`).join(', ') : (cur.B ? 'ни во что и ни в кого не входит' : 'в предметы не входит'));
  $('#meter').textContent = lines.join('\n');
}
const PART = { body: 'другой человек', top: 'столешница', leg: 'ножка', seat: 'сиденье', back: 'спинка', arm: 'подлокотник', base: 'низ кресла' };

// ———— the panel ————
const panel = document.createElement('div'); panel.id = 'panel';
panel.innerHTML = `
  <h1>Касания: человек подходит и касается</h1>
  <div class="row" id="scenes"></div>
  <div class="about" id="about"></div>
  <div class="row"><button id="play" aria-label="Пауза">❚❚</button><input id="time" type="range" min="0" max="0" step="0.01" value="0" aria-label="Время"><span id="flab"></span></div>
  <div class="row"><span class="lab">Камера</span><button data-view="front">спереди</button><button data-view="side">сбоку</button><button data-view="close">рука близко</button><button data-view="whole">весь путь</button><button id="follow">следует</button></div>
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
// the other person's skin near the contact (for measuring the hand against it): its vertices within reach of the place
function nearOther() {
  const { A, B } = cur; if (!B) return;
  B.near = []; const bp = B.fig.positions;
  B.fig.frame(B.clip, 0);
  const c = A.fig.contacts.find(c => c.def.on); if (!c) return;
  const x = c.target(0);
  for (let i = 0; i < B.fig.body.N; i++) if (Math.hypot(bp[i * 3] - x[0], bp[i * 3 + 1] - x[1], bp[i * 3 + 2] - x[2]) < 0.35) B.near.push(i);
}
const setSceneAndNear = async id => { await setScene(id); nearOther(); draw(); };
panel.querySelectorAll('#scenes button').forEach(b => b.onclick = () => { S.t = 0; setSceneAndNear(b.dataset.id); });
nearOther(); draw();
window.__contacts = {
  S, cam, stage, get cur() { return cur; }, view,
  async set(o) { const sc = o.scene && o.scene !== S.scene; Object.assign(S, o); if (sc) await setSceneAndNear(S.scene); press(); draw(); },
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
