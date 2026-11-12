// К1, next step — things that move with the hand: a door opened by its handle, a cup taken from a table and put
// back, a box carried in both hands. Grown from experiments/contacts/contacts.js (copied and changed).
// The motions are Kimodo's, ordered with the places given to it as hand constraints (tools/plan.py); this page plays
// them on the early engine's bodies (engine/), finishes each touch with a small arm correction (contact-figure.js),
// and moves the thing with the hand while it is held: the thing is attached to the hand (or to both hands, or, for a
// door, to its hinge and the hand on its handle). It measures, every frame, how far each palm is from its place,
// what of the body goes into the things, and where a thing stands once it is put down.
// URL: ?s=<scene>&t=<frame>&paused&raw (no correction) — and window.__moving for tools (pictures, numbers).
import * as THREE from 'three';
import { createEngine } from '../../engine/src/engine.js';
import { loadMotion, clipOf } from '../../engine/src/motion.js';
import { makeStage, figureMesh } from '../../engine/src/view3d.js';
import { readJSON } from '../../engine/src/pack.js';
import { qRot, qMul, qConj, qAxisAngle, qAngle, getQ, sub, add, len, normalize, cross, dot, clamp } from '../../engine/src/math.js';
import { ContactFigure } from './contact-figure.js';

const here = new URL('./', import.meta.url);
const q = new URLSearchParams(location.search);
const msg = document.getElementById('msg'), canvas = document.getElementById('cv');
const E = await createEngine();
const SC = await readJSON(new URL('scenes.json', here));
const stage = makeStage(THREE, canvas, { pixelRatio: Math.min(devicePixelRatio || 1, 2) });
Object.assign(stage.key.shadow.camera, { left: -5, right: 5, top: 5, bottom: -3, far: 20 }); stage.key.shadow.camera.updateProjectionMatrix();
stage.key.shadow.mapSize.set(4096, 4096);
const fit = () => { const p = document.getElementById('panel'), w = p && innerWidth > 760 ? p.offsetWidth + 12 : 0; stage.size(innerWidth, innerHeight, w / 2); };
addEventListener('resize', fit); fit();

const S = { scene: q.get('s') || SC.scenes[0].id, t: +(q.get('t') || 0), playing: !q.has('paused'), correct: !q.has('raw'), marks: true, follow: false };
const cam = { yaw: 0.9, pitch: 0.18, dist: 4.4, target: [0, 0.8, 0] };
let cur = null;

// ———— things: boxes in a thing's own frame (x across, y up, z ahead), the thing placed by {at, q} ————
const Y = a => qAxisAngle([0, 1, 0], a);
function boxesOf(p) {
  const B = [];
  if (p.kind === 'table') {
    const [w, d] = p.size, h = p.height, t = 0.035, l = 0.05;
    B.push({ c: [0, h - t / 2, 0], s: [w, t, d], part: 'top' });
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) B.push({ c: [sx * (w / 2 - 0.06), (h - t) / 2, sz * (d / 2 - 0.06)], s: [l, h - t, l], part: 'leg' });
  } else if (p.kind === 'wall') {
    for (const b of p.boxes) B.push({ ...b, part: 'wall' });
  } else if (p.kind === 'leaf') {          // a door's leaf: its frame at the hinge, the leaf along −x
    const { width: w, height: h, thick: t, handle } = p;
    B.push({ c: [-w / 2, h / 2, 0], s: [w, h, t], part: 'leaf' });
    for (const sz of [-1, 1]) {                // on each side: a stem off the leaf, and the lever on it towards the hinge
      B.push({ c: [-(w - handle.in), handle.y, sz * (t / 2 + handle.out / 2)], s: [0.02, 0.02, handle.out], part: 'handle', look: 'metal' });
      B.push({ c: [-(w - handle.in) + 0.05, handle.y, sz * (t / 2 + handle.out - 0.011)], s: [0.12, 0.022, 0.022], part: 'handle', look: 'metal' });
    }
  } else if (p.kind === 'cup') {           // its frame at the middle of its bottom
    B.push({ c: [0, p.h / 2, 0], s: [p.r * 1.7, p.h, p.r * 1.7], part: 'cup', cyl: [p.r, p.h] });
  } else if (p.kind === 'box') {
    B.push({ c: [0, p.size[1] / 2, 0], s: p.size, part: 'box' });
  }
  return B;
}
const toLocal = (tr, x) => qRot(qConj(tr.q), sub(x, tr.at));
function insideDepth(b, xl) { let d = Infinity; for (let k = 0; k < 3; k++) d = Math.min(d, b.s[k] / 2 - Math.abs(xl[k] - b.c[k])); return d; }

