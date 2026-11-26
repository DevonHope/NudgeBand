import json, copy; from lib import *
def up(objs,dz):
    o=copy.deepcopy(objs)
    for x in o:
        if x['type']=='arrow': x['from'][2]+=dz; x['to'][2]+=dz
        elif x['type']=='tube': 
            for p in x['pts']: p[2]+=dz
        else:
            p=x.get('pos',[0,0,0]); x['pos']=[p[0],p[1],p[2]+dz]
    return o
def move(objs,dx=0,dy=0,dz=0):
    o=copy.deepcopy(objs)
    for x in o:
        if x['type']=='arrow':
            for k in('from','to'): x[k]=[x[k][0]+dx,x[k][1]+dy,x[k][2]+dz]
        elif x['type']=='tube': x['pts']=[[p[0]+dx,p[1]+dy,p[2]+dz] for p in x['pts']]
        else:
            p=x.get('pos',[0,0,0]); x['pos']=[p[0]+dx,p[1]+dy,p[2]+dz]
    return o
def bed(z,x0=88,x1=150,y0=-128,y1=-92,col='#8d99ae'):
    return [dict(type='box',size=[x1-x0,y1-y0,1.0],pos=[(x0+x1)/2,(y0+y1)/2,z-0.5],color=col,rough=0.8,edgeAngle=60)]
def strap(side):
    if side=='L': sx,bar,far=95.95,91.0,72
    else: sx,bar,far=142.15,146.3,165
    t=1.2; w=16
    o=[dict(type='box',size=[t,w,5.0],pos=[sx,-107.5,1.5],color='#2a9d8f',rough=0.9),
       dict(type='box',size=[abs(sx-bar)+t,w,t],pos=[(sx+bar)/2,-107.5,4.0+t/2],color='#2a9d8f',rough=0.9),
       dict(type='box',size=[t,w,6.2],pos=[bar,-107.5,1.5],color='#2a9d8f',rough=0.9),
       dict(type='box',size=[abs(far-sx),w,t],pos=[(far+sx)/2,-107.5,-1.0-t/2],color='#2a9d8f',rough=0.9)]
    return o
A={}
S={}
V_ISO=[1,-1.4,1.1]
# ---------- thumbnails
TH=dict(w=700,h=520,margin=1.15)
S['p_board']=dict(objects=band_board(),view=[0.4,-1,1.4],**TH)
S['p_cell']=dict(objects=cell()+[dict(type='tube',r=0.35,pts=[[124,-112.6,4.5],[130,-112.6,4.5],[134,-113.5,4.5]],color=C['red']),dict(type='tube',r=0.35,pts=[[124,-102.4,4.5],[130,-102.4,4.5],[134,-101.6,4.5]],color=C['black'])]
                 +[dict(type='box',size=[3,5,2.6],pos=[135.5,-107.5,4.5],color='#f4f4f4')],view=V_ISO,**TH)
