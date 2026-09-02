#!/Applications/FreeCAD.app/Contents/Resources/bin/python
"""leg_plots.py — the sweep and the policy runs as figures, drawn from the same
arrays the numbers in out/motion/legs.json came from.

  out/motion/legs_sweep_tracking.png  — commanded vs achieved angle and joint
      velocity for all ten leg joints, with the MJCF limits drawn as rules.
  out/motion/legs_envelope.png        — how much of each joint's MJCF range each
      motion actually uses (full sweep / walk / sit-stand / squat).
  out/motion/legs_selfcollision.png   — the self-collision onsets on the range bars.

    /Applications/FreeCAD.app/Contents/Resources/bin/python sim/leg_plots.py
"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "out", "motion")
TRAJ = os.path.join(OUT, "traj")
J = json.load(open(os.path.join(OUT, "legs.json")))
R = J["mjcf_ranges"]
ORDER = list(R.keys())
D = math.degrees
INK, RULE, ACC, WARN = "#1a1a1a", "#9a2b1e", "#243b53", "#8a5a00"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": "#555", "axes.linewidth": .8,
                     "figure.facecolor": "white", "savefig.facecolor": "white"})


def tracking():
    fig, axs = plt.subplots(5, 4, figsize=(15.5, 12.5), sharex=True)
    for i, j in enumerate(ORDER):
        z = np.load(os.path.join(TRAJ, "dyn_%s.npz" % j))
        t, q, v, tgt = z["t"], np.degrees(z["q"]), np.degrees(z["v"]), np.degrees(z["tgt"])
        c = i % 5
        col = 0 if j.startswith("left") else 2
        a = axs[c][col]; b = axs[c][col + 1]
        a.axhline(R[j]["lo_deg"], color=RULE, lw=.9, ls="--")
        a.axhline(R[j]["hi_deg"], color=RULE, lw=.9, ls="--")
        a.plot(t, tgt, color="#aaa", lw=1.4, label="commanded")
        a.plot(t, q, color=ACC, lw=1.2, label="achieved")
        a.set_ylabel("%s\ndeg" % j, fontsize=7.5)
        a.set_ylim(min(R[j]["lo_deg"], q.min()) - 12, max(R[j]["hi_deg"], q.max()) + 12)
        if i == 0:
            a.legend(fontsize=6.5, frameon=False, loc="upper right")
        b.plot(t, v, color=WARN, lw=1.0)
        pk = np.abs(v).max()
        b.axhline(0, color="#ccc", lw=.6)
        b.annotate("peak %.1f deg/s" % pk, xy=(0.02, 0.86), xycoords="axes fraction", fontsize=7)
        b.set_ylabel("deg/s", fontsize=7.5)
    for k in range(4):
        axs[4][k].set_xlabel("s")
    fig.suptitle("Leg joints: commanded vs achieved (dashed = MJCF limit) and joint velocity — "
                 "policy paused, trunk pinned, one joint at a time   ·   left leg | right leg",
                 fontsize=10, y=.995)
    fig.tight_layout(rect=[0, 0, 1, .985])
    p = os.path.join(OUT, "legs_sweep_tracking.png")
    fig.savefig(p, dpi=110); plt.close(fig)
    return p


def envelope():
    fig, ax = plt.subplots(figsize=(11, 5.2))
    y = np.arange(len(ORDER))[::-1]
    src = [("full MJCF range", None, "#e6e2da"),
           ("swept (policy paused)", J["dynamic_step_policy_paused"]["joints"], ACC),
           ("sit-stand policy", J["sitstand_policy"]["joints"], "#1c6b3c"),
           ("walking policy vx 0.25", J.get("walking_policy", {}).get("joints"), WARN),
           ("squat (stand policy)", J["squat"]["joints"], "#7a4fa3")]
    for k, j in enumerate(ORDER):
        ax.barh(y[k], R[j]["hi_deg"] - R[j]["lo_deg"], left=R[j]["lo_deg"], height=.72,
                color="#e6e2da", zorder=1)
    h = .5
    for si, (lab, dat, col) in enumerate(src[1:]):
        if not dat:
            continue
        for k, j in enumerate(ORDER):
            r = dat[j]
            d0 = r.get("min_deg", r.get("reached_min_deg"))
            d1 = r.get("max_deg", r.get("reached_max_deg"))
            ax.barh(y[k] - .26 + si * .18, d1 - d0, left=d0, height=.15, color=col, zorder=3,
                    label=lab if k == 0 else None)
    ax.set_yticks(y); ax.set_yticklabels(ORDER, fontsize=8)
    ax.set_xlabel("joint angle (deg)")
    ax.axvline(0, color="#bbb", lw=.8)
    ax.legend(fontsize=7.5, frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(.5, -.19))
    ax.set_title("How much of each leg joint's MJCF range each motion actually uses\n"
                 "(grey bar = the MJCF limit pair; every number measured off the simulation)", fontsize=10)
    fig.tight_layout()
    p = os.path.join(OUT, "legs_envelope.png")
    fig.savefig(p, dpi=120); plt.close(fig)
    return p


def collisions():
    cases = []
    for k, v in J["self_collision"]["combinations"]["cases"].items():
        for pn, pp in (v["pairs"] or {}).items():
            cases.append((k, pn, pp, v.get("swept_deg", [-90, 90])))
    for k, v in J["self_collision"]["both_legs_mirrored"]["cases"].items():
        for pn, pp in (v["pairs"] or {}).items():
            cases.append((k, pn, pp, v.get("swept_deg", [-90, 90])))
    if not cases:
        return None
    fig, ax = plt.subplots(figsize=(14.5, .70 * len(cases) + 2.2))
    y = np.arange(len(cases))[::-1]
    for i, (k, pn, pp, sw) in enumerate(cases):
        lo, hi = pp["contact_interval_deg"]
        ax.barh(y[i], sw[1] - sw[0], left=sw[0], height=.5, color="#eeebe4", zorder=1)
        ax.barh(y[i], hi - lo, left=lo, height=.5, color="#e0b2ab", zorder=2)
        ax.plot([pp["onset_deg"]], [y[i]], marker="|", ms=16, color=RULE, mew=2.2, zorder=4)
        ax.annotate("onset %.1f°  ·  max pen %.2f mm  ·  %s" %
                    (pp["onset_deg"], pp["max_penetration_mm"], pn),
                    xy=(92, y[i]), va="center", fontsize=7)
    ax.set_yticks(y)
    ax.set_yticklabels([c[0][:66] for c in cases], fontsize=7)
    ax.set_xlim(-100, 430); ax.set_xticks([-90, -45, 0, 45, 90])
    ax.set_xlabel("swept angle / offset (deg)")
    ax.set_title("Every self-collision MuJoCo reports on our model, with the angle at which the pair "
                 "first touches\n(pink = the contact interval; the tick is the onset as the joint leaves "
                 "neutral; 0.05–0.10° sweep resolution)", fontsize=10)
    fig.tight_layout()
    p = os.path.join(OUT, "legs_selfcollision_plot.png")
    fig.savefig(p, dpi=120); plt.close(fig)
    return p


if __name__ == "__main__":
    out = [tracking(), envelope(), collisions()]
    figs = [dict(png=os.path.relpath(p, ROOT), bytes=os.path.getsize(p)) for p in out if p]
    j = json.load(open(os.path.join(OUT, "legs.json")))
    j["figures"] = figs
    json.dump(j, open(os.path.join(OUT, "legs.json"), "w"), indent=1)
    for f in figs:
        print("wrote", f["png"], f["bytes"], "bytes")
