import tempfile
import unittest
from pathlib import Path

from transcription.infrastructure.logging.file_logger import FileLogger


class FileLoggerTests(unittest.TestCase):
    def test_info_and_error_write_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "logs" / "app.log"
            logger = FileLogger(str(log_path))

            logger.info("hello")
            logger.error("boom")

            content = log_path.read_text(encoding="utf-8")
            self.assertIn("INFO - hello", content)
            self.assertIn("ERROR - boom", content)


if __name__ == "__main__":
    unittest.main()
