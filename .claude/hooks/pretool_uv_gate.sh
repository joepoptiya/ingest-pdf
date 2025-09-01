#!/usr/bin/env bash
set -euo pipefail
payload="$(cat || true)"

# Extract the pending command (best effort)
cmd=""
if command -v jq >/dev/null 2>&1; then
  cmd="$(printf '%s' "$payload" | jq -r '.command // .args // empty' 2>/dev/null || true)"
fi
[[ -z "$cmd" ]] && cmd="${CLAUDE_PENDING_COMMAND:-}"
[[ -z "$cmd" ]] && cmd="${payload}"
normalized="$(echo "$cmd" | tr '[:upper:]' '[:lower:]')"

block() { >&2 echo "$1"; exit 2; }

# Forbid legacy tools entirely
if echo "$normalized" | grep -Eq '(^|[[:space:]])pip3?([[:space:]]|$)';                   then block "BLOCKED: Use uv instead of pip. Try: uv add <pkg> or uv pip install -r requirements.txt"; fi
if echo "$normalized" | grep -Eq 'python[[:space:]]+-m[[:space:]]+pip\b';                 then block "BLOCKED: Use uv instead of python -m pip. Try: uv add <pkg>"; fi
if echo "$normalized" | grep -Eq 'python[[:space:]]+-m[[:space:]]+venv\b';                then block "BLOCKED: Use uv venv instead of python -m venv. Run: uv venv"; fi
if echo "$normalized" | grep -Eq '\b(poetry|pipx|pyenv)\b';                               then block "BLOCKED: Project standard is uv. Quickstart: uv init && uv venv"; fi

# Identify mutating uv commands (install/add/remove/sync/lock/venv/python install)
is_mutating=false
if echo "$normalized" | grep -Eq '\buv[[:space:]]+(add|remove|sync|lock|pip|python|venv)\b'; then is_mutating=true; fi

# Enforce project venv for any mutating actions
if [[ "$is_mutating" == "true" ]]; then
  if [[ -z "${VIRTUAL_ENV:-}" && ! -d ".venv" ]]; then
    block "BLOCKED: No project virtualenv detected. Create one first: uv init && uv venv (then re-run your command via uv run/uvx)."
  fi
fi

echo "uv gate: allowed"
exit 0