function propMesh(p) {
  const g = new THREE.Group();
  const mat = {
    wood: new THREE.MeshStandardMaterial({ color: p.color || '#8a6a4f', roughness: 0.8 }),
    metal: new THREE.MeshStandardMaterial({ color: '#c9c3b8', roughness: 0.35, metalness: 0.6 }),
  };
  for (const b of p.boxes) {
    const m = b.cyl ? new THREE.Mesh(new THREE.CylinderGeometry(b.cyl[0], b.cyl[0] * 0.9, b.cyl[1], 28), mat.wood)
      : new THREE.Mesh(new THREE.BoxGeometry(...b.s), b.look === 'metal' ? mat.metal : mat.wood);
    m.position.set(...b.c); m.castShadow = m.receiveShadow = true; g.add(m);
  }
  if (p.kind === 'cup') {                  // its handle, on the side away from the hand that holds it
    const h = new THREE.Mesh(new THREE.TorusGeometry(p.h * 0.28, 0.008, 8, 20), mat.wood);
    h.position.set(...(p.handleAt || [p.r + 0.012, p.h * 0.55, 0])); h.rotation.y = p.handleTurn || 0; h.castShadow = true; g.add(h);
  }
  return g;
}
const place = (g, tr) => { g.position.set(...tr.at); g.quaternion.set(...tr.q); };

// ———— the person ————
async function figureOf(who) {
  const spec = await E.character(who.character);
  const body = await E.body(spec.body);
  const fig = new ContactFigure(body, spec, who.place);
  const motions = await Promise.all(who.motions.map(id => loadMotion(new URL(`motions/${id}.json`, here), E.skeleton)));
  const clip = clipOf(motions);
  const view = figureMesh(THREE, fig, spec.look);
  const sk = body.skeleton, under = s => new Set(sk.under(sk.index[s + 'Hand']));
  const hands = { Left: [], Right: [] }, Lh = under('Left'), Rh = under('Right'), handOf = new Int8Array(body.N);
  for (let i = 0; i < body.N; i++) {
    let best = 0, bj = -1; for (let k = 0; k < 4; k++) { const w = body.skin.weights[i * 4 + k]; if (w > best) { best = w; bj = body.skin.joints[i * 4 + k]; } }
    if (Lh.has(bj)) { hands.Left.push(i); handOf[i] = 1; } else if (Rh.has(bj)) { hands.Right.push(i); handOf[i] = 2; }
  }
  const PN = body.parts.names, NP = PN.length, partOf = new Array(body.N);
  for (let i = 0; i < body.N; i++) { let best = -1, bk = 0; for (let k = 0; k < NP; k++) { const w = body.parts.weights[i * NP + k]; if (w > best) { best = w; bk = k; } } partOf[i] = PN[bk]; }
  // the mouth: at rest (standing, facing +z), the head's foremost skin 6–8.5 cm under the eyes' height
  const ri = sk.index.RightEye, li = sk.index.LeftEye, eyeY = (body.joints[ri * 3 + 1] + body.joints[li * 3 + 1]) / 2, head = body.part('head');
  let mouth = -1, front = -Infinity;
  for (let i = 0; i < body.N; i++) {
    const y = body.positions[i * 3 + 1], z = body.positions[i * 3 + 2];
    if (head[i] > 0.5 && y < eyeY - 0.06 && y > eyeY - 0.085 && Math.abs(body.positions[i * 3] - (body.joints[ri * 3] + body.joints[li * 3]) / 2) < 0.01 && z > front) { front = z; mouth = i; }
  }
  fig.mouth = mouth;
  return { fig, clip, view, hands, handOf, who, partOf };
}

