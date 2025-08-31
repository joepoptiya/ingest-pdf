"""Command-line interface for PDF ingestion."""

import logging
import sys
from pathlib import Path

import click

from . import __version__
from .config import ConfigLoader, get_config
from .exceptions import PDFProcessingError
from .processor import PDFProcessor


def setup_logging(verbose: bool = False, config_path: str | None = None) -> None:
    """Set up logging configuration using config settings."""
    try:
        # Initialize config loader if config_path provided
        if config_path:
            ConfigLoader(config_path)

        config = get_config()

        # Use verbose flag to override config level if provided
        if verbose:
            level = logging.DEBUG
        else:
            level = getattr(logging, config.logging.level)

        # Create log directory
        log_dir = Path(config.logging.dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_dir / "pdf-ingestor.log"),
            ],
        )

        # Log config info
        logger = logging.getLogger(__name__)
        logger.info(
            f"Logging configured: level={logging.getLevelName(level)}, dir={log_dir}"
        )

    except Exception as e:
        # Fallback to basic logging if config fails
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.getLogger(__name__).warning(f"Failed to setup logging from config: {e}")


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to config file"
)
@click.option(
    "--dry-run", is_flag=True, help="Dry run mode (no external calls or writes)"
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: str | None, dry_run: bool) -> None:
    """PDF ingestion and processing tool."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config_path"] = config
    ctx.obj["dry_run"] = dry_run
    setup_logging(verbose, config)


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
@click.option("--use-pypdf2", is_flag=True, help="Use PyPDF2 instead of pdfplumber")
@click.pass_context
def process(
    ctx: click.Context,
    pdf_path: Path,
    output_dir: Path | None,
    save_results: bool,
    text_only: bool,
    use_pypdf2: bool,
) -> None:
    """Process a single PDF file."""
    try:
        processor = PDFProcessor(output_dir=output_dir, use_pdfplumber=not use_pypdf2)

        if text_only:
            text = processor.extract_text_only(pdf_path)
            click.echo(text)
        else:
            result = processor.process_file(pdf_path)

            if save_results:
                output_file = processor.save_results(result)
                click.echo(f"Results saved to: {output_file}")
            else:
                import json

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
@click.option("--use-pypdf2", is_flag=True, help="Use PyPDF2 instead of pdfplumber")
@click.pass_context
def batch(
    ctx: click.Context,
    directory_path: Path,
    output_dir: Path | None,
    recursive: bool,
    save_results: bool,
    use_pypdf2: bool,
) -> None:
    """Process all PDF files in a directory."""
    try:
        processor = PDFProcessor(output_dir=output_dir, use_pdfplumber=not use_pypdf2)

        results = processor.process_directory(directory_path, recursive=recursive)

        if not results:
            click.echo("No PDF files found or processed.")
            return

        if save_results:
            output_file = processor.save_results(results)
            click.echo(f"Results saved to: {output_file}")
        else:
            import json

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
@click.option("--use-pypdf2", is_flag=True, help="Use PyPDF2 instead of pdfplumber")
@click.pass_context
def page(
    ctx: click.Context, pdf_path: Path, page_number: int, use_pypdf2: bool
) -> None:
    """Extract text from a specific page (0-indexed)."""
    try:
        processor = PDFProcessor(use_pdfplumber=not use_pypdf2)
        text = processor.extractor.extract_page_text(pdf_path, page_number)
        click.echo(text)

    except PDFProcessingError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def watch(ctx: click.Context) -> None:
    """Start watching directory for new PDFs."""
    dry_run = ctx.obj.get("dry_run", False)

    try:
        config = get_config()

        if dry_run:
            click.echo("DRY RUN MODE: Would start watching directory for new PDFs")
            click.echo(f"Watch directory: {config.input.dir}")
            click.echo(f"File pattern: {config.input.pattern}")
            click.echo(f"Max workers: {config.concurrency.max_workers}")
            return

        click.echo("Starting PDF ingestion watcher...")
        click.echo(f"Watching: {config.input.dir}")
        click.echo(f"Pattern: {config.input.pattern}")
        click.echo("Press Ctrl+C to stop")

        # TODO: Implement actual watcher functionality
        # This is a placeholder for the watcher implementation
        click.echo("Watcher functionality not yet implemented")

    except Exception as e:
        click.echo(f"Error starting watcher: {e}", err=True)
        sys.exit(1)


@cli.command(name="ingest-once")
@click.pass_context
def ingest_once(ctx: click.Context) -> None:
    """Process files once (no watching)."""
    dry_run = ctx.obj.get("dry_run", False)

    try:
        config = get_config()

        if dry_run:
            click.echo("DRY RUN MODE: Would process files once")
            click.echo(f"Input directory: {config.input.dir}")
            click.echo(f"File pattern: {config.input.pattern}")
            return

        click.echo(f"Processing PDFs from: {config.input.dir}")

        # TODO: Implement actual ingestion functionality
        # This is a placeholder for the ingestion implementation
        click.echo("Ingestion functionality not yet implemented")

    except Exception as e:
        click.echo(f"Error during ingestion: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def reprocess(ctx: click.Context) -> None:
    """Reprocess files from ledger."""
    dry_run = ctx.obj.get("dry_run", False)

    try:
        config = get_config()

        if dry_run:
            click.echo("DRY RUN MODE: Would reprocess files from ledger")
            click.echo(f"State directory: {config.state.dir}")
            return

        click.echo(f"Reprocessing files from ledger in: {config.state.dir}")

        # TODO: Implement actual reprocessing functionality
        # This is a placeholder for the reprocessing implementation
        click.echo("Reprocessing functionality not yet implemented")

    except Exception as e:
        click.echo(f"Error during reprocessing: {e}", err=True)
        sys.exit(1)


@cli.command(name="show-config")
@click.pass_context
def show_config(ctx: click.Context) -> None:
    """Show current configuration."""
    try:
        config = get_config()

        click.echo("Current Configuration:")
        click.echo("=" * 50)
        click.echo(f"Input directory: {config.input.dir}")
        click.echo(f"File pattern: {config.input.pattern}")
        click.echo(f"Max workers: {config.concurrency.max_workers}")
        click.echo(f"Retry attempts: {config.retry.max_attempts}")
        click.echo(f"Log level: {config.logging.level}")
        click.echo(f"Output JSONL: {config.output.jsonl_dir}")
        click.echo(f"Output Markdown: {config.output.markdown_dir}")
        click.echo(f"Processed dir: {config.processed.dir}")
        click.echo(f"Quarantine dir: {config.quarantine.dir}")
        click.echo(f"State dir: {config.state.dir}")
        click.echo(f"Runs dir: {config.runs.dir}")

    except Exception as e:
        click.echo(f"Error showing config: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    try:
        cli()
    finally:
        # Cleanup config loader on exit
        try:
            from .config import config_loader

            config_loader.stop_watcher()
        except Exception:
            pass  # Ignore cleanup errors


if __name__ == "__main__":
    main()
