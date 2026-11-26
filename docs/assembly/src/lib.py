import json, math
import os
H=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../hardware'))
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'r'))
STL=dict(shell=f'/fs{H}/band/rev-d/case/wakeband-case-rev-d-shell.stl', cover=f'/fs{H}/band/rev-d/case/wakeband-case-rev-d-cover.stl',
         dtop=f'/fs{H}/dock/rev-d/case/wakeband-dock-rev-d-top.stl', dtray=f'/fs{H}/dock/rev-d/case/wakeband-dock-rev-d-tray.stl',
         cover_tilt=f'/fs{R}/cover-tilt.stl', dtop_tilt=f'/fs{R}/dtop-tilt.stl')   # tilted parts: python tilt.py
C=dict(shell='#f4efe4', cover='#5bc0eb', dtop='#f4efe4', dtray='#3d5a80', pcb='#1f7a4a', gold='#e8b923', ic='#2b2d31',
       cap='#c8a878', res='#222222', steel='#a7adb5', brass='#d4a640', red='#d62828', black='#222222', N='#e63946', S='#1d70b8',
       cell='#c9d1da', lra='#9aa4ae', kapton='#e39a2b', foam='#f2f2f2', epoxy='#ffb703', carrier='#2e8b57')
def mirror(dy): return -dy
def chain(edges):
    segs=[list(map(tuple,e)) for e in edges]; out=segs.pop(0)
    while segs:
        last=out[-1]; best=None
        for i,s in enumerate(segs):
            for rev in (False,True):
                p=s[-1] if rev else s[0]; d=math.hypot(p[0]-last[0],p[1]-last[1])
                if best is None or d<best[0]: best=(d,i,rev)
        s=segs.pop(best[1]); s=s[::-1] if best[2] else s; out+=s[1:]
    return out
def part_style(ref,val,fp):
    v=(val or '').lower()
    if ref.startswith('AE'): return '#f0f0f0',1.3
    if ref.startswith('D7') or ref in('D1','D2'): return '#fafafa',0.6
    if ref.startswith('X') or ref.startswith('Y'): return '#cfd4d9',0.6
    if ref.startswith('U'): return C['ic'],0.9
    if ref.startswith('J') and 'usb' in v: return '#b8bec6',3.2
    if ref.startswith('SW'): return '#d9d9d9',1.5
    if ref.startswith('L') or ref.startswith('FB'): return '#555a60',0.7
    if ref.startswith('C'): return C['cap'],0.5
    if ref.startswith('R') or ref.startswith('TH'): return C['res'],0.35
    if ref.startswith('D'): return C['ic'],0.45
    return None,0
def board(geo_path,zbot,t=None,color=None,parts=True,bpads=True,flip=False,skip=()):
    G=json.load(open(geo_path)); objs=[]
    t=t or 0.8; ol=chain(G['edges'])
    objs.append(dict(type='extrude',pts=[(x,-y) for x,y in ol],h=t,pos=[0,0,zbot],color=color or C['pcb'],edgeAngle=60,rough=0.7))
    ztop=zbot+t
    for f in G['fps']:
        if f['ref'] in skip: continue
        top=f['layer']=='F.Cu'
        for p in f['pads']:
            for L,z in (('F.Mask',ztop),('B.Mask',zbot-0.03)):
                if L in p['layers'] or '*.Mask' in p['layers']:
                    if not bpads and L=='B.Mask': continue
                    x,y=p['at']; w,h=p['w'],p['h']
                    if abs(p['ang'])%180==90: w,h=h,w
                    if p['shape']=='circle': objs.append(dict(type='cyl',r=w/2,h=0.03,pos=[x,-y,z],color=C['gold'],metal=0.25,rough=0.35,edges=False))
                    else: objs.append(dict(type='box',size=[w,h,0.03],pos=[x,-y,z+0.015],color=C['gold'],metal=0.25,rough=0.35,edges=False))
        if not parts or not top: continue
        col,hgt=part_style(f['ref'],f['val'],f)
        if not col: continue
        pts=[q for l in f['lines'] if l['layer']=='F.Fab' for q in l['pts']]
        if not pts: pts=[(p['at'][0]+sx*p['w']/2,p['at'][1]+sy*p['h']/2) for p in f['pads'] for sx in(-1,1) for sy in(-1,1)]
        x0=min(q[0] for q in pts);x1=max(q[0] for q in pts);y0=min(q[1] for q in pts);y1=max(q[1] for q in pts)
        if (x1-x0)*(y1-y0)<0.01: continue
        objs.append(dict(type='box',size=[x1-x0,y1-y0,hgt],pos=[(x0+x1)/2,-(y0+y1)/2,ztop+hgt/2],color=col,edgeAngle=40,edgeColor='#333'))
    return objs
