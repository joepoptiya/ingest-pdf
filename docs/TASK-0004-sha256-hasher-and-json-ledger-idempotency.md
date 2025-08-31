---
id: TASK-0004
title: SHA256 hasher and JSON ledger (idempotency)
status: Pending
priority: P1
owner: @you
parent: EPIC-0002
created: 2025-08-31
due: 
timebox: 90m
labels: [state]
environments: [local]
require_confirm: []
---

# Task 0004: SHA256 hasher and JSON ledger (idempotency)

## Summary

Compute SHA256; consult and update ./ops/state/ledger.json to avoid duplicates.

## Prerequisites

- [ ] None

## Objective (Outcomes)

- Compute SHA256; consult and update ./ops/state/ledger.json to avoid duplicates.

## Scope

### In-Scope

- SHA256 file hashing implementation
- JSON ledger for tracking processed files
- Atomic ledger updates
- Duplicate detection and handling

### Out-of-Scope

- Other hashing algorithms
- Database-based ledger storage
- Distributed ledger synchronization

## Components to Install

- hashlib (built-in Python)
- json (built-in Python)

## Commands

None specified.

## File Changes

None specified.

## Acceptance Criteria

- Given an identical file re-added, Then outputs are overwritten safely if configured, no duplicates

## Verification

- Test: Process same file twice, verify duplicate handling
- Check: Ledger contains hash entries with timestamps
- Evidence to capture: ledger.json contents, duplicate processing logs

## Rollback

None specified.

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-0004-summary.md