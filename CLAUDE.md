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
@./.claude/agents/05-data-ai/data-engineer.md

## Project Overview

A Python PDF ingestion application that extracts text and metadata from PDF files using PyPDF2 and pdfplumber. Built with modern Python 3.11+ features and comprehensive tooling.

## Essential Commands

### Development Setup

```bash
# Complete development environment setup
make dev-setup

# Install dependencies only
uv sync --dev
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test types
uv run pytest -m "unit"           # Unit tests only
uv run pytest -m "integration"   # Integration tests only
uv run pytest -m "not slow"      # Exclude slow tests
```

### Code Quality (Run After Every Change)

```bash
# Auto-fix and format (run in this order)
uv run ruff check --fix .
uv run black .
uv run mypy src/
uv run pytest

# Or use single command
make check
```

### CLI Usage

```bash
# Process single PDF
ingest-pdf process document.pdf

# Batch process directory
ingest-pdf batch ./pdfs/ --recursive

# Get PDF metadata
ingest-pdf info document.pdf

# Extract specific page
ingest-pdf page document.pdf 0
```

## Architecture

### Core Components

- **PDFExtractor** (`extractor.py`): Low-level PDF operations using PyPDF2/pdfplumber
- **PDFProcessor** (`processor.py`): High-level file processing and business logic
- **CLI Module** (`main.py`): Click-based command interface
- **Custom Exceptions** (`exceptions.py`): Domain-specific error handling

### Design Patterns

- **Strategy Pattern**: PDFExtractor switches between PyPDF2 and pdfplumber
- **Facade Pattern**: PDFProcessor provides simplified interface over PDFExtractor
- **Command Pattern**: CLI commands with shared options and validation

### Key Classes

```python
# Main processing facade
PDFProcessor(output_dir: Path, use_pdfplumber: bool = True)

# Low-level extraction
PDFExtractor(use_pdfplumber: bool = True)
```

## Code Standards

### Type Checking

- **Strict MyPy** configuration enabled
- All public methods require type annotations
- Python 3.11+ type features used

### Code Style

- **Line length**: 88 characters (Black)
- **Import sorting**: Ruff handles import organization
- **Naming**: snake_case for functions/variables, PascalCase for classes

### Error Handling

All exceptions inherit from `PDFProcessingError`:

- `PDFNotFoundError`: File not found
- `PDFReadError`: File reading issues  
- `PDFExtractionError`: Text extraction failures

## Testing Strategy

### Test Organization

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test CLI commands end-to-end
- **Fixtures**: Shared test data in `conftest.py`
- **Sample PDFs**: Generated with reportlab for consistent testing

### Test Markers

```python
@pytest.mark.unit          # Fast isolated tests
@pytest.mark.integration   # CLI and file system tests
@pytest.mark.slow         # Resource-intensive tests
```

## Development Workflow

### Task Completion Checklist

After any code changes, run these commands:

1. `uv run ruff check --fix .` - Auto-fix linting
2. `uv run black .` - Format code
3. `uv run mypy src/` - Type check
4. `uv run pytest` - Run tests
5. `uv run pre-commit run --all-files` - Final validation

### Common Development Tasks

- **Add new extraction method**: Extend PDFExtractor with private method
- **Add CLI command**: Add Click command to `main.py`
- **Add validation**: Extend custom exceptions in `exceptions.py`
- **Modify output format**: Update JSON structure in PDFProcessor methods

## Package Management

- **Package Manager**: uv (fast Python package manager)
- **Build System**: hatchling
- **Dependencies**: Defined in `pyproject.toml` with version constraints
- **CLI Entry Point**: `ingest-pdf` command installed via package scripts

## Configuration Files

- **pyproject.toml**: All tool configuration (pytest, ruff, black, mypy)
- **Makefile**: Common development commands
- **.pre-commit-config.yaml**: Git hooks for code quality
- **CLAUDE.md**: This guidance file
