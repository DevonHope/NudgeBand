import sexpdata, math, sys
from sexpdata import Symbol
def S(x): return x.value() if isinstance(x,Symbol) else x
def load(p):
    return sexpdata.loads(open(p).read())
def find(node, name):
    return [c for c in node if isinstance(c,list) and c and S(c[0])==name]
def one(node,name):
    r=find(node,name); return r[0] if r else None
def rot(x,y,a):
    a=math.radians(a); return x*math.cos(a)+y*math.sin(a), -x*math.sin(a)+y*math.cos(a)
def footprints(pcb):
    out=[]
    for fp in find(pcb,'footprint'):
        at=one(fp,'at'); fx,fy=at[1],at[2]; fa=at[3] if len(at)>3 else 0
        layer=S(one(fp,'layer')[1])
        props={S(p[1]) if not isinstance(p[1],str) else p[1]:p[2] for p in find(fp,'property')}
        pads=[]
        for pd in find(fp,'pad'):
            pat=one(pd,'at'); px,py=pat[1],pat[2]; pa=pat[3] if len(pat)>3 else 0
            rx,ry=rot(px,py,fa)
            sz=one(pd,'size'); net=one(pd,'net')
            layers=[S(l) for l in one(pd,'layers')[1:]]
            pads.append(dict(num=pd[1],type=S(pd[2]),shape=S(pd[3]),x=fx+rx,y=fy+ry,w=sz[1],h=sz[2],ang=pa,
                net=(net[-1] if net else ''),layers=layers))
        out.append(dict(ref=props.get('Reference'),val=props.get('Value'),desc=props.get('Description'),layer=layer,x=fx,y=fy,a=fa,pads=pads,raw=fp))
    return out
if __name__=='__main__':
    pcb=load(sys.argv[1])
    for f in footprints(pcb):
        if any(l.startswith('B.') for p in f['pads'] for l in p['layers']) or f['layer']=='B.Cu':
            print(f['ref'],f['val'],f['layer'],round(f['x'],2),round(f['y'],2),f['a'])
            for p in f['pads']: print('   ',p['num'],p['type'],p['shape'],round(p['x'],2),round(p['y'],2),p['w'],p['h'],p['net'],p['layers'])
