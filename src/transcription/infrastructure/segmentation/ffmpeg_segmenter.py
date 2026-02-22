from __future__ import annotations

import math
import subprocess
from pathlib import Path
from typing import Sequence

from transcription.domain.interfaces.audio_segmenter import AudioSegmenter


class FfmpegSegmenter(AudioSegmenter):
    def __init__(self, segment_length_seconds: int) -> None:
        self._segment_length_seconds = segment_length_seconds

    def split(self, input_audio_path: str, output_directory: str) -> Sequence[str]:
        input_path = Path(input_audio_path)
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        duration = self._probe_duration_seconds(input_path)
        parts = max(1, math.ceil(duration / self._segment_length_seconds))

        output_files: list[str] = []
        stem = input_path.stem
        suffix = input_path.suffix or ".m4a"
        for idx in range(parts):
            start = idx * self._segment_length_seconds
            output_path = output_dir / f"{stem}_part_{idx + 1}{suffix}"
            command = [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-ss",
                str(start),
                "-t",
                str(self._segment_length_seconds),
                "-vn",
                "-acodec",
                "copy",
                str(output_path),
            ]
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            output_files.append(str(output_path))

        return output_files

    @staticmethod
    def _probe_duration_seconds(path: Path) -> float:
        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        return float(result.stdout.strip())
