from __future__ import annotations

from abc import ABC, abstractmethod


class SrtValidator(ABC):
    @abstractmethod
    def validate_pair(self, source_srt: str, translated_srt: str) -> None:
        raise NotImplementedError
