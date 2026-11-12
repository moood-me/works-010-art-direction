"""The cast: a module per character. Each has HEAD (the numbers of the face), HAIR, EXTRAS (glasses, beard...),
and the body (see body.py) as FIGURE(s) and BUST."""
from . import anya, sav, tim, vera, marat, kira
CAST = dict(anya=anya, sav=sav, tim=tim, vera=vera, marat=marat, kira=kira)
NAMES = dict(anya='Аня', sav='Савелий Петрович', tim='Тим', vera='Вера', marat='Марат', kira='Кира')
ORDER4 = ['anya', 'sav', 'tim', 'vera']
ORDER6 = ORDER4 + ['marat', 'kira']
