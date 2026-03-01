"""
Embeddings using Google Gemini
"""


from google import genai
from google.genai import types
import os
from typing import List, Tuple
import yaml

from src.utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingClient:
    """Google Gemini embeddings client using google-genai SDK"""
    

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize embeddings client
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.config = config
        self.provider = config.get('embeddings', {}).get('provider', 'gemini')
        self.model_name = config['embeddings']['model']
        self.chunk_size = config['embeddings']['chunk_size']
        self.chunk_overlap = config['embeddings']['chunk_overlap']
        
        if self.provider == 'openai':
            from openai import OpenAI
            
            api_key_env = config.get('llm', {}).get('openai', {}).get('api_key_env', 'OPENAI_API_KEY')
            api_key = os.getenv(api_key_env)
            if not api_key:
                # Fallback to standard env var
                api_key = os.getenv("OPENAI_API_KEY")
                
            if not api_key:
                raise ValueError(f"OpenAI API key not found")
                
            self.client = OpenAI(api_key=api_key)
            logger.info(f"Initialized EmbeddingClient with OpenAI model: {self.model_name}")
            
        else:
            # Default to Gemini
            # Check new config structure first
            llm_config = config.get('llm', {})
            if 'gemini' in llm_config:
                api_key_env = llm_config['gemini']['api_key_env']
            elif 'gemini' in config:
                api_key_env = config['gemini']['api_key_env']
            else:
                # Fallback/Default
                api_key_env = "GEMINI_API_KEY"
                
            api_key = os.getenv(api_key_env)
            if not api_key:
                # Try fallback
                api_key = os.getenv("GOOGLE_API_KEY")
                
            if not api_key:
                raise ValueError(f"Google/Gemini API key not found")
            
            self.client = genai.Client(api_key=api_key)
            logger.info(f"Initialized EmbeddingClient with Gemini model: {self.model_name}")
    
    def embed_text(self, text: str, retries: int = 10) -> List[float]:
        """
        Generate embedding for text with retry logic
        
        Args:
            text: Text to embed
            retries: Number of retries on rate limit error
            
        Returns:
            Embedding vector
        """
        import time
        import random
        
        for attempt in range(retries):
            try:
                if self.provider == 'openai':
                    # OpenAI Embedding
                    text = text.replace("\n", " ")
                    response = self.client.embeddings.create(
                        input=[text],
                        model=self.model_name
                    )
                    return response.data[0].embedding
                else:
                    # Gemini Embedding
                    # https://ai.google.dev/api/embeddings#v1beta.models.embedContent
                    response = self.client.models.embed_content(
                        model=self.model_name,
                        contents=text,
                        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
                    )
                    return response.embeddings[0].values
                    
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    if attempt < retries - 1:
                        # Exponential backoff + jitter: 2, 4, 8, 16, 32... seconds + random
                        sleep_time = (2 ** attempt) + (random.random() * 1)
                        logger.warning(f"Rate limit hit. Retrying in {sleep_time:.2f}s (Attempt {attempt+1}/{retries})")
                        time.sleep(sleep_time)
                        continue
                logger.error(f"Error generating embedding: {e}")
                raise

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector
        """
        try:
            if self.provider == 'openai':
                # OpenAI Query Embedding (same as doc for OpenAI usually, just verifying model)
                query = query.replace("\n", " ")
                response = self.client.embeddings.create(
                    input=[query],
                    model=self.model_name
                )
                return response.data[0].embedding
            else:
                # Gemini Query Embedding
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=query,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
                )
                return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        # For OpenAI we can batch efficiently
        if self.provider == 'openai':
            try:
                # Standardize texts
                clean_texts = [t.replace("\n", " ") for t in texts]
                response = self.client.embeddings.create(
                    input=clean_texts,
                    model=self.model_name
                )
                # Sort by index to ensure order (OpenAI usually preserves, but good to be safe if strictly required, 
                # though response.data list usually matches input list order. 
                # We'll assume list order is preserved as per API guarantees)
                return [d.embedding for d in response.data]
            except Exception as e:
                logger.error(f"Error generating batch embeddings: {e}")
                raise
        else:
            # Gemini batching (existing logic or iterative)
            # Keeping iterative for safety/rate limits on free tier
            for i, text in enumerate(texts):
                try:
                    emb = self.embed_text(text)
                    embeddings.append(emb)
                except Exception as e:
                    logger.error(f"Failed to embed text at index {i}: {e}")
                    raise
            return embeddings

# Global client instance
_embedding_client = None

def get_embedding_client(config_path: str = "config.yaml") -> EmbeddingClient:
    """Get or create embedding client singleton"""
    global _embedding_client
    
    if _embedding_client is None:
        _embedding_client = EmbeddingClient(config_path)
    
    return _embedding_client

def get_embeddings(texts: List[str], config_path: str = "config.yaml") -> List[List[float]]:
    """
    Convenience function to get embeddings for texts
    
    Args:
        texts: List of texts to embed
        config_path: Path to configuration file
        
    Returns:
        List of embedding vectors
    """
    client = get_embedding_client(config_path)
    return client.embed_batch(texts)

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Tuple[str, int]]:
    """
    Split text into chunks with overlap
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Overlap between chunks in characters
        
    Returns:
        List of (chunk_text, start_position) tuples
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for last period, question mark, or exclamation point
            last_period = max(
                chunk.rfind('.'),
                chunk.rfind('?'),
                chunk.rfind('!'),
                chunk.rfind('\n\n')
            )
            
            if last_period > chunk_size // 2:  # Only if it's not too early
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1
        
        chunks.append((chunk.strip(), start))
        
        # Move start position with overlap
        start = end - overlap if end < len(text) else end
    
    return chunks
