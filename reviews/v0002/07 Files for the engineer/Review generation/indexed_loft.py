"""Ruled polygon loft with explicit vertex correspondence.

Unlike automatic wire matching, vertex i always joins vertex i in the next
section. Use only for ordered, equally sized polygon profiles. Units: mm.
"""
import math


def indexed_loft(sections, axis="z"):
    import FreeCAD as App
    import Part
    if axis not in ("x", "y", "z") or len(sections) < 2:
        raise ValueError("indexed_loft needs an axis and at least two sections")
    n = len(sections[0][0])
    if n < 3 or any(len(points) != n for points, _ in sections):
        raise ValueError("indexed_loft requires equal polygon vertex counts >=3")
    if any(b[1] <= a[1] for a, b in zip(sections, sections[1:])):
        raise ValueError("indexed_loft section heights must increase")
    rings = []
    for points, height in sections:
        ring = []
        for u, v in points:
            xyz = {"x": (height, u, v), "y": (v, height, u),
                   "z": (u, v, height)}[axis]
            if not all(math.isfinite(x) for x in xyz):
                raise ValueError("indexed_loft requires finite coordinates")
            ring.append(App.Vector(*xyz))
        rings.append(ring)
    def face(points):
        return Part.Face(Part.makePolygon(points + [points[0]]))
    faces = [face(list(reversed(rings[0]))), face(rings[-1])]
    for lower, upper in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            faces.extend((face([lower[i], lower[j], upper[j]]),
                          face([lower[i], upper[j], upper[i]])))
    solid = Part.makeSolid(Part.makeShell(faces))
    if solid.Volume < 0:
        solid.reverse()
    if not solid.isValid() or not solid.isClosed() or len(solid.Solids) != 1:
        raise ValueError("indexed_loft did not produce one valid closed solid")
    return solid.removeSplitter()
