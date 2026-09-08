"""Annotated render-panel drawing route for slender parametric parts.

Uses existing solid enumeration, rendering, native sheet annotations and
independent readback. The A0 panel arrangement refuses parts whose measured
raster margins cannot contain its annotations. No other parts are regenerated.
Automated sheet PASS and manufacturing-contract status are separate subjects.
"""
import json, math, textwrap, sys
from pathlib import Path
import FreeCAD
import numpy as np
from PIL import Image
from cecad import triad, drawing as D, sheetcheck
from cecad.render import render
from cecad.sheets import _wrap
ROOT=Path(__file__).resolve().parent.parent

def _panel(index, width, height, margin=10.):
    fw,fh=width-2*margin,height-2*margin
    row=0 if index<3 else 1;col=index%3
    widths=[.4,.3,.3] if row==0 else [.345,.3275,.3275]
    x=margin+fw*sum(widths[:col]);y=margin+fh*.46+1 if row==0 else margin
    w=fw*widths[col]-1;h=fh*(.54 if row==0 else .46)-1
    return x,y,w,h,1200,round(1200*h/w)

def verify_render_scales(svg, panels):
    """Read paper placement, embedded raster bytes and scale labels back."""
    import base64, xml.etree.ElementTree as ET
    tree=ET.parse(svg)
    images=[e for e in tree.iter() if e.tag.endswith('}image')]
    texts=[''.join(e.itertext()) for e in tree.iter() if e.tag.endswith('}text')]
    failures=[]
    scales=[]
    if len(images)!=len(panels):
        failures.append('image count disagrees with camera records')
    for i,(element,panel) in enumerate(zip(images,panels)):
        frame=panel['framing']; w=float(element.get('width'));h=float(element.get('height'))
        rx=w/frame['image_px'][0]*frame['pixels_per_model_mm']
        ry=h/frame['image_px'][1]*frame['pixels_per_model_mm']
        scales.append(rx)
        label=f"RENDER {i+1} / SCALE {rx:.5f}:1"
        if label not in texts or abs(rx-ry)>1e-5:
            failures.append(f'render {i+1}: printed scale or image aspect disagrees with camera transform')
        href=element.get('href') or element.get('{http://www.w3.org/1999/xlink}href','')
        try:
            if base64.b64decode(href.split(',',1)[1]) != Path(panel['raster']).read_bytes():
                failures.append(f'render {i+1}: embedded pixels differ from measured source')
        except Exception as e:
            failures.append(f'render {i+1}: unreadable pixels: {e}')
    if scales and max(scales)-min(scales)>1e-5:
        failures.append('principal renders do not share one paper scale')
    return {'verdict':'FAIL' if failures else 'PASS','findings':failures,'renders':len(images),
            'paper_scales':scales}

