#!/usr/bin/env bash
set -euo pipefail
APPROVAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
mkdir -p "$APPROVAL_DIR"
jq -n --arg ts "$(date +%s)" '{"approved":true,"timestamp":($ts|tonumber)}' > "$APPROVAL_DIR/approved.json"
echo "Approval token created (15 min TTL). Next Edit/Write will consume it."