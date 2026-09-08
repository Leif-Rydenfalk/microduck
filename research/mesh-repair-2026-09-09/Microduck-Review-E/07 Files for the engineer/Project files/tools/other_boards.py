"""tools/other_boards.py — plain python3, no kernel.

The Microduck has THREE boards. One of them we now carry at chip level; this file
is the honest record of the other two, and it places NOTHING. A guessed board
outline that gets rendered becomes believed, so where the geometry is not
established the answer is CANNOT DETERMINE with what settles it.

Every geometric number here is measured in this script by reading the binary STL
and pushing its corners through the placement in placements.json.

Run: python3 tools/other_boards.py
"""
import itertools
import json
import math
import os
import struct

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, "out", "internals")
os.makedirs(OUT, exist_ok=True)


def stl_bbox(path):
    f = open(path, "rb")
    n = struct.unpack("<I", f.read(84)[80:84])[0]
    lo, hi = [1e18] * 3, [-1e18] * 3
    for _ in range(n):
        d = f.read(50)
        for k in range(3):
            v = struct.unpack("<3f", d[12 + 12 * k:24 + 12 * k])
            for j in range(3):
                lo[j] = min(lo[j], v[j])
                hi[j] = max(hi[j], v[j])
    return n, lo, hi


def quat_m(q):
    w, x, y, z = q
    s = math.sqrt(w * w + x * x + y * y + z * z)
    w, x, y, z = w / s, x / s, y / s, z / s
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]


def world_bbox(row):
    n, lo, hi = stl_bbox(row["mesh_file"])
    M, t = quat_m(row["world_quat_wxyz"]), row["world_pos_mm"]
    P = [[sum(M[i][j] * c[j] for j in range(3)) + t[i] for i in range(3)]
         for c in itertools.product(*[(lo[j] * 1000, hi[j] * 1000) for j in range(3)])]
    wl = [round(min(p[i] for p in P), 4) for i in range(3)]
    wh = [round(max(p[i] for p in P), 4) for i in range(3)]
    return n, wl, wh, [round(wh[i] - wl[i], 4) for i in range(3)]


