"""
FAISS vector store for document retrieval
"""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import yaml

from src.rag.embeddings import get_embedding_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

class VectorStore:
    """FAISS-based vector store for semantic search"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize vector store
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.config = config['rag']
        self.store_path = Path(self.config['vector_store_path'])
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        self.embedding_client = get_embedding_client(config_path)
        
        self.index: Optional[faiss.Index] = None
        self.documents: List[Dict] = []  # List of document metadata
        self.dimension: Optional[int] = None
        
        # Try to load existing index
        if (self.store_path / "default.index").exists():
            self.load("default")
        else:
            logger.info("No existing vector store index found. Starting empty.")

        logger.info("Initialized VectorStore")
    
    def create_index(self, dimension: int):
        """
        Create a new FAISS index
        
        Args:
            dimension: Embedding dimension
        """
        self.dimension = dimension
        # Using IndexFlatL2 for exact search (good for < 1M vectors)
        # For larger datasets, consider IndexIVFFlat
        self.index = faiss.IndexFlatL2(dimension)
        logger.info(f"Created FAISS index with dimension {dimension}")
    
    def add_documents(self, documents: List[Dict]):
        """
        Add documents to the vector store
        
        Args:
            documents: List of document dictionaries with 'text', 'metadata' keys
        """
        if not documents:
            return
        
        import time
        
        # Process in batches to handle rate limits and memory better
        # Free tier is very limited, so we use small batches and delays
        batch_size = 10
        total_docs = len(documents)
        
        logger.info(f"Adding {total_docs} documents in batches of {batch_size}...")
        
        for i in range(0, total_docs, batch_size):
            batch = documents[i:i+batch_size]
            batch_texts = [doc['text'] for doc in batch]
            
            try:
                # Generate embeddings for batch
                # The embedding client now has retry logic for rate limits
                embeddings = self.embedding_client.embed_batch(batch_texts)
                
                # Create index if it doesn't exist
                if self.index is None:
                    self.create_index(len(embeddings[0]))
                
                # Add to FAISS index
                vectors = np.array(embeddings).astype('float32')
                self.index.add(vectors)
                
                # Store document metadata
                self.documents.extend(batch)
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(total_docs + batch_size - 1)//batch_size} ({min(i+batch_size, total_docs)}/{total_docs})")
                
                # Conservative delay to avoid per-minute limits
                time.sleep(2)
                
                
            except Exception as e:
                logger.error(f"Error processing batch starting at index {i}: {e}")
                # We save what we have so far
                if self.index is not None:
                     self.save("partial_backup")
                raise

        logger.info(f"Successfully added all documents. Total in store: {len(self.documents)}")
    
    def search(
        self,
        query: str,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[Tuple[Dict, float]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of (document, similarity_score) tuples
        """
        if self.index is None:
            logger.warning("Vector store index is None")
            return []
            
        logger.info(f"Searching vector store with {self.index.ntotal} documents")
            
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty (ntotal=0)")
            return []
        
        top_k = top_k or self.config['top_k']
        similarity_threshold = similarity_threshold or self.config.get('similarity_threshold', 0.0)
        
        # Generate query embedding
        query_embedding = self.embedding_client.embed_query(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_vector, top_k)
        
        # Convert distances to similarity scores (lower distance = higher similarity)
        # For L2 distance, we can use negative distance as score
        results = []
        
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):
                # Convert L2 distance to similarity score (0-1 range)
                # Using exponential decay: similarity = exp(-distance)
                similarity = np.exp(-dist)
                
                if similarity >= similarity_threshold:
                    results.append((self.documents[idx], float(similarity)))
        
        return results
    
    def save(self, name: str = "default"):
        """
        Save vector store to disk
        
        Args:
            name: Name for the saved store
        """
        if self.index is None:
            logger.warning("No index to save")
            return
        
        index_path = self.store_path / f"{name}.index"
        metadata_path = self.store_path / f"{name}.pkl"
        
        # Save FAISS index
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'dimension': self.dimension,
            }, f)
        
        logger.info(f"Saved vector store to {self.store_path}")
    
    def load(self, name: str = "default") -> bool:
        """
        Load vector store from disk
        
        Args:
            name: Name of the saved store
            
        Returns:
            True if loaded successfully, False otherwise
        """
        index_path = self.store_path / f"{name}.index"
        metadata_path = self.store_path / f"{name}.pkl"
        
        if not index_path.exists() or not metadata_path.exists():
            logger.warning(f"Vector store '{name}' not found")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_path))
            
            # Load metadata
            with open(metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.dimension = data['dimension']
            
            logger.info(f"Loaded vector store with {len(self.documents)} documents")
            return True
        
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            'num_documents': len(self.documents),
            'dimension': self.dimension,
            'index_size': self.index.ntotal if self.index else 0,
        }

# Global vector store instance
_vector_store: Optional[VectorStore] = None

def get_vector_store(config_path: str = "config.yaml") -> VectorStore:
    """
    Get or create vector store singleton
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        VectorStore instance
    """
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStore(config_path)
    
    return _vector_store
