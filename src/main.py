"""Main entry point for the PDF ingestion pipeline."""

import logging
import sys
from pathlib import Path

from config import settings
from ingest_pdf.main import main as cli_main
from utils.context import RunContext

CFG = settings()


def setup_global_logging(run_context: RunContext) -> None:
    """Setup global logging configuration with run_id.
    
    Args:
        run_context: RunContext containing run_id and configuration
    """
    try:
        # Get logging config from settings
        log_level = CFG.get("logging", {}).get("level", "INFO")
        log_dir = Path(CFG.get("logging", {}).get("dir", "./logs"))

        # Ensure log directory exists
        log_dir.mkdir(parents=True, exist_ok=True)

        # Configure logging with run_id
        log_format = f"%(asctime)s - %(name)s - %(levelname)s - [run_id:{run_context.run_id}] - %(message)s"

        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format=log_format,
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_dir / "pdf-pipeline.log"),
            ],
            force=True,
        )

        logger = logging.getLogger(__name__)
        logger.info(f"Global logging initialized for run: {run_context.run_id}")
        logger.info(f"App version: {CFG.get('version', {}).get('app_version', 'unknown')}")

    except Exception as e:
        # Fallback logging
        logging.basicConfig(
            level=logging.INFO,
            format=f"%(asctime)s - %(name)s - %(levelname)s - [run_id:{run_context.run_id}] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            force=True,
        )
        logging.getLogger(__name__).warning(f"Failed to setup global logging: {e}")


def main() -> None:
    """Main entry point for the PDF processing pipeline."""
    # Create global run context
    run_context = RunContext.create()

    # Setup global logging with run_id
    setup_global_logging(run_context)

    logger = logging.getLogger(__name__)
    logger.info(f"Starting PDF processing pipeline with run_id: {run_context.run_id}")

    try:
        # Start the CLI main function
        # Note: The CLI will create its own RunContext for each command
        # The global run_context here is for the overall pipeline session
        cli_main()
    except KeyboardInterrupt:
        logger.info(f"Pipeline interrupted by user [run_id: {run_context.run_id}]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e} [run_id: {run_context.run_id}]")
        sys.exit(1)
    finally:
        logger.info(f"Pipeline execution completed [run_id: {run_context.run_id}]")


if __name__ == "__main__":
    main()
