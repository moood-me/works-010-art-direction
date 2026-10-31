# python3 sheet.py out.png name... : a row per character — the drawing, then front, three-quarter, side, full figure
import sys
from PIL import Image
R='/home/user/works-010-art-direction/docs/pictures/references/'
REF={'anime':('anime-hair-closeup.png',None),'mask':('cel-action-group.webp',(0,0,210,240)),'hood':('cel-action-group.webp',(165,20,335,240)),
 'blond':('cel-action-group.webp',(355,40,530,250)),'tails':('cel-action-group.webp',(480,80,700,280)),'boy7':('cartoon-7.png',(0,45,85,115)),
 'old':('cartoon-7.png',(118,15,245,115)),'semi':('illustrated-semireal.png',(0,0,422,260)),'red':('cartoon-anatomical-2.png',None)}
out,names=sys.argv[1],sys.argv[2:]; S=360; views=['ref','front','side','full']
sheet=Image.new('RGB',(S*5+S//2,S*len(names)),'white')
for r,n in enumerate(names):
    f,box=REF[n]; im=Image.open(R+f).convert('RGB')
    if box: im=im.crop(box)
    k=min(S*1.5/im.size[0],S/im.size[1]); im=im.resize((int(im.size[0]*k),int(im.size[1]*k)),Image.LANCZOS)
    sheet.paste(im,((S*3//2-im.size[0])//2,r*S+(S-im.size[1])//2))
    for c,v in enumerate(views):
        try: x=Image.open(f's-{n}-{v}.png').convert('RGB')
        except: continue
        if v=='full': x=x.crop((150,0,650,800)).resize((S*500//800,S))
        else: x=x.crop((100,60,700,660)).resize((S,S))
        sheet.paste(x,(S*3//2+c*S,r*S))
sheet.save(out)
