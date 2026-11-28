import re, math, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
s=open(sys.argv[1]).read()
def fp(ref):
    i=s.find(f'"Reference" "{ref}"'); j=s.rfind('(footprint',0,i); k=s.find('(footprint',i); return s[j:k]
def padpos(ref, net):
    f=fp(ref); a=re.search(r'\(at ([\d.\-]+) ([\d.\-]+)(?: ([\d.\-]+))?\)',f); X,Y=float(a[1]),float(a[2]); r=math.radians(float(a[3] or 0))
    for m in re.finditer(r'\(pad "[^"]+" \w+ \w+\s*\(at ([\d.\-]+) ([\d.\-]+)[^)]*\)(.*?)\(net (?:\d+ )?"([^"]+)"',f,re.S):
        if m[4]==net:
            px,py=float(m[1]),float(m[2])
            return X+px*math.cos(r)+py*math.sin(r), Y-px*math.sin(r)+py*math.cos(r)
    return X,Y
C={'VIN':'#d62728','GND':'#333333','SWDCLK':'#1f77b4','SWDIO':'#2ca02c','BAT':'#ff7f0e','MOT':'#9467bd','PMID':'#8c564b','2V0':'#17becf','MR':'#e377c2','RST':'#7f7f7f'}
dock=[(131.5,101.1,'SWDCLK','1'),(131.5,103.3,'SWDIO','2'),(131.5,111.7,'GND','3'),(131.5,113.9,'VIN','4')]
fig,axs=plt.subplots(3,1,figsize=(9,13.5))
def board(ax,title,mirror,outline=(100,133,100,115),label_ends=True):
    x0,x1,y0,y1=outline
    ax.add_patch(FancyBboxPatch((x0,y0),x1-x0,y1-y0,boxstyle="round,pad=0,rounding_size=1",fc='#e8f2e0',ec='k',lw=1.5))
    ax.set_xlim((x1+9,x0-9) if mirror else (x0-9,x1+9)); ax.set_ylim(y1+3.5,y0-4); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title,fontsize=13,fontweight='bold',loc='left')
    if label_ends:
        ax.text(x0+2.5,(y0+y1)/2,'antenna\nend',ha='center',va='center',fontsize=9,color='#666')
        ax.text(x1-6.5,(y0+y1)/2,'motor end',ha='center',va='center',fontsize=9,color='#666')
def pad(ax,x,y,name,col,num=None,r=0.8,side='r',mirror=False,txt=None):
    ax.add_patch(Circle((x,y),r,fc=col,ec='k',lw=1))
    if num: ax.text(x,y,num,ha='center',va='center',color='w',fontsize=8,fontweight='bold')
    d=1 if side=='r' else -1
    if mirror: d=-d
    ax.annotate(txt or name,(x,y),xytext=(x+d*(r+1.6)*(1 if not mirror else 1),y),fontsize=10,fontweight='bold',color=col,va='center',ha='left' if (side=='r') else 'right')
# 1: band wrist side
ax=axs[0]; board(ax,'Band board rev C, WRIST side (B side, what the dock touches)',True,label_ends=False)
ax.text(102.5,107.5,'antenna\nend',ha='center',va='center',fontsize=9,color='#666')
ax.add_patch(Rectangle((106.75,102.5),17.25,10,fc='none',ec='#bbb',ls='--')); ax.text(115.4,107.5,'cell (17.25 x 10)',ha='center',color='#999',fontsize=9)
ax.add_patch(Circle((128.75,107.5),4.0,fc='none',ec='#bbb',ls='--')); ax.text(128.75,107.5,'motor',ha='center',color='#999',fontsize=9)
for x,y,n,k in dock:
    ax.add_patch(Circle((x,y),0.8,fc=C[n],ec='k',lw=1)); ax.text(x,y,k,ha='center',va='center',color='w',fontsize=8,fontweight='bold')
    ax.text(133.6,y,f'{k}  {n}',ha='right',va='center',fontsize=10,fontweight='bold',color=C[n])
