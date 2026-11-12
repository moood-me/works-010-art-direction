// The viewer: the sprite turned with the mouse (drag left and right), the portrait, a motion, an expression, speech
// on and off, play / pause / scrub. Off when the page is opened with ?shots (pictures for the page).
if (!new URLSearchParams(location.search).has('shots')) {
  while (!window.__ready) await new Promise(r => setTimeout(r, 50));
  const A = window.A, ui = document.getElementById('ui'), cv = document.getElementById('cv');
  const S = { view: 'stage', clip: 'stand', expr: 'rest', talk: false, playing: true, t: 0, yaw: -20 };
  const fit = () => {
    const pad = ui.classList.contains('folded') ? 0 : ui.offsetHeight + 24, w = A.V.W + (S.view === 'portrait' ? 6 : 0), h = A.V.H + (S.view === 'portrait' ? 6 : 0);
    A.V.scale = Math.max(2, Math.floor(Math.min(innerWidth / w, (innerHeight - pad) / h)));
    document.getElementById('stage').style.bottom = pad + 'px';
    dirty = true;
  };
  let dirty = true, lastQ = -1;
  async function apply() {
    await A.set({ ...A.VIEWS[S.view], yaw: S.view === 'portrait' ? 0 : S.yaw, clip: S.clip, live: true, expr: S.expr, talk: S.talk, t: S.t, mode: 'sprite', rules: true });
    fit();
  }
  const row = (id, items, key, cur) => { const box = document.getElementById(id); for (const [k, ru] of items) { const b = document.createElement('button'); b.textContent = ru; b.dataset[key] = k; b.setAttribute('aria-pressed', String(k === cur)); box.appendChild(b); } return box; };
  const press = (box, key, v) => box.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset[key] === v)));
  const views = row('views', [['stage', 'спрайт'], ['portrait', 'портрет']], 'view', S.view);
  const clips = row('clips', Object.entries(A.CLIPS).map(([k, c]) => [k, c.ru]), 'clip', S.clip);
  const exprs = row('exprs', Object.entries(A.EXPR_RU), 'expr', S.expr);
  await apply();
  document.getElementById('msg').remove(); ui.classList.add('on'); fit();
  views.addEventListener('click', async e => { const v = e.target.dataset.view; if (!v) return; S.view = v; press(views, 'view', v); await apply(); });
  clips.addEventListener('click', async e => { const v = e.target.dataset.clip; if (!v) return; S.clip = v; S.t = 0; press(clips, 'clip', v); await apply(); });
  exprs.addEventListener('click', e => { const v = e.target.dataset.expr; if (!v) return; S.expr = v; press(exprs, 'expr', v); dirty = true; });
  const talk = document.getElementById('talk'); talk.addEventListener('click', () => { S.talk = !S.talk; talk.setAttribute('aria-pressed', String(S.talk)); dirty = true; });
  const play = document.getElementById('play'), scrub = document.getElementById('scrub'), time = document.getElementById('time');
  play.addEventListener('click', () => { S.playing = !S.playing; play.textContent = S.playing ? 'пауза' : 'играть'; play.setAttribute('aria-pressed', String(S.playing)); });
  scrub.addEventListener('input', () => { S.t = +scrub.value * A.duration(); dirty = true; });
  const fold = document.getElementById('fold');
  fold.addEventListener('click', () => { ui.classList.toggle('folded'); fold.textContent = ui.classList.contains('folded') ? 'настройки' : 'свернуть'; fit(); });
  addEventListener('resize', fit);
  let drag = null;
  cv.addEventListener('pointerdown', e => { cv.setPointerCapture(e.pointerId); drag = e.clientX; cv.style.cursor = 'grabbing'; });
  cv.addEventListener('pointermove', e => { if (drag === null || S.view === 'portrait') return; S.yaw -= (e.clientX - drag) * 0.6; drag = e.clientX; A.V.yaw = S.yaw; dirty = true; });
  const up = () => { drag = null; cv.style.cursor = 'grab'; };
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  // the loop: a new picture only when the sprite's frame (12 a second) or something set by hand has changed
  let prev = performance.now();
  const tick = now => {
    const dt = Math.min(0.1, (now - prev) / 1000); prev = now;
    if (S.playing) S.t += dt;
    const q = Math.floor(S.t * A.FPS);
    if (q !== lastQ || dirty) {
      lastQ = q; dirty = false;
      A.frame({ t: S.t, expr: S.expr, talk: S.talk }); A.render();
      const d = A.duration(); scrub.value = (S.t % d) / d; time.textContent = (S.t % d).toFixed(1) + ' с';
    }
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
