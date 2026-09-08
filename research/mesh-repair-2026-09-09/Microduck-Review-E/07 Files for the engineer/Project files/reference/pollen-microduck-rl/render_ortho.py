import sys,struct,math,os
sys.path.insert(0,'/private/tmp/claude-501/-Users-leifrydenfalk/191ca988-e752-45fb-a6f7-89dde34532e7/scratchpad/microduck/pylib')
from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET
def qmul(a,b):
    w1,x1,y1,z1=a; w2,x2,y2,z2=b
    return (w1*w2-x1*x2-y1*y2-z1*z2, w1*x2+x1*w2+y1*z2-z1*y2, w1*y2-x1*z2+y1*w2+z1*x2, w1*z2+x1*y2-y1*x2+z1*w2)
def qrotm(q):
    w,x,y,z=q
    return [[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
def mv(M,v): return (M[0][0]*v[0]+M[0][1]*v[1]+M[0][2]*v[2], M[1][0]*v[0]+M[1][1]*v[1]+M[1][2]*v[2], M[2][0]*v[0]+M[2][1]*v[1]+M[2][2]*v[2])
def norm(q):
    n=math.sqrt(sum(c*c for c in q)); return tuple(c/n for c in q)
def axang(axis,ang):
    s=math.sin(ang/2); return norm((math.cos(ang/2),axis[0]*s,axis[1]*s,axis[2]*s))
meshes={}
def load(name):
    if name in meshes: return meshes[name]
    p=f"assets/{name}.stl"
    if not os.path.exists(p): meshes[name]=[]; return []
    b=open(p,"rb").read(); n=struct.unpack("<I",b[80:84])[0]
    tris=[]
    for i in range(n):
        off=84+i*50+12
        tris.append(tuple(struct.unpack_from('<3f',b,off+k*12) for k in range(3)))
    meshes[name]=tris; return tris
root=ET.parse('robot_walk.xml').getroot()
# pose: STAND keyframe joint angles by order of joints
stand=[0,-0.08726646259971647,-0.457924,-0.004940,0.452984, 0.3490658503988659,0.3490658503988659,0,0, 0,0.08726646259971647,0.457924,0.004940,-0.452984]
pose=sys.argv[1] if len(sys.argv)>1 else 'STAND'
angles=stand if pose=='STAND' else [0]*14
jidx=[0]
tris_world=[]  # (verts, colorkey)
def walk(body, ppos, pq):
    pos=tuple(float(v) for v in body.get('pos','0 0 0').split())
    q=norm(tuple(float(v) for v in body.get('quat','1 0 0 0').split()))
    R=qrotm(pq); wpos=tuple(ppos[i]+mv(R,pos)[i] for i in range(3)); wq=qmul(pq,q)
    j=body.find('joint')
    if j is not None:
        ax=tuple(float(v) for v in j.get('axis').split()); a=angles[jidx[0]]; jidx[0]+=1
        wq=qmul(wq,axang(ax,a))
    Rb=qrotm(wq)
    for g in body.findall('geom'):
        if g.get('class')!='visual' or g.get('type')!='mesh': continue
        m=g.get('mesh'); gp=tuple(float(v) for v in g.get('pos','0 0 0').split()); gq=norm(tuple(float(v) for v in g.get('quat','1 0 0 0').split()))
        Rg=qrotm(gq)
        for t in load(m):
            vs=[]
            for v in t:
                lv=mv(Rg,v); lv=(lv[0]+gp[0],lv[1]+gp[1],lv[2]+gp[2])
                wv=mv(Rb,lv); vs.append((wv[0]+wpos[0],wv[1]+wpos[1],wv[2]+wpos[2]))
            tris_world.append((vs,m))
    for c in body.findall('body'): walk(c,wpos,wq)
for b in root.find('worldbody').findall('body'): walk(b,(0,0,0),(1,0,0,0))
print('tris',len(tris_world))
pal={'left_shell':(240,200,120),'right_shell':(240,200,120),'trunk_shell_left':(247,230,203),'trunk_shell_right':(247,230,203),'top_head_shell':(247,230,203),'bottom_head_shell':(247,230,203),'jaw':(255,140,40),'jaw_soft':(255,140,40),'soft_mouth_top':(255,140,40),'face_part':(60,60,60),'noenoeil':(30,30,30),'xl330':(90,90,90),'np_f970':(50,50,50)}
def render(view, out, scale=4.0):
    # view: (u axis, v axis, depth axis sign) in world coords; z up
    W=1400; H=1400
    def proj(p):
        if view=='front': u,v,d=-p[1],p[2],p[0]      # look from +x toward -x
        elif view=='side': u,v,d=p[0],p[2],-p[1]     # look from -y (left side)... show +x to right
        elif view=='top': u,v,d=p[0],p[1],p[2]
        elif view=='back': u,v,d=p[1],p[2],-p[0]
        return (u*1000*scale+W/2, H-60-v*1000*scale if view!='top' else H/2 - v*1000*scale, d)
    img=Image.new('RGB',(W,H),(255,255,255)); dr=ImageDraw.Draw(img)
    polys=[]
    for vs,m in tris_world:
        pv=[proj(p) for p in vs]
        # normal for shading
        ax=(vs[1][0]-vs[0][0],vs[1][1]-vs[0][1],vs[1][2]-vs[0][2]); bx=(vs[2][0]-vs[0][0],vs[2][1]-vs[0][1],vs[2][2]-vs[0][2])
        n=(ax[1]*bx[2]-ax[2]*bx[1], ax[2]*bx[0]-ax[0]*bx[2], ax[0]*bx[1]-ax[1]*bx[0]); ln=math.sqrt(sum(c*c for c in n)) or 1
        L=(0.5,0.3,0.8); sh=abs(sum(n[i]*L[i] for i in range(3))/ln)
        col=pal.get(m,(200,200,200)); col=tuple(int(c*(0.45+0.55*sh)) for c in col)
        polys.append((sum(p[2] for p in pv)/3, [(p[0],p[1]) for p in pv], col))
    polys.sort(key=lambda t:t[0])
    for d,pts,col in polys: dr.polygon(pts,fill=col)
    # scale bar 100 mm and grid lines every 50 mm
    for k in range(0,6):
        y=H-60-k*50*scale
        dr.line([(20,y),(W-20,y)],fill=(200,200,255)); dr.text((22,y-12),f"{k*50} mm",fill=(0,0,200))
    dr.line([(W/2-50*scale,H-30),(W/2+50*scale,H-30)],fill=(255,0,0),width=3); dr.text((W/2-30,H-25),"100 mm",fill=(255,0,0))
    if view=='top':
        for k in range(-3,4):
            x=W/2+k*50*scale; dr.line([(x,20),(x,H-20)],fill=(200,200,255)); dr.text((x+2,22),f"{k*50}",fill=(0,0,200))
    img.save(out); print(out)
os.makedirs('renders',exist_ok=True)
for v in ['front','side','back','top']: render(v, f'renders/{pose}_{v}.png')
