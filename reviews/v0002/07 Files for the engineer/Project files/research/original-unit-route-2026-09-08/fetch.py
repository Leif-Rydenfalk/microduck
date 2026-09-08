from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures
p=Path(__file__).resolve().parent
urls={'product':'https://store.pollen-robotics.com/products/microduck','variants':'https://store.pollen-robotics.com/products/microduck.js','shipping':'https://store.pollen-robotics.com/policies/shipping-policy','landing':'https://pollen-robotics.com/microduck/'}
def get(kv):
 k,u=kv;r={'id':k,'url':u,'fetched':'2026-09-08'}
 try:
  b=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read();f=k+('.json' if k=='variants' else '.html');(p/f).write_bytes(b);r.update(file=f,sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:r=list(ex.map(get,urls.items()))
(p/'manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
if (p/'variants.json').exists():
 d=json.loads((p/'variants.json').read_text());print([{k:v.get(k) for k in ['id','title','sku','available','price','inventory_management']} for v in d['variants']])
