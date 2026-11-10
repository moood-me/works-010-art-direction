// The page: a character of С14 «Вырезанная бумага» in 3D (view.html). window.A drives it for pictures and films
// (tools/shots.mjs):  A.set({size, motion, t, expr, talk, alive, headYaw, cam: {...}, look: {...}, ground, hide, only})
//                     A.frame({dt, ...}) — time goes on by dt;  A.render()
import { makeSkeleton } from '../../../../engine/src/skeleton.js';
import { readJSON } from '../../../../engine/src/pack.js';
import { loadMotion, clipOf } from '../../../../engine/src/motion.js';
import { getV } from '../../../../engine/src/math.js';
import { Look } from './look.js';
import { Figure, Life } from './figure.js';
import { ground } from './body.js';
import { mix } from './paper.js';
import { C } from './char.js';

const params = new URLSearchParams(location.search), SHOTS = params.has('shots');
const canvas = document.getElementById('cv');
if (SHOTS) document.getElementById('msg').style.display = 'none';
document.title = C.title + ' — вырезанная бумага в 3D';
const DATA = new URL('data/', import.meta.url);
const sk = makeSkeleton(await readJSON(new URL('skeleton.json', DATA)));
const look = new Look(canvas);
const grounds = { disc: ground(look, { color: C.groundColor }), path: ground(look, { color: C.groundColor, path: true, seed: 11 }) };
const fig = new Figure(look, sk, C);
const clips = {};
for (const m of C.motions) clips[m.id] = clipOf([await loadMotion(new URL(`motions/${m.id}.json`, DATA), sk)]);

const S = {
  size: [800, 1000], motion: null, t: 0, loop: true, expr: 'calm', talk: false, alive: true, headYaw: 0, headTilt: 0, headNod: 0, hold: true,
  heading: 0, position: [0, 0, 0], travel: [0, 0, 0], ground: 'disc', twos: false,
  cam: { ...C.view, follow: [0, C.view.h, 0], smooth: 3, target: null },
  look: { grain: 1, shadowK: 1, flat: false, bg: C.sheet }, hide: null, only: null,
};
let life = new Life(fig.spec, 7, C);

function moment() {
  const clip = S.motion ? clips[S.motion] : null;
  let t = 0; const place = { position: S.position.slice(), heading: S.heading };
  if (clip) {
    const F = clip.frames - 1; let tf = S.t * clip.fps;
    if (S.loop) {                                         // loops go on where the last one ended: the walk travels
      const n = Math.floor(tf / F); tf -= n * F;
      if (n !== S.travel[2]) {
        const mk = () => ({ q: new Float64Array(clip.J * 4), p: new Float64Array(clip.J * 3) }), end = clip.sample(F, mk()), beg = clip.sample(0, mk());
        const k = fig.retarget.k, dx = (end.p[0] - beg.p[0]) * k, dz = (end.p[2] - beg.p[2]) * k, c = Math.cos(S.heading), s = Math.sin(S.heading);
        S.travel = [n * (c * dx + s * dz), n * (-s * dx + c * dz), n];
      }
      place.position = [S.position[0] + S.travel[0], S.position[1], S.position[2] + S.travel[1]];
    } else tf = Math.min(tf, F);
    t = tf;
  }
  life.alive = S.alive; life.talk = S.talk;
  const L = { breath: () => S.alive ? life.breath() : 0, headYaw: S.headYaw + (S.alive ? life.headYaw : 0), headNod: S.headNod, headTilt: S.headTilt, nod: S.alive ? life.nod : 0 };
  fig.frame({ clip, t, place, life: L, hold: S.hold });
  fig.setFace(life.face());
}
function camera(dt) {
  const hips = getV(fig.pose.P, sk.index.Hips), c = S.cam, goal = c.target || [hips[0], c.h, hips[2]];
  if (dt == null) c.follow = goal.slice(); else { const a = 1 - Math.exp(-c.smooth * dt); for (let i = 0; i < 3; i++) c.follow[i] += (goal[i] - c.follow[i]) * a; }
  // pxu: the picture's size given as pixels in one unit of the drawing (to lay the render over the drawing)
  const f = c.follow, d = c.pxu ? S.size[1] / (2 * Math.tan(c.fov * Math.PI / 360)) * .003 / c.pxu : c.dist, cp = Math.cos(c.pitch);
  return { fov: c.fov, target: f, pos: [f[0] + Math.sin(c.yaw) * cp * d, f[1] + Math.sin(c.pitch) * d, f[2] + Math.cos(c.yaw) * cp * d] };
}
function render(dt) {
  look.resize(...S.size);
  const view = camera(dt);
  for (const k in grounds) for (const m of grounds[k]) m.visible = S.ground === k;   // 'none': no ground
  for (const p of look.pieces) if (p.name) p.mesh.visible = (!S.hide || !S.hide.some(h => p.name.startsWith(h))) && (!S.only || S.only.some(h => p.name.startsWith(h)));
  look.cam.position.set(...view.pos); look.cam.lookAt(...view.target);
  fig.face(view.pos, look.cam.quaternion.toArray());
  look.draw(view, S.look);
}
function set(o = {}) {
  const prev = S.motion;
  if (o.cam) { Object.assign(S.cam, o.cam); delete o.cam; }
  if (o.look) { Object.assign(S.look, o.look); delete o.look; }
  if (o.lifeSeed != null) life = new Life(fig.spec, o.lifeSeed, C);
  Object.assign(S, o);
  if ('expr' in o) life.setExpr(S.expr, true);
  if ('motion' in o && o.motion !== prev) S.travel = [0, 0, 0];
  moment(); camera(null);
}
let acc = 0;
function frame(o = {}) {
  const dt = o.dt ?? 1 / 30; delete o.dt; const draw = !o.skip; delete o.skip;
  if (o.cam) { Object.assign(S.cam, o.cam); delete o.cam; }
  if ('expr' in o) { S.expr = o.expr; life.setExpr(o.expr); delete o.expr; }
  Object.assign(S, o);
  life.step(dt); if (S.motion) S.t += dt;
  moment();
  if (draw) render(dt); else camera(dt);
}
window.A = { set, frame, render: () => render(), S, fig, look, C, life: () => life };

