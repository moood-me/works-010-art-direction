// The viewer's controls (not in shots mode): turn with the mouse, zoom with the wheel; choose a motion and an
// expression (it blends in), talk on/off, play/pause, scrub. Everything goes through window.A (tim.js).
const q = new URLSearchParams(location.search);
if (q.get('shots')) { document.body.classList.add('shots'); document.documentElement.style.background = 'transparent'; }
else {
  while (!window.__ready) await new Promise(r => setTimeout(r, 50));
  const A = window.A, $ = id => document.getElementById(id), canvas = $('c');
  const MOTIONS = [[null, 'стоит'], ['walk', 'шаг'], ['run', 'бег'], ['sneak', 'крадётся'], ['wave', 'машет'], ['jump', 'прыжок'],
    ['dance', 'танец'], ['bow', 'поклон'], ['stomp', 'топает'], ['idle', 'оглядывается']];
  const EXPR = [['calm', 'спокойно'], ['joy', 'радость'], ['surprise', 'удивление'], ['sad', 'грусть'], ['anger', 'злость']];
  const st = { motion: 'walk', frames: 120, fps: 30, t: 0, play: true, talk: false, clock: 0, yaw: -0.5, pitch: 0.08, dist: 6.0, expr: [{ t: 0, name: 'calm' }], cur: 'calm' };
  for (const [id, name] of MOTIONS) { const o = document.createElement('option'); o.value = id ?? ''; o.textContent = name; $('motion').append(o); }
  $('motion').value = st.motion;
  for (const [id, name] of EXPR) {
    const b = document.createElement('button'); b.textContent = name; b.dataset.id = id; if (id === 'calm') b.classList.add('on');
    b.onclick = () => { const now = face(); st.expr = [{ t: 0, name: st.cur }, { t: now, name: id }]; st.cur = id;
      [...$('exprs').children].forEach(x => x.classList.toggle('on', x === b)); };
    $('exprs').append(b);
  }
  const face = () => st.motion ? st.t / st.fps : st.clock;
  async function pickMotion(id) {
    st.motion = id || null; st.t = 0;
    await A.set({ motion: st.motion ? [st.motion] : null, t: 0 });
    const info = A.clipInfo(); st.frames = info ? info.frames : 1; st.fps = info ? info.fps : 30;
    $('scrub').max = Math.max(1, st.frames - 1);
  }
  $('motion').onchange = e => pickMotion(e.target.value);
  $('play').onclick = () => { st.play = !st.play; $('play').textContent = st.play ? 'пауза' : 'играть'; };
  $('talk').onclick = () => { st.talk = !st.talk; $('talk').classList.toggle('on', st.talk); };
  $('scrub').oninput = e => { st.t = +e.target.value; };
  // the mouse turns the camera round him, the wheel brings it nearer
  let drag = null;
  canvas.onpointerdown = e => { drag = [e.clientX, e.clientY, st.yaw, st.pitch]; canvas.setPointerCapture(e.pointerId); canvas.style.cursor = 'grabbing'; };
  canvas.onpointermove = e => { if (!drag) return; st.yaw = drag[2] - (e.clientX - drag[0]) * 0.008; st.pitch = Math.max(-0.4, Math.min(1.2, drag[3] + (e.clientY - drag[1]) * 0.006)); };
  canvas.onpointerup = () => { drag = null; canvas.style.cursor = 'grab'; };
  canvas.onwheel = e => { e.preventDefault(); st.dist = Math.max(1.2, Math.min(9, st.dist * Math.exp(e.deltaY * 0.001))); };
  await pickMotion(st.motion);
  let last = performance.now(), busy = false;
  async function frame(now) {
    const dt = Math.min(0.1, (now - last) / 1000); last = now;
    if (!busy) {
      busy = true;
      if (st.play) { st.clock += dt; if (st.motion) { st.t += dt * st.fps; if (st.t > st.frames - 1) st.t = 0; } }
      const w = innerWidth, h = innerHeight;
      await A.set({ ground: true, t: st.t, expr: st.expr, talk: st.talk, faceTime: face(), w: Math.round(w * Math.min(devicePixelRatio, 2)), h: Math.round(h * Math.min(devicePixelRatio, 2)),
        cam: { yaw: st.yaw, pitch: st.pitch, dist: st.dist, follow: [0, 0.85, 0], fov: 22 } });
      canvas.style.width = '100%'; canvas.style.height = '100%';
      A.render();
      $('scrub').value = st.t; $('time').textContent = st.motion ? `${(st.t / st.fps).toFixed(1)} с` : '';
      busy = false;
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}
