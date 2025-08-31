---
id: TASK-0001
title: Initialize UV project and repo scaffolding
status: Pending
priority: P1
owner: @you
parent: EPIC-0002
created: 2025-08-31
due: 
timebox: 60m
labels: [uv, scaffolding]
environments: [local]
require_confirm: []
---

# Task 0001: Initialize UV project and repo scaffolding

## Summary

Create a Python 3.11.13+ project managed by UV with baseline folders and deps.

## Prerequisites

- [ ] None

## Objective (Outcomes)

- Create a Python 3.11.13+ project managed by UV with baseline folders and deps.

## Scope

### In-Scope

- Create src/, tests/, inbox/, outputs/{jsonl,markdown}/, processed/, quarantine/, state/, logs/, runs/
- Initialize pyproject via UV; add runtime and dev deps

### Out-of-Scope

- Configuration setup
- Implementation of core functionality

## Components to Install

- watchdog
- httpx
- typer
- pydantic
- tomli-w
- tenacity
- python-dotenv
- pytest (dev)
- pytest-cov (dev)

## Commands

- type: shell
  cwd: .
  run:
  - uv init --package pdf_ingestor
  - uv venv
  - uv add watchdog httpx typer pydantic tomli-w tenacity python-dotenv
  - uv add --dev pytest pytest-cov

## File Changes

None specified.

## Acceptance Criteria

- Given the repo, When I run uv commands, Then venv exists and deps are added

## Verification

- Run: uv list (expect all dependencies listed)
- Check: Directory structure created with all folders
- Evidence to capture: uv list output, directory tree

## Rollback

- Delete created directories and pyproject.toml if needed

## Definition of Done

- [ ] All acceptance criteria verified
- [ ] Tests updated/passing
- [ ] Docs updated
- [ ] Observability updated (if applicable)
- [ ] task_summary.md created under summaries/tasks/TASK-0001-summary.md