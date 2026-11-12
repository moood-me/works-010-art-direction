// The scenes. Each person's chain was made in the order of cause and effect (notes.md says how): who goes first, what
// of them became the other's constraint. Places are in metres; A stands at the origin facing +z.
export const SCENES = [
  {
    id: 'touch', label: 'рука на плече',
    about: 'Женщина стоит. Мужчина подходит сзади и кладёт правую руку ей на плечо; она оглядывается через правое плечо, рука остаётся на плече.',
    frames: 250,
    people: [
      { id: 'A', character: 'woman', chain: ['a-stand', 'a-look'], start: 0, place: { position: [0, 0, 0], heading: 0 } },
      { id: 'B', character: 'man', chain: ['b-touch', 'b-hold'], start: 42, place: { position: [0, 0, -4.0], heading: 0 } },
    ],
    // B's palm on the top of A's right shoulder, at the back (a point of A's skin at rest, 1.5 cm out from it along the skin's normal, carried by her collarbone)
    contacts: [{ who: 'B', side: 'Right', on: 'A', joint: 'RightShoulder', point: [-0.1394, 1.3335, -0.020], turnWith: 1.4, from: 160, to: 249, ramp: 8 }],
    camera: { yaw: -1.05, pitch: 0.12, dist: 5.2, target: [0, 0.95, -1.0] },
  },
];
