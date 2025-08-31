# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Imports

@./.claude/rules/overview-to-tasks.md
@./.claude/rules/code-review.md
@./.claude/rules/review.md
@./.claude/templates/task_templates.md
@./.claude/templates/PROJECT_OVERVIEW_template.md
@./.claude/agents/agent-creator.md
@./.claude/agents/documentation-generator.md
@./.claude/agents/02-language-specialists/python-pro.md
@./.claude/agents/05-data-ai/data-engineer.md
@./.claude/agents/06-developer-experience/documentation-engineer.md

## Project Overview

A Python 3.11.13+ PDF ingestion component that watches a configured folder for new files, hot-reloads its root config.toml, ingests each file through LlamaParse, redacts full account numbers to last-4, writes JSONL and Markdown outputs, and manages idempotency via SHA256 with a simple JSON ledger. Built with modern Python features and comprehensive tooling.

## Essential Commands

### Development Setup

```bash
# Initialize UV project and dependencies
uv init --package pdf_ingestor
uv venv
uv add watchdog httpx typer pydantic tomli-w tenacity python-dotenv
uv add --dev pytest pytest-cov

# Complete development environment setup (recommended)
make dev-setup

# Install pre-commit hooks  
make pre-commit
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
make test-cov

# Run specific test types
uv run pytest -m "unit"           # Unit tests only
uv run pytest -m "integration"   # Integration tests only
uv run pytest -m "not slow"      # Exclude slow tests

# Run single test file
uv run pytest tests/test_processor.py -v
```

### Code Quality (Run After Every Change)

```bash
# Auto-fix and format (run in this order)
make lint-fix
make format
make type-check
make test

# Or run all checks at once
make check

# Run pre-commit on all files
make pre-commit-run
```

### CLI Usage

```bash
# Start watching directory for new PDFs
pdf-ingestor watch

# Process files once (no watching)
pdf-ingestor ingest-once

# Reprocess files from ledger
pdf-ingestor reprocess

# Dry run mode (no external calls or writes)
pdf-ingestor watch --dry-run
pdf-ingestor ingest-once --dry-run
```

## Architecture

### Core Components

- **Config Loader**: Reads root ./config.toml with hot-reload capability; publishes typed settings; reloads on file change
- **Watcher**: Watchdog observers on configured directory; debounces until file is stable
- **Hasher + Ledger**: SHA256 of input files; ledger.json for idempotency; loaded at start, saved atomically on updates
- **Ingestor**: HTTPX client to LlamaParse; retries with exponential backoff; returns normalized JSONL/Markdown blobs
- **Redactor**: Stream filters to mask account numbers to last-4 before persistence and logging
- **Output Writer**: Atomic writes (.tmp → rename) to JSONL and Markdown; templated filenames {stem}, {hash}, {ts}
- **Dispatcher**: ThreadPoolExecutor with max_workers=10 (I/O bound); backpressure via bounded queue
- **Mover**: On success move input to processed/; on failure move to quarantine/ with reason file
- **Logger**: logging + TimedRotatingFileHandler (daily) under ./logs
- **Run Reporter**: Per-run JSONL (./runs/run-YYYYmmdd-HHMMSS.jsonl) plus ./runs/latest.json with summary counts
- **CLI**: Typer-based entrypoint with subcommands and --dry-run mode

### Design Patterns

- **Observer Pattern**: Config file watching with hot reload
- **Strategy Pattern**: LlamaParse ingestion with retry strategies  
- **Command Pattern**: CLI commands with shared options and validation
- **Template Method**: File processing pipeline with consistent steps

### Key Configuration (config.toml)

```toml
[input]
dir = "./inbox"
pattern = "*.pdf"
file_type = "pdf"

[output]
jsonl_dir = "./outputs/jsonl/{stem}-{hash}.jsonl"
markdown_dir = "./outputs/markdown/{stem}-{hash}.md"

[processed]
dir = "./processed"
overwrite_on_dup = true

[concurrency]
max_workers = 10

[retry]
max_attempts = 3
initial_backoff_ms = 500
max_backoff_ms = 5000
jitter = true

[redaction]
account_numbers = true
```

