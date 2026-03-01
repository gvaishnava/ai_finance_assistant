"""
News Synthesizer Agent - Summarizes and contextualizes financial news
"""

import asyncio
from typing import Dict, Optional, List
import os
from src.agents.base_agent import BaseAgent
from src.utils.logger import get_logger
from src.utils.visualizers import get_news_impact_chart
from tavily import TavilyClient

logger = get_logger(__name__)

class NewsSynthesizerAgent(BaseAgent):
    """Agent for financial news summarization and contextualization"""
    
    def __init__(self, config_path: str = "config.yaml"):
        super().__init__(
            agent_name="news",
            config_path=config_path,
            use_rag=True
        )
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY")) if os.getenv("TAVILY_API_KEY") else None
        if not self.tavily_client:
            logger.warning("TAVILY_API_KEY not found. Live news search will be disabled.")
    
    @traceable(name="news_agent_process", tags=["agent", "news"])
    def process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """
        Synthesize and explain financial news
        
        Args:
            query: User query about news or news article
            context: Optional context including news article
            **kwargs: Additional parameters (news_article text)
            
        Returns:
            Response dictionary with news synthesis
        """
        logger.info(f"News Synthesizer processing: {query[:50]}...")
        
        news_article = kwargs.get('news_article')
        
        if news_article:
            return self._synthesize_article(query, news_article)
        elif "news" in query.lower() or "latest" in query.lower() or "update" in query.lower():
             # Try to search if it looks like a news request
             search_results = self.search_news(query)
             if search_results:
                 # Pass the top result as the article to synthesize
                 combined_text = "\n\n".join([f"Title: {r['title']}\nSource: {r['url']}\nContent: {r['content']}" for r in search_results[:3]])
                 return self._synthesize_article(query, combined_text)
             else:
                 return self._explain_news_concept(query)
        else:
            return self._explain_news_concept(query)

    def search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for financial news using Tavily"""
        if not self.tavily_client:
            logger.warning("Tavily client not initialized")
            return []
            
        try:
            logger.info(f"Searching news for: {query}")
            response = self.tavily_client.search(
                query=query, 
                search_depth="advanced",
                topic="finance",
                max_results=max_results
            )
            return response.get('results', [])
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []
    
    def _synthesize_article(self, query: str, article: str) -> Dict:
        """Synthesize and explain a news article"""
        edu_context = self.retrieve_context(
            f"financial news market analysis {query}",
            top_k=3
        )
        prompt = f"""Financial News Article:
{article}

User Question: {query}

Please:
1. Summarize the key points in simple language
2. Explain any financial jargon or concepts mentioned
3. Provide educational context from the knowledge base
4. Explain potential implications for beginner investors
5. Clarify what this means in layman's terms

Focus on education and helping users understand, not on making predictions."""
        response = self.generate_response(prompt, edu_context)
        # Simulate a sentiment score for educational demonstration
        sentiment_score = 0.5 if "positive" in response.lower() or "gain" in response.lower() else -0.2
        visualizations = [get_news_impact_chart(sentiment_score)]

        return self.format_response(
            self.add_disclaimer(response, "general"),
            metadata={
                'article_provided': True,
                'visualizations': visualizations
            }
        )

    def _explain_news_concept(self, query: str) -> Dict:
        """Explain concepts related to financial news"""
        edu_context = self.retrieve_context(
            f"financial news market events {query}",
            top_k=5
        )
        prompt = f"""User Query: {query}

Provide educational explanation about:
1. What this financial news/event means
2. Key concepts and terminology involved
3. How such events typically affect markets (educational context)
4. What beginners should understand about this topic

Use simple language and include examples where helpful."""
        response = self.generate_response(prompt, edu_context)
        citations = self.retriever.get_citations(query, top_k=5) if self.retriever else []
        # Simulate a sentiment score
        sentiment_score = 0.1
        visualizations = [get_news_impact_chart(sentiment_score)]

        return self.format_response(
            self.add_disclaimer(response, "general"),
            citations=citations,
            metadata={
                'news_type': 'concept_explanation',
                'visualizations': visualizations
            }
        )

    # ── Asynchronous ──────────────────────────────────────────────────────────

    @atraceable(name="news_agent_async_process", tags=["agent", "news", "async"])
    async def async_process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs,
    ) -> Dict:
        """Async version of process() — uses async LLM calls."""
        logger.info(f"News Synthesizer async processing: {query[:50]}...")
        news_article = kwargs.get('news_article')

        if news_article:
            return await self._async_synthesize_article(query, news_article)
        elif any(kw in query.lower() for kw in ("news", "latest", "update")):
            search_results = await self._async_search_news(query)
            if search_results:
                combined_text = "\n\n".join(
                    [f"Title: {r['title']}\nSource: {r['url']}\nContent: {r['content']}"
                     for r in search_results[:3]]
                )
                return await self._async_synthesize_article(query, combined_text)
            return await self._async_explain_news_concept(query)
        return await self._async_explain_news_concept(query)

    async def _async_search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """Async Tavily search (runs blocking call in executor)."""
        if not self.tavily_client:
            logger.warning("Tavily client not initialized")
            return []
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.search_news(query, max_results),
        )

    async def _async_synthesize_article(self, query: str, article: str) -> Dict:
        """Async article synthesis."""
        edu_context = self.retrieve_context(
            f"financial news market analysis {query}", top_k=3
        )
        prompt = f"""Financial News Article:
{article}

User Question: {query}

Please:
1. Summarize the key points in simple language
2. Explain any financial jargon or concepts mentioned
3. Provide educational context from the knowledge base
4. Explain potential implications for beginner investors
5. Clarify what this means in layman's terms

Focus on education and helping users understand, not on making predictions."""
        response = await self.async_generate_response(prompt, edu_context)
        # Simulate a sentiment score for educational demonstration
        sentiment_score = 0.5 if "positive" in response.lower() or "gain" in response.lower() else -0.2
        visualizations = [get_news_impact_chart(sentiment_score)]

        return self.format_response(
            self.add_disclaimer(response, "general"),
            metadata={
                'article_provided': True,
                'visualizations': visualizations
            }
        )

    async def _async_explain_news_concept(self, query: str) -> Dict:
        """Async concept explanation."""
        edu_context = self.retrieve_context(
            f"financial news market events {query}", top_k=5
        )
        prompt = f"""User Query: {query}

Provide educational explanation about:
1. What this financial news/event means
2. Key concepts and terminology involved
3. How such events typically affect markets (educational context)
4. What beginners should understand about this topic

Use simple language and include examples where helpful."""
        response = await self.async_generate_response(prompt, edu_context)
        citations = self.retriever.get_citations(query, top_k=5) if self.retriever else []
        
        # Simulate a sentiment score
        sentiment_score = 0.1
        visualizations = [get_news_impact_chart(sentiment_score)]

        return self.format_response(
            self.add_disclaimer(response, "general"),
            citations=citations,
            metadata={
                'news_type': 'concept_explanation',
                'visualizations': visualizations
            }
        )

