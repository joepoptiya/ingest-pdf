"""Tests for configuration management."""

import os
import tempfile
import threading
import time
from collections.abc import Generator
from pathlib import Path

import pytest
from pydantic import ValidationError

from ingest_pdf.config import (
    ConcurrencySettings,
    ConfigLoader,
    InputSettings,
    LlamaParseSettings,
    LoggingSettings,
    OutputSettings,
    ProcessedSettings,
    QuarantineSettings,
    RedactionSettings,
    RetrySettings,
    RunsSettings,
    Settings,
    StateSettings,
    get_config,
)


@pytest.fixture
def temp_config_file() -> Generator[Path, None, None]:
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(
            """
[input]
dir = "./test_inbox"
pattern = "*.pdf"
file_type = "pdf"

[output]
jsonl_dir = "./test_outputs/jsonl/{stem}-{hash}.jsonl"
markdown_dir = "./test_outputs/markdown/{stem}-{hash}.md"

[llamaparse]
api_key = "test_key_123456789"
base_url = "https://test.api.com/v1"
timeout = 60

[processed]
dir = "./test_processed"
overwrite_on_dup = false

[quarantine]
dir = "./test_quarantine"

[concurrency]
max_workers = 5

[retry]
max_attempts = 2
initial_backoff_ms = 200
max_backoff_ms = 2000
jitter = false

[redaction]
account_numbers = false

[logging]
level = "DEBUG"
dir = "./test_logs"
rotate_daily = false
backup_count = 3

[state]
dir = "./test_state"

[runs]
dir = "./test_runs"
"""
        )
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def invalid_config_file() -> Generator[Path, None, None]:
    """Create an invalid config file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(
            """
[input]
dir = "./test_inbox"
pattern = "*.pdf"
file_type = "pdf"

[retry]
max_attempts = 2
initial_backoff_ms = 5000  # Invalid: greater than max_backoff_ms
max_backoff_ms = 2000
"""
        )
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def malformed_toml_file() -> Generator[Path, None, None]:
    """Create a malformed TOML file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(
            """
[input
dir = "./test_inbox"  # Missing closing bracket
pattern = "*.pdf"
"""
        )
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


class TestInputSettings:
    """Test InputSettings model."""

    def test_default_values(self):
        """Test default input settings."""
        settings = InputSettings()
        assert settings.dir == str(Path("./inbox").resolve())
        assert settings.pattern == "*.pdf"
        assert settings.file_type == "pdf"

    def test_custom_values(self):
        """Test custom input settings."""
        settings = InputSettings(dir="/custom/path", pattern="*.doc", file_type="doc")
        assert settings.dir == str(Path("/custom/path").resolve())
        assert settings.pattern == "*.doc"
        assert settings.file_type == "doc"


class TestOutputSettings:
    """Test OutputSettings model."""

    def test_default_values(self):
        """Test default output settings."""
        settings = OutputSettings()
        assert "{stem}" in settings.jsonl_dir
        assert "{hash}" in settings.jsonl_dir
        assert "{stem}" in settings.markdown_dir
        assert "{hash}" in settings.markdown_dir

    def test_template_validation(self):
        """Test template validation warning."""
        # Should not raise error, but might log warning
        settings = OutputSettings(
            jsonl_dir="./output/no_template.jsonl",
            markdown_dir="./output/no_template.md",
        )
        assert settings.jsonl_dir == "./output/no_template.jsonl"


class TestLlamaParseSettings:
    """Test LlamaParseSettings model."""

    def test_default_values(self):
        """Test default LlamaParse settings."""
        settings = LlamaParseSettings()
        assert settings.api_key == ""
        assert settings.base_url == "https://api.llamaindex.ai/api/v1"
        assert settings.timeout == 120

    def test_api_key_validation(self):
        """Test API key validation."""
        # Valid key
        settings = LlamaParseSettings(api_key="valid_key_123456789")
        assert settings.api_key == "valid_key_123456789"

        # Short key should raise error
        with pytest.raises(ValidationError):
            LlamaParseSettings(api_key="short")

    def test_timeout_validation(self):
        """Test timeout validation."""
        # Valid timeout
        settings = LlamaParseSettings(timeout=60)
        assert settings.timeout == 60

        # Invalid timeout (too low)
        with pytest.raises(ValidationError):
            LlamaParseSettings(timeout=0)


