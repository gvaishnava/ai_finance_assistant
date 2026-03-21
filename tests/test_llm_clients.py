import pytest
from src.core.llm import GeminiClient, FallbackLLMClient, get_llm_client
from src.core.openai_client import OpenAIClient
from unittest.mock import MagicMock, AsyncMock, patch
import yaml

@pytest.fixture
def real_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

class MockResponse:
    def __init__(self, text):
        self.text = text

def test_gemini_client(mocker, real_config):
    mocker.patch("os.getenv", return_value="dummy_key")
    mocker.patch("src.core.llm.genai.Client")
    
    client = GeminiClient(real_config)
    
    # Mock generation
    client.client.models.generate_content.return_value = MockResponse("Gemini Response")
    res = client.generate("Hello")
    assert res == "Gemini Response"
    
    res = client.generate_with_context("Hello", ["Context 1"])
    assert "Gemini Response" in res

@pytest.mark.asyncio
async def test_gemini_client_async(mocker, real_config):
    mocker.patch("os.getenv", return_value="dummy_key")
    mocker.patch("src.core.llm.genai.Client")
    
    client = GeminiClient(real_config)
    
    client.client.models.generate_content.return_value = MockResponse("Async Gemini Response")
    
    res = await client.agenerate("Hello")
    assert res == "Async Gemini Response"

def test_openai_client(mocker, real_config):
    mocker.patch("os.getenv", return_value="dummy_key")
    mocker.patch("src.core.openai_client.OpenAI")
    
    client = OpenAIClient(real_config)
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "OpenAI Response"
    client.client.chat.completions.create.return_value = mock_response
    
    res = client.generate("Hello")
    assert res == "OpenAI Response"
    
    res = client.generate_with_context("Hello", ["Context"])
    assert "OpenAI" in res

@pytest.mark.asyncio
async def test_openai_client_async(mocker, real_config):
    mocker.patch("os.getenv", return_value="dummy_key")
    mocker.patch("src.core.openai_client.OpenAI")
    
    client = OpenAIClient(real_config)
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Async OpenAI Response"
    client.client.chat.completions.create.return_value = mock_response
    
    res = await client.agenerate("Hello")
    assert res == "Async OpenAI Response"

@pytest.mark.asyncio
async def test_fallback_client():
    mock_primary = MagicMock()
    mock_primary.generate.side_effect = Exception("Primary failed")
    mock_primary.generate_with_context.side_effect = Exception("Primary failed")
    
    mock_fallback = MagicMock()
    mock_fallback.generate.return_value = "Fallback Response"
    mock_fallback.generate_with_context.return_value = "Fallback Context"
    
    client = FallbackLLMClient(mock_primary, mock_fallback)
    
    res = client.generate("Hello")
    assert res == "Fallback Response"
    
    res = client.generate_with_context("Hello", ["Ctx"])
    assert res == "Fallback Context"
    
    mock_primary.agenerate = AsyncMock(side_effect=Exception("Primary failed"))
    mock_primary.agenerate_with_context = AsyncMock(side_effect=Exception("Primary failed"))
    mock_fallback.agenerate = AsyncMock(return_value="Fallback Async")
    mock_fallback.agenerate_with_context = AsyncMock(return_value="Fallback Async Context")
    
    res = await client.agenerate("Hello")
    assert res == "Fallback Async"
    
    res = await client.agenerate_with_context("Hello", ["Ctx"])
    assert res == "Fallback Async Context"

def test_get_llm_client(mocker):
    # Test singleton returning logic
    mocker.patch("os.getenv", return_value="dummy_key")
    
    # Needs to ensure internal clients don't crash without real imports if configured
    import src.core.llm as llm
    llm._llm_client = None
    
    # This might actually load FallbackLLMClient because fallback_provider is now configured
    client = get_llm_client("config.yaml")
    assert client is not None
