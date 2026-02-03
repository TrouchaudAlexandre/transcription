from __future__ import annotations

import argparse

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

    # TODO: Wire the pipeline once the use cases are implemented.
    print(settings)


if __name__ == "__main__":
    main()
