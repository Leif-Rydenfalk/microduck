import FreeCAD,json
from pathlib import Path
from types import SimpleNamespace
from cecad import triad,sheetcheck
from cecad.render import render
out=Path(__file__).resolve().parent/'lighting-study';out.mkdir(exist_ok=True)
p=triad.load(FreeCAD.newDocument('bottom_lighting'),'part:microduck-shin')
rows=[]
for intensity in (0.25,0.0):
 f=out/('bottom-ambient-'+str(intensity)+'.png')
 render(p,str(f),view=(-90,-90),W=1200,H=1184,ss=2,mode='pbr',projection='ortho',edges=True,bg=1.,env={'intensity':intensity},verbose=False)
 row={'ambient_environment_intensity':intensity,**sheetcheck.image_tone(SimpleNamespace(attrs={'href':str(f)}),str(out))}
 rows.append(row);print(row)
(out/'results.json').write_text(json.dumps(rows,indent=1))
