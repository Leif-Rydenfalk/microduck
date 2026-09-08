from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures,re,html
p=Path(__file__).resolve().parent
urls={'abra':'https://abra-electronics.com/electromechanical/audible-devices/speakers/spk-3525-2w-gh-3525-8r-2w-box-speaker-with-gh1-25-terminal-wire.html','thingbits':'https://www.thingbits.net/products/3525-waterproof-8-ohm-2w-cavity-speaker','hubtronics':'https://hubtronics.in/peripheral-modules/3525-8ohm-2w-1-25-jst-mini-speaker?limit=100','led_digikey':'https://www.digikey.com/en/products/detail/kingbright/APTD1608LSECK-J3-PF/5177475','led_mouser':'https://www.mouser.com/ProductDetail/Kingbright/APTD1608LSECK-J3-PF?qs=6oMev5NRZMF205XngnIJQg%3D%3D','pn_lcsc':'https://www.lcsc.com/product-detail/C702907.html','pn_digikey':'https://www.digikey.com/en/products/detail/nxp-usa-inc/PN7150B0HN-C11002Y/6128021','st_lcsc':'https://www.lcsc.com/product-detail/C2908147.html','roadmap':'https://raw.githubusercontent.com/pollen-robotics/microduck/5984efb770855432b03dafd3d879e9929981e45b/docs/project/roadmap.md','tree':'https://api.github.com/repos/pollen-robotics/microduck/git/trees/5984efb770855432b03dafd3d879e9929981e45b?recursive=1'}
def get(kv):
 k,u=kv;r={'id':k,'url':u,'fetched':'2026-09-08'}
 try:
  b=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read();f=k+('.json' if k=='tree' else '.md' if k=='roadmap' else '.html');(p/f).write_bytes(b);r.update(file=f,sha256=hashlib.sha256(b).hexdigest());s=re.sub(r'<(script|style)\b.*?</\1>','',b.decode(errors='replace'),flags=re.S|re.I);t=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s)));(p/(k+'.txt')).write_text(t)
 except Exception as e:r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:r=list(ex.map(get,urls.items()))
(p/'manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
