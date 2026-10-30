from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.config import settings


class OpenAIService:
    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        self.model = model or settings.OPENAI_MODEL
        self.base_url = base_url or settings.OPENAI_BASE_URL
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate_text(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.responses.create(
            model=self.model,
            input=messages,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        return getattr(response, "output_text", "")

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
