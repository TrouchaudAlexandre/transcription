import tempfile
import unittest
from pathlib import Path
from unittest import mock

from transcription.application.run_translate import run_translate
from transcription.config.settings import Settings


class RunTranslateTests(unittest.TestCase):
    def test_run_translate_wires_and_executes_use_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            settings = Settings(
                playlist_csv=str(Path(tmp) / "playlists.csv"),
                files_list_csv=str(Path(tmp) / "files_list.csv"),
                log_path=str(Path(tmp) / "log.txt"),
                audio_base_path=str(Path(tmp) / "audio"),
                video_base_path=str(Path(tmp) / "video"),
                segmentation_root=str(Path(tmp) / "segmentation"),
                transcription_root=str(Path(tmp) / "transcription"),
                translation_root=str(Path(tmp) / "translation"),
                output_root=str(Path(tmp) / "output"),
                segment_length_seconds=60,
                whisper_model="large-v3-turbo",
                language="Arabic",
                source_variant="tunisian_arabic",
                target_language="French",
                translation_provider="openai",
                translation_model="gpt-4.1-mini",
                translation_api_key="secret",
                translation_context="keep local references",
                translation_prompt_version="v1",
                use_mock=False,
            )
            with mock.patch(
                "transcription.application.run_translate.TranslateUseCase"
            ) as use_case_cls:
                run_translate(settings)

        use_case_cls.assert_called_once()
        use_case_cls.return_value.execute.assert_called_once()
