#!/bin/bash
# serve — the repository browser live over the real repo files.
#   tools/serve.sh [port]     default 8842; opens http://localhost:<port>/
# Runs tools/docs_server.py (the halo-style sidebar browser in doc.css ink,
# 2026-09-03). The old `python3 -m http.server` is gone: the browser serves
# every file at its real path too, so nothing that linked into the bare index
# breaks — /BUILD-BOOK.html, /tools/doc.css and /out/... answer as before.
cd "$(dirname "$0")/.." || exit 1
PORT=${1:-8842}
( sleep 1; open "http://localhost:$PORT/" ) &
exec python3 tools/docs_server.py "$PORT"
