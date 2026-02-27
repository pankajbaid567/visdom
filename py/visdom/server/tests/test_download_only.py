"""Smoke tests for the --download_only flag and download_scripts_only entry point."""

import sys
from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def _patch_download(monkeypatch):
    """Prevent actual network calls during tests."""
    monkeypatch.setattr(
        "visdom.server.run_server.download_scripts", lambda *a, **kw: None
    )


# ── --download_only flag via main() ──────────────────────────────────────────


def test_download_only_flag_exits_without_server(capsys, monkeypatch):
    """``visdom --download_only`` should download, print, and return – no server."""
    monkeypatch.setattr(sys, "argv", ["visdom", "--download_only"])

    from visdom.server.run_server import main

    with mock.patch("visdom.server.run_server.start_server") as mock_start:
        main()

    mock_start.assert_not_called()

    captured = capsys.readouterr()
    assert "Downloaded all required scripts. Exiting." in captured.out
    assert "It's Alive!" not in captured.out


# ── download_scripts_only() entry point ──────────────────────────────────────


def test_download_scripts_only_calls_download(capsys, monkeypatch):
    """``visdom-download`` entry point should call download_scripts and exit."""
    with mock.patch("visdom.server.run_server.download_scripts") as mock_dl:
        from visdom.server.run_server import download_scripts_only

        download_scripts_only()

    mock_dl.assert_called_once()

    captured = capsys.readouterr()
    assert "Downloaded all required scripts. Exiting." in captured.out
    assert "It's Alive!" not in captured.out


# ── download_scripts_and_run() entry point ───────────────────────────────────


def test_download_scripts_and_run_calls_download_then_main(monkeypatch):
    """``visdom`` entry point should call download_scripts *then* main."""
    call_order = []

    monkeypatch.setattr(
        "visdom.server.run_server.download_scripts",
        lambda *a, **kw: call_order.append("download"),
    )
    monkeypatch.setattr(
        "visdom.server.run_server.main",
        lambda *a, **kw: call_order.append("main"),
    )

    from visdom.server.run_server import download_scripts_and_run

    download_scripts_and_run()

    assert call_order == ["download", "main"]
