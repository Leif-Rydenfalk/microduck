#!/bin/bash
# watch-pass — open each part's overlay the moment its refcheck reports PASS.
# Leif, 2026-09-01: "show me the overlays as they pass". One window per slug,
# the LATEST passing round; runs until tools/watch-pass.stop exists or 4 h.
cd "$(dirname "$0")/.." || exit 1
seen=""
end=$(( $(date +%s) + 4*3600 ))
while [ $(date +%s) -lt $end ] && [ ! -f tools/watch-pass.stop ]; do
  for rep in $(ls out/refcheck/*/r*/report.md ce-parts/*/iterations/*/evidence/refcheck/*/report.md 2>/dev/null); do
    if grep -q '^\*\*PASS\*\*' "$rep"; then
      slug=$(echo "$rep" | sed -E 's#(out/refcheck/|ce-parts/)([^/]+)/.*#\2#')
      case " $seen " in *" $slug "*) continue;; esac
      seen="$seen $slug"
      dir=$(dirname "$rep")
      echo "$(date +%H:%M:%S) PASS $slug  $(grep 'p95 mm' "$rep" | head -1)" >> tools/watch-pass.log
      [ -f "$dir/overlay_iso.png" ] && open "$dir/overlay_iso.png" "$dir/overlay_front.png"
    fi
  done
  sleep 20
done
