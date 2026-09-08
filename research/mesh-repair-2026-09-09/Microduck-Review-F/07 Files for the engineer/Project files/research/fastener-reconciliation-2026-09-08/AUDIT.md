# Fastener reconciliation — 2026-09-08

**The 325-piece buy list does not cover even the current modeled screw schedule.** It is not a verified upper bound with spares. No purchasing quantities or thread identities were changed in this audit.

`reconciliation.json` and `per-line.csv` compare each nominal purchase identity with `out/fasteners/placed.json` and the assembly BOM. Both model artifacts agree on 64 screws, without repeated exact position/orientation pairs. This narrow duplicate check does not exclude overlapping or incorrectly matched physical runs.

| Nominal identity | Buy quantity | Modeled quantity | Finding |
|---|---:|---:|---|
| M2 × 4 ISO 4762 | 60 | 4 | 56 above modeled subset; not proven excess |
| M2 × 5 ISO 4762 | 0 | 12 | Missing purchase line |
| M2 × 6 ISO 4762 | 80 | 21 | 59 above modeled subset; not proven excess |
| M2 × 8 ISO 4762 | 40 | 12 | 28 above modeled subset; not proven excess |
| M2 × 10 ISO 4762 | 0 | 8 | Missing purchase line |
| M2 × 12 ISO 4762 | 15 | 4 | 11 above modeled subset; not proven excess |
| M2.5 × 6 ISO 4762 | 20 | 0 | No matching placed screw in this subset |
| M2.5 × 8 ISO 4762 | 0 | 3 | Missing purchase line; different from M2.5 × 6 |
| M2 nuts | 50 | — | Screw-only placements cannot verify nut demand |
| M2 heat-set inserts | 60 | — | Screw-only placements cannot verify insert demand |

The three absent nominal sizes total **23 modeled screws**. They are quote questions, not instructions to buy them: modeled lengths and thread types remain unverified. Sources: `spec/sourcing.json` B18a/B18b/B18c `rfq_spec`, `out/fasteners/placed.json`, `ce-assemblies/microduck/current/bom.json`. Input hashes are in `PROVENANCE.json`.

## Bundled ROBOTIS hardware is a separate identity

The [official XL330-M288-T retail listing](https://en.robotis.com/shop_en/item.php?it_id=902-0163-000) lists six **PHS M2x6 TAP** screws and ten **PHS M2x8 TAP** screws per actuator. Fifteen matching retail packs would therefore contain **90 and 150**, respectively. The saved page and hash preserve that observation; an OEM quote must confirm its own contents.

These are not the ISO 4762 metric socket-head screws named by B18a/B18b. No equivalence or deduction is justified. A joint-level schedule must establish head form, thread form, usable length and engagement before counting a bundled screw toward a requirement. We found no provable duplicated purchase line: a possible overlap in function is not proof of identical hardware.

## Thread classification defect

All **52** modeled runs into `xl330` use `connection:threaded-m2` and `part:screw-m2-iso4762`. `tools/place_fasteners.py:34–38` explains that choice by excluding the molded case from the PLA self-tap connection. That exclusion does not prove a pre-existing metric female thread. The source run itself describes a Ø1.6 pilot as **“M2 tap drill / self-tap pilot”** (`out/fasteners/runs.json`); diameter alone cannot disambiguate those thread forms.

The remaining 12 placed screws use printed-part self-tap connections (nine M2, three M2.5), while their purchased/model part records still name ISO 4762 screws. This may represent intentional thread forming with metric screws, but it is not an automatically established TAP screw identity. Their mechanical assumptions and material tests need verification.

Do not replace the 52 metric rows with TAP rows based only on package counts. Obtain the actual per-joint original screw schedule or inspect representative servo horn/frame joints, including whether threads are molded, formed by the screw or metallic inserts. Preserve head seating and maximum insertion depth evidence. A mesh pilot does not establish any of those facts.

## Why four counts cannot be a procurement range

145 counts community hole features, potentially counting clearance and counterbore separately. 79 counts measured interface features. 64 counts modeled screws. 325 counts a purchase assortment including nuts/inserts. Different units and incomplete coverage prevent either a 64–325-piece procurement range or an “upper bound” guarantee.

The owning reconciliation generator now explains this limitation. Physical evidence, thread identity, nut/insert placement and complete joint coverage remain open. No CAD, printer or hardware operation was performed.
