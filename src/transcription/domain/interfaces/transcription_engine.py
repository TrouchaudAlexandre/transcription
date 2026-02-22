from __future__ import annotations

from abc import ABC, abstractmethod


class TranscriptionEngine(ABC):
    @abstractmethod
    def transcribe(self, input_audio_path: str, output_directory: str) -> None:
        raise NotImplementedError
