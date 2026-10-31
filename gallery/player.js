// The gallery's viewer: a page opened with ?viewer becomes one full-window stage where a character can be turned,
// zoomed and moved, and played in Kimodo's motions. The page gives `window.__vp` (what it is and how to reach its
// models); this file does the rest: the panel, the camera, and moving the models along the motions.
//
// Motions are Kimodo's, as converted for the indie heroes (experiments/indie/motions): for each SOMA joint and frame
// its turn against SOMA's rest, in the person's space; the pelvis's height; the feet's height above the floor.
// A body standing on SOMA's 77 joints takes them directly: each joint turned as SOMA's, a bone first turned from its
// own rest direction to SOMA's, the pelvis as high as the body's legs make it, the feet as high above the floor as
// SOMA's are. Everything that isn't the body (clothes, hair, a head of its own) goes with the body skin nearest to it.

const MOTIONS = [['', 'покой'], ['walk', 'шаг'], ['run', 'бег'], ['wave', 'машет'], ['jump', 'прыжок'], ['dance', 'танец'],
  ['bow', 'поклон'], ['sneak', 'крадётся'], ['stomp', 'топает'], ['sit', 'садится'], ['idle', 'стоит, дышит']];
const MOTION_URL = new URL('../experiments/indie/motions/', import.meta.url);
const motionCache = {};
const loadMotion = name => motionCache[name] ??= fetch(new URL(name + '.json', MOTION_URL)).then(r => r.json());

import { turns, Skinner } from './player-core.js';


// ———— the adapters: how each kind of page shows a character and moves it ————
const meshesUnder = o => { const a = []; o.traverse(m => { if (m.isMesh && m.geometry?.attributes?.position) a.push(m); }); return a; };

async function annyAdapter(vp) {
  const chars = await (await fetch('viewer.json')).json();
  let sk = null;
  return {
    chars, cam: vp.cam,
    async show(c) {
      window.__restPose = true;
      const S = vp.state, st = c.state;
      Object.assign(S, { mode: 'one', who: st.who || 'woman', gw: st.gw || {}, cw: st.cw || {}, over: st.over || {} });
      if (st.look) S.look = st.look;
      if (st.lookDef && vp.LOOKS) vp.LOOKS[st.look] = st.lookDef;
      await vp.refresh();
      vp.cam.dist *= 1.3; vp.cam.pitch = 0.08;   // the whole figure in a full window
      const G = vp.group.children[0], N = vp.BASE.N, J = window.__restJ;
      const meshes = meshesUnder(G).map(mesh => ({ mesh, isBody: mesh.geometry.attributes.position.count === N && !mesh.material?.side }));
      // the body: the one mesh with Anny's vertex count drawn from the front (an outline copy is drawn from the back)
      let body = meshes.find(m => m.isBody) || meshes.find(m => m.mesh.geometry.attributes.position.count === N);
      meshes.forEach(m => { m.isBody = m === body; });
      sk = new Skinner(vp.THREE, { names: vp.JN, parent: vp.PARENT, rest: J, body: Float32Array.from(body.mesh.geometry.attributes.position.array), joint: vp.BASE.joint, weight: vp.BASE.weight, meshes });
    },
    frame(M, f) { sk?.pose(M, f); },
    rest() { sk?.restPose(); },
  };
}

// pages that build one character as the page loads (heads): another character is another load
function oneAdapter(vp) {
  const sk = new Skinner(vp.THREE, { names: vp.JN, parent: vp.PARENT, rest: vp.J, body: vp.restBody, joint: vp.BASE.joint, weight: vp.BASE.weight,
    meshes: meshesUnder(vp.scene).filter(m => m.userData.move !== false).map(mesh => ({ mesh, isBody: mesh.userData.body === true, rigid: mesh.userData.rigid ?? mesh.parent?.userData?.rigid })) });
  return {
    chars: vp.chars, current: vp.current, render: () => vp.renderer.render(vp.scene, vp.camera), camera: vp.camera, renderer: vp.renderer, target: vp.target, view0: { yaw: 0.4, pitch: 0.06, dist: vp.target.y * 6.4 },
    show(c) { const q = new URLSearchParams(location.search); q.set('c', c.id); location.search = q.toString(); },
    frame(M, f) { sk.pose(M, f); },
    rest() { sk.restPose(); },
  };
}

