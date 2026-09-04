#!/bin/bash
# iterate_blueprints.sh — ONE TURN of the blueprint iteration loop, measured.
#
# Leif, 2026-09-04: "lots of tegh blueprints still arent perfect and all of
# them needs the revisions ive talked about ... it must put workflows on
# iterating on these blueprints."
#
# A turn is: grade every sheet, keep the run, rebuild the baseline page, and
# SAY WHAT MOVED against the previous turn. It changes nothing itself — the
# generator is what you edit between turns (ce-cad/cecad/autosheet.py,
# cecad/sheets.py, tools/draw_part.py), never a single sheet by hand.
#
#   tools/iterate_blueprints.sh            grade, archive, baseline, delta
#   tools/iterate_blueprints.sh --draw     redraw every part FIRST, then grade
#
# Exit: 0 something improved and nothing regressed · 1 a REGRESSION, named
#       · 2 nothing moved (the turn bought nothing).
#
# The loop STOPS when the measured verdict stops improving, not when the
# sheets look finished.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WS="$(cd "$ROOT/../.." && pwd)"
export CE_TRIAD_ROOT="$ROOT:$WS"
cd "$ROOT"

HIST="$ROOT/out/drawings/history"
CUR="$ROOT/out/drawings/sheetcheck.json"
mkdir -p "$HIST"
STAMP="$(date +%Y-%m-%dT%H-%M-%SZ)"

if [ "${1:-}" = "--draw" ]; then
  echo "== redrawing every part (one kernel) — log out/drawings/history/draw-$STAMP.log"
  SLUGS="$(ls "$ROOT/out/drawings" | grep '^microduck-' | tr '\n' ' ')"
  "$WS/ce-cad/bin/cad" tools/draw_part.py $SLUGS \
      > "$HIST/draw-$STAMP.log" 2>&1
  tail -1 "$HIST/draw-$STAMP.log"
fi

# the PREVIOUS turn, kept before this one overwrites it
PREV=""
if [ -f "$CUR" ]; then
  PREV="$HIST/sheetcheck-$STAMP.json"
  cp "$CUR" "$PREV"
fi

echo "== grading every sheet against A2+A3+A4 (--refresh: the solids are re-probed)"
"$WS/ce-cad/bin/sheetcheck" --all out/drawings --refresh --json "$CUR" \
    > "$HIST/sheetcheck-$STAMP.log" 2>&1
SC=$?
sed -n '/^[0-9]* sheets/,$p' "$HIST/sheetcheck-$STAMP.log"
echo "   full table: out/drawings/history/sheetcheck-$STAMP.log (exit $SC)"

echo "== rebuilding out/drawings/BASELINE.md"
python3 tools/gen_sheet_baseline.py

echo "== rebuilding the index (both verdicts, the SHEET one first)"
python3 tools/collect_drawings.py && python3 tools/gen_drawings_index.py

if [ -n "$PREV" ]; then
  echo "== WHAT MOVED since the previous turn"
  python3 tools/sheet_delta.py "$PREV" "$CUR"
  exit $?
fi
echo "== no previous run to compare against; this turn is the baseline"
exit 0
