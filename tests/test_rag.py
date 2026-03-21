import pytest
from src.rag.embeddings import EmbeddingClient
from src.rag.vector_store import VectorStore
from src.rag.knowledge_base import load_knowledge_base
from src.rag.retriever import Retriever
from unittest.mock import MagicMock

def test_embedding_client(mocker):
    mocker.patch("src.rag.embeddings.genai.Client")
    
    config = {
        "embeddings": {"provider": "gemini", "model": "gemini", "chunk_size": 1000, "chunk_overlap": 200},
        "llm": {"gemini": {"api_key_env": "dummy"}}
    }
    def mock_yaml(f): return config
    mocker.patch("yaml.safe_load", side_effect=mock_yaml)
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("os.getenv", return_value="dummy")
    
    model = EmbeddingClient("config.yaml")
    
    class MockEmb:
        values = [1.0, 2.0]
    class MockResponse:
        embeddings = [MockEmb()]
    
    model.client.models.embed_content.return_value = MockResponse()
    
    emb = model.embed_text("Hello")
    assert emb == [1.0, 2.0]

def test_vector_store(mocker):
    import numpy as np
    mock_emb = mocker.patch("src.rag.vector_store.get_embedding_client").return_value
    mock_emb.embed_batch.return_value = [[1.0, 2.0]]
    mock_emb.embed_query.return_value = [1.0, 2.0]
    
    # Mock FAISS index directly
    mock_index = MagicMock()
    mock_index.ntotal = 1
    mock_index.search.return_value = (np.array([[0.1]]), np.array([[0]]))
    
    mocker.patch("faiss.IndexFlatL2", return_value=mock_index)
    mocker.patch("faiss.read_index", return_value=mock_index)
    
    vs = VectorStore("config.yaml")
    vs.index = mock_index
    vs.documents = [{"text": "Hello", "metadata": {}}]
    
    results = vs.search("Hello", top_k=1)
    assert len(results) == 1
    assert results[0][1] > 0
    
    # Test save/load coverage
    mocker.patch("faiss.write_index")
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("pickle.dump")
    vs.save("test")
    
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pickle.load", return_value={'documents': [], 'dimension': 2})
    vs.load("test")
    
def test_knowledge_base(mocker):
    mocker.patch("src.rag.knowledge_base.get_vector_store")
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("yaml.safe_load", return_value={'rag': {'knowledge_base_path': 'test'}, 'embeddings': {'chunk_size': 100, 'chunk_overlap': 10}})
    mocker.patch("builtins.open", mocker.mock_open())
    
    load_knowledge_base("config.yaml")
    
def test_retriever(mocker):
    mocker.patch("src.rag.retriever.get_vector_store")
    ret = Retriever("config.yaml")
    ret.retrieve("query", top_k=5)
