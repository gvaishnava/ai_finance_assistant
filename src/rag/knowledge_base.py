"""
Knowledge base loader for Zerodha course materials
"""

import pypdf
from pathlib import Path
from typing import List, Dict
import yaml

from src.rag.embeddings import chunk_text
from src.rag.vector_store import get_vector_store
from src.utils.logger import get_logger

logger = get_logger(__name__)

def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text from a PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text
    """
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        text = ""
        
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text += f"\n\n[Page {page_num}]\n{page_text}"
        
        return text
    
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        return ""

def load_text_file(file_path: Path) -> str:
    """
    Load text from a text file
    
    Args:
        file_path: Path to text file
        
    Returns:
        File content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return ""

def process_document(
    file_path: Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Dict]:
    """
    Process a document into chunks with metadata
    
    Args:
        file_path: Path to document
        chunk_size: Chunk size in characters
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of document chunks with metadata
    """
    logger.info(f"Processing document: {file_path.name}")
    
    # Extract text based on file type
    if file_path.suffix.lower() == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_path.suffix.lower() in ['.txt', '.md']:
        text = load_text_file(file_path)
    else:
        logger.warning(f"Unsupported file type: {file_path.suffix}")
        return []
    
    if not text:
        logger.warning(f"No text extracted from {file_path.name}")
        return []
    
    # Chunk the text
    chunks = chunk_text(text, chunk_size, chunk_overlap)
    
    # Create documents with metadata
    documents = []
    for i, (text_chunk, position) in enumerate(chunks):
        doc = {
            'text': text_chunk,
            'metadata': {
                'source': file_path.name,
                'file_path': str(file_path),
                'chunk_index': i,
                'position': position,
                'module': extract_module_name(file_path.name),
            }
        }
        documents.append(doc)
    
    logger.info(f"Created {len(documents)} chunks from {file_path.name}")
    return documents

def extract_module_name(filename: str) -> str:
    """
    Extract module name from filename
    
    Args:
        filename: Document filename
        
    Returns:
        Module name
    """
    # Remove extension
    name = filename.rsplit('.', 1)[0]
    
    # Extract module number and name
    if 'Module' in name:
        # Handle various formats like "Module 1", "Module1", etc.
        parts = name.split('_')
        for part in parts:
            if 'Module' in part:
                return part
    
    return name

def load_knowledge_base(config_path: str = "config.yaml") -> bool:
    """
    Load all documents from knowledge base into vector store
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Load configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        kb_path = Path(config['rag']['knowledge_base_path'])
        chunk_size = config['embeddings']['chunk_size']
        chunk_overlap = config['embeddings']['chunk_overlap']
        
        if not kb_path.exists():
            logger.error(f"Knowledge base path not found: {kb_path}")
            return False
        
        logger.info(f"Loading knowledge base from: {kb_path}")
        
        # Get vector store
        vector_store = get_vector_store(config_path)
        
        # Try to load existing index
        if vector_store.load():
            logger.info("Loaded existing vector store")
            return True
        
        # Process all documents
        all_documents = []
        
        # Process PDFs
        pdf_files = list(kb_path.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            docs = process_document(pdf_file, chunk_size, chunk_overlap)
            all_documents.extend(docs)
        
        # Process text files
        txt_files = list(kb_path.glob("*.txt"))
        logger.info(f"Found {len(txt_files)} text files")
        
        for txt_file in txt_files:
            docs = process_document(txt_file, chunk_size, chunk_overlap)
            all_documents.extend(docs)
        
        if not all_documents:
            logger.error("No documents were processed")
            return False
        
        logger.info(f"Total documents to index: {len(all_documents)}")
        
        # Add to vector store
        vector_store.add_documents(all_documents)
        
        # Save the index
        vector_store.save()
        
        logger.info("Knowledge base loaded successfully!")
        return True
    
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")
        return False