const smooth = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);
const weightOf = c => t => smooth((t - (c.frames[0] - c.ramp)) / c.ramp) * (c.frames[1] >= 1e8 ? 1 : 1 - smooth((t - c.frames[1]) / c.ramp));

// ———— holding: where a held thing is ————
// A hand's frame: the palm's middle and the hand's turn. Two hands: the middle between the palms, turned so its x runs
// from the right palm to the left one, kept level-ish (y as near up as that allows).
function quatOfBasis(x, y, z) {
  const m = [x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2]], tr = m[0] + m[4] + m[8];
  let qq;
  if (tr > 0) { const s = Math.sqrt(tr + 1) * 2; qq = [(m[7] - m[5]) / s, (m[2] - m[6]) / s, (m[3] - m[1]) / s, 0.25 * s]; }
  else if (m[0] > m[4] && m[0] > m[8]) { const s = Math.sqrt(1 + m[0] - m[4] - m[8]) * 2; qq = [0.25 * s, (m[1] + m[3]) / s, (m[2] + m[6]) / s, (m[7] - m[5]) / s]; }
  else if (m[4] > m[8]) { const s = Math.sqrt(1 + m[4] - m[0] - m[8]) * 2; qq = [(m[1] + m[3]) / s, 0.25 * s, (m[5] + m[7]) / s, (m[2] - m[6]) / s]; }
  else { const s = Math.sqrt(1 + m[8] - m[0] - m[4]) * 2; qq = [(m[2] + m[6]) / s, (m[5] + m[7]) / s, 0.25 * s, (m[3] - m[1]) / s]; }
  return qq;
}
function handFrame(fig, pose, hands) {
  if (hands.length === 1) return { at: fig.palm(pose, hands[0]), q: getQ(pose.Q, fig.body.skeleton.index[hands[0] + 'Hand']) };
  const L = fig.palm(pose, 'Left'), R = fig.palm(pose, 'Right');
  const x = normalize(sub(L, R)), z = normalize(cross(x, [0, 1, 0])), y = cross(z, x);
  return { at: [(L[0] + R[0]) / 2, (L[1] + R[1]) / 2, (L[2] + R[2]) / 2], q: quatOfBasis(x, y, z) };
}
const compose = (a, b) => ({ at: add(a.at, qRot(a.q, b.at)), q: qMul(a.q, b.q) });
const inverse = a => { const qi = qConj(a.q); return { at: qRot(qi, a.at).map(v => -v), q: qi }; };
const angleAbout = (hinge, x) => Math.atan2(x[2] - hinge[2], -(x[0] - hinge[0]));   // 0 along −x, growing towards +z

// what each held thing does at the frame the figure is posed at now (fig.pose)
function heldAt(h, p, fig, t) {
  if (h.kind === 'hinge') {
    const a = angleAbout(p.rest.at, fig.palm(fig.pose, h.hands[0])) - h.a0;
    return { at: p.rest.at, q: Y(clamp(a, 0, p.maxOpen || 2)) };
  }
  return compose(handFrame(fig, fig.pose, h.hands), h.rel);
}

