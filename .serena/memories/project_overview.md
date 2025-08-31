# Project Overview

## Purpose
A Python PDF ingestion application that extracts text and metadata from PDF files. Built using PyPDF2 and pdfplumber libraries with comprehensive CLI interface.

## Tech Stack
- **Python**: 3.11+ with modern typing
- **Core Libraries**: PyPDF2, pdfplumber, click, pathlib, typing-extensions  
- **Dev Tools**: pytest, ruff, black, mypy, pre-commit, reportlab
- **Package Manager**: uv (modern Python package manager)
- **Build System**: hatchling

## Key Features
- Single file and batch PDF processing
- Text extraction using PyPDF2 or pdfplumber
- Metadata extraction (title, author, dates, etc.)
- CLI interface with multiple commands
- JSON output format
- Comprehensive test coverage
- Pre-commit hooks for code quality

## Architecture
Modular design with clear separation of concerns:
1. **PDFExtractor** (extractor.py): Low-level PDF text/metadata extraction
2. **PDFProcessor** (processor.py): High-level processing and file management  
3. **CLI Module** (main.py): Command-line interface using Click
4. **Custom Exceptions** (exceptions.py): Domain-specific error handling