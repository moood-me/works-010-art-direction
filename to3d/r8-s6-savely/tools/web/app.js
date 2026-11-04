// The page: Савелий Петрович on his dusk street (view.html). window.A drives it for pictures and films (tools/shots.mjs):
//   A.set({size, stat | motion, t, mood, talk, breath, view, look, lamp, plate, lightDir, ...}) — what to show
//   A.frame({dt, ...}) — time goes on by dt seconds (motion, breathing, mood springs, talking, the following camera)
//   A.render()
import { loadSavely, Stage, Life, MOTIONS, getMotion } from './savely.js';
import { clipOf } from '../../../../engine/src/motion.js';
import { getV } from '../../../../engine/src/math.js';

const params = new URLSearchParams(location.search), SHOTS = params.has('shots');
const canvas = document.getElementById('cv');
const data = await loadSavely();
const stage = new Stage(canvas, data);
const clips = {};
for (const m of MOTIONS) clips[m.id] = clipOf([await getMotion(m.id, data.sk)]);

const S = {
  size: [800, 800], stat: 'drawn', motion: null, t: 0, mood: null, talk: false, breath: true, loop: true,
  view: null, look: {}, lamp: [1.15, 0, -1.5], lampYaw: 0, plate: null, lightDir: null, heading: 0, position: [0, 0, 0],
  // the following camera: its turn about him, height of its eye, distance, and where it looks (smoothed)
  cam: { yaw: 0.35, pitch: 0.06, dist: 3.6, h: .95, fov: 30, follow: [0, .8, 0], smooth: 3 },
  seed: 0, life: null, travel: [0, 0],
};
let life = new Life(data, 7);

function moment(o = {}) {
  const clip = S.motion ? clips[S.motion] : null;
  let t = 0, place = { position: S.position.slice(), heading: S.heading };
  if (clip) {
    const F = clip.frames - 1;
    let tf = S.t * clip.fps;
    if (S.loop) {
      // loops go on where the last one ended (the walk travels on; never on the spot)
      const n = Math.floor(tf / F); tf -= n * F;
      if (n !== S.travel[2]) {
        const end = clip.sample(F, { q: new Float64Array(clip.J * 4), p: new Float64Array(clip.J * 3) }), beg = clip.sample(0, { q: new Float64Array(clip.J * 4), p: new Float64Array(clip.J * 3) });
        const k = stage.poser.retarget.k, dx = (end.p[0] - beg.p[0]) * k, dz = (end.p[2] - beg.p[2]) * k;
        const c = Math.cos(S.heading), s = Math.sin(S.heading);
        S.travel = [n * (c * dx + s * dz), n * (-s * dx + c * dz), n];
      }
      place.position = [S.position[0] + S.travel[0], S.position[1], S.position[2] + S.travel[1]];
    } else tf = Math.min(tf, F);
    t = tf;
  }
  const stat = clip ? null : (S.stat === 'drawn' || S.stat === 'rest' ? data.poses[S.stat] : data.poses.moods[S.stat]);
  stage.poser.frame({ clip, t, stat, life: S.breath || S.talk || S.mood || clip ? life : null, place, normals: !!S.look.shaded });
}

function camera(dt) {
  if (S.view) return S.view;
  const hips = getV(stage.poser.pose.P, data.sk.index.Hips), c = S.cam;
  const goal = [hips[0], c.h, hips[2]];
  if (dt == null) c.follow = goal;
  else { const a = 1 - Math.exp(-c.smooth * dt); for (let i = 0; i < 3; i++) c.follow[i] += (goal[i] - c.follow[i]) * a; }
  const f = c.follow, d = c.dist, cp = Math.cos(c.pitch);
  return { type: 'persp', fov: c.fov, target: [f[0], f[1] - .05, f[2]], pos: [f[0] + Math.sin(c.yaw) * cp * d, f[1] + Math.sin(c.pitch) * d, f[2] + Math.cos(c.yaw) * cp * d] };
}

function render(dt) {
  const [w, h] = S.size;
  stage.resize(w, h);
  stage.draw({ view: camera(dt), look: S.look, lamp: S.lamp, lampYaw: S.lampYaw, plate: S.plate, lightDir: S.lightDir, seed: S.seed, rimScale: S.rimScale, lampVisible: S.lampVisible, grain: S.grain, vign: S.vign });
}

function set(o = {}) {
  const prev = { motion: S.motion, mood: S.mood };
  if (o.cam) { Object.assign(S.cam, o.cam); delete o.cam; }
  Object.assign(S, o);
  if (o.lifeSeed != null) life = new Life(data, o.lifeSeed);
  if ('mood' in o) life.setMood(S.mood, !!o.snap);
  if ('motion' in o && o.motion !== prev.motion) S.travel = [0, 0, 0];
  life.talk = S.talk;
  moment();
  camera(null);
}
function frame(o = {}) {
  const dt = o.dt ?? 1 / 30; delete o.dt;
  const draw = !o.skip; delete o.skip;
  if (o.cam) { Object.assign(S.cam, o.cam); delete o.cam; }
  if ('mood' in o) { S.mood = o.mood; life.setMood(S.mood); delete o.mood; }
  if ('talk' in o) { S.talk = o.talk; life.talk = S.talk; delete o.talk; }
  Object.assign(S, o);
  life.step(dt);
  if (S.motion) S.t += dt;
  S.seed = (S.seed + 1) % 997;
  moment();
  if (draw) render(dt); else camera(dt);
}
window.A = { set, frame, render: () => render(), S, stage, data };