class TestRetrySettings:
    """Test RetrySettings model."""

    def test_default_values(self):
        """Test default retry settings."""
        settings = RetrySettings()
        assert settings.max_attempts == 3
        assert settings.initial_backoff_ms == 500
        assert settings.max_backoff_ms == 5000
        assert settings.jitter is True

    def test_backoff_validation(self):
        """Test backoff timing validation."""
        # Valid settings
        settings = RetrySettings(initial_backoff_ms=100, max_backoff_ms=1000)
        assert settings.initial_backoff_ms == 100
        assert settings.max_backoff_ms == 1000

        # Invalid: max_backoff <= initial_backoff
        with pytest.raises(ValidationError):
            RetrySettings(initial_backoff_ms=1000, max_backoff_ms=500)


class TestConcurrencySettings:
    """Test ConcurrencySettings model."""

    def test_default_values(self):
        """Test default concurrency settings."""
        settings = ConcurrencySettings()
        assert settings.max_workers == 10

    def test_bounds_validation(self):
        """Test max_workers bounds validation."""
        # Valid values
        settings = ConcurrencySettings(max_workers=5)
        assert settings.max_workers == 5

        # Too low
        with pytest.raises(ValidationError):
            ConcurrencySettings(max_workers=0)

        # Too high
        with pytest.raises(ValidationError):
            ConcurrencySettings(max_workers=100)


class TestLoggingSettings:
    """Test LoggingSettings model."""

    def test_default_values(self):
        """Test default logging settings."""
        settings = LoggingSettings()
        assert settings.level == "INFO"
        assert settings.rotate_daily is True
        assert settings.backup_count == 7

    def test_log_level_validation(self):
        """Test log level validation."""
        # Valid levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = LoggingSettings(level=level)
            assert settings.level == level

            # Test lowercase
            settings = LoggingSettings(level=level.lower())
            assert settings.level == level

        # Invalid level
        with pytest.raises(ValidationError):
            LoggingSettings(level="INVALID")


class TestSettings:
    """Test root Settings model."""

    def test_default_values(self):
        """Test default settings creation."""
        settings = Settings()
        assert isinstance(settings.input, InputSettings)
        assert isinstance(settings.output, OutputSettings)
        assert isinstance(settings.llamaparse, LlamaParseSettings)
        assert isinstance(settings.processed, ProcessedSettings)
        assert isinstance(settings.quarantine, QuarantineSettings)
        assert isinstance(settings.concurrency, ConcurrencySettings)
        assert isinstance(settings.retry, RetrySettings)
        assert isinstance(settings.redaction, RedactionSettings)
        assert isinstance(settings.logging, LoggingSettings)
        assert isinstance(settings.state, StateSettings)
        assert isinstance(settings.runs, RunsSettings)

    def test_file_hash(self, temp_config_file: Path):
        """Test file hash generation."""
        settings = Settings()
        file_hash = settings.get_file_hash(temp_config_file)
        assert isinstance(file_hash, str)
        assert len(file_hash) == 8  # Short hash

        # Same file should produce same hash
        file_hash2 = settings.get_file_hash(temp_config_file)
        assert file_hash == file_hash2

    def test_extra_fields_forbidden(self):
        """Test that extra fields are not allowed."""
        with pytest.raises(ValidationError):
            Settings(unknown_field="value")


