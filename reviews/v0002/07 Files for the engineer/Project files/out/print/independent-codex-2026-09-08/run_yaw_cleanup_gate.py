import sys,json
from pathlib import Path
sys.path.insert(0,'/Users/leifrydenfalk/dev/ce-workshop/ce-print-scheduler')
from scheduler import config,partgate
out=Path(__file__).parent/'experiments';doc=config.load();matches=[m for m in doc['printers'].values() if 'H2D' in m.get('model','')];mc=matches[0]
for stem in ['yaw-original.3mf','yaw-cleaned.3mf']:
 work=out/(stem.replace('.','-'));work.mkdir(exist_ok=True)
 print('BEGIN',stem,flush=True)
 res=partgate.gate([str(out/stem)],mc,doc.get('policy',{}),mc['model'],'PLA',nozzle_pair=['0.4','0.6'],keep_dir=str(work));(work/'result.json').write_text(json.dumps(res,indent=2))
