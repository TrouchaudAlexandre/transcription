import os
import unittest
from unittest import mock

from transcription.config.settings import load_settings, override_settings


class SettingsTests(unittest.TestCase):
    def test_load_settings_reads_env(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "PLAYLIST_CSV": "/tmp/playlists.csv",
                "FILES_LIST_CSV": "/tmp/files.csv",
                "SEGMENT_LENGTH_SECONDS": "90",
                "USE_MOCK": "true",
                "WHISPER_LANGUAGE": "French",
                "SOURCE_VARIANT": "tunisian_arabic",
                "TRANSLATION_ROOT": "/tmp/translation",
                "TARGET_LANGUAGE": "English",
                "TRANSLATION_PROVIDER": "mistral",
                "TRANSLATION_MODEL": "gpt-test",
                "TRANSLATION_MAX_RETRIES": "3",
                "TRANSLATION_RETRY_BASE_DELAY_SECONDS": "2.0",
                "TRANSLATION_CONTEXT": "dialect content",
            },
            clear=False,
        ):
            settings = load_settings()

        self.assertEqual(settings.playlist_csv, "/tmp/playlists.csv")
        self.assertEqual(settings.files_list_csv, "/tmp/files.csv")
        self.assertEqual(settings.segment_length_seconds, 90)
        self.assertTrue(settings.use_mock)
        self.assertEqual(settings.language, "French")
        self.assertEqual(settings.source_variant, "tunisian_arabic")
        self.assertEqual(settings.translation_root, "/tmp/translation")
        self.assertEqual(settings.target_language, "English")
        self.assertEqual(settings.translation_provider, "mistral")
        self.assertEqual(settings.translation_model, "gpt-test")
        self.assertEqual(settings.translation_max_retries, 3)
        self.assertEqual(settings.translation_retry_base_delay_seconds, 2.0)
        self.assertEqual(settings.translation_context, "dialect content")

    def test_override_settings_applies_types(self) -> None:
        settings = load_settings()
        updated = override_settings(
            settings,
            segment_length_seconds="30",
            use_mock="true",
            whisper_model="tiny",
            source_variant="levantine_arabic",
            target_language="Spanish",
            translation_provider="gemini",
            translation_max_retries="5",
            translation_retry_base_delay_seconds="1.5",
            translation_context="keep local idioms natural",
        )

        self.assertEqual(updated.segment_length_seconds, 30)
        self.assertTrue(updated.use_mock)
        self.assertEqual(updated.whisper_model, "tiny")
        self.assertEqual(updated.source_variant, "levantine_arabic")
        self.assertEqual(updated.target_language, "Spanish")
        self.assertEqual(updated.translation_provider, "gemini")
        self.assertEqual(updated.translation_max_retries, 5)
        self.assertEqual(updated.translation_retry_base_delay_seconds, 1.5)
        self.assertEqual(updated.translation_context, "keep local idioms natural")


if __name__ == "__main__":
    unittest.main()