// ———— the scene ————
async function setScene(id) {
  msg.style.display = 'grid'; await new Promise(r => setTimeout(r, 20));
  if (cur) { for (const o of cur.objects) stage.scene.remove(o); cur.A.view.dispose(); }
  const scene = SC.scenes.find(s => s.id === id);
  S.scene = id;
  const A = await figureOf(scene.person);
  const objects = [A.view.mesh];
  const props = scene.props.map(p => {
    const pr = { ...p, boxes: boxesOf(p), rest: { at: p.at, q: Y(p.heading || 0) } };
    pr.tr = pr.rest; pr.mesh = propMesh(pr); place(pr.mesh, pr.tr); objects.push(pr.mesh); return pr;
  });
  const byId = Object.fromEntries(props.map(p => [p.id, p]));
  const marks = new THREE.Group(); objects.push(marks);
  A.fig.contacts = scene.contacts.map(c => {
    const k = { side: c.side, def: c, weight: weightOf(c), surface: c.surface, over: c.over, verts: A.hands[c.side] };
    k.target = targetOf(c, A.fig, byId);
    return k;
  });
  for (const c of scene.contacts) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.016, 16, 12), new THREE.MeshBasicMaterial({ color: '#e0592a', depthTest: false, transparent: true, opacity: 0.85 }));
    m.renderOrder = 10; marks.add(m);
  }
  for (const o of objects) stage.scene.add(o);
  cur = { scene, A, props, byId, marks, objects, memo: {} };
  cur.frames = A.clip.frames;
  $('#time').max = cur.frames - 1;
  $('#about').textContent = scene.about;
  if (S.t > cur.frames - 1) S.t = 0;
  stage.showPath([], []);
  Object.assign(cam, scene.camera || {}, { target: (scene.look || [0, 0.8, 1]).slice() });
  draw(); press();
  msg.style.display = 'none';
}

// A contact's place, frame by frame (read off Kimodo's pose before any correction):
//  at      — a fixed place (a cup's grip at rest, where the palm goes to put it back);
//  handle  — a door's handle: on its arc about the hinge, at the angle Kimodo's palm is at (never behind closed);
//  grip    — one side of a box held in both hands: where it lies till it is taken, where it is put from a little
//            before it is put; between, the box's side from the middle between Kimodo's two palms, so the palms
//            stay the box's width apart.
function targetOf(c, fig, byId) {
  if (c.at) return () => c.at;
  if (c.lips) {
    // a held cup's rim to the lips of this body: the rim's point nearest the face (the cup as the hand holds it now, in
    // Kimodo's pose) is taken to the mouth (a vertex of the skin, found once), 1 cm in front of it; the palm goes
    // with it. The plan gave Kimodo the same for SOMA's face; on another face the mouth is elsewhere by a few cm.
    const cp = byId[c.lips.prop];
    return (t, pose) => {
      const hold = cur && cur.scene.holds.find(x => x.prop === c.lips.prop);
      if (!hold || !hold.rel || !fig.mouth) return null;
      const cupNow = compose(handFrame(fig, pose, hold.hands), hold.rel);
      const rim = add(cupNow.at, qRot(cupNow.q, [0, cp.h, -cp.r]));
      const m = fig.mouth, lips = [fig.positions[m * 3], fig.positions[m * 3 + 1] + fig.shift, fig.positions[m * 3 + 2]];
      const fwd = normalize(qRot(getQ(pose.Q, fig.body.skeleton.index.Head), [0, 0, 1]).map((v, k) => k === 1 ? 0 : v));
      return add(fig.palm(pose, c.side), sub(add(lips, fwd.map(v => v * 0.01)), rim));
    };
  }
  if (c.handle) {
    const p = byId[c.handle.prop], hinge = p.at, r = c.handle.r, y = c.handle.y, a0 = c.handle.a0;
    return (t, pose) => {
      const a = clamp(angleAbout(hinge, fig.palm(pose, c.side)) - a0, 0, p.maxOpen || 2) + a0;
      return [hinge[0] - r * Math.cos(a), y, hinge[2] + r * Math.sin(a)];
    };
  }
  if (c.grip) {
    // rest → held: weighed while the hands are on it, still on the floor (f0–f1: Kimodo holds them there, so the two
    // agree); held → put: over `ramp` frames up to the
    // frame the hands are asked to be where it is put (f2), so the box comes down exactly onto its place
    const g = c.grip, p = byId[g.prop], sgn = c.side === 'Left' ? 1 : -1;
    const side = tr => add(tr.at, qRot(tr.q, [sgn * g.half, g.y, 0]));
    const mix = (a, b, w) => a.map((v, k) => v + (b[k] - v) * w);
    return (t, pose) => {
      const L = fig.palm(pose, 'Left'), R = fig.palm(pose, 'Right'), m = [(L[0] + R[0]) / 2, (L[1] + R[1]) / 2, (L[2] + R[2]) / 2];
      const held = add(m, normalize(sub(L, R)).map(v => v * sgn * g.half));
      const put = { at: g.put, q: p.rest.q };
      return mix(mix(side(p.rest), held, smooth((t - g.f0) / (g.f1 - g.f0))), side(put), smooth((t - (g.f2 - g.ramp)) / g.ramp));
    };
  }
  return () => null;
}

