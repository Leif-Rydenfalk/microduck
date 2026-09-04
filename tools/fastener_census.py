#!/usr/bin/env python3
"""fastener_census.py — every fastening feature in the model, from the measured
interface records. Runs under plain python3; no CAD kernel needed.

    python3 tools/fastener_census.py            -> out/fasteners/census.json + a table

Leif, 2026-09-04, verbatim: "we need more detail in the microdcuk for joints and
wires and every single part and system must be in the cad". This is step one of
that: you cannot place a fastener you have not counted.

WHAT IT READS, and it invents nothing:
    ce-parts/*/current/cad/interfaces.json    every interface each part MEASURED

Each part folder already records where its screw holes, tapped bosses, insert
seats and bearing seats are, with the frame, the diameter and the measurement
method quoted. This walks all of them, classifies each fastening feature, pulls
the diameter out of the measured prose, and says which fastener that implies.

A diameter it cannot read stays null and the row is CANNOT DETERMINE. A feature
whose mate is stated as unknown in its own record keeps that verdict — the
census never upgrades a part's own refusal.
"""
import collections
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out", "fasteners", "census.json")

# The shelf's own role vocabulary, read off the records rather than assumed.
# A screw passes THROUGH a clearance feature and threads INTO a tapped one.
CLEARANCE_ROLES = {
    "clearance_hole", "screw_clearance", "screw_pattern", "servo_screw",
    "case_screws", "axle_screw", "fastener_pattern", "screw_hole", "counterbore",
    "mount_holes", "mounting_holes",
}
TAPPED_ROLES = {
    "tapped_boss", "tapped_hole", "self_tapped_boss", "screw_boss", "set_screw",
    "insert_boss", "heatset_boss", "servo_rear_seat", "thread_int", "captive_nut",
}
# a locating pin is not a fastener: it carries no thread and clamps nothing.
PIN_ROLES = {"locating_pin", "dowel", "pin"}
FASTENING_ROLES = CLEARANCE_ROLES | TAPPED_ROLES | {"thread_ext"}
# roles that are a JOINT rather than a fastener — counted separately, because
# Leif asked for joints too and they need parts just as much
JOINT_ROLES = {
    "bearing_seat", "bearing_face", "housing_bore", "shaft", "boss", "pocket",
    "socket", "ball_socket", "ball_stud", "horn_face", "spline", "pivot",
    "joint_child_link", "servo_mount",
}

DIA = re.compile(r"[ØØ]\s*([0-9]+(?:\.[0-9]+)?)")
LEN_X = re.compile(r"[ØØ]\s*[0-9.]+\s*[x×]\s*([0-9]+(?:\.[0-9]+)?)")
DEPTH = re.compile(r"(?:deep|depth|length)\s*([0-9]+(?:\.[0-9]+)?)")


CLEAR_TBL = [("M2", 2.10, 2.60, "close 2.2 / medium 2.4"),
              ("M2.5", 2.60, 3.00, "close 2.7 / medium 2.9"),
              ("M3", 3.00, 3.60, "close 3.2 / medium 3.4")]
TAP_TBL = [("M2", 1.45, 1.75, "nominal 1.6"),
           ("M2.5", 1.95, 2.15, "nominal 2.05"),
           ("M3", 2.40, 2.60, "nominal 2.5")]


def pick(dias, tbl):
    """A record often quotes several diameters — a boss OD and its bore, or a
    counterbore and its through-hole. Take the one that lands in the table and
    say which; if several do, take the smallest (the thread is the small one)."""
    hits = []
    for d in dias or []:
        for size, lo, hi, note in tbl:
            if lo <= round(float(d), 3) <= hi:
                hits.append((float(d), size, note))
    if not hits:
        return None, None, None
    d, size, note = sorted(hits)[0]
    return d, size, note


def thread_for(dia, role, dias=None):
    """Which fastener a measured diameter implies. ISO metric close-clearance
    and tap-drill figures are cecad/fasteners.py's table; anything outside them
    returns None rather than a guess."""
    dias = dias or ([dia] if dia is not None else [])
    if not dias:
        return None, "no diameter stated in the measured record"
    if role in CLEARANCE_ROLES:
        d, size, note = pick(dias, CLEAR_TBL)
        if size:
            return size, f"Ø{d} of {dias} is {size} clearance ({note})"
        return None, f"none of {dias} matches an ISO clearance size"
    if role in TAPPED_ROLES:
        d, size, note = pick(dias, TAP_TBL)
        if size:
            return size, f"Ø{d} of {dias} is the {size} tap/self-tap pilot ({note})"
        return None, f"none of {dias} is a tap pilot size; these may all be boss ODs"
    return None, f"role {role!r} does not imply a threaded fastener"


