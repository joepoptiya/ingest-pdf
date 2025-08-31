"""Tests for PDF extractor functionality."""

import pytest

from ingest_pdf.exceptions import PDFExtractionError, PDFNotFoundError
from ingest_pdf.extractor import PDFExtractor


class TestPDFExtractor:
    """Test cases for PDFExtractor."""

    def test_init_default(self):
        """Test extractor initialization with default parameters."""
        extractor = PDFExtractor()
        assert extractor.use_pdfplumber is True

    def test_init_pypdf2(self):
        """Test extractor initialization with PyPDF2."""
        extractor = PDFExtractor(use_pdfplumber=False)
        assert extractor.use_pdfplumber is False

    def test_extract_text_pdfplumber(self, sample_pdf):
        """Test text extraction with pdfplumber."""
        extractor = PDFExtractor(use_pdfplumber=True)
        text = extractor.extract_text(sample_pdf)

        assert "sample PDF document" in text
        assert "multiple lines of text" in text
        assert "page 2" in text

    def test_extract_text_pypdf2(self, sample_pdf):
        """Test text extraction with PyPDF2."""
        extractor = PDFExtractor(use_pdfplumber=False)
        text = extractor.extract_text(sample_pdf)

        assert "sample PDF document" in text
        assert "multiple lines of text" in text

    def test_extract_text_file_not_found(self, temp_dir):
        """Test extraction with non-existent file."""
        extractor = PDFExtractor()
        non_existent_file = temp_dir / "does_not_exist.pdf"

        with pytest.raises(PDFNotFoundError):
            extractor.extract_text(non_existent_file)

    def test_extract_metadata(self, sample_pdf_with_metadata):
        """Test metadata extraction."""
        extractor = PDFExtractor()
        metadata = extractor.extract_metadata(sample_pdf_with_metadata)

        assert metadata["title"] == "Test PDF Document"
        assert metadata["author"] == "Test Author"
        assert metadata["subject"] == "Test Subject"
        assert metadata["page_count"] == 1
        assert "creation_date" in metadata

    def test_extract_metadata_file_not_found(self, temp_dir):
        """Test metadata extraction with non-existent file."""
        extractor = PDFExtractor()
        non_existent_file = temp_dir / "does_not_exist.pdf"

        with pytest.raises(PDFNotFoundError):
            extractor.extract_metadata(non_existent_file)

    def test_extract_page_text_pdfplumber(self, sample_pdf):
        """Test single page text extraction with pdfplumber."""
        extractor = PDFExtractor(use_pdfplumber=True)

        # Test first page
        page_0_text = extractor.extract_page_text(sample_pdf, 0)
        assert "sample PDF document" in page_0_text
        assert "page 2" not in page_0_text

        # Test second page
        page_1_text = extractor.extract_page_text(sample_pdf, 1)
        assert "page 2" in page_1_text
        assert "sample PDF document" not in page_1_text

    def test_extract_page_text_pypdf2(self, sample_pdf):
        """Test single page text extraction with PyPDF2."""
        extractor = PDFExtractor(use_pdfplumber=False)

        page_0_text = extractor.extract_page_text(sample_pdf, 0)
        assert "sample PDF document" in page_0_text

    def test_extract_page_text_invalid_page(self, sample_pdf):
        """Test extraction with invalid page number."""
        extractor = PDFExtractor()

        with pytest.raises(PDFExtractionError):
            extractor.extract_page_text(sample_pdf, 999)

    def test_extract_page_text_file_not_found(self, temp_dir):
        """Test page extraction with non-existent file."""
        extractor = PDFExtractor()
        non_existent_file = temp_dir / "does_not_exist.pdf"

        with pytest.raises(PDFNotFoundError):
            extractor.extract_page_text(non_existent_file, 0)