def draw_rendered(slug, outdir=None):
    p=ROOT/'out'/'drawings'/slug
    out=Path(outdir) if outdir is not None else p/'render-panel-build'
    out.mkdir(parents=True,exist_ok=True)
    integrate=True
    doc=FreeCAD.newDocument(slug.replace('-', '_') + '_panels')
    part=triad.load(doc,'part:'+slug)
    from drawing_facts import classify, part_record
    if classify(slug,part)[0] != 'drawing':
        raise ValueError('render-panels requires a dimensionable parametric solid')
    features, unknowns, meta=sheetcheck.enumerate_features(part.shape)
    W,H=1189.,841.; margin=10.; fw,fh=W-20,H-20
    cams=[(26,-52),(26,-128),(26,128),(26,52),(90,-90),(-90,-90)]
    caps=['ISOMETRIC 1 FRONT LEFT','ISOMETRIC 2 FRONT RIGHT','ISOMETRIC 3 REAR RIGHT','ISOMETRIC 4 REAR LEFT','TOP-DOWN RENDER','BOTTOM-UP RENDER']
    prims=D.rect(margin,margin,W-margin,H-margin,'FRAME')
    evidence=[]; failures=[]
    fitted=[]
    for i,camera in enumerate(cams):
        x,y,w,h,px,py=_panel(i,W,H,margin)
        frame={}
        render(part,str(out/('fit-render-%d.png'%(i+1))),view=camera,W=px,H=py,
               ss=2,mode='pbr',projection='ortho',edges=True,bg=1.,
               env={'intensity':1. if i<4 else .25},verbose=False,framing=frame)
        fitted.append(w/px*frame['pixels_per_model_mm'])
    common_scale=min(fitted)
    chunk_size=math.ceil(len(features)/6)
    chunks=[features[i*chunk_size:(i+1)*chunk_size] for i in range(6)]
    for i,(camera,cap) in enumerate(zip(cams,caps)):
     x,y,w,h,px,py=_panel(i,W,H,margin)
     path=out/('render-%d.png'%(i+1))
     framing={}
     # The end-on faces need lower ambient fill to show their depth; the
     # directional key/fill/rim rig and its shadow direction stay unchanged.
     environment_intensity=1. if i<4 else .25
     render(part,str(path),view=camera,W=px,H=py,ss=2,mode='pbr',projection='ortho',edges=True,bg=1.,env={'intensity':environment_intensity},verbose=False,framing=framing,ortho_pixels_per_mm=common_scale*px/w)
     # Preserve the raster aspect, even for a sub-pixel rounding difference.
     h_actual=w*py/px
     arr=np.asarray(Image.open(path).convert('RGB'))
     ys,xs=np.where(np.min(arr,axis=2)<245)
     xb=(float(xs.min())/px*w,float(xs.max()+1)/px*w)
     left=xb[0]-7.; right=w-xb[1]-7.
     prims.append(D.image((x,y),w,h_actual,str(path),'VISIBLE'))
     prims+=D.rect(x,y,x+w,y+h_actual,'TITLE')
     prims.append(D.text((x+w/2,y+4),5,cap,'TEXT',anchor='middle'))
     render_scale=w/px*framing['pixels_per_model_mm']
     assert abs(render_scale-common_scale)<1e-10, 'Camera did not preserve common paper scale'
     prims.append(D.text((x+w/2,y+11),3.5,f'RENDER {i+1} / SCALE {render_scale:.5f}:1','TEXT',anchor='middle'))
     # Test text rectangles against the actual rendered-solid box, not an
     # assumed empty side margin. Leave both image end margins clear.
     assert left>55, ('No space for feature schedule',i,left)
     yy=y+h_actual-12
     title=slug.upper()+' — NOMINAL mm' if i==0 else 'MEASURED FEATURES — mm'
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
     evidence.append({'caption':cap,'box_mm':[x,y,w,h_actual],'area_pct':100*w*h_actual/(W*H),'rendered_solid_x_span_in_panel_mm':xb,'left_annotation_width_mm':left,'right_annotation_width_mm':right,'camera':camera,'pixel_size':[px,py],'framing':framing,'paper_scale':render_scale,'raster':str(path),'environment_intensity':environment_intensity})
    if integrate:
     from cecad.sheets import Sheet, verify_sheet, text_boxes
     from cecad.autosheet import choose_section, dfm_lines, detail_regions, _circle_holes
     sys.path.insert(0,str(ROOT/'tools'))
     from drawing_facts import GENERAL_TOLERANCE
     part.blueprint.meta['general_tolerance']=GENERAL_TOLERANCE
     sh=Sheet(part,size='A0',scale=(2,1),source='ce-parts/'+slug+'/current/cad/part.py')
     sh.view('right',hidden=True,radii=True)
     sh.view('front',hidden=False,holes=False)
     axis,coord,background=choose_section(part,'right')
     sh.section('A',axis=axis,coord=coord,keep='min',walls=2,background=background)
     details=detail_regions(part,'right',max_n=3)
     # A transitive cluster may join two separate features along a long
     # plate. Split that oversized viewport at measured axial gaps; this
     # changes only view selection, never a dimension or the solid.
     max_radius=min(e['right_annotation_width_mm'] for e in evidence[3:])/8.-2.
     if any(d['radius']>max_radius for d in details):
      circles=_circle_holes(part,'right')
      axis=max(range(2),key=lambda a:max(c[a] for c in circles)-min(c[a] for c in circles))
      groups=[]
      for c in sorted(circles,key=lambda c:c[axis]):
       if not groups or c[axis]-groups[-1][-1][axis]>max_radius:
        groups.append([])
       groups[-1].append(c)
      details=[]
      for group in groups:
       center=tuple(sum(c[a] for c in group)/len(group) for a in range(2))
       radius=max(math.hypot(c[0]-center[0],c[1]-center[1])+c[2] for c in group)+1.5
       details.append({'center':center,'radius':radius,'n':len(group),'why':'measured axial hole cluster'})
      assert len(details)<=3, 'Feature clusters require an additional drawing sheet'
     for detail in details:
      sh.detail('right',detail['center'],detail['radius'],scale=(4,1))
     sh.build()  # Measure and initialise core view/hole/cutting-plane contracts.
     placements=[evidence[0],evidence[1],evidence[0]]+evidence[3:3+len(details)]
     for vi,(v,pan) in enumerate(zip(sh.views,placements)):
      x,y,w,h=pan['box_mm']; rw=pan['right_annotation_width_mm']
      v.S=4. if v.detail else 2.
      assert v.w*v.S < rw-12, ('Detail does not fit measured margin',v.key)
      v.ox=x+w-rw+(rw-v.w*v.S)/2; v.oy=y+(235 if vi==2 else 90 if v.detail else 45)
      v.annotation_box=(x+w-rw+3,y+20,x+w-3,y+h-12)
     sh._cut_segs=sh._cut_segments()
     for v in sh.views:
      prims += D.transform(v.prims,v.S,v.ox-v.bb[0]*v.S,v.oy-v.bb[1]*v.S)
     prims += sh._detail_rings()
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
     title=[slug.upper().replace('-', ' '),'2:1','A0 / THIRD ANGLE / mm','%.2f x %.2f x %.2f'%tuple(meta['bbox_mm']),
            '%.2f cm3'%(part.shape.Volume/1000.),'CAD SOURCE: part:'+slug,
            'DATUM: XYZ MINIMUM ENCLOSING PLANES','XYZ origin mm: '+', '.join('%.4f'%v for v in meta['datum_origin_mm']),
            'GENERAL TOLERANCE '+GENERAL_TOLERANCE+' UNLESS STATED.',
            'DRAFT — NOT RELEASED']
     yy=y+160
     for line in title:
      lettering=7. if line==slug.upper().replace('-', ' ') else 3.5
      for t in _wrap(line,left,lettering):
       prims.append(D.text((x+3,yy),lettering,t,'TEXT'));yy-=lettering+1.5
     # Retain the full measured DFM notes; distribute complete notes across two
     # spare right margins. They remain declared on sh for verify_sheet readback.
     notes=dfm_lines(part)
     sh._dfm_lines=list(notes)
     halves=[notes[:(len(notes)+1)//2],notes[(len(notes)+1)//2:]]
     for pan,group in zip(evidence[1:3],halves):
      x,y,w,h=pan['box_mm'];rw=pan['left_annotation_width_mm'];yy=y+120
      prims.append(D.text((x+3,yy),3.5,'PRINT / DFM','TEXT'));yy-=7
      for note in group:
       for t in _wrap(note,rw,3.5):
        assert yy>y+20, 'DFM text overflow'
        prims.append(D.text((x+3,yy),3.5,t,'TEXT'));yy-=5
     record=part_record(slug)
     source_notes=['SOURCE / PROCESS',
       'RECREATION MATERIAL: '+str(record.get('material','CANNOT DETERMINE')),
       'PROCESS: '+str(record.get('process','CANNOT DETERMINE')),
       'RECORD: ce-parts/'+slug+'/component.json',
       'GEOMETRY SOURCE: '+str(record.get('source_reference','CANNOT DETERMINE')),
       'ORIGINAL MATERIAL / SURFACE FINISH: CANNOT DETERMINE; obtain original specification or measure original part.',
       'FASTENER LENGTH / TORQUE / FIT CLASS: CANNOT DETERMINE; verify interface stack and test production coupon.']
     interface_file=ROOT/'ce-parts'/slug/'current'/'cad'/'interfaces.json'
     if interface_file.exists():
      interfaces=json.loads(interface_file.read_text())['record']['interfaces']
      for interface in interfaces:
       refs=interface.get('accepts',[])
       source_notes.append(interface['name'].upper()+' MATE CONTRACT: '+', '.join(refs))
       for ref in refs:
        if ref.startswith('connection:'):
         cp=ROOT/'ce-connections'/ref.split(':',1)[1]/'connection.json'
         if cp.exists():
          import re
          cr=json.loads(cp.read_text())['record']
          mates=sorted(set(re.findall(r'part:[a-z0-9-]+',json.dumps(cr.get('joins',{})))))
          if mates:
           source_notes.append('MATING PART: '+', '.join(mates))
     pan=evidence[3];x,y,w,h=pan['box_mm'];rw=pan['left_annotation_width_mm'];yy=y+225
     for note in source_notes:
      for t in _wrap(note,rw,3.5):
       assert yy>y+20, 'Source metadata does not fit measured margin'
       prims.append(D.text((x+3,yy),3.5,t,'TEXT'));yy-=5
     sh._prims=prims
    D.write_svg(prims,str(out/(slug+'.svg')),page=(W,H),quiet=True)
    # Print the instrument's occupancy number on the sheet's own face.
    # This note lies inside an existing image panel, so it must not change
    # the occupied-area measurement; the final grade checks that invariant.
    preliminary=sheetcheck.grade_sheet(str(out/(slug+'.svg')),slug=slug,use_kernel=False)
    px0,py0,_,_=evidence[0]['box_mm']
    prims.append(D.text((px0+3,py0+22),3.5,
                       f"FRAME OCCUPANCY {preliminary['occupancy_pct']:.2f}%",'TEXT'))
    D.write_svg(prims,str(out/(slug+'.svg')),page=(W,H),quiet=True)
    scale_readback=verify_render_scales(str(out/(slug+'.svg')),evidence)
    (out/'render-scale-readback.json').write_text(json.dumps(scale_readback,indent=1))
    if integrate:
     import contextlib,io
     log=io.StringIO()
     with contextlib.redirect_stdout(log):
      verified=verify_sheet(sh,str(out/(slug+'.svg')),part)
     (out/'verify-sheet.log').write_text(log.getvalue())
     print('BUILD / READBACK',verified)
     from cecad.pdfsheet import write_pdf, verify_pdf
     pdf=out/(slug+'.pdf')
     write_pdf(prims,str(pdf),page=(W,H),quiet=True,title=slug+' — candidate')
     (out/'pdf-readback.json').write_text(json.dumps(verify_pdf(str(pdf),prims,(W,H)),indent=1))
     D.write_dxf(prims,str(out/(slug+'.dxf')),extents=(0,0,W,H),quiet=True)

    gaps=[
      {'clause':'A.5 / A4','kind':'drafting','status':'PARTIAL',
       'evidence':'Native radius leaders, hole table, measured feature schedule and three enlarged vector details.',
       'remaining':'Prove an individual locator for every radius/fillet occurrence; class/value matching alone is insufficient.',
       'next_action':'Map each measured BRep occurrence to a visible leader or coordinate locator and independently read it back.'},
      {'clause':'A3.2','kind':'drafting','status':'PARTIAL',
       'evidence':'Four large shaded isometric corners and true top-down/bottom-up colour renders; three 4:1 vector details.',
       'remaining':'Enlarged shaded feature-cluster detail renders.',
       'next_action':'Add a detail sheet with six true camera-rendered feature views and preserve every per-sheet area threshold.'},
      {'clause':'A4','kind':'measurement','status':'CANNOT DETERMINE',
       'evidence':str(len(unknowns))+' unmeasured feature classes disclosed on the sheet with what settles them.',
       'remaining':'Unmeasured chamfer, rib, draft, step, mate and wall geometry as enumerated by the instrument.',
       'next_action':'Use original CAD or independently measured feature sections and interface observations.'},
      {'clause':'A4 tolerances / A3.5','kind':'measurement','status':'CANNOT DETERMINE',
       'evidence':'Tolerance, original material/finish and fastener length/torque/fit uncertainties explicitly printed.',
       'remaining':'Production fit bands, original material/finish specification and qualified fastener stack.',
       'next_action':'Obtain source drawings and perform recorded fit/coupon and fastener-stack measurements.'}]
    limits=['Automated BUILD, PDF pixels/placement, render scale and eight sheet gates grade separate subjects; none alone authorizes manufacturing release.',
            'DXF is the vector companion; SVG and PDF carry the actual raster views.']
    (out/'layout-evidence.json').write_text(json.dumps({'limits':limits,'full_contract_gaps':gaps,'build_readback':bool(verified) if integrate else None,'panels':evidence,'features':features,'cannot_determine':unknowns,'source':'part:'+slug+' live solid; cecad.sheetcheck.enumerate_features'},indent=1))
    from cecad.vision import screenshot_url
    (out/'view.html').write_text('<!doctype html><style>html,body{margin:0}img{width:100vw}</style><img src="'+slug+'.svg">')
    screenshot_url((out/'view.html').as_uri(),str(out/'sheet.png'),width=1600,height=1132,verify=False)
    g=sheetcheck.grade_sheet(str(out/(slug+'.svg')),png_path=str(out/'sheet.png'),slug=slug,use_kernel=True,refresh=True)
    assert abs(g['occupancy_pct']-preliminary['occupancy_pct'])<1e-4, 'Printed occupancy changed after annotation'
    (out/'sheetcheck.json').write_text(json.dumps(g,indent=1))
    print(g['verdict'],g['rules'])

    result = {'slug':slug, 'kind':'drawing', 'layout':'render-panels',
     'build_verdict':'PASS' if verified else 'FAIL',
     'sheet_verdict':g['verdict'], 'sheet_rules':g['rules'],
     'full_contract_verdict':'INCOMPLETE', 'manufacturing_release':'NOT RELEASED',
     'full_contract_gaps':gaps,
     'source_notes':source_notes, 'details':details, 'views':[v.key for v in sh.views],
     'requirements_source':'docs/MANUFACTURING-REQUIREMENTS.md',
     'verdict_note':'BUILD verifies solid readback; sheet_verdict measures eight layout/nominal-dimension gates. Full manufacturing-contract coverage and release are independent and are not implied by either PASS.',
     'svg':str(out/(slug+'.svg')), 'pdf':str(out/(slug+'.pdf')), 'dxf':str(out/(slug+'.dxf')),
     'dxf_scope':'vector companion; raster views are carried by SVG and PDF',
     'thumbnail':str(out/'sheet.png'), 'feature_count':len(features),
     'cannot_determine':unknowns, 'bbox_mm':meta['bbox_mm'],
     'material_record':record.get('material'), 'process_record':record.get('process'),
     'origin':'generated', 'record_verdict':record.get('verdict'),
     'source':'part:'+slug, 'pdf_readback':verify_pdf(str(pdf),prims,(W,H)),
     'render_scale_readback':scale_readback,
     'common_render_scale':common_scale,'individual_fit_scales':fitted,
     'common_scale_basis':'Minimum of the six actual fit-camera paper scales; retains the renderer standard 10% framing margin and fits every required view.',
     'generated':__import__('datetime').datetime.now().isoformat(timespec='seconds')}
    (out/'result.json').write_text(json.dumps(result,indent=1))
    if outdir is None and verified and g['verdict']=='PASS' and scale_readback['verdict']=='PASS' and result['pdf_readback']['verdict']=='PASS':
        import shutil
        names=[slug+'.svg',slug+'.pdf',slug+'.dxf','result.json','sheetcheck.json',
               'verify-sheet.log','layout-evidence.json','pdf-readback.json',
               'render-scale-readback.json','view.html','sheetcheck-solid.json',
               'sheetcheck-edges.json']+[f'render-{i}.png' for i in range(1,7)]
        backup=p/'verified-a0-before-render-panels-2026-09-08'
        if not backup.exists():
            backup.mkdir()
            for name in names+[slug+'-sheet.png','sheetcheck-current.json']:
                if (p/name).is_file():
                    shutil.copy2(p/name,backup/name)
        # Publish the coherent artifact set only after every instrument passes;
        # result.json is last so readers never see a new PASS over old files.
        for name in names:
            if name!='result.json':
                shutil.copy2(out/name,p/name)
        shutil.copy2(out/'sheet.png',p/(slug+'-sheet.png'))
        shutil.copy2(out/'sheet.png',p/'sheet.png')
        shutil.copy2(out/'sheetcheck.json',p/'sheetcheck-current.json')
        published_evidence=json.loads((p/'layout-evidence.json').read_text())
        for panel in published_evidence['panels']:
            panel['raster']=str(p/Path(panel['raster']).name)
        (p/'layout-evidence.json').write_text(json.dumps(published_evidence,indent=1))
        for key in ('svg','pdf','dxf'):
            result[key]=str(p/Path(result[key]).name)
        result['thumbnail']=str(p/(slug+'-sheet.png'))
        (p/'result.json').write_text(json.dumps(result,indent=1))
    return result
