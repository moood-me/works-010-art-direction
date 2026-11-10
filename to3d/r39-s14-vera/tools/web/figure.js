// С14 in 3D — the figure: a paper puppet on SOMA's skeleton.
// The skeleton is SOMA's 77 joints placed by the drawing's sizes (the character's `joints`), the frames SOMA's own, so
// Kimodo's motions are carried by the engine as they are (engine/src: retarget, build). Limbs are stiff strips, each
// on one bone, overlapping at the joint with a brass brad through it — a cut-out puppet (перекладка); only the coat
// bends (a few joints per point). On top of a motion: the arm that holds something, the head's turn after the gaze,
// breath. The face is re-glued when its numbers change (blink, glance, expression, speech).
import * as THREE from 'three';
import { makeRetarget, build, turnUnder } from '../../../../engine/src/retarget.js';
import { qMul, qConj, qAxisAngle, qRot, getQ, setQ, getV } from '../../../../engine/src/math.js';
import { newSample } from '../../../../engine/src/motion.js';
import { facePieces, mixExpr, onHead, DEFAULT } from './face.js';
import { ell, curve, patch, V } from './paper.js';

export function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const qArc = (a, b) => {                                   // the shortest turn taking direction a to b
  const d = a[0] * b[0] + a[1] * b[1] + a[2] * b[2], c = V.cross(a, b);
  if (d < -.9999) return qAxisAngle(Math.abs(a[0]) < .9 ? [1, 0, 0] : [0, 1, 0], Math.PI);
  const q = [c[0], c[1], c[2], 1 + d], l = Math.hypot(...q); return q.map(x => x / l);
};

export class Figure {
  constructor(look, sk, C) {
    this.look = look; this.sk = sk; this.C = C; this.J = sk.J;
    const joints = C.joints(sk);
    this.body = { skeleton: sk, joints, frames: sk.frames, measures: { floor: 0, hipHeight: joints[sk.index.Hips * 3 + 1] } };
    this.retarget = makeRetarget(this.body, {});
    this.sample = newSample(sk.J);
    this.pose = { Q: new Float64Array(sk.J * 4), P: new Float64Array(sk.J * 3), floor: 0 };
    this.rigid = []; this.soft = []; this.bills = []; this.groups = {};
    this.spec = { ...DEFAULT, ...C.spec };
    this.faceMeshes = new Map(); this.faceKey = '';
    this.feet = ['LeftFoot', 'RightFoot', 'LeftToeBase', 'RightToeBase'].map(n => [sk.index[n], joints[sk.index[n] * 3 + 1]]);
    C.build(this);
    this.standPose();
  }
  R(name) { return getV(this.body.joints, this.sk.index[name]); }
  // a group that rides a joint; its own space starts at `origin` (rest, world)
  group(name, joint, origin) {
    const g = new THREE.Group(); g.matrixAutoUpdate = false; this.look.scene.add(g);
    this.groups[name] = { g, j: this.sk.index[joint], origin }; return g;
  }
  // a piece: {geo, color, kind, v, joint} rigid on a joint (geo in the rest's world space), or {weights: p → [[joint, w], …]}
  // or {group: name} (geo in the group's space)
  piece(p) {
    if (p.group) { p.parent = this.groups[p.group].g; this.look.add(p); p.mesh.matrix.identity(); return p; }
    this.look.add(p);
    if (p.weights) {
      const n = p.geo.pos.length / 3, W = [];
      for (let i = 0; i < n; i++) { const w = p.weights([p.geo.pos[i * 3], p.geo.pos[i * 3 + 1], p.geo.pos[i * 3 + 2]]); let s = 0; for (const x of w) s += x[1]; W.push(w.map(([j, x]) => [this.sk.index[j], x / s])); }
      this.soft.push({ p, W, rest: Float32Array.from(p.geo.pos) });
    } else this.rigid.push({ p, j: this.sk.index[p.joint] });
    return p;
  }
  // a small disc that always faces the eye (a brad in a joint, the end of a rolled strip): at a rest point of a joint
  bill(b) {
    const discs = b.discs.map((d, i) => {
      const geo = patch(ell(0, 0, 1, 1, 0, d.n || 12), (x, y) => [x, y, 0], { maxEdge: 9 });
      const p = { name: b.name || 'brad', geo, color: d.color, kind: i === 0 && !b.flat ? 'card' : 'flat', paint: d.paint, v: d.v }; this.look.add(p); return { ...d, p };
    });
    this.bills.push({ ...b, j: this.sk.index[b.joint], discs });
  }
  jointMatrix(j, m = new THREE.Matrix4()) {
    const q = getQ(this.pose.Q, j), P = this.pose.P, R = this.body.joints;
    const r = qRot(q, [R[j * 3], R[j * 3 + 1], R[j * 3 + 2]]);
    return m.compose(new THREE.Vector3(P[j * 3] - r[0], P[j * 3 + 1] - r[1], P[j * 3 + 2] - r[2]), new THREE.Quaternion(...q), new THREE.Vector3(1, 1, 1));
  }
  at(j, r) { const q = getQ(this.pose.Q, j), R = this.body.joints, P = this.pose.P, v = qRot(q, [r[0] - R[j * 3], r[1] - R[j * 3 + 1], r[2] - R[j * 3 + 2]]); return [P[j * 3] + v[0], P[j * 3 + 1] + v[1], P[j * 3 + 2] + v[2]]; }

