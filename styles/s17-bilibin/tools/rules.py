"""Small diagram sheets for the page's «Правила стиля»: the line, the face, the ornament of cloth, the hands."""
import kit
import parts
from kit import Doc, INK, RED, GOLD, CREAM


def _sheet(w, h, seed=7):
    d = Doc(w, h, seed)
    return d


def line_sheet():
    import pages
    d = _sheet(1200, 520)
    # one even weight for every contour; a thinner one inside; strands of hair tapering
    pages.label(d, 205, 80, 'контур — один вес', 22)
    d.shape([(80, 380), (120, 160), (220, 120), (320, 180), (330, 380)], '#c99a3c')
    pages.label(d, 600, 80, 'внутри — тоньше', 22)
    d.shape([(480, 380), (500, 150), (700, 150), (720, 380)], '#f6f0e2')
    for x in (540, 600, 660):
        d.thin([(x, 170), (x + 6, 270), (x - 4, 370)])
    pages.label(d, 980, 80, 'локон с завитком', 22)
    parts.ribbon(d, [(880, 120), (930, 200), (900, 300), (960, 400)], 40, 12, '#8a4a2a', inner=3, curl=-16,
                 taper0=0.3)
    parts.ribbon(d, [(980, 120), (1040, 220), (1030, 330), (1090, 410)], 32, 10, '#8a4a2a', inner=2, curl=14,
                 taper0=0.3)
    d.frame(0, 0, 1200, 520, width=22)
    return d


def ornament_sheet():
    import pages
    d = _sheet(1200, 640)
    kinds = [('rhomb', RED, CREAM, 'ромбы'), ('cross', RED, CREAM, 'крест-вышивка'), ('teeth', RED, CREAM, 'зубцы'),
             ('wave', '#5d6b3a', CREAM, 'вьюнок'), ('flower', '#5d7a8c', CREAM, 'цветок'),
             ('dots', '#c99a3c', '#5d6b3a', 'горох')]
    for i, (k, ink, gr, name) in enumerate(kinds):
        y = 80 + i * 66
        d.band([(60, y), (560, y)], 34, None, k, ink, ground=gr, n=2)
        pages.label(d, 700, y + 9, name, 24)
    pats = [(d.p_sprig('#e9d9b0', '#9fb06a', 40, 3.6), '#55708a', 'ситец'),
            (d.p_rhombs('#c9b77a', 22, 1.6), '#5d6b3a', 'вязка'),
            (d.p_herring('#a87c2a', 12, 1.2), '#c99a3c', 'ёлочка'),
            (d.p_stripes('#b0402e', 26, 12, 90), '#f2e8d2', 'полоска')]
    for i, (pid, col, name) in enumerate(pats):
        x = 820 + (i % 2) * 180
        y = 70 + (i // 2) * 260
        d.shape([(x, y, 'c'), (x + 150, y, 'c'), (x + 150, y + 190, 'c'), (x, y + 190, 'c')], col, pattern=pid, n=2)
        pages.label(d, x + 75, y + 226, name, 22)
    d.frame(0, 0, 1200, 640, width=22)
    return d


def face_sheet():
    import pages, anya, savely, tim, marat
    d = _sheet(1400, 600)
    for i, (mod, lab) in enumerate(((anya, 'девушка'), (tim, 'мальчик'), (savely, 'старик'), (marat, 'здоровяк'))):
        cx = 190 + i * 340
        with d.clipped([(cx - 165, 40, 'c'), (cx + 165, 40, 'c'), (cx + 165, 490, 'c'), (cx - 165, 490, 'c')], n=2), \
                d.g(cx, 250, 1.15):
            front = {anya: anya.hair_front, tim: tim.hair, savely: savely.fringe, marat: marat.hair}[mod]
            if mod is anya:
                anya.hair_back(d, parts.View(mod.p, 0))
            parts.head(d, mod.p, 0, mod.e_('calm'), under=getattr(mod, 'beard', None), front=front,
                       extra=getattr(mod, 'extra', None) if mod is savely else getattr(mod, 'moustache', None))
        pages.label(d, 190 + i * 340, 545, lab, 26)
    d.frame(0, 0, 1400, 600, width=22)
    return d


def hands_sheet():
    import pages
    d = _sheet(1100, 420)
    names = {'rest': 'висит', 'open': 'раскрыта', 'fist': 'кулак', 'point': 'указывает'}
    for i, pose in enumerate(('rest', 'open', 'fist', 'point')):
        parts.hand(d, 150 + i * 260, 90, 0, 2.0, pose)
        pages.label(d, 150 + i * 260, 360, names[pose], 24)
    d.frame(0, 0, 1100, 420, width=22)
    return d


SHEETS = {'rule-line': line_sheet, 'rule-ornament': ornament_sheet, 'rule-face': face_sheet, 'rule-hands': hands_sheet}
