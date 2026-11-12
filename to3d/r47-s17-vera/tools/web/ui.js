// The viewer's controls: turn with the mouse (drag; wheel or two fingers come closer), the motion, the face's
// expression (buttons or a mix by sliders), speech on/off, play/pause and a scrub bar. ?shots: no controls
// (shots.mjs drives window.A itself).
const q = new URLSearchParams(location.search);
await import('./vera.js');
const A = window.A;
document.getElementById('msg')?.remove();
if (!q.has('shots')) {
  const MOTIONS = [['stand', 'стоит с папкой'], ['walk', 'идёт'], ['idle', 'ждёт'], ['wave', 'машет']];
  const EXPR = [['calm', 'спокойна'], ['joy', 'радость'], ['surprise', 'удивление'], ['sad', 'грусть'], ['anger', 'гнев']];
  const ui = document.createElement('div'); ui.id = 'ui'; document.body.appendChild(ui);
  const el = (tag, props = {}, parent = ui) => { const e = Object.assign(document.createElement(tag), props); parent.appendChild(e); return e; };
  const fold = el('button', { id: 'fold', textContent: '☰' }); fold.onclick = () => ui.classList.toggle('folded');
  const sel = el('select'); for (const [id, ru] of MOTIONS) el('option', { value: id, textContent: ru }, sel);
  const play = el('button', { textContent: '❚❚' });
  const scrubBox = el('span', { id: 'scrub' }); const scrub = el('input', { type: 'range', min: 0, max: 1000, value: 0 }, scrubBox);
  const talk = el('label'); const talkCb = el('input', { type: 'checkbox' }, talk); el('span', { textContent: 'говорит' }, talk);
  const close = el('button', { textContent: 'лицо крупно' });
  const eb = {}; for (const [id, ru] of EXPR) { eb[id] = el('button', { textContent: ru }); eb[id].onclick = () => setMix({ [id]: 1 }); }
  const sl = {}; for (const [id, ru] of EXPR.slice(1)) { const l = el('label'); el('span', { textContent: ru }, l); sl[id] = el('input', { type: 'range', min: 0, max: 100, value: 0 }, l); sl[id].oninput = () => setMix(Object.fromEntries(Object.entries(sl).map(([k, s]) => [k, s.value / 100])), true); }

  const st = { motion: 'stand', playing: true, t: 0, len: 12, mix: { calm: 1 }, talk: false, yaw: -0.35, pitch: 0.05, dist: 5.2, close: false };
  let exprTrack = [[0, { calm: 1 }]];
  const secs = () => st.motion === 'stand' ? st.t : st.t / 30;
  async function setLive() { await A.set({ live: { seconds: st.motion === 'stand' ? 12 : undefined, talk: st.talk, expr: exprTrack, seed: 7 } }); }
  async function setMix(m, fromSliders) {
    const w = { ...m }; let tot = Object.values(w).reduce((a, b) => a + b, 0); if (tot < 1) w.calm = 1 - tot;
    st.mix = w; exprTrack = [[0, exprTrack[exprTrack.length - 1][1]], [Math.max(0, secs() - 0.001), exprTrack[exprTrack.length - 1][1]], [secs(), w]];
    for (const [id] of EXPR) eb[id].classList.toggle('on', w[id] === 1);
    if (!fromSliders) for (const k in sl) sl[k].value = (w[k] || 0) * 100;
    await setLive();
  }
  async function setMotion(id) {
    st.motion = id; st.t = 0;
    await A.set({ clip: id === 'stand' ? null : id, pose: 'stand', folder: true, floor3d: id !== 'stand', lightSpace: 'world', light: [-0.45, 0.62, 0.65] });
    st.len = id === 'stand' ? 12 : A.frames() - 1;
    exprTrack = [[0, st.mix]]; await setLive();
  }
  sel.onchange = () => setMotion(sel.value);
  play.onclick = () => { st.playing = !st.playing; play.textContent = st.playing ? '❚❚' : '▶'; };
  scrub.oninput = () => { st.t = scrub.value / 1000 * st.len; };
  talkCb.onchange = () => { st.talk = talkCb.checked; setLive(); };
  close.onclick = () => { st.close = !st.close; close.classList.toggle('on', st.close); };
  // turning with the mouse / a finger; coming closer with the wheel / two fingers
  const cv = document.getElementById('cv'), pts = new Map(); let pinch = 0;
  cv.onpointerdown = e => { cv.setPointerCapture(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]); };
  cv.onpointerup = cv.onpointercancel = e => { pts.delete(e.pointerId); pinch = 0; };
  cv.onpointermove = e => {
    if (!pts.has(e.pointerId)) return;
    const [x0, y0] = pts.get(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]);
    if (pts.size === 2) { const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]); if (pinch) st.dist *= pinch / d; pinch = d; }
    else { st.yaw -= (e.clientX - x0) * 0.008; st.pitch = Math.max(-0.4, Math.min(0.8, st.pitch + (e.clientY - y0) * 0.005)); }
  };
  cv.onwheel = e => { e.preventDefault(); st.dist = Math.max(1.2, Math.min(12, st.dist * Math.exp(e.deltaY * 0.001))); };
  await setMotion('stand'); eb.calm.classList.add('on');
  let last = performance.now();
  async function loop(now) {
    const dt = Math.min(0.1, (now - last) / 1000); last = now;
    if (st.playing) { st.t += st.motion === 'stand' ? dt : dt * 30; if (st.t > st.len) st.t = 0; scrub.value = st.t / st.len * 1000; }
    const cy = st.close ? 1.52 : 0.9, dist = st.close ? st.dist * 0.24 : st.dist;
    await A.set({ t: st.t, cam: { mode: 'persp', yaw: st.yaw, pitch: st.pitch, cy, dist, fov: 24, follow: true } });
    const cvs = document.getElementById('cv'); const hh = innerHeight - (ui.classList.contains('folded') ? 0 : ui.offsetHeight);
    if (cvs.style.height !== hh + 'px') cvs.style.height = hh + 'px';
    A.render();
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
}
