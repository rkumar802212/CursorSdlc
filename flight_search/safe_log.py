"""Safe logger: exception type/message only, never secrets or request bodies."""

from __future__ import annotations

import logging

logger = logging.getLogger("flight_search")


def configure_logging() -> None:
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def log_exception(kind: str, exc: BaseException) -> None:
    logger.exception("%s: %s: %s", kind, type(exc).__name__, str(exc))


def log_event(message: str) -> None:
    logger.info("%s", message)
