import logging
import json
from datetime import datetime
from .config import settings

def setup_logging():
    """Configure structured logging"""
    logger = logging.getLogger("mara")
    logger.setLevel(settings.log_level)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

logger = setup_logging()
