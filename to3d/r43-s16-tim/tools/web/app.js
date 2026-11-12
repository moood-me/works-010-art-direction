// The viewer: the figure on the street, on its own pixel grid, enlarged a whole number of times. Turn with the mouse
// (in 16 directions, as a game's sprite, or freely), choose a motion and an expression, play, pause, scrub, talk.
import { Palette, Figure, paint } from './vox.js';
import { Stage, Player, Life, FPS } from './stage.js';
import * as ch from './char.js';

const D = await (await fetch('drawing.json')).json();
const pal = Palette(D.ramps), fig = Figure(ch, pal), stage = Stage(ch, pal, D, fig);
const motions = {};
await Promise.all([...new Set(ch.CLIPS.map(c => c.motion).filter(Boolean))].map(async m => { motions[m] = await (await fetch(`../motions/${m}.json`)).json(); }));
const player = Player(ch, fig, motions), life = Life(7);

const W = 128, H = 76, BY = 24, cv = document.getElementById('c'), g = cv.getContext('2d');
cv.width = W; cv.height = H;
const S = { clip: ch.CLIPS[0], t: 0, playing: true, yaw: ch.CLIPS[0].yaw || 0, expr: 'rest', talk: false, box: true, snap: true, steady: true, hold: true };
const $ = id => document.getElementById(id);
function fit() { const r = $('wrap').getBoundingClientRect(), k = Math.max(1, Math.floor(Math.min(r.width / W, r.height / H))); cv.style.width = W * k + 'px'; cv.style.height = H * k + 'px'; }
addEventListener('resize', fit); fit();

function buttons(host, items, get, set) {
  const bs = items.map(([id, label]) => { const b = document.createElement('button'); b.textContent = label; b.onclick = () => { set(id); upd(); }; host.append(b, ' '); return [id, b]; });
  const upd = () => bs.forEach(([id, b]) => b.classList.toggle('on', get() === id)); upd(); return upd;
}
const updClips = buttons($('clips'), ch.CLIPS.map(c => [c.id, c.label]), () => S.clip.id, id => { S.clip = ch.CLIPS.find(c => c.id === id); S.t = 0; S.yaw = S.clip.yaw || 0; });
const NAMES = { rest: 'спокойно', joy: 'радость', surprise: 'удивление', sadness: 'грусть', anger: 'злость' };
buttons($('exprs'), ch.EXPRS.map(e => [e, NAMES[e]]), () => S.expr, e => { S.expr = e; });
const toggle = (id, key, on) => { const b = $(id); b.onclick = () => { S[key] = !S[key]; b.classList.toggle('on', S[key]); if (on) on(); }; b.classList.toggle('on', S[key]); };
toggle('talk', 'talk'); toggle('box', 'box'); toggle('snap', 'snap'); toggle('steady', 'steady'); toggle('hold', 'hold');
$('play').onclick = () => { S.playing = !S.playing; $('play').textContent = S.playing ? 'пауза' : 'пуск'; };
$('scrub').oninput = e => { S.t = +e.target.value * player.dur(S.clip); S.playing = false; $('play').textContent = 'пуск'; };
let drag = null;
cv.onpointerdown = e => { drag = { x: e.clientX, yaw: S.yaw }; cv.setPointerCapture(e.pointerId); };
cv.onpointermove = e => { if (drag) S.yaw = drag.yaw + (e.clientX - drag.x) * 0.6; };
cv.onpointerup = () => { drag = null; };

function draw() {
  const dur = player.dur(S.clip), t = S.t % dur, fps = S.hold ? FPS : 0;
  const a = player.at(S.clip, t, fps), yaw = S.snap ? Math.round(S.yaw / 22.5) * 22.5 : S.yaw;
  const face = life(S.hold ? Math.floor(S.t * FPS) / FPS : S.t, { talk: S.talk, expr: S.expr });
  const f = stage.frame({ bg: 'street', w: W, h: H, by: BY, bx: S.clip.travel ? 40 : 62, x: S.box ? 38 : 64, pose: a.pose, lift: a.lift, yaw, follow: !!S.clip.travel, face, steady: S.steady });
  if (S.box) { const p = stage.portrait(face); for (let r = 0; r < p.h; r++) for (let c = 0; c < p.w; c++) f.key[(r + 5) * W + c + 60] = p.key[r * p.w + c]; }
  g.putImageData(new ImageData(paint(pal, f.key, W, H, 1, [0, 0, 0]), W, H), 0, 0);
  if (S.playing) $('scrub').value = t / dur;
}
let last = performance.now();
function tick(now) { const dt = Math.min(0.1, (now - last) / 1000); last = now; if (S.playing) S.t += dt; draw(); requestAnimationFrame(tick); }
requestAnimationFrame(tick);
// for pictures of the viewer: the state can be set from outside
window.A = { S, draw, set: o => { Object.assign(S, o); if (o.clip) { S.clip = ch.CLIPS.find(c => c.id === o.clip); updClips(); } draw(); } };
