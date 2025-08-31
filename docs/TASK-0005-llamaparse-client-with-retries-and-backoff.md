---
id: TASK-0005
title: LlamaParse client with retries and backoff
status: Pending
priority: P1
owner: @you
parent: EPIC-0001
created: 2025-08-31
due: 
timebox: 90m
labels: [ingestion]
environments: [local]
require_confirm: []
---

# Task 0005: LlamaParse client with retries and backoff

## Summary

Wrap HTTPX calls to LlamaParse with tenacity retries; 3 attempts, jitter, exponential backoff.

## Prerequisites

- [ ] None

## Objective (Outcomes)

- Wrap HTTPX calls to LlamaParse with tenacity retries; 3 attempts, jitter, exponential backoff.

## Scope

### In-Scope

- HTTPX client for LlamaParse API
- Tenacity retry mechanism with exponential backoff
- Jitter for retry timing
- Error handling and logging

### Out-of-Scope

- Alternative PDF parsing engines
- Custom retry logic outside tenacity
- API key rotation strategies

## Components to Install

- httpx (for HTTP client)
- tenacity (for retry logic)

## Commands

None specified.

## File Changes

None specified.

## Acceptance Criteria

- Given transient failures, Then final success produces normalized JSONL and Markdown blobs

## Verification

- Test: Simulate API failures and verify retries
- Check: Exponential backoff timing with jitter
- Evidence to capture: retry attempt logs, success after failures

## Rollback

None specified.

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-0005-summary.md