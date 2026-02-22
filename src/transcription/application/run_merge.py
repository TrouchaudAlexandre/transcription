from __future__ import annotations

from transcription.application.merge_use_case import MergeUseCase
from transcription.config.settings import Settings
from transcription.infrastructure.logging.file_logger import FileLogger
from transcription.infrastructure.state.csv_state_repository import CsvStateRepository


def run_merge(settings: Settings) -> None:
    logger = FileLogger(settings.log_path)
    state_repository = CsvStateRepository(settings.files_list_csv)

    use_case = MergeUseCase(
        state_repository=state_repository,
        logger=logger,
        transcription_root=settings.transcription_root,
        output_root=settings.output_root,
        segment_length_seconds=settings.segment_length_seconds,
    )
    use_case.execute()
