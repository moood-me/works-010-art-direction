import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from kit import *
import importlib
m = importlib.import_module(sys.argv[1])
OUT = '/home/user/cache/styles-s2-klaus/try'
d = Doc(500, 900, Light(-0.85, -0.5, key='#ffc47a', shade='#3a2a5a'))
bg(d, '#2a2640', '#4a3048', glow='#e89a5a', gx=0.15, gy=0.3, gr=0.7)
out = []
m.figure(d, out)
for s in out: d.add(s)
d.grain(0.12)
p = f'{OUT}/{sys.argv[1]}_fig.svg'; d.save(p); render(p, p.replace('.svg', '.png'), 500, 900)
