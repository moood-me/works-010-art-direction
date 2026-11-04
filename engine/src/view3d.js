// Drawing figures with three.js — the viewer's and the picture check's stage (three.js passed in: the repository's own
// copy, vendor/three). A soft studio: a warm key light with shadows and a cool rim, both fitted each frame to the box
// around every figure drawn (any number of them), a floor with a metre grid, the pelvis's paths drawn on it.
// The camera is framed by a box (fit): what is seen is the figures, whatever the page around them is.
import { paintFace } from './head/paint.js';
import { paintState } from './head/expressions.js';

export function makeStage(THREE, canvas, { background = '#cfc8bd', pixelRatio = 1 } = {}) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(pixelRatio);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const scene = new THREE.Scene(); scene.background = new THREE.Color(background);
  const camera = new THREE.PerspectiveCamera(26, 1, 0.05, 200);
  scene.add(new THREE.HemisphereLight('#fff4e6', '#5b544c', 1.05));
  const key = new THREE.DirectionalLight('#fff0dc', 2.1); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0004; key.shadow.normalBias = 0.02;
  const rim = new THREE.DirectionalLight('#cfe0ff', 1.2);
  scene.add(key, key.target, rim, rim.target);
  // the floor, with a line every metre drawn into its texture (lines as geometry get lost behind the camera in some
  // WebGL implementations; a texture is drawn the same everywhere)
  const tile = document.createElement('canvas'); tile.width = tile.height = 256;
  const g2 = tile.getContext('2d'); g2.fillStyle = '#c9c1b5'; g2.fillRect(0, 0, 256, 256);
  g2.fillStyle = '#a89e90'; g2.fillRect(0, 0, 256, 4); g2.fillRect(0, 0, 4, 256);
  const tex = new THREE.CanvasTexture(tile); tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.repeat.set(400, 400);
  tex.anisotropy = renderer.capabilities.getMaxAnisotropy(); tex.colorSpace = THREE.SRGBColorSpace;
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({ map: tex, roughness: 1 }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
  const paths = new THREE.Group(); scene.add(paths);
  const KEY = norm([-2.2, 3.6, 2.6]), RIM = norm([2.4, 2.2, -2.8]);
  const stage = {
    THREE, renderer, scene, camera, key, rim, floor, free: 1,
    // the lights fitted to a box (src/figure.js bounds(), or several joined: joinBounds): the same light on every
    // figure, the shadow covering them all
    light(b) {
      const c = b.center, r = Math.max(0.6, Math.hypot(...b.size) / 2) + 0.4, d = r + 3;
      key.position.set(c[0] + KEY[0] * d, c[1] + KEY[1] * d, c[2] + KEY[2] * d); key.target.position.set(...c);
      rim.position.set(c[0] + RIM[0] * d, c[1] + RIM[1] * d, c[2] + RIM[2] * d); rim.target.position.set(...c);
      Object.assign(key.shadow.camera, { left: -r, right: r, top: r, bottom: -r, near: Math.max(0.1, d - r * 1.5), far: d + r * 2 });
      key.shadow.camera.updateProjectionMatrix();
    },
    // the pelvis's paths on the floor, each with marks where one motion of a chain goes on into the next
    showPaths(list) {
      for (const o of [...paths.children]) { o.geometry.dispose(); o.material.dispose(); }
      paths.clear();
      for (const { points, marks = [] } of list) {
        if (points.length > 1) { const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points.map(p => new THREE.Vector3(p[0], 0.003, p[1]))), new THREE.LineBasicMaterial({ color: '#b4532a' })); paths.add(l); }
        for (const m of marks) { const d = new THREE.Mesh(new THREE.CircleGeometry(0.05, 24), new THREE.MeshBasicMaterial({ color: '#b4532a' })); d.rotation.x = -Math.PI / 2; d.position.set(m[0], 0.004, m[1]); paths.add(d); }
      }
    },
    // the picture's size; shift: how many pixels the view's centre moves right (to keep clear of a panel on the left)
    size(w, h, shift = 0) {
      renderer.setSize(w, h, false); camera.aspect = w / h; stage.free = Math.max(0.2, 1 - 2 * shift / w);
      if (shift) camera.setViewOffset(w, h, -shift, 0, w, h); else camera.clearViewOffset();
      camera.updateProjectionMatrix();
    },
    // a camera around a point: yaw 0 looks from +z (the figure's front, before it turns), pitch up, distance
    look(target, { yaw, pitch, dist }) {
      const cp = Math.cos(pitch);
      camera.position.set(target[0] + Math.sin(yaw) * cp * dist, target[1] + Math.sin(pitch) * dist, target[2] + Math.cos(yaw) * cp * dist);
      camera.lookAt(target[0], target[1], target[2]);
    },
    // the target and distance that show the whole box from (yaw, pitch), with a margin (a share of the picture)
    fit(b, { yaw, pitch, margin = 0.08 }) {
      // (what the panel's shift leaves free on the narrower side)
      const fy = Math.tan(camera.fov * Math.PI / 360) * (1 - 2 * margin), fx = fy * camera.aspect * stage.free;
      const f = [-Math.sin(yaw) * Math.cos(pitch), -Math.sin(pitch), -Math.cos(yaw) * Math.cos(pitch)];   // looking along
      const rgt = norm([f[2], 0, -f[0]]).map(v => -v), up = cross(rgt, f);
      let dist = 0.3;
      for (const x of [b.min[0], b.max[0]]) for (const y of [b.min[1], b.max[1]]) for (const z of [b.min[2], b.max[2]]) {
        const v = [x - b.center[0], y - b.center[1], z - b.center[2]], depth = dot(v, f);
        dist = Math.max(dist, Math.abs(dot(v, rgt)) / fx - depth, Math.abs(dot(v, up)) / fy - depth);
      }
      return { target: b.center.slice(), dist };
    },
    render() { renderer.render(scene, camera); },
  };
  return stage;
}

