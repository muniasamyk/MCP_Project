import logging
import sys
import json
from datetime import datetime, timezone
from app.core.config import settings

class JsonFormatter(logging.Formatter):
    """
    Simple JSON formatter for production logs.
    Example: {"timestamp": "...", "level": "INFO", "message": "..."}
    """
    def format(self, record):
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # Avoid adding duplicate handlers if get_logger is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)

        if settings.DEBUG:
            # Readable format for development
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        else:
            # Structured JSON for prod
            formatter = JsonFormatter()

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
