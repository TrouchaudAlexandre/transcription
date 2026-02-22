import unittest
import tempfile
from pathlib import Path
from unittest import mock

from transcription.application.run_segment import run_segment
from transcription.config.settings import Settings


class RunSegmentTests(unittest.TestCase):
    def test_run_segment_wires_and_executes_use_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            settings = Settings(
                playlist_csv=str(Path(tmp) / "playlists.csv"),
                files_list_csv=str(Path(tmp) / "files_list.csv"),
                log_path=str(Path(tmp) / "log.txt"),
                audio_base_path=str(Path(tmp) / "audio"),
                video_base_path=str(Path(tmp) / "video"),
                segmentation_root=str(Path(tmp) / "segmentation"),
                transcription_root=str(Path(tmp) / "transcription"),
                output_root=str(Path(tmp) / "output"),
                segment_length_seconds=60,
                whisper_model="large-v3-turbo",
                language="Arabic",
                use_mock=False,
            )
            with mock.patch(
                "transcription.application.run_segment.SegmentUseCase"
            ) as use_case_cls:
                run_segment(settings)
        use_case_cls.assert_called_once()
        use_case_cls.return_value.execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