// one box around several
export function joinBounds(list) {
  const min = [0, 1, 2].map(c => Math.min(...list.map(b => b.min[c]))), max = [0, 1, 2].map(c => Math.max(...list.map(b => b.max[c])));
  return { min, max, center: min.map((v, c) => (v + max[c]) / 2), size: min.map((v, c) => max[c] - v) };
}

// a figure's meshes (every output: body, head, pieces, clothes, sweeps) as three.js meshes, updated from the figure
// each frame; the joints and the body's collision capsules drawn over them when asked. A head (src/head/head.js) brings
// its face's picture (painted each time its expressions ask the drawing something else: src/head/paint.js) and its
// light: toon (three soft tones, not tone-mapped) with an outline (the back of a shell a little outside, set back in
// depth so it shows only past the silhouette), and no cast shadows on the face when it asks.
export function figureView(THREE, figure, look) {
  const group = new THREE.Group(), parts = [], head = figure.body?.head, light = head?.light;
  const face = head ? facePicture(THREE, head) : null;
  for (const o of figure.outputs) {
    const g = new THREE.BufferGeometry(), m = o.mesh;
    g.setAttribute('position', new THREE.BufferAttribute(o.positions, 3));
    g.setAttribute('normal', new THREE.BufferAttribute(o.normals, 3));
    g.setIndex(new THREE.BufferAttribute(m.triangles, 1));
    if (m.uv) g.setAttribute('uv', new THREE.BufferAttribute(m.uv, 2));
    if (m.colors) g.setAttribute('color', new THREE.BufferAttribute(m.colors, 3));
    const color = o.name === 'body' || m.painted ? (head?.skin ?? look.skin) : (m.color || '#8a8f99'), map = m.uv && face ? face.texture : null;
    const toon = !!light?.toon, side = m.double ? THREE.DoubleSide : THREE.FrontSide;
    const mat = toon ? new THREE.MeshToonMaterial({ color: map || m.colors ? '#ffffff' : color, gradientMap: toonRamp(THREE, light.soft), map, vertexColors: !!m.colors, side })
      : new THREE.MeshStandardMaterial({ color: map ? '#ffffff' : color, roughness: look.roughness, map, vertexColors: !!m.colors, side });
    if (toon) mat.toneMapped = false;
    if (m.noShadow) g.setAttribute('noShadow', new THREE.BufferAttribute(m.noShadow, 1));
    if (m.paintMask) g.setAttribute('paintMask', new THREE.BufferAttribute(m.paintMask, 1));
    if (m.noShadow || m.paintMask) faceMaterial(THREE, mat, { shadows: !m.noShadow, skin: m.paintMask ? new THREE.Color(head.skin) : null });
    const mesh = new THREE.Mesh(g, mat);
    mesh.castShadow = m.shadows !== false; mesh.receiveShadow = m.shadows !== false; mesh.frustumCulled = false;
    group.add(mesh); parts.push({ o, g, mesh });
    const ink = o.name === 'body' ? (light?.outline ? { width: light.outline, color: light.outlineColor } : null) : light?.toon || light?.outline ? m.ink : null;
    if (ink) { const om = new THREE.Mesh(g, outlineMaterial(THREE, ink)); om.frustumCulled = false; group.add(om); parts.push({ g, mesh: om, ink: true }); }
  }
  const J = figure.rig.J;
  const dots = new THREE.InstancedMesh(new THREE.SphereGeometry(0.008, 10, 8), new THREE.MeshBasicMaterial({ color: '#e0592a', depthTest: false, transparent: true }), J);
  dots.renderOrder = 10; dots.visible = false; dots.frustumCulled = false; group.add(dots);
  const caps = new THREE.Group(); caps.visible = false; group.add(caps);
  const m = new THREE.Matrix4(), capMat = new THREE.MeshBasicMaterial({ color: '#2a7ab4', wireframe: true, transparent: true, opacity: 0.35 });
  let collider = null;
  return {
    group, dots, caps,
    update() {
      for (const p of parts) if (!p.ink) { p.g.attributes.position.needsUpdate = true; p.g.attributes.normal.needsUpdate = true; }
      if (face) face.paint(figure.ctx.expressions);
      const P = figure.pose.P;
      if (dots.visible) { for (let j = 0; j < J; j++) dots.setMatrixAt(j, m.makeTranslation(P[j * 3], P[j * 3 + 1], P[j * 3 + 2])); dots.instanceMatrix.needsUpdate = true; }
      if (caps.visible) {
        collider ??= figure.collider();
        collider.update(figure.pose);
        if (!caps.children.length) for (const c of collider.capsules) caps.add(new THREE.Mesh(capsuleGeometry(THREE, c), capMat));
        collider.capsules.forEach((c, n) => placeCapsule(THREE, caps.children[n], c));
      }
    },
    dispose() {
      for (const p of parts) { if (!p.ink) p.g.dispose(); p.mesh.material.dispose(); }
      if (face) face.texture.dispose();
      dots.geometry.dispose(); dots.material.dispose(); for (const c of caps.children) c.geometry.dispose(); capMat.dispose();
    },
  };
}

