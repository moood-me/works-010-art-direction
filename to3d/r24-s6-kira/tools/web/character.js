// Кира in the symbolic style (С6): what is her own in the 3D page — her sheet's colours, her world, her motions, how
// she breathes, looks about and speaks. (The solids and the moods are in ../character.py → data/.)
export const CHAR = {
  id: 'kira', title: 'Кира',
  // the drawing's palette (scenes_more.py PLUM)
  pal: { top: '#15111d', hor: '#49395c', fog: '#5f4d74', ground: '#19141f', rim: '#b8a9d8', warm: '#d2ee3c' },
  // one light: the far blocks of the town and its glow — the light she has turned her back on (her sheet)
  world: { kind: 'town', span: 44, block: '#2a2238', lit: '#f2c88e', glow: '#8f7fb4', glowR: 24, glowK: .6, glowY: 7, lightY: 16, pool: 0,
    rimGain: 19, hills: .7, shadow: { alpha: .3, fade: .5, floor: .3 } },
  stand: { label: 'стоит спиной к городу', mood: 'slouch', lamp: [-9, 0, -60], heading: .95, camYaw: .05 },
  motions: [
    { id: 'walk', label: 'идёт', loop: true, mood: 'plain', heading: 1.5708 },
    { id: 'sneak', label: 'крадётся', loop: true, mood: 'loose', heading: 1.5708 },
    { id: 'dance', label: 'танцует', mood: 'music' },
  ],
  phrases: ['Отстаньте.', 'Ну и что.', 'Мне всё равно.', 'Ладно… ладно.', 'Не трогайте меня.'],
  life: {
    breath: [2.9, 1.3], breathDepth: 1,
    moodOmega: 8,                              // fifteen: the posture changes at once
    jawDeg: 8,
    // she looks sideways from under the brows, quickly, and looks away again
    glance: { first: 1.8, hold: [.7, 1.2], gap: [2.4, 3.6], yaw: [22, 20], nod: [-2, 6], bias: .35 },
  },
};
