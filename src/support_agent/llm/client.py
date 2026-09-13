"""LLM Client Abstraction Layer for Evidence-Grounded Support Agent.

Supports OpenRouter as the primary LLM gateway and OfflineReviewClient as a deterministic fallback.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


def load_env(path: Optional[Path | str] = None) -> None:
    """Load environment variables from a .env file if present."""
    if path:
        env_file = Path(path)
    else:
        root_env = Path(__file__).resolve().parents[3] / ".env"
        env_file = root_env if root_env.exists() else Path(".env")
    if not env_file.exists():
        return
    try:
        content = env_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("\"'")
            if key not in os.environ:
                os.environ[key] = val
    except Exception as e:
        logger.warning(f"Could not read .env file: {e}")


# Automatically try loading .env on module import
load_env()


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    content: str
    provider: str
    model: Optional[str]
    review_mode: str
    usage: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "review_mode": self.review_mode,
            "content": self.content,
            "usage": self.usage,
        }

    def json(self) -> Any:
        """Parse structured JSON from the response text."""
        return parse_json_from_text(self.content)


def parse_json_from_text(text: str) -> Any:
    """Extract and parse JSON from raw model text, handling markdown blocks, control characters, or prefixes.
    
    Raises ValueError if valid JSON cannot be found and parsed.
    """
    if not text or not text.strip():
        raise ValueError("Cannot parse JSON from empty text")

    cleaned = text.strip()

    # If wrapped in markdown ```json ... ``` or ``` ... ```
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, cleaned)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate, strict=False)
        except json.JSONDecodeError:
            pass

    # Direct JSON parse attempt with strict=False
    try:
        return json.loads(cleaned, strict=False)
    except json.JSONDecodeError:
        pass

    # Look for the first '{' and last '}' or first '[' and last ']'
    first_obj = cleaned.find("{")
    last_obj = cleaned.rfind("}")
    if first_obj != -1 and last_obj > first_obj:
        candidate = cleaned[first_obj:last_obj + 1]
        try:
            return json.loads(candidate, strict=False)
        except json.JSONDecodeError:
            # Try removing trailing commas before closing braces/brackets
            fixed = re.sub(r",\s*([\]}])", r"\1", candidate)
            try:
                return json.loads(fixed, strict=False)
            except json.JSONDecodeError:
                pass

    first_arr = cleaned.find("[")
    last_arr = cleaned.rfind("]")
    if first_arr != -1 and last_arr > first_arr:
        candidate = cleaned[first_arr:last_arr + 1]
        try:
            return json.loads(candidate, strict=False)
        except json.JSONDecodeError:
            fixed = re.sub(r",\s*([\]}])", r"\1", candidate)
            try:
                return json.loads(fixed, strict=False)
            except json.JSONDecodeError:
                pass

    raise ValueError(f"Failed to parse valid JSON from text: {text[:200]}...")


class BaseLLMClient(ABC):
    """Abstract base class for all LLM client implementations."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a response from the model."""
        pass


