#!/bin/bash
# commit-lane.sh — commit ONLY the given paths, retrying on git's index.lock
# (several lane agents commit into this repo concurrently). Never `git add -A`.
# usage: tools/commit-lane.sh "<message>" <path>...
set -u
cd "$(dirname "$0")/.."
msg="$1"; shift
[ $# -gt 0 ] || { echo "commit-lane: no paths" >&2; exit 2; }
for i in 1 2 3 4 5 6 7 8 9 10; do
  if git add -- "$@" 2>/tmp/commit-lane.err && git commit -q -m "$msg" -- "$@" 2>>/tmp/commit-lane.err; then
    echo "committed $(git rev-parse --short HEAD): $msg"; exit 0
  fi
  if grep -q "nothing to commit\|no changes added" /tmp/commit-lane.err; then echo "commit-lane: nothing to commit for $*"; exit 0; fi
  sleep $((i*2))
done
echo "commit-lane: FAILED after retries" >&2; cat /tmp/commit-lane.err >&2; exit 1