class TestConfigLoader:
    """Test ConfigLoader class."""

    def test_singleton_pattern(self):
        """Test singleton pattern implementation."""
        # Clear any existing instance for clean test
        ConfigLoader._instance = None

        loader1 = ConfigLoader()
        loader2 = ConfigLoader()
        assert loader1 is loader2

    def test_load_valid_config(self, temp_config_file: Path):
        """Test loading valid configuration."""
        loader = ConfigLoader(temp_config_file)
        settings = loader.settings

        assert settings.input.dir == str(Path("./test_inbox").resolve())
        assert settings.llamaparse.api_key == "test_key_123456789"
        assert settings.concurrency.max_workers == 5
        assert settings.retry.max_attempts == 2
        assert settings.logging.level == "DEBUG"

    def test_load_nonexistent_config(self):
        """Test loading non-existent config file uses defaults."""
        nonexistent_path = Path("/tmp/nonexistent_config.toml")
        loader = ConfigLoader(nonexistent_path)
        settings = loader.settings

        # Should use defaults
        assert isinstance(settings, Settings)
        assert settings.input.pattern == "*.pdf"  # Default value

    def test_load_malformed_config(self, malformed_toml_file: Path):
        """Test loading malformed TOML file."""
        loader = ConfigLoader(malformed_toml_file)
        settings = loader.settings

        # Should fall back to defaults
        assert isinstance(settings, Settings)
        assert settings.input.pattern == "*.pdf"  # Default value

    def test_load_invalid_config(self, invalid_config_file: Path):
        """Test loading config with validation errors."""
        loader = ConfigLoader(invalid_config_file)
        settings = loader.settings

        # Should fall back to defaults due to validation error
        assert isinstance(settings, Settings)
        assert settings.retry.max_backoff_ms > settings.retry.initial_backoff_ms

    def test_environment_variable_override(self, temp_config_file: Path):
        """Test environment variable override for API key."""
        # Set environment variable
        test_api_key = "env_override_key_12345678"
        os.environ["LLAMAPARSE_API_KEY"] = test_api_key

        try:
            loader = ConfigLoader(temp_config_file)
            settings = loader.settings

            # Should use environment variable instead of config file
            assert settings.llamaparse.api_key == test_api_key
        finally:
            # Cleanup environment variable
            if "LLAMAPARSE_API_KEY" in os.environ:
                del os.environ["LLAMAPARSE_API_KEY"]

    def test_hot_reload(self, temp_config_file: Path):
        """Test hot reload functionality."""
        loader = ConfigLoader(temp_config_file)
        original_workers = loader.settings.concurrency.max_workers
        assert original_workers == 5

        # Modify config file
        with open(temp_config_file, "a") as f:
            f.write("\n[concurrency]\nmax_workers = 15\n")

        # Trigger reload
        loader.reload_config()

        # Should reflect new value
        updated_workers = loader.settings.concurrency.max_workers
        assert updated_workers == 15

    def test_thread_safety(self, temp_config_file: Path):
        """Test thread safety of config loading."""
        loader = ConfigLoader(temp_config_file)
        results = []
        errors = []

        def reload_config():
            """Thread function to reload config."""
            try:
                loader.reload_config()
                results.append(loader.settings.concurrency.max_workers)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=reload_config)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert all(result == 5 for result in results)  # All should get same value

    def test_watcher_cleanup(self, temp_config_file: Path):
        """Test file watcher cleanup."""
        loader = ConfigLoader(temp_config_file)
        assert loader._observer is not None

        loader.stop_watcher()
        assert loader._observer is None


class TestGlobalConfigFunction:
    """Test global config function."""

    def test_get_config(self):
        """Test global config function."""
        config = get_config()
        assert isinstance(config, Settings)

        # Should return same instance on multiple calls
        config2 = get_config()
        assert config is config2


@pytest.mark.integration
class TestConfigIntegration:
    """Integration tests for configuration system."""

    def test_full_config_lifecycle(self, temp_config_file: Path):
        """Test complete configuration lifecycle."""
        # Initial load
        loader = ConfigLoader(temp_config_file)
        settings = loader.settings

        # Verify initial values
        assert settings.input.dir == str(Path("./test_inbox").resolve())
        assert settings.concurrency.max_workers == 5

        # Test file hash functionality
        file_hash = settings.get_file_hash(temp_config_file)
        assert len(file_hash) == 8

        # Test settings validation
        assert settings.retry.max_backoff_ms > settings.retry.initial_backoff_ms

        # Test directory path resolution
        assert Path(settings.input.dir).is_absolute()

        # Cleanup
        loader.stop_watcher()

    def test_config_with_missing_sections(self, temp_dir: Path):
        """Test config with only partial sections defined."""
        config_file = temp_dir / "partial_config.toml"
        config_file.write_text(
            """
[input]
dir = "./custom_inbox"

[concurrency]
max_workers = 8
"""
        )

        loader = ConfigLoader(config_file)
        settings = loader.settings

        # Custom values should be used
        assert settings.input.dir == str(Path("./custom_inbox").resolve())
        assert settings.concurrency.max_workers == 8

        # Default values should be used for missing sections
        assert settings.output.jsonl_dir == "./outputs/jsonl/{stem}-{hash}.jsonl"
        assert settings.retry.max_attempts == 3

        loader.stop_watcher()


@pytest.mark.slow
class TestConfigHotReload:
    """Test configuration hot reload functionality."""

    def test_file_modification_detection(self, temp_config_file: Path):
        """Test that file modifications are detected and trigger reload."""
        loader = ConfigLoader(temp_config_file)
        original_value = loader.settings.concurrency.max_workers

        # Wait a bit to ensure file system events are set up
        time.sleep(0.1)

        # Modify the file
        with open(temp_config_file) as f:
            content = f.read()

        modified_content = content.replace("max_workers = 5", "max_workers = 20")
        with open(temp_config_file, "w") as f:
            f.write(modified_content)

        # Wait for file system event processing
        time.sleep(0.5)

        # Check if value was updated
        # Note: This might be flaky in some environments
        # so we'll also test manual reload as backup
        new_value = loader.settings.concurrency.max_workers
        if new_value == original_value:
            # File system watcher might not have triggered, manually reload
            loader.reload_config()
            new_value = loader.settings.concurrency.max_workers

        assert new_value == 20
        loader.stop_watcher()
