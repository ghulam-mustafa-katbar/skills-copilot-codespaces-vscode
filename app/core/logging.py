"""Logging setup for console and file outputs."""

from pathlib import Path
import sys

from loguru import logger


def configure_logging(log_level: str = "INFO") -> None:
    """Configure application logging sinks."""

    log_dir = Path("app/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(sys.stdout, level=log_level.upper(), colorize=True, backtrace=True, diagnose=False)
    logger.add(log_dir / "application.log", level=log_level.upper(), rotation="10 MB", retention="14 days")
    logger.add(log_dir / "errors.log", level="ERROR", rotation="10 MB", retention="30 days")
