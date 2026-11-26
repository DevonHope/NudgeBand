import math, json, sys
from kp import load, find, one, S, rot
def arcpts(s,m,e,n=16):
    (x1,y1),(x2,y2),(x3,y3)=s,m,e
    d=2*(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))
    ux=((x1*x1+y1*y1)*(y2-y3)+(x2*x2+y2*y2)*(y3-y1)+(x3*x3+y3*y3)*(y1-y2))/d
    uy=((x1*x1+y1*y1)*(x3-x2)+(x2*x2+y2*y2)*(x1-x3)+(x3*x3+y3*y3)*(x2-x1))/d
    r=math.hypot(x1-ux,y1-uy)
    a1=math.atan2(y1-uy,x1-ux); a2=math.atan2(y2-uy,x2-ux); a3=math.atan2(y3-uy,x3-ux)
    def norm(a): return a%(2*math.pi)
    # go from a1 to a3 passing a2
    d13=norm(a3-a1); d12=norm(a2-a1)
    sweep=d13 if d12<d13 else d13-2*math.pi
    return [(ux+r*math.cos(a1+sweep*i/n), uy+r*math.sin(a1+sweep*i/n)) for i in range(n+1)]
def xy(n): return (n[1],n[2])
def geo(path):
    pcb=load(path); G={'edges':[], 'tracks':[], 'vias':[], 'zones':[], 'fps':[], 'gr':[]}
    for kind in ('gr_line','gr_arc','gr_circle','gr_poly','gr_rect'):
        for g in find(pcb,kind):
            L=S(one(g,'layer')[1])
            if kind=='gr_line': pts=[xy(one(g,'start')),xy(one(g,'end'))]
            elif kind=='gr_arc': pts=arcpts(xy(one(g,'start')),xy(one(g,'mid')),xy(one(g,'end')))
            elif kind=='gr_circle':
                c=xy(one(g,'center')); e=xy(one(g,'end')); r=math.hypot(e[0]-c[0],e[1]-c[1])
                pts=[(c[0]+r*math.cos(t*math.pi/16),c[1]+r*math.sin(t*math.pi/16)) for t in range(33)]
            elif kind=='gr_rect':
                a=xy(one(g,'start')); b=xy(one(g,'end')); pts=[a,(b[0],a[1]),b,(a[0],b[1]),a]
            else:
                pts=[xy(p) for p in find(one(g,'pts'),'xy')]; pts.append(pts[0])
            fill=one(g,'fill'); 
            G['gr'].append(dict(layer=L,pts=pts,kind=kind))
            if L=='Edge.Cuts': G['edges'].append(pts)
    for s in find(pcb,'segment'):
        G['tracks'].append(dict(a=xy(one(s,'start')),b=xy(one(s,'end')),w=one(s,'width')[1],layer=S(one(s,'layer')[1])))
    for v in find(pcb,'via'):
        G['vias'].append(dict(at=xy(one(v,'at')),size=one(v,'size')[1],drill=one(v,'drill')[1]))
    for z in find(pcb,'zone'):
        for fpoly in find(z,'filled_polygon'):
            G['zones'].append(dict(layer=S(one(fpoly,'layer')[1]),pts=[xy(p) for p in find(one(fpoly,'pts'),'xy')]))
    for fp in find(pcb,'footprint'):
        at=one(fp,'at'); fx,fy=at[1],at[2]; fa=at[3] if len(at)>3 else 0
        layer=S(one(fp,'layer')[1])
        props={(S(p[1])):p[2] for p in find(fp,'property')}
        def T(x,y):
            rx,ry=rot(x,y,fa); return (fx+rx,fy+ry)
        pads=[]
        for pd in find(fp,'pad'):
            pat=one(pd,'at'); px,py=pat[1],pat[2]; pa=pat[3] if len(pat)>3 else fa
            sz=one(pd,'size'); net=one(pd,'net'); dr=one(pd,'drill')
            pads.append(dict(num=str(pd[1]),type=S(pd[2]),shape=S(pd[3]),at=T(px,py),w=sz[1],h=sz[2],ang=pa,
                net=(net[-1] if net else ''),layers=[S(l) for l in one(pd,'layers')[1:]],drill=(dr[1] if dr else 0)))
        lines=[]
        for kind in ('fp_line','fp_rect','fp_poly','fp_circle','fp_arc'):
            for g in find(fp,kind):
                L=S(one(g,'layer')[1])
                if kind=='fp_line': pts=[T(*xy(one(g,'start'))),T(*xy(one(g,'end')))]
                elif kind=='fp_rect':
                    a=xy(one(g,'start')); b=xy(one(g,'end')); pts=[T(*p) for p in [a,(b[0],a[1]),b,(a[0],b[1]),a]]
                elif kind=='fp_poly':
                    pts=[T(*xy(p)) for p in find(one(g,'pts'),'xy')]; pts.append(pts[0])
                elif kind=='fp_circle':
                    c=xy(one(g,'center')); e=xy(one(g,'end')); r=math.hypot(e[0]-c[0],e[1]-c[1])
                    pts=[T(c[0]+r*math.cos(t*math.pi/12),c[1]+r*math.sin(t*math.pi/12)) for t in range(25)]
                else:
                    pts=[T(*p) for p in arcpts(xy(one(g,'start')),xy(one(g,'mid')),xy(one(g,'end')),8)]
                lines.append(dict(layer=L,pts=pts))
        mdl=one(fp,'model')
        G['fps'].append(dict(ref=props.get('Reference'),val=props.get('Value'),layer=layer,at=(fx,fy),ang=fa,pads=pads,lines=lines,
                             model=(mdl[1] if mdl else None)))
    return G
if __name__=='__main__':
    G=geo(sys.argv[1]); json.dump(G,open(sys.argv[2],'w'))
    print(len(G['edges']),len(G['tracks']),len(G['zones']),len(G['fps']))
    print(sorted(set(z['layer'] for z in G['zones'])))
