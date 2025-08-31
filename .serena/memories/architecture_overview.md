# Architecture Overview

## Core Components

### 1. PDFExtractor (`src/ingest_pdf/extractor.py`)
**Purpose**: Low-level PDF text and metadata extraction
**Key Methods**:
- `extract_text()` - Main text extraction with fallback between libraries
- `extract_metadata()` - PDF metadata extraction (title, author, dates)
- `extract_page_text()` - Single page text extraction
- `_extract_with_pdfplumber()` - pdfplumber-based extraction
- `_extract_with_pypdf2()` - PyPDF2-based extraction

**Design**: Strategy pattern for extraction methods (pdfplumber vs PyPDF2)

### 2. PDFProcessor (`src/ingest_pdf/processor.py`) 
**Purpose**: High-level file processing and business logic
**Key Methods**:
- `process_file()` - Single PDF processing with full metadata
- `process_directory()` - Batch processing with filtering
- `save_results()` - JSON output handling
- `extract_text_only()` - Simple text extraction
- `get_file_info()` - File information without full processing

**Design**: Facade pattern over PDFExtractor with added file management

### 3. CLI Interface (`src/ingest_pdf/main.py`)
**Purpose**: Command-line interface using Click framework
**Commands**:
- `process` - Single file processing
- `batch` - Directory batch processing  
- `info` - File information display
- `page` - Single page extraction

**Design**: Click command groups with shared options

### 4. Exception Hierarchy (`src/ingest_pdf/exceptions.py`)
**Base**: `PDFProcessingError`
**Specific Exceptions**:
- `PDFNotFoundError` - File not found
- `PDFReadError` - File reading issues
- `PDFExtractionError` - Text extraction failures

## Data Flow

1. **CLI Command** → Parse arguments and options
2. **PDFProcessor** → Validate input and coordinate processing  
3. **PDFExtractor** → Perform actual PDF operations
4. **Result Formatting** → Convert to JSON structure
5. **Output** → Console display or file saving

## Configuration Management

- **pyproject.toml**: All tool configuration centralized
- **Environment**: Uses Python 3.11+ features
- **Logging**: Structured logging throughout application
- **Error Handling**: Consistent exception propagation

## Testing Architecture

- **Test Structure**: Mirrors source structure in `tests/`
- **Fixtures**: Shared test utilities in `conftest.py`
- **Sample Data**: Generated PDFs using reportlab for testing
- **Coverage**: Comprehensive unit and integration tests