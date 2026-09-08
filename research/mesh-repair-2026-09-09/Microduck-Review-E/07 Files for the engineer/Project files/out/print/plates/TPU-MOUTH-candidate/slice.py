from pathlib import Path
import sys,json,copy
sys.path.insert(0,'/Users/leifrydenfalk/dev/ce-workshop/ce-print-scheduler')
from scheduler import config,partgate
out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).parent
cfg=config.load();mc=copy.deepcopy(next(m for m in cfg['printers'].values() if m.get('nickname')=='H2D AMS HT'))
mc['slice_overrides'].update(nozzle='0.6',process='0.18mm Balanced Quality @BBL H2D 0.6 nozzle')
mc['slice_overrides']['process_values'].update(filament_map=['2'],filament_map_mode='Manual')
mc['slice_overrides']['process_values'].pop('bridge_line_width',None)
res=partgate.gate([str(out/'microduck-mouth-tpu.3mf')],mc,cfg.get('policy',{}),mc['model'],'TPU',nozzle_pair=['0.4','0.6'],keep_dir=str(out/'sliced'))
(out/'partgate-result.json').write_text(json.dumps(res,indent=2))
print(json.dumps(res,indent=2))
