"""Configuration management with hot reload capability."""

import hashlib
import logging
import threading
import tomllib
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, validator
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class InputSettings(BaseModel):
    """Input directory and file pattern settings."""

    dir: str = Field(
        default="./inbox", description="Directory to watch for new PDF files"
    )
    pattern: str = Field(
        default="*.pdf", description="File pattern to match (glob pattern)"
    )
    file_type: str = Field(default="pdf", description="File type to process")

    @validator("dir")
    def validate_dir(cls, v: str) -> str:
        """Ensure directory path is valid."""
        return str(Path(v).resolve())


class OutputSettings(BaseModel):
    """Output directory template settings."""

    jsonl_dir: str = Field(
        default="./outputs/jsonl/{stem}-{hash}.jsonl",
        description="JSONL output directory template",
    )
    markdown_dir: str = Field(
        default="./outputs/markdown/{stem}-{hash}.md",
        description="Markdown output directory template",
    )

    @validator("jsonl_dir", "markdown_dir")
    def validate_template(cls, v: str) -> str:
        """Ensure template contains valid placeholders."""
        required_placeholders = {"{stem}", "{hash}"}
        if not any(placeholder in v for placeholder in required_placeholders):
            logger.warning(
                f"Template '{v}' should contain at least one of: {required_placeholders}"
            )
        return v


class LlamaParseSettings(BaseModel):
    """LlamaParse API configuration."""

    api_key: str = Field(default="", description="LlamaParse API key")
    base_url: str = Field(
        default="https://api.llamaindex.ai/api/v1", description="API base URL"
    )
    timeout: int = Field(default=120, ge=1, description="Request timeout in seconds")

    @validator("api_key")
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if v and len(v.strip()) < 10:
            raise ValueError("API key appears to be too short")
        return v.strip()


class ProcessedSettings(BaseModel):
    """Settings for processed file handling."""

    dir: str = Field(
        default="./processed",
        description="Directory to move successfully processed files",
    )
    overwrite_on_dup: bool = Field(
        default=True, description="Whether to overwrite files with duplicate names"
    )

    @validator("dir")
    def validate_dir(cls, v: str) -> str:
        """Ensure directory path is valid."""
        return str(Path(v).resolve())


class QuarantineSettings(BaseModel):
    """Settings for quarantine file handling."""

    dir: str = Field(
        default="./quarantine", description="Directory to move failed files"
    )

    @validator("dir")
    def validate_dir(cls, v: str) -> str:
        """Ensure directory path is valid."""
        return str(Path(v).resolve())


class ConcurrencySettings(BaseModel):
    """Concurrency and threading settings."""

    max_workers: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of worker threads for processing",
    )


class RetrySettings(BaseModel):
    """Retry logic configuration."""

    max_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts for LlamaParse API calls",
    )
    initial_backoff_ms: int = Field(
        default=500, ge=100, description="Initial backoff time in milliseconds"
    )
    max_backoff_ms: int = Field(
        default=5000, ge=1000, description="Maximum backoff time in milliseconds"
    )
    jitter: bool = Field(
        default=True, description="Whether to add jitter to backoff timing"
    )

    @validator("max_backoff_ms")
    def validate_max_backoff(cls, v: int, values: dict[str, Any]) -> int:
        """Ensure max_backoff is greater than initial_backoff."""
        initial = values.get("initial_backoff_ms", 500)
        if v <= initial:
            raise ValueError("max_backoff_ms must be greater than initial_backoff_ms")
        return v


class RedactionSettings(BaseModel):
    """Data redaction configuration."""

    account_numbers: bool = Field(
        default=True, description="Whether to redact account numbers to last-4 format"
    )


