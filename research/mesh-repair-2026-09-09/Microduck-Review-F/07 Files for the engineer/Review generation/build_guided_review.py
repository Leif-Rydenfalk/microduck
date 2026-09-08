"""Build an offline, source-mapped component and connection walkthrough."""
import argparse,csv,json,html,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parents[1]/'ce-cad'))
from cecad.reviewpack import viewer,page

def build(out):
 model=json.loads((out/'01 See the robot/Published assembly mesh.json').read_text())
 joints=json.loads((ROOT/'ce-assemblies/microduck/current/joints.json').read_text())['record']['rows']
 parts=list(csv.DictReader((out/'PARTS.csv').open(encoding='utf-8-sig')))
 dest=out/'09 Review step by step';dest.mkdir(exist_ok=True)
 lookup={p['name']:p for p in model['parts']};by_id={p['name'].rsplit('#',1)[-1]:p for p in model['parts']}
 e=html.escape
 def resolve(side):
  if not side:return None
  i=str(side.get('instance',''))
  return lookup.get(i) or by_id.get(i)
 bodies={}
 for p in model['parts']:bodies.setdefault(p['name'].split('/')[0],[]).append(p)
 labels={'trunk_base':'Body and battery / 机身与电池','yaw2roll':'Left hip yaw / 左髋偏航','hip_l':'Left hip / 左髋','hip_l_2':'Right hip / 右髋','upper_leg_left':'Left upper leg / 左大腿','upper_leg_right':'Right upper leg / 右大腿','leg':'Left lower leg / 左小腿','leg_2':'Right lower leg / 右小腿','ankle_left':'Left foot / 左脚','ankle_right':'Right foot / 右脚','neck':'Neck / 颈部','neck_pitch':'Neck pitch / 颈部俯仰','yaw_roll_motion':'Head yaw and roll / 头部偏航与横滚','bearing_roll':'Head roll support / 头部横滚支撑','jaw_soft':'Head and face / 头部与面部'}
 body='<a href="../START HERE.html">← Start here / 返回首页</a><h1>Review step by step / 逐项检查</h1><p>Start with each section, then each component, then its connections. Use the review sheet to record the item number and your comment. / 先看各部位，再看零件与连接；请在检查表中填写编号及意见。</p><p><a href="Review sheet.csv">Open review sheet / 打开检查表</a></p>'
 body+='<h2>1. Sections / 各部位</h2><div class="grid">';records=[]
 for n,(name,meshes) in enumerate(bodies.items(),1):
  title=labels.get(name,name.replace('_',' ').title());file=f'Section {n:02d}.html';viewer(dest/file,{'parts':meshes,'units':'mm'},title,'Review the shape, access and arrangement / 检查形状、操作空间与排列','START HERE.html')
  body+=f'<article><h3>S{n:02d} · {e(title)}</h3><a href="{file}">Turn this section around / 旋转查看部位</a></article>'
  records.append({'id':f'S{n:02d}','item':title,'type':'Section','review_result':'','comment':''})
 body+='</div><h2>2. Components / 每个零件</h2><table><tr><th>Number / 编号</th><th>Component / 零件</th><th>Qty / 数量</th><th>Review / 检查</th></tr>'
 for p in parts:
  folder=str(Path(p['stl']).parent);body+=f'<tr><td>P{int(p["number"]):02d}</td><td>{e(p["part"])}</td><td>{p["quantity"]}</td><td><a href="../{folder}/Look at this part.html">Rotate / 旋转</a> · <a href="../{e(p["stl"])}">STL</a></td></tr>'
  records.append({'id':f'P{int(p["number"]):02d}','item':p['part'],'type':'Component','review_result':'','comment':''})
 body+='</table><h2>3. Connections / 每处连接</h2><p>Rotate each connection to inspect its parts. A view alone does not confirm fit. Where a screw is absent from the model, the page shows its mounting part and says so. / 旋转查看各连接。图片不代表配合已确认；模型中没有螺钉时仅显示安装零件，并作说明。</p>'
 evidence=[]
 for n,j in enumerate(joints,1):
  params=j.get('params',{});title=params.get('joint') or ('Fastener '+str(n-14));title=title.replace('_',' ').title()
  a,b=resolve(j.get('a')),resolve(j.get('b'));shown=[]
  for m in (a,b):
   if m and m['name'] not in [x['name'] for x in shown]:shown.append(m)
  state='Check fit, clearance and access / 检查配合、间隙及操作空间'
  if not a or not b:state='Mounting part view; mating hardware is not fully shown / 安装零件视图，配套五金未完整显示'
  file=f'Connection {n:02d}.html'
  if shown:viewer(dest/file,{'parts':shown,'units':'mm'},f'J{n:02d} · '+title,state,'START HERE.html')
  names=[(j.get(k) or {}).get('ref','Unspecified').removeprefix('part:').replace('microduck-','').replace('-',' ').title() for k in ('a','b')]
  body+=f'<article id="J{n:02d}"><h3>J{n:02d} · {e(title)}</h3><p>{e(names[0])} ↔ {e(names[1])}</p>'
  if shown:body+=f'<p><a href="{file}">Inspect this connection / 查看此连接</a></p>'
  else:body+='<p>Connection geometry needs confirmation / 连接几何待确认</p>'
  if 'range_deg' in params:body+=f'<p>Recorded motion range / 记录运动范围: {e(str(params["range_deg"]))}°</p>'
  body+='<p>□ Looks right / 外观正常　□ Needs a change / 需要修改　□ Question / 有疑问</p></article>'
  records.append({'id':f'J{n:02d}','item':title,'type':'Connection','review_result':'','comment':''})
  evidence.append({'id':f'J{n:02d}','source_row':n-1,'source':j,'displayed_parts':[p['name'] for p in shown],'complete_pair_shown':bool(a and b),'view':file if shown else None})
 (dest/'START HERE.html').write_text(page('Review step by step',body))
 with (dest/'Review sheet.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 (dest/'Connection mapping.json').write_text(json.dumps(evidence,indent=2))
 intro=f'<section id="guided-review"><h2>Review one item at a time / 逐项检查</h2><p>{len(bodies)} sections · {len(parts)} components · {len(joints)} recorded connections / {len(bodies)}个部位 · {len(parts)}种零件 · {len(joints)}处已记录连接</p><p><a href="09 Review step by step/START HERE.html">Start the guided review / 开始逐项检查</a> · <a href="09 Review step by step/Review sheet.csv">Review sheet / 检查表</a></p><p>Inspect each part and connection in 3D, then note its number and your comments. / 逐项查看3D，记录编号及意见。</p></section>'
 f=out/'START HERE.html';s=f.read_text();s=s.replace('<section id="guided-review">','<section id="previous-guided-review">');s=s.replace('</main>',intro+'</main>');f.write_text(s)
 print(json.dumps({'sections':len(bodies),'components':len(parts),'connections':len(joints),'views':len(list(dest.glob('*.html')))-1}))
def navigation(out):
 dest=out/'09 Review step by step'
 pages=sorted(dest.glob('Section *.html'))+sorted(dest.glob('Connection *.html'))
 for i,p in enumerate(pages):
  links=[]
  if i:links.append('<a href="'+pages[i-1].name+'">← Previous / 上一项</a>')
  links.append('<a href="START HERE.html">Review list / 检查目录</a>')
  if i+1<len(pages):links.append('<a href="'+pages[i+1].name+'">Next / 下一项 →</a>')
  s=p.read_text().replace('</header>','<nav>'+' · '.join(links)+'</nav></header>');p.write_text(s)
 p=out/'START HERE.html';s=p.read_text();s=s.replace('<main>','<main><p><a href="09 Review step by step/START HERE.html"><strong>Review step by step / 逐项检查 →</strong></a></p>',1);p.write_text(s)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('out',type=Path);args=p.parse_args();build(args.out);navigation(args.out)
