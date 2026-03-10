from __future__ import annotations

from transcription.domain.interfaces.translation_engine import TranslationEngine
from transcription.infrastructure.translation.retry_policy import (
    execute_with_retry,
    is_retryable_http_error,
)


class GeminiTranslationEngine(TranslationEngine):
    def __init__(
        self,
        model: str,
        api_key: str,
        prompt_version: str = "v1",
        max_retries: int = 3,
        retry_base_delay_seconds: float = 2.0,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._prompt_version = prompt_version
        self._max_retries = max_retries
        self._retry_base_delay_seconds = retry_base_delay_seconds

    def translate_srt_segment(
        self,
        source_srt: str,
        source_language: str,
        source_variant: str,
        target_language: str,
        translation_context: str,
    ) -> str:
        client, types = self._create_client()
        response = execute_with_retry(
            operation=lambda: client.models.generate_content(
                model=self._model,
                contents=source_srt,
                config=types.GenerateContentConfig(
                    system_instruction=self._instructions(
                        source_language,
                        source_variant,
                        target_language,
                        translation_context,
                    ),
                    temperature=0.1,
                ),
            ),
            max_retries=self._max_retries,
            base_delay_seconds=self._retry_base_delay_seconds,
            is_retryable=is_retryable_http_error,
        )
        output_text = getattr(response, "text", "").strip()
        if not output_text:
            raise RuntimeError("Gemini translation returned an empty response")
        return self._sanitize_output(output_text)

    def _create_client(self):
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "google-genai package is required for Gemini translation"
            ) from exc

        if self._api_key:
            return genai.Client(api_key=self._api_key), types
        return genai.Client(), types

    def _instructions(
        self,
        source_language: str,
        source_variant: str,
        target_language: str,
        translation_context: str,
    ) -> str:
        normalized_source = source_language or "the source language"
        variant_clause = ""
        if source_variant.strip():
            variant_clause = f" The source variant/dialect is {source_variant.strip()}."
        context_clause = ""
        if translation_context.strip():
            context_clause = f" Additional translation context: {translation_context.strip()}."
        return (
            f"You are an SRT subtitle translator. Prompt version: {self._prompt_version}. "
            f"Translate subtitle text from {normalized_source} to {target_language}. "
            f"{variant_clause}"
            f"{context_clause}"
            "Keep the SRT structure exactly intact. Do not change entry numbering. "
            "Do not change timestamps. Translate only subtitle text lines. "
            "Return only valid SRT content, with no markdown fences and no commentary."
        )

    @staticmethod
    def _sanitize_output(value: str) -> str:
        cleaned = value.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        return cleaned
