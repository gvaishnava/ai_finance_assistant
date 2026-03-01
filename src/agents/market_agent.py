"""
Market Analysis Agent - Provides real-time market insights
"""

import asyncio
from typing import Dict, Optional, List
from src.agents.base_agent import BaseAgent
from src.data.market_data import get_market_client
from src.utils.formatters import format_currency, format_percentage
from src.utils.logger import get_logger
from src.utils.tracing import traceable, atraceable
from src.utils.visualizers import get_market_history_chart

logger = get_logger(__name__)


class MarketAgent(BaseAgent):
    """Agent for market analysis and trends"""
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(
            agent_name="market",
            config_path=config_path,
            use_rag=True  # Use RAG for educational context
        )
        self.market_client = get_market_client(config_path)
    
    @traceable(name="market_agent_process", tags=["agent", "market"])
    def process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Analyze market or specific stocks
        
        Args:
            query: User query about market/stocks
            context: Optional context
            **kwargs: Additional parameters (symbols list)
            
        Returns:
            Response dictionary with market insights
        """
        logger.info(f"Market Agent processing: {query[:50]}...")
        
        # Check if query is about specific stocks or general market
        symbols = kwargs.get('symbols', [])
        
        if not symbols:
            # Analyze general market
            return self._analyze_market_overview(query)
        else:
            # Analyze specific stocks
            return self._analyze_stocks(query, symbols)
    
    def _analyze_market_overview(self, query: str) -> Dict:
        """Analyze general market conditions"""
        
        # Get market indices
        indices = self.market_client.get_market_indices()
        
        if not indices:
            return self.format_response(
                "I'm having trouble fetching market data right now. Please try again later."
            )
        
        # Build market summary
        market_summary = "**Current Market Status:**\n\n"
        
        for index in indices:
            name = index.get('name', index['symbol'])
            price = index.get('price', 0)
            change_pct = index.get('change_percent', 0) / 100 if index.get('change_percent') else 0
            
            market_summary += f"- **{name}**: {format_currency(price)} ({format_percentage(change_pct)})\n"
        
        # Retrieve educational context
        edu_context = self.retrieve_context(
            "market trends stock market indices",
            top_k=3
        )
        
        # Generate insights
        prompt = f"""{market_summary}

User Query: {query}

Provide educational insights about:
1. What these market movements might indicate (in simple terms)
2. Key concepts for understanding market trends
3. How beginners should interpret this information

Focus on education, not predictions."""
        
        response = self.generate_response(prompt, edu_context)
        
        full_response = f"{market_summary}\n**Market Insights:**\n\n{response}"
        
        return self.format_response(
            self.add_disclaimer(full_response, "general"),
            metadata={'indices_count': len(indices), 'visualizations': [get_market_indices_chart(indices)]}
        )
    
    def _analyze_stocks(self, query: str, symbols: List[str]) -> Dict:
        """Analyze specific stocks"""
        
        stock_data = []
        stock_summary = "**Stock Information:**\n\n"
        
        for symbol in symbols[:5]:  # Limit to 5 stocks
            quote = self.market_client.get_quote(symbol)
            
            if quote:
                stock_data.append(quote)
                name = quote.get('name', symbol)
                price = quote.get('price', 0)
                change_pct = quote.get('change_percent', 0) / 100 if quote.get('change_percent') else 0
                volume = quote.get('volume', 0)
                sector = quote.get('sector', 'N/A')
                
                stock_summary += f"**{name}** ({symbol}):\n"
                stock_summary += f"- Price: {format_currency(price)} ({format_percentage(change_pct)})\n"
                stock_summary += f"- Sector: {sector}\n"
                if volume:
                    stock_summary += f"- Volume: {format_number(volume)}\n"
                stock_summary += "\n"
        
        if not stock_data:
            return self.format_response(
                f"I couldn't find market data for the specified symbols. Please check the symbols and try again."
            )
        
        # Retrieve educational context
        edu_context = self.retrieve_context(
            f"stock analysis fundamental analysis {' '.join([s.get('sector', '') for s in stock_data])}",
            top_k=3
        )
        
        # Generate insights
        prompt = f"""{stock_summary}

User Query: {query}

Provide educational insights about:
1. Key metrics to understand for these stocks
2. What the data tells us (educational perspective)
3. Concepts beginners should know when analyzing stocks

