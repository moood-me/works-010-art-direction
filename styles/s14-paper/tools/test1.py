from kit import *
import face as F
d = Doc(1500, 700)
specs = [dict(lash=True, eye_w=17, eye_h=15, iris='#5d7f5a'), dict(rx=84, jaw=.8, nose='broad', eye_h=10), dict(rx=72, jaw=.5, chin=.12, eye_h=9, eye_w=13, nose='long')]
for j, sp in enumerate(specs[:2]):
    for i, yaw in enumerate((0, .5, 1)):
        f = F.face(sp, yaw, ['calm','joy','sad'][i] if j==0 else ['laugh','angry','surprise'][i])
        d.add([F.neck(sp, yaw), F.stack(f)], 150 + i*240 + j*740, 180 + 0, 1.0)
for i, ex in enumerate(['calm','joy','laugh','surprise','sad','angry','smirk','tired','grump']):
    f = F.face(specs[2] if i%2 else specs[0], 0, ex)
    d.add([F.stack(f)], 90 + i*165, 520, 0.72)
d.save('test1')
