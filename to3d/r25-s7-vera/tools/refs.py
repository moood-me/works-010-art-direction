"""The drawing's sheets this page compares with, as PNG in the cache: the turnaround (front, three-quarter, profile)
and the expression sheet. Where the style's page has no such sheet for the character (Вера has only a portrait and a
figure), it is drawn here by the style's own code, unchanged (styles/s7-ghibli/tools/build.py turnaround / expressions)
— into the cache, the style's folder is not touched.   python3 refs.py"""
import os, sys, subprocess
import config
HERE = os.path.dirname(os.path.abspath(__file__))
S7 = os.path.join(HERE, '..', '..', '..', 'styles', 's7-ghibli')
OUT = os.path.join(config.CACHE, 'refs'); os.makedirs(OUT, exist_ok=True)
ENV = dict(os.environ, NODE_PATH='/opt/node-tools/node_modules')
W = config.WHO


def png(svg, out, w, h, scale):
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{ const b = await chromium.launch(); const p = await b.newPage({{ viewport: {{ width: {w}, height: {h} }}, deviceScaleFactor: {scale} }});
await p.goto('file://{os.path.abspath(svg)}'); await p.screenshot({{ path: '{out}' }}); await b.close(); }})();"""
    subprocess.run(['node', '-e', js], check=True, env=ENV)


for name, (w, h, sc) in dict(turn=(1500, 1000, 2), expr=(2000, 620, 1)).items():
    svg = os.path.join(S7, 'svg', f'{name}-{W}.svg')
    if not os.path.exists(svg):
        sys.path.insert(0, os.path.join(S7, 'tools'))
        import build as SB
        d = SB.turnaround(W, calm=True) if name == 'turn' else SB.expressions(W)
        d.grain(0.06)
        svg = os.path.join(OUT, f'{name}-{W}.svg'); d.save(svg)
    png(svg, os.path.join(OUT, f'{name}.png'), w, h, sc)
    print(name, svg)
