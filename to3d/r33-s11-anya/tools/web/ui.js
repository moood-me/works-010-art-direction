// The viewer's controls: turn with the mouse (drag; wheel or pinch to come closer), a motion, an expression or a mix,
// speech on and off, colour or black-and-white film, the face close, play / pause / scrub. Off with ?shots.
import { EXPR_RU } from './face.js';
const qs = new URLSearchParams(location.search);
if (!qs.has('shots')) {
  while (!window.__ready) await new Promise(r => setTimeout(r, 50));
  const A = window.A, st = A.st, ui = document.getElementById('ui'), msg = document.getElementById('msg'), cv = document.getElementById('cv');
  const S = { clip: 'stand', expr: { neutral: 1 }, talk: false, playing: true, t: 0, dur: 6, close: false };
  const size = () => [innerWidth, innerHeight];
  const frameCam = () => {
    const close = S.close;
    Object.assign(st.cam, { mode: 'persp', fov: 24, follow: true, followHead: close, followY: S.clip === 'sit' ? 0.75 : 1.0 }); A.camK = 1;
    st.cam.dist = close ? 2.9 : (S.clip === 'dance' || S.clip === 'jump' ? 8.8 : 8.0);
  };
  async function place() {
    await A.set({ size: size(), clip: S.clip, t: 0, expr: S.expr, talk: S.talk, still: false, settle: false });
    S.dur = A.duration(); S.t = 0; frameCam();
  }
  st.cam.yaw = 28; st.cam.pitch = 6;
  await place();
  msg.remove(); ui.classList.add('on');
  const fold = document.getElementById('fold');
  const pad = () => { st.cam.pad = ui.classList.contains('folded') ? 0 : ui.offsetHeight + 12; };
  fold.addEventListener('click', () => { ui.classList.toggle('folded'); fold.textContent = ui.classList.contains('folded') ? 'настройки' : 'свернуть'; pad(); });
  new ResizeObserver(pad).observe(ui); pad();
  const press = (box, key, v) => box.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset[key] === v)));
  const clips = document.getElementById('clips'), exprs = document.getElementById('exprs'), mix = document.getElementById('mix');
  for (const [id, c] of Object.entries(A.CLIPS)) { const b = document.createElement('button'); b.textContent = c.ru; b.dataset.clip = id; b.setAttribute('aria-pressed', String(id === S.clip)); clips.appendChild(b); }
  const sliders = {};
  const send = () => { A.ch.live.setExpr(S.expr); A.ch.live.setTalk(S.talk); };
  for (const [id, ru] of Object.entries(EXPR_RU)) {
    const b = document.createElement('button'); b.textContent = ru; b.dataset.expr = id; b.setAttribute('aria-pressed', String(id === 'neutral')); exprs.appendChild(b);
    const l = document.createElement('label'); l.textContent = ru; const r = document.createElement('input'); r.type = 'range'; r.min = 0; r.max = 1; r.step = 0.05; r.value = id === 'neutral' ? 1 : 0; l.appendChild(r); mix.appendChild(l); sliders[id] = r;
    r.addEventListener('input', () => { S.expr = Object.fromEntries(Object.entries(sliders).map(([k, s]) => [k, +s.value])); press(exprs, 'expr', null); send(); });
  }
  clips.addEventListener('click', async e => { const id = e.target.dataset.clip; if (!id) return; S.clip = id; press(clips, 'clip', id); await place(); });
  exprs.addEventListener('click', e => { const id = e.target.dataset.expr; if (!id) return; S.expr = { [id]: 1 }; for (const [k, s] of Object.entries(sliders)) s.value = k === id ? 1 : 0; press(exprs, 'expr', id); send(); });
  const mixb = document.getElementById('mixb'); mixb.addEventListener('click', () => { const on = mix.classList.toggle('on'); mixb.setAttribute('aria-pressed', String(on)); });
  const talk = document.getElementById('talk'); talk.addEventListener('click', () => { S.talk = !S.talk; talk.setAttribute('aria-pressed', String(S.talk)); send(); });
  const film = document.getElementById('film'), bw = document.getElementById('bw'), close = document.getElementById('close');
  film.addEventListener('click', () => { st.post.uniforms.uBW.value = 0; film.setAttribute('aria-pressed', 'true'); bw.setAttribute('aria-pressed', 'false'); });
  bw.addEventListener('click', () => { st.post.uniforms.uBW.value = 1; bw.setAttribute('aria-pressed', 'true'); film.setAttribute('aria-pressed', 'false'); });
  close.addEventListener('click', () => { S.close = !S.close; close.setAttribute('aria-pressed', String(S.close)); frameCam(); });
  const play = document.getElementById('play'), scrub = document.getElementById('scrub'), time = document.getElementById('time');
  play.addEventListener('click', () => { S.playing = !S.playing; play.textContent = S.playing ? 'пауза' : 'играть'; play.setAttribute('aria-pressed', String(S.playing)); });
  let scrubbing = false;
  scrub.addEventListener('input', () => { scrubbing = true; S.t = +scrub.value * S.dur; });
  scrub.addEventListener('change', () => { scrubbing = false; });
  const pts = new Map(); let drag = null;
  cv.addEventListener('pointerdown', e => { cv.setPointerCapture(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]); drag = { x: e.clientX, y: e.clientY, d: null }; cv.style.cursor = 'grabbing'; });
  cv.addEventListener('pointermove', e => {
    if (!pts.has(e.pointerId)) return;
    pts.set(e.pointerId, [e.clientX, e.clientY]);
    if (pts.size === 2) { const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]); if (drag.d) st.cam.dist = Math.min(14, Math.max(1.0, st.cam.dist * drag.d / d)); drag.d = d; return; }
    st.cam.yaw -= (e.clientX - drag.x) * 0.4; st.cam.pitch = Math.min(60, Math.max(-10, st.cam.pitch + (e.clientY - drag.y) * 0.25)); drag.x = e.clientX; drag.y = e.clientY;
  });
  const up = e => { pts.delete(e.pointerId); if (!pts.size) { drag = null; cv.style.cursor = 'grab'; } };
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  cv.addEventListener('wheel', e => { e.preventDefault(); st.cam.dist = Math.min(14, Math.max(1.0, st.cam.dist * Math.exp(e.deltaY * 0.001))); }, { passive: false });
  addEventListener('resize', () => st.size(...size()));
  // the loop: the motion runs with play (a clip loops; sitting stays down a while); the face lives on always
  let last = performance.now();
  function tick(now) {
    const dt = Math.min(0.1, (now - last) / 1000); last = now;
    if (S.playing && !scrubbing) S.t += dt;
    const hold = S.clip === 'sit' || S.clip === 'bow';
    if (hold && S.t > S.dur + 2) S.t = 0;
    const t = hold ? Math.min(S.t, S.dur - 1e-3) : S.t % S.dur;
    A.frame({ t, dt });
    A.render();
    if (!scrubbing) scrub.value = t / S.dur;
    time.textContent = t.toFixed(1) + ' с';
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}
