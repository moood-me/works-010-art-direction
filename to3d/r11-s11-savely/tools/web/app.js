// The page's driver: the stage, Kimodo clips through the engine, the live face, and window.A for pictures
// (tools/shots.mjs). ui.js adds the controls when the page is opened without ?shots.
import * as THREE from 'three';
import { createStage, S } from './savely.js';
const qs = new URLSearchParams(location.search);
const cv = document.getElementById('cv');
const st = await createStage(cv, { pixelRatio: qs.has('shots') ? 1 : undefined });
const ch = st.ch, V3 = THREE.Vector3;

// motions: Kimodo's, from engine/motions (none made for him); "stand" is the still pose of the drawing
export const CLIPS = { stand: { ru: 'стоит' }, idle: { ru: 'стоит (Kimodo)' }, walk: { ru: 'идёт' }, wave: { ru: 'машет' }, dance: { ru: 'танцует' }, stomp: { ru: 'топает' }, sit: { ru: 'садится' }, bow: { ru: 'кланяется' } };
const clips = {};
const clipOf = async id => (clips[id] ??= await st.E.clip([id]));
const S0 = { clip: 'stand', t: 0, head: null, follow: null };
let cur = { ...S0 }, clip = null, lastHead = null;

// the head's turn against the chest (degrees), for the eyes to lead it
function headTurn(pose) {
  const ix = st.E.skeleton.index, q = i => new THREE.Quaternion(pose.Q[i * 4], pose.Q[i * 4 + 1], pose.Q[i * 4 + 2], pose.Q[i * 4 + 3]);
  const rel = q(ix.Chest).invert().multiply(q(ix.Head)), f = new V3(0, 0, 1).applyQuaternion(rel);
  return [Math.atan2(f.x, f.z) * 180 / Math.PI, Math.asin(Math.max(-1, Math.min(1, f.y))) * 180 / Math.PI];
}
function poseAt(t) {
  if (!clip) return ch.standPose(true, { head: cur.head });
  return ch.clipPose(clip, Math.min(clip.frames - 1, t * clip.fps));
}
const lowest = () => {   // the soles' lowest point now
  let lo = Infinity; const v = new V3();
  for (const sd of ['Left', 'Right']) { const g = ch.shoes[sd].parts[1].mesh.geometry, p = g.attributes.position; ch.shoes[sd].grp.updateMatrixWorld(true); const M = ch.shoes[sd].grp.matrixWorld; for (let i = 0; i < p.count; i += 3) { v.fromBufferAttribute(p, i).applyMatrix4(M); if (v.y < lo) lo = v.y; } }
  return lo;
};
function place(t) {
  const pose = poseAt(t);
  ch.root.position.y = 0;
  ch.apply(pose);
  const shift = (pose.floor ?? 0) - lowest() + (clip ? 0 : 0);
  ch.root.position.y = shift; ch.shadow.position.y = (pose.floor ?? 0) + 0.002;
  return pose;
}
function face() { const f = ch.live.face(); ch.setFace(f.e, { look: f.look, blink: f.blink }); }

// steps for the page: 'skeleton' (SOMA's joints at his proportions, bones as sticks), 'clay' (the forms alone, one
// grey, with the ink hull), 'paint' (the drawing's paints and marks, no film), 'film' (all)
let bones = null;
function setMode(mode) {
  const clay = mode === 'clay' || mode === 'skeleton';
  ch.root.traverse(o => {
    const u = o.material?.uniforms; if (!u?.uColor) return;
    u.__keep ??= { c: u.uColor.value.clone(), p: u.uPaint.value, s: u.uShine.value, sh: u.uShade.value };
    if (clay) { u.uColor.value.setRGB(0.80, 0.78, 0.74); u.uPaint.value = 0; u.uShine.value = 0; u.uShade.value = 0.28; }
    else { u.uColor.value.copy(u.__keep.c); u.uPaint.value = u.__keep.p; u.uShine.value = u.__keep.s; u.uShade.value = u.__keep.sh; }
  });
  ch.root.traverse(o => { if (o.isMesh) o.visible = mode !== 'skeleton'; });
  if (bones) { st.scene.remove(bones); bones = null; }
  if (mode === 'skeleton') {
    const sk = st.E.skeleton, P = ch.pose.P, g = new THREE.Group(), y = ch.root.position.y;
    const mat = new THREE.MeshBasicMaterial({ color: 0x8a2c22 }), mat2 = new THREE.MeshBasicMaterial({ color: 0x2a221e });
    for (let j = 0; j < sk.J; j++) {
      const p = new V3(P[j * 3], P[j * 3 + 1] + y, P[j * 3 + 2]), big = !/Hand[A-Z]|Toe|Eye|Jaw|HeadEnd/.test(sk.names[j]);
      const s = new THREE.Mesh(new THREE.SphereGeometry(big ? 0.022 : 0.008, 12, 8), mat); s.position.copy(p); g.add(s);
      const pj = sk.parent[j]; if (pj < 0) continue;
      const q = new V3(P[pj * 3], P[pj * 3 + 1] + y, P[pj * 3 + 2]), L = p.distanceTo(q); if (L < 1e-4) continue;
      const c = new THREE.Mesh(new THREE.CylinderGeometry(big ? 0.007 : 0.003, big ? 0.007 : 0.003, L, 8), mat2);
      c.position.copy(p).add(q).multiplyScalar(0.5); c.quaternion.setFromUnitVectors(new V3(0, 1, 0), p.clone().sub(q).normalize()); g.add(c);
    }
    bones = g; st.scene.add(g);
  }
  ch.shadow.visible = mode !== 'skeleton';
}

