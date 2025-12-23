"""Centralized logging configuration for ngx-renamer modules."""

import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Get a configured logger instance for ngx-renamer modules.

    Args:
        name: Name for the logger (typically the class name)
        level: Optional logging level (defaults to INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(f"ngx_renamer.{name}")

    if level is None:
        level = logging.INFO

    logger.setLevel(level)

    # Only add handler if none exists (avoid duplicates)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
