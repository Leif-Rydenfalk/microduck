#!/usr/bin/env python3
"""stress_evidence.py — the FIRST structural pass (2026-09-02, superseded).

What it was: cecad.stress on four leg parts under a ROUND 20 N "design load"
per link, with the fixed/loaded connectors picked as `cons[0], cons[1]` when a
case was not named. That is the connector-name bug: on the ankle it held
`bearing_seat` and loaded `horn_face` — both on the SAME ankle axle, a case
no load path produces (out/stress/report.json: SF 2.021) — and on the upper
leg it picked `hip_pitch_axle`/`knee_axle` by dictionary order.

What it is now: a thin wrapper over sim/stress_all.py, which declares every
case by NAME through the part's real load path, loads each part with the
force MuJoCo measured (sim/measure_loads.py), sweeps the gmsh size, and writes
one JSON per study to out/sim-evidence/. The four original parts are the
default selection so the old command keeps working:

    ce-cad/bin/cad ce-designs/microduck/sim/stress_evidence.py
      == ce-cad/bin/cad ce-designs/microduck/sim/stress_all.py \
             microduck-shin microduck-upper-leg-left microduck-ankle-left microduck-hip-bracket

out/stress/report.json (the 20 N results) is kept as history and is not
rewritten by this file.
"""
import os
import sys

if not [a for a in sys.argv[1:] if not a.startswith("--")]:
    sys.argv += ["microduck-shin", "microduck-upper-leg-left", "microduck-ankle-left", "microduck-hip-bracket"]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stress_all  # noqa: E402

if __name__ == "__main__":
    stress_all.main()
