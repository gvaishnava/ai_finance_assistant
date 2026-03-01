"""
Main application entry point for AI Finance Assistant
"""

import uvicorn
import yaml
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST (so tracing env vars are available)
load_dotenv()

from src.utils.logger import setup_logging, get_logger

# ── Logging: use config.yaml logging section ─────────────────────────────────
with open("config.yaml", "r") as _f:
    _boot_config = yaml.safe_load(_f)

setup_logging(_boot_config.get("logging", "INFO"))
logger = get_logger(__name__)


def initialize_app():
    """Initialize application (load knowledge base, configure tracing, etc.)"""
    logger.info("Initializing AI Finance Assistant...")

    # Load configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # ── Check for LLM API key ────────────────────────────────────────────────
    import os
    llm_config = config.get("llm", {})
    provider = llm_config.get("provider", "gemini")

    if provider in llm_config:
        api_key_env = llm_config[provider]["api_key_env"]
    elif "gemini" in config:  # Fallback to old structure
        api_key_env = config["gemini"]["api_key_env"]
    else:
        logger.error(f"Configuration error: Provider '{provider}' settings not found.")
        sys.exit(1)

    if not os.getenv(api_key_env):
        logger.error(f"API key not found! Please set {api_key_env} environment variable.")
        logger.error("You can create a .env file based on .env.example")
        sys.exit(1)

    # ── LangSmith Tracing (opt-in) ───────────────────────────────────────────
    from src.utils.tracing import init_langsmith
    langsmith_project = config.get("langsmith", {}).get("project", "financial-ai-chatbot")
    init_langsmith(project=langsmith_project)

    # ── Load knowledge base ──────────────────────────────────────────────────
    from src.rag.knowledge_base import load_knowledge_base
    logger.info("Loading knowledge base...")
    success = load_knowledge_base()

    if not success:
        logger.warning("Knowledge base not loaded. Some features may not work optimally.")
        logger.warning("You can initialize it later using: python scripts/init_knowledge_base.py")
    else:
        logger.info("Knowledge base loaded successfully!")

    logger.info("Initialization complete!")


def main():
    """Main entry point"""
    initialize_app()

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    host  = config["app"]["host"]
    port  = config["app"]["port"]
    debug = config["app"]["debug"]

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "src.web_app.api:app",
        host=host,
        port=port,
        reload=debug,
        reload_dirs=["src"] if debug else None,
        reload_includes=["config.yaml"] if debug else None,
        log_level="info",
    )


if __name__ == "__main__":
    main()