// ———— one moment: the figure, the held things, the marks, the numbers ————
// A held thing keeps, from the frame it is taken, its place relative to the hand(s) then; from the frame it is let go
// it stays where it was. Both moments are posed once (with or without the correction) and remembered.
function holdState(h) {
  const { A, byId, memo } = cur, p = byId[h.prop], key = `${p.id}|${S.correct}`;
  if (!memo['grab' + key]) {
    A.fig.correct = S.correct; A.fig.frame(A.clip, h.from);
    // a door: its angle is the handle's (the palm on it) less where the handle is when the door is shut (h.a0, the
    // scene's); anything else keeps its place relative to the hand(s) as they were when it was taken
    if (h.kind !== 'hinge') h.rel = compose(inverse(handFrame(A.fig, A.fig.pose, h.hands)), p.rest);
    memo['grab' + key] = { rel: h.rel };
    A.fig.frame(A.clip, h.to);
    memo[key] = heldAt(h, p, A.fig, h.to);
    if (h.kind === 'hinge') {          // how fast the door was turning when let go (over the last 4 frames held)
      A.fig.frame(A.clip, h.to - 4);
      memo[key].speed = (qAngle(memo[key].q) - qAngle(heldAt(h, p, A.fig, h.to - 4).q)) / 4;
    }
  }
  Object.assign(h, memo['grab' + key]);
  return memo[key];
}
// let go, a thing stays where it was — but a door pushed open swings on, slowing (a third of a second to lose two
// thirds of its speed), till it stops or meets its stop (p.maxOpen)
function afterLetGo(h, p, t) {
  const m = cur.memo[`${p.id}|${S.correct}`];
  if (h.kind !== 'hinge' || !(m.speed > 0)) return m;
  const tau = 10, a = qAngle(m.q) + m.speed * tau * (1 - Math.exp(-(t - h.to) / tau));
  return { at: m.at, q: Y(Math.min(a, p.maxOpen || 2)) };
}
function poseAt(t) {
  const { A, scene, byId } = cur;
  for (const h of scene.holds || []) holdState(h);
  A.fig.correct = S.correct;
  A.fig.frame(A.clip, Math.min(t, A.clip.frames - 1));
  for (const h of scene.holds || []) {
    const p = byId[h.prop];
    p.tr = t < h.from ? p.rest : t > h.to ? afterLetGo(h, p, t) : heldAt(h, p, A.fig, t);
    p.held = t >= h.from && t <= h.to ? h.hands : null;
    p.on = t > h.to && p.putOn != null ? p.putOn : p.standsOn;
  }
}
function measure(t) {
  const { A, props, scene } = cur, pos = A.fig.positions, out = { t, contacts: [], into: [], things: [] };
  A.fig.contacts.forEach((c, k) => {
    const r = A.fig.reach[k];
    const o = { side: c.side, name: c.def.name, w: +r.w.toFixed(2), palmBefore: r.before, palmAfter: r.after };
    if (c.def.surface != null) { let lo = Infinity; for (const i of c.verts) lo = Math.min(lo, pos[i * 3 + 1]); o.gap = lo - c.def.surface; }
    out.contacts.push(o);
  });
  // the body into the things: the deepest vertex in each part; a held thing's own hands are counted apart ("grip")
  for (const p of props) for (const b of p.boxes) {
    let deep = 0, n = 0, who = -1, gdeep = 0;
    for (let i = 0; i < A.fig.body.N; i++) {
      const d = insideDepth(b, toLocal(p.tr, [pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]]));
      if (d <= 0) continue;
      const own = p.held && A.handOf[i] && p.held.includes(A.handOf[i] === 1 ? 'Left' : 'Right');
      if (own) { gdeep = Math.max(gdeep, d); continue; }
      n++; if (d > deep) { deep = d; who = i; }
    }
    if (n) out.into.push({ thing: p.id, part: b.part, vertices: n, deepest: deep, by: A.partOf[who] });
    if (gdeep) out.into.push({ thing: p.id, part: b.part, grip: true, deepest: gdeep });
  }
  // a thing that stands on something: how high its bottom is over it, how far it leans from upright
  for (const p of props) if (p.standsOn != null) {
    const on = p.on != null ? p.on : p.standsOn;
    const up = qRot(p.tr.q, [0, 1, 0]);
    out.things.push({ id: p.id, over: p.tr.at[1] - on, tilt: Math.acos(clamp(up[1], -1, 1)) * 180 / Math.PI, at: p.tr.at, held: !!p.held });
  }
  // a cup in the hand: how far the rim's point nearest the face is from the mouth
  const m = A.fig.mouth;
  for (const p of props) if (p.kind === 'cup' && p.held && m >= 0) {
    const rim = add(p.tr.at, qRot(p.tr.q, [0, p.h, -p.r]));
    out.things.push({ id: p.id + '-lips', lips: len(sub(rim, [pos[m * 3], pos[m * 3 + 1], pos[m * 3 + 2]])) });
  }
  for (const p of props) if (p.kind === 'leaf') out.things.push({ id: p.id, open: qAngle(p.tr.q) * 180 / Math.PI, held: !!p.held });
  return out;
}

