"""A row of pictures on one sheet, to look at.  usage: python3 montage.py OUT.png W FILES…"""
import sys
from PIL import Image
ims = [Image.open(f).convert('RGB') for f in sys.argv[3:]]
h = max(i.height for i in ims)
s = Image.new('RGB', (sum(i.width for i in ims), h), 'white')
x = 0
for i in ims:
    s.paste(i, (x, 0)); x += i.width
W = int(sys.argv[2])
if s.width > W:
    s = s.resize((W, s.height * W // s.width))
s.save(sys.argv[1])
