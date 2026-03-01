"""
Utility to resolve company names to ticker symbols using Tavily Search
"""

import os
import re
from typing import Optional
from tavily import TavilyClient
from src.utils.logger import get_logger
from src.core.constants import TICKER_BLACKLIST

logger = get_logger(__name__)

class TickerResolver:
    """Resolves company names to stock tickers using web search"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the resolver
        
        Args:
            api_key: Tavily API key. If None, looks for TAVILY_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            logger.warning("TAVILY_API_KEY not found. Ticker resolution will be disabled.")
            self.client = None
        else:
            self.client = TavilyClient(api_key=self.api_key)
            
        self.cache = {}
        
    def resolve(self, query: str) -> Optional[str]:
        """
        Resolve a query (e.g., "Infosys") to a ticker (e.g., "INFY.NS")
        
        Args:
            query: Name of the company or a descriptive query
            
        Returns:
            The resolved ticker symbol or None if not found
        """
        if not self.client:
            return None
            
        if not query or query.upper() in TICKER_BLACKLIST:
            return None
            
        if query in self.cache:
            return self.cache[query]
            
        try:
            # Search for the ticker
            search_query = f"NSE and BSE stock symbol for {query} india"
            logger.info(f"Searching Tavily for ticker: {search_query}")
            
            search_result = self.client.search(
                query=search_query,
                search_depth="basic",
                max_results=5
            )
            
            # Extract text from results
            results = search_result.get('results', [])
            combined_text = " ".join([r.get('content', '') + " " + r.get('title', '') for r in results])
            
            # Look for Indian tickers (NAME.NS or NAME.BO) or clear identifiers
            patterns = [
                r'([A-Z0-9]+)\.NS',
                r'([A-Z0-9]+)\.BO',
                r'\(([A-Z0-9]+)\:NSE\)',
                r'\(([A-Z0-9]+)\:BSE\)',
                r'Ticker: ([A-Z]+)',
                r'Symbol: ([A-Z]+)',
                r'NSE:\s*([A-Z]+)',
                r'BSE:\s*([A-Z]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, combined_text, re.IGNORECASE)
                if match:
                    # Extract the symbol part (might be group 1 or group 0 depending on pattern)
                    found = match.group(1) if len(match.groups()) > 0 else match.group(0)
                    found = found.upper()
                    
                    # Sanitize and add suffix if not present
                    if '.' in found:
                        ticker = found
                    elif ':NSE' in match.group(0).upper() or 'NSE' in match.group(0).upper():
                        ticker = f"{found}.NS"
                    elif ':BSE' in match.group(0).upper() or 'BSE' in match.group(0).upper():
                        ticker = f"{found}.BO"
                    else:
                        ticker = f"{found}.NS" # Default to NSE
                        
                    logger.info(f"Resolved {query} to {ticker}")
                    self.cache[query] = ticker
                    return ticker
                    
            logger.warning(f"Could not resolve ticker for {query} from search results")
            return None
            
        except Exception as e:
            logger.error(f"Error resolving ticker for {query}: {e}")
            return None

# Global instance
_resolver = None

def get_ticker_resolver() -> TickerResolver:
    """Get the global TickerResolver instance"""
    global _resolver
    if _resolver is None:
        _resolver = TickerResolver()
    return _resolver
