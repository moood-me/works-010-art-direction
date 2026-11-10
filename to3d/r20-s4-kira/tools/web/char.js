// What belongs to Кира alone: where her pack is, her colours, the clothes painted by place (the hoodie's pocket, hem
// and drawstrings, the trousers below its hem, the boots' acid laces and soles), the standing pose (a slouch, the head
// down, hands in the hoodie's pocket), the drawing's expressions as params of the 3D face, the motions offered in the viewer.
export const CHAR = {
  pack: 'data/kira.json',
  bg: ['#a892bc', '#4e3c60', '#17131d'],          // the drawing's backdrop (cast2.py: CAST.kira.bg)
  iris: ['#1c2224', '#4e6660', '#a9c0a8'],
  hair: { streak: 6.0, depth: 0.34, light: '#8c74a0', shine: 0.6 },
  frameGlint: '#ffffff',
  blinkUp: 32,
  faceY: 1.4, midY: 0.84,
  motions: [['stand', 'стоит'], ['walk', 'идёт'], ['sneak', 'крадётся'], ['idle', 'ждёт']],
  exprNames: [['calm', 'закрыта'], ['joy', 'усмешка'], ['surprise', 'удивление'], ['sad', 'грусть'], ['anger', 'гнев']],
  // cast2.py: CAST.kira.neutral (heavy lids, brows low and knit, a look from under them and aside, the mouth pressed,
  // one corner up) and her own sheet: joy is a crooked half-smile, never an open one
  expressions: {
    calm: { up: 9, low: 3, brow: -1.0, knit: 0.45, inner: -0.7, smile: -0.2, smirk: 0.3, lookX: -7, lookY: -5 },
    joy: { up: 6, low: 11, smile: 0.35, smirk: 0.9, brow: 0.5, inner: 0.2, lookX: -5, lookY: -3 },
    surprise: { up: -11, low: -3, jaw: 4.0, pucker: 0.3, brow: 4.6, inner: 1.0, iris: 0.9 },
    sad: { up: 13, smile: -0.8, brow: 0.3, inner: 3.4, knit: 0.3, lookX: 3, lookY: 9 },
    anger: { up: 5, low: 9, jaw: 1.2, smile: -0.8, wide: 0.4, brow: -3.0, inner: -2.4, knit: 1.2, lookY: -4 },
  },
  // the clothes, from each point's rest place in the drawing's units (x to her left, y down from the eye line, z
  // forward); trunk: 1 on the trunk and the legs, 0 on the arms, the neckband and the hood (build.py)
  glsl: (M, leg) => `
    void paintChar(inout vec3 base, inout vec3 bshd, inout vec3 glw, inout float gloss, vec3 dw, float trunk, float m) {
      float ax = abs(dw.x), y = dw.y;
      if (abs(m - ${M('lime')}) < 0.5) { gloss = 0.8;                  // the cups: a ring pressed into the plastic
        return; }
      if (abs(m - ${M('shoe')}) < 0.5) {                               // boots: a thick sole, acid laces up the front
        float bx = ax - ${leg.ankle[0].toFixed(1)};
        if (y > ${leg.feet.toFixed(1)} - 16.0) { base = vec3(0.16, 0.155, 0.18); if (y < ${leg.feet.toFixed(1)} - 14.5) base *= 1.6; }
        else if (dw.z > ${(leg.ankle[2] + 22).toFixed(1)} && y > ${leg.feet.toFixed(1)} - 190.0 && y < ${leg.feet.toFixed(1)} - 62.0) {
          float ph = fract((y - ${leg.feet.toFixed(1)}) / 26.0);
          float zig = (abs(ph - 0.5) * 4.0 - 1.0) * 9.0;
          if (abs(bx - zig) < 1.5 && abs(bx) < 10.5) { base = vec3(0.79, 0.93, 0.17); bshd = vec3(0.45, 0.56, 0.1); glw = vec3(0.9, 0.94, 0.4); }
        }
        return;
      }
      if (abs(m - ${M('suit')}) > 0.5) return;
      const float HEM = 640.0;
      if (trunk > 0.5 && y > HEM) {                                    // the trousers: narrow, charcoal
        base = vec3(0.172, 0.168, 0.196); bshd = vec3(0.075, 0.07, 0.1); glw = vec3(0.3, 0.2, 0.3);
        return;
      }
      if (trunk < 0.5) {                                               // sleeves, hood, neckband
        if (y < 172.0 && ax < 75.0 && dw.z > -70.0) { base *= 0.72; bshd *= 0.8; }
        return;
      }
      if (y > HEM - 24.0) { base *= 0.74; bshd *= 0.8;                 // the hem's ribbing
        if (fract(dw.x * 0.22) < 0.22) base *= 0.86; return; }
      if (dw.z > 0.0) {
        float px = mix(70.0, 96.0, clamp((y - 462.0) / 120.0, 0.0, 1.0));       // the pocket on the belly
        if (y > 462.0 && y < 584.0 && ax < px) {
          base *= 0.9;
          if (ax > px - 1.6 || y < 464.0) { base *= 0.62; bshd *= 0.8; }
        }
        float end = dw.x > 0.0 ? 262.0 : 244.0;                        // the drawstrings, of uneven length
        float xs = 11.0 + 2.5 * sin(y * 0.045 + (dw.x > 0.0 ? 0.0 : 1.3));
        if (y > 150.0 && y < end && abs(ax - xs) < 1.25) { base = vec3(0.81, 0.77, 0.84); bshd = vec3(0.5, 0.46, 0.58); if (y > end - 7.0) { base = vec3(0.79, 0.93, 0.17); bshd = vec3(0.45, 0.56, 0.1); } }
      }
    }`,
  // a slouch (the back round, the head forward and down, the look from under the brows), hands in the pocket
  stand(T) {
    const { pose, I, reach, turnUnder, sk, getV, qAxisAngle, normalize, sub, body, o } = T;
    const X = [1, 0, 0];
    const sl = o.slouch ?? 1;
    turnUnder(pose, sk, I.Hips, qAxisAngle(X, -0.05 * sl));
    for (const s of ['Left', 'Right']) turnUnder(pose, sk, I[s + 'Leg'], qAxisAngle(X, 0.05 * sl));
    turnUnder(pose, sk, I.Spine1, qAxisAngle(X, 0.07 * sl));
    turnUnder(pose, sk, I.Spine2, qAxisAngle(X, 0.09 * sl));
    turnUnder(pose, sk, I.Chest, qAxisAngle(X, 0.12 * sl));
    turnUnder(pose, sk, I.Neck1, qAxisAngle(X, 0.12 * sl));
    turnUnder(pose, sk, I.Head, qAxisAngle(X, -0.22 * sl));
    turnUnder(pose, sk, I.Head, qAxisAngle([0, 0, 1], 0.07 * sl));
    turnUnder(pose, sk, I.Head, qAxisAngle([0, 1, 0], -0.08 * sl));
    T.build();
    if (o.arms === 'down') {
      for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
        const Sh = getV(pose.P, I[s + 'Arm']), Wr = getV(pose.P, I[s + 'Hand']), El = getV(pose.P, I[s + 'ForeArm']);
        const Ln = T.len(sub(El, Sh)) + T.len(sub(Wr, El));
        reach(pose, s, [Sh[0] + sg * 0.06, Sh[1] - Ln * 0.985, Sh[2] + 0.04], [sg * 0.2, 0, -1]);
      }
    } else {
      // hands in the hoodie's pocket: each wrist put on the belly under the pouch, elbows out and a little back
      const hips = getV(pose.P, I.Hips);
      for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
        reach(pose, s, [hips[0] + sg * (o.hx ?? 0.085), hips[1] + (o.hy ?? 0.075), hips[2] + (o.hz ?? 0.1)], o.pole ?? [sg * 1.0, -0.1, -0.55]);
        turnUnder(pose, sk, I[s + 'ForeArm'], qAxisAngle(normalize(sub(getV(pose.P, I[s + 'Hand']), getV(pose.P, I[s + 'ForeArm']))), sg * (o.twist ?? 0.9)));
      }
    }
    for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
      const P0 = body.joints, jp = n => [P0[I[s + n] * 3], P0[I[s + n] * 3 + 1], P0[I[s + n] * 3 + 2]];
      const ix = jp('HandIndex1'), pk = jp('HandPinky1');
      const ax = [pk[0] - ix[0], pk[1] - ix[1], pk[2] - ix[2]];
      for (const f of ['Index', 'Middle', 'Ring', 'Pinky']) for (const k of [1, 2, 3])
        turnUnder(pose, sk, I[s + 'Hand' + f + k], qAxisAngle(ax, sg * (o.curl ?? 0.5) * (k === 1 ? 0.6 : 1)));
    }
  },
};
