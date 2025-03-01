"""Tests for the CLI module."""

import sys
import pytest
from unittest.mock import patch
from walgreens_print.cli import parse_args


def test_parse_args_with_path():
    """Test parsing arguments with a valid path."""
    with patch.object(sys, 'argv', ['walgreens-print', 'path/to/image.jpg']):
        args = parse_args()
        assert args.path == 'path/to/image.jpg'


def test_parse_args_no_path():
    """Test parsing arguments with no path prints help and returns None."""
    with patch.object(sys, 'argv', ['walgreens-print']):
        with patch('argparse.ArgumentParser.print_help') as mock_print_help:
            args = parse_args()
            assert args is None
            mock_print_help.assert_called_once()


def test_version_flag(capsys):
    """Test the version flag prints the correct version."""
    with patch.object(sys, 'argv', ['walgreens-print', '--version']):
        with pytest.raises(SystemExit):
            parse_args()
        captured = capsys.readouterr()
        assert "walgreens-print version" in captured.out 