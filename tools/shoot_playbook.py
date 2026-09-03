#!/usr/bin/env python3
"""shoot_playbook.py — the read-back evidence for MANUFACTURING-PLAYBOOK.html.

    ce-cad/bin/cad tools/shoot_playbook.py [--port 8842]

WHY IT EXISTS. The house rule is LOOK at every artifact you produce, and the
playbook's frames used to be taken by hand, one `screenshot_url` call at a time,
with nothing checking that the anchor scroll actually took. tools/shoot_test_plan.py
was written for TEST-PLAN.html after exactly that failure put five byte-identical
pictures on disk under five different section names; this script reuses its
discipline for this document rather than repeating the mistake in a second lane:

1. `READY` scrolls the target itself and returns false until the element's own
   getBoundingClientRect() says it landed, then holds REPAINT_MS so headless
   Chrome cannot composite a frame mid-scroll.
2. A frame that never proves it scrolled is DELETED, not filed.
3. Every frame is sha256'd and the run refuses to write the manifest if any two
   are identical.

The manifest (out/playbook/MANIFEST.json) records for each frame the anchor, the
offset, what it must show, its sha256 and size, so a reader can check that the
evidence is N different pictures and not one picture N times.
"""
import sys, os, json, time, hashlib, argparse, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
sys.path.insert(0, HERE)
from cecad import vision                                       # noqa: E402
from shoot_test_plan import READY, REPAINT_MS                   # noqa: E402

OUT = os.path.join(REPO, "out", "playbook")
DOC = "MANUFACTURING-PLAYBOOK.html"

# name, anchor (None = page top), offset of the anchor from the top of the
# viewport in px (negative scrolls PAST it), what the frame must show.
FRAMES = [
    ("pb-top",       None,    0,    "masthead, the rev C note and the stat bar"),
    ("pb-process",   "s2-2",  6,    "2.2 cost per robot and the slicer-flag block that names the "
                                    "possibly-bought lens holder"),
    ("pb-buffer",    "s2-3",  -1900, "2.3 the failure-buffer sensitivity table and its verdict"),
    ("pb-dfm",       "dfm",   6,    "3 DFM head: the per-part table with the cecad printability "
                                    "column and the bed reconciliation"),
    ("pb-dfmrow",    "s3-1",  6,    "3.1 the finding table, incl. the slice.json flag bullet"),
    ("pb-profiles",  "s4-3",  6,    "4.3 what the stale print files cost"),
    ("pb-line",      "line",  6,    "5 the assembly line and its jigs"),
    ("pb-qa",        "qa",    6,    "6 QA gates per station"),
    ("pb-pack",      "pack",  6,    "7 packaging, the three shipping configurations"),
    ("pb-battery",   "s7-2",  6,    "7.2 which pack, the candidate Wh table and the regime verdict"),
    ("pb-open",      "open",  6,    "8 open items incl. the two new CANNOT DETERMINEs"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8842)
    a = ap.parse_args()
    base = "http://localhost:%d/%s" % (a.port, DOC)
    docp = os.path.join(REPO, DOC)
    if not os.path.exists(docp):
        raise SystemExit("shoot_playbook: %s is not built; run tools/gen_playbook.py first" % DOC)
    served = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                             "--max-time", "5", base], capture_output=True, text=True).stdout
    if served != "200":
        raise SystemExit("shoot_playbook: %s answered %r — start tools/serve.sh %d first"
                         % (base, served, a.port))
    os.makedirs(OUT, exist_ok=True)

    rows, byhash = [], {}
    for name, anchor, off, what in FRAMES:
        path = os.path.join(OUT, name + ".png")
        url = base + ("#" + anchor if anchor else "")
        el = ("document.getElementById(%s)" % json.dumps(anchor)) if anchor else "document.body"
        vision.screenshot_url(url, path, width=1400, height=1000, wait_ms=30000,
                              settle_ms=400, ready_js=READY % (el, off, REPAINT_MS),
                              ready_timeout_ms=25000)
        f = vision.last_shot()["facts"] or {}
        if anchor and not f.get("ready"):
            os.remove(path)
            raise SystemExit("shoot_playbook: %s never proved it scrolled to #%s — deleted"
                             % (name, anchor))
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if h in byhash:
            os.remove(path)
            raise SystemExit("shoot_playbook: %s is byte-identical to %s (sha256 %s) — deleted"
                             % (name, byhash[h], h[:16]))
        byhash[h] = name
        rows.append({"file": name + ".png", "anchor": anchor, "offset_px": off, "shows": what,
                     "sha256": h, "bytes": os.path.getsize(path),
                     "ready_ms": f.get("ready_ms"), "how": vision.last_shot()["how"], "url": url})
        print("  %-14s %-8s %6d B  ready %sms" % (name, anchor or "(top)",
                                                  os.path.getsize(path), f.get("ready_ms")))

    man = {"note": "Read-back evidence for the CURRENT revision of MANUFACTURING-PLAYBOOK.html, "
                   "taken by tools/shoot_playbook.py with the anchor-proof and identical-frame "
                   "refusals tools/shoot_test_plan.py established.",
           "document": DOC,
           "document_sha256": hashlib.sha256(open(docp, "rb").read()).hexdigest(),
           "document_bytes": os.path.getsize(docp),
           "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "viewport": "1400x1000", "repaint_hold_ms": REPAINT_MS,
           "distinct_images": len(byhash), "frames": rows}
    with open(os.path.join(OUT, "MANIFEST.json"), "w") as fh:
        json.dump(man, fh, indent=1)
        fh.write("\n")
    print("\n%d frames, %d distinct images, manifest written" % (len(rows), len(byhash)))


if __name__ == "__main__":
    main()
