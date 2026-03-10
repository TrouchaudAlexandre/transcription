from __future__ import annotations

import time

from transcription.domain.interfaces.translation_engine import TranslationEngine


class OpenAITranslationEngine(TranslationEngine):
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
        self._max_retries = max(0, max_retries)
        self._retry_base_delay_seconds = max(0.0, retry_base_delay_seconds)

    def translate_srt_segment(
        self,
        source_srt: str,
        source_language: str,
        source_variant: str,
        target_language: str,
        translation_context: str,
    ) -> str:
        client = self._create_client()
        response = self._create_response(
            client=client,
            source_srt=source_srt,
            source_language=source_language,
            source_variant=source_variant,
            target_language=target_language,
            translation_context=translation_context,
        )
        output_text = getattr(response, "output_text", "").strip()
        if not output_text:
            raise RuntimeError("OpenAI translation returned an empty response")
        return self._sanitize_output(output_text)

    def _create_response(
        self,
        client,
        source_srt: str,
        source_language: str,
        source_variant: str,
        target_language: str,
        translation_context: str,
    ):
        for attempt in range(self._max_retries + 1):
            try:
                return client.responses.create(
                    model=self._model,
                    instructions=self._instructions(
                        source_language,
                        source_variant,
                        target_language,
                        translation_context,
                    ),
                    input=source_srt,
                )
            except Exception as exc:
                if not self._is_retryable_error(exc) or attempt >= self._max_retries:
                    raise
                time.sleep(self._retry_delay_seconds(attempt))
        raise RuntimeError("OpenAI translation retry loop exited unexpectedly")

    def _create_client(self):
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("openai package is required for GPT translation") from exc

        if self._api_key:
            return OpenAI(api_key=self._api_key)
        return OpenAI()

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

    def _retry_delay_seconds(self, attempt: int) -> float:
        return self._retry_base_delay_seconds * (2**attempt)

    @staticmethod
    def _is_retryable_error(exc: Exception) -> bool:
        status_code = getattr(exc, "status_code", None)
        if status_code is None:
            status_code = getattr(exc, "status", None)
        if status_code in (408, 409, 429):
            return True
        if isinstance(status_code, int) and status_code >= 500:
            return True

        message = str(exc).lower()
        retryable_markers = (
            "timeout",
            "temporarily unavailable",
            "connection",
            "rate limit",
            "server error",
        )
        return any(marker in message for marker in retryable_markers)
