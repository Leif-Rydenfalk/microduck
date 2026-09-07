import json, os, struct, sys, time, zipfile, re, subprocess
import numpy as np
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-print-scheduler')
from scheduler import slicer, queue, config
SCR='/private/tmp/claude-501/-Users-leifrydenfalk-dev/f5f13e03-e37d-40f7-b905-4faa16e201c7/scratchpad'
STL=os.environ.get('STLDIR','/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/out/print/stl/oriented/PLA')
fp=json.load(open(SCR+'/footprints.json'))
GROUPS=[('head',['top-head-shell','bottom-head-shell','jaw','face-part','motor-support','yaw-roll-motion','neck-pitch-bracket','eye-ring','m12-lens-holder','neck-plate','neck-plate']),
        ('trunk',['trunk-shell-left','trunk-shell-right','power-support','trunk-base','banana-pcb-locker']),
        ('hips',['yaw2roll','yaw2roll','bearing-roll','bearing-roll','hip-bracket','hip-bracket']),
        ('upper legs',['upper-leg-left','upper-leg-right','upper-leg-rigidity-plate','upper-leg-rigidity-plate']),
        ('shins',['shin','shin']),('ankles',['ankle-left','ankle-right']),('feet',['foot-left','foot-right'])]
MARGIN=3.0; GAP=float(__import__('os').environ.get('GAP','4')); BED=(300.0,320.0)
SUPPORTED={'ankle-left','ankle-right','bottom-head-shell','foot-left','foot-right','motor-support','neck-pitch-bracket','power-support','top-head-shell','upper-leg-left','upper-leg-right','yaw-roll-motion'}
PAD=float(__import__('os').environ.get('PAD','6'))
SKIP=set(x for x in __import__('os').environ.get('SKIP','').split(',') if x)
GROUPS=[(g,[x for x in sl if x not in SKIP]) for g,sl in GROUPS]  # extra clearance each side of a part that gets supports
W=BED[0]-2*MARGIN+GAP; H=BED[1]-2*MARGIN+GAP
# ---- maxrects, best short side fit, rotation allowed
class MaxRects:
    def __init__(s,W,H): s.free=[[0,0,W,H]]; s.placed=[]
    def _score(s,w,h):
        best=None
        for i,(fx,fy,fw,fh) in enumerate(s.free):
            for rot in (False,True):
                ww,hh=(h,w) if rot else (w,h)
                if ww<=fw and hh<=fh:
                    sc=(min(fw-ww,fh-hh), max(fw-ww,fh-hh))
                    if best is None or sc<best[0]: best=(sc,fx,fy,ww,hh,rot)
        return best
    def place(s,w,h):
        b=s._score(w,h)
        if not b: return None
        _,x,y,ww,hh,rot=b; r=[x,y,ww,hh]
        nf=[]
        for f in s.free:
            fx,fy,fw,fh=f
            if x>=fx+fw or x+ww<=fx or y>=fy+fh or y+hh<=fy: nf.append(f); continue
            if x>fx: nf.append([fx,fy,x-fx,fh])
            if x+ww<fx+fw: nf.append([x+ww,fy,fx+fw-(x+ww),fh])
            if y>fy: nf.append([fx,fy,fw,y-fy])
            if y+hh<fy+fh: nf.append([fx,y+hh,fw,fy+fh-(y+hh)])
        # prune contained
        pr=[]
        for i,a in enumerate(nf):
            if any(j!=i and b[0]<=a[0] and b[1]<=a[1] and b[0]+b[2]>=a[0]+a[2] and b[1]+b[3]>=a[1]+a[3] for j,b in enumerate(nf)): continue
            pr.append(a)
        s.free=pr; s.placed.append(r); return (x,y,rot)
def snapshot(m): return ([list(f) for f in m.free],[list(p) for p in m.placed])
def restore(m,snap): m.free,m.placed=[list(f) for f in snap[0]],[list(p) for p in snap[1]]
mr=MaxRects(W,H); layout=[]; skipped=[]
def try_item(slug):
    f=fp[f'microduck-{slug}']; pad=PAD if slug in SUPPORTED else 0.0
    w,h=f['w']+GAP+2*pad,f['h']+GAP+2*pad
    r=mr.place(w,h)
    if not r: return None
    x,y,rot=r; return dict(slug=slug,x=x+MARGIN+pad,y=y+MARGIN+pad,rot90=rot,w=(f['h'] if rot else f['w']),h=(f['w'] if rot else f['h']),z=f['z'],prerot=f['rot_deg'],pad=pad)
