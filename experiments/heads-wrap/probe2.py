exec(open('probe.py').read().split("print('N'")[0])
used=np.zeros(N,bool); used[tris.ravel()]=True
import re as _re
def w(re_): return np.array([sum(weight[i,k] for k in range(4) if _re.match(re_,JN[joint[i,k]])) for i in range(N)])
wh=w(r'^(Head|HeadEnd|Jaw|LeftEye|RightEye)$'); wj=w(r'^Jaw$')
sel=np.where(used&(np.abs(at[:,0])<0.0015)&(at[:,1]>1.38)&(at[:,1]<1.52)&(at[:,2]>0.06))[0]
for i in sorted(sel,key=lambda i:-at[i,1]): print(i, round(at[i,1],4), round(at[i,2],4), round(wj[i],2), round(wh[i],2))
