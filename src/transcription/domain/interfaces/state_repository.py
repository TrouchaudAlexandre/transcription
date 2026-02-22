from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class FileState:
    path: str
    downloaded: bool
    segmented: bool
    transcribed: bool


class StateRepository(ABC):
    @abstractmethod
    def get(self, path: str) -> Optional[FileState]:
        raise NotImplementedError

    @abstractmethod
    def upsert(self, state: FileState) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> Iterable[FileState]:
        raise NotImplementedError
