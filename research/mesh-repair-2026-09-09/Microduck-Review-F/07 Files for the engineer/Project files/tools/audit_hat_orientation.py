#!/usr/bin/env python3
"""Check the claimed in-plane half-turn symmetry directly from pinned PCB drills.

No CAD build or physical-fit claim. Coordinates stay in J4's footprint frame;
rigid placement of the footprint cannot change this symmetry test.
"""
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / 'reference/pollen-elec-rpi-robot-hat/elec_RPI_Robot_HAT.kicad_pcb'
SHA = '26c6d77af6a650c8f601edede4389699ca4ebb942763842d60b4c2c5cc1e2cb5'
OUT = ROOT / 'research/hat-orientation-audit-2026-09-08.json'


def inspect(raw):
    if hashlib.sha256(raw).hexdigest() != SHA:
        raise ValueError('PCB sha256 differs from pinned source')
    blocks = re.split(r'(?m)(?=^\t\()', raw.decode())
    j4 = [b for b in blocks if b.startswith('\t(footprint ') and '(property "Reference" "J4"' in b]
    if len(j4) != 1:
        raise ValueError('Expected one J4 footprint')
    groups = {}
    for pad in re.split(r'(?m)(?=^\t\t\(pad )', j4[0])[1:]:
        d = re.search(r'\(drill ([-\d.]+)\)', pad)
        xy = re.search(r'\(at ([-\d.]+) ([-\d.]+)', pad)
        if d and xy:
            groups.setdefault(float(d[1]), []).append(tuple(map(float, xy.groups())))
    assert {d: len(groups[d]) for d in (2.7, 2.0, 1.02)} == {2.7: 4, 2.0: 2, 1.02: 40}
    center = tuple(sum(p[i] for p in groups[2.7])/4 for i in (0, 1))
    result = {}
    for d, name in ((2.7, 'mounts'), (2.0, 'anchors'), (1.02, 'gpio')):
        original = groups[d]
        flipped = [(2*center[0]-x, 2*center[1]-y) for x,y in original]
        distances = [min(math.dist(p,q) for q in original) for p in flipped]
        centroid = tuple(sum(p[i] for p in original)/len(original) for i in (0,1))
        result[name] = dict(count=len(original), diameter_mm=d,
            half_turn_nearest_hole_max_mm=round(max(distances),6),
            centroid_displacement_mm=round(2*math.dist(center,centroid),6),
            preserved_within_0p001mm=max(distances)<=0.001)
    return dict(source=str(PCB.relative_to(ROOT)), sha256=SHA,
        method='180-degree rotation in board plane about four-mount centroid; nearest same-diameter hole and centroid displacement, in J4 local coordinates.',
        center_footprint_local_xy_mm=center, groups=result,
        verdict='FAIL — the half-turn preserves the mounts but moves the GPIO header and anchors',
        implication='The historical 180-degree collision result is a hypothetical moved-header pose, not an interchangeable orientation of the same fixed stack.',
        limit='Does not identify the installed original board or establish assembled fit; existing collision volumes are historical, not rerun by this audit.')


def qualify_fit(fit, audit):
    fit['flip_about_board_normal'] = dict(verdict='FAIL — header alignment is not preserved',
        why=audit['implication'], evidence=str(OUT.relative_to(ROOT)),
        both_measured=True, measurement_status='Historical collision measurements retained; symmetry independently rechecked 2026-09-08')
    fit['results']['180']['orientation_admissibility'] = 'FAIL — GPIO header and anchors move relative to the fixed stack'
    fit['results']['180']['orientation_evidence'] = str(OUT.relative_to(ROOT))
    return fit


if __name__ == '__main__':
    report = inspect(PCB.read_bytes())
    OUT.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
