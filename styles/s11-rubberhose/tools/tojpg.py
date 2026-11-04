"""Turn the rendered sheets into JPEG (the film grain makes PNG heavy): python3 tojpg.py ../pics"""
import sys
import os
import glob
from PIL import Image

for p in glob.glob(os.path.join(sys.argv[1], '*.png')):
    Image.open(p).convert('RGB').save(p[:-4] + '.jpg', quality=86, optimize=True)
    os.remove(p)
