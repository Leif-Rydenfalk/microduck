#!/usr/bin/env python3
"""Read pinned upstream PCB evidence; no CAD build, design edit or hardware IO.

Print JSON to stdout. This deliberately reports coordinate spans rather than
claiming kernel geometry, board fit, electrical validation, or DRC success.
"""
import collections
import hashlib
import json
import re
import urllib.request

REVISION = "23eab11927f95ceca0dfa35bf182caeb7db39ea0"
URL = ("https://raw.githubusercontent.com/pollen-robotics/elec_RPI_Robot_HAT/"
       + REVISION + "/elec_RPI_Robot_HAT.kicad_pcb")


def inspect(raw):
    source = raw.decode("utf-8")
    blocks = re.split(r"(?m)(?=^\t\()", source)
    edges = [b.rstrip() for b in blocks
             if re.match(r"\t\(gr_(line|arc)\b", b)
             and '(layer "Edge.Cuts")' in b]
    if len(edges) != 8:
        raise ValueError("Pinned outline changed: expected four lines and four arcs")
    points = [tuple(map(float, xy)) for b in edges for xy in
              re.findall(r"\((?:start|mid|end) ([-\d.]+) ([-\d.]+)\)", b)]
    holes = []
    for b in blocks:
        if not b.startswith('\t(footprint '):
            continue
        ref = re.search(r'\(property "Reference" "([^"]+)"', b).group(1)
        for pad in re.split(r"(?m)(?=^\t\t\(pad )", b)[1:]:
            drill = re.search(r"\(drill ([-\d.]+)\)", pad)
            at = re.search(r"\(at ([-\d.]+) ([-\d.]+)", pad)
            if drill and at:
                holes.append({"footprint_reference": ref,
                              "diameter_mm": float(drill.group(1)),
                              "footprint_local_xy_mm": list(map(float, at.groups()))})
    mount = [h for h in holes if h['diameter_mm'] == 2.7]
    if len(mount) != 4 or {h['footprint_reference'] for h in mount} != {'J4'}:
        raise ValueError("Expected four 2.7 mm holes in J4")
    def spans(coords):
        return [round(max(p[i] for p in coords) - min(p[i] for p in coords), 6)
                for i in (0, 1)]
    return {
        "source_url": URL, "revision": REVISION,
        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
        "method": "Read top-level Edge.Cuts lines/arcs and footprint drill declarations. For this rounded rectangle the stored endpoints include the x/y extrema. Dimensions exclude plotted stroke width.",
        "edge_coordinate_span_xy_mm": spans(points),
        "declared_board_thickness_mm": float(re.search(r'\(thickness ([\d.]+)\)', source).group(1)),
        "drill_counts": dict(collections.Counter(str(h['diameter_mm']) for h in holes)),
        "mounting_holes": mount,
        "mounting_pattern_footprint_local_xy_mm": spans([h['footprint_local_xy_mm'] for h in mount]),
        "edge_source_blocks": edges,
        "limits": "Source-file evidence only. Does not verify assembled fit, component heights, electrical behavior, fabrication readiness or identity of the production Microduck revision."
    }


if __name__ == "__main__":
    with urllib.request.urlopen(URL, timeout=30) as response:
        report = inspect(response.read())
    print(json.dumps(report, indent=2))
