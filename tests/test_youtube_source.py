import csv
import sys
import tempfile
import types
import unittest
from pathlib import Path

from transcription.domain.models.media import PlaylistVideo
from transcription.infrastructure.sources.youtube_pytube_source import YouTubePytubeSource


class FakeLogger:
    def __init__(self) -> None:
        self.infos: list[str] = []
        self.errors: list[str] = []

    def info(self, message: str) -> None:
        self.infos.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)


class FakeStream:
    def download(self, output_path: str, filename: str) -> None:
        Path(output_path).mkdir(parents=True, exist_ok=True)
        Path(output_path, filename).write_text("x", encoding="utf-8")


class FakeStreams:
    def get_audio_only(self):
        return FakeStream()

    def get_highest_resolution(self):
        return FakeStream()


class FakePlaylist:
    def __init__(self, _url: str) -> None:
        self.title = "My Fancy Playlist"
        self.video_urls = ["https://video/1", "https://video/2"]


class FakeYouTube:
    def __init__(self, _url: str) -> None:
        self.streams = FakeStreams()


class YouTubeSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.old_pytube = sys.modules.get("pytube")
        fake_module = types.SimpleNamespace(Playlist=FakePlaylist, YouTube=FakeYouTube)
        sys.modules["pytube"] = fake_module

    def tearDown(self) -> None:
        if self.old_pytube is None:
            sys.modules.pop("pytube", None)
        else:
            sys.modules["pytube"] = self.old_pytube

    def test_list_videos_and_resolve_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            playlist_csv = Path(tmp) / "playlists.csv"
            with playlist_csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["https://playlist/url", "Mon titre !"]) 

            logger = FakeLogger()
            source = YouTubePytubeSource(
                playlist_csv=str(playlist_csv),
                audio_base_path=f"{tmp}/audio",
                video_base_path=f"{tmp}/video",
                logger=logger,
            )

            items = list(source.list_videos())
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0].playlist_title, "Mon-titre")

            resolved = source.resolve_paths(items[0])
            self.assertTrue(resolved.audio_path.endswith("Mon-titre-episode1.m4a"))
            self.assertTrue(resolved.video_path.endswith("Mon-titre-episode1.mp4"))

    def test_download_video_creates_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            playlist_csv = Path(tmp) / "playlists.csv"
            playlist_csv.write_text("", encoding="utf-8")

            logger = FakeLogger()
            source = YouTubePytubeSource(
                playlist_csv=str(playlist_csv),
                audio_base_path=f"{tmp}/audio",
                video_base_path=f"{tmp}/video",
                logger=logger,
            )

            item = PlaylistVideo(playlist_title="pl", video_url="https://video/1", index=1)
            result = source.download_video(item)
            self.assertTrue(Path(result.audio_path).exists())
            self.assertTrue(Path(result.video_path).exists())


if __name__ == "__main__":
    unittest.main()
