# PDF Ingest App

A Python application for ingesting and processing PDF files with text extraction capabilities.

## Features

- Extract text from PDF files using PyPDF2 or pdfplumber
- Extract PDF metadata (title, author, creation date, etc.)
- Batch process multiple PDF files in a directory
- Command-line interface for easy usage
- Support for both single file and directory processing
- JSON output for processed results
- Comprehensive test coverage

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ingest-pdf

# Install dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd ingest-pdf

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Usage

### Command Line Interface

The application provides several CLI commands:

#### Process a single PDF file

```bash
# Extract text and metadata (JSON output)
ingest-pdf process document.pdf

# Extract text only
ingest-pdf process document.pdf --text-only

# Save results to a JSON file
ingest-pdf process document.pdf --save-results --output-dir ./results

# Use PyPDF2 instead of pdfplumber
ingest-pdf process document.pdf --use-pypdf2
```

#### Batch process PDF files in a directory

```bash
# Process all PDFs in a directory
ingest-pdf batch ./pdfs/

# Process recursively (including subdirectories)
ingest-pdf batch ./pdfs/ --recursive

# Save results to JSON file
ingest-pdf batch ./pdfs/ --save-results
```

#### Get PDF file information

```bash
# Display basic file info and metadata
ingest-pdf info document.pdf
```

#### Extract text from a specific page

```bash
# Extract text from page 0 (first page)
ingest-pdf page document.pdf 0

# Extract text from page 1 (second page)
ingest-pdf page document.pdf 1
```

### Python API

You can also use the library programmatically:

```python
from pathlib import Path
from ingest_pdf import PDFProcessor, PDFExtractor

# Initialize processor
processor = PDFProcessor(output_dir=Path("./results"))

# Process a single file
result = processor.process_file("document.pdf")
print(result["extracted_text"])

# Process directory
results = processor.process_directory("./pdfs", recursive=True)

# Save results
processor.save_results(results, "batch_results.json")

# Extract text only
text = processor.extract_text_only("document.pdf")

# Get file information
info = processor.get_file_info("document.pdf")
```

#### Direct text extraction

```python
from ingest_pdf import PDFExtractor

# Initialize extractor
extractor = PDFExtractor(use_pdfplumber=True)

# Extract text
text = extractor.extract_text(Path("document.pdf"))

# Extract metadata
metadata = extractor.extract_metadata(Path("document.pdf"))

# Extract specific page
page_text = extractor.extract_page_text(Path("document.pdf"), page_number=0)
```

## Output Format

The processed results are returned as JSON with the following structure:

```json
{
  "file_path": "/path/to/document.pdf",
  "file_name": "document.pdf",
  "file_size": 12345,
  "text_length": 1500,
  "extracted_text": "Full extracted text content...",
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "subject": "Document Subject",
    "creator": "PDF Creator",
    "producer": "PDF Producer",
    "creation_date": "2023-01-01T12:00:00",
    "modification_date": "2023-01-02T12:00:00",
    "page_count": 5
  },
  "processed_at": "2023-12-01T10:30:00.123456"
}
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_processor.py

# Run tests in verbose mode
uv run pytest -v
```

### Code Quality

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src/

# Run all quality checks
uv run pre-commit run --all-files
```

### Using Make Commands

```bash
# Install dependencies
make install

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Type check
make type-check

# Run all checks
make check

# Build package
make build

# Clean build artifacts
make clean
```

## Dependencies

### Core Dependencies

- **PyPDF2**: PDF reading and metadata extraction
- **pdfplumber**: Advanced PDF text extraction with better formatting
- **click**: Command-line interface framework
- **pathlib**: Path handling (built-in)
- **typing-extensions**: Type hints support

### Development Dependencies

- **pytest**: Testing framework
- **pytest-cov**: Test coverage reporting
- **pytest-mock**: Mocking for tests
- **ruff**: Fast Python linter
- **black**: Code formatter
- **mypy**: Static type checker
- **pre-commit**: Git hooks framework
- **reportlab**: PDF generation for tests

## Configuration

The application can be configured through:

1. **Command-line arguments**: Control extraction method, output directory, etc.
2. **Environment variables**: (Future enhancement)
3. **Configuration files**: (Future enhancement)

## Error Handling

The application includes comprehensive error handling:

- **PDFNotFoundError**: Raised when PDF file doesn't exist
- **PDFReadError**: Raised when PDF file cannot be read
- **PDFExtractionError**: Raised when text extraction fails
- **PDFProcessingError**: General processing errors

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`make test`)
6. Run code quality checks (`make check`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **PDF files not recognized**: Ensure files have `.pdf` extension
2. **Text extraction returns empty**: Try switching between PyPDF2 and pdfplumber
3. **Permission errors**: Check file permissions and output directory access
4. **Memory issues with large PDFs**: Process files individually rather than in batch

### Performance Tips

- Use pdfplumber for better text extraction quality
- Use PyPDF2 for faster processing of simple PDFs
- Process large directories in smaller batches
- Use appropriate output directory to avoid disk space issues

## Changelog

### v0.1.0

- Initial release
- Basic PDF text extraction
- CLI interface
- Batch processing
- Comprehensive test suite
