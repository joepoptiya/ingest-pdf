---
id: TASK-0002
title: Implement config.toml loader with hot reload
status: Pending
priority: P1
owner: @you
parent: EPIC-0002
created: 2025-08-31
due: 
timebox: 90m
labels: [config]
environments: [local]
require_confirm: []
---

# Task 0002: Implement config.toml loader with hot reload

## Summary

Load ./config.toml into typed settings; watch file for changes and atomically apply updates.

## Prerequisites

- [ ] None

## Objective (Outcomes)

- Load ./config.toml into typed settings; watch file for changes and atomically apply updates.

## Scope

### In-Scope

- Define Settings model (pydantic)
- Watch config.toml via watchdog and reload safely

### Out-of-Scope

- Complex configuration validation beyond basic types
- Multi-file configuration support

## Components to Install

- pydantic (for settings model)
- watchdog (for file monitoring)

## Commands

None specified.

## File Changes

None specified.

## Acceptance Criteria

- Given a changed key (e.g., concurrency.max_workers), Then new value applies without restart

## Verification

- Test: Modify config.toml and verify reload
- Check: Settings object reflects changes without restart
- Evidence to capture: before/after config values, reload timestamps

## Rollback

None specified.

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-0002-summary.md