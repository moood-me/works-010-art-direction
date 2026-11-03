import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from lib import svg, g
import importlib
mod = importlib.import_module(sys.argv[1]); fn = sys.argv[2]; out = sys.argv[3]
exprs = sys.argv[4].split(',') if len(sys.argv) > 4 else [None]
parts=[]
for i,e in enumerate(exprs):
    body = getattr(mod, fn)(e) if e else getattr(mod, fn)()
    parts.append(g(body, 260 + i*480, 280))
open(out,'w').write(svg(480*len(exprs)+40, 640, ''.join(parts), '#f3e3d3'))
