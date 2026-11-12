// Вера in 3D, the Bilibin look: the character pack (tools/build.py) on the engine's skeleton, skinning and Kimodo
// retargeting, shown the way the style's rules say —
//   · flat paint, no light: every piece one colour of the drawing (vera.py's hex);
//   · the contour: one even ink line found on the screen from the 3D — where the piece under a pixel changes (the
//     figure against the paper, hair against skin, shawl against dress …) or where one form passes in front of
//     another part of the same piece (an arm over the dress); its weight on the page follows kit.py's rule;
//   · ornament that sits on the cloth: the shawl's roses are placed on its surface (each with its own frame on the
//     shell), its border of teeth runs along its cut edge, the hem's band round the skirt; thin inner lines (the
//     hair's strands, the skirt's folds) are painted in the cloth's own coordinates;
//   · the face is drawn each frame by the style's drawing code (face.js) at the head's place and turn, and laid
//     over the head's skin only (a hand in front of the face covers it).
//   view.html?pack=<url of vera.json>;   window.A.set({clip, t, pose, expr, face, cam, draw, …}) then A.render()
import * as THREE from 'three';
THREE.ColorManagement.enabled = false;
import { createEngine } from '../../../../engine/src/engine.js';
import { makeBody } from '../../../../engine/src/body.js';
import { Figure } from '../../../../engine/src/figure.js';
import { loadPack } from '../../../../engine/src/pack.js';
import { build, turnUnder } from '../../../../engine/src/retarget.js';
import { qAxisAngle, getV, qBetween, sub, add, scale, dot, len, normalize, qRot, cross as crossV } from '../../../../engine/src/math.js';
import { Head, drawFace, drawGlasses, mix as faceMix, INK } from './face.js';
import { lifeTrack, headFacing } from './life.js';

const q = new URLSearchParams(location.search);
const packUrl = new URL(q.get('pack') || 'data/vera.json', location.href);
const E = await createEngine({ root: new URL('../../../../engine/', import.meta.url) });
const { header: H, arrays: a } = await loadPack(packUrl.href);
const sk = E.skeleton;
const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: sk,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const spec = { skinning: { method: 'dqs', clavicleShare: 0.33, seam: null }, motion: { floor: 'lowest', corrections: {} } };
const fig = new Figure(body, spec, { position: [0, 0, 0], heading: 0 });
const K = H.K, FEET = H.FEET, ZOFF = H.ZOFF;
const Wd = (x, y, z) => [x * K, (FEET - y) * K, z * K + ZOFF];       // drawing units → world (rest)
const head = new Head(H.head);
const PIECES = H.pieces, PI = n => PIECES.indexOf(n), PF = n => PI(n).toFixed(1);

// ---------------------------------------------------------------- the stage
const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true, alpha: false });
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
const scene = new THREE.Scene();
const g = new THREE.BufferGeometry();
g.setAttribute('position', new THREE.BufferAttribute(fig.positions, 3));
g.setAttribute('normal', new THREE.BufferAttribute(fig.normals, 3));
for (const [k, n] of [['mat', 1], ['em', 1], ['ea', 1], ['hs', 1], ['dr', 3]]) g.setAttribute(k, new THREE.BufferAttribute(a[k], n));
g.setIndex(new THREE.BufferAttribute(a.triangles, 1));

// the shawl's roses: centre + radius, and each rose's frame on the cloth (drawing units, at rest)
const NR = H.roses.length, roseData = new Float32Array(NR * 3 * 4);
H.roses.forEach((r, i) => { roseData.set([r[0], r[1], r[2], r[9]], i * 12); roseData.set([r[3], r[4], r[5], 0], i * 12 + 4); roseData.set([r[6], r[7], r[8], 0], i * 12 + 8); });
const roseTex = new THREE.DataTexture(roseData, 3, NR, THREE.RGBAFormat, THREE.FloatType); roseTex.needsUpdate = true;

const hex = c => { const v = new THREE.Color(c); return `vec3(${v.r.toFixed(4)}, ${v.g.toFixed(4)}, ${v.b.toFixed(4)})`; };
const COL = { skin: '#efd6bb', dress: '#2f5a5a', legs: '#3a3030', shoe: '#2a2220', hair: '#2e2420', grey: '#8f8780', shawl: '#231d1b', rose: '#b8402f',
  leaf: '#5d6b3a', ring: '#7a2418', cover: '#8a3a2a', pages: '#f3ead6', gold: '#c99a3c', ink: INK, strand: '#6a5a52', coil: '#7a6a60', ground: '#b9b382', paper: '#e6dcbf' };
const U = {
  roses: { value: roseTex }, px: { value: 1 }, thin: { value: 1.5 }, clay: { value: 0 }, depth0: { value: 0 }, Vd: { value: new THREE.Vector3(0, 0, 1) },
  only: { value: -1 },
};
const VERT = `
  attribute float mat; attribute float em; attribute float ea; attribute float hs; attribute vec3 dr;
  varying float vMat; varying float vEm; varying float vEa; varying float vHs; varying vec3 vDr; varying float vZ; varying vec3 vN;
  void main() {
    vMat = mat; vEm = em; vEa = ea; vHs = hs; vDr = dr; vN = normalize(mat3(modelMatrix) * normal);
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    vZ = -mv.z;
    gl_Position = projectionMatrix * mv;
  }`;
