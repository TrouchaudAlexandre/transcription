from __future__ import annotations

from transcription.application.translate_use_case import TranslateUseCase
from transcription.config.settings import Settings
from transcription.infrastructure.logging.file_logger import FileLogger
from transcription.infrastructure.state.csv_state_repository import CsvStateRepository
from transcription.infrastructure.translation.srt_validator import DeterministicSrtValidator
from transcription.infrastructure.translation.translation_engine_factory import (
    TranslationEngineFactory,
)


def run_translate(settings: Settings) -> None:
    logger = FileLogger(settings.log_path)
    state_repository = CsvStateRepository(settings.files_list_csv)
    engine = TranslationEngineFactory.create(settings)
    validator = DeterministicSrtValidator()

    use_case = TranslateUseCase(
        engine=engine,
        validator=validator,
        state_repository=state_repository,
        logger=logger,
        transcription_root=settings.transcription_root,
        translation_root=settings.translation_root,
        source_language=settings.language,
        source_variant=settings.source_variant,
        target_language=settings.target_language,
        translation_context=settings.translation_context,
    )
    use_case.execute()
