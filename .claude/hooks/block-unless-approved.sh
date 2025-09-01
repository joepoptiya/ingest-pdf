#!/usr/bin/env bash
set -euo pipefail

APPROVAL="$CLAUDE_PROJECT_DIR/.claude/approved.json"
MAX_AGE_SECS=900  # 15 minutes

fail() {
  # Exit code 2 = blocking error; stderr is fed back to Claude automatically.
  >&2 echo "BLOCKED: No recent approval token. Produce a plan first, wait for approval, then ask user to run '.claude/hooks/approve.sh'."
  >&2 echo "Required flow: plan → confirm → execute. No edits/writes allowed until approved."
  exit 2
}

if [[ ! -f "$APPROVAL" ]]; then fail; fi

now=$(date +%s)
approved=$(jq -r '.approved // false' "$APPROVAL" 2>/dev/null || echo "false")
ts=$(jq -r '.timestamp // 0' "$APPROVAL" 2>/dev/null || echo "0")
if [[ "$approved" != "true" ]]; then fail; fi
age=$(( now - ts ))
if (( age > MAX_AGE_SECS )); then fail; fi

# Optional: one-shot token – consume it to force per-operation approval
jq '.approved=false' "$APPROVAL" > "$APPROVAL.tmp" && mv "$APPROVAL.tmp" "$APPROVAL"

echo "Approval verified (token age ${age}s). Proceeding with tool call."
exit 0