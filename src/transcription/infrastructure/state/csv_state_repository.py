from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Optional

from transcription.domain.interfaces.state_repository import FileState, StateRepository


class CsvStateRepository(StateRepository):
    def __init__(self, csv_path: str) -> None:
        self._path = Path(csv_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, path: str) -> Optional[FileState]:
        for item in self.list_all():
            if item.path == path:
                return item
        return None

    def upsert(self, state: FileState) -> None:
        all_states = list(self.list_all())
        replaced = False
        for idx, current in enumerate(all_states):
            if current.path == state.path:
                all_states[idx] = state
                replaced = True
                break
        if not replaced:
            all_states.append(state)

        with self._path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            for item in all_states:
                writer.writerow([
                    item.path,
                    "true" if item.downloaded else "false",
                    "true" if item.segmented else "false",
                    "true" if item.transcribed else "false",
                ])

    def list_all(self) -> Iterable[FileState]:
        if not self._path.exists():
            return []

        states: list[FileState] = []
        with self._path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            for row in reader:
                if not row:
                    continue
                states.append(
                    FileState(
                        path=row[0],
                        downloaded=self._as_bool(row, 1),
                        segmented=self._as_bool(row, 2),
                        transcribed=self._as_bool(row, 3),
                    )
                )
        return states

    @staticmethod
    def _as_bool(row: list[str], index: int) -> bool:
        if len(row) <= index:
            return False
        return row[index].strip().lower() == "true"