  // ------------------------------------------------------------ poses
  // turn joint j (and all under it) so that its bone to `child` points along dir (world)
  aim(pose, j, child, dir) {
    const sk = this.sk, R = this.body.joints, a = sk.index[j], c = sk.index[child];
    const cur = V.norm(qRot(getQ(pose.Q, a), [R[c * 3] - R[a * 3], R[c * 3 + 1] - R[a * 3 + 1], R[c * 3 + 2] - R[a * 3 + 2]]));
    turnUnder(pose, sk, a, qArc(cur, V.norm(dir)));
  }
  twist(pose, j, child, deg) {
    const sk = this.sk, R = this.body.joints, a = sk.index[j], c = sk.index[child];
    const ax = V.norm(qRot(getQ(pose.Q, a), [R[c * 3] - R[a * 3], R[c * 3 + 1] - R[a * 3 + 1], R[c * 3 + 2] - R[a * 3 + 2]]));
    turnUnder(pose, sk, a, qAxisAngle(ax, deg * Math.PI / 180));
  }
  turn(pose, j, axis, deg) { turnUnder(pose, this.sk, this.sk.index[j], qAxisAngle(axis, deg * Math.PI / 180)); }
  // the drawn stand (the character's own), kept: the held arm is taken from it on every motion
  standPose() {
    const sk = this.sk, st = { Q: new Float64Array(sk.J * 4), P: new Float64Array(sk.J * 3) };
    for (let j = 0; j < sk.J; j++) setQ(st.Q, j, [0, 0, 0, 1]);
    this.C.stand(this, st);
    this.stand = st;
    const chest = sk.index.Chest;
    this.holdRel = (this.C.hold || []).map(n => { const j = sk.index[n]; return sk.under(j).map(k => [k, qMul(qConj(getQ(st.Q, chest)), getQ(st.Q, k))]); }).flat();
  }
  // the figure at a moment: a motion (clip, t in frames) or the stand; life adds the head's turn and breath
  frame({ clip = null, t = 0, place = { position: [0, 0, 0], heading: 0 }, life = null, hold = true }) {
    const sk = this.sk, body = this.body; let pose, hip;
    Object.assign(this.retarget.place, place);
    if (clip) {
      pose = this.retarget.pose(clip.sample(t, this.sample));
      hip = getV(pose.P, sk.index.Hips);
      if (hold) { const qc = getQ(pose.Q, sk.index.Chest); for (const [k, rel] of this.holdRel) setQ(pose.Q, k, qMul(qc, rel)); }
      if (this.C.onMotion) this.C.onMotion(this, pose);
    } else {
      pose = this.pose; pose.Q.set(this.stand.Q); pose.floor = 0;
      hip = getV(body.joints, sk.index.Hips);
    }
    if (life) {
      const D = Math.PI / 180, tw = (n, ax, rad) => turnUnder(pose, sk, sk.index[n], qAxisAngle(qRot(getQ(pose.Q, sk.index[n]), ax), rad));
      const br = life.breath() * (this.C.breath ?? 1) * D;
      tw('Chest', [1, 0, 0], -1.2 * br); tw('Neck1', [1, 0, 0], 1.0 * br);
      tw('Neck1', [0, 1, 0], .35 * life.headYaw * D); tw('Head', [0, 1, 0], .65 * life.headYaw * D); tw('Head', [1, 0, 0], (life.headNod + life.nod * 3) * D);
      tw('Head', [0, 0, 1], life.headTilt * D);
    }
    build(pose, body, hip);
    this.retarget.placed(pose);
    // on the floor: the lowest foot joint as high above it as at rest
    let lo = Infinity; for (const [j, h] of this.feet) lo = Math.min(lo, pose.P[j * 3 + 1] - h);
    const sh = (clip ? pose.floor : place.position[1]) - lo;
    for (let j = 0; j < sk.J; j++) pose.P[j * 3 + 1] += sh;
    this.pose = pose;
    this.apply();
  }
  apply() {
    for (const { p, j } of this.rigid) this.jointMatrix(j, p.mesh.matrix);
    const m = new THREE.Matrix4();
    for (const k in this.groups) { const G = this.groups[k]; this.jointMatrix(G.j, G.g.matrix); G.g.matrix.multiply(m.makeTranslation(...G.origin)); G.g.matrixWorldNeedsUpdate = true; }
    for (const { p, W, rest } of this.soft) {
      const a = p.mesh.geometry.attributes.position, out = a.array;
      for (let i = 0; i < W.length; i++) {
        let x = 0, y = 0, z = 0; const r = [rest[i * 3], rest[i * 3 + 1], rest[i * 3 + 2]];
        for (const [j, w] of W[i]) { const v = this.at(j, r); x += v[0] * w; y += v[1] * w; z += v[2] * w; }
        out[i * 3] = x; out[i * 3 + 1] = y; out[i * 3 + 2] = z;
      }
      a.needsUpdate = true;
    }
  }
  // discs that face the eye: called with the camera's place before drawing
  face(camPos, camQuat) {
    const q = new THREE.Quaternion(...camQuat), s = new THREE.Vector3();
    const right = new THREE.Vector3(1, 0, 0).applyQuaternion(q), up = new THREE.Vector3(0, 1, 0).applyQuaternion(q);
    for (const b of this.bills) {
      const c = new THREE.Vector3(...this.at(b.j, b.at)), to = new THREE.Vector3(...camPos).sub(c).normalize();
      b.discs.forEach((d, i) => {
        const p = c.clone().addScaledVector(to, (b.out || 0) + i * .0012).addScaledVector(right, (d.dx || 0) * b.r).addScaledVector(up, (d.dy || 0) * b.r);
        d.p.mesh.matrix.compose(p, q, s.set(b.r * d.k, b.r * d.k, 1));
      });
    }
  }
  // ------------------------------------------------------------ the face
  // e: the expression's numbers and mouth (+ look, look_y, say); re-glued only when something changed
  setFace(e) {
    const key = JSON.stringify(e, (k, v) => typeof v === 'number' ? Math.round(v * 60) / 60 : v);
    if (key === this.faceKey) return; this.faceKey = key;
    const C = this.C, H = this.head, hu = C.hu, seen = new Set();
    const list = [...facePieces(this.spec, e), ...(C.extras ? C.extras(this, e) : [])];
    for (const f of list) {
      const geo = onHead(H, hu, f.pts, f.layer, f);
      let p = this.faceMeshes.get(f.key);
      if (!p) { p = { name: 'f:' + f.key, color: f.color, kind: f.kind, parent: this.groups.head.g, geo }; this.look.add(p); p.mesh.matrix.identity(); this.faceMeshes.set(f.key, p); }
      else { this.look.setGeo(p.mesh, geo); p.mesh.material.uniforms.color.value.set(f.color); }
      p.mesh.visible = true; seen.add(f.key);
    }
    for (const [k, p] of this.faceMeshes) if (!seen.has(k)) p.mesh.visible = false;
  }
}

