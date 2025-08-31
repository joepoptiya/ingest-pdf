# Task Completion Checklist

When completing any development task, follow this checklist in order:

## 1. Code Quality Checks
- [ ] `uv run ruff check --fix .` - Auto-fix linting issues
- [ ] `uv run black .` - Format code with Black
- [ ] `uv run mypy src/` - Run type checking
- [ ] Fix any mypy errors or warnings

## 2. Testing
- [ ] `uv run pytest` - Run full test suite
- [ ] Ensure all tests pass
- [ ] Add tests for new functionality
- [ ] Check test coverage with `uv run pytest --cov`

## 3. Pre-commit Validation
- [ ] `uv run pre-commit run --all-files` - Run all pre-commit hooks
- [ ] Address any pre-commit failures

## 4. Integration Testing
- [ ] Test CLI commands manually if applicable:
  - `ingest-pdf --help`
  - `ingest-pdf process <test-file>`
  - `ingest-pdf batch <test-dir>`

## 5. Build Verification (if applicable)
- [ ] `uv build` - Verify package builds successfully
- [ ] Check that all required files are included

## Alternative: Use Make Target
Instead of individual commands, you can use:
- [ ] `make check` - Runs linting, formatting check, type check, and tests

## Pre-commit Setup (One-time)
If not already done:
- [ ] `uv run pre-commit install` - Install git hooks
- [ ] `make dev-setup` - Complete development environment setup

## Notes
- **Never bypass pre-commit hooks** with `--no-verify`
- **Fix failing tests** rather than skipping them
- **Address type checking errors** - don't ignore mypy warnings
- **Maintain test coverage** - add tests for new code