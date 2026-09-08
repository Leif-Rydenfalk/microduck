"""Exact circular-edge occurrences and candidate visible drawing locators.

Topology occurrences deliberately are not collapsed by radius or rounded centre.
This ledger is evidence for annotation placement, not proof that labels have
been printed. Failed visibility booleans remain unknown, never visible.
"""
import math
import FreeCAD as App
import Part


def paper_point(point, panel):
    frame = panel['framing']
    if frame['projection'] != 'ortho':
        raise ValueError('Locator projection requires orthographic camera metadata')
    x, y, width, height = panel['box_mm']
    px, py = frame['image_px']
    ppm = frame['pixels_per_model_mm']
    if not all(math.isfinite(v) and v > 0 for v in (width, height, px, py, ppm)):
        raise ValueError('Invalid projection dimensions')
    if abs(width / px - height / py) > 1e-8:
        raise ValueError('Stretched raster cannot establish a locator')
    right, up = frame['camera_right'], frame['camera_up']
    cx, cy = frame['center_projected_mm']
    dot = lambda a, b: sum(v*w for v, w in zip(a, b))
    return [x + width/2 + (dot(point, right)-cx)*ppm*width/px,
            y + height/2 + (dot(point, up)-cy)*ppm*height/py]


def visible(shape, point, toward_camera):
    """BRep ray test; even thin walls obstruct an edge point behind them."""
    direction = App.Vector(*toward_camera)
    if direction.Length < 1e-9:
        raise ValueError('Camera direction is zero')
    direction.normalize()
    start = App.Vector(*point) + direction*1e-5
    end = start + direction*(shape.BoundBox.DiagonalLength + 2.)
    try:
        intersection = shape.common(Part.makeLine(start, end))
        return not any(edge.Length > 1e-4 for edge in intersection.Edges)
    except Exception:
        return None


def occurrences(shape):
    rows = []
    for index, edge in enumerate(shape.Edges, 1):
        curve = edge.Curve
        if not isinstance(curve, Part.Circle):
            continue
        a, b = edge.ParameterRange
        samples = [edge.valueAt(a+(b-a)*f) for f in (.5,.25,.75,.125,.375,.625,.875,.01,.99)]
        rows.append({'id': 'R%03d' % (len(rows)+1), 'source_edge': 'Edge%d' % index,
                     'radius_mm': float(curve.Radius), 'center_mm': list(curve.Center),
                     'axis': list(curve.Axis), 'parameter_range_rad': [a,b],
                     'start_mm':list(edge.valueAt(a)), 'end_mm':list(edge.valueAt(b)),
                     'sweep_deg': abs(b-a)*180/math.pi,
                     'samples_mm': [list(p) for p in samples]})
    return rows


def locate(shape, panels, preferred_panels=None):
    rows = occurrences(shape)
    order=list(range(1,len(panels)+1)) if preferred_panels is None else list(preferred_panels)
    if sorted(order)!=list(range(1,len(panels)+1)):
        raise ValueError('Locator view order must include every panel exactly once')
    for row in rows:
        row['locator'] = None
        unknown = False
        # Try each actual trimmed-edge point; no sample extends the edge.
        for point in row['samples_mm']:
            for index in order:
                panel=panels[index-1]
                frame = panel['framing']
                toward = App.Vector(*frame['camera_right']).cross(App.Vector(*frame['camera_up']))
                projected = paper_point(point, panel)
                x,y,w,h = panel['box_mm']
                if not (x <= projected[0] <= x+w and y <= projected[1] <= y+h):
                    continue
                verdict = visible(shape, point, list(toward))
                unknown |= verdict is None
                if verdict is True:
                    row['locator'] = {'panel': index, 'point_mm': point, 'paper_mm': projected}
                    break
            if row['locator'] is not None:
                break
        row['status'] = ('VISIBLE_CANDIDATE' if row['locator'] else
                         'CANNOT DETERMINE' if unknown else 'NO_VISIBLE_SAMPLE')
        del row['samples_mm']
    return {'schema':1, 'scope':'Every topological circular edge; candidates are not printed annotation acceptance',
            'occurrences':rows, 'count':len(rows),
            'visible_candidates':sum(r['locator'] is not None for r in rows),
            'unresolved':[r['id'] for r in rows if r['locator'] is None]}