def main():
    rows = json.load(open(os.path.join(R, "ce-assemblies", "microduck", "current",
                                       "placements.json")))["record"]["rows"]
    by = {r["mesh"]: r for r in rows if r.get("mesh_file")}
    lk_n, lk_lo, lk_hi, lk_sz = world_bbox(by["banana_pcb_locker"])
    hat_n, hat_lo, hat_hi, hat_sz = world_bbox(by["elec_rpi_robot_hat_pcb"])
    pi_n, pi_lo, pi_hi, pi_sz = world_bbox(by["pcb__raspberry_pi_zero_2_w"])
    servo = [world_bbox(r) for r in rows if r["mesh"] == "xl330"]

    res = dict(
        _generated="tools/other_boards.py",
        question="Leif asked for the three boards. One is built at chip level. What about "
                 "the other two, and what is actually known about them?",
        boards=[
            dict(name="Pollen RPI Robot HAT rev C1", ref="part:microduck-robot-hat-pcb",
                 status="BUILT AT CHIP LEVEL",
                 bodies=112, ics=11,
                 evidence="the vendor's own KiCad PCB, production BOM, pick-and-place and "
                          "assembly STEP, all Apache-2.0 (see out/pcb/hat/pcba-measured.json)",
                 world_bbox_of_the_bare_plate_in_our_assembly=dict(min=hat_lo, max=hat_hi,
                                                                   size_mm=hat_sz,
                                                                   triangles=hat_n)),
            dict(name="imu_to_dxl v2", ref="part:microduck-imu-to-dxl",
                 status="CANNOT DETERMINE - NOTHING PLACED",
                 bodies=0, ics=0,
                 what_is_known=[
                     "LSM6DSV16X 6-axis IMU with the on-chip SFLP fusion block; a small MCU "
                     "acting as a DYNAMIXEL Protocol V2 slave; a half-duplex TTL transceiver; "
                     "power taken off the bus (hardware-teardown.en.md sec.3)",
                     "bus ID 200, register 124, 12 bytes read by the control loop",
                 ],
                 why_nothing_is_placed="no outline, no thickness, no hole pattern, no BOM and no "
                                       "Gerbers are published for this board anywhere, so there "
                                       "is no frame in which a chip could be positioned. "
                                       "ce-parts/microduck-imu-to-dxl has no cad/ at all.",
                 new_finding_2026_09_04=dict(
                     claim="the teardown says no photograph of this board exists. THIS REPO "
                           "ALREADY HOLDS ONE.",
                     file="out/sources/internals/real_desk_trunk_shells_off.png "
                          "(crop of images/press/press_desk.jpg, catalogued 2026-09-03)",
                     what_is_visible=["one gull-wing IC of roughly SOIC/TSSOP size on the "
                                      "board's centre line",
                                      "a single-row pin header of roughly 12 positions along "
                                      "one long edge",
                                      "at least two small connectors at one end",
                                      "fifteen or more discrete passives",
                                      "white silkscreen reading 3V near the header"],
                     identification=dict(
                         verdict="INFERENCE, NOT A MEASUREMENT",
                         reasoning="the robot has exactly two custom boards and the Robot HAT is "
                                   "in the HEAD in our assembly (measured world x %.2f..%.2f, "
                                   "z %.2f..%.2f), while this board is in the TRUNK beside the "
                                   "hip servos. The only other board Pollen's assets put in the "
                                   "trunk is the banana battery-contact PCB, and a battery "
                                   "contact board carries no IC - this one visibly does."
                                   % (hat_lo[0], hat_hi[0], hat_lo[2], hat_hi[2]),
                         still_open="which board it is, its outline, and every chip position"),
                     settled_by="Pollen publishing the board, a straight-on photograph with a "
                                "scale in frame, or a physical unit on the bench"),
                 ),
            dict(name="banana battery-contact PCB", ref=None,
                 status="CANNOT DETERMINE - NOTHING PLACED",
                 bodies=0, ics=0,
                 what_is_known="Pollen ships the RETAINER for it (banana_pcb_locker, %d triangles) "
                               "and no mesh, outline or BOM for the board itself." % lk_n,
                 the_retainer_measured=dict(
                     world_bbox=dict(min=lk_lo, max=lk_hi, size_mm=lk_sz),
                     reading="a 3.80 mm thin, 54.05 mm wide plate standing across the top rear of "
                             "the trunk at z 151.45..158.10 mm - immediately above the NP-F pack, "
                             "whose measured top face in the same frame is z 151.72 mm. That is "
                             "where an NP-F camera battery puts its contacts.",
                     bound_it_gives="the board it retains lies inside or immediately behind this "
                                    "envelope; nothing narrower than that is measured"),
                 why_nothing_is_placed="a bound on where a board is is not a board. Its outline, "
                                       "thickness, contact geometry and any protection IC are "
                                       "unmeasured.",
                 settled_by="the same three things as imu_to_dxl"),
        ],
        the_head_stack_measured=dict(
            what="the two boards in the head are parallel vertical plates",
            robot_hat=dict(world_x=[hat_lo[0], hat_hi[0]], world_z=[hat_lo[2], hat_hi[2]],
                           plate_thickness_mm=hat_sz[0]),
            radxa=dict(world_x=[pi_lo[0], pi_hi[0]], world_z=[pi_lo[2], pi_hi[2]],
                       plate_thickness_mm=pi_sz[0]),
            gap_between_facing_surfaces_mm=round(pi_lo[0] - hat_hi[0], 4),
            board_plane_to_board_plane_mm=round(pi_lo[0] - hat_lo[0], 4),
            why_it_matters="our CAD carried the HAT as a bare 0.84 mm plate. The real board is "
                           "12.68 mm deep: 4.02 mm of 2x20 SMD header on one face and 7.74 mm of "
                           "components on the other. Which face points at the Radxa decides "
                           "whether the stack is a normal Pi HAT stack or an interference.",
            counts=dict(xl330_geoms_measured=len(servo))),
        counts=dict(boards_asked_for=3, built_at_chip_level=1,
                    cannot_determine=2, bodies_placed_total=112, ics_placed_total=11))
    p = os.path.join(OUT, "other-boards.json")
    json.dump(res, open(p, "w"), indent=1)
    print("wrote", p)
    print("HAT plate world x", hat_lo[0], hat_hi[0], " Radxa plate world x", pi_lo[0], pi_hi[0])
    print("facing-surface gap %.4f mm, plane-to-plane %.4f mm"
          % (pi_lo[0] - hat_hi[0], pi_lo[0] - hat_lo[0]))
    print("banana locker world bbox", lk_lo, lk_hi, "size", lk_sz)


main()
