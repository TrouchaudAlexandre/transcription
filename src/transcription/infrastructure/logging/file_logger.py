from __future__ import annotations

from datetime import datetime
from pathlib import Path

from transcription.domain.interfaces.logger import Logger


class FileLogger(Logger):
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def info(self, message: str) -> None:
        self._write("INFO", message)

    def error(self, message: str) -> None:
        self._write("ERROR", message)

    def _write(self, level: str, message: str) -> None:
        line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - {message}"
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        print(line)
