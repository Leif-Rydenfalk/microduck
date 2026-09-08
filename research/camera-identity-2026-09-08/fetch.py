from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures,re,html
p=Path(__file__).resolve().parent
headers={'User-Agent':'Mozilla/5.0'}
def raw(u):return urllib.request.urlopen(urllib.request.Request(u,headers=headers),timeout=30).read()
commit=json.loads(raw('https://api.github.com/repos/pollen-robotics/microduck/commits/main'))['sha']
urls={'seeed':'https://www.seeedstudio.com/IMX-219-CMOS-camera-module-M12-and-CS-camera-available-p-5372.html','uctronics':'https://www.uctronics.com/camera-modules/camera-for-nvidia/arducam-8-mp-sony-imx219-m12-mount-low-distortion-camera-module-for-nvidia-jetson-nano.html','welectron':'https://www.welectron.com/Arducam-B0183-IMX219-Low-Distortion-M12-Mount-Camera-Module-for-NVIDIA-Jetson-Nano-Xavier-NX_1','radxa':'https://docs.radxa.com/en/zero/zero3/accessories/camera','presskit':'https://pollen-robotics.com/microduck/press-kit/','runtime':'https://raw.githubusercontent.com/pollen-robotics/microduck/'+commit+'/mediad/src/main.rs','bringup':'https://raw.githubusercontent.com/pollen-robotics/microduck/'+commit+'/docs/project/media-bringup.md','adafruit':'https://www.adafruit.com/product/5211','pimoroni':'https://shop.pimoroni.com/en-us/products/camera-cable-raspberry-pi-zero-edition'}
def get(kv):
 k,u=kv;r={'id':k,'url':u,'fetched':'2026-09-08'}
 try:
  b=raw(u);f=k+('.rs' if k=='runtime' else '.md' if k=='bringup' else '.html');(p/f).write_bytes(b);r.update(file=f,sha256=hashlib.sha256(b).hexdigest());s=re.sub(r'<(script|style)\b.*?</\1>','',b.decode(errors='replace'),flags=re.S|re.I);t=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s)));(p/(k+'.txt')).write_text(t)
 except Exception as e:r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:r=list(ex.map(get,urls.items()))
(p/'manifest.json').write_text(json.dumps({'runtime_commit':commit,'sources':r},indent=2)+'\n');print(r)
