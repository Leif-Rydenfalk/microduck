from pathlib import Path
import zipfile,json,hashlib
out=Path(__file__).parent.parent/'plates/HEAD-V9-candidate';src=out/'microduck-head-v9-clean.gate.gcode.3mf';dst=out/'microduck-head-v9.gcode.3mf';z=zipfile.ZipFile(src);original=json.loads(zipfile.ZipFile(out.parent/'HEAD-V5/microduck-head-v5.gcode.3mf').read('Metadata/project_settings.config'));cfg=json.loads(z.read('Metadata/project_settings.config'));cfg['filament_map_mode']=original['filament_map_mode']
with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as w:
 for n in z.namelist():w.writestr(n,json.dumps(cfg,indent=2) if n=='Metadata/project_settings.config' else z.read(n))
a=zipfile.ZipFile(dst);assert a.read('Metadata/plate_1.gcode')==z.read('Metadata/plate_1.gcode');diff={k:{'v5':original[k],'v9':cfg.get(k)} for k in original if original[k]!=cfg.get(k)};assert not diff,diff
proof={'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'original_project_setting_differences':diff,'restored_filament_map_mode':cfg['filament_map_mode'],'gcode_bytes_unchanged_from_slice':True};(out/'final-metadata-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
