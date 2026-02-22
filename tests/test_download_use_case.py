import tempfile
import unittest
from pathlib import Path

from transcription.application.download_use_case import DownloadUseCase
from transcription.domain.interfaces.state_repository import FileState
from transcription.domain.models.media import DownloadResult, PlaylistVideo
from transcription.infrastructure.state.csv_state_repository import CsvStateRepository


class FakeLogger:
    def __init__(self) -> None:
        self.infos: list[str] = []
        self.errors: list[str] = []

    def info(self, message: str) -> None:
        self.infos.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)


class FakeSource:
    def __init__(self, items, paths, fail=False) -> None:
        self._items = items
        self._paths = paths
        self._fail = fail
        self.download_calls = 0

    def list_videos(self):
        return self._items

    def resolve_paths(self, item):
        return self._paths[item.index]

    def download_video(self, item):
        self.download_calls += 1
        if self._fail:
            raise RuntimeError("download failed")
        result = self._paths[item.index]
        Path(result.audio_path).parent.mkdir(parents=True, exist_ok=True)
        Path(result.video_path).parent.mkdir(parents=True, exist_ok=True)
        Path(result.audio_path).write_text("audio", encoding="utf-8")
        Path(result.video_path).write_text("video", encoding="utf-8")
        return result


class DownloadUseCaseTests(unittest.TestCase):
    def test_execute_downloads_and_updates_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            item = PlaylistVideo(playlist_title="pl", video_url="u1", index=1)
            paths = {
                1: DownloadResult(
                    audio_path=f"{tmp}/audio/pl-episode1.m4a",
                    video_path=f"{tmp}/video/pl-episode1.mp4",
                )
            }
            source = FakeSource([item], paths)
            state_repo = CsvStateRepository(f"{tmp}/state.csv")
            logger = FakeLogger()

            DownloadUseCase(source, state_repo, logger).execute()

            self.assertEqual(source.download_calls, 1)
            self.assertTrue(state_repo.get(paths[1].audio_path).downloaded)
            self.assertTrue(state_repo.get(paths[1].video_path).downloaded)
            self.assertTrue(any("Download done" in msg for msg in logger.infos))

    def test_execute_skips_when_already_done(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            item = PlaylistVideo(playlist_title="pl", video_url="u1", index=1)
            paths = {
                1: DownloadResult(
                    audio_path=f"{tmp}/audio/pl-episode1.m4a",
                    video_path=f"{tmp}/video/pl-episode1.mp4",
                )
            }
            Path(paths[1].audio_path).parent.mkdir(parents=True, exist_ok=True)
            Path(paths[1].video_path).parent.mkdir(parents=True, exist_ok=True)
            Path(paths[1].audio_path).write_text("audio", encoding="utf-8")
            Path(paths[1].video_path).write_text("video", encoding="utf-8")

            source = FakeSource([item], paths)
            state_repo = CsvStateRepository(f"{tmp}/state.csv")
            state_repo.upsert(FileState(paths[1].audio_path, True, False, False))
            state_repo.upsert(FileState(paths[1].video_path, True, False, False))
            logger = FakeLogger()

            DownloadUseCase(source, state_repo, logger).execute()

            self.assertEqual(source.download_calls, 0)
            self.assertTrue(any("Skip download" in msg for msg in logger.infos))

    def test_execute_logs_error_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            item = PlaylistVideo(playlist_title="pl", video_url="u1", index=1)
            paths = {
                1: DownloadResult(
                    audio_path=f"{tmp}/audio/pl-episode1.m4a",
                    video_path=f"{tmp}/video/pl-episode1.mp4",
                )
            }
            source = FakeSource([item], paths, fail=True)
            state_repo = CsvStateRepository(f"{tmp}/state.csv")
            logger = FakeLogger()

            DownloadUseCase(source, state_repo, logger).execute()

            self.assertEqual(source.download_calls, 1)
            self.assertTrue(any("Download failed" in msg for msg in logger.errors))
            self.assertIsNone(state_repo.get(paths[1].audio_path))


if __name__ == "__main__":
    unittest.main()
