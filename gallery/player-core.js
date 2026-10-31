// What the gallery's viewer and the pages share: a motion's turns on a skeleton, and skinning meshes along them.

// the bone that follows each joint, to know which way the joint's bone points at rest
const CHAIN = { Hips: 'Spine1', Spine1: 'Spine2', Spine2: 'Chest', Chest: 'Neck1', Neck1: 'Neck2', Neck2: 'Head', Head: 'HeadEnd',
  LeftShoulder: 'LeftArm', LeftArm: 'LeftForeArm', LeftForeArm: 'LeftHand', LeftHand: 'LeftHandMiddle1',
  RightShoulder: 'RightArm', RightArm: 'RightForeArm', RightForeArm: 'RightHand', RightHand: 'RightHandMiddle1',
  LeftLeg: 'LeftShin', LeftShin: 'LeftFoot', LeftFoot: 'LeftToeBase', RightLeg: 'RightShin', RightShin: 'RightFoot', RightFoot: 'RightToeBase' };

// each joint's turn in the person's space at a frame, for a skeleton of `names` with rest positions `rest` (V3)
export function turns(THREE, M, f, names, parent, rest, memo) {
  const Q = THREE.Quaternion, W = new Array(names.length);
  const C = memo.C ??= names.map((n, j) => {
    const c = CHAIN[n], ci = names.indexOf(c);
    if (!c || ci < 0 || !M.rest[c] || !M.rest[n]) return null;
    const ours = rest[ci].clone().sub(rest[j]), soma = new THREE.Vector3(...M.rest[c]).sub(new THREE.Vector3(...M.rest[n]));
    if (ours.lengthSq() < 1e-10 || soma.lengthSq() < 1e-10) return null;
    return new Q().setFromUnitVectors(ours.normalize(), soma.normalize());
  });
  for (let j = 0; j < names.length; j++) {
    const d = M.D[names[j]], p = parent[j];
    if (d) { const o = f * 4; W[j] = new Q(d[o], d[o + 1], d[o + 2], d[o + 3]); if (C[j]) W[j].multiply(C[j]); }
    else W[j] = p >= 0 ? W[p].clone() : new Q();
  }
  return W;
}

