# Public HAT Y1 — YXC OT3EL89CJI-111YLC-12M

One folder, one part. Everything here reads without our tooling: this page for humans, `electrical.<kind>.json` for any program, open formats for the rest. Records are the SOURCE — regenerate this page with `bin/parts build microduck-public-hat-y1`; edit the records, never this page.

Records carried: chip, part.

**Origin: vendor** — the manufacturer or a distributor page said so, and the page was fetched. Sector `chip`, lifecycle `unknown`.

## The silicon / device

- manufacturer: YXC Crystal Oscillators (扬兴科技)
- what it is: Public HAT Y1; exact LCSC product identity and supply band. Family timing is separately recorded in docs/SOURCE-FACTS.json.
- datasheet: https://www.lcsc.com/product-detail/C7425459.html
- revision read: Exact LCSC C7425459 listing fetched2026-09-08; linked YSO110TR family PDF archived, no printed revision or full MPN.
- supply VDD: min 1.8 / typ — (not documented) / max 3.3 V (cited in the record)
- recorded unknowns: 4 — read them before trusting silence

## Attachment (netlist part record)

- attaches: direct
- needs (3): GND [ground], VDD [supply], TRISTATE [signal]
- device record: OT3EL89CJI-111YLC-12M (its own folder if shared, this one if not)

## Files

- `PROVENANCE.json` — record / data
- `component.json` — record / data
- `datasheet.pdf` — source document
- `docs/SOURCE-FACTS.json` — record / data
- `docs/YXC-YSO110TR.pdf` — source document
- `docs/lcsc-datasheet.txt` — file
- `docs/lcsc-page-1.png` — image
- `docs/lcsc-page-2.png` — image
- `docs/verification.json` — record / data
- `docs/verify.py` — file
- `docs/yxc-page-1.png` — image
- `docs/yxc-page-2.png` — image
- `electrical.chip.json` — record / data
- `electrical.part.json` — record / data

Provenance: records moved from chips.json, parts.json (document identity preserved as `$from`). Facts inside each record carry their own quote+cite; a null is a documented silence, never zero.
