// the bodies' sizes against SOMA's (Kimodo's own body): what proportions the scene has to deal with
import { createEngine } from '../../../../engine/src/engine.js';
import { read } from '../../../../engine/check/node-read.mjs';
const E = await createEngine({ read });
const sk = E.skeleton, H = sk.index.Hips, somaHip = sk.rest[H * 3 + 1] - sk.floor;
const r = (n) => sk.rest.slice(sk.index[n] * 3, sk.index[n] * 3 + 3);
console.log('SOMA hip', somaHip.toFixed(3), 'shoulder', (r('RightArm')[1] - sk.floor).toFixed(3), 'armLen', (Math.hypot(...r('RightArm').map((v, i) => v - r('RightForeArm')[i])) + Math.hypot(...r('RightForeArm').map((v, i) => v - r('RightHand')[i]))).toFixed(3));
for (const id of process.argv.slice(2)) {
  const b = await E.body(id), m = b.measures;
  const sh = b.joints[sk.index.RightArm * 3 + 1] - m.floor;
  console.log(id, 'h', m.height.toFixed(3), 'hip', m.hipHeight.toFixed(3), 'k', (m.hipHeight / somaHip).toFixed(3), 'shoulderY', sh.toFixed(3), 'arm', m.armLength.toFixed(3), 'arm/k', (m.armLength / (m.hipHeight / somaHip)).toFixed(3));
}
