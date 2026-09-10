"""Source-edge section locator; a display section never replaces full geometry."""
import math
import FreeCAD as App
import Part
from cecad import drawing as D
from cecad.sheets import Sheet, _clip_to_disc, text_boxes, section_cut, section_view_dir
from radius_locators import visible


def e061_section(part, ledger, existing, box):
    row=next(r for r in ledger['occurrences'] if r['id']=='R061')
    edge=part.shape.Edges[int(row['source_edge'][4:])-1]
    if not isinstance(edge.Curve,Part.Circle) or abs(edge.Curve.Radius-row['radius_mm'])>1e-8:
        raise ValueError('E061 no longer identifies the recorded source circle')
    centre=edge.Curve.Center
    if abs(abs(edge.Curve.Axis.x)-1.)>1e-8:
        raise ValueError('E061 section requires its measured X-axis circle')
    plane=centre.x-.01  # documented display clearance, not a manufactured feature
    sheet=Sheet(part,size='A0')
    view=sheet.section('D',axis='x',coord=plane,keep='max',on=False,
                       dims=False,walls=0,background=True)
    cut=view.obj.shape
    if not cut.isValid() or not (0<cut.Volume<part.shape.Volume-1e-6):
        raise ValueError('Display section did not produce a valid reduced solid')
    matches=[]
    for e in cut.Edges:
        if (isinstance(e.Curve,Part.Circle) and
            abs(e.Curve.Radius-edge.Curve.Radius)<1e-8 and
            (e.Curve.Center-centre).Length<1e-8):
            overlap=edge.common(e)
            if sum(x.Length for x in overlap.Edges)>=edge.Length-1e-6:
                matches.append(e)
    if not matches:
        raise ValueError('Original trimmed source edge was not preserved by section')
    a,b=edge.ParameterRange
    points=[edge.valueAt(a+(b-a)*t) for t in (.5,.25,.75,.125,.875)]
    point=next((p for p in points if visible(cut,list(p),(-1.,0.,0.)) is True),None)
    if point is None:
        raise ValueError('No original edge point is proven visible through section')
    project=D.to2d_fn(view.view); c=project(centre); anchor=project(point)
    radius=6.;scale=4.
    x0,y0,x1,y1=box; ox=(x0+x1)/2;oy=(y0+y1)/2
    if min(x1-x0,y1-y0)<2*radius*scale+24:
        raise ValueError('Section inset has insufficient measured paper')
    bounds=(ox-radius*scale-8,oy-radius*scale-12,ox+radius*scale+8,oy+radius*scale+12)
    if any(bounds[0]<q[2] and bounds[2]>q[0] and bounds[1]<q[3] and bounds[3]>q[1] for q in text_boxes(existing)):
        raise ValueError('Section inset would collide with existing text')
    clipped=_clip_to_disc(view.prims,c,radius)
    if not any(p['k'] in ('circle','arc') and abs(p['r']-edge.Curve.Radius)<1e-5
               and math.dist(p['c'],c)<1e-5 for p in clipped):
        raise ValueError('Visible source circle is missing from the clipped section ink: '+str([p for p in clipped if p['k'] in ('circle','arc')]))
    prims=D.transform(clipped,scale,ox-c[0]*scale,oy-c[1]*scale)
    prims.append(D.circle((ox,oy),radius*scale,'SECTION'))
    paper=(ox+(anchor[0]-c[0])*scale,oy+(anchor[1]-c[1])*scale)
    label='E061 R%.4f'%edge.Curve.Radius
    text_at=(ox+28,oy-12);end=(ox+27,oy-11)
    prims.extend([D.line(paper,end,'DIM'),D.circle(paper,.45,'DIM'),
                  D.text(text_at,3.5,label,'DIM')])
    notes=[('SECTION D / SCALE 4:1',oy+radius*scale+8),
           ('X = %.4f mm / KEEP X >= CUT'%plane,oy-radius*scale-6),
           ('LOCAL SECTION ONLY / VIEW LIMIT 6 mm',oy-radius*scale-11)]
    for text,y in notes:
        prims.append(D.text((ox,y),3.5,text,'TEXT',anchor='middle'))
    record={'source_id':row['id'],'source_edge':row['source_edge'],
            'radius_mm':edge.Curve.Radius,'source_center_mm':list(centre),
            'source_point_mm':list(point),'plane_axis':'x','plane_mm':plane,'keep':'max',
            'source_edge_length_mm':edge.Length,'preserved_edge_matches':len(matches),
            'original_volume_mm3':part.shape.Volume,'section_volume_mm3':cut.Volume,
            'source_visibility':'PASS','paper_anchor_mm':list(paper),
            'leader_end_mm':list(end),'label':label,'text_at_mm':list(text_at),
            'scale':scale,'view_radius_mm':radius,'paper_center_mm':[ox,oy],
            'notes':[n[0] for n in notes],
            'scope':'Leader locates original E061 edge in a disclosed local section; this does not establish the complete physical feature.'}
    return prims,record


