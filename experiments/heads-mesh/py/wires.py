import sys; sys.path.insert(0, 'py'); from anny import *
from PIL import Image, ImageDraw
who = sys.argv[1]; bs = base(); at, J = person(who, bs); T = bs['tris']
eL = J[JI['LeftEye']]; hw = wOf(bs, ['Head','HeadEnd','Jaw','LeftEye','RightEye'])
cz, cy, half = 0.03, eL[1]-0.0, 0.13
S = 1200; tp = lambda p: ((p[2]-cz+half)/(2*half)*S, (cy+half-p[1])/(2*half)*S)
P = at[T]; n = np.cross(P[:,1]-P[:,0], P[:,2]-P[:,0]); front = (n[:,0] > 0) & (P.mean(1)[:,0] > 0.0)
im = Image.new('RGB', (S, S), 'white'); d = ImageDraw.Draw(im)
for t in np.where(front)[0]:
    q = [tp(at[v]) for v in T[t]]; d.polygon(q, outline=(0,0,0))
for v in np.unique(T[front]):
    x, y = tp(at[v]); g = int(255*min(1,max(0,(at[v,0]-0.05)/0.03))); d.ellipse([x-2,y-2,x+2,y+2], fill=(g,0,255-g))
im.save('_wires-%s.png' % who)
print('x max head', at[hw>.5,0].max(), 'top', at[hw>.5,1].max()-eL[1], 'back', at[hw>.5,2].min(), 'eyeZ', eL[2])
