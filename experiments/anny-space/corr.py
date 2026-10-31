import numpy as np, torch, anny, pickle
B=open('/home/user/moood/engines/1/bodies/base.bin','rb').read()
N,T=np.frombuffer(B,np.uint32,2,0); off=8
tris=np.frombuffer(B,np.uint16,T*3,off).reshape(-1,3); off+=T*3*2
print('moood',N,T)
m=anny.Anny(phenotypes="all", local_changes="default")
F=m.faces.numpy(); print('anny faces',F.shape, F.max())
# same triangles?
a=set(map(tuple,np.sort(tris,1))); b=set(map(tuple,np.sort(F,1)))
print('common tris',len(a&b), len(a), len(b))
W=open('/home/user/moood/engines/1/bodies/woman.bin','rb').read()
at=np.frombuffer(W,np.int16,N*3,0).reshape(-1,3)/10000.
tv=m.template_vertices.numpy()
print('moood woman bbox',at.min(0),at.max(0)); print('anny tmpl bbox',tv.min(0),tv.max(0))
np.save('moood_woman.npy',at); np.save('moood_tris.npy',tris)