S['p_lra']=dict(objects=lra()+[dict(type='tube',r=0.15,pts=[[127.5,-103.9,6.2],[126.5,-100.5,6.3],[126,-98,6.3]],color=C['red']),dict(type='tube',r=0.15,pts=[[126.9,-104.2,6.2],[125.5,-101,6.3],[125,-98.2,6.3]],color=C['black'])],view=V_ISO,**TH)
S['p_carrier']=dict(objects=carrier(),view=[1,-0.9,1.2],**TH)
S['p_pin']=dict(objects=[o for o in pins() if abs(o['pos'][1]+101.1)<0.01],view=[1,-1,0.35],**TH)
S['p_mag3']=dict(objects=magnet(0,0,0,3,1,'N'),view=[1,-1.2,1.0],**TH)
S['p_mag4']=dict(objects=magnet(0,0,0,4,1.5,'N'),view=[1,-1.2,1.0],**TH)
S['p_screw']=dict(objects=screw(),view=[1,-1,0.5],**TH)
S['p_insert']=dict(objects=insert(),view=[1,-1,0.9],**TH)
S['p_shell']=dict(objects=shell(),view=V_ISO,**TH)
S['p_cover']=dict(objects=cover(),view=V_ISO,**TH)
S['p_dtop']=dict(objects=dock_top(),view=V_ISO,**TH)
S['p_dtray']=dict(objects=dock_tray(),view=V_ISO,**TH)
S['p_dpcb']=dict(objects=dock_pcb(),view=V_ISO,**TH)
S['p_dpin']=dict(objects=[o for o in dock_pins() if abs(o['pos'][1]+101.1)<0.01],view=[1,-1,0.35],**TH)
S['p_feet']=dict(objects=[dict(type='cyl',r=4,h=1.5,pos=[0,0,0],color='#333333',rough=0.9),dict(type='cyl',r=4,h=1.5,pos=[10,0,0],color='#333333',rough=0.9)],view=[1,-1.2,1.2],**TH)
S['p_foam']=dict(objects=[dict(type='box',size=[15,12,1.5],pos=[0,0,0.75],color=C['foam'],rough=0.9),dict(type='box',size=[15,12,0.1],pos=[0,0,1.55],color='#e05a47',edges=False)],view=V_ISO,**TH)
S['p_kapton']=dict(objects=[dict(type='cyl',r=8,h=12,pos=[0,0,0],color=C['kapton'],rough=0.4,seg=48),dict(type='cyl',r=5,h=12.1,pos=[0,0,-0.05],color='#f3e9d2',seg=48)],view=[1,-1.2,1.4],**TH)
# ---------- print plates
PR=dict(w=1100,h=760,margin=1.08)
S['print_shell']=dict(objects=shell()+bed(11.0,95,143,-119,-96),flip=True,view=V_ISO,**PR)
S['print_cover']=dict(objects=cover()+bed(0,89,148,-120,-95),view=V_ISO,**PR)
S['print_dtop']=dict(objects=dock_top()+bed(-2.05,86,151,-128,-92),view=V_ISO,**PR)
S['print_dtray']=dict(objects=dock_tray()+bed(-8.24,86,151,-128,-92),view=V_ISO,**PR)
# ---------- steps
ST=dict(w=1600,h=1050)
# 1 magnets at the pause
cv=cover(); cv[0]['clipZ']=1.25
S['s_magnets']=dict(objects=cv+bed(0,89,148,-120,-95)+up(band_magnets(),6)+[arrow([112.5,-107.5,5.6],[112.5,-107.5,1.6],'#e63946',0.3,1.2),arrow([120.5,-107.5,5.6],[120.5,-107.5,1.6],'#e63946',0.3,1.2)],
    view=[0.5,-1.3,1.6],fitBox=[[101,-116,0],[131,-99,6]],**ST)
A['s_magnets']={'m1':[112.5,-107.5,7.3],'m2':[120.5,-107.5,7.3]}
# 2 insert
S['s_insert']=dict(objects=shell()+up(insert(),-6)+[arrow([136.6,-107.5,-2.0],[136.6,-107.5,2.8],'#e63946',0.35,1.4)],flip=True,view=[1,-1.3,1.3],**ST)
A['s_insert']={'ins':[136.6,-107.5,-3.0]}
# 3 pins into carrier
S['s_pins']=dict(objects=carrier()+up(pins(),6)+[arrow([133.2,-y,9.2],[133.2,-y,3.4],'#e63946',0.18,0.8) for y in (101.1,113.9)]+
    [dict(type='cyl',r=0.6,h=0.12,pos=[131.5,-y,2.33],color='#b0b6bc',edges=False) for y in SPY],view=[1,-0.8,0.9],**ST)
A['s_pins']={'paste':[131.5,-111.7,2.4],'tail':[131.5,-113.9,0.55]}
# 4 hotplate
S['s_reflow']=dict(objects=carrier(dz=1.0)+pins(dz=1.0)+[dict(type='box',size=[12,22,1.0],pos=[131.5,-107.5,1.0],color='#9aa3ab'),dict(type='box',size=[26,30,4],pos=[131.5,-107.5,-1.6],color='#c1121f')],view=[1,-1.1,0.8],**ST)
# 5 carrier into cover
S['s_carrier']=dict(objects=cover()+band_magnets()+up(carrier()+pins(),9)+[arrow([134.5,-107.5,14],[134.5,-107.5,5],'#e63946',0.35,1.6)],view=[1.3,-0.9,1.5],fitBox=[[112,-118,0],[146,-97,14]],**ST)
A['s_carrier']={'car':[131.5,-115.5,10.5]}
# 6 epoxy
bead=[dict(type='box',size=[0.7,15.8,0.9],pos=[x,-107.5,2.75],color=C['epoxy'],opacity=0.85,edges=False) for x in (130.1,132.9)]+\
     [dict(type='box',size=[3.6,0.7,0.9],pos=[131.5,-y,2.75],color=C['epoxy'],opacity=0.85,edges=False) for y in (99.7,115.3)]
