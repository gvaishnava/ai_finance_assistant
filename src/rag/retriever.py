"""
Retriever for RAG system
"""

from typing import List, Dict, Tuple
import yaml

from src.rag.vector_store import get_vector_store
from src.utils.logger import get_logger

logger = get_logger(__name__)

class Retriever:
    """Retrieves relevant context for user queries"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize retriever
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.config = config['rag']
        self.vector_store = get_vector_store(config_path)
        
        logger.info("Initialized Retriever")
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        filter_metadata: Dict = None
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of retrieved documents with metadata and scores
        """
        results = self.vector_store.search(query, top_k=top_k)
        
        retrieved_docs = []
        
        for doc, score in results:
            # Apply metadata filters if provided
            if filter_metadata:
                match = all(
                    doc.get('metadata', {}).get(k) == v
                    for k, v in filter_metadata.items()
                )
                if not match:
                    continue
            
            retrieved_docs.append({
                'text': doc['text'],
                'metadata': doc.get('metadata', {}),
                'score': score,
            })
        
        logger.debug(f"Retrieved {len(retrieved_docs)} documents for query: {query[:50]}...")
        
        return retrieved_docs
    
    def get_context(
        self,
        query: str,
        top_k: int = None,
        include_metadata: bool = True
    ) -> List[str]:
        """
        Get context strings for RAG
        
        Args:
            query: Search query
            top_k: Number of results
            include_metadata: Whether to include metadata in context
            
        Returns:
            List of context strings
        """
        docs = self.retrieve(query, top_k)
        
        contexts = []
        for doc in docs:
            if include_metadata and doc['metadata']:
                # Format with metadata
                metadata_str = ', '.join([
                    f"{k}: {v}" for k, v in doc['metadata'].items()
                ])
                context = f"[{metadata_str}]\n{doc['text']}"
            else:
                context = doc['text']
            
            contexts.append(context)
        
        return contexts
    
    def get_citations(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Get citations for retrieved documents
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of citation dictionaries
        """
        docs = self.retrieve(query, top_k)
        
        citations = []
        for i, doc in enumerate(docs, 1):
            metadata = doc.get('metadata', {})
            citation = {
                'index': i,
                'source': metadata.get('source', 'Unknown'),
                'page': metadata.get('page'),
                'module': metadata.get('module'),
                'score': doc['score'],
            }
            citations.append(citation)
        
        return citations
