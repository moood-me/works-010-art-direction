"""pics/*.png → pics/*.webp (the png is removed). `python3 webp.py [name…]`"""
import os, sys, glob
from PIL import Image
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pics')
for f in ([os.path.join(P, n + '.png') for n in sys.argv[1:]] or glob.glob(os.path.join(P, '*.png'))):
    Image.open(f).convert('RGB').save(f[:-4] + '.webp', quality=88, method=5)
    os.remove(f)
    print('webp', os.path.basename(f)[:-4])
