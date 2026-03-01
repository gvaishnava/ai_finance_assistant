"""
Agent specialized in resolving company names to stock ticker symbols
"""

import json
import re
from typing import Dict, Optional, List

from src.agents.base_agent import BaseAgent
from src.utils.ticker_resolver import get_ticker_resolver
from src.utils.logger import get_logger
from src.utils.tracing import traceable, atraceable

logger = get_logger(__name__)

class TickerResolverAgent(BaseAgent):
    """Agent that resolves company names to tickers using search and LLM"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize ticker resolver agent"""
        super().__init__("ticker_resolver", config_path, use_rag=False)
        self.resolver = get_ticker_resolver()
        
    @traceable(name="ticker_resolver_agent_process", tags=["agent", "ticker_resolution"])
    def process(self, query: str, context: Optional[Dict] = None, **kwargs) -> Dict:
        """
        Resolve tickers for query (synchronous)
        
        Args:
            query: User query or company name
            context: Context dictionary
            
        Returns:
            Dictionary with resolved symbols in response and metadata
        """
        logger.info(f"TickerResolverAgent resolving: {query}")
        
        # 1. Try to get context from search if the query is a company name
        # We use the existing resolver to fetch search results
        search_context = ""
        if self.resolver.client:
            try:
                search_query = f"NSE and BSE stock symbol for {query} india"
                search_result = self.resolver.client.search(
                    query=search_query,
                    search_depth="basic",
                    max_results=3
                )
                results = search_result.get('results', [])
                search_context = "\n".join([f"Title: {r.get('title')}\nContent: {r.get('content')}" for r in results])
            except Exception as e:
                logger.error(f"Search failed in TickerResolverAgent: {e}")
        
        # 2. Build prompt for LLM
        prompt = f"""Identify the most accurate Yahoo Finance stock symbols (tickers) for the following company or instrument: "{query}"

Available Search Context:
{search_context}

Respond only with a JSON object: {{"symbols": ["TICKER1", "TICKER2"]}}
Prioritize Indian exchanges (.NS or .BO) for Indian companies.
Return an empty list if no clear ticker is found.
"""
        
        try:
            response_text = self.llm_client.generate(
                prompt,
                system_prompt=self.system_prompt,
                temperature=0.1
            )
            
            # Clean response for JSON parsing
            json_match = re.search(r'\{.*\}', response_text.replace('\n', ' '))
            if json_match:
                data = json.loads(json_match.group(0))
                symbols = data.get('symbols', [])
            else:
                symbols = []
                
            logger.info(f"TickerResolverAgent resolved symbols: {symbols}")
            
            return self.format_response(
                response_text=f"Resolved symbols: {', '.join(symbols) if symbols else 'None'}",
                metadata={'symbols': symbols, 'query': query}
            )
            
        except Exception as e:
            logger.error(f"Error in TickerResolverAgent logic: {e}")
            return self.format_response(
                response_text="Failed to resolve tickers",
                metadata={'symbols': [], 'error': str(e)}
            )

    @atraceable(name="ticker_resolver_agent_async_process", tags=["agent", "ticker_resolution", "async"])
    async def async_process(self, query: str, context: Optional[Dict] = None, **kwargs) -> Dict:
        """Resolve tickers for query (asynchronous)"""
        # For now, we reuse the sync process in an executor as per BaseAgent implementation
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.process(query, context, **kwargs))
