#!/usr/bin/env python3
"""open_items.py — every open CANNOT DETERMINE in this repository, counted and
classified by what would actually close it. Re-runnable, so the count is a live
number and not a snapshot.

    python3 tools/open_items.py              -> out/open/cannot-determine.json + the table
    python3 tools/open_items.py --by class   -> group the table differently

Leif, 2026-09-04, verbatim: "way too miuch cannot determine still in microduck
tell it to put workflows on it."

By Leif's own standing rule every CANNOT DETERMINE is a WORK ITEM, never a
question for him and never a permanent state. But they are not one problem, and
treating them as one is why the count does not move. This sorts them by the
thing that would close each:

  measurable   the geometry is already in the model, or the simulation is
               runnable here. Undone work, not unknown work. Should fall fastest.
  research     a real part number, a published material property, a vendor
               figure. Closes with a cited source and a fetch date.
  in-sources   probably already answered in material sitting in reference/ that
               nobody has mined: the fanhao375 hardware teardown, the 15
               MakerWorld STLs, the Pollen develop tree, the 193 images.
  hardware     genuinely needs a physical sample — a durometer reading, a real
               stall torque, a measured mass. A LEGITIMATE resting place, but
               only with an exact procedure and acceptance limit attached, so
               the factory closes it the day a sample exists.
  badly-posed  a question nobody needs answered. Retire it explicitly with the
               reason. An open item nobody intends to close is noise that hides
               the real ones.

CLOSING AN ITEM BY WEAKENING WHAT WAS ASKED IS THE WORST OUTCOME AVAILABLE: it
looks like progress and destroys the record. This tool therefore records the
SUBJECT and the STATED REASON verbatim, so a later closure can be checked
against what was actually asked.
"""
import collections
import glob
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_JSON = os.path.join(ROOT, "out", "open", "cannot-determine.json")

SKIP_DIRS = {".git", "__pycache__", "trash", "node_modules", ".triad-index"}
# reference/ is source material we ingested; its own CANNOT DETERMINEs are the
# upstream author's, not ours, and counting them would inflate our number.
SKIP_PREFIX = ("reference/", "out/handover/", "images/")
# THE TOOL MUST NOT COUNT ITSELF. Measured 2026-09-04: the first run scanned its
# own output and reported 12025 occurrences from that one file, swamping the real
# population. A census that includes its own census is not a census — the same
# rule as "a check that can agree with what it checks is not a check".
SKIP_FILES = {"out/open/cannot-determine.json", "out/open/cannot-determine-harvest.json",
              "tools/open_items.py", "out/open/OPEN-ITEMS.html"}
TEXT_EXT = {".json", ".md", ".html", ".py", ".txt", ".csv", ".svg"}

CD = re.compile(r"CANNOT[\s_-]?DETERMINE", re.I)
TAG = re.compile(r"<[^>]+>")

# what settles it, when the item says so itself
SETTLES = re.compile(r"(what[_ ]settles[_ ]it|settled by|would settle|settles it)", re.I)

HARDWARE_WORDS = re.compile(
    r"\b(caliper|durometer|bench|physical sample|retail unit|teardown|multimeter|"
    r"meter on|oscilloscope|scale|weigh|coupon|specimen|pull-out test|torque wrench|"
    r"a real unit|production unit|hardware)\b", re.I)
RESEARCH_WORDS = re.compile(
    r"\b(datasheet|vendor|distributor|manufacturer|catalogue|catalog|published|"
    r"e-manual|drawing page|part number|MPN|SKU|price|lead time|MOQ|licence|license)\b", re.I)
SOURCE_WORDS = re.compile(
    r"\b(teardown|makerworld|upstream|develop branch|reference mesh|MJCF|"
    r"photograph|photo|image|fanhao|pollen)\b", re.I)
MEASURE_WORDS = re.compile(
    r"\b(mesh|solid|bbox|bounding box|geometry|simulate|simulation|MuJoCo|FEA|"
    r"mesh(?:features|compare|slice)|kernel|render|measure off|p95|interface)\b", re.I)


def classify(text):
    """Route an item to the thing that would close it. Order matters: hardware
    wins over research, because a question that needs a physical sample is not
    closed by a datasheet even if a datasheet is mentioned."""
    t = text[:1200]
    if HARDWARE_WORDS.search(t):
        return "hardware", "names a physical measurement or a real unit"
    if SOURCE_WORDS.search(t):
        return "in-sources", "names material we have already ingested into reference/"
    if RESEARCH_WORDS.search(t):
        return "research", "names a published figure, a vendor or a part number"
    if MEASURE_WORDS.search(t):
        return "measurable", "names geometry or a simulation we can run here"
    return "unclassified", "no closure route stated — triage by hand"


