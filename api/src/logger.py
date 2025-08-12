"""Ultra-strong logging configuration for Nightcrawler API."""

import sys
from pathlib import Path

from loguru import logger

from settings import settings


def setup_logging(
    log_level: str = "INFO",
    log_file: str | None = None,
    enable_json: bool = False,
) -> None:
    """Configure loguru logging with multiple outputs and formats.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        enable_json: Enable JSON structured logging
        enable_cloudwatch: Enable CloudWatch logging (future)
        cloudwatch_group: CloudWatch log group name
        cloudwatch_stream: CloudWatch log stream name
    """
    # Remove default handler
    logger.remove()

    # Console handler with colors
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    if enable_json:
        # JSON format for production
        console_format = "{time} | {level} | {name}:{function}:{line} | {message}"
        logger.add(
            sys.stderr,
            format=console_format,
            level=log_level,
            serialize=True,  # JSON output
            backtrace=True,
            diagnose=True,
        )
    else:
        # Human-readable format for development
        logger.add(
            sys.stderr,
            format=console_format,
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )

        logger.add(
            log_file,
            format=file_format,
            level=log_level,
            rotation="5 MB",  # Rotate when file reaches 10MB
            retention="7 days",  # Keep logs for 30 days
            compression="zip",  # Compress old logs
            serialize=enable_json,
            backtrace=True,
            diagnose=True,
        )

    # Add context information
    logger.configure(
        extra={
            "app": "nightcrawler-api",
            "environment": "development" if settings.debug else "production",
        }
    )


def get_logger(name: str) -> logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logger.bind(name=name)


# Configure logging on module import
def configure_default_logging():
    """Configure default logging based on settings."""
    log_level = "DEBUG" if settings.debug else "INFO"
    log_file = f"logs/nightcrawler-{settings.environment}.log"
    enable_json = settings.environment == "production"

    setup_logging(
        log_level=log_level,
        log_file=log_file,
        enable_json=enable_json,
    )


# Auto-configure on import
configure_default_logging()

# Export the main logger
__all__ = ["logger", "get_logger", "setup_logging"]
