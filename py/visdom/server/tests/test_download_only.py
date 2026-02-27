"""Smoke tests for the --download_only flag and download_scripts_only entry point."""

import io
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock


class DownloadOnlyTests(unittest.TestCase):
    # ── --download_only flag via main() ──────────────────────────────────────

    def test_download_only_flag_exits_without_server(self):
        """``visdom --download_only`` should download, print, and return – no server."""
        argv = ["visdom", "--download_only"]

        from visdom.server.run_server import main

        buf = io.StringIO()
        with (
            mock.patch.object(sys, "argv", argv),
            mock.patch(
                "visdom.server.run_server.download_scripts", lambda *a, **kw: None
            ),
            mock.patch("visdom.server.run_server.start_server") as mock_start,
            redirect_stdout(buf),
        ):
            main()

        mock_start.assert_not_called()

        output = buf.getvalue()
        self.assertIn("Downloaded all required scripts. Exiting.", output)
        self.assertNotIn("It's Alive!", output)

    # ── download_scripts_only() entry point ──────────────────────────────────

    def test_download_scripts_only_calls_download(self):
        """``visdom-download`` entry point should call download_scripts and exit."""
        buf = io.StringIO()
        with (
            mock.patch("visdom.server.run_server.download_scripts") as mock_dl,
            redirect_stdout(buf),
        ):
            from visdom.server.run_server import download_scripts_only

            download_scripts_only()

        mock_dl.assert_called_once()

        output = buf.getvalue()
        self.assertIn("Downloaded all required scripts. Exiting.", output)
        self.assertNotIn("It's Alive!", output)

    # ── download_scripts_and_run() entry point ───────────────────────────────

    def test_download_scripts_and_run_calls_download_then_main(self):
        """``visdom`` entry point should call download_scripts *then* main."""
        call_order = []

        with (
            mock.patch(
                "visdom.server.run_server.download_scripts",
                side_effect=lambda *a, **kw: call_order.append("download"),
            ),
            mock.patch(
                "visdom.server.run_server.main",
                side_effect=lambda *a, **kw: call_order.append("main"),
            ),
        ):
            from visdom.server.run_server import download_scripts_and_run

            download_scripts_and_run()

        self.assertEqual(call_order, ["download", "main"])


if __name__ == "__main__":
    unittest.main()
