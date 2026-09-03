#!/usr/bin/env python3
"""tools/gen_upstream_develop.py — consolidate the SOURCE 2 ingest (pollen-robotics/
microduck_rl DEVELOP branch, pinned 29e887e) into ONE data file and ONE document:

  out/sources/upstream-develop.json   (the deliverable: pins, licence, file/mesh/
                                       MJCF diffs, findings, verdicts, invalidated docs)
  out/sources/upstream-develop.html   (house style, tools/doc.css)

Reads only measured inputs already on disk:
  out/sources/upstream-develop-files.json      git-level file diff 5946fd9..29e887e
  out/sources/upstream-develop-meshdiff.json   tools/upstream_meshdiff.py (cecad.meshcompare)
  out/sources/upstream-develop-mjcfdiff.json   tools/upstream_mjcfdiff.py
  out/sources/upstream-main-alpha-vs-develop.json  runtime repo's bundled MJCF vs develop
  reference/pollen-microduck-rl-develop/SOURCE-COMMIT.txt
Pure stdlib (system python3 has a broken pyexpat, so the XML census below uses regex).
"""
import json, os, re, html, time, subprocess

R = "/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck"
S = f"{R}/out/sources"
DEV = f"{R}/reference/pollen-microduck-rl-develop"
J = lambda p: json.load(open(p))
files = J(f"{S}/upstream-develop-files.json")
mesh = J(f"{S}/upstream-develop-meshdiff.json")
mj = J(f"{S}/upstream-develop-mjcfdiff.json")
main = J(f"{S}/upstream-main-alpha-vs-develop.json")
srccommit = open(f"{DEV}/SOURCE-COMMIT.txt").read()

OLD_SHA, NEW_SHA = "5946fd9cdbc58956424420153e51975af3b30d77", "29e887ecfbf5d37144759e5a9f8a176dfb83d547"
NOW = time.strftime("%Y-%m-%d %H:%M %z")

def grep_count(path, pat):
    try:
        return len(re.findall(pat, open(path).read()))
    except FileNotFoundError:
        return None

# ---- measured censuses off the develop tree (regex, no pyexpat) ----------------
def collision_census(xml):
    txt = open(xml).read()
    out = {}
    for m in re.finditer(r'<geom[^>]*>', txt):
        g = m.group(0)
        cls = re.search(r'class="([^"]+)"', g); mesh_ = re.search(r'mesh="([^"]+)"', g)
        if cls and mesh_ and cls.group(1) in ("collision", "self_collision_only"):
            k = f"{mesh_.group(1)} [{cls.group(1)}]"; out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))
def visual_census(xml):
    txt = open(xml).read(); out = {}
    for m in re.finditer(r'<geom[^>]*class="visual"[^>]*mesh="([^"]+)"', txt):
        out[m.group(1)] = out.get(m.group(1), 0) + 1
    return dict(sorted(out.items()))
allcol = collision_census(f"{DEV}/microduck/robot_allcollisions.xml")
groundcontact = collision_census(f"{DEV}/microduck/robot_groundcontact.xml")
walk_vis = visual_census(f"{DEV}/microduck/robot_walk.xml")
ankle_v1_use = {os.path.basename(x): grep_count(x, r'mesh="ankle_[lr]_v1"') for x in
                [f"{DEV}/microduck/robot_walk.xml", f"{DEV}/microduck/robot_groundcontact.xml", f"{DEV}/microduck/robot_allcollisions.xml"]}
ankle_use = {os.path.basename(x): grep_count(x, r'mesh="ankle_(left|right)"') for x in
             [f"{DEV}/microduck/robot_walk.xml", f"{DEV}/microduck/robot_groundcontact.xml", f"{DEV}/microduck/robot_allcollisions.xml"]}
contacts_note = open(f"{DEV}/microduck/allcollisions_contacts.xml").read()
readme = open(f"{DEV}/microduck_rl_README.md").read().splitlines()
lic_lines = [(i + 1, l) for i, l in enumerate(readme) if "licen" in l.lower() or l.strip() == "## License"]
lic_quote = "\n".join(f"{n}: {l}" for n, l in lic_lines)

# ---- our own documents that carry a number this source moved or superseded ----
def repo_hits(pattern, exclude=("out/", "reference/", "research/raw/", "trash/", ".git/", "__pycache__", "node_modules")):
    hits = []
    for root, dirs, fs in os.walk(R):
        rel = os.path.relpath(root, R) + "/"
        if any(rel.startswith(e) or f"/{e}" in rel for e in exclude):
            dirs[:] = []; continue
        for f in fs:
            if f.endswith((".png", ".jpg", ".stl", ".step", ".glb", ".pdf", ".mp4", ".bin", ".pyc")):
                continue
            p = os.path.join(root, f)
            try:
                for i, line in enumerate(open(p, errors="ignore")):
                    if re.search(pattern, line):
                        hits.append(f"{os.path.relpath(p, R)}:{i+1}")
            except Exception:
                pass
    return sorted(hits)
old_colour_hits = repo_hits(r"fab601|89dad3|cfdbe5|0\.980392 0\.713725|0\.537255 0\.854902|c4e2f3")
licence_40_hits = repo_hits(r"BY-SA-NC 4\.0|BY-NC-SA 4\.0")
old_pin_hits = repo_hits(r"5946fd9")
tof_hits = repo_hits(r"VL53L5CX/L8CX|L5CX/L8CX")

