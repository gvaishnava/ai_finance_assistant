"""
Market data endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List

from src.web_app.models import StockQuote, MarketTrendsResponse
from src.data.market_data import get_market_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Initialize market client
market_client = get_market_client()

@router.get("/quote/{symbol}", response_model=StockQuote)
async def get_quote(symbol: str):
    """
    Get stock quote
    
    Args:
        symbol: Stock symbol (e.g., RELIANCE.NS)
        
    Returns:
        Stock quote data
    """
    try:
        quote = market_client.get_quote(symbol)
        
        if not quote:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        return StockQuote(**quote)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends", response_model=MarketTrendsResponse)
async def get_trends():
    """
    Get market trends (major indices)
    
    Returns:
        Market indices data
    """
    try:
        indices = market_client.get_market_indices()
        
        stock_quotes = [StockQuote(**index) for index in indices]
        
        return MarketTrendsResponse(indices=stock_quotes)
        
    except Exception as e:
        logger.error(f"Error fetching market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/{query}")
async def search_symbol(query: str):
    """
    Search for stock symbols
    
    Args:
        query: Search query
        
    Returns:
        List of matching stocks
    """
    try:
        results = market_client.search_symbol(query)
        return {"results": results}
        
    except Exception as e:
        logger.error(f"Error searching for {query}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