for ref,nm,col,t in (('TP201','BAT+','BAT','TP201 BAT+ (red)'),('TP202','BAT-','GND','TP202 BAT- (black)'),('TP501','M','MOT','TP501 motor'),('TP502','M','MOT','TP502 motor')):
    f=fp(ref); a=re.search(r'\(at ([\d.\-]+) ([\d.\-]+)',f); x,y=float(a[1]),float(a[2])
    ax.add_patch(Rectangle((x-0.6,y-0.6),1.2,1.2,fc=C[col],ec='k'))
yo={'TP201':115.9,'TP202':99.2,'TP501':104.0,'TP502':104.0}
ax.text(129,116.2,'TP201 BAT+ (red wire)',color=C['BAT'],fontsize=9,ha='center',fontweight='bold')
ax.text(124.5,98.9,'TP202 BAT- (black wire)',color='#333',fontsize=9,ha='center',fontweight='bold')
ax.text(126.25,103.4,'TP501/502 motor',color=C['MOT'],fontsize=8,ha='center')
ax.text(138.5,107.5,'dock pads J601\n(gold, keep bare)\nmotor end',fontsize=9,ha='center',va='center')
# 2: dock top
ax=axs[1]; board(ax,'Dock spring pins, seen from ABOVE (band lies wrist side down on these)',False,label_ends=False)
ax.text(102.5,107.5,'band\nantenna end\nsits here',ha='center',va='center',fontsize=9,color='#666')
for x,y,n,k in dock: pad(ax,x,y,n,C[n],'P'+k,r=0.9,side='r',txt=f'P{k}  {n}')
ax.text(116,107.5,'(outline = band position)',ha='center',color='#999',fontsize=9)
# 3: band top probe points
ax=axs[2]; board(ax,'Band board rev C, TOP (F side): probe points for bring-up',False,label_ends=False)
ax.text(102.5,110.5,'antenna\nend',ha='center',va='center',fontsize=9,color='#666')
pts=[('TP705','PMID','PMID','TP705 PMID: ~5 V docked, ~cell V off'),('TP706','VBAT','BAT','TP706 VBAT: 3.0-4.2 V'),('TP707','GND','GND','TP707 GND'),
     ('TP203','MR','MR','TP203 /MR: tap to GND wakes charger'),('TP701','RST','RST','TP701 nRESET (~2.0 V)')]
lab={'TP705':(118,98.6,'center'),'TP706':(118,117.0,'center'),'TP707':(140.5,109.5,'center'),'TP203':(140.5,105.4,'center'),'TP701':(105.2,98.6,'center')}
for ref,net,col,t in pts:
    f=fp(ref); a=re.search(r'\(at ([\d.\-]+) ([\d.\-]+)',f); x,y=float(a[1]),float(a[2])
    ax.add_patch(Circle((x,y),0.55,fc=C[col],ec='k')); lx,ly,ha=lab[ref]
    ax.annotate(t,(x,y),xytext=(lx,ly),fontsize=8.5,color=C[col],fontweight='bold',ha=ha,arrowprops=dict(arrowstyle='-',color=C[col],lw=0.8))
x,y=padpos('R203','/VDD_2V0'); ax.add_patch(Circle((x,y),0.4,fc=C['2V0'],ec='k'))
ax.annotate('R203 pad: 2.0 V rail',(x,y),xytext=(108,117.0),fontsize=8.5,color=C['2V0'],fontweight='bold',ha='center',arrowprops=dict(arrowstyle='-',color=C['2V0'],lw=0.8))
x,y=padpos('C201','/VIN'); ax.add_patch(Circle((x,y),0.4,fc=C['VIN'],ec='k'))
ax.annotate('C201 pad: VIN ~5 V docked',(x,y),xytext=(134,118.3),fontsize=8.5,color=C['VIN'],fontweight='bold',ha='center',arrowprops=dict(arrowstyle='-',color=C['VIN'],lw=0.8))
ax.add_patch(Rectangle((109,102.6),4,4,fc='#ccc',ec='k')); ax.text(111,104.6,'U1',ha='center',va='center',fontsize=8)
fig.text(0.5,0.01,'NudgeBand dock contacts. Pad and pin positions from hardware/band/rev-c/pcb (J601) and hardware/dock/rev-d/pcb (P1-P4).',ha='center',fontsize=8,color='#555')
plt.tight_layout(rect=(0,0.02,1,1)); plt.savefig(sys.argv[2],dpi=150)
