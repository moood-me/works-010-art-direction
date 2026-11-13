// Skinning on the video card: the engine's skinning (engine/src/skin.js — centres of rotation, dual quaternions,
// linear) and its normals (normalsOf: from the posed triangles) computed on the video card, so each frame the
// processor works out only the joints.
//
// Each frame the skin is drawn twice into two small textures, a texel a vertex:
//   1. every vertex skinned (its place in the pose) → skinPos;
//   2. every vertex's normal, from the posed places of the triangles around it → skinNrm.
// The materials that draw the skin (the body, an outline's hull, a shadow map's depth) only read the two texels of
// their vertex. So the skin is skinned once a frame however many times it is drawn, the normals are those of the
// posed skin (folds of cloth, bends), and the drawn geometry carries no skinning attributes.
//
//   const gs = new GpuSkin(THREE, skinner)        the engine's Skinner of a body (its centres of rotation are reused)
//   gs.attributes(geometry)                       position and normal: the rest's (three.js wants them; the shader reads the textures)
//   material: uniforms: { ...gs.uniforms }, vertexShader: gs.glsl + `… vec3 P, N; skinVertex(P, N); …`
//   each frame: gs.setPose(pose); …; gs.update(renderer) before the skin is drawn
//
// What the processor still needs of the posed skin, it gets for a few vertices only:
//   gs.subset(indices) → { skin(pose, out) }      those vertices skinned as the engine does (the same numbers)
//   gs.lowest(pose)                               the skin's lowest point, from a probe of the skin
//   gs.skinD, gs.displace(first, count)           an offset (world) added after skinning: refill a part, say which
import { normalsOf } from '../../engine/src/skin.js';

const WIDTH = 256;      // the textures' width: vertex i is texel (i % WIDTH, i / WIDTH)
const AT = `ivec2 skinAt(int i) { return ivec2(i % ${WIDTH}, i / ${WIDTH}); }`;
const TEXEL = `gl_Position = vec4((vec2(skinAt(gl_VertexID)) + 0.5) / skinSize * 2.0 - 1.0, 0.0, 1.0); gl_PointSize = 1.0;`;
// pass 1: a vertex's place in the pose
const PLACE = method => `
uniform sampler2D skinTex;             // J × 2: row 0 — each joint's turn (quaternion), row 1 — its T (x ↦ R x + T)
uniform vec2 skinSize;
attribute vec4 skinJ; attribute vec4 skinW; attribute vec4 skinC; attribute vec3 skinD;
varying vec3 vP;
${AT}
vec3 skinRot(vec4 q, vec3 v) { return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v); }
vec4 skinMul(vec4 a, vec4 b) { return vec4(a.w * b.xyz + b.w * a.xyz + cross(a.xyz, b.xyz), a.w * b.w - dot(a.xyz, b.xyz)); }
void main() {
  vec3 p = position;
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
  ${method === 'dqs' ? 'd /= l; vP = skinRot(q, p) + 2.0 * skinMul(d, vec4(-q.xyz, q.w)).xyz;'
    : method === 'cor' ? 'vP = skinRot(q, p - c) + t;' : 'vP = t;'}
  vP += skinD;
  ${TEXEL}
}`;
// pass 2: a vertex's normal — the sum of the posed triangles' around it (each as large as its area), as normalsOf
const NORMAL = `
uniform sampler2D skinPos; uniform sampler2D skinRing; uniform sampler2D skinFan; uniform vec2 skinSize;
varying vec3 vP;
${AT}
void main() {
  ivec2 at = skinAt(gl_VertexID);
  vec3 p = texelFetch(skinPos, at, 0).xyz, n = vec3(0.0);
  vec2 ring = texelFetch(skinRing, at, 0).xy;                     // where this vertex's triangles begin in skinFan, how many
  int first = int(ring.x + 0.5), count = int(ring.y + 0.5);
  for (int k = 0; k < count; k++) {
    vec2 bc = texelFetch(skinFan, skinAt(first + k), 0).xy;         // the triangle's two other vertices, in its order
    n += cross(texelFetch(skinPos, skinAt(int(bc.x + 0.5)), 0).xyz - p, texelFetch(skinPos, skinAt(int(bc.y + 0.5)), 0).xyz - p);
  }
  float l = length(n); vP = l > 0.0 ? n / l : n;
  ${TEXEL}
}`;
const OUT = `varying vec3 vP; void main() { gl_FragColor = vec4(vP, 1.0); }`;
// what a material that draws the skin takes
const GLSL = `
uniform sampler2D skinPos; uniform sampler2D skinNrm;
void skinVertex(out vec3 P, out vec3 N) {
  ivec2 at = ivec2(gl_VertexID % ${WIDTH}, gl_VertexID / ${WIDTH});
  P = texelFetch(skinPos, at, 0).xyz; N = texelFetch(skinNrm, at, 0).xyz;
}`;

