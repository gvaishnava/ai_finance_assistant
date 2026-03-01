"""
Portfolio Analysis Agent - Reviews and analyzes user portfolios
"""

import asyncio
from typing import Dict, Optional
from src.agents.base_agent import BaseAgent
from src.data.portfolio import Portfolio
from src.utils.formatters import format_currency, format_percentage
from src.utils.logger import get_logger
from src.utils.tracing import traceable, atraceable
from src.utils.visualizers import get_portfolio_allocation_chart, get_sector_allocation_chart

logger = get_logger(__name__)


class PortfolioAgent(BaseAgent):
    """Agent for portfolio analysis and diversification"""
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(
            agent_name="portfolio",
            config_path=config_path,
            use_rag=True  # Use RAG for educational context
        )
    
    @traceable(name="portfolio_agent_process", tags=["agent", "portfolio"])
    def process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Analyze a portfolio
        
        Args:
            query: User query about their portfolio
            context: Context including portfolio data
            **kwargs: Additional parameters (portfolio dict)
            
        Returns:
            Response dictionary with analysis
        """
        logger.info("Portfolio Agent analyzing portfolio...")
        
        # Get portfolio from context or kwargs
        portfolio_data = kwargs.get('portfolio') or (context or {}).get('portfolio')
        
        if not portfolio_data:
            return self.format_response(
                "I'd be happy to analyze your portfolio! Please provide your holdings information (stock symbols and quantities).",
                metadata={'status': 'awaiting_portfolio'}
            )
        
        # Create Portfolio object
        portfolio = Portfolio.from_dict(portfolio_data) if isinstance(portfolio_data, dict) else portfolio_data
        
        # Get portfolio metrics
        allocations = portfolio.get_allocation()
        sector_allocation = portfolio.get_sector_allocation()
        pl_data = portfolio.get_profit_loss()
        
        # Build analysis summary
        analysis_text = self._build_analysis_text(allocations, sector_allocation, pl_data)
        
        # Retrieve educational context about diversification
        edu_context = self.retrieve_context(
            "portfolio diversification and asset allocation",
            top_k=3
        )
        
        # Generate educational insights
        prompt = f"""Based on this portfolio analysis, provide educational insights about diversification and risk:

{analysis_text}

User Query: {query}

Focus on:
1. Educational explanation of their current allocation
2. General principles of diversification
3. Concepts they should understand (sector risk, concentration risk, etc.)

Remember: Provide education, not specific investment advice."""
        
        response = self.generate_response(prompt, edu_context)
        
        # Add portfolio disclaimer
        response_with_disclaimer = self.add_disclaimer(response, "portfolio")
        
        # Combine analysis with educational response
        full_response = f"""**Portfolio Overview:**

{analysis_text}

**Educational Insights:**

{response_with_disclaimer}
"""
        
        # Prepare visualizations
        visualizations = []
        if allocations:
            visualizations.append(get_portfolio_allocation_chart(allocations))
        if sector_allocation:
            visualizations.append(get_sector_allocation_chart(sector_allocation))

        return self.format_response(
            full_response,
            metadata={
                'num_holdings': len(allocations),
                'num_sectors': len(sector_allocation),
                'has_pl_data': pl_data is not None,
                'visualizations': visualizations
            }
        )
    
    def _build_analysis_text(
        self,
        allocations: list,
        sector_allocation: dict,
        pl_data: Optional[dict]
    ) -> str:
        """Build portfolio analysis text"""
        
        text = []
        
        # Holdings summary
        if allocations:
            text.append("**Holdings:**")
            for holding in allocations[:5]:  # Top 5
                name = holding['name']
                allocation_pct = holding['allocation_percentage']
                value = holding['value']
                text.append(f"- {name}: {format_currency(value)} ({format_percentage(allocation_pct/100)})")
            
            if len(allocations) > 5:
                text.append(f"- ...and {len(allocations) - 5} more holdings")
        
        # Sector allocation
        if sector_allocation:
            text.append("\n**Sector Allocation:**")
            sorted_sectors = sorted(sector_allocation.items(), key=lambda x: x[1], reverse=True)
            for sector, pct in sorted_sectors:
                text.append(f"- {sector}: {format_percentage(pct/100)}")
        
        # P&L if available
        if pl_data:
            text.append(f"\n**Performance:**")
            text.append(f"- Current Value: {format_currency(pl_data['current_value'])}")
            text.append(f"- Invested Value: {format_currency(pl_data['invested_value'])}")
            text.append(f"- Profit/Loss: {format_currency(pl_data['absolute'])} ({format_percentage(pl_data['percentage']/100)})")
        
        return "\n".join(text)

    # ── Asynchronous ──────────────────────────────────────────────────────────

    @atraceable(name="portfolio_agent_async_process", tags=["agent", "portfolio", "async"])
    async def async_process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs,
    ) -> Dict:
        """Async portfolio analysis — computes metrics synchronously, LLM call is async."""
        logger.info("Portfolio Agent async analyzing portfolio...")

        portfolio_data = kwargs.get('portfolio') or (context or {}).get('portfolio')

        if not portfolio_data:
            return self.format_response(
                "I'd be happy to analyze your portfolio! Please provide your holdings information (stock symbols and quantities).",
                metadata={'status': 'awaiting_portfolio'}
            )

        portfolio = Portfolio.from_dict(portfolio_data) if isinstance(portfolio_data, dict) else portfolio_data
        allocations = portfolio.get_allocation()
        sector_allocation = portfolio.get_sector_allocation()
        pl_data = portfolio.get_profit_loss()
        analysis_text = self._build_analysis_text(allocations, sector_allocation, pl_data)

        edu_context = self.retrieve_context(
            "portfolio diversification and asset allocation", top_k=3
        )
        prompt = f"""Based on this portfolio analysis, provide educational insights about diversification and risk:

{analysis_text}

User Query: {query}

Focus on:
1. Educational explanation of their current allocation
2. General principles of diversification
3. Concepts they should understand (sector risk, concentration risk, etc.)

Remember: Provide education, not specific investment advice."""

        response = await self.async_generate_response(prompt, edu_context)
        response_with_disclaimer = self.add_disclaimer(response, "portfolio")
        full_response = f"""**Portfolio Overview:**

{analysis_text}

**Educational Insights:**

{response_with_disclaimer}
"""
        # Prepare visualizations
        visualizations = []
        if allocations:
            visualizations.append(get_portfolio_allocation_chart(allocations))
        if sector_allocation:
            visualizations.append(get_sector_allocation_chart(sector_allocation))

        return self.format_response(
            full_response,
            metadata={
                'num_holdings': len(allocations),
                'num_sectors': len(sector_allocation),
                'has_pl_data': pl_data is not None,
                'visualizations': visualizations
            }
        )

