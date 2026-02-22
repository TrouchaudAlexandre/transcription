from __future__ import annotations

import argparse
import sys

from transcription.application.run_download import run_download
from transcription.config.settings import load_settings, override_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transcription pipeline CLI")
    parser.add_argument("--playlist-csv")
    parser.add_argument("--files-list-csv")
    parser.add_argument("--log-path")
    parser.add_argument("--audio-base-path")
    parser.add_argument("--video-base-path")
    parser.add_argument("--segmentation-root")
    parser.add_argument("--transcription-root")
    parser.add_argument("--output-root")
    parser.add_argument("--segment-length-seconds")
    parser.add_argument("--whisper-model")
    parser.add_argument("--language")
    parser.add_argument("--use-mock")
    parser.add_argument(
        "--step",
        default="download",
        choices=["download"],
        help="Pipeline step to execute. T4 supports download only.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    settings = load_settings()
    settings = override_settings(
        settings,
        playlist_csv=args.playlist_csv,
        files_list_csv=args.files_list_csv,
        log_path=args.log_path,
        audio_base_path=args.audio_base_path,
        video_base_path=args.video_base_path,
        segmentation_root=args.segmentation_root,
        transcription_root=args.transcription_root,
        output_root=args.output_root,
        segment_length_seconds=args.segment_length_seconds,
        whisper_model=args.whisper_model,
        language=args.language,
        use_mock=args.use_mock,
    )

    if args.step == "download":
        try:
            run_download(settings)
        except RuntimeError as exc:
            print(f"Runtime error: {exc}", file=sys.stderr)
            print(
                "Install missing dependencies in your environment, e.g. `pip install pytube python-dotenv`.",
                file=sys.stderr,
            )
            raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
