// The viewer's controls: turn the character with the mouse (or a finger), come closer with the wheel; choose a Kimodo motion
// and an expression (it eases in), play / pause, scrub, talk on / off. The camera follows.
const A = window.A;
const $ = id => document.getElementById(id);
const MOTIONS = [['walk', 'идёт'], ['sneak', 'крадётся'], ['idle', 'стоит'], ['stomp', 'топает'], ['sit', 'садится'], ['jump', 'прыгает'], ['dance', 'танцует'], ['run', 'бежит'], ['wave', 'машет'], ['bow', 'кланяется']];
const EXPR = [['calm', 'исподлобья'], ['look', 'косится'], ['smirk', 'ухмылка'], ['surprise', 'удивление'], ['sad', 'грусть'], ['anger', 'злость']];
const st = { motion: 'walk', t: 0, clock: 0, play: true, talk: false, yaw: -0.35, pitch: 0.08, dist: 4.8, expr: [{ t: 0, name: 'calm' }], talkSpans: [], drag: null, close: false };

const sel = $('motion');
for (const [k, n] of MOTIONS) sel.add(new Option(n, k));
sel.onchange = () => { st.motion = sel.value; st.t = 0; };
const ex = $('exprs');
for (const [k, n] of EXPR) {
  const b = document.createElement('button'); b.textContent = n; b.dataset.k = k;
  b.onclick = () => { st.expr = st.expr.filter(e => e.t <= st.clock).concat([{ t: st.clock, name: k }]); mark(); };
  ex.appendChild(b);
}
function mark() { const cur = st.expr[st.expr.length - 1].name; for (const b of ex.children) b.classList.toggle('on', b.dataset.k === cur); }
mark();
$('play').onclick = () => { st.play = !st.play; $('play').textContent = st.play ? 'пауза' : 'играть'; };
$('talk').onclick = () => {
  st.talk = !st.talk; $('talk').classList.toggle('on', st.talk);
  if (st.talk) st.talkSpans.push([st.clock, 1e9]); else { const s = st.talkSpans[st.talkSpans.length - 1]; if (s) s[1] = st.clock; }
};
$('face').onclick = () => { st.close = !st.close; $('face').classList.toggle('on', st.close); };
const scrub = $('scrub');
scrub.oninput = () => { const ci = A.clipInfo(); if (ci) { st.t = scrub.value * (ci.frames - 1); st.clock = st.t / ci.fps; } };
const cv = $('c');
cv.onpointerdown = e => { st.drag = [e.clientX, e.clientY, st.yaw, st.pitch]; cv.setPointerCapture(e.pointerId); cv.style.cursor = 'grabbing'; };
cv.onpointermove = e => { if (!st.drag) return; st.yaw = st.drag[2] - (e.clientX - st.drag[0]) * 0.01; st.pitch = Math.max(-0.4, Math.min(1.0, st.drag[3] + (e.clientY - st.drag[1]) * 0.006)); };
cv.onpointerup = () => { st.drag = null; cv.style.cursor = 'grab'; };
cv.onwheel = e => { e.preventDefault(); st.dist = Math.max(1.0, Math.min(8, st.dist * Math.exp(e.deltaY * 0.001))); };

let last = performance.now(), busy = false, lastKey = '';
async function loop(now) {
  requestAnimationFrame(loop);
  if (busy) return; busy = true;
  const dt = Math.min(0.1, (now - last) / 1000); last = now;
  const w = innerWidth, h = innerHeight;
  const ci = A.clipInfo();
  // paused and nothing changed: draw nothing (the page stays quiet)
  const key = [w, h, st.motion, st.t, st.clock, st.yaw, st.pitch, st.dist, st.close, st.expr.length, st.talkSpans.length].join();
  if (!st.play && key === lastKey) { busy = false; return; }
  lastKey = key;
  if (st.play) { st.clock += dt; if (ci) { st.t += dt * ci.fps; if (st.t > ci.frames - 1) st.t = 0; } }
  const cam = st.close ? { yaw: st.yaw, pitch: st.pitch * 0.4, dist: st.dist * 0.42, joint: 'Head', offset: [0, 0.07, 0], fov: 20 }
    : { yaw: st.yaw, pitch: st.pitch, dist: st.dist, follow: [0, 0.84, 0], fov: 22 };
  await A.set({ w, h, motion: [st.motion], t: st.t, faceTime: st.clock, expr: st.expr, talk: st.talkSpans, cam, floor: true, lightCam: false });
  A.render();
  if (ci) { scrub.value = st.t / (ci.frames - 1); $('time').textContent = (st.t / ci.fps).toFixed(1) + ' с'; }
  busy = false;
}
requestAnimationFrame(loop);