// which piece a pixel belongs to (the contour separates pieces); cut edges are decided here, per pixel
const PIECE = `
  varying float vMat; varying float vEm; varying float vEa; varying float vHs; varying vec3 vDr; varying float vZ; varying vec3 vN;
  uniform float only;
  float piece() {
    float m = floor(vMat + 0.5);
    if (only >= 0.0 && abs(m - only) > 0.5 && !(only == ${PF('hair')} && m == ${PF('knot')})) discard;
    if (m == ${PF('dress')} && vEm < 0.0) m = ${PF('skin')};                                   // the sleeve's end
    // the round neckline (vera.py: from (−34, 120) through (0, 152) to (34, 120)), cut on the body at rest
    if (m == ${PF('dress')} && vHs < 5.0 && vEm > 50.0 && vDr.z > ${H.neckZ.toFixed(1)} && vDr.y < 150.0 - 26.0 * (vDr.x / 36.0) * (vDr.x / 36.0)) m = ${PF('skin')};
    if ((m == ${PF('hair')} || m == ${PF('shawl')}) && vEm < 0.0) discard;                     // the hairline, the shawl's edge
    return m;
  }`;
const idMat = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.DoubleSide, vertexShader: VERT,
  fragmentShader: `${PIECE} uniform float depth0;
    void main() { float m = piece(); gl_FragColor = vec4(m, vZ - depth0, 0.0, 1.0); }`,
});
const paint = new THREE.ShaderMaterial({
  uniforms: U, side: THREE.DoubleSide, vertexShader: VERT,
  fragmentShader: `${PIECE}
    uniform sampler2D roses; uniform float px; uniform float thin; uniform float clay; uniform vec3 Vd;
    // a thin line where c crosses 0, of an even weight on the screen (w pixels)
    float lineAt(float c, float w) { float d = abs(c) / max(fwidth(c), 1e-6); return 1.0 - smoothstep(w * 0.5 - 0.5, w * 0.5 + 0.5, d); }
    // the border of teeth along a cut edge: m units in from the edge, s along it; band wide
    vec3 teeth(vec3 base, vec3 ground, float m, float s, float band) {
      if (m > band) return mix(base, ${hex(COL.ink)}, lineAt(m - band, thin) * 0.0);
      float v = m / band, u = fract(s / band);
      vec3 c = ground;
      if (abs(u - 0.5) * 2.0 < 1.0 - (v - 0.125) / 0.75 && v > 0.125) c = ${hex(COL.rose)};
      return c;
    }
    void main() {
      float m = piece();
      vec3 c = ${hex(COL.skin)};
      if (m == ${PF('dress')}) {
        c = ${hex(COL.dress)};
        if (vHs > 5.0) {                                                   // the skirt
          // folds: a few thin lines running down from the hips
          float fl = 0.0;
          for (int i = 0; i < 7; i++) { float a0 = 10.0 - 2.75 + float(i) * 0.8976; float dd = vHs - a0; fl = max(fl, lineAt(dd, thin * 0.9)); }
          fl *= smoothstep(520.0, 600.0, vDr.y) * step(30.0, vEm);
          c = mix(c, ${hex(COL.ink)}, fl);
          if (vEm < 30.0) { c = teeth(c, ${hex(COL.dress)}, vEm - 3.0, vEa, 24.0); if (vEm < 3.0) c = ${hex(COL.dress)}; c = mix(c, ${hex(COL.ink)}, max(lineAt(vEm - 28.5, thin), lineAt(vEm - 3.0, thin))); }
        }
      } else if (m == ${PF('legs')}) c = ${hex(COL.legs)};
      else if (m == ${PF('shoe')}) c = ${hex(COL.shoe)};
      else if (m == ${PF('hair')}) {
        c = ${hex(COL.hair)};
        // strands combed back to the knot: thin lighter lines by the angle round the axis forehead → knot
        float st = 0.0;
        for (int i = -4; i <= 4; i++) st = max(st, lineAt(vHs - (float(i) * 0.34 + 0.05), thin * 0.8));
        st *= smoothstep(4.0, 14.0, vEm) * step(fwidth(vHs), 0.3);
        c = mix(c, ${hex(COL.strand)}, st);
        // the grey lock at her left temple: from the hairline down and back toward the ear
        if (vDr.x > 0.0 && vDr.z > -20.0) {
          float th = atan(vDr.x, max(vDr.z, 1.0));
          float t = (th - 0.3) / 0.9;
          if (t > 0.0 && t < 1.0) {
            float yc = -85.0 + 50.0 * pow(t, 1.6), hw = mix(6.5, 2.5, t);
            float d = abs(vDr.y - yc) - hw;
            if (d < 0.0) c = ${hex(COL.grey)};
            c = mix(c, ${hex(COL.ink)}, lineAt(d, thin));
          }
        }
      } else if (m == ${PF('knot')}) {
        c = ${hex(COL.hair)};
        c = mix(c, ${hex(COL.coil)}, max(lineAt(vHs - 12.0, thin * 0.9), lineAt(vHs - 22.0, thin * 0.9)) * step(vDr.z, ${(H.knot[2] - 6).toFixed(1)}));
      } else if (m == ${PF('shawl')}) {
        c = ${hex(COL.shawl)};
        for (int i = 0; i < ${NR}; i++) {
          vec4 rc = texelFetch(roses, ivec2(0, i), 0);
          vec3 d = vDr - rc.xyz; float r = rc.w;
          if (dot(d, d) > 5.3 * r * r) continue;
          vec2 p = vec2(dot(d, texelFetch(roses, ivec2(1, i), 0).xyz), dot(d, texelFetch(roses, ivec2(2, i), 0).xyz));
          for (int k = 0; k < 2; k++) {                                                   // two leaves
            float an = radians(20.0 + 120.0 * float(k)), ca = cos(an), sa = sin(an);
            vec2 ql = vec2(ca * p.x + sa * p.y, -sa * p.x + ca * p.y) - vec2(r + 6.0, 4.0);
            if (dot(ql / vec2(r * 0.8, r * 0.35), ql / vec2(r * 0.8, r * 0.35)) < 1.0) c = ${hex(COL.leaf)};
          }
          float rr = length(p);
          if (rr < r) {
            c = ${hex(COL.rose)};
            vec2 po = p - vec2(0.08, -0.05) * r; float ro = length(po), ang = atan(po.y, po.x) + 3.1416;
            for (int k = 1; k <= 3; k++) {                                                 // the petals: three broken rings
              float rk = r * 0.25 * float(k);
              float w = max(0.75, 0.55 * fwidth(ro));
              if (abs(ro - rk) < w && mod(ang + float(k), 3.3) < 2.2) c = ${hex(COL.ring)};
            }
          }
        }
        if (vEm < 13.0) { c = teeth(c, ${hex(COL.shawl)}, vEm - 1.0, vEa, 11.0); if (vEm < 1.0) c = ${hex(COL.shawl)}; }
      } else if (m == ${PF('cover')}) {
        c = ${hex(COL.cover)};
        // the gold band of rhombs across the folder's front (vera.folder: at y −60, 16 wide, from −50 to 50)
        if (vDr.z > 0.0 && abs(vDr.y + 60.0) < 8.0 && abs(vDr.x) < 50.0) {
          float u = fract((vDr.x + 50.0) / 16.667), v = (vDr.y + 60.0) / 8.0;
          if (abs(u - 0.5) / 0.38 + abs(v) / 0.62 < 1.0) c = ${hex(COL.gold)};
          if (length(vec2((u - 0.5) * 16.667, v * 8.0)) < 1.44) c = ${hex(COL.cover)};
          c = mix(c, ${hex(COL.ink)}, max(lineAt(abs(vDr.y + 60.0) - 8.0, thin), 0.0));
        }
      } else if (m == ${PF('pages')}) c = ${hex(COL.pages)};
      else if (m == ${PF('ground')}) c = vHs > 3.5 ? ${hex('#5d6b3a')} : ${hex(COL.ground)};
      else if (m == ${PF('flower')}) {
        float k = floor(vHs + 0.5);
        c = k < 0.5 ? ${hex('#b8402f')} : k < 1.5 ? ${hex('#d9b040')} : k < 2.5 ? ${hex('#f6edd5')} : k < 3.5 ? ${hex('#5d7a8c')} : ${hex('#5d6b3a')};
        if (k < 3.5 && length(vDr.xy) < 0.3) c = k < 1.5 ? ${hex('#f6edd5')} : ${hex('#d9b040')};
      }
      if (clay > 0.5) {                                                                   // the form alone, for the steps picture
        vec3 n = normalize(vN); if (!gl_FrontFacing) n = -n;
        float l = 0.35 + 0.65 * clamp(dot(n, normalize(Vd + vec3(-0.5, 0.6, 0.2))), 0.0, 1.0);
        c = mix(vec3(0.78, 0.76, 0.72), c, clay - 1.0 > 0.0 ? 0.6 : 0.0) * l;
      }
      gl_FragColor = vec4(c, 1.0);
    }`,
});
const mesh = new THREE.Mesh(g, paint); mesh.frustumCulled = false; scene.add(mesh);

