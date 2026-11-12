// The viewer's controls (not in shots mode): turn with the mouse, zoom with the wheel; choose a motion and an
// expression (it blends in), talk on/off, the face nearer, play/pause, scrub. Everything goes through window.A (kira.js).
const q = new URLSearchParams(location.search);
if (q.get('shots')) document.body.classList.add('shots');
else {
  while (!window.__ready) await new Promise(r => setTimeout(r, 50));
  const A = window.A, $ = id => document.getElementById(id), canvas = $('c');
  const MOTIONS = [['idle', 'стоит, оглядывается'], ['walk', 'идёт'], ['sneak', 'крадётся'], ['wave', 'машет'], ['sit', 'садится'], ['stomp', 'топает'],
    ['run', 'бежит'], ['jump', 'прыгает'], ['bow', 'кланяется'], ['dance', 'танцует']];
  const EXPR = [['calm', 'как обычно'], ['joy', 'усмешка'], ['surprise', 'удивление'], ['sad', 'грусть'], ['angry', 'злость']];
  const st = { motion: 'idle', frames: 120, fps: 30, t: 0, play: true, talk: false, close: false, clock: 0, yaw: -0.45, pitch: 0.06, dist: 5.2, expr: [{ t: 0, name: 'calm' }], cur: 'calm' };
  for (const [id, name] of MOTIONS) { const o = document.createElement('option'); o.value = id; o.textContent = name; $('motion').append(o); }
  $('motion').value = st.motion;
  for (const [id, name] of EXPR) {
    const b = document.createElement('button'); b.textContent = name; if (id === 'calm') b.classList.add('on');
    b.onclick = () => { st.expr = [{ t: 0, name: st.cur }, { t: st.clock, name: id }]; st.cur = id; [...$('exprs').children].forEach(x => x.classList.toggle('on', x === b)); };
    $('exprs').append(b);
  }
  async function pickMotion(id) {
    st.motion = id; st.t = 0;
    await A.set({ motion: [id], t: 0 });
    const info = A.clipInfo(); st.frames = info.frames; st.fps = info.fps; $('scrub').max = st.frames - 1;
  }
  $('motion').onchange = e => pickMotion(e.target.value);
  $('play').onclick = () => { st.play = !st.play; $('play').textContent = st.play ? 'пауза' : 'играть'; };
  $('talk').onclick = () => { st.talk = !st.talk; $('talk').classList.toggle('on', st.talk); };
  $('close').onclick = () => { st.close = !st.close; $('close').classList.toggle('on', st.close); };
  $('scrub').oninput = e => { st.t = +e.target.value; };
  let drag = null;
  canvas.onpointerdown = e => { drag = [e.clientX, e.clientY, st.yaw, st.pitch]; canvas.setPointerCapture(e.pointerId); canvas.style.cursor = 'grabbing'; };
  canvas.onpointermove = e => { if (!drag) return; st.yaw = drag[2] - (e.clientX - drag[0]) * 0.008; st.pitch = Math.max(-0.3, Math.min(1.2, drag[3] + (e.clientY - drag[1]) * 0.006)); };
  canvas.onpointerup = () => { drag = null; canvas.style.cursor = 'grab'; };
  canvas.onwheel = e => { e.preventDefault(); st.dist = Math.max(1.0, Math.min(11, st.dist * Math.exp(e.deltaY * 0.001))); };
  await pickMotion(st.motion);
  let last = performance.now(), busy = false;
  async function frame(now) {
    const dt = Math.min(0.1, (now - last) / 1000); last = now;
    if (!busy) {
      busy = true;
      if (st.play) { st.clock += dt; st.t += dt * st.fps; if (st.t > st.frames - 1) st.t = 0; }
      const k = Math.min(devicePixelRatio, 2);
      // the face lives on its own clock, so it goes on blinking and talking while the motion is paused or scrubbed
      await A.set({ ground: true, t: st.t, expr: st.expr, talk: st.talk, faceTime: st.clock, w: Math.round(innerWidth * k), h: Math.round(innerHeight * k),
        cam: st.close ? { yaw: st.yaw, pitch: st.pitch, dist: st.dist * 0.34, joint: 'Head', offset: [0, 0.04, 0], fov: 22 }
          : { yaw: st.yaw, pitch: st.pitch, dist: st.dist, follow: [0, 0.78, 0], fov: 22 } });
      canvas.style.width = '100%'; canvas.style.height = '100%';
      A.render();
      $('scrub').value = st.t; $('time').textContent = `${(st.t / st.fps).toFixed(1)} с`;
      busy = false;
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}
