---
id: TASK-0006
title: Redaction stage mask account numbers to last-4
status: Pending
priority: P1
owner: @you
parent: EPIC-0003
created: 2025-08-31
due: 
timebox: 90m
labels: [redaction, privacy]
environments: [local]
require_confirm: []
---

# Task 0006: Redaction stage: mask account numbers to last-4

## Summary

Apply regex-based masking to outputs and any loggable snippets so that only last-4 remain.

## Prerequisites

- [ ] None

## Objective (Outcomes)

- Apply regex-based masking to outputs and any loggable snippets so that only last-4 remain.

## Scope

### In-Scope

- Regex patterns for account number detection
- Masking to last-4 digits format
- Apply to all output content and logs
- Configurable redaction rules

### Out-of-Scope

- Other PII redaction beyond account numbers
- Advanced ML-based PII detection
- Reversible encryption instead of masking

## Components to Install

- re (built-in Python regex)

## Commands

None specified.

## File Changes

None specified.

## Acceptance Criteria

- Given output text containing account numbers, Then no full numbers remain in persisted files or logs

## Verification

- Test: Process content with account numbers
- Check: All outputs show only last-4 format (****1234)
- Evidence to capture: before/after redaction samples

## Rollback

None specified.

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-0006-summary.md