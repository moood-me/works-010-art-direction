// The viewer by hand (Р12's, to3d/r12-s12-anya; the expressions and the views are the character's, from char.js): turn with the mouse (wheel — nearer), choose the motion, play / pause / scrub,
// the sheet's expressions (a button — that one; the sliders mix them), talk on/off, the face close. The picture is drawn
// anew 12 times a second — as a hand-drawn film is, a drawing held for two frames.
const MOTIONS = [['', 'стоит'], ['idle', 'стоит, оглядывается'], ['walk', 'шаг'], ['wave', 'машет'], ['sit', 'садится'],
  ['bow', 'поклон'], ['stomp', 'топает'], ['dance', 'танец'], ['jump', 'прыжок'], ['run', 'бег'], ['sneak', 'крадётся']];
import * as CH from './char.js';
const EXPR = CH.NAMES.map(n => [n, CH.LABELS[n]]);

export function ui(A, stage) {
  const css = document.createElement('style');
  css.textContent = `
  #ui { position: fixed; left: 10px; top: 10px; z-index: 4; width: min(330px, calc(100vw - 20px)); max-height: calc(100vh - 20px); overflow-y: auto;
    background: rgba(255,253,249,.93); border-radius: 10px; padding: 10px 12px; box-shadow: 0 2px 10px rgba(0,0,0,.15);
    font: 13px/1.4 system-ui, sans-serif; color: #26231f; display: grid; gap: 7px; }
  #ui .row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
  #ui select, #ui button { font: inherit; border: 1px solid #d5cec4; background: #fff; border-radius: 6px; padding: 3px 9px; cursor: pointer; color: inherit; }
  #ui button[aria-pressed="true"] { background: #b4532a; border-color: #b4532a; color: #fff; }
  #ui input[type=range] { flex: 1; min-width: 80px; accent-color: #b4532a; }
  #ui .lab { color: #75706a; font-size: 12px; min-width: 72px; }
  #ui .hint { color: #75706a; font-size: 12px; }`;
  document.head.appendChild(css);
  const box = document.createElement('div'); box.id = 'ui'; document.body.appendChild(box);
  box.innerHTML = `
    <div class="row"><span class="lab">движение</span><select id="mv">${MOTIONS.map(([v, l]) => `<option value="${v}">${l}</option>`).join('')}</select>
      <button id="play" aria-pressed="true">▶︎ ❚❚</button></div>
    <div class="row"><input id="scrub" type="range" min="0" max="1" step="1" value="0"><span id="tt" class="hint"></span></div>
    <div class="row">${EXPR.map(([v, l]) => `<button data-e="${v}">${l}</button>`).join('')}</div>
    ${EXPR.map(([v, l]) => `<div class="row"><span class="lab">${l}</span><input data-w="${v}" type="range" min="0" max="1" step="0.01" value="${v === CH.NAMES[0] ? 1 : 0}"></div>`).join('')}
    <div class="row"><button id="talk" aria-pressed="false">говорит</button><button id="close" aria-pressed="false">лицо крупно</button><button id="home">вид спереди</button></div>
    <div class="hint">Тянуть мышью — повернуть, колесо — ближе. Каждый кадр заново нарисован пером и акварелью по 3D: контуры, заливки, лицо. Моргание, взгляд и речь — по своим часам, движение — Kimodo через движок.</div>`;
  const $ = s => box.querySelector(s);
  let playing = true, t = 0, last = performance.now(), frames = 0, fps = 30, lastDraw = 0;
  const t0 = performance.now(), clock = () => (performance.now() - t0) / 1000;
  const far = { mode: 'persp', dist: 5.6, fov: 22, cy: 0.86, follow: true, focus: null, yaw: 0.5, pitch: 0.05, ...(CH.VIEW?.far || {}) };
  const near = { mode: 'persp', dist: 1.6, fov: 22, follow: false, focus: 'Head', up: 0.05, pitch: 0.03, ...(CH.VIEW?.near || {}) };
  A.set({ liveClock: true, cam: far, pose: 'stand', poseOpts: {}, anchorGrain: true });
  async function motion(id) {
    await A.set({ clip: id || null, t: 0, time: clock() });
    const c = A.clipInfo(); frames = c ? c.frames : 0; fps = c ? c.fps : 30; t = 0;
    $('#scrub').max = Math.max(1, frames - 1);
  }
  $('#mv').onchange = e => motion(e.target.value);
  $('#play').onclick = e => { playing = !playing; e.target.setAttribute('aria-pressed', playing); };
  $('#scrub').oninput = e => { t = Number(e.target.value); };
  const sliders = [...box.querySelectorAll('[data-w]')];
  const weights = () => Object.fromEntries(sliders.map(s => [s.dataset.w, Number(s.value)]));
  for (const b of box.querySelectorAll('[data-e]')) b.onclick = () => { for (const s of sliders) s.value = s.dataset.w === b.dataset.e ? 1 : 0; A.set({ time: clock(), expr: weights() }); };
  for (const s of sliders) s.oninput = () => A.set({ time: clock(), expr: weights() });
  $('#talk').onclick = e => { const on = e.target.getAttribute('aria-pressed') !== 'true'; e.target.setAttribute('aria-pressed', on); A.set({ time: clock(), talk: on }); };
  $('#close').onclick = e => { const on = e.target.getAttribute('aria-pressed') !== 'true'; e.target.setAttribute('aria-pressed', on); A.set({ cam: { ...(on ? near : far), yaw: A.S.cam.yaw } }); };
  $('#home').onclick = () => A.set({ cam: { yaw: A.facing(), pitch: 0.04 } });
  let drag = null;
  stage.addEventListener('pointerdown', e => { drag = [e.clientX, e.clientY, A.S.cam.yaw, A.S.cam.pitch]; stage.setPointerCapture(e.pointerId); });
  stage.addEventListener('pointerup', () => { drag = null; });
  stage.addEventListener('pointermove', e => { if (!drag) return; A.S.cam.yaw = drag[2] - (e.clientX - drag[0]) * 0.01; A.S.cam.pitch = Math.max(-0.5, Math.min(0.9, drag[3] + (e.clientY - drag[1]) * 0.005)); });
  stage.addEventListener('wheel', e => { e.preventDefault(); A.S.cam.dist = Math.max(0.6, Math.min(14, A.S.cam.dist * Math.exp(e.deltaY * 0.001))); }, { passive: false });
  stage.style.touchAction = 'none';
  const loop = async () => {
    const now = performance.now(), dt = (now - last) / 1000; last = now;
    if (frames && playing) { t += dt * fps; if (t > frames - 1) t = 0; $('#scrub').value = t; }
    $('#tt').textContent = frames ? (t / fps).toFixed(1) + ' с' : '';
    if (now - lastDraw > 1000 / 12) { lastDraw = now; await A.set({ t, time: clock() }); A.render(); }
    requestAnimationFrame(loop);
  };
  loop();
}
