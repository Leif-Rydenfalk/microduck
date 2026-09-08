"""Write connected 3MF triangles rather than STL-style disconnected facets.

OrcaSlicer 2.4.2 silently omits Microduck's eye-ring body when each triangle
owns separate indices, even when their coordinates coincide. Sharing vertices
at the output precision preserves the same oriented surface and its topology.
"""

def mesh_xml(triangle_vertices, precision=4):
    """Return a mesh XML element from consecutive oriented triangle vertices."""
    vertices, indices, lookup = [], [], {}
    for vertex in triangle_vertices:
        key = tuple(format(float(value), f'.{precision}f') for value in vertex)
        # Avoid separate indices for signed zero, which XML readers equate.
        key = tuple(format(0., f'.{precision}f') if float(s) == 0 else s for s in key)
        if key not in lookup:
            lookup[key] = len(vertices)
            vertices.append(key)
        indices.append(lookup[key])
    if len(indices) % 3:
        raise ValueError('mesh vertices must describe complete triangles')
    return ('<mesh><vertices>\n' + ''.join(
        f'<vertex x="{x}" y="{y}" z="{z}"/>\n' for x, y, z in vertices
    ) + '</vertices><triangles>\n' + ''.join(
        f'<triangle v1="{indices[i]}" v2="{indices[i+1]}" v3="{indices[i+2]}"/>\n'
        for i in range(0, len(indices), 3)
    ) + '</triangles></mesh>')
