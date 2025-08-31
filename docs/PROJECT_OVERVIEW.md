---
project_id: PROJ-0001
name: PDF Ingestion Component (watch + ingest via TOML, UV, Python 3.11.13+)
owner: @you
stakeholders: [@you]
repo: .
environments: [local, docker, kubernetes]
created: 2025-08-30
target_release: 2025-09-06
risk_level: low
status: Active
labels: [area/ingestion, python311, uv, watchdog, llamaparse]
---

# Project Overview — PROJ-0001 PDF Ingestion Component

## Vision

A dependable Python 3.11.13+ component that watches a configured folder for new files (PDF in v1), hot-reloads its root config.toml, ingests each file through LlamaParse, redacts full account numbers to last-4, writes JSONL and Markdown outputs, and manages idempotency via SHA256 with a simple JSON ledger.

## Goals (Measurable)

- Detect and enqueue new files within ≤ 5 seconds after file finalization.
- Produce JSONL + Markdown outputs for ≥ 99% of valid PDFs.
- Zero duplicate reprocessing for identical files using SHA256 ledger.
- Redaction: 100% of detected account numbers masked to last-4 in outputs and logs.
- Concurrency: process up to 10 files concurrently without starvation or dropped events.

## Non-Goals

- No OCR fallback engines (LlamaParse only).
- No cloud/object storage or message queues in v1.
- No permanent daemon/service deployment in v1 (CLI-driven process).

## Success Metrics

- P95 time from file-ready to outputs ≤ 10s.
- Ingestion failure rate ≤ 1% on a representative sample.
- 0 duplicate output artifacts for identical content.
- 0 full account numbers in any persisted output or logs.

## Scope

### In-Scope

- Config at project root: config.toml with hot reload (path/patterns/types/outputs/concurrency/retry/logging/redaction).
- Single directory watch (patterns configurable); default to “pdf”.
- LlamaParse ingestion with backoff retries and quarantining failed inputs.
- Output JSONL and Markdown to directories from config.toml; per-file naming by template.
- SHA256 hashing and JSON ledger (load on start, update per processed file).
- Move processed inputs to processed/; if a duplicate by hash is re-seen, overwrite target outputs safely.
- Python logging with daily rotation in ./logs (INFO default; include ERROR).
- CLI with watch, ingest-once, reprocess, and --dry-run.
- Run status reporting (append-only JSONL under ./runs).

### Out-of-Scope

- Metrics HTTP endpoint (planned later).
- Recursive directory trees and multi-source orchestration (future).
- PII beyond account-number last-4 redaction.

## Architecture (High Level)

- Config Loader (hot-reload): reads root ./config.toml; publishes typed settings; reloads on file change.
- Watcher: watchdog observers on the configured directory; debounces until file is stable.
- Hasher + Ledger: SHA256 of input; ledger.json for idempotency; loaded at start, saved atomically on updates.
- Ingestor: HTTPX client to LlamaParse; retries with exponential backoff; returns normalized JSONL/Markdown blobs.
- Redactor: stream filters to mask account numbers to last-4 before persistence and logging.
- Output Writer: atomic writes (.tmp → rename) to JSONL and Markdown; templated filenames {stem}, {hash}, {ts}.
- Dispatcher: ThreadPoolExecutor with max_workers=10 (I/O bound); backpressure via bounded queue.
- Mover: on success move input to processed/; on failure move to quarantine/ with a reason file.
- Logger: logging + TimedRotatingFileHandler (daily) under ./logs.
- Run Reporter: per-run JSONL (./runs/run-YYYYmmdd-HHMMSS.jsonl) plus ./runs/latest.json with summary counts.
- CLI: Typer-based entrypoint with subcommands and --dry-run mode (no external calls, no writes).

## Config (root config.toml — indicative keys)

```toml
[input]
dir = "./inbox"
pattern = "*.pdf"         # configurable; v1 default pdf
file_type = "pdf"         # future-proof

[output]
jsonl_dir = "./outputs/jsonl/{stem}-{hash}.jsonl"
markdown_dir = "./outputs/markdown/{stem}-{hash}.md"

[processed]
dir = "./processed"
overwrite_on_dup = true   # based on identical SHA256 hash

[quarantine]
dir = "./quarantine"

[ledger]
path = "./state/ledger.json"  # JSON file: { "<sha256>": { "first_seen": "...", "files": [ ... ] } }

[concurrency]
max_workers = 10

[retry]
max_attempts = 3
initial_backoff_ms = 500
max_backoff_ms = 5000
jitter = true

[logging]
level = "INFO"
dir = "./logs"
rotation = "daily"

[redaction]
account_numbers = true   # last-4 only; redact elsewhere

[reporting]
runs_dir = "./runs"
```

---

## Task Seeds (YAML)

