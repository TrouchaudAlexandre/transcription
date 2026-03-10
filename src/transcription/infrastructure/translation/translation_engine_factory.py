from __future__ import annotations

from transcription.config.settings import Settings
from transcription.domain.interfaces.translation_engine import TranslationEngine
from transcription.infrastructure.translation.openai_translation_engine import (
    OpenAITranslationEngine,
)


class TranslationEngineFactory:
    @staticmethod
    def create(settings: Settings) -> TranslationEngine:
        provider = settings.translation_provider.strip().lower()
        if provider == "openai":
            return OpenAITranslationEngine(
                model=settings.translation_model,
                api_key=settings.translation_api_key,
                prompt_version=settings.translation_prompt_version,
                max_retries=settings.translation_max_retries,
                retry_base_delay_seconds=settings.translation_retry_base_delay_seconds,
            )
        raise RuntimeError(f"Unsupported translation provider: {settings.translation_provider}")