S['s_epoxy']=dict(objects=cover()+carrier()+pins()+band_magnets()+bead,view=[0.35,-0.6,2.0],fitBox=[[120,-118,0],[143,-97,4]],margin=1.05,**ST)
A['s_epoxy']={'bead':[132.9,-104,2.6],'plunger':[131.5,-111.7,6.7]}
# 7 continuity check on the dock
S['s_cover_dock']=dict(objects=dock_top()+dock_tray()+dock_pins()+dock_magnets()+cover()+carrier()+pins()+band_magnets(),view=V_ISO,**ST)
# 8 battery solder (board back up = flipped, cell+wires)
S['s_battery']=dict(objects=band_board()+up(cell(),-3)+[dict(type='tube',r=0.35,pts=[[124,-112.6,1.5],[127.5,-113,3.2],[129,-113.5,6.6]],color=C['red']),
     dict(type='tube',r=0.35,pts=[[124,-102.0,1.5],[127.5,-101.2,3.2],[129.05,-101.6,6.6]],color=C['black'])],flip=True,view=[0.6,-1.0,1.5],**ST)
A['s_battery']={'p':[129,-113.5,6.6],'n':[129.05,-101.6,6.6],'cell':[114,-107.5,0.5],'dock':[131.5,-107.5,6.7]}
S['s_motor']=dict(objects=band_board()+up(cell(),-3)+[dict(type='tube',r=0.35,pts=[[124,-112.6,1.5],[127.5,-113,3.2],[129,-113.5,6.6]],color=C['red']),
     dict(type='tube',r=0.35,pts=[[124,-102.0,1.5],[127.5,-101.2,3.2],[129.05,-101.6,6.6]],color=C['black'])]+up(lra(),-4)+
     [dict(type='tube',r=0.14,pts=[[127.5,-103.9,2.2],[127.2,-102.2,4.5],[127.0,-101.5,6.62]],color=C['red']),dict(type='tube',r=0.14,pts=[[126.9,-104.2,2.2],[125.7,-102.3,4.5],[125.5,-101.5,6.62]],color=C['black'])],
     flip=True,view=[0.6,-1.0,1.5],**ST)
A['s_motor']={'p':[126.25,-100.2,6.6],'lra':[128.75,-107.5,-0.5]}
# 9 kapton
S['s_kapton']=dict(objects=band_board()+kapton(op=0.75)+[dict(type='tube',r=0.35,pts=[[129,-113.5,6.6],[127.5,-113,6.0],[124,-112.6,5.0]],color=C['red']),dict(type='tube',r=0.35,pts=[[129.05,-101.6,6.6],[127.5,-101.2,6.0],[124,-102.0,5.0]],color=C['black'])],flip=True,view=[0.6,-1.0,1.5],**ST)
A['s_kapton']={'k':[110,-107.5,6.6],'dock':[131.5,-107.5,6.7]}
# 10 board into shell (shell face down: flip everything)
S['s_board_shell']=dict(objects=shell()+up(band_board(),-9)+[arrow([115,-107.5,-4],[115,-107.5,3.2],'#e63946',0.4,1.6)],flip=True,view=V_ISO,**ST)
# 11 cell + motor lie on board back, foam in cover
S['s_stack']=dict(objects=shell()+band_board()+kapton(op=0.75)+cell()+cell_wires()+lra()+lra_wires(),flip=True,view=V_ISO,**ST)
S['s_foam']=dict(objects=cover()+band_magnets()+carrier()+pins()+up(foam(),6)+[arrow([114.5,-107.5,11.5],[114.5,-107.5,4.2],'#e63946',0.4,1.6)],view=[1,-1.2,1.5],**ST)
A['s_foam']={'ped':[128.75,-107.5,3.2]}
# 12 cover onto shell (flipped): cover high above
S['s_close']=dict(objects=shell()+band_board()+kapton(op=0.75)+cell()+cell_wires()+lra()+lra_wires()+foam()+cover_tilt()+
     [arrow([142,-107.5,-12],[142,-107.5,-4],'#e63946',0.45,1.8)],flip=True,view=[0.9,-1.5,0.9],**ST)
