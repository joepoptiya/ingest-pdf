"""Tests for PDF extractor functionality."""

import os
from unittest.mock import Mock, patch

import pytest

from ingest_pdf.exceptions import PDFExtractionError, PDFNotFoundError
from ingest_pdf.extractor import PDFExtractor


class TestPDFExtractor:
    """Test cases for PDFExtractor."""

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_init_with_api_key(self):
        """Test extractor initialization with API key."""
        with patch("ingest_pdf.extractor.LlamaParse") as mock_llama_parse:
            extractor = PDFExtractor()
            assert extractor.parser is not None
            mock_llama_parse.assert_called_once_with(
                api_key="test-api-key",
                result_type="markdown",
                language="en",
                verbose=True,
            )

    def test_init_without_api_key(self):
        """Test extractor initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                PDFExtractionError,
                match="LLAMA_CLOUD_API_KEY environment variable is required",
            ):
                PDFExtractor()

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_extract_text_success(self, sample_pdf):
        """Test successful text extraction with LlamaParse."""
        mock_doc = Mock()
        mock_doc.text = "This is extracted text from PDF\n\nSecond paragraph"

        with patch("ingest_pdf.extractor.LlamaParse") as mock_llama_parse:
            mock_parser = Mock()
            mock_parser.load_data.return_value = [mock_doc]
            mock_llama_parse.return_value = mock_parser

            extractor = PDFExtractor()
            text = extractor.extract_text(sample_pdf)

            assert "This is extracted text from PDF" in text
            assert "Second paragraph" in text
            mock_parser.load_data.assert_called_once_with(str(sample_pdf))

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_extract_text_no_content(self, sample_pdf):
        """Test text extraction with no content returned."""
        with patch("ingest_pdf.extractor.LlamaParse") as mock_llama_parse:
            mock_parser = Mock()
            mock_parser.load_data.return_value = []
            mock_llama_parse.return_value = mock_parser

            extractor = PDFExtractor()
            text = extractor.extract_text(sample_pdf)

            assert text == ""

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_extract_text_file_not_found(self, temp_dir):
        """Test extraction with non-existent file."""
        with patch("ingest_pdf.extractor.LlamaParse"):
            extractor = PDFExtractor()
            non_existent_file = temp_dir / "does_not_exist.pdf"

            with pytest.raises(PDFNotFoundError):
                extractor.extract_text(non_existent_file)

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_extract_metadata(self, sample_pdf):
        """Test metadata extraction."""
        mock_doc = Mock()
        mock_doc.text = "Sample PDF content for metadata extraction"

        with patch("ingest_pdf.extractor.LlamaParse") as mock_llama_parse:
            mock_parser = Mock()
            mock_parser.load_data.return_value = [mock_doc]
            mock_llama_parse.return_value = mock_parser

            extractor = PDFExtractor()
            metadata = extractor.extract_metadata(sample_pdf)

            assert metadata["title"] == sample_pdf.stem
            assert metadata["author"] is None
            assert metadata["producer"] == "LlamaParse"
            assert "creation_date" in metadata
            assert "modification_date" in metadata
            assert "page_count" in metadata
            assert "file_size" in metadata
            assert "text_length" in metadata

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_extract_metadata_file_not_found(self, temp_dir):
        """Test metadata extraction with non-existent file."""
        with patch("ingest_pdf.extractor.LlamaParse"):
            extractor = PDFExtractor()
            non_existent_file = temp_dir / "does_not_exist.pdf"

            with pytest.raises(PDFNotFoundError):
                extractor.extract_metadata(non_existent_file)

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_extract_page_text_success(self, sample_pdf):
        """Test single page text extraction."""
        mock_doc = Mock()
        mock_doc.text = "Page 1 content\f\nPage 2 content"

        with patch("ingest_pdf.extractor.LlamaParse") as mock_llama_parse:
            mock_parser = Mock()
            mock_parser.load_data.return_value = [mock_doc]
            mock_llama_parse.return_value = mock_parser

            extractor = PDFExtractor()

            # Test first page
            page_0_text = extractor.extract_page_text(sample_pdf, 0)
            assert "Page 1 content" in page_0_text

            # Test second page
            page_1_text = extractor.extract_page_text(sample_pdf, 1)
            assert "Page 2 content" in page_1_text

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_extract_page_text_no_page_breaks(self, sample_pdf):
        """Test page extraction when no page breaks are detected."""
        mock_doc = Mock()
        mock_doc.text = (
            "Long continuous text content without page breaks" * 100
        )  # Make it long

        with patch("ingest_pdf.extractor.LlamaParse") as mock_llama_parse:
            mock_parser = Mock()
            mock_parser.load_data.return_value = [mock_doc]
            mock_llama_parse.return_value = mock_parser

            extractor = PDFExtractor()
            page_0_text = extractor.extract_page_text(sample_pdf, 0)

            assert len(page_0_text) > 0
            assert "Long continuous text" in page_0_text

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_extract_page_text_invalid_page(self, sample_pdf):
        """Test extraction with invalid page number."""
        mock_doc = Mock()
        mock_doc.text = "Single page content"

        with patch("ingest_pdf.extractor.LlamaParse") as mock_llama_parse:
            mock_parser = Mock()
            mock_parser.load_data.return_value = [mock_doc]
            mock_llama_parse.return_value = mock_parser

            extractor = PDFExtractor()

            with pytest.raises(PDFExtractionError):
                extractor.extract_page_text(sample_pdf, 999)

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_extract_page_text_file_not_found(self, temp_dir):
        """Test page extraction with non-existent file."""
        with patch("ingest_pdf.extractor.LlamaParse"):
            extractor = PDFExtractor()
            non_existent_file = temp_dir / "does_not_exist.pdf"

            with pytest.raises(PDFNotFoundError):
                extractor.extract_page_text(non_existent_file, 0)

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_extract_text_api_error(self, sample_pdf):
        """Test extraction with API error and retry."""
        with patch("ingest_pdf.extractor.LlamaParse") as mock_llama_parse:
            mock_parser = Mock()
            mock_parser.load_data.side_effect = Exception("API Error")
            mock_llama_parse.return_value = mock_parser

            extractor = PDFExtractor()

            with pytest.raises(PDFExtractionError):
                extractor.extract_text(sample_pdf)
