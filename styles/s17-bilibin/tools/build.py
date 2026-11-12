"""Build every picture: python3 tools/build.py [filter] — SVG into svg/, JPEG into pics/ (one headless Chromium)."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import pages  # noqa: E402
import anya, savely, tim, vera, marat, kira  # noqa: E402
import rules  # noqa: E402

CAST = [('anya', anya), ('savely', savely), ('tim', tim), ('vera', vera), ('marat', marat), ('kira', kira)]
E = ['joy', 'surprise', 'sadness', 'anger']
E_RU = ['радость', 'удивление', 'грусть', 'злость']


def sheets():
    out = {}
    for i, (key, mod) in enumerate(CAST):
        out['portrait-' + key] = (lambda mod=mod, i=i: pages.portrait(mod, seed=10 + i), 1.0)
        out['figure-' + key] = (lambda mod=mod, i=i: pages.figure(mod, seed=20 + i), 1.0)
    for key, mod, yaws in (('anya', anya, (0, 35, 90)), ('vera', vera, (0, 35, 90)), ('kira', kira, (0, 35, 90))):
        out['turn-' + key] = (lambda mod=mod, yaws=yaws: pages.row(
            [(mod, dict(yaw=y)) for y in yaws], ['анфас', 'три четверти', 'профиль'], scale=0.95), 0.8)
    for key, mod in (('tim', tim), ('marat', marat)):
        out['expr-' + key] = (lambda mod=mod: pages.row(
            [(mod, dict(e=mod.e_(n))) for n in E], E_RU, scale=0.95), 0.75)
    out['cast'] = (lambda: pages.group([savely, anya, tim, vera], w=2000, h=1200, scale=0.66,
                                       xs=[330, 760, 1170, 1600]), 0.8)
    out['cast6'] = (lambda: pages.group([kira, vera, anya, marat, tim, savely], w=2800, h=1250, scale=0.64,
                                        xs=[300, 700, 1100, 1530, 1980, 2400]), 0.7)
    for name, fn in rules.SHEETS.items():
        out[name] = (fn, 1.0)
    return out


def main():
    flt = sys.argv[1] if len(sys.argv) > 1 else ''
    jobs = []
    for name, (fn, k) in sheets().items():
        if flt and flt not in name:
            continue
        svg = os.path.join(ROOT, 'svg', name + '.svg')
        with open(svg, 'w') as f:
            f.write(fn().svg())
        jobs += [svg, os.path.join(ROOT, 'pics', name + '.jpg'), str(k)]
        print(name)
    subprocess.run(['node', os.path.join(HERE, 'render.js')] + jobs, check=True)


if __name__ == '__main__':
    main()
