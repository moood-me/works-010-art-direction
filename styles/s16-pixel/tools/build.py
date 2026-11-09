"""Build the pictures of С16: python3 tools/build.py [name ...]  ->  svg/<name>.svg and pics/<name>.png"""
import os
import subprocess
import sys

import sheets

ROOT = os.path.dirname(sheets.HERE)


def main(names):
    args = []
    for n in names or list(sheets.PICS):
        fn, *a = sheets.PICS[n]
        c, scale = fn(*a)
        svg = os.path.join(ROOT, 'svg', n + '.svg')
        open(svg, 'w').write(c.svg(scale))
        args += [svg, os.path.join(ROOT, 'pics', n + '.png')]
    subprocess.run(['node', os.path.join(sheets.HERE, 'render.js')] + args, check=True)


if __name__ == '__main__':
    main(sys.argv[1:])
