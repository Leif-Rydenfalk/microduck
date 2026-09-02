"""Read sim/microduck_ours.xml and answer, as plain data: what bodies exist,
how they nest, which hinge drives each one, and which visual meshes hang off
each body.

No MuJoCo, no numpy, no FreeCAD — xml.etree and struct only, so the exporter
runs under plain python3 and the answer can be diffed by eye.

MEASURE NEVER ASSERT: every number here is READ from the MJCF (or from the
STL header's own triangle count), never guessed. Mesh scale is the MJCF's own
`scale` attribute; a mesh with no scale is metres, which is what Pollen's
assets are.
"""
import os, struct, xml.etree.ElementTree as ET

def _floats(s, n=None, default=None):
    if s is None:
        return list(default) if default is not None else None
    v = [float(x) for x in s.replace(",", " ").split()]
    if n and len(v) != n:
        raise ValueError(f"expected {n} floats, read {len(v)}: {s!r}")
    return v

class Body:
    def __init__(self, name, pos, quat, parent):
        self.name, self.pos, self.quat, self.parent = name, pos, quat, parent
        self.children, self.geoms, self.joints = [], [], []

def parse(xml_path):
    """-> (root_body, bodies_by_name, meshes {name: (abspath, scale)}, materials {name: rgba})."""
    tree = ET.parse(xml_path)
    r = tree.getroot()
    xml_dir = os.path.dirname(os.path.abspath(xml_path))
    comp = r.find("compiler")
    meshdir = comp.get("meshdir", "") if comp is not None else ""

    meshes, materials = {}, {}
    for asset in r.findall("asset"):
        for m in asset.findall("mesh"):
            f = m.get("file")
            name = m.get("name") or os.path.splitext(os.path.basename(f))[0]
            p = f if os.path.isabs(f) else os.path.normpath(os.path.join(xml_dir, meshdir, f))
            meshes[name] = (p, _floats(m.get("scale"), 3, (1.0, 1.0, 1.0)))
        for m in asset.findall("material"):
            materials[m.get("name")] = _floats(m.get("rgba"), 4, (0.7, 0.7, 0.7, 1.0))

    def walk(el, parent):
        b = Body(el.get("name"),
                 _floats(el.get("pos"), 3, (0, 0, 0)),
                 _floats(el.get("quat"), 4, (1, 0, 0, 0)),
                 parent.name if parent else None)
        for j in el.findall("joint"):
            b.joints.append({
                "name": j.get("name"),
                "type": j.get("type", "hinge"),
                "axis": _floats(j.get("axis"), 3, (0, 0, 1)),
                "range": _floats(j.get("range"), 2),
                "pos": _floats(j.get("pos"), 3, (0, 0, 0)),
            })
        for g in el.findall("geom"):
            # VISUAL ONLY. class="collision"/"self_collision_only" geoms are
            # Pollen's convex hulls; drawing them would double the triangle
            # count and show the robot wearing its own collision proxy.
            if g.get("class") != "visual" or g.get("type") != "mesh":
                continue
            b.geoms.append({
                "mesh": g.get("mesh"),
                "pos": _floats(g.get("pos"), 3, (0, 0, 0)),
                "quat": _floats(g.get("quat"), 4, (1, 0, 0, 0)),
                "material": g.get("material"),
            })
        for child in el.findall("body"):
            b.children.append(walk(child, b))
        return b

    wb = r.find("worldbody")
    roots = wb.findall("body")
    if len(roots) != 1:
        raise ValueError(f"expected one root body, MJCF has {len(roots)}")
    root = walk(roots[0], None)

    by_name = {}
    def index(b):
        by_name[b.name] = b
        for c in b.children:
            index(c)
    index(root)
    return root, by_name, meshes, materials

def read_stl(path, scale=(1, 1, 1)):
    """Binary or ASCII STL -> (verts[[x,y,z]...], tris[[i,j,k]...]) with
    vertices welded on an exact-bit key. Returns flat float lists."""
    with open(path, "rb") as fh:
        data = fh.read()
    tris_xyz = []
    if len(data) >= 84 and not data[:5].lower().startswith(b"solid "):
        n = struct.unpack_from("<I", data, 80)[0]
        if 84 + n * 50 != len(data):
            raise ValueError(f"{path}: header says {n} triangles, file is {len(data)} bytes")
        off = 84
        for _ in range(n):
            vals = struct.unpack_from("<12fH", data, off)
            off += 50
            tris_xyz.append(vals[3:12])
    else:
        nums, cur = [], []
        for line in data.decode("utf-8", "replace").splitlines():
            t = line.split()
            if t and t[0] == "vertex":
                cur.extend(float(x) for x in t[1:4])
                if len(cur) == 9:
                    nums.append(tuple(cur)); cur = []
        tris_xyz = nums
    sx, sy, sz = scale
    weld, verts, tris = {}, [], []
    for t in tris_xyz:
        idx = []
        for k in range(3):
            v = (t[k * 3] * sx, t[k * 3 + 1] * sy, t[k * 3 + 2] * sz)
            i = weld.get(v)
            if i is None:
                i = len(verts) // 3
                weld[v] = i
                verts.extend(v)
            idx.append(i)
        if idx[0] != idx[1] and idx[1] != idx[2] and idx[0] != idx[2]:
            tris.extend(idx)
    return verts, tris

if __name__ == "__main__":
    import sys, json
    root, by_name, meshes, materials = parse(sys.argv[1])
    def show(b, d=0):
        j = ",".join(x["name"] for x in b.joints) or "-"
        print("  " * d + f"{b.name}  joint={j}  geoms={len(b.geoms)}")
        for c in b.children:
            show(c, d + 1)
    show(root)
    print(f"\n{len(by_name)} bodies, {len(meshes)} meshes declared, {len(materials)} materials")
    used = sorted({g['mesh'] for b in by_name.values() for g in b.geoms})
    print(f"{sum(len(b.geoms) for b in by_name.values())} visual geoms over {len(used)} distinct meshes")
