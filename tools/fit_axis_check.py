#!/usr/bin/env python3
"""fit_axis_check.py — does every hinge axis in the compiled MuJoCo model pass
through the bearing that carries it in placements.json?  Off-axis distance of
each bearing/servo centroid and the tilt between its principal axis and the
joint axis, at the zero pose. The 2026-09-09 run of this check found every
horizontal hinge anchored ~120 mm below its bearing because prove_fit.py drove
the free joint from an all-zero qpos instead of qpos0; after the fix every
carrying bearing is 0.02 mm off-axis, 0.0 deg tilt.

    ce-cad/bin/cad tools/fit_axis_check.py   -> out/fit/axis-check.log
"""
import json,os,sys
import numpy as np
REPO=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.argv=[sys.argv[0],'axis-check']; sys.path.insert(0,REPO+'/tools')
import prove_fit as pf
from cecad import meshfit as mf
M=pf.Model(); m,d,mj=M.m,M.d,M.mujoco
d.qpos[:]=M.qpos_for({}); mj.mj_forward(m,d)
W=M.world(M.zero)
def axis_of(tris):
    V=np.unique(tris.reshape(-1,3),axis=0); c=V.mean(0); u,s,vt=np.linalg.svd(V-c,full_matrices=False); return c,vt[2],s
for i in range(m.njnt):
    if m.jnt_type[i]!=mj.mjtJoint.mjJNT_HINGE: continue
    jn=mj.mj_id2name(m,mj.mjtObj.mjOBJ_JOINT,i); b=m.jnt_bodyid[i]
    Rb=np.asarray(d.xmat[b]).reshape(3,3); tb=np.asarray(d.xpos[b])*1000
    p=Rb@(np.asarray(m.jnt_pos[i])*1000)+tb; a=Rb@np.asarray(m.jnt_axis[i]); a/=np.linalg.norm(a)
    body=M.bname[b]; parent=M.bname[m.body_parentid[b]]
    print('JOINT %-16s body=%-16s parent=%-12s anchor=%s axis=%s'%(jn,body,parent,np.round(p,2),np.round(a,3)))
    # bearings and servos in body and parent
    for k in range(M.n):
        if M.body_of[k] not in (body,parent): continue
        lab=M.label[k]
        if 'bearing' not in lab and 'xl330' not in lab: continue
        c,ax,s=axis_of(W[k])
        # distance from joint axis line to mesh centroid, angle between axes
        v=c-p; dist=np.linalg.norm(v-np.dot(v,a)*a); ang=np.degrees(np.arccos(min(1,abs(np.dot(ax,a)))))
        if 'bearing' in lab:
            print('   %-58s centroid off-axis %6.2f mm   axis tilt %5.1f deg'%(lab,dist,ang))
        else:
            # servo: report the servo's own principal axes vs joint axis (which servo face axis aligns)
            V=np.unique(W[k].reshape(-1,3),axis=0); cc=V.mean(0); u,sv,vt=np.linalg.svd(V-cc,full_matrices=False)
            aligns=[np.degrees(np.arccos(min(1,abs(np.dot(vt[j],a))))) for j in range(3)]
            vv=cc-p; dd=np.linalg.norm(vv-np.dot(vv,a)*a)
            print('   %-58s centroid off-axis %6.2f mm   best-aligned principal axis tilt %5.1f deg'%(lab,dd,min(aligns)))