// things that are not the body: the folder she holds, the ground and its flowers — the same paints and pieces
function deco(parts) {
  const P = [], T = [], A = { mat: [], em: [], ea: [], hs: [], dr: [] }; let n = 0;
  for (const p of parts) {
    for (let i = 0; i < p.v.length; i++) { P.push(...p.v[i]); A.mat.push(p.mat); A.em.push(100); A.ea.push(0); A.hs.push(p.hs ?? 0); A.dr.push(...(p.dr ? p.dr[i] : [0, 0, 0])); }
    for (const t of p.t) T.push(t[0] + n, t[1] + n, t[2] + n);
    n += p.v.length;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(P), 3));
  for (const k in A) geo.setAttribute(k, new THREE.BufferAttribute(new Float32Array(A[k]), k === 'dr' ? 3 : 1));
  geo.setIndex(T); geo.computeVertexNormals();
  const m = new THREE.Mesh(geo, paint); m.frustumCulled = false; return m;
}
// the folder: 140 × 200 × 12 units (vera.folder), cover on the faces and the spine, pages at the other three edges
const BK = [70 * K, 100 * K, 6 * K];
function quad(c, ex, ey, mat, drOf) {
  const v = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([s, t]) => [c[0] + ex[0] * s + ey[0] * t, c[1] + ex[1] * s + ey[1] * t, c[2] + ex[2] * s + ey[2] * t]);
  return { v, t: [[0, 1, 2], [0, 2, 3]], mat, dr: v.map(drOf) };
}
const bdr = p => [p[0] / K, -p[1] / K, p[2] / K];
const folder = deco([
  quad([0, 0, BK[2]], [BK[0], 0, 0], [0, BK[1], 0], PI('cover'), bdr), quad([0, 0, -BK[2]], [BK[0], 0, 0], [0, BK[1], 0], PI('cover'), bdr),
  quad([-BK[0], 0, 0], [0, 0, BK[2]], [0, BK[1], 0], PI('cover'), bdr),
  quad([BK[0] * 0.97, 0, 0], [0, 0, BK[2] * 0.8], [0, BK[1] * 0.97, 0], PI('pages'), bdr),
  quad([0, BK[1] * 0.97, 0], [BK[0] * 0.97, 0, 0], [0, 0, BK[2] * 0.8], PI('pages'), bdr), quad([0, -BK[1] * 0.97, 0], [BK[0] * 0.97, 0, 0], [0, 0, BK[2] * 0.8], PI('pages'), bdr),
]);
folder.matrixAutoUpdate = false; scene.add(folder);
// the ground: a flat field with small flowers (a Bilibin meadow), so a walk is seen to go somewhere
function rnd(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return (s >>> 0) / 4294967296; }; }
const groundParts = [{ v: [[-60, 0, -60], [60, 0, -60], [60, 0, 60], [-60, 0, 60]], t: [[0, 2, 1], [0, 3, 2]], mat: PI('ground') }];
{
  const R = rnd(11);
  for (let i = 0; i < 260; i++) {
    const x = (R() - 0.5) * 9, z = -3 + R() * 14, kind = Math.floor(R() * 4), r = 0.04 + R() * 0.02, v = [[x, 0.004, z]], t = [], dr = [[0, 0, 0]];
    for (let k = 0; k < 10; k++) { const an = k / 10 * 2 * Math.PI, rr = r * (k % 2 ? 0.72 : 1); v.push([x + Math.cos(an) * rr, 0.004, z + Math.sin(an) * rr]); dr.push([Math.cos(an), Math.sin(an), 0]); t.push([0, 1 + (k + 1) % 10, 1 + k]); }
    groundParts.push({ v, t, mat: PI('flower'), hs: kind, dr });
    // a tuft of grass beside it: three blades
    const gx = x + (R() - 0.5) * 0.3, gz = z + (R() - 0.5) * 0.3, bv = [], bt = [];
    for (let k = 0; k < 3; k++) { const o = (k - 1) * 0.035, hgt = 0.09 + R() * 0.06; bv.push([gx + o - 0.016, 0, gz], [gx + o + 0.016, 0, gz], [gx + o * 2.2, hgt, gz]); bt.push([k * 3, k * 3 + 1, k * 3 + 2]); }
    groundParts.push({ v: bv, t: bt, mat: PI('ground'), hs: 4 });
  }
}
const ground = deco(groundParts); ground.visible = false; scene.add(ground);

