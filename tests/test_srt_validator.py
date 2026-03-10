import unittest

from transcription.infrastructure.translation.srt_validator import DeterministicSrtValidator


class DeterministicSrtValidatorTests(unittest.TestCase):
    def test_validate_pair_accepts_same_structure(self) -> None:
        validator = DeterministicSrtValidator()
        source = "1\n00:00:00,000 --> 00:00:01,000\nHello\n"
        translated = "1\n00:00:00,000 --> 00:00:01,000\nBonjour\n"

        validator.validate_pair(source, translated)

    def test_validate_pair_rejects_timecode_change(self) -> None:
        validator = DeterministicSrtValidator()
        source = "1\n00:00:00,000 --> 00:00:01,000\nHello\n"
        translated = "1\n00:00:02,000 --> 00:00:03,000\nBonjour\n"

        with self.assertRaises(ValueError):
            validator.validate_pair(source, translated)

    def test_validate_pair_rejects_block_count_change(self) -> None:
        validator = DeterministicSrtValidator()
        source = "1\n00:00:00,000 --> 00:00:01,000\nHello\n"
        translated = (
            "1\n00:00:00,000 --> 00:00:01,000\nBonjour\n\n"
            "2\n00:00:01,000 --> 00:00:02,000\nSalut\n"
        )

        with self.assertRaises(ValueError):
            validator.validate_pair(source, translated)
