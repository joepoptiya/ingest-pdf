#!/usr/bin/env bash
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

# 0) Pre-flight
[ -f ".envrc" ] || fail ".envrc missing"
[ -x "tools/interceptors/bin/pip" ] || fail "interceptor pip missing or not executable"
[ -x "tools/interceptors/bin/python" ] || fail "interceptor python missing or not executable"

# 1) direnv applied and PATH order
FIRST_PATH="$(echo "$PATH" | tr ':' '\n' | head -1)"
[[ "$FIRST_PATH" == "$ROOT/tools/interceptors/bin" ]] || fail "interceptors not first in PATH (got: $FIRST_PATH)"
pass "interceptors are first in PATH"

# 2) which checks
PIP_PATH="$(command -v pip || true)"
PY_PATH="$(command -v python || true)"
[[ "$PIP_PATH" == "$ROOT/tools/interceptors/bin/pip" ]] || fail "pip not intercepted ($PIP_PATH)"
[[ "$PY_PATH" == "$ROOT/tools/interceptors/bin/python" ]] || fail "python not intercepted ($PY_PATH)"
pass "pip/python resolve to interceptors"

# 3) ensure venv is NOT active
[[ -z "${VIRTUAL_ENV:-}" ]] || fail "A virtualenv is active; run 'deactivate' and retry"
pass "no active venv (good)"

# 4) pip is blocked
set +e
pip install requests 1>/dev/null 2>&1
RC=$?
set -e
[[ $RC -ne 0 ]] || fail "pip install should be blocked"
pass "pip install blocked as expected"

# 5) python -m venv is blocked
set +e
python -m venv .tmp-venv 1>/dev/null 2>&1
RC=$?
set -e
[[ $RC -ne 0 ]] || fail "python -m venv should be blocked"
pass "python -m venv blocked as expected"
rm -rf .tmp-venv || true

# 6) uv run executes INSIDE .venv (no shell activation)
[ -d ".venv" ] || uv venv >/dev/null
EXE="$(uv run python -c 'import sys; print(sys.executable)')"
[[ "$EXE" == *"/.venv/"*"python"* ]] || fail "uv run not using project .venv (exe: $EXE)"
pass "uv run uses project .venv: $EXE"

# 7) tools via uvx (ruff as example)
uvx ruff --version >/dev/null 2>&1 || fail "uvx ruff failed"
pass "uvx tool execution ok (ruff)"

# 8) pytest via uv run (fast smoke)
uv run pytest -q >/dev/null 2>&1 || fail "pytest failed"
pass "pytest runs via uv run"

echo "ALL CHECKS PASSED ✅"