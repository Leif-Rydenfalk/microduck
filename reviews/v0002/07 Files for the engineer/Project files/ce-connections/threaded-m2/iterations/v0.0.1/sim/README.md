# Simulation status — threaded-m2

No structural, motion, thermal or physical validation case exists in this
iteration's sim directory as inspected on 2026-09-08. This README documents
that absence; it is not simulation evidence or a load-rating claim.

The existing `../compat.py` is a pure-Python conditional ISO M2x0.4 geometry
and compatibility calculation. Running `python3 ../compat.py` derives pitch
and minor diameters and tensile area and compares them with the table values
stated in that same source. It is an analytic check, not finite-element or
bench validation, and does not identify the actual screws in Microduck.
`compatible(a_iface, b_iface)` retains unknown engagement capacity and preload
when material/friction measurements are missing. `../cad/mate.py` computes a
nominal rigid placement; that transformation is not a strength test.

The shared instrument `ce-connections/bin/check.py threaded-m2` checks folder
contracts. This iteration still has no `cad/fixture.json` or
`cad/shelf_cases.json`; those integration exercises remain CANNOT DETERMINE.

To establish a usable joint rating requires source-backed actual screw and
boss identity, engagement, material properties and measured torque/friction
or pull-out evidence for that pairing. No such values are supplied here.
