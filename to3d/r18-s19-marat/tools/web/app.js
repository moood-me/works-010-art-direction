// The page's driver: the stage, Kimodo clips through the engine, the live face, and window.A for pictures
// (tools/shots.mjs). ui.js adds the controls when the page is opened without ?shots.
import * as THREE from 'three';
import { createStage, getClip, MOTIONS } from './marat.js';
const qs = new URLSearchParams(location.search);
const cv = document.getElementById('cv');
const st = await createStage(cv, { pixelRatio: qs.has('shots') ? 1 : undefined });
const ch = st.ch, sk = st.data.sk, V3 = THREE.Vector3;

// which of the drawing's poses a still "motion" is, and what is in his hands in each motion
const STILL = { stand: 'stand', turn: 'turn', portrait: 'portrait' };
const HANDS = { walk: [{ L: 'fist', R: 'fist' }, true], stand: [{ L: 'fist', R: 'fist' }, true], wave: [{ L: 'fist', R: 'open' }, false], bow: [{ L: 'open', R: 'open' }, false], dance: [{ L: 'open', R: 'open' }, false] };
const cur = { clip: 'stand', t: 0, heading: 0, breath: true };
let clip = null, bones = null, mode = 'full';

function headTurn(pose) {   // the head's turn against the chest (degrees), for the eyes to lead it
  const q = i => new THREE.Quaternion(pose.Q[i * 4], pose.Q[i * 4 + 1], pose.Q[i * 4 + 2], pose.Q[i * 4 + 3]);
  const f = new V3(0, 0, 1).applyQuaternion(q(sk.index.Chest).invert().multiply(q(sk.index.Head)));
  return [Math.atan2(f.x, f.z) * 180 / Math.PI, Math.asin(Math.max(-1, Math.min(1, f.y))) * 180 / Math.PI];
}
function place(t, face) {
  const o = { place: { position: [0, 0, 0], heading: cur.heading }, open: face ? face.open : ch.open };
  if (clip) return ch.frame({ ...o, clip, t: Math.min(clip.frames - 1, t * clip.fps) });
  return ch.frame({ ...o, stat: st.data.poses[STILL[cur.clip]], breath: cur.breath ? ch.live.breath() : 0 });
}
function showBones(pose) {
  if (bones) { st.scene.remove(bones); bones = null; }
  if (mode !== 'skeleton') return;
  const P = pose.P, g = new THREE.Group(), mat = new THREE.MeshBasicMaterial({ color: 0xc25a36 }), mat2 = new THREE.MeshBasicMaterial({ color: 0x3a3540 });
  for (let j = 0; j < sk.J; j++) {
    const p = new V3(P[j * 3], P[j * 3 + 1], P[j * 3 + 2]), big = !/Hand[A-Z]|Toe|Eye|Jaw|HeadEnd/.test(sk.names[j]);
    const s = new THREE.Mesh(new THREE.SphereGeometry(big ? 0.022 : 0.008, 10, 6), mat); s.position.copy(p); g.add(s);
    const pj = sk.parent[j]; if (pj < 0) continue;
    const q = new V3(P[pj * 3], P[pj * 3 + 1], P[pj * 3 + 2]), L = p.distanceTo(q); if (L < 1e-4) continue;
    const c = new THREE.Mesh(new THREE.CylinderGeometry(big ? 0.007 : 0.003, big ? 0.007 : 0.003, L, 6), mat2);
    c.position.copy(p).add(q).multiplyScalar(0.5); c.quaternion.setFromUnitVectors(new V3(0, 1, 0), p.clone().sub(q).normalize()); g.add(c);
  }
  bones = g; st.scene.add(g);
}
function aim(pose) {
  const c = st.cam; if (!c.follow) return;
  if (c.follow === 'head') {
    const h = sk.index.Head, he = sk.index.HeadEnd, want = new V3((pose.P[h * 3] + pose.P[he * 3]) / 2, (pose.P[h * 3 + 1] + pose.P[he * 3 + 1]) / 2 - 0.02, (pose.P[h * 3 + 2] + pose.P[he * 3 + 2]) / 2);
    c.target.lerp(want, A.camK); A.camK = 0.3; return;
  }
  const h = sk.index.Hips; c.target.set(pose.P[h * 3], c.followY ?? 0.95, pose.P[h * 3 + 2]);
}
function applyMode() {
  st.look.flat = mode === 'clay' || mode === 'skeleton' ? [0.86, 0.83, 0.8] : null;
  ch.group.visible = mode !== 'skeleton'; st.look.shadow = mode !== 'skeleton' && A.shadow;
  ch.parts.face.mesh.material.uniforms.tFace.value = ch.texture;
}

const A = {
  MOTIONS, st, ch, camK: 1, shadow: true,
  // {size, clip, t, expr, talk, still, cam: {...}, look: {...}, mode, heading, hands, ladle, breath}
  async set(o) {
    this.camK = 1;
    if (o.size) st.size(o.size[0], o.size[1]);
    if (o.cam) for (const [k, v] of Object.entries(o.cam)) { if (k === 'target') st.cam.target.set(...v); else st.cam[k] = v; }
    if (o.look) { Object.assign(st.look, o.look); if ('shadow' in o.look) this.shadow = o.look.shadow; }
    if (o.mode) mode = o.mode;
    if ('heading' in o) cur.heading = o.heading;
    if ('breath' in o) cur.breath = o.breath;
    if (o.clip) {
      const next = STILL[o.clip] ? null : await getClip(o.clip, sk);   // loaded first: a frame may be drawn meanwhile
      cur.clip = o.clip; clip = next;
      const [hands, ladle] = HANDS[o.clip] || [{ L: 'fist', R: 'fist' }, false]; ch.setHands(hands, ladle);
    }
    if (o.hands || 'ladle' in o) ch.setHands(o.hands || {}, o.ladle ?? ch.ladle);
    if ('t' in o) cur.t = o.t;
    if (o.expr) ch.live.setExpr(o.expr);
    if ('talk' in o) ch.live.setTalk(o.talk);
    if ('still' in o) ch.live.still = o.still;
    if (o.settle !== false && (o.expr || o.still)) ch.live.settle();
    if (o.still) ch.live.step(0.001);
    const f = ch.live.face(); if (o.still) f.blink = 0;
    const pose = place(cur.t, f);
    ch.drawFace(f); aim(pose); applyMode(); showBones(pose);
  },
  // one moment of a film: the motion at t, the face lived on by dt
  frame({ t, dt = 1 / 30, expr, talk, cam_yaw, heading }) {
    if (cam_yaw !== undefined) st.cam.yaw = cam_yaw;
    if (heading !== undefined) cur.heading = heading;
    if (expr) ch.live.setExpr(expr);
    if (talk !== undefined) ch.live.setTalk(talk);
    cur.t = t;
    let ht = [0, 0], ah = [0, 0];
    if (clip) { ah = headTurn(place(t + 0.25)); ht = headTurn(place(t)); }
    ch.live.step(dt, { yaw: ht[0], pitch: ht[1], aheadYaw: ah[0], aheadPitch: ah[1] });
    const f = ch.live.face(), pose = place(t, f);
    ch.drawFace(f); aim(pose); showBones(pose);
  },
  render() { st.render(); },
  duration() { return clip ? clip.frames / clip.fps : 8; },
};
window.A = A;
st.size(cv.clientWidth || innerWidth, cv.clientHeight || innerHeight);
await A.set({ clip: 'stand', expr: { rest: 1 } });
A.render();
if (qs.has('shots')) { document.getElementById('msg')?.remove(); document.body.style.background = document.documentElement.style.background = 'transparent'; }
window.__ready = true;
