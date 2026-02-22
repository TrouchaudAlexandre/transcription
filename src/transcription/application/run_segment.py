from __future__ import annotations

from transcription.application.segment_use_case import SegmentUseCase
from transcription.config.settings import Settings
from transcription.infrastructure.logging.file_logger import FileLogger
from transcription.infrastructure.segmentation.ffmpeg_segmenter import FfmpegSegmenter
from transcription.infrastructure.state.csv_state_repository import CsvStateRepository


def run_segment(settings: Settings) -> None:
    logger = FileLogger(settings.log_path)
    state_repository = CsvStateRepository(settings.files_list_csv)
    segmenter = FfmpegSegmenter(segment_length_seconds=settings.segment_length_seconds)

    use_case = SegmentUseCase(
        segmenter=segmenter,
        state_repository=state_repository,
        logger=logger,
        segmentation_root=settings.segmentation_root,
    )
    use_case.execute()
