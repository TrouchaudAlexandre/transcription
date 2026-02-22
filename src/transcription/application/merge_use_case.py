from __future__ import annotations

import re
from pathlib import Path

from transcription.domain.interfaces.logger import Logger
from transcription.domain.interfaces.state_repository import FileState, StateRepository


class MergeUseCase:
    AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".aac"}
    PART_PATTERN = re.compile(r"_part_(\d+)")
    TIMECODE_PATTERN = re.compile(
        r"^(\d{2}:\d{2}:\d{2},\d{3})\s-->\s(\d{2}:\d{2}:\d{2},\d{3})$"
    )

    def __init__(
        self,
        state_repository: StateRepository,
        logger: Logger,
        transcription_root: str,
        output_root: str,
        segment_length_seconds: int,
    ) -> None:
        self._state_repository = state_repository
        self._logger = logger
        self._transcription_root = Path(transcription_root)
        self._output_root = Path(output_root)
        self._segment_length_seconds = segment_length_seconds

    def execute(self) -> None:
        self._output_root.mkdir(parents=True, exist_ok=True)

        for state in self._state_repository.list_all():
            audio_path = Path(state.path)
            if not self._is_eligible_audio(state, audio_path):
                continue

            srt_files = self._find_srt_files(audio_path)
            if not srt_files:
                self._logger.info(f"Merge skipped (no srt): {audio_path}")
                continue

            merged_content = self._merge_files(srt_files)
            output_path = self._output_path_for(audio_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(merged_content.strip() + "\n", encoding="utf-8")
            self._logger.info(f"Merge done: {output_path}")

    def _is_eligible_audio(self, state: FileState, audio_path: Path) -> bool:
        return state.transcribed and audio_path.suffix.lower() in self.AUDIO_EXTENSIONS

    def _find_srt_files(self, audio_path: Path) -> list[Path]:
        root = self._transcription_root / audio_path.parent.name / audio_path.name
        if not root.exists():
            return []

        files = [p for p in root.iterdir() if p.is_file() and p.suffix.lower() == ".srt"]
        return sorted(files, key=self._srt_sort_key)

    def _output_path_for(self, audio_path: Path) -> Path:
        playlist_name = audio_path.parent.name
        output_name = f"{audio_path.stem}_sous-titres_complets.srt"
        return self._output_root / playlist_name / output_name

    def _merge_files(self, srt_files: list[Path]) -> str:
        lines: list[str] = []
        entry_counter = 1

        for srt_file in srt_files:
            offset_seconds = self._offset_for_file(srt_file)
            content = srt_file.read_text(encoding="utf-8").splitlines()

            for line in content:
                stripped = line.strip()
                if stripped.isdigit():
                    lines.append(str(entry_counter))
                    entry_counter += 1
                    continue

                timecode = self.TIMECODE_PATTERN.match(stripped)
                if timecode:
                    start = self._shift_timecode(timecode.group(1), offset_seconds)
                    end = self._shift_timecode(timecode.group(2), offset_seconds)
                    lines.append(f"{start} --> {end}")
                    continue

                lines.append(line)

            lines.append("")

        return "\n".join(lines)

    def _offset_for_file(self, srt_file: Path) -> float:
        part = self._extract_part_number(srt_file.name)
        if part <= 1:
            return 0.0
        return float((part - 1) * self._segment_length_seconds)

    @classmethod
    def _extract_part_number(cls, filename: str) -> int:
        match = cls.PART_PATTERN.search(filename)
        if match is None:
            return 0
        return int(match.group(1))

    @classmethod
    def _srt_sort_key(cls, path: Path) -> tuple[int, str]:
        part = cls._extract_part_number(path.name)
        return (part, path.name)

    @staticmethod
    def _shift_timecode(value: str, offset_seconds: float) -> str:
        hours, minutes, seconds_ms = value.split(":")
        seconds, milliseconds = seconds_ms.split(",")
        total_seconds = (
            int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
        )
        shifted = total_seconds + offset_seconds

        out_hours = int(shifted // 3600)
        out_minutes = int((shifted % 3600) // 60)
        out_seconds = int(shifted % 60)
        out_milliseconds = int(round((shifted - int(shifted)) * 1000))

        if out_milliseconds == 1000:
            out_milliseconds = 0
            out_seconds += 1
        if out_seconds == 60:
            out_seconds = 0
            out_minutes += 1
        if out_minutes == 60:
            out_minutes = 0
            out_hours += 1

        return (
            f"{out_hours:02d}:{out_minutes:02d}:{out_seconds:02d},{out_milliseconds:03d}"
        )
