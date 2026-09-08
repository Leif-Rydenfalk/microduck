from pathlib import Path
import urllib.request,urllib.error,json,hashlib,concurrent.futures,subprocess
p=Path(__file__).resolve().parent
base='https://cad.onshape.com';did='804927696f06d877f3f1803e';wid='5b75db19292e71970de02dee';eid='ef6e972847fec8d82570b35e';mid='2f167ea7efece4caa36b89eb';studio='cceb83ef371fcd79b077022f'
urls={'document-page':base+f'/documents/{did}/w/{wid}/e/{eid}','document-api':base+f'/api/v6/documents/{did}','elements-api':base+f'/api/v6/documents/d/{did}/w/{wid}/elements','parts-pinned-api':base+f'/api/v6/parts/d/{did}/m/{mid}/e/{studio}','official-export-docs':'https://onshape-public.github.io/docs/api-adv/translation/','official-auth-docs':'https://onshape-public.github.io/docs/auth/apikeys/'}
def get(x):
 name,url=x;r={'id':name,'url':url,'method':'GET','authenticated':False,'date':'2026-09-08'}
 try:
  q=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json,text/html'}),timeout=20);b=q.read();r.update(status=q.status,content_type=q.headers.get('Content-Type'),final_url=q.url)
 except urllib.error.HTTPError as q:b=q.read();r.update(status=q.code,content_type=q.headers.get('Content-Type'))
 except Exception as q:r['error']=str(q);return r
 f=name+'.txt';(p/f).write_bytes(b);r.update(file=f,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));return r
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:m=list(ex.map(get,urls.items()))
(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print([{k:x.get(k) for k in ['id','status','bytes','error']} for x in m])
r=subprocess.run(['/Users/leifrydenfalk/dev/ce-workshop/ce-onshape/bin/onshape','doctor'],capture_output=True,text=True);(p/'doctor.txt').write_text(r.stdout+r.stderr)
