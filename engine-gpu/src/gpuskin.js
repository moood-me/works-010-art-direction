// Skinning on the video card: the engine's skinning (engine/src/skin.js — centres of rotation, dual quaternions,
// linear) computed in the vertex shader, so each frame the processor works out only the joints.
//
//   const gs = new GpuSkin(THREE, skinner)        the engine's Skinner of a body (its centres of rotation are reused)
//   gs.attributes(geometry)                       position, normal (the rest's), skinJ, skinW, skinC, skinD
//   material: uniforms: { ...gs.uniforms }, vertexShader: gs.glsl + `… skinVertex(position, normal, P, N) …`
//   gs.setPose(pose)                              each frame: the joints' turns and places into the joint texture
//
// What the processor still needs of the posed skin, it gets for a few vertices only:
//   gs.subset(indices) → { skin(pose, out) }      those vertices skinned as the engine does (the same numbers)
//   gs.lowest(pose)                               the skin's lowest point, from a probe of each part's outermost vertices
//   gs.displace(first, count)                     a part of skinD to refill: an offset added after skinning (world)
//
// Normals are the rest's, turned with the vertex's blended joint turn — not recomputed from the posed triangles.
// At a deep bend they differ a little from the recomputed ones; nothing is added for that.
import { normalsOf } from '../../engine/src/skin.js';

const GLSL = method => `
uniform sampler2D skinTex;             // J × 2: row 0 — each joint's turn (quaternion), row 1 — its T (x ↦ R x + T)
attribute vec4 skinJ; attribute vec4 skinW; attribute vec4 skinC; attribute vec3 skinD;
vec3 skinRot(vec4 q, vec3 v) { return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v); }
vec4 skinMul(vec4 a, vec4 b) { return vec4(a.w * b.xyz + b.w * a.xyz + cross(a.xyz, b.xyz), a.w * b.w - dot(a.xyz, b.xyz)); }
void skinVertex(vec3 p, vec3 n, out vec3 P, out vec3 N) {
  vec4 q0 = texelFetch(skinTex, ivec2(int(skinJ.x + 0.5), 0), 0), q = vec4(0.0), d = vec4(0.0);
  vec3 c = skinC.w > 0.5 ? skinC.xyz : p, t = vec3(0.0);
  for (int k = 0; k < 4; k++) {
    float w = skinW[k]; if (w <= 0.0) continue;
    int j = int(skinJ[k] + 0.5);
    vec4 qj = texelFetch(skinTex, ivec2(j, 0), 0); vec3 tj = texelFetch(skinTex, ivec2(j, 1), 0).xyz;
    float s = dot(qj, q0) < 0.0 ? -w : w;
    q += s * qj;
    ${method === 'dqs' ? 'd += s * 0.5 * skinMul(vec4(tj, 0.0), qj);' : 't += w * (skinRot(qj, c) + tj);'}
  }
  float l = length(q); l = l > 0.0 ? l : 1.0; q /= l;
  ${method === 'dqs' ? 'd /= l; P = skinRot(q, p) + 2.0 * skinMul(d, vec4(-q.xyz, q.w)).xyz;'
    : method === 'cor' ? 'P = skinRot(q, p - c) + t;' : 'P = t;'}
  P += skinD;
  N = skinRot(q, n);
}`;

export class GpuSkin {
  constructor(THREE, skinner) {
    this.THREE = THREE; this.skinner = skinner; this.body = skinner.body; this.method = skinner.method;
    const { N, J } = skinner, body = this.body;
    this.N = N; this.J = J;
    this.data = new Float32Array(J * 2 * 4);
    this.texture = new THREE.DataTexture(this.data, J, 2, THREE.RGBAFormat, THREE.FloatType);
    this.texture.minFilter = this.texture.magFilter = THREE.NearestFilter; this.texture.needsUpdate = true;
    this.uniforms = { skinTex: { value: this.texture } };
    this.glsl = GLSL(this.method);
    // per vertex: the joints, the weights, the centre of rotation (w: it has one), the rest's normal, the offset
    this.skinJ = Float32Array.from(body.skin.joints); this.skinW = Float32Array.from(body.skin.weights);
    this.skinC = new Float32Array(N * 4);
    if (this.method === 'cor') for (let i = 0; i < N; i++) if (skinner.hasCor[i]) { this.skinC.set(skinner.cor.subarray(i * 3, i * 3 + 3), i * 4); this.skinC[i * 4 + 3] = 1; }
    this.rest = Float32Array.from(body.positions);
    this.normal = normalsOf(this.rest, body.triangles, new Float32Array(N * 3));
    this.skinD = new Float32Array(N * 3);
  }

