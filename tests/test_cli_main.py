import unittest
from unittest import mock

from transcription.cli import main


class CliMainTests(unittest.TestCase):
    def test_build_parser_accepts_step(self) -> None:
        parser = main.build_parser()
        args = parser.parse_args(["--step", "download"])
        self.assertEqual(args.step, "download")

    def test_main_calls_run_download(self) -> None:
        with mock.patch("transcription.cli.main.run_download") as run_download:
            with mock.patch("sys.argv", ["prog", "--step", "download"]):
                main.main()
        run_download.assert_called_once()

    def test_main_handles_runtime_error(self) -> None:
        with mock.patch(
            "transcription.cli.main.run_download",
            side_effect=RuntimeError("pytube is required for YouTube download"),
        ):
            with mock.patch("sys.argv", ["prog", "--step", "download"]):
                with self.assertRaises(SystemExit) as exc:
                    main.main()
        self.assertEqual(exc.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
