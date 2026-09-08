"""mate.py — the JST EH 3-pin joint, as a transform.

Contract (TRIAD.md): `def mate(a_iface, b_iface, params=None) -> Mate` — the
transform, the DOF the joint leaves free, and the fastener BOM it adds.

THE TRANSFORM IS THREE VENDOR NUMBERS AND NOTHING ELSE (JST eEH.pdf, fetched
2026-09-04, sha256 9e35874b…, vendored in all three EH part folders):

    housing height        6.5000 mm   p.3, EHR-3
    mated assembly height 8.1000 mm   p.2 '(8.1)', p.1 'and 8.1 mm in height'
    seat                  1.6000 mm   the difference — and the SAME figure is
                                      printed on p.4's Type A side view as
                                      '(1.6)', so two places in JST's own
                                      drawing agree to 0.0000 mm.

so: put the housing's `mate` frame onto the header's `mate` frame with the two
z axes ANTI-PARALLEL (the insertion directions oppose — one goes in, the other
receives), the two x axes PARALLEL (circuit No.1 onto circuit No.1: the wafer is
polarised, there is no second orientation), and the housing's mating face
standing 1.6000 mm off the header's board plane along the header's +z.

`a` is the HOUSING side (role `eh_housing`), `b` the HEADER side (role
`eh_header`). Either order is accepted and the roles decide, because a caller
holding a cable and a servo should not have to know which the folder calls `a`.

THE BOM IS THREE FOLDERS, NOT ONE: 1 x part:jst-ehr-03 and 3 x
part:jst-seh-001t-p0.6 (eEH.pdf p.2 prints the contacts as "Sold Separately"),
plus 1 x part:jst-b3b-eh-a on the board side — EXCEPT when the header belongs to
a bought servo, where the header is already inside part:xl330-m288-t and adding
it again would double-count. That exception is by REF, not by adjective.

No FreeCAD import: the transform is a 4x4 and a caller applies it.
"""
import math

HOUSING_HEIGHT_MM = 6.5      # eEH.pdf p.3, EHR-3
MATED_HEIGHT_MM = 8.1        # eEH.pdf p.2 '(8.1)'
SEAT_MM = MATED_HEIGHT_MM - HOUSING_HEIGHT_MM      # 1.6000, and p.4 prints '(1.6)'
PITCH_MM = 2.5               # eEH.pdf p.1 title / p.3 / p.4
CONTACT_X_MM = (-2.5, 0.0, 2.5)
CURRENT_RATING_A = 3.0       # eEH.pdf p.1 'Current rating: 3 A AC/DC (AWG #22)'
INSERTION_FORCE_N = 15.0     # eEH.pdf p.1 'Insertion force: 15 N max.'
WITHDRAWAL_FORCE_N = 1.0     # eEH.pdf p.1 'Withdrawal force: 1 N min.'

# a header that lives inside a bought device: its part folder already carries it
HEADER_INSIDE = ("part:xl330-m288-t",)


class Mate(object):
    """The answer: a transform, what is still free, and what it costs in parts."""

    def __init__(self, transform, dof_left, adds_parts, why, verdict, findings=None,
                 provenance=None):
        self.transform = transform          # 4x4 row-major, housing frame -> world
        self.dof_left = dof_left
        self.adds_parts = adds_parts        # [{"ref": …, "qty": …, "why": …}]
        self.why = why
        self.verdict = verdict
        self.findings = findings or []
        self.provenance = provenance or {}

    def to_dict(self):
        return {"transform": self.transform, "dof_left": self.dof_left,
                "adds_parts": self.adds_parts, "why": self.why,
                "verdict": self.verdict, "findings": self.findings,
                "provenance": self.provenance}


def _frame(iface):
    f = (iface or {}).get("frame") or {}
    o = [float(v) for v in f.get("origin_mm", [0.0, 0.0, 0.0])]
    z = [float(v) for v in f.get("z_axis", [0, 0, 1])]
    x = [float(v) for v in f.get("x_axis", [1, 0, 0])]
    return o, _unit(z), _unit(x)


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    if n < 1e-12:
        raise ValueError("jst-eh-3pin: a frame axis is zero length: %r" % (v,))
    return [c / n for c in v]


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _ortho(z, x):
    d = sum(z[i] * x[i] for i in range(3))
    x = _unit([x[i] - d * z[i] for i in range(3)])
    return x, _cross(z, x)


