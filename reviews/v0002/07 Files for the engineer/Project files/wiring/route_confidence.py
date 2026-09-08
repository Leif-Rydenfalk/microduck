"""Keep conditional routing arithmetic separate from manufacturing evidence."""

def qualify(cable, devices):
    c = cable
    c['route_verdict'] = 'CANNOT DETERMINE'
    c['cut_verdict'] = 'CANNOT DETERMINE'
    c['endpoint_evidence'] = {side: devices[c[side]]['endpoint_evidence'] for side in ('from','to')}
    if c['id'] == 'hat-radxa-40pin':
        c['length_scope'] = 'Board-to-board interface, no wire cut; target stack identity unconfirmed.'
        return
    c['modeled_floor_mm'] = c.get('floor_mm') if c.get('floor_mm') is not None else c.get('proxy_distance_mm')
    c['modeled_slack_mm'] = c.get('slack_mm')
    c['modeled_cable_mm'] = c.get('cable_mm') if c.get('cable_mm') is not None else c.get('historical_rounded_proxy_mm')
    c['floor_mm'] = c['slack_mm'] = c['cable_mm'] = None
    c['length_scope'] = 'Historical conditional model only. Proxies, socket choice, actual endpoints and obstacle/service routing are unverified; no actual route floor or manufacturing cut established.'


def worst(*values):
    return 'FAIL' if 'FAIL' in values else 'CANNOT DETERMINE' if 'CANNOT DETERMINE' in values else 'PASS'


def drop_verdict(calculated, cable_verdict, upstream_verdict):
    return worst(calculated, cable_verdict, upstream_verdict)
