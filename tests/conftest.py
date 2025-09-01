"""Test configuration and fixtures."""

import logging
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


@pytest.fixture(autouse=True)
def disable_console_logging():
    """Disable console logging during tests to avoid cluttering output."""
    # Set a flag to indicate we're in test mode
    logging._in_test_mode = True
    yield
    # Clean up
    if hasattr(logging, '_in_test_mode'):
        delattr(logging, '_in_test_mode')


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_pdf(temp_dir: Path) -> Path:
    """Create a sample PDF file for testing."""
    pdf_path = temp_dir / "sample.pdf"

    # Create a simple PDF with some text
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(100, 750, "This is a sample PDF document.")
    c.drawString(100, 730, "It contains multiple lines of text.")
    c.drawString(100, 710, "This text is used for testing PDF extraction.")

    # Add a second page
    c.showPage()
    c.drawString(100, 750, "This is page 2 of the sample PDF.")
    c.drawString(100, 730, "It has different content.")

    c.save()
    return pdf_path


@pytest.fixture
def sample_pdf_with_metadata(temp_dir: Path) -> Path:
    """Create a sample PDF with metadata."""
    pdf_path = temp_dir / "sample_with_metadata.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.setTitle("Test PDF Document")
    c.setAuthor("Test Author")
    c.setSubject("Test Subject")

    c.drawString(100, 750, "This PDF has metadata.")
    c.save()

    return pdf_path


@pytest.fixture
def empty_directory(temp_dir: Path) -> Path:
    """Create an empty directory for testing."""
    empty_dir = temp_dir / "empty"
    empty_dir.mkdir()
    return empty_dir


@pytest.fixture
def pdf_directory(temp_dir: Path) -> Path:
    """Create a directory with multiple PDF files."""
    pdf_dir = temp_dir / "pdfs"
    pdf_dir.mkdir()

    # Create multiple PDF files
    for i in range(3):
        pdf_path = pdf_dir / f"document_{i}.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, f"This is document number {i}")
        c.save()

    return pdf_dir
