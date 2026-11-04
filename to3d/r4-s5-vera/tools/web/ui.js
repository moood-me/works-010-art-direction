// The viewer: Вера turned with the mouse (drag; wheel or pinch to come closer), a motion, an expression or a mix of
// them, speech on and off, play / pause / scrub. Off when the page is opened with ?shots (pictures for the page).
import { EXPR_RU } from './face.js';
if (!new URLSearchParams(location.search).has('shots') && !new URLSearchParams(location.search).has('blank')) {
  while (!window.__ready) await new Promise(r => setTimeout(r, 50));
  const A = window.A, ui = document.getElementById('ui'), msg = document.getElementById('msg');
  const S = { clip: 'stand', expr: { neutral: 1 }, talk: false, playing: true, t: 0, dur: 4 };
  const CAM = { stand: [0.55, 3.0], walk: [0.55, 3.2], sit: [0.38, 2.9], idle: [0.55, 3.0], look: [0.7, 2.2], wave: [0.6, 3.3] };
  const size = () => [innerWidth, innerHeight];
  async function place() {
    await A.set({ size: size(), floor: true, view: 'style', line: 2.1, figures: [{ clip: S.clip, live: true, exprW: S.expr, talk: S.talk, yaw: 0 }] });
    const I = A.placed()[0];
    S.dur = I.M ? I.M.n / I.M.fps : 6;
    A.cam.ty = CAM[S.clip][0]; if (!placed) A.cam.dist = CAM[S.clip][1];
    A.setCam({ follow: true, fov: 24 });
    S.t = 0; placed = true;
  }
  let placed = false;
  A.setCam({ yaw: 28, pitch: 7, dist: 3.0, ty: 0.55, fov: 24, follow: true });
  await place();
  msg.remove(); ui.classList.add('on');
  // the controls cover the bottom: the picture is centred above them (and fills the window when they are folded)
  const fold = document.getElementById('fold');
  const pad = () => { A.cam.pad = ui.classList.contains('folded') ? 0 : ui.offsetHeight + 12; };
  fold.addEventListener('click', () => { ui.classList.toggle('folded'); fold.textContent = ui.classList.contains('folded') ? 'настройки' : 'свернуть'; pad(); });
  new ResizeObserver(pad).observe(ui); pad();
  // controls
  const clips = document.getElementById('clips'), exprs = document.getElementById('exprs'), mix = document.getElementById('mix');
  for (const [id, c] of Object.entries(A.CLIPS)) { const b = document.createElement('button'); b.textContent = c.ru; b.dataset.clip = id; b.setAttribute('aria-pressed', String(id === S.clip)); clips.appendChild(b); }
  const sliders = {};
  for (const [id, ru] of Object.entries(EXPR_RU)) {
    const b = document.createElement('button'); b.textContent = ru; b.dataset.expr = id; b.setAttribute('aria-pressed', String(id === 'neutral')); exprs.appendChild(b);
    const l = document.createElement('label'); l.textContent = ru; const r = document.createElement('input'); r.type = 'range'; r.min = 0; r.max = 1; r.step = 0.05; r.value = id === 'neutral' ? 1 : 0; l.appendChild(r); mix.appendChild(l); sliders[id] = r;
    r.addEventListener('input', () => { S.expr = Object.fromEntries(Object.entries(sliders).map(([k, s]) => [k, +s.value])); press(exprs, 'expr', null); send(); });
  }
  const press = (box, key, v) => box.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset[key] === v)));
  const send = () => { const I = A.placed()[0]; if (I && I.live) { I.live.setExpr(S.expr); I.live.setTalk(S.talk); } };
  clips.addEventListener('click', async e => { const id = e.target.dataset.clip; if (!id) return; S.clip = id; press(clips, 'clip', id); await place(); });
  exprs.addEventListener('click', e => { const id = e.target.dataset.expr; if (!id) return; S.expr = { [id]: 1 }; for (const [k, s] of Object.entries(sliders)) s.value = k === id ? 1 : 0; press(exprs, 'expr', id); send(); });
  const mixb = document.getElementById('mixb'); mixb.addEventListener('click', () => { const on = mix.classList.toggle('on'); mixb.setAttribute('aria-pressed', String(on)); });
  const talk = document.getElementById('talk'); talk.addEventListener('click', () => { S.talk = !S.talk; talk.setAttribute('aria-pressed', String(S.talk)); send(); });
  const play = document.getElementById('play'), scrub = document.getElementById('scrub'), time = document.getElementById('time');
  play.addEventListener('click', () => { S.playing = !S.playing; play.textContent = S.playing ? 'пауза' : 'играть'; play.setAttribute('aria-pressed', String(S.playing)); });
  let scrubbing = false;
  scrub.addEventListener('input', () => { scrubbing = true; S.t = +scrub.value * S.dur; });
  scrub.addEventListener('change', () => { scrubbing = false; });
  // turning and coming closer
  const cv = document.getElementById('cv'); let drag = null; const pts = new Map();
  cv.addEventListener('pointerdown', e => { cv.setPointerCapture(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]); drag = { x: e.clientX, y: e.clientY, d: null }; cv.style.cursor = 'grabbing'; });
  cv.addEventListener('pointermove', e => {
    if (!pts.has(e.pointerId)) return;
    pts.set(e.pointerId, [e.clientX, e.clientY]);
    if (pts.size === 2) { const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]); if (drag.d) A.cam.dist = Math.min(8, Math.max(0.8, A.cam.dist * drag.d / d)); drag.d = d; return; }
    A.cam.yaw -= (e.clientX - drag.x) * 0.4; A.cam.pitch = Math.min(60, Math.max(-10, A.cam.pitch + (e.clientY - drag.y) * 0.25)); drag.x = e.clientX; drag.y = e.clientY;
  });
  const up = e => { pts.delete(e.pointerId); if (!pts.size) { drag = null; cv.style.cursor = 'grab'; } };
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  cv.addEventListener('wheel', e => { e.preventDefault(); A.cam.dist = Math.min(8, Math.max(0.8, A.cam.dist * Math.exp(e.deltaY * 0.001))); }, { passive: false });
  addEventListener('resize', () => A.set({ size: size() }).then(() => A.aimCam(true)));
  // the loop: the motion runs with play; the face lives on always (blinks, gaze, speech), as a person does
  let last = performance.now();
  function tick(now) {
    const dt = Math.min(0.1, (now - last) / 1000); last = now;
    if (S.playing && !scrubbing) S.t += dt;
    const loopT = S.clip === 'sit' || S.clip === 'stand' ? Math.min(S.t, S.dur - 1e-3) : S.t;
    if (S.clip === 'sit' && S.t > S.dur + 2) S.t = 0;
    A.frame({ t: loopT, dt });
    A.render();
    if (!scrubbing) scrub.value = (loopT % S.dur) / S.dur;
    time.textContent = (loopT % S.dur).toFixed(1) + ' с';
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
if (new URLSearchParams(location.search).has('shots')) document.getElementById('msg')?.remove();
