---
id: TASK-0009
title: Move processed to ./processed/ and quarantine failures
status: Pending
priority: P1
owner: @you
parent: EPIC-0001
created: 2025-08-31
due: 
timebox: 60m
labels: [io, reliability]
environments: [local]
require_confirm: []
---

# Task 0009: Move processed to ./processed/ and quarantine failures

## Summary

On success move to processed/; on failure move to quarantine/ with a reason file.

## Prerequisites

- [ ] None

## Objective (Outcomes)

- On success move to processed/; on failure move to quarantine/ with a reason file.

## Scope

### In-Scope

- File movement on successful processing
- Quarantine directory for failed files
- Reason files explaining failures
- Directory creation as needed

### Out-of-Scope

- Automatic retry from quarantine
- File archival/compression
- Network-based quarantine storage

## Components to Install

- shutil (built-in Python)
- pathlib (built-in Python)

## Commands

None specified.

## File Changes

None specified.

## Acceptance Criteria

- Given a failure, Then input ends in quarantine/ and reason.txt contains the error summary

## Verification

- Test: Process successful and failed files
- Check: Files moved to correct directories with reason files
- Evidence to capture: file movements, reason file contents

## Rollback

None specified.

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-0009-summary.md