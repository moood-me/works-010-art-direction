import json, random, sys
seed=int(sys.argv[1]); n=int(sys.argv[2]); out=sys.argv[3]
R=random.Random(seed)
U=lambda a,b: round(R.uniform(a,b),3)
GENRES=['disney','pixar','anime','burton','clay','soviet','comic','chibi','upa','hose','stick']
CHARS=['princess','care','teen','hero','elf','sage','tomboy','teacher','baby','wardrobe','']
OUTFITS=[[('dress',)],[('tshirt',),('skirt',)],[('sweater',),('pants',)],[('polo',),('shorts',)],[('oversized',),('skirt',)],[('tunic',),('vikingpants',)],[('robe',)],[('tshirt',),('pants',)],[('sweater',),('skirt',)],[('dress',),('apron',)]]
HAIR=['bob','shoulder','bun','bob','fringe','short','long']
WHO=['woman','girl','oldwoman','man','boy','woman','girl']
SKIN=['#f3d2bd','#eec0a0','#e3a983','#c98d67','#a8704f','#7d4f36','#f6dccb']
HAIRC=['#2a1d18','#4a2a1c','#6a3a22','#8a5a32','#b07a3e','#d8b06a','#c9c3bb','#9a3a22','#1f2a3a']
CLOTH=['#3d5f8c','#a8574a','#e9e4dc','#2f3c58','#5a7a4a','#d9a441','#7a4a6a','#4b4a42','#c76b7a','#2b6b6b','#e0c8a0','#8a8f96']
IRIS=['#3f6a8c','#5a3b26','#3a2a26','#4f7a4a','#7a5a2a','#2a2a3a','#6a8aa8']
LIPS=['#8a4740','#a0504a','#6a3a36','#b0605a']
items=[]
for k in range(n):
  g=GENRES[k%len(GENRES)] if k<len(GENRES) else R.choice(GENRES)
  ch=R.choice(CHARS)
  fit=R.choice(OUTFITS); cols=R.sample(CLOTH,3); hc=R.choice(HAIRC)
  wear=[[w[0],cols[i]] for i,w in enumerate(fit)]+[['flats' if R.random()<0.6 else 'boots','#2a2230'],[R.choice(HAIR),hc]]
  big=U(0.22,0.42)
  look={'skin':R.choice(SKIN),'wear':wear,'hair':hc,
    'face':{'soft':R.choice([0.02,0.028,0.035])},
    'eye':{'size':big,'tall':R.choice([1,1,1.1,1.25]),'flat':R.choice([1,1,0.7]),'depth':U(0.55,0.75),'apart':U(-0.04,0.08),'lift':U(-0.06,0.03),
      'iris':U(0.55,0.85),'irisColor':R.choice(IRIS),'lid':U(0.22,0.34),'lidTilt':U(0.05,0.35),'lower':R.choice([0,0.1,0.15]),'gaze':[0,0.04],
      'brow':U(0.04,0.1),'browUp':U(-0.05,0.3),'lash':U(0.04,0.11),'open':[1,0.85],'mouthW':U(0.012,0.03),'smile':U(-0.1,0.6),'mouthLine':U(0.018,0.035),
      'mouthDrop':0.02,'lips':None,'glint':U(0.09,0.16),
      'nose':None if R.random()<0.2 else {'drop':U(0.5,0.75),'size':U(0.1,0.24),'height':U(0.03,0.14),'bridge':U(1,3),'turn':U(-0.2,0.5)}}}
  over={'faceLen':U(-0.8,0.3),'jaw':U(-0.7,0.4),'cheeks':U(-0.2,0.7),'cranium':U(-0.3,0.4),'nose':-1}
  sk=look['skin']; dark=int(sk[1:3],16)<0xd0
  look['eye']['lips']='#e08a80' if dark else R.choice(LIPS)
  name=f"g{seed}-{k:02d}"
  who=R.choice(WHO)
  if who in ('man','boy') and wear[-1][0] in ('long','bun','shoulder'): wear[-1][0]=R.choice(['short','fringe'])
  if who in ('man','boy') and fit[0][0] in ('dress','robe'): wear[0][0]='sweater'
  base={'who':who,'gw':{g:1},'cw':({ch:round(R.uniform(0.4,0.9),2)} if ch else {}),'look':name,'lookDef':look,'over':over}
  items.append({**base,'name':name+'-h','yaw':0.3,'dist':0.8,'head':-0.03})
  items.append({**base,'name':name+'-f','yaw':0.35})
  items[-1]['meta']=f"{who} {g}+{ch}"
json.dump(items,open(out,'w'))
print(len(items))
