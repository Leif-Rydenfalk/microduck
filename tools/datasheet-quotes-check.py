#!/usr/bin/env python3
"""datasheet-quotes-check — is every `quote` in an electrical record really in
the document the record says it read?

Walks ce-parts/<slug>/electrical.<kind>.json in this design. For every string
found under a key named `quote`, `quotes` (list) or ending in `_quote`, the
checker finds the document the quote claims to come from — the enclosing
object's `source` key naming an entry of `record.sources`, else
`record.datasheet_local` — extracts that document's text (pdftotext -layout
for PDFs, tag-stripped + entity-unescaped for HTML), collapses whitespace on
both sides, and requires the quote to be a substring.

Three verdicts per part, exit code deliver-style:
  0 PASS              every quote found in its named document
  1 FAIL              at least one quote NOT in its document (a quote that is
                      not in the document is not a quote)
  2 CANNOT DETERMINE  a record names no local document, the file is missing,
                      or pdftotext is not installed — nothing could be read

Break it on purpose before trusting it: edit one quote and watch this exit 1.

    python3 tools/datasheet-quotes-check.py [--json] [slug ...]
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(HERE, "ce-parts")


def collapse(s):
    return re.sub(r"\s+", " ", s).strip()


def doc_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        if not shutil.which("pdftotext"):
            return None, "pdftotext not installed"
        r = subprocess.run(["pdftotext", "-layout", path, "-"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return None, "pdftotext failed: %s" % r.stderr.strip()[:200]
        return collapse(r.stdout), None
    if ext in (".html", ".htm"):
        t = open(path, errors="ignore").read()
        t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
        t = html.unescape(re.sub(r"<[^>]+>", " ", t))
        return collapse(t), None
    return collapse(open(path, errors="ignore").read()), None


def walk(obj, path=()):
    """Yield (path, quote, source_name) for every quote string."""
    if isinstance(obj, dict):
        src = obj.get("source")
        for k, v in obj.items():
            if k == "quote" and isinstance(v, str):
                yield path + (k,), v, src
            elif k == "quotes" and isinstance(v, list):
                for i, q in enumerate(v):
                    if isinstance(q, str):
                        yield path + (k, i), q, src
            elif k.endswith("_quote") and isinstance(v, str):
                yield path + (k,), v, src
            else:
                for r in walk(v, path + (k,)):
                    yield r
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            for r in walk(v, path + (i,)):
                yield r


def check_part(slug):
    base = os.path.join(PARTS, slug)
    recs = [f for f in os.listdir(base) if re.match(r"electrical\.\w+\.json$", f)]
    if not recs:
        return "CANNOT DETERMINE", ["no electrical.<kind>.json"], 0
    findings, verdict, n = [], "PASS", 0
    cache = {}
    for f in recs:
        rec = json.load(open(os.path.join(base, f))).get("record", {})
        sources = {s.get("name"): s for s in rec.get("sources", []) if isinstance(s, dict)}
        default = rec.get("datasheet_local")
        for path, quote, src in walk(rec):
            n += 1
            local = None
            if src and src in sources:
                local = sources[src].get("local")
            elif src is None and default:
                local = default
            elif src is None and len(sources) == 1:
                local = list(sources.values())[0].get("local")
            where = "%s:%s" % (f, "/".join(str(p) for p in path))
            if not local:
                verdict = worst(verdict, "CANNOT DETERMINE")
                findings.append("CANNOT DETERMINE %s: no document named (source=%r)" % (where, src))
                continue
            lp = os.path.join(base, local)
            if lp not in cache:
                if not os.path.exists(lp):
                    cache[lp] = (None, "missing file %s" % local)
                else:
                    cache[lp] = doc_text(lp)
            text, err = cache[lp]
            if text is None:
                verdict = worst(verdict, "CANNOT DETERMINE")
                findings.append("CANNOT DETERMINE %s: %s" % (where, err))
                continue
            if collapse(quote) not in text:
                verdict = "FAIL"
                findings.append("FAIL %s: not in %s: %r" % (where, local, quote[:90]))
    return verdict, findings, n


ORDER = {"PASS": 0, "CANNOT DETERMINE": 1, "FAIL": 2}


def worst(a, b):
    return a if ORDER[a] >= ORDER[b] else b


def main(argv):
    as_json = "--json" in argv
    slugs = [a for a in argv if not a.startswith("--")] or sorted(
        s for s in os.listdir(PARTS)
        if any(re.match(r"electrical\.\w+\.json$", f)
               for f in os.listdir(os.path.join(PARTS, s))
               if os.path.isdir(os.path.join(PARTS, s))))
    out, overall = {}, "PASS"
    for s in slugs:
        v, fnd, n = check_part(s)
        out[s] = {"verdict": v, "quotes": n, "findings": fnd}
        overall = worst(overall, v)
        if not as_json:
            print("%-17s part:%s  %d quote(s)" % (v, s, n))
            for x in fnd:
                print("                  " + x)
    if as_json:
        print(json.dumps({"overall": overall, "parts": out}, indent=1))
    else:
        print("---\noverall %s  (%d part(s))" % (overall, len(slugs)))
    return {"PASS": 0, "FAIL": 1, "CANNOT DETERMINE": 2}[overall]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