def mate(a_iface, b_iface, params=None):
    params = params or {}
    a_role = (a_iface or {}).get("role")
    b_role = (b_iface or {}).get("role")
    roles = {a_role, b_role}
    if roles != {"eh_housing", "eh_header"}:
        raise ValueError(
            "connection:jst-eh-3pin joins one interface of role 'eh_housing' to one of role "
            "'eh_header'; got %r and %r. REFUSED by name rather than guessed."
            % (a_role, b_role))
    housing, header = (a_iface, b_iface) if a_role == "eh_housing" else (b_iface, a_iface)

    for side, nm in ((housing, "housing"), (header, "header")):
        c = side.get("circuits")
        if c is not None and int(c) != 3:
            raise ValueError("connection:jst-eh-3pin is 3-circuit; the %s declares %s. "
                             "A 2- or 4-way EH is a DIFFERENT connection folder." % (nm, c))
        p = side.get("pitch_mm")
        if p is not None and abs(float(p) - PITCH_MM) > 1e-6:
            raise ValueError("connection:jst-eh-3pin is %.4f mm pitch; the %s declares %.4f."
                             % (PITCH_MM, nm, float(p)))

    ho, hz, hx = _frame(header)
    hx, hy = _ortho(hz, hx)
    state = params.get("state", "mated")
    seat = float(params.get("seat_mm", SEAT_MM))
    if state == "unmated":
        seat = float(params.get("gap_mm", SEAT_MM + 6.0))

    # housing frame in the header's world: z anti-parallel, x parallel, origin
    # `seat` along the header's +z from its board plane.
    nz = [-hz[i] for i in range(3)]
    nx = hx[:]
    ny = _cross(nz, nx)
    origin = [ho[i] + hz[i] * seat for i in range(3)]
    T = [[nx[0], ny[0], nz[0], origin[0]],
         [nx[1], ny[1], nz[1], origin[1]],
         [nx[2], ny[2], nz[2], origin[2]],
         [0.0, 0.0, 0.0, 1.0]]

    header_owner = (header.get("owner_ref") or header.get("part") or "")
    adds = [{"ref": "part:jst-ehr-03", "qty": 1,
             "why": "the cable housing at this end (eEH.pdf p.3)"},
            {"ref": "part:jst-seh-001t-p0.6", "qty": 3,
             "why": "three crimp contacts per housing — eEH.pdf p.2 prints them "
                    "'Sold Separately', so a housing alone is not a made joint"}]
    if header_owner in HEADER_INSIDE:
        header_note = ("the header is INSIDE %s and is not added: the servo is bought whole "
                       "and part:jst-b3b-eh-a would double-count it" % header_owner)
    else:
        adds.append({"ref": "part:jst-b3b-eh-a", "qty": 1,
                     "why": "the board header this housing seats onto (eEH.pdf p.4, Type A)"})
        header_note = "the header is a separate line: part:jst-b3b-eh-a"

    if state == "unmated":
        dof = [{"axis": "tz", "of": "the header's +z", "why": "an unseated housing is free to "
                "travel along the insertion direction; every other axis is still held by the "
                "polarised wafer once the contacts are engaged"}]
        verdict = "PASS"
        why = ("UNMATED, held %.4f mm off the board plane; one free axis (insertion). "
               "The seated joint is the default." % seat)
    else:
        dof = []
        verdict = "PASS"
        why = ("MATED: housing mating face %.4f mm above the header's board plane "
               "(8.1000 mated height, eEH.pdf p.2, minus 6.5000 housing height, p.3 — and p.4's "
               "side view prints the same '(1.6)'), z anti-parallel, x parallel because the "
               "wafer is polarised. Contacts meet at x = -2.5000 / 0.0000 / +2.5000. %s."
               % (seat, header_note))

    findings = [{
        "id": "EH-CURRENT-1",
        "verdict": "CANNOT DETERMINE",
        "what": "this joint is rated 3.0000 A (eEH.pdf p.1) and the Microduck daisy-chains "
                "fifteen servos through one of them",
        "break_even_A_per_servo": round(CURRENT_RATING_A / 15.0, 4),
        "what_settles_it": "a clamp meter on the first X3P lead of a running Microduck, or a "
                           "published RUNNING current for the XL330-M288-T",
    }, {
        "id": "EH-WIRE-1",
        "verdict": "CANNOT DETERMINE",
        "what": "ROBOTIS names 21 AWG (0.4105 mm2) and the SEH-001T-P0.6 crimp in the same "
                "table; JST gives that crimp 0.05-0.33 mm2 — the wire is 24.39 % over",
        "what_settles_it": "a stripped X3P lead under a micrometer",
    }]

    return Mate(T, dof, adds, why, verdict, findings, provenance={
        "seat_mm": SEAT_MM,
        "seat_derivation": "8.1000 (eEH.pdf p.2) - 6.5000 (p.3) = 1.6000; p.4 prints '(1.6)'",
        "pitch_mm": PITCH_MM,
        "contacts_x_mm": list(CONTACT_X_MM),
        "current_rating_A": CURRENT_RATING_A,
        "insertion_force_N": INSERTION_FORCE_N,
        "withdrawal_force_N": WITHDRAWAL_FORCE_N,
        "source": "JST eEH.pdf p.1-p.4, fetched jst-mfg.com 2026-09-04, sha256 9e35874b…, "
                  "vendored at ce-parts/jst-ehr-03/current/docs/fetched/eEH.pdf",
    })
