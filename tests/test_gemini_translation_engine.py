import unittest
from unittest import mock

from transcription.infrastructure.translation.gemini_translation_engine import (
    GeminiTranslationEngine,
)


class FakeGenerateContentResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeModelsApi:
    def __init__(self, *results) -> None:
        self._results = list(results)
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        result = self._results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class FakeClient:
    def __init__(self, *results) -> None:
        self.models = FakeModelsApi(*results)


class FakeTypes:
    class GenerateContentConfig:
        def __init__(self, system_instruction: str, temperature: float) -> None:
            self.system_instruction = system_instruction
            self.temperature = temperature


class FakeApiError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class GeminiTranslationEngineTests(unittest.TestCase):
    def test_translate_srt_segment_uses_generate_content(self) -> None:
        engine = GeminiTranslationEngine(
            model="gemini-3.1-flash-lite",
            api_key="secret",
            prompt_version="v1",
        )
        fake_client = FakeClient(
            FakeGenerateContentResponse("1\n00:00:00,000 --> 00:00:01,000\nBonjour")
        )
        engine._create_client = lambda: (fake_client, FakeTypes)  # type: ignore[method-assign]

        result = engine.translate_srt_segment(
            "1\n00:00:00,000 --> 00:00:01,000\nHello",
            source_language="English",
            source_variant="tunisian_arabic",
            target_language="French",
            translation_context="Prefer natural French with cultural adaptation",
        )

        self.assertEqual(result, "1\n00:00:00,000 --> 00:00:01,000\nBonjour")
        self.assertEqual(len(fake_client.models.calls), 1)
        self.assertEqual(fake_client.models.calls[0]["model"], "gemini-3.1-flash-lite")
        config = fake_client.models.calls[0]["config"]
        self.assertIn("Translate subtitle text from English to French", config.system_instruction)
        self.assertIn("source variant/dialect is tunisian_arabic", config.system_instruction)
        self.assertIn("Prefer natural French with cultural adaptation", config.system_instruction)

    def test_translate_srt_segment_strips_markdown_fences(self) -> None:
        engine = GeminiTranslationEngine(model="gemini-3.1-flash-lite", api_key="")
        fake_client = FakeClient(
            FakeGenerateContentResponse("```srt\n1\n00:00:00,000 --> 00:00:01,000\nBonjour\n```")
        )
        engine._create_client = lambda: (fake_client, FakeTypes)  # type: ignore[method-assign]

        result = engine.translate_srt_segment(
            "1\n00:00:00,000 --> 00:00:01,000\nHello",
            source_language="English",
            source_variant="",
            target_language="French",
            translation_context="",
        )

        self.assertEqual(result, "1\n00:00:00,000 --> 00:00:01,000\nBonjour")

    def test_translate_srt_segment_retries_retryable_errors(self) -> None:
        engine = GeminiTranslationEngine(
            model="gemini-3.1-flash-lite",
            api_key="secret",
            max_retries=2,
            retry_base_delay_seconds=0.5,
        )
        fake_client = FakeClient(
            FakeApiError("resource exhausted", 429),
            FakeGenerateContentResponse("1\n00:00:00,000 --> 00:00:01,000\nBonjour"),
        )
        engine._create_client = lambda: (fake_client, FakeTypes)  # type: ignore[method-assign]

        with mock.patch("transcription.infrastructure.translation.retry_policy.time.sleep") as sleep:
            result = engine.translate_srt_segment(
                "1\n00:00:00,000 --> 00:00:01,000\nHello",
                source_language="English",
                source_variant="",
                target_language="French",
                translation_context="",
            )

        self.assertEqual(result, "1\n00:00:00,000 --> 00:00:01,000\nBonjour")
        self.assertEqual(len(fake_client.models.calls), 2)
        sleep.assert_called_once_with(0.5)

    def test_translate_srt_segment_does_not_retry_invalid_request(self) -> None:
        engine = GeminiTranslationEngine(
            model="gemini-3.1-flash-lite",
            api_key="secret",
            max_retries=3,
            retry_base_delay_seconds=0.5,
        )
        fake_client = FakeClient(FakeApiError("invalid api key", 401))
        engine._create_client = lambda: (fake_client, FakeTypes)  # type: ignore[method-assign]

        with mock.patch("transcription.infrastructure.translation.retry_policy.time.sleep") as sleep:
            with self.assertRaises(FakeApiError):
                engine.translate_srt_segment(
                    "1\n00:00:00,000 --> 00:00:01,000\nHello",
                    source_language="English",
                    source_variant="",
                    target_language="French",
                    translation_context="",
                )

        self.assertEqual(len(fake_client.models.calls), 1)
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
