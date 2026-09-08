from pathlib import Path
import sys,json,subprocess
sys.path.insert(0,'/Users/leifrydenfalk/dev/ce-workshop/ce-print-scheduler')
from scheduler import config,partgate
out=Path(__file__).parent
cfg=config.load();mc=next(m for m in cfg['printers'].values() if m.get('nickname')=='H2D AMS HT')
realrun=subprocess.run
counter=0
def capture(cmd,*args,**kw):
 global counter
 counter+=1
 result=realrun(cmd,*args,**kw)
 if isinstance(cmd,(list,tuple)) and any('Slicer.app' in str(x) or 'Studio.app' in str(x) for x in cmd):
  (out/f'command-{counter}.json').write_text(json.dumps(list(cmd),indent=2))
  (out/f'stdout-{counter}.log').write_text(str(result.stdout))
  for log in Path(kw.get('cwd','.')).glob('*.log'):
   (out/f'raw-{counter}-{log.name}').write_bytes(log.read_bytes())
  (out/f'stderr-{counter}.log').write_text(str(result.stderr))
 return result
subprocess.run=capture
res=partgate.gate([str(out.parents[1]/'stl/fixed/TPU/microduck-jaw-soft.stl')],mc,cfg.get('policy',{}),mc['model'],'TPU',nozzle_pair=['0.4','0.6'],keep_dir=str(out/'repro-jaw'))
(out/'repro-result.json').write_text(json.dumps(res,indent=2))
