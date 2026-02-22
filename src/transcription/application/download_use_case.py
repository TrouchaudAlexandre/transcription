from __future__ import annotations

from pathlib import Path

from transcription.domain.interfaces.logger import Logger
from transcription.domain.interfaces.media_source import MediaSource
from transcription.domain.interfaces.state_repository import FileState, StateRepository


class DownloadUseCase:
    def __init__(
        self,
        source: MediaSource,
        state_repository: StateRepository,
        logger: Logger,
    ) -> None:
        self._source = source
        self._state_repository = state_repository
        self._logger = logger

    def execute(self) -> None:
        for item in self._source.list_videos():
            resolved = self._source.resolve_paths(item)
            audio_state = self._state_repository.get(resolved.audio_path)
            video_state = self._state_repository.get(resolved.video_path)

            already_done = (
                audio_state is not None
                and video_state is not None
                and audio_state.downloaded
                and video_state.downloaded
                and Path(resolved.audio_path).exists()
                and Path(resolved.video_path).exists()
            )
            if already_done:
                self._logger.info(
                    f"Skip download (already done): {item.playlist_title} #{item.index}"
                )
                continue

            self._logger.info(f"Download start: {item.playlist_title} #{item.index}")

            try:
                result = self._source.download_video(item)
            except Exception as exc:  # pylint: disable=broad-except
                self._logger.error(
                    f"Download failed for {item.video_url} ({item.playlist_title}#{item.index}): {exc}"
                )
                continue

            self._upsert_downloaded(result.audio_path)
            self._upsert_downloaded(result.video_path)
            self._logger.info(
                f"Download done: audio={result.audio_path} video={result.video_path}"
            )

    def _upsert_downloaded(self, path: str) -> None:
        current = self._state_repository.get(path)
        self._state_repository.upsert(
            FileState(
                path=path,
                downloaded=True,
                segmented=current.segmented if current else False,
                transcribed=current.transcribed if current else False,
            )
        )
