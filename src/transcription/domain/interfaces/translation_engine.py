from __future__ import annotations

from abc import ABC, abstractmethod


class TranslationEngine(ABC):
    @abstractmethod
    def translate_srt_segment(
        self,
        source_srt: str,
        source_language: str,
        source_variant: str,
        target_language: str,
        translation_context: str,
    ) -> str:
        raise NotImplementedError