stop=False
for gname,slugs in GROUPS:
    snap=snapshot(mr); got=[]
    order=sorted(slugs,key=lambda s:-fp[f'microduck-{s}']['w']*fp[f'microduck-{s}']['h'])
    for s in order:
        it=try_item(s)
        if it: got.append(it)
        else: break
    if len(got)==len(slugs): layout+=got; print(f'group {gname}: all {len(slugs)} placed'); continue
    restore(mr,snap); got=[]
    for s in order:
        it=try_item(s)
        if it: got.append(it)
        else: skipped.append(s)
    layout+=got; print(f'group {gname}: {len(got)}/{len(slugs)} fit individually, skipped {skipped}'); stop=True; break
used=sum(i['w']*i['h'] for i in layout); print(f'{len(layout)} pieces, footprint {used:.0f} mm2 of {(BED[0]-2*MARGIN)*(BED[1]-2*MARGIN):.0f}; extent x {min(i["x"] for i in layout):.1f}..{max(i["x"]+i["w"] for i in layout):.1f}  y {min(i["y"] for i in layout):.1f}..{max(i["y"]+i["h"] for i in layout):.1f}')
# ---- meshes -> 3MF with baked transforms
def read(p):
    b=open(p,'rb').read(); n=struct.unpack('<I',b[80:84])[0]; d=np.frombuffer(b[84:84+n*50],dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]); return d['v'].reshape(-1,3).astype(float)
objs=[]
for i,it in enumerate(layout):
    V=read(f"{STL}/microduck-{it['slug']}.stl")
    a=np.radians(-it['prerot']) + (np.pi/2 if it['rot90'] else 0)
    R=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]]); Wv=V@R.T; Wv-=Wv.min(0)
    bb=Wv.max(0); assert abs(bb[0]-it['w'])<0.6 and abs(bb[1]-it['h'])<0.6, (it['slug'],bb,it['w'],it['h'])
    Wv[:,0]+=it['x']; Wv[:,1]+=it['y']; it['bbox']=[round(float(x),2) for x in Wv.min(0)]+[round(float(x),2) for x in Wv.max(0)]
    assert Wv[:,0].max()<=BED[0]-MARGIN+0.01 and Wv[:,1].max()<=BED[1]-MARGIN+0.01
    objs.append((i+1,f"microduck-{it['slug']}",Wv))
# overlap check on real bboxes
for i in range(len(layout)):
    for j in range(i+1,len(layout)):
        a,b=layout[i]['bbox'],layout[j]['bbox']
        assert a[3]<=b[0] or b[3]<=a[0] or a[4]<=b[1] or b[4]<=a[1], ('overlap',layout[i]['slug'],layout[j]['slug'])
