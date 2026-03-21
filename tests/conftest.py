
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

import httpx

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