```yaml
tasks:
  - id_hint: 1
    title: Initialize UV project and repo scaffolding
    epic: EPIC-0002
    priority: P1
    owner: @you
    timebox: 60m
    environments: [local]
    labels: [uv, scaffolding]
    objective: >
      Create a Python 3.11.13+ project managed by UV with baseline folders and deps.
    in_scope:
      - Create src/, tests/, inbox/, outputs/{jsonl,markdown}/, processed/, quarantine/, state/, logs/, runs/
      - Initialize pyproject via UV; add runtime and dev deps
    commands:
      - type: shell
        cwd: .
        run:
          - uv init --package pdf_ingestor
          - uv venv
          - uv add watchdog httpx typer pydantic tomli-w tenacity python-dotenv
          - uv add --dev pytest pytest-cov
    acceptance:
      - Given the repo, When I run uv commands, Then venv exists and deps are added

  - id_hint: 2
    title: Implement config.toml loader with hot reload
    epic: EPIC-0002
    priority: P1
    owner: @you
    timebox: 90m
    environments: [local]
    labels: [config]
    objective: >
      Load ./config.toml into typed settings; watch file for changes and atomically apply updates.
    in_scope:
      - Define Settings model (pydantic)
      - Watch config.toml via watchdog and reload safely
    acceptance:
      - Given a changed key (e.g., concurrency.max_workers), Then new value applies without restart

  - id_hint: 3
    title: Watcher with stable-file debounce (single dir, pattern from config)
    epic: EPIC-0001
    priority: P1
    owner: @you
    timebox: 90m
    environments: [local]
    labels: [watcher]
    objective: >
      Detect new files matching pattern; enqueue only after size/timestamp stability.
    acceptance:
      - Given a copy-in of a large file, Then ingestion begins only after stabilization

  - id_hint: 4
    title: SHA256 hasher and JSON ledger (idempotency)
    epic: EPIC-0002
    priority: P1
    owner: @you
    timebox: 90m
    environments: [local]
    labels: [state]
    objective: >
      Compute SHA256; consult and update ./state/ledger.json to avoid duplicates.
    acceptance:
      - Given an identical file re-added, Then outputs are overwritten safely if configured, no duplicates

  - id_hint: 5
    title: LlamaParse client with retries and backoff
    epic: EPIC-0001
    priority: P1
    owner: @you
    timebox: 90m
    environments: [local]
    labels: [ingestion]
    objective: >
      Wrap HTTPX calls to LlamaParse with tenacity retries; 3 attempts, jitter, exponential backoff.
    acceptance:
      - Given transient failures, Then final success produces normalized JSONL and Markdown blobs

  - id_hint: 6
    title: Redaction stage: mask account numbers to last-4
    epic: EPIC-0003
    priority: P1
    owner: @you
    timebox: 90m
    environments: [local]
    labels: [redaction, privacy]
    objective: >
      Apply regex-based masking to outputs and any loggable snippets so that only last-4 remain.
    acceptance:
      - Given output text containing account numbers, Then no full numbers remain in persisted files or logs

  - id_hint: 7
    title: Output writers with atomic writes and templates
    epic: EPIC-0001
    priority: P1
    owner: @you
    timebox: 90m
    environments: [local]
    labels: [io]
    objective: >
      Persist JSONL and Markdown to paths from config with {stem}/{hash}/{ts} templating; atomic rename from .tmp.
    acceptance:
      - Given a valid input, Then {stem}-{hash}.jsonl and {stem}-{hash}.md are written atomically

  - id_hint: 8
    title: Dispatcher with max_workers=10 and bounded queue
    epic: EPIC-0001
    priority: P2
    owner: @you
    timebox: 60m
    environments: [local]
    labels: [concurrency]
    objective: >
      ThreadPoolExecutor (I/O bound) capped at 10; backpressure to avoid unbounded memory.
    acceptance:
      - Given N>10 enqueued files, Then only 10 run concurrently and queue drains

  - id_hint: 9
    title: Move processed to ./processed/ and quarantine failures
    epic: EPIC-0001
    priority: P1
    owner: @you
    timebox: 60m
    environments: [local]
    labels: [io, reliability]
    objective: >
      On success move to processed/; on failure move to quarantine/ with a reason file.
    acceptance:
      - Given a failure, Then input ends in quarantine/ and reason.txt contains the error summary

  - id_hint: 10
    title: Logging with daily rotation in ./logs (INFO + ERROR)
    epic: EPIC-0003
    priority: P1
    owner: @you
    timebox: 60m
    environments: [local]
    labels: [logging]
    objective: >
      Configure logging.handlers.TimedRotatingFileHandler (daily), INFO default; include ERROR stack traces.
    acceptance:
      - Given a run, Then daily log files appear in ./logs with clear INFO/ERROR lines

  - id_hint: 11
    title: Run Reporter (append-only JSONL and latest summary)
    epic: EPIC-0003
    priority: P2
    owner: @you
    timebox: 60m
    environments: [local]
    labels: [reporting]
    objective: >
      Write per-run JSONL under ./runs and a ./runs/latest.json with counts (processed, failed, skipped).
    acceptance:
      - Given a run, Then run-*.jsonl appended and latest.json accurately summarizes

  - id_hint: 12
    title: CLI: watch, ingest-once, reprocess, --dry-run
    epic: EPIC-0002
    priority: P1
    owner: @you
    timebox: 90m
    environments: [local]
    labels: [cli]
    objective: >
      Typer CLI with subcommands; --dry-run simulates without external calls or writes.
    acceptance:
      - Given CLI args, Then the correct subcommand executes; dry-run logs intended actions only

  - id_hint: 13
    title: TDD unit tests (config, watcher debounce, hashing, redaction)
    epic: EPIC-0003
    priority: P1
    owner: @you
    timebox: 120m
    environments: [local]
    labels: [tests, tdd]
    objective: >
      Unit tests with fixtures and sample PDFs; strict red/green development.
    acceptance:
      - Given pytest, Then all unit tests pass locally and in CI

  - id_hint: 14
    title: End-to-end integration test (happy path)
    epic: EPIC-0003
    priority: P1
    owner: @you
    timebox: 90m
    environments: [local]
    labels: [tests, e2e]
    objective: >
      Verify watch → ingest → redact → outputs → move to processed on a real sample PDF.
    acceptance:
      - Given a sample bank PDF dropped in inbox, Then outputs exist, redaction applied, input moved to processed
```
