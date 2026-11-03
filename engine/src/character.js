// A character: data that refers to presets and parameters (characters/<id>.json) — which body, how it is skinned, how
// a motion is carried onto it, how it looks. Versioned: a description says which version of this format it was
// written for, and each version keeps its own defaults, so a later engine that changes a default (or adds a step)
// leaves the characters written before it as they were. A new version adds DEFAULTS[n] and a step in `upgrade`.
//
//   {format: "engine/character", version: 1, id, label: {ru, en},
//    body: "<body preset id>"  (data/bodies/<id>.json),
//    skinning: {method: "cor" | "dqs" | "lbs", clavicleShare: 0…1, seam: null | {iterations, rings}},
//    motion: {floor: "lowest" | "pelvis", corrections: {<name>: {…}}  (src/corrections.js)},
//    look: {skin: "#rrggbb", roughness}}
// motion.floor: "lowest" — the body's lowest point as high as SOMA's skin's lowest then (scaled): standing on its
// feet, lying on its back, nothing goes into the floor; "pelvis" — only the pelvis's height scaled, nothing more.

export const DEFAULTS = {
  1: {
    skinning: { method: 'cor', clavicleShare: 0, seam: null },
    motion: { floor: 'lowest', corrections: {} },
    look: { skin: '#d9b49a', roughness: 0.65 },
  },
};
export const LATEST = 1;

export function resolve(desc) {
  if (desc.format !== 'engine/character') throw new Error(`${desc.id ?? '?'}: not a character`);
  const D = DEFAULTS[desc.version];
  if (!D) throw new Error(`${desc.id}: character version ${desc.version} is not known to this engine (it knows ${Object.keys(DEFAULTS).join(', ')})`);
  if (typeof desc.body !== 'string') throw new Error(`${desc.id}: body must name a body preset`);
  return {
    id: desc.id, label: desc.label, version: desc.version, body: desc.body,
    skinning: { ...D.skinning, ...(desc.skinning || {}) },
    motion: { ...D.motion, ...(desc.motion || {}), corrections: { ...D.motion.corrections, ...(desc.motion?.corrections || {}) } },
    look: { ...D.look, ...(desc.look || {}) },
  };
}
