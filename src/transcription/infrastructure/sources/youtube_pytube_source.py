from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Iterable

from transcription.domain.interfaces.media_source import MediaSource
from transcription.domain.models.media import DownloadResult, PlaylistVideo


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    return cleaned.strip("-") or "playlist"


class YouTubePytubeSource(MediaSource):
    def __init__(
        self,
        playlist_csv: str,
        audio_base_path: str,
        video_base_path: str,
        logger,
    ) -> None:
        self._playlist_csv = Path(playlist_csv)
        self._audio_root = Path(audio_base_path)
        self._video_root = Path(video_base_path)
        self._logger = logger

    def list_videos(self) -> Iterable[PlaylistVideo]:
        try:
            from pytube import Playlist
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("pytube is required for YouTube download") from exc

        items: list[PlaylistVideo] = []
        if not self._playlist_csv.exists():
            self._logger.error(f"Playlist CSV not found: {self._playlist_csv}")
            return items

        with self._playlist_csv.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            for row in reader:
                if not row:
                    continue
                playlist_url = row[0].strip()
                if not playlist_url:
                    continue

                playlist = Playlist(playlist_url)
                title = row[1].strip() if len(row) > 1 and row[1].strip() else playlist.title
                safe_title = _safe_name(title)

                self._logger.info(f"Processing playlist: {safe_title}")
                for index, video_url in enumerate(playlist.video_urls, start=1):
                    items.append(
                        PlaylistVideo(
                            playlist_title=safe_title,
                            video_url=video_url,
                            index=index,
                        )
                    )
        return items

    def download_video(self, item: PlaylistVideo) -> DownloadResult:
        try:
            from pytube import YouTube
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("pytube is required for YouTube download") from exc

        yt = YouTube(item.video_url)

        resolved = self.resolve_paths(item)
        audio_path = Path(resolved.audio_path)
        video_path = Path(resolved.video_path)
        audio_dir = audio_path.parent
        video_dir = video_path.parent
        audio_dir.mkdir(parents=True, exist_ok=True)
        video_dir.mkdir(parents=True, exist_ok=True)

        audio_filename = audio_path.name
        video_filename = video_path.name

        if not audio_path.exists():
            yt.streams.get_audio_only().download(
                output_path=str(audio_dir),
                filename=audio_filename,
            )
        if not video_path.exists():
            yt.streams.get_highest_resolution().download(
                output_path=str(video_dir),
                filename=video_filename,
            )

        return DownloadResult(audio_path=str(audio_path), video_path=str(video_path))

    def resolve_paths(self, item: PlaylistVideo) -> DownloadResult:
        audio_dir = self._audio_root / item.playlist_title
        video_dir = self._video_root / item.playlist_title
        audio_filename = f"{item.playlist_title}-episode{item.index}.m4a"
        video_filename = f"{item.playlist_title}-episode{item.index}.mp4"
        return DownloadResult(
            audio_path=str(audio_dir / audio_filename),
            video_path=str(video_dir / video_filename),
        )
