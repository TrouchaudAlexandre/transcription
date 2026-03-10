import unittest

from transcription.infrastructure.translation.openai_translation_engine import (
    OpenAITranslationEngine,
)


class FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class FakeResponsesApi:
    def __init__(self, response: FakeResponse) -> None:
        self._response = response
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self._response


class FakeClient:
    def __init__(self, response: FakeResponse) -> None:
        self.responses = FakeResponsesApi(response)


class OpenAITranslationEngineTests(unittest.TestCase):
    def test_translate_srt_segment_uses_responses_api(self) -> None:
        engine = OpenAITranslationEngine(
            model="gpt-4.1-mini",
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
        self.assertEqual(fake_client.responses.calls[0]["model"], "gpt-4.1-mini")
        self.assertIn("Translate subtitle text from English to French", fake_client.responses.calls[0]["instructions"])
        self.assertIn("source variant/dialect is tunisian_arabic", fake_client.responses.calls[0]["instructions"])
        self.assertIn("Prefer natural French with cultural adaptation", fake_client.responses.calls[0]["instructions"])

    def test_translate_srt_segment_strips_markdown_fences(self) -> None:
        engine = OpenAITranslationEngine(model="gpt-4.1-mini", api_key="")
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
        engine = OpenAITranslationEngine(model="gpt-4.1-mini", api_key="")
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


if __name__ == "__main__":
    unittest.main()
