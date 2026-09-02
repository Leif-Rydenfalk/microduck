#!/usr/bin/env python3
"""shoot_test_plan.py — the read-back evidence for TEST-PLAN.html, and it does not trust itself.

    ce-cad/bin/cad tools/shoot_test_plan.py [--port 8842]

WHY THIS IS A TOOL AND NOT A SCRIPT SOMEBODY TYPED ONCE. On 2026-09-02 five of the twenty
committed screenshots of this document were the SAME PICTURE filed under five different
section names — out/testplan/tp-elec.png, tp-sens.png, tp-servo.png and tp-walk.png were
byte-identical to tp-top.png (sha256 5677d814…, 242,403 B), all five showing the top of the
page. Navigating to `…#WK-02` had not scrolled, the shutter fired anyway, and the house rule
"LOOK at every artifact you produce" was recorded as done when it had not been done. Two more
pairs (tp2-scope/tp2-top, tp3-top/tp4-top) were the same failure.

So the anchor is never trusted here. Three things stand between a scroll and a filed frame:

1. `ready_js` SCROLLS the target itself and returns FALSE until the element's own
   getBoundingClientRect() says it arrived. `screenshot_url` POLLS that expression, so a
   scroll that does not take never returns true and the shot times out instead of lying.
2. It then holds for REPAINT_MS after the final scroll before allowing the shutter. Without
   that, headless Chrome composites the frame mid-scroll and files a picture with a band of
   the previous viewport spliced into it — measured twice while writing this.
3. Every file is sha256'd and the run REFUSES to write the manifest if any two frames are
   identical, which is exactly the defect above, caught at the source.

The manifest (out/testplan/MANIFEST.json) records for every frame: the anchor, the offset,
what the frame is supposed to show, the sha256, the byte size and how long readiness took —
so a reader can check that the evidence is twenty different pictures and not one picture
twenty times.
"""
import sys, os, json, time, hashlib, argparse, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, "/Users/leifrydenfalk/dev/ce-workshop/ce-cad")
from cecad import vision                                       # noqa: E402

OUT        = os.path.join(REPO, "out", "testplan")
DOC        = "TEST-PLAN.html"
REPAINT_MS = 900          # measured: 400 ms still spliced two viewports into one frame

# name, anchor (None = the page top), offset of the anchor from the top of the viewport in px,
# what the frame must show. A negative offset scrolls PAST the anchor, which is how a long
# basis box below a test's heading is photographed.
FRAMES = [
    ("h-top",            None,      0,     "masthead, abstract and contents of the current revision"),
    ("h-elec",           "EB-01",   6,     "section 4 electrical bring-up, first test"),
    ("h-servo",          "SV-01",   6,     "section 5 servo identity and the read-back list"),
    ("h-registers",      "SV-04",   6,     "section 5 calibration, the register writes"),
    ("h-sens-tof",       "SN-06",   6,     "section 6 ToF ranging, the rewritten procedure"),
    ("h-sens-tof-basis", "SN-06",   -600,  "SN-06 gate and the datasheet basis, both columns named"),
    ("h-sens-imu",       "SN-03",   6,     "section 6 BMI088 self-test procedure"),
    ("h-sens-imu-basis", "SN-03",   -560,  "SN-03 gate and the corrected page-17 citation"),
    ("h-sw02",           "SW-02",   6,     "section 7 health verdict and the configure step"),
    ("h-rd04",           "RD-04",   6,     "section 8 duckctl over BLE, now citing the local mirror"),
    ("h-walk-note",      "walk",    6,     "section 9 head, acceptance surface, where the walk gate comes from"),
    ("h-walk",           "WK-02",   6,     "section 9 walk acceptance procedure"),
    ("h-walk-gate",      "WK-03",   1010,  "WK-02 gate and basis, incl. the commented-default paragraph"),
    ("h-limp",           "WK-05",   6,     "section 9 limp-fall thresholds"),
    ("h-open",           "open",    6,     "the open-questions section, head"),
    ("h-open-toml",      "open-16", 6,     "the open question about the commented robotd.toml defaults"),
    ("h-resolved-tof",   "resolved",-40,   "the corrected 'SN-06 needs no change' resolved block"),
]

