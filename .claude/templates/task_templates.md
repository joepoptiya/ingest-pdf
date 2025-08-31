---
id: TASK-####                 # e.g., TASK-0123
title: <short action title>
status: Pending | In Progress | Blocked | Done
priority: P0 | P1 | P2 | P3
owner: @handle
parent: EPIC-#### | PRD-####
created: YYYY-MM-DD
due: YYYY-MM-DD
timebox: 90m
labels: [area/backend, cli]
environments: [local]         # local | dev | stage
require_confirm: [publish, deploy, delete, network-external]
---

# Task #: <title>

## Summary

One or two sentences describing the target end-state.

## Prerequisites

- [ ] TASK-#### — <name> (must be Done)
- [ ] <prereq n>

## Objective (Outcomes)

- <objective 1>
- <objective n>

## Scope

### In-Scope

- <item>

### Out-of-Scope

- <item>

## Components to Install

- <component 1>
- <component n>

## Commands

# Each entry is an atomic action Claude Code can run with confirmation

- type: shell
  cwd: ./app
  run:
  - pnpm install
  - pnpm build
  - pnpm test

- type: shell
  cwd: ./infra
  run:
  - terraform fmt -check
  - terraform validate

## File Changes

# Use unified patches so Claude can apply them exactly

- path: app/src/config.ts
  intent: Add FEATURE_X flag
  patch: |
    --- a/app/src/config.ts
    +++ b/app/src/config.ts
    @@
    -export const FEATURE_X = false;
    +export const FEATURE_X = true;

## Acceptance Criteria

- Given <precondition>, When <action>, Then <verifiable outcome>
- Given <...>, When <...>, Then <...>

## Verification

- Run: pnpm test (expect all green)
- Check: curl <http://localhost:3000/healthz> → 200 OK
- Evidence to capture: test summary, healthz output, commit SHA

## Rollback

- Revert patch to config.ts (record git SHA)
- Undo infra change: terraform apply -target=<resource> -var 'feature_x=false'

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-####-summary.md
