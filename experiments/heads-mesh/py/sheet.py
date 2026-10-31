# python3 py/sheet.py name ref crop(json) keys out — the reference's crop beside the renders o/<name>-<k>.png
import sys, json
from PIL import Image
name, ref, crop, keys, out = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]), sys.argv[4], sys.argv[5]
r = Image.open('/home/user/works-010-art-direction/docs/pictures/references/' + ref).convert('RGB')
if crop: r = r.crop(crop)
H = 640; r = r.resize((int(r.width * H / r.height), H), Image.LANCZOS)
ims = [r] + [Image.open('o/%s-%s.png' % (name, k)) for k in keys]
o = Image.new('RGB', (sum(i.width for i in ims), H), 'white'); x = 0
for im in ims: o.paste(im, (x, 0)); x += im.width
o.save(out)
