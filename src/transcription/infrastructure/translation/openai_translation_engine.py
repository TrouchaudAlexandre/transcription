from __future__ import annotations

from transcription.domain.interfaces.translation_engine import TranslationEngine


class OpenAITranslationEngine(TranslationEngine):
    def __init__(
        self,
        model: str,
        api_key: str,
        prompt_version: str = "v1",
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._prompt_version = prompt_version

    def translate_srt_segment(
        self,
        source_srt: str,
        source_language: str,
        source_variant: str,
        target_language: str,
        translation_context: str,
    ) -> str:
        client = self._create_client()
        response = client.responses.create(
            model=self._model,
            instructions=self._instructions(
                source_language,
                source_variant,
                target_language,
                translation_context,
            ),
            input=source_srt,
        )
        output_text = getattr(response, "output_text", "").strip()
        if not output_text:
            raise RuntimeError("OpenAI translation returned an empty response")
        return self._sanitize_output(output_text)

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
