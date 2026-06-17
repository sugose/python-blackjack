"""Structured event logger for blackjack game events."""

import logging

_logger = logging.getLogger("blackjack")


def log_event(tag: str, message: str) -> None:
    """Log a tagged event at INFO level in the format '[TAG] message'."""
    _logger.info("[%s] %s", tag, message)
