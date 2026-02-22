from __future__ import annotations

from pathlib import Path

from transcription.domain.interfaces.logger import Logger
from transcription.domain.interfaces.state_repository import FileState, StateRepository
from transcription.domain.interfaces.transcription_engine import TranscriptionEngine


class TranscribeUseCase:
    AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".aac"}
    TRANSCRIPT_EXTENSIONS = {".srt", ".txt", ".vtt", ".json", ".tsv"}

    def __init__(
        self,
        engine: TranscriptionEngine,
        state_repository: StateRepository,
        logger: Logger,
        segmentation_root: str,
        transcription_root: str,
    ) -> None:
        self._engine = engine
        self._state_repository = state_repository
        self._logger = logger
        self._segmentation_root = Path(segmentation_root)
        self._transcription_root = Path(transcription_root)

    def execute(self) -> None:
        self._transcription_root.mkdir(parents=True, exist_ok=True)

        for state in self._state_repository.list_all():
            audio_path = Path(state.path)
            if not self._is_eligible_audio(state, audio_path):
                continue

            segment_files = self._segment_files_for(audio_path)
            inputs = segment_files if segment_files else [audio_path]
            output_dir = self._output_dir_for(audio_path)

            self._logger.info(f"Transcription start: {audio_path}")
            all_ok = True
            total = len(inputs)
            for idx, input_file in enumerate(inputs, start=1):
                label = f"{input_file.name} ({idx}/{total})"
                if self._has_transcript_for(input_file, output_dir):
                    self._logger.info(f"Transcription skip (already done): {label}")
                    continue

                self._logger.info(f"Transcription segment start: {label}")
                try:
                    self._engine.transcribe(str(input_file), str(output_dir))
                except Exception as exc:  # pylint: disable=broad-except
                    self._logger.error(f"Transcription segment failed: {label}: {exc}")
                    all_ok = False
                    continue

                if self._has_transcript_for(input_file, output_dir):
                    self._logger.info(f"Transcription segment done: {label}")
                else:
                    self._logger.error(
                        f"Transcription segment failed: {label}: missing output artifact"
                    )
                    all_ok = False

            if not all_ok:
                self._logger.error(
                    f"Transcription incomplete for {audio_path}: fix failed segments and rerun."
                )
                continue

            self._logger.info(f"Transcription done: {audio_path} -> {len(inputs)} file(s)")
            self._mark_transcribed(str(audio_path))
            self._mark_related_video_transcribed(audio_path)

    def _is_eligible_audio(self, state: FileState, audio_path: Path) -> bool:
        return (
            state.downloaded
            and state.segmented
            and not state.transcribed
            and audio_path.suffix.lower() in self.AUDIO_EXTENSIONS
        )

    def _segment_files_for(self, audio_path: Path) -> list[Path]:
        segment_dir = self._segmentation_root / audio_path.parent.name / audio_path.name
        if not segment_dir.exists():
            return []
        return sorted([p for p in segment_dir.iterdir() if p.is_file()])

    def _output_dir_for(self, audio_path: Path) -> Path:
        return self._transcription_root / audio_path.parent.name / audio_path.name

    def _has_transcript_for(self, input_file: Path, output_dir: Path) -> bool:
        if not output_dir.exists():
            return False
        stem = input_file.stem
        for candidate in output_dir.glob(f"{stem}.*"):
            if candidate.suffix.lower() in self.TRANSCRIPT_EXTENSIONS:
                return True
        return False

    def _mark_transcribed(self, path: str) -> None:
        current = self._state_repository.get(path)
        if current is None:
            return
        self._state_repository.upsert(
            FileState(
                path=current.path,
                downloaded=current.downloaded,
                segmented=current.segmented,
                transcribed=True,
            )
        )

    def _mark_related_video_transcribed(self, audio_path: Path) -> None:
        video_path = str(audio_path.with_suffix(".mp4"))
        current = self._state_repository.get(video_path)
        if current is None:
            return
        self._state_repository.upsert(
            FileState(
                path=current.path,
                downloaded=current.downloaded,
                segmented=current.segmented,
                transcribed=True,
            )
        )
