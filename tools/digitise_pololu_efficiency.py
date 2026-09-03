import numpy as np; from PIL import Image, ImageDraw
im=np.array(Image.open('/private/tmp/resolve-power/pololu-eff.png').convert('RGB')).astype(int)
# calibration from the measured grid: x lines at 164 (0 A), 244 (1 A), 324 (2 A) -> 80.0 px/A; y lines 75 (100%), 149 (90), 223 (80), 296 (70) -> 73.67 px per 10 %
x0=164.0; pxA=80.0; y100=75.0; pxper10=(296-75)/3.0
def A2px(A): return x0+A*pxA
def py2eff(py): return 100-(py-y100)/pxper10*10
targets={'6V blue':np.array([0,120,255]),'12V green':np.array([0,220,0]),'24V orange':np.array([255,140,0])}
out={}
for name,col in targets.items():
    mask=(np.abs(im-col).sum(2)<120)
    res=[]
    for A in (0.2,0.3,0.4,0.5,0.75,1.0,1.5,2.0):
        px=int(round(A2px(A)))
        ys=np.where(mask[:,px-1:px+2].any(1))[0]; ys=ys[(ys>60)&(ys<380)]
        res.append((A, round(float(py2eff(ys.mean())),2) if len(ys) else None, int(len(ys))))
    out[name]=res; print(name,res)
# sanity: the 6 V curve's peak should be ~97 % near 0.7-0.9 A per the legend reading
import json; json.dump({'calibration':{'x0_px':x0,'px_per_A':pxA,'y100_px':y100,'px_per_10pct':pxper10},'samples':out},open('pololu_eff_digitised.json','w'),indent=1)
