from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlaylistVideo:
    playlist_title: str
    video_url: str
    index: int


@dataclass(frozen=True)
class DownloadResult:
    audio_path: str
    video_path: str
