import html
import re
import os
from typing import Optional, List
from app.core.exceptions import CorruptDocumentError, ToolExecutionError

# Patterns indicative of prompt injection attempts attempting to override system behavior
INJECTION_OVERRIDE_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?instructions", re.IGNORECASE),
    re.compile(r"system\s*:\s*you\s+are", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"<\|im_end\|>", re.IGNORECASE),
]

def sanitize_untrusted_text(text: str) -> str:
    """
    Sanitizes untrusted text (like document passages) by escaping XML/HTML delimiters,
    preventing boundary breaking in grounded prompt frames.
    """
    if not text:
        return ""
    # Escape XML delimiters
    return html.escape(text, quote=True)

def sanitize_query(query: str, max_length: int = 4000) -> str:
    """
    Validates and normalizes user query string.
    """
    if not query or not query.strip():
        raise ToolExecutionError("Query cannot be empty.")
    
    cleaned = query.strip()
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    return cleaned

def validate_safe_storage_path(storage_path: str, allowed_base_dir: str = None) -> str:
    """
    Verifies that a file path does not contain path traversal attacks (..).
    """
    if not storage_path or not storage_path.strip():
        raise CorruptDocumentError("Storage path is required.")
    
    normalized = os.path.abspath(storage_path)
    if ".." in storage_path:
        raise CorruptDocumentError("Directory traversal detected in storage path.")
        
    return normalized
