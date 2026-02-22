from __future__ import annotations

from pathlib import Path

from transcription.domain.interfaces.audio_segmenter import AudioSegmenter
from transcription.domain.interfaces.logger import Logger
from transcription.domain.interfaces.state_repository import FileState, StateRepository


class SegmentUseCase:
    AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".aac"}

    def __init__(
        self,
        segmenter: AudioSegmenter,
        state_repository: StateRepository,
        logger: Logger,
        segmentation_root: str,
    ) -> None:
        self._segmenter = segmenter
        self._state_repository = state_repository
        self._logger = logger
        self._segmentation_root = Path(segmentation_root)

    def execute(self) -> None:
        self._segmentation_root.mkdir(parents=True, exist_ok=True)

        for state in self._state_repository.list_all():
            audio_path = Path(state.path)
            if not self._is_eligible_audio(state, audio_path):
                continue

            output_dir = self._build_output_dir(audio_path)
            self._logger.info(f"Segmentation start: {audio_path}")
            try:
                segments = self._segmenter.split(str(audio_path), str(output_dir))
            except Exception as exc:  # pylint: disable=broad-except
                self._logger.error(f"Segmentation failed for {audio_path}: {exc}")
                continue

            self._logger.info(
                f"Segmentation done: {audio_path} -> {len(segments)} segments"
            )
            self._mark_segmented(str(audio_path))
            self._mark_related_video_segmented(audio_path)

    def _is_eligible_audio(self, state: FileState, audio_path: Path) -> bool:
        return (
            state.downloaded
            and not state.segmented
            and audio_path.suffix.lower() in self.AUDIO_EXTENSIONS
        )

    def _build_output_dir(self, audio_path: Path) -> Path:
        playlist_dir = audio_path.parent.name
        file_dir = audio_path.name
        return self._segmentation_root / playlist_dir / file_dir

    def _mark_segmented(self, path: str) -> None:
        current = self._state_repository.get(path)
        if current is None:
            return
        self._state_repository.upsert(
            FileState(
                path=current.path,
                downloaded=current.downloaded,
                segmented=True,
                transcribed=current.transcribed,
            )
        )

    def _mark_related_video_segmented(self, audio_path: Path) -> None:
        video_path = str(audio_path.with_suffix(".mp4"))
        current = self._state_repository.get(video_path)
        if current is None:
            return
        self._state_repository.upsert(
            FileState(
                path=current.path,
                downloaded=current.downloaded,
                segmented=True,
                transcribed=current.transcribed,
            )
        )
