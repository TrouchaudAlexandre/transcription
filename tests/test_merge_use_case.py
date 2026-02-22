import tempfile
import unittest
from pathlib import Path

from transcription.application.merge_use_case import MergeUseCase
from transcription.domain.interfaces.state_repository import FileState
from transcription.infrastructure.state.csv_state_repository import CsvStateRepository


class FakeLogger:
    def __init__(self) -> None:
        self.infos: list[str] = []
        self.errors: list[str] = []

    def info(self, message: str) -> None:
        self.infos.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)


class MergeUseCaseTests(unittest.TestCase):
    def test_merge_reindexes_and_offsets_segments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "audio" / "playlist" / "ep1.m4a"
            audio.parent.mkdir(parents=True, exist_ok=True)
            audio.write_text("a", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(audio), True, True, True))

            root = Path(tmp) / "transcription" / "playlist" / "ep1.m4a"
            root.mkdir(parents=True, exist_ok=True)
            (root / "ep1_part_1.srt").write_text(
                "1\n00:00:00,000 --> 00:00:02,000\nHello\n\n", encoding="utf-8"
            )
            (root / "ep1_part_2.srt").write_text(
                "1\n00:00:00,500 --> 00:00:01,000\nWorld\n\n", encoding="utf-8"
            )

            logger = FakeLogger()
            use_case = MergeUseCase(
                state_repository=repo,
                logger=logger,
                transcription_root=str(Path(tmp) / "transcription"),
                output_root=str(Path(tmp) / "output"),
                segment_length_seconds=60,
            )

            use_case.execute()

            out = Path(tmp) / "output" / "playlist" / "ep1_sous-titres_complets.srt"
            self.assertTrue(out.exists())
            content = out.read_text(encoding="utf-8")
            self.assertIn("1\n00:00:00,000 --> 00:00:02,000\nHello", content)
            self.assertIn("2\n00:01:00,500 --> 00:01:01,000\nWorld", content)

    def test_merge_skips_when_no_srt_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "audio" / "playlist" / "ep1.m4a"
            audio.parent.mkdir(parents=True, exist_ok=True)
            audio.write_text("a", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(audio), True, True, True))

            logger = FakeLogger()
            use_case = MergeUseCase(
                state_repository=repo,
                logger=logger,
                transcription_root=str(Path(tmp) / "transcription"),
                output_root=str(Path(tmp) / "output"),
                segment_length_seconds=60,
            )

            use_case.execute()

            self.assertTrue(any("Merge skipped" in msg for msg in logger.infos))


if __name__ == "__main__":
    unittest.main()