// the picture: flat paint (antialiased) + the piece/depth picture (twice the size) → contour, the drawn face over the head
const rtPaint = new THREE.WebGLRenderTarget(16, 16, { samples: 4 });
const rtId = new THREE.WebGLRenderTarget(16, 16, { type: THREE.HalfFloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
const faceCv = document.createElement('canvas'), glassCv = document.createElement('canvas');
const faceTex = new THREE.CanvasTexture(faceCv), glassTex = new THREE.CanvasTexture(glassCv);
for (const t of [faceTex, glassTex]) { t.premultiplyAlpha = true; t.minFilter = t.magFilter = THREE.LinearFilter; t.generateMipmaps = false; }
const post = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
  uniforms: { img: { value: rtPaint.texture }, ids: { value: rtId.texture }, face: { value: faceTex }, glass: { value: glassTex }, res: { value: new THREE.Vector2(1, 1) },
    r: { value: 1.4 }, kink: { value: 0.012 }, paper: { value: new THREE.Color(COL.paper) }, ink: { value: new THREE.Color(INK) }, lines: { value: 1 }, grain: { value: 1 } },
  depthTest: false, depthWrite: false,
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }',
  fragmentShader: `
    uniform sampler2D img; uniform sampler2D ids; uniform sampler2D face; uniform sampler2D glass; uniform vec2 res; uniform float r; uniform float kink;
    uniform vec3 paper; uniform vec3 ink; uniform float lines; uniform float grain;
    varying vec2 vUv;
    float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.0-2.0*f);
      return mix(mix(h(i), h(i+vec2(1,0)), f.x), mix(h(i+vec2(0,1)), h(i+vec2(1,1)), f.x), f.y); }
    void main() {
      vec4 f = texture2D(img, vUv);
      vec3 c = mix(paper, f.rgb, f.a);
      float line = 0.0, fm = 0.0, gm = 0.0;
      for (int s = 0; s < 4; s++) {
        vec2 uv = vUv + (vec2(float(s / 2), float(s - (s / 2) * 2)) - 0.5) * 0.5 / res;
        vec4 c0 = texture2D(ids, uv);
        float hit = 0.0;
        for (int k = 0; k < 8; k++) {
          float an = 6.2832 * float(k) / 8.0 + 0.3;
          vec2 o = vec2(cos(an), sin(an)) * r / res;
          vec4 a1 = texture2D(ids, uv + o), a2 = texture2D(ids, uv - o), b1 = texture2D(ids, uv + o * 0.5);
          if (a1.r != c0.r || b1.r != c0.r) hit = 1.0;
          else if (a2.r == c0.r && c0.r > 0.5 && c0.r < ${PF('ground')} && c0.r != ${PF('head')} && abs(a1.g + a2.g - 2.0 * c0.g) > kink) hit = 1.0;
        }
        line += hit * 0.25;
        if (c0.r == ${PF('head')}) fm += 0.25;
        if (!(c0.r == ${PF('skin')} || c0.r == ${PF('dress')} || c0.r == ${PF('cover')} || c0.r == ${PF('pages')})) gm += 0.25;
      }
      vec4 fc = texture2D(face, vUv);
      c = mix(c, fc.rgb / max(fc.a, 1e-3), fc.a * fm);
      c = mix(c, ink, line * lines);
      vec4 gc = texture2D(glass, vUv);
      c = mix(c, gc.rgb / max(gc.a, 1e-3), gc.a * gm);
      // paper: a faint tooth and mottling, as the drawing's sheets have
      vec2 p = gl_FragCoord.xy;
      c *= 1.0 + grain * ((vn(p * 0.035) - 0.5) * 0.045 + (h(p) - 0.5) * 0.03);
      gl_FragColor = vec4(c, 1.0);
    }`,
}));
const postScene = new THREE.Scene(); postScene.add(post);
const postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.01, 100);
const persp = new THREE.PerspectiveCamera(24, 1, 0.05, 200);
let camera = ortho;

