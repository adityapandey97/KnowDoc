import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict

SENSITIVE_KEYS = {
    "authorization",
    "x-internal-service-key",
    "password",
    "token",
    "api_key",
    "openai_api_key",
    "secret"
}

def sanitize_data(data: Any, depth: int = 0) -> Any:
    if depth > 4 or data is None:
        return data
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if str(k).lower() in SENSITIVE_KEYS:
                cleaned[k] = "[REDACTED]"
            elif isinstance(v, (dict, list)):
                cleaned[k] = sanitize_data(v, depth + 1)
            else:
                cleaned[k] = v
        return cleaned
    if isinstance(data, list):
        return [sanitize_data(item, depth + 1) for item in data]
    return data

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "knowdoc-ai-service",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage()
        }
        if hasattr(record, "correlation_id"):
            log_obj["correlation_id"] = record.correlation_id
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_obj["data"] = sanitize_data(record.extra_data)
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def get_logger(name: str = "knowdoc.ai") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger

logger = get_logger("knowdoc.ai")
