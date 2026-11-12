// The scenes. Each person's chain was made in the order of cause and effect (notes.md says how): who goes first, what
// of them became the other's constraint. Places are in metres; A stands at the origin facing +z.
export const SCENES = [
  {
    id: 'touch', label: 'рука на плече',
    about: 'Женщина стоит. Мужчина подходит сзади и кладёт правую руку ей на плечо; она оглядывается через правое плечо, рука остаётся на плече.',
    frames: 250,
    people: [
      { id: 'A', name: 'женщина', character: 'woman', chain: ['a-stand', 'a-look'], start: 0, place: { position: [0, 0, 0], heading: 0 } },
      { id: 'B', name: 'мужчина', character: 'man', chain: ['b-touch', 'b-hold'], start: 42, place: { position: [0, 0, -4.0], heading: 0 } },
    ],
    // B's palm on the top of A's right shoulder, at the back (a point of A's skin at rest, 1.5 cm out from it along the skin's normal, carried by her collarbone)
    contacts: [{ who: 'B', side: 'Right', on: 'A', joint: 'RightShoulder', point: [-0.1394, 1.3335, -0.020], turnWith: 1.4, from: 160, to: 249, ramp: 8 }],
    camera: { yaw: -1.05, pitch: 0.12, dist: 5.2, target: [0, 0.95, -1.0] },
  },
  {
    id: 'carry', label: 'поднимает и несёт',
    about: 'Ребёнок стоит и поднимает руки. Мужчина подходит, наклоняется, берёт его под мышки, поднимает, несёт и ставит. Пока его несут, ребёнок прикреплён к рукам мужчины; его поза — своё движение Kimodo (обнимает за шею, потом отпускает).',
    frames: 420,
    people: [
      { id: 'C', name: 'ребёнок', character: 'child', chain: ['c-wait', 'c-held', 'c-rest'], start: 0, place: { position: [0, 0, 0], heading: Math.PI } },
      { id: 'M', name: 'мужчина', character: 'man', chain: ['m-lift', 'm-walk', 'm-down'], start: 26, place: { position: [0, 0, -4.0], heading: 0 } },
    ],
    // M's palms on the child's sides under the arms (points of the child's trunk at rest, 2.5 cm out)
    contacts: [
      { who: 'M', side: 'Right', on: 'C', joint: 'Chest', point: [0.1429, 0.8795, 0.025], from: 152, to: 376, ramp: 10 },
      { who: 'M', side: 'Left', on: 'C', joint: 'Chest', point: [-0.1428, 0.8795, 0.025], from: 152, to: 376, ramp: 10 },
    ],
    carry: { who: 'C', by: 'M', from: 152, to: 376 },
    camera: { yaw: -1.2, pitch: 0.12, dist: 5, target: [0, 0.9, -0.8] },
  },
];
