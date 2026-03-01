"""
News endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.agents.news_agent import NewsSynthesizerAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Initialize agent
news_agent = NewsSynthesizerAgent()

class NewsSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class NewsArticleModel(BaseModel):
    title: str
    url: str
    content: str
    score: float
    published_date: Optional[str] = None

class NewsSearchResponse(BaseModel):
    results: List[NewsArticleModel]

@router.post("/search", response_model=NewsSearchResponse)
async def search_news(request: NewsSearchRequest):
    """
    Search for financial news
    """
    try:
        results = news_agent.search_news(request.query, request.max_results)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))
