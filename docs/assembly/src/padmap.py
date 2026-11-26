import json, math, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch, Rectangle, Ellipse
from matplotlib.collections import LineCollection
import matplotlib.patheffects as pe
G=json.load(open('band.json'))
M=lambda p:(-p[0],p[1])   # view from the back: mirror x
MASK='#1f6e43'; MASK_CU='#2a8a55'; GOLD='#e8b923'
plt.rcParams['font.family']='DejaVu Sans'
fig,ax=plt.subplots(figsize=(15,9.6),dpi=200)
ax.set_facecolor('white')
# board
outline=[]
for e in G['edges']: outline+= [M(p) for p in e]
# order edges into a polygon: simple approach - use convex-ish by angle around centre
cx=sum(p[0] for p in outline)/len(outline); cy=sum(p[1] for p in outline)/len(outline)
outline.sort(key=lambda p:math.atan2(p[1]-cy,p[0]-cx))
ax.add_patch(Polygon(outline,closed=True,fc=MASK,ec='#0d3b22',lw=2.5,zorder=1))
for z in G['zones']:
    if z['layer']=='B.Cu': ax.add_patch(Polygon([M(p) for p in z['pts']],closed=True,fc=MASK_CU,ec='none',zorder=2))
segs=[[M(t['a']),M(t['b'])] for t in G['tracks'] if t['layer']=='B.Cu']
ax.add_collection(LineCollection(segs,linewidths=[t['w']*72/25.4*7.5 for t in G['tracks'] if t['layer']=='B.Cu'],colors='#3aa46a',capstyle='round',zorder=3))
for v in G['vias']:
    x,y=M(v['at']); ax.add_patch(Circle((x,y),v['size']/2,fc='#3aa46a',ec='none',zorder=3))
# all exposed B pads in gold
def padpatch(p,fc,ec='#7a5a00',lw=1,z=5):
    x,y=M(p['at'])
    if p['shape']=='circle': return Circle((x,y),p['w']/2,fc=fc,ec=ec,lw=lw,zorder=z)
    w,h=p['w'],p['h']
    if abs(p['ang'])%180==90: w,h=h,w
    return FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0,rounding_size=%g'%(0.25 if p['shape']!='rect' else 0.02),fc=fc,ec=ec,lw=lw,zorder=z)
fps={f['ref']:f for f in G['fps']}
for f in G['fps']:
    for p in f['pads']:
        if 'B.Mask' in p['layers']: ax.add_patch(padpatch(p,GOLD))
# JP201 copper bridge
a=M(fps['JP201']['pads'][0]['at']); b=M(fps['JP201']['pads'][1]['at'])
ax.add_patch(Rectangle((min(a[0],b[0]),a[1]-0.25),abs(a[0]-b[0]),0.5,fc=GOLD,ec='none',zorder=4))
# ghost cell + motor (on top of the board, as fitted)
cell_c=M((115.5,107.5)); ax.add_patch(FancyBboxPatch((cell_c[0]-8.5+0.0,cell_c[1]-6.5),17,13,boxstyle='round,pad=0,rounding_size=1',fc='#c9ced6',ec='#59606b',lw=2,ls='--',alpha=0.35,zorder=6))
ax.text(cell_c[0],cell_c[1]-0.6,'BATTERY\n(60 mAh LiPo)',ha='center',va='center',fontsize=15,weight='bold',color='#2b2f36',zorder=7)
ax.text(cell_c[0],cell_c[1]+3.2,'sits here, on kapton',ha='center',va='center',fontsize=10.5,color='#2b2f36',zorder=7)
lra_c=M((128.75,107.5)); ax.add_patch(Circle(lra_c,4,fc='#b9c3cf',ec='#59606b',lw=2,ls='--',alpha=0.35,zorder=6))
ax.text(lra_c[0],lra_c[1],'MOTOR',ha='center',va='center',fontsize=11,weight='bold',color='#2b2f36',zorder=7)
# wires
def wire(pts,c,lw=5):
    P=[M(p) for p in pts]
    ax.plot([p[0] for p in P],[p[1] for p in P],color='black' if c=='#222222' else c,lw=lw+2.4,solid_capstyle='round',solid_joinstyle='round',zorder=8,alpha=0.35)
    ax.plot([p[0] for p in P],[p[1] for p in P],color=c,lw=lw,solid_capstyle='round',solid_joinstyle='round',zorder=8)