const cm = x => x == null ? '—' : (x * 100).toFixed(1) + ' см';
const PART = { top: 'столешница', leg: 'ножка', wall: 'стена', leaf: 'дверь', handle: 'ручка', cup: 'чашка', box: 'коробка' };
function draw() {
  const t = S.t; poseAt(t);
  const { A, marks, props } = cur;
  A.view.update();
  for (const p of props) place(p.mesh, p.tr);
  A.fig.contacts.forEach((c, k) => { const x = c.now; marks.children[k].visible = S.marks && !!x && A.fig.reach[k].w > 0.01; if (x) marks.children[k].position.set(...x); });
  const P = A.fig.pose.P; stage.light([P[0], 0, P[2]]);
  if (S.follow) { cam.target[0] = P[0]; cam.target[2] = P[2]; }
  $('#time').value = t; $('#flab').textContent = `${Math.floor(t)}/${cur.frames - 1}`;
  const m = measure(t), lines = [];
  for (const c of m.contacts) if (c.w > 0.01)
    lines.push(`${c.name}: ладонь от места ${cm(c.palmAfter)}${S.correct ? ` (Kimodo: ${cm(c.palmBefore)})` : ''}`);
  for (const x of m.things) {
    if (x.lips != null) { lines.push(`край чашки от губ ${cm(x.lips)}`); continue; }
    if (x.open != null) lines.push(`дверь открыта на ${x.open.toFixed(0)}°${x.held ? ', рука на ручке' : ''}`);
    else lines.push(`${PART[cur.byId[x.id].kind] || x.id}: ${x.held ? 'в руках' : `дно над опорой ${cm(x.over)}, наклон ${x.tilt.toFixed(1)}°`}`);
  }
  const deep = m.into.filter(x => !x.grip && x.deepest > 0.005);
  lines.push(deep.length ? 'входит: ' + deep.map(x => `${PART[x.part] || x.part} ${cm(x.deepest)} (${x.by})`).join(', ') : 'тело в предметы не входит');
  $('#meter').textContent = lines.join('\n');
}

// ———— the panel ————
const panel = document.createElement('div'); panel.id = 'panel';
panel.innerHTML = `
  <h1>Вещи в руках: дверь, чашка, коробка</h1>
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
window.__moving = {
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
