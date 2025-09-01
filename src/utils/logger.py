import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from pythonjsonlogger import jsonlogger

from . import config


class JobNameFilter(logging.Filter):
    """Custom logging filter to inject job name into log records."""

    def __init__(self, job_name):
        super().__init__()
        self.job_name = job_name

    def filter(self, record):
        record.job_name = self.job_name
        return True


def json_setup_logger(job_name: str, log_name: str = config.LOG_FILE_NAME, log_dir: str = config.LOG_DIR):
    # Ensure the 'logs' directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Create a logger
    logger = logging.getLogger(log_name)
    logger.setLevel(config.LOGGING_LEVEL)  # Use the logging level from config

    # Create a file handler with TimedRotatingFileHandler
    handler = TimedRotatingFileHandler(
        filename=Path(log_dir) / f'{log_name}.log',
        when='midnight',
        interval=1,
        backupCount=7
    )

    # Set JSON log format
    json_format = jsonlogger.JsonFormatter(
        '%(asctime)s %(job_name)s %(name)s %(levelname)s %(message)s %(filename)s %(lineno)d'
    )
    handler.setFormatter(json_format)

    # Add job name filter
    logger.addFilter(JobNameFilter(job_name))

    # Add the handler to logger
    logger.addHandler(handler)

    # Optionally add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_format)
    console_handler.setLevel(config.LOGGING_LEVEL)
    logger.addHandler(console_handler)

    return logger


def setup_logger(job_name: str, log_name: str = config.LOG_FILE_NAME, log_dir: str = config.LOG_DIR):
    # Ensure the 'logs' directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Create a logger
    logger = logging.getLogger(log_name)
    logger.setLevel(config.LOGGING_LEVEL)

    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = Path(f"{log_dir}/{log_name}_{timestamp}.log")

    # Create a file handler with TimedRotatingFileHandler
    handler = TimedRotatingFileHandler(
        filename=Path(log_dir) / f'{log_name}.log',
        when='midnight',
        interval=1,
        backupCount=7
    )

    # Set the log format, including the job_name placeholder
    formatter = logging.Formatter(
        '%(asctime)s - %(job_name)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger.addFilter(JobNameFilter(job_name))

    # Add the handler to logger
    logger.addHandler(handler)

    # Optionally add console handler as well
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(config.LOGGING_LEVEL)
    logger.addHandler(console_handler)

    return logger
