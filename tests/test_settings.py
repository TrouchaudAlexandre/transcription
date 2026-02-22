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
            },
            clear=False,
        ):
            settings = load_settings()

        self.assertEqual(settings.playlist_csv, "/tmp/playlists.csv")
        self.assertEqual(settings.files_list_csv, "/tmp/files.csv")
        self.assertEqual(settings.segment_length_seconds, 90)
        self.assertTrue(settings.use_mock)
        self.assertEqual(settings.language, "French")

    def test_override_settings_applies_types(self) -> None:
        settings = load_settings()
        updated = override_settings(
            settings,
            segment_length_seconds="30",
            use_mock="true",
            whisper_model="tiny",
        )

        self.assertEqual(updated.segment_length_seconds, 30)
        self.assertTrue(updated.use_mock)
        self.assertEqual(updated.whisper_model, "tiny")


if __name__ == "__main__":
    unittest.main()
