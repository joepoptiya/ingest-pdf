"""CLI interface for PDF processing."""

import json
import logging
import sys
from pathlib import Path

import click

from . import __version__
from .exceptions import PDFProcessingError
from .processor import PDFProcessor


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """PDF ingestion and processing tool."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    setup_logging(verbose)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for results",
)
@click.option("--save-results", "-s", is_flag=True, help="Save results to JSON file")
@click.option("--text-only", "-t", is_flag=True, help="Extract text only (no metadata)")
@click.pass_context
def process(
    ctx: click.Context,
    pdf_path: Path,
    output_dir: Path | None,
    save_results: bool,
    text_only: bool,
) -> None:
    """Process a single PDF file."""
    try:
        processor = PDFProcessor(output_dir=output_dir)

        if text_only:
            text = processor.extract_text_only(pdf_path)
            click.echo(text)
        else:
            result = processor.process_file(pdf_path)

            if save_results:
                output_file = processor.save_results(result)
                click.echo(f"Results saved to: {output_file}")
            else:
                click.echo(json.dumps(result, indent=2, ensure_ascii=False))

    except PDFProcessingError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("directory_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for results",
)
@click.option(
    "--recursive", "-r", is_flag=True, help="Process subdirectories recursively"
)
@click.option("--save-results", "-s", is_flag=True, help="Save results to JSON file")
@click.pass_context
def batch(
    ctx: click.Context,
    directory_path: Path,
    output_dir: Path | None,
    recursive: bool,
    save_results: bool,
) -> None:
    """Process all PDF files in a directory."""
    try:
        processor = PDFProcessor(output_dir=output_dir)

        results = processor.process_directory(directory_path, recursive=recursive)

        if not results:
            click.echo("No PDF files found or processed.")
            return

        if save_results:
            output_file = processor.save_results(results)
            click.echo(f"Results saved to: {output_file}")
        else:
            click.echo(json.dumps(results, indent=2, ensure_ascii=False))

    except PDFProcessingError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)



@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def info(ctx: click.Context, pdf_path: Path) -> None:
    """Get basic information about a PDF file."""
    try:
        processor = PDFProcessor()
        file_info = processor.get_file_info(pdf_path)

        click.echo("PDF File Information:")
        click.echo("-" * 20)
        for key, value in file_info.items():
            click.echo(f"{key.replace('_', ' ').title()}: {value}")

    except PDFProcessingError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))
@click.argument("page_number", type=int)
@click.pass_context
def page(ctx: click.Context, pdf_path: Path, page_number: int) -> None:
    """Extract text from a specific page (0-indexed)."""
    try:
        processor = PDFProcessor()
        text = processor.extractor.extract_page_text(pdf_path, page_number)
        click.echo(text)

    except PDFProcessingError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    cli()
