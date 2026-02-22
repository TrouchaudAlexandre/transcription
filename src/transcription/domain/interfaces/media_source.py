from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from transcription.domain.models.media import DownloadResult, PlaylistVideo


class MediaSource(ABC):
    @abstractmethod
    def resolve_paths(self, item: PlaylistVideo) -> DownloadResult:
        raise NotImplementedError

    @abstractmethod
    def list_videos(self) -> Iterable[PlaylistVideo]:
        raise NotImplementedError

    @abstractmethod
    def download_video(self, item: PlaylistVideo) -> DownloadResult:
        raise NotImplementedError
