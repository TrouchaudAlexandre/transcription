import tempfile
import unittest
from pathlib import Path

from transcription.config.settings import Settings
from transcription.infrastructure.translation.openai_translation_engine import (
    OpenAITranslationEngine,
)
from transcription.infrastructure.translation.translation_engine_factory import (
    TranslationEngineFactory,
)


class TranslationEngineFactoryTests(unittest.TestCase):
    def test_create_returns_openai_engine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            settings = Settings(
                playlist_csv=str(Path(tmp) / "playlists.csv"),
                files_list_csv=str(Path(tmp) / "files.csv"),
                log_path=str(Path(tmp) / "log.txt"),
                audio_base_path=str(Path(tmp) / "audio"),
                video_base_path=str(Path(tmp) / "video"),
                segmentation_root=str(Path(tmp) / "seg"),
                transcription_root=str(Path(tmp) / "tr"),
                translation_root=str(Path(tmp) / "translation"),
                output_root=str(Path(tmp) / "output"),
                segment_length_seconds=60,
                whisper_model="large-v3-turbo",
                language="Arabic",
                source_variant="",
                target_language="French",
                translation_provider="openai",
                translation_model="gpt-4.1-mini",
                translation_api_key="secret",
                translation_context="",
                translation_prompt_version="v1",
                use_mock=False,
            )

            engine = TranslationEngineFactory.create(settings)

        self.assertIsInstance(engine, OpenAITranslationEngine)

    def test_create_rejects_unknown_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            settings = Settings(
                playlist_csv=str(Path(tmp) / "playlists.csv"),
                files_list_csv=str(Path(tmp) / "files.csv"),
                log_path=str(Path(tmp) / "log.txt"),
                audio_base_path=str(Path(tmp) / "audio"),
                video_base_path=str(Path(tmp) / "video"),
                segmentation_root=str(Path(tmp) / "seg"),
                transcription_root=str(Path(tmp) / "tr"),
                translation_root=str(Path(tmp) / "translation"),
                output_root=str(Path(tmp) / "output"),
                segment_length_seconds=60,
                whisper_model="large-v3-turbo",
                language="Arabic",
                source_variant="",
                target_language="French",
                translation_provider="gemini",
                translation_model="gemini-2.0-flash",
                translation_api_key="secret",
                translation_context="",
                translation_prompt_version="v1",
                use_mock=False,
            )

            with self.assertRaises(RuntimeError):
                TranslationEngineFactory.create(settings)


if __name__ == "__main__":
    unittest.main()
