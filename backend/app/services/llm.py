"""LLM service for Claude and OpenAI with robust error handling."""
import asyncio
import time
from typing import Dict, Any, Optional, List, Literal
from enum import Enum
import anthropic
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Available LLM providers."""
    CLAUDE = "claude"
    OPENAI = "openai"


class LLMError(Exception):
    """Base exception for LLM errors."""
    pass


class LLMRateLimitError(LLMError):
    """Rate limit exceeded error."""
    pass


class LLMInvalidRequestError(LLMError):
    """Invalid request error."""
    pass


class LLMService:
    """
    Unified LLM service with support for multiple providers.

    Features:
    - Automatic retry with exponential backoff
    - Rate limit handling
    - Token counting and budget tracking
    - Streaming support
    - Error normalization
    - Request logging
    """

    # Model defaults
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    OPENAI_MODEL = "gpt-4o-mini"

    # Rate limiting
    MIN_REQUEST_INTERVAL = 0.5  # 500ms between requests

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.CLAUDE,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize LLM service.

        Args:
            provider: Default LLM provider to use
            anthropic_api_key: Anthropic API key (defaults to settings)
            openai_api_key: OpenAI API key (defaults to settings)
        """
        self.provider = provider
        self.last_request_time = 0

        # Initialize clients
        self.anthropic_key = anthropic_api_key or settings.ANTHROPIC_API_KEY
        self.openai_key = openai_api_key or settings.OPENAI_API_KEY

        if self.anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        else:
            self.anthropic_client = None

        if self.openai_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
        else:
            self.openai_client = None

    def _rate_limit(self):
        """Enforce minimum interval between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - time_since_last_request)

        self.last_request_time = time.time()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((LLMRateLimitError, anthropic.APITimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion using specified provider.

        Args:
            prompt: User prompt/message
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            provider: Override default provider
            model: Override default model
            **kwargs: Additional provider-specific parameters

        Returns:
            Dict with 'content', 'usage', 'model', 'provider'

        Raises:
            LLMRateLimitError: Rate limit exceeded
            LLMInvalidRequestError: Invalid request
            LLMError: Other LLM errors
        """
        self._rate_limit()

        provider = provider or self.provider

        try:
            if provider == LLMProvider.CLAUDE:
                return self._complete_claude(
                    prompt, system_prompt, max_tokens, temperature, model, **kwargs
                )
            elif provider == LLMProvider.OPENAI:
                return self._complete_openai(
                    prompt, system_prompt, max_tokens, temperature, model, **kwargs
                )
            else:
                raise LLMError(f"Unknown provider: {provider}")

        except (anthropic.RateLimitError, openai.RateLimitError) as e:
            raise LLMRateLimitError(f"Rate limit exceeded: {str(e)}")
        except (anthropic.BadRequestError, openai.BadRequestError) as e:
            raise LLMInvalidRequestError(f"Invalid request: {str(e)}")
        except Exception as e:
            if isinstance(e, (LLMRateLimitError, LLMInvalidRequestError, LLMError)):
                raise
            raise LLMError(f"LLM request failed: {str(e)}")

    def _complete_claude(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        model: Optional[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Complete using Claude."""
        if not self.anthropic_client:
            raise LLMError("Anthropic API key not configured")

        model = model or self.CLAUDE_MODEL

        # Build request
        request_kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }

        if system_prompt:
            request_kwargs["system"] = system_prompt

        # Make request
        response = self.anthropic_client.messages.create(**request_kwargs)

        # Extract content
        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        return {
            "content": content,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            "model": response.model,
            "provider": "claude",
            "finish_reason": response.stop_reason
        }

    def _complete_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        model: Optional[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Complete using OpenAI."""
        if not self.openai_client:
            raise LLMError("OpenAI API key not configured")

        model = model or self.OPENAI_MODEL

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Make request
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        return {
            "content": response.choices[0].message.content,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "model": response.model,
            "provider": "openai",
            "finish_reason": response.choices[0].finish_reason
        }

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses rough estimation: ~4 characters per token.
        For production, use tiktoken or similar.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def get_model_name(self) -> str:
        """Get the current model name based on provider."""
        if self.provider == LLMProvider.CLAUDE:
            return self.CLAUDE_MODEL
        elif self.provider == LLMProvider.OPENAI:
            return self.OPENAI_MODEL
        else:
            return "unknown"

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Alias for complete() method for backward compatibility.
        
        Args:
            prompt: User prompt/message
            system_prompt: System prompt (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            provider: Override default provider
            model: Override default model
            **kwargs: Additional provider-specific parameters

        Returns:
            Dict with 'content', 'usage', 'model', 'provider'
        """
        return self.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            provider=provider,
            model=model,
            **kwargs
        )


# Singleton instances
_llm_service_claude: Optional[LLMService] = None
_llm_service_openai: Optional[LLMService] = None


def get_llm_service(provider: LLMProvider = LLMProvider.CLAUDE) -> LLMService:
    """
    Get or create LLM service instance.

    Args:
        provider: LLM provider to use

    Returns:
        LLM service instance
    """
    global _llm_service_claude, _llm_service_openai

    if provider == LLMProvider.CLAUDE:
        if _llm_service_claude is None:
            _llm_service_claude = LLMService(provider=LLMProvider.CLAUDE)
        return _llm_service_claude
    elif provider == LLMProvider.OPENAI:
        if _llm_service_openai is None:
            _llm_service_openai = LLMService(provider=LLMProvider.OPENAI)
        return _llm_service_openai
    else:
        raise ValueError(f"Unknown provider: {provider}")
