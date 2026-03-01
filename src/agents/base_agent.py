"""
Base agent class with common functionality
"""

import asyncio
from typing import List, Dict, Optional
import yaml

from src.core.llm import get_llm_client
from src.rag.retriever import Retriever
from src.core.disclaimers import add_disclaimer_to_response
from src.utils.logger import get_logger, set_log_context
from src.utils.tracing import traceable, atraceable

logger = get_logger(__name__)


class BaseAgent:
    """Base class for all specialized agents"""

    def __init__(
        self,
        agent_name: str,
        config_path: str = "config.yaml",
        use_rag: bool = True,
    ):
        """
        Initialize base agent

        Args:
            agent_name: Name of the agent (must match config)
            config_path: Path to configuration file
            use_rag: Whether this agent uses RAG
        """
        self.agent_name = agent_name
        self.config_path = config_path

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        agent_config = config["agents"].get(agent_name, {})
        self.display_name = agent_config.get("name", agent_name)
        self.description = agent_config.get("description", "")
        self.system_prompt = agent_config.get("system_prompt", "")
        self.temperature = agent_config.get("temperature", 0.7)

        self.llm_client = get_llm_client(config_path)

        self.use_rag = use_rag
        if use_rag:
            self.retriever = Retriever(config_path)
        else:
            self.retriever = None

        logger.info(f"Initialized {self.display_name}")

    # ── Synchronous interface ─────────────────────────────────────────────────

    def process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs,
    ) -> Dict:
        """
        Process a user query (synchronous).

        Args:
            query: User query
            context: Optional context dictionary
            **kwargs: Additional agent-specific parameters

        Returns:
            Response dictionary with 'response', 'metadata', etc.
        """
        raise NotImplementedError("Subclasses must implement process()")

    @traceable(name="base_agent_generate_response", tags=["agent", "llm"], run_type="chain")
    def generate_response(
        self,
        prompt: str,
        retrieved_context: List[str] = None,
        temperature: float = None,
    ) -> str:
        """
        Generate response using LLM (synchronous).

        Args:
            prompt: User prompt
            retrieved_context: Optional retrieved context for RAG
            temperature: Optional temperature override

        Returns:
            Generated response
        """
        set_log_context(agent_name=self.agent_name)
        temp = temperature if temperature is not None else self.temperature

        if retrieved_context:
            return self.llm_client.generate_with_context(
                prompt,
                retrieved_context,
                system_prompt=self.system_prompt,
                temperature=temp,
            )
        return self.llm_client.generate(
            prompt,
            system_prompt=self.system_prompt,
            temperature=temp,
        )

    # ── Asynchronous interface ────────────────────────────────────────────────

    async def async_process(
        self,
        query: str,
        context: Optional[Dict] = None,
        **kwargs,
    ) -> Dict:
        """
        Process a user query (asynchronous).

        Falls back to running the synchronous process() in an executor
        unless overridden by a subclass with a native implementation.

        Args:
            query: User query
            context: Optional context dictionary
            **kwargs: Additional agent-specific parameters

        Returns:
            Response dictionary with 'response', 'metadata', etc.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.process(query, context, **kwargs),
        )

    @atraceable(name="base_agent_async_generate_response", tags=["agent", "llm", "async"], run_type="chain")
    async def async_generate_response(
        self,
        prompt: str,
        retrieved_context: List[str] = None,
        temperature: float = None,
    ) -> str:
        """
        Generate response using LLM (asynchronous).

        Args:
            prompt: User prompt
            retrieved_context: Optional retrieved context for RAG
            temperature: Optional temperature override

        Returns:
            Generated response
        """
        set_log_context(agent_name=self.agent_name)
        temp = temperature if temperature is not None else self.temperature

        if retrieved_context:
            return await self.llm_client.agenerate_with_context(
                prompt,
                retrieved_context,
                system_prompt=self.system_prompt,
                temperature=temp,
            )
        return await self.llm_client.agenerate(
            prompt,
            system_prompt=self.system_prompt,
            temperature=temp,
        )

    # ── Shared helpers ────────────────────────────────────────────────────────

    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Dict = None,
    ) -> List[str]:
        """
        Retrieve relevant context using RAG

        Args:
            query: Search query
            top_k: Number of results
            filter_metadata: Optional metadata filters

        Returns:
            List of context strings
        """
        if not self.use_rag or not self.retriever:
            return []
        return self.retriever.get_context(query, top_k, include_metadata=True)

    def add_disclaimer(self, response: str, disclaimer_type: str = "general") -> str:
        """Add disclaimer to response"""
        return add_disclaimer_to_response(response, disclaimer_type, self.config_path)

    def format_response(
        self,
        response_text: str,
        citations: List[Dict] = None,
        metadata: Dict = None,
    ) -> Dict:
        """
        Format response as dictionary

        Args:
            response_text: Response text
            citations: Optional list of citations
            metadata: Optional metadata

        Returns:
            Formatted response dictionary
        """
        result = {
            "agent": self.agent_name,
            "agent_display_name": self.display_name,
            "response": response_text,
        }
        if citations:
            result["citations"] = citations
        if metadata:
            result["metadata"] = metadata
        return result