A['s_close']={'hook':[98.6,-107.5,7.0]}
S['s_screw']=dict(objects=shell()+insert()+band_board()+cell()+lra()+cover()+carrier()+pins()+band_magnets()+up(screw(),-9)+[arrow([136.6,-107.5,-4.0],[136.6,-107.5,-0.6],'#e63946',0.35,1.3)],flip=True,view=[1,-1.2,1.2],**ST)
A['s_screw']={'s':[136.6,-107.5,-9.5]}
# finished band
S['s_done_top']=dict(objects=shell()+cover(),view=V_ISO,**ST)
S['s_done_wrist']=dict(objects=shell()+cover(),flip=True,view=V_ISO,**ST)
S['s_xray']=dict(objects=shell(op=0.25)+cover(op=0.3)+band_board()+cell()+cell_wires()+lra()+lra_wires()+carrier()+pins()+band_magnets()+screw()+insert()+foam()+kapton(op=0.6),view=V_ISO,**ST)
# dock
S['d_pins']=dict(objects=dock_pcb()+up(dock_pins(),6)+[arrow([134.5,-107.5,8],[134.5,-107.5,-2.5],'#e63946',0.3,1.2)],view=V_ISO,**ST)
S['d_tray']=dict(objects=dock_tray()+up(dock_pcb()+dock_pins(),10)+[arrow([100,-112,10],[100,-112,1],'#e63946',0.45,1.8)],view=V_ISO,**ST)
S['d_magnets']=dict(objects=dock_top()+up(dock_magnets(),-6)+[arrow([112.5,-107.5,-5.0],[112.5,-107.5,-2.2],'#e63946',0.3,1.0),arrow([120.5,-107.5,-5.0],[120.5,-107.5,-2.2],'#e63946',0.3,1.0)],flip=True,view=[0.4,-1.2,1.5],fitBox=[[100,-123,-8],[147,-97,1.2]],**ST)
A['d_magnets']={'m1':[112.5,-107.5,-8.0],'m2':[120.5,-107.5,-8.0]}
S['d_top']=dict(objects=dock_tray()+dock_pcb()+dock_pins()+dock_top_tilt()+[arrow([140,-107.5,30],[140,-107.5,6],'#e63946',0.5,2.0)],view=[1,-1.6,0.9],**ST)
A['d_top']={'hook':[91.7,-119.3,0.5]}
S['d_feet']=dict(objects=dock_tray()+dock_top()+up(feet(),-6)+
    [arrow([x,-y,-15],[x,-y,-10.2],'#e63946',0.4,1.4) for x,y in FEET],flip=True,view=V_ISO,**ST)
S['d_band']=dict(objects=dock_top()+dock_tray()+up(shell()+cover(),12)+[arrow([118,-107.5,22],[118,-107.5,13],'#e63946',0.5,2)],view=V_ISO,**ST)
S['hero']=dict(objects=dock_top()+dock_tray()+shell()+cover()+[dict(type='cyl',r=1.0,h=0.05,pos=[130.225,-113.2,10.0],color='#ff4d6d',edges=False)],view=[1,-1.5,1.0],w=1800,h=1100,bg=False)
S['strap']=dict(objects=shell()+cover()+strap('L')+strap('R'),view=[1,-1.4,0.9],**ST)
S['explode']=dict(objects=up(shell(),26)+up(band_board(),16)+up(cell()+lra(),11)+foam()+cover()+carrier()+pins()+band_magnets()+up(screw(),-10)+up(insert(),24),view=[1,-1.6,0.95],w=1400,h=1500)
S['t_board_back']=dict(objects=band_board(),flip=True,view=[0.4,-1,1.4],**ST)
for k,v in S.items():
    if k in A: v['anchors']=A[k]
json.dump(S,open('r/scenes.json','w'))
print(len(S))
