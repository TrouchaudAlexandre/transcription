from __future__ import annotations

from transcription.application.transcribe_use_case import TranscribeUseCase
from transcription.config.settings import Settings
from transcription.infrastructure.logging.file_logger import FileLogger
from transcription.infrastructure.state.csv_state_repository import CsvStateRepository
from transcription.infrastructure.transcription.whisper_engine import WhisperEngine


def run_transcribe(settings: Settings) -> None:
    logger = FileLogger(settings.log_path)
    state_repository = CsvStateRepository(settings.files_list_csv)
    engine = WhisperEngine(model=settings.whisper_model, language=settings.language)

    use_case = TranscribeUseCase(
        engine=engine,
        state_repository=state_repository,
        logger=logger,
        segmentation_root=settings.segmentation_root,
        transcription_root=settings.transcription_root,
    )
    use_case.execute()