def verify_candidates(shape, panels, ledger):
    """Independently read each source edge, trim, projection and visibility."""
    failures = []
    expected = {'Edge%d' % i for i,e in enumerate(shape.Edges,1)
                if isinstance(e.Curve,Part.Circle)}
    actual = [r['source_edge'] for r in ledger['occurrences']]
    if set(actual) != expected or len(actual) != len(expected):
        failures.append('Circular edge occurrence coverage differs from live topology')
    for row in ledger['occurrences']:
        try:
            edge = shape.Edges[int(row['source_edge'][4:])-1]
            curve = edge.Curve
            if abs(curve.Radius-row['radius_mm']) > 1e-8:
                raise ValueError('radius differs from source')
            if (curve.Center-App.Vector(*row['center_mm'])).Length > 1e-8:
                raise ValueError('centre differs from source')
            if (curve.Axis-App.Vector(*row['axis'])).Length > 1e-8:
                raise ValueError('axis differs from source')
            a,b=edge.ParameterRange
            if max(abs(a-row['parameter_range_rad'][0]),abs(b-row['parameter_range_rad'][1]))>1e-8:
                raise ValueError('trim parameters differ from source')
            for field,param in (('start_mm',a),('end_mm',b)):
                if (edge.valueAt(param)-App.Vector(*row[field])).Length>1e-8:
                    raise ValueError('trim endpoint differs from source')
            loc = row['locator']
            if loc is None:
                continue
            point = App.Vector(*loc['point_mm'])
            if edge.distToShape(Part.Vertex(point))[0] > 1e-7:
                raise ValueError('anchor is not on the actual trimmed source edge')
            panel = panels[loc['panel']-1]
            frame = panel['framing']
            right,up = App.Vector(*frame['camera_right']),App.Vector(*frame['camera_up'])
            x,y,w,h = panel['box_mm']
            nx,ny = frame['image_px']
            cx,cy = frame['center_projected_mm']
            scale = frame['pixels_per_model_mm']
            wanted = (x+w/2+(point.dot(right)-cx)*scale*w/nx,
                      y+h/2+(point.dot(up)-cy)*scale*h/ny)
            if max(abs(a-b) for a,b in zip(wanted,loc['paper_mm'])) > 1e-7:
                raise ValueError('paper anchor differs from actual camera projection')
            if visible(shape,list(point),list(right.cross(up))) is not True:
                raise ValueError('source anchor is not proven visible')
        except Exception as error:
            failures.append(row['id']+': '+str(error))
    return {'verdict':'FAIL' if failures else 'PASS','failures':failures,
            'scope':'Candidate geometry only; printed labels and leader placement remain separate'}


def annotate(prims, panels, ledger):
    """Place visible occurrence leaders on measured white raster space.

    A failed placement is kept in the ledger. Existing text is an obstacle;
    this function never removes existing dimensions to make room.
    """
    import numpy as np
    from PIL import Image
    from cecad import drawing as D
    from cecad.sheets import text_boxes, text_box
    boxes = text_boxes(prims, pad=1.)
    masks = [np.min(np.asarray(Image.open(p['raster']).convert('RGB')),axis=2)<245 for p in panels]
    added = []
    def crosses_box(start,end,box):
        low,high=0.,1.
        for a in (0,1):
            delta=end[a]-start[a]
            if abs(delta)<1e-10:
                if not box[a]<=start[a]<=box[a+2]: return False
            else:
                t0,t1=sorted(((box[a]-start[a])/delta,(box[a+2]-start[a])/delta))
                low,high=max(low,t0),min(high,t1)
                if low>high:return False
        return True
    for row in ledger['occurrences']:
        loc = row['locator']
        row['printed_locator'] = None
        if not loc or row.get('in_detail') is False:
            continue
        pan = panels[loc['panel']-1]
        mask = masks[loc['panel']-1]
        x,y,w,h = pan['box_mm']; ih,iw = mask.shape
        ax,ay = loc['paper_mm']
        label = 'E'+row['id'][1:]+' R%.4f' % row['radius_mm']
        # Nearest free paper first; equal radii retain separate IDs and anchors.
        for distance in range(12,102,6):
            placed = False
            for degree in range(0,360,15):
                theta = math.radians(degree)
                tx,ty = ax+distance*math.cos(theta),ay+distance*math.sin(theta)
                text = D.text((tx,ty),3.5,label,'DIM',anchor='middle')
                b = text_box(text,pad=1.)
                if not (x+3<b[0]<b[2]<x+w-3 and y+20<b[1]<b[3]<y+h-8):
                    continue
                if any(b[0]<q[2] and b[2]>q[0] and b[1]<q[3] and b[3]>q[1] for q in boxes):
                    continue
                ix0=max(0,int((b[0]-x)/w*iw)); ix1=min(iw,math.ceil((b[2]-x)/w*iw))
                iy0=max(0,int((y+h-b[3])/h*ih)); iy1=min(ih,math.ceil((y+h-b[1])/h*ih))
                if mask[iy0:iy1,ix0:ix1].any():
                    continue
                # Terminate on the nearest label edge, clear of lettering.
                end = (b[0] if ax<tx else b[2],(b[1]+b[3])/2)
                if any(crosses_box((ax,ay),end,q) for q in boxes):
                    continue
                added.extend([D.line((ax,ay),end,'DIM'),D.circle((ax,ay),.45,'DIM'),text])
                boxes.append(b)
                row['printed_locator'] = {'label':label,'text_at_mm':[tx,ty],
                                           'leader_start_mm':[ax,ay],'leader_end_mm':list(end)}
                placed=True
                break
            if placed:
                break
    ledger['printed_count'] = sum(r['printed_locator'] is not None for r in ledger['occurrences'])
    ledger['scope_count']=sum(r.get('in_detail',True) for r in ledger['occurrences'])
    ledger['outside_detail']=[r['id'] for r in ledger['occurrences'] if r.get('in_detail') is False]
    ledger['unprinted'] = [r['id'] for r in ledger['occurrences'] if r.get('in_detail',True) and r['printed_locator'] is None]
    return added