const A = {
  CLIPS, st, ch,
  // {size, clip, t, expr, talk, still, head: [yaw, pitch], cam: {...}, film, bw, seed}
  async set(o) {
    this.camK = 1;
    if (o.size) st.size(o.size[0], o.size[1]);
    if (o.cam) { for (const [k, v] of Object.entries(o.cam)) { if (k === 'target') st.cam.target.set(...v); else if (k === 'ortho') Object.assign(st.cam.ortho, v); else st.cam[k] = v; } }
    if ('film' in o) st.film = o.film;
    if (o.mode) { this.mode = o.mode; }
    if ('bw' in o) st.post.uniforms.uBW.value = o.bw ? 1 : 0;
    if ('seed' in o) st.seed = o.seed;
    if ('wob' in o) st.post.uniforms.uWob.value = o.wob;
    if (o.clip) { cur.clip = o.clip; clip = o.clip === 'stand' ? null : await clipOf(o.clip); }
    if ('head' in o) cur.head = o.head;
    if ('t' in o) cur.t = o.t;
    if (o.expr) ch.live.setExpr(o.expr);
    if ('talk' in o) ch.live.setTalk(o.talk);
    if ('still' in o) ch.live.still = o.still;
    if (o.settle !== false && (o.expr || o.still)) ch.live.settle();
    const pose = place(cur.t);
    if (o.still) { ch.live.step(0.001); }
    face(); this.aim(pose);
    if (this.mode) setMode(this.mode);
  },
  // one moment of a film: the motion at t, the face lived on by dt
  frame({ t, dt = 1 / 30, expr, talk, cam_yaw }) {
    if (cam_yaw !== undefined) st.cam.yaw = cam_yaw;
    if (expr) ch.live.setExpr(expr);
    if (talk !== undefined) ch.live.setTalk(talk);
    cur.t = t;
    const pose = place(t);
    // the head's centre and its bounce: a rubber spring kicked by the head's vertical acceleration
    const hy = ch.head.position.y + ch.root.position.y;
    if (lastHead !== null && dt > 0) {
      const vy = (hy - lastHead.y) / dt, ay = (vy - lastHead.vy) / dt, d = ch.dyn, w = 16, z = 0.3;
      d.v += (-w * w * d.sy - 2 * z * w * d.v - Math.max(-60, Math.min(60, ay)) * 0.0011) * dt; d.sy += d.v * dt; d.sy = Math.max(-0.06, Math.min(0.06, d.sy));
      lastHead = { y: hy, vy };
    } else lastHead = { y: hy, vy: 0 };
    let ht = [0, 0], ah = [0, 0];
    if (clip) { ht = headTurn(pose); ah = headTurn(ch.clipPose(clip, Math.min(clip.frames - 1, (t + 0.25) * clip.fps))); place(t); }
    ch.live.step(dt, { yaw: ht[0], pitch: ht[1], aheadYaw: ah[0], aheadPitch: ah[1] });
    face(); this.aim(pose);
    st.seed = Math.floor(t * 12);   // the line boils at 12 drawings a second, as on film
  },
  aim(pose) {
    if (!st.cam.follow) return;
    if (st.cam.followHead) {   // the face close: the head's centre, smoothed a little so the camera does not shake
      const h = ch.head.getWorldPosition(new V3()), t = st.cam.target, k = this.camK ?? 1;
      t.lerp(new V3(h.x, h.y - 0.03, h.z), k); this.camK = 0.25; return;
    }
    const ix = st.E.skeleton.index, h = new V3(pose.P[ix.Hips * 3], 0, pose.P[ix.Hips * 3 + 2]);
    st.cam.target.set(h.x, st.cam.followY ?? 0.75, h.z);
  },
  render() { st.render(); },
  duration() { return clip ? clip.frames / clip.fps : 6; },
};
window.A = A;
st.size(cv.clientWidth || innerWidth, cv.clientHeight || innerHeight);
await A.set({ clip: 'stand', expr: { neutral: 1 } });
A.render();
if (qs.has('shots')) document.getElementById('msg')?.remove();
window.__ready = true;