  attributes(geometry) {
    const { THREE } = this, A = (a, n) => new THREE.BufferAttribute(a, n);
    geometry.setAttribute('position', A(this.rest, 3)); geometry.setAttribute('normal', A(this.normal, 3));
    geometry.setAttribute('skinJ', A(this.skinJ, 4)); geometry.setAttribute('skinW', A(this.skinW, 4));
    geometry.setAttribute('skinC', A(this.skinC, 4));
    this.dAttr = A(this.skinD, 3); this.dAttr.setUsage(THREE.DynamicDrawUsage); geometry.setAttribute('skinD', this.dAttr);
    return geometry;
  }

  // the pose's joints into the texture
  setPose(pose) {
    const s = this.skinner, D = this.data, J = this.J; s.transforms(pose);
    for (let j = 0; j < J; j++) {
      D[j * 4] = pose.Q[j * 4]; D[j * 4 + 1] = pose.Q[j * 4 + 1]; D[j * 4 + 2] = pose.Q[j * 4 + 2]; D[j * 4 + 3] = pose.Q[j * 4 + 3];
      const o = (J + j) * 4; D[o] = s.T[j * 3]; D[o + 1] = s.T[j * 3 + 1]; D[o + 2] = s.T[j * 3 + 2];
    }
    this.texture.needsUpdate = true;
  }