# ---- summaries ---------------------------------------------------------------------
mrows = mesh["meshes"]
mesh_summary = {
    "common": len(mrows),
    "PASS": sum(1 for v in mrows.values() if v["compare"]["verdict"] == "PASS"),
    "FAIL": sum(1 for v in mrows.values() if v["compare"]["verdict"] == "FAIL"),
    "CANNOT DETERMINE": sum(1 for v in mrows.values() if v["compare"]["verdict"] not in ("PASS", "FAIL")),
    "worst_p95_mm": max(max(v["compare"]["old_to_new"]["p95_mm"], v["compare"]["new_to_old"]["p95_mm"]) for v in mrows.values()),
    "worst_max_sample_mm": max(max(v["compare"]["old_to_new"]["max_mm"], v["compare"]["new_to_old"]["max_mm"]) for v in mrows.values()),
    "worst_bbox_delta_mm": max(max(abs(x) for x in v["bbox_delta_mm"]["size_mm"] + v["bbox_delta_mm"]["centre_mm"]) for v in mrows.values()),
    "vertex_identical": sum(1 for v in mrows.values() if v["vertex_set_identical"]),
    "retriangulated": sorted(k for k, v in mrows.items() if not v["vertex_set_identical"]),
    "byte_identical": 0,
    "only_in_old": mesh["only_in_old"], "only_in_new": mesh["only_in_new"],
}
mat_changed = {m: r for m, r in mj["materials"].items() if r["verdict"] == "CHANGED"}
palette_new = {}
for m, r in mj["materials"].items():
    palette_new.setdefault(r["new_hex"], []).append(m.replace("_material", ""))

