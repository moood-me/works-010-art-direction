from kit import *
import sys, importlib
m = importlib.import_module(sys.argv[1])
d = Doc(1700, 760, '#dfe6da')
for i, yaw in enumerate((0, .5, 1)):
    d.add(m.bust(yaw), 170 + i*330, 200, 1.0)
d.add(mirror(m.bust(.5, 'joy')), 1140, 200, 1.0)
d.add(m.figure(), 1480, 720, 1.2)
for i, ex in enumerate(['joy','surprise','sad','angry']):
    d.add(m.bust(0, ex), 120 + i*230, 560, 0.62)
d.save('t_' + sys.argv[1])