// ---------------------------------------------------------------- poses
const J = sk.J, I = sk.index;
// the front of the clothes (rest) at a height and side: where the folder lies against the chest
function chestZ(y, x) {
  let zf = -1; const rp = a.positions, [b0, b1] = H.ranges.body, [s0, s1] = H.ranges.shawl;
  for (let i = b0; i < s1; i++) { if (i >= b1 && i < s0) continue; const yy = rp[i * 3 + 1], xx = rp[i * 3];
    if (Math.abs(yy - y) < 0.02 && Math.abs(xx - x) < 0.03) zf = Math.max(zf, rp[i * 3 + 2]); }
  return zf;
}
// two bones (upper arm, forearm) turned so the wrist reaches T, the elbow toward the pole (Р7's)
function reach(pose, s, T, pole) {
  const jS = I[s + 'Arm'], jE = I[s + 'ForeArm'], jW = I[s + 'Hand'];
  const S0 = getV(pose.P, jS), E0 = getV(pose.P, jE), W0 = getV(pose.P, jW);
  const l1 = len(sub(E0, S0)), l2 = len(sub(W0, E0));
  let dv = sub(T, S0); let d = len(dv); d = Math.min(d, (l1 + l2) * 0.999); const ax = normalize(dv);
  const cosA = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), sinA = Math.sqrt(Math.max(0, 1 - cosA * cosA));
  const pp = normalize(sub(pole, scale(ax, dot(pole, ax))));
  const E1 = add(S0, add(scale(ax, l1 * cosA), scale(pp, l1 * sinA)));
  turnUnder(pose, sk, jS, qBetween(normalize(sub(E0, S0)), normalize(sub(E1, S0))));
  build(pose, body, getV(pose.P, I.Hips));
  const E2 = getV(pose.P, jE), W2 = getV(pose.P, jW);
  turnUnder(pose, sk, jE, qBetween(normalize(sub(W2, E2)), normalize(sub(T, E2))));
  build(pose, body, getV(pose.P, I.Hips));
}
// standing as drawn: the folder held to the chest with both forearms; or the arms hanging (hold: false)
function standPose(o = {}) {
  const pose = fig.restPose();
  const off = getV(pose.P, I.Hips); const r0 = [body.joints[I.Hips * 3], body.joints[I.Hips * 3 + 1], body.joints[I.Hips * 3 + 2]];
  const sh = sub(off, r0);                                        // rest → placed
  build(pose, body, getV(pose.P, I.Hips));
  const at = (x, y, z) => add(Wd(x, y, 0).map((v, i) => i === 2 ? z : v), sh);
  for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
    const Sh = getV(pose.P, I[s + 'Arm']), Wr = getV(pose.P, I[s + 'Hand']), El = getV(pose.P, I[s + 'ForeArm']);
    const L = len(sub(El, Sh)) + len(sub(Wr, El));
    reach(pose, s, [Sh[0] + sg * (o.out ?? 0.06), Sh[1] - L * 0.985, Sh[2] + (o.fwd ?? 0.03)], [sg * 0.2, 0, -1]);
    turnUnder(pose, sk, I[s + 'ForeArm'], qAxisAngle(normalize(sub(getV(pose.P, I[s + 'Hand']), getV(pose.P, I[s + 'ForeArm']))), sg * (o.twist ?? 0.9)));
  }
  build(pose, body, getV(pose.P, I.Hips));
  if (o.hold !== false) {
    const fa = o.folderAt ?? [6, 372];
    const zb = chestZ(Wd(0, fa[1], 0)[1], 0) + (o.folderOut ?? 0.02);          // the folder's middle plane
    // her left forearm lies across under the folder's middle, the hand on its far lower corner; her right hand on its front
    const L = o.left ?? [-6, 442], R = o.right ?? [-22, 364];
    reach(pose, 'Left', at(L[0], L[1], zb + (o.handOut ?? 0.03)), o.poleL ?? [0.9, -0.5, -0.1]);
    reach(pose, 'Right', at(R[0], R[1], zb + (o.handOut ?? 0.03) + 0.006), o.poleR ?? [-0.9, -0.5, -0.1]);
    // each hand laid flat on the folder: the fingers along it, the palm to the body
    for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
      const P = pose.P, wv = getV(P, I[s + 'Hand']), mid = getV(P, I[s + 'HandMiddle1']), ix = getV(P, I[s + 'HandIndex1']), pk = getV(P, I[s + 'HandPinky1']);
      const f = normalize(sub(mid, wv)), ft = normalize(o['fingers' + s] ?? (s === 'Left' ? [-1, 0.12, 0.1] : [1, 0.1, 0.05]));
      const q1 = qBetween(f, ft);
      let n = normalize(crossV(sub(ix, wv), sub(pk, wv))); n = scale(n, sg * (o.palmSign ?? 1));       // out of the hand's back
      const n1 = qRot(q1, n), want = [0, 0, 1];
      const pr = v => normalize(sub(v, scale(ft, dot(v, ft))));
      const q2 = qBetween(pr(n1), pr(want));
      turnUnder(pose, sk, I[s + 'Hand'], q1); turnUnder(pose, sk, I[s + 'Hand'], q2);
    }
  }
  const curl = o.curl ?? 0.3;
  for (const s of ['Left', 'Right']) {
    const P0 = body.joints, jp = n => [P0[I[s + n] * 3], P0[I[s + n] * 3 + 1], P0[I[s + n] * 3 + 2]];
    const ix = jp('HandIndex1'), pk = jp('HandPinky1');
    const ax = [pk[0] - ix[0], pk[1] - ix[1], pk[2] - ix[2]];
    const c = o.hold !== false ? (o.grip ?? 0.25) : curl;
    for (const f of ['Index', 'Middle', 'Ring', 'Pinky']) for (const k of [1, 2, 3])
      turnUnder(pose, sk, I[s + 'Hand' + f + k], qAxisAngle(ax, (s === 'Left' ? 1 : -1) * c * (k === 1 ? 0.6 : 1)));
  }
  if (o.head) {
    const hd = o.head;
    if (hd.yaw) { turnUnder(pose, sk, I.Neck1, qAxisAngle([0, 1, 0], hd.yaw * 0.35)); turnUnder(pose, sk, I.Head, qAxisAngle([0, 1, 0], hd.yaw * 0.65)); }
    if (hd.pitch) turnUnder(pose, sk, I.Head, qAxisAngle(qRot(qAxisAngle([0, 1, 0], hd.yaw || 0), [1, 0, 0]), hd.pitch));
    if (hd.roll) turnUnder(pose, sk, I.Head, qAxisAngle(qRot(qAxisAngle([0, 1, 0], hd.yaw || 0), [0, 0, 1]), hd.roll));
  }
  build(pose, body, getV(pose.P, I.Hips));
  return pose;
}

