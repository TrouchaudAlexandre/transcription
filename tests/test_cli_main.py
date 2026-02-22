import unittest
import subprocess
from unittest import mock

from transcription.cli import main


class CliMainTests(unittest.TestCase):
    def test_build_parser_accepts_step(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(["--step", "download"])
        self.assertEqual(args.step, "download")
        args = parser.parse_args(["--step", "segment"])
        self.assertEqual(args.step, "segment")
        args = parser.parse_args(["--step", "transcribe"])
        self.assertEqual(args.step, "transcribe")
        args = parser.parse_args(["--step", "merge"])
        self.assertEqual(args.step, "merge")

    def test_main_calls_run_download(self) -> None:
        with mock.patch("transcription.cli.main.run_download") as run_download:
            with mock.patch("transcription.cli.main.run_segment") as run_segment:
                with mock.patch("sys.argv", ["prog", "--step", "download"]):
                    main.main()
        run_download.assert_called_once()
        run_segment.assert_not_called()

    def test_main_calls_run_segment(self) -> None:
        with mock.patch("transcription.cli.main.run_download") as run_download:
            with mock.patch("transcription.cli.main.run_segment") as run_segment:
                with mock.patch("sys.argv", ["prog", "--step", "segment"]):
                    main.main()
        run_download.assert_not_called()
        run_segment.assert_called_once()

    def test_main_calls_run_transcribe(self) -> None:
        with mock.patch("transcription.cli.main.run_download") as run_download:
            with mock.patch("transcription.cli.main.run_segment") as run_segment:
                with mock.patch("transcription.cli.main.run_transcribe") as run_transcribe:
                    with mock.patch("sys.argv", ["prog", "--step", "transcribe"]):
                        main.main()
        run_download.assert_not_called()
        run_segment.assert_not_called()
        run_transcribe.assert_called_once()

    def test_main_calls_run_merge(self) -> None:
        with mock.patch("transcription.cli.main.run_download") as run_download:
            with mock.patch("transcription.cli.main.run_segment") as run_segment:
                with mock.patch("transcription.cli.main.run_transcribe") as run_transcribe:
                    with mock.patch("transcription.cli.main.run_merge") as run_merge:
                        with mock.patch("sys.argv", ["prog", "--step", "merge"]):
                            main.main()
        run_download.assert_not_called()
        run_segment.assert_not_called()
        run_transcribe.assert_not_called()
        run_merge.assert_called_once()

    def test_main_handles_runtime_error(self) -> None:
        with mock.patch(
            "transcription.cli.main.run_download",
            side_effect=RuntimeError("pytube is required for YouTube download"),
        ):
            with mock.patch("sys.argv", ["prog", "--step", "download"]):
                with self.assertRaises(SystemExit) as exc:
                    main.main()
        self.assertEqual(exc.exception.code, 1)

    def test_main_handles_subprocess_error(self) -> None:
        with mock.patch(
            "transcription.cli.main.run_segment",
            side_effect=subprocess.CalledProcessError(1, ["ffmpeg"]),
        ):
            with mock.patch("sys.argv", ["prog", "--step", "segment"]):
                with self.assertRaises(SystemExit) as exc:
                    main.main()
        self.assertEqual(exc.exception.code, 1)

    def test_main_handles_missing_command(self) -> None:
        with mock.patch(
            "transcription.cli.main.run_transcribe",
            side_effect=FileNotFoundError("whisper"),
        ):
            with mock.patch("sys.argv", ["prog", "--step", "transcribe"]):
                with self.assertRaises(SystemExit) as exc:
                    main.main()
        self.assertEqual(exc.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
