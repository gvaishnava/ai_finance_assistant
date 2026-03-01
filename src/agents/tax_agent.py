"""
Tax Education Agent - Explains tax concepts and account types
"""

from typing import Dict, Optional
from src.agents.base_agent import BaseAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TaxEducationAgent(BaseAgent):
    """Agent for tax education"""
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(
            agent_name="tax",
            config_path=config_path,
            use_rag=True
        )
    
    def process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Provide tax education
        
        Args:
            query: User query about taxes
            context: Optional context
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with tax education
        """
        logger.info(f"Tax Education Agent processing: {query[:50]}...")
        
        # Retrieve tax-related educational context
        edu_context = self.retrieve_context(
            f"taxation tax {query}",
            top_k=5
        )
        
        # Build educational prompt
        prompt = f"""User Query: {query}

Provide educational information about tax concepts:
1. Explain the tax concept in simple terms
2. Use examples to illustrate
3. Mention any relevant Indian tax regulations (as educational information)
4. Explain implications for investors (educational only)

IMPORTANT: 
- This is general tax education only
- Tax situations vary greatly by individual circumstances
- Always recommend consulting a qualified tax professional for personalized advice
- Do not provide specific tax advice or recommendations"""
        
        response = self.generate_response(prompt, edu_context)
        
        # Add extra emphasis on the tax disclaimer
        tax_disclaimer = """

---

**⚠️ Important Tax Disclaimer:**

This information is for educational purposes only and should not be considered as tax advice. Tax laws are complex and change frequently. Your individual tax situation depends on many factors including your income, investments, deductions, and jurisdiction.

**Always consult with a qualified tax professional or Chartered Accountant before making any tax-related decisions.**

The information provided here is general in nature and may not apply to your specific circumstances."""
        
        response_with_disclaimer = response + tax_disclaimer
        
        citations = self.retriever.get_citations(query, top_k=5) if self.retriever else []
        
        return self.format_response(
            response_with_disclaimer,
            citations=citations,
            metadata={'requires_professional_advice': True}
        )

    # ── Asynchronous ──────────────────────────────────────────────────────────

    async def async_process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs,
    ) -> Dict:
        """Async tax education — uses async LLM call."""
        logger.info(f"Tax Education Agent async processing: {query[:50]}...")

        edu_context = self.retrieve_context(f"taxation tax {query}", top_k=5)

        prompt = f"""User Query: {query}

Provide educational information about tax concepts:
1. Explain the tax concept in simple terms
2. Use examples to illustrate
3. Mention any relevant Indian tax regulations (as educational information)
4. Explain implications for investors (educational only)

IMPORTANT:
- This is general tax education only
- Tax situations vary greatly by individual circumstances
- Always recommend consulting a qualified tax professional for personalized advice
- Do not provide specific tax advice or recommendations"""

        response = await self.async_generate_response(prompt, edu_context)

        tax_disclaimer = """

---

**⚠️ Important Tax Disclaimer:**

This information is for educational purposes only and should not be considered as tax advice. Tax laws are complex and change frequently. Your individual tax situation depends on many factors including your income, investments, deductions, and jurisdiction.

**Always consult with a qualified tax professional or Chartered Accountant before making any tax-related decisions.**

The information provided here is general in nature and may not apply to your specific circumstances."""

        response_with_disclaimer = response + tax_disclaimer
        citations = self.retriever.get_citations(query, top_k=5) if self.retriever else []

        return self.format_response(
            response_with_disclaimer,
            citations=citations,
            metadata={'requires_professional_advice': True}
        )