## Code Standards

### PDF Processing Rule

**CRITICAL: This system uses LlamaParse ONLY for PDF parsing. Do NOT use PyPDF2, pdfplumber, or any other PDF parsing libraries. PyPDF2 and pdfplumber have been tested extensively and do not work for this use case. LlamaParse is the only solution that works reliably.**

### Type Checking

- **Strict MyPy** configuration enabled
- All public methods require type annotations
- Python 3.11+ type features used

### Code Style

- **Line length**: 88 characters (Black)
- **Import sorting**: Ruff handles import organization
- **Naming**: snake_case for functions/variables, PascalCase for classes

### Error Handling

- **Retry Logic**: Exponential backoff with jitter for LlamaParse API calls (3 attempts max)
- **Quarantine System**: Failed files moved to quarantine/ with reason files
- **Graceful Degradation**: System continues processing other files when individual files fail
- **Comprehensive Logging**: All errors logged with stack traces for debugging

## Testing Strategy

### Test Organization

- **Unit tests**: Test config loading, watcher debounce, hashing, redaction logic
- **Integration tests**: Test full watch → ingest → redact → outputs → move pipeline
- **TDD Approach**: Strict red/green development with fixtures and sample PDFs
- **Mock External APIs**: LlamaParse API calls mocked in unit tests

### Test Markers

```python
@pytest.mark.unit          # Fast isolated tests
@pytest.mark.integration   # End-to-end pipeline tests
@pytest.mark.slow         # Resource-intensive tests
```

### Key Test Areas

- **Config hot-reload**: Verify settings update without restart
- **File stability**: Ensure large files processed only after stabilization
- **Idempotency**: Verify SHA256 ledger prevents duplicate processing
- **Redaction**: Confirm account numbers masked to last-4 format
- **Atomic writes**: Test .tmp → rename operations
- **Error handling**: Verify quarantine system and retry logic

## Development Workflow

### Task Completion Checklist

After any code changes, run these commands:

1. `make lint-fix` - Auto-fix linting
2. `make format` - Format code
3. `make type-check` - Type check
4. `make test` - Run tests
5. `make pre-commit-run` - Final validation

Or simply run: `make check` to execute all quality checks at once.

### Common Development Tasks

- **Add config option**: Extend Settings model in config loader with pydantic field
- **Modify file processing**: Update pipeline stages in main processing loop
- **Add CLI command**: Add Typer command with --dry-run support
- **Change output format**: Update JSONL/Markdown templates and atomic write logic
- **Add redaction rule**: Extend regex patterns in redaction module
- **Modify retry logic**: Update tenacity configuration for LlamaParse calls

## Package Management

- **Package Manager**: uv (fast Python package manager)
- **Build System**: hatchling
- **Dependencies**: watchdog, httpx, typer, pydantic, tomli-w, tenacity, python-dotenv
- **CLI Entry Point**: `pdf-ingestor` command with watch/ingest-once/reprocess subcommands

## Key Files & Directories

### Configuration
- **config.toml**: Root configuration file with hot-reload capability
- **pyproject.toml**: Package and tool configuration (pytest, ruff, black, mypy)
- **Makefile**: Common development commands

### Runtime Directories
- **inbox/**: Input directory for PDFs (configurable)
- **outputs/**: JSONL and Markdown outputs with templated paths
- **processed/**: Successfully processed files moved here
- **quarantine/**: Failed files with reason files
- **state/**: ledger.json for SHA256 idempotency tracking
- **logs/**: Daily rotated log files
- **runs/**: Per-run JSONL files and latest.json summary

### Development
- **.pre-commit-config.yaml**: Git hooks for code quality
- **tests/**: Unit and integration tests with TDD approach
- **CLAUDE.md**: This guidance file
