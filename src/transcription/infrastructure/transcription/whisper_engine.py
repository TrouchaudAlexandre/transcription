from __future__ import annotations

import subprocess
from pathlib import Path

from transcription.domain.interfaces.transcription_engine import TranscriptionEngine


class WhisperEngine(TranscriptionEngine):
    def __init__(self, model: str, language: str) -> None:
        self._model = model
        self._language = language

    def transcribe(self, input_audio_path: str, output_directory: str) -> None:
        Path(output_directory).mkdir(parents=True, exist_ok=True)
        command = [
            "whisper",
            input_audio_path,
            "--language",
            self._language,
            "--model",
            self._model,
            "--output_dir",
            output_directory,
        ]
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
