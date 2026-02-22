import tempfile
import unittest
from pathlib import Path

from transcription.application.segment_use_case import SegmentUseCase
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


class FakeSegmenter:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[tuple[str, str]] = []

    def split(self, input_audio_path: str, output_directory: str):
        self.calls.append((input_audio_path, output_directory))
        if self.fail:
            raise RuntimeError("boom")
        Path(output_directory).mkdir(parents=True, exist_ok=True)
        out = Path(output_directory) / "segment_1.m4a"
        out.write_text("x", encoding="utf-8")
        return [str(out)]


class SegmentUseCaseTests(unittest.TestCase):
    def test_execute_segments_and_updates_audio_video_states(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "audio" / "playlist" / "ep1.m4a"
            video = audio.with_suffix(".mp4")
            audio.parent.mkdir(parents=True, exist_ok=True)
            audio.write_text("a", encoding="utf-8")
            video.write_text("v", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(audio), True, False, False))
            repo.upsert(FileState(str(video), True, False, False))

            logger = FakeLogger()
            segmenter = FakeSegmenter()
            use_case = SegmentUseCase(
                segmenter=segmenter,
                state_repository=repo,
                logger=logger,
                segmentation_root=str(Path(tmp) / "seg"),
            )

            use_case.execute()

            self.assertEqual(len(segmenter.calls), 1)
            self.assertTrue(repo.get(str(audio)).segmented)
            self.assertTrue(repo.get(str(video)).segmented)
            self.assertTrue(any("Segmentation done" in m for m in logger.infos))

    def test_execute_logs_error_and_keeps_state_when_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "audio" / "playlist" / "ep1.m4a"
            audio.parent.mkdir(parents=True, exist_ok=True)
            audio.write_text("a", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(audio), True, False, False))

            logger = FakeLogger()
            segmenter = FakeSegmenter(fail=True)
            use_case = SegmentUseCase(
                segmenter=segmenter,
                state_repository=repo,
                logger=logger,
                segmentation_root=str(Path(tmp) / "seg"),
            )

            use_case.execute()

            self.assertFalse(repo.get(str(audio)).segmented)
            self.assertTrue(any("Segmentation failed" in m for m in logger.errors))

    def test_execute_ignores_non_audio_or_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text_path = Path(tmp) / "x.txt"
            text_path.write_text("x", encoding="utf-8")
            audio = Path(tmp) / "a.m4a"
            audio.write_text("a", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(text_path), True, False, False))
            repo.upsert(FileState(str(audio), False, False, False))

            logger = FakeLogger()
            segmenter = FakeSegmenter()
            use_case = SegmentUseCase(
                segmenter=segmenter,
                state_repository=repo,
                logger=logger,
                segmentation_root=str(Path(tmp) / "seg"),
            )

            use_case.execute()

            self.assertEqual(segmenter.calls, [])


if __name__ == "__main__":
    unittest.main()
