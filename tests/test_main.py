"""
Tests for main initialization module.
"""

from pathlib import Path
from main import main


def test_main_execution():
    """Test that main() executes cleanly and returns exit code 0."""
    exit_code = main()
    assert exit_code == 0, "main() must return 0 indicating success"