const S = { clip: null, clipIds: null, t: 0, pose: 'stand', poseOpts: {}, face: faceMix({ calm: 1 }), folder: true, faceOn: true, life: null,
  cam: { mode: 'ortho', yaw: 0, pitch: 0, cx: 0, cy: 0.9, h: 1.9, dist: 6, follow: false }, draw: null, lineK: 1 };
let clip = null, folderLocal = null;
const M4 = m => new THREE.Matrix4().set(m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11], 0, 0, 0, 1);
// the skirt is not cloth. After skinning: (1) every skirt point is moved outward (away from the body's axis) until
// no leg or foot lies beyond it — legs are rows of balls from hip to knee to ankle to toe; (2) each ring of the
// skirt is pulled taut round what it holds (its convex outline), so the cloth spans from leg to leg as a skirt
// does and doesn't wrap each leg like trousers.
const SK = H.ranges.skirt, [SROWS, SCOLS] = H.skirt;
function pushSkirt() {
  const P = fig.pose.P, X = fig.positions;
  const hc = getV(P, I.Hips), balls = [];
  for (const s of ['Left', 'Right']) {
    const a0 = getV(P, I[s + 'Leg']), k = getV(P, I[s + 'Shin']), f = getV(P, I[s + 'Foot']), t = getV(P, I[s + 'ToeBase']), e = getV(P, I[s + 'ToeEnd'] ?? I[s + 'ToeBase']);
    for (const [A, B, r0, r1, n, from] of [[a0, k, 0.074, 0.06, 9, 2], [k, f, 0.058, 0.046, 9, 0], [f, t, 0.05, 0.045, 4, 0], [t, e, 0.045, 0.04, 2, 1]])
      for (let i = from; i <= n; i++) { const u = i / n; balls.push([A[0] + (B[0] - A[0]) * u, A[1] + (B[1] - A[1]) * u, A[2] + (B[2] - A[2]) * u, r0 + (r1 - r0) * u]); }
  }
  for (let i = H.ranges.shoes[0]; i < H.ranges.shoes[1]; i += 3) balls.push([X[i * 3], X[i * 3 + 1], X[i * 3 + 2], 0.022]);     // the shoes themselves
  for (let i = SK[0]; i < SK[1]; i++) {
    const px = X[i * 3], py = X[i * 3 + 1], pz = X[i * 3 + 2];
    let dx = px - hc[0], dz = pz - hc[2]; const dl = Math.hypot(dx, dz) || 1; dx /= dl; dz /= dl;
    let sMax = 0;
    for (const [bx, by, bz, r] of balls) {
      const ex = bx - px, ey = by - py, ez = bz - pz, al = ex * dx + ez * dz;
      const l2 = ex * ex + ey * ey + ez * ez - al * al;
      if (l2 >= r * r) continue;
      const out = al + Math.sqrt(r * r - l2) + 0.004;
      if (out > sMax) sMax = out;
    }
    if (sMax > 0) { X[i * 3] = px + dx * sMax; X[i * 3 + 2] = pz + dz * sMax; }
  }
  const hull = [], idx = new Array(SCOLS - 1);
  for (let r = 3; r < SROWS; r++) {
    const o = SK[0] + r * SCOLS, w = Math.min(1, (r - 3) / 6);
    let cx = 0, cz = 0;
    for (let c = 0; c < SCOLS - 1; c++) { idx[c] = c; cx += X[(o + c) * 3]; cz += X[(o + c) * 3 + 2]; }
    cx /= SCOLS - 1; cz /= SCOLS - 1;
    idx.sort((a, b) => X[(o + a) * 3] - X[(o + b) * 3] || X[(o + a) * 3 + 2] - X[(o + b) * 3 + 2]);
    const crs = (a, b, c) => (X[(o + b) * 3] - X[(o + a) * 3]) * (X[(o + c) * 3 + 2] - X[(o + a) * 3 + 2]) - (X[(o + b) * 3 + 2] - X[(o + a) * 3 + 2]) * (X[(o + c) * 3] - X[(o + a) * 3]);
    hull.length = 0;
    for (const c of idx) { while (hull.length >= 2 && crs(hull[hull.length - 2], hull[hull.length - 1], c) <= 0) hull.pop(); hull.push(c); }
    const lo = hull.length + 1;
    for (let k = idx.length - 2; k >= 0; k--) { const c = idx[k]; while (hull.length >= lo && crs(hull[hull.length - 2], hull[hull.length - 1], c) <= 0) hull.pop(); hull.push(c); }
    hull.pop();
    const hp = hull.map(c => [X[(o + c) * 3], X[(o + c) * 3 + 2]]);
    for (let c = 0; c < SCOLS; c++) {
      const i = o + c, vx = X[i * 3] - cx, vz = X[i * 3 + 2] - cz; let best = 1;
      for (let k = 0; k < hp.length; k++) {
        const A = hp[k], B = hp[(k + 1) % hp.length], ex = B[0] - A[0], ez = B[1] - A[1];
        const den = vx * ez - vz * ex; if (Math.abs(den) < 1e-12) continue;
        const t = ((A[0] - cx) * ez - (A[1] - cz) * ex) / den, u = ((A[0] - cx) * vz - (A[1] - cz) * vx) / den;
        if (t > 0 && u >= -1e-6 && u <= 1 + 1e-6 && t > best) best = t;
      }
      if (best > 1) { const k = 1 + (best - 1) * w; X[i * 3] = cx + vx * k; X[i * 3 + 2] = cz + vz * k; }
    }
  }
}
let headMat = null;
function frame() {
  if (S.clip) fig.frame(clip, S.t);
  else {
    const pose = S.pose === 'rest' ? fig.restPose() : standPose(S.poseOpts);
    fig.skinner.skin(pose, fig.positions); fig.pose = pose;
  }
  pushSkirt();
  if (S.life) S.face = S.life.at(S.clip ? S.t / 30 : S.t);
  g.attributes.position.needsUpdate = true;
  if (U.clay.value > 0.5) { g.computeVertexNormals(); }
  headMat = M4(fig.skinner.matrix(fig.pose, I.Head));
  // the folder: its place in the left hand's frame is set once from the standing pose (held against the chest)
  if (!folderLocal) {
    const sp = standPose(S.poseOpts), M0 = M4(fig.skinner.matrix(sp, I.LeftHand));
    const o = S.poseOpts, fa = o.folderAt ?? [6, 372];
    const c = Wd(fa[0], fa[1], 0); const hipRest = [body.joints[I.Hips * 3], body.joints[I.Hips * 3 + 2]], hp = getV(sp.P, I.Hips);
    const W0 = new THREE.Matrix4().compose(new THREE.Vector3(c[0] + hp[0] - hipRest[0], c[1] + hp[1] - body.joints[I.Hips * 3 + 1], chestZ(c[1], 0) + (o.folderOut ?? 0.02) + hp[2] - hipRest[1]),
      new THREE.Quaternion().setFromEuler(new THREE.Euler(o.folderTilt ?? 0.1, 0, o.folderRoll ?? 0.14)), new THREE.Vector3(1, 1, 1));
    folderLocal = new THREE.Matrix4().copy(M0).invert().multiply(W0);
  }
  folder.matrix.copy(M4(fig.skinner.matrix(fig.pose, I.LeftHand))).multiply(folderLocal); folder.matrixWorldNeedsUpdate = true;
  folder.visible = S.folder;
}

