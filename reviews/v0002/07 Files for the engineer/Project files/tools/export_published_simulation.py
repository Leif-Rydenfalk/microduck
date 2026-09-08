#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""Use the exact ce-cad published assembly in the articulated MuJoCo study.

Published vertices are in world mm. This adapter places them in the MJCF's
zero-pose body frame (derived via mj_forward, no guessed transforms), then
exports the same body-local triangles to the visual bench and collision model.
No physical source is modified. Inertias remain sourced upstream assumptions.
"""
import argparse, hashlib, json, struct, sys
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import mujoco
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import export_viewer
from export_live_dynamics import export

def generate(published,out,evidence):
    evidence.mkdir(parents=True,exist_ok=True)
    source=ROOT/'sim/microduck_ours.xml'
    model=mujoco.MjModel.from_xml_path(str(source));data=mujoco.MjData(model);mujoco.mj_forward(model,data)
    tree=ET.parse(source);root=tree.getroot();asset=root.find('asset');compiler=root.find('compiler')
    meshdir=(source.parent/compiler.get('meshdir')).resolve()
    # Other source meshes retain their names and exact locations, including collisions.
    for mesh in root.findall('./asset/mesh'):
        mesh.set('name',mesh.get('name') or Path(mesh.get('file')).stem)
        mesh.set('file',str((meshdir/mesh.get('file')).resolve()))
    compiler.set('meshdir','.')
    bodies={b.get('name'):b for b in root.iter('body')}
    for b in bodies.values():
        for g in list(b.findall('geom')):
            if g.get('class')=='visual':b.remove(g)
            else:g.set('contype','3');g.set('conaffinity','3')
    snapshot=json.loads(published.read_text());rows=[];worst=0
    for i,part in enumerate(snapshot['parts']):
        name=part['name'];body=name.split('/')[0]
        if body not in bodies:raise ValueError('Published part has no articulated body: '+name)
        bid=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,body)
        world=np.array(part['positions']).reshape(-1,3)/1000
        rotation=data.xmat[bid].reshape(3,3)
        local=(world-data.xpos[bid])@rotation
        # Quantize exactly as the written binary STL does before checking the return transform.
        reconstructed=local.astype(np.float32).astype(float)@rotation.T+data.xpos[bid]
        error=float(np.max(np.abs(reconstructed-world)))*1000;worst=max(worst,error)
        indices=np.array(part['indices'],dtype=int).reshape(-1,3)
        triangles=local[indices].astype(np.float32)
        meshname='current_%03d__ours'%i;path=evidence/(meshname+'.stl')
        with path.open('wb') as f:
            f.write(b'ce-cad published assembly body-local metres'.ljust(80,b'\0'));f.write(struct.pack('<I',len(triangles)))
            for t in triangles:f.write(struct.pack('<12fH',0,0,0,*t.flatten(),0))
        ET.SubElement(asset,'mesh',name=meshname,file=str(path))
        ET.SubElement(bodies[body],'geom',name='current_%03d'%i,type='mesh',mesh=meshname,
                      **{'class':'visual','contype':'3','conaffinity':'3','rgba':' '.join(map(str,part['color'][:3]+[1]))})
        rows.append(dict(part=name,body=body,mesh=meshname,triangles=len(triangles),world_roundtrip_max_mm=error,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    used_meshes={g.get('mesh') for g in root.iter('geom') if g.get('mesh')}
    for mesh in list(asset.findall('mesh')):
        if mesh.get('name') not in used_meshes:asset.remove(mesh)
    xml=evidence/'current-assembly.xml';tree.write(xml,encoding='utf-8',xml_declaration=True)
    # The existing scene exporter consumes the resulting tree and exact triangle files.
    oldargv=sys.argv;sys.argv=['export_viewer','--out',str(out)]
    try:
        export_viewer.MJCF=str(xml);export_viewer.main()
    finally:sys.argv=oldargv
    scene=json.loads((out/'scene.json').read_text())
    for g in scene['geoms']:
        published_index=int(scene['meshes'][g['mesh']]['name'].split('_')[1])
        row=rows[published_index];part=snapshot['parts'][published_index]
        slug=part['name'].split('/',1)[1].split('#')[0]
        g.update(ref='part:'+slug,model=slug,label=slug.replace('microduck-','').replace('-',' '),color=part['color'][:3],ours=slug.startswith('microduck-'))
    scene['source']['published_mesh']=str(published)
    scene['source']['published_sha256']=hashlib.sha256(published.read_bytes()).hexdigest()
    (out/'scene.json').write_text(json.dumps(scene,indent=1)+'\n')
    export(xml,out/'live')
    proof=dict(source=str(published),source_sha256=hashlib.sha256(published.read_bytes()).hexdigest(),parts=len(rows),triangles=sum(r['triangles'] for r in rows),world_roundtrip_max_mm=worst,rows=rows,
      scope='All published triangles round-tripped through native MuJoCo zero-pose body frames. Collision shape is each triangle mesh convex hull, not a concave solid. Upstream inertias and actuator parameters retained, not recalibrated to the rebuilt parts.')
    (evidence/'published-mapping.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k!='rows'}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--published',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--evidence',type=Path,required=True)
    a=ap.parse_args();generate(a.published.resolve(),a.out.resolve(),a.evidence.resolve())
