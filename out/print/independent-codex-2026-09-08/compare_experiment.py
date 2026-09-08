import zipfile,json,re,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
source=Path(__file__).with_name('analyze.py').read_text();parser=source[source.index('# Parse actual motion'):source.index("print('Parsed'")];out=Path(__file__).parent/'experiments';fig,axes=plt.subplots(3,3,figsize=(13,13));results=[]
for row,name in enumerate(['eye-ring-exact-stl','eye-ring-indexed-3mf','eye-ring-soup-3mf']):
 z=zipfile.ZipFile(next((out/name).glob('*.gcode.3mf')));exec(parser);model_layers=[]
 for i,l in enumerate(layers):
  if any(not f.startswith('Support') for o,f,w,zv,s in l['moves']):model_layers.append(i+1)
 results.append({'name':name,'total_layers':len(layers),'model_layers':model_layers})
 for col,i in enumerate([0,17,40]):
  ax=axes[row,col]
  for o,f,w,zv,s in layers[i]['moves']:ax.add_collection(LineCollection(s,colors='#bbb' if f.startswith('Support') else '#156499',linewidths=.7))
  ax.autoscale();ax.set_aspect('equal');ax.set_title(f'{name}\nLayer{i+1}, Z{layers[i]["z"]}')
fig.suptitle('Controlled identical-surface test: shared indices restore the missing body\nActual model extrusion blue; support grey; identical slicer profiles, checks ON');fig.tight_layout();fig.savefig(out/'vertex-sharing-controlled-test.png',dpi=160);(out/'comparison.json').write_text(json.dumps(results,indent=2))