def coordinate_locators(prims, ledger, datum, box):
    """Explicit trimmed-arc coordinate locators for occurrences hidden in views."""
    from cecad import drawing as D
    from cecad.sheets import text_boxes, text_box
    obstacles=text_boxes(prims,pad=.7)
    x0,y0,x1,y1=box
    height=3.5; yy=y1-height
    added=[]
    def emit(label):
        nonlocal yy
        p=D.text((x0+1,yy),height,label,'TEXT')
        b=text_box(p,pad=.7)
        if b[2]>x1 or b[1]<y0 or any(b[0]<q[2] and b[2]>q[0] and b[1]<q[3] and b[3]>q[1] for q in obstacles):
            raise ValueError('Hidden-edge coordinate locator exceeds free paper')
        added.append(p); yy-=5.
        return {'label':label,'at_mm':[x0+1,yy+5.]}
    emit('HIDDEN ARC LOCATORS / DATUM XYZ mm')
    xyz=lambda p:', '.join('%.4f'%(v-d) for v,d in zip(p,datum))
    for row in ledger['occurrences']:
        if row.get('in_detail') is False:continue
        if row['printed_locator'] is not None:continue
        labels=[('E'+row['id'][1:]+' R%.4f / SWEEP %.4f deg'%(row['radius_mm'],row['sweep_deg'])),
                'CENTRE '+xyz(row['center_mm']),
                'AXIS '+', '.join('%.4f'%v for v in row['axis']),
                'START '+xyz(row['start_mm']), 'END '+xyz(row['end_mm'])]
        row['coordinate_locator']={'datum_mm':list(datum),'lines':[emit(t) for t in labels]}
        yy-=2.
    ledger['coordinate_count']=sum('coordinate_locator' in r for r in ledger['occurrences'])
    ledger['unlocated']=[r['id'] for r in ledger['occurrences'] if r.get('in_detail',True) and not r['printed_locator'] and 'coordinate_locator' not in r]
    return added


def verify_printed(svg, ledger, page_height):
    """Read actual serialized labels and both leader endpoints from SVG."""
    import xml.etree.ElementTree as ET
    tree = ET.parse(svg)
    texts = [e for e in tree.iter() if e.tag.endswith('}text')]
    lines = [e for e in tree.iter() if e.tag.endswith('}line')]
    failures=[]
    for row in ledger['occurrences']:
        for record in row.get('coordinate_locator',{}).get('lines',[]):
            matches=[t for t in texts if ''.join(t.itertext())==record['label']]
            tx,ty=record['at_mm']
            if not any(abs(float(t.get('x'))-tx)<.002 and abs(float(t.get('y'))-(page_height-ty))<.002 for t in matches):
                failures.append(row['id']+': coordinate locator line missing or displaced')
        p=row.get('printed_locator')
        if not p:continue
        matching=[t for t in texts if ''.join(t.itertext())==p['label']]
        tx,ty=p['text_at_mm']
        if len(matching)!=1 or abs(float(matching[0].get('x'))-tx)>.002 or abs(float(matching[0].get('y'))-(page_height-ty))>.002:
            failures.append(row['id']+': label missing, duplicated or displaced')
        a,b=p['leader_start_mm'],p['leader_end_mm']
        expected=[a[0],page_height-a[1],b[0],page_height-b[1]]
        if not any(max(abs(float(e.get(k))-v) for k,v in zip(('x1','y1','x2','y2'),expected))<.002 for e in lines):
            failures.append(row['id']+': source-linked leader missing or displaced')
    return {'verdict':'FAIL' if failures else 'PASS','failures':failures,
            'printed_count':ledger['printed_count'],'unprinted':ledger['unprinted'],
            'scope_count':ledger.get('scope_count',ledger['count']),
            'outside_detail':ledger.get('outside_detail',[]),
            'coordinate_count':ledger.get('coordinate_count',0),'unlocated':ledger.get('unlocated',ledger['unprinted']),
            'scope':'Printed occurrence leaders; unresolved occurrences still prevent full coverage'}
