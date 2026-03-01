
import pytest
from httpx import AsyncClient
# Connect to the FastAPI app
try:
    from src.web_app.api import app
except ImportError:
    # Fallback/Debug if path issues occur
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.web_app.api import app

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
