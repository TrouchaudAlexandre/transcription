from __future__ import annotations

from transcription.application.download_use_case import DownloadUseCase
from transcription.config.settings import Settings
from transcription.infrastructure.logging.file_logger import FileLogger
from transcription.infrastructure.sources.youtube_pytube_source import YouTubePytubeSource
from transcription.infrastructure.state.csv_state_repository import CsvStateRepository


def run_download(settings: Settings) -> None:
    logger = FileLogger(settings.log_path)
    state_repository = CsvStateRepository(settings.files_list_csv)
    source = YouTubePytubeSource(
        playlist_csv=settings.playlist_csv,
        audio_base_path=settings.audio_base_path,
        video_base_path=settings.video_base_path,
        logger=logger,
    )

    use_case = DownloadUseCase(
        source=source,
        state_repository=state_repository,
        logger=logger,
    )
    use_case.execute()
