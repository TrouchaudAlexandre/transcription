from __future__ import annotations

from transcription.application.merge_use_case import MergeUseCase
from transcription.config.settings import Settings
from transcription.infrastructure.logging.file_logger import FileLogger
from transcription.infrastructure.state.csv_state_repository import CsvStateRepository


def run_merge(settings: Settings) -> None:
    logger = FileLogger(settings.log_path)
    state_repository = CsvStateRepository(settings.files_list_csv)

    source_use_case = MergeUseCase(
        state_repository=state_repository,
        logger=logger,
        input_root=settings.transcription_root,
        output_root=settings.output_root,
        segment_length_seconds=settings.segment_length_seconds,
        require_translated=False,
        output_suffix="",
        merge_label="source",
    )
    translated_use_case = MergeUseCase(
        state_repository=state_repository,
        logger=logger,
        input_root=settings.translation_root,
        output_root=settings.output_root,
        segment_length_seconds=settings.segment_length_seconds,
        require_translated=True,
        output_suffix=f"_{_normalize_label(settings.target_language)}",
        merge_label="translated",
    )
    source_use_case.execute()
    translated_use_case.execute()


def _normalize_label(value: str) -> str:
    return value.strip().lower().replace(" ", "_")
