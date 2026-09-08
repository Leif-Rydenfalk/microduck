#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""Independent native MuJoCo measurement of the exact browser bundle."""
import argparse,json,time
from pathlib import Path
import mujoco
import numpy as np

def measure(bundle,out):
    spec=json.loads((bundle/'study.json').read_text());m=mujoco.MjModel.from_xml_path(str(bundle/spec['model']));d=mujoco.MjData(m)
    d.qpos[:]=spec['initial_qpos'];d.ctrl[:]=d.qpos[7:];mujoco.mj_forward(m,d)
    t=time.process_time();peak_contacts=0;peak_torque=0;max_excess=0;min_z=float(d.qpos[2]);sample=None
    for i in range(2000):
        mujoco.mj_step(m,d)
        if not np.all(np.isfinite(d.qpos)):raise ValueError('Non-finite state')
        peak_contacts=max(peak_contacts,d.ncon);peak_torque=max(peak_torque,float(np.max(np.abs(d.actuator_force)))*1000);min_z=min(min_z,float(d.qpos[2]))
        for j in range(m.njnt):
            if m.jnt_type[j]!=mujoco.mjtJoint.mjJNT_HINGE:continue
            q=d.qpos[m.jnt_qposadr[j]];lo,hi=m.jnt_range[j];max_excess=max(max_excess,float(max(lo-q,q-hi,0))*180/np.pi)
        if i==200:sample=dict(time_s=d.time,root_mm=(d.qpos[:3]*1000).tolist(),contacts=d.ncon,max_torque_Nmm=float(np.max(np.abs(d.actuator_force)))*1000)
    elapsed=time.process_time()-t
    report=dict(engine=mujoco.__version__,steps=2000,simulated_seconds=float(d.time),cpu_seconds=elapsed,physics_steps_per_cpu_second=2000/elapsed,
        bodies=m.nbody-1,hinges=m.njnt-1,actuators=m.nu,geoms=m.ngeom,peak_contacts=peak_contacts,peak_torque_Nmm=peak_torque,max_limit_excess_deg=max_excess,min_root_z_mm=min_z*1000,
        after_201_steps=sample,finite_state='PASS',strength='CANNOT DETERMINE',standing_stability='FAIL' if min_z<.06 else 'CANNOT DETERMINE',
        scope=spec['scope'],note='Open-loop position targets; no feedback balance policy. A fall is a measured study outcome, not hidden by a fixed root or clipped output.')
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('bundle',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();measure(a.bundle,a.out)
