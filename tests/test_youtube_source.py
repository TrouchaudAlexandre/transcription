import csv
import sys
import tempfile
import types
import unittest
from pathlib import Path

from transcription.domain.models.media import PlaylistVideo
from transcription.infrastructure.sources.youtube_ytdlp_source import YouTubeYtDlpSource


class FakeLogger:
    def __init__(self) -> None:
        self.infos: list[str] = []
        self.errors: list[str] = []

    def info(self, message: str) -> None:
        self.infos.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)


class FakeYoutubeDL:
    def __init__(self, opts: dict) -> None:
        self.opts = opts

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def extract_info(self, _url: str, download: bool = False):
        return {
            "title": "My Fancy Playlist",
            "entries": [
                {"url": "https://video/1"},
                {"id": "video2id"},
            ],
        }

    def download(self, _urls):
        outtmpl = self.opts.get("outtmpl")
        if outtmpl:
            path = Path(outtmpl)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x", encoding="utf-8")


class YouTubeSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.old_ytdlp = sys.modules.get("yt_dlp")
        fake_module = types.SimpleNamespace(YoutubeDL=FakeYoutubeDL)
        sys.modules["yt_dlp"] = fake_module

    def tearDown(self) -> None:
        if self.old_ytdlp is None:
            sys.modules.pop("yt_dlp", None)
        else:
            sys.modules["yt_dlp"] = self.old_ytdlp

    def test_list_videos_and_resolve_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            playlist_csv = Path(tmp) / "playlists.csv"
            with playlist_csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["https://playlist/url", "Mon titre !"])

            logger = FakeLogger()
            source = YouTubeYtDlpSource(
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
            source = YouTubeYtDlpSource(
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
