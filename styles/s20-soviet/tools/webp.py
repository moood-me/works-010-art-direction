"""python3 webp.py [dir] — every PNG in ../pics (or dir) → WebP (quality 86), the PNG removed."""
import glob, os, sys
from PIL import Image
d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pics')
for f in sorted(glob.glob(os.path.join(d, '*.png'))):
    Image.open(f).convert('RGB').save(f[:-4] + '.webp', quality=86, method=5)
    os.remove(f)
    print('webp', os.path.basename(f)[:-4])
