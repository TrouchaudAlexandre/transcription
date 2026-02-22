import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from transcription.infrastructure.segmentation.ffmpeg_segmenter import FfmpegSegmenter


class FfmpegSegmenterTests(unittest.TestCase):
    def test_split_builds_ffprobe_and_ffmpeg_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_file = Path(tmp) / "audio.m4a"
            input_file.write_text("x", encoding="utf-8")

            calls = []

            def fake_run(cmd, **kwargs):
                calls.append(cmd)
                if cmd[0] == "ffprobe":
                    return subprocess.CompletedProcess(cmd, 0, stdout="125.0\n", stderr="")
                return subprocess.CompletedProcess(cmd, 0)

            with mock.patch("subprocess.run", side_effect=fake_run):
                segmenter = FfmpegSegmenter(segment_length_seconds=60)
                outputs = segmenter.split(str(input_file), str(Path(tmp) / "seg"))

            self.assertEqual(calls[0][0], "ffprobe")
            self.assertEqual(calls[1][0], "ffmpeg")
            self.assertEqual(calls[2][0], "ffmpeg")
            self.assertEqual(calls[3][0], "ffmpeg")
            self.assertEqual(len(outputs), 3)


if __name__ == "__main__":
    unittest.main()