// ———— the panel, the camera, the clock ————
const vp = await new Promise(r => { const t = setInterval(() => { if (window.__vp?.ready !== false && window.__vp) { clearInterval(t); r(window.__vp); } }, 50); });
const THREE = vp.THREE;
const A = vp.kind === 'anny' ? await annyAdapter(vp) : vp.kind === 'one' ? oneAdapter(vp) : vp.adapter;
if (A.noMotion) { A.frame = A.rest = () => {}; }

const css = document.createElement('style');
css.textContent = `
  html, body { overflow: hidden !important; }
  #vpStage { position: fixed !important; inset: 0 !important; width: 100vw !important; height: 100vh !important; max-width: none !important; aspect-ratio: auto !important; border-radius: 0 !important; z-index: 5; margin: 0 !important; }
  #vpGrab { position: fixed; inset: 0; z-index: 6; cursor: grab; touch-action: none; }
  #vpGrab:active { cursor: grabbing; }
  #vpPanel { position: fixed; left: 12px; top: 12px; z-index: 7; background: rgba(250,247,242,.92); color: #26231f; border-radius: 10px; padding: 10px 12px; font: 13px/1.4 system-ui, sans-serif; box-shadow: 0 2px 12px rgba(0,0,0,.18); display: grid; gap: 8px; max-width: min(420px, calc(100vw - 24px)); }
  #vpPanel select, #vpPanel button { font: inherit; border: 1px solid #d5cec4; background: #fff; border-radius: 6px; padding: 4px 8px; color: #26231f; }
  #vpPanel .row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
  #vpPanel .mv { display: flex; flex-wrap: wrap; gap: 4px; }
  #vpPanel .mv button[aria-pressed="true"] { background: #b4532a; border-color: #b4532a; color: #fff; }
  #vpPanel input[type=range] { flex: 1; min-width: 120px; }
  #vpPanel .hint { color: #75706a; font-size: 12px; }
  #vpMsg { position: fixed; inset: 0; z-index: 8; display: none; place-items: center; font: italic 22px Georgia, serif; color: #4a4640; pointer-events: none; }`;
document.head.appendChild(css);
const stageEl = vp.stage || vp.renderer?.domElement;
stageEl.id = stageEl.id || 'vpStage'; stageEl.classList.add('vp'); stageEl.setAttribute('id', stageEl.id); stageEl.style.cssText += ';position:fixed;inset:0;width:100vw;height:100vh;max-width:none;aspect-ratio:auto;border-radius:0;z-index:5;margin:0';
const grab = document.createElement('div'); grab.id = 'vpGrab'; document.body.appendChild(grab);
const msg = document.createElement('div'); msg.id = 'vpMsg'; msg.textContent = 'собирается…'; document.body.appendChild(msg);
const panel = document.createElement('div'); panel.id = 'vpPanel';
panel.innerHTML = `<div class="row"><select id="vpChar" aria-label="Персонаж"></select></div>
  <div class="mv" id="vpMoves"></div>
  <div class="row"><button id="vpPlay">❚❚</button><input id="vpTime" type="range" min="0" max="1" step="1" value="0" aria-label="Время"><span id="vpF">0</span></div>
  <div class="hint">мышь: вращать · колесо: ближе/дальше · правая кнопка или Shift: сдвинуть</div>`;
document.body.appendChild(panel);
const sel = panel.querySelector('#vpChar'), moves = panel.querySelector('#vpMoves'), playB = panel.querySelector('#vpPlay'), timeR = panel.querySelector('#vpTime'), fLab = panel.querySelector('#vpF');
A.chars.forEach(c => { const o = document.createElement('option'); o.value = c.id; o.textContent = c.label; sel.appendChild(o); });
const q = new URLSearchParams(location.search);
let motion = q.get('m') || 'walk', M = null, t = 0, playing = true;
for (const [id, name] of MOTIONS) { const b = document.createElement('button'); b.textContent = name; b.dataset.m = id; b.onclick = () => setMotion(id); moves.appendChild(b); }

