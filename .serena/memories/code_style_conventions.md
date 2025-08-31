# Code Style and Conventions

## Python Version and Typing
- **Python 3.11+** required
- **Strict typing**: All functions must have type annotations
- Use `typing-extensions` for modern type hints
- MyPy strict configuration enabled

## Code Formatting and Style
- **Line length**: 88 characters (Black default)
- **Formatter**: Black (configured in pyproject.toml)
- **Import sorting**: Handled by Ruff
- **Quote style**: Black's default (generally double quotes)

## Linting Rules (Ruff Configuration)
- **Enabled rules**:
  - E, W: pycodestyle errors and warnings
  - F: pyflakes
  - I: isort (import sorting)
  - B: flake8-bugbear
  - C4: flake8-comprehensions
  - UP: pyupgrade
- **Disabled rules**:
  - E501: line too long (handled by Black)
  - B008: function calls in argument defaults
  - C901: too complex

## Naming Conventions
- **Classes**: PascalCase (e.g., `PDFProcessor`, `PDFExtractor`)
- **Functions/Methods**: snake_case (e.g., `process_file`, `extract_text`)
- **Variables**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Private methods**: prefix with underscore (e.g., `_extract_with_pdfplumber`)

## File and Directory Structure
- **Package structure**: `src/ingest_pdf/` layout
- **Test files**: `test_*.py` pattern in `tests/` directory
- **Module imports**: Use relative imports within package

## Error Handling
- **Custom exceptions**: Defined in `exceptions.py`
- **Exception hierarchy**: All inherit from `PDFProcessingError`
- **Logging**: Use structured logging with appropriate levels
- **Error messages**: Descriptive and actionable

## Documentation and Comments
- **Docstrings**: Required for all public classes and methods
- **Type hints**: Comprehensive type annotations required
- **Inline comments**: Minimal, focus on "why" not "what"

## Testing Conventions
- **Test markers**: Use `@pytest.mark.unit` and `@pytest.mark.integration`
- **Test fixtures**: Defined in `conftest.py`
- **Coverage target**: High coverage expected
- **Test isolation**: Each test should be independent