"""Tests for CLI functionality."""

import json
from pathlib import Path

from click.testing import CliRunner

from ingest_pdf.main import cli


class TestCLI:
    """Test cases for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "PDF ingestion and processing tool" in result.output

    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_process_command(self, sample_pdf):
        """Test process command."""
        result = self.runner.invoke(cli, ["process", str(sample_pdf)])
        assert result.exit_code == 0

        # Parse JSON output
        output_data = json.loads(result.output)
        assert "file_name" in output_data
        assert "extracted_text" in output_data
        assert sample_pdf.name == output_data["file_name"]

    def test_process_command_text_only(self, sample_pdf):
        """Test process command with text-only flag."""
        result = self.runner.invoke(cli, ["process", str(sample_pdf), "--text-only"])
        assert result.exit_code == 0
        assert "sample PDF document" in result.output

    def test_process_command_save_results(self, sample_pdf, temp_dir):
        """Test process command with save results flag."""
        with self.runner.isolated_filesystem():
            # Copy the sample PDF to the isolated filesystem
            import shutil
            isolated_pdf = Path("sample.pdf")
            shutil.copy2(sample_pdf, isolated_pdf)

            result = self.runner.invoke(
                cli, ["process", "sample.pdf", "--save-results", "--output-dir", "."]
            )
            assert result.exit_code == 0
            assert "Results saved to" in result.output

            # Check that file was created
            json_files = list(Path(".").glob("*.json"))
            assert len(json_files) == 1

    def test_process_command_pypdf2(self, sample_pdf):
        """Test process command with PyPDF2."""
        result = self.runner.invoke(cli, ["process", str(sample_pdf), "--use-pypdf2"])
        assert result.exit_code == 0

        output_data = json.loads(result.output)
        assert "extracted_text" in output_data

    def test_process_command_not_found(self):
        """Test process command with non-existent file."""
        result = self.runner.invoke(cli, ["process", "nonexistent.pdf"])
        assert result.exit_code == 2  # Click returns 2 for file not found errors
        assert "Error" in result.output

    def test_batch_command(self, pdf_directory):
        """Test batch processing command."""
        result = self.runner.invoke(cli, ["batch", str(pdf_directory)])
        assert result.exit_code == 0

        output_data = json.loads(result.output)
        assert isinstance(output_data, list)
        assert len(output_data) == 3

    def test_batch_command_recursive(self, temp_dir):
        """Test batch command with recursive flag."""
        # Create nested structure
        sub_dir = temp_dir / "subdir"
        sub_dir.mkdir()

        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf_path = sub_dir / "nested.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "Nested PDF")
        c.save()

        result = self.runner.invoke(cli, ["batch", str(temp_dir), "--recursive"])
        assert result.exit_code == 0

        output_data = json.loads(result.output)
        assert len(output_data) == 1
        assert "nested.pdf" in output_data[0]["file_name"]

    def test_batch_command_empty_directory(self, empty_directory):
        """Test batch command on empty directory."""
        result = self.runner.invoke(cli, ["batch", str(empty_directory)])
        assert result.exit_code == 0
        assert "No PDF files found" in result.output

    def test_info_command(self, sample_pdf_with_metadata):
        """Test info command."""
        result = self.runner.invoke(cli, ["info", str(sample_pdf_with_metadata)])
        assert result.exit_code == 0
        assert "PDF File Information" in result.output
        assert "Test PDF Document" in result.output
        assert "Test Author" in result.output

    def test_page_command(self, sample_pdf):
        """Test page extraction command."""
        result = self.runner.invoke(cli, ["page", str(sample_pdf), "0"])
        assert result.exit_code == 0
        assert "sample PDF document" in result.output
        assert "page 2" not in result.output

    def test_page_command_second_page(self, sample_pdf):
        """Test extracting second page."""
        result = self.runner.invoke(cli, ["page", str(sample_pdf), "1"])
        assert result.exit_code == 0
        assert "page 2" in result.output

    def test_page_command_invalid_page(self, sample_pdf):
        """Test page command with invalid page number."""
        result = self.runner.invoke(cli, ["page", str(sample_pdf), "999"])
        assert result.exit_code == 1
        assert "Error" in result.output

    def test_verbose_flag(self, sample_pdf):
        """Test verbose logging flag."""
        result = self.runner.invoke(
            cli, ["--verbose", "process", str(sample_pdf), "--text-only"]
        )
        assert result.exit_code == 0
