import json,glob,os
from PIL import Image, ImageChops
src='r/out'; dst='img'; os.makedirs(dst,exist_ok=True)
A=json.load(open(f'{src}/anchors.json')); out={}
for f in glob.glob(f'{src}/*.png'):
    n=os.path.basename(f)[:-4]
    if n.startswith('sheet'): continue
    if n=='hero':
        im=Image.open(f).convert('RGBA'); bb=im.getbbox(); c=im.crop(bb); c.save(f'{dst}/{n}.png'); out[n]={}; continue
    im=Image.open(f).convert('RGBA'); bg=Image.new('RGBA',im.size,'white'); bg.alpha_composite(im); im=bg.convert('RGB')
    diff=ImageChops.difference(im,Image.new('RGB',im.size,'white')).convert('L').point(lambda v:255 if v>8 else 0)
    bb=diff.getbbox() or (0,0,im.width,im.height); pad=int(0.03*max(im.size))
    bb=(max(0,bb[0]-pad),max(0,bb[1]-pad),min(im.width,bb[2]+pad),min(im.height,bb[3]+pad))
    c=im.crop(bb); c.save(f'{dst}/{n}.png',optimize=True)
    out[n]={k:[(v[0]*im.width-bb[0])/c.width,(v[1]*im.height-bb[1])/c.height] for k,v in A.get(n,{}).items()}
json.dump(out,open('img/anchors.json','w'),indent=1)
print(len(out))
