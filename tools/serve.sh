#!/bin/bash
# serve — the build book live over the real repo files.
#   tools/serve.sh [port]     default 8842; opens http://localhost:<port>/BUILD-BOOK.html
cd "$(dirname "$0")/.." || exit 1
PORT=${1:-8842}
( sleep 1; open "http://localhost:$PORT/BUILD-BOOK.html" ) &
exec python3 -m http.server "$PORT"
