import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from kit import *
import importlib
m = importlib.import_module(sys.argv[1])
OUT = '/home/user/cache/styles-s2-klaus/try'
d = Doc(500, 600, Light(-0.85, -0.5, key='#ffc47a', shade='#3a2a5a'))
bg(d, '#2a2640', '#4a3048', glow='#e89a5a', gx=0.15, gy=0.35, gr=0.65)
out = []
dy = int(sys.argv[3]) if len(sys.argv) > 3 else -52
out.append(f'<g transform="translate(0,{dy})">'); m.bust(d, out); out.append('</g>')
m.head34(d, out, sys.argv[2] if len(sys.argv) > 2 else 'calm')
for s in out: d.add(s)
d.grain(0.12)
p = f'{OUT}/{sys.argv[1]}_bust.svg'; d.save(p); render(p, p.replace('.svg', '.png'), 500, 600)
