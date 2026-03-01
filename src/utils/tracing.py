"""
LangSmith tracing utilities for AI Finance Assistant.

Tracing is entirely opt-in — controlled by environment variables.
When LANGCHAIN_TRACING_V2 is not "true", all decorators are no-ops
and the application behaves identically to a non-traced build.

Required .env entries to enable tracing:
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
    LANGCHAIN_API_KEY=ls__xxxxxxxxxxxxxxxx
    LANGCHAIN_PROJECT=financial-ai-chatbot   # optional, falls back to config.yaml

Usage:
    from src.utils.tracing import traceable, atraceable

    @traceable(name="generate_response", tags=["llm"])
    def my_sync_fn(...):
        ...

    @atraceable(name="async_generate", tags=["llm"])
    async def my_async_fn(...):
        ...
"""

import os
import functools
import asyncio
from typing import Callable, Optional, Any

from src.utils.logger import get_logger

logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Initialisation
# ──────────────────────────────────────────────────────────────────────────────

_tracing_enabled: bool = False


def init_langsmith(project: Optional[str] = None) -> bool:
    """
    Initialise LangSmith tracing.

    Reads env vars set by the user and logs whether tracing is active.
    Returns True if tracing is successfully enabled.

    Args:
        project: LangSmith project name (falls back to LANGCHAIN_PROJECT
                 env var, then the value passed from config.yaml).
    """
    global _tracing_enabled

    enabled = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"

    if not enabled:
        logger.info("LangSmith tracing is DISABLED (LANGCHAIN_TRACING_V2 != true)")
        _tracing_enabled = False
        return False

    api_key = os.getenv("LANGCHAIN_API_KEY", "")
    if not api_key:
        logger.warning(
            "LangSmith tracing requested but LANGCHAIN_API_KEY is not set — tracing disabled."
        )
        _tracing_enabled = False
        return False

    # Allow project to be set via env var or caller
    effective_project = (
        os.getenv("LANGCHAIN_PROJECT")
        or project
        or "financial-ai-chatbot"
    )

    # Set env var so langsmith SDK picks it up automatically
    os.environ["LANGCHAIN_PROJECT"] = effective_project

    try:
        # Lightweight import check — langsmith >= 0.1 exposes this module
        import langsmith  # noqa: F401
        _tracing_enabled = True
        logger.info(
            f"LangSmith tracing ENABLED — project='{effective_project}', "
            f"endpoint={os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')}"
        )
        return True
    except ImportError:
        logger.warning(
            "langsmith package not installed. Run: pip install langsmith>=0.1.0 — tracing disabled."
        )
        _tracing_enabled = False
        return False


def is_tracing_enabled() -> bool:
    """Return True if LangSmith tracing was successfully initialised."""
    return _tracing_enabled


# ──────────────────────────────────────────────────────────────────────────────
# Decorators
# ──────────────────────────────────────────────────────────────────────────────

def traceable(
    name: Optional[str] = None,
    tags: Optional[list] = None,
    metadata: Optional[dict] = None,
    run_type: str = "chain",
):
    """
    Decorator for **synchronous** functions.

    Wraps the function with a LangSmith trace span when tracing is enabled.
    Falls back to a no-op wrapper when disabled.

    Args:
        name:      Display name in LangSmith UI (defaults to function name).
        tags:      List of string tags (e.g. ["llm", "agent"]).
        metadata:  Extra key/value pairs attached to the run.
        run_type:  LangSmith run type — "chain", "llm", "tool", "retriever".
    """
    def decorator(fn: Callable) -> Callable:
        if not _tracing_enabled:
            return fn  # Pure no-op

        try:
            from langsmith import traceable as ls_traceable
            return ls_traceable(
                name=name or fn.__name__,
                tags=tags or [],
                metadata=metadata or {},
                run_type=run_type,
            )(fn)
        except Exception as exc:
            logger.debug(f"LangSmith traceable wrapping failed for {fn.__name__}: {exc}")
            return fn

    return decorator


def atraceable(
    name: Optional[str] = None,
    tags: Optional[list] = None,
    metadata: Optional[dict] = None,
    run_type: str = "chain",
):
    """
    Decorator for **asynchronous** functions.

    Same semantics as ``traceable`` but for ``async def`` functions.
    """
    def decorator(fn: Callable) -> Callable:
        if not _tracing_enabled:
            return fn  # Pure no-op

        try:
            from langsmith import traceable as ls_traceable
            # langsmith's @traceable supports async functions natively (>=0.1)
            return ls_traceable(
                name=name or fn.__name__,
                tags=tags or [],
                metadata=metadata or {},
                run_type=run_type,
            )(fn)
        except Exception as exc:
            logger.debug(f"LangSmith atraceable wrapping failed for {fn.__name__}: {exc}")
            return fn

    return decorator