BAND='band.json'; DOCK='dock.json'
def band_board(**k): return board(BAND,6.7,0.8,**k)
SPY=(101.1,103.3,111.7,113.9)
def cell(dz=0,dx=0,dy=0,op=1):
    z0=2.5+dz
    o=[dict(type='box',size=[15.0,13,4],pos=[114.5+dx,-107.5+dy,z0+2],color=C['cell'],metal=0.3,rough=0.35,opacity=op),
       dict(type='box',size=[2.0,12,3.4],pos=[123.0+dx,-107.5+dy,z0+2],color='#e0a43a',opacity=op)]
    return o
def cell_wires(dz=0,dx=0,dy=0,dzb=0):
    z=4.5+dz
    return [dict(type='tube',r=0.35,pts=[[124+dx,-112.6+dy,z],[127.5+dx,-112.9+dy,z+0.6],[129+dx*0,-113.5+dy*0,6.5+dzb]],color=C['red']),
            dict(type='tube',r=0.35,pts=[[124+dx,-102.0+dy,z],[127.5+dx,-100.9+dy,z+0.6],[129.05+dx*0,-101.6+dy*0,6.5+dzb]],color=C['black'])]
def lra(dz=0,dx=0,dy=0,op=1):
    return [dict(type='cyl',r=4,h=3.25,pos=[128.75+dx,-107.5+dy,3.25+dz],color=C['lra'],metal=0.5,rough=0.35,seg=48,opacity=op),
            dict(type='cyl',r=3.6,h=0.05,pos=[128.75+dx,-107.5+dy,3.2+dz],color='#f5f5f5',edges=False,opacity=op)]
def lra_wires(dz=0,dx=0,dy=0,dzb=0):
    return [dict(type='tube',r=0.12,pts=[[127.5+dx,-103.9+dy,6.2+dz],[127.1,-102.4,6.45+(dz+dzb)/2],[127.0,-101.5,6.62+dzb]],color=C['red']),
            dict(type='tube',r=0.12,pts=[[126.9+dx,-104.2+dy,6.2+dz],[125.7,-102.4,6.45+(dz+dzb)/2],[125.5,-101.5,6.62+dzb]],color=C['black'])]
def carrier(dz=0,dx=0,dy=0):
    o=[dict(type='box',size=[2.2,15.1,1.6],pos=[131.5+dx,-107.5+dy,1.5+dz],color=C['carrier'],edgeAngle=60)]
    for y in SPY: o.append(dict(type='cyl',r=0.7,h=0.03,pos=[131.5+dx,-y+dy,2.3+dz],color=C['gold'],metal=0.25,edges=False))
    return o
def pins(dz=0,dx=0,dy=0,carrier_dz=None):
    o=[]
    for y in SPY:
        X,Y=131.5+dx,-y+dy
        o+= [dict(type='cyl',r=0.215,h=1.75,pos=[X,Y,0.55+dz],color=C['gold'],metal=0.25,rough=0.3,edges=False),
             dict(type='cyl',r=0.915,h=0.25,pos=[X,Y,2.3+dz],color=C['gold'],metal=0.25,rough=0.3),
             dict(type='cyl',r=0.6,h=2.45,pos=[X,Y,2.55+dz],color=C['gold'],metal=0.25,rough=0.3),
             dict(type='cyl',r=0.4,h=1.7,pos=[X,Y,5.0+dz],color='#f0d36a',metal=0.25,rough=0.3)]
    return o
def magnet(x,y,z0,d,t,down_pole,op=1):
    a,b=(C['N'],C['S']) if down_pole=='N' else (C['S'],C['N'])
    return [dict(type='cyl',r=d/2,h=t/2,pos=[x,y,z0],color=a,opacity=op),dict(type='cyl',r=d/2,h=t/2,pos=[x,y,z0+t/2],color=b,opacity=op)]
def band_magnets(dz=0,op=1):
    return magnet(112.5,-107.5,0.2+dz,3,1,'N',op)+magnet(120.5,-107.5,0.2+dz,3,1,'S',op)
