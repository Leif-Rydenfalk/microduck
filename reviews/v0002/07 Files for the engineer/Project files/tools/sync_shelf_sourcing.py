#!/usr/bin/env python3
"""sync_shelf_sourcing.py - push lane E's offers into the triad shelf.

spec/sourcing.json holds the offers as a bill of materials sees them (per
LINE). ce-parts/<slug>/sourcing.json holds them as the shelf sees them (per
PART), in ce-parts/SCHEMA.md v2's shape. This copies the second from the first
so the two cannot drift, and so `bin/triad check part:<slug>` sees the prices.

MERGE, NEVER CLOBBER SOMEONE ELSE'S. Another lane owns these folders. An offer
this tool did not write is left exactly as it is - matched_on, note and all.
An offer this tool DID write (its note starts with "from spec/sourcing.json
line ") is REPLACED from the current data on every run, because the alternative
is what happened on 2026-09-03: three offers were cited to a listing page in
spec/sourcing.json, the citations were corrected there, and the stale listing
URLs stayed on the shelf marked "verified" because appending cannot fix a
record that is already present. A part with no line in spec/sourcing.json is
not touched at all.

The schema's hard rules are enforced here rather than assumed:
  * confidence "verified" requires url AND retrieved AND matched_on, AND that
    the url IS THE PRODUCT PAGE - ce-parts/SCHEMA.md's own words. A vendor's
    family price table gets "family"; a listing or search page is refused;
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
MARK = "from spec/sourcing.json line "

MULTI_SUFFIX = {
    "co.uk", "org.uk", "ac.uk", "co.nz", "com.au", "net.au", "co.in", "co.jp",
    "com.cn", "com.br", "com.mx", "co.za", "com.sg", "com.hk", "com.tw",
}


def reg_domain(url):
    """The shop a URL belongs to. Vendor NAME STRINGS are not shops: 'DigiKey'
    and 'DigiKey (cut tape)' are one distributor under two spellings, and
    counting names is what let a one-shop line look like two (measured
    2026-09-03; the same fix is in tools/gen_sourcing.py)."""
    host = (url or "").split("//", 1)[-1].split("/", 1)[0].split("?", 1)[0]
    host = host.split("@")[-1].split(":")[0].lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    parts = [p for p in host.split(".") if p]
    if len(parts) <= 2:
        return ".".join(parts)
    if ".".join(parts[-2:]) in MULTI_SUFFIX:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])

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
    kind = off.get("page_kind") or "product"
    if kind == "listing":             # a listing page is not a citation
        return None
    conf = "verified" if kind == "product" else "family"
    tiers = sorted(off.get("tiers") or [])
    matched = [f'vendor page identifies it as "{off.get("sku") or line["mpn"]}"']
    if conf == "family":
        matched.append("the URL is the vendor's FAMILY price table, not a per-size "
                       "product page: the size and its price are printed on it, but "
                       "ce-parts/SCHEMA.md reserves \"verified\" for the product page")
    if tiers:
        matched.append(f'price {off["currency"]} {tiers[0][1]:g} at {tiers[0][0]}+ read on the page')
    if off.get("note"):
        matched.append(off["note"])
    return {
        "vendor": off["vendor"],
        "mpn": off.get("sku") or line["mpn"],
        "url": off["url"],
        "confidence": conf,
        "retrieved": off["fetched"],
        "price": ({"currency": off["currency"], "unit": tiers[0][1],
                   "moq": off.get("moq"),
                   "break": [{"qty": q, "unit": p} for q, p in tiers[1:]] or None}
                  if tiers else None),
        "stock": off.get("stock"),
        "packaging": None,
        "matched_on": matched,
        "note": (f'{MARK}{line["id"]} ({line["item"]}). '
                 + (off.get("excluded_from_rollup") or "")).strip(),
    }


def shelf_verdict(line, offs, current):
    """The verdict a part folder may carry. Never PASS on fewer than two
    distinct SHOPS, and never stronger than the line's own verdict in
    spec/sourcing.json - B7 was PASS on the shelf for a day after the line
    itself moved to CANNOT DETERMINE, because nothing re-derived it."""
    if len({reg_domain(o["url"]) for o in offs}) < 2:
        return "CANNOT DETERMINE"
    if line["verdict"] != "PASS":
        return "CANNOT DETERMINE"
    return current if current in ("PASS", "CANNOT DETERMINE", "FAIL") else "PASS"


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


def bookkeeping(line):
    return (f'Offers tagged "{MARK}{line["id"]}" were merged in by '
            f'tools/sync_shelf_sourcing.py; the pages behind them were fetched '
            f'{" and ".join(DATA["fetch_dates"])}, and each offer carries its own date. '
            f'SOURCING.html is the full record including the pages that refused a price.')


def finish(rec, line, offs):
    """Everything this tool re-derives on every run: the verdict, and its own
    bookkeeping line (REWRITTEN, not appended to, or one stale copy accumulates
    per run). Called BEFORE the unchanged test, so a change to either is a
    change - the first version of this ran after an early `continue` and could
    never update an existing file."""
    rec["offers"] = offs
    rec["verdict"] = shelf_verdict(line, offs, rec.get("verdict"))
    rec.setdefault("uncertainties", [])
    rec["uncertainties"].extend(
        u for u in line.get("unknowns", []) if u not in rec["uncertainties"])
    rec["uncertainties"] = [u for u in rec["uncertainties"]
                            if not str(u).startswith(f'Offers tagged "{MARK}')]
    rec["uncertainties"].append(bookkeeping(line))
    rec["uncertainties"] = list(dict.fromkeys(rec["uncertainties"]))
    return rec


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
            foreign = [o for o in rec.get("offers", [])
                       if not str(o.get("note") or "").startswith(MARK)]
            mine_before = len(rec.get("offers", [])) - len(foreign)
            have = {o.get("url") for o in foreign}
            fresh = [o for o in offs if o["url"] not in have]
            after = foreign + fresh
            before = json.dumps(rec, sort_keys=True)
            finish(rec, line, after)
            if json.dumps(rec, sort_keys=True) == before:
                print(f"  keep {slug}: {len(rec['offers'])} offer(s), nothing changed")
                kept += 1
                continue
            action = (f"{len(foreign)} foreign offer(s) kept, {mine_before} of ours "
                      f"replaced by {len(fresh)} -> {len(after)}")
        else:
            doc = {"$parts_folder": 2, "kind": "sourcing",
                   "record": finish({"slug": slug, "verdict": "PASS",
                                     "uncertainties": []}, line, offs)}
            action = f"created with {len(offs)} offer(s)"
        print(f"  {slug}: {action}{' (dry run)' if DRY else ''}")
        if not DRY:
            json.dump(doc, open(path, "w"), indent=2, ensure_ascii=False)
            open(path, "a").write("\n")
        wrote += 1
    print(f"\n{wrote} part folder(s) written, {kept} left untouched, {skipped} absent from the shelf")


if __name__ == "__main__":
    main()
