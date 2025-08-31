---
id: TASK-0011
title: Run Reporter (append-only JSONL and latest summary)
status: Pending
priority: P2
owner: @you
parent: EPIC-0003
created: 2025-08-31
due: 
timebox: 60m
labels: [reporting]
environments: [local]
require_confirm: []
---

# Task 0011: Run Reporter (append-only JSONL and latest summary)

## Summary

Write per-run JSONL under ./ops/runs and a ./ops/runs/latest.json with counts (processed, failed, skipped).

## Prerequisites

- [ ] None

## Objective (Outcomes)

- Write per-run JSONL under ./ops/runs and a ./ops/runs/latest.json with counts (processed, failed, skipped).

## Scope

### In-Scope

- Per-run JSONL files with timestamped names
- Latest summary JSON with run statistics
- Append-only logging of run events
- Run metrics tracking

### Out-of-Scope

- Run history analysis tools
- Metrics visualization
- Real-time run monitoring dashboards

## Components to Install

- json (built-in Python)
- datetime (built-in Python)

## Commands

None specified.

## File Changes

None specified.

## Acceptance Criteria

- Given a run, Then run-*.jsonl appended and latest.json accurately summarizes

## Verification

- Test: Execute runs and verify JSONL creation
- Check: Latest.json contains accurate counts
- Evidence to capture: run file contents, summary accuracy

## Rollback

None specified.

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-0011-summary.md