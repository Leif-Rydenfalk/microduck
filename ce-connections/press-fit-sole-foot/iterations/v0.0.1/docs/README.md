# connection:press-fit-sole-foot — the TPU sole on the printed foot cap

A **36.8000 × 49.8000 mm prismatic plug in a prismatic socket, at zero
clearance, with no fastener of any kind.** The soft sole is the part of this
robot that touches the ground, and it is held on by nothing but the grip of
the elastomer on the plug's walls.

## The fit, measured on both sides on the same lines

`cecad.meshfeatures.intervals` casts a ray through **both** meshes on one
line and reports where each enters and leaves. Run over 75 stations — 54
y-lines at z −19/−20/−21/−22/−23/−24 across x 34…66, and 21 x-lines at
z −19/−21/−23 across y −6…37 — that gives **150 gaps** between the socket's
inner wall and the plug's outer wall:

| | mm |
|---|---|
| minimum gap | **−0.0020** |
| maximum gap | **+0.0020** |
| mean gap | **−0.000007** |

**Zero clearance.** The two walls are the same surface to within the
0.002 mm the decimated STL can express. There is no allowance to grade and
`compat.py` does not pretend there is.

## The rest of the geometry

| | measured |
|---|---|
| section | x 31.6000…68.4000 × y −9.9000…39.9000 = **36.8000 × 49.8000 mm**, identical at every z section from −18.342 to −24.0 |
| rim plane | **z −18.3419** — the sole's own bbox maximum; `meshslice` finds 0 segments at −18.3419 and 659 at −18.3421 |
| socket wall | 1.594…2.479 mm, mean **2.0165**; a **2.1000** plateau on the long walls from x 38 to 62 |
| socket floor | **2.000 ± 0.001 mm** of TPU at nine independent stations — agreeing with the sole folder's own 27 × 31 grid, measured a different way |
| depth | **7.9170 mm at the toe → 10.6550 mm at the heel** (the outer floor slopes 0.087 and the inner floor follows it) |
| fasteners | **none.** No hole through the socket wall or floor. The ankle group's single M2 at (x 50.0000, y 4.5020) hangs the *foot* from the *ankle* and never enters the sole. |

## Why `mate()` has no `spin_deg`

A rectangular plug has exactly one seating rotation. Its 180° flip puts the
toe at the heel — that is a **different assembly**, not a free parameter —
so `mate()` takes `flip=True` and **refuses** `spin_deg` by name. And unlike
the bearing folders, this joint has a real self-locating datum (the plug
bottoms, the flange lands on the rim), so `seat_dz_mm` defaults to 0.0 at
that rim without inventing anything.

## Two things that stay CANNOT DETERMINE

- **Pull-off force.** Zero modelled clearance, TPU socket, printed rigid
  plug: the grip is whatever the two processes and the elastomer's modulus
  deliver, and no file here holds any of it. *What settles it:* pull a real
  sole off a real foot on a gauge and state `pull_off_N`.
- **A 0.2539 mm overlap.** The foot's ribs reach z −29.2509 while the sole's
  inner floor at that station is −28.9970. Deliberate squeeze, or an overlap
  in the visual meshes? The MJCF carries two rigid geoms and resolves no
  penetration, so nothing here separates the two readings. *What settles it:*
  measure a real pair, or establish whether the floor is compressed when the
  foot is home.

## Corner radii — not re-measured here, and why

The part folders already carry them (socket R3.4 back / R4.9 front; plug
R3.45 / R4.89), fitted at z −19 in their own lanes. Lane T's own corner
circle fits were **rejected rather than published**: the fit windows catch
the internal ribs as well as the wall and the residual mean came out
0.13–1.05 mm. A worse instrument does not get to overwrite a better one.