findings = [
 {"id": "F1", "finding": "The develop tree carries NO geometry our seeded copy lacks. All 43 common STLs are the same surface: p95 0.0000 mm both ways and bbox delta 0.0000 mm on every axis (SPEC.md §8 rule, 15 000 area-weighted samples each way, no alignment). 8 meshes were re-triangulated by the re-export (different vertex set, same surface; worst single sample 2.3557 mm on upper_leg_left is a chord of the new tessellation, not a moved face). No fastener seats, insert bosses, ball sockets, STEP, print files or assembly exist anywhere in the tree — it is still onshape-to-robot's decimated visual export (`max_stl_size: 1.0`, `simplify_stls: true` in every config_mjcf_*.json).",
  "evidence": "out/sources/upstream-develop-meshdiff.json (43 rows); config_mjcf_walk.json:6-7; git ls-tree 29e887e -- src/mjlab_microduck/robot/microduck (no .step/.3mf/.f3d)",
  "changes_what": "Nothing in the CAD. The 145-hole / zero-fastener gap (GOAL.md standing order 1) is NOT closed by this source; it stays with the fastener lane and the MakerWorld source (SOURCE 1)."},
 {"id": "F2", "finding": f"What DID move is colour: {len(mat_changed)} of {len(mj['materials'])} <material rgba> values changed in commit 8dfc08f 're-export all robot models from updated CAD (new colors)'. Feet, jaw, ankles and bottom_head_shell go #fab601 (yellow) -> #ff671f (orange); soles and the eye ring (noenoeil) -> #f4af23; trunk_base, yaw2roll, bearing_roll, motor_support, yaw_roll_motion -> #212721 (near-black); hip_l, neck, leg, face_part, power_support, rigidity plate -> #aca39a (warm grey); top_head_shell, right_shell, upper legs -> #d9d9d6; battery -> #4d4d4d. Rendered old-beside-new with MuJoCo at the STAND keyframe: out/sources/render-colours-old-vs-new.png.",
  "evidence": "out/sources/upstream-develop-mjcfdiff.json materials; robot_walk.xml <asset> diff 5946fd9..29e887e; render read back (front ink 0.1227 old / 0.1252 new)",
  "changes_what": f"Every document of ours that prints the OLD MJCF palette as Pollen's: {len(old_colour_hits)} lines — " + ", ".join(old_colour_hits[:12]) + (" …" if len(old_colour_hits) > 12 else "") + ". SPEC.md:38 ('beak/feet/ankles #fab601 yellow; soles + rigidity plate #89dad3 mint') is superseded. The new palette is the CREAM colourway's trim (orange feet/beak, yellow eye ring) and should drive our render materials."},
 {"id": "F3", "finding": "Four STLs vanished upstream. left_upper_leg / right_upper_leg were exact duplicates of upper_leg_left / upper_leg_right (p95 0.0000 mm, same 12 250 triangles, same bbox 28.0000 x 47.6594 x 60.9966 mm) from a stale Onshape microversion 49900cb4. trunk_shell_left / trunk_shell_right were an OLDER trunk-shell revision: 30.9000 x 82.4292 x 35.6959 mm against left_shell's 33.7145 x 80.8901 x 41.6905 mm, p95 2.9439 / 8.0664 mm — FAIL against the survivors, so they were a different part, not a rename.",
  "evidence": "out/sources/upstream-develop-meshdiff.json removed_vs_survivor; .part sidecars at 5946fd9 (documentMicroversion 49900cb439825f734c36e098)",
  "changes_what": "Nothing of ours references them (0 hits in sim/microduck_ours.xml, spec/mesh-placements.json, ce-assemblies/microduck/current/placements.json). reference/pollen-microduck-rl/assets/ keeps them as history; the develop tree is the one to seed from now."},
 {"id": "F4", "finding": "Every NUMBER in robot_walk.xml is unchanged between our pin and develop: 14 joint ranges (max |delta| 0.000000 deg), 15 inertial masses (total 737.2431 g both), CoMs (max 0.0001 mm), full inertias, body positions, 7 site positions, all 75 geom placements, the actuator classes (chosen_actuator kp 0.55, forcerange +-0.96, damping 0.053, frictionloss 0.0048, armature 0.0018), and the INIT/STAND/SIT/FOLD keyframes. sim/microduck_ours.xml agrees with develop on all 14 ranges and 15 masses.",
  "evidence": "out/sources/upstream-develop-mjcfdiff.json summary (joints_changed_beyond_eps [], mass_max_abs_change_g 0, geom_placement_changes 0, defaults/actuators/keyframes same_old_new true)",
  "changes_what": "No joint range, mass or keyframe published in SPEC.md §2-3, ce-assemblies/microduck/current/joints.json or MOTION/LEG-MOTION/HEAD-MOTION is invalidated by this source."},
 {"id": "F5", "finding": f"The runtime repo (pollen-robotics/microduck bc41fb5, 2026-09-03) bundles a DIFFERENT, older MJCF for its own FK/odometry: kinematics/assets/alpha/robot_walk.xml (last changed cc972c5, 2026-08-21). Total mass {main['total_mass_g']['main']} g vs {main['total_mass_g']['develop']} g; trunk_base 264.3850 g vs 199.2240 g; yaw_roll_motion 24.9200 vs 48.6000 g; ankles 26.4653 vs 30.0246 g; the head body is still named bottom_head_shell (develop: jaw_soft); head_camera / head_imu / tof sites sit +3.7500 mm further forward (x) and +0.2000 mm up; the trunk imu site is at z -14.8911 vs -14.6984 mm; the neck body origin differs by (0, -0.0011, -0.0209) mm; and it carries an extra site imu_bno at (-32.0000, 14.0011, 43.0618) mm that develop dropped. Joint ranges are identical (max 3.0e-12 deg).",
  "evidence": "out/sources/upstream-main-alpha-vs-develop.json; reference/pollen-microduck-rl-develop/sibling-pollen-microduck-main/",
  "changes_what": "The robot's own kinematics crate and Pollen's sim disagree by up to 3.75 mm on the camera/ToF/IMU positions and by 7.118 g on mass. Which one the BUILT unit matches is CANNOT DETERMINE from either file — a photograph of the head interior or a calliper on the camera aperture settles it. Our SPEC.md §3 sensor sites quote the sim values; they should say the runtime disagrees."},
 {"id": "F6", "finding": "Pollen MEASURED an interference in their own model and wrote it into the tree: allcollisions_contacts.xml — 'The jaw closed-loop linkage positions the jaw/bottom_head_shell meshes (merged into the jaw_soft body) 2-4.5mm inside the neck_pitch bracket and its bearing in EVERY pose - a permanent phantom self-contact, measured at the INIT/STAND/SIT keyframes on the 2026-09 export.' They exclude the neck_pitch/jaw_soft contact pair rather than move geometry.",
  "evidence": "reference/pollen-microduck-rl-develop/microduck/allcollisions_contacts.xml:1-10; additional.xml:8-12 (the older 'jaw overlaps bottom head shell by ~2cm' note)",
  "changes_what": "The head-to-neck_pitch interface cannot be taken from these meshes as-is: as placed, the head shells penetrate the neck_pitch bracket by 2-4.5 mm. The joints/harness lane must measure that clash on our assembly (cecad.clearance) and the real bracket clearance is CANNOT DETERMINE until a unit is measured."},
 {"id": "F7", "finding": "New upstream file robot_allcollisions.xml is a TRUE all-collisions export (every part gets a collision geom) and doubles as a per-instance census: 70 collision geoms over 37 meshes — xl330 x15, seeed_bearing 22x16x4 x11, seeed_bearing default (15x10x3) x3, neck x2, leg x2, hip_l x2, bearing_roll x2, yaw2roll x2, upper_leg_rigidity_plate x2, everything else x1; power_support demoted to self_collision_only.",
  "evidence": "regex census of reference/pollen-microduck-rl-develop/microduck/robot_allcollisions.xml (this generator, collision_census)",
  "changes_what": "Corroborates SPEC.md §4 (15 servos, bearings 11 + 3). A ready-made full-contact model for the simulation lane's drop/self-collision runs — no task upstream uses it yet (microduck_constants.py:22-25)."},
 {"id": "F8", "finding": "Upstream defect inherited by every sim of ours copied from 'allcollisions': config_mjcf_groundcontact.json's ignore list un-ignores parts by their OLD Onshape names ('!left_upper_leg', '!right_upper_leg', '!trunk_shell_left', '!trunk_shell_right'), but the exported parts are now named upper_leg_left / left_shell etc., so the thighs and the trunk shells carry NO collision geom in robot_groundcontact.xml (measured census: bottom_head_shell, hip_l x2, jaw, leg x2, np_f970, sole_left, sole_right, top_head_shell, power_support[self] — nothing else). microduck_constants.py:17-20 claims the set includes 'trunk shells'. Same census in our 5946fd9 copy's robot_allcollisions.xml.",
  "evidence": "config_mjcf_groundcontact.json:8-21; regex census of robot_groundcontact.xml (this generator); .part names upper_leg_left <1>, left_shell <1>",
  "changes_what": "out/sim-sweep/scene_walk_allcollisions.xml and every 'allcollisions' run in SIMULATION.html modelled a robot whose thighs and egg shells cannot touch the floor. Sit/stand/roulade and fall results that rest on that model need re-judging against robot_allcollisions.xml (F7)."},
 {"id": "F9", "finding": "Licence, settled from the primary text: README.md:260-261 at 29e887e reads 'This project is licensed under the Apache 2.0 License. See the LICENSE file for details.' / '3D model files are licensed under Creative Commons BY-SA-NC.' — no version number, and the CC text is not shipped (LICENSE is Apache-2.0 only). The same two lines were at README.md:195-196 in our 5946fd9 copy.",
  "evidence": "reference/pollen-microduck-rl-develop/microduck_rl_README.md:258-261; reference/pollen-microduck-rl-develop/LICENSE-Apache-2.0.txt",
  "changes_what": "Cite 'CC BY-SA-NC (version not stated)'. " + (f"{len(licence_40_hits)} lines of ours assert '4.0' that the source does not: " + ", ".join(h for h in licence_40_hits if not h.startswith("research/")) if licence_40_hits else "No file of ours asserts a version.") + " — ce-parts/microduck-eye-ring/component.json:15 already has it right ('version not stated'); the two '4.0' strings are lane A's to drop."},
 {"id": "F10", "finding": "Runtime constants read off pollen-robotics/microduck (bc41fb5) corroborate SPEC.md: mouth travel -5 deg closed / +30 deg open (duck-control/src/model.rs:62-63); battery window 6.6-8.2 V (model.rs:109,113 BATTERY_EMPTY_V/BATTERY_FULL_V); servo position gain 200 (deploy/robotd.toml:136 'gain = 200', joints_properties.xml '200 kp', microduck_constants.py kp_fw=200); IDs 30-34 = neck, head, mouth (model.rs:17); bus /dev/ttyS2 at 50 Hz (robotd.toml:20,41). The ToF is named specifically: 'tof VL53L8CX · 15 Hz · 8x8 · 48/64 ranged · 0.12-3.54 m' (docs/robot/cheatsheet.md:691) where SPEC.md §5 hedges 'VL53L5CX/L8CX'. BAM actuator domain randomisation upstream: vin 6.5-8.2 V, load sag gain 0-0.2, vin_min 6.0, 3-6 tick delay, backlash +-1 deg (2 deg total).",
  "evidence": "reference/pollen-microduck-rl-develop/sibling-pollen-microduck-main/deploy/robotd.toml; microduck_constants.py:132-144; microduck_rl add_backlash.py:26-28",
  "changes_what": ("SPEC.md §5 ToF row can name VL53L8CX (cheatsheet line 691 is the live monitor's own header). " + (", ".join(tof_hits) if tof_hits else "")) },
 {"id": "F11", "finding": "Onshape provenance is cleaner upstream: all 37 core .part sidecars now carry ONE documentMicroversion 2f167ea7efece4caa36b89eb (plus 9306fb07 for jaw_soft / soft_mouth_top / neck_pitch and f694115e for rim / tire / roller_blade, unchanged), where our 5946fd9 copy mixed five microversions (fc823765 x31, 48ccc523 x6, 49900cb4 x4, 9306fb07 x3, f694115e x3). The document is still 804927696f06d877f3f1803e, workspace 5b75db19292e71970de02dee, element ef6e972847fec8d82570b35e (config_mjcf_*.json url), and still not readable without a key.",
  "evidence": "reference/pollen-microduck-rl-develop/microduck/assets/*.part; config_mjcf_walk.json:2",
  "changes_what": "SPEC.md §1's Onshape row can carry the workspace/element ids; every ce-parts folder that cites a .part microversion should cite 2f167ea7 from now on."},
 {"id": "F12", "finding": "Two things in the tree were never in reference/ before: robot/xl330_test_bench/ (Pollen's BAM servo-identification rig — 11 STL + MJCF, a 100 g arm on a +-80 deg hinge, its own Onshape element 54c1186243f1b4db10e4bd59) and apartment.xml / scene_apartment.xml (a walk-around scene, no mechanics). The test bench's xl330.stl is byte-identical to our OLD xl330.stl (sha256 c9f6bf7d…), i.e. the servo mesh before the 2026-09-01 re-export.",
  "evidence": "reference/pollen-microduck-rl-develop/xl330_test_bench/; shasum of xl330_test_bench/assets/xl330.stl vs reference/pollen-microduck-rl/assets/xl330.stl",
  "changes_what": "The rig is a candidate for TEST-PLAN.html's servo-characterisation step (a printable fixture that Pollen themselves used to fit the BAM model)."},
 {"id": "F13", "finding": f"Ankle revision (GOAL.md finding 4): develop still SHIPS ankle_l_v1 / ankle_r_v1 STLs but PLACES none of them — 0 geoms reference ankle_[lr]_v1 in robot_walk.xml, robot_groundcontact.xml or robot_allcollisions.xml, while ankle_left / ankle_right are placed {ankle_use['robot_walk.xml']} / {ankle_use['robot_groundcontact.xml']} / {ankle_use['robot_allcollisions.xml']} times. The _v1 pair is an unplaced export of an older part.",
  "evidence": "regex count of mesh=\"ankle_[lr]_v1\" vs mesh=\"ankle_(left|right)\" across the three develop models (this generator)",
  "changes_what": "ankle_left / ankle_right are current in Pollen's own model; ankle_l_v1 / ankle_r_v1 should not be drawn, quoted or priced as a live part."},
]

