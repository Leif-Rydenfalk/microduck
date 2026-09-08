import mujoco, numpy as np, json, xml.etree.ElementTree as ET
root='/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck'
xml=root+'/reference/pollen-microduck-rl/robot_walk.xml'
m=mujoco.MjModel.from_xml_path(xml); d=mujoco.MjData(m); mujoco.mj_forward(m,d)
def quat2mat(q):
    r=np.zeros(9); mujoco.mju_quat2Mat(r,np.array(q,dtype=float)); return r.reshape(3,3)
tree=ET.parse(xml); geoms=[]
for body in tree.iter('body'):
    bn=body.get('name')
    for g in body.findall('geom'):
        if g.get('mesh')=='xl330':
            pos=np.array([float(x) for x in g.get('pos','0 0 0').split()]); q=[float(x) for x in g.get('quat','1 0 0 0').split()]
            geoms.append((bn,pos,quat2mat(q)))
out=[]
for j in range(m.njnt):
    if m.jnt_type[j]!=mujoco.mjtJoint.mjJNT_HINGE: continue
    name=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_JOINT,j)
    child=m.jnt_bodyid[j]; parent=m.body_parentid[child]
    cn=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,child); pn=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,parent)
    anchor=d.xanchor[j]; axis=d.xaxis[j]/np.linalg.norm(d.xaxis[j])
    rows=[]
    for bn,pos,R in geoms:
        b=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,bn)
        Rb=d.xmat[b].reshape(3,3); pw=d.xpos[b]+Rb@pos; Rw=Rb@R
        hx=Rw[:,0]; dot=float(np.dot(hx,axis))
        v=pw-anchor; along=float(np.dot(v,axis))*1000; off=float(np.linalg.norm(v-np.dot(v,axis)*axis))*1000
        if abs(abs(dot)-1)<1e-3 and off<0.5:
            rows.append(dict(body=bn,body_is='child' if b==child else ('parent' if b==parent else 'OTHER:'+pn),horn_plus_x_dot_joint_axis=round(dot,4),origin_along_axis_mm=round(along,4),offaxis_mm=round(off,4),horn_face_world=[round(float(x),4) for x in hx],mesh_z_up_world=[round(float(x),4) for x in Rw[:,2]]))
    out.append(dict(joint=name,child=cn,parent=pn,axis_world=[round(float(x),4) for x in axis],anchor_world_mm=[round(float(x)*1000,3) for x in anchor],servo=rows))
json.dump(out,open('/private/tmp/resolve-servo/jointsides.json','w'),indent=1)
with open('/private/tmp/resolve-servo/jointsides.log','w') as f:
    for o in out:
        f.write('%-16s child=%-16s parent=%-16s axis=%s\n'%(o['joint'],o['child'],o['parent'],o['axis_world']))
        for c in o['servo']: f.write('     servo geom in %-16s (%s) horn(+x).axis=%+.3f origin_along=%+.3f mm off=%.3f mm\n'%(c['body'],c['body_is'],c['horn_plus_x_dot_joint_axis'],c['origin_along_axis_mm'],c['offaxis_mm']))
    f.write('xl330 geoms parsed: %d\n'%len(geoms))
