from __future__ import annotations

import argparse
import subprocess
import sys

from transcription.application.run_download import run_download
from transcription.application.run_merge import run_merge
from transcription.application.run_segment import run_segment
from transcription.application.run_transcribe import run_transcribe
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
        choices=["download", "segment", "transcribe", "merge"],
        help="Pipeline step to execute.",
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

    try:
        if args.step == "download":
            run_download(settings)
        if args.step == "segment":
            run_segment(settings)
        if args.step == "transcribe":
            run_transcribe(settings)
        if args.step == "merge":
            run_merge(settings)
    except RuntimeError as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        print(
            "Install missing dependencies in your environment, e.g. `pip install pytube python-dotenv`.",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    except subprocess.CalledProcessError as exc:
        print(f"Subprocess failed: {exc}", file=sys.stderr)
        print(
            "Check that ffmpeg and ffprobe are installed and available in PATH.",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    except FileNotFoundError as exc:
        print(f"Command not found: {exc}", file=sys.stderr)
        print(
            "Check that `whisper`, `ffmpeg`, and `ffprobe` are installed and available in PATH.",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