class LoggingSettings(BaseModel):
    """Logging configuration."""

    level: str = Field(
        default="INFO", description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    dir: str = Field(default="./logs", description="Log directory")
    rotate_daily: bool = Field(default=True, description="Log file rotation - daily")
    backup_count: int = Field(
        default=7, ge=1, description="Number of backup log files to keep"
    )

    @validator("level")
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v_upper

    @validator("dir")
    def validate_dir(cls, v: str) -> str:
        """Ensure directory path is valid."""
        return str(Path(v).resolve())


class StateSettings(BaseModel):
    """State file configuration."""

    dir: str = Field(
        default="./state", description="Directory for state files (ledger.json)"
    )

    @validator("dir")
    def validate_dir(cls, v: str) -> str:
        """Ensure directory path is valid."""
        return str(Path(v).resolve())


class RunsSettings(BaseModel):
    """Run reports configuration."""

    dir: str = Field(default="./runs", description="Directory for run reports")

    @validator("dir")
    def validate_dir(cls, v: str) -> str:
        """Ensure directory path is valid."""
        return str(Path(v).resolve())


class Settings(BaseModel):
    """Root configuration settings."""

    input: InputSettings = Field(default_factory=InputSettings)
    output: OutputSettings = Field(default_factory=OutputSettings)
    llamaparse: LlamaParseSettings = Field(default_factory=LlamaParseSettings)
    processed: ProcessedSettings = Field(default_factory=ProcessedSettings)
    quarantine: QuarantineSettings = Field(default_factory=QuarantineSettings)
    concurrency: ConcurrencySettings = Field(default_factory=ConcurrencySettings)
    retry: RetrySettings = Field(default_factory=RetrySettings)
    redaction: RedactionSettings = Field(default_factory=RedactionSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    state: StateSettings = Field(default_factory=StateSettings)
    runs: RunsSettings = Field(default_factory=RunsSettings)

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        extra = "forbid"

    def get_file_hash(self, file_path: Path) -> str:
        """Generate SHA256 hash for a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()[:8]  # Short hash for filenames


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for config file changes."""

    def __init__(self, config_loader: "ConfigLoader") -> None:
        """Initialize handler with reference to config loader."""
        self.config_loader = config_loader
        super().__init__()

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory and event.src_path == str(
            self.config_loader.config_path
        ):
            logger.info(f"Config file modified: {event.src_path}")
            self.config_loader.reload_config()


class ConfigLoader:
    """Configuration loader with hot reload capability."""

    _instance: Optional["ConfigLoader"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, config_path: str | Path | None = None) -> "ConfigLoader":
        """Implement singleton pattern with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized: bool = False
        return cls._instance

    def __init__(self, config_path: str | Path | None = None) -> None:
        """Initialize config loader."""
        if getattr(self, '_initialized', False):
            return

        self.config_path: Path = Path(config_path or "config.toml").resolve()
        self._settings: Settings | None = None
        self._observer: Optional[Observer] = None
        self._reload_lock = threading.Lock()
        self._initialized: bool = True

        # Initial config load
        self.reload_config()

        # Start file watcher
        self._start_watcher()

    def _start_watcher(self) -> None:
        """Start file system watcher for config changes."""
        try:
            self._observer = Observer()
            handler = ConfigFileHandler(self)
            watch_dir = self.config_path.parent
            self._observer.schedule(handler, str(watch_dir), recursive=False)
            self._observer.start()
            logger.info(f"Started config watcher for: {self.config_path}")
        except Exception as e:
            logger.warning(f"Failed to start config file watcher: {e}")
            self._observer = None

    def stop_watcher(self) -> None:
        """Stop the file system watcher."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            logger.info("Stopped config file watcher")

    def reload_config(self) -> None:
        """Reload configuration from file with thread safety."""
        with self._reload_lock:
            try:
                logger.debug(f"Loading config from: {self.config_path}")

                if not self.config_path.exists():
                    logger.warning(
                        f"Config file not found: {self.config_path}, using defaults"
                    )
                    self._settings = Settings()
                    return

                with open(self.config_path, "rb") as f:
                    config_data = tomllib.load(f)

                # Merge with environment variables for sensitive data
                self._merge_env_vars(config_data)

                self._settings = Settings(**config_data)
                logger.info("Configuration reloaded successfully")

            except tomllib.TOMLDecodeError as e:
                logger.error(f"Invalid TOML in config file: {e}")
                if self._settings is None:
                    # First load failed, use defaults
                    self._settings = Settings()
                # Keep existing settings on reload failure

            except Exception as e:
                logger.error(f"Error loading config: {e}")
                if self._settings is None:
                    # First load failed, use defaults
                    self._settings = Settings()
                # Keep existing settings on reload failure

    def _merge_env_vars(self, config_data: dict[str, Any]) -> None:
        """Merge environment variables into config data."""
        import os

        # LlamaParse API key from environment
        env_api_key = os.getenv("LLAMAPARSE_API_KEY")
        if env_api_key:
            if "llamaparse" not in config_data:
                config_data["llamaparse"] = {}
            config_data["llamaparse"]["api_key"] = env_api_key

    @property
    def settings(self) -> Settings:
        """Get current settings."""
        if self._settings is None:
            self.reload_config()
        assert self._settings is not None  # Should always be set after reload_config
        return self._settings

    def __del__(self) -> None:
        """Cleanup on deletion."""
        self.stop_watcher()


def get_config() -> Settings:
    """Get global configuration instance."""
    loader = ConfigLoader()
    return loader.settings


# For convenience, create module-level instance
config_loader = ConfigLoader()
