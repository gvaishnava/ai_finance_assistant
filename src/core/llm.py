"""
Google Gemini LLM client and utilities
"""

import os
import asyncio
from google import genai
from typing import Optional, List, Dict
import yaml
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.tracing import traceable, atraceable

logger = get_logger(__name__)


class GeminiClient:
    """Google Gemini API client using google-genai SDK"""

    def __init__(self, config: dict):
        """
        Initialize Gemini client

        Args:
            config: Configuration dictionary
        """
        self.config = config
        llm_config = config["llm"]["gemini"]
        api_key = os.getenv(llm_config["api_key_env"])

        if not api_key:
            raise ValueError(
                f"API key not found. Please set {llm_config['api_key_env']} "
                "environment variable"
            )

        self.client = genai.Client(api_key=api_key)
        self.model_name = llm_config["model"]
        self.temperature = llm_config["temperature"]
        self.max_tokens = llm_config.get("max_tokens", 2048)

        logger.info(f"Initialized Gemini client with model: {self.model_name}")

    # ── Synchronous ───────────────────────────────────────────────────────────

    @traceable(name="gemini_generate", tags=["llm", "gemini"], run_type="llm")
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate response from Gemini

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Generated response text
        """
        import time
        import random

        config = {
            "temperature": temperature or self.temperature,
            "max_output_tokens": max_tokens or self.max_tokens,
            "system_instruction": system_prompt,
        }

        retries = 5
        for attempt in range(retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )
                return response.text
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    if attempt < retries - 1:
                        sleep_time = (5 * (2 ** attempt)) + (random.random() * 2)
                        logger.warning(
                            f"LLM Rate limit hit. Retrying in {sleep_time:.2f}s "
                            f"(Attempt {attempt + 1}/{retries})"
                        )
                        time.sleep(sleep_time)
                        continue
                logger.error(f"Error generating Gemini response: {e}")
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

    @atraceable(name="gemini_agenerate", tags=["llm", "gemini", "async"], run_type="llm")
    async def agenerate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Asynchronously generate a response from Gemini.

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


class FallbackLLMClient:
    """Wrapper that tries a primary client and falls back to a secondary client on failure."""

    def __init__(self, primary_client, fallback_client):
        self.primary_client = primary_client
        self.fallback_client = fallback_client

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        try:
            return self.primary_client.generate(prompt, system_prompt, temperature, max_tokens)
        except Exception as e:
            logger.warning(f"Primary LLM client failed with error: {e}. Falling back to secondary client.")
            return self.fallback_client.generate(prompt, system_prompt, temperature, max_tokens)

    def generate_with_context(self, prompt: str, context: List[str], system_prompt: Optional[str] = None, temperature: Optional[float] = None) -> str:
        try:
            return self.primary_client.generate_with_context(prompt, context, system_prompt, temperature)
        except Exception as e:
            logger.warning(f"Primary LLM client failed with error: {e}. Falling back to secondary client.")
            return self.fallback_client.generate_with_context(prompt, context, system_prompt, temperature)

    async def agenerate(self, prompt: str, system_prompt: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        try:
            return await self.primary_client.agenerate(prompt, system_prompt, temperature, max_tokens)
        except Exception as e:
            logger.warning(f"Primary LLM async client failed with error: {e}. Falling back to secondary client.")
            return await self.fallback_client.agenerate(prompt, system_prompt, temperature, max_tokens)

    async def agenerate_with_context(self, prompt: str, context: List[str], system_prompt: Optional[str] = None, temperature: Optional[float] = None) -> str:
        try:
            return await self.primary_client.agenerate_with_context(prompt, context, system_prompt, temperature)
        except Exception as e:
            logger.warning(f"Primary LLM async client failed with error: {e}. Falling back to secondary client.")
            return await self.fallback_client.agenerate_with_context(prompt, context, system_prompt, temperature)


# ── Module-level singleton ────────────────────────────────────────────────────
_llm_client = None


def get_llm_client(config_path: str = "config.yaml"):
    """Get or create LLM client singleton based on configuration."""
    global _llm_client

    if _llm_client is None:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        llm_config = config.get("llm", {})
        provider = llm_config.get("provider", "gemini")
        fallback_provider = llm_config.get("fallback_provider")

        def create_client(prov_name):
            if prov_name == "openai":
                from src.core.openai_client import OpenAIClient
                return OpenAIClient(config)
            else:
                return GeminiClient(config)

        primary = create_client(provider)
        
        if fallback_provider and fallback_provider != provider:
            try:
                fallback = create_client(fallback_provider)
                _llm_client = FallbackLLMClient(primary, fallback)
                logger.info(f"Initialized LLM with primary='{provider}', fallback='{fallback_provider}'")
            except Exception as e:
                logger.warning(f"Failed to initialize fallback provider '{fallback_provider}': {e}")
                _llm_client = primary
        else:
            _llm_client = primary

    return _llm_client


def generate_response(
    prompt: str,
    system_prompt: Optional[str] = None,
    context: Optional[List[str]] = None,
    config_path: str = "config.yaml",
) -> str:
    """
    Convenience function to generate a response.

    Args:
        prompt: User prompt
        system_prompt: System instructions
        context: Optional retrieved context for RAG
        config_path: Path to configuration file

    Returns:
        Generated response text
    """
    client = get_llm_client(config_path)
    if context:
        return client.generate_with_context(prompt, context, system_prompt)
    return client.generate(prompt, system_prompt)


async def agenerate_response(
    prompt: str,
    system_prompt: Optional[str] = None,
    context: Optional[List[str]] = None,
    config_path: str = "config.yaml",
) -> str:
    """
    Async convenience function to generate a response.

    Args:
        prompt: User prompt
        system_prompt: System instructions
        context: Optional retrieved context for RAG
        config_path: Path to configuration file

    Returns:
        Generated response text
    """
    client = get_llm_client(config_path)
    if context:
        return await client.agenerate_with_context(prompt, context, system_prompt)
    return await client.agenerate(prompt, system_prompt)
