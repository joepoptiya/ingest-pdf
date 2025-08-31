# Essential Commands for Development

## Setup Commands
```bash
# Install all dependencies including dev dependencies
uv sync --dev

# Set up development environment (install deps + pre-commit hooks)
make dev-setup

# Install pre-commit hooks manually
uv run pre-commit install
```

## Testing Commands
```bash
# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_processor.py

# Run tests in verbose mode
uv run pytest -v

# Run only unit tests
uv run pytest -m "unit"

# Run only integration tests
uv run pytest -m "integration"

# Run fast tests (exclude slow tests)
uv run pytest -m "not slow"
```

## Code Quality Commands
```bash
# Format code with Black
uv run black .

# Check code formatting
uv run black --check .

# Lint code with Ruff
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Type check with MyPy
uv run mypy src/

# Run all quality checks
make check

# Run pre-commit on all files
uv run pre-commit run --all-files
```

## Build and Package Commands
```bash
# Build package
uv build

# Clean build artifacts
make clean

# Install package in development mode
uv pip install -e .
```

## CLI Usage Commands
```bash
# Process single PDF
ingest-pdf process document.pdf

# Process directory of PDFs
ingest-pdf batch ./pdfs/

# Get PDF info
ingest-pdf info document.pdf

# Extract specific page
ingest-pdf page document.pdf 0
```

## Task Completion Commands
After completing any development task, run these commands in order:
1. `uv run ruff check --fix .` - Fix linting issues
2. `uv run black .` - Format code
3. `uv run mypy src/` - Type check
4. `uv run pytest` - Run tests
5. `uv run pre-commit run --all-files` - Run all pre-commit hooks