# Microduck one-robot sourcing inquiry — 2026-09-08

MESSAGE.txt is the intended Chinese request. SOURCE-LIST.csv preserves all 32 current sourcing lines, including integrated reference-only components and unverified quantities. No fresh supplier stock/price claim is made, and no order is authorized. Quantities refer to one whole robot; head priorities are a subset, not extra units.

## Authorities and corrections

- `docs/BOM.md` §§1–4: base bought/printed/soft item list, quantities, original-identity gaps. Its old claim that all PCB files are unavailable is superseded below.
- `spec/sourcing.json` lines B1–P3: current vendor candidate identities and line quantities; sourcing PASS does not mean original identity, fit, safe power, or availability.
- `docs/RECREATION-2026-09-08.md`: public Robot HAT source correction, production revision uncertainty, electrical failures and conditional engineering review.
- `research/servo-power-audit-2026-09-08/AUDIT.md`: standard XL330 3.7–6.0V versus runtime 6.6–8.2V; no hardware power experiment performed for this inquiry.
- `research/bearing-sourcing-2026-09-08/conditional-rfq.csv`: 10×15×3mm open 6700 candidates versus generally 4mm shielded/sealed versions; original closure unknown. Bearing dimensions in message explicitly use OD/ID/width to avoid reversed conventions.
- `research/fastener-reconciliation-2026-09-08/AUDIT.md`: 64 modeled screws, missing M2×5 ×12 / M2×10 ×8 / M2.5×8 ×3; 325-piece old buy assortment not complete or a bound; included PHS TAP screws not ISO4762 equivalents. All are provisional quote questions.
- `research/servo-thread-verification-2026-09-08/AUDIT.md`: actual thread identity unknown for all 64 modeled fastener placements; nominal pose is not screw verification.
- `research/hat-pcba-rfq-2026-09-08/conditional-pcba-quote.csv`: public HAT conditional PCB/SMT component quantities; not manufacturing release.
- `research/ming-handoff-2026-09-08/update-b/MESSAGE.txt`: prior prepared review packet; no claim it was sent.

## Practical priority

Ask Ming for local stock and real purchase links first for the head's compute, camera/CSI, ToF, audio and board set. The whole robot additionally needs the 15-servo total, two bearing size groups, battery/charger, IMU/battery boards, checked screw schedule, control accessories and printing materials. Printed head job state is owned by the printer lane; no print-success claim is included here. Exact original SKU and quantity gaps remain explicit rather than replaced with a shopping basket.
