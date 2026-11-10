"""The drawing's own views of the character, made by the style's code (styles/s14-paper/tools) without the sheet's mat:
python3 drawing.py → /home/user/cache/to3d-<folder>/drawing/*.png — the figure, the busts (front, three-quarter and
profile where the style has one), the expressions. character.py says who."""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import character as C
STYLE = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'styles', 's14-paper', 'tools'))
sys.path.insert(0, STYLE)
import kit, importlib   # noqa: E402
M = importlib.import_module(C.WHO)
OUT = os.path.join('/home/user/cache/to3d-' + C.FOLDER, 'drawing')
os.makedirs(OUT, exist_ok=True)


def save(doc, name):
    open(os.path.join(OUT, name + '.svg'), 'w').write(doc.svg())


def main():
    # the figure: feet at (400, 880), FIG_S pixels a unit
    d = kit.Doc(800, 1000, C.SHEET)
    f = M.figure()
    d.add(kit.mirror(f) if C.MIRROR else f, 400, 880, C.FIG_S)
    save(d, 'figure')
    for yaw, name in C.BUSTS:
        d = kit.Doc(800, 960, C.SHEET)
        b = M.bust(yaw)
        d.add(kit.mirror(b) if C.MIRROR and yaw else b, 400, 440, C.BUST_S)
        save(d, 'bust-' + name)
    for ex in C.EXPRS:
        d = kit.Doc(560, 620, C.SHEET)
        d.add(M.bust(0, None if ex == 'calm' else ex), 280, 300, C.EXPR_S)
        save(d, 'expr-' + ex)
    subprocess.run(['node', os.path.join(HERE, 'svg2png.mjs'), OUT], check=True)


if __name__ == '__main__':
    main()