verdicts = [
 {"item": "Upstream tree fetched, commit SHA pinned, fetch date and licence recorded", "verdict": "PASS", "evidence": f"reference/pollen-microduck-rl-develop/SOURCE-COMMIT.txt: {NEW_SHA} (2026-09-02 22:20:08 +0200), fetched 2026-09-03 23:11 +0800"},
 {"item": "Licence text quoted verbatim and version settled", "verdict": "PASS", "evidence": "README.md:261 '3D model files are licensed under Creative Commons BY-SA-NC.' — no version; '4.0' in two of our files is unsupported"},
 {"item": "Every common mesh within SPEC.md §8 (p95 <= 1.0 mm both ways, bbox <= 1.5 mm/axis) between pin and develop", "verdict": "PASS", "evidence": f"{mesh_summary['PASS']}/{mesh_summary['common']} PASS, worst p95 {mesh_summary['worst_p95_mm']:.4f} mm, worst bbox delta {mesh_summary['worst_bbox_delta_mm']:.4f} mm"},
 {"item": "Develop carries geometry our seeded copy lacked (fasteners, inserts, ball sockets, print files, assembly, newer head shell)", "verdict": "FAIL", "evidence": "0 new STLs (only_in_new = []); 43/43 surfaces identical; no STEP/3MF/assembly in the tree; top_head_shell p95 0.0000 mm"},
 {"item": "Joint ranges, masses, inertials, actuator params, keyframes unchanged upstream (nothing of ours invalidated)", "verdict": "PASS", "evidence": "upstream-develop-mjcfdiff.json: 0 joints changed, 0 inertials changed, defaults/actuators/keyframes identical; ours agrees on 14/14 ranges and 15/15 masses"},
 {"item": "Material colours unchanged upstream", "verdict": "FAIL", "evidence": f"{len(mat_changed)}/{len(mj['materials'])} rgba changed; {len(old_colour_hits)} lines of ours print the old palette"},
 {"item": "Runtime repo's bundled MJCF agrees with the sim MJCF", "verdict": "FAIL", "evidence": f"total mass {main['total_mass_g']['main']} vs {main['total_mass_g']['develop']} g; head sites +3.7500 mm x; trunk imu z -14.8911 vs -14.6984 mm"},
 {"item": "Which of the two head sensor-site positions the built unit has", "verdict": "CANNOT DETERMINE", "evidence": "two official files disagree by 3.75 mm; settled by a photograph of the head interior or a calliper on the camera aperture"},
 {"item": "Real clearance between head shells and neck_pitch bracket", "verdict": "CANNOT DETERMINE", "evidence": "Pollen measured 2-4.5 mm interference in their own export (allcollisions_contacts.xml) and excluded the contact instead of fixing geometry"},
 {"item": "groundcontact / 'allcollisions' collision set covers thighs and trunk shells as documented", "verdict": "FAIL", "evidence": "ignore list uses stale part names; measured census has no upper_leg_* or *_shell collision geom"},
 {"item": "Current ankle revision", "verdict": "PASS", "evidence": f"ankle_left/right placed in all three models; ankle_[lr]_v1 placed 0 times ({ankle_v1_use})"},
]

