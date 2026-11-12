"""The drawing's sheets that the style's page doesn't have for Савелий Петрович — a turnaround and an expression
sheet — made by the style's own code (styles/s8-stopmotion/tools/build.py: turnaround(), expressions()) into the cache,
to compare the 3D with. Nothing in the style's folder is touched. (The style's notes: his turnaround was dropped
because the flat moustache and tufts don't hold in profile — it shows; the comparison says so.)
usage: python3 drawn.py"""
import os, sys
from common import CACHE, STYLE, NAME
from PIL import Image
sys.argv = [sys.argv[0], '-none-']            # the style's build.py reads a name filter from argv; build nothing on import
import importlib.util                         # noqa: E402
_sp = importlib.util.spec_from_file_location('style_build', os.path.join(STYLE, 'tools/build.py'))
SB = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SB)
from sculpt import finish, render

OUT = os.path.join(CACHE, 'drawn'); os.makedirs(OUT, exist_ok=True)
for name, d in (('turn', SB.turnaround(NAME)), ('expr', SB.expressions(NAME))):
    finish(d)
    p = os.path.join(OUT, f'{name}-{NAME}.svg'); d.save(p)
    render(p, p[:-3] + 'png', d.w, d.h)
    Image.open(p[:-3] + 'png').convert('RGB').save(p[:-3] + 'jpg', quality=90)
    print(p[:-3] + 'jpg')
