#!/usr/bin/env python3
"""gen_comparison.py — build COMPARISON.html: every render of ours beside the
real product photo at the same camera angle, plus the measured dimension table.
Data-driven from out/verify/mech_dims.json + out/compare/*.png. Regenerable.
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DIMS = json.load(open(os.path.join(REPO, "out", "verify", "mech_dims.json")))
HEAD_PATH = os.path.join(REPO, "out", "head", "head.json")
HEAD = json.load(open(HEAD_PATH)) if os.path.exists(HEAD_PATH) else None   # tools/head_verdict.py (lane A)


def _pm(v, u, nd=2):
    if v is None: return "CANNOT DETERMINE"
    return ("%+." + str(nd) + "f&nbsp;±&nbsp;%." + str(nd) + "f") % (v, u)


def head_verdict_block():
    """§1 head verdict + §5 finding-1 row + §5.1, all from out/head/head.json so this page and
    HEAD-RECONSTRUCTION.html cannot disagree."""
    if HEAD is None:
        return None
    C = HEAD["combined"]; V = HEAD["verdict"]; FV = HEAD["front_view"]["comparison"]
    cls = {"PASS": "", "FAIL": " warn", "CANNOT DETERMINE": " cd"}[V["head"]]
    v1 = f"""  <div class="verdict{cls}">
    <b>The head — {html.escape(V["head"])}, measured in millimetres.</b> Lane A scaled {C["n_photos"]} product photographs by the
    XL330-M288-T case in the same frame (20.000 mm), posed our model to each with a perspective camera and compared the head shell
    against the mesh: product/mesh size ratio <b>{_pm(C["product_over_mesh"], C["product_over_mesh_unc"], 4)}</b>, head-length deviation
    <b>{_pm(C["head_length_dev_mm"], C["head_length_dev_unc_mm"])}&nbsp;mm</b> on 122.690&nbsp;mm; along the head's own axes
    {_pm(C["dev_major_mm"], C["dev_major_unc_mm"])} / {_pm(C["dev_minor_mm"], C["dev_minor_unc_mm"])}&nbsp;mm. The eye bezel is
    <b>{html.escape(V["eye_bezel"])}</b>: it is the <code>noenoeil</code> mesh (Ø30.000&nbsp;×&nbsp;7.5&nbsp;mm ring proud of the face), the product ring
    reads {_pm(C["eye_dev_mm"], C["eye_dev_unc_mm"])}&nbsp;mm against it in the profiles and {C["eye_front_view_dev_mm"]:+.2f}&nbsp;mm in the true front view.
    Full evidence, every overlay real-beside-ours: <a href="HEAD-RECONSTRUCTION.html">HEAD-RECONSTRUCTION.html</a>.
  </div>"""
    row = f"""      <tr><td class="n">1</td><td><b>Head conformance — {html.escape(V["head"])}.</b> Product/mesh size ratio
        {_pm(C["product_over_mesh"], C["product_over_mesh_unc"], 4)} over {C["n_photos"]} servo-scaled photographs; head length
        {_pm(C["head_length_dev_mm"], C["head_length_dev_unc_mm"])}&nbsp;mm; eye bezel {html.escape(V["eye_bezel"])}
        ({_pm(C["eye_dev_mm"], C["eye_dev_unc_mm"])}&nbsp;mm profile, {C["eye_front_view_dev_mm"]:+.2f}&nbsp;mm front view).</td>
        <td><a href="HEAD-RECONSTRUCTION.html">HEAD-RECONSTRUCTION.html</a>, <code>out/head/head.json</code></td>
        <td>{"Head tooling can be cut from the published meshes." if V["head"] == "PASS" else ("The head must be re-modelled from the photographs before tooling." if V["head"] == "FAIL" else "Tooling waits on one calliper reading of a product head (or one purpose-shot photograph); the 1.5 mm rule cannot be decided from the store photographs alone.")}</td>
        <td>{html.escape("; ".join(V["what_would_settle"])) if V["what_would_settle"] else "None — closed."}</td></tr>"""
    sub = f"""{HEAD_SUB}
</section>

<section id="method">
  <h2><span class="n">6</span>Method and honest limits</h2>
  <ul>
    <li><b>Renders.</b> MuJoCo 3.12 offscreen at 1400², white studio, no floor, two directional
      fills plus a reduced headlight. Script <code>sim/compare_render.py</code>; the exact scene is
      written to <code>out/compare/_studio_scene.xml</code>.</li>
    <li><b>Measurements.</b> <code>sim/mech_dims.py</code> reads every STL through the FreeCAD
      mesh kernel and reports the axis-aligned bounding box. Reference assets are stored in
      metres and multiplied by 1000; our rebuilds are native millimetres.</li>
    <li><b>Bounding box is not a tolerance.</b> Table 1 proves overall envelope agreement. It does
      not prove feature-level agreement — that is the surface-distance check (p95 ≤ 1 mm both ways)
      recorded separately in the refcheck ledger. Neither is a manufacturing tolerance: no drawing
      dimension here carries a ± yet.</li>
    <li><b>Meshes are decimated.</b> Pollen published decimated STLs, so fine radii and small
      features are approximations of the true CAD, which was never released.</li>
    <li><b>No physical unit has been measured.</b> Every number here is derived from published
      digital assets and photographs. Nothing has been laser-scanned or callipered.</li>
  </ul>
</section>

</div>
</body>
</html>
"""
open(os.path.join(REPO, "COMPARISON.html"), "w").write(HTML)
print("wrote COMPARISON.html  parts=%d rebuilds=%d pass=%d worst=%.4f mm"
      % (DIMS["count"], n_reb, n_pass, worst))
