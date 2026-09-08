#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""Freeze a self-contained, hashed MJCF bundle for ce-cad's browser solver.

All visual geometry is included in full-contact collision detection (MuJoCo
convex hulls, with parent-child collision filtering). Inertias and actuator
parameters remain upstream assumptions. This is explicitly not FEA or a fit
certificate. Existing input files are never modified.
"""
import argparse, hashlib, json, os, shutil, sys
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sim'))
from common import scene_xml, DEFAULT_POSE, JOINT_NAMES

def export(source, out):
    out.mkdir(parents=True,exist_ok=True)
    root=ET.fromstring(scene_xml(str(source)))
    compiler=root.find('compiler');meshdir=Path(compiler.get('meshdir'));compiler.set('meshdir','.')
    root.find('option').set('timestep','0.002')
    files=[]
    for mesh in root.findall('./asset/mesh'):
        mesh.set('name',mesh.get('name') or Path(mesh.get('file')).stem)
        p=Path(mesh.get('file'));p=p if p.is_absolute() else meshdir/p
        content=p.read_bytes();digest=hashlib.sha256(content).hexdigest()
        name=digest[:16]+p.suffix.lower();target=out/name
        if not target.exists():target.write_bytes(content)
        mesh.set('file',name)
        if not any(f['name']==name for f in files):files.append(dict(name=name,url=name,sha256=digest,source=str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)))
    # Variant is read from source, never quietly changes the input model's filtering.
    xml=ET.tostring(root,encoding='utf-8');(out/'robot.xml').write_bytes(xml)
    files.append(dict(name='robot.xml',url='robot.xml',sha256=hashlib.sha256(xml).hexdigest(),source=str(source.relative_to(ROOT))))
    doc=dict(format='cecad-mujoco-study-1',model='robot.xml',engine='MuJoCo 3.12.0',
       units={'geometry':'m internally; dashboard mm','angles':'rad internally; dashboard degrees'},
       source=str(source.relative_to(ROOT)),joints=JOINT_NAMES,
       initial_qpos=[0,0,.12,1,0,0,0]+DEFAULT_POSE.tolist(),files=files,
       scope='Rigid-body dynamics with gravity, actuator forces, joint limits and full-body/floor convex-hull contacts. Adjacent parent-child body contact is filtered by MuJoCo. Upstream inertia, friction and servo parameters are assumptions; no deformation, cable dynamics or physical strength qualification.',
       hardware='Current assembly names ROBOTIS XL330-M288-T. Upstream actuator fit is not a measured torque curve for the assembled robot. No cheaper-servo substitution has been made by this exporter.')
    # Bind every named hinge to its compiled parent/child, local frame and actuator.
    import mujoco
    compiled=mujoco.MjModel.from_xml_path(str(out/'robot.xml'))
    constraints=[]
    for name in JOINT_NAMES:
        jid=mujoco.mj_name2id(compiled,mujoco.mjtObj.mjOBJ_JOINT,name)
        bid=int(compiled.jnt_bodyid[jid]);parent=int(compiled.body_parentid[bid])
        actuators=[i for i in range(compiled.nu) if compiled.actuator_trnid[i,0]==jid]
        constraints.append(dict(id=name,kind='revolute',body=mujoco.mj_id2name(compiled,mujoco.mjtObj.mjOBJ_BODY,bid),
            parent=mujoco.mj_id2name(compiled,mujoco.mjtObj.mjOBJ_BODY,parent),
            child_anchor_mm=(compiled.jnt_pos[jid]*1000).tolist(),child_axis=compiled.jnt_axis[jid].tolist(),
            limits_deg=(compiled.jnt_range[jid]*180/3.141592653589793).tolist(),free_axes=['rz_about_named_axis'],
            constrained_dof=5,actuators=[dict(index=i,force_range_Nmm=(compiled.actuator_forcerange[i]*1000).tolist(),
                parameters_status='upstream fitted assumptions, not measured on this build') for i in actuators]))
    doc['constraints']=constraints
    (out/'constraint-map.json').write_text(json.dumps(dict(format='cecad-articulated-constraints-1',length_unit='mm',angle_unit='deg',
        base='free: 3 translation and 3 rotation degrees of freedom',constraints=constraints,
        scope='Compiled MJCF joint frames and limits. No native SolidWorks/FreeCAD import validation or fastener/strength qualification.'),indent=2)+'\n')
    (out/'study.json').write_text(json.dumps(doc,indent=2)+'\n')
    print(json.dumps({'assets':len(files),'bytes':sum((out/f['name']).stat().st_size for f in files),'out':str(out)}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=ROOT/'sim/microduck_ours_fullcontact.xml');ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();export(a.source,a.out)
