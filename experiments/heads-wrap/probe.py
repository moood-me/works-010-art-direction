import json,base64,re,numpy as np
def load(n): s=open(f'data/{n}.js').read(); return base64.b64decode(re.search(r'"(.*)"',s).group(1))
m=json.load(open('meta.json')); JN=m['joints']; JI={n:i for i,n in enumerate(JN)}
b=load('base'); o=0
def take(dt,n):
    global o; a=np.frombuffer(b,dt,n,o); o+=a.nbytes; return a
N,T=take('<u4',2); tris=take('<u2',T*3).reshape(-1,3); joint=take('u1',N*4).reshape(-1,4); weight=take('u1',N*4).reshape(-1,4)/255
F=take('<u4',1)[0]; face=take('<u2',F)
p=load('woman'); at=np.frombuffer(p,'<i2',N*3,0).reshape(-1,3)/10000; inv=np.frombuffer(p,'<f4',77*12,(N*3+F*3)*2).reshape(77,3,4)
J=[]
for j in range(77):
    M=np.eye(4); M[:3]=inv[j]; J.append(np.linalg.inv(M)[:3,3])
J=np.array(J)
print('N',N,'T',T,'F',F)
def w(re_):
    return np.array([sum(weight[i,k] for k in range(4) if re.match(re_,JN[joint[i,k]])) for i in range(N)])
we=w(r'^(LeftEye)$'); wj=w(r'^Jaw$'); wh=w(r'^(Head|HeadEnd|Jaw|LeftEye|RightEye)$')
used=np.zeros(N,bool); used[tris.ravel()]=True
print('used',used.sum(),'eyeW>0.5',(we>0.5).sum(),'used&eye',(used&(we>0.5)).sum(),'jaw>0.5',(wj>0.5).sum(),'head',(wh>0.5).sum())
print('LeftEye joint',J[JI['LeftEye']],'Head',J[JI['Head']],'HeadEnd',J[JI['HeadEnd']],'Jaw',J[JI['Jaw']],'Neck2',J[JI['Neck2']])
# boundary edges among used
from collections import Counter
E=Counter()
for t in tris:
    for a,c in ((t[0],t[1]),(t[1],t[2]),(t[2],t[0])): E[tuple(sorted((a,c)))]+=1
bnd=[e for e,c in E.items() if c==1]; print('boundary edges',len(bnd))

np.save('tris.npy',tris)
e=J[JI['LeftEye']]
d=np.linalg.norm(at-e,axis=1)
near=np.where(used&(d<0.02))[0]; print('used near eye',len(near))
unused=np.where(~used)[0]; print('unused y range',at[unused].min(0),at[unused].max(0))
# cluster unused by distance to eyes
print('unused near Leye',(np.linalg.norm(at[unused]-e,axis=1)<0.03).sum())
print('face idx range',face.min(),face.max(), 'face unique',len(np.unique(face)))
fv=np.unique(face); print('face verts used?',used[fv].mean(), 'y',at[fv].min(0),at[fv].max(0))
# front-most points near eye: local surface z
sel=np.where(used&(np.abs(at[:,0]-e[0])<0.006)&(np.abs(at[:,1]-e[1])<0.02))[0]
print(sorted([(round(at[i,1],4),round(at[i,2],4)) for i in sel])[:40])
