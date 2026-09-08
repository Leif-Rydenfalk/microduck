from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures
p=Path(__file__).resolve().parent;root=p.parents[1];commit='2b25a48b08f1f17bc38c90bb03144c81fbd9ed07'
files=['microduck/config_mjcf_allcollisions.json','microduck/assets/top_head_shell.part','microduck/assets/noenoeil.part','microduck/assets/jaw_soft.part','microduck/assets/rim.part','microduck/assets/banana_pcb_locker.part']
def get(f):
 url='https://raw.githubusercontent.com/pollen-robotics/microduck_rl/'+commit+'/src/mjlab_microduck/robot/'+f;r={'path':f,'url':url,'commit':commit,'date':'2026-09-08'}
 try:
  b=urllib.request.urlopen(url,timeout=15).read();out='upstream-'+Path(f).name;(p/out).write_bytes(b);r.update(file=out,sha256=hashlib.sha256(b).hexdigest(),matches_local=(root/'reference/pollen-microduck-rl-develop'/f).read_bytes()==b)
 except Exception as e:r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:r=list(ex.map(get,files))
(p/'pinned-sources.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
