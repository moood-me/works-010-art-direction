import json, base64, struct, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot
b=open('/home/user/moood/engines/1/soma.bin','rb').read()
V,F,n=struct.unpack('<3I',b[:12]); at=12+V*12+F*6+V*16
I=np.frombuffer(b[at:at+n*48],dtype='<f4').reshape(n,3,4).copy(); at+=n*48
par=np.frombuffer(b[at:at+n],dtype=np.uint8).astype(int)
RB=np.array([I[j][:,:3].T for j in range(n)])      # bind turn (joint frame at rest -> space)
REST=np.array([-(I[j][:,:3].T@I[j][:,3]) for j in range(n)])
def load(path):
    d=json.load(open(path)); N=d['n']
    q=np.frombuffer(base64.b64decode(d['q']),dtype='<i2').reshape(N,77,4)/32767.0
    p=np.frombuffer(base64.b64decode(d['p']),dtype='<i2').reshape(N,77,3)
    return d,q,p
OURS=['Hips','Spine1','Spine2','Chest','Neck1','Neck2','Head','HeadEnd','Jaw','LeftEye','RightEye']+[s+b for s in ['Left','Right'] for b in ['Shoulder','Arm','ForeArm','Hand','Leg','Shin','Foot','ToeBase','ToeEnd']]
def convert(path,out):
    d,q,p=load(path); names=d['names']; A={nm:i for i,nm in enumerate(names)}; N=d['n']
    D={}
    for nm in OURS:
        j=A[nm]; R=Rot.from_quat(q[:,j]).as_matrix()
        Dm=R@RB[j].T
        D[nm]=[round(float(x),5) for x in Rot.from_matrix(Dm).as_quat().reshape(-1)]
    feet=[A[s+b] for s in ['Left','Right'] for b in ['Foot','ToeBase','ToeEnd']]
    restMin=min(REST[j][1] for j in feet)
    foot=[round(float(p[f,feet,1].min()/1000-restMin),4) for f in range(N)]
    rest={nm:[round(float(x),4) for x in REST[A[nm]]] for nm in OURS+['LeftHandMiddle1','RightHandMiddle1']}
    json.dump({'n':N,'fps':d['fps'],'D':D,'rest':rest,'hipY':round(float(REST[A['Hips']][1]),4),'hips':[round(float(x)/1000,4) for x in p[:,A['Hips']].reshape(-1)],'foot':foot},open(out,'w'))

if __name__=='__main__':
    convert(sys.argv[1], sys.argv[2])
