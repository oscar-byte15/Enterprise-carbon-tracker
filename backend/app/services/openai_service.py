from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI, OpenAIError

from app.config import settings

logger = logging.getLogger(__name__)


def _mask_key(key: str | None) -> str:
    if not key:
        return "<None>"
    if len(key) <= 4:
        return "****"
    return f"...{key[-4:]}"


class OpenAIService:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.base_url = base_url or settings.OPENAI_BASE_URL
        self.client: OpenAI | None = None

        key_detected = bool(self.api_key)
        masked = _mask_key(self.api_key)
        logger.info(
            "[OpenAI Debug] Init: API key detected=%s (masked: %s), Model=%s, Base URL=%s",
            key_detected,
            masked,
            self.model,
            self.base_url or "<default>",
        )

        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                logger.info("[OpenAI Debug] OpenAI client successfully created: True")
            except Exception as err:
                logger.exception("[OpenAI Debug] Failed to initialize OpenAI client: %s", err)
                self.client = None
        else:
            logger.warning("[OpenAI Debug] OpenAI client NOT created (no API key configured)")

    @property
    def is_available(self) -> bool:
        available = self.client is not None and bool(self.api_key)
        logger.debug("[OpenAI Debug] is_available evaluated to: %s", available)
        return available

    def generate_text(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        if not self.is_available or self.client is None:
            logger.error(
                "[OpenAI Debug] generate_text aborted: client unavailable or key missing. Key detected: %s",
                bool(self.api_key),
            )
            raise RuntimeError("OPENAI_API_KEY is not configured or client failed to initialize.")

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        logger.info(
            "[OpenAI Debug] Attempting API request via chat.completions.create (model=%s, temp=%.2f, max_tokens=%s)",
            self.model,
            temperature,
            max_tokens,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
                max_tokens=max_tokens,
            )
            choice = response.choices[0] if response.choices else None
            content = choice.message.content.strip() if choice and choice.message.content else ""
            logger.info("[OpenAI Debug] API request succeeded. Received %d characters.", len(content))
            return content
        except OpenAIError as exc:
            logger.exception("[OpenAI Debug] OpenAI API call failed with OpenAIError: %s", exc)
            raise RuntimeError(f"OpenAI completion error: {exc}") from exc
        except Exception as exc:
            logger.exception("[OpenAI Debug] OpenAI API call failed with unexpected exception: %s", exc)
            raise RuntimeError(f"OpenAI unexpected error: {exc}") from exc

    def generate_enterprise_summary(self, company_name: str, industry: str, departments: list[str]) -> str:
        prompt = (
            f"Company: {company_name}\n"
            f"Industry: {industry}\n"
            f"Departments: {', '.join(departments) if departments else 'Not provided'}\n\n"
            "Provide a compact executive summary for the company profile and operations setup."
        )
        return self.generate_text(
            prompt,
            system_prompt="You are an enterprise carbon tracking operations assistant. Keep the answer concise, business-oriented, and useful for a sustainability dashboard.",
        )


def get_openai_client() -> OpenAI:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    return OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)


def generate_text(prompt: str, *, system_prompt: str | None = None, model: str | None = None) -> str:
    service = OpenAIService(model=model)
    return service.generate_text(prompt, system_prompt=system_prompt)

