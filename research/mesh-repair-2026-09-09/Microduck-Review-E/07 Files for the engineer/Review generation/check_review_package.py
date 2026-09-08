from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
from collections import Counter
import json,csv,re
from cecad.reviewpack import stl_mesh,sha
import sys
p=Path(sys.argv[1])
files=[q for q in p.rglob('*') if q.is_file()];bad=[];cache={};stls=[]
for q in files:
 if q.suffix.lower()!='.stl':continue
 digest=sha(q)
 if digest not in cache:
  try:cache[digest]={'triangles':len(stl_mesh(q)['positions'])//9}
  except Exception as e:cache[digest]={'error':str(e)}
 r={'file':q.relative_to(p).as_posix(),**cache[digest]};stls.append(r)
 if 'error' in r:bad.append(r)
(p/'STL FILE CHECK.json').write_text(json.dumps({'files':len(stls),'unique':len(cache),'invalid':bad,'scope':'Triangle count, finite coordinates and file structure. Not whole-solid or manufacturing validation.','rows':stls},indent=2))
win=[];seen=set()
for q in files:
 rel=q.relative_to(p).as_posix();key=rel.casefold()
 if key in seen:win.append([rel,'case collision'])
 seen.add(key)
 for c in q.relative_to(p).parts:
  if re.search(r'[<>:"\\|?*\x00-\x1f]',c) or c.endswith((' ','.')) or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..*)?',c,re.I):win.append([rel,'Windows path invalid'])
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for k in ['href','src']:
   if k in a:self.links.append(a[k])
missing=[];external=[]
for q in [p/'START HERE.html',p/'PARTS.html']+list((p/'02 Look at the parts').glob('*/*.html'))+list((p/'01 See the robot').glob('*.html')):
 parser=Links();parser.feed(q.read_text())
 for link in parser.links:
  u=urlsplit(link)
  if u.scheme in ('data',):continue
  if u.scheme or u.netloc:external.append([q.name,link]);continue
  if u.path and not (q.parent/unquote(u.path)).exists():missing.append([str(q.relative_to(p)),link])
source_bad=[]
for r in csv.DictReader((p/'SOURCE FILES.csv').open(encoding='utf-8-sig')):
 q=p/r['file']
 if not q.is_file() or sha(q)!=r['sha256']:source_bad.append(r['file'])
report={'stl_files':len(stls),'invalid_stls':len(bad),'windows_path_errors':win,'longest_path_including_top_folder':max(len(p.name+'/'+q.relative_to(p).as_posix()) for q in files),'primary_review_missing_links':missing,'primary_review_external_links':external,'source_hash_mismatches':source_bad,'extensions':dict(Counter(q.suffix.lower() for q in files)),'windows_native_os_test':'Not performed; offline Chrome on macOS and filename compatibility measured.'}
(p/'FINAL FILE CHECK.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not bad+win+missing+source_bad
