import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from transcription.infrastructure.transcription.whisper_engine import WhisperEngine


class WhisperEngineTests(unittest.TestCase):
    def test_transcribe_calls_whisper_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "in.m4a"
            audio.write_text("x", encoding="utf-8")
            output_dir = Path(tmp) / "out"

            with mock.patch("subprocess.run") as run:
                engine = WhisperEngine(model="large-v3-turbo", language="Arabic")
                engine.transcribe(str(audio), str(output_dir))

            run.assert_called_once()
            called = run.call_args[0][0]
            self.assertEqual(called[0], "whisper")
            self.assertIn("--model", called)
            self.assertIn("--language", called)


if __name__ == "__main__":
    unittest.main()