export class GpuSkin {
  constructor(THREE, skinner) {
    this.THREE = THREE; this.skinner = skinner; this.body = skinner.body; this.method = skinner.method;
    const { N, J } = skinner, body = this.body, tris = body.triangles;
    this.N = N; this.J = J;
    const data = (a, w, h, format) => { const t = new THREE.DataTexture(a, w, h, format, THREE.FloatType); t.minFilter = t.magFilter = THREE.NearestFilter; t.needsUpdate = true; return t; };
    this.data = new Float32Array(J * 2 * 4); this.texture = data(this.data, J, 2, THREE.RGBAFormat);
    // per vertex: the joints, the weights, the centre of rotation (w: it has one), the offset; the rest and its normals
    this.skinJ = Float32Array.from(body.skin.joints); this.skinW = Float32Array.from(body.skin.weights);
    this.skinC = new Float32Array(N * 4);
    if (this.method === 'cor') for (let i = 0; i < N; i++) if (skinner.hasCor[i]) { this.skinC.set(skinner.cor.subarray(i * 3, i * 3 + 3), i * 4); this.skinC[i * 4 + 3] = 1; }
    this.rest = Float32Array.from(body.positions);
    this.normal = normalsOf(this.rest, tris, new Float32Array(N * 3));
    this.skinD = new Float32Array(N * 3);
    // the triangles around each vertex: ring — where they begin and how many; fan — each one's two other vertices
    const H = Math.ceil(N / WIDTH), ring = new Float32Array(WIDTH * H * 2), FH = Math.ceil(tris.length / WIDTH), fan = new Float32Array(WIDTH * FH * 2), fill = new Int32Array(N);
    for (let t = 0; t < tris.length; t++) ring[tris[t] * 2 + 1]++;
    for (let i = 0, at = 0; i < N; i++) { ring[i * 2] = at; at += ring[i * 2 + 1]; }
    for (let t = 0; t < tris.length; t += 3) for (let k = 0; k < 3; k++) {
      const v = tris[t + k], o = (ring[v * 2] + fill[v]++) * 2; fan[o] = tris[t + (k + 1) % 3]; fan[o + 1] = tris[t + (k + 2) % 3];
    }
    const target = () => new THREE.WebGLRenderTarget(WIDTH, H, { type: THREE.FloatType, format: THREE.RGBAFormat, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, depthBuffer: false });
    this.posRT = target(); this.nrmRT = target();
    this.uniforms = { skinPos: { value: this.posRT.texture }, skinNrm: { value: this.nrmRT.texture } };
    this.glsl = GLSL;
    // the two passes: the vertices as points, each onto its own texel
    const A = (a, n) => new THREE.BufferAttribute(a, n), g = new THREE.BufferGeometry();
    g.setAttribute('position', A(this.rest, 3)); g.setAttribute('skinJ', A(this.skinJ, 4)); g.setAttribute('skinW', A(this.skinW, 4)); g.setAttribute('skinC', A(this.skinC, 4));
    this.dAttr = A(this.skinD, 3); this.dAttr.setUsage(THREE.DynamicDrawUsage); g.setAttribute('skinD', this.dAttr);
    const size = { value: new THREE.Vector2(WIDTH, H) }, pass = (vertexShader, uniforms) => {
      const m = new THREE.Points(g, new THREE.ShaderMaterial({ uniforms: { skinSize: size, ...uniforms }, vertexShader, fragmentShader: OUT, depthTest: false, depthWrite: false }));
      m.frustumCulled = false; const scene = new THREE.Scene(); scene.add(m); return scene;
    };
    this.place = pass(PLACE(this.method), { skinTex: { value: this.texture } });
    this.around = pass(NORMAL, { skinPos: { value: this.posRT.texture }, skinRing: { value: data(ring, WIDTH, H, THREE.RGFormat) }, skinFan: { value: data(fan, WIDTH, FH, THREE.RGFormat) } });
    this.camera = new THREE.Camera();
  }

