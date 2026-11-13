// Several characters in one scene, skinned the old way (on the processor: engine/src/figure.js — skinning, the floor,
// normals — and the whole skin sent to the video card each frame) or the new way (engine-gpu: in the vertex shader).
// Drawn as the Р pages draw: a shadow map from the key light, the body with a two-tone light, an outline (a hull).
//   index.html?n=6&way=gpu|cpu&pack=<a character pack's json, from the repository's root>&clip=walk
// The numbers on the page: frames a second, the longest gap between frames over the last seconds, and the
// processor's milliseconds a frame for the characters. window.B.measure(seconds) gives them to a script.
import * as THREE from 'three';
import { createEngine } from '../../engine/src/engine.js';
import { makeBody } from '../../engine/src/body.js';
import { Figure } from '../../engine/src/figure.js';
import { loadPack } from '../../engine/src/pack.js';
import { GpuSkin } from '../src/gpuskin.js';

const q = new URLSearchParams(location.search);
const n = Number(q.get('n') || 6), way = q.get('way') || 'gpu', clipId = q.get('clip') || 'walk';
const root = new URL('../../', import.meta.url);
const E = await createEngine({ root: new URL('engine/', root) });
const { header: H, arrays: a } = await loadPack(new URL(q.get('pack') || 'to3d/r45-s15-anya/data/anya.json', root).href);
const body = makeBody({
  id: H.id, label: H.label, source: H.source, topology: H.id, skeleton: E.skeleton,
  positions: Float32Array.from(a.positions), triangles: a.triangles, skin: { joints: a.skinJoints, weights: a.skinWeights },
  parts: { names: [], weights: new Uint8Array(0) }, joints: Float64Array.from(a.joints), frames: Float64Array.from(a.frames),
});
const clip = await E.clip([clipId]);
const spec = { skinning: { method: H.skinning || 'cor', clavicleShare: 0, seam: null }, motion: { floor: 'lowest', corrections: {} } };

const canvas = document.getElementById('cv');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(1); renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene(); scene.background = new THREE.Color('#cfc8bd');
const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 200);
const SM = 2048, shadowRT = new THREE.WebGLRenderTarget(SM, SM, { depthTexture: new THREE.DepthTexture(SM, SM, THREE.UnsignedIntType) });
const shadowCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.5, 40);
const L = new THREE.Vector3(-0.5, 0.75, 0.45).normalize();
const shared = { L: { value: L }, smap: { value: shadowRT.depthTexture }, SMx: { value: new THREE.Matrix4() }, width: { value: 0.004 } };

const cols = Math.ceil(Math.sqrt(n)), gap = 1.3;
const chars = [];
for (let k = 0; k < n; k++) {
  const fig = new Figure(body, spec, { position: [(k % cols - (cols - 1) / 2) * gap, 0, (Math.floor(k / cols) - (Math.ceil(n / cols) - 1) / 2) * gap], heading: 0 });
  const gs = way === 'gpu' ? new GpuSkin(THREE, fig.skinner) : null;
  const g = new THREE.BufferGeometry();
  if (gs) gs.attributes(g);
  else { g.setAttribute('position', new THREE.BufferAttribute(fig.positions, 3)); g.setAttribute('normal', new THREE.BufferAttribute(fig.normals, 3)); }
  if (a.col) g.setAttribute('col', new THREE.BufferAttribute(a.col, 3, true));
  g.setIndex(new THREE.BufferAttribute(a.triangles, 1));
  const U = { ...shared, ...(gs ? gs.uniforms : {}) };
  const posed = gs ? `${gs.glsl}\n void posed(out vec3 P, out vec3 N) { skinVertex(P, N); }` : `void posed(out vec3 P, out vec3 N) { P = position; N = normal; }`;
  const toon = new THREE.ShaderMaterial({ uniforms: U, side: THREE.DoubleSide,
    vertexShader: `${a.col ? 'attribute vec3 col;' : 'const vec3 col = vec3(0.8, 0.74, 0.68);'} uniform mat4 SMx; varying vec3 vN; varying vec3 vCol; varying vec4 vS; ${posed}
      void main() { vec3 P, N; posed(P, N); vN = N; vCol = col; vS = SMx * vec4(P + N * 0.012, 1.0); gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0); }`,
    fragmentShader: `uniform vec3 L; uniform sampler2D smap; varying vec3 vN; varying vec3 vCol; varying vec4 vS;
      void main() { vec3 s = vS.xyz / vS.w; float sh = texture2D(smap, s.xy).r < s.z - 0.0015 ? 1.0 : 0.0;
        float d = dot(normalize(vN) * (gl_FrontFacing ? 1.0 : -1.0), L), w = fwidth(d) * 0.7 + 1e-4, lit = smoothstep(0.1 - w, 0.1 + w, d) * (1.0 - sh);
        gl_FragColor = vec4(vCol * mix(0.45, 1.0, lit), 1.0); }` });
  const hull = new THREE.ShaderMaterial({ uniforms: U, side: THREE.BackSide,
    vertexShader: `uniform float width; ${posed}
      void main() { vec3 P, N; posed(P, N); gl_Position = projectionMatrix * viewMatrix * vec4(P + N * width, 1.0); gl_Position.z += 0.0004 * gl_Position.w; }`,
    fragmentShader: `void main() { gl_FragColor = vec4(0.1, 0.09, 0.1, 1.0); }` });
  const depth = new THREE.ShaderMaterial({ uniforms: U, side: THREE.DoubleSide,
    vertexShader: `${posed} void main() { vec3 P, N; posed(P, N); gl_Position = projectionMatrix * viewMatrix * vec4(P, 1.0); }`, fragmentShader: `void main() { gl_FragColor = vec4(1.0); }` });
  const mesh = new THREE.Mesh(g, toon), line = new THREE.Mesh(g, hull); mesh.frustumCulled = line.frustumCulled = false;
  scene.add(mesh, line);
  chars.push({ fig, gs, g, mesh, line, toon, depth, t0: k * 17 % (clip.frames - 1) });
}
const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.ShaderMaterial({ uniforms: shared,
  vertexShader: `uniform mat4 SMx; varying vec4 vS; void main() { vec4 w = modelMatrix * vec4(position, 1.0); vS = SMx * w; gl_Position = projectionMatrix * viewMatrix * w; }`,
  fragmentShader: `uniform sampler2D smap; varying vec4 vS; void main() { vec3 s = vS.xyz / vS.w; float sh = (s.x > 0.0 && s.x < 1.0 && s.y > 0.0 && s.y < 1.0 && texture2D(smap, s.xy).r < s.z - 0.002) ? 1.0 : 0.0; gl_FragColor = vec4(mix(vec3(0.79, 0.76, 0.71), vec3(0.5, 0.47, 0.45), sh), 1.0); }` }));