def verify_section(svg,record,page_height,part):
    import xml.etree.ElementTree as ET
    tree=ET.parse(svg); failures=[]
    try:
        edge=part.shape.Edges[int(record['source_edge'][4:])-1]
        point=App.Vector(*record['source_point_mm']);centre=edge.Curve.Center
        if (not isinstance(edge.Curve,Part.Circle) or
            abs(edge.Curve.Radius-record['radius_mm'])>1e-8 or
            (centre-App.Vector(*record['source_center_mm'])).Length>1e-8 or
            edge.distToShape(Part.Vertex(point))[0]>1e-7):
            raise ValueError('Source point/circle differs from live trimmed edge')
        if record['plane_axis']!='x' or record['keep']!='max' or record['plane_mm']>=centre.x:
            raise ValueError('Section removes the original circular edge')
        cut=section_cut(part.shape,'x',record['plane_mm'],'max')
        if not (0<cut.Volume<part.shape.Volume-1e-6) or visible(cut,list(point),(-1.,0.,0.)) is not True:
            raise ValueError('Independent section/ray readback does not prove visibility')
        right,up,_=D.view_basis(section_view_dir('x','max'))
        wanted=[record['paper_center_mm'][i]+(point-centre).dot(v)*record['scale']
                for i,v in enumerate((right,up))]
        if math.dist(wanted,record['paper_anchor_mm'])>1e-7:
            raise ValueError('Printed anchor disagrees with original point projection')
    except Exception as error:
        failures.append(str(error))
    texts=[e for e in tree.iter() if e.tag.endswith('}text')]
    values=[''.join(e.itertext()) for e in texts]
    if 'X = %.4f mm / KEEP X >= CUT'%record['plane_mm'] not in values:
        failures.append('Printed cut plane differs from the independently checked section')
    for label in [record['label']]+record['notes']:
        if label not in values:failures.append('Missing section label: '+label)
    matching=[e for e in texts if ''.join(e.itertext())==record['label']]
    tx,ty=record['text_at_mm']
    if len(matching)!=1 or abs(float(matching[0].get('x'))-tx)>.002 or abs(float(matching[0].get('y'))-(page_height-ty))>.002:
        failures.append('Section feature label is duplicated or displaced')
    a,b=record['paper_anchor_mm'],record['leader_end_mm']
    wanted=[a[0],page_height-a[1],b[0],page_height-b[1]]
    if not any(max(abs(float(e.get(k))-v) for k,v in zip(('x1','y1','x2','y2'),wanted))<.002
               for e in tree.iter() if e.tag.endswith('}line')):
        failures.append('Section leader is missing or displaced')
    cx,cy=record['paper_center_mm'];radius=record['view_radius_mm']*record['scale']
    if not any(abs(float(e.get('cx'))-cx)<.002 and abs(float(e.get('cy'))-(page_height-cy))<.002
               and abs(float(e.get('r'))-radius)<.002 for e in tree.iter() if e.tag.endswith('}circle')):
        failures.append('Section scale/circular view boundary differs from source record')
    return {'verdict':'FAIL' if failures else 'PASS','failures':failures,'source_edge':record['source_edge'],'source_id':record['source_id']}
