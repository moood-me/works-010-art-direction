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
