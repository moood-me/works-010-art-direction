# python3 wsheet.py out.png name... : per character two rows — reference, designed (front, side), wrapped (front, three-quarter, side);
# then wrapped close-ups (eye, neck join) and the moving face (blink, jaw open, smile)
import sys
from PIL import Image, ImageDraw
R='/home/user/works-010-art-direction/docs/pictures/references/'
REF={'hood':('cel-action-group.webp',(165,20,335,240)),'old':('cartoon-7.png',(118,15,245,115)),'semi':('illustrated-semireal.png',(0,0,422,260)),'red':('cartoon-anatomical-2.png',None)}
out,names=sys.argv[1],sys.argv[2:]; S=300
sheet=Image.new('RGB',(S*6,S*2*len(names)),'white'); d=ImageDraw.Draw(sheet)
def tile(p,crop=(100,60,700,660)):
    try: return Image.open(p).convert('RGB').crop(crop).resize((S,S))
    except Exception: return None
for r,n in enumerate(names):
    y0=r*2*S
    f,box=REF[n]; im=Image.open(R+f).convert('RGB')
    if box: im=im.crop(box)
    k=min(S/im.size[0],S/im.size[1]); im=im.resize((int(im.size[0]*k),int(im.size[1]*k)))
    sheet.paste(im,((S-im.size[0])//2,y0+(S-im.size[1])//2))
    row1=[f'designed/s-{n}-front.png',f'designed/s-{n}-side.png',f's-{n}-front.png',f's-{n}-tq.png',f's-{n}-side.png']
    labels1=['designed front','designed side','wrapped front','wrapped 3/4','wrapped side']
    for c,(p,l) in enumerate(zip(row1,labels1)):
        t=tile(p)
        if t: sheet.paste(t,(S*(c+1),y0))
        d.text((S*(c+1)+6,y0+4),l,fill=(60,60,60))
    row2=[(f's-{n}-eye.png',(150,110,650,610),'eye'),(f's-{n}-neck.png',(100,60,700,660),'neck join'),(f's-{n}-front-blink.png',(200,160,600,560),'blink'),(f's-{n}-front-jaw.png',(200,160,600,560),'jaw open'),(f's-{n}-front-smile.png',(200,160,600,560),'smile'),(f's-{n}-full.png',(200,0,600,800),'figure')]
    for c,(p,cr,l) in enumerate(row2):
        t=tile(p,cr)
        if t: sheet.paste(t,(S*c,y0+S))
        d.text((S*c+6,y0+S+4),l,fill=(60,60,60))
sheet.save(out)