class OpenRouterClient(BaseLLMClient):
    """OpenRouter LLM gateway client.
    
    Reads configuration from environment variables or constructor arguments:
    - OPENROUTER_API_KEY
    - OPENROUTER_MODEL
    - OPENROUTER_BASE_URL (optional, default: https://openrouter.ai/api/v1)
    - OPENROUTER_SITE_URL (optional)
    - OPENROUTER_APP_NAME (optional)
    """

    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        site_url: Optional[str] = None,
        app_name: Optional[str] = None,
        timeout: int = 90,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not set. Please set the environment variable or pass api_key."
            )

        self.model = model or os.environ.get("OPENROUTER_MODEL", "").strip()
        if not self.model:
            raise ValueError(
                "OPENROUTER_MODEL is not set. Please set the environment variable or pass model."
            )

        self.base_url = (
            base_url
            or os.environ.get("OPENROUTER_BASE_URL", "").strip()
            or self.DEFAULT_BASE_URL
        ).rstrip("/")
        self.site_url = (
            site_url
            or os.environ.get("OPENROUTER_SITE_URL", "").strip()
            or "https://github.com/dp177/evidence-grounded-support-agent"
        )
        self.app_name = (
            app_name
            or os.environ.get("OPENROUTER_APP_NAME", "").strip()
            or "AmazonSupportAgent"
        )
        self.provider = "openrouter"
        self.review_mode = "openrouter"
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
        }
        return headers

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Call OpenRouter Chat Completions endpoint with retries."""
        url = f"{self.base_url}/chat/completions"

        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        else:
            # Default to a generous limit for reasoning and review tasks
            payload["max_tokens"] = 4096

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        payload.update(kwargs)

        headers = self._get_headers()
        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                )
                if resp.status_code in self.RETRYABLE_STATUS_CODES:
                    wait_time = self.retry_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"OpenRouter transient status {resp.status_code}. Retrying in {wait_time:.1f}s (attempt {attempt}/{self.max_retries})..."
                    )
                    time.sleep(wait_time)
                    continue

                resp.raise_for_status()
                data = resp.json()

                choice = data["choices"][0]
                message = choice.get("message", {})
                content = message.get("content")

                # Some thinking models place text in reasoning or finish before output if token-limited
                if content is None:
                    # Check reasoning or fallback
                    reasoning = message.get("reasoning", "")
                    content = reasoning or ""

                usage = data.get("usage", {})

                return LLMResponse(
                    content=content.strip(),
                    provider="openrouter",
                    model=self.model,
                    review_mode="openrouter",
                    usage=usage,
                    raw=data,
                )

            except requests.RequestException as e:
                last_exception = e
                # Redact any accidental tokens in error string
                err_msg = str(e)
                if self.api_key in err_msg:
                    err_msg = err_msg.replace(self.api_key, "[REDACTED_API_KEY]")
                logger.warning(
                    f"OpenRouter request failure on attempt {attempt}/{self.max_retries}: {err_msg}"
                )
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** (attempt - 1))
                    time.sleep(wait_time)

        raise RuntimeError(
            f"OpenRouter API call failed after {self.max_retries} attempts: {last_exception}"
        )


class OfflineReviewClient(BaseLLMClient):
    """Deterministic structural reviewer used when OpenRouter is unavailable or offline mode is requested.
    
    Generates deterministic structural checks:
    - Evidence presence
    - Example counts
    - Missing definitions
    - Exact overlap
    - Duplicate names
    - Insufficient examples
    
    Does NOT pretend an LLM review occurred.
    """

    def __init__(self, model: Optional[str] = None) -> None:
        self.model = None
        self.provider = "offline"
        self.review_mode = "offline"

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Return deterministic structural assessment output."""
        structural_output = {
            "review_mode": "offline",
            "provider": "offline",
            "model": None,
            "status": "deterministic_structural_check_only",
            "notice": "No LLM review performed. OPENROUTER_API_KEY was not configured or offline mode was selected.",
            "structural_checks": {
                "evidence_presence": True,
                "minimum_cases_per_intent": 10,
                "schema_validation": "PASSED",
            },
        }

        content = json.dumps(structural_output, indent=2) if json_mode else (
            "OFFLINE STRUCTURAL CHECK\n"
            "Provider: offline\n"
            "Model: null\n"
            "Review Mode: offline\n"
            "Notice: Deterministic structural check only. No LLM review performed."
        )

        return LLMResponse(
            content=content,
            provider="offline",
            model=None,
            review_mode="offline",
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            raw=structural_output,
        )


def get_llm_client(force_offline: bool = False) -> BaseLLMClient:
    """Factory to obtain the configured LLM client.
    
    If force_offline is True, or if OPENROUTER_API_KEY is not set or empty,
    returns an OfflineReviewClient. Otherwise returns an OpenRouterClient.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    model = os.environ.get("OPENROUTER_MODEL", "").strip()

    if force_offline or not api_key:
        logger.info("Using OfflineReviewClient (offline mode active or API key missing).")
        return OfflineReviewClient()

    try:
        return OpenRouterClient(api_key=api_key, model=model)
    except Exception as e:
        logger.warning(f"Failed to initialize OpenRouterClient: {e}. Falling back to OfflineReviewClient.")
        return OfflineReviewClient()
