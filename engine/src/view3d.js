// Drawing figures with three.js — the viewer's and the picture check's one stage, so what is checked is what is seen.
// A soft studio: a warm key light with shadows that follows the figures, a cool rim, a floor with a metre grid,
// and the pelvis's path drawn on it.
export function makeStage(THREE, canvas, { background = '#cfc8bd', pixelRatio = 1 } = {}) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(pixelRatio);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const scene = new THREE.Scene(); scene.background = new THREE.Color(background);
  const camera = new THREE.PerspectiveCamera(26, 1, 0.05, 200);
  scene.add(new THREE.HemisphereLight('#fff4e6', '#5b544c', 1.05));
  const key = new THREE.DirectionalLight('#fff0dc', 2.1); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -2.2, right: 2.2, top: 2.6, bottom: -1.2, near: 0.5, far: 14 });
  key.shadow.bias = -0.0004; key.shadow.normalBias = 0.02;
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
  const path = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: '#b4532a' })); path.position.y = 0.003; scene.add(path);
  const joins = new THREE.Group(); scene.add(joins);
  const stage = {
    THREE, renderer, scene, camera, key, rim, floor,
    // light from the same side of the figure wherever it is
    light(at) {
      key.position.set(at[0] - 2.2, 3.6, at[2] + 2.6); key.target.position.set(at[0], 0.8, at[2]);
      rim.position.set(at[0] + 2.4, 2.2, at[2] - 2.8); rim.target.position.set(at[0], 0.9, at[2]);
    },
    // the path on the floor, and a mark where one motion of a chain goes on into the next
    showPath(points, marks = []) {
      path.geometry.dispose(); path.geometry = new THREE.BufferGeometry().setFromPoints(points.map(p => new THREE.Vector3(p[0], 0, p[1])));
      joins.clear();
      for (const m of marks) { const d = new THREE.Mesh(new THREE.CircleGeometry(0.05, 24), new THREE.MeshBasicMaterial({ color: '#b4532a' })); d.rotation.x = -Math.PI / 2; d.position.set(m[0], 0.004, m[1]); joins.add(d); }
    },
    // the picture's size; shift: how many pixels the view's centre moves right (to keep clear of a panel on the left)
    size(w, h, shift = 0) {
      renderer.setSize(w, h, false); camera.aspect = w / h;
      if (shift) camera.setViewOffset(w, h, -shift, 0, w, h); else camera.clearViewOffset();
      camera.updateProjectionMatrix();
    },
    // a camera around a point: yaw 0 looks from +z (the figure's front, before it turns), pitch up, distance
    look(target, { yaw, pitch, dist }) {
      const cp = Math.cos(pitch);
      camera.position.set(target[0] + Math.sin(yaw) * cp * dist, target[1] + Math.sin(pitch) * dist, target[2] + Math.cos(yaw) * cp * dist);
      camera.lookAt(target[0], target[1], target[2]);
    },
    render() { renderer.render(scene, camera); },
  };
  return stage;
}

// a figure's skin as a three.js mesh, updated from the figure each frame
export function figureMesh(THREE, figure, look) {
  const b = figure.body, g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(figure.positions, 3));
  g.setAttribute('normal', new THREE.BufferAttribute(figure.normals, 3));
  g.setIndex(new THREE.BufferAttribute(b.triangles, 1));
  const mesh = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: look.skin, roughness: look.roughness }));
  mesh.castShadow = mesh.receiveShadow = true; mesh.frustumCulled = false;
  // the joints, drawn over the body when asked
  const dots = new THREE.InstancedMesh(new THREE.SphereGeometry(0.008, 10, 8), new THREE.MeshBasicMaterial({ color: '#e0592a', depthTest: false, transparent: true }), b.skeleton.J);
  dots.renderOrder = 10; dots.visible = false; dots.frustumCulled = false;
  const m = new THREE.Matrix4();
  return {
    mesh, dots,
    update() {
      g.attributes.position.needsUpdate = true; g.attributes.normal.needsUpdate = true;
      if (dots.visible) { const P = figure.pose.P; for (let j = 0; j < b.skeleton.J; j++) dots.setMatrixAt(j, m.makeTranslation(P[j * 3], P[j * 3 + 1], P[j * 3 + 2])); dots.instanceMatrix.needsUpdate = true; }
    },
    dispose() { g.dispose(); mesh.material.dispose(); dots.geometry.dispose(); dots.material.dispose(); },
  };
}
