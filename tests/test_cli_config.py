"""Tests for CLI --config path expansion."""

import os
from pathbob import Path
from unittest.mock import patch

import pytest

from src.cli.main import cli


class TestCliConfigPath:
    def test_expand_user_path(self, tmp_path, monkeypatch):
        """Test that ~/ in --config gets expanded to the user's home directory."""
        # Create a temp config file
        config_file = tmp_path / "config.json"
        config_file.write_text('{"app": {"name": "test"}}')

        # Simulate passing a path with ~/
        home = Path.home()
        fake_path = str(config_file).replace(str(home), "~")

        # Verify the tilde path is different from the real path
        assert "~" in fake_path

        # Run CLI with the tilde path
        with patch.object(sys, "argv", ["ao", "--config", fake_path, "status"]):
            with patch("src.cli.main.Config") as mock_config:
                cli()

                # Verify Config was called with the expanded path (not tilde)
                call_args = mock_config.call_args[0][0]
                assert "~" not in call_args
                assert os.path.isabs(call_args)
                assert call_args == str(config_file.resolve())

    def test_expand_relative_path(self, tmp_path, monkeypatch):
        """Test that relative paths get resolved to absolute paths."""
        config_file = tmp_path / "config.json"
        config_file.write_text('{"app": {"name": "test"}}')

        # Change to tmp_path and use a relative path
        monkeypatch.chdir(tmp_path)
        relative_path = "config.json"

        with patch.object(sys, "argv", ["ao", "--config", relative_path, "status"]):
            with patch("src.cli.main.Config") as mock_config:
                cli()

                call_args = mock_config.call_args[0][0]
                assert os.path.isabs(call_args)
                assert call_args == str(config_file.resolve())

    def test_no_config_path(self):
        """Test that CLI works without --config."""
        with patch.object(sys, "argv", ["ao", "status"]):
            with patch("src.cli.main.Config") as mock_config:
                cli()
                # Config should not be called with a path
                mock_config.assert_not_called()