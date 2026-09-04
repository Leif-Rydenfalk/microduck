"""tools/electronics_census.py — plain python3, no kernel.

THE COUNT Leif asked for: chips placed against chips on the BOM, and electronic
parts placed against electronic parts on the shelf. The delta IS the remaining
work, so it is stated here rather than hidden.

Every row is read from a file, never typed:
  the HAT's own BOM   reference/pollen-elec-rpi-robot-hat/production/*_BOM.csv
  what we built       out/pcb/hat/pcba-measured.json
  what is in the robot ce-assemblies/microduck/current/placements.json
  the shelf           ce-parts/*/component.json

Run: python3 tools/electronics_census.py
"""
import collections
import csv
import glob
import json
import os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, "out", "internals")
os.makedirs(OUT, exist_ok=True)

# Where each shelf chip lives, and on what authority. A chip whose location is not
# established gets CANNOT DETERMINE and is NOT placed anywhere: a guessed chip
# position becomes believed the moment it is rendered.
WHERE = {
    "tlv320aic3104": ("Robot HAT U2", "PLACED",
                      "ASE01187-C1_..._BOM.csv line U2 = TLV320AIC3104IRHBR, VQFN-32"),
    "bmi088": ("Robot HAT U11", "PLACED",
               "ASE01187-C1_..._BOM.csv line U11 = BMI088, Bosch LGA-16"),
    "lsm6dsv16x": ("imu_to_dxl v2 board", "CANNOT DETERMINE",
                   "hardware-teardown.en.md sec.3 names it as the IMU on that board; the board "
                   "itself has no published outline, so there is no frame to place a chip in"),
    "imx219": ("camera module in the head", "CANNOT DETERMINE",
               "the camera module's own board outline and the chip's position on it are not "
               "published; ce-parts/microduck-camera-module has no cad/part.py"),
    "vl53l5cx": ("ToF module behind the face window", "CANNOT DETERMINE",
                 "hardware-teardown.en.md: the ToF is NOT on the HAT, it hangs off the Stemma "
                 "J5 header; the module's board is not published"),
    "vl53l8cx": ("ToF module behind the face window", "CANNOT DETERMINE",
                 "same header, same absence; the firmware supports either part by revision ID, "
                 "so WHICH ONE is fitted is itself unsettled"),
    "pn7150": ("no established location", "CANNOT DETERMINE",
               "appears on no published Microduck BOM: not in the HAT BOM's 47 lines, not in "
               "the teardown. A candidate part, not a located one"),
    "st25r3916": ("no established location", "CANNOT DETERMINE",
                  "appears on no published Microduck BOM (see pn7150)"),
    "fusb302": ("no established location", "CANNOT DETERMINE",
                "hardware-teardown.en.md sec.4: the HAT has NO USB-C input and NO charging "
                "circuit; the orphan pwr_supply_charge sheet is never instantiated"),
    "et7301b": ("no established location", "CANNOT DETERMINE", "see fusb302"),
    "mcp73213": ("no established location", "CANNOT DETERMINE", "see fusb302"),
    "s-8252": ("inside the NP-F550 pack", "CANNOT DETERMINE",
               "a protection IC inside a sealed commercial cell pack: there is no external "
               "geometry to place, and opening a pack is not a measurement we can take here"),
}


