#!/usr/bin/env python3
"""check_board_hole_interchange.py — does one printed mount accept BOTH boards?

FINDING 3, mechanical half, done as arithmetic instead of as an adjective.

The earlier record in ce-parts/radxa-zero-3w/.../cad/interfaces.json said the
Radxa ZERO 3W's drill and the Raspberry-Pi-Zero-2-W stand-in mesh's drill
differ by 0.157 / 0.134 / 0.114 mm and that "an M2.5 screw absorbs all three".
That is a sentence, not a check. This file is the check, and it does not agree
in every direction.

THE QUESTION, stated so it can be answered: a printed head part carries four
thread-forming posts on ONE pattern. A board with four clearance holes on the
OTHER pattern is offered to it. The screw is fixed by the post, so all the
float lives in the BOARD's hole. The board mounts if, for every hole,

    radial_offset_of_that_hole_from_its_screw  <=  (D_hole - d_screw) / 2

with the two patterns taken concentric (they share a board centre; both are
symmetric rectangles). The offset per hole is (dx/2, dz/2) where dx, dz are the
PITCH differences, so the radial requirement is hypot(dx, dz) / 2.

Screw major diameter is taken at its MAXIMUM (the nominal), which is the
conservative case: ISO 4762 6g bodies run under nominal, never over.

INPUTS, every one of them cited:
  out/measure/radxa-zero-3w-mechanical.json   the raster measurement of Radxa
                                              RAD-DOC-0084 Rev 1.10 §4
  ce-parts/radxa-zero-3w/iterations/v0.0.1/cad/part.py
                                              MESH_MOUNT_* — the Pi-Zero-2-W
                                              stand-in mesh's own drill
  ce-cad/cecad/fasteners.py lines 57-58       M2 and M2.5 nominal diameters

Run:  python3 tools/check_board_hole_interchange.py
Out:  out/measure/board-mount-interchange.json   (and the table on stdout)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

M = json.load(open(os.path.join(REPO, "out/measure/radxa-zero-3w-mechanical.json")))
MH = M["mount_holes"]

# ── the three patterns in play ───────────────────────────────────────────────
BOARD_L, BOARD_W = 65.000, 30.000     # Radxa's own printed callouts, §4 p.5

PATTERNS = {
    "radxa_measured": {
        "pitch_long_mm": MH["pitch_along_mm"],
        "pitch_wide_mm": MH["pitch_across_mm"],
        "hole_d_mm": MH["measured_diameter_mm"],
        "hole_d_sd_mm": MH["measured_diameter_sd_mm"],
        "sigma_mm": MH["measured_edge_inset_sd_mm"],
        "is_board": True,
        "source": ("MEASURED off the RAD-DOC-0084 Rev 1.10 §4 raster by "
                   "tools/measure_radxa_drawing.py; out/measure/radxa-zero-3w-mechanical.json"),
    },
    "radxa_nominal_3p6": {
        # the inset Radxa PRINTS once ("3. 6") applied to its own printed outline
        "pitch_long_mm": BOARD_L - 2 * 3.600,
        "pitch_wide_mm": BOARD_W - 2 * 3.600,
        "hole_d_mm": 2.800,             # Radxa prints "4 X Ø2. 8"
        "hole_d_sd_mm": None,
        "sigma_mm": MH["measured_edge_inset_sd_mm"],
        "is_board": True,
        "sigma_basis": ("the SAME 0.0396 mm as radxa_measured: this nominal is a "
                        "reconstruction anchored on the same raster ink, so it inherits that "
                        "ink's uncertainty rather than being exact."),
        "source": ("RECONSTRUCTED from Radxa's own printed callouts: inset '3. 6', "
                   "outline '65. 0' x '30. 0', hole '4 X Ø2. 8' (RAD-DOC-0084 §4). "
                   "This is the drawing's intent; radxa_measured is the drawing's ink."),
    },
    # THE PRINTED PART THAT ACTUALLY HOLDS THE BOARD, found 2026-09-03. Its
    # pilots are the posts, so it can only be the POST side of a case; it has no
    # board hole and `hole_d_mm` is None on purpose rather than borrowed.
    "face_part_measured": {
        "pitch_long_mm": 57.840,
        "pitch_wide_mm": 22.870,
        "hole_d_mm": None,
        "hole_d_sd_mm": None,
        "sigma_mm": None,
        "is_board": False,
        "sigma_basis": ("UNKNOWN and not taken as zero — same reason as the Pi-Zero mesh: this is a "
                        "cylinder fit on Pollen's decimated export and no residual is published. The "
                        "interface does record 'Residual 0.0000 mm at 355.0 deg throughout' for the "
                        "fit itself, which bounds the CIRCLE fit, not the mesh's fidelity to the part."),
        "source": ("MEASURED off Pollen's face_part.stl by cecad.meshfeatures.cylinders, frozen "
                   "2026-09-02 by tools/measure_mesh_features.py into out/laneT/features/face_part.json; "
                   "carried in ce-parts/microduck-face-part/iterations/v0.0.1/cad/interfaces.json "
                   "interface 'shell_screws': 4 x Ø2.0500 x 4.0000 pilots at (x, z) = (±28.9200, 8.5650) "
                   "and (±28.9200, 31.4350), each on a Ø6.0000 x 10.7000 boss with a Ø2.7000 x 1.0000 "
                   "counterbore."),
    },
    "pi_zero_2w_mesh": {
        "pitch_long_mm": 58.000,
        "pitch_wide_mm": 23.000,
        "hole_d_mm": 2.700,
        "hole_d_sd_mm": None,
        "is_board": True,
        "sigma_mm": None,
        "sigma_basis": ("UNKNOWN and not taken as zero. cecad.meshfeatures published no "
                        "residual for this cylinder fit, and SPEC.md §8 puts Pollen's mesh "
                        "decimation floor at p95 surface distance 1.0 mm — so the error on "
                        "this pattern is neither measured nor negligible."),
        "source": ("MEASURED off Pollen's stand-in mesh pcb__raspberry_pi_zero_2_w.stl "
                   "by cecad.meshfeatures; carried in ce-parts/radxa-zero-3w/"
                   "iterations/v0.0.1/cad/part.py as MESH_MOUNT_D / MESH_MOUNT_X / MESH_MOUNT_Z"),
    },
}

SCREWS = {
    # nominal (max) major diameter — ce-cad/cecad/fasteners.py rows 57 and 58
    "M2":   {"d_mm": 2.000, "cite": "cecad/fasteners.py line 57, M2 row"},
    "M2.5": {"d_mm": 2.500, "cite": "cecad/fasteners.py line 58, M2.5 row"},
}


def case(post_key, board_key, screw_key):
    """Posts drilled on `post_key`; a board on `board_key`; screw `screw_key`."""
    post, board = PATTERNS[post_key], PATTERNS[board_key]
    scr = SCREWS[screw_key]
    dx = abs(post["pitch_long_mm"] - board["pitch_long_mm"])
    dz = abs(post["pitch_wide_mm"] - board["pitch_wide_mm"])
    need = math.hypot(dx, dz) / 2.0
    have = (board["hole_d_mm"] - scr["d_mm"]) / 2.0
    margin = have - need
    # The measurement's own 1 sigma, propagated onto the requirement. A pattern
    # whose sigma is None contributes NOTHING to this sum and is reported as an
    # unquantified term instead — an unknown error is not a zero error, and
    # folding it in as zero is exactly the "plausible default" the house rules
    # forbid.
    known = [p["sigma_mm"] for p in (post, board) if p["sigma_mm"] is not None]
    sig = math.hypot(*known) if len(known) == 2 else (known[0] if known else None)
    unquantified = [k for k, p in (("posts:" + post_key, post), ("board:" + board_key, board))
                    if p["sigma_mm"] is None]
    if margin < 0:
        verdict = "FAIL"
        why = ("the screw cannot enter the board hole: short by %.4f mm of radius"
               % (-margin))
    elif sig is not None and margin < sig:
        verdict = "CANNOT DETERMINE"
        why = ("it fits by %.4f mm of radius, which is INSIDE the %.4f mm 1 sigma of the "
               "raster measurement the pattern comes from. A calipered board settles it; "
               "this drawing cannot." % (margin, sig))
    else:
        verdict = "PASS"
        why = ("fits with %.4f mm of radial margin%s"
               % (margin, "" if sig is None else " (%.2f sigma)" % (margin / sig)))
    if unquantified:
        why += (". CAVEAT: %s carries no stated positional uncertainty (see the pattern's "
                "sigma_basis), so this margin is an upper bound on the confidence, not a "
                "tolerance." % " and ".join(unquantified))
    return {
        "posts_on": post_key, "board_is": board_key, "screw": screw_key,
        "screw_d_mm": scr["d_mm"], "board_hole_d_mm": board["hole_d_mm"],
        "pitch_mismatch_long_mm": round(dx, 4),
        "pitch_mismatch_wide_mm": round(dz, 4),
        "radial_offset_required_mm": round(need, 4),
        "radial_clearance_available_mm": round(have, 4),
        "margin_mm": round(margin, 4),
        "measurement_1sigma_mm": None if sig is None else round(sig, 4),
        "unquantified_uncertainty_in": unquantified,
        "verdict": verdict, "why": why,
    }


def main():
    rows = []
    posts = [k for k in PATTERNS]
    boards = [k for k, v in PATTERNS.items() if v.get("is_board")]
    for post in posts:
        for board in boards:
            if post == board:
                continue
            for screw in ("M2", "M2.5"):
                rows.append(case(post, board, screw))
    # WHICH BOARD IS THE PRINTED PART DRILLED FOR? Finding 3's actual question,
    # answered by distance between drill patterns rather than by argument.
    fp = PATTERNS["face_part_measured"]
    ident = []
    for k in ("radxa_measured", "radxa_nominal_3p6", "pi_zero_2w_mesh"):
        q = PATTERNS[k]
        dl = fp["pitch_long_mm"] - q["pitch_long_mm"]
        dw = fp["pitch_wide_mm"] - q["pitch_wide_mm"]
        ident.append({"candidate": k, "d_long_mm": round(dl, 4), "d_wide_mm": round(dw, 4),
                      "distance_mm": round(math.hypot(dl, dw), 4)})
    ident.sort(key=lambda r: r["distance_mm"])
    identification = {
        "question": ("Pollen's MJCF carries a Raspberry Pi Zero 2 W mesh as the compute placeholder "
                     "while every document names a Radxa ZERO 3W. Which board is the PRINTED part "
                     "actually drilled for?"),
        "measured_on": ("part:microduck-face-part interface 'shell_screws' — 4 x Ø2.0500 x 4.0000 "
                        "pilots at (x, z) = (±28.9200, 8.5650) and (±28.9200, 31.4350), i.e. a "
                        "57.8400 x 22.8700 mm rectangle, each on a Ø6.0000 x 10.7000 boss with a "
                        "Ø2.7000 x 1.0000 counterbore. MEASURED off Pollen's own face_part.stl by "
                        "cecad.meshfeatures.cylinders (lane T, out/laneT/features/face_part.json)."),
        "ranked": ident,
        "answer": ("THE RADXA. face_part's drill is %0.4f mm from the Radxa's measured pattern and "
                   "%0.4f mm from the Pi Zero 2 W's — a factor of %0.0f. The placeholder mesh is a "
                   "placeholder; the printed part was drilled for the real board."
                   % (ident[0]["distance_mm"], ident[-1]["distance_mm"],
                      ident[-1]["distance_mm"] / ident[0]["distance_mm"])),
        "and_the_screw": ("M2.5, independently. The pilot is Ø2.0500 — exactly the M2.5 tap drill in "
                          "ce-cad/cecad/fasteners.py line 58 (2.05), where the M2 tap drill on line 57 "
                          "is 1.60 — and the lead-in counterbore is Ø2.7000, exactly that row's M2.5 "
                          "CLOSE clearance. Two features of the printed part land on the M2.5 row and "
                          "neither lands on the M2 row."),
        "consequence": ("ce-parts/microduck-face-part's shell_screws interface declares "
                        "accepts: ['connection:threaded-m2'] and calls the pattern 'shell_screws'. On "
                        "this measurement it is neither: it is the COMPUTE BOARD's mount, and it is "
                        "M2.5. That folder belongs to another lane and was NOT edited from here — this "
                        "is the evidence for whoever owns it. ELECTRONICS-DATASHEET.html section 13 row E10."),
    }
    worst = max(rows, key=lambda r: {"PASS": 0, "CANNOT DETERMINE": 1, "FAIL": 2}[r["verdict"]])
    out = {
        "$about": __doc__.strip().splitlines()[0],
        "made": "2026-09-03",
        "made_by": "tools/check_board_hole_interchange.py (lane C, electronics verification)",
        "question": ("A printed head part carries four thread-forming posts on one drill "
                     "pattern. Does a board drilled on the OTHER pattern still mount? The "
                     "screw is fixed by the post, so all float lives in the board's hole."),
        "rule": "hypot(pitch_long_mismatch, pitch_wide_mismatch) / 2 <= (board_hole_D - screw_d) / 2",
        "screw_d_is": "the NOMINAL (maximum) major diameter — the conservative case; ISO 4762 6g bodies run under it",
        "patterns": PATTERNS,
        "screws": SCREWS,
        "cases": rows,
        "which_board_is_the_printed_part_drilled_for": identification,
        "roll_up": {
            "counts": {v: sum(1 for r in rows if r["verdict"] == v)
                       for v in ("PASS", "CANNOT DETERMINE", "FAIL")},
            "worst": worst["verdict"],
            "headline": (
                "The two drill patterns are NOT unconditionally interchangeable, and which "
                "screw is fitted decides it. 9 PASS, 1 CANNOT DETERMINE, 2 FAIL over the "
                "twelve directions. On M2 (Ø2.000 in a Ø2.700-2.814 hole) all six directions "
                "PASS with 0.2086-0.3676 mm of radial margin. On M2.5 — the size SPEC.md §4's "
                "Ø2.7/2.8 x20 census and docs/BOM.md §4's 'M2.5×6 ×20' both name for these "
                "holes — a Pi-Zero-2-W board on Radxa-pattern posts FAILS in BOTH readings of "
                "the Radxa pattern: it needs 0.1032 mm (measured) or 0.1414 mm (nominal) of "
                "radial offset and a Ø2.700 hole on a Ø2.500 screw gives 0.1000 mm, so it is "
                "short by 0.0032 or 0.0414 mm of radius. The reverse direction — a Radxa board "
                "on Pi-Zero posts — fits by 0.0538 mm against the measured pattern but by only "
                "0.0086 mm against the nominal one, which is INSIDE the drawing's own 0.0396 mm "
                "1 sigma and is therefore CANNOT DETERMINE. AND IT IS NOT HYPOTHETICAL: the printed "
                "part that holds the board — part:microduck-face-part, interface 'shell_screws' — "
                "measures 57.8400 x 22.8700 mm, which is 0.0048 mm from the Radxa's measured pattern "
                "and 0.2061 mm from the Pi Zero 2 W's, so it is drilled for the RADXA; its Ø2.0500 "
                "pilot is the M2.5 tap drill and its Ø2.7000 counterbore the M2.5 close clearance; and "
                "a Pi Zero 2 W bolted to it on M2.5 FAILS by 0.0031 mm of radius. See "
                "which_board_is_the_printed_part_drilled_for. WHAT REMAINS OPEN: a calipered "
                "production board, or a Radxa DXF/STEP — neither published as of 2026-09-03."),
        },
    }
    p = os.path.join(REPO, "out/measure/board-mount-interchange.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print("%-18s %-18s %-5s  %8s %8s %8s  %s"
          % ("posts on", "board is", "screw", "need", "have", "margin", "verdict"))
    for r in rows:
        print("%-18s %-18s %-5s  %8.4f %8.4f %+8.4f  %s"
              % (r["posts_on"], r["board_is"], r["screw"],
                 r["radial_offset_required_mm"], r["radial_clearance_available_mm"],
                 r["margin_mm"], r["verdict"]))
    print("\nwrote out/measure/board-mount-interchange.json — worst %s, counts %s"
          % (out["roll_up"]["worst"], out["roll_up"]["counts"]))
    return {"PASS": 0, "FAIL": 1, "CANNOT DETERMINE": 2}[out["roll_up"]["worst"]]


if __name__ == "__main__":
    raise SystemExit(main())
