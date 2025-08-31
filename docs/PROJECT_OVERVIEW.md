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
