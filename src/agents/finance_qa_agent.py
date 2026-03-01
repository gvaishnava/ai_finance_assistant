"""
Finance Q&A Agent - Handles general financial education queries
"""

from typing import Dict, Optional
from src.agents.base_agent import BaseAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FinanceQAAgent(BaseAgent):
    """Agent for general financial education and terminology"""
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(
            agent_name="finance_qa",
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
        Process a financial education query
        
        Args:
            query: User question about financial concepts
            context: Optional context (user profile for personalization)
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        logger.info(f"Finance Q&A Agent processing query: {query[:50]}...")
        
        # Retrieve relevant context from knowledge base
        retrieved_context = self.retrieve_context(query, top_k=5)
        
        # Build enhanced prompt with user knowledge level
        user_knowledge = "beginner"
        if context and 'user_profile' in context:
            user_knowledge = context['user_profile'].get('knowledge_level', 'beginner')
        
        enhanced_prompt = f"""User Knowledge Level: {user_knowledge}

Question: {query}

Please provide a clear, educational explanation that matches the user's knowledge level. 
- For beginners: Use simple language, avoid jargon, include analogies
- For intermediate: Use some technical terms with brief explanations
- For advanced: Use technical terminology freely, focus on nuances

Include practical examples where relevant."""
        
        # Generate response
        response = self.generate_response(enhanced_prompt, retrieved_context)
        
        # Add educational disclaimer
        response_with_disclaimer = self.add_disclaimer(response, "general")
        
        # Get citations
        citations = self.retriever.get_citations(query, top_k=5) if self.retriever else []
        
        return self.format_response(
            response_with_disclaimer,
            citations=citations,
            metadata={
                'knowledge_level': user_knowledge,
                'num_citations': len(citations)
            }
        )

    # ── Asynchronous ──────────────────────────────────────────────────────────

    async def async_process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs,
    ) -> Dict:
        """Async finance Q&A — uses async LLM call."""
        logger.info(f"Finance Q&A Agent async processing: {query[:50]}...")

        retrieved_context = self.retrieve_context(query, top_k=5)

        user_knowledge = "beginner"
        if context and 'user_profile' in context:
            user_knowledge = context['user_profile'].get('knowledge_level', 'beginner')

        enhanced_prompt = f"""User Knowledge Level: {user_knowledge}

Question: {query}

Please provide a clear, educational explanation that matches the user's knowledge level.
- For beginners: Use simple language, avoid jargon, include analogies
- For intermediate: Use some technical terms with brief explanations
- For advanced: Use technical terminology freely, focus on nuances

Include practical examples where relevant."""

        response = await self.async_generate_response(enhanced_prompt, retrieved_context)
        response_with_disclaimer = self.add_disclaimer(response, "general")
        citations = self.retriever.get_citations(query, top_k=5) if self.retriever else []

        return self.format_response(
            response_with_disclaimer,
            citations=citations,
            metadata={
                'knowledge_level': user_knowledge,
                'num_citations': len(citations)
            }
        )

