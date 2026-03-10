import tempfile
import unittest
from pathlib import Path

from transcription.application.translate_use_case import TranslateUseCase
from transcription.domain.interfaces.state_repository import FileState
from transcription.infrastructure.state.csv_state_repository import CsvStateRepository
from transcription.infrastructure.translation.srt_validator import DeterministicSrtValidator


class FakeLogger:
    def __init__(self) -> None:
        self.infos: list[str] = []
        self.errors: list[str] = []

    def info(self, message: str) -> None:
        self.infos.append(message)

    def error(self, message: str) -> None:
        self.errors.append(message)


class FakeTranslationEngine:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[dict[str, str]] = []

    def translate_srt_segment(
        self,
        source_srt: str,
        source_language: str,
        source_variant: str,
        target_language: str,
        translation_context: str,
    ) -> str:
        self.calls.append(
            {
                "source_srt": source_srt,
                "source_language": source_language,
                "source_variant": source_variant,
                "target_language": target_language,
                "translation_context": translation_context,
            }
        )
        if self.fail:
            raise RuntimeError("boom")
        return source_srt.replace("Hello", "Bonjour")


class TranslateUseCaseTests(unittest.TestCase):
    def test_translate_segments_and_updates_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "audio" / "playlist" / "ep1.m4a"
            video = audio.with_suffix(".mp4")
            source_dir = Path(tmp) / "transcription" / "playlist" / "ep1.m4a"
            seg1 = source_dir / "ep1_part_1.srt"
            seg2 = source_dir / "ep1_part_2.srt"

            audio.parent.mkdir(parents=True, exist_ok=True)
            source_dir.mkdir(parents=True, exist_ok=True)
            audio.write_text("a", encoding="utf-8")
            video.write_text("v", encoding="utf-8")
            seg1.write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n", encoding="utf-8")
            seg2.write_text("1\n00:00:01,000 --> 00:00:02,000\nHello\n", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(audio), True, True, True, False))
            repo.upsert(FileState(str(video), True, True, True, False))

            logger = FakeLogger()
            engine = FakeTranslationEngine()
            use_case = TranslateUseCase(
                engine=engine,
                validator=DeterministicSrtValidator(),
                state_repository=repo,
                logger=logger,
                transcription_root=str(Path(tmp) / "transcription"),
                translation_root=str(Path(tmp) / "translation"),
                source_language="Arabic",
                source_variant="tunisian_arabic",
                target_language="French",
                translation_context="Prefer natural French",
            )

            use_case.execute()

            self.assertEqual(len(engine.calls), 2)
            self.assertEqual(engine.calls[0]["source_variant"], "tunisian_arabic")
            self.assertEqual(engine.calls[0]["translation_context"], "Prefer natural French")
            self.assertTrue(repo.get(str(audio)).translated)
            self.assertTrue(repo.get(str(video)).translated)
            out = Path(tmp) / "translation" / "playlist" / "ep1.m4a" / "ep1_part_1.srt"
            self.assertTrue(out.exists())
            self.assertIn("Bonjour", out.read_text(encoding="utf-8"))

    def test_skip_already_translated_segments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "audio" / "playlist" / "ep1.m4a"
            source_dir = Path(tmp) / "transcription" / "playlist" / "ep1.m4a"
            output_dir = Path(tmp) / "translation" / "playlist" / "ep1.m4a"
            seg1 = source_dir / "ep1_part_1.srt"
            seg2 = source_dir / "ep1_part_2.srt"

            audio.parent.mkdir(parents=True, exist_ok=True)
            source_dir.mkdir(parents=True, exist_ok=True)
            output_dir.mkdir(parents=True, exist_ok=True)
            audio.write_text("a", encoding="utf-8")
            seg1.write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n", encoding="utf-8")
            seg2.write_text("1\n00:00:01,000 --> 00:00:02,000\nHello\n", encoding="utf-8")
            (output_dir / "ep1_part_1.srt").write_text("done\n", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(audio), True, True, True, False))

            logger = FakeLogger()
            engine = FakeTranslationEngine()
            use_case = TranslateUseCase(
                engine=engine,
                validator=DeterministicSrtValidator(),
                state_repository=repo,
                logger=logger,
                transcription_root=str(Path(tmp) / "transcription"),
                translation_root=str(Path(tmp) / "translation"),
                source_language="Arabic",
                source_variant="",
                target_language="French",
                translation_context="",
            )

            use_case.execute()

            self.assertEqual(len(engine.calls), 1)
            self.assertTrue(any("Translation skip" in msg for msg in logger.infos))
            self.assertTrue(repo.get(str(audio)).translated)

    def test_keep_state_false_when_translation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "audio" / "playlist" / "ep1.m4a"
            source_dir = Path(tmp) / "transcription" / "playlist" / "ep1.m4a"
            seg1 = source_dir / "ep1_part_1.srt"

            audio.parent.mkdir(parents=True, exist_ok=True)
            source_dir.mkdir(parents=True, exist_ok=True)
            audio.write_text("a", encoding="utf-8")
            seg1.write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(audio), True, True, True, False))

            logger = FakeLogger()
            engine = FakeTranslationEngine(fail=True)
            use_case = TranslateUseCase(
                engine=engine,
                validator=DeterministicSrtValidator(),
                state_repository=repo,
                logger=logger,
                transcription_root=str(Path(tmp) / "transcription"),
                translation_root=str(Path(tmp) / "translation"),
                source_language="Arabic",
                source_variant="",
                target_language="French",
                translation_context="",
            )

            use_case.execute()

            self.assertFalse(repo.get(str(audio)).translated)
            self.assertTrue(any("Translation segment failed" in msg for msg in logger.errors))
            self.assertTrue(any("Translation incomplete" in msg for msg in logger.errors))

    def test_keep_state_false_when_translation_breaks_srt_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "audio" / "playlist" / "ep1.m4a"
            source_dir = Path(tmp) / "transcription" / "playlist" / "ep1.m4a"
            seg1 = source_dir / "ep1_part_1.srt"

            audio.parent.mkdir(parents=True, exist_ok=True)
            source_dir.mkdir(parents=True, exist_ok=True)
            audio.write_text("a", encoding="utf-8")
            seg1.write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n", encoding="utf-8")

            repo = CsvStateRepository(str(Path(tmp) / "files.csv"))
            repo.upsert(FileState(str(audio), True, True, True, False))

            logger = FakeLogger()
            engine = FakeTranslationEngine()
            engine.translate_srt_segment = (  # type: ignore[method-assign]
                lambda **_: "1\n00:00:05,000 --> 00:00:06,000\nBonjour\n"
            )
            use_case = TranslateUseCase(
                engine=engine,
                validator=DeterministicSrtValidator(),
                state_repository=repo,
                logger=logger,
                transcription_root=str(Path(tmp) / "transcription"),
                translation_root=str(Path(tmp) / "translation"),
                source_language="Arabic",
                source_variant="",
                target_language="French",
                translation_context="",
            )

            use_case.execute()

            self.assertFalse(repo.get(str(audio)).translated)
            self.assertTrue(any("timecode mismatch" in msg.lower() for msg in logger.errors))


if __name__ == "__main__":
    unittest.main()
