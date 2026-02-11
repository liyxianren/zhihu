#!/usr/bin/env bash
set -euo pipefail

CDP_PORT="${AGENT_BROWSER_CDP_PORT:-9222}"
PROFILE_DIR="${AGENT_BROWSER_ZHIHU_PROFILE_DIR:-/tmp/zhihu-chrome-profile}"
CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CDP_URL="http://127.0.0.1:${CDP_PORT}/json/version"
LIST_URL="http://127.0.0.1:${CDP_PORT}/json/list"
START_URL="${AGENT_BROWSER_ZHIHU_START_URL:-https://zhuanlan.zhihu.com/write}"

has_page() {
  curl -sf "$LIST_URL" | python3 -c '
import json
import sys
try:
    data = json.load(sys.stdin)
except Exception:
    raise SystemExit(1)
raise SystemExit(0 if any(item.get("type") == "page" for item in data) else 1)
'
}

wait_ready() {
  for _ in {1..20}; do
    if curl -sf "$CDP_URL" >/dev/null && has_page; then
      return 0
    fi
    sleep 0.5
  done
  return 1
}

if [[ ! -x "$CHROME_BIN" ]]; then
  echo "Google Chrome not found at: $CHROME_BIN" >&2
  exit 1
fi

if curl -sf "$CDP_URL" >/dev/null; then
  if has_page; then
    echo "Chrome CDP already ready on :$CDP_PORT (page attached)"
    exit 0
  fi
  # CDP may be alive but contain zero tabs; create one to avoid "No page found".
  open -a "Google Chrome" "$START_URL"
  if wait_ready; then
    echo "Chrome CDP ready on :$CDP_PORT (page created)"
    exit 0
  fi
  echo "CDP is reachable but failed to create an attached page on :$CDP_PORT" >&2
  exit 2
fi

# macOS-safe launch: open a new Chrome app instance with dedicated profile.
open -na "Google Chrome" --args \
  --remote-debugging-port="$CDP_PORT" \
  --user-data-dir="$PROFILE_DIR" \
  --no-first-run \
  "$START_URL"

if wait_ready; then
  echo "Chrome CDP is ready on :$CDP_PORT (page attached)"
  exit 0
fi

echo "Failed to start Chrome CDP on :$CDP_PORT" >&2
exit 2
