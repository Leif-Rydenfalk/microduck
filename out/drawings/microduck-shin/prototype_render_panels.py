"""Experimental annotated render layout; does not replace the canonical drawing.

Each image is rendered directly at its actual panel aspect, without padding or
stretching. Annotations use measured white margins beside the solid; refuse any
text box touching its rendered bounding box. All feature figures come from the
live solid census. --insets adds independently verified native orthographic
views, section, measured hole table, title facts and DFM notes. Passing the
automated instruments is not a manufacturing-release verdict.
"""
import json, math, textwrap, sys
from pathlib import Path
import FreeCAD
import numpy as np
from PIL import Image
from cecad import triad, drawing as D, sheetcheck
from cecad.render import render
from cecad.sheets import _wrap
p = Path(__file__).resolve().parent
integrate = '--insets' in sys.argv
out = p/('render-panel-candidate' if integrate else 'render-panel-prototype'); out.mkdir(exist_ok=True)
doc=FreeCAD.newDocument('shin_panels')
part=triad.load(doc,'part:microduck-shin')
features, unknowns, meta=sheetcheck.enumerate_features(part.shape)
W,H=1189.,841.; margin=10.; fw,fh=W-20,H-20
cams=[(26,-52),(26,-128),(26,128),(26,52),(45,-128),(-60,52)]
caps=['ISOMETRIC 1 FRONT LEFT','ISOMETRIC 2 FRONT RIGHT','ISOMETRIC 3 REAR RIGHT','ISOMETRIC 4 REAR LEFT','TOP OBLIQUE RENDER','BOTTOM OBLIQUE RENDER']
prims=D.rect(margin,margin,W-margin,H-margin,'FRAME')
evidence=[]; failures=[]
chunk_size=math.ceil(len(features)/6)
chunks=[features[i*chunk_size:(i+1)*chunk_size] for i in range(6)]
for i,(camera,cap) in enumerate(zip(cams,caps)):
 row=0 if i<3 else 1; col=i%3
 widths=[.4,.3,.3] if row==0 else [.345,.3275,.3275]
 bh=fh*(.54 if row==0 else .46)-1
 x=margin+fw*sum(widths[:col]); y=margin+fh*.46+1 if row==0 else margin
 w=fw*widths[col]-1; h=bh
 px=1200; py=round(px*h/w)
 path=out/('render-%d.png'%(i+1))
 render(part,str(path),view=camera,W=px,H=py,ss=2,mode='pbr',projection='ortho',edges=True,bg=1.,verbose=False)
 # Preserve the raster aspect, even for a sub-pixel rounding difference.
 h_actual=w*py/px
 arr=np.asarray(Image.open(path).convert('RGB'))
 ys,xs=np.where(np.min(arr,axis=2)<245)
 xb=(float(xs.min())/px*w,float(xs.max()+1)/px*w)
 left=xb[0]-7.; right=w-xb[1]-7.
 prims.append(D.image((x,y),w,h_actual,str(path),'VISIBLE'))
 prims+=D.rect(x,y,x+w,y+h_actual,'TITLE')
 prims.append(D.text((x+w/2,y+4),5,cap,'TEXT',anchor='middle'))
 # Test text rectangles against the actual rendered-solid box, not an
 # assumed empty side margin. Leave both image end margins clear.
 assert left>55, ('No space for feature schedule',i,left)
 yy=y+h_actual-12
 title='SHIN — NOMINAL mm' if i==0 else 'MEASURED FEATURES — mm'
 for line in _wrap(title,left,3.5):
  prims.append(D.text((x+3,yy),3.5,line,'TEXT'));yy-=5
 for f in chunks[i]:
  val=f['value_mm']; prefix={'dia':'Ø','rad':'R','ang':''}.get(f.get('match_class'),'')
  suffix='°' if f.get('match_class')=='ang' else ''
  s=prefix+('%.4f'%val)+suffix
  # IDs identify the measurements precisely; full feature definitions travel
  # in the source-linked evidence, and will need visible-feature callouts.
  for label in _wrap(f['what'],left-26,3.5):
   prims.append(D.text((x+3,yy),3.5,label,'TEXT'));yy-=5
  assert yy>y+15, ('Feature table overflow',i)
  prims.append(D.text((x+left,yy+5),3.5,s,'DIM',anchor='end'))
 # Spread the six complete uncertainty disclosures across panel right margins.
 if i<len(unknowns):
  u=unknowns[i]; assert right>45,(i,right)
  txt='CANNOT DETERMINE — '+u['kind']+': '+u['why']+' SETTLED BY: '+u['settled_by']
  yy=y+h_actual-12
  for line in _wrap(txt,right,3.5):
   assert yy>y+15,('Refusal overflow',i)
   prims.append(D.text((x+w-right,yy),3.5,line,'TEXT'));yy-=5
 evidence.append({'caption':cap,'box_mm':[x,y,w,h_actual],'area_pct':100*w*h_actual/(W*H),'rendered_solid_x_span_in_panel_mm':xb,'left_annotation_width_mm':left,'right_annotation_width_mm':right,'camera':camera,'pixel_size':[px,py]})
