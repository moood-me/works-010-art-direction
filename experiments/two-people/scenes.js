// The scenes. Each person's chain was made in the order of cause and effect (notes.md says how): who goes first, what
// of them became the other's constraint. Places are in metres; A stands at the origin facing +z.
export const SCENES = [
  {
    id: 'touch3', label: 'рука на плече',
    about: 'Женщина стоит. Мужчина подходит сзади-слева, близко, и кладёт правую руку ей на правое плечо; она оглядывается через правое плечо, его ладонь остаётся лежать на плече и сползает к его краю.',
    frames: 250,
    people: [
      { id: 'A', name: 'женщина', character: 'woman', chain: ['a-stand', 'a-look'], start: 0, place: { position: [0, 0, 0], heading: 0 } },
      { id: 'B', name: 'мужчина', character: 'man', chain: ['b-touch3', 'b-hold4'], start: 42, place: { position: [0, 0, -4.0], heading: 0 } },
    ],
    // B's palm on the outer top of A's right shoulder (a point of her skin at rest, 2 cm out along its normal, carried
    // by her collarbone); as she looks round it slides out to the shoulder's edge (b-hold4 was made so), away from her
    // chin. The two contacts are the same palm, one after the other.
    contacts: [{ who: 'B', side: 'Right', on: 'A', joint: 'RightShoulder', point: [-0.1625, 1.3196, -0.0155], from: 160, to: 192, ramp: 8 },
      { who: 'B', side: 'Right', on: 'A', joint: 'RightShoulder', point: [-0.1903, 1.2948, 0.0063], from: 200, to: 249, ramp: 8 }],
    // he looks at her: Kimodo, asked to, kept his head tilted back; turned towards her head by 0.6 of the way, 25° at most
    looks: [{ who: 'B', at: 'A', share: 0.6, max: 0.44, from: 130, to: 249, ramp: 15 }],
    camera: { yaw: -1.05, pitch: 0.12, dist: 5.2, target: [0, 0.95, -1.0] },
  },
  {
    id: 'touch', label: 'рука на плече (первая версия)',
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
    id: 'shake', label: 'рукопожатие',
    about: 'Двое идут навстречу друг другу, останавливаются и пожимают руки, потом отпускают. Мужчина сделан первым (Kimodo, без ограничений); женщина — вторым: её ладонь на его ладони в каждом кадре, где он держит руку.',
    frames: 195,
    people: [
      { id: 'P', name: 'мужчина', character: 'man', chain: ['h-p'], start: 0, place: { position: [0, 0, -3.9], heading: 0 } },
      { id: 'Q', name: 'женщина', character: 'woman', chain: ['h-q'], start: 0, place: { position: [-0.47, 0, 3.4], heading: Math.PI } },
    ],
    // her palm on his (his palm's point: scene.js palmRest of his body, on his right hand)
    contacts: [{ who: 'Q', side: 'Right', on: 'P', joint: 'RightHand', point: [-0.5041, 1.0649, 0.2235], from: 100, to: 160, ramp: 8 }],
    camera: { yaw: -1.4, pitch: 0.1, dist: 5.5, target: [-0.3, 0.95, 0] },
  },
  {
    id: 'lead', label: 'ведёт за руку',
    about: 'Мужчина идёт и ведёт женщину за руку. Он сделан первым (Kimodo, без ограничений); она — вторым: её правая ладонь на его левой в четырнадцати кадрах пути, её таз рядом с его.',
    frames: 150,
    people: [
      { id: 'L', name: 'мужчина', character: 'man', chain: ['l-lead2'], start: 0, place: { position: [0, 0, 0], heading: 0 } },
      { id: 'G', name: 'женщина', character: 'woman', chain: ['g-led2'], start: 0, place: { position: [0.62, 0, 0], heading: 0 } },
    ],
    // her right palm on his left palm (his palm's point: scene.js palmRest of his body, on his left hand)
    contacts: [{ who: 'G', side: 'Right', on: 'L', joint: 'LeftHand', point: [0.5041, 1.0649, 0.2235], from: 8, to: 142, ramp: 8 }],
    camera: { yaw: -0.9, pitch: 0.12, dist: 6, target: [0.2, 0.9, 2.5] },
    follow: true,
  },
  {
    id: 'carry3', label: 'поднимает и несёт',
    about: 'Ребёнок стоит и поднимает руки. Мужчина подходит, наклоняется, берёт его под мышки, поднимает к груди, несёт и ставит. Ребёнок обнимает его за шею; пока его несут, он прикреплён к рукам мужчины, а его поза — своё движение Kimodo.',
    frames: 440,
    people: [
      { id: 'C', name: 'ребёнок', character: 'child', chain: ['c-wait', 'c-hug2', 'c-rest2'], start: 0, place: { position: [0, 0, 0], heading: Math.PI } },
      { id: 'M', name: 'мужчина', character: 'man', chain: ['m-lift2', 'm-walk2', 'm-down4'], start: 26, place: { position: [0, 0, -4.0], heading: 0 } },
    ],
    // M's palms on the child's sides under the arms (points of the child's trunk at rest, 2.5 cm out)
    contacts: [
      { who: 'M', side: 'Right', on: 'C', joint: 'Chest', point: [0.1429, 0.8795, 0.025], from: 152, to: 376, ramp: 10 },
      { who: 'M', side: 'Left', on: 'C', joint: 'Chest', point: [-0.1428, 0.8795, 0.025], from: 152, to: 376, ramp: 10 },
      // the child's hands on the top of his shoulders: c-hug2 was made with them there (through the attachment); this
      // brings the last centimetres
      { who: 'C', side: 'Right', on: 'M', joint: 'LeftShoulder', point: [0.103, 1.5019, -0.0537], from: 205, to: 362, ramp: 15 },
      { who: 'C', side: 'Left', on: 'M', joint: 'RightShoulder', point: [-0.1111, 1.4899, -0.0597], from: 205, to: 362, ramp: 15 },
    ],
    carry: { who: 'C', by: 'M', from: 152, to: 376 },
    camera: { yaw: -1.2, pitch: 0.12, dist: 5, target: [0, 0.9, -0.8] },
  },
  {
    id: 'carry2', label: 'поднимает и несёт (вторая версия)',
    about: 'Ребёнок стоит и поднимает руки. Мужчина подходит, наклоняется, берёт его под мышки, поднимает к груди, несёт и ставит. Ребёнок обнимает его за шею; пока его несут, он прикреплён к рукам мужчины, а его поза — своё движение Kimodo.',
    frames: 420,
    people: [
      { id: 'C', name: 'ребёнок', character: 'child', chain: ['c-wait', 'c-hug2', 'c-rest2'], start: 0, place: { position: [0, 0, 0], heading: Math.PI } },
      { id: 'M', name: 'мужчина', character: 'man', chain: ['m-lift2', 'm-walk2', 'm-down3'], start: 26, place: { position: [0, 0, -4.0], heading: 0 } },
    ],
    // M's palms on the child's sides under the arms (points of the child's trunk at rest, 2.5 cm out)
    contacts: [
      { who: 'M', side: 'Right', on: 'C', joint: 'Chest', point: [0.1429, 0.8795, 0.025], from: 152, to: 376, ramp: 10 },
      { who: 'M', side: 'Left', on: 'C', joint: 'Chest', point: [-0.1428, 0.8795, 0.025], from: 152, to: 376, ramp: 10 },
      // the child's hands on the top of his shoulders: c-hug2 was made with them there (through the attachment); this
      // brings the last centimetres
      { who: 'C', side: 'Right', on: 'M', joint: 'LeftShoulder', point: [0.103, 1.5019, -0.0537], from: 205, to: 362, ramp: 15 },
      { who: 'C', side: 'Left', on: 'M', joint: 'RightShoulder', point: [-0.1111, 1.4899, -0.0597], from: 205, to: 362, ramp: 15 },
    ],
    carry: { who: 'C', by: 'M', from: 152, to: 376 },
    camera: { yaw: -1.2, pitch: 0.12, dist: 5, target: [0, 0.9, -0.8] },
  },
  {
    id: 'carry', label: 'поднимает и несёт (первая версия)',
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