READY = """(function(){
  var e = %s;
  if (!e) return false;
  var want = %d;
  var y = e.getBoundingClientRect().top;
  if (Math.abs(y - want) > 3) {
    window.scrollTo(0, window.scrollY + y - want);
    window.__ceLanded = 0;
    return false;
  }
  if (!window.__ceLanded) { window.__ceLanded = Date.now(); return false; }
  return (Date.now() - window.__ceLanded) > %d;
})()"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8842)
    a = ap.parse_args()
    base = "http://localhost:%d/%s" % (a.port, DOC)
    docp = os.path.join(REPO, DOC)
    if not os.path.exists(docp):
        raise SystemExit("shoot_test_plan: %s is not built; run tools/gen_test_plan.py first" % DOC)
    served = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                             "--max-time", "5", base], capture_output=True, text=True).stdout
    if served != "200":
        raise SystemExit("shoot_test_plan: %s answered %r — start tools/serve.sh %d first"
                         % (base, served, a.port))
    os.makedirs(OUT, exist_ok=True)

    rows, byhash = [], {}
    for name, anchor, off, what in FRAMES:
        path = os.path.join(OUT, name + ".png")
        url  = base + ("#" + anchor if anchor else "")
        el   = ("document.getElementById(%s)" % json.dumps(anchor)) if anchor \
               else "document.body"
        rj   = READY % (el, off, REPAINT_MS)
        vision.screenshot_url(url, path, width=1400, height=1000, wait_ms=30000,
                              settle_ms=400, ready_js=rj, ready_timeout_ms=25000)
        f = vision.last_shot()["facts"] or {}
        # A refused frame is DELETED, not left on disk. The 2026-09-02 defect was a picture on
        # disk under a name it did not show; a refusal that leaves the file behind recreates it.
        if anchor and not f.get("ready"):
            os.remove(path)
            raise SystemExit("shoot_test_plan: %s never proved it scrolled to #%s — the frame is "
                             "deleted rather than filed under a section it may not show" % (name, anchor))
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if h in byhash:
            os.remove(path)
            raise SystemExit("shoot_test_plan: %s is byte-identical to %s (sha256 %s) — that is "
                             "the 2026-09-02 defect this tool exists to prevent; the frame is "
                             "deleted and nothing is written" % (name, byhash[h], h[:16]))
        byhash[h] = name
        rows.append({"file": name + ".png", "anchor": anchor, "offset_px": off, "shows": what,
                     "sha256": h, "bytes": os.path.getsize(path),
                     "ready_ms": f.get("ready_ms"), "how": vision.last_shot()["how"],
                     "url": url})
        print("%-18s %-8s %s %8d B  ready %sms" % (name, anchor or "-", h[:16],
                                                   os.path.getsize(path), f.get("ready_ms")))

    man = {"note": "The frames below are the read-back evidence for the CURRENT revision of "
                   "TEST-PLAN.html. The tp*.png files beside them are earlier revisions' "
                   "shots, kept as history.",
           "deleted_2026_09_03": {
             "why": "Filed under a section name they did not show. Six files, three "
                    "byte-identical groups, all from a run whose anchor scroll silently failed.",
             "files": {
               "tp-elec.png / tp-sens.png / tp-servo.png / tp-walk.png":
                 "byte-identical to tp-top.png, sha256 5677d81496283c0aa35c6ea014145a4c13b75ecf"
                 "e3921916fc93836ec0b3109f, 242403 B each; all five showed the top of Rev A",
               "tp2-scope.png": "byte-identical to tp2-top.png, sha256 42140a9c2239f10f75ca58f4"
                                "db75003643a102af197035442cd135d3bda382f5",
               "tp4-top.png":   "byte-identical to tp3-top.png, sha256 530bc46bd5e8fe3841bb5e98"
                                "0e9c59fc9178669ccf1e3382401b1ac43c770d1b"}},
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
