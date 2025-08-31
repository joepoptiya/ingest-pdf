---
id: TASK-0007
title: Output writers with atomic writes and templates
status: Pending
priority: P1
owner: @you
parent: EPIC-0001
created: 2025-08-31
due: 
timebox: 90m
labels: [io]
environments: [local]
require_confirm: []
---

# Task 0007: Output writers with atomic writes and templates

## Summary

Persist JSONL and Markdown to paths from config with {stem}/{hash}/{ts} templating; atomic rename from .tmp.

## Prerequisites

- [ ] None

## Objective (Outcomes)

- Persist JSONL and Markdown to paths from config with {stem}/{hash}/{ts} templating; atomic rename from .tmp.

## Scope

### In-Scope

- Atomic file writes using temp files + rename
- Template-based output path generation
- JSONL and Markdown output formats
- Directory creation as needed

### Out-of-Scope

- Other output formats beyond JSONL/Markdown
- Cloud storage output destinations
- Compression of output files

## Components to Install

- pathlib (built-in Python)
- tempfile (built-in Python)

## Commands

None specified.

## File Changes

None specified.

## Acceptance Criteria

- Given a valid input, Then {stem}-{hash}.jsonl and {stem}-{hash}.md are written atomically

## Verification

- Test: Verify atomic writes complete without corruption
- Check: Template variables correctly substituted in paths
- Evidence to capture: output file paths, atomic operation logs

## Rollback

None specified.

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-0007-summary.md