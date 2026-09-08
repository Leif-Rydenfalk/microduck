from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures,re,html
p=Path(__file__).resolve().parent
urls={'nz':'https://nzminiaturebearings.co.nz/product/16x22x4-mm-mr1622-zz-bearing-sku-00206030.html','vxb':'https://vxb.com/products/6700-ball-bearing-10mm-x-15mm-x-3mm-single-row-ope','direct':'https://bearingsdirect.com/6700-ball-bearing-10x15x3-open-mr6700/','smb':'https://www.smbbearings.com/products/thin-section-bearings.html','zen':'https://www.zen.biz/thin-section-bearings','mvb':'https://www.mvbbearing.com/productInfo/681882c2-e6f4-45b0-ab5d-266f7a55174d.html'}
def get(kv):
 k,u=kv;r={'id':k,'url':u,'fetched_date':'2026-09-08'}
 try:
  b=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read();(p/(k+'.html')).write_bytes(b);s=re.sub(r'<(script|style)\b.*?</\1>','',b.decode(errors='replace'),flags=re.S|re.I);t=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s)));(p/(k+'.txt')).write_text(t);r.update({'file':k+'.html','sha256':hashlib.sha256(b).hexdigest()});print(k,[(t[max(0,t.find(term)-100):t.find(term)+450]) for term in ['$','In Stock','OEM'] if term in t])
 except Exception as e:r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex: out=list(ex.map(get,urls.items()))
(p/'web-manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
