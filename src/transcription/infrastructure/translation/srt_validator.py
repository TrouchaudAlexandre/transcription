from __future__ import annotations

import re

from transcription.domain.interfaces.srt_validator import SrtValidator


class DeterministicSrtValidator(SrtValidator):
    TIMECODE_PATTERN = re.compile(
        r"^(\d{2}:\d{2}:\d{2},\d{3})\s-->\s(\d{2}:\d{2}:\d{2},\d{3})$"
    )

    def validate_pair(self, source_srt: str, translated_srt: str) -> None:
        source_blocks = self._parse_blocks(source_srt)
        translated_blocks = self._parse_blocks(translated_srt)

        if len(source_blocks) != len(translated_blocks):
            raise ValueError("SRT block count mismatch")

        for source_block, translated_block in zip(source_blocks, translated_blocks):
            if source_block["index"] != translated_block["index"]:
                raise ValueError("SRT index mismatch")
            if source_block["timecode"] != translated_block["timecode"]:
                raise ValueError("SRT timecode mismatch")
            if not translated_block["text_lines"]:
                raise ValueError("Translated SRT block has no text")
            if any(not line.strip() for line in translated_block["text_lines"]):
                raise ValueError("Translated SRT block contains empty text lines")

    def _parse_blocks(self, raw_srt: str) -> list[dict[str, object]]:
        normalized = raw_srt.strip()
        if not normalized:
            raise ValueError("SRT content is empty")

        blocks = [block for block in re.split(r"\n\s*\n", normalized) if block.strip()]
        parsed_blocks: list[dict[str, object]] = []
        for block in blocks:
            lines = [line.rstrip() for line in block.splitlines()]
            if len(lines) < 3:
                raise ValueError("SRT block is incomplete")
            index = lines[0].strip()
            if not index.isdigit():
                raise ValueError("SRT block index is invalid")
            timecode = lines[1].strip()
            if self.TIMECODE_PATTERN.match(timecode) is None:
                raise ValueError("SRT timecode is invalid")
            text_lines = lines[2:]
            parsed_blocks.append(
                {
                    "index": index,
                    "timecode": timecode,
                    "text_lines": text_lines,
                }
            )
        return parsed_blocks
