from pathlib import Path
import urllib.request,concurrent.futures,json,hashlib,re,html
p=Path(__file__).resolve().parent
urls={'pololu':'https://www.pololu.com/product/3419','sparkfun':'https://www.sparkfun.com/sparkfun-qwiic-mini-tof-imager-vl53l5cx.html','neewer':'https://neewer.com/products/batteries-chargers-66600244.js','next':'https://www.nextbatteries.com/products/sony-np-f550-battery-2-pack-2600mah-l-series-dual-charger.js','pollen':'https://store.pollen-robotics.com/products/charger-pack.js','deity':'https://deitymic.com/products/np-f550/','duracell':'https://www.duracellcharge.info/en/product/replacement-sony-np-f330-np-f550-battery/'}
def fetch(pair):
 k,u=pair;r={'id':k,'url':u,'fetched':'2026-09-08'}
 try:
  b=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read();f=k+('.json' if u.endswith('.js') else '.html');(p/f).write_bytes(b);r.update(file=f,sha256=hashlib.sha256(b).hexdigest());t=re.sub(r'<(script|style)\b.*?</\1>','',b.decode(errors='replace'),flags=re.S|re.I);(p/(k+'.txt')).write_text(re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',t))))
 except Exception as e:r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as ex:r=list(ex.map(fetch,urls.items()))
(p/'manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
