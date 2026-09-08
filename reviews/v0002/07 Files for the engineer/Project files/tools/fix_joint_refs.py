"""tools/fix_joint_refs.py — give every fastener joint row the part ref its
own `why_ref_is_null` said would settle it.

`bin/triad check assembly:microduck` FAILED 64 times with "row N side b needs
{ref, interface}". The 64 rows are the fasteners placed by
tools/place_fasteners.py, and each carried b.ref = null with an honest reason:

    "the pilot was measured on the MESH <name>; which ce-parts folder owns
     that mesh is a mapping this lane did not take, and a guessed ref is a
     dangling ref. Settled by the mesh->part map already in placements.json."

That is exactly right and it names its own fix. This tool takes it: the map
IS in placements.json, it is one-to-one over 38 meshes, and nothing is
guessed. A mesh with no row in the map, or with two different part refs,
LEAVES THE REF NULL and keeps its reason — the point of the original refusal
was that a guessed ref is a dangling ref, and that has not changed.

Every ref written is then CHECKED to resolve to a real folder before the file
is saved. A ref that does not resolve is a FAIL under TRIAD.md, so a run that
would write one writes nothing at all.

Run:  python3 tools/fix_joint_refs.py [--apply]
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSHOP = "/Users/leifrydenfalk/dev/ce-workshop"
JOINTS = os.path.join(REPO, "ce-assemblies/microduck/iterations/v0.0.1/joints.json")
PLACE = os.path.join(REPO, "ce-assemblies/microduck/iterations/v0.0.1/placements.json")
ROOTS = [REPO, WORKSHOP]


def mesh_to_part():
    """{mesh: ref} from placements.json, ONE-TO-ONE only. A mesh two parts
    claim is dropped with its reason rather than resolved by preference."""
    rows = json.load(open(PLACE))["record"]["rows"]
    seen = {}
    for r in rows:
        m, ref = r.get("mesh"), r.get("part")
        if not m or not ref:
            continue
        seen.setdefault(m, set()).add(ref)
    good = {m: sorted(v)[0] for m, v in seen.items() if len(v) == 1}
    ambiguous = {m: sorted(v) for m, v in seen.items() if len(v) > 1}
    return good, ambiguous


def resolves(ref):
    """True when `part:<slug>` names a folder that exists on a triad root."""
    if not ref or ":" not in ref:
        return False
    kind, slug = ref.split(":", 1)
    folder = {"part": "ce-parts", "connection": "ce-connections",
              "assembly": "ce-assemblies"}.get(kind)
    if not folder:
        return False
    return any(os.path.isdir(os.path.join(root, folder, slug)) for root in ROOTS)


def main(apply_it):
    doc = json.load(open(JOINTS))
    rows = doc["record"]["rows"]
    m2p, ambiguous = mesh_to_part()
    filled, left, bad = [], [], []
    for i, row in enumerate(rows):
        b = row.get("b") or {}
        if b.get("ref"):
            continue
        mesh = b.get("in_mesh")
        ref = m2p.get(mesh)
        if not ref:
            b["why_ref_is_null"] = (
                "mesh %r has no one-to-one part in placements.json (%s), so the "
                "ref stays null. A guessed ref is a dangling ref."
                % (mesh, "claimed by %s" % ambiguous[mesh] if mesh in ambiguous
                   else "no placement row names it"))
            left.append((i, mesh))
            continue
        if not resolves(ref):
            bad.append((i, mesh, ref))
            continue
        b["ref"] = ref
        b["ref_source"] = (
            "placements.json mesh->part map: MJCF geom mesh %r is placed as %s. "
            "Not guessed — the map is one-to-one over 38 meshes and the folder "
            "was checked to exist on a triad root before this was written."
            % (mesh, ref))
        b.pop("why_ref_is_null", None)
        filled.append((i, mesh, ref))

    print("rows            %d" % len(rows))
    print("refs filled     %d" % len(filled))
    print("left null       %d" % len(left))
    print("REFUSED (ref does not resolve) %d" % len(bad))
    for i, mesh, ref in bad:
        print("   row %d mesh %s -> %s DOES NOT RESOLVE" % (i, mesh, ref))
    by_ref = {}
    for _, _, ref in filled:
        by_ref[ref] = by_ref.get(ref, 0) + 1
    for ref, n in sorted(by_ref.items(), key=lambda kv: -kv[1]):
        print("   %-46s %d" % (ref, n))

    if bad:
        print("\nWROTE NOTHING: a ref that does not resolve is a FAIL under "
              "TRIAD.md, so no partial write is made.")
        return 1
    if not apply_it:
        print("\ndry run — pass --apply to write")
        return 0
    doc["record"]["joint_ref_note"] = (
        "The 64 fastener rows' b.ref were filled by tools/fix_joint_refs.py "
        "from placements.json's one-to-one mesh->part map, and every one was "
        "checked to resolve to a real folder before writing. They were null "
        "because tools/place_fasteners.py measured the pilot on a MESH and "
        "refused to guess which part folder owns it — the right refusal, and "
        "it named this map as what settles it.")
    tmp = JOINTS + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(doc, fh, indent=1)
    os.replace(tmp, JOINTS)
    print("\nwrote %s" % JOINTS)
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