if (!SHOTS) {
  document.getElementById('msg').style.display = 'none';
  const ui = document.getElementById('ui'); ui.classList.add('on');
  const fit = () => { const w = innerWidth, h = innerHeight, k = Math.min(1, 900 / Math.max(w, h)); canvas.style.width = w + 'px'; canvas.style.height = h + 'px'; S.size = [Math.round(w * k), Math.round(h * k)]; };
  fit(); addEventListener('resize', fit);
  set({ expr: 'calm', headYaw: 0 }); S.cam.yaw = .35; S.cam.dist = 11;
  let playing = true, last = performance.now(), step = -1;
  const btn = (el, label, on) => { const b = document.createElement('button'); b.textContent = label; b.onclick = on; el.appendChild(b); return b; };
  const mB = [], eB = [], press = (list, v) => list.forEach(([b, k]) => b.setAttribute('aria-pressed', String(k === v)));
  const scrub = document.getElementById('scrub'), time = document.getElementById('time');
  const choose = id => { S.motion = id; S.t = 0; S.travel = [0, 0, 0]; S.ground = id === 'walk' ? 'path' : 'disc'; press(mB, id); scrub.max = id ? String((clips[id].frames - 1) / clips[id].fps) : '1'; };
  mB.push([btn(document.getElementById('clips'), 'стоит', () => choose(null)), null]);
  for (const m of C.motions) mB.push([btn(document.getElementById('clips'), m.label, () => choose(m.id)), m.id]);
  for (const [k, l] of C.exprs) eB.push([btn(document.getElementById('exprs'), l, () => { S.expr = k; life.setExpr(k); press(eB, k); }), k]);
  press(mB, null); press(eB, 'calm');
  const tog = (id, get, flip) => { const b = document.getElementById(id); b.onclick = () => { flip(); b.setAttribute('aria-pressed', String(get())); }; };
  tog('talk', () => S.talk, () => S.talk = !S.talk);
  tog('twos', () => S.twos, () => S.twos = !S.twos);
  tog('flat', () => !S.look.flat, () => S.look.flat = !S.look.flat);
  const playB = document.getElementById('play'); playB.onclick = () => { playing = !playing; playB.textContent = playing ? 'пауза' : 'играть'; };
  scrub.oninput = () => { if (S.motion) { S.t = +scrub.value; S.travel = [0, 0, 0]; } };
  document.getElementById('fold').onclick = () => ui.classList.toggle('folded');
  let drag = null;
  canvas.addEventListener('pointerdown', e => { drag = [e.clientX, e.clientY]; canvas.setPointerCapture(e.pointerId); });
  canvas.addEventListener('pointermove', e => { if (!drag) return; S.cam.yaw -= (e.clientX - drag[0]) * .008; S.cam.pitch = Math.max(-.1, Math.min(.8, S.cam.pitch + (e.clientY - drag[1]) * .005)); drag = [e.clientX, e.clientY]; });
  canvas.addEventListener('pointerup', () => { drag = null; });
  canvas.addEventListener('wheel', e => { e.preventDefault(); S.cam.dist = Math.max(2.5, Math.min(22, S.cam.dist * Math.exp(e.deltaY * .001))); S.cam.h = S.cam.dist < 6 ? 1.45 : C.view.h; }, { passive: false });
  const tick = now => {
    let dt = Math.min(.1, (now - last) / 1000); last = now;
    if (S.twos) { acc += dt; const n = Math.floor(acc * 12); if (n === step) { requestAnimationFrame(tick); return; } dt = (n - step) / 12; if (step < 0) dt = 1 / 12; step = n; } else step = -1, acc = 0;
    life.step(dt);
    if (playing && S.motion) { S.t += dt; const len = (clips[S.motion].frames - 1) / clips[S.motion].fps; if (!S.loop && S.t > len) S.t = 0; scrub.value = String(S.t % len); time.textContent = (S.t % len).toFixed(1) + ' с'; }
    moment(); render(dt);
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
window.__ready = true;