floor.rotation.x = -Math.PI / 2; scene.add(floor);

const J = E.skeleton.J;
// the characters at the clip's frame t: the processor's part
function pose(t) {
  for (const c of chars) {
    const tt = (c.t0 + t) % (clip.frames - 1), f = c.fig;
    if (c.gs) {
      const p = f.retarget.pose(clip.sample(tt, f.sample)); f.retarget.placed(p);
      const shift = p.floor - c.gs.lowest(p); for (let j = 0; j < J; j++) p.P[j * 3 + 1] += shift;
      c.gs.setPose(p); c.gs.update(renderer); f.pose = p;
    } else { f.frame(clip, tt); c.g.attributes.position.needsUpdate = true; c.g.attributes.normal.needsUpdate = true; }
  }
}
function draw() {
  const w = canvas.clientWidth, h = canvas.clientHeight; renderer.setSize(w, h, false);
  const rows = Math.ceil(n / cols), span = Math.max(cols, rows) * gap + 1.5, P = chars[0].fig.pose.P, H0 = E.skeleton.index.Hips;
  // the camera and the light keep the group in view as it walks (the group's middle moves as the first figure's pelvis does)
  const mid = [P[H0 * 3] - chars[0].fig.place.position[0], 0.9, P[H0 * 3 + 2] - chars[0].fig.place.position[2]];
  camera.aspect = w / h; camera.updateProjectionMatrix();
  const dist = span / (2 * Math.tan(camera.fov * Math.PI / 360)) / Math.min(1, camera.aspect) * 0.75 + 2;
  camera.position.set(mid[0] + dist * 0.45, mid[1] + dist * 0.28, mid[2] + dist * 0.85); camera.lookAt(mid[0], mid[1], mid[2]);
  const r = span * 0.75; Object.assign(shadowCam, { left: -r, right: r, top: r, bottom: -r }); shadowCam.updateProjectionMatrix();
  shadowCam.position.set(mid[0] + L.x * 15, mid[1] + L.y * 15, mid[2] + L.z * 15); shadowCam.lookAt(mid[0], mid[1], mid[2]); shadowCam.updateMatrixWorld();
  shared.SMx.value.set(0.5, 0, 0, 0.5, 0, 0.5, 0, 0.5, 0, 0, 0.5, 0.5, 0, 0, 0, 1).multiply(shadowCam.projectionMatrix).multiply(shadowCam.matrixWorldInverse);
  floor.visible = false; for (const c of chars) { c.line.visible = false; c.mesh.material = c.depth; }
  renderer.setRenderTarget(shadowRT); renderer.clear(); renderer.render(scene, shadowCam); renderer.setRenderTarget(null);
  floor.visible = true; for (const c of chars) { c.line.visible = true; c.mesh.material = c.toon; }
  renderer.render(scene, camera);
}

const info = document.getElementById('info');
let gaps = [], cpu = [], last = performance.now(), t = 0, shown = last;
function loop() {
  const now = performance.now(), dt = now - last; last = now; gaps.push(dt);
  t += dt / 1000 * clip.fps;
  const a0 = performance.now(); pose(t); cpu.push(performance.now() - a0);
  draw();
  if (now - shown > 1000) {
    const g = gaps.slice(-180), c = cpu.slice(-180), mean = v => v.reduce((x, y) => x + y, 0) / v.length;
    info.textContent = `${n} × ${body.N} вершин, ${way === 'gpu' ? 'на видеокарте' : 'на процессоре'} · ${(1000 / mean(g)).toFixed(0)} кадров/с · самая длинная пауза ${Math.max(...g).toFixed(0)} мс · процессор ${mean(c).toFixed(1)} мс на кадр`;
    shown = now; if (gaps.length > 4000) { gaps = gaps.slice(-600); cpu = cpu.slice(-600); }
  }
  requestAnimationFrame(loop);
}
pose(0); draw();
window.B = {
  n, way, verts: body.N,
  // the page's own frames over some seconds
  measure(seconds = 5) {
    return new Promise(res => { const g0 = gaps.length; setTimeout(() => {
      const g = gaps.slice(g0 + 5), c = cpu.slice(g0 + 5), mean = v => v.reduce((x, y) => x + y, 0) / v.length, s = [...g].sort((x, y) => x - y);
      res({ n, way, verts: body.N, fps: +(1000 / mean(g)).toFixed(1), worstGapMs: +s[s.length - 1].toFixed(1), p95GapMs: +s[Math.floor(s.length * 0.95)].toFixed(1), processorMs: +mean(c).toFixed(2) });
    }, seconds * 1000); });
  },
};
window.__ready = true;
requestAnimationFrame(loop);
