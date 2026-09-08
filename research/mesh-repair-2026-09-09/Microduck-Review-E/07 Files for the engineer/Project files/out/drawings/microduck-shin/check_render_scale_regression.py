import json, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image
from cecad.core import Part
from cecad.render import render
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p.parents[2]/'tools'))
from rendered_drawing import verify_render_scales
with tempfile.TemporaryDirectory() as td:
 box=Part('scale_fixture').box(20,10,4)
 f={};raster=Path(td)/'box.png'
 render(box,str(raster),view=(90,-90),W=220,H=220,ss=2,edges=False,bg=1.,mode='cad',framing=f,verbose=False)
 assert abs(f['pixels_per_model_mm']-10.)<1e-8,f
 arr=np.asarray(Image.open(raster).convert('RGB')); ys,xs=np.where(arr.min(axis=2)<245)
 assert abs((xs.max()-xs.min()+1)-200)<=3,(xs.min(),xs.max())
 assert abs((ys.max()-ys.min()+1)-100)<=3,(ys.min(),ys.max())
 cached={}
 render(box,str(raster),view=(90,-90),W=220,H=220,ss=2,edges=False,bg=1.,mode='cad',framing=cached,verbose=False)
 assert cached==f, (cached,f)
 source=p/'render-panel-next'/'microduck-shin.svg'
 panels=json.loads((source.parent/'layout-evidence.json').read_text())['panels']
 assert verify_render_scales(source,panels)['verdict']=='PASS'
 raw=source.read_text();bad=Path(td)/'bad.svg'
 import re
 bad.write_text(re.sub(r'RENDER 1 / SCALE [0-9.]+:1','RENDER 1 / SCALE 0.00000:1',raw,count=1))
 assert verify_render_scales(bad,panels)['verdict']=='FAIL'
 import xml.etree.ElementTree as ET
 tree=ET.parse(source);im=next(e for e in tree.iter() if e.tag.endswith('}image'))
 im.set('width',str(float(im.get('width'))*1.1));tree.write(bad)
 assert verify_render_scales(bad,panels)['verdict']=='FAIL'
 print('PASS: known 20x10 mm solid measures 200x100 raster pixels; exact camera scale; cache-hit metadata; altered scale label and paper width both rejected')
