---
id: TASK-0012
title: CLI watch, ingest-once, reprocess, --dry-run
status: Pending
priority: P1
owner: @you
parent: EPIC-0002
created: 2025-08-31
due: 
timebox: 90m
labels: [cli]
environments: [local]
require_confirm: []
---

# Task 0012: CLI: watch, ingest-once, reprocess, --dry-run

## Summary

Typer CLI with subcommands; --dry-run simulates without external calls or writes.

## Prerequisites

- [ ] None

## Objective (Outcomes)

- Typer CLI with subcommands; --dry-run simulates without external calls or writes.

## Scope

### In-Scope

- Typer-based CLI framework
- watch, ingest-once, reprocess subcommands
- --dry-run flag for simulation mode
- Command argument validation

### Out-of-Scope

- Interactive CLI prompts
- Shell completion scripts
- CLI configuration files

## Components to Install

- typer (for CLI framework)

## Commands

None specified.

## File Changes

None specified.

## Acceptance Criteria

- Given CLI args, Then the correct subcommand executes; dry-run logs intended actions only

## Verification

- Test: Execute each subcommand with and without --dry-run
- Check: Dry-run mode prevents external calls and writes
- Evidence to capture: CLI help output, dry-run logs

## Rollback

None specified.

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-0012-summary.md