# lra lead tab towards TP501/502
ang=math.radians(-110)
import numpy as np
tip=(128.75+5.0*math.cos(math.radians(-110))*0+ -1.6, 103.0)
# highlight rings
def ring(ref,col):
    p=fps[ref]['pads'][0]; x,y=M(p['at']); r=max(p['w'],p['h'])/2+0.55
    ax.add_patch(Circle((x,y),r,fc='none',ec=col,lw=4,zorder=9))
    return x,y
def callout(xy,txt,tx,ty,col,sub=None):
    ax.annotate('',xy=xy,xytext=(tx,ty),arrowprops=dict(arrowstyle='-|>,head_width=0.5,head_length=0.9',color=col,lw=3.2,shrinkA=0,shrinkB=8),zorder=10)
    t=ax.text(tx,ty,txt,ha='center',va='center',fontsize=13.5,weight='bold',color='white',zorder=11,
        bbox=dict(boxstyle='round,pad=0.45',fc=col,ec='none'))
    if sub: ax.text(tx,ty+(1.55 if ty>108 else -1.55),sub,ha='center',va='center',fontsize=10.5,color='#222',zorder=11)
p=ring('TP201','#d62828'); callout(p,'BATTERY +  (red)','TP201',0,0,'#d62828') if False else callout(p,'BATTERY +  red wire',-127.5,119.2,'#d62828','TP201, big square pad')
p=ring('TP202','#111111'); callout(p,'BATTERY –  black wire',-129.5,95.8,'#111111','TP202, square pad')
p=ring('TP501','#7b2cbf'); callout(p,'MOTOR lead 1',-115.5,95.8,'#7b2cbf','TP501 (+), oval pad')
p=ring('TP502','#7b2cbf'); callout(p,'MOTOR lead 2',-104.0,95.8,'#7b2cbf','TP502 (–), oval pad')
# dock landings
for p in fps['J601']['pads']:
    x,y=M(p['at']); ax.add_patch(Circle((x,y),1.35,fc='none',ec='#0077b6',lw=2.6,ls=(0,(2,1.2)),zorder=9))
ax.text(-135.6,107.4,'DOCK\nCONTACTS\n\nno solder,\nno tape',ha='center',va='center',fontsize=11,weight='bold',color='#0077b6')
ax.annotate('',xy=(-132.4,102.2),xytext=(-135.2,105.2),arrowprops=dict(arrowstyle='-|>',color='#0077b6',lw=2.2))
ax.annotate('',xy=(-132.4,112.8),xytext=(-135.2,109.8),arrowprops=dict(arrowstyle='-|>',color='#0077b6',lw=2.2))
jx,jy=M((125.7,113.5)); ax.add_patch(Ellipse((jx,jy),2.6,1.3,fc='none',ec='#f77f00',lw=2.6,zorder=9))
ax.annotate('JP201 is already joined by copper.\nLeave it alone.',xy=(jx,jy+0.7),xytext=(-110.5,119.2),ha='center',va='center',fontsize=11,color='#b85c00',weight='bold',
            arrowprops=dict(arrowstyle='-|>',color='#f77f00',lw=2.2),zorder=11)
# orientation cues
ax.text(-101.8,113.6,'antenna\nend',ha='center',va='center',fontsize=9.5,color='white',style='italic',zorder=7)
ax.set_xlim(-140,-95.5); ax.set_ylim(122,92.5); ax.set_aspect('equal'); ax.axis('off')
ax.text(-117.75,92.0,'NudgeBand rev C  •  BACK of the board (the side with no parts, faces your wrist)',ha='center',va='bottom',fontsize=17,weight='bold',color='#111')
ax.text(-117.75,121.6,'Square pads = battery.  Oval pads = motor.  Solder each wire flat on its pad (insulated wires may cross), then cover the board with kapton, leaving the 4 dock contacts bare.\n'
        'Battery polarity MATTERS: red to +, black to –. The motor is driven back and forth, so its two leads can go either way round.',ha='center',va='top',fontsize=10.5,color='#333')
fig.savefig('band-rev-c-back-pads.png',bbox_inches='tight',pad_inches=0.25,facecolor='white')
