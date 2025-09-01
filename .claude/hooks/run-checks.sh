#!/usr/bin/env bash
set -euo pipefail
cd "$CLAUDE_PROJECT_DIR"

# Replace these with your real checks
if command -v git >/dev/null 2>&1; then
  git status --porcelain > /dev/null || { >&2 echo "Git not available."; exit 1; }
fi

# Example: run format + quick lint if present
OK=1
if command -v npm >/dev/null 2>&1 && [[ -f package.json ]]; then
  npm run -s format || OK=0
  npm run -s lint || OK=0
fi
if command -v ruff >/dev/null 2>&1; then
  ruff . || OK=0
fi
if command -v pytest >/dev/null 2>&1 && [[ -d tests ]]; then
  pytest -q || OK=0
fi

if [[ $OK -ne 1 ]]; then
  >&2 echo "CHECKS FAILED: Fix formatting/lint/tests before continuing."
  exit 2
fi

echo "Checks passed."
exit 0