rows = []
parts_seen = 0
for path in sorted(glob.glob(os.path.join(ROOT, "ce-parts", "*", "current", "cad", "interfaces.json"))):
    slug = path.split(os.sep)[-5]
    try:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as e:
        rows.append(dict(part=slug, name=None, verdict="CANNOT DETERMINE",
                         why=f"interfaces.json unreadable: {e}"))
        continue
    parts_seen += 1
    for itf in (doc.get("record", {}).get("interfaces") or []):
        role = (itf.get("role") or "").strip()
        what = itf.get("what") or ""
        accepts = itf.get("accepts") or []
        threaded = any("threaded" in a or "insert" in a or "self-tap" in a for a in accepts)
        is_fast = role in FASTENING_ROLES or threaded
        is_joint = role in JOINT_ROLES
        is_pin = role in PIN_ROLES
        if not (is_fast or is_joint or is_pin):
            continue
        dias = [float(x) for x in DIA.findall(what)]
        dia = dias[0] if dias else None
        mlen = LEN_X.search(what)
        dep = DEPTH.search(what)
        depth = float(mlen.group(1)) if mlen else (float(dep.group(1)) if dep else None)
        size, why = (None, "") if is_joint and not is_fast else thread_for(dia, role, dias)
        # does the record itself refuse to say what it mates?
        mate_unknown = "CANNOT DETERMINE" in what.upper()
        fr = itf.get("frame") or {}
        rows.append(dict(
            part=slug,
            name=itf.get("name"),
            kind="fastening" if is_fast else ("pin" if is_pin else "joint"),
            role=role or None,
            accepts=accepts,
            diameter_mm=dia,
            all_diameters_mm=dias or None,
            depth_or_length_mm=depth,
            origin_mm=fr.get("origin_mm"),
            axis=fr.get("z_axis"),
            implied_fastener=size,
            implied_why=why,
            mate_stated=not mate_unknown,
            verdict=("PASS" if (size or is_joint) and not mate_unknown else "CANNOT DETERMINE"),
            why=(why if size else
                 ("the record states its mate is CANNOT DETERMINE" if mate_unknown else why)),
            measured=itf.get("source"),
            what=what,
        ))

fast = [r for r in rows if r.get("kind") == "fastening"]
joints = [r for r in rows if r.get("kind") == "joint"]
pins = [r for r in rows if r.get("kind") == "pin"]
by_size = collections.Counter(r["implied_fastener"] for r in fast if r.get("implied_fastener"))
by_role = collections.Counter(r["role"] for r in fast)
no_size = [r for r in fast if not r.get("implied_fastener")]
no_mate = [r for r in fast if not r.get("mate_stated")]

doc = dict(
    doc=dict(id="MD-FAST-CEN-001", rev="A",
             title="Fastening-feature census, from the measured interface records",
             generated_by="tools/fastener_census.py",
             reads="ce-parts/*/current/cad/interfaces.json"),
    note=("Every row is a feature a part MEASURED off its own geometry and recorded. "
          "The census classifies and counts them; it measures nothing new and upgrades "
          "no part's own CANNOT DETERMINE. The implied fastener comes from the ISO "
          "clearance and tap-drill tables in cecad/fasteners.py, never from a guess."),
    parts_with_interfaces=parts_seen,
    fastening_features=len(fast),
    joint_features=len(joints),
    locating_pin_features=len(pins),
    implied_by_size=dict(by_size),
    by_role=dict(by_role),
    features_without_a_size=len(no_size),
    features_whose_mate_is_unstated=len(no_mate),
    open_question=("SPEC.md:75-76 reads the whole robot as a 145-hole M2 system "
                   "(77 clearance, 28 counterbore, 20 tap, 20 larger) from a community "
                   "hole analysis. This census reads only what our part folders have "
                   "recorded so far. The difference between the two counts is the "
                   "measurement still to do, and it is stated rather than reconciled away."),
    rows=rows,
)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1, ensure_ascii=False)

print(f"parts with interface records : {parts_seen}")
print(f"fastening features           : {len(fast)}")
print(f"joint features               : {len(joints)}")
print(f"locating pins (not fasteners): {len(pins)}")
print(f"implied fasteners by size    : {dict(by_size)}")
print(f"by role                      : {dict(by_role)}")
print(f"no size determined           : {len(no_size)}")
print(f"mate not stated by the record: {len(no_mate)}")
print(f"\nwrote {OUT}")
print("\nSPEC.md:75-76 community census: 145 holes (77 clearance, 28 c'bore, 20 tap, 20 larger)")
print(f"this census from our own records: {len(fast)} fastening features — the gap is "
      "the measurement still to do, not a discrepancy to average away.")
