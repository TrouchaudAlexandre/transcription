import tempfile
import unittest
from pathlib import Path

from transcription.domain.interfaces.state_repository import FileState
from transcription.infrastructure.state.csv_state_repository import CsvStateRepository


class CsvStateRepositoryTests(unittest.TestCase):
    def test_upsert_get_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "files.csv"
            repo = CsvStateRepository(str(csv_path))

            repo.upsert(
                FileState(
                    path="/tmp/a.m4a",
                    downloaded=True,
                    segmented=False,
                    transcribed=False,
                    translated=False,
                )
            )
            repo.upsert(
                FileState(
                    path="/tmp/a.m4a",
                    downloaded=True,
                    segmented=True,
                    transcribed=False,
                    translated=True,
                )
            )

            item = repo.get("/tmp/a.m4a")
            self.assertIsNotNone(item)
            self.assertTrue(item.downloaded)
            self.assertTrue(item.segmented)
            self.assertFalse(item.transcribed)
            self.assertTrue(item.translated)
            self.assertEqual(len(list(repo.list_all())), 1)

    def test_list_all_parses_missing_flags_as_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "files.csv"
            csv_path.write_text("/tmp/a.m4a,true\n", encoding="utf-8")
            repo = CsvStateRepository(str(csv_path))

            item = repo.get("/tmp/a.m4a")
            self.assertIsNotNone(item)
            self.assertTrue(item.downloaded)
            self.assertFalse(item.segmented)
            self.assertFalse(item.transcribed)
            self.assertFalse(item.translated)

    def test_list_all_parses_translated_column_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "files.csv"
            csv_path.write_text(
                "/tmp/a.m4a,true,true,true,true\n",
                encoding="utf-8",
            )
            repo = CsvStateRepository(str(csv_path))

            item = repo.get("/tmp/a.m4a")
            self.assertIsNotNone(item)
            self.assertTrue(item.downloaded)
            self.assertTrue(item.segmented)
            self.assertTrue(item.transcribed)
            self.assertTrue(item.translated)


if __name__ == "__main__":
    unittest.main()
