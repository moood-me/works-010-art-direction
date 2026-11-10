// What belongs to Савелий Петрович alone: where his pack is, his colours, the clothes painted by place (the waistcoat
// over the shirt, the tie, buttons, the watch chain, trousers with a crease), the standing pose (hands clasped behind
// the back, as drawn), the drawing's expressions as params of the 3D face, the motions offered in the viewer.
export const CHAR = {
  pack: 'data/savely.json',
  bg: ['#d7a45a', '#5a4a3a', '#1f2324'],          // the drawing's backdrop (cast.py: CAST.savely.bg)
  iris: ['#26303a', '#5a7284', '#a9bcc6'],
  hair: { streak: 5.0, depth: 0.22, light: '#ffffff', shine: 0.5 },
  eyeShade: [27.0, 15.0, 0.8],                    // cast shadows fade round the eyes: from, to (units from an eye's centre), by how much
  faceRim: 1.0,                                    // how much of the rim light the face's front takes (a coloured rim on lips and lids reads as dirt)
  frameGlint: '#fff0c0',
  blinkUp: 30,
  faceY: 1.44, midY: 0.86,
  motions: [['stand', 'стоит'], ['walk', 'идёт'], ['bow', 'кланяется'], ['wave', 'машет'], ['idle', 'ждёт']],
  exprNames: [['calm', 'спокоен'], ['joy', 'радость'], ['surprise', 'удивление'], ['sad', 'грусть'], ['anger', 'гнев']],
  // cast.py: CAST.savely.neutral (brows a little knit and low, the mouth's corners down) and EXPR
  expressions: {
    calm: { up: 5, brow: -0.8, knit: 0.55, inner: -0.3, smile: -0.3 },
    joy: { up: 11, low: 18, jaw: 0.6, smile: 1.5, wide: 0.3, brow: 1.6, inner: 0.6 },
    surprise: { up: -11, low: -4, jaw: 4.0, pucker: 0.5, brow: 5.0, inner: 1.2, iris: 0.9 },
    sad: { up: 13, smile: -0.9, brow: 0.4, inner: 3.4, knit: 0.3, lookY: 9 },
    anger: { up: 8, low: 8, jaw: 1.5, smile: -0.7, wide: 0.4, brow: -3.0, inner: -2.2, knit: 1.1 },
  },
  // the suit, from each point's rest place in the drawing's units (x to his left, y down from the eye line, z forward);
  // trunk: 1 on the trunk and the legs, 0 on the arms and the collar (build.py)
  glsl: (M, leg) => `
    float seg(vec2 p, vec2 a, vec2 b) { vec2 pa = p - a, ba = b - a; return length(pa - ba * clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0)); }
    void paintChar(inout vec3 base, inout vec3 bshd, inout vec3 glw, inout float gloss, vec3 dw, float trunk, float m) {
      if (abs(m - ${M('suit')}) > 0.5) return;
      float ax = abs(dw.x), y = dw.y;
      const float HEM = 622.0;
      if (y < 200.0 && ax < 70.0 && dw.z > -100.0) {                  // the collar: open in front (a notch shows the throat), its fold's edge a line
        if (dw.z > 0.0 && y < 137.0 + 15.0 * (1.0 - ax / 13.0)) discard;
        float fold = 157.0 + (dw.z > 0.0 ? 16.0 * smoothstep(34.0, 6.0, ax) : 0.0);
        if (trunk < 0.5 && abs(y - fold) < 0.7 && ax > 5.0) base *= 0.74;
      }
      if (dw.z > 0.0 && y > 171.0 && y < 288.0) {                     // the tie: a knot under the collar and its blade
        float tw = y < 186.0 ? 9.5 - abs(y - 178.0) * 0.4 : 5.5 + (y - 186.0) * 0.035;
        if (ax < tw) { base = vec3(0.43, 0.16, 0.15); bshd = vec3(0.27, 0.09, 0.11); glw = vec3(0.62, 0.22, 0.18);
          if (abs(y - 186.5) < 0.6) base *= 0.7; return; }
      }
      if (trunk < 0.5) return;                                        // sleeves and collar: the shirt
      if (y > HEM + (dw.z > 0.0 ? 10.0 * smoothstep(26.0, 4.0, ax) * smoothstep(0.0, 3.0, ax) : 0.0)) {     // trousers; the crease down each leg's front
        base = vec3(0.353, 0.275, 0.212); bshd = vec3(0.19, 0.14, 0.16); glw = vec3(0.47, 0.30, 0.24);
        float lx = mix(${leg.hip[0].toFixed(1)}, ${leg.ankle[0].toFixed(1)}, clamp((y - ${leg.hip[1].toFixed(1)}) / ${(leg.ankle[1] - leg.hip[1]).toFixed(1)}, 0.0, 1.0));
        if (dw.z > 0.0 && y > 700.0 && abs(ax - lx) < 0.7) { base *= 1.22; bshd *= 0.8; }
        if (y < HEM + 16.0 && y > HEM + 13.0 && dw.z < 0.0) base *= 0.8;
        return;
      }
      float xv = y < 190.0 ? 40.0 : mix(40.0, 0.0, clamp((y - 190.0) / 100.0, 0.0, 1.0));       // the waistcoat's V
      if (dw.z > 0.0 && ax < xv) {
        if (ax < xv - 1.2 && ax > xv - 2.0 && y > 190.0) { base *= 0.9; }
        return;
      }
      base = vec3(0.239, 0.322, 0.267); bshd = vec3(0.125, 0.16, 0.175); glw = vec3(0.42, 0.34, 0.27);     // the waistcoat
      if (dw.z > 0.0) {
        if (ax < xv + 1.6) base *= 0.72;                               // the V's edge
        if (ax < 0.8 && y > 290.0) { base *= 0.6; bshd *= 0.7; }       // the front edge
        for (int i = 0; i < 5; i++) {                                  // buttons
          vec2 b = vec2(dw.x - 4.5, y - (322.0 + float(i) * 66.0));
          if (length(b) < 3.4) { base = vec3(0.79, 0.63, 0.31); bshd = vec3(0.42, 0.3, 0.16); gloss = 0.9; if (length(b) > 2.6) base *= 0.75; }
        }
        float px = abs(ax - 70.0);                                     // pocket welts
        if (px < 22.0 && abs(y - 470.0 + (ax - 70.0) * 0.08) < 1.0) base *= 0.66;
        // the watch chain: from a button to the pocket on his left, sagging
        if (dw.x > 6.0 && dw.x < 66.0) { float u = (dw.x - 36.0) / 30.0; float yc = 454.0 + 24.0 * (1.0 - u * u);
          if (abs(y - yc) < 1.1 + 0.5 * abs(u)) { base = vec3(0.82, 0.66, 0.33); bshd = vec3(0.46, 0.33, 0.17); gloss = 1.0; } }
      } else if (ax < 0.7 && y > 200.0) base *= 0.75;                  // the back seam
    }`,
  // hands clasped behind the back: each wrist put behind the pelvis (two-bone reach), elbows out and back
  stand(T) {
    const { pose, I, reach, turnUnder, sk, getV, qAxisAngle, normalize, sub, body, o } = T;
    const hips = getV(pose.P, I.Hips);
    for (const [s, sg] of [['Left', 1], ['Right', -1]]) {
      if (o.arms === 'down') {
        const Sh = getV(pose.P, I[s + 'Arm']), Wr = getV(pose.P, I[s + 'Hand']), El = getV(pose.P, I[s + 'ForeArm']);
        const L = T.len(sub(El, Sh)) + T.len(sub(Wr, El));
        reach(pose, s, [Sh[0] + sg * 0.05, Sh[1] - L * 0.985, Sh[2] + 0.02], [sg * 0.2, 0, -1]);
      } else {
        reach(pose, s, [hips[0] + sg * (o.hx ?? 0.05), hips[1] + (o.hy ?? 0.0) + (sg > 0 ? 0.012 : -0.012), hips[2] - (o.hz ?? 0.15)], o.pole ?? [sg * 0.55, -0.2, -1.0]);
        turnUnder(pose, sk, I[s + 'ForeArm'], qAxisAngle(normalize(sub(getV(pose.P, I[s + 'Hand']), getV(pose.P, I[s + 'ForeArm']))), sg * (o.twist ?? -1.2)));
      }
      const P0 = body.joints, jp = n => [P0[I[s + n] * 3], P0[I[s + n] * 3 + 1], P0[I[s + n] * 3 + 2]];
      const ix = jp('HandIndex1'), pk = jp('HandPinky1');
      const ax = [pk[0] - ix[0], pk[1] - ix[1], pk[2] - ix[2]];
      for (const f of ['Index', 'Middle', 'Ring', 'Pinky']) for (const k of [1, 2, 3])
        turnUnder(pose, sk, I[s + 'Hand' + f + k], qAxisAngle(ax, sg * (o.curl ?? 0.95) * (k === 1 ? 0.6 : 1)));
    }
    if (o.head) turnUnder(pose, sk, I.Head, qAxisAngle(o.head.axis, o.head.a));
  },
};
