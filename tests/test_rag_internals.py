import pytest
from pathlib import Path
from src.rag.knowledge_base import load_knowledge_base

from src.rag.embeddings import EmbeddingClient, get_embedding_client
from unittest.mock import MagicMock, patch

def test_knowledge_base_loading(mocker):
    mocker.patch("src.rag.knowledge_base.get_vector_store")
    # Mock glob to simulate files
    mocker.patch("pathlib.Path.glob", return_value=[MagicMock()])
    mocker.patch("builtins.open", mocker.mock_open(read_data="test content"))
    
    kb = load_knowledge_base("config.yaml")
    assert kb is not None

def test_pdf_extraction(mocker):
    from src.rag.knowledge_base import extract_text_from_pdf
    mock_pdf = mocker.patch("pypdf.PdfReader")
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Page text"
    mock_pdf.return_value.pages = [mock_page]
    
    text = extract_text_from_pdf(Path("dummy.pdf"))
    assert "Page text" in text

def test_process_document(mocker):
    from src.rag.knowledge_base import process_document
    mocker.patch("src.rag.knowledge_base.extract_text_from_pdf", return_value="Some text content")
    mocker.patch("src.rag.knowledge_base.chunk_text", return_value=[("chunk1", 0)])
    
    docs = process_document(Path("test.pdf"))
    assert len(docs) == 1
    assert docs[0]["text"] == "chunk1"
    assert docs[0]["metadata"]["source"] == "test.pdf"

def test_embedding_client_gemini(mocker):
    # Mock genai Client
    mock_genai = mocker.patch("src.rag.embeddings.genai.Client")
    mocker.patch("yaml.safe_load", return_value={"embeddings": {"provider": "gemini", "model": "m", "chunk_size": 1, "chunk_overlap": 0}})
    
    client = EmbeddingClient("config.yaml")
    mock_genai.return_value.models.embed_content.return_value.embeddings = [MagicMock(values=[0.1, 0.2])]
    
    emb = client.embed_query("test")
    assert len(emb) == 2

def test_embedding_client(mocker):
    # Mock genai Client
    mock_genai = mocker.patch("src.rag.embeddings.genai.Client")
    # Mock OpenAI Client
    mock_openai = mocker.patch("openai.OpenAI")
    
    client = EmbeddingClient("config.yaml")
    
    if client.provider == 'openai':
        mock_openai.return_value.embeddings.create.return_value.data = [MagicMock(embedding=[0.1, 0.2])]
    else:
        mock_genai.return_value.models.embed_content.return_value.embeddings = [MagicMock(values=[0.1, 0.2])]
    
    emb = client.embed_query("test")
    assert len(emb) == 2

    
    # Batch
    if client.provider == 'openai':
        mock_openai.return_value.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1, 0.2]),
            MagicMock(embedding=[0.3, 0.4])
        ]
    
    embs = client.embed_batch(["test1", "test2"])
    assert len(embs) == 2
