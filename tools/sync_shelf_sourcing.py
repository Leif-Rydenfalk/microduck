#!/usr/bin/env python3
"""sync_shelf_sourcing.py - push lane E's offers into the triad shelf.

spec/sourcing.json holds the offers as a bill of materials sees them (per
LINE). ce-parts/<slug>/sourcing.json holds them as the shelf sees them (per
PART), in ce-parts/SCHEMA.md v2's shape. This copies the second from the first
so the two cannot drift, and so `bin/triad check part:<slug>` sees the prices.

MERGE ONLY, NEVER OVERWRITE. Another lane owns these folders. An offer already
in a part's sourcing.json is left exactly as it is - matched_on, note and all -
and only offers whose URL is not already present are appended. Nothing is
deleted, and a part with no line in spec/sourcing.json is not touched.

The schema's hard rules are enforced here rather than assumed:
  * confidence "verified" requires url AND retrieved AND matched_on;
  * a price with no retrieved date is a FAIL, so an offer without a fetch date
    is refused rather than written;
  * zero offers is CANNOT DETERMINE, never PASS;
  * nothing the vendor did not state becomes a default - it stays null.

Run:  python3 tools/sync_shelf_sourcing.py [--dry-run]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SHELF = os.path.join(REPO, "ce-parts")
DATA = json.load(open(os.path.join(REPO, "spec", "sourcing.json")))
DRY = "--dry-run" in sys.argv

# One line can source more than one part (B9 covers both ToF generations, B14
# both NFC candidates, R1 both USB-C controllers). The slug is named per offer
# where the line alone is ambiguous.
EXTRA = {
    "B9":  {"vl53l5cx": ("VL53L5CX", "VL53L5"), "vl53l8cx": ("VL53L8CX", "VL53L8")},
    "B14": {"pn7150": ("PN7150",), "st25r3916": ("ST25R3916",)},
    "R1":  {"fusb302": ("FUSB302",), "et7301b": ("ET7301",)},
}


def to_shelf_offer(line, off):
    """One spec/sourcing.json offer as a ce-parts v2 offer, or None."""
    if off.get("confidence") != "read":
        return None
    if not off.get("fetched"):        # a price with no date is a FAIL
        return None
    tiers = sorted(off.get("tiers") or [])
    matched = [f'vendor page identifies it as "{off.get("sku") or line["mpn"]}"']
    if tiers:
        matched.append(f'price {off["currency"]} {tiers[0][1]:g} at {tiers[0][0]}+ read on the page')
    if off.get("note"):
        matched.append(off["note"])
    return {
        "vendor": off["vendor"],
        "mpn": off.get("sku") or line["mpn"],
        "url": off["url"],
        "confidence": "verified",
        "retrieved": off["fetched"],
        "price": ({"currency": off["currency"], "unit": tiers[0][1],
                   "moq": off.get("moq"),
                   "break": [{"qty": q, "unit": p} for q, p in tiers[1:]] or None}
                  if tiers else None),
        "stock": off.get("stock"),
        "packaging": None,
        "matched_on": matched,
        "note": (f'from spec/sourcing.json line {line["id"]} ({line["item"]}). '
                 + (off.get("excluded_from_rollup") or "")).strip(),
    }


def verdict_for(line, offs):
    """The shelf verdict for one part. Never stronger than the line's own, and
    never PASS on fewer than two DISTINCT vendors - one shop priced two ways is
    one source of supply."""
    if len({o["vendor"] for o in offs}) < 2:
        return "CANNOT DETERMINE"
    return "PASS" if line["verdict"] == "PASS" else "CANNOT DETERMINE"


def offers_for(slug, line):
    keys = EXTRA.get(line["id"], {}).get(slug)
    out = []
    for off in line["offers"]:
        if keys:
            # SKU and URL only. The NOTE is prose and mentions the rival
            # candidate by name ("cheaper than the PN7150 at DigiKey"), which
            # matched the wrong part on the first run - measured, then fixed.
            hay = f'{off.get("sku","")} {off["url"]}'.upper()
            if not any(k.upper() in hay for k in keys):
                continue
        o = to_shelf_offer(line, off)
        if o:
            out.append(o)
    return out


def main():
    targets = {}          # slug -> (line, [offers])
    for line in DATA["lines"]:
        slugs = list(EXTRA.get(line["id"], {})) or (
            [line["ce_part"].split(":", 1)[1]] if line.get("ce_part") else [])
        for slug in slugs:
            offs = offers_for(slug, line)
            if offs:
                targets.setdefault(slug, (line, []))[1].extend(offs)

    wrote = kept = skipped = 0
    for slug, (line, offs) in sorted(targets.items()):
        folder = os.path.join(SHELF, slug)
        if not os.path.isdir(folder):
            print(f"  skip {slug}: no folder on the shelf")
            skipped += 1
            continue
        path = os.path.join(folder, "sourcing.json")
        if os.path.exists(path):
            doc = json.load(open(path))
            rec = doc["record"]
            have = {o.get("url") for o in rec.get("offers", [])}
            new = [o for o in offs if o["url"] not in have]
            if not new:
                print(f"  keep {slug}: {len(rec.get('offers', []))} offer(s), nothing new")
                kept += 1
                continue
            rec.setdefault("offers", []).extend(new)
            rec.setdefault("uncertainties", []).extend(
                u for u in line.get("unknowns", []) if u not in rec["uncertainties"])
            action = f"merged +{len(new)} -> {len(rec['offers'])}"
        else:
            doc = {"$parts_folder": 2, "kind": "sourcing",
                   "record": {"slug": slug,
                              "verdict": verdict_for(line, offs),
                              "offers": offs,
                              "uncertainties": list(line.get("unknowns", []))}}
            action = f"created with {len(offs)} offer(s)"
        # zero offers is CANNOT DETERMINE, never PASS - re-derive every time
        r = doc["record"]
        if len({o["vendor"] for o in r["offers"]}) < 2:
            r["verdict"] = "CANNOT DETERMINE"
        r["uncertainties"].append(
            f'Offers tagged "from spec/sourcing.json line {line["id"]}" were merged in by '
            f'tools/sync_shelf_sourcing.py on {DATA["fetch_dates"][0]}; SOURCING.html is the '
            f'full record including the pages that refused a price.')
        r["uncertainties"] = list(dict.fromkeys(r["uncertainties"]))
        print(f"  {slug}: {action}{' (dry run)' if DRY else ''}")
        if not DRY:
            json.dump(doc, open(path, "w"), indent=2, ensure_ascii=False)
            open(path, "a").write("\n")
        wrote += 1
    print(f"\n{wrote} part folder(s) written, {kept} left untouched, {skipped} absent from the shelf")


if __name__ == "__main__":
    main()