// ------------------------------------------------------------------ the viewer
if (!SHOTS) {
  const msg = document.getElementById('msg'); msg.style.display = 'none';
  const ui = document.getElementById('ui'); ui.classList.add('on');
  const fit = () => { const w = innerWidth, h = innerHeight; canvas.style.width = w + 'px'; canvas.style.height = h + 'px'; S.size = [Math.round(w * Math.min(devicePixelRatio, 1.5)), Math.round(h * Math.min(devicePixelRatio, 1.5))]; };
  fit(); addEventListener('resize', fit);
  set({ stat: 'drawn', mood: 'watch', snap: true, motion: null, lamp: [1.15, 0, -1.5] });
  S.cam.yaw = 1.2;
  let playing = true, last = performance.now();
  const motionsEl = document.getElementById('clips'), moodsEl = document.getElementById('moods');
  const btn = (el, label, on) => { const b = document.createElement('button'); b.textContent = label; b.onclick = on; el.appendChild(b); return b; };
  const motionBtns = [];
  const choose = id => {
    S.motion = id; S.t = 0; S.travel = [0, 0, 0];
    if (!id) S.stat = 'drawn';
    // the lamp stands where he will pass it
    S.lamp = id === 'walk' ? [3.2, 0, -1.4] : [1.15, 0, -1.5];
    for (const [b, m] of motionBtns) b.setAttribute('aria-pressed', String(m === id));
    scrub.max = id ? String((clips[id].frames - 1) / clips[id].fps) : '1';
  };
  motionBtns.push([btn(motionsEl, 'стоит у фонаря', () => choose(null)), null]);
  for (const m of MOTIONS) motionBtns.push([btn(motionsEl, m.label, () => choose(m.id)), m.id]);
  motionBtns[0][0].setAttribute('aria-pressed', 'true');
  const moodBtns = [];
  const setMoodUI = k => { S.mood = k; life.setMood(k); for (const [b, kk] of moodBtns) b.setAttribute('aria-pressed', String(kk === k)); };
  moodBtns.push([btn(moodsEl, 'без позы', () => setMoodUI(null)), null]);
  for (const [k, m] of Object.entries(data.poses.moods)) moodBtns.push([btn(moodsEl, m.label, () => setMoodUI(k)), k]);
  setMoodUI('watch');
  const talkB = document.getElementById('talk'); talkB.onclick = () => { S.talk = !S.talk; life.talk = S.talk; talkB.setAttribute('aria-pressed', String(S.talk)); };
  const playB = document.getElementById('play'); playB.onclick = () => { playing = !playing; playB.textContent = playing ? 'пауза' : 'играть'; playB.setAttribute('aria-pressed', String(playing)); };
  const scrub = document.getElementById('scrub'), time = document.getElementById('time');
  scrub.oninput = () => { if (S.motion) { S.t = +scrub.value; S.travel = [0, 0, 0]; } };
  document.getElementById('fold').onclick = () => ui.classList.toggle('folded');
  // turn with the mouse / a finger; come closer with the wheel
  let drag = null;
  canvas.addEventListener('pointerdown', e => { drag = [e.clientX, e.clientY]; canvas.setPointerCapture(e.pointerId); canvas.style.cursor = 'grabbing'; });
  canvas.addEventListener('pointermove', e => { if (!drag) return; S.cam.yaw -= (e.clientX - drag[0]) * .008; S.cam.pitch = Math.max(-.15, Math.min(.9, S.cam.pitch + (e.clientY - drag[1]) * .005)); drag = [e.clientX, e.clientY]; });
  canvas.addEventListener('pointerup', () => { drag = null; canvas.style.cursor = 'grab'; });
  canvas.addEventListener('wheel', e => { e.preventDefault(); S.cam.dist = Math.max(1.4, Math.min(9, S.cam.dist * Math.exp(e.deltaY * .001))); }, { passive: false });
  const tick = now => {
    const dt = Math.min(.1, (now - last) / 1000); last = now;
    life.step(playing ? dt : 0);
    if (playing && S.motion) {
      S.t += dt;
      const clip = clips[S.motion], len = (clip.frames - 1) / clip.fps;
      if (S.motion !== 'walk' && S.t > len + 1.2) { S.t = 0; }
    }
    if (S.motion) { const clip = clips[S.motion], len = (clip.frames - 1) / clip.fps; scrub.value = String(S.t % len); time.textContent = (S.t % len).toFixed(1) + ' с'; }
    else time.textContent = '';
    S.loop = S.motion === 'walk' || S.motion === 'idle';
    S.seed = (S.seed + 1) % 997;
    moment(); render(playing ? dt : 0);
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
document.getElementById('msg').style.display = 'none';
window.__ready = true;
