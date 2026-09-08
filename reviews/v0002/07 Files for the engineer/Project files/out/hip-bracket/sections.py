"""Plane cuts through hip_l.stl rendered as ASCII rasters (0.5 mm cells) and
material-interval lists — the fine structure the 20-plane cad-mjcf table hides.
Run with FreeCAD's python (numpy). Usage: sections.py <stl> <axis> <c> [<axis> <c> ...]"""
import sys, struct, numpy as np
def load_stl(path, scale=1000.0):
    b = open(path, 'rb').read()
    if b[:5] == b'solid' and b'facet' in b[:400]:
        v = []
        for line in b.decode(errors='ignore').splitlines():
            t = line.split()
            if t and t[0] == 'vertex': v.append([float(t[1]), float(t[2]), float(t[3])])
        tri = np.array(v).reshape(-1, 3, 3)
    else:
        n = struct.unpack('<I', b[80:84])[0]
        a = np.frombuffer(b[84:84 + n * 50], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
        tri = a['v'].astype(float)
    return tri * scale
def slice_segments(tri, ax, c):
    d = tri[:, :, ax] - c
    segs = []
    for t, dd in zip(tri, d):
        pts = []
        for i in range(3):
            j = (i + 1) % 3
            if (dd[i] < 0) != (dd[j] < 0):
                s = dd[i] / (dd[i] - dd[j])
                pts.append(t[i] + s * (t[j] - t[i]))
        if len(pts) == 2: segs.append(pts)
    return np.array(segs)
def raster(tri, ax, c, cell=0.5):
    segs = slice_segments(tri, ax, c)
    if len(segs) == 0: print('no material'); return
    oth = [i for i in range(3) if i != ax]
    u, v = oth
    P = segs[:, :, [u, v]]
    umin, umax = P[:, :, 0].min(), P[:, :, 0].max(); vmin, vmax = P[:, :, 1].min(), P[:, :, 1].max()
    names = 'xyz'
    print(f'--- plane {names[ax]}={c:.3f}: {names[u]} {umin:.2f}..{umax:.2f}  {names[v]} {vmin:.2f}..{vmax:.2f}')
    vs = np.arange(vmax - cell / 2, vmin, -cell)
    us = np.arange(umin + cell / 2, umax, cell)
    hdr = '        ' + ''.join(('|' if abs((uu) % 5) < cell / 2 or abs(uu % 5 - 5) < cell / 2 else ' ') for uu in us)
    print(hdr)
    for vv in vs:
        # crossings of scanline v=vv with segments
        a, b = P[:, 0, :], P[:, 1, :]
        m = (a[:, 1] < vv) != (b[:, 1] < vv)
        if not m.any(): print(f'{vv:7.2f} '); continue
        s = (vv - a[m, 1]) / (b[m, 1] - a[m, 1])
        xs = np.sort(a[m, 0] + s * (b[m, 0] - a[m, 0]))
        row = ''
        for uu in us:
            inside = (np.searchsorted(xs, uu) % 2) == 1
            row += '#' if inside else '.'
        ivs = ' '.join(f'[{xs[i]:.2f},{xs[i+1]:.2f}]' for i in range(0, len(xs) - 1, 2))
        print(f'{vv:7.2f} {row}  {ivs}')
if __name__ == '__main__':
    tri = load_stl(sys.argv[1])
    args = sys.argv[2:]
    for i in range(0, len(args), 2):
        raster(tri, 'xyz'.index(args[i]), float(args[i + 1]))
