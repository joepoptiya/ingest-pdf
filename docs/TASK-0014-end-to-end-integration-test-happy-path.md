---
id: TASK-0014
title: End-to-end integration test (happy path)
status: Pending
priority: P1
owner: @you
parent: EPIC-0003
created: 2025-08-31
due: 
timebox: 90m
labels: [tests, e2e]
environments: [local]
require_confirm: []
---

# Task 0014: End-to-end integration test (happy path)

## Summary

Verify watch → ingest → redact → outputs → move to processed on a real sample PDF.

## Prerequisites

- [ ] None

## Objective (Outcomes)

- Verify watch → ingest → redact → outputs → move to processed on a real sample PDF.

## Scope

### In-Scope

- End-to-end workflow testing
- Real sample PDF processing
- Full pipeline verification
- Happy path scenarios

### Out-of-Scope

- Error path integration tests
- Performance testing
- Load testing with multiple files

## Components to Install

- Sample PDF files for testing

## Commands

None specified.

## File Changes

None specified.

## Acceptance Criteria

- Given a sample bank PDF dropped in inbox, Then outputs exist, redaction applied, input moved to processed

## Verification

- Test: Drop sample PDF and verify complete workflow
- Check: All outputs created correctly with redaction
- Evidence to capture: workflow logs, output files, file movements

## Rollback

None specified.

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-0014-summary.md