// Вера in the symbolic style (С6): what is her own in the 3D page — her sheet's colours, her world, her motions, how
// she breathes, looks about and speaks. (The solids and the moods are in ../character.py → data/.)
export const CHAR = {
  id: 'vera', title: 'Вера',
  // the drawing's palette (scenes.py DAWN)
  pal: { top: '#2b3550', hor: '#c7a59a', fog: '#d9bfb4', ground: '#3a3346', rim: '#ffe2c4', warm: '#fff0d0' },
  // one light: a tall lit window standing in the dusk, as on her sheet
  world: { kind: 'window', w: 1.25, h: 2.5, y0: .5, col: '#f4dcc0', glow: '#ffe7c8', glowR: 3.4, glowK: .5, pool: .8, poolR: 1.6, poolCol: '#ffe7c8',
    rimGain: 1.7, hills: .8, shadow: { alpha: .34, fade: .1, floor: .08 } },
  // standing: where the window is, how she is turned, where we look from
  stand: { label: 'стоит у окна', mood: 'folder', lamp: [-1.65, 0, -4.2], heading: -1.3, camYaw: .1 },
  motions: [
    { id: 'walk', label: 'идёт', loop: true, mood: 'plain', lamp: [3.4, 0, -2.0], heading: 1.5708 },
    { id: 'run', label: 'бежит', mood: 'plain', lamp: [3.6, 0, -2.2], heading: 1.5708 },
    { id: 'bow', label: 'кланяется', mood: 'plain' },
  ],
  phrases: ['Так.', 'Это мы уже проходили.', 'Нет, не сходится — пересчитаем.', 'Ладно, завтра.', 'Кто это подписал, хотела бы я знать.'],
  life: {
    breath: [3.6, 1.4], breathDepth: .85,      // even, restrained breaths
    moodOmega: 6.5,                            // she changes her posture briskly, without fuss
    jawDeg: 8,
    // she looks about rarely and briefly: a short turn of the head, mostly to the window's side
    glance: { first: 2.6, hold: [1.1, 1.6], gap: [3.2, 4.5], yaw: [16, 16], nod: [-4, 8], bias: .65 },
  },
};
