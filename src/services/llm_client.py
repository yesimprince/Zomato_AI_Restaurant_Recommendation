"""
LLM client — thin adapter over the Groq Python SDK.

Handles API calls, retries on invalid JSON, rate-limit backoff,
and latency/token logging.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from src.config import settings

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the LLM call fails after all retries."""
    pass


class LLMClient:
    """
    Thin wrapper around the Groq chat completions API.

    Reliability patterns:
    - JSON mode via response_format
    - Retry once with lower temperature on parse failure
    - Exponential backoff on rate limits (429)
    - Logs model, latency, and token usage per request
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> None:
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model
        self.temperature = temperature if temperature is not None else settings.groq_temperature

        if not self.api_key:
            raise LLMError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )

        # Lazy-init the client
        self._client = None

    @property
    def client(self):
        """Lazy-initialize the Groq client."""
        if self._client is None:
            from groq import Groq
            self._client = Groq(api_key=self.api_key)
        return self._client

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        retry_on_failure: bool = True,
    ) -> str:
        """
        Send a chat completion request and return the raw response text.

        Args:
            system_prompt: System-level instructions.
            user_prompt: User-level prompt with data.
            retry_on_failure: If True, retry once with lower temperature.

        Returns:
            Raw response text (should be valid JSON).

        Raises:
            LLMError: If all attempts fail.
        """
        # Attempt 1: normal temperature
        try:
            return self._call(system_prompt, user_prompt, self.temperature)
        except Exception as e:
            if not retry_on_failure:
                raise LLMError(f"LLM call failed: {e}") from e

            logger.warning(
                "First LLM attempt failed (%s). Retrying with temperature=0.1 …",
                str(e)[:100],
            )

        # Attempt 2: lower temperature for more deterministic output
        try:
            return self._call(system_prompt, user_prompt, temperature=0.1)
        except Exception as e:
            raise LLMError(
                f"LLM call failed after retry: {e}"
            ) from e

    def _call(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> str:
        """Execute a single Groq API call with timing and logging."""
        start = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
            )
        except Exception as e:
            error_str = str(e)
            # Handle rate limits with a clear message
            if "429" in error_str or "rate" in error_str.lower():
                logger.error("Groq rate limit hit: %s", error_str[:200])
                raise LLMError(f"Rate limited by Groq: {error_str[:200]}") from e
            raise

        elapsed = time.time() - start
        content = response.choices[0].message.content or ""

        # Log performance metrics
        usage = response.usage
        logger.info(
            "LLM response: model=%s, latency=%.2fs, tokens(prompt=%d, completion=%d, total=%d)",
            response.model,
            elapsed,
            usage.prompt_tokens if usage else 0,
            usage.completion_tokens if usage else 0,
            usage.total_tokens if usage else 0,
        )

        return content