out3=SCR+'/microduck-head-down-compact.3mf'
with zipfile.ZipFile(out3,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    parts=['<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n<resources>\n']
    for oid,name,Wv in objs:
        parts.append(f'<object id="{oid}" name="{name}" type="model"><mesh><vertices>\n')
        parts.append(''.join(f'<vertex x="{v[0]:.4f}" y="{v[1]:.4f}" z="{v[2]:.4f}"/>\n' for v in Wv))
        n=len(Wv)//3
        parts.append('</vertices><triangles>\n'+''.join(f'<triangle v1="{3*k}" v2="{3*k+1}" v3="{3*k+2}"/>\n' for k in range(n))+'</triangles></mesh></object>\n')
    parts.append('</resources>\n<build>\n'+''.join(f'<item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n' for oid,_,_ in objs)+'</build>\n</model>\n')
    z.writestr('3D/3dmodel.model',''.join(parts))
print('3mf written', os.path.getsize(out3)//1024,'KB'); json.dump(layout,open(SCR+'/layout.json','w'),indent=1)
if os.environ.get('PACK_ONLY'): sys.exit(0)
# ---- slice through the farm's slicer, arrange/orient OFF
doc=config.load(); ps=doc.get('printers'); ps=ps.values() if isinstance(ps,dict) else ps
mc=[p for p in ps if p.get('serial')=='0947BJ610900152'][0]; policy=doc.get('policy',{})
real_run=subprocess.run
def patched(cmd,*a,**k):
    c=list(cmd)
    for flag in ('--arrange','--orient'):
        if flag in c: c[c.index(flag)+1]='0'
    c=[x for x in c if x!='--allow-rotations']
    open(SCR+'/slice_cmd.txt','w').write(' '.join(repr(x) for x in c)); return real_run(c,*a,**k)
slicer.subprocess.run=patched
PROJ=os.path.expanduser('~/.config/ce-print-scheduler/projects'); name='microduck-head-down-compact_0001.gcode.3mf'
import copy
for tag,pv in (('tree',{"enable_support":"1","support_type":"tree(auto)","support_on_build_plate_only":"1"}),('normal',{"enable_support":"1","support_type":"normal(auto)","support_on_build_plate_only":"1"})):
    m2=copy.deepcopy(mc); m2['slice_overrides']['process_values']=pv
    t0=time.time(); rec=slicer.slice_plate([out3],PROJ,name,'Bambu Lab H2D','PLA',policy=policy,machine_cfg=m2,timeout=1800)
    err=(rec.get('error') or '').replace('Error: Not precalculated Placeable areas requested, radius 0, layer 0, critical: 0\n','')
    print(tag,'slice %.0fs ->'%(time.time()-t0), err[-300:] if err else {k:v for k,v in rec.items() if k not in ('said','stdout')})
    if not rec.get('error'): print('USING', tag, pv); break
else:
    import glob; lg=sorted(glob.glob(PROJ+'/00000.log'),key=os.path.getmtime); print(open(lg[-1]).read()[-800:] if lg else 'no orca log'); sys.exit(1)
path=rec['path']; ok,why=slicer._stamp_model_id(path,'O1D'); print('stamp:',ok,why)
z=zipfile.ZipFile(path); si=z.read('Metadata/slice_info.config').decode(); ms=z.read('Metadata/model_settings.config').decode(); c=json.loads(z.read('Metadata/project_settings.config'))
print('plates:', si.count('<plate>'), '| filament rows:', re.findall(r'<filament [^>]*>',si)[:3]); print('prediction s:', re.findall(r'prediction" value="([^"]+)"',si), 'weight:', re.findall(r'weight" value="([^"]+)"',si))
print('objects in file:', len(set(re.findall(r'key="name" value="([^"]+)"',ms))), 'unique names, placements:', len(re.findall(r'<item ',z.read('3D/3dmodel.model').decode())))
print({k:c.get(k) for k in ('printer_settings_id','print_settings_id','filament_settings_id','brim_type','brim_width','enable_support','support_type','curr_bed_type','nozzle_diameter')})
# positions check: re-read build items -> bbox per object
model=z.read('3D/3dmodel.model').decode()
comps={oid:re.search(r'p:path="([^"]+)" objectid="(\d+)"[^>]*transform="([^"]+)"',b).groups() for oid,b in re.findall(r'<object id="(\d+)"[^>]*type="model">(.*?)</object>',model,re.S)}
def T(s):
    v=[float(x) for x in s.split()]; M=np.eye(4); M[:3,:3]=np.array(v[:9]).reshape(3,3).T; M[:3,3]=v[9:12]; return M
mx_x=0; hs=[]
for oid,tr in re.findall(r'<item objectid="(\d+)"[^>]*transform="([^"]+)"',model):
    p_,objid,ct=comps[oid]; x=z.read(p_.lstrip('/')).decode(); ob=re.search(r'<object id="%s".*?</object>'%objid,x,re.S).group(0)
    V=np.array([[float(a),float(b),float(cc)] for a,b,cc in re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"',ob)]); Wv=(np.c_[V,np.ones(len(V))]@(T(tr)@T(ct)).T)[:,:3]
    mx_x=max(mx_x,Wv[:,0].max()); hs.append(round(float(np.ptp(Wv[:,2])),1))
print('max x in sliced file: %.1f (must be < 300); heights:'%mx_x, sorted(hs))
json.dump(dict(path=path,rec={k:v for k,v in rec.items() if k not in ('said',)},layout=layout),open(SCR+'/compact_result.json','w'),indent=1)
