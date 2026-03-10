import unittest
from unittest import mock

from transcription.infrastructure.translation.openai_translation_engine import (
    OpenAITranslationEngine,
)


class FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class FakeResponsesApi:
    def __init__(self, *results) -> None:
        self._results = list(results)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        result = self._results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class FakeClient:
    def __init__(self, *results) -> None:
        self.responses = FakeResponsesApi(*results)


class FakeApiError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class OpenAITranslationEngineTests(unittest.TestCase):
    def test_translate_srt_segment_uses_responses_api(self) -> None:
        engine = OpenAITranslationEngine(
            model="gpt-5-mini",
            api_key="secret",
            prompt_version="v1",
        )
        fake_client = FakeClient(FakeResponse("1\n00:00:00,000 --> 00:00:01,000\nBonjour"))
        engine._create_client = lambda: fake_client  # type: ignore[method-assign]

        result = engine.translate_srt_segment(
            "1\n00:00:00,000 --> 00:00:01,000\nHello",
            source_language="English",
            source_variant="tunisian_arabic",
            target_language="French",
            translation_context="Prefer natural French with cultural adaptation",
        )

        self.assertEqual(
            result,
            "1\n00:00:00,000 --> 00:00:01,000\nBonjour",
        )
        self.assertEqual(len(fake_client.responses.calls), 1)
        self.assertEqual(fake_client.responses.calls[0]["model"], "gpt-5-mini")
        self.assertIn("Translate subtitle text from English to French", fake_client.responses.calls[0]["instructions"])
        self.assertIn("source variant/dialect is tunisian_arabic", fake_client.responses.calls[0]["instructions"])
        self.assertIn("Prefer natural French with cultural adaptation", fake_client.responses.calls[0]["instructions"])

    def test_translate_srt_segment_strips_markdown_fences(self) -> None:
        engine = OpenAITranslationEngine(model="gpt-5-mini", api_key="")
        fake_client = FakeClient(
            FakeResponse("```srt\n1\n00:00:00,000 --> 00:00:01,000\nBonjour\n```")
        )
        engine._create_client = lambda: fake_client  # type: ignore[method-assign]

        result = engine.translate_srt_segment(
            "1\n00:00:00,000 --> 00:00:01,000\nHello",
            source_language="English",
            source_variant="",
            target_language="French",
            translation_context="",
        )

        self.assertEqual(
            result,
            "1\n00:00:00,000 --> 00:00:01,000\nBonjour",
        )

    def test_translate_srt_segment_rejects_empty_output(self) -> None:
        engine = OpenAITranslationEngine(model="gpt-5-mini", api_key="")
        fake_client = FakeClient(FakeResponse(""))
        engine._create_client = lambda: fake_client  # type: ignore[method-assign]

        with self.assertRaises(RuntimeError):
            engine.translate_srt_segment(
                "1\n00:00:00,000 --> 00:00:01,000\nHello",
                source_language="English",
                source_variant="",
                target_language="French",
                translation_context="",
            )

    def test_translate_srt_segment_retries_retryable_errors(self) -> None:
        engine = OpenAITranslationEngine(
            model="gpt-5-mini",
            api_key="secret",
            max_retries=2,
            retry_base_delay_seconds=0.5,
        )
        fake_client = FakeClient(
            FakeApiError("rate limit", 429),
            FakeResponse("1\n00:00:00,000 --> 00:00:01,000\nBonjour"),
        )
        engine._create_client = lambda: fake_client  # type: ignore[method-assign]

        with mock.patch("transcription.infrastructure.translation.openai_translation_engine.time.sleep") as sleep:
            result = engine.translate_srt_segment(
                "1\n00:00:00,000 --> 00:00:01,000\nHello",
                source_language="English",
                source_variant="",
                target_language="French",
                translation_context="",
            )

        self.assertEqual(result, "1\n00:00:00,000 --> 00:00:01,000\nBonjour")
        self.assertEqual(len(fake_client.responses.calls), 2)
        sleep.assert_called_once_with(0.5)

    def test_translate_srt_segment_does_not_retry_invalid_request(self) -> None:
        engine = OpenAITranslationEngine(
            model="gpt-5-mini",
            api_key="secret",
            max_retries=3,
            retry_base_delay_seconds=0.5,
        )
        fake_client = FakeClient(FakeApiError("invalid api key", 401))
        engine._create_client = lambda: fake_client  # type: ignore[method-assign]

        with mock.patch("transcription.infrastructure.translation.openai_translation_engine.time.sleep") as sleep:
            with self.assertRaises(FakeApiError):
                engine.translate_srt_segment(
                    "1\n00:00:00,000 --> 00:00:01,000\nHello",
                    source_language="English",
                    source_variant="",
                    target_language="French",
                    translation_context="",
                )

        self.assertEqual(len(fake_client.responses.calls), 1)
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
