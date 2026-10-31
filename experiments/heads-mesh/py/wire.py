import sys; sys.path.insert(0, 'py'); from anny import *
from PIL import Image, ImageDraw
who = sys.argv[1]; bs = base(); at, J = person(who, bs); T = bs['tris']
eL = J[JI['LeftEye']]; jw = wOf(bs, ['Jaw'])
cx, cy, half = float(sys.argv[2]) if len(sys.argv)>2 else 0, eL[1]-0.035, float(sys.argv[3]) if len(sys.argv)>3 else 0.08
S = 1400; tp = lambda p: ((p[0]-cx+half)/(2*half)*S, (cy+half-p[1])/(2*half)*S)
P = at[T]; n = np.cross(P[:,1]-P[:,0], P[:,2]-P[:,0]); front = (n[:,2] > 0) & (P.mean(1)[:,2] > 0.05)
im = Image.new('RGB', (S, S), 'white'); d = ImageDraw.Draw(im)
for t in np.where(front)[0]:
    q = [tp(at[v]) for v in T[t]]; d.polygon(q, outline=(0,0,0))
for v in np.unique(T[front]):
    x, y = tp(at[v]); col = (255,0,0) if jw[v] > .5 else (0,0,255); d.ellipse([x-2,y-2,x+2,y+2], fill=col)
im.save('_wire-%s.png' % who)