if integrate:
 from cecad.sheets import Sheet, verify_sheet, text_boxes
 from cecad.autosheet import choose_section, dfm_lines
 sys.path.insert(0,str(p.parents[2]/'tools'))
 from drawing_facts import GENERAL_TOLERANCE
 part.blueprint.meta['general_tolerance']=GENERAL_TOLERANCE
 sh=Sheet(part,size='A0',scale=(2,1),source='ce-parts/microduck-shin/current/cad/part.py')
 sh.view('right',hidden=True,radii=True)
 sh.view('front',hidden=False,holes=False)
 axis,coord,background=choose_section(part,'right')
 sh.section('A',axis=axis,coord=coord,keep='min',walls=2,background=background)
 sh.build()  # Measure and initialise core view/hole/cutting-plane contracts.
 for vi,(v,pan) in enumerate(zip(sh.views,[evidence[0],evidence[1],evidence[0]])):
  x,y,w,h=pan['box_mm']; rw=pan['right_annotation_width_mm']
  v.S=2.; v.ox=x+w-rw+(rw-v.w*v.S)/2; v.oy=y+(235 if vi==2 else 45)
 sh._cut_segs=sh._cut_segments()
 for v in sh.views:
  prims += D.transform(v.prims,v.S,v.ox-v.bb[0]*v.S,v.oy-v.bb[1]*v.S)
 for v in sh.views:
  prims += sh._annotate(v,prims)
 prims += sh._cutting_planes(text_boxes(prims))
 # The hole table is the existing measured table, moved into a measured
 # empty margin. No copied dimensions and no new hole numbering scheme.
 pan=evidence[2];x,y,w,h=pan['box_mm'];rw=pan['right_annotation_width_mm']
 table,_=sh._hole_table(sh._table_view,sh.W-10-sh._side_column()+2,y+230)
 prims += table
 # Compact title facts and datums, with every numeric value read from solid.
 pan=evidence[0];x,y,w,h=pan['box_mm'];left=pan['left_annotation_width_mm']
 title=['MICRODUCK SHIN','2:1','A0 / THIRD ANGLE / mm','%.2f x %.2f x %.2f'%tuple(meta['bbox_mm']),
        '%.2f cm3'%(part.shape.Volume/1000.),'CAD SOURCE: part:microduck-shin',
        'DATUM: XYZ MINIMUM ENCLOSING PLANES','XYZ origin mm: '+', '.join('%.4f'%v for v in meta['datum_origin_mm']),
        'GENERAL TOLERANCE '+GENERAL_TOLERANCE+' UNLESS STATED.',
        'EXPERIMENTAL — NOT RELEASED']
 yy=y+160
 for line in title:
  lettering=7. if line=='MICRODUCK SHIN' else 3.5
  for t in _wrap(line,left,lettering):
   prims.append(D.text((x+3,yy),lettering,t,'TEXT'));yy-=lettering+1.5
 # Retain the full measured DFM notes; distribute complete notes across two
 # spare right margins. They remain declared on sh for verify_sheet readback.
 notes=dfm_lines(part)
 sh._dfm_lines=list(notes)
 halves=[notes[:(len(notes)+1)//2],notes[(len(notes)+1)//2:]]
 for pan,group in zip(evidence[4:],halves):
  x,y,w,h=pan['box_mm'];rw=pan['right_annotation_width_mm'];yy=y+225
  prims.append(D.text((x+w-rw,yy),3.5,'PRINT / DFM','TEXT'));yy-=7
  for note in group:
   for t in _wrap(note,rw,3.5):
    assert yy>y+20, 'DFM text overflow'
    prims.append(D.text((x+w-rw,yy),3.5,t,'TEXT'));yy-=5
 sh._prims=prims
D.write_svg(prims,str(out/'shin-render-panels.svg'),page=(W,H),quiet=True)
if integrate:
 import contextlib,io
 log=io.StringIO()
 with contextlib.redirect_stdout(log):
  verified=verify_sheet(sh,str(out/'shin-render-panels.svg'),part)
 (out/'verify-sheet.log').write_text(log.getvalue())
 print('BUILD / READBACK',verified)
 from cecad.pdfsheet import write_pdf, verify_pdf
 pdf=out/'shin-render-panels.pdf'
 write_pdf(prims,str(pdf),page=(W,H),quiet=True,title='Microduck shin — candidate')
 (out/'pdf-readback.json').write_text(json.dumps(verify_pdf(str(pdf),prims,(W,H)),indent=1))
 D.write_dxf(prims,str(out/'shin-render-panels-vectors.dxf'),extents=(0,0,W,H),quiet=True)

limits=(['Candidate only: automated BUILD/readback and layout/nominal dimension coverage do not establish manufacturing release.',
 'Six solid feature classes remain unmeasured and explicitly disclosed.',
 'Production tolerance and fit basis require measured coupons; no numeric tolerances invented.',
 'Full governing-contract review still requires enlarged feature-cluster details and individual feature-linked radius/fillet leaders.',
 'PDF source pixels and placement are verified; DXF is explicitly the vector-only companion.',
 'Render scale and complete mating/fastener/source/finish metadata require explicit review.'] if integrate else
 ['Layout prototype only: lacks native geometry insets, section, hole table, title facts and datum mapping.'])
(out/'layout-evidence.json').write_text(json.dumps({'limits':limits,'build_readback':bool(verified) if integrate else None,'panels':evidence,'features':features,'cannot_determine':unknowns,'source':'part:microduck-shin live solid; cecad.sheetcheck.enumerate_features'},indent=1))
from cecad.vision import screenshot_url
(out/'view.html').write_text('<!doctype html><style>html,body{margin:0}img{width:100vw}</style><img src="shin-render-panels.svg">')
screenshot_url((out/'view.html').as_uri(),str(out/'sheet.png'),width=1600,height=1132,verify=False)
g=sheetcheck.grade_sheet(str(out/'shin-render-panels.svg'),png_path=str(out/'sheet.png'),slug='microduck-shin',use_kernel=True,refresh=True)
(out/'sheetcheck.json').write_text(json.dumps(g,indent=1))
print(g['verdict'],g['rules']);print(evidence)