invalidated = {
  "old_mjcf_palette_lines": old_colour_hits,
  "licence_version_asserted_lines": licence_40_hits,
  "old_pin_5946fd9_lines": old_pin_hits,
  "tof_hedged_lines": tof_hits,
}

out = {
 "what": "SOURCE 2 — pollen-robotics/microduck_rl, DEVELOP branch, src/mjlab_microduck/robot/microduck/assets and its siblings: fetched, pinned, licensed, and diffed file-by-file, mesh-by-mesh and number-by-number against the copy that seeded our model.",
 "generated": NOW, "generator": "tools/gen_upstream_develop.py",
 "source": {"repo": "https://github.com/pollen-robotics/microduck_rl", "branch": "develop", "commit": NEW_SHA, "commit_date": "2026-09-02 22:20:08 +0200",
            "fetched": "2026-09-03 23:11 +0800", "path": "src/mjlab_microduck/robot/microduck/", "archived_as": "reference/pollen-microduck-rl-develop/",
            "assets_last_commit": "8dfc08f33d408e62ca2e9d3ec107d0acbe747a91 2026-09-01 16:39:02 +0200 'chore: re-export all robot models from updated CAD (new colors)'",
            "onshape": {"documentId": "804927696f06d877f3f1803e", "workspace": "5b75db19292e71970de02dee", "element": "ef6e972847fec8d82570b35e", "microversion_core": "2f167ea7efece4caa36b89eb"},
            "licence": {"code": "Apache-2.0", "models": "Creative Commons BY-SA-NC (no version stated)", "quote": lic_quote, "where": "reference/pollen-microduck-rl-develop/microduck_rl_README.md",
                        "attribution": "Pollen Robotics (Bordeaux), Antoine Pirrone (apirrone); exported from Onshape with onshape-to-robot"}},
 "previous_copy": {"commit": OLD_SHA, "commit_date": "2026-09-01 14:09:12 +0200", "path": "reference/pollen-microduck-rl/", "cited_in": "research/02-repos-and-code.md:29"},
 "sibling_runtime_repo": {"repo": "https://github.com/pollen-robotics/microduck", "commit": "bc41fb5c9a9b39894669c1e022e375cf83800382", "commit_date": "2026-09-03 14:46:02 +0200",
                          "archived_as": "reference/pollen-microduck-rl-develop/sibling-pollen-microduck-main/", "mjcf_last_changed": "cc972c5 2026-08-21", "diff": "out/sources/upstream-main-alpha-vs-develop.json"},
 "file_diff": {"counts": files["counts"], "commits_between": files["commits_between"],
               "changed_non_asset": [r for r in files["files"] if r["status"] not in ("unchanged", "same") and not r["path"].startswith("assets/")],
               "assets": {"stl_old": 47, "stl_new": 43, "byte_identical": 0, "removed": mesh["only_in_old"], "added": mesh["only_in_new"]},
               "all": files["files"]},
 "mesh_diff": {"rule": mesh["rule"], "summary": mesh_summary, "removed_vs_survivor": mesh.get("removed_vs_survivor", {}),
               "rows": {k: {"verdict": v["compare"]["verdict"], "old_bbox_size_mm": v["old"]["bbox"]["size_mm"], "new_bbox_size_mm": v["new"]["bbox"]["size_mm"],
                            "old_bbox_min_mm": v["old"]["bbox"]["min_mm"], "new_bbox_min_mm": v["new"]["bbox"]["min_mm"],
                            "bbox_size_delta_mm": v["bbox_delta_mm"]["size_mm"], "bbox_centre_delta_mm": v["bbox_delta_mm"]["centre_mm"],
                            "p95_old_to_new_mm": v["compare"]["old_to_new"]["p95_mm"], "p95_new_to_old_mm": v["compare"]["new_to_old"]["p95_mm"],
                            "max_old_to_new_mm": v["compare"]["old_to_new"]["max_mm"], "max_new_to_old_mm": v["compare"]["new_to_old"]["max_mm"],
                            "tris_old": v["old"]["tris"], "tris_new": v["new"]["tris"], "vertex_set_identical": v["vertex_set_identical"],
                            "sha256_old": v["old"]["sha256"][:16], "sha256_new": v["new"]["sha256"][:16]} for k, v in mrows.items()}},
 "mjcf_diff": {"summary": mj["summary"], "total_mass_g": mj["total_mass_g"], "counts": mj["counts"],
               "joints": mj["joints"], "inertials": {b: {k: r[k] for k in ("old_mass_g", "new_mass_g", "ours_mass_g", "new_minus_old_mass_g", "new_minus_old_com_mm", "verdict")} for b, r in mj["inertials"].items()},
               "materials": mj["materials"], "new_palette": palette_new, "actuator_defaults_same": mj["defaults"]["same_old_new"], "keyframes_same": mj["keyframes"]["same_old_new"]},
 "runtime_vs_develop": {"total_mass_g": main["total_mass_g"], "inertials": main["inertials"], "sites": main["sites"],
                        "bodies_moved": {k: v for k, v in main["bodies"].items() if v["delta_mm"] and max(abs(x) for x in v["delta_mm"]) > 1e-4}},
 "collision_census": {"robot_allcollisions.xml": allcol, "robot_groundcontact.xml": groundcontact, "robot_walk.xml_visual": walk_vis,
                      "ankle_v1_placed": ankle_v1_use, "ankle_current_placed": ankle_use},
 "upstream_measured_interference": contacts_note,
 "findings": findings, "verdicts": verdicts, "documents_to_update": invalidated,
 "artifacts": ["out/sources/upstream-develop.json", "out/sources/upstream-develop.html", "out/sources/upstream-develop-meshdiff.json", "out/sources/upstream-develop-mjcfdiff.json",
               "out/sources/upstream-develop-files.json", "out/sources/upstream-main-alpha-vs-develop.json", "out/sources/render-colours-old-vs-new.png",
               "reference/pollen-microduck-rl-develop/", "tools/upstream_meshdiff.py", "tools/upstream_mjcfdiff.py", "tools/upstream_render.py", "tools/gen_upstream_develop.py"],
}
json.dump(out, open(f"{S}/upstream-develop.json", "w"), indent=1)