Focus on education about stock analysis, not buy/sell recommendations."""
        
        response = self.generate_response(prompt, edu_context)
        
        full_response = f"{stock_summary}**Educational Analysis:**\n\n{response}"
        
        return self.format_response(
            self.add_disclaimer(full_response, "general"),
            metadata={'stocks_analyzed': len(stock_data)}
        )

def format_number(value: float) -> str:
    """Format large numbers"""
    if value >= 10000000:
        return f"{value/10000000:.2f} Cr"
    elif value >= 100000:
        return f"{value/100000:.2f} L"
    else:
        return f"{value:,.0f}"


# Add async_process to MarketAgent via method injection (keeps class definition intact)
async def _market_async_process(
    self,
    query: str,
    context: Optional[Dict] = None,
    **kwargs,
) -> Dict:
    """Async version of process() — uses async LLM calls."""
    logger.info(f"Market Agent async processing: {query[:50]}...")
    symbols = kwargs.get('symbols', [])
    loop = asyncio.get_event_loop()

    if not symbols:
        # Fetch market indices in executor (yfinance is blocking)
        indices = await loop.run_in_executor(None, self.market_client.get_market_indices)
        if not indices:
            return self.format_response(
                "I'm having trouble fetching market data right now. Please try again later."
            )
        market_summary = "**Current Market Status:**\n\n"
        for index in indices:
            name = index.get('name', index['symbol'])
            price = index.get('price', 0)
            change_pct = index.get('change_percent', 0) / 100 if index.get('change_percent') else 0
            market_summary += f"- **{name}**: {format_currency(price)} ({format_percentage(change_pct)})\n"
        edu_context = self.retrieve_context("market trends stock market indices", top_k=3)
        prompt = f"""{market_summary}\n\nUser Query: {query}\n\nProvide educational insights about:\n1. What these market movements might indicate (in simple terms)\n2. Key concepts for understanding market trends\n3. How beginners should interpret this information\n\nFocus on education, not predictions."""
        response = await self.async_generate_response(prompt, edu_context)
        full_response = f"{market_summary}\n**Market Insights:**\n\n{response}"
        return self.format_response(
            self.add_disclaimer(full_response, "general"),
            metadata={'indices_count': len(indices), 'visualizations': [get_market_indices_chart(indices)]}
        )
    else:
        stock_data = []
        stock_summary = "**Stock Information:**\n\n"
        for symbol in symbols[:5]:
            quote = await loop.run_in_executor(None, lambda s=symbol: self.market_client.get_quote(s))
            if quote:
                stock_data.append(quote)
                name = quote.get('name', symbol)
                price = quote.get('price', 0)
                change_pct = quote.get('change_percent', 0) / 100 if quote.get('change_percent') else 0
                volume = quote.get('volume', 0)
                sector = quote.get('sector', 'N/A')
                stock_summary += f"**{name}** ({symbol}):\n"
                stock_summary += f"- Price: {format_currency(price)} ({format_percentage(change_pct)})\n"
                stock_summary += f"- Sector: {sector}\n"
                if volume:
                    stock_summary += f"- Volume: {format_number(volume)}\n"
                stock_summary += "\n"
        if not stock_data:
            return self.format_response(
                "I couldn't find market data for the specified symbols. Please check the symbols and try again."
            )
        edu_context = self.retrieve_context(
            f"stock analysis fundamental analysis {' '.join([s.get('sector', '') for s in stock_data])}",
            top_k=3,
        )
        prompt = f"""{stock_summary}\n\nUser Query: {query}\n\nProvide educational insights about:\n1. Key metrics to understand for these stocks\n2. What the data tells us (educational perspective)\n3. Concepts beginners should know when analyzing stocks\n\nFocus on education about stock analysis, not buy/sell recommendations."""
        response = await self.async_generate_response(prompt, edu_context)
        full_response = f"{stock_summary}**Educational Analysis:**\n\n{response}"
        
        # Prepare visualizations
        visualizations = []
        for stock in stock_data:
            hist_data = await loop.run_in_executor(
                None, 
                lambda s=stock['symbol']: self.market_client.get_historical_data(s, period="1mo")
            )
            if hist_data is not None and not hist_data.empty:
                chart = get_market_history_chart(hist_data, stock['symbol'])
                if chart:
                    visualizations.append(chart)

        return self.format_response(
            self.add_disclaimer(full_response, "general"),
            metadata={
                'stocks_analyzed': len(stock_data),
                'visualizations': visualizations
            }
        )


MarketAgent.async_process = _market_async_process