  // the drawn geometry's position and normal: the rest's (the shader takes the posed ones from the textures)
  attributes(geometry) {
    const { THREE } = this;
    geometry.setAttribute('position', new THREE.BufferAttribute(this.rest, 3)); geometry.setAttribute('normal', new THREE.BufferAttribute(this.normal, 3));
    return geometry;
  }

  // the pose's joints into the joint texture
  setPose(pose) {
    const s = this.skinner, D = this.data, J = this.J; s.transforms(pose);
    for (let j = 0; j < J; j++) {
      D[j * 4] = pose.Q[j * 4]; D[j * 4 + 1] = pose.Q[j * 4 + 1]; D[j * 4 + 2] = pose.Q[j * 4 + 2]; D[j * 4 + 3] = pose.Q[j * 4 + 3];
      const o = (J + j) * 4; D[o] = s.T[j * 3]; D[o + 1] = s.T[j * 3 + 1]; D[o + 2] = s.T[j * 3 + 2];
    }
    this.texture.needsUpdate = true;
  }

  // the posed skin into skinPos and skinNrm: once a frame, after setPose and the offsets, before the skin is drawn
  update(renderer) {
    if (!renderer.extensions.get('EXT_color_buffer_float')) throw new Error('GpuSkin: this video card cannot draw into float textures (EXT_color_buffer_float)');
    const was = renderer.getRenderTarget();
    renderer.setRenderTarget(this.posRT); renderer.render(this.place, this.camera);
    renderer.setRenderTarget(this.nrmRT); renderer.render(this.around, this.camera);
    renderer.setRenderTarget(was);
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
  //     joint, the vertices it leads that lie furthest out in 1000 directions (fewer leave millimetres on a flat sole);
  //   · where joints share the skin (bends, cloth between the legs) no such vertex is known beforehand — there, one
  //     vertex of every `cell` of space (1.5 cm) for each different sharing of the joints (shells lie one inside
  //     another, a foot in a shoe, with different joints), so the lowest of them is that near the lowest of all.
  lowest(pose, cell = 0.015) {
    if (!this.probe) {
      const { N, rest: P, skinJ, skinW } = this, dirs = [], n = 1000, pick = new Set(), cells = new Set();
      for (let k = 0; k < n; k++) { const y = 1 - 2 * (k + 0.5) / n, r = Math.sqrt(1 - y * y), a = k * Math.PI * (3 - Math.sqrt(5)); dirs.push([Math.cos(a) * r, y, Math.sin(a) * r]); }
      const lead = new Int32Array(N), share = new Float32Array(N);
      for (let i = 0; i < N; i++) { let b = 0; for (let k = 1; k < 4; k++) if (skinW[i * 4 + k] > skinW[i * 4 + b]) b = k; lead[i] = skinJ[i * 4 + b]; share[i] = skinW[i * 4 + b]; }
      const best = new Float64Array(this.J * n).fill(-Infinity), at = new Int32Array(this.J * n).fill(-1);
      for (let i = 0; i < N; i++) { const o = lead[i] * n, x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
        for (let k = 0; k < n; k++) { const d = dirs[k], v = x * d[0] + y * d[1] + z * d[2]; if (v > best[o + k]) { best[o + k] = v; at[o + k] = i; } }
        if (share[i] < 0.95) {
          const how = []; for (let k = 0; k < 4; k++) if (skinW[i * 4 + k] > 0.02) how.push(skinJ[i * 4 + k] + ':' + Math.round(skinW[i * 4 + k] * 5));
          const key = Math.floor(x / cell) + ',' + Math.floor(y / cell) + ',' + Math.floor(z / cell) + ' ' + how.sort().join(' ');
          if (!cells.has(key)) { cells.add(key); pick.add(i); }
        } }
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
