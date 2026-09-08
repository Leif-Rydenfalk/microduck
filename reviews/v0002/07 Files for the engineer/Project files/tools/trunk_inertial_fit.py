"""Does Pollen's trunk_base inertial (0.199224 kg) include the battery?
Measure: signed volume + centroid of every geom parented directly under trunk_base,
placed by the MJCF pos/quat, then least-squares fit densities under two hypotheses."""
import numpy as np, struct, json, xml.etree.ElementTree as ET, sys
ROOT='/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-simulator/'
def read_stl(p):
    b=open(p,'rb').read()
    n=struct.unpack('<I',b[80:84])[0]
    a=np.frombuffer(b[84:84+n*50],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))
    return a['v'].reshape(-1,3,3).astype(np.float64)
def quat2mat(q):
    w,x,y,z=q/np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def vol_centroid(tri):
    v0,v1,v2=tri[:,0],tri[:,1],tri[:,2]
    d=np.einsum('ij,ij->i',v0,np.cross(v1,v2))/6.0
    c=(v0+v1+v2)/4.0
    V=d.sum(); C=(d[:,None]*c).sum(0)/V
    return V,C
t=ET.parse(ROOT+'robot_allcollisions.xml')
scale=None
for m in t.iter('mesh'):
    pass
comp=t.find('compiler'); print('compiler',comp.attrib if comp is not None else None)
meshdir=comp.get('meshdir','') if comp is not None else ''
rows=[]
for b in t.iter('body'):
    if b.get('name')!='trunk_base': continue
    inert=b.find('inertial')
    M=float(inert.get('mass')); P=np.array(list(map(float,inert.get('pos').split())))
    for g in b.findall('geom'):
        if g.get('class')!='visual': continue
        name=g.get('mesh'); pos=np.array(list(map(float,g.get('pos').split()))); q=np.array(list(map(float,g.get('quat').split())))
        tri=read_stl(ROOT+'meshes/'+name+'.stl')  # metres? check bbox
        V,C=vol_centroid(tri)
        R=quat2mat(q); Cw=R@C+pos
        rows.append(dict(mesh=name,V_m3=float(V),C_local=C.tolist(),C_world=Cw.tolist(),bbox=(tri.reshape(-1,3).max(0)-tri.reshape(-1,3).min(0)).tolist()))
for r in rows: print(f"{r['mesh']:40s} V={r['V_m3']*1e6:9.3f} cm3  Cw={np.round(r['C_world'],4)} bbox={np.round(r['bbox'],4)}")
print('MJCF trunk inertial mass',M,'pos',P)
# hypotheses: printed parts share density rho_p; servos 18 g each (ROBOTIS); bearings: steel-ish, solve; battery mass m_b (free) or 0.
def fit(include_batt):
    printed=['right_shell','left_shell','trunk_base','power_support','banana_pcb_locker']
    A=[];  # unknowns: rho_p, rho_bearing, m_batt(if)
    # equations: total mass, COMx*M, COMz*M  (3 eq)
    cols=['rho_printed','rho_bearing']+(['m_batt'] if include_batt else [])
    Vp=sum(r['V_m3'] for r in rows if r['mesh'] in printed)
    Cp=sum(r['V_m3']*np.array(r['C_world']) for r in rows if r['mesh'] in printed)
    Vb=sum(r['V_m3'] for r in rows if r['mesh'].startswith('seeed'))
    Cb=sum(r['V_m3']*np.array(r['C_world']) for r in rows if r['mesh'].startswith('seeed'))
    ms=0.018; Cs=sum(np.array(r['C_world']) for r in rows if r['mesh']=='xl330')  # sum of 2 servo centroids
    bat=[r for r in rows if r['mesh']=='np_f970'][0]; Cbat=np.array(bat['C_world'])
    # mass eq
    rowsA=[[Vp,Vb]+([1.0] if include_batt else [])]; rhs=[M-2*ms]
    for ax in (0,2):
        rowsA.append([Cp[ax],Cb[ax]]+([Cbat[ax]] if include_batt else [])); rhs.append(M*P[ax]-ms*Cs[ax])
    A=np.array(rowsA); y=np.array(rhs)
    x,res,rk,sv=np.linalg.lstsq(A,y,rcond=None)
    pred=A@x
    print('\n== hypothesis battery','INCLUDED' if include_batt else 'EXCLUDED')
    for c,v in zip(cols,x): print('  ',c,'=',v)
    print('   residual mass/COM eqs:',(pred-y).tolist(),' |r|=',np.linalg.norm(pred-y))
    # also COM prediction
    mtot=x[0]*Vp+x[1]*Vb+2*ms+(x[2] if include_batt else 0)
    com=(x[0]*Cp+x[1]*Cb+ms*Cs+((x[2]*Cbat) if include_batt else 0))/mtot
    print('   predicted mass',mtot,'COM',com,' MJCF',M,P)
    return dict(cols=cols,x=x.tolist(),residual=(pred-y).tolist(),pred_mass=float(mtot),pred_com=com.tolist())
out=dict(rows=rows,mjcf_mass=M,mjcf_com=P.tolist(),fit_included=fit(True),fit_excluded=fit(False))
# Fixed-density test: PLA 1.24 g/cc printed parts (solid), steel bearing 7.85, servo 18 g, battery 99 g: what mass/COM results?
def fixed(rho_p,rho_b,mb):
    printed=['right_shell','left_shell','trunk_base','power_support','banana_pcb_locker']
    m=0;c=np.zeros(3)
    for r in rows:
        if r['mesh'] in printed: mi=rho_p*r['V_m3']
        elif r['mesh'].startswith('seeed'): mi=rho_b*r['V_m3']
        elif r['mesh']=='xl330': mi=0.018
        elif r['mesh']=='np_f970': mi=mb
        m+=mi; c+=mi*np.array(r['C_world'])
    return m,c/m
for mb in (0,0.099,0.095):
    m,c=fixed(1240,7850,mb); print(f'fixed PLA1.24 steel7.85 batt{mb*1000:.0f}g -> mass {m*1000:.2f} g COM {np.round(c,4)}')
out['fixed_density_cases']={str(mb):list(map(float,[fixed(1240,7850,mb)[0]]+fixed(1240,7850,mb)[1].tolist())) for mb in (0,0.099,0.095)}
json.dump(out,open('/private/tmp/resolve-power/trunk_fit.json','w'),indent=1)