# ---- HTML ---------------------------------------------------------------------------
E = html.escape
def chip(v):
    c = {"PASS": "ok", "FAIL": "no", "CANNOT DETERMINE": "cd"}.get(v, "")
    return f'<span class="chip {c}">{E(v)}</span>'
def sw(hexc):
    return f'<span style="display:inline-block;width:14px;height:14px;border:1px solid #999;vertical-align:middle;background:{hexc}"></span> <code>{hexc}</code>' if hexc else "—"
H = []
H.append(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Source 2 — microduck_rl develop</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="../../tools/doc.css">
<style>
 .chip.no{{color:var(--no)}} .chip.ok{{color:var(--ok,#2f7d52)}} .chip.cd{{color:#8a6d1f}}
 .verdict{{border-left:3px solid var(--accent);padding:2px 0 2px 18px;margin:14px 0;font-size:15.5px}} .verdict b{{color:var(--accent)}}
 .verdict.warn{{border-left-color:var(--no)}} .verdict.warn b{{color:var(--no)}}
 .statbar{{display:flex;flex-wrap:wrap;gap:0;border-bottom:1px solid var(--hair);margin:8px 0 2px}}
 .stat{{padding:10px 22px 10px 0;margin-right:22px}} .stat b{{display:block;font-size:22px}} .stat span{{font-family:var(--sans);font-size:12px;color:var(--ink-2)}}
 table.data{{font-size:12.5px;border-collapse:collapse;width:100%}} table.data th,table.data td{{padding:3px 6px;border-bottom:1px solid var(--hair);text-align:left;vertical-align:top}}
 table.data td code{{font-size:11.5px}} figure{{margin:12px 0}} figure img{{width:100%;background:#fff;border:1px solid var(--hair)}} figcaption{{font-family:var(--sans);font-size:12.5px;color:var(--ink-2)}}
 pre.q{{font-size:12px;background:#faf8f3;border-left:3px solid var(--hair);padding:8px 12px;white-space:pre-wrap}}
 #findings table.data{{table-layout:fixed}} #findings td:nth-child(1){{width:32px}} #findings td:nth-child(2){{width:44%}} #findings td:nth-child(3){{width:22%}} #findings td{{overflow-wrap:anywhere}}
</style></head><body><div class="wrap">
<p class="backlink"><a href="../../INDEX.html">← Repository index</a> · <a href="../../GOAL.md">GOAL.md</a> · <a href="../../SPEC.md">SPEC.md</a></p>
<header class="hero"><p class="eyebrow">Microduck reverse-engineering · new sources · source 2</p>
<h1>pollen-robotics/microduck_rl, <code>develop</code> — what moved since the copy that seeded us</h1>
<p class="sub">The same origin as every mesh and number in our model, one branch and 24 commits later. Fetched, pinned at <code>{NEW_SHA[:7]}</code>, licence quoted, then diffed file by file, mesh by mesh (cecad.meshcompare, SPEC.md §8 rule) and number by number against our <code>{OLD_SHA[:7]}</code> copy, our SPEC.md, joints.json and sim/microduck_ours.xml. Generated {E(NOW)} by tools/gen_upstream_develop.py from out/sources/*.json.</p>
<div class="rev">Leif, verbatim: “Give the microduck these researches to injest and utilize … the cad and 3d printable files and stuff should be in these resourches tell it to dive deeply into it”.</div></header>
<div class="statbar">
 <div class="stat"><b>{mesh_summary['common']}</b><span>meshes in both trees</span></div>
 <div class="stat"><b>{mesh_summary['PASS']}/{mesh_summary['common']}</b><span>same surface (p95 {mesh_summary['worst_p95_mm']:.4f} mm)</span></div>
 <div class="stat"><b>0</b><span>new STLs upstream</span></div>
 <div class="stat"><b>{len(mesh['only_in_old'])}</b><span>STLs removed upstream</span></div>
 <div class="stat"><b>0 / 0</b><span>joint ranges / masses changed</span></div>
 <div class="stat"><b>{len(mat_changed)}/{len(mj['materials'])}</b><span>material colours changed</span></div>
 <div class="stat"><b>{len(old_colour_hits)}</b><span>lines of ours printing the old palette</span></div>
 <div class="stat"><b>{main['total_mass_g']['main'] - main['total_mass_g']['develop']:+.4f} g</b><span>runtime MJCF vs sim MJCF</span></div>
</div>
<nav class="toc"><a href="#answer">1 Verdict</a> <a href="#pin">2 Pin &amp; licence</a> <a href="#files">3 Files</a> <a href="#meshes">4 Meshes</a> <a href="#numbers">5 Numbers</a> <a href="#colours">6 Colours</a> <a href="#runtime">7 Runtime model</a> <a href="#census">8 Censuses</a> <a href="#findings">9 Findings</a> <a href="#verdicts">10 Verdicts</a> <a href="#docs">11 Our documents to update</a></nav>
""")
H.append('<section id="answer"><h2><span class="n">1</span>Verdict — does develop carry anything our seeded copy did not?</h2>')
H.append(f'<div class="verdict warn"><b>No new geometry.</b> All {mesh_summary["common"]} common STLs are the same surface to 0.0000 mm (p95, both ways, 15 000 samples each); 0 STLs were added; the tree still holds only onshape-to-robot’s decimated visual export — no fastener seats, insert bosses, ball sockets, STEP, print files or assembly. The 145-hole / zero-fastener gap is <b>not</b> closed by this source.</div>')
H.append(f'<div class="verdict"><b>What did move:</b> {len(mat_changed)} of {len(mj["materials"])} material colours (the cream colourway’s orange trim and yellow eye ring, F2); four orphan STLs dropped (F3); a TRUE all-collisions model with a per-instance census (F7); a measured 2–4.5 mm head/neck_pitch interference written into the tree by Pollen (F6); a stale-name defect that leaves thighs and trunk shells without collision geoms in the “groundcontact” family (F8). Every joint range, mass, inertia, actuator parameter and keyframe is unchanged (F4), so nothing published in SPEC.md §2–3, joints.json or the motion documents is invalidated by this branch.</div>')
H.append(f'<div class="verdict warn"><b>The robot’s own runtime bundles a different, older model</b> (pollen-robotics/microduck, kinematics/assets/alpha/robot_walk.xml): {main["total_mass_g"]["main"]} g against {main["total_mass_g"]["develop"]} g, head sensor sites 3.7500 mm further forward, an extra <code>imu_bno</code> site. Which one the built unit matches is CANNOT DETERMINE from the files (F5).</div></section>')

H.append('<section id="pin"><h2><span class="n">2</span>Pin, provenance and licence</h2><pre class="q">' + E(srccommit) + '</pre>')
H.append('<p class="lede">The licence lines, verbatim from README.md at this commit (line numbers are the file’s):</p><pre class="q">' + E(lic_quote) + '</pre></section>')

H.append(f'<section id="files"><h2><span class="n">3</span>File-level diff of <code>src/mjlab_microduck/robot/microduck/</code>, {OLD_SHA[:7]}..{NEW_SHA[:7]}</h2>')
H.append('<p class="lede">Counts: ' + ", ".join(f"{k} {v}" for k, v in files["counts"].items()) + '. Every STL and every .part sidecar is “modified” (new Onshape microversion, re-decimated); the non-asset changes are listed in full.</p>')
H.append('<table class="data"><tr><th>path</th><th>status</th><th>renamed from</th><th>old bytes</th><th>new bytes</th></tr>')
for r in out["file_diff"]["changed_non_asset"]:
    H.append(f'<tr><td><code>{E(r["path"])}</code></td><td>{E(r["status"])}</td><td>{E(r["renamed_from"] or "")}</td><td>{r["old_bytes"] if r["old_bytes"] is not None else "—"}</td><td>{r["new_bytes"] if r["new_bytes"] is not None else "—"}</td></tr>')
H.append('</table><p class="lede">Commits between the two pins that touched this path:</p><ul>' + "".join(f"<li><code>{E(c)}</code></li>" for c in files["commits_between"]) + '</ul></section>')

H.append(f'<section id="meshes"><h2><span class="n">4</span>Mesh by mesh — {mesh_summary["common"]} STLs in both trees</h2><p class="lede">{E(mesh["rule"])}. bbox in the part’s own file frame, mm, 4 dp; p95/max are surface distances in mm. “verts” = the two files carry the identical vertex set (a re-decimated mesh does not, yet its surface can still be 0.0000 mm away).</p>')
H.append('<table class="data"><tr><th>mesh</th><th>verdict</th><th>old bbox size</th><th>new bbox size</th><th>Δsize</th><th>Δcentre</th><th>p95 old→new</th><th>p95 new→old</th><th>max</th><th>tris old→new</th><th>verts</th></tr>')
for k, v in out["mesh_diff"]["rows"].items():
    f4 = lambda a: " × ".join(f"{x:.4f}" for x in a)
    H.append(f'<tr><td><code>{E(k)}</code></td><td>{chip(v["verdict"])}</td><td>{f4(v["old_bbox_size_mm"])}</td><td>{f4(v["new_bbox_size_mm"])}</td><td>{f4(v["bbox_size_delta_mm"])}</td><td>{f4(v["bbox_centre_delta_mm"])}</td><td>{v["p95_old_to_new_mm"]:.4f}</td><td>{v["p95_new_to_old_mm"]:.4f}</td><td>{max(v["max_old_to_new_mm"], v["max_new_to_old_mm"]):.4f}</td><td>{v["tris_old"]}→{v["tris_new"]}</td><td>{"same" if v["vertex_set_identical"] else "re-tri"}</td></tr>')
H.append('</table><h3>Removed upstream, compared with the part that survives</h3><table class="data"><tr><th>removed STL</th><th>survivor</th><th>verdict</th><th>removed bbox size</th><th>survivor bbox size</th><th>p95 removed→survivor</th><th>p95 survivor→removed</th><th>tris</th></tr>')
for k, v in out["mesh_diff"]["removed_vs_survivor"].items():
    H.append(f'<tr><td><code>{E(k)}</code></td><td><code>{E(v["survivor_in_new"])}</code></td><td>{chip(v["verdict"])}</td><td>{" × ".join(f"{x:.4f}" for x in v["removed_bbox"]["size_mm"])}</td><td>{" × ".join(f"{x:.4f}" for x in v["survivor_bbox"]["size_mm"])}</td><td>{v["removed_to_survivor_p95_mm"]:.4f}</td><td>{v["survivor_to_removed_p95_mm"]:.4f}</td><td>{v["removed_tris"]} / {v["survivor_tris"]}</td></tr>')
H.append('</table></section>')

H.append('<section id="numbers"><h2><span class="n">5</span>Numbers — robot_walk.xml pin vs develop vs ours</h2>')
H.append(f'<p class="lede">Total inertial mass: pin {mj["total_mass_g"]["old_5946fd9"]} g · develop {mj["total_mass_g"]["new_29e887e"]} g · ours {mj["total_mass_g"]["ours"]} g. Defaults/actuators identical: {mj["defaults"]["same_old_new"]} · keyframes identical: {mj["keyframes"]["same_old_new"]} · geom placements changed: {mj["summary"]["geom_placement_changes"]}.</p>')
H.append('<table class="data"><tr><th>joint</th><th>pin range (deg)</th><th>develop range (deg)</th><th>Δ (deg)</th><th>ours (deg)</th><th>ours vs develop</th></tr>')
for j, r in mj["joints"].items():
    H.append(f'<tr><td><code>{E(j)}</code></td><td>{r["old_deg"]}</td><td>{r["new_deg"]}</td><td>{r["new_minus_old_deg"]}</td><td>{r["ours_deg"]}</td><td>{E(r["verdict_ours_vs_new"])}</td></tr>')
H.append('</table><table class="data"><tr><th>body</th><th>pin mass (g)</th><th>develop mass (g)</th><th>Δ (g)</th><th>Δ CoM (mm)</th><th>ours (g)</th></tr>')
for b, r in out["mjcf_diff"]["inertials"].items():
    H.append(f'<tr><td><code>{E(b)}</code></td><td>{r["old_mass_g"]}</td><td>{r["new_mass_g"]}</td><td>{r["new_minus_old_mass_g"]}</td><td>{r["new_minus_old_com_mm"]}</td><td>{r["ours_mass_g"]}</td></tr>')
H.append('</table></section>')

H.append('<section id="colours"><h2><span class="n">6</span>Colours — the one thing the re-export changed</h2>')
H.append('<figure><img src="render-colours-old-vs-new.png" alt="old vs new material colours, MuJoCo render"><figcaption>Pollen’s own robot_walk.xml rendered with its own &lt;material rgba&gt;, STAND keyframe, same camera: top row our pin 5946fd9, bottom row develop 29e887e. tools/upstream_render.py; read back — front-view ink 0.1227 / 0.1252.</figcaption></figure>')
H.append('<table class="data"><tr><th>material</th><th>pin</th><th>develop</th><th>verdict</th><th>ours (sim/microduck_ours.xml)</th></tr>')
for m, r in mj["materials"].items():
    H.append(f'<tr><td><code>{E(m)}</code></td><td>{sw(r["old_hex"])}</td><td>{sw(r["new_hex"])}</td><td>{E(r["verdict"])}</td><td><code>{E(r["ours_rgba"] or "—")}</code></td></tr>')
H.append('</table><h3>The develop palette, grouped</h3><ul>' + "".join(f'<li>{sw(h)} — {E(", ".join(ms))}</li>' for h, ms in sorted(palette_new.items())) + '</ul></section>')

H.append('<section id="runtime"><h2><span class="n">7</span>The runtime’s own model — pollen-robotics/microduck kinematics/assets/alpha/robot_walk.xml</h2>')
H.append(f'<p class="lede">{E(main["what"])}</p><table class="data"><tr><th>body</th><th>runtime mass (g)</th><th>develop mass (g)</th><th>Δ (g)</th><th>Δ CoM (mm)</th></tr>')
for b, r in main["inertials"].items():
    H.append(f'<tr><td><code>{E(b)}</code></td><td>{r["main_mass_g"]}</td><td>{r["develop_mass_g"]}</td><td>{r["delta_g"]}</td><td>{r["delta_com_mm"]}</td></tr>')
H.append('</table><table class="data"><tr><th>site</th><th>runtime (body, mm)</th><th>develop (body, mm)</th><th>Δ (mm)</th></tr>')
for s, r in main["sites"].items():
    H.append(f'<tr><td><code>{E(s)}</code></td><td>{E(str(r["main"]))}</td><td>{E(str(r["develop"]))}</td><td>{r["delta_mm"]}</td></tr>')
H.append('</table></section>')

H.append('<section id="census"><h2><span class="n">8</span>Censuses read off the develop models</h2><p class="lede">Collision geoms per mesh — the true all-collisions model (new upstream) against the “groundcontact” family that our sims copied.</p>')
H.append('<table class="data"><tr><th>mesh [class]</th><th>robot_allcollisions.xml</th></tr>' + "".join(f'<tr><td><code>{E(k)}</code></td><td>{v}</td></tr>' for k, v in allcol.items()) + '</table>')
H.append('<table class="data"><tr><th>mesh [class]</th><th>robot_groundcontact.xml</th></tr>' + "".join(f'<tr><td><code>{E(k)}</code></td><td>{v}</td></tr>' for k, v in groundcontact.items()) + '</table>')
H.append(f'<p>ankle_[lr]_v1 placed: <code>{E(json.dumps(ankle_v1_use))}</code> · ankle_left/right placed: <code>{E(json.dumps(ankle_use))}</code></p>')
H.append('<h3>Upstream’s own measured interference note (allcollisions_contacts.xml, verbatim)</h3><pre class="q">' + E(contacts_note) + '</pre></section>')

H.append('<section id="findings"><h2><span class="n">9</span>Findings</h2><table class="data"><tr><th>#</th><th>finding</th><th>evidence</th><th>what it changes</th></tr>')
for f in findings:
    H.append(f'<tr><td>{E(f["id"])}</td><td>{E(f["finding"])}</td><td><code>{E(f["evidence"])}</code></td><td>{E(f["changes_what"])}</td></tr>')
H.append('</table></section>')
H.append('<section id="verdicts"><h2><span class="n">10</span>Verdicts</h2><table class="data"><tr><th>item</th><th>verdict</th><th>evidence</th></tr>')
for v in verdicts:
    H.append(f'<tr><td>{E(v["item"])}</td><td>{chip(v["verdict"])}</td><td>{E(v["evidence"])}</td></tr>')
H.append('</table></section>')
H.append('<section id="docs"><h2><span class="n">11</span>Our documents that carry something this source superseded</h2>')
for k, lst in invalidated.items():
    H.append(f'<h3>{E(k.replace("_", " "))} — {len(lst)}</h3><ul>' + "".join(f'<li><code>{E(x)}</code></li>' for x in lst) + '</ul>')
H.append('</section></div></body></html>')
open(f"{S}/upstream-develop.html", "w").write("\n".join(H))
print("wrote", f"{S}/upstream-develop.json", f"{S}/upstream-develop.html", "findings", len(findings), "verdicts", len(verdicts), "old-colour lines", len(old_colour_hits), "licence-4.0 lines", len(licence_40_hits), "tof", tof_hits)