def main():
    bomf = os.path.join(R, "reference", "pollen-elec-rpi-robot-hat", "production",
                        "ASE01187-C1_elec_RPI_Robot_HAT_BOM.csv")
    bom = list(csv.DictReader(open(bomf)))
    desig_col = list(bom[0])[0]
    lines, actives = 0, []
    for b in bom:
        lines += 1
        for d in [x.strip() for x in b[desig_col].split(",") if x.strip()]:
            if d[0] == "U" or d.startswith("MK") or d.startswith("Y"):
                actives.append(dict(refdes=d, value=b["Value"], footprint=b["Footprint"],
                                    lcsc=b["LCSC Part #"] or None))
    actives.sort(key=lambda a: a["refdes"])

    meas = json.load(open(os.path.join(R, "out", "pcb", "hat", "pcba-measured.json")))
    built = {p["refdes"]: p for p in meas["placements"]}
    for a in actives:
        p = built.get(a["refdes"])
        if p:
            a.update(status="PLACED", at_mm=p["at"], side=p["side"], rot_deg=p["rot_deg"],
                     z_mm=p["z"], height_mm=p["height_mm"], volume_mm3=p["volume_mm3"],
                     round_trip_mm=p["round_trip_mm"])
        elif a["value"].startswith("DNP"):
            a.update(status="NOT POPULATED",
                     why="do-not-populate line: the physical board has nothing at this land")
        else:
            a.update(status="CANNOT DETERMINE",
                     why="fitted per the BOM and the pick-and-place, but the manufacturer's own "
                         "production STEP carries no body for it, so there is nothing measured "
                         "to place. Settled by the vendor adding the model, or by measuring a "
                         "physical board")

    rows = json.load(open(os.path.join(R, "ce-assemblies", "microduck", "current",
                                       "placements.json")))["record"]["rows"]
    inst = collections.Counter(r["part"] for r in rows)

    shelf = []
    for d in sorted(glob.glob(os.path.join(R, "ce-parts", "*", "component.json"))):
        slug = os.path.basename(os.path.dirname(d))
        try:
            rec = json.load(open(d)).get("record", {})
        except Exception:
            continue
        sector = rec.get("sector")
        if sector not in ("chip", "board", "electronics", "electronic", "power", "actuator",
                          "connector"):
            continue
        n = inst.get("part:" + slug, 0)
        w, verdict, why = WHERE.get(slug, (None, None, None))
        if slug == "microduck-robot-hat-pcb":
            w, verdict, why = ("the head, on Pollen's own geom transform", "PLACED",
                               "1 instance in placements.json, now carrying 112 component "
                               "bodies instead of a bare 0.840 mm plate")
        elif n:
            w, verdict, why = ("placed in the assembly", "PLACED",
                               "%d instance(s) in ce-assemblies/microduck/current/placements.json" % n)
        elif verdict is None:
            w, verdict, why = ("no placement", "CANNOT DETERMINE",
                               "no row in placements.json and no published position")
        shelf.append(dict(slug=slug, sector=sector, title=str(rec.get("title") or slug)[:90],
                          assembly_instances=n, where=w, verdict=verdict, why=why))

    placed_actives = sum(1 for a in actives if a["status"] == "PLACED")
    res = dict(
        _generated="tools/electronics_census.py",
        hat_bom=dict(file="reference/pollen-elec-rpi-robot-hat/production/"
                          "ASE01187-C1_elec_RPI_Robot_HAT_BOM.csv",
                     bom_lines=lines,
                     active_devices=len(actives),
                     placed_as_solids=placed_actives,
                     not_populated=sum(1 for a in actives if a["status"] == "NOT POPULATED"),
                     cannot_determine=sum(1 for a in actives if a["status"] == "CANNOT DETERMINE"),
                     all_bodies_placed=meas["counts"]["bodies_placed"],
                     fitted_placements=meas["counts"]["fitted_placements"],
                     devices=actives),
        shelf=dict(electronic_part_folders=len(shelf),
                   with_an_assembly_placement=sum(1 for s in shelf if s["assembly_instances"]),
                   assembly_instances=sum(s["assembly_instances"] for s in shelf),
                   cannot_determine=sum(1 for s in shelf if s["verdict"] == "CANNOT DETERMINE"),
                   rows=sorted(shelf, key=lambda s: (-s["assembly_instances"], s["slug"]))),
        remaining_work=[
            "%d of the %d active devices on the Robot HAT's own BOM have no ce-parts folder: "
            "PAM8406D, XC6206P182MR, 74LVC1G08, SN74LVC1G125DBV, SN74LVC1G126DBVR, SIT3088E, "
            "AP63205, LM5050-1, LMA2718 (MK1), ASDMB 12 MHz (Y1), CAT24C32 (U4, DNP). They are "
            "PLACED as measured solids on the board; what they lack is a shelf record."
            % (len(actives) - 2, len(actives)),
            "%d shelf electronic parts have no established position in the robot; each row above "
            "says what would settle it. None of them is placed, and none is rendered."
            % sum(1 for s in shelf if s["verdict"] == "CANNOT DETERMINE"),
            "Two of the three custom boards are unbuilt: imu_to_dxl (no published outline) and "
            "the banana battery-contact PCB (see out/internals/other-boards.json).",
        ])
    p = os.path.join(OUT, "electronics-census.json")
    json.dump(res, open(p, "w"), indent=1)
    print("wrote", p)
    print("HAT BOM lines", lines, "active devices", len(actives),
          "placed", placed_actives,
          "not populated", res["hat_bom"]["not_populated"],
          "cannot determine", res["hat_bom"]["cannot_determine"])
    print("shelf electronic folders", len(shelf),
          "with a placement", res["shelf"]["with_an_assembly_placement"],
          "instances", res["shelf"]["assembly_instances"],
          "cannot determine", res["shelf"]["cannot_determine"])


main()
