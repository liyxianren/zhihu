#!/usr/bin/env bash
set -euo pipefail

# Force all agent-browser commands to use Zhihu CDP endpoint.
# Usage:
#   bash ab_zhihu.sh open "https://zhuanlan.zhihu.com/write"
#   bash ab_zhihu.sh snapshot -i --json

CDP_PORT="${AGENT_BROWSER_CDP_PORT:-9222}"
SESSION="${AGENT_BROWSER_ZHIHU_SESSION:-zhihu-cdp}"
CDP_URL="http://127.0.0.1:${CDP_PORT}/json/version"
LIST_URL="http://127.0.0.1:${CDP_PORT}/json/list"
DEFAULT_URL="${AGENT_BROWSER_ZHIHU_START_URL:-https://zhuanlan.zhihu.com/write}"

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

ensure_page() {
  local url="$1"
  if has_page; then
    return 0
  fi
  # CDP can be alive with zero tabs; open one so agent-browser commands can attach.
  open -a "Google Chrome" "$url" >/dev/null 2>&1 || true
  for _ in {1..12}; do
    if has_page; then
      return 0
    fi
    sleep 0.4
  done
  return 1
}

if [[ $# -eq 0 ]]; then
  echo "Usage: bash ab_zhihu.sh <agent-browser-subcommand> [args...]" >&2
  exit 1
fi

if ! curl -sf "$CDP_URL" >/dev/null; then
  cat >&2 <<EOF
CDP endpoint is not reachable: $CDP_URL
Start Chrome with:
  bash ./start_zhihu_chrome.sh
EOF
  exit 2
fi

# Avoid "No page found" in CDP mode when all tabs were closed.
SUBCOMMAND="${1:-}"
TARGET_URL="$DEFAULT_URL"
if [[ "$SUBCOMMAND" == "open" && $# -ge 2 ]]; then
  TARGET_URL="$2"
fi
if ! ensure_page "$TARGET_URL"; then
  echo "CDP is reachable but no page is attached. Open a Chrome tab and retry." >&2
  exit 3
fi

# If caller already passed --cdp/--session, keep those args.
HAS_CDP=0
HAS_SESSION=0
for arg in "$@"; do
  if [[ "$arg" == "--cdp" ]]; then
    HAS_CDP=1
  fi
  if [[ "$arg" == "--session" ]]; then
    HAS_SESSION=1
  fi
done

if [[ "$HAS_CDP" -eq 1 && "$HAS_SESSION" -eq 1 ]]; then
  exec agent-browser "$@"
elif [[ "$HAS_CDP" -eq 1 ]]; then
  exec agent-browser "$@" --session "$SESSION"
elif [[ "$HAS_SESSION" -eq 1 ]]; then
  exec agent-browser "$@" --cdp "$CDP_PORT"
else
  exec agent-browser "$@" --cdp "$CDP_PORT" --session "$SESSION"
fi
