"""
Script to initialize the knowledge base (vector store) from Zerodha course materials
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.utils.logger import setup_logging, get_logger
from src.rag.knowledge_base import load_knowledge_base

# Setup logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)

def main():
    """Initialize knowledge base"""
    logger.info("=" * 60)
    logger.info("Initializing Knowledge Base")
    logger.info("=" * 60)
    
    logger.info("This will process all PDFs and text files from the Zerodha course")
    logger.info("and create a vector store for semantic search.")
    logger.info("")
    logger.info("This may take several minutes depending on the number of documents...")
    logger.info("")
    
    success = load_knowledge_base()
    
    if success:
        logger.info("=" * 60)
        logger.info("✓ Knowledge base initialized successfully!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("The vector store has been created and saved.")
        logger.info("You can now start the application with: python main.py")
    else:
        logger.error("=" * 60)
        logger.error("✗ Failed to initialize knowledge base")
        logger.error("=" * 60)
        logger.error("")
        logger.error("Please check the logs above for error details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