// the face's picture, drawn again when what the expressions ask of it changes
function facePicture(THREE, head) {
  const canvas = document.createElement('canvas'); canvas.width = canvas.height = 1024;
  const g = canvas.getContext('2d'), texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace; texture.anisotropy = 8;
  let last = null;
  const paint = weights => {
    const st = paintState(head, weights), key = JSON.stringify(st); if (key === last) return;
    last = key; paintFace(g, 1024, head.features, head.skin, st); texture.needsUpdate = true;
  };
  paint({});
  return { texture, paint };
}
// three tones, their edges eased over `soft` texels of 32, so an uneven mesh doesn't fray them (Г3's)
const RAMPS = new Map();
function toonRamp(THREE, soft = 3) {
  if (RAMPS.has(soft)) return RAMPS.get(soft);
  const W = 32, d = new Uint8Array(W * 4), sst = t => t <= 0 ? 0 : t >= 1 ? 1 : t * t * (3 - 2 * t), e = Math.max(0.01, soft);
  for (let k = 0; k < W; k++) { const x = (k + 0.5) / W * 3, t1 = sst((x - 1) * W / 3 / (2 * e) + 0.5), t2 = sst((x - 2) * W / 3 / (2 * e) + 0.5), v = 150 + 72 * t1 + 33 * t2; d.set([v, v, v, 255], k * 4); }
  const t = new THREE.DataTexture(d, W, 1); t.minFilter = t.magFilter = THREE.LinearFilter; t.needsUpdate = true;
  RAMPS.set(soft, t); return t;
}
function outlineMaterial(THREE, { width, color }) {
  const m = new THREE.MeshBasicMaterial({ color, side: THREE.BackSide, polygonOffset: true, polygonOffsetFactor: 3, polygonOffsetUnits: 30 });
  m.toneMapped = false;
  m.onBeforeCompile = sh => { sh.vertexShader = sh.vertexShader.replace('#include <begin_vertex>', `#include <begin_vertex>\n transformed += normalize( normal ) * ${width.toFixed(6)};`); };
  m.customProgramCacheKey = () => 'outline' + width;
  return m;
}
// a face's material: its picture shown as far as the mesh's paint mask says (the plain skin beyond it), and the key
// light's shadow left off where the mesh says (the face: no cast shadows on it)
function faceMaterial(THREE, mat, { shadows, skin }) {
  mat.onBeforeCompile = sh => {
    let vs = sh.vertexShader, fs = sh.fragmentShader;
    if (!shadows) {
      vs = 'attribute float noShadow;\nvarying float vNoShadow;\n' + vs.replace('#include <begin_vertex>', '#include <begin_vertex>\n vNoShadow = noShadow;');
      const chunk = THREE.ShaderChunk.lights_fragment_begin.replace('? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;',
        '? mix( getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ), 1.0, vNoShadow ) : 1.0;');
      if (chunk === THREE.ShaderChunk.lights_fragment_begin) throw new Error('three.js: the directional shadow line is not where it was (no face shadows)');
      fs = 'varying float vNoShadow;\n' + fs.replace('#include <lights_fragment_begin>', chunk);
    }
    if (skin) {
      sh.uniforms.faceSkin = { value: skin };
      vs = 'attribute float paintMask;\nvarying float vPaint;\n' + vs.replace('#include <begin_vertex>', '#include <begin_vertex>\n vPaint = paintMask;');
      const chunk = THREE.ShaderChunk.map_fragment.replace('diffuseColor *= sampledDiffuseColor;', 'diffuseColor *= mix( vec4( faceSkin, 1.0 ), sampledDiffuseColor, vPaint );');
      if (chunk === THREE.ShaderChunk.map_fragment) throw new Error('three.js: the map line is not where it was (the face\'s picture)');
      fs = 'uniform vec3 faceSkin;\nvarying float vPaint;\n' + fs.replace('#include <map_fragment>', chunk);
    }
    sh.vertexShader = vs; sh.fragmentShader = fs;
  };
  mat.customProgramCacheKey = () => `face:${shadows}:${!!skin}`;
}

// a tapered capsule along +y from 0 to its length, radius ra below and rb above
function capsuleGeometry(THREE, c) {
  const L = Math.hypot(c.b[0] - c.a[0], c.b[1] - c.a[1], c.b[2] - c.a[2]), pts = [], n = 6;
  for (let i = 0; i <= n; i++) { const t = -Math.PI / 2 + (i / n) * Math.PI / 2; pts.push(new THREE.Vector2(Math.cos(t) * c.ra, Math.sin(t) * c.ra)); }
  for (let i = 0; i <= n; i++) { const t = (i / n) * Math.PI / 2; pts.push(new THREE.Vector2(Math.cos(t) * c.rb, L + Math.sin(t) * c.rb)); }
  return new THREE.LatheGeometry(pts, 12);
}
function placeCapsule(THREE, mesh, c) {
  const d = new THREE.Vector3(c.b[0] - c.a[0], c.b[1] - c.a[1], c.b[2] - c.a[2]).normalize();
  mesh.position.set(...c.a); mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d);
}

const norm = a => { const l = Math.hypot(...a); return a.map(v => v / l); };
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
