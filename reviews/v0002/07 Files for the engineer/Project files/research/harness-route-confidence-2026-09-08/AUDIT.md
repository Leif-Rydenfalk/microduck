# Harness route confidence — 2026-09-08

The previous harness generator treated device centroids, inferred contact ends and
MJCF sensor sites as connector exits. It then published a polyline plus assumed
10 mm hinge-bypass slack as cable_mm, called that a route floor, and used those
lengths to obtain PASS voltage-drop results. None establishes an original wire
cut. Smooth pocket centers are also proxies: the two XL330 socket sides were
chosen independently per hop, without checking actual ingress/egress allocation.

## Endpoint classification

| Endpoint | Available source evidence | Missing original-unit evidence |
|---|---|---|
| HAT | Public PCB connector footprints, pad nets and family placement centers | Installed revision, selected DXL/power ports, connector insertion and wire exits |
| Servo | Two mesh socket-pocket center proxies | Exact contact/exit datums and consistent physical port allocation |
| Speaker | Reference mesh centroid; public HAT J1 Wago pads | Fitted speaker/terminal side, lead and actual route |
| Battery | End of model pack nearest mechanical locker, inferred | Exact pack/contact PCB, spring/contact positions and wire termination |
| IMU | MJCF IMU site | Physical bridge board identity, ports and chain branch location |
| ToF/camera | MJCF sensor sites, host centroid | Exact module and host connector exits, contact sides and ribbon bends |
| Microphone | Public PCB has onboard MK1 and optional external J2/J9 paths | Whether target has any external microphone cable |

No public C1 position was adopted as an original endpoint. `tools/hat_connectors.py`
now calls its projected coordinates public_c1_world, explicitly footprint centers
at board surface, not wire exits. The inferred mesh-reflection alternative remains
separate. Bounding-box alignment is retained as its narrow numerical check; it
cannot establish installed revision or complete frame alignment. The old
as_built_world claim is removed. The one repository consumer, gen_wiring3d.py,
was updated and WIRING-3D.html regenerated with historical-table and source-scope
labels; existing router/clearance failures were not changed or rerun.

## Changed source contract

`wiring/measure.py` and new `wiring/route_confidence.py` emit:

- Physical cable_mm, floor_mm and slack_mm = null, route/cut verdict CD.
- Historical numbers retained as modeled_floor_mm, modeled_slack_mm and
  modeled_cable_mm. The prior camera proxy fields remain intact.
- The board-to-board header keeps zero wire length, explicitly not a wire cut.
- total_length_mm = null; modeled_total_length_mm = 1615 mm, including the
  historical 15 mm camera proxy. This is not a cutting/purchasing total.
- Existing modeled quantity rows retained; mic-hat has explicit unknown presence
  and historical-quantity scope, avoiding an unsupported assertion that the
  public-board onboard mic requires another external cable.

Public audio facts were checked against pinned PCB pads using hat_netlist:
U1 PAM8406D +OUT_R pin16 → FB3 → J1.1; -OUT_R pin14 → FB2 → J1.2.
MK1.1 → C10.1, C10.2 → codec U2.16; MK1 has +3V3 and ground pads.
This closes public-family topology, not the identity of the fitted original mic
or speaker. The board's external mic option does not establish a fitted cable.

## Conditional voltage drop

All previous numerical drops and endpoint voltages are preserved exactly using
modeled_cable_mm, including 0.5502 V AWG21 and 0.6938 V AWG22 to the farthest
ankle. All four formerly PASS runs are now CANNOT DETERMINE for actual routes.
Every hop carries both modeled_verdict and route confidence; unknown or failing
upstream confidence propagates. A calculated FAIL always outranks unknown.
A missing modeled length leaves downstream voltage/drop null instead of assuming
zero length or crashing. Table formatting also handles null numeric results.
The existing modeled supply assumptions were not changed; their known XL330
voltage-limit conflict remains documented in the servo-power audit and netlist.

## Validation

Six route regressions pass: exact historical arithmetic preservation, no proxy
cut, absent length propagation, failure preservation including an intentionally
100 m first hop, actual public PCB audio topology, and no as-built public-C1
claim. Five existing camera tests pass. Six I2S tests pass; its source-row test
now checks the unchanged literal fields plus the exact four new confidence
fields instead of incorrectly requiring the enriched output to equal a literal.
No test was relaxed on electrical connectivity or manufacturing confidence.
`git diff --check` passes for owned files.

Files owned: wiring/measure.py, wiring/route_confidence.py, wiring/cables.json,
wiring/drop.json, wiring/CABLES.md, tools/hat_connectors.py,
out/wiring/hat-connectors.json, tools/gen_wiring3d.py, WIRING-3D.html,
tools/test_hat_i2s_wiring.py, and this audit directory. Existing CSI null handling
was preserved. No desktop, physical hardware, purchasing or external contact
operation was performed.