// the life of the face over the clip (blinks, gaze leading the head, speech, expressions): one track per clip
function makeLife(opts) {
  const seconds = opts.seconds ?? (clip ? clip.frames / 30 : 12);
  let hd = () => ({ yaw: 0, pitch: 0 });
  if (clip) {
    const yaws = [], pitches = [], smp = fig.sample;
    for (let f = 0; f <= clip.frames; f++) {
      const pose = fig.retarget.pose(clip.sample(Math.min(f, clip.frames - 1), smp));
      const hf = headFacing(pose, I.Head, qRot); yaws.push(hf.yaw); pitches.push(hf.pitch);
    }
    hd = t => { const x = Math.max(0, Math.min(clip.frames, t * 30)), i = Math.floor(x), j = Math.min(clip.frames, i + 1), f = x - i;
      return { yaw: yaws[i] + (yaws[j] - yaws[i]) * f, pitch: pitches[i] + (pitches[j] - pitches[i]) * f }; };
  }
  return lifeTrack(hd, { seconds, seed: opts.seed ?? 7, talk: opts.talk, expr: opts.expr, talkFrom: opts.talkFrom, talkTo: opts.talkTo });
}

// the drawn face: where the head is on the picture, how it is turned, and the style's drawing of it there
const v4 = new THREE.Vector4();
function drawFaceLayer(w, h, s) {
  for (const [cv, tx] of [[faceCv, faceTex], [glassCv, glassTex]]) { if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; tx.dispose(); } }
  const gf = faceCv.getContext('2d'), gg = glassCv.getContext('2d');
  gf.setTransform(1, 0, 0, 1, 0, 0); gf.clearRect(0, 0, w, h); gg.setTransform(1, 0, 0, 1, 0, 0); gg.clearRect(0, 0, w, h);
  faceTex.needsUpdate = true; glassTex.needsUpdate = true;
  if (!S.faceOn) return;
  const PV = new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse).multiply(headMat);
  const proj = (x, y, z) => { const p = Wd(x, y, z); v4.set(p[0], p[1], p[2], 1).applyMatrix4(PV); return [(v4.x / v4.w * 0.5 + 0.5) * w, (0.5 - v4.y / v4.w * 0.5) * h]; };
  const O = proj(0, 0, 0), dn = proj(0, 50, 0), up = proj(0, -50, 0);
  const rho = Math.atan2(-(dn[0] - up[0]), dn[1] - up[1]), cr = Math.cos(rho), sr = Math.sin(rho);
  // the head's turn against the picture: its forward against the direction to the eye, and the sheet's x
  const e = camera.matrixWorld.elements, hm = headMat.elements;
  const fwd = new THREE.Vector3(hm[8], hm[9], hm[10]).normalize(), right = new THREE.Vector3(e[0], e[1], e[2]), upv = new THREE.Vector3(e[4], e[5], e[6]);
  const hp = new THREE.Vector3(...Wd(0, 0, 0)).applyMatrix4(headMat);
  const toCam = camera.isPerspectiveCamera ? new THREE.Vector3().setFromMatrixPosition(camera.matrixWorld).sub(hp).normalize() : new THREE.Vector3(e[8], e[9], e[10]);
  const xs = right.clone().multiplyScalar(cr).addScaledVector(upv, -sr);
  let yaw = Math.atan2(-fwd.dot(xs), fwd.dot(toCam)) * 180 / Math.PI;
  const mir = yaw < 0 ? -1 : 1; yaw = Math.abs(yaw);
  const sheet = {
    yaw, lw: Math.pow(s, 0.25) / s * S.lineK,
    pt: (x, y, z) => { const p = proj(x * mir, y, z), dx = (p[0] - O[0]) / s, dy = (p[1] - O[1]) / s; return [(dx * cr + dy * sr) * mir, -dx * sr + dy * cr]; },
  };
  const f = { ...S.face, lookX: (S.face.lookX || 0) * mir };
  for (const [gx, fn] of [[gf, () => drawFace(gf, head, sheet, f)], [gg, () => drawGlasses(gg, head, sheet)]]) {
    gx.setTransform(cr * s * mir, sr * s * mir, -sr * s, cr * s, O[0], O[1]);
    fn();
  }
}

