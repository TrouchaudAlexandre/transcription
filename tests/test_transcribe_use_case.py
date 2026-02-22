import tempfile
import unittest
from pathlib import Path

from transcription.application.transcribe_use_case import TranscribeUseCase
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


class FakeEngine:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[tuple[str, str]] = []

    def transcribe(self, input_audio_path: str, output_directory: str) -> None:
        self.calls.append((input_audio_path, output_directory))
        if self.fail:
            raise RuntimeError("boom")
        Path(output_directory).mkdir(parents=True, exist_ok=True)


class TranscribeUseCaseTests(unittest.TestCase):
    def test_transcribes_segments_and_updates_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "audio" / "playlist" / "ep1.m4a"
            video = audio.with_suffix(".mp4")
            seg_dir = Path(tmp) / "seg" / "playlist" / "ep1.m4a"
            seg1 = seg_dir / "ep1_part_1.m4a"
            seg2 = seg_dir / "ep1_part_2.m4a"

            audio.parent.mkdir(parents=True, exist_ok=True)
            seg_dir.mkdir(parents=True, exist_ok=True)
            audio.write_text("a", encoding="utf-8")
            video.write_text("v", encoding="utf-8")
            seg1.write_text("s1", encoding="utf-8")
            seg2.write_text("s2", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(audio), True, True, False))
            repo.upsert(FileState(str(video), True, True, False))

            logger = FakeLogger()
            engine = FakeEngine()
            use_case = TranscribeUseCase(
                engine=engine,
                state_repository=repo,
                logger=logger,
                segmentation_root=str(Path(tmp) / "seg"),
                transcription_root=str(Path(tmp) / "tr"),
            )

            use_case.execute()

            self.assertEqual(len(engine.calls), 2)
            self.assertTrue(repo.get(str(audio)).transcribed)
            self.assertTrue(repo.get(str(video)).transcribed)
            self.assertTrue(any("Transcription done" in m for m in logger.infos))

    def test_fallback_to_source_audio_when_no_segments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "audio" / "playlist" / "ep1.m4a"
            audio.parent.mkdir(parents=True, exist_ok=True)
            audio.write_text("a", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(audio), True, True, False))

            logger = FakeLogger()
            engine = FakeEngine()
            use_case = TranscribeUseCase(
                engine=engine,
                state_repository=repo,
                logger=logger,
                segmentation_root=str(Path(tmp) / "seg"),
                transcription_root=str(Path(tmp) / "tr"),
            )

            use_case.execute()

            self.assertEqual(len(engine.calls), 1)
            self.assertEqual(engine.calls[0][0], str(audio))
            self.assertTrue(repo.get(str(audio)).transcribed)

    def test_logs_error_and_keeps_state_when_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "audio" / "playlist" / "ep1.m4a"
            audio.parent.mkdir(parents=True, exist_ok=True)
            audio.write_text("a", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(audio), True, True, False))

            logger = FakeLogger()
            engine = FakeEngine(fail=True)
            use_case = TranscribeUseCase(
                engine=engine,
                state_repository=repo,
                logger=logger,
                segmentation_root=str(Path(tmp) / "seg"),
                transcription_root=str(Path(tmp) / "tr"),
            )

            use_case.execute()

            self.assertFalse(repo.get(str(audio)).transcribed)
            self.assertTrue(any("Transcription failed" in m for m in logger.errors))


if __name__ == "__main__":
    unittest.main()
