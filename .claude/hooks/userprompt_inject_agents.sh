#!/usr/bin/env bash
set -euo pipefail

# Anything printed to STDOUT here becomes extra context for the next model turn.
cat <<'MENU'
[Agent Menu]
You MUST select exactly one of the following sub-agents and handoff before taking any action:
1) api-planner — API integrations, client/server endpoints, auth flows, SDK usage, oRPC/REST/GraphQL plans.
2) db-designer — schema design, data modeling, migrations, indexing/partitioning, ERDs.
3) doc-writer — README/ADR/PRD/CLAUDE.md/CHANGELOG and developer docs.

Rule of engagement (ROE):
- If the user’s request maps to API → handoff to api-planner.
- If it maps to data/schema → handoff to db-designer.
- If it’s documentation → handoff to doc-writer.
- Main actor MUST NOT call Edit/Write/Bash. Main should only analyze, choose an agent, and /handoff.

Output immediately:
{"agent_choice":"<api-planner|db-designer|doc-writer>","why":"<1-2 sentences>"}
Then perform /handoff to that agent.
MENU