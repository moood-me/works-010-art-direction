"""Lay 3D renders (transparent PNGs) onto the drawing's own backdrop and pass them through the drawing's gouache filter
(styles/s9-midcentury/tools/kit.py: FILTERS, scenery.py) — the same paper, ragged edge, paint density and grain.
compose(out_png, w, h, kind, [(png, x, y), …], gouache=True)"""
import base64, os, subprocess, tempfile
import common
from common import HERE, CACHE
from kit import Doc, g
import scenery


def compose(out, w, h, kind, figs, gouache=True, backdrop=True):
    d = Doc(w, h)
    if backdrop: scenery.backdrop(d, 'tim', kind)
    for png, x, y in figs:
        b64 = base64.b64encode(open(png, 'rb').read()).decode()
        from PIL import Image
        iw, ih = Image.open(png).size
        d.add(g([f'<image href="data:image/png;base64,{b64}" x="{x}" y="{y}" width="{iw}" height="{ih}"/>'], filt='gouache' if gouache else None))
    tmp = tempfile.mkdtemp(dir=CACHE)
    open(f'{tmp}/x.svg', 'w').write(d.svg())
    subprocess.run(['node', f'{HERE}/svg2png.mjs', tmp, f'{w}x{h}', 'x'], check=True)
    os.replace(f'{tmp}/x.png', out); os.remove(f'{tmp}/x.svg'); os.rmdir(tmp)


def compose_many(jobs, w, h, kind, gouache=True):
    """jobs: [(out_png, [(png, x, y), …]), …] — one browser for all (films)"""
    from PIL import Image
    tmp = tempfile.mkdtemp(dir=CACHE); names = []
    for i, (out, figs) in enumerate(jobs):
        d = Doc(w, h); scenery.backdrop(d, 'tim', kind)
        for png, x, y in figs:
            b64 = base64.b64encode(open(png, 'rb').read()).decode(); iw, ih = Image.open(png).size
            d.add(g([f'<image href="data:image/png;base64,{b64}" x="{x}" y="{y}" width="{iw}" height="{ih}"/>'], filt='gouache' if gouache else None))
        open(f'{tmp}/f{i:04d}.svg', 'w').write(d.svg()); names.append(f'f{i:04d}')
    for k in range(0, len(names), 40):
        subprocess.run(['node', f'{HERE}/svg2png.mjs', tmp, f'{w}x{h}'] + names[k:k + 40], check=True)
    for i, (out, _) in enumerate(jobs):
        os.replace(f'{tmp}/f{i:04d}.png', out); os.remove(f'{tmp}/f{i:04d}.svg')
    os.rmdir(tmp)
