import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from kit import *
import importlib
m = importlib.import_module(sys.argv[1])
dy = int(sys.argv[2]) if len(sys.argv) > 2 else -52
OUT = '/home/user/cache/styles-s2-klaus/try'
d = Doc(1500, 600, Light(-0.85, -0.5, key='#ffc47a', shade='#3a2a5a'))
bg(d, '#2a2640', '#4a3048', glow='#e89a5a', gx=0.2, gy=0.35, gr=0.8)
out = []
for i, (fn, bf) in enumerate((('head_front', 'bust_front'), ('head34', 'bust'), ('head_side', 'bust_side'))):
    out.append(f'<g transform="translate({i*500},0)">')
    out.append(f'<g transform="translate(0,{dy})">'); getattr(m, bf)(d, out); out.append('</g>')
    getattr(m, fn)(d, out, 'calm')
    out.append('</g>')
for s in out: d.add(s)
d.grain(0.12)
p = f'{OUT}/{sys.argv[1]}_turn.svg'; d.save(p); render(p, p.replace('.svg', '.png'), 1500, 600)
