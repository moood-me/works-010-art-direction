"""Expressions made with the characters' own face controls (bone moves the animators use)."""
def LR(b, x=0, y=0, z=0, mirror_x=True):
    return {b + '.L': {'loc': [x, y, z]}, b + '.R': {'loc': [-x if mirror_x else x, y, z]}}
def M(*ds):
    r = {}
    for d in ds: r.update(d)
    return r
RAIN = {
  'neutral': {},
  'smile': M(LR('ACT-Lips_Corner', 0, 0.022, 0.012, False), LR('ACT-Cheek_Outer', 0, 0.02, 0), LR('ACT-Eyelid_Lower', 0, 0.012, 0), LR('MSTR-Eyebrow', 0, 0.006, 0)),
  'surprise': M({'MSTR-Jaw': {'rot': [14, 0, 0]}}, LR('MSTR-Eyebrow', 0, 0.03, 0), LR('ACT-Eyelid_Upper', 0, 0.015, 0), LR('ACT-Lips_Corner', 0, 0, -0.008, False)),
  'blink': M(LR('ACT-Eyelid_Upper', 0, -0.04, 0)),
  'anger': M(LR('MSTR-Eyebrow', -0.012, -0.025, 0), LR('ACT-Sneer', 0, 0.012, 0), LR('ACT-Lips_Corner', 0, -0.012, -0.005, False), LR('ACT-Eyelid_Upper', 0, -0.008, 0), LR('ACT-Eyelid_Lower', 0, 0.01, 0)),
}
SNOW = {
  'neutral': {},
  'smile': M(LR('ACT-Lips_Corner', -0.015, 0.026, 0), LR('CheekRaiser', 0, 0.02, 0), LR('CenterCheekRaiser', 0, 0.012, 0), LR('MSTR-Eyelid_Lower', 0, 0.006, 0), LR('MSTR-Eyebrow', 0, 0.005, 0)),
  'surprise': M({'Jaw': {'rot': [14, 0, 0]}}, LR('MSTR-Eyebrow', 0, 0.03, 0), LR('MSTR-Eyelid_Upper', 0, 0.008, 0), LR('ACT-Lips_Corner', 0.006, 0, 0)),
  'blink': M(LR('MSTR-Eyelid_Upper', 0, -0.024, 0)),
  'anger': M(LR('MSTR-Eyebrow', -0.012, -0.025, 0), LR('ACT-Lips_Corner', 0, -0.012, 0), LR('MSTR-Eyelid_Upper', 0, -0.005, 0), LR('MSTR-Eyelid_Lower', 0, 0.006, 0)),
}

# more expressions, for the range of the rigs
RAIN.update({
  'sad': M(LR('MSTR-Eyebrow', -0.008, 0.02, 0), LR('ACT-Lips_Corner', 0, -0.015, 0, False), LR('ACT-Eyelid_Upper', 0, -0.01, 0)),
  'disgust': M({'ACT-Sneer.L': {'loc': [0, 0.02, 0]}, 'ACT-Lips_Corner.L': {'loc': [0, 0.012, 0]}, 'MSTR-Eyebrow.L': {'loc': [0, -0.02, 0]}, 'ACT-Eyelid_Lower.L': {'loc': [0, 0.012, 0]}}),
  'puff': M(LR('SK-Cheek_Puff', 0, 0.02, 0), LR('MSTR-Eyebrow', 0, 0.01, 0)),
  'wink': M({'ACT-Eyelid_Upper.L': {'loc': [0, -0.04, 0]}, 'ACT-Lips_Corner.L': {'loc': [0, 0.02, 0.008]}, 'ACT-Cheek_Outer.L': {'loc': [0, 0.02, 0]}}),
  'oo': M({'MSTR-Jaw': {'rot': [9, 0, 0]}}, LR('ACT-Lips_Corner', 0.015, 0, -0.01, False), {'SK-Lip_Puff_Upper': {'loc': [0, 0.008, 0]}, 'SK-Lip_Puff_Lower': {'loc': [0, 0.008, 0]}}),
})
SNOW.update({
  'sad': M(LR('MSTR-Eyebrow', -0.012, 0.02, 0), LR('ACT-Lips_Corner', 0, -0.015, 0), LR('MSTR-Eyelid_Upper', 0, -0.006, 0)),
  'disgust': M({'ACT-Lips_Corner.L': {'loc': [0, 0.012, 0]}, 'MSTR-Eyebrow.L': {'loc': [0, -0.02, 0]}, 'CheekRaiser.L': {'loc': [0, 0.02, 0]}}),
  'puff': M({'ACT-CheekPuff.L': {'loc': [0, 0, -0.02]}, 'ACT-CheekPuff.R': {'loc': [0, 0, -0.02]}}),
  'wink': M({'MSTR-Eyelid_Upper.L': {'loc': [0, -0.024, 0]}, 'CheekRaiser.L': {'loc': [0, 0.015, 0]}, 'ACT-Lips_Corner.L': {'loc': [-0.01, 0.02, 0]}}),
  'oo': M({'Jaw': {'rot': [9, 0, 0]}}, LR('ACT-Lips_Corner', 0.012, 0, 0)),
})
