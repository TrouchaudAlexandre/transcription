from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence


class AudioSegmenter(ABC):
    @abstractmethod
    def split(self, input_audio_path: str, output_directory: str) -> Sequence[str]:
        raise NotImplementedError
