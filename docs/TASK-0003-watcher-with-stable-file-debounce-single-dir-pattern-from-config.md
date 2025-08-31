---
id: TASK-0003
title: Watcher with stable-file debounce (single dir, pattern from config)
status: Pending
priority: P1
owner: @you
parent: EPIC-0001
created: 2025-08-31
due: 
timebox: 90m
labels: [watcher]
environments: [local]
require_confirm: []
---

# Task 0003: Watcher with stable-file debounce (single dir, pattern from config)

## Summary

Detect new files matching pattern; enqueue only after size/timestamp stability.

## Prerequisites

- [ ] None

## Objective (Outcomes)

- Detect new files matching pattern; enqueue only after size/timestamp stability.

## Scope

### In-Scope

- Single directory watching with configurable patterns
- File stability detection via size/timestamp
- Debouncing mechanism for large file transfers

### Out-of-Scope

- Recursive directory monitoring
- Multiple directory sources
- Real-time processing without stability checks

## Components to Install

- watchdog (for file system monitoring)

## Commands

None specified.

## File Changes

None specified.

## Acceptance Criteria

- Given a copy-in of a large file, Then ingestion begins only after stabilization

## Verification

- Test: Copy large file and verify delayed processing
- Check: No premature processing during file transfer
- Evidence to capture: file detection timestamps, stability wait times

## Rollback

None specified.

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-0003-summary.md