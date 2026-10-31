// the characters: each head from its own picture — the outline from the front and the profile, read off the drawing,
// its own nose, lips, cheekbones, eyes and hair
export default (CH, { L, braid, bun, band, helmet, stripe, THREE }) => {
  // the two lines of a face, from named places on it (head units: the skull's radius ~1, eyes at y ≈ -0.12)
  // front: half-widths — skull, temples, brow, cheekbone (the widest of the face), jaw angle, chin; frontB: the back half (skull, then the neck)
  // prof: the front of the face — forehead, brow, under the eye, the cheek plane, philtrum, chin; then under the chin into the neck
  const face = o => {
    const c = Object.assign({ crown: 1.12, skull: 0.86, temple: 0.84, brow: 0.82, cheekY: -0.35, cheek: 0.8, jawY: -0.82, jaw: 0.56, chinY: -1.18, chin: 0.16, neck: 0.36,
      fore: 0.8, browZ: 0.84, eyeZ: 0.8, plane: 0.8, phil: 0.78, chinZ: 0.72, back: -1.0, nape: -0.62 }, o);
    const front = [[c.crown, 0.05], [c.crown - 0.08, 0.42], [0.85, 0.7], [0.5, c.skull], [0.2, c.temple], [0.0, c.brow], [c.cheekY, c.cheek], [(c.cheekY + c.jawY) / 2, (c.cheek + c.jaw) / 2 + 0.02], [c.jawY, c.jaw], [(c.jawY + c.chinY) / 2, (c.jaw + c.chin) / 2 - 0.02], [c.chinY + 0.06, c.chin], [c.chinY - 0.04, c.chin * 0.85 + 0.04], [c.chinY - 0.2, c.neck]];
    const frontB = [[c.crown, 0.05], [c.crown - 0.08, 0.42], [0.85, 0.7], [0.5, c.skull], [0.2, c.temple], [-0.2, c.brow * 0.95], [-0.5, c.jaw * 0.9 + 0.05], [-0.8, c.neck + 0.12], [c.chinY - 0.2, c.neck]];
    const prof = [[c.crown, 0.0], [c.crown - 0.08, 0.32], [0.85, 0.62], [0.5, c.fore], [0.2, c.browZ], [-0.12, c.eyeZ], [-0.4, c.plane], [-0.6, c.phil], [c.chinY + 0.12, c.chinZ], [c.chinY + 0.02, c.chinZ - 0.05], [c.chinY - 0.07, c.chinZ - 0.18], [c.chinY - 0.2, 0.42], [c.chinY - 0.36, 0.3]];
    const back = [[c.crown, -0.02], [c.crown - 0.08, -0.4], [0.75, -0.8], [0.3, c.back], [-0.1, c.back * 0.95], [-0.5, c.nape], [-0.8, -0.42], [c.chinY - 0.3, -0.38]];
    return { front, frontB, prof, back, chinY0: c.chinY, cs: c };
  };


  // the profile's front at a height (linear between the points read off the picture)
  const zfOf = prof => y => { const P = prof.slice().sort((a, b) => a[0] - b[0]); if (y <= P[0][0]) return P[0][1]; for (let i = 0; i < P.length - 1; i++) if (y <= P[i + 1][0]) { const t = (y - P[i][0]) / (P[i + 1][0] - P[i][0]); return P[i][1] + (P[i + 1][1] - P[i][1]) * t; } return P[P.length - 1][1]; };
  // the face sculpted: planes cut first (the cheek under the cheekbone, the jaw, the chin's front, the forehead), each
  // edge as soft as this face wants; then hollows carved (sockets, under the cheekbone, above the lip, nostrils) and
  // forms added (the nose as a wedge with a ridge, its tip and wings, a cheekbone ridge, the lips, the chin)
  const sculptFace = (prof, p, c) => {
    const zf = zfOf(prof), o = [];
    const q = Object.assign({ cbX: 0.5, cbY: -0.3, cbK: 0.12, cbH: 0.0, jawX: 0.5, jawY: -0.85, jawK: 0.12, chinFlat: 0, chinK: 0.15,
      sock: 0, sockK: 0.2, hollow: 0, noseTop: -0.12, tipY: -0.45, tipOut: 0.12, noseW: 0.04, noseRound: 0.03, tipR: 0.055, wingX: 0.075, wing: 1, nostril: 1, bend: 0,
      mouthY: -0.76, mouthW: 0.15, up: 0.035, lo: 0.045, lipZ: 0.03, lipK: 0.02, bow: 0.035, philtrum: 1, chinW: 0.16, chinH: 0, chinK2: 0.08, brow: 0.0 }, p);
    // planes, each touching the face at its own place and shaving beyond it: the cheek under the cheekbone, the jaw, the chin's front
    if (q.cheekCut > 0) o.push(['cut', ['plane', ['@', q.cbX + 0.04, q.cbY - 0.22, -q.cheekCut], [0.45, -0.62, 0.64]], q.cbK, true, ['ell', [q.cbX + 0.1, q.cbY - 0.3, 0.3], [0.38, 0.32, 0.6]]]);
    if (q.jawCut > 0) o.push(['cut', ['plane', ['@', q.jawX - 0.06, q.jawY + 0.06, -q.jawCut], [0.8, -0.55, 0.22]], q.jawK, true, ['ell', [q.jawX, q.jawY - 0.05, 0.2], [0.4, 0.35, 0.7]]]);
    if (q.chinFlat > 0) o.push(['cut', ['plane', ['@', 0, q.chinY + 0.1, -q.chinFlat], [0, -0.3, 1]], q.chinK, false, ['ell', [0, q.chinY + 0.05, 0.6], [0.3, 0.16, 0.5]]]);
    // hollows: the eye sockets
    if (q.sock) o.push(['carve', ['ell', ['@', c.eyeX, c.eyeY + 0.03, 0.02], [c.eyeR * 1.45, c.eyeR * 1.1, 0.07 * q.sock], ['n', 0]], q.sockK, true]);
    // the cheekbone: a ridge lying on the skin along its line; the hollow under it
    if (q.cbH) o.push(['add', ['ell', ['@', q.cbX, q.cbY, -0.04 + q.cbH], [0.22, 0.045, 0.06], ['n', -0.35]], q.cbK * 0.6, true]);
    if (q.hollow) o.push(['carve', ['ell', ['@', q.cbX - 0.05, q.cbY - 0.28, 0.03], [0.15, 0.12, 0.06 * q.hollow], ['n', 0]], 0.12, true]);
    // the nose: a wedge, ridge forward, from the bridge to the tip; the tip; the wings; the nostrils carved
    const zt = zf(q.tipY) + q.tipOut, zb = zf(q.noseTop) + 0.01, len = Math.hypot(q.noseTop - q.tipY, zt - zb), pitch = Math.atan2(zb - zt, q.noseTop - q.tipY);
    o.push(['add', ['nose', ['@', 0, q.noseTop, -0.03], ['@', 0, q.tipY + 0.02, q.tipOut - q.tipR * 0.5 + q.bend], q.noseW * 1.0, q.tipR * (q.baseW ?? 1.3), 0.1, 0.12], q.noseK ?? 0.035]);
    o.push(['add', ['ell', ['@', 0, q.tipY, -q.tipR * 0.55], [q.tipR * 1.05, q.tipR * 0.92, q.tipR]], 0.045]);
    if (q.wing) o.push(['add', ['ell', ['@', q.wingX, q.tipY - 0.03, -0.01], [0.045, 0.035, 0.04], ['n', 0]], 0.035, true]);
    if (q.nostril) o.push(['carve', ['ell', ['@', 0.036, q.tipY - q.tipR * 0.75, -0.012], [0.019, 0.01, 0.026]], 0.01, true]);
    // above the lip: the philtrum's dip
    if (q.philtrum) o.push(['carve', ['ell', ['@', 0, (q.tipY + q.mouthY) / 2 - 0.02, 0.012], [0.032, 0.065, 0.022], ['n', 0]], 0.03]);
    // the lips: the upper one with its bow (two halves), the lower one; the parting cut thin
    if (q.lipZ > 0) {
      o.push(['add', ['ell', ['@', q.bow, q.mouthY + q.up * 0.5, -0.02 + q.lipZ * 0.5], [q.mouthW * 0.56, q.up * 0.62, 0.04], ['n', -0.12]], q.lipK]);
      o.push(['add', ['ell', ['@', -q.bow, q.mouthY + q.up * 0.5, -0.02 + q.lipZ * 0.5], [q.mouthW * 0.56, q.up * 0.62, 0.04], ['n', 0.12]], q.lipK]);
      o.push(['add', ['ell', ['@', 0, q.mouthY - q.lo * 0.5, -0.025 + q.lipZ * 0.6], [q.mouthW * 0.76, q.lo * 0.62, 0.045], ['n', 0]], q.lipK * 1.2]);
    }
    o.push(['carve', ['box', ['@', 0, q.mouthY, 0.0], [q.mouthW * 0.98, 0.0035, 0.04], ['n', 0], 0.003], 0.006]);
    // the chin
    if (q.chinH) o.push(['add', ['ell', ['@', 0, q.chinY + 0.1, -0.06 + q.chinH], [q.chinW, 0.09, 0.07], ['n', 0]], q.chinK2]);
    return { sculpt: o, mouth: { y: q.mouthY, w: q.mouthW, up: q.up, lo: q.lo, tint: q.tint ?? 0.7 } };
  };

  // Gogo — a round face, wide soft cheeks, a small chin; a short upturned nose; a small mouth open in an "o"; big brown eyes
  CH.gogo = {
    S: { cbK: 0.25, jawK: 0.25, chinH: 0.02, tint: 0.5, sock: 0.7 },
    ...face({ cheek: 0.86, cheekY: -0.42, jaw: 0.62, jawY: -0.78, chin: 0.2, chinY: -1.08, temple: 0.86, plane: 0.84, phil: 0.8, chinZ: 0.74 }),
    view: [0.0, 0.08], body: 'girl', scale: 0.125, skin: '#f0bfa0', blush: 0.7,
    nose: { top: -0.12, tipY: -0.42, out: 0.08, rTop: 0.03, rTip: 0.065, wing: 0.1, up: 0.02 },
    lips: { y: -0.72, w: 0.07, uh: 0.03, ud: 0.03, lh: 0.035, ld: 0.035, out: -0.01, bow: 0.02 }, open: 0.1, lipLine: '#5a2a2a', lip: '#c47a7a',
    eyeX: 0.4, eyeY: -0.12, eyeR: 0.28, eyeH: 0.8, eyeW: 1.1, lowerH: 0.6, iris: '#5a3420', irisA: 0.7, pupilA: 0.36, lash: 0.026, gaze: [0.18, 0.06], lowerLid: false,
    browY: 0.22, browLen: 0.3, browT: 0.035, browArch: 0.07, browIn: 0.06, browCol: '#1e1418',
    hair: '#1d171c', hairK: 0.1, hairline: { front: 0.5, side: -0.2, back: -0.9 },
    hair3: [['S', 0.07], ['E', [0, 0.25, -0.15], [1.0, 1.0, 1.02]], ['X', [0, -0.42, 0.9], [0.74, 0.86, 0.62]], ['X', [0, -1.75, 0], [2.0, 1.0, 2.0]]],
    extras: [stripe([[0.25, 1.1, 0.25], [0.5, 0.92, 0.85], [0.62, 0.5, 1.08]], 0.08, '#6a3e9a'), helmet('#d8b13e')],
    top: '#d6ae3c', bottom: '#2d2b30', shoes: '#c9a23a', gloves: '#d6ae3c', sleeve: 'long', legs: 'long', boots: true,
  };
  // Jack — a long narrow face, cheekbones high and marked, a lean jaw to a pointed chin; a long straight nose; a wide sly smile with thin lips; low heavy brows
  CH.jack = {
    S: { cbX: 0.52, cbY: -0.28, cbH: 0.02, cbK: 0.07, jawK: 0.07, hollow: 0.35, chinK: 0.07, faceK: 0.07, noseRound: 0.02, tint: 0.35 },
    ...face({ cheek: 0.76, cheekY: -0.3, jaw: 0.5, jawY: -0.9, chin: 0.13, chinY: -1.28, temple: 0.8, skull: 0.84, plane: 0.78, phil: 0.76, chinZ: 0.7, eyeZ: 0.76 }),
    cheekbones: [{ x: 0.5, y: -0.36, r: 0.2, sink: 0.62, h: 0.7 }],
    view: [-0.2, 0.0], body: 'boy', scale: 0.12, skin: '#f0d0bc', blush: 0.12,
    nose: { top: -0.04, tipY: -0.52, out: 0.2, rTop: 0.035, rTip: 0.06, wing: 0.09, bend: -0.01, up: 0.0 },
    lips: { y: -0.84, w: 0.2, uh: 0.02, ud: 0.025, lh: 0.028, ld: 0.03, out: -0.02, bow: 0.05 }, smile: 0.07, smirk: 0.6, open: 0.07, lip: '#c8908a',
    eyeX: 0.35, eyeY: -0.14, eyeR: 0.2, eyeH: 0.48, eyeW: 1.05, eyeTilt: -0.06, lowerH: 0.55, iris: '#6a96b8', irisA: 0.62, pupilA: 0.3, lash: 0.02, gaze: [-0.12, -0.04],
    browY: 0.08, browLen: 0.4, browT: 0.045, browArch: -0.01, browIn: -0.03, browTilt: 0.05, browCol: '#8a7a6a',
    hair: '#ece8e2', hairK: 0.07, hairline: { front: 0.6, side: -0.15, back: -0.75 },
    hair3: [['S', 0.08],
      ...[[-0.6, 0.95, 0.45], [-0.25, 1.1, 0.55], [0.15, 1.12, 0.55], [0.5, 1.0, 0.5], [-0.75, 0.75, 0.6], [0.7, 0.8, 0.62]].map(([x, y, z], i) => ['C', [x * 0.8, y - 0.15, z - 0.2], [x * 1.25, y + 0.3, z + 0.25 - (i % 2) * 0.15], 0.17, 0.02]),
      ...[[-0.5, 1.0, -0.2], [0.0, 1.15, -0.1], [0.45, 1.0, -0.25], [-0.2, 0.9, -0.7], [0.3, 0.85, -0.75]].map(([x, y, z]) => ['C', [x * 0.8, y - 0.2, z * 0.8], [x * 1.3, y + 0.32, z * 1.3], 0.18, 0.02]),
      ['X', [0, -0.45, 0.95], [0.7, 0.92, 0.55]]],
    top: '#4a5a8a', bottom: '#6a5a48', shoes: '#f0d0bc', sleeve: 'long', legs: 'long',
  };
  // Gwen — a long oval face, a narrow jaw to a small pointed chin; a long nose ending in a small turned-up tip; small lips, slightly parted, the lower one full
  CH.gwen = {
    S: { cbK: 0.08, jawK: 0.08, noseRound: 0.022, tint: 0.6 }, 
    ...face({ cheek: 0.74, cheekY: -0.3, jaw: 0.48, jawY: -0.88, chin: 0.14, chinY: -1.24, temple: 0.8, skull: 0.84, plane: 0.78, phil: 0.77, chinZ: 0.72 }),
    view: [-0.15, 0.04], body: 'girl', scale: 0.12, skin: '#f3c8aa', blush: 0.3,
    nose: { top: -0.2, tipY: -0.5, out: 0.1, rTop: 0.024, rTip: 0.052, wing: 0.08, bend: -0.015, up: 0.025 },
    lips: { y: -0.82, w: 0.12, uh: 0.026, ud: 0.03, lh: 0.042, ld: 0.04, out: -0.015, bow: 0.03 }, open: 0, lip: '#d08a80',
    eyeX: 0.37, eyeY: -0.12, eyeR: 0.25, eyeH: 0.7, eyeW: 1.05, eyeTilt: -0.05, iris: '#4a7fb0', irisA: 0.66, pupilA: 0.33, lash: 0.024, lowerLid: false,
    browY: 0.2, browLen: 0.34, browT: 0.03, browArch: 0.05, browIn: 0.06, browCol: '#a07a4a',
    hair: '#e3c37e', hairK: 0.12, hairline: { front: 0.6, side: -0.1, back: -1.0 },
    hair3: [['S', 0.11], ['E', [0.0, 0.2, -0.3], [0.92, 0.95, 0.82]],
      // the long side: a wide flat sheet from the part over the top, falling past the cheek to the jaw, the end flicking out
      ['R', [[-0.35, 1.12, 0.3], [0.2, 1.08, 0.72], [0.68, 0.55, 0.8], [0.88, -0.15, 0.55], [0.98, -0.62, 0.32]], [0.3, 0.38, 0.36, 0.3, 0.16], [0.07, 0.1, 0.1, 0.09, 0.04]],
      ['R', [[-0.3, 1.05, 0.55], [0.08, 0.8, 0.98], [0.35, 0.3, 1.02]], [0.18, 0.2, 0.08], [0.05, 0.06, 0.03]],
      ['R', [[-0.5, 1.0, 0.1], [-0.82, 0.55, 0.3], [-0.92, 0.05, 0.25]], [0.24, 0.24, 0.1], [0.05, 0.06, 0.03]],
      ['X', [-0.25, -0.45, 0.95], [0.68, 0.85, 0.55]], ['X', [0, -1.55, -0.2], [1.6, 0.85, 1.6]]],
    top: '#f1eee9', bottom: '#2b2730', shoes: '#efe9f2', sleeve: 'long', legs: 'long',
  };
  // Marco — a round face, the jaw wide and soft, a rounded chin; a small pointed nose; a wide gentle smile; very big round eyes with small pupils; thick brows
  CH.marco = {
    S: { cbK: 0.22, jawK: 0.2, noseRound: 0.025, tint: 0, lipZ: 0, up: 0.012, lo: 0.014, philtrum: 0, chinH: 0 },
    ...face({ cheek: 0.86, cheekY: -0.45, jaw: 0.72, jawY: -0.82, chin: 0.3, chinY: -1.12, temple: 0.86, plane: 0.82, phil: 0.8, chinZ: 0.74 }),
    view: [0.0, 0.04], body: 'boy', scale: 0.13, skin: '#f1c39f', blush: 0.2, flat: 2.8,
    nose: { top: -0.16, tipY: -0.4, out: 0.1, rTop: 0.025, rTip: 0.045, wing: 0.07, bend: 0.0, up: -0.01 },
    lips: { y: -0.74, w: 0.2, uh: 0.015, ud: 0.02, lh: 0.02, ld: 0.02, out: -0.03, bow: 0.06 }, smile: 0.08, lipT: 0.014, lipLine: '#5a2a24', lip: '#e0a888',
    eyeX: 0.38, eyeY: -0.1, eyeR: 0.29, eyeH: 0.9, eyeW: 1.18, lowerH: 0.75, iris: '#4a2a1a', irisA: 0.46, pupilA: 0.48, gaze: [0.3, 0.02], lash: 0.012, lowerLid: false,
    browY: 0.15, browLen: 0.38, browT: 0.055, browArch: 0.03, browCol: '#2a1a14',
    hair: '#3a2219', hairK: 0.12, hairline: { front: 0.55, side: -0.2, back: -0.75 },
    hair3: [['S', 0.1], ['E', [0.1, 0.78, 0.55], [0.85, 0.36, 0.5]], ['C', [-0.15, 0.95, 0.65], [-0.62, 0.6, 1.0], 0.22, 0.04], ['C', [0.2, 1.0, 0.6], [0.55, 0.62, 1.0], 0.2, 0.04],
      ['C', [0.0, 1.1, 0.2], [0.2, 1.45, 0.1], 0.14, 0.02], ['E', [0.8, 0.3, 0.0], [0.22, 0.4, 0.45]], ['E', [-0.8, 0.3, 0.0], [0.22, 0.4, 0.45]], ['X', [0, -0.4, 0.95], [0.78, 0.86, 0.55]]],
    top: '#c9353a', bottom: '#2c2b33', shoes: '#3a2f2a', sleeve: 'long', legs: 'long',
  };
  // Ariel — a heart face: wide high cheekbones, a tiny pointed chin; a tiny turned-up nose; small full pouting lips; huge eyes set low
  CH.ariel = {
    S: { cbK: 0.15, jawK: 0.12, tint: 0.85, lipZ: 0.045, noseRound: 0.015 },
    ...face({ cheek: 0.8, cheekY: -0.22, jaw: 0.42, jawY: -0.86, chin: 0.1, chinY: -1.2, temple: 0.84, plane: 0.8, phil: 0.77, chinZ: 0.72 }),
    view: [0.25, 0.1], body: 'woman', scale: 0.12, skin: '#f6d8c8', blush: 0.45,
    nose: { top: -0.2, tipY: -0.5, out: 0.08, rTop: 0.022, rTip: 0.045, wing: 0.07, bend: -0.01, up: 0.025 },
    lips: { y: -0.8, w: 0.09, uh: 0.035, ud: 0.035, lh: 0.05, ld: 0.045, out: -0.005, bow: 0.025 }, open: 0.03, lip: '#d0605e',
    eyeX: 0.38, eyeY: -0.18, eyeR: 0.29, eyeH: 0.78, eyeW: 1.1, eyeTilt: 0.05, iris: '#3a9a8a', irisA: 0.68, pupilA: 0.3, lash: 0.032, wing: 0.08, gaze: [-0.2, -0.05],
    browY: 0.18, browLen: 0.32, browT: 0.026, browArch: 0.08, browIn: 0.07, browCol: '#9a3a28',
    hair: '#c8322a', hairK: 0.16, hairline: { front: 0.6, side: -0.3, back: -1.1 }, hairBox: [[-1.9, -3.0, -1.9], [1.9, 1.9, 1.8]],
    hair3: [['S', 0.12], ['E', [0.0, 0.5, -0.1], [1.12, 0.85, 1.15]], ['E', [-0.3, 0.75, 0.6], [0.6, 0.32, 0.45]],
      ['T', [[-0.7, 0.6, 0.5], [-0.98, -0.2, 0.55], [-1.05, -1.2, 0.35], [-0.85, -2.3, 0.3]], [0.3, 0.32, 0.28, 0.14]],
      ['T', [[0.7, 0.6, 0.45], [0.98, -0.2, 0.5], [1.02, -1.2, 0.3], [0.85, -2.2, 0.25]], [0.3, 0.32, 0.26, 0.12]],
      ['T', [[0, 0.3, -0.8], [0, -0.8, -1.0], [0, -2.4, -0.7]], [0.7, 0.6, 0.3]], ['X', [0.05, -0.5, 0.95], [0.64, 0.86, 0.55]]],
    top: '#b9b2d8', bottom: '#b9b2d8', shoes: '#e8d8d0', sleeve: 'none', legs: 'long',
  };
  // the 3D boy — wide cheeks tapering to a pointed chin; a small nose; a lopsided smirk; one brow up; ginger hair in a big swoop up and to one side
  CH.boy3d = {
    S: { cbK: 0.12, jawK: 0.1, tint: 0.4 },
    ...face({ cheek: 0.84, cheekY: -0.35, jaw: 0.52, jawY: -0.86, chin: 0.15, chinY: -1.17, temple: 0.85, plane: 0.8, phil: 0.78, chinZ: 0.72 }),
    view: [0.15, 0.04], body: 'boy', scale: 0.13, skin: '#f4cdb2', blush: 0.3,
    nose: { top: -0.12, tipY: -0.45, out: 0.1, rTop: 0.028, rTip: 0.055, wing: 0.08, up: 0.01 },
    lips: { y: -0.8, w: 0.17, uh: 0.02, ud: 0.025, lh: 0.03, ld: 0.03, out: -0.02, bow: 0.04 }, smile: 0.05, smirk: 0.9, lip: '#c08078',
    eyeX: 0.37, eyeY: -0.12, eyeR: 0.25, eyeH: 0.6, eyeW: 1.08, lowerH: 0.45, iris: '#a87a28', irisA: 0.62, pupilA: 0.3, lash: 0.02,
    browY: 0.14, browLen: 0.38, browT: 0.05, browArch: 0.02, browIn: -0.02, browTilt: 0.14, browCol: '#6a3018',
    hair: '#b4522a', hairK: 0.12, hairline: { front: 0.55, side: -0.15, back: -0.75 },
    hair3: [['S', 0.1], ['T', [[-0.6, 0.8, 0.4], [-0.25, 1.3, 0.55], [0.35, 1.35, 0.6], [0.85, 0.95, 0.7]], [0.3, 0.38, 0.32, 0.08]],
      ['C', [0.1, 1.1, 0.75], [0.6, 0.55, 1.0], 0.2, 0.03], ['C', [-0.2, 1.15, 0.7], [-0.35, 0.7, 1.0], 0.16, 0.03], ['E', [-0.8, 0.3, 0.0], [0.2, 0.42, 0.45]], ['E', [0.82, 0.3, 0.0], [0.2, 0.42, 0.45]], ['X', [0, -0.42, 0.95], [0.76, 0.86, 0.55]]],
    top: '#24304a', bottom: '#3a3238', shoes: '#2a2422', sleeve: 'long', legs: 'long',
  };
  // the doll — a wide round face, plump cheeks, a small pointed chin; a tiny button nose; a small smile; huge purple eyes with lashes; long straight purple hair, a swept fringe
  CH.doll = {
    S: { cbK: 0.25, jawK: 0.2, tint: 0.6, lipZ: 0.035 },
    ...face({ cheek: 0.88, cheekY: -0.4, jaw: 0.56, jawY: -0.82, chin: 0.15, chinY: -1.12, temple: 0.88, skull: 0.9, plane: 0.84, phil: 0.8, chinZ: 0.74 }),
    view: [0.2, 0.05], body: 'girl', scale: 0.14, skin: '#e9b892', blush: 0.45,
    nose: { top: -0.22, tipY: -0.46, out: 0.07, rTop: 0.02, rTip: 0.045, wing: 0.07, up: 0.02 },
    lips: { y: -0.77, w: 0.12, uh: 0.025, ud: 0.03, lh: 0.035, ld: 0.035, out: -0.015, bow: 0.03 }, smile: 0.05, smirk: 0.3, lip: '#c86a6a',
    eyeX: 0.4, eyeY: -0.16, eyeR: 0.3, eyeH: 0.74, eyeW: 1.1, eyeTilt: 0.06, iris: '#6a46a8', irisA: 0.7, pupilA: 0.32, lash: 0.034, wing: 0.1,
    browY: 0.18, browLen: 0.34, browT: 0.032, browArch: 0.07, browCol: '#5a2a8a',
    hair: '#6a2ec0', hairK: 0.14, hairline: { front: 0.6, side: -0.3, back: -1.1 }, hairBox: [[-1.8, -2.6, -1.8], [1.8, 1.9, 1.8]],
    hair3: [['S', 0.1], ['E', [0, 0.4, -0.2], [1.05, 0.9, 1.05]],
      ['T', [[0.35, 1.15, 0.4], [-0.3, 1.0, 0.95], [-0.82, 0.4, 0.85], [-0.98, -0.5, 0.55], [-0.92, -1.6, 0.35]], [0.22, 0.3, 0.3, 0.26, 0.12]],
      ['T', [[0.6, 0.9, 0.5], [0.95, 0.1, 0.5], [0.95, -1.5, 0.3]], [0.26, 0.28, 0.12]],
      ['T', [[0, 0.3, -0.85], [0, -0.9, -0.95], [0, -1.9, -0.6]], [0.75, 0.62, 0.3]], ['X', [0.05, -0.45, 0.95], [0.66, 0.86, 0.55]]],
    top: '#e8e2f2', bottom: '#9aa0b8', shoes: '#6a2ec0', sleeve: 'none', legs: 'shorts', boots: true,
  };
  // K-pop — young women: a long face, a V-shaped jaw to a small chin, cheekbones; a small straight narrow nose; full lips, singing; almond eyes with a liner wing
  const kp = o => ({
    S: { cbX: 0.48, cbY: -0.3, cbH: 0.02, cbK: 0.08, jawK: 0.08, hollow: 0.5, noseRound: 0.022, tint: 0.55, lipZ: 0.04 },
    ...face({ cheek: 0.74, cheekY: -0.25, jaw: 0.46, jawY: -0.92, chin: 0.12, chinY: -1.3, temple: 0.8, skull: 0.84, plane: 0.78, phil: 0.76, chinZ: 0.7, eyeZ: 0.77 }),
    cheekbones: [{ x: 0.48, y: -0.32, r: 0.2, sink: 0.62, h: 0.7 }],
    body: 'woman', scale: 0.115, skin: '#f2cdb6', blush: 0.4, view: [0.2, 0.25],
    nose: { top: -0.05, tipY: -0.5, out: 0.11, rTop: 0.025, rTip: 0.045, wing: 0.075, bend: -0.005, up: 0.015 },
    lips: { y: -0.86, w: 0.13, uh: 0.032, ud: 0.034, lh: 0.048, ld: 0.044, out: -0.01, bow: 0.035 }, smile: 0.05, open: 0.14, lip: '#d0707a',
    eyeX: 0.35, eyeY: -0.14, eyeR: 0.21, eyeH: 0.56, eyeW: 1.15, eyeTilt: 0.12, lowerH: 0.35, iris: '#3a2620', irisA: 0.68, pupilA: 0.32, lash: 0.032, wing: 0.12, gaze: [0, 0.15],
    browY: 0.14, browLen: 0.37, browT: 0.03, browArch: 0.06, browCol: '#2a1c1a', tilt: [-0.2, 0, 0],
    top: '#f2e6ee', bottom: '#f2e6ee', shoes: '#f6eef2', sleeve: 'long', legs: 'shorts', boots: true, hairK: 0.1, ...o });
  CH.kpopBraid = kp({ hair: '#7a5ac0', hairline: { front: 0.68, side: -0.2, back: -0.9 },
    hair3: [['S', 0.08], ['E', [0, 0.65, -0.25], [0.95, 0.6, 0.95]], ['T', [[0.55, 0.8, 0.55], [0.82, 0.1, 0.62], [0.78, -0.6, 0.5]], [0.08, 0.07, 0.03]], ['X', [0, -0.45, 0.95], [0.7, 0.9, 0.55]]],
    extras: [braid([[0, 0.45, -1.1], [0.02, -0.5, -1.2], [0.05, -1.6, -1.0], [0.1, -2.8, -0.8]], 0.22)] });
  CH.kpopPony = kp({ eyeTilt: 0.08, hair: '#c03a68', hairline: { front: 0.62, side: -0.2, back: -0.9 }, view: [-0.25, 0.25], hairBox: [[-1.8, -3.0, -2.2], [1.8, 2.1, 1.8]],
    hair3: [['S', 0.08], ['E', [0, 0.85, -0.3], [0.92, 0.5, 0.9]], ['E', [0, 1.25, -0.55], [0.22, 0.2, 0.22]],
      ['T', [[0, 1.3, -0.6], [0.05, 1.5, -1.0], [0.15, 0.6, -1.4], [0.25, -0.9, -1.4], [0.4, -2.6, -1.1]], [0.2, 0.28, 0.3, 0.24, 0.06]],
      ['T', [[0.4, 1.0, 0.7], [0.68, 0.35, 0.85], [0.75, -0.4, 0.62]], [0.12, 0.1, 0.03]], ['T', [[-0.4, 1.0, 0.7], [-0.68, 0.35, 0.85], [-0.75, -0.4, 0.62]], [0.12, 0.1, 0.03]], ['X', [0, -0.45, 0.95], [0.7, 0.9, 0.55]]],
    extras: [bun([0, 1.32, -0.62], 0.1, '#e8c060')] });
  CH.kpopBuns = kp({ eyeH: 0.62, eyeTilt: 0.04, hair: '#1a2240', hairline: { front: 0.55, side: -0.2, back: -0.9 }, open: 0.18, smile: 0.07, view: [0.35, 0.25],
    hair3: [['S', 0.08], ['E', [0, 0.45, -0.25], [0.95, 0.85, 0.92]], ['E', [0, 0.66, 0.72], [0.72, 0.24, 0.32]], ['E', [0.45, 0.9, -0.85], [0.32, 0.3, 0.3]], ['E', [-0.45, 0.9, -0.85], [0.32, 0.3, 0.3]],
      ['T', [[0.62, 0.6, 0.6], [0.85, -0.1, 0.62], [0.8, -0.75, 0.5]], [0.1, 0.09, 0.03]], ['T', [[-0.62, 0.6, 0.6], [-0.85, -0.1, 0.62], [-0.8, -0.75, 0.5]], [0.1, 0.09, 0.03]], ['X', [0, -0.48, 0.95], [0.68, 0.84, 0.55]]] });
  // Claire — an oval face with a pointed chin and marked cheekbones; a small turned-up nose; a confident half-smile; tilted almond eyes, brows down at the middle; black spiky hair, a purple streak, a little side tail
  CH.claire = {
    S: { cbX: 0.5, cbY: -0.3, cbH: 0.02, cbK: 0.08, jawK: 0.08, hollow: 0.4, noseRound: 0.022, tint: 0.5 },
    ...face({ cheek: 0.8, cheekY: -0.3, jaw: 0.5, jawY: -0.86, chin: 0.13, chinY: -1.2, temple: 0.84, plane: 0.8, phil: 0.77, chinZ: 0.72 }),
    cheekbones: [{ x: 0.5, y: -0.34, r: 0.2, sink: 0.62, h: 0.7 }],
    view: [-0.35, 0.04], body: 'girl', scale: 0.13, skin: '#f0c4a2', blush: 0.25,
    nose: { top: -0.14, tipY: -0.47, out: 0.09, rTop: 0.024, rTip: 0.048, wing: 0.075, up: 0.02 },
    lips: { y: -0.8, w: 0.12, uh: 0.025, ud: 0.03, lh: 0.035, ld: 0.035, out: -0.015, bow: 0.03 }, smile: 0.05, smirk: 0.6, lip: '#c06a64',
    eyeX: 0.37, eyeY: -0.14, eyeR: 0.25, eyeH: 0.56, eyeW: 1.1, eyeTilt: 0.14, lowerH: 0.5, iris: '#6a3a1a', irisA: 0.66, pupilA: 0.32, lash: 0.03, wing: 0.07, gaze: [0.12, 0],
    browY: 0.1, browLen: 0.36, browT: 0.042, browArch: 0.0, browIn: -0.08, browTilt: 0.06, browCol: '#1a1214',
    hair: '#1b1618', hairK: 0.1, hairline: { front: 0.55, side: -0.2, back: -0.85 },
    hair3: [['S', 0.1], ['E', [0, 0.55, -0.2], [0.98, 0.75, 1.0]],
      ...[[-0.45, 1.1, 0.2], [0.0, 1.2, 0.0], [0.45, 1.1, 0.15], [0.3, 1.0, -0.55], [-0.35, 1.0, -0.55]].map(([x, y, z]) => ['C', [x * 0.7, y - 0.25, z * 0.7], [x * 1.4, y + 0.38, z * 1.2 - 0.25], 0.2, 0.02]),
      ['T', [[-0.2, 1.1, 0.5], [0.25, 0.9, 0.95], [0.62, 0.35, 0.95], [0.78, -0.2, 0.7]], [0.16, 0.2, 0.18, 0.06]],
      ['C', [-0.8, 0.4, -0.45], [-1.45, 0.15, -0.6], 0.2, 0.03], ['C', [-0.85, 0.3, -0.4], [-1.35, -0.25, -0.45], 0.16, 0.02], ['X', [0.05, -0.45, 0.95], [0.7, 0.86, 0.55]]],
    extras: [stripe([[-0.1, 1.15, 0.45], [0.25, 0.98, 0.9], [0.58, 0.5, 1.0], [0.75, -0.05, 0.78]], 0.12, '#7a3eaa')],
    top: '#5a2e78', bottom: '#2a2848', shoes: '#3a3a52', sleeve: 'none', legs: 'long', boots: true,
  };

  // Giulia (Luca) — a round face, wide soft cheeks with freckles, a small rounded chin; a long sharp nose pointing forward
  // and down; a small closed smile; big round brown eyes; thick red brows; curly red hair in big clumps under a blue beanie
  CH.giulia = {
    S: { cbK: 0.22, jawK: 0.2, noseRound: 0.01, tint: 0.25, lipZ: 0.012, sock: 0.6 },
    ...face({ cheek: 0.88, cheekY: -0.42, jaw: 0.62, jawY: -0.82, chin: 0.2, chinY: -1.12, temple: 0.86, skull: 0.88, plane: 0.84, phil: 0.8, chinZ: 0.74 }),
    view: [-0.35, 0.05], body: 'girl', scale: 0.135, skin: '#e9a47c', blush: 0.35, blushAt: [0.5, -0.42, [0.2, 0.12]],
    nose: { top: -0.12, tipY: -0.5, out: 0.3, rTop: 0.035, rTip: 0.05, wing: 0.075 },
    lips: { y: -0.76, w: 0.13, uh: 0.015, ud: 0.02, lh: 0.02, ld: 0.02, out: -0.02, bow: 0.03 }, smile: 0.05, smirk: 0.2, lipT: 0.012, lipLine: '#6a2a20', lip: '#c86a5a',
    eyeX: 0.38, eyeY: -0.12, eyeR: 0.26, eyeH: 0.82, eyeW: 1.12, lowerH: 0.7, iris: '#6a3a1a', irisA: 0.62, pupilA: 0.36, lash: 0.02, gaze: [-0.05, 0.02], lowerLid: false,
    browY: 0.16, browLen: 0.36, browT: 0.055, browArch: 0.05, browIn: 0.04, browCol: '#a8322a',
    hair: '#a8281e', hairK: 0.06, hairline: { front: 0.5, side: -0.3, back: -1.0 }, hairBox: [[-1.9, -2.0, -1.9], [1.9, 2.0, 1.8]],
    hair3: [['S', 0.08],
      // curls in big clumps: round masses down the sides and the back, bulging out at the jaw
      ...[[-0.9, 0.2, 0.25], [-1.0, -0.25, 0.2], [-1.05, -0.65, 0.05], [-0.85, -0.9, -0.3], [0.95, -0.2, 0.15], [1.05, -0.6, 0.0], [0.9, -0.9, -0.3], [-0.5, -0.8, -0.75], [0.5, -0.8, -0.75], [0, -0.75, -0.9], [-0.6, 0.2, -0.85], [0.6, 0.2, -0.85]]
        .map(([x, y, z], i) => ['E', [x, y, z], [0.3 + (i % 3) * 0.03, 0.27, 0.3]]),
      // a high bun of curls on top, peeking out to the left of the beanie
      ['E', [-0.45, 1.12, 0.25], [0.38, 0.32, 0.36]], ['E', [-0.65, 0.9, 0.55], [0.26, 0.24, 0.25]],
      ['X', [0.05, -0.42, 0.95], [0.74, 0.86, 0.55]]],
    extras: [(H) => { const g = new THREE.Group(); const m = new THREE.MeshStandardMaterial({ color: '#2a7fb8', roughness: 0.95 });
      const b = new THREE.Mesh(new THREE.SphereGeometry(1.08, 48, 32, 0, Math.PI * 2, 0, 1.55), m); b.position.set(0.15, 0.32, -0.12); b.rotation.set(-0.35, 0, -0.38); b.scale.set(1.0, 0.95, 1.05); g.add(b);
      const r = new THREE.Mesh(new THREE.TorusGeometry(1.06, 0.1, 12, 48), m); r.position.copy(b.position); r.rotation.set(Math.PI / 2 - 0.35, 0, -0.38); r.position.y -= 0.01; g.add(r);
      // freckles across the nose and cheeks
      const fm = new THREE.MeshBasicMaterial({ color: '#b86848' }); for (let i = 0; i < 26; i++) { const sx = i % 2 ? 1 : -1, a = (i * 0.618) % 1; const f = new THREE.Mesh(new THREE.SphereGeometry(0.012, 6, 4), fm); f.position.set(sx * (0.18 + a * 0.38), -0.32 - ((i * 0.37) % 1) * 0.16, 0.0); f.userData.onSkin = true; g.add(f); }
      return g; }],
    top: 'stripes', stripes: ['#f2e6d8', '#e0603a'], bottom: '#3f8f8a', shoes: '#7a5232', sleeve: 'short', legs: 'wide',
  };
  // Ambrosius (Nimona) — a long narrow face, a long straight nose, a narrow pointed chin, marked cheekbones; worried brows
  // high in the middle; round eyes under heavy lids; light grey-blond hair swept back, a long lock at the side
  CH.ambrosius = {
    S: { cbX: 0.48, cbY: -0.32, cbH: 0.015, cbK: 0.08, jawK: 0.08, hollow: 0.3, faceK: 0.08, noseRound: 0.018, tint: 0.3, lipZ: 0.02 },
    ...face({ cheek: 0.7, cheekY: -0.32, jaw: 0.46, jawY: -1.0, chin: 0.13, chinY: -1.42, temple: 0.78, skull: 0.82, plane: 0.78, phil: 0.76, chinZ: 0.7, eyeZ: 0.76 }),
    view: [0.3, 0.0], body: 'man', scale: 0.11, skin: '#d9a07a', blush: 0.15,
    nose: { top: -0.08, tipY: -0.62, out: 0.3, rTop: 0.035, rTip: 0.055, wing: 0.08 },
    lips: { y: -0.96, w: 0.13, uh: 0.02, ud: 0.025, lh: 0.03, ld: 0.03, out: -0.02, bow: 0.03 }, open: 0.06, smile: -0.02, lip: '#b07060',
    eyeX: 0.33, eyeY: -0.12, eyeR: 0.2, eyeH: 0.62, eyeW: 1.05, lowerH: 0.65, iris: '#2a1c16', irisA: 0.5, pupilA: 0.5, lash: 0.022, gaze: [-0.25, 0.0], lowerLid: true,
    browY: 0.13, browLen: 0.34, browT: 0.04, browArch: 0.02, browIn: 0.08, browTilt: -0.06, browCol: '#5a4a3a',
    hair: '#b8b2a6', hairK: 0.1, hairline: { front: 0.65, side: -0.2, back: -0.9 },
    hair3: [['S', 0.1], ['E', [0, 0.85, -0.2], [0.95, 0.5, 1.0]],
      ...[[-0.5, 1.1, 0.4], [0.0, 1.2, 0.45], [0.45, 1.1, 0.4]].map(([x, y, z]) => ['C', [x * 0.7, y - 0.1, z + 0.1], [x * 1.1, y + 0.18, z - 0.55], 0.2, 0.06]),
      ['T', [[-0.7, 0.6, 0.4], [-0.9, 0.0, 0.45], [-0.95, -0.7, 0.3], [-0.9, -1.3, 0.1]], [0.12, 0.12, 0.09, 0.03]],
      ['X', [0, -0.5, 0.95], [0.68, 0.98, 0.55]]],
    top: '#7a86a6', bottom: '#4a4e5e', shoes: '#2a2a30', sleeve: 'long', legs: 'long',
  };
  // Nimona — a round face, full cheeks, a short round chin; a small upturned nose; a huge wide toothy grin; big round eyes;
  // pink-red hair in tufts, short and spiky, one side shaved
  CH.nimona = {
    S: { cbK: 0.25, jawK: 0.2, noseRound: 0.02, tint: 0.3, lipZ: 0.0, philtrum: 0, sock: 0.6 },
    ...face({ cheek: 0.9, cheekY: -0.45, jaw: 0.68, jawY: -0.82, chin: 0.26, chinY: -1.1, temple: 0.88, skull: 0.9, plane: 0.86, phil: 0.82, chinZ: 0.74 }),
    view: [0.15, 0.08], body: 'girl', scale: 0.135, skin: '#f2bfa0', blush: 0.5,
    nose: { top: -0.24, tipY: -0.44, out: 0.08, rTop: 0.025, rTip: 0.05, wing: 0.075 },
    lips: { y: -0.72, w: 0.3, uh: 0.01, ud: 0.01, lh: 0.01, ld: 0.01, out: -0.02, bow: 0.0 }, smile: 0.1, open: 0.22, lip: '#c06a6a',
    eyeX: 0.4, eyeY: -0.1, eyeR: 0.28, eyeH: 0.86, eyeW: 1.15, lowerH: 0.6, iris: '#3a2418', irisA: 0.56, pupilA: 0.42, lash: 0.028, gaze: [-0.1, 0.0], lowerLid: false,
    browY: 0.2, browLen: 0.32, browT: 0.05, browArch: 0.07, browIn: -0.03, browCol: '#c8483a',
    hair: '#e8604a', hairK: 0.06, hairline: { front: 0.55, side: -0.15, back: -0.8 },
    hair3: [['S', 0.1], ['E', [0.15, 0.7, -0.1], [0.85, 0.55, 0.95]],
      ...[[-0.2, 1.15, 0.5], [0.25, 1.2, 0.4], [0.6, 1.0, 0.45], [-0.55, 1.0, 0.45], [0.0, 1.25, -0.2], [0.55, 1.1, -0.3], [0.85, 0.7, 0.2]].map(([x, y, z], i) => ['C', [x * 0.6, y - 0.25, z * 0.5], [x * 1.25, y + 0.25, z + 0.3 - (i % 2) * 0.2], 0.2, 0.025]),
      ['T', [[0.7, 0.5, 0.5], [0.92, -0.1, 0.55], [0.85, -0.6, 0.45]], [0.14, 0.12, 0.03]],
      // the shaved side: the cap cut back to the skin above the ear
      ['X', [-1.0, 0.2, -0.1], [0.32, 0.6, 0.8]], ['X', [0.0, -0.42, 0.95], [0.78, 0.86, 0.55]]],
    top: '#8a2a2a', bottom: '#4a3a32', shoes: '#3a2a22', sleeve: 'none', legs: 'long', boots: true,
  };
  for (const [k, c] of Object.entries(CH)) {
    const n = c.nose || {}, l = c.lips || {}, chinY = c.front ? Math.min(...c.front.filter(p => p[1] < 0.3 && p[0] < -0.8).map(p => p[0])) + 0.2 : -1.18;
    const p = Object.assign({ noseTop: n.top ?? -0.12, tipY: n.tipY ?? -0.45, tipOut: n.out ?? 0.12, noseW: (n.rTop ?? 0.03) * 1.25, tipR: n.rTip ?? 0.055, wingX: n.wing ?? 0.075,
      mouthY: l.y ?? -0.76, mouthW: (l.w ?? 0.13) * 1.15, up: (l.uh ?? 0.03) * 1.2, lo: (l.lh ?? 0.04) * 1.2, chinY: c.chinY0 ?? chinY }, c.S || {});
    Object.assign(c, sculptFace(c.prof, p, c));
  }
};
