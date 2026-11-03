// Our scenes drawn with MToon (pixiv three-vrm, @pixiv/three-vrm-materials-mtoon 3.5.5) instead of our toon light.
// look(scene, name): every lit material of the figures becomes an MToonMaterial with the look's settings; our own
// outline shells (back-faced dark copies) are hidden and MToon's own outline is used instead. look(scene, 'ours')
// puts everything back as it was.
import * as THREE from 'three';
import { MToonMaterial } from 'https://cdn.jsdelivr.net/npm/@pixiv/three-vrm-materials-mtoon@3.5.5/lib/three-vrm-materials-mtoon.module.js';

// a matcap: a soft light spot up-left, dark rim — MToon adds it on top of the colour
let MATCAP = null;
function matcap() {
  if (MATCAP) return MATCAP;
  const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');
  g.fillStyle = '#000'; g.fillRect(0, 0, 256, 256);
  const r = g.createRadialGradient(92, 78, 4, 92, 78, 70); r.addColorStop(0, 'rgba(255,255,255,0.55)'); r.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = r; g.fillRect(0, 0, 256, 256);
  MATCAP = new THREE.CanvasTexture(c); MATCAP.colorSpace = THREE.SRGBColorSpace; return MATCAP;
}

// shade: how the shade colour comes from the base colour ([r,g,b] multiplier, linear)
// toony: 0 smooth … 1 hard edge; shift: moves the edge (−: less shade); outline: [mode, width] (world: metres,
// screen: share of half the picture's height)
export const LOOKS = {
  hard:   { toony: 0.95, shift: 0.0,  shade: [0.42, 0.42, 0.42], outline: ['world', 0.0022] },
  soft:   { toony: 0.3,  shift: 0.0,  shade: [0.42, 0.42, 0.42], outline: ['world', 0.0022] },
  tint:   { toony: 0.92, shift: -0.05, shade: [0.55, 0.36, 0.48], outline: ['world', 0.0022], outlineColor: '#3a1830' },
  rim:    { toony: 0.92, shift: -0.05, shade: [0.55, 0.36, 0.48], rim: ['#ffe2c4', 3.0, 0.08], matcap: true, outline: ['world', 0.0022], outlineColor: '#3a1830' },
  thin:   { toony: 0.92, shift: -0.05, shade: [0.55, 0.36, 0.48], outline: ['world', 0.0008], outlineColor: '#3a1830' },
  thick:  { toony: 0.92, shift: -0.05, shade: [0.55, 0.36, 0.48], outline: ['world', 0.006], outlineColor: '#3a1830' },
  screen: { toony: 0.92, shift: -0.05, shade: [0.55, 0.36, 0.48], outline: ['screen', 0.006], outlineColor: '#3a1830' },
  none:   { toony: 0.92, shift: -0.05, shade: [0.55, 0.36, 0.48], outline: null },
};

const isInk = m => m && m.isMeshBasicMaterial && m.side === THREE.BackSide;
const isLit = m => m && (m.isMeshToonMaterial || m.isMeshStandardMaterial || m.isMeshPhongMaterial || m.isMeshLambertMaterial);

export function look(scene, name, over = {}) {
  // a name may carry '+one': the same look with only the key light (see oneLight)
  const [base, ...flags] = name.split('+');
  const L = base === 'ours' ? null : { ...LOOKS[base], ...over, oneLight: flags.includes('one') };
  const meshes = []; scene.traverse(o => { if (o.isMesh && !o.isInstancedMesh) meshes.push(o); });
  // oneLight: the back (rim) light off — MToon counts every directional light as a sun, and draws its own rim
  scene.traverse(o => { if (o.isDirectionalLight && !o.castShadow) { if (o.userData.mtoonI === undefined) o.userData.mtoonI = o.intensity; o.intensity = L && L.oneLight ? 0 : o.userData.mtoonI; } });
  for (const o of meshes) {
    const u = o.userData;
    if (u.mtoonOrig === undefined) {
      const m = o.material;
      if (isInk(m)) u.mtoonOrig = { ink: true, visible: o.visible };
      else if (isLit(m) && o.castShadow /* the figures cast shadows, floors do not */) u.mtoonOrig = { mat: m, groups: o.geometry.groups.slice() };
      else u.mtoonOrig = null;
    }
    const O = u.mtoonOrig; if (!O) continue;
    if (O.ink) { o.visible = L ? false : O.visible; continue; }
    // back to ours first
    o.material = O.mat; o.geometry.clearGroups(); for (const g of O.groups) o.geometry.addGroup(g.start, g.count, g.materialIndex);
    if (!L) continue;
    const src = O.mat, vc = !!src.vertexColors && !!o.geometry.attributes.color;
    const mt = new MToonMaterial({
      color: src.color.clone(), map: src.map || null, side: src.side, transparent: src.transparent, opacity: src.opacity,
      shadeColorFactor: new THREE.Color(src.color.r * L.shade[0], src.color.g * L.shade[1], src.color.b * L.shade[2]),
      shadeMultiplyTexture: src.map || null,        // so a drawn face stays drawn in the shade
      shadingToonyFactor: L.toony, shadingShiftFactor: L.shift, giEqualizationFactor: 0.9,
    });
    mt.vertexColors = vc; mt.ignoreVertexColor = !vc;
    if (L.rim) { mt.parametricRimColorFactor = new THREE.Color(L.rim[0]); mt.parametricRimFresnelPowerFactor = L.rim[1]; mt.parametricRimLiftFactor = L.rim[2]; mt.rimLightingMixFactor = 0.5; }
    if (L.matcap) { mt.matcapTexture = matcap(); mt.matcapFactor = new THREE.Color(1, 1, 1); }
    if (L.outline) {
      mt.outlineWidthMode = L.outline[0] === 'screen' ? 'screenCoordinates' : 'worldCoordinates';
      mt.outlineWidthFactor = L.outline[1] * (L.outline[0] === 'world' ? over.outlineScale || 1 : 1); mt.outlineColorFactor = new THREE.Color(L.outlineColor || '#24161e'); mt.outlineLightingMixFactor = 0;
    }
    if (L.outline) {
      // as three-vrm's loader does it: the same triangles twice, the second time with the outline copy
      const out = mt.clone(); out.isOutline = true; out.side = THREE.BackSide;
      const n = o.geometry.index ? o.geometry.index.count : o.geometry.attributes.position.count;
      o.geometry.clearGroups(); o.geometry.addGroup(0, n, 0); o.geometry.addGroup(0, n, 1);
      o.material = [mt, out];
    } else o.material = mt;
  }
}
