from pathlib import Path
import urllib.request,concurrent.futures,json,hashlib,datetime
import re,html
D=Path(__file__).parent
urls={'pegnitz-m2x5':'https://www.pegnitz-schrauben.de/100-x-Zylinderschr-mI-6kt-ISO-4762-129-M2-x-5-blank-schwarz','pegnitz-m2x10':'https://www.pegnitz-schrauben.de/100-x-Zylinderschr-mI-6kt-ISO-4762-129-M2-x-10-blank-schwarz','pegnitz-m25x8':'https://www.pegnitz-schrauben.de/100-x-Zylinderschr-mI-6kt-ISO-4762-129-M25-x-8-blank-schwarz','misumi-cn':'https://www.misumi.com.cn/pdf/fa/2018/p1861.pdf','misumi-jp':'https://jp.misumi-ec.com/vona2/detail/110300239070/','luchs-m2x5':'https://www.schraubenluchs.de/100-Stueck-Zylinderschrauben-mit-Innensechskant-DIN-912-ISO-4762-129-M2-x-5-blank','luchs-m2x10':'https://www.schraubenluchs.de/100-Stueck-Zylinderschrauben-mit-Innensechskant-DIN-912-ISO-4762-129-M2-x-10-blank','luchs-m25x8':'https://www.schraubenluchs.de/100-Stueck-Zylinderschrauben-mit-Innensechskant-DIN-912-ISO-4762-129-M25-x-8-blank'}
def run(item):
 k,u=item;r={'key':k,'url':u,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  f=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=35);b=f.read();ext='.pdf' if 'pdf' in f.headers.get('Content-Type','') else '.html';p=D/(k+ext);p.write_bytes(b);r.update(status=f.status,file=p.name,sha256=hashlib.sha256(b).hexdigest(),final_url=f.url)
  if ext=='.html':
   s=b.decode('utf-8',errors='replace');s=re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '',s,flags=re.S|re.I);(D/(k+'.txt')).write_text(html.unescape(re.sub(r'<[^>]+>', ' ',s)))
 except Exception as e:r['error']=str(e)
 return r
r=list(concurrent.futures.ThreadPoolExecutor(max_workers=8).map(run,urls.items()));(D/'captures.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