// the camera: around a point, as the page's own camera object or one of ours
const cam = A.cam || { yaw: 0.35, pitch: 0.08, dist: 3, ...(A.view0 || {}), target: A.target ? A.target.clone() : new THREE.Vector3(0, 0.9, 0) };
function place() {
  if (A.cam) return;   // the page places its own camera from cam every frame
  const c = A.camera, cp = Math.cos(cam.pitch);
  c.position.set(cam.target.x + Math.sin(cam.yaw) * cp * cam.dist, cam.target.y + Math.sin(cam.pitch) * cam.dist, cam.target.z + Math.cos(cam.yaw) * cp * cam.dist); c.lookAt(cam.target);
}
let drag = null;
grab.addEventListener('contextmenu', e => e.preventDefault());
grab.addEventListener('pointerdown', e => { drag = { x: e.clientX, y: e.clientY, pan: e.button === 2 || e.shiftKey }; grab.setPointerCapture(e.pointerId); });
grab.addEventListener('pointermove', e => {
  if (!drag) return; const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.x = e.clientX; drag.y = e.clientY;
  if (drag.pan) {
    const s = cam.dist * 0.0012, right = new THREE.Vector3(Math.cos(cam.yaw), 0, -Math.sin(cam.yaw));
    cam.target.addScaledVector(right, -dx * s); cam.target.y += dy * s;
  } else { cam.yaw -= dx * 0.007; cam.pitch = Math.max(-0.6, Math.min(1.2, cam.pitch + dy * 0.005)); }
});
grab.addEventListener('pointerup', () => drag = null); grab.addEventListener('pointercancel', () => drag = null);
grab.addEventListener('wheel', e => { e.preventDefault(); cam.dist = Math.max(0.2, Math.min(30, cam.dist * Math.exp(e.deltaY * 0.001))); }, { passive: false });
function resize() {
  if (A.renderer && A.camera) { A.renderer.setSize(innerWidth, innerHeight, false); A.camera.aspect = innerWidth / innerHeight; A.camera.updateProjectionMatrix(); }
  A.resize?.();
}
addEventListener('resize', resize);

async function setMotion(id) {
  motion = id; moves.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.m === id)));
  if (!id) { M = null; timeR.max = 0; A.rest(); fLab.textContent = ''; return; }
  M = await loadMotion(id); timeR.max = M.n - 1; t = 0;
  A.motionChanged?.(id);
  A.frame(M, 0);
}
async function setChar(id) {
  const c = A.chars.find(x => x.id === id) || A.chars[0]; sel.value = c.id;
  if (A.current) { const qq = new URLSearchParams(location.search); qq.set('c', c.id); qq.set('s', c.id); if (motion) qq.set('m', motion); location.search = qq.toString(); return; }   // a page that builds one character as it loads
  msg.style.display = 'grid'; await new Promise(r => setTimeout(r, 30));
  await A.show(c);
  msg.style.display = 'none';
  if (M) A.frame(M, Math.min(M.n - 1, Math.floor(t))); else A.rest();
}
sel.onchange = () => setChar(sel.value);
playB.onclick = () => { playing = !playing; playB.textContent = playing ? '❚❚' : '▶'; };
timeR.oninput = () => { t = +timeR.value; playing = false; playB.textContent = '▶'; if (M) A.frame(M, Math.floor(t)); };

window.__player = { setChar, setMotion, cam, get frame() { return Math.floor(t); }, set playing(v) { playing = v; }, A };
resize();
if (!A.current) await setChar(q.get('c') || A.chars[0].id); else { sel.value = A.current; }
if (A.noMotion) { moves.style.display = 'none'; playB.parentElement.style.display = 'none'; panel.querySelector('.hint').textContent = 'мышь: вращать · колесо: ближе/дальше · правая кнопка или Shift: сдвинуть'; }
else await setMotion(motion);
let last = performance.now();
(function loop(now) {
  const dt = Math.min(0.1, (now - last) / 1000); last = now;
  if (M && playing) { t = (t + dt * (M.fps || 30)) % M.n; timeR.value = Math.floor(t); A.frame(M, Math.floor(t)); }
  if (M) fLab.textContent = Math.floor(t) + '/' + (M.n - 1);
  place(); A.render?.();
  requestAnimationFrame(loop);
})(last);