// ---------------------------------------------------------------- life: blinks, glances, the head after the gaze, speech, expressions
// Everything from one seeded stream stepped forward in time: the same film is the same every time. No sines.
export class Life {
  constructor(spec, seed = 7, C = {}) {
    this.spec = spec; this.r = rng(seed); this.C = C; this.t = 0;
    this.W = { calm: 1 }; this.goal = 'calm';
    this.blinkAt = 1 + this.r() * 2; this.blink = 0; this.bt = -1;
    this.look = 0; this.lookY = 0; this.gx = 0; this.gy = 0; this.sacAt = .4; this.headGoal = 0; this.headAt = 0; this.headYaw = 0; this.headNod = 0; this.headTilt = 0; this.nod = 0;
    this.talk = false; this.say = 0; this.sylAt = 0; this.sayGoal = 0; this.bre = 0;
    this.alive = true;
  }
  setExpr(name, snap) { this.goal = name; if (snap) this.W = { [name]: 1 }; }
  breath() { return this.bre; }
  step(dt) {
    const r = this.r; this.t += dt; const t = this.t;
    // expressions flow one into another (the mouth is swapped half-way)
    const a = 1 - Math.exp(-dt / .14); let sum = 0;
    for (const k of new Set([...Object.keys(this.W), this.goal])) { const g = k === this.goal ? 1 : 0; this.W[k] = (this.W[k] || 0) + (g - (this.W[k] || 0)) * a; if (this.W[k] < .003) delete this.W[k]; else sum += this.W[k]; }
    if (!this.alive) return;
    // breath: in a little faster than out, a pause after — a saw of two smooth pieces, period ~3.6 s
    const ph = (t % 3.6) / 3.6; this.bre = ph < .38 ? .5 - .5 * Math.cos(Math.PI * ph / .38) : ph < .9 ? .5 + .5 * Math.cos(Math.PI * (ph - .38) / .52) : 0;
    // blinks at uneven intervals: shut in ~75 ms, open in ~150 ms
    if (this.bt < 0 && t >= this.blinkAt) { this.bt = 0; this.blinkAt = t + .9 + r() * 4.2 + (r() < .15 ? -.6 : 0); }
    if (this.bt >= 0) { this.bt += dt; this.blink = this.bt < .075 ? this.bt / .075 : this.bt < .11 ? 1 : Math.max(0, 1 - (this.bt - .11) / .15); if (this.bt > .27) { this.bt = -1; this.blink = 0; } }
    // glances: the eyes jump and hold 0.2–1.6 s; a far glance takes the head along a quarter of a second later
    if (t >= this.sacAt) {
      const far = r() < .22;
      this.gx = far ? (r() < .5 ? -1 : 1) * (.55 + r() * .4) : (r() - .5) * .7; this.gy = (r() - .5) * (far ? .5 : .4);
      if (r() < .35) { this.gx *= .2; this.gy *= .2; }                    // back to the one she talks to
      this.sacAt = t + .2 + r() * 1.4;
      if (far || Math.abs(this.gx) < .15) { this.headGoal = this.gx * (this.C.headTurn ?? 16); this.headAt = t + .25; if (far && this.bt < 0 && r() < .6) this.bt = 0; }
    }
    const e = 1 - Math.exp(-dt / .035); this.look += (this.gx - this.look) * e; this.lookY += (this.gy - this.lookY) * e;
    if (t >= this.headAt) { const h = 1 - Math.exp(-dt / .22); this.headYaw += (this.headGoal - this.headYaw) * h; }
    // speech: syllables — the mouth opens to a height and shuts between; pauses between phrases
    if (this.talk) {
      if (t >= this.sylAt) {
        if (this.sayGoal > .1) { this.sayGoal = r() < .3 ? 0 : .08; this.sylAt = t + .05 + r() * .06; if (r() < .12) { this.sayGoal = 0; this.sylAt = t + .35 + r() * .7; } }
        else { this.sayGoal = .35 + r() * .65; this.sylAt = t + .09 + r() * .1; if (r() < .25) this.nod = 1; }
      }
    } else this.sayGoal = 0;
    this.say += (this.sayGoal - this.say) * (1 - Math.exp(-dt / .03));
    this.nod *= Math.exp(-dt / .18);
  }
  // the face's numbers now
  face() {
    const e = mixExpr(this.spec, this.W);
    if (this.alive) {
      if (e.open > .05) e.open = Math.max(.06, e.open * (1 - this.blink));
      e.look = clamp(this.look - this.headYaw / 40, -1, 1); e.look_y = this.lookY;
    }
    if (this.talk || this.say > .03) { if (['flat', 'smile', 'frown', 'smirk', 'talk'].includes(e.mouth) || this.say > .25) { e.mouth = 'talk'; e.say = this.say; } }
    return e;
  }
}
