import sys; sys.path.insert(0,'py')
from trace import render; from target import Head; from chars import CH
import numpy as np; from PIL import Image
H=Head(CH[sys.argv[1]]); cy=float(sys.argv[2]) if len(sys.argv)>2 else -0.35; hf=float(sys.argv[3]) if len(sys.argv)>3 else 0.55
ims=[render(H,a,b,S=320,half=hf,cy=cy) for a,b in [(0,0.05),(0.5,0.05),(-0.6,-0.2),(1.57,0)]]
Image.fromarray(np.concatenate(ims,1)).save('_tn.png')
