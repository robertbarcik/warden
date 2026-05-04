"""Async OpenRouter client wrapping the official OpenAI SDK.

Why the OpenAI SDK and not LiteLLM (bloom's choice)?
  - geobias and selfjudge already use this pattern; it's the user's most
    recent house style for OpenRouter integration.
  - The SDK's async client gives us native asyncio support without the
    LiteLLM abstraction surface.

Concurrency throttling and retry-with-backoff live in `orchestrator.py`,
not here. This module only exposes the per-call coroutine.
"""
from __future__ import annotations
import os
import asyncio
import random
from dataclasses import dataclass
from typing import Optional

import httpx
from openai import AsyncOpenAI
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError
from dotenv import load_dotenv

from . import config

load_dotenv(dotenv_path=config.REPO_ROOT / ".env", override=False)


@dataclass
class ChatResult:
    text: str
    prompt_tokens: int
    completion_tokens: int
    model: str
    latency_s: float
    finish_reason: str = ""


class OpenRouterClient:
    def __init__(self) -> None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY not set. Copy .env.example to .env and fill it in."
            )
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=config.OPENROUTER_BASE_URL,
            timeout=config.REQUEST_TIMEOUT,
            default_headers={
                "HTTP-Referer": "https://github.com/robertbarcik/warden",
                "X-Title": "Warden",
            },
        )

    async def chat(
        self,
        model: str,
        system: Optional[str],
        user: str,
        max_tokens: int,
        temperature: float,
    ) -> ChatResult:
        """Single chat completion. Caller is responsible for retries/backoff."""
        messages = []
        if system is not None:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})

        import time as _t
        t0 = _t.perf_counter()
        resp = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        latency = _t.perf_counter() - t0

        choice = resp.choices[0]
        text = choice.message.content or ""
        usage = resp.usage
        return ChatResult(
            text=text,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            model=resp.model or model,
            latency_s=latency,
            finish_reason=choice.finish_reason or "",
        )

    async def chat_with_retry(
        self,
        model: str,
        system: Optional[str],
        user: str,
        max_tokens: int,
        temperature: float,
    ) -> ChatResult:
        last_exc: Optional[Exception] = None
        delay = config.RETRY_INITIAL_DELAY
        for attempt in range(config.MAX_RETRIES):
            try:
                return await self.chat(model, system, user, max_tokens, temperature)
            except (RateLimitError, APIConnectionError, APITimeoutError, httpx.HTTPError) as e:
                last_exc = e
            except APIError as e:
                # Some 5xx are retryable; 4xx other than 429 we surface immediately.
                status = getattr(e, "status_code", None)
                if status is not None and 400 <= status < 500 and status != 429:
                    raise
                last_exc = e
            jitter = random.uniform(0, delay * 0.3)
            await asyncio.sleep(min(delay + jitter, config.RETRY_MAX_DELAY))
            delay = min(delay * 2, config.RETRY_MAX_DELAY)
        assert last_exc is not None
        raise last_exc


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    p = config.PRICING.get(model)
    if not p:
        return 0.0
    return prompt_tokens * p["prompt"] + completion_tokens * p["completion"]