def dock_magnets(dz=0,op=1):
    return magnet(112.5,-107.5,-1.72+dz,4,1.5,'N',op)+magnet(120.5,-107.5,-1.72+dz,4,1.5,'S',op)
    # x112.5: S up (top blue) -> bottom N red ; x120.5: N up -> bottom S
def screw(dz=0):
    return [dict(type='cyl',r=1.9,r2=1.0,h=1.2,pos=[136.6,-107.5,0.2+dz],color=C['steel'],metal=0.3,rough=0.3),
            dict(type='cyl',r=1.0,h=4.8,pos=[136.6,-107.5,1.4+dz],color=C['steel'],metal=0.3,rough=0.3)]
def insert(dz=0):
    return [dict(type='cyl',r=1.65,h=3.0,pos=[136.6,-107.5,3.5+dz],color=C['brass'],metal=0.3,rough=0.3,seg=12,edgeAngle=20)]
def kapton(dz=0,op=0.55):
    return [dict(type='box',size=[29.8,14.4,0.06],pos=[100.3+14.9,-107.5,6.67+dz],color=C['kapton'],opacity=op,edges=False)]
def foam(dz=0):
    return [dict(type='box',size=[15,12,1.5],pos=[114.5,-107.5,1.0+0.75+dz],color=C['foam'],rough=0.9)]
def shell(op=1,dz=0,flip=False): 
    o=dict(type='stl',url=STL['shell'],color=C['shell'],opacity=op,edgeAngle=35)
    if dz: o['pos']=[0,0,dz]
    return [o]
def cover(op=1,dz=0):
    o=dict(type='stl',url=STL['cover'],color=C['cover'],opacity=op,edgeAngle=35)
    if dz: o['pos']=[0,0,dz]
    return [o]
def cover_tilt(op=1): return [dict(type='stl',url=STL['cover_tilt'],color=C['cover'],opacity=op,edgeAngle=35)]
def dock_top_tilt(op=1): return [dict(type='stl',url=STL['dtop_tilt'],color=C['dtop'],opacity=op,edgeAngle=35)]
DSCREW=(143.8,121.0)   # dock rev D: M2 x 8 countersunk from below into an M2 nut in the top plate
def dock_screw(dz=0):
    x,y=DSCREW
    return [dict(type='cyl',r=1.9,r2=1.0,h=1.2,pos=[x,-y,-8.04+dz],color=C['steel'],metal=0.3,rough=0.3),
            dict(type='cyl',r=1.0,h=6.8,pos=[x,-y,-6.84+dz],color=C['steel'],metal=0.3,rough=0.3)]
def dock_nut(dz=0):
    x,y=DSCREW
    return [dict(type='cyl',r=2.31,h=1.6,pos=[x,-y,-2.03+dz],color=C['steel'],metal=0.3,rough=0.3,seg=6,edgeAngle=20)]
def dock_top(op=1,dz=0): return [dict(type='stl',url=STL['dtop'],color=C['dtop'],opacity=op,pos=[0,0,dz],edgeAngle=35)]
def dock_tray(op=1,dz=0): return [dict(type='stl',url=STL['dtray'],color=C['dtray'],opacity=op,pos=[0,0,dz],edgeAngle=35)]
def dock_pcb(dz=0): return board(DOCK,-6.34+dz,1.6)
def dock_pins(dz=0):
    o=[]
    for y in SPY:
        o+=[dict(type='cyl',r=0.915,h=0.25,pos=[131.5,-y,-4.74+dz],color=C['gold'],metal=0.25),
            dict(type='cyl',r=0.6,h=3.2,pos=[131.5,-y,-4.49+dz],color=C['gold'],metal=0.25),
            dict(type='cyl',r=0.4,h=2.4,pos=[131.5,-y,-1.3+dz],color='#f0d36a',metal=0.25)]
    return o
FEET=[(x,y) for x in (100.35,136.95) for y in (100.5,119.6)]   # dock rev D
def feet(dz=0): return [dict(type='cyl',r=4,h=1.5,pos=[x,-y,-9.74+dz],color='#333333',rough=0.9) for x,y in FEET]
def arrow(a,b,color='#e63946',r=0.45,head=None):
    d={'type':'arrow','from':a,'to':b,'color':color,'r':r,'noFit':True}
    if head: d['head']=head
    return d
def flipZ(objs, zc):
    """rotate whole list 180 deg about the x axis around height zc (to show things upside down)"""
    return objs
