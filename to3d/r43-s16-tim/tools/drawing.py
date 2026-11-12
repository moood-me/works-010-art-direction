"""The drawing's own data for the 3D: the palette, the character's sprites (before and after the outline), its
portraits in the dialogue box for every expression, the backdrops of the style's sheets. → web/drawing.json
python3 drawing.py tim"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ST = os.path.join(HERE, '../../../styles/s16-pixel/tools')
sys.path.insert(0, ST); sys.path.insert(0, os.path.join(ST, 'chars'))
import pal
import px
import sheets
import sprite
import portrait as P


BLINK = {'tim': (17, 23, 'b1'), 'anya': (18, 24, 'a0')}     # the eye stamp's corner and the lid's colour


def rows(c):
    return [''.join(k or '..' for k in r) for r in c.g]


def main(name):
    m = sheets.char(name)
    out = {'name': name, 'ramps': pal.RAMPS, 'base': sprite.BASE, 'leg': m.LEG, 'views': {}, 'raw': {}}
    for v, mp in m.VIEWS.items():
        out['views'][v] = rows(sprite.make(mp, m.LEG))            # with the outline, cropped (1 px margin)
        leg = dict(sprite.BASE); leg.update(m.LEG)
        w = max(len(r) for r in mp)
        out['raw'][v] = rows(px.from_ascii([r.ljust(w, '.') for r in mp], leg, pad=0))
    out['portraits'] = {e: rows(P.framed(m.portrait(e))) for e in ['rest'] + sheets.EXPRS}
    # a blink for the portrait: the resting face with the eyes' pixels given back to the skin and a lid line typed
    x, y, lid = BLINK[name]
    c = m.portrait('rest')
    for ex in (x, 2 * P.CX - x - 6):
        for j in range(y, y + 5):
            for i in range(ex, ex + 6):
                if c.g[j][i] and c.g[j][i][0] not in 'sm':
                    c.g[j][i] = 's3'
        c.hline(ex, ex + 5, y + 2, lid)
        c.px(ex if ex == x else ex + 5, y + 1, lid)
    out['portraits']['blink'] = rows(P.framed(c))
    out['backdrop'] = rows(sheets.backdrop(96, 70, 58))
    out['street'] = rows(sheets.street(224, 100, 84))
    json.dump(out, open(os.path.join(HERE, 'web', 'drawing.json'), 'w'), ensure_ascii=False)
    print(name, {v: (len(r[0]) // 2, len(r)) for v, r in out['views'].items()})


if __name__ == '__main__':
    main(sys.argv[1])
