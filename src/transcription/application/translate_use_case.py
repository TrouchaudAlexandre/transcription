from __future__ import annotations

from pathlib import Path

from transcription.domain.interfaces.logger import Logger
from transcription.domain.interfaces.srt_validator import SrtValidator
from transcription.domain.interfaces.state_repository import FileState, StateRepository
from transcription.domain.interfaces.translation_engine import TranslationEngine


class TranslateUseCase:
    AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".aac"}

    def __init__(
        self,
        engine: TranslationEngine,
        validator: SrtValidator,
        state_repository: StateRepository,
        logger: Logger,
        transcription_root: str,
        translation_root: str,
        source_language: str,
        source_variant: str,
        target_language: str,
        translation_context: str,
    ) -> None:
        self._engine = engine
        self._validator = validator
        self._state_repository = state_repository
        self._logger = logger
        self._transcription_root = Path(transcription_root)
        self._translation_root = Path(translation_root)
        self._source_language = source_language
        self._source_variant = source_variant
        self._target_language = target_language
        self._translation_context = translation_context

    def execute(self) -> None:
        self._translation_root.mkdir(parents=True, exist_ok=True)

        for state in self._state_repository.list_all():
            audio_path = Path(state.path)
            if not self._is_eligible_audio(state, audio_path):
                continue

            source_segments = self._source_segments_for(audio_path)
            if not source_segments:
                self._logger.info(f"Translation skipped (no source srt): {audio_path}")
                continue

            output_dir = self._output_dir_for(audio_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            self._logger.info(f"Translation start: {audio_path}")

            all_ok = True
            total = len(source_segments)
            for idx, source_file in enumerate(source_segments, start=1):
                label = f"{source_file.name} ({idx}/{total})"
                output_file = output_dir / source_file.name
                if output_file.exists() and output_file.stat().st_size > 0:
                    self._logger.info(f"Translation skip (already done): {label}")
                    continue

                self._logger.info(f"Translation segment start: {label}")
                try:
                    source_srt = source_file.read_text(encoding="utf-8")
                    translated = self._engine.translate_srt_segment(
                        source_srt=source_srt,
                        source_language=self._source_language,
                        source_variant=self._source_variant,
                        target_language=self._target_language,
                        translation_context=self._translation_context,
                    )
                    self._validator.validate_pair(source_srt, translated)
                    output_file.write_text(translated.strip() + "\n", encoding="utf-8")
                except Exception as exc:  # pylint: disable=broad-except
                    self._logger.error(f"Translation segment failed: {label}: {exc}")
                    all_ok = False
                    continue

                if output_file.exists() and output_file.stat().st_size > 0:
                    self._logger.info(f"Translation segment done: {label}")
                else:
                    self._logger.error(
                        f"Translation segment failed: {label}: missing output artifact"
                    )
                    all_ok = False

            if not all_ok:
                self._logger.error(
                    f"Translation incomplete for {audio_path}: fix failed segments and rerun."
                )
                continue

            self._logger.info(f"Translation done: {audio_path} -> {len(source_segments)} file(s)")
            self._mark_translated(str(audio_path))
            self._mark_related_video_translated(audio_path)

    def _is_eligible_audio(self, state: FileState, audio_path: Path) -> bool:
        return (
            state.downloaded
            and state.segmented
            and state.transcribed
            and not state.translated
            and audio_path.suffix.lower() in self.AUDIO_EXTENSIONS
        )

    def _source_segments_for(self, audio_path: Path) -> list[Path]:
        root = self._transcription_root / audio_path.parent.name / audio_path.name
        if not root.exists():
            return []
        return sorted(
            [item for item in root.iterdir() if item.is_file() and item.suffix.lower() == ".srt"]
        )

    def _output_dir_for(self, audio_path: Path) -> Path:
        return self._translation_root / audio_path.parent.name / audio_path.name

    def _mark_translated(self, path: str) -> None:
        current = self._state_repository.get(path)
        if current is None:
            return
        self._state_repository.upsert(
            FileState(
                path=current.path,
                downloaded=current.downloaded,
                segmented=current.segmented,
                transcribed=current.transcribed,
                translated=True,
            )
        )

    def _mark_related_video_translated(self, audio_path: Path) -> None:
        video_path = str(audio_path.with_suffix(".mp4"))
        current = self._state_repository.get(video_path)
        if current is None:
            return
        self._state_repository.upsert(
            FileState(
                path=current.path,
                downloaded=current.downloaded,
                segmented=current.segmented,
                transcribed=current.transcribed,
                translated=True,
            )
        )
