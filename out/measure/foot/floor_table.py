import sys, json
sys.path.insert(0, '/Users/leifrydenfalk/dev/ce-workshop/ce-cad')
import numpy as np
from cecad import meshslice
REF='/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/reference/pollen-microduck-rl/assets/'
T = meshslice.load(REF+'sole_left.stl',1000)
XS = [29.35,29.6,30.0,30.5,31.0,31.5,32.5,33.5,35.0,36.5,38.0,40.0,44.0,48.0,52.0,56.0,60.0,62.0,64.0,65.5,67.0,68.0,68.8,69.4,70.0,70.35,70.6]
YS = [-12.4,-12.0,-11.5,-11.0,-10.5,-10.0,-9.0,-8.0,-7.0,-6.0,-5.0,-3.0,0.0,5.0,10.0,15.0,20.0,25.0,30.0,33.0,35.0,36.0,37.0,38.0,39.0,40.0,40.5,41.0,41.5,42.0,42.4]
tab = []
for x in XS:
    row = []
    for y in YS:
        r = meshslice.intervals(T,'z',x,y)
        row.append(round(r[0][0],3) if r else None)
    tab.append(row)
# fill None by nearest neighbour in row, else column
import copy
filled = copy.deepcopy(tab)
for i,row in enumerate(filled):
    vals = [v for v in row if v is not None]
    for j,v in enumerate(row):
        if v is None:
            # nearest non-None in the row
            best=None
            for k,w in enumerate(row):
                if w is not None and (best is None or abs(k-j)<abs(best[0]-j)): best=(k,w)
            if best: row[j]=best[1]
for i,row in enumerate(filled):
    if all(v is None for v in row):
        j = i+1 if i==0 else i-1
        filled[i] = list(filled[j])
        print('# row x=%.2f was empty; borrowed from x=%.2f'%(XS[i],XS[j]))
print('XS =', XS)
print('YS =', YS)
print('ZB = [')
for i,row in enumerate(filled):
    print('  [' + ','.join('%.3f'%v for v in row) + '],  # x=%.2f'%XS[i])
print(']')
# count raw empties
n_empty = sum(1 for row in tab for v in row if v is None)
print('# raw empty cells:', n_empty, 'of', len(XS)*len(YS))
json.dump({'XS':XS,'YS':YS,'ZB':filled}, open('/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/out/measure/foot/floor_table.json','w'))
