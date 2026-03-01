"""
OpenAI LLM client and utilities
"""

import os
import asyncio
from openai import OpenAI
from typing import Optional, List, Dict
import yaml
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.tracing import traceable, atraceable

logger = get_logger(__name__)


class OpenAIClient:
    """OpenAI API client"""

    def __init__(self, config: dict):
        """
        Initialize OpenAI client

        Args:
            config: Configuration dictionary (full config)
        """
        self.config = config
        llm_config = config["llm"]["openai"]

        api_key_env = llm_config["api_key_env"]
        api_key = os.getenv(api_key_env)

        if not api_key:
            raise ValueError(
                f"API key not found. Please set {api_key_env} environment variable"
            )

        self.client = OpenAI(api_key=api_key)
        self.model_name = llm_config["model"]
        self.temperature = llm_config["temperature"]
        self.max_tokens = llm_config["max_tokens"]

        logger.info(f"Initialized OpenAI client with model: {self.model_name}")

    # ── Synchronous ───────────────────────────────────────────────────────────

    @traceable(name="openai_generate", tags=["llm", "openai"], run_type="llm")
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate response from OpenAI

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Generated response text
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # gpt-5-nano requires temperature=1
            if self.model_name == "gpt-5-nano":
                if (temperature or self.temperature) != 1:
                    logger.warning(
                        f"Model {self.model_name} requires temperature=1. Overriding."
                    )
                temperature = 1

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens or self.max_tokens,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            raise

    def generate_with_context(
        self,
        prompt: str,
        context: List[str],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate response with retrieved context (for RAG)

        Args:
            prompt: User prompt
            context: List of retrieved context strings
            system_prompt: System instructions
            temperature: Override default temperature

        Returns:
            Generated response text
        """
        context_str = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(context)])
        rag_prompt = (
            "Use the following context to answer the user's question. "
            "If the context doesn't contain relevant information, you can use your "
            "general knowledge but mention that.\n\n"
            f"{context_str}\n\nUser Question: {prompt}\n\nAnswer:"
        )
        return self.generate(rag_prompt, system_prompt=system_prompt, temperature=temperature)

    # ── Asynchronous ──────────────────────────────────────────────────────────

    @atraceable(name="openai_agenerate", tags=["llm", "openai", "async"], run_type="llm")
    async def agenerate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Asynchronously generate a response from OpenAI.

        Runs the blocking SDK call in a ThreadPoolExecutor so the event loop
        is not blocked while the network I/O completes.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Generated response text
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.generate(prompt, system_prompt, temperature, max_tokens),
        )

    async def agenerate_with_context(
        self,
        prompt: str,
        context: List[str],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Asynchronously generate a response with RAG context.

        Args:
            prompt: User prompt
            context: List of retrieved context strings
            system_prompt: System instructions
            temperature: Override default temperature

        Returns:
            Generated response text
        """
        context_str = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(context)])
        rag_prompt = (
            "Use the following context to answer the user's question. "
            "If the context doesn't contain relevant information, you can use your "
            "general knowledge but mention that.\n\n"
            f"{context_str}\n\nUser Question: {prompt}\n\nAnswer:"
        )
        return await self.agenerate(rag_prompt, system_prompt=system_prompt, temperature=temperature)
