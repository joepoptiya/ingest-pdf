#!/usr/bin/env bash
# Blocks tool calls from Main and guides a handoff to a permitted sub-agent.
# Exits 2 to signal a blocking error; STDERR is shown to the assistant.

set -euo pipefail

# Read hook payload from STDIN if provided; fall back to env if needed.
payload="$(cat || true)"

# Try to detect actor/agent name from JSON payload (best-effort).
# We accept multiple possible shapes to be resilient.
actor=""
if command -v jq >/dev/null 2>&1; then
  a="$(printf '%s' "$payload" | jq -r '
    .actor.name // .actor // .agent // .currentAgent // empty
  ' 2>/dev/null || true)"
  actor="${a:-}"
fi

# Fallback: try environment variables some builds expose.
actor="${actor:-${CLAUDE_ACTOR_NAME:-}}"
actor="${actor:-${CLAUDE_AGENT_NAME:-}}"

# Normalize
actor="$(printf '%s' "$actor" | tr '[:upper:]' '[:lower:]')"

allowed_regex='^(api-planner|db-designer|doc-writer)$'

if [[ -z "$actor" || "$actor" == "main" || ! "$actor" =~ $allowed_regex ]]; then
  {
    echo "BLOCKED: Tool use is restricted to sub-agents (api-planner, db-designer, doc-writer)."
    echo "Detected actor: '${actor:-unknown}'."
    echo "Action required:"
    echo "1) Choose an agent and output: {\"agent_choice\":\"<api-planner|db-designer|doc-writer>\",\"why\":\"...\"}"
    echo "2) Use /handoff to that agent, then retry the tool call."
    echo "Policy: Main may not call Edit/Write/Bash. Handoff is mandatory."
  } 1>&2
  exit 2
fi

# If we reach here, the actor is an allowed sub-agent; permit the tool call.
echo "Agent '$actor' authorized for tool use."
exit 0