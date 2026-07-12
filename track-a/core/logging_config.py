"""
Centralized logging configuration for Smart Academic OS.

Provides structured logging with proper formatting, log levels,
and optional file output. Import this at application startup.
"""

import logging
import os
import sys
from datetime import datetime


class _AcademicFormatter(logging.Formatter):
    """Custom formatter with color support and structured output."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_color: bool = True):
        super().__init__()
        self._use_color = use_color and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname.ljust(8)
        module = record.module.ljust(20)
        message = record.getMessage()

        if record.exc_info and record.exc_info[0]:
            exc_text = self.formatException(record.exc_info)
            message = f"{message}\n{exc_text}"

        if self._use_color and record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            return f"{color}{timestamp} [{level}]{self.RESET} {module} {message}"

        return f"{timestamp} [{level}] {module} {message}"


_configured = False


def setup_logging(
    level: str = "INFO",
    log_file: str = None,
    use_color: bool = True,
) -> None:
    """Configure application-wide logging.

    Parameters
    ----------
    level : str
        Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    log_file : str, optional
        If provided, also write logs to this file.
    use_color : bool
        Whether to use ANSI color codes in console output.
    """
    global _configured
    if _configured:
        return

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = _AcademicFormatter(use_color=use_color)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)-8s] %(module)-20s %(message)s")
        )
        root.addHandler(file_handler)

    _configured = True
    logging.getLogger(__name__).info("Logging initialized: level=%s", level)
