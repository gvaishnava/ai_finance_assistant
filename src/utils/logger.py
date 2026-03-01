"""
Centralized logging configuration for AI Finance Assistant.

Features:
- Rotating file handler with JSON-structured output
- Color-coded console output (ANSI)
- ContextVar-based request context (session_id, agent_name) injected into every record
- Configurable via config.yaml `logging:` section or legacy keyword args
"""

import logging
import logging.handlers
import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from contextvars import ContextVar
from typing import Optional, Union

# ── Context variables (set these at the start of each request) ──────────────
log_context: ContextVar[dict] = ContextVar("log_context", default={})


def set_log_context(session_id: Optional[str] = None, agent_name: Optional[str] = None):
    """Inject request-level context into every subsequent log record."""
    ctx = {}
    if session_id:
        ctx["session_id"] = session_id
    if agent_name:
        ctx["agent_name"] = agent_name
    log_context.set(ctx)


def clear_log_context():
    """Reset log context (call at end of request)."""
    log_context.set({})


# ── Filters ─────────────────────────────────────────────────────────────────
class ContextFilter(logging.Filter):
    """Injects session_id / agent_name from ContextVar into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = log_context.get({})
        record.session_id = ctx.get("session_id", "-")
        record.agent_name = ctx.get("agent_name", "-")
        return True


# ── Formatters ───────────────────────────────────────────────────────────────
class JSONFormatter(logging.Formatter):
    """Emits one JSON object per log line — suitable for log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        # Optional context fields
        for field in ("session_id", "agent_name"):
            val = getattr(record, field, None)
            if val and val != "-":
                log_obj[field] = val

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj, ensure_ascii=False)


class ColorConsoleFormatter(logging.Formatter):
    """Human-readable, ANSI-color console formatter."""

    COLORS = {
        "DEBUG":    "\033[36m",   # Cyan
        "INFO":     "\033[32m",   # Green
        "WARNING":  "\033[33m",   # Yellow
        "ERROR":    "\033[31m",   # Red
        "CRITICAL": "\033[1;31m", # Bold Red
    }
    RESET = "\033[0m"

    FMT = "{color}[{{levelname:<8}}]{reset} {{asctime}} | {{name}} | {{message}}"
    DATE_FMT = "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        reset = self.RESET
        formatter = logging.Formatter(
            self.FMT.format(color=color, reset=reset),
            datefmt=self.DATE_FMT,
            style="{"
        )
        # Add context suffix if available
        formatted = formatter.format(record)
        ctx_parts = []
        if getattr(record, "session_id", "-") != "-":
            ctx_parts.append(f"session={record.session_id}")
        if getattr(record, "agent_name", "-") != "-":
            ctx_parts.append(f"agent={record.agent_name}")
        if ctx_parts:
            formatted += f"  [{', '.join(ctx_parts)}]"
        return formatted


# ── Public API ───────────────────────────────────────────────────────────────
def setup_logging(
    log_level: Union[str, dict] = "INFO",
    log_file: Optional[str] = None,
    *,
    max_bytes: int = 10 * 1024 * 1024,   # 10 MB
    backup_count: int = 5,
    json_file_logs: bool = True,
    color_console: bool = True,
):
    """
    Set up application-wide logging.

    Can be called two ways:

    1. Legacy (positional string args — keeps backward compatibility):
       ``setup_logging("INFO", "logs/app.log")``

    2. Config-dict-based (preferred):
       ``setup_logging(config["logging"])``
       where ``config["logging"]`` is a dict with keys:
       level, log_file, max_bytes, backup_count, json_file_logs, color_console.
    """
    # ── Unpack config dict if provided ──────────────────────────────────────
    if isinstance(log_level, dict):
        cfg = log_level
        log_level     = cfg.get("level",       "INFO")
        log_file      = cfg.get("log_file",    log_file)
        max_bytes     = cfg.get("max_bytes",   max_bytes)
        backup_count  = cfg.get("backup_count", backup_count)
        json_file_logs = cfg.get("json_file_logs", json_file_logs)
        color_console = cfg.get("color_console", color_console)

    numeric_level = getattr(logging, str(log_level).upper(), logging.INFO)

    context_filter = ContextFilter()

    # ── Console handler ──────────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.addFilter(context_filter)
    if color_console and sys.stdout.isatty():
        console_handler.setFormatter(ColorConsoleFormatter())
    else:
        # Plain format for non-TTY (CI, Docker logs, etc.)
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)-8s] %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )

    handlers: list[logging.Handler] = [console_handler]

    # ── Rotating file handler ────────────────────────────────────────────────
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.addFilter(context_filter)
        file_handler.setFormatter(JSONFormatter() if json_file_logs else logging.Formatter(
            "%(asctime)s [%(levelname)-8s] %(name)s | %(message)s | %(session_id)s | %(agent_name)s"
        ))
        handlers.append(file_handler)

    # ── Configure root logger ────────────────────────────────────────────────
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove any pre-existing handlers (avoid duplicate logs on reload)
    root_logger.handlers.clear()
    for h in handlers:
        root_logger.addHandler(h)

    # Silence noisy third-party loggers
    for noisy in ("httpcore", "httpx", "openai", "urllib3", "faiss"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        f"Logging initialized — level={log_level}, "
        f"file={'enabled (' + str(log_file) + ')' if log_file else 'disabled'}, "
        f"json={json_file_logs}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger.

    Args:
        name: Typically ``__name__``

    Returns:
        Logger instance (inherits root handlers set up by ``setup_logging``).
    """
    return logging.getLogger(name)
