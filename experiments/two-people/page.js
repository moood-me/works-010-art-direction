// The page: the scenes of two people (scenes.js) played on the early engine (engine/), both people in one space.
// URL: ?s=<scene>&t=<frame>&paused&corr=0 — and window.__page for tools/pictures.mjs.
import * as THREE from 'three';
import { createEngine } from '../../engine/src/engine.js';
import { makeStage, figureMesh } from '../../engine/src/view3d.js';
import { loadScene, jointAt } from './scene.js';
import { SCENES } from './scenes.js';

const q = new URLSearchParams(location.search);
const $ = s => document.querySelector(s), msg = $('#msg');
const E = await createEngine();
const stage = makeStage(THREE, $('#cv'), { pixelRatio: Math.min(devicePixelRatio || 1, 2) });
if (q.has('bare')) $('#panel').style.display = 'none';
const fit = () => { const w = innerWidth > 760 && !q.has('bare') ? $('#panel').offsetWidth + 12 : 0; stage.size(innerWidth, innerHeight, w / 2); };
addEventListener('resize', fit); fit();
stage.key.shadow.camera.left = -3.5; stage.key.shadow.camera.right = 3.5; stage.key.shadow.camera.top = 3; stage.key.shadow.camera.bottom = -2;
stage.key.shadow.camera.updateProjectionMatrix();

const P = { scene: q.get('s') || SCENES[0].id, t: +(q.get('t') || 0), playing: !q.has('paused'), slow: false, corr: q.get('corr') !== '0', mark: false, close: false };
const cam = { yaw: 0.9, pitch: 0.12, dist: 6, target: [0, 0.9, 0] };
let S = null, views = [], marks = [];

