# part:microduck-trunk-shell-right — the right half of the Microduck's egg trunk

**What it is.** The right half of the Microduck's trunk shell — Pollen's
MJCF mesh `right_shell` (body `trunk_base`, pos (4, −0.5, −17.5) mm, quat
(0.7071, 0, 0, 0.7071)), 31.8 × 80.9 × 41.7 mm, a printed colourway part.
The mirror of `part:microduck-trunk-shell-left` in everything but the
midplane joint: this half ends AT the midplane (bbox x max = 0.0 — no lap
strip, which is why it is 31.8 wide against the left's 33.7) and carries
the tapped side of the cross screw: a Ø1.6 M2 pilot (x −0.3..−5.0 in its
own frame) with a Ø3.0→4.0 drafted bore in a Ø6.0→7.4 boss.

**How it is built.** `cad/part.py` is the same file as the left's with
`SIDE = "right"`: the shell is modelled in the LEFT mesh's frame from this
mesh's own measurements (`cad/measure.py` mirrors the mesh into that frame,
writes `cad/measured.json`) and mirrored about yz at the end, landing in
the right mesh's own frame so the MJCF geom pos/quat place it directly.
Measurement method, wall thicknesses, features: see the left half's
`docs/README.md` — every outline was RE-MEASURED off `right_shell.stl`,
not copied; the measured outlines agree with the left's to 0.01 mm.

**The other mesh name.** `trunk_shell_right.stl` in the same asset set is a
different, unplaced revision (see the left README's numbers); graded
against `right_shell.stl`, the mesh the MJCF places.

**Verdict.** See `component.json` and `evidence/refcheck/` — the
`cad-refcheck` report against `right_shell.stl` is the proof of shape.

**CANNOT DETERMINE, written down:**
- Same four items as the left half (foot's mating part, hidden fillet
  radii, the slot beside the cross-screw boss — 2.4 mm wide on this side,
  not modelled — and the colourway).