window.A = {
  H, body, fig, sk, standPose, S, U, post,
  async set(o) {
    if (o.clip !== undefined) {
      const ids = o.clip ? (Array.isArray(o.clip) ? o.clip : [o.clip]) : null;
      if (JSON.stringify(ids) !== JSON.stringify(S.clipIds)) { clip = ids ? await E.clip(ids) : null; S.clipIds = ids; }
      S.clip = !!ids;
    }
    for (const k of ['t', 'pose', 'draw', 'folder', 'faceOn', 'lineK']) if (o[k] !== undefined) S[k] = o[k];
    if (o.poseOpts !== undefined) { S.poseOpts = o.poseOpts; folderLocal = null; }
    if (o.face !== undefined) S.face = { ...faceMix({ calm: 1 }), ...o.face };
    if (o.live !== undefined) S.life = o.live ? makeLife(o.live) : null;
    if (o.expr !== undefined) S.face = faceMix(typeof o.expr === 'string' ? { [o.expr]: 1 } : o.expr);
    if (o.cam) Object.assign(S.cam, o.cam);
    if (o.floor3d !== undefined) ground.visible = o.floor3d;
    if (o.clay !== undefined) U.clay.value = o.clay;
    if (o.only !== undefined) U.only.value = o.only === null ? -1 : PI(o.only);
    if (o.parts !== undefined) {
      const tr = a.triangles, keep = [];
      const inR = v => !o.parts || o.parts.some(n => v >= H.ranges[n][0] && v < H.ranges[n][1]);
      for (let i = 0; i < tr.length; i += 3) if (inR(tr[i])) keep.push(tr[i], tr[i + 1], tr[i + 2]);
      g.setIndex(new THREE.BufferAttribute(new Uint32Array(keep), 1));
    }
    if (o.lines !== undefined) post.material.uniforms.lines.value = o.lines;
    if (o.paper !== undefined) post.material.uniforms.paper.value.set(o.paper);
    frame();
  },
  frames: () => clip ? clip.frames : 0,
  hips: () => getV(fig.pose.P, I.Hips),
  render() {
    const w = canvas.clientWidth, h = canvas.clientHeight; renderer.setSize(w, h, false);
    rtPaint.setSize(w, h); rtId.setSize(w * 2, h * 2); post.material.uniforms.res.value.set(w, h);
    const c = S.cam;
    let dir, tg, s;                       // s: pixels per drawing unit at the figure
    if (S.draw) {
      // the drawing's own camera: the head's origin (eye line, middle) at pixel (cx, cy), s px per unit, turned by yaw
      const D = S.draw, yaw = -D.yaw * Math.PI / 180;
      dir = [Math.sin(yaw), 0, Math.cos(yaw)];
      const right = [Math.cos(yaw), 0, -Math.sin(yaw)];
      const o0 = Wd(0, 0, 0), hj = I.Hips * 3; o0[0] -= body.joints[hj]; o0[2] -= body.joints[hj + 2]; o0[1] -= body.measures.floor;
      const dx = (w / 2 - D.cx) / D.s, dy = (h / 2 - D.cy) / D.s;
      tg = [o0[0] + right[0] * dx * K, o0[1] - dy * K, o0[2] + right[2] * dx * K];
      camera = ortho; const hh = h / D.s * K / 2, ww = w / D.s * K / 2;
      Object.assign(ortho, { left: -ww, right: ww, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
      ortho.position.set(tg[0] + dir[0] * 20, tg[1], tg[2] + dir[2] * 20);
      s = D.s; U.depth0.value = 20;
    } else {
      const cp = Math.cos(c.pitch);
      tg = c.target || [c.cx, c.cy, 0];
      if (c.follow && fig.pose) { const P = fig.pose.P; tg = [P[I.Hips * 3] + (c.dx || 0), c.cy, P[I.Hips * 3 + 2] + (c.dz || 0)]; }
      dir = [Math.sin(c.yaw) * cp, Math.sin(c.pitch), Math.cos(c.yaw) * cp];
      if (c.mode === 'ortho') {
        camera = ortho; const hh = c.h / 2, ww = hh * w / h;
        Object.assign(ortho, { left: -ww, right: ww, top: hh, bottom: -hh }); ortho.updateProjectionMatrix();
        ortho.position.set(tg[0] + dir[0] * 20, tg[1] + dir[1] * 20, tg[2] + dir[2] * 20);
        s = h / c.h * K; U.depth0.value = 20;
      } else {
        camera = persp; persp.aspect = w / h; persp.fov = c.fov || 24; persp.updateProjectionMatrix();
        persp.position.set(tg[0] + dir[0] * c.dist, tg[1] + dir[1] * c.dist, tg[2] + dir[2] * c.dist);
        s = K * (h / 2) / Math.tan(persp.fov * Math.PI / 360) / c.dist; U.depth0.value = c.dist;
      }
    }
    camera.lookAt(tg[0], tg[1], tg[2]); camera.updateMatrixWorld();
    const Vd = new THREE.Vector3(); camera.getWorldDirection(Vd); U.Vd.value.copy(Vd).negate();
    // kit.py's rule for the line: one weight on the page whatever the scale, a little heavier when the figure is large
    const lw = 3.2 * Math.pow(s, 0.25) * S.lineK;
    U.px.value = s; U.thin.value = Math.max(1.0, 1.7 * Math.pow(s, 0.25) * S.lineK);
    post.material.uniforms.r.value = lw / 2;
    drawFaceLayer(w, h, s);
    mesh.material = folder.material = ground.material = idMat;
    renderer.setRenderTarget(rtId); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera);
    mesh.material = folder.material = ground.material = paint;
    renderer.setRenderTarget(rtPaint); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, camera);
    renderer.setRenderTarget(null); renderer.render(postScene, postCam);
  },
};
await window.A.set({});
window.A.render();
window.__ready = true;
