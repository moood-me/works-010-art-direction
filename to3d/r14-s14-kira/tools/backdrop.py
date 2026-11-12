"""The drawing's own sheets without the figure (styles/s14-paper/tools: kit.Doc, scenery — the torn mat, the floor
strip, the paper's grain), as PNG in the cache: python3 backdrop.py → figure (800×1000), portrait (800×960),
film (640×720), wide (1470×720: the turnaround's plain sheet), expr (1600×560)."""
import subprocess
from common import CACHE, HERE
from kit import Doc, lite, dark
import scenery as S

BG = '#d5d9c4'      # Кира's sheet (styles/s14-paper/tools/build.py: BG)


def sheet(w, h, mat=True, floor=None, bg=BG):
    d = Doc(w, h, bg)
    if mat: d.add(S.mat(w, h, lite(BG, 0.55)))
    if floor: d.add(S.floor(w, h, floor, dark(BG, 0.10)))
    return d.svg()


if __name__ == '__main__':
    for name, (w, h, mat, fl) in dict(figure=(800, 1000, True, 880), portrait=(800, 960, True, None), film=(640, 720, False, None),
                                      wide=(1470, 720, False, None), expr=(1600, 560, False, None), close=(640, 640, True, None)).items():
        open(f'{CACHE}/bd-{name}.svg', 'w').write(sheet(w, h, mat, fl, lite(BG, 0.4) if name == 'film' else BG))
        subprocess.run(['node', f'{HERE}/svg2png.mjs', CACHE, f'{w}x{h}', f'bd-{name}'], check=True)