  // a few vertices skinned on the processor, as engine/src/skin.js skins them (after skinner.transforms(pose))
  subset(indices) {
    const idx = Int32Array.from(indices), self = this;
    return {
      indices: idx,
      // out: Float32Array idx.length × 3
      skin(pose, out) {
        const s = self.skinner, { R, T } = s, P = self.rest, Jn = self.skinJ, W = self.skinW, C = self.skinC, Q = pose.Q, dqs = self.method === 'dqs';
        s.transforms(pose);
        for (let n = 0; n < idx.length; n++) {
          const i = idx[n], x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2], has = C[i * 4 + 3] > 0.5;
          const cx = has ? C[i * 4] : x, cy = has ? C[i * 4 + 1] : y, cz = has ? C[i * 4 + 2] : z;
          const j0 = Jn[i * 4] * 4; let qx = 0, qy = 0, qz = 0, qw = 0, X = 0, Y = 0, Z = 0, dx = 0, dy = 0, dz = 0, dw = 0;
          for (let k = 0; k < 4; k++) {
            const w = W[i * 4 + k]; if (!(w > 0)) continue; const j = Jn[i * 4 + k], o = j * 4, r = j * 9;
            const ax = Q[o], ay = Q[o + 1], az = Q[o + 2], aw = Q[o + 3];
            const sg = (ax * Q[j0] + ay * Q[j0 + 1] + az * Q[j0 + 2] + aw * Q[j0 + 3]) < 0 ? -w : w;
            qx += sg * ax; qy += sg * ay; qz += sg * az; qw += sg * aw;
            if (dqs) {       // ½ (t, 0) · q
              const tx = T[j * 3], ty = T[j * 3 + 1], tz = T[j * 3 + 2], h = sg * 0.5;
              dx += h * (aw * tx + ty * az - tz * ay); dy += h * (aw * ty + tz * ax - tx * az); dz += h * (aw * tz + tx * ay - ty * ax); dw += h * -(tx * ax + ty * ay + tz * az);
            } else {
              X += w * (R[r] * cx + R[r + 1] * cy + R[r + 2] * cz + T[j * 3]);
              Y += w * (R[r + 3] * cx + R[r + 4] * cy + R[r + 5] * cz + T[j * 3 + 1]);
              Z += w * (R[r + 6] * cx + R[r + 7] * cy + R[r + 8] * cz + T[j * 3 + 2]);
            }
          }
          const l = Math.hypot(qx, qy, qz, qw) || 1; qx /= l; qy /= l; qz /= l; qw /= l;
          let vx, vy, vz;
          if (dqs) { vx = x; vy = y; vz = z; } else if (has) { vx = x - cx; vy = y - cy; vz = z - cz; } else { vx = vy = vz = 0; }
          // v + 2 q × (q × v + w v)
          const ux = qy * vz - qz * vy + qw * vx, uy = qz * vx - qx * vz + qw * vy, uz = qx * vy - qy * vx + qw * vz;
          let ox = vx + 2 * (qy * uz - qz * uy), oy = vy + 2 * (qz * ux - qx * uz), oz = vz + 2 * (qx * uy - qy * ux);
          if (dqs) {         // + 2 (d · q*).xyz
            dx /= l; dy /= l; dz /= l; dw /= l;
            ox += 2 * (-dw * qx + qw * dx - (dy * qz - dz * qy)); oy += 2 * (-dw * qy + qw * dy - (dz * qx - dx * qz)); oz += 2 * (-dw * qz + qw * dz - (dx * qy - dy * qx));
          } else { ox += X; oy += Y; oz += Z; }
          out[n * 3] = ox; out[n * 3 + 1] = oy; out[n * 3 + 2] = oz;
        }
        return out;
      },
    };
  }

  // the skin's lowest point in the pose, from a probe of the skin instead of all of it:
  //   · where the skin turns with one joint, it is lowest at one of that part's own outermost vertices — for each
  //     joint, the vertices it leads that lie furthest out in 200 directions;
  //   · where joints share the skin (bends, cloth between the legs) no such vertex is known beforehand — there, one
  //     vertex of every `cell` of space (1.5 cm), so the lowest of them is that near the lowest of all.
  lowest(pose, cell = 0.015) {
    if (!this.probe) {
      const { N, rest: P, skinJ, skinW } = this, dirs = [], n = 200, pick = new Set(), cells = new Set();
      for (let k = 0; k < n; k++) { const y = 1 - 2 * (k + 0.5) / n, r = Math.sqrt(1 - y * y), a = k * Math.PI * (3 - Math.sqrt(5)); dirs.push([Math.cos(a) * r, y, Math.sin(a) * r]); }
      const lead = new Int32Array(N), share = new Float32Array(N);
      for (let i = 0; i < N; i++) { let b = 0; for (let k = 1; k < 4; k++) if (skinW[i * 4 + k] > skinW[i * 4 + b]) b = k; lead[i] = skinJ[i * 4 + b]; share[i] = skinW[i * 4 + b]; }
      const best = new Float64Array(this.J * n).fill(-Infinity), at = new Int32Array(this.J * n).fill(-1);
      for (let i = 0; i < N; i++) { const o = lead[i] * n, x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
        for (let k = 0; k < n; k++) { const d = dirs[k], v = x * d[0] + y * d[1] + z * d[2]; if (v > best[o + k]) { best[o + k] = v; at[o + k] = i; } }
        if (share[i] < 0.95) { const key = Math.floor(x / cell) + ',' + Math.floor(y / cell) + ',' + Math.floor(z / cell); if (!cells.has(key)) { cells.add(key); pick.add(i); } } }
      for (const i of at) if (i >= 0) pick.add(i);
      this.probe = this.subset([...pick]); this.probeOut = new Float32Array(pick.size * 3);
    }
    const out = this.probe.skin(pose, this.probeOut); let lo = Infinity;
    for (let i = 1; i < out.length; i += 3) if (out[i] < lo) lo = out[i];
    return lo;
  }

  // skinD's vertices first … first + count were refilled: send them (several parts a frame may be sent)
  displace(first, count) {
    const a = this.dAttr; a.addUpdateRange(first * 3, count * 3); a.needsUpdate = true;
  }
}
