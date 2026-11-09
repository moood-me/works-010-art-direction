"""The style drew Вера only as a portrait and a figure. For the comparisons in the drawing's own views this draws her
turnaround and expression sheet with the style's code as it is (styles/s1-pixar/tools: build.turnaround and
build.expressions with their numbers, cast.vera_person) — into the cache, not into the style's folder.
  python3 drawn.py        → CACHE/drawn/vera-turnaround.png, vera-expressions.png"""
import os, sys, subprocess
from common import STYLE, CACHE
sys.path.insert(0, f'{STYLE}/tools')
import build as SB
from pix import Canvas
from face import expr
from person import draw_person
import char

OUT = f'{CACHE}/drawn'; os.makedirs(OUT, exist_ok=True)


def save(cv, name):
    p = f'{OUT}/{name}.svg'
    open(p, 'w').write(cv.svg())
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                    f'--window-size={cv.w},{cv.h}', f'--screenshot={OUT}/{name}.png', 'file://' + p],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print('drawn', name)


SB.save = save
# her calm face of the portrait (build.PORTRAIT), looking ahead
SB.CALM[char.NAME] = expr(open=0.84, brow_in=-0.15, frown=0.15)
SB.turnaround(char.NAME)
SB.expressions(char.NAME)
