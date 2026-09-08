"""Measured rendered cluster detail sheets; original solid stays unchanged."""
import json
import math
from pathlib import Path
import FreeCAD as App
import numpy as np
from PIL import Image
from cecad import triad
from cecad.render import render, _basis, _section_cut
from radius_locators import occurrences, visible
from rendered_drawing import _panel, draw_rendered

ROOT=Path(__file__).resolve().parent.parent


def verify_context(source, actual, source_frame, actual_frame):
    """Refuse stale or substituted context instead of mixing geometry versions."""
    import hashlib
    a,b=Path(source).read_bytes(),Path(actual).read_bytes()
    if a!=b or source_frame!=actual_frame:
        raise ValueError('Principal context differs from the live-solid render; regenerate principal sheet first')
    return {'verdict':'PASS','sha256':hashlib.sha256(b).hexdigest(),
            'scope':'Exact pixels and camera frame match a render keyed by the live solid geometry'}


def draw_details(slug):
    """Stage the ankle cluster exemplar before extending to further clusters."""
    if slug!='microduck-shin':
        raise ValueError('render-details currently validates only the microduck-shin ankle exemplar')
    canonical=ROOT/'out/drawings'/slug
    main=json.loads((canonical/'result.json').read_text())
    cluster=main['details'][0]
    part=triad.load(App.newDocument('detail_cluster_source'),'part:'+slug)
    rows=occurrences(part.shape)
    axial=[]
    for row in rows:
        if row['id'] not in ('R009','R047','R061'):continue
        for direction in ((1.,0.,0.),(-1.,0.,0.)):
            found=next((p for p in row['samples_mm'] if visible(part.shape,p,direction) is True),None)
            axial.append({'id':row['id'],'toward_camera':direction,'visible_point_mm':found})
    cy,cz=cluster['center']; radius=cluster['radius']
    selected=[r for r in rows if math.hypot(-r['center_mm'][1]-cy,r['center_mm'][2]-cz)<=radius]
    if not selected:raise ValueError('Measured cluster has no source circular edges')
    edges=[part.shape.Edges[int(r['source_edge'][4:])-1] for r in selected]
    lo=[min(getattr(e.BoundBox,a+'Min') for e in edges) for a in 'XYZ']
    hi=[max(getattr(e.BoundBox,a+'Max') for e in edges) for a in 'XYZ']
    centre=[(a+b)/2 for a,b in zip(lo,hi)]
    # A disclosed section removes the distant upper body, rather than silently
    # erasing pixels or changing the recreated geometry. Cut lies beyond every
    # selected feature edge and is dimensioned relative to the same datum.
    section=('z',hi[2]+1.,'min')
    section_shape=_section_cut(part.shape,section)
    if not (0<section_shape.Volume<part.shape.Volume-1e-6):
        raise ValueError('Detail display section did not remove the documented half-space')
    out=canonical/'detail-A-supplement-build';out.mkdir(exist_ok=True)
    cams=[(26,-52),(26,-128)]
    scales=[]; records=[]
    for index,cam in enumerate(cams,4):
        x,y,w,h,px,py=_panel(index,1189.,841.)
        right,up,_=_basis(*cam)
        target=[float(np.dot(centre,right)),float(np.dot(centre,up))]
        frame={};path=out/('fit-render-%d.png'%(index+1))
        args=dict(view=cam,W=px,H=py,ss=2,mode='pbr',projection='ortho',edges=True,bg=1.,
                  section=section,env={'intensity':1.},verbose=False,
                  ortho_center_projected_mm=target)
        render(part,str(path),framing=frame,**args)
        a=np.asarray(Image.open(path).convert('RGB'));ys,xs=np.where(a.min(axis=2)<245)
        # Choose the greatest common scale compatible with the measured solid
        # and the two required annotation columns. Scale still comes from the
        # actual camera transform, independently read back after serialization.
        dx=max(abs(xs.min()-px/2),abs(xs.max()+1-px/2))*w/px
        dy=max(abs(ys.min()-py/2),abs(ys.max()+1-py/2))*w/px
        factor=min((w/2-126.)/dx,(h/2-22.)/dy)
        scales.append(w/px*frame['pixels_per_model_mm']*factor)
        records.append({'args':args,'box_mm':[x,y,w,h],'pixel_size':[px,py]})
    scale=min(scales)
    if scale<=main['common_render_scale']:
        raise ValueError('Detail does not enlarge the source cluster')
    original=json.loads((canonical/'layout-evidence.json').read_text())['panels']
    panels=[];context_checks=[]
    for index,panel in enumerate(original[:4]):
        path=out/('render-%d.png'%(index+1));frame={}
        px,py=panel['pixel_size']
        render(part,str(path),view=panel['camera'],W=px,H=py,ss=2,mode='pbr',
               projection='ortho',edges=True,bg=1.,verbose=False,framing=frame,
               env={'intensity':panel['environment_intensity']},
               ortho_pixels_per_mm=panel['framing']['pixels_per_model_mm'])
        context_checks.append(verify_context(panel['raster'],path,panel['framing'],frame))
        panels.append({'raster':str(path),'framing':panel['framing'],
                       'paper_scale':panel['paper_scale'],'caption':panel['caption']+' / CONTEXT',
                       'environment_intensity':panel['environment_intensity']})
    for index,record in enumerate(records,4):
        x,y,w,h=record['box_mm'];px,py=record['pixel_size'];frame={}
        path=out/('render-%d.png'%(index+1))
        render(part,str(path),framing=frame,ortho_pixels_per_mm=scale*px/w,**record['args'])
        panels.append({'raster':str(path),'framing':frame,'paper_scale':scale,
                       'caption':'DETAIL A '+('FRONT' if index==4 else 'BACK')+' / ENLARGED SECTION',
                       'environment_intensity':record['args']['env']['intensity']})
    evidence={'detail':'A','source':'part:'+slug,'source_edge_ids':[r['source_edge'] for r in selected],
              'cluster':cluster,'cluster_edge_bbox_mm':[lo,hi],'centre_world_mm':centre,
              'display_section':list(section),'display_section_volume_mm3':section_shape.Volume,
              'source_volume_mm3':part.shape.Volume,'common_scale':scale,
              'fit_scale_limits':scales,
              'axial_visibility_audit':axial,
              'principal_scale':main['common_render_scale'],'panels':panels,
              'context_readback':context_checks,
              'scale_groups':[{'kind':'principal','renders':[1,2,3,4]},
                              {'kind':'detail','renders':[5,6]}],
              'requirements_interpretation':'A3.1 six colour views and A2.2 four large ISO corners remain on this sheet. A3.2 top/bottom are on the retained principal sheet; this supplement adds enlarged cluster views. Full set acceptance remains incomplete.',
              'clipping':'Raster frame clips the view; Z display section removes only the stated half-space. Original source solid is unchanged.'}
    (out/'detail-source.json').write_text(json.dumps(evidence,indent=1))
    return draw_rendered(slug,outdir=out,render_bundle=evidence)