def snippet(s, i, before=160, after=420):
    a = max(0, i - before)
    b = min(len(s), i + after)
    out = s[a:b].replace("\\n", " ")
    out = TAG.sub(" ", out)
    return re.sub(r"\s+", " ", out).strip()


def walk():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, ROOT)
            if rel.startswith(SKIP_PREFIX) or rel in SKIP_FILES:
                continue
            if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
                continue
            if os.path.getsize(p) > 12_000_000:
                continue
            yield p, rel


items = []
files_scanned = 0
for path, rel in walk():
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            s = f.read()
    except Exception:
        continue
    files_scanned += 1
    if not CD.search(s):
        continue
    # one row per occurrence, but collapse identical snippets within a file
    seen = set()
    for m in CD.finditer(s):
        sn = snippet(s, m.start())
        key = sn[:180]
        if key in seen:
            continue
        seen.add(key)
        line = s.count("\n", 0, m.start()) + 1
        cls, why = classify(sn)
        items.append(dict(
            file=rel,
            line=line,
            subject=sn[:300],
            context=sn,
            closure_class=cls,
            classified_because=why,
            states_what_settles_it=bool(SETTLES.search(sn)),
        ))

# DEDUPE. A generated page, its source JSON and every intermediate carry the
# same item, so raw occurrences overcount badly (measured: 6070 occurrences
# collapse to far fewer distinct questions). The honest number is the count of
# DISTINCT SUBJECTS; the occurrence count is kept because it says where an item
# is republished and therefore how many documents a closure has to reach.
def norm(t):
    t = re.sub(r"[0-9]+(?:\.[0-9]+)?", "#", t.lower())
    t = re.sub(r"[^a-z#% ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()[:150]

groups = collections.OrderedDict()
for it in items:
    k = norm(it["subject"])
    g = groups.setdefault(k, dict(subject=it["subject"], closure_class=it["closure_class"],
                                  classified_because=it["classified_because"],
                                  states_what_settles_it=it["states_what_settles_it"],
                                  occurrences=0, files=[]))
    g["occurrences"] += 1
    if it["file"] not in g["files"]:
        g["files"].append(it["file"])
    g["states_what_settles_it"] = g["states_what_settles_it"] or it["states_what_settles_it"]
distinct = list(groups.values())
by_class = collections.Counter(i["closure_class"] for i in distinct)
by_file = collections.Counter(i["file"] for i in items)
no_route = [i for i in distinct if not i["states_what_settles_it"]]

doc = dict(
    doc=dict(id="MD-OPEN-001", rev="A",
             title="Open CANNOT DETERMINE items, classified by what would close them",
             generated_by="tools/open_items.py",
             rule=("Leif's standing rule: a CANNOT DETERMINE is a work item, never a "
                   "question for him and never permanent. Closing one by weakening what "
                   "was asked is the worst outcome available — it looks like progress "
                   "and destroys the record.")),
    scanned=dict(files=files_scanned, excluded_prefixes=list(SKIP_PREFIX),
                 excluded_reason=("reference/ holds ingested source material whose "
                                  "CANNOT DETERMINEs belong to their authors, not to us; "
                                  "counting them would inflate our number")),
    occurrences=len(items),
    total=len(distinct),
    note_on_counting=("total is DISTINCT subjects after normalising numbers and "
                      "punctuation; occurrences counts every place one is republished, "
                      "which is how many documents a single closure must reach"),
    by_class=dict(by_class),
    items_stating_what_settles_them=len(distinct) - len(no_route),
    items_with_no_closure_route=len(no_route),
    worst_files=by_file.most_common(15),
    items=distinct,
    occurrence_rows=items,
)
os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1, ensure_ascii=False)

print(f"files scanned                 : {files_scanned}")
print(f"raw occurrences               : {len(items)}")
print(f"DISTINCT open items           : {len(distinct)}")
print("by what would close them      :")
for k, v in by_class.most_common():
    print(f"    {k:14s} {v:5d}")
print(f"state what would settle them  : {len(distinct) - len(no_route)}")
print(f"NO closure route stated       : {len(no_route)}   <- these are the real defect")
print("\nworst files:")
for fn, n in by_file.most_common(10):
    print(f"    {n:5d}  {fn}")
print(f"\nwrote {OUT_JSON}")
