// the characters: each a head from Pavel's references, as a study
export default (CH, { L, braid, bun, band, helmet, stripe }) => {
  // a fan of locks: from roots spread along x at the crown, combed to tips
  const fan = (n, f) => Array.from({ length: n }, (_, i) => f(n === 1 ? 0.5 : i / (n - 1), i));

  // Marco — round face, big round eyes without lashes, a dot nose, an easy smile; short thick dark hair swept up and over
  CH.marco = {
    body: 'boy', scale: 0.13, skin: '#f1c39f', blush: 0.25,
    cranium: [1, 1.0, 1.0], face: [0.82, 0.78, 0.7], faceY: -0.4, chin: [0.34, 0.26, 0.3], chinY: -0.98,
    eyeX: 0.38, eyeY: -0.1, eyeR: 0.269, eyeSink: 0.58, eyeH: 0.896, eyeW: 1.15, lowerH: 0.7, iris: '#4a2a1a', irisA: 0.5, pupilA: 0.45, gaze: [0.25, 0], lash: 0.012,
    noseS: 0.07, noseW: 0.07, noseLen: 0.2, noseY: -0.4, mouthY: -0.74, mouthW: 0.24, smile: 0.06, lipT: 0.016, lip: '#7a3a34',
    browY: 0.16, browLen: 0.36, browT: 0.05, browArch: 0.03, browCol: '#2a1a14',
    hair: '#3a2219', hairT: 0.12, hairline: { front: 0.55, side: -0.2, back: -0.7 }, hairVol: { top: 0.22, back: 0.1 },
    locks: [
      // a thick fringe swept to one side, tips pointing out over the brow
      ...fan(5, (t, i) => L([[-0.35 + t * 0.6, 1.2, 0.1], [-0.3 + t * 0.75, 1.15, 0.65], [-0.15 + t * 0.95, 0.85, 1.0], [-0.35 + t * 1.15, 0.6, 1.08]], 0.3, { t: 0.16, tip: 1.3, root: 1 })),
      // a tuft up at the crown and two over the ears
      L([[-0.1, 1.15, -0.2], [0.05, 1.45, -0.05], [0.25, 1.55, 0.1]], 0.16, { t: 0.1, tip: 0.8, free: true }),
      L([[0.85, 0.75, 0.1], [1.0, 0.3, 0.2], [0.98, -0.05, 0.35]], 0.22, { t: 0.1, tip: 0.9 }), L([[-0.85, 0.75, 0.1], [-1.0, 0.3, 0.2], [-0.98, -0.05, 0.35]], 0.22, { t: 0.1, tip: 0.9 }),
    ],
    top: '#c9353a', bottom: '#2c2b33', shoes: '#3a2f2a', sleeve: 'long', legs: 'long',
  };
  // Gwen — a long narrow face, big blue eyes, a small nose, lips slightly parted; a blond bob swept to one side, shaved on the other
  CH.gwen = {
    body: 'girl', scale: 0.12, skin: '#f3c8aa', blush: 0.3,
    cranium: [0.95, 1.02, 1.0], face: [0.7, 0.85, 0.66], faceY: -0.45, chin: [0.24, 0.24, 0.26], chinY: -1.08, chinZ: 0.3,
    eyeX: 0.36, eyeY: -0.12, eyeR: 0.246, eyeH: 0.694, eyeW: 1.05, eyeTilt: -0.05, iris: '#4a7fb0', irisA: 0.6, pupilA: 0.33, lash: 0.024,
    noseS: 0.075, noseW: 0.065, noseLen: 0.3, noseY: -0.46, mouthY: -0.8, mouthW: 0.2, smile: -0.01, open: 0.05, lip: '#c87a70', lowerLip: true,
    browY: 0.2, browLen: 0.34, browT: 0.03, browArch: 0.04, browIn: 0.04, browCol: '#a07a4a',
    hair: '#e3c37e', hairT: 0.1, hairline: { front: 0.6, side: 0.0, back: -0.95 }, hairVol: { top: 0.1, back: 0.14 },
    locks: [
      // the long side: from a deep part, over the top and down past the cheek, ends flicking out
      ...fan(6, (t, i) => L([[-0.45, 1.12, 0.05 - t * 0.5], [-0.05, 1.2, 0.55 - t * 0.9], [0.55 + t * 0.2, 0.85, 0.85 - t * 1.2], [0.92, 0.2, 0.75 - t * 1.1], [0.98, -0.45, 0.55 - t * 0.9], [1.12, -0.62, 0.45 - t * 0.8]], 0.36, { t: 0.15, tip: 1.2 })),
      // across the forehead to the eye
      ...fan(3, t => L([[-0.4, 1.12, 0.3], [-0.1 + t * 0.2, 1.0, 0.85], [0.2 + t * 0.25, 0.55, 1.08], [0.38 + t * 0.2, 0.1, 1.02]], 0.26, { t: 0.11, tip: 1.3 })),
      // the short side
      L([[-0.5, 1.1, 0.25], [-0.8, 0.85, 0.45], [-0.95, 0.5, 0.45]], 0.24, { t: 0.1 }),
    ],
    hairlineShort: true,
    top: '#f1eee9', bottom: '#2b2730', shoes: '#efe9f2', sleeve: 'long', legs: 'long',
  };
  // Gogo — a round face, big brown eyes, the mouth an "o"; a dark bob with a purple streak, inside a golden helmet
  CH.gogo = {
    body: 'girl', scale: 0.125, skin: '#f0bfa0', blush: 0.6,
    cranium: [1, 0.98, 1.0], face: [0.84, 0.78, 0.7], faceY: -0.42, chin: [0.3, 0.24, 0.28], chinY: -0.98,
    eyeX: 0.39, eyeY: -0.12, eyeR: 0.28, eyeH: 0.806, eyeW: 1.1, iris: '#5a3420', irisA: 0.64, pupilA: 0.35, lash: 0.026, gaze: [0.15, 0.05],
    noseS: 0.08, noseW: 0.08, noseLen: 0.24, noseY: -0.44, mouthY: -0.76, mouthW: 0.1, smile: -0.02, open: 0.1, lip: '#b86870', lowerLip: true,
    browY: 0.24, browLen: 0.3, browT: 0.035, browArch: 0.06, browIn: 0.05, browCol: '#1e1418',
    hair: '#1d171c', hairT: 0.08, hairline: { front: 0.5, side: -0.2, back: -0.9 }, hairVol: { top: 0.04, back: 0.04 },
    locks: [
      ...fan(5, (t, i) => L([[-0.1 + t * 0.2, 1.15, 0.2], [-0.55 + t * 1.1, 0.95, 0.85], [-0.7 + t * 1.4, 0.5 + (i % 2) * 0.05, 1.05]], 0.3, { t: 0.13, tip: 1.2 })),
      ...[1, -1].map(x => L([[x * 0.6, 0.95, 0.4], [x * 0.98, 0.3, 0.6], [x * 0.95, -0.35, 0.65], [x * 0.75, -0.62, 0.72]], 0.32, { t: 0.14, tip: 1.2 })),
    ],
    extras: [stripe([[0.25, 1.1, 0.25], [0.5, 0.92, 0.85], [0.62, 0.5, 1.08]], 0.08, '#6a3e9a'), helmet('#d8b13e')],
    top: '#d6ae3c', bottom: '#2d2b30', shoes: '#c9a23a', gloves: '#d6ae3c', sleeve: 'long', legs: 'long', boots: true,
  };
  // Jack — a narrow chin, a sly open smile, sharp low brows, pale blue eyes; white hair in spikes pointing up and forward
  CH.jack = {
    body: 'boy', scale: 0.12, skin: '#f0d0bc', blush: 0.15,
    cranium: [0.96, 1.0, 1.02], face: [0.72, 0.82, 0.68], faceY: -0.44, chin: [0.22, 0.22, 0.26], chinY: -1.06,
    eyeX: 0.36, eyeY: -0.14, eyeR: 0.224, eyeH: 0.504, eyeW: 1.05, eyeTilt: -0.08, lowerH: 0.5, iris: '#6a96b8', irisA: 0.6, pupilA: 0.3, lash: 0.02, gaze: [0, -0.05],
    noseS: 0.085, noseW: 0.075, noseLen: 0.34, noseY: -0.46, mouthY: -0.8, mouthW: 0.24, smile: 0.06, smirk: 0.5, open: 0.07, lip: '#c08080',
    browY: 0.1, browLen: 0.38, browT: 0.04, browArch: -0.01, browIn: -0.03, browTilt: 0.05, browCol: '#8a7a6a',
    hair: '#ece8e2', hairT: 0.08, lockW: 2.0, hairline: { front: 0.6, side: -0.1, back: -0.75 }, hairVol: { top: 0.1, back: 0.06 },
    locks: [
      ...fan(9, (t, i) => L([[-0.7 + t * 1.4, 0.9, 0.0], [-0.8 + t * 1.6, 1.25, 0.35], [-0.9 + t * 1.8 + (i % 2 ? 0.1 : -0.1), 1.45 + (i % 3) * 0.08, 0.55]], 0.16, { t: 0.08, tip: 0.8, free: true })),
      ...fan(5, (t, i) => L([[-0.4 + t * 0.8, 1.0, 0.4], [-0.5 + t * 1.0, 0.75, 0.9], [-0.6 + t * 1.2 + (i % 2 ? 0.08 : -0.06), 0.42 - (i % 2) * 0.1, 1.08]], 0.15, { t: 0.06, tip: 0.8 })),
      ...fan(5, (t, i) => L([[-0.6 + t * 1.2, 0.9, -0.6], [-0.7 + t * 1.4, 1.1, -0.9], [-0.8 + t * 1.6, 1.0, -1.25]], 0.15, { t: 0.07, tip: 0.8, free: true })),
    ],
    top: '#4a5a8a', bottom: '#6a5a48', shoes: '#f0d0bc', sleeve: 'long', legs: 'long',
  };
  // Ariel — huge eyes low on the face, a tiny nose, small full lips; long red hair in big soft volume
  CH.ariel = {
    body: 'woman', scale: 0.12, skin: '#f6d8c8', blush: 0.4,
    cranium: [1, 1.0, 1.02], face: [0.76, 0.78, 0.66], faceY: -0.45, chin: [0.24, 0.24, 0.26], chinY: -1.04,
    eyeX: 0.37, eyeY: -0.18, eyeR: 0.291, eyeH: 0.806, eyeW: 1.1, eyeTilt: 0.04, iris: '#3a9a8a', irisA: 0.66, pupilA: 0.3, lash: 0.03, wing: 0.08,
    noseS: 0.065, noseW: 0.06, noseLen: 0.24, noseY: -0.5, mouthY: -0.8, mouthW: 0.15, smile: -0.01, open: 0.03, lip: '#d0605e', lowerLip: true,
    browY: 0.18, browLen: 0.32, browT: 0.026, browArch: 0.07, browIn: 0.06, browCol: '#9a3a28',
    hair: '#c8322a', hairT: 0.12, lockW: 2.2, lockT: 2.0, hairline: { front: 0.6, side: -0.3, back: -1.1, part: { x: 0.25, dip: -0.05 } }, hairVol: { top: 0.14, back: 0.12 },
    locks: [
      ...fan(6, t => L([[0.25, 1.15, 0.3], [0.2 - t * 0.6, 1.1, 0.75], [-0.3 - t * 0.6, 0.6, 1.0], [-0.75 - t * 0.35, -0.1, 0.7], [-0.85 - t * 0.3, -1.0, 0.4], [-0.8 - t * 0.2, -1.9, 0.3]], 0.26, { t: 0.11, tip: 1.4 })),
      ...fan(4, t => L([[0.3, 1.15, 0.3], [0.6, 0.9, 0.7], [0.9 + t * 0.1, 0.2, 0.5], [0.95, -0.8, 0.3 - t * 0.2], [0.85, -1.8, 0.2]], 0.26, { t: 0.11, tip: 1.4 })),
      ...fan(7, t => L([[-0.7 + t * 1.4, 1.0, -0.5], [-1.0 + t * 2.0, 0.3, -1.05], [-1.05 + t * 2.1, -0.8, -0.9], [-0.9 + t * 1.8, -2.0, -0.6]], 0.32, { t: 0.13 })),
    ],
    top: '#b9b2d8', bottom: '#b9b2d8', shoes: '#e8d8d0', sleeve: 'none', legs: 'long',
  };
  // the 3D boy — a sly look: one brow up, a lopsided smile; ginger hair swept up and to one side
  CH.boy3d = {
    body: 'boy', scale: 0.13, skin: '#f4cdb2', blush: 0.3,
    cranium: [1, 1.02, 1.0], face: [0.8, 0.8, 0.68], faceY: -0.42, chin: [0.28, 0.26, 0.28], chinY: -1.02,
    eyeX: 0.37, eyeY: -0.12, eyeR: 0.246, eyeH: 0.627, eyeW: 1.08, lowerH: 0.45, iris: '#a87a28', irisA: 0.6, pupilA: 0.3, lash: 0.02,
    noseS: 0.08, noseW: 0.075, noseLen: 0.28, noseY: -0.44, mouthY: -0.78, mouthW: 0.22, smile: 0.04, smirk: 0.8, lip: '#b8706a',
    browY: 0.16, browLen: 0.36, browT: 0.045, browArch: 0.02, browIn: -0.02, browTilt: 0.12, browCol: '#6a3018', smirkBrow: true,
    hair: '#b4522a', hairT: 0.1, lockW: 1.9, lockT: 1.9, hairline: { front: 0.55, side: -0.15, back: -0.75 }, hairVol: { top: 0.18, back: 0.08 },
    locks: [
      ...fan(6, (t, i) => L([[-0.4, 1.05, -0.2], [-0.5 + t * 0.6, 1.3, 0.3], [-0.2 + t * 0.9, 1.25, 0.8], [0.0 + t * 1.0, 0.85, 1.0]], 0.2, { t: 0.09, tip: 1.0 })),
      ...fan(3, t => L([[0.3, 1.2, 0.2], [0.8, 1.0, 0.6], [1.05, 0.55, 0.65 - t * 0.2]], 0.16, { t: 0.07, tip: 0.9 })),
      L([[-0.85, 0.6, 0.3], [-0.98, 0.2, 0.4], [-0.95, -0.15, 0.4]], 0.14, { t: 0.06 }),
    ],
    top: '#24304a', bottom: '#3a3238', shoes: '#2a2422', sleeve: 'long', legs: 'long',
  };
  // the doll — a big head, huge purple eyes with lashes, a small turned-up nose, a smile; long straight purple hair, swept fringe
  CH.doll = {
    body: 'girl', scale: 0.14, skin: '#e9b892', blush: 0.4,
    cranium: [1.02, 1.0, 1.0], face: [0.78, 0.76, 0.66], faceY: -0.44, chin: [0.25, 0.24, 0.26], chinY: -1.0,
    eyeX: 0.38, eyeY: -0.16, eyeR: 0.291, eyeH: 0.739, eyeW: 1.1, eyeTilt: 0.06, iris: '#6a46a8', irisA: 0.66, pupilA: 0.32, lash: 0.032, wing: 0.1,
    noseS: 0.065, noseW: 0.065, noseLen: 0.22, noseY: -0.5, mouthY: -0.8, mouthW: 0.18, smile: 0.05, smirk: 0.3, lip: '#c86a6a',
    browY: 0.18, browLen: 0.34, browT: 0.032, browArch: 0.06, browCol: '#5a2a8a',
    hair: '#6a2ec0', hairT: 0.11, lockW: 2.0, lockT: 1.9, hairline: { front: 0.6, side: -0.3, back: -1.1, part: { x: 0.3, dip: -0.08 } }, hairVol: { top: 0.1, back: 0.08 },
    locks: [
      ...fan(5, t => L([[0.3, 1.15, 0.2], [0.0 - t * 0.5, 1.05, 0.85], [-0.55 - t * 0.35, 0.5, 0.95], [-0.95, -0.3, 0.55], [-0.95, -1.5, 0.3]], 0.28, { t: 0.11 })),
      ...fan(3, t => L([[0.35, 1.15, 0.2], [0.75, 0.85, 0.6], [1.0, 0.0, 0.55 - t * 0.2], [0.9, -1.4, 0.3]], 0.28, { t: 0.11 })),
      ...fan(6, t => L([[-0.7 + t * 1.4, 1.0, -0.5], [-0.95 + t * 1.9, 0.2, -1.0], [-0.95 + t * 1.9, -1.6, -0.7]], 0.3, { t: 0.11 })),
    ],
    top: '#e8e2f2', bottom: '#9aa0b8', shoes: '#6a2ec0', sleeve: 'none', legs: 'shorts', boots: true,
  };
  // K-pop — three young women: a longer face, almond eyes with a liner wing, a defined small chin, singing
  const kp = {
    body: 'woman', scale: 0.115, skin: '#f2cdb6', blush: 0.35,
    cranium: [0.9, 1.0, 0.98], face: [0.66, 0.95, 0.6], faceY: -0.52, chin: [0.2, 0.24, 0.24], chinY: -1.2, chinZ: 0.3, cheekR: 0.24, cheekY: -0.5,
    eyeX: 0.34, eyeY: -0.14, eyeR: 0.2, eyeH: 0.6, eyeW: 1.15, eyeTilt: 0.1, lowerH: 0.35, iris: '#3a2620', irisA: 0.66, pupilA: 0.32, lash: 0.03, wing: 0.11,
    noseS: 0.07, noseW: 0.06, noseLen: 0.32, noseY: -0.5, mouthY: -0.84, mouthW: 0.2, smile: 0.04, open: 0.13, lip: '#d0707a', lowerLip: true,
    browY: 0.15, browLen: 0.36, browT: 0.03, browArch: 0.05, browCol: '#2a1c1a', tilt: [-0.18, 0, 0],
    top: '#f2e6ee', bottom: '#f2e6ee', shoes: '#f6eef2', sleeve: 'long', legs: 'shorts', boots: true,
  };
  CH.kpopBraid = { ...kp, hair: '#7a5ac0', hairT: 0.1, lockW: 2.0, hairline: { front: 0.65, side: -0.2, back: -0.9 }, hairVol: { top: 0.08, back: 0.06 },
    locks: [ ...fan(8, t => L([[-0.7 + t * 1.4, 0.75, 0.75], [-0.6 + t * 1.2, 1.1, 0.2], [-0.3 + t * 0.6, 1.0, -0.6], [0, 0.5, -1.05]], 0.18, { t: 0.06 })) ],
    extras: [braid([[0, 0.45, -1.1], [0.02, -0.5, -1.2], [0.05, -1.6, -1.0], [0.1, -2.8, -0.8]], 0.2)] };
  CH.kpopPony = { ...kp, eyeTilt: 0.06, hair: '#c03a68', hairT: 0.1, lockW: 2.0, hairline: { front: 0.6, side: -0.2, back: -0.9, part: { x: 0.2, dip: -0.05 } }, hairVol: { top: 0.06, back: 0.04 },
    locks: [ ...fan(8, t => L([[-0.75 + t * 1.5, 0.7, 0.75], [-0.6 + t * 1.2, 1.15, 0.0], [0, 1.25, -0.45]], 0.18, { t: 0.06 })),
      L([[0.18, 1.0, 0.3], [0.5, 0.55, 0.9], [0.62, -0.1, 0.85], [0.7, -0.6, 0.6]], 0.13, { t: 0.05 }),
      L([[0, 1.3, -0.5], [0.05, 1.45, -0.9], [0.1, 0.6, -1.3], [0.2, -0.8, -1.3], [0.35, -2.6, -1.0]], 0.36, { t: 0.18, root: 0.6, tip: 1.6, free: true }) ],
    extras: [bun([0, 1.28, -0.55], 0.1, '#e8c060')] };
  CH.kpopBuns = { ...kp, eyeH: 0.65, eyeTilt: 0.03, hair: '#1a2240', hairT: 0.1, lockW: 2.0, hairline: { front: 0.55, side: -0.2, back: -0.9 }, hairVol: { top: 0.06, back: 0.05 }, open: 0.17, smile: 0.06,
    locks: [ ...fan(9, t => L([[-0.5 + t, 1.1, 0.2], [-0.6 + t * 1.2, 0.85, 0.85], [-0.7 + t * 1.4, 0.38, 1.0]], 0.13, { t: 0.05, tip: 1.6 })),
      L([[0.7, 0.6, 0.5], [0.9, 0.0, 0.6], [0.85, -0.7, 0.5]], 0.12, { t: 0.04 }), L([[-0.7, 0.6, 0.5], [-0.9, 0.0, 0.6], [-0.85, -0.7, 0.5]], 0.12, { t: 0.04 }) ],
    extras: [bun([0.45, 0.85, -0.85], 0.28), bun([-0.45, 0.85, -0.85], 0.28)] };
  // Claire — determined: brows down at the middle, a confident half-smile; black spiky hair with a purple streak, a little side tail
  CH.claire = {
    body: 'girl', scale: 0.13, skin: '#f0c4a2', blush: 0.25,
    cranium: [1, 1.0, 1.0], face: [0.76, 0.8, 0.66], faceY: -0.44, chin: [0.24, 0.24, 0.26], chinY: -1.03,
    eyeX: 0.37, eyeY: -0.14, eyeR: 0.258, eyeH: 0.56, eyeW: 1.1, eyeTilt: 0.12, lowerH: 0.5, iris: '#6a3a1a', irisA: 0.64, pupilA: 0.32, lash: 0.03, wing: 0.06, gaze: [0.1, 0],
    noseS: 0.07, noseW: 0.065, noseLen: 0.26, noseY: -0.48, mouthY: -0.8, mouthW: 0.18, smile: 0.04, smirk: 0.5, lip: '#c06a64',
    browY: 0.12, browLen: 0.34, browT: 0.04, browArch: 0.0, browIn: -0.07, browTilt: 0.06, browCol: '#1a1214',
    hair: '#1b1618', hairT: 0.09, hairline: { front: 0.55, side: -0.2, back: -0.85 }, hairVol: { top: 0.12, back: 0.08 },
    locks: [
      // big spiky locks swept up and back, like horns of hair
      ...fan(4, (t, i) => L([[-0.5 + t, 1.0, 0.35], [-0.6 + t * 1.2, 1.35, 0.0], [-0.75 + t * 1.5, 1.5 + (i % 2) * 0.1, -0.45]], 0.26, { t: 0.12, tip: 0.6, free: true })),
      ...fan(4, t => L([[-0.2, 1.1, 0.3], [0.1 + t * 0.3, 0.95, 0.85], [0.5 + t * 0.45, 0.4, 0.95], [0.7 + t * 0.3, -0.15, 0.7]], 0.2, { t: 0.08, tip: 1.0 })),
      L([[-0.8, 0.5, -0.5], [-1.15, 0.3, -0.7], [-1.45, 0.15, -0.6]], 0.2, { t: 0.1, tip: 0.8, free: true }),
      L([[-0.9, 0.5, -0.4], [-1.2, 0.0, -0.55], [-1.4, -0.2, -0.4]], 0.18, { t: 0.08, tip: 0.8, free: true }),
    ],
    extras: [stripe([[-0.1, 1.15, 0.2], [0.2, 1.0, 0.8], [0.55, 0.55, 1.0], [0.75, 0.0, 0.8]], 0.12, '#7a3eaa')],
    top: '#5a2e78', bottom: '#2a2848', shoes: '#3a3a52', sleeve: 'none', legs: 'long', boots: true,
  };
};