// moving meshes along a body on SOMA's joints: the body by its own skin weights, the rest by the nearest body skin
class Skinner {
  constructor(THREE, o) {
    Object.assign(this, { THREE, names: o.names, parent: o.parent, rest: o.rest, memo: {} });
    const N = o.body.length / 3;
    this.root = o.names.indexOf('Hips');
    this.items = [];
    // a grid over the body at rest, to find the nearest skin
    const cell = 0.03, grid = new Map(), key = (x, y, z) => x + ',' + y + ',' + z;
    for (let i = 0; i < N; i++) { const k = key(Math.floor(o.body[i * 3] / cell), Math.floor(o.body[i * 3 + 1] / cell), Math.floor(o.body[i * 3 + 2] / cell)); let a = grid.get(k); if (!a) grid.set(k, a = []); a.push(i); }
    const nearest = (x, y, z) => {
      const cx = Math.floor(x / cell), cy = Math.floor(y / cell), cz = Math.floor(z / cell);
      for (let r = 0; r < 14; r++) {
        let best = -1, bd = Infinity;
        for (let dx = -r; dx <= r; dx++) for (let dy = -r; dy <= r; dy++) for (let dz = -r; dz <= r; dz++) {
          if (Math.max(Math.abs(dx), Math.abs(dy), Math.abs(dz)) !== r) continue;
          const a = grid.get(key(cx + dx, cy + dy, cz + dz)); if (!a) continue;
          for (const i of a) { const d = (o.body[i * 3] - x) ** 2 + (o.body[i * 3 + 1] - y) ** 2 + (o.body[i * 3 + 2] - z) ** 2; if (d < bd) { bd = d; best = i; } }
        }
        if (best >= 0 && Math.sqrt(bd) < (r + 1) * cell) return best;
      }
      let best = 0, bd = Infinity; for (let i = 0; i < N; i++) { const d = (o.body[i * 3] - x) ** 2 + (o.body[i * 3 + 1] - y) ** 2 + (o.body[i * 3 + 2] - z) ** 2; if (d < bd) { bd = d; best = i; } }
      return best;
    };
    for (const { mesh, isBody, rigid } of o.meshes) {
      const g = mesh.geometry, pa = g.attributes.position, n = pa.count;
      const it = { mesh, pos: Float32Array.from(pa.array), nor: g.attributes.normal ? Float32Array.from(g.attributes.normal.array) : null, j: new Uint8Array(n * 4), w: new Float32Array(n * 4), isBody };
      if (isBody) { for (let i = 0; i < n * 4; i++) { it.j[i] = o.joint[i]; it.w[i] = o.weight[i] / 255; } }
      else if (rigid != null) { for (let i = 0; i < n; i++) { it.j[i * 4] = rigid; it.w[i * 4] = 1; } }
      else for (let i = 0; i < n; i++) { const b = nearest(it.pos[i * 3], it.pos[i * 3 + 1], it.pos[i * 3 + 2]); for (let k = 0; k < 4; k++) { it.j[i * 4 + k] = o.joint[b * 4 + k]; it.w[i * 4 + k] = o.weight[b * 4 + k] / 255; } }
      this.items.push(it);
    }
    this.bodyItem = this.items.find(t => t.isBody);
    this.floor0 = this.minY(this.bodyItem ? this.bodyItem.pos : this.items[0].pos);
  }
  minY(a) { let m = Infinity; for (let i = 1; i < a.length; i += 3) if (a[i] < m) m = a[i]; return m; }
  restPose() { for (const t of this.items) this.write(t, t.pos, t.nor); }
  write(t, p, n) {
    const g = t.mesh.geometry; g.attributes.position.array.set(p); g.attributes.position.needsUpdate = true;
    if (n && g.attributes.normal) { g.attributes.normal.array.set(n); g.attributes.normal.needsUpdate = true; }
    g.computeBoundingSphere();
  }
  pose(M, f) {
    const { THREE, names, parent, rest } = this, V3 = THREE.Vector3;
    const W = turns(THREE, M, f, names, parent, rest, this.memo), P = new Array(names.length);
    const k = rest[this.root].y / M.hipY;
    for (let j = 0; j < names.length; j++) {
      const p = parent[j];
      P[j] = p < 0 ? new V3(rest[j].x, M.hips[f * 3 + 1] * k, rest[j].z) : P[p].clone().add(rest[j].clone().sub(rest[p]).applyQuaternion(W[p]));
    }
    const E = names.map((_, j) => new THREE.Matrix4().makeTranslation(P[j].x, P[j].y, P[j].z).multiply(new THREE.Matrix4().makeRotationFromQuaternion(W[j])).multiply(new THREE.Matrix4().makeTranslation(-rest[j].x, -rest[j].y, -rest[j].z)).elements);
    const out = this.items.map(t => this.skin(t, E));
    // the feet as high above the floor as SOMA's are now
    const bi = this.bodyItem ? this.items.indexOf(this.bodyItem) : 0;
    const shift = this.floor0 + M.foot[f] * k - this.minY(out[bi][0]);
    out.forEach(([p, n], i) => { for (let v = 1; v < p.length; v += 3) p[v] += shift; this.write(this.items[i], p, n); });
  }
  skin(t, E) {
    const n = t.pos.length / 3, p = new Float32Array(n * 3), q = t.nor ? new Float32Array(n * 3) : null;
    for (let i = 0; i < n; i++) {
      const x = t.pos[i * 3], y = t.pos[i * 3 + 1], z = t.pos[i * 3 + 2];
      let X = 0, Y = 0, Z = 0, nx = 0, ny = 0, nz = 0, ws = 0;
      const ax = q ? t.nor[i * 3] : 0, ay = q ? t.nor[i * 3 + 1] : 0, az = q ? t.nor[i * 3 + 2] : 0;
      for (let k = 0; k < 4; k++) {
        const w = t.w[i * 4 + k]; if (!w) continue; const e = E[t.j[i * 4 + k]];
        X += w * (e[0] * x + e[4] * y + e[8] * z + e[12]); Y += w * (e[1] * x + e[5] * y + e[9] * z + e[13]); Z += w * (e[2] * x + e[6] * y + e[10] * z + e[14]);
        if (q) { nx += w * (e[0] * ax + e[4] * ay + e[8] * az); ny += w * (e[1] * ax + e[5] * ay + e[9] * az); nz += w * (e[2] * ax + e[6] * ay + e[10] * az); }
        ws += w;
      }
      if (ws < 1e-6) { X = x; Y = y; Z = z; ws = 1; }
      p[i * 3] = X / ws; p[i * 3 + 1] = Y / ws; p[i * 3 + 2] = Z / ws;
      if (q) { const l = Math.hypot(nx, ny, nz) || 1; q[i * 3] = nx / l; q[i * 3 + 1] = ny / l; q[i * 3 + 2] = nz / l; }
    }
    return [p, q];
  }
}
export { Skinner };
