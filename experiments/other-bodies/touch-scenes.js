// The scenes: К2's touch3 (a hand on the shoulder, she looks round) repeated on other bodies. Each person's chain was
// made in the order of cause and effect, as К2's notes say: the woman's a-stand and a-look are К2's own (one motion,
// carried onto each body by the engine); the toucher's two motions were ordered here, with the points of *this*
// touched body given to Kimodo. Places are in metres; A stands at the origin facing +z.
const pear = { format: 'engine/character', version: 1, id: 'pear', label: { ru: 'Невысокая женщина', en: 'Short woman' }, body: 'anny-C-pear', look: { skin: '#e3b99c' } };
export const SCENES = [
  {
    id: 'man-short', label: 'высокий мужчина и невысокая женщина',
    about: 'Невысокая женщина (1,49 м) стоит. Мужчина (1,77 м) подходит сзади-слева и кладёт правую руку ей на правое плечо; она оглядывается, его ладонь остаётся на плече и сползает к краю. Сделано по К2 (touch3) как написано: те же точки плеча, но на её теле, пересчитанные в пространство Kimodo мужчины.',
    frames: 250,
    people: [
      { id: 'A', name: 'женщина', character: pear, chain: ['a-stand', 'a-look'], start: 0, place: { position: [0, 0, 0], heading: 0 } },
      { id: 'B', name: 'мужчина', character: 'man', chain: ['m-touch', 'm-hold'], start: 42, place: { position: [0, 0, -4.0], heading: 0 } },
    ],
    // the same two points as К2's (tools/touch/points.mjs), on her body: the outer top of the shoulder, then its edge
    contacts: [{ who: 'B', side: 'Right', on: 'A', joint: 'RightShoulder', point: [-0.1487, 1.2281, -0.0264], from: 160, to: 192, ramp: 8 },
      { who: 'B', side: 'Right', on: 'A', joint: 'RightShoulder', point: [-0.172, 1.2001, -0.0036], from: 200, to: 249, ramp: 8 }],
    looks: [{ who: 'B', at: 'A', share: 0.6, max: 0.44, from: 130, to: 249, ramp: 15 }],
    camera: { yaw: -1.05, pitch: 0.12, dist: 5.2, target: [0, 0.95, -1.0] },
  },
  {
    id: 'child-woman2', label: 'ребёнок и женщина',
    about: 'Женщина (1,59 м) стоит. Ребёнок (1,31 м) подходит сзади-слева и кладёт правую руку ей на правую руку выше локтя — до плеча он не достаёт; она оглядывается, его ладонь остаётся на её руке. Сделано по К2 (touch3); точка — на её руке, ребёнок стоит на 44 см позади точки (первая попытка — на 30 см: он упирался лицом ей в спину).',
    frames: 250,
    people: [
      { id: 'A', name: 'женщина', character: 'woman', chain: ['a-stand', 'a-look'], start: 0, place: { position: [0, 0, 0], heading: 0 } },
      { id: 'B', name: 'ребёнок', character: 'child', chain: ['c-touch2', 'c-hold2'], start: 42, place: { position: [0, 0, -2.8], heading: 0 } },
    ],
    // the back of her right upper arm, 35 % of the way to the elbow (tools/touch/points.mjs armSurface 0.35, 1.2)
    contacts: [{ who: 'B', side: 'Right', on: 'A', joint: 'RightArm', point: [-0.1959, 1.1842, -0.0273], from: 160, to: 249, ramp: 8 }],
    looks: [{ who: 'B', at: 'A', share: 0.6, max: 0.44, from: 130, to: 249, ramp: 15 }],
    camera: { yaw: -1.05, pitch: 0.12, dist: 4.6, target: [0, 0.85, -0.7] },
  },
  {
    id: 'child-woman', label: 'ребёнок и женщина (первая попытка)',
    about: 'Женщина (1,59 м) стоит. Ребёнок (1,31 м) подходит сзади-слева и кладёт правую руку ей на правую руку выше локтя — до плеча он не достаёт; она оглядывается, его ладонь остаётся на её руке. Сделано по К2 (touch3); точка — на её руке, первая попытка: ребёнок стоит слишком близко, упирается лицом ей в спину, левую руку подносит ко рту.',
    frames: 250,
    people: [
      { id: 'A', name: 'женщина', character: 'woman', chain: ['a-stand', 'a-look'], start: 0, place: { position: [0, 0, 0], heading: 0 } },
      { id: 'B', name: 'ребёнок', character: 'child', chain: ['c-touch', 'c-hold'], start: 42, place: { position: [0, 0, -2.8], heading: 0 } },
    ],
    // the back of her right upper arm, 35 % of the way to the elbow (tools/touch/points.mjs armSurface 0.35, 1.2)
    contacts: [{ who: 'B', side: 'Right', on: 'A', joint: 'RightArm', point: [-0.1959, 1.1842, -0.0273], from: 160, to: 249, ramp: 8 }],
    looks: [{ who: 'B', at: 'A', share: 0.6, max: 0.44, from: 130, to: 249, ramp: 15 }],
    camera: { yaw: -1.05, pitch: 0.12, dist: 4.6, target: [0, 0.85, -0.7] },
  },
  // the same ask as m-touch with other seeds (2, 3; m-touch is seed 1): only the coming up and the touch, no hold —
  // how much the result depends on luck
  {
    id: 'man-short-s2', label: 'мужчина и невысокая женщина — seed 2',
    about: 'То же, что «высокий мужчина и невысокая женщина», только подход и касание (до 6,4 с), тот же заказ с другим seed (2): насколько результат зависит от случая.',
    frames: 192,
    people: [
      { id: 'A', name: 'женщина', character: pear, chain: ['a-stand', 'a-look'], start: 0, place: { position: [0, 0, 0], heading: 0 } },
      { id: 'B', name: 'мужчина', character: 'man', chain: ['m-touch-s2'], start: 42, place: { position: [0, 0, -4.0], heading: 0 } },
    ],
    contacts: [{ who: 'B', side: 'Right', on: 'A', joint: 'RightShoulder', point: [-0.1487, 1.2281, -0.0264], from: 160, to: 191, ramp: 8 }],
    looks: [{ who: 'B', at: 'A', share: 0.6, max: 0.44, from: 130, to: 191, ramp: 15 }],
    camera: { yaw: -1.05, pitch: 0.12, dist: 5.2, target: [0, 0.95, -1.0] },
  },
  {
    id: 'man-short-s3', label: 'мужчина и невысокая женщина — seed 3',
    about: 'То же, что «высокий мужчина и невысокая женщина», только подход и касание (до 6,4 с), тот же заказ с другим seed (3): насколько результат зависит от случая.',
    frames: 192,
    people: [
      { id: 'A', name: 'женщина', character: pear, chain: ['a-stand', 'a-look'], start: 0, place: { position: [0, 0, 0], heading: 0 } },
      { id: 'B', name: 'мужчина', character: 'man', chain: ['m-touch-s3'], start: 42, place: { position: [0, 0, -4.0], heading: 0 } },
    ],
    contacts: [{ who: 'B', side: 'Right', on: 'A', joint: 'RightShoulder', point: [-0.1487, 1.2281, -0.0264], from: 160, to: 191, ramp: 8 }],
    looks: [{ who: 'B', at: 'A', share: 0.6, max: 0.44, from: 130, to: 191, ramp: 15 }],
    camera: { yaw: -1.05, pitch: 0.12, dist: 5.2, target: [0, 0.95, -1.0] },
  },
];