for (const d of SCENES) {
  const b = document.createElement('button'); b.textContent = d.label; b.dataset.id = d.id;
  b.onclick = () => setScene(d.id); $('#scenes').appendChild(b);
}
function press() {
  document.querySelectorAll('#scenes button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.id === P.scene)));
  $('#play').textContent = P.playing ? '❚❚' : '▶';
  for (const [id, on] of [['#slow', P.slow], ['#corr', P.corr], ['#mark', P.mark], ['#close', P.close]]) $(id).setAttribute('aria-pressed', String(on));
}

async function setScene(id) {
  msg.style.display = 'grid'; await new Promise(r => setTimeout(r, 20));
  P.scene = id; const def = SCENES.find(d => d.id === id);
  for (const v of views) { stage.scene.remove(v.mesh); v.dispose(); } for (const m of marks) stage.scene.remove(m);
  S = await loadScene(E, new URL('./', import.meta.url), def);
  views = S.people.map(p => { const v = figureMesh(THREE, p.fig, p.spec.look); stage.scene.add(v.mesh); return v; });
  marks = (def.contacts || []).map(() => { const m = new THREE.Mesh(new THREE.SphereGeometry(0.018, 16, 12), new THREE.MeshBasicMaterial({ color: '#e0592a', depthTest: false, transparent: true, opacity: 0.85 })); m.renderOrder = 10; stage.scene.add(m); return m; });
  $('#about').textContent = def.about;
  $('#time').max = S.frames - 1; P.t = Math.min(P.t, S.frames - 1);
  if (def.camera) Object.assign(cam, def.camera, { target: [...def.camera.target] });
  draw(); press();
  msg.style.display = 'none';
}

function draw() {
  S.corrections = P.corr; S.misses = {};
  S.at(P.t);
  views.forEach(v => v.update());
  const def = S.def;
  (def.contacts || []).forEach((c, i) => {
    const O = S.by[c.on], on = P.t >= c.from - c.ramp && P.t <= c.to + c.ramp;
    marks[i].visible = P.mark && on;
    if (marks[i].visible) marks[i].position.set(...jointAt(O.fig.pose, O.body, O.body.skeleton.index[c.joint], c.point));
  });
  // the light and the camera's point: between the two (or near the touch)
  const hs = S.people.map(p => getHip(p));
  const mid = [(hs[0][0] + hs[1][0]) / 2, 0, (hs[0][2] + hs[1][2]) / 2];
  stage.light(mid);
  if (P.close && def.contacts?.length) { const c = def.contacts[0], O = S.by[c.on]; const t = jointAt(O.fig.pose, O.body, O.body.skeleton.index[c.joint], c.point); cam.target = t; }
  else if (def.follow) cam.target = [mid[0], 0.85, mid[2]];
  const miss = Object.entries(S.misses).map(([w, d]) => `рука ${w} от точки без поправки: ${(d * 100).toFixed(1)} см`).join(' · ');
  $('#time').value = P.t; $('#flab').textContent = `${Math.floor(P.t)}/${S.frames - 1}`;
  $('#status').textContent = miss;
}
const getHip = p => [p.fig.pose.P[0], p.fig.pose.P[1], p.fig.pose.P[2]];

$('#play').onclick = () => { P.playing = !P.playing; press(); };
$('#time').oninput = () => { P.t = +$('#time').value; P.playing = false; press(); draw(); };
$('#slow').onclick = () => { P.slow = !P.slow; press(); };
$('#corr').onclick = () => { P.corr = !P.corr; press(); draw(); };
$('#mark').onclick = () => { P.mark = !P.mark; press(); draw(); };
$('#close').onclick = () => { P.close = !P.close; cam.dist = P.close ? 1.6 : 6; if (!P.close) cam.target = [...S.def.camera.target]; press(); draw(); };
document.querySelectorAll('[data-view]').forEach(b => b.onclick = () => {
  const base = S.def.camera?.yaw ?? 0, v = +b.dataset.view;
  if (v === 3) { cam.pitch = 1.25; return; }
  cam.yaw = base + [0, Math.PI / 2, Math.PI][v] - (S.def.camera?.yaw0 ?? 0); cam.pitch = 0.1;
});

const cv = $('#cv'); let drag = null;
cv.addEventListener('contextmenu', e => e.preventDefault());
cv.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY, pan: e.button === 2 || e.shiftKey }; cv.setPointerCapture(e.pointerId); });
cv.addEventListener('pointermove', e => {
  if (!drag) return; const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.x = e.clientX; drag.y = e.clientY;
  if (drag.pan) { const s = cam.dist * 0.0012; cam.target[0] -= Math.cos(cam.yaw) * dx * s; cam.target[2] += Math.sin(cam.yaw) * dx * s; cam.target[1] += dy * s; }
  else { cam.yaw -= dx * 0.007; cam.pitch = Math.max(-0.4, Math.min(1.4, cam.pitch + dy * 0.005)); }
});
cv.addEventListener('pointerup', () => drag = null); cv.addEventListener('pointercancel', () => drag = null);
cv.addEventListener('wheel', e => { e.preventDefault(); cam.dist = Math.max(0.4, Math.min(40, cam.dist * Math.exp(e.deltaY * 0.001))); }, { passive: false });
addEventListener('keydown', e => { if (e.key === ' ' && e.target === document.body) { e.preventDefault(); P.playing = !P.playing; press(); } });

await setScene(P.scene);
window.__page = {
  P, cam, stage, get S() { return S; },
  async set(o) { if (o.scene && o.scene !== P.scene) await setScene(o.scene); Object.assign(P, o); draw(); press(); },
  render() { draw(); stage.look(cam.target, cam); stage.render(); },
};
let last = performance.now();
(function loop(now) {
  const dt = Math.min(0.1, (now - last) / 1000); last = now;
  if (S && P.playing) { P.t += dt * 30 * (P.slow ? 0.3 : 1); if (P.t > S.frames - 1) P.t = 0; draw(); }
  stage.look(cam.target, cam); stage.render();
  requestAnimationFrame(loop);
})(